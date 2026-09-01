"""Data & Pengaturan: connector, impor, taxonomy, re-analysis, dan audit log."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.timeutil import utcnow
from app.config import settings
from app.connectors.csv_import import CsvImportConnector, ImportValidationError
from app.connectors.official_x import (
    ConnectorUnavailable,
    OfficialXApiConnector,
    available_connectors,
)
from app.database import get_db
from app.deps import get_current_user, require_admin, write_audit
from app.ingest import ingest_posts, reanalyze_all
from app.models import AuditLog, IngestionRun, Post, PostAnalysis, Topic, User
from app.schemas import ImportResult, IngestionRunOut, TopicOut, TopicUpdate
from app.taxonomy import INTENTS, JOB_ROLES, LANGUAGES, PRODUCT_LIMITATIONS, SENTIMENTS

router = APIRouter(prefix="/data", tags=["data"])

MAX_UPLOAD_BYTES = 8 * 1024 * 1024


@router.get("/connectors")
def connectors(_user: User = Depends(get_current_user)) -> dict:
    return {
        "mode": settings.effective_source_mode,
        "requested_mode": settings.data_source_mode,
        "live_available": settings.live_mode_available,
        "connectors": [c.status() for c in available_connectors()],
        "notice": (
            "Mode live hanya aktif bila X_API_BEARER_TOKEN tersedia pada environment "
            "server. Token tidak pernah dikirim ke browser."
        ),
    }


@router.get("/taxonomy")
def taxonomy(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    topics = db.scalars(select(Topic).order_by(Topic.name)).all()
    return {
        "topics": [TopicOut.model_validate(t) for t in topics],
        "job_roles": JOB_ROLES,
        "intents": INTENTS,
        "sentiments": SENTIMENTS,
        "languages": LANGUAGES,
        "limitations": PRODUCT_LIMITATIONS,
        "engagement_formula": (
            f"likes x {settings.engagement_weight_like} + "
            f"reposts x {settings.engagement_weight_repost} + "
            f"replies x {settings.engagement_weight_reply} + "
            f"quotes x {settings.engagement_weight_quote}"
        ),
    }


@router.patch("/topics/{topic_id}", response_model=TopicOut)
def update_topic(
    topic_id: str,
    payload: TopicUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> TopicOut:
    topic = db.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topik tidak ditemukan.")
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(topic, field, value)
    write_audit(db, user, "taxonomy.update", "topic", topic.id, changes)
    db.commit()
    return TopicOut.model_validate(topic)


@router.get("/quality")
def data_quality(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    total = int(db.scalar(select(func.count(Post.id)).where(Post.deleted_at.is_(None))) or 0)
    analyzed = int(db.scalar(select(func.count(PostAnalysis.id))) or 0)
    unclassified = int(
        db.scalar(select(func.count(PostAnalysis.id)).where(PostAnalysis.topic_id.is_(None))) or 0
    )
    needs_review = int(
        db.scalar(select(func.count(PostAnalysis.id)).where(PostAnalysis.needs_review.is_(True)))
        or 0
    )
    uncertain = int(
        db.scalar(
            select(func.count(PostAnalysis.id)).where(
                PostAnalysis.sentiment_label == "Tidak Yakin"
            )
        )
        or 0
    )
    synthetic = int(
        db.scalar(select(func.count(Post.id)).where(Post.is_synthetic.is_(True))) or 0
    )
    earliest = db.scalar(select(func.min(Post.created_at_source)))
    latest = db.scalar(select(func.max(Post.created_at_source)))

    def share(part: int) -> float:
        return round(part / total * 100, 1) if total else 0.0

    return {
        "total_posts": total,
        "analyzed_posts": analyzed,
        "coverage_percent": share(analyzed),
        "unclassified_topic": unclassified,
        "unclassified_percent": share(unclassified),
        "needs_review": needs_review,
        "needs_review_percent": share(needs_review),
        "uncertain_sentiment": uncertain,
        "uncertain_percent": share(uncertain),
        "synthetic_posts": synthetic,
        "synthetic_percent": share(synthetic),
        "earliest_post": earliest.isoformat() if earliest else None,
        "latest_post": latest.isoformat() if latest else None,
    }


@router.post("/import", response_model=ImportResult)
def import_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> ImportResult:
    content = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Ukuran berkas melebihi 8 MB.")
    if not content:
        raise HTTPException(status_code=422, detail="Berkas kosong.")

    connector = CsvImportConnector()
    try:
        raw_posts = connector.fetch(content=content, filename=file.filename or "")
    except ImportValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    errors = getattr(connector, "last_errors", [])
    received = getattr(connector, "last_received", len(raw_posts))
    run = ingest_posts(
        db,
        raw_posts,
        source="import",
        triggered_by=user.id,
        extra_errors=errors,
        records_received=received,
    )
    write_audit(
        db, user, "data.import", "ingestion_run", run.id,
        {"filename": file.filename, "processed": run.records_processed},
    )
    db.commit()

    return ImportResult(
        run_id=run.id,
        records_received=run.records_received,
        records_processed=run.records_processed,
        records_failed=run.records_failed,
        status=run.status,
        errors=errors[:20],
    )


@router.post("/seed")
def seed_demo_data(
    count: int = Query(1400, ge=100, le=5000),
    days: int = Query(90, ge=7, le=365),
    reset: bool = Query(False),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> dict:
    from app.seed import run_seed

    # run_seed membuka session-nya sendiri; session request hanya dipakai
    # untuk mencatat audit setelah proses selesai.
    actor_email = user.email
    summary = run_seed(reset=reset, count=count, days=days)
    # Setelah reset, ID pengguna lama sudah tidak ada sehingga actor disimpan
    # sebagai email saja agar tidak melanggar foreign key.
    db.expire_all()
    db.add(
        AuditLog(
            actor_id=None if reset else user.id,
            actor_email=actor_email,
            action="data.seed",
            entity="system",
            detail=summary,
        )
    )
    db.commit()
    return {**summary, "message": "Seed data demo selesai."}


@router.post("/fetch-live", response_model=ImportResult)
def fetch_live(
    query: str = Query(..., min_length=2, max_length=300),
    days: int = Query(7, ge=1, le=7, description="X API recent search hanya 7 hari terakhir."),
    max_results: int = Query(100, ge=10, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> ImportResult:
    """Tarik post nyata melalui X API resmi lalu jalankan pipeline yang sama.

    Token dibaca dari environment server dan tidak pernah dikirim ke browser.
    Bila credential belum tersedia, permintaan ditolak dengan pesan yang jelas
    dan aplikasi tetap dapat dipakai pada mode demo.
    """
    connector = OfficialXApiConnector()
    if not connector.is_available:
        raise HTTPException(
            status_code=409,
            detail=(
                "Connector X API belum aktif. Isi X_API_BEARER_TOKEN pada "
                "environment server, lalu jalankan ulang backend."
            ),
        )

    try:
        raw_posts = connector.fetch(query=query, max_results=max_results, days=days)
    except ConnectorUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    run = ingest_posts(
        db,
        raw_posts,
        source="x_api",
        triggered_by=user.id,
        records_received=len(raw_posts),
    )
    write_audit(
        db,
        user,
        "data.fetch_live",
        "ingestion_run",
        run.id,
        # Query pencarian dicatat sebagai jejak audit; tidak ada data pribadi.
        {"query": query, "days": days, "processed": run.records_processed},
    )
    db.commit()

    return ImportResult(
        run_id=run.id,
        records_received=run.records_received,
        records_processed=run.records_processed,
        records_failed=run.records_failed,
        status=run.status,
        errors=[run.error_summary] if run.error_summary else [],
    )


@router.post("/reanalyze")
def reanalyze(
    db: Session = Depends(get_db), user: User = Depends(require_admin)
) -> IngestionRunOut:
    run = reanalyze_all(db, triggered_by=user.id)
    write_audit(db, user, "data.reanalyze", "ingestion_run", run.id)
    db.commit()
    return IngestionRunOut.model_validate(run, from_attributes=True)


@router.get("/runs", response_model=list[IngestionRunOut])
def list_runs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[IngestionRunOut]:
    runs = db.scalars(
        select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit)
    ).all()
    return [IngestionRunOut.model_validate(r, from_attributes=True) for r in runs]


@router.get("/audit")
def audit_log(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _user: User = Depends(require_admin),
) -> dict:
    rows = db.scalars(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    ).all()
    return {
        "items": [
            {
                "id": row.id,
                "actor_email": row.actor_email,
                "action": row.action,
                "entity": row.entity,
                "entity_id": row.entity_id,
                "detail": row.detail,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ],
        "generated_at": utcnow().isoformat(),
    }
