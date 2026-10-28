"""Read public posts through twitterapi.io with a bounded request budget."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from math import ceil

import httpx

from app.config import settings
from app.connectors.base import RawPost, SocialDataConnector
from app.connectors.official_x import ConnectorUnavailable

SEARCH_ENDPOINT = "https://api.twitterapi.io/twitter/tweet/advanced_search"


class TwitterApiIoConnector(SocialDataConnector):
    name = "twitterapi_io"
    label = "twitterapi.io (pihak ketiga)"
    description = "Pencarian post X melalui twitterapi.io. Credential hanya disimpan di server."

    @property
    def is_available(self) -> bool:
        return bool(settings.twitterapi_io_key)

    def fetch(self, *, query: str = "", max_results: int = 20, days: int = 7, **_kwargs) -> list[RawPost]:
        if not self.is_available:
            raise ConnectorUnavailable("TWITTERAPI_IO_KEY belum tersedia pada server.")
        if not query.strip():
            raise ConnectorUnavailable("Query pencarian wajib diisi.")
        limit = min(max(max_results, 1), 100)
        since = int((datetime.now(timezone.utc) - timedelta(days=min(max(days, 1), 7))).timestamp())
        params = {
            "query": f"({query.strip()}) lang:in -filter:retweets since_time:{since}",
            "queryType": "Latest",
            "cursor": "",
        }
        posts: list[RawPost] = []
        seen_ids: set[str] = set()
        seen_cursors: set[str] = set()
        try:
            with httpx.Client(timeout=25.0) as client:
                # No retries: each page can consume credits, even when it is short.
                for _ in range(ceil(limit / 20)):
                    response = client.get(SEARCH_ENDPOINT, params=params,
                                          headers={"X-API-Key": settings.twitterapi_io_key})
                    if response.status_code != 200:
                        hints = {401: "API key tidak valid.", 403: "Akses ditolak.",
                                 402: "Kredit tidak cukup.", 429: "Batas permintaan tercapai; coba lagi nanti."}
                        raise ConnectorUnavailable(
                            f"twitterapi.io HTTP {response.status_code}. "
                            + hints.get(response.status_code, "Provider belum dapat melayani permintaan."))
                    payload = response.json()
                    if not isinstance(payload, dict) or not isinstance(payload.get("tweets"), list):
                        raise ValueError("Invalid tweets response")
                    for item in payload["tweets"]:
                        post_id = str(item["id"])
                        if post_id in seen_ids:
                            continue
                        created = item["createdAt"]
                        try:
                            timestamp = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        except ValueError:
                            timestamp = parsedate_to_datetime(created)
                        if timestamp.tzinfo is None:
                            timestamp = timestamp.replace(tzinfo=timezone.utc)
                        posts.append(RawPost(
                            external_post_id=post_id,
                            text=item["text"],
                            created_at_source=timestamp.astimezone(timezone.utc).replace(tzinfo=None),
                            language="id" if item.get("lang") in ("in", "id", None, "") else item["lang"],
                            author_public_id=None,
                            like_count=max(0, int(item.get("likeCount") or 0)),
                            repost_count=max(0, int(item.get("retweetCount") or 0)),
                            reply_count=max(0, int(item.get("replyCount") or 0)),
                            quote_count=max(0, int(item.get("quoteCount") or 0)),
                            url=f"https://x.com/i/status/{post_id}",
                            is_synthetic=False,
                            source="twitterapi_io",
                        ))
                        seen_ids.add(post_id)
                        if len(posts) >= limit:
                            return posts
                    cursor = payload.get("next_cursor")
                    if not payload.get("has_next_page") or not cursor or cursor in seen_cursors:
                        break
                    seen_cursors.add(cursor)
                    params["cursor"] = cursor
        except httpx.RequestError:
            raise ConnectorUnavailable("Tidak dapat terhubung ke twitterapi.io. Coba lagi nanti.") from None
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError):
            raise ConnectorUnavailable("Format respons twitterapi.io tidak valid; data belum diimpor.") from None
        return posts
