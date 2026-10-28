"""Filter global yang dipakai konsisten oleh seluruh endpoint dashboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal

DataType = Literal["all", "real", "demo", "twitterapi_io"]

from fastapi import Query
from sqlalchemy import Select, and_, select
from sqlalchemy.orm import Session

from app.timeutil import utcnow
from app.models import Post, PostAnalysis, SourceQuery, Topic
from app.search.base import ParsedQuery, parse_query
from app.search.sql import get_search_provider

DEFAULT_WINDOW_DAYS = 30


@dataclass
class FilterSet:
    date_from: datetime
    date_to: datetime
    data_type: DataType = "all"
    query_id: str | None = None
    job_roles: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    sentiments: list[str] = field(default_factory=list)
    intents: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    min_engagement: float | None = None
    max_engagement: float | None = None
    q: str | None = None
    parsed_query: ParsedQuery = field(default_factory=ParsedQuery)

    @property
    def window_days(self) -> int:
        return max(1, (self.date_to.date() - self.date_from.date()).days + 1)

    @property
    def previous_window(self) -> tuple[datetime, datetime]:
        """Periode sebelumnya dengan panjang identik, tanpa tumpang tindih."""
        length = timedelta(days=self.window_days)
        prev_end = self.date_from - timedelta(seconds=1)
        prev_start = self.date_from - length
        return prev_start, prev_end

    def period_label(self) -> str:
        return (
            f"{self.date_from.strftime('%d %b %Y')} – {self.date_to.strftime('%d %b %Y')}"
        )

    def as_dict(self) -> dict:
        return {
            "date_from": self.date_from.isoformat(),
            "date_to": self.date_to.isoformat(),
            "data_type": self.data_type,
            "query_id": self.query_id,
            "job_roles": self.job_roles,
            "topics": self.topics,
            "sentiments": self.sentiments,
            "intents": self.intents,
            "languages": self.languages,
            "min_engagement": self.min_engagement,
            "max_engagement": self.max_engagement,
            "q": self.q,
        }


def _end_of_day(value: datetime) -> datetime:
    return value.replace(hour=23, minute=59, second=59, microsecond=0)


def _start_of_day(value: datetime) -> datetime:
    return value.replace(hour=0, minute=0, second=0, microsecond=0)


def filter_params(
    date_from: datetime | None = Query(None, description="Awal periode (ISO 8601)"),
    date_to: datetime | None = Query(None, description="Akhir periode (ISO 8601)"),
    data_type: DataType = Query("all"),
    query_id: str | None = Query(None, description="ID query/monitor tersimpan"),
    job_roles: list[str] = Query(default=[]),
    topics: list[str] = Query(default=[], description="Slug topik"),
    sentiments: list[str] = Query(default=[]),
    intents: list[str] = Query(default=[]),
    languages: list[str] = Query(default=[]),
    min_engagement: float | None = Query(None, ge=0),
    max_engagement: float | None = Query(None, ge=0),
    q: str | None = Query(None, description="Query teks dengan AND/OR/-exclude"),
) -> FilterSet:
    resolved_to = _end_of_day(date_to or utcnow())
    resolved_from = _start_of_day(
        date_from or (resolved_to - timedelta(days=DEFAULT_WINDOW_DAYS - 1))
    )
    if resolved_from > resolved_to:
        resolved_from, resolved_to = _start_of_day(resolved_to), _end_of_day(resolved_from)

    return FilterSet(
        date_from=resolved_from,
        date_to=resolved_to,
        data_type=data_type,
        query_id=query_id,
        job_roles=[v for v in job_roles if v],
        topics=[v for v in topics if v],
        sentiments=[v for v in sentiments if v],
        intents=[v for v in intents if v],
        languages=[v for v in languages if v],
        min_engagement=min_engagement,
        max_engagement=max_engagement,
        q=q,
        parsed_query=parse_query(q),
    )


def apply_saved_query(db: Session, filters: FilterSet) -> FilterSet:
    """Gabungkan filter tersimpan dari `source_queries` dengan filter aktif."""
    if not filters.query_id:
        return filters
    saved = db.get(SourceQuery, filters.query_id)
    if not saved:
        return filters

    combined_terms = list(filters.parsed_query.all_terms)
    # include_keywords adalah daftar alternatif (OR): monitor "Penipuan Lowongan"
    # harus cocok bila salah satu kata kunci muncul, bukan seluruhnya sekaligus.
    saved_any = [
        keyword.lower()
        for keyword in (saved.include_keywords or [])
        if keyword.lower() not in combined_terms
    ]
    excluded = list(filters.parsed_query.exclude_terms)
    for keyword in saved.exclude_keywords or []:
        if keyword.lower() not in excluded:
            excluded.append(keyword.lower())

    any_terms = list(filters.parsed_query.any_terms)
    any_terms.extend(t for t in saved_any if t not in any_terms)
    if saved.query_text:
        saved_parsed = parse_query(saved.query_text)
        for term in saved_parsed.all_terms:
            if term not in combined_terms:
                combined_terms.append(term)
        any_terms.extend(t for t in saved_parsed.any_terms if t not in any_terms)

    filters.parsed_query = ParsedQuery(
        all_terms=combined_terms,
        any_terms=any_terms,
        exclude_terms=excluded,
        raw=filters.q or saved.query_text or "",
    )
    filters.job_roles = filters.job_roles or list(saved.job_roles or [])
    filters.topics = filters.topics or list(saved.topics or [])
    filters.sentiments = filters.sentiments or list(saved.sentiments or [])
    filters.intents = filters.intents or list(saved.intents or [])
    return filters


def base_conditions(
    filters: FilterSet,
    db: Session,
    *,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    include_text_query: bool = True,
) -> list:
    """Bangun daftar kondisi WHERE dari filter global."""
    conditions = [
        Post.deleted_at.is_(None),
        Post.created_at_source >= (date_from or filters.date_from),
        Post.created_at_source <= (date_to or filters.date_to),
    ]

    if filters.data_type in ("real", "twitterapi_io"):
        conditions.append(Post.is_synthetic.is_(False))
    elif filters.data_type == "demo":
        conditions.append(Post.is_synthetic.is_(True))
    if filters.data_type == "twitterapi_io":
        conditions.append(Post.source == "twitterapi_io")

    if filters.job_roles:
        conditions.append(PostAnalysis.job_role.in_(filters.job_roles))
    if filters.sentiments:
        conditions.append(PostAnalysis.sentiment_label.in_(filters.sentiments))
    if filters.intents:
        conditions.append(PostAnalysis.intent_label.in_(filters.intents))
    if filters.languages:
        conditions.append(Post.language.in_(filters.languages))
    if filters.min_engagement is not None:
        conditions.append(PostAnalysis.engagement_score >= filters.min_engagement)
    if filters.max_engagement is not None:
        conditions.append(PostAnalysis.engagement_score <= filters.max_engagement)

    if filters.topics:
        topic_ids = list(
            db.scalars(select(Topic.id).where(Topic.slug.in_(filters.topics))).all()
        )
        # Slug yang tidak dikenal harus menghasilkan nol baris, bukan diabaikan.
        conditions.append(PostAnalysis.topic_id.in_(topic_ids or ["__none__"]))

    if include_text_query and not filters.parsed_query.is_empty:
        clause = get_search_provider().text_filter(filters.parsed_query)
        if clause is not None:
            conditions.append(clause)

    return conditions


def filtered_query(
    filters: FilterSet,
    db: Session,
    *columns,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> Select:
    """Select ter-join Post + PostAnalysis dengan seluruh filter diterapkan."""
    selected = columns or (Post, PostAnalysis)
    stmt = (
        select(*selected)
        .select_from(Post)
        .join(PostAnalysis, PostAnalysis.post_id == Post.id)
        .where(and_(*base_conditions(filters, db, date_from=date_from, date_to=date_to)))
    )
    return stmt
