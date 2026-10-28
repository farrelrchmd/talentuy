"""Impor satu post X publik melalui endpoint oEmbed milik X.

Connector ini tidak melakukan pencarian. Pengguna memberikan URL post yang
sudah diketahui, lalu server meminta representasi embed publik dari X.
"""

from __future__ import annotations

from datetime import datetime
from html.parser import HTMLParser
import re
from urllib.parse import quote, urlparse

import httpx

from app.connectors.base import RawPost, SocialDataConnector

OEMBED_ENDPOINT = "https://publish.twitter.com/oembed"
POST_PATH = re.compile(r"^/([A-Za-z0-9_]{1,15})/status/(\d+)(?:/.*)?$")


class PublicPostImportError(Exception):
    pass


class _EmbedParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.paragraph_depth = 0
        self.anchor_depth = 0
        self.text_parts: list[str] = []
        self.anchor_parts: list[str] = []

    def handle_starttag(self, tag: str, _attrs) -> None:
        if tag == "p":
            self.paragraph_depth += 1
        elif tag == "a":
            self.anchor_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self.paragraph_depth:
            self.paragraph_depth -= 1
        elif tag == "a" and self.anchor_depth:
            self.anchor_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.paragraph_depth:
            self.text_parts.append(data)
        elif self.anchor_depth:
            self.anchor_parts.append(data)


def parse_x_post_url(value: str) -> tuple[str, str, str]:
    raw = value.strip()
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host not in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}:
        raise PublicPostImportError("URL harus berupa post publik dari x.com atau twitter.com.")
    match = POST_PATH.match(parsed.path)
    if not match:
        raise PublicPostImportError("Format URL post X tidak dikenali.")
    username, post_id = match.groups()
    canonical = f"https://x.com/{username}/status/{post_id}"
    return username, post_id, canonical


def parse_embed_html(value: str) -> tuple[str, datetime]:
    parser = _EmbedParser()
    parser.feed(value)
    text = " ".join("".join(parser.text_parts).split())
    if not text:
        raise PublicPostImportError("Teks post tidak tersedia pada respons publik X.")

    published_at = None
    for candidate in reversed(parser.anchor_parts):
        cleaned = " ".join(candidate.split())
        try:
            published_at = datetime.strptime(cleaned, "%B %d, %Y")
            break
        except ValueError:
            continue
    if published_at is None:
        raise PublicPostImportError("Tanggal publikasi post tidak dapat dibaca.")
    return text, published_at


class XPublicEmbedConnector(SocialDataConnector):
    name = "x_public_embed"
    label = "URL Post X Publik"
    description = "Impor satu post X publik dari URL melalui layanan embed publik X."

    @property
    def is_available(self) -> bool:
        return True

    def fetch(self, *, url: str = "", **_kwargs) -> list[RawPost]:
        username, post_id, canonical = parse_x_post_url(url)
        endpoint = f"{OEMBED_ENDPOINT}?url={quote(canonical, safe='')}&omit_script=true"
        try:
            with httpx.Client(timeout=20.0, follow_redirects=True) as client:
                response = client.get(endpoint)
        except httpx.HTTPError as exc:
            raise PublicPostImportError("Layanan embed publik X tidak dapat dihubungi.") from exc
        if response.status_code != 200:
            raise PublicPostImportError(
                f"Post tidak dapat dibaca melalui layanan publik X (HTTP {response.status_code})."
            )
        try:
            payload = response.json()
            text, published_at = parse_embed_html(str(payload.get("html", "")))
        except (ValueError, TypeError) as exc:
            raise PublicPostImportError("Respons layanan publik X tidak valid.") from exc

        return [
            RawPost(
                external_post_id=post_id,
                text=text,
                created_at_source=published_at,
                language="id",
                author_public_id=username,
                url=canonical,
                is_synthetic=False,
                source="x_public_embed",
                extra={"provider": payload.get("provider_name", "X")},
            )
        ]
