"""Pembuatan berkas ekspor laporan (PDF dan CSV agregat).

Ekspor post-level dibatasi pada Post ID dan tautan saja. Seluruh laporan dari
data sintetis diberi watermark.
"""

from __future__ import annotations

import csv
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.timeutil import utcnow
from app.taxonomy import PRODUCT_LIMITATIONS

WATERMARK = "DATA SINTETIS — BUKAN TEMUAN AKTUAL"

METHODOLOGY = (
    "Data dikumpulkan melalui connector resmi atau dibangkitkan secara sintetis untuk "
    "keperluan prototipe. Label topik, sentimen, dan intent dihasilkan oleh model "
    "baseline berbasis leksikon dan aturan, lalu ditinjau manusia. Angka pada laporan "
    "merupakan hasil agregasi, bukan penilaian terhadap individu."
)

def _draw_watermark(canvas, doc) -> None:  # pragma: no cover - rendering
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 42)
    canvas.setFillColor(colors.Color(0.85, 0.87, 0.92, alpha=0.45))
    canvas.translate(A4[0] / 2, A4[1] / 2)
    canvas.rotate(38)
    canvas.drawCentredString(0, 0, "DATA SINTETIS")
    canvas.restoreState()

    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(18 * mm, 12 * mm, WATERMARK)
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, f"Halaman {doc.page}")
    canvas.restoreState()


def build_report_pdf(payload: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title=payload["title"],
        author="TalentPulse",
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "TPTitle", parent=styles["Title"], fontSize=19, spaceAfter=4, textColor=colors.HexColor("#0B1220")
    )
    h2 = ParagraphStyle(
        "TPHeading", parent=styles["Heading2"], fontSize=12.5, spaceBefore=12,
        textColor=colors.HexColor("#111827"),
    )
    body = ParagraphStyle("TPBody", parent=styles["BodyText"], fontSize=9.5, leading=14)
    muted = ParagraphStyle("TPMuted", parent=body, textColor=colors.HexColor("#667085"), fontSize=8.5)

    story: list = [
        Paragraph(payload["title"], h1),
        Paragraph(
            f"Periode {payload['period_start']} – {payload['period_end']} · "
            f"Dibuat {payload['generated_at']} · Sumber data: {payload['data_source_mode'].upper()}",
            muted,
        ),
        Spacer(1, 6),
    ]

    if payload.get("is_synthetic", True):
        story.append(
            Paragraph(
                f"<b>{WATERMARK}.</b> Laporan ini dihasilkan dari data demo dan tidak "
                "menggambarkan kondisi aktual.",
                ParagraphStyle("TPWarn", parent=body, textColor=colors.HexColor("#B45309")),
            )
        )
        story.append(Spacer(1, 8))

    story.append(Paragraph("Query dan filter yang digunakan", h2))
    filter_rows = [["Parameter", "Nilai"]]
    for key, value in (payload.get("query_snapshot") or {}).items():
        if value in (None, [], "", {}):
            continue
        filter_rows.append([str(key), ", ".join(map(str, value)) if isinstance(value, list) else str(value)])
    if len(filter_rows) == 1:
        filter_rows.append(["(tidak ada filter khusus)", "seluruh data pada periode"])
    story.append(_table(filter_rows, [55 * mm, 110 * mm]))

    story.append(Paragraph("Statistik agregat", h2))
    stats = payload.get("statistics") or {}
    stat_rows = [["Metrik", "Nilai"]] + [[k, str(v)] for k, v in stats.items()]
    story.append(_table(stat_rows, [85 * mm, 80 * mm]))

    charts = payload.get("charts_data") or []
    if charts:
        story.append(Paragraph("Grafik terpilih (disajikan sebagai tabel data)", h2))
        for chart in charts:
            story.append(Paragraph(chart["title"], ParagraphStyle("TPChart", parent=body, fontSize=10)))
            rows = [chart["columns"]] + [list(map(str, r)) for r in chart["rows"][:15]]
            story.append(_table(rows, None))
            story.append(Spacer(1, 6))

    story.append(Paragraph("Temuan yang ditinjau manusia", h2))
    insights = payload.get("insights") or []
    if not insights:
        story.append(Paragraph("Belum ada insight yang dilampirkan pada laporan ini.", muted))
    for index, insight in enumerate(insights, start=1):
        story.append(
            Paragraph(f"{index}. {insight['title']} <font size=8>[{insight['human_status']}]</font>", body)
        )
        story.append(Paragraph(insight.get("summary", ""), muted))
        if insight.get("human_note"):
            story.append(Paragraph(f"<i>Catatan analis: {insight['human_note']}</i>", muted))
        story.append(Spacer(1, 4))

    if payload.get("notes"):
        story.append(Paragraph("Catatan laporan", h2))
        story.append(Paragraph(payload["notes"], body))

    story.append(PageBreak())
    story.append(Paragraph("Metodologi", h2))
    story.append(Paragraph(METHODOLOGY, body))
    story.append(Paragraph("Keterbatasan", h2))
    for limitation in PRODUCT_LIMITATIONS:
        story.append(Paragraph(f"• {limitation}", muted))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "TalentPulse adalah prototipe internal dan tidak berafiliasi resmi dengan X. "
            "Dashboard ini tidak digunakan untuk menilai atau menyaring kandidat.",
            muted,
        )
    )

    doc.build(story, onFirstPage=_draw_watermark, onLaterPages=_draw_watermark)
    return buffer.getvalue()


def _table(rows: list[list[str]], widths: list[float] | None) -> Table:
    table = Table(rows, colWidths=widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E4E7EC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
            ]
        )
    )
    return table


def build_report_csv(payload: dict) -> str:
    """CSV agregat. Tidak memuat teks post — hanya angka dan identitas post."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["# TalentPulse — laporan agregat"])
    if payload.get("is_synthetic", True):
        writer.writerow(["# " + WATERMARK])
    writer.writerow(["# Judul", payload["title"]])
    writer.writerow(["# Periode", f"{payload['period_start']} s/d {payload['period_end']}"])
    writer.writerow(["# Sumber data", payload["data_source_mode"]])
    writer.writerow(["# Dibuat", payload["generated_at"]])
    writer.writerow([])

    writer.writerow(["bagian", "label", "nilai", "satuan"])
    for key, value in (payload.get("statistics") or {}).items():
        writer.writerow(["statistik", key, value, ""])
    for chart in payload.get("charts_data") or []:
        for row in chart["rows"]:
            writer.writerow([chart["key"], row[0], row[1], chart.get("unit", "post")])
    for insight in payload.get("insights") or []:
        writer.writerow(["insight", insight["title"], insight["human_status"], ""])

    writer.writerow([])
    writer.writerow(["# Keterbatasan"])
    for limitation in PRODUCT_LIMITATIONS:
        writer.writerow(["# ", limitation])
    return buffer.getvalue()


def build_post_reference_csv(rows: list[dict], is_synthetic: bool) -> str:
    """Ekspor referensi post: hanya Post ID, tanggal, dan tautan."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    if is_synthetic:
        writer.writerow(["# " + WATERMARK])
    writer.writerow(["# Ekspor dibatasi pada Post ID dan tautan (tanpa teks dan tanpa identitas)"])
    writer.writerow(["external_post_id", "created_at_source", "topic", "job_role", "url"])
    for row in rows:
        writer.writerow(
            [row["external_post_id"], row["created_at"], row["topic"], row["job_role"], row["url"] or ""]
        )
    return buffer.getvalue()


def timestamp_slug() -> str:
    return utcnow().strftime("%Y%m%d-%H%M")
