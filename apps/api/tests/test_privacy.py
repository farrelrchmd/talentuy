"""Penyamaran identitas akun: username tidak boleh tersimpan atau terkirim ke frontend."""

from __future__ import annotations

import re
from datetime import datetime

from sqlalchemy import select

from app.connectors.base import RawPost
from app.ingest import ingest_posts
from app.models import Post
from app.privacy import anonymize_post_url, hash_author_id

HEX64 = re.compile(r"^[0-9a-f]{64}$")
USERNAME = "HrdBacot_Asli"
POST_ID = "1566952453937299999"


def test_hash_author_id_is_keyed_and_normalized():
    hashed = hash_author_id(USERNAME)
    assert HEX64.match(hashed)
    assert USERNAME.lower() not in hashed
    # Akun yang sama tetap bisa dikelompokkan, apa pun penulisannya.
    assert hash_author_id(f"@{USERNAME.lower()} ") == hashed
    # Tanpa kunci yang sama, hash tidak bisa dicocokkan.
    assert hash_author_id(USERNAME, key="kunci-lain") != hashed
    assert hash_author_id(None) is None
    assert hash_author_id("  @ ") is None


def test_anonymize_post_url_drops_username():
    expected = f"https://x.com/i/status/{POST_ID}"
    for url in (
        f"https://x.com/{USERNAME}/status/{POST_ID}",
        f"https://twitter.com/{USERNAME}/status/{POST_ID}?s=20",
        f"http://www.twitter.com/{USERNAME}/statuses/{POST_ID}/photo/1",
        f"https://mobile.x.com/{USERNAME}/status/{POST_ID}",
        expected,
    ):
        assert anonymize_post_url(url) == expected
    assert anonymize_post_url(None) is None
    assert anonymize_post_url("https://example.com/berita/1") == "https://example.com/berita/1"


def test_ingest_never_stores_username(client, admin_headers, db):
    raw = RawPost(
        external_post_id=POST_ID,
        text="Baru dapat offering letter, tetapi gaji yang ditawarkan 5 juta.",
        created_at_source=datetime(2022, 9, 6),
        author_public_id=USERNAME,
        url=f"https://x.com/{USERNAME}/status/{POST_ID}",
        is_synthetic=False,
        source="x_public_embed",
    )
    try:
        ingest_posts(db, [raw], source="x_public_embed")

        post = db.scalar(select(Post).where(Post.external_post_id == POST_ID))
        assert post is not None
        assert post.author_public_id == hash_author_id(USERNAME)
        assert post.url == f"https://x.com/i/status/{POST_ID}"
        assert USERNAME.lower() not in f"{post.author_public_id} {post.url}".lower()

        response = client.get(f"/posts/{post.id}", headers=admin_headers)
        assert response.status_code == 200, response.text
        assert USERNAME.lower() not in response.text.lower()
        assert "author_public_id" not in response.json()
    finally:
        post = db.scalar(select(Post).where(Post.external_post_id == POST_ID))
        if post is not None:
            db.delete(post)
            db.commit()


def test_no_stored_post_contains_username():
    """Seluruh korpus (termasuk data sintetis seed) hanya menyimpan hash."""
    from app.database import SessionLocal

    with SessionLocal() as session:
        rows = session.execute(select(Post.author_public_id, Post.url)).all()
    assert rows
    for author, url in rows:
        assert author is None or HEX64.match(author), author
        if url and "/status/" in url:
            assert "/i/status/" in url, url
