"""Penyamaran identitas akun sebelum post disimpan (UU PDP: tidak memprofilkan individu).

Username tidak pernah disimpan. ``author_public_id`` berisi HMAC-SHA256 dari
username sehingga post dari akun yang sama tetap bisa dikelompokkan, tetapi
username tidak dapat dibaca kembali tanpa kunci ``AUTHOR_HASH_KEY``.
"""

from __future__ import annotations

import hashlib
import hmac
import re

from app.config import settings

# Menangkap x.com/{username}/status/{id} beserta variannya (twitter.com, www, mobile).
_X_STATUS_URL = re.compile(
    r"^https?://(?:www\.|mobile\.)?(?:x|twitter)\.com/[^/?#]+/status(?:es)?/(\d+)",
    re.IGNORECASE,
)


def hash_author_id(value: str | None, key: str | None = None) -> str | None:
    """HMAC-SHA256 (hex, 64 karakter) dari username yang sudah dinormalisasi."""
    if value is None:
        return None
    normalized = value.strip().lstrip("@").lower()
    if not normalized:
        return None
    secret = (key if key is not None else settings.author_hash_key).encode()
    return hmac.new(secret, normalized.encode(), hashlib.sha256).hexdigest()


def anonymize_post_url(url: str | None) -> str | None:
    """Ganti URL post X menjadi x.com/i/status/{id} agar tidak memuat username."""
    if not url:
        return url
    match = _X_STATUS_URL.match(url.strip())
    if match is None:
        return url
    return f"https://x.com/i/status/{match.group(1)}"
