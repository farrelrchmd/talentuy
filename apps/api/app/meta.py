"""Pembangun metadata response (sumber data, periode, dan kesegaran data)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.analytics import data_freshness
from app.config import settings
from app.filters import FilterSet
from app.nlp.baseline import MODEL_VERSION
from app.schemas import ResponseMeta


def build_meta(db: Session, filters: FilterSet, record_count: int) -> ResponseMeta:
    freshness = data_freshness(db)
    prev_from, prev_to = filters.previous_window
    mode = settings.effective_source_mode
    return ResponseMeta(
        record_count=record_count,
        period_start=filters.date_from.isoformat(),
        period_end=filters.date_to.isoformat(),
        period_label=filters.period_label(),
        comparison_start=prev_from.isoformat(),
        comparison_end=prev_to.isoformat(),
        data_source_mode=mode,
        is_synthetic=mode == "demo" or freshness["synthetic_posts"] > 0,
        last_updated=freshness["last_updated"],
        is_stale=freshness["is_stale"],
        model_version=MODEL_VERSION,
        search_provider=freshness["search_provider"],
        applied_filters=filters.as_dict(),
    )
