"""Insight workflow: draft -> reviewed -> approved, selalu melalui manusia."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user, require_analyst, write_audit
from app.models import Insight, User
from app.schemas import InsightIn, InsightOut, InsightUpdate

router = APIRouter(prefix="/insights", tags=["insights"])


def _out(insight: Insight) -> InsightOut:
    return InsightOut(
        id=insight.id,
        title=insight.title,
        summary=insight.summary,
        human_note=insight.human_note,
        evidence_filters=insight.evidence_filters or {},
        metric_snapshot=insight.metric_snapshot or {},
        human_status=insight.human_status,
        is_synthetic_data=insight.is_synthetic_data,
        author_name=insight.author.name if insight.author else None,
        created_at=insight.created_at,
        updated_at=insight.updated_at,
    )


@router.get("", response_model=list[InsightOut])
def list_insights(
    status: str | None = Query(None, pattern="^(draft|reviewed|approved)$"),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[InsightOut]:
    stmt = select(Insight).order_by(Insight.created_at.desc())
    if status:
        stmt = stmt.where(Insight.human_status == status)
    return [_out(i) for i in db.scalars(stmt).all()]


@router.post("", response_model=InsightOut, status_code=201)
def create_insight(
    payload: InsightIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_analyst),
) -> InsightOut:
    insight = Insight(
        **payload.model_dump(),
        created_by=user.id,
        is_synthetic_data=settings.effective_source_mode == "demo",
    )
    db.add(insight)
    db.flush()
    write_audit(db, user, "insight.create", "insight", insight.id, {"title": insight.title})
    db.commit()
    return _out(insight)


@router.patch("/{insight_id}", response_model=InsightOut)
def update_insight(
    insight_id: str,
    payload: InsightUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_analyst),
) -> InsightOut:
    insight = db.get(Insight, insight_id)
    if insight is None:
        raise HTTPException(status_code=404, detail="Insight tidak ditemukan.")
    # Analyst hanya boleh mengubah insight miliknya sendiri.
    if user.role == "analyst" and insight.created_by not in (None, user.id):
        raise HTTPException(
            status_code=403, detail="Anda hanya dapat mengubah insight milik sendiri."
        )

    changes = payload.model_dump(exclude_unset=True)
    if changes.get("human_status") == "approved" and user.role not in {"admin", "analyst"}:
        raise HTTPException(status_code=403, detail="Persetujuan memerlukan role analyst/admin.")
    for field, value in changes.items():
        setattr(insight, field, value)

    write_audit(db, user, "insight.update", "insight", insight.id, changes)
    db.commit()
    return _out(insight)


@router.delete("/{insight_id}", status_code=204)
def delete_insight(
    insight_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_analyst),
) -> Response:
    insight = db.get(Insight, insight_id)
    if insight is None:
        raise HTTPException(status_code=404, detail="Insight tidak ditemukan.")
    if user.role == "analyst" and insight.created_by not in (None, user.id):
        raise HTTPException(status_code=403, detail="Hanya pemilik insight yang dapat menghapus.")
    db.delete(insight)
    write_audit(db, user, "insight.delete", "insight", insight_id)
    db.commit()
    return Response(status_code=204)
