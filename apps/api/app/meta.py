"""Pembangun metadata response (sumber data, periode, dan kesegaran data)."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Post

from app.analytics import data_freshness
from app.filters import FilterSet, filtered_query
from app.nlp.baseline import MODEL_VERSION
from app.schemas import ResponseMeta


def build_meta(db: Session, filters: FilterSet, record_count: int) -> ResponseMeta:
    freshness = data_freshness(db)
    prev_from, prev_to = filters.previous_window
    synthetic_count = int(db.scalar(filtered_query(filters, db, func.count(Post.id)).where(Post.is_synthetic.is_(True))) or 0)
    mode = "demo" if synthetic_count > 0 or filters.data_type == "demo" else "live"
    return ResponseMeta(
        record_count=record_count,
        period_start=filters.date_from.isoformat(),
        period_end=filters.date_to.isoformat(),
        period_label=filters.period_label(),
        comparison_start=prev_from.isoformat(),
        comparison_end=prev_to.isoformat(),
        data_source_mode=mode,
        is_synthetic=mode == "demo",
        last_updated=freshness["last_updated"],
        is_stale=freshness["is_stale"],
        model_version=MODEL_VERSION,
        search_provider=freshness["search_provider"],
        applied_filters=filters.as_dict(),
    )
