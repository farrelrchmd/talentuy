"""Interface SearchProvider.

MVP memakai PostgreSQL full-text search + pg_trgm. Interface ini memungkinkan
Elasticsearch/OpenSearch atau semantic search ditambahkan tanpa mengubah
pemanggil di layer analitik dan router.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ParsedQuery:
    """Hasil parsing boolean sederhana: AND, OR, dan exclude (-)."""

    all_terms: list[str] = field(default_factory=list)
    any_terms: list[str] = field(default_factory=list)
    exclude_terms: list[str] = field(default_factory=list)
    raw: str = ""

    @property
    def is_empty(self) -> bool:
        return not (self.all_terms or self.any_terms or self.exclude_terms)

    @property
    def highlight_terms(self) -> list[str]:
        return sorted({*self.all_terms, *self.any_terms}, key=len, reverse=True)


_TOKEN_RE = re.compile(r'"[^"]+"|\S+')


def parse_query(raw: str | None) -> ParsedQuery:
    """Parser boolean ringan: `gaji AND gudang OR lembur -penipuan`.

    Tanpa operator eksplisit, seluruh kata diperlakukan sebagai AND karena
    itu ekspektasi paling umum pengguna non-teknis.
    """
    parsed = ParsedQuery(raw=(raw or "").strip())
    if not parsed.raw:
        return parsed

    tokens = [t.strip() for t in _TOKEN_RE.findall(parsed.raw) if t.strip()]
    mode = "AND"
    pending_or = False

    for token in tokens:
        upper = token.upper()
        if upper in {"AND", "DAN"}:
            mode = "AND"
            continue
        if upper in {"OR", "ATAU"}:
            mode = "OR"
            pending_or = True
            continue
        if upper in {"NOT", "TANPA"}:
            mode = "NOT"
            continue

        term = token.strip('"').lower()
        if term.startswith("-") and len(term) > 1:
            parsed.exclude_terms.append(term[1:])
            continue
        if mode == "NOT":
            parsed.exclude_terms.append(term)
            mode = "AND"
            continue
        if mode == "OR":
            # `A OR B` memindahkan A terakhir ke grup OR agar semantik benar.
            if pending_or and parsed.all_terms:
                parsed.any_terms.append(parsed.all_terms.pop())
                pending_or = False
            parsed.any_terms.append(term)
            mode = "AND"
            continue
        parsed.all_terms.append(term)

    return parsed


class SearchProvider(ABC):
    """Menyediakan predikat pencarian dan ekspresi ranking untuk SQLAlchemy."""

    name: str = "abstract"

    @abstractmethod
    def text_filter(self, parsed: ParsedQuery):
        """Kembalikan klausa SQLAlchemy atau None jika query kosong."""

    @abstractmethod
    def rank_expression(self, parsed: ParsedQuery):
        """Kembalikan ekspresi skor relevansi tekstual (0..1)."""
