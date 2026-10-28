"""Pipeline analisis: menggabungkan seluruh komponen NLP dan skoring."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.nlp.base import Label
from app.nlp.baseline import (
    MODEL_VERSION,
    FrequencyKeywordExtractor,
    KeywordRoleTagger,
    KeywordTopicClassifier,
    LexiconSentimentAnalyzer,
    RuleIntentClassifier,
    normalize_text,
)

NEEDS_REVIEW_THRESHOLD = 0.55


@dataclass
class AnalysisResult:
    normalized_text: str
    sentiment_label: str
    sentiment_confidence: float
    intent_label: str
    intent_confidence: float
    topic_slug: str
    topic_confidence: float
    job_role: str
    job_role_confidence: float
    keywords: list[str]
    engagement_score: float
    relevance_score: float
    needs_review: bool
    # Dasar penetapan tiap label: {"topic"|"sentiment"|"intent"|"job_role":
    # {"rule": str, "triggers": [str]}}. Disimpan apa adanya agar frontend
    # tidak perlu menghitung ulang aturan.
    explanation: dict[str, dict]
    model_version: str = MODEL_VERSION


def engagement_score(
    likes: int, reposts: int, replies: int, quotes: int
) -> float:
    """Formula engagement yang dapat dikonfigurasi (lihat tooltip UI)."""
    return round(
        likes * settings.engagement_weight_like
        + reposts * settings.engagement_weight_repost
        + replies * settings.engagement_weight_reply
        + quotes * settings.engagement_weight_quote,
        2,
    )


def _explain(label: Label) -> dict:
    return {"rule": label.rule, "triggers": list(label.evidence)}


class AnalysisPipeline:
    def __init__(self) -> None:
        self.sentiment = LexiconSentimentAnalyzer()
        self.topic = KeywordTopicClassifier()
        self.intent = RuleIntentClassifier()
        self.role = KeywordRoleTagger()
        self.keywords = FrequencyKeywordExtractor()

    def run(
        self,
        text: str,
        *,
        likes: int = 0,
        reposts: int = 0,
        replies: int = 0,
        quotes: int = 0,
    ) -> AnalysisResult:
        normalized = normalize_text(text)
        sentiment = self.sentiment.analyze(text)
        intent = self.intent.classify(text)
        topic = self.topic.classify(text)
        role = self.role.tag(text)
        keywords = self.keywords.extract(text)
        engagement = engagement_score(likes, reposts, replies, quotes)

        # Relevansi dasar: kekuatan sinyal tekstual, bukan popularitas akun.
        # Engagement hanya menyumbang porsi kecil agar tidak mendominasi.
        textual = topic.confidence * 0.5 + role.confidence * 0.3 + intent.confidence * 0.2
        engagement_component = min(engagement / 400.0, 1.0) * 0.15
        relevance = round(min(1.0, textual * 0.85 + engagement_component), 4)

        needs_review = (
            sentiment.label == "Tidak Yakin"
            or sentiment.confidence < NEEDS_REVIEW_THRESHOLD
            or topic.confidence < NEEDS_REVIEW_THRESHOLD
        )

        return AnalysisResult(
            normalized_text=normalized,
            sentiment_label=sentiment.label,
            sentiment_confidence=sentiment.confidence,
            intent_label=intent.label,
            intent_confidence=intent.confidence,
            topic_slug=topic.label,
            topic_confidence=topic.confidence,
            job_role=role.label,
            job_role_confidence=role.confidence,
            keywords=keywords,
            engagement_score=engagement,
            relevance_score=relevance,
            needs_review=needs_review,
            explanation={
                "topic": _explain(topic),
                "sentiment": _explain(sentiment),
                "intent": _explain(intent),
                "job_role": _explain(role),
            },
        )


pipeline = AnalysisPipeline()
