"""Interface pipeline NLP.

Interface dipisahkan agar model baseline deterministik dapat diganti dengan
adapter model Bahasa Indonesia yang lebih berat tanpa mengubah arsitektur.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Label:
    label: str
    confidence: float
    evidence: list[str] = field(default_factory=list)


class SentimentAnalyzer(ABC):
    version: str = "abstract"

    @abstractmethod
    def analyze(self, text: str) -> Label: ...


class TopicClassifier(ABC):
    version: str = "abstract"

    @abstractmethod
    def classify(self, text: str) -> Label: ...


class IntentClassifier(ABC):
    version: str = "abstract"

    @abstractmethod
    def classify(self, text: str) -> Label: ...


class KeywordExtractor(ABC):
    version: str = "abstract"

    @abstractmethod
    def extract(self, text: str, limit: int = 8) -> list[str]: ...


class JobRoleTagger(ABC):
    version: str = "abstract"

    @abstractmethod
    def tag(self, text: str) -> Label: ...


class InsightSummarizer(ABC):
    version: str = "abstract"

    @abstractmethod
    def summarize(self, context: dict) -> str: ...
