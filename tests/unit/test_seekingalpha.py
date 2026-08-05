from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.config import Settings
from papertrader.queue import RunBudget, claim_next, prepare_queue
from papertrader.research import record_source
from papertrader.seekingalpha import (
    SeekingAlphaError,
    canonical_article_url,
    enqueue_seekingalpha_leads,
    schedule_seekingalpha_discovery,
    seekingalpha_dedupe_key,
    seekingalpha_source_id,
)
from papertrader.tables import append_unique, read_table, write_table

NOW = datetime(2026, 7, 29, 15, tzinfo=UTC)


def _claim_discovery(repository: Path, settings: Settings, *, run_id: str) -> str:
    prepare_queue(repository, now=NOW)
    operation = claim_next(
        repository,
        settings,
        run_id=run_id,
        budget=RunBudget.from_settings(settings),
        now=NOW,
    )
    assert operation is not None
    assert operation.operation_type == "source_discovery"
    return operation.operation_id


def _discovery_document(
    operation_id: str,
    *,
    run_id: str,
    content_kind: str = "analysis",
    article_id: str = "4904319",
    related_entity_ids: list[str] | None = None,
) -> dict[str, object]:
    section = "article" if content_kind == "analysis" else "news"
    return {
        "seekingalpha_discovery_version": 1,
        "run_id": run_id,
        "operation_id": operation_id,
        "discovery_date": "2026-07-29",
        "discovered_at": "2026-07-29T15:05:00Z",
        "status": "succeeded",
        "reason_code": "",
        "access_mode": "search_index",
        "direct_site_access": False,
        "attempt_count": 1,
        "candidate_counts": {"analysis": 1, "news": int(content_kind == "news")},
        "search_queries": [
            {
                "attempt": 1,
                "provider": "bundled_web_search",
                "query": "site:seekingalpha.com/trending-analysis current",
                "result_count": 1,
            }
        ],
        "selected": [
            {
                "content_kind": content_kind,
                "article_id": article_id,
                "title": "A material indexed investment lead",
                "canonical_url": (
                    f"https://seekingalpha.com/{section}/{article_id}-material-indexed-lead"
                ),
                "author": "Example Analyst",
                "published_at": "2026-07-29T12:00:00Z",
                "rank": 1,
                "summary_hash": "a" * 64,
                "related_entity_ids": related_entity_ids or [],
                "lead_reason": "The indexed metadata presents a testable causal hypothesis.",
            }
        ],
        "rejected": [],
    }


def test_canonical_seekingalpha_article_identities() -> None:
    assert canonical_article_url(
        "https://www.seekingalpha.com/article/4904319-material-indexed-lead"
    ) == (
        "analysis",
        "4904319",
        "https://seekingalpha.com/article/4904319-material-indexed-lead",
    )
    assert seekingalpha_source_id("news", "4592633") == "seekingalpha_news_4592633"
    assert seekingalpha_dedupe_key("analysis", "4904319") == (
        "wiki_ingest:seekingalpha:analysis:4904319:v1"
    )
    with pytest.raises(SeekingAlphaError, match="invalid Seeking Alpha canonical URL"):
        canonical_article_url("http://seekingalpha.com/article/4904319-test")
    with pytest.raises(SeekingAlphaError, match="article path"):
        canonical_article_url("https://seekingalpha.com/trending-analysis")


def test_daily_schedule_is_expiring_idempotent_and_network_free(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    first = schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id="daily-source-run",
        now=NOW,
    )

    assert first["status"] == "queued"
    assert first["operation_created"] is True
    rows = read_table(sandbox_repository, "operations_todo")
    assert len(rows) == 1
    assert rows[0]["operation_type"] == "source_discovery"
    assert rows[0]["priority"] == "69"
    assert rows[0]["deadline"] == "2026-07-30T00:00:00Z"
    payload = json.loads((sandbox_repository / rows[0]["payload_path"]).read_text(encoding="utf-8"))
    assert payload["inputs"]["direct_site_access_allowed"] is False
    assert payload["inputs"]["maximum_leads"] == 5

    duplicate = schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id="daily-source-rerun",
        now=NOW,
    )
    assert duplicate["status"] == "duplicate"
    assert duplicate["operation_id"] == first["operation_id"]
    assert read_table(sandbox_repository, "operations_todo") == rows


def test_existing_schedule_manifest_returns_successful_skip_without_mutation(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    run_id = "daily-source-repeat"
    first = schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        now=NOW,
    )
    manifest_path = sandbox_repository / "data" / "runs" / run_id / "seekingalpha_schedule.json"
    manifest_before = manifest_path.read_bytes()
    operations_before = read_table(sandbox_repository, "operations_todo")

    repeated = schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        now=datetime(2026, 7, 29, 16, tzinfo=UTC),
    )

    assert repeated == {
        "seekingalpha_schedule_version": 1,
        "run_id": run_id,
        "status": "skipped",
        "reason": "manifest_already_exists",
        "existing_manifest_status": first["status"],
        "manifest_path": f"data/runs/{run_id}/seekingalpha_schedule.json",
        "operation_id": first["operation_id"],
        "operation_created": False,
    }
    assert manifest_path.read_bytes() == manifest_before
    assert read_table(sandbox_repository, "operations_todo") == operations_before


def test_dry_schedule_writes_only_a_run_artifact(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    result = schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id="source-dry-run",
        dry_run=True,
        now=NOW,
    )

    assert result["status"] == "dry_run"
    assert read_table(sandbox_repository, "operations_todo") == []


def test_discovery_enqueues_a_closed_analysis_payload_and_second_call_is_a_noop(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    run_id = "daily-source-run"
    schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        now=NOW,
    )
    operation_id = _claim_discovery(sandbox_repository, sandbox_settings, run_id=run_id)
    document = _discovery_document(operation_id, run_id=run_id)

    first = enqueue_seekingalpha_leads(
        sandbox_repository,
        sandbox_settings,
        document,
        now=NOW,
    )
    assert first["operation_count"] == 1
    lead_row = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_type"] == "wiki_ingest"
    )
    assert lead_row["priority"] == "67"
    assert lead_row["depends_on"] == operation_id
    payload = json.loads(
        (sandbox_repository / lead_row["payload_path"]).read_text(encoding="utf-8")
    )
    assert payload["inputs"]["source_kind"] == "seekingalpha_search_lead"
    assert payload["inputs"]["metadata_hash"] != payload["inputs"]["summary_hash"]
    assert "summary" not in payload["inputs"]
    assert payload["inputs"]["direct_site_access_allowed"] is False

    second = enqueue_seekingalpha_leads(
        sandbox_repository,
        sandbox_settings,
        document,
        now=NOW,
    )
    assert second["operation_count"] == 0
    assert second["duplicate_source_ids"] == ["seekingalpha_analysis_4904319"]


@pytest.mark.parametrize(
    "terminal_status", ["succeeded", "skipped", "failed", "cancelled", "expired"]
)
def test_article_is_never_requeued_after_any_terminal_history_status(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    terminal_status: str,
) -> None:
    run_id = "daily-source-run"
    schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        now=NOW,
    )
    operation_id = _claim_discovery(sandbox_repository, sandbox_settings, run_id=run_id)
    document = _discovery_document(operation_id, run_id=run_id)
    enqueue_seekingalpha_leads(
        sandbox_repository,
        sandbox_settings,
        document,
        now=NOW,
    )
    rows = read_table(sandbox_repository, "operations_todo")
    lead = next(row for row in rows if row["operation_type"] == "wiki_ingest")
    history = lead | {
        "terminal_status": terminal_status,
        "completed_at": "2026-07-29T15:10:00Z",
        "result_path": "",
        "result_summary": "Synthetic exact-once fixture",
        "terminal_reason": "fixture",
    }
    append_unique(
        sandbox_repository,
        "operations_history",
        [history],
        key_columns=("operation_id",),
    )
    write_table(
        sandbox_repository,
        "operations_todo",
        [row for row in rows if row["operation_id"] != lead["operation_id"]],
    )

    repeated = enqueue_seekingalpha_leads(
        sandbox_repository,
        sandbox_settings,
        document,
        now=NOW,
    )
    assert repeated["operation_count"] == 0
    assert repeated["duplicate_source_ids"] == ["seekingalpha_analysis_4904319"]


def test_news_requires_an_existing_related_entity(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    run_id = "daily-source-run"
    schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        now=NOW,
    )
    operation_id = _claim_discovery(sandbox_repository, sandbox_settings, run_id=run_id)
    document = _discovery_document(
        operation_id,
        run_id=run_id,
        content_kind="news",
        article_id="4592633",
    )

    with pytest.raises(SeekingAlphaError, match="require an existing related entity"):
        enqueue_seekingalpha_leads(
            sandbox_repository,
            sandbox_settings,
            document,
            now=NOW,
        )


def test_registered_source_is_never_requeued(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    run_id = "daily-source-run"
    schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        now=NOW,
    )
    operation_id = _claim_discovery(sandbox_repository, sandbox_settings, run_id=run_id)
    document = _discovery_document(operation_id, run_id=run_id)
    canonical_url = "https://seekingalpha.com/article/4904319-an-earlier-indexed-slug"
    record_source(
        sandbox_repository,
        {
            "source_id": "seekingalpha_analysis_4904319",
            "url": canonical_url,
            "canonical_url": canonical_url,
            "source_type": "seekingalpha_search_lead",
            "title": "Previously registered indexed lead",
            "publisher": "Seeking Alpha",
            "license": "copyrighted-article-not-retrieved",
            "status": "available",
            "content_hash": "c" * 64,
            "related_entity_ids": "",
            "checked_at": "2026-07-29T15:00:00Z",
            "http_status": "",
            "changed": "true",
            "excerpt": "",
            "summary": "Previously reviewed search-index lead.",
            "run_id": run_id,
        },
        now=NOW,
    )

    result = enqueue_seekingalpha_leads(
        sandbox_repository,
        sandbox_settings,
        document,
        now=NOW,
    )
    assert result["operation_count"] == 0
    assert result["duplicate_source_ids"] == ["seekingalpha_analysis_4904319"]


def test_manifest_rejects_mismatched_kind_id_and_url(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    run_id = "daily-source-run"
    schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        now=NOW,
    )
    operation_id = _claim_discovery(sandbox_repository, sandbox_settings, run_id=run_id)
    document = _discovery_document(operation_id, run_id=run_id)
    selected = document["selected"]
    assert isinstance(selected, list) and isinstance(selected[0], dict)
    selected[0]["canonical_url"] = "https://seekingalpha.com/news/4904319-wrong-kind"

    with pytest.raises(SeekingAlphaError, match="URL, kind, and article ID do not match"):
        enqueue_seekingalpha_leads(
            sandbox_repository,
            sandbox_settings,
            document,
            now=NOW,
        )


def test_manifest_rejects_raw_summary_content(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    run_id = "daily-source-run"
    schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        now=NOW,
    )
    operation_id = _claim_discovery(sandbox_repository, sandbox_settings, run_id=run_id)
    document = _discovery_document(operation_id, run_id=run_id)
    selected = document["selected"]
    assert isinstance(selected, list) and isinstance(selected[0], dict)
    selected[0]["summary"] = "This text must never be persisted."

    with pytest.raises(SeekingAlphaError, match="invalid Seeking Alpha discovery manifest"):
        enqueue_seekingalpha_leads(
            sandbox_repository,
            sandbox_settings,
            document,
            now=NOW,
        )
