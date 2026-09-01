"""Insight summarizer berbasis template.

Semua kalimat wajib berbasis angka yang dihitung backend dan selalu ditandai
sebagai draft yang harus ditinjau manusia.
"""

from __future__ import annotations

from app.nlp.base import InsightSummarizer

TEMPLATE = (
    "Topik {topic} mencakup {share}% percakapan pada periode {period}, "
    "{direction} {change}% dibandingkan periode sebelumnya. "
    "Pertanyaan yang sering muncul berkaitan dengan {keywords}."
)


def direction_word(change: float | None) -> str:
    if change is None:
        return "belum dapat dibandingkan"
    if change > 1:
        return "naik"
    if change < -1:
        return "turun"
    return "relatif stabil"


class TemplateInsightSummarizer(InsightSummarizer):
    version = "template-1.0.0"

    def summarize(self, context: dict) -> str:
        change = context.get("change_percent")
        direction = direction_word(change)
        change_text = "0,0" if change is None else f"{abs(change):.1f}".replace(".", ",")
        share = f"{context.get('share_percent', 0):.1f}".replace(".", ",")
        keywords = context.get("keywords") or []
        keyword_text = ", ".join(keywords[:4]) if keywords else "beragam kata kunci"

        if change is None:
            return (
                f"Topik {context.get('topic', '-')} mencakup {share}% percakapan pada periode "
                f"{context.get('period', '-')}. Tidak cukup data untuk membuat perbandingan "
                f"dengan periode sebelumnya. Pertanyaan yang sering muncul berkaitan dengan "
                f"{keyword_text}."
            )

        return TEMPLATE.format(
            topic=context.get("topic", "-"),
            share=share,
            period=context.get("period", "-"),
            direction=direction,
            change=change_text,
            keywords=keyword_text,
        )


summarizer = TemplateInsightSummarizer()
