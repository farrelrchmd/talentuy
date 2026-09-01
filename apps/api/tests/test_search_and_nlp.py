"""Uji parser query boolean, pipeline NLP, dan template insight."""

from __future__ import annotations

from app.nlp.baseline import normalize_text
from app.nlp.pipeline import engagement_score, pipeline
from app.nlp.summarizer import summarizer
from app.search.base import parse_query


def test_parse_query_defaults_to_and():
    parsed = parse_query("gaji gudang")
    assert parsed.all_terms == ["gaji", "gudang"]
    assert parsed.any_terms == []


def test_parse_query_or_moves_previous_term():
    parsed = parse_query("gaji OR lembur")
    assert set(parsed.any_terms) == {"gaji", "lembur"}
    assert parsed.all_terms == []


def test_parse_query_exclusions():
    parsed = parse_query("gudang -penipuan NOT promosi")
    assert parsed.all_terms == ["gudang"]
    assert set(parsed.exclude_terms) == {"penipuan", "promosi"}


def test_parse_query_quoted_phrase():
    parsed = parse_query('"loker palsu" gudang')
    assert "loker palsu" in parsed.all_terms


def test_parse_query_empty():
    assert parse_query("").is_empty
    assert parse_query(None).is_empty


def test_normalize_expands_slang_and_strips_urls():
    normalized = normalize_text("Gaji nya brp sih? cek https://contoh.id @akun #loker")
    assert "https" not in normalized
    assert "@akun" not in normalized
    assert "berapa" in normalized


def test_question_detection():
    result = pipeline.run("min gaji staf gudang berapa ya?")
    assert result.intent_label == "Pertanyaan"
    assert result.intent_confidence >= 0.7


def test_fraud_warning_intent():
    result = pipeline.run("hati hati loker palsu minta bayar administrasi, itu penipuan")
    assert result.intent_label in {"Peringatan Penipuan", "Pertanyaan"}
    assert result.topic_slug == "keamanan-penipuan"


def test_low_confidence_becomes_uncertain():
    """Teks tanpa penanda kuat tidak boleh dipaksa jadi positif/negatif."""
    result = pipeline.run("sistem shift rolling per minggu")
    assert result.sentiment_label in {"Netral", "Tidak Yakin"}


def test_negation_flips_positive_phrase():
    result = pipeline.run("gaji tidak sesuai dan tidak dibayar tepat waktu, kecewa")
    assert result.sentiment_label == "Negatif"


def test_job_role_tagging():
    assert pipeline.run("lowongan helper gudang di cikarang").job_role == "Staf Gudang"
    assert pipeline.run("dibutuhkan spg mall untuk event").job_role == "Sales Promotion Girl/Boy"
    assert pipeline.run("cuaca hari ini cerah sekali").job_role == "Lainnya"


def test_engagement_formula_uses_configured_weights():
    assert engagement_score(10, 2, 4, 2) == 10 + 2 * 2 + 4 * 1.5 + 2 * 1.5


def test_relevance_not_dominated_by_engagement():
    """Post viral tanpa sinyal tekstual tidak boleh mengungguli post relevan."""
    viral_noise = pipeline.run("hari ini panas banget", likes=5000, reposts=5000)
    relevant = pipeline.run("berapa gaji staf gudang di cikarang sekarang?", likes=0)
    assert relevant.relevance_score > viral_noise.relevance_score


def test_insight_template_formats_indonesian_numbers():
    text = summarizer.summarize(
        {"topic": "Gaji dan Benefit", "share_percent": 18.42, "period": "Juli 2026",
         "change_percent": 12.5, "keywords": ["gaji", "lembur"]}
    )
    assert "Gaji dan Benefit" in text
    assert "18,4%" in text
    assert "naik 12,5%" in text


def test_insight_template_without_comparison():
    text = summarizer.summarize(
        {"topic": "Shift", "share_percent": 5.0, "period": "Juli", "change_percent": None}
    )
    assert "Tidak cukup data untuk membuat perbandingan" in text
