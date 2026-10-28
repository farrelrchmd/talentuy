"""lima jenis pekerjaan, preset kata kunci, dasar klasifikasi

Revision ID: b7c2d9e4f1a0
Revises: e41ab7dc6ea3
Create Date: 2026-10-20 09:00:00.000000

- Menambah kolom post_analysis.explanation (aturan + kata pemicu per label).
- Membuat tabel keyword_presets dan mengisinya untuk topik yang sudah ada.
- Memetakan 10 jenis pekerjaan lama ke lima partisi naskah + "Lainnya".
  Pemetaan ini hanya pendekatan; jalankan "Analisis ulang" di Data &
  Pengaturan agar label jenis pekerjaan dan dasar klasifikasi dihitung ulang
  dari teks post.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.taxonomy import JOB_ROLE_FALLBACK, KEYWORD_PRESET_SEED, LEGACY_JOB_ROLE_MAP

revision: str = "b7c2d9e4f1a0"
down_revision: Union[str, None] = "e41ab7dc6ea3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("post_analysis", schema=None) as batch_op:
        batch_op.add_column(sa.Column("explanation", sa.JSON(), nullable=True))

    op.create_table(
        "keyword_presets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("topic_id", sa.String(length=36), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("query_text", sa.String(length=300), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("keyword_presets", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_keyword_presets_topic_id"), ["topic_id"], unique=False
        )

    bind = op.get_bind()

    # --- jenis pekerjaan pada hasil analisis
    for old, new in LEGACY_JOB_ROLE_MAP.items():
        if old != new:
            bind.execute(
                sa.text("UPDATE post_analysis SET job_role = :new WHERE job_role = :old"),
                {"new": new, "old": old},
            )

    # --- jenis pekerjaan pada query tersimpan (kolom JSON berisi daftar)
    queries = sa.table(
        "source_queries", sa.column("id", sa.String), sa.column("job_roles", sa.JSON)
    )
    for query_id, roles in bind.execute(sa.select(queries.c.id, queries.c.job_roles)).all():
        if not roles:
            continue
        mapped = list(dict.fromkeys(LEGACY_JOB_ROLE_MAP.get(r, r) for r in roles))
        if JOB_ROLE_FALLBACK in mapped and len(mapped) > 1:
            mapped.remove(JOB_ROLE_FALLBACK)
        if mapped != roles:
            bind.execute(
                queries.update().where(queries.c.id == query_id).values(job_roles=mapped)
            )

    # --- preset kata kunci awal untuk topik yang sudah ada
    topics = dict(bind.execute(sa.text("SELECT slug, id FROM topics")).all())
    presets = sa.table(
        "keyword_presets",
        sa.column("id", sa.String),
        sa.column("topic_id", sa.String),
        sa.column("label", sa.String),
        sa.column("query_text", sa.String),
        sa.column("sort_order", sa.Integer),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime),
    )
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    rows = [
        {
            "id": str(uuid.uuid4()),
            "topic_id": topics[slug],
            "label": label,
            "query_text": query_text,
            "sort_order": order,
            "is_active": True,
            "created_at": now,
        }
        for slug, items in KEYWORD_PRESET_SEED.items()
        if slug in topics
        for order, (label, query_text) in enumerate(items)
    ]
    if rows:
        op.bulk_insert(presets, rows)


def downgrade() -> None:
    with op.batch_alter_table("keyword_presets", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_keyword_presets_topic_id"))
    op.drop_table("keyword_presets")

    with op.batch_alter_table("post_analysis", schema=None) as batch_op:
        batch_op.drop_column("explanation")
    # Pemetaan jenis pekerjaan tidak dapat dibalik (beberapa label lama
    # digabung menjadi "Lainnya").
