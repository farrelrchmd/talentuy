"""samarkan identitas akun pada post

Revision ID: c4e8a1f2d3b5
Revises: b7c2d9e4f1a0
Create Date: 2026-10-27 09:00:00.000000

- posts.author_public_id: username diganti HMAC-SHA256 (kunci AUTHOR_HASH_KEY).
- posts.url: x.com/{username}/status/{id} diganti x.com/i/status/{id}.
Skema tidak berubah (String(80) cukup untuk hash hex 64 karakter). Nilai yang
sudah berupa hash dilewati, karena username X paling panjang 15 karakter.
"""

from __future__ import annotations

import re
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.privacy import anonymize_post_url, hash_author_id

revision: str = "c4e8a1f2d3b5"
down_revision: Union[str, None] = "b7c2d9e4f1a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_HASHED = re.compile(r"^[0-9a-f]{64}$")


def upgrade() -> None:
    bind = op.get_bind()
    posts = sa.table(
        "posts",
        sa.column("id", sa.String),
        sa.column("author_public_id", sa.String),
        sa.column("url", sa.String),
    )
    rows = bind.execute(sa.select(posts.c.id, posts.c.author_public_id, posts.c.url)).all()
    for post_id, author, url in rows:
        changes: dict[str, str | None] = {}
        if author and not _HASHED.match(author):
            changes["author_public_id"] = hash_author_id(author)
        new_url = anonymize_post_url(url)
        if new_url != url:
            changes["url"] = new_url
        if changes:
            bind.execute(posts.update().where(posts.c.id == post_id).values(**changes))


def downgrade() -> None:
    # Tidak dapat dibalik: username asli memang tidak disimpan lagi.
    pass
