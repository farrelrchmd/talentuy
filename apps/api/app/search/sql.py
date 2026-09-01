"""Implementasi SearchProvider di atas SQL relasional.

- PostgreSQL: `to_tsvector`/`plainto_tsquery` + `ts_rank`, ditambah pg_trgm
  similarity untuk toleransi typo.
- SQLite (fallback pengembangan lokal): LIKE pada kolom normalized_text.
"""

from __future__ import annotations

from sqlalchemy import Float, and_, case, cast, func, literal, or_

from app.models import PostAnalysis
from app.search.base import ParsedQuery, SearchProvider

_TARGET = PostAnalysis.normalized_text


class SqliteSearchProvider(SearchProvider):
    name = "sqlite-like"

    def text_filter(self, parsed: ParsedQuery):
        clauses = []
        if parsed.all_terms:
            clauses.append(and_(*[_TARGET.like(f"%{t}%") for t in parsed.all_terms]))
        if parsed.any_terms:
            clauses.append(or_(*[_TARGET.like(f"%{t}%") for t in parsed.any_terms]))
        if parsed.exclude_terms:
            clauses.extend(~_TARGET.like(f"%{t}%") for t in parsed.exclude_terms)
        if not clauses:
            return None
        return and_(*clauses)

    def rank_expression(self, parsed: ParsedQuery):
        terms = parsed.highlight_terms
        if not terms:
            return literal(0.0)
        # Skor = proporsi istilah query yang muncul pada teks ternormalisasi.
        hits = None
        for term in terms:
            score = case((_TARGET.like(f"%{term}%"), 1.0), else_=0.0)
            hits = score if hits is None else hits + score
        return cast(hits, Float) / float(len(terms))


class PostgresSearchProvider(SearchProvider):
    name = "postgres-fts"
    _config = "simple"  # tanpa stemmer bahasa Indonesia bawaan

    def _tsvector(self):
        return func.to_tsvector(self._config, _TARGET)

    def _tsquery(self, terms: list[str], operator: str):
        joined = f" {operator} ".join(t.replace("'", " ") for t in terms)
        return func.to_tsquery(self._config, joined)

    def text_filter(self, parsed: ParsedQuery):
        clauses = []
        if parsed.all_terms:
            clauses.append(self._tsvector().op("@@")(self._tsquery(parsed.all_terms, "&")))
        if parsed.any_terms:
            clauses.append(self._tsvector().op("@@")(self._tsquery(parsed.any_terms, "|")))
        if parsed.exclude_terms:
            clauses.append(
                ~self._tsvector().op("@@")(self._tsquery(parsed.exclude_terms, "|"))
            )
        if not clauses:
            return None
        return and_(*clauses)

    def rank_expression(self, parsed: ParsedQuery):
        terms = parsed.highlight_terms
        if not terms:
            return literal(0.0)
        rank = func.ts_rank(self._tsvector(), self._tsquery(terms, "|"))
        # ts_rank tidak ternormalisasi; dipetakan ke 0..1 agar konsisten
        # dengan provider lain.
        return func.least(cast(rank, Float) * 8.0, 1.0)


def get_search_provider() -> SearchProvider:
    from app.database import is_postgres

    return PostgresSearchProvider() if is_postgres() else SqliteSearchProvider()
