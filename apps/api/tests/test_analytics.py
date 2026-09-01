"""Uji logika analitik: KPI, periode pembanding, pembagi nol, dan peak."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app import analytics
from app.filters import FilterSet
from app.search.base import parse_query


def make_filters(days: int = 30, **kwargs) -> FilterSet:
    end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0)
    start = (end - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0)
    return FilterSet(date_from=start, date_to=end, **kwargs)


def test_percent_change_handles_zero_divisor():
    """Pembagi nol tidak boleh menghasilkan infinity."""
    assert analytics.percent_change(10, 0) is None
    assert analytics.percent_change(0, 0) is None
    assert analytics.percent_change(150, 100) == 50.0
    assert analytics.percent_change(50, 100) == -50.0


def test_share_percent_zero_total():
    assert analytics.share_percent(5, 0) == 0.0
    assert analytics.share_percent(25, 100) == 25.0


def test_previous_window_has_same_length_and_no_overlap():
    filters = make_filters(days=30)
    prev_start, prev_end = filters.previous_window
    assert prev_end < filters.date_from
    assert (filters.date_to.date() - filters.date_from.date()).days == (
        prev_end.date() - prev_start.date()
    ).days


def test_daily_volume_fills_empty_days(db):
    filters = make_filters(days=14)
    series = analytics.daily_volume(db, filters)
    assert len(series) == 14
    assert all("date" in point and "count" in point for point in series)
    assert series == sorted(series, key=lambda p: p["date"])


def test_weekly_aggregation_preserves_total(db):
    filters = make_filters(days=28)
    daily = analytics.daily_volume(db, filters)
    weekly = analytics.weekly_volume(daily)
    assert sum(p["count"] for p in weekly) == sum(p["count"] for p in daily)


def test_kpi_total_matches_count_query(db):
    filters = make_filters(days=30)
    kpis = analytics.overview_kpis(db, filters)
    assert kpis["total_posts"]["value"] == analytics.count_posts(db, filters)
    assert kpis["dominant_sentiment"]["value"] in {
        "Positif", "Netral", "Negatif", "Tidak Yakin", "Tidak ada data",
    }
    assert kpis["detected_questions"]["value"] >= 0
    assert kpis["active_topics"]["threshold"] == analytics.MIN_TOPIC_POSTS


def test_topic_shares_sum_to_about_hundred(db):
    filters = make_filters(days=45)
    topics = analytics.topic_breakdown(db, filters)
    assert topics, "seed harus menghasilkan topik"
    assert sum(t["share"] for t in topics) == pytest.approx(100.0, abs=0.5)
    assert topics == sorted(topics, key=lambda t: -t["count"])


def test_peak_detection_flags_only_above_baseline():
    flat = [{"date": f"2026-01-{d:02d}", "count": 10} for d in range(1, 15)]
    assert analytics.detect_peaks(flat) == []

    spiky = list(flat)
    spiky[12] = {"date": "2026-01-13", "count": 90}
    peaks = analytics.detect_peaks(spiky)
    assert peaks and peaks[0]["date"] == "2026-01-13"
    assert peaks[0]["count"] == 90


def test_peak_detection_needs_minimum_history():
    short = [{"date": f"2026-01-{d:02d}", "count": 5} for d in range(1, 5)]
    assert analytics.detect_peaks(short) == []


def test_indexed_series_starts_at_hundred():
    series = [{"date": "2026-01-01", "count": 20}, {"date": "2026-01-02", "count": 30}]
    indexed = analytics.indexed_series(series)
    assert indexed[0]["indexed"] == 100.0
    assert indexed[1]["indexed"] == 150.0


def test_filter_combination_narrows_results(db):
    base = make_filters(days=60)
    total = analytics.count_posts(db, base)

    narrowed = make_filters(days=60, job_roles=["Staf Gudang"], sentiments=["Negatif"])
    subset = analytics.count_posts(db, narrowed)
    assert subset <= total

    unknown_topic = make_filters(days=60, topics=["topik-tidak-ada"])
    assert analytics.count_posts(db, unknown_topic) == 0


def test_text_query_filters_posts(db):
    filters = make_filters(days=60, q="gaji")
    filters.parsed_query = parse_query("gaji")
    assert analytics.count_posts(db, filters) < analytics.count_posts(db, make_filters(days=60))


def test_heatmap_matrix_is_rectangular(db):
    data = analytics.concern_heatmap(db, make_filters(days=60))
    assert len(data["cells"]) == len(data["rows"]) * len(data["columns"])
    assert data["max_count"] >= 0


def test_related_keywords_edges_reference_existing_nodes(db):
    graph = analytics.related_keywords(db, make_filters(days=60))
    node_ids = {node["id"] for node in graph["nodes"]}
    assert all(e["source"] in node_ids and e["target"] in node_ids for e in graph["edges"])


def test_attention_issues_respect_threshold(db):
    issues = analytics.attention_issues(db, make_filters(days=60))
    assert all(issue["count"] >= analytics.MIN_TOPIC_POSTS for issue in issues)
    assert all(issue["reasons"] for issue in issues)
