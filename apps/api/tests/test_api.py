"""Uji endpoint API: auth, role, filter, search, monitor, insight, dan ekspor."""

from __future__ import annotations

from datetime import datetime, timedelta


def test_health_reports_seeded_database(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["seeded"] is True
    assert body["post_count"] > 0


def test_login_rejects_wrong_password(client):
    response = client.post(
        "/auth/login", json={"email": "analyst@talentpulse.local", "password": "salah"}
    )
    assert response.status_code == 401
    assert "tidak sesuai" in response.json()["detail"]


def test_protected_endpoint_requires_token(client):
    assert client.get("/dashboard/overview").status_code == 401


def test_overview_returns_all_sections_with_meta(client, analyst_headers):
    body = client.get("/dashboard/overview", headers=analyst_headers).json()
    for key in (
        "kpis", "volume_series", "peaks", "topics", "heatmap",
        "attention_issues", "top_questions", "limitations", "meta",
    ):
        assert key in body

    meta = body["meta"]
    assert meta["data_source_mode"] == "demo"
    assert meta["is_synthetic"] is True  # badge DATA DEMO
    assert meta["record_count"] == body["kpis"]["total_posts"]["value"]
    assert meta["model_version"]
    assert meta["comparison_start"] < meta["period_start"]


def test_overview_respects_job_role_filter(client, analyst_headers):
    everything = client.get("/dashboard/overview", headers=analyst_headers).json()
    filtered = client.get(
        "/dashboard/overview", headers=analyst_headers, params={"job_roles": ["Staf Gudang"]}
    ).json()
    assert filtered["kpis"]["total_posts"]["value"] <= everything["kpis"]["total_posts"]["value"]
    assert filtered["meta"]["applied_filters"]["job_roles"] == ["Staf Gudang"]


def test_trends_weekly_and_annotations(client, analyst_headers):
    body = client.get(
        "/dashboard/trends",
        headers=analyst_headers,
        params={"granularity": "weekly", "breakdown": "sentiment"},
    ).json()
    assert body["granularity"] == "weekly"
    assert body["breakdown_type"] == "sentiment"
    assert all("indexed" in point for point in body["series"])
    for annotation in body["annotations"]:
        # Anotasi tidak boleh mengklaim penyebab.
        assert "Lonjakan terdeteksi" in annotation["label"]


def test_topic_detail_share_is_relative_to_all_conversations(client, analyst_headers):
    topics = client.get("/dashboard/topics", headers=analyst_headers).json()["topics"]
    slug = topics[0]["slug"]
    detail = client.get(f"/dashboard/topics/{slug}", headers=analyst_headers).json()
    assert detail["topic"]["share"] < 100.0
    assert detail["suggested_summary"]


def test_post_search_sorting_and_pagination(client, analyst_headers):
    first = client.get(
        "/posts", headers=analyst_headers, params={"sort": "recent", "page_size": 10}
    ).json()
    assert first["page"] == 1
    assert len(first["items"]) <= 10
    dates = [item["created_at_source"] for item in first["items"]]
    assert dates == sorted(dates, reverse=True)

    second = client.get(
        "/posts", headers=analyst_headers, params={"sort": "recent", "page": 2, "page_size": 10}
    ).json()
    assert {i["id"] for i in first["items"]}.isdisjoint({i["id"] for i in second["items"]})


def test_post_search_engagement_sorting(client, analyst_headers):
    body = client.get(
        "/posts", headers=analyst_headers, params={"sort": "engagement", "page_size": 20}
    ).json()
    scores = [item["engagement_score"] for item in body["items"]]
    assert scores == sorted(scores, reverse=True)


def test_post_search_boolean_exclusion(client, analyst_headers):
    body = client.get(
        "/posts", headers=analyst_headers, params={"q": "gaji -penipuan", "page_size": 20}
    ).json()
    assert body["highlight_terms"] == ["gaji"]
    assert all("penipuan" not in item["text"].lower() for item in body["items"])


def test_post_search_no_result_state(client, analyst_headers):
    body = client.get(
        "/posts", headers=analyst_headers, params={"q": "qqqzzzxxx"}
    ).json()
    assert body["total"] == 0
    assert body["items"] == []
    assert body["total_pages"] == 1


def test_invalid_sort_is_rejected(client, analyst_headers):
    response = client.get("/posts", headers=analyst_headers, params={"sort": "populer"})
    assert response.status_code == 422


def test_confidence_hidden_from_viewer(client, viewer_headers, analyst_headers):
    viewer_item = client.get(
        "/posts", headers=viewer_headers, params={"page_size": 5}
    ).json()["items"][0]
    analyst_item = client.get(
        "/posts", headers=analyst_headers, params={"page_size": 5}
    ).json()["items"][0]
    assert viewer_item["sentiment_confidence"] is None
    assert analyst_item["sentiment_confidence"] is not None


def test_viewer_cannot_write(client, viewer_headers):
    response = client.post("/queries", headers=viewer_headers, json={"name": "uji"})
    assert response.status_code == 403


def test_analyst_cannot_read_audit_log(client, analyst_headers):
    assert client.get("/data/audit", headers=analyst_headers).status_code == 403


def test_admin_can_read_audit_log(client, admin_headers):
    assert client.get("/data/audit", headers=admin_headers).status_code == 200


def test_saved_query_and_monitor_lifecycle(client, analyst_headers):
    created = client.post(
        "/queries",
        headers=analyst_headers,
        json={
            "name": "Uji Monitor Shift",
            "query_text": "",
            "include_keywords": ["shift", "jam kerja"],
            "exclude_keywords": [],
            "job_roles": [],
            "topics": [],
            "sentiments": [],
            "intents": [],
        },
    )
    assert created.status_code == 201
    query_id = created.json()["id"]

    monitor = client.post(
        "/monitors",
        headers=analyst_headers,
        json={"name": "Monitor Shift", "source_query_id": query_id, "comparison_window": 7},
    )
    assert monitor.status_code == 201
    body = monitor.json()
    assert body["trend_direction"] in {"naik", "turun", "stabil", "tidak cukup data"}
    assert len(body["sparkline"]) == 7

    duplicated = client.post(
        f"/monitors/{body['id']}/duplicate", headers=analyst_headers
    )
    assert duplicated.status_code == 201
    assert duplicated.json()["name"].endswith("(salinan)")

    archived = client.patch(
        f"/monitors/{body['id']}", headers=analyst_headers, json={"is_archived": True}
    )
    assert archived.json()["is_archived"] is True
    listed = client.get("/monitors", headers=analyst_headers).json()
    assert body["id"] not in {m["id"] for m in listed}


def test_monitor_requires_valid_query(client, analyst_headers):
    response = client.post(
        "/monitors",
        headers=analyst_headers,
        json={"name": "Tanpa query", "source_query_id": "tidak-ada"},
    )
    assert response.status_code == 422


def test_insight_workflow_and_report_export(client, analyst_headers):
    suggestion = client.get(
        "/dashboard/insight-suggestions", headers=analyst_headers
    ).json()["suggestions"][0]

    insight = client.post(
        "/insights",
        headers=analyst_headers,
        json={
            "title": suggestion["title"],
            "summary": suggestion["summary"],
            "evidence_filters": suggestion["evidence_filters"],
            "metric_snapshot": suggestion["metric_snapshot"],
        },
    ).json()
    assert insight["human_status"] == "draft"
    assert insight["is_synthetic_data"] is True

    reviewed = client.patch(
        f"/insights/{insight['id']}",
        headers=analyst_headers,
        json={"human_status": "approved", "human_note": "Sudah diperiksa."},
    ).json()
    assert reviewed["human_status"] == "approved"

    end = datetime.utcnow()
    report = client.post(
        "/reports",
        headers=analyst_headers,
        json={
            "title": "Laporan Uji",
            "period_start": (end - timedelta(days=30)).isoformat(),
            "period_end": end.isoformat(),
            "insight_ids": [insight["id"]],
            "charts": ["volume", "topics", "sentiment"],
            "notes": "Catatan uji.",
        },
    )
    assert report.status_code == 201
    report_id = report.json()["id"]

    pdf = client.get(f"/reports/{report_id}/export", headers=analyst_headers, params={"format": "pdf"})
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")

    csv_export = client.get(
        f"/reports/{report_id}/export", headers=analyst_headers, params={"format": "csv"}
    )
    assert csv_export.status_code == 200
    text = csv_export.content.decode("utf-8-sig")
    assert "DATA SINTETIS — BUKAN TEMUAN AKTUAL" in text

    posts_export = client.get(
        f"/reports/{report_id}/export", headers=analyst_headers, params={"format": "posts"}
    )
    body = posts_export.content.decode("utf-8-sig")
    # Ekspor post-level dibatasi: hanya ID dan metadata minimum.
    assert "external_post_id" in body
    assert "text" not in body.split("\n")[2]


def test_report_rejects_unknown_insight(client, analyst_headers):
    end = datetime.utcnow()
    response = client.post(
        "/reports",
        headers=analyst_headers,
        json={
            "title": "Gagal",
            "period_start": (end - timedelta(days=7)).isoformat(),
            "period_end": end.isoformat(),
            "insight_ids": ["tidak-ada"],
        },
    )
    assert response.status_code == 422


def test_csv_import_validation(client, admin_headers):
    missing_columns = client.post(
        "/data/import", headers=admin_headers, files={"file": ("x.csv", b"a,b\n1,2", "text/csv")}
    )
    assert missing_columns.status_code == 422
    assert "Kolom wajib tidak ditemukan" in missing_columns.json()["detail"]

    payload = (
        "external_post_id,text,created_at_source,like_count\n"
        "uji_0001,berapa gaji staf gudang sekarang?,2026-08-01,4\n"
        "uji_0002,,2026-08-02,1\n"
        "uji_0003,tanggal salah,bukan-tanggal,1\n"
    ).encode()
    result = client.post(
        "/data/import", headers=admin_headers, files={"file": ("data.csv", payload, "text/csv")}
    ).json()
    assert result["records_processed"] == 1
    assert result["records_failed"] == 2
    assert result["status"] == "partial"


def test_import_requires_admin(client, analyst_headers):
    response = client.post(
        "/data/import",
        headers=analyst_headers,
        files={"file": ("x.csv", b"external_post_id,text,created_at_source\n", "text/csv")},
    )
    assert response.status_code == 403


def test_fetch_live_requires_admin(client, analyst_headers):
    response = client.post(
        "/data/fetch-live", params={"query": "loker gudang"}, headers=analyst_headers
    )
    assert response.status_code == 403


def test_fetch_live_rejected_without_credential(client, admin_headers):
    """Tanpa X_API_BEARER_TOKEN, mode live ditolak dengan pesan yang jelas."""
    response = client.post(
        "/data/fetch-live", params={"query": "loker gudang"}, headers=admin_headers
    )
    assert response.status_code == 409
    assert "X_API_BEARER_TOKEN" in response.json()["detail"]


def test_fetch_live_ingests_real_posts(client, admin_headers, db, monkeypatch):
    """Post dari connector resmi masuk lewat pipeline yang sama dan bukan sintetis."""
    from sqlalchemy import select

    from app.connectors.base import RawPost
    from app.connectors.official_x import OfficialXApiConnector
    from app.models import Post

    sample = [
        RawPost(
            external_post_id="live-uji-0001",
            text="berapa gaji staf gudang di kawasan industri sekarang?",
            created_at_source=datetime.utcnow() - timedelta(days=1),
            language="id",
            like_count=5,
            repost_count=1,
            is_synthetic=False,
            source="x_api",
        )
    ]
    monkeypatch.setattr(
        OfficialXApiConnector, "is_available", property(lambda self: True)
    )
    monkeypatch.setattr(OfficialXApiConnector, "fetch", lambda self, **kwargs: sample)

    try:
        result = client.post(
            "/data/fetch-live",
            params={"query": "gaji gudang", "days": 7},
            headers=admin_headers,
        )
        assert result.status_code == 200, result.text
        assert result.json()["records_processed"] == 1

        post = db.scalar(
            select(Post).where(Post.external_post_id == "live-uji-0001")
        )
        assert post is not None
        assert post.is_synthetic is False
        assert post.source == "x_api"
        assert post.analysis is not None  # pipeline NLP tetap dijalankan

        runs = client.get("/data/runs", headers=admin_headers).json()
        assert any(run["source"] == "x_api" for run in runs)

        audit = client.get("/data/audit", headers=admin_headers).json()["items"]
        assert any(entry["action"] == "data.fetch_live" for entry in audit)
    finally:
        # Korpus uji dikembalikan agar pengujian lain tidak terpengaruh.
        stale = db.scalar(select(Post).where(Post.external_post_id == "live-uji-0001"))
        if stale is not None:
            db.delete(stale)
            db.commit()


def test_label_correction_marks_manual_review(client, admin_headers, analyst_headers):
    post = client.get("/posts", headers=analyst_headers, params={"page_size": 5}).json()["items"][0]
    response = client.patch(
        f"/posts/{post['id']}/labels",
        headers=admin_headers,
        json={"sentiment_label": "Netral", "topic_slug": "gaji-benefit"},
    )
    assert response.status_code == 200

    updated = client.get(f"/posts/{post['id']}", headers=analyst_headers).json()
    assert updated["sentiment_label"] == "Netral"
    assert updated["topic_slug"] == "gaji-benefit"
    assert updated["sentiment_confidence"] == 1.0
    assert "koreksi-manual" in updated["model_version"]


def test_label_correction_rejects_unknown_topic(client, admin_headers, analyst_headers):
    post = client.get("/posts", headers=analyst_headers, params={"page_size": 5}).json()["items"][0]
    response = client.patch(
        f"/posts/{post['id']}/labels", headers=admin_headers, json={"topic_slug": "tidak-ada"}
    )
    assert response.status_code == 422


def test_methodology_exposes_limitations(client):
    body = client.get("/methodology").json()
    assert body["is_synthetic"] is True
    assert len(body["limitations"]) >= 5
    assert any("tidak berafiliasi resmi" in item for item in body["ethics"])


def test_connectors_never_expose_credentials(client, analyst_headers, monkeypatch):
    """Nilai credential tidak boleh bocor ke response, bahkan saat mode live."""
    from app.config import settings

    body = client.get("/data/connectors", headers=analyst_headers).json()
    assert body["mode"] == "demo"
    assert body["live_available"] is False

    sentinel = "RAHASIA-TOKEN-JANGAN-BOCOR"
    monkeypatch.setattr(settings, "x_api_bearer_token", sentinel)
    live_body = client.get("/data/connectors", headers=analyst_headers).json()
    assert sentinel not in str(live_body)
    assert live_body["live_available"] is True


def test_data_quality_reports_synthetic_share(client, analyst_headers):
    body = client.get("/data/quality", headers=analyst_headers).json()
    assert body["total_posts"] > 0
    assert body["coverage_percent"] == 100.0
    assert body["synthetic_percent"] > 0


def test_usability_event_logging_is_privacy_preserving(client, analyst_headers, admin_headers):
    response = client.post(
        "/usability/events",
        headers=analyst_headers,
        json={
            "session_key": "sesi-uji-1",
            "task_code": "T1",
            "event_type": "task_complete",
            "step_count": 6,
            "duration_ms": 45000,
            "filter_keys": ["job_roles", "topics"],
        },
    )
    assert response.status_code == 201
    summary = client.get("/usability/summary", headers=admin_headers).json()
    assert any(item["task_code"] == "T1" for item in summary["items"])
