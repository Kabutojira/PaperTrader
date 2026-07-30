from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from papertrader.config import Settings
from papertrader.research import (
    _migration_priority,
    assessment_by_id,
    migrate_legacy_assessments,
    security_research_context,
    upsert_assessment,
)
from papertrader.tables import contract_by_name, read_table, write_table

NOW = datetime(2026, 7, 24, 22, tzinfo=UTC)


def test_v2_backfill_priority_orders_exposure_near_miss_stale_and_watchlist() -> None:
    fresh = {"expires_at": "2026-08-24T22:00:00Z", "assessment_schema_version": "legacy_v1"}
    stale = {"expires_at": "2026-07-23T22:00:00Z", "assessment_schema_version": "legacy_v1"}
    positive_target = {"target_weight_pct": "5", "candidate_edge": "8", "rank": "1"}
    near_miss = {"target_weight_pct": "0", "candidate_edge": "7", "rank": "2"}
    assert (
        _migration_priority(
            "holding", fresh, holding_ids={"holding"}, pending_ids=set(), target=None, now=NOW
        )[0]
        == 96
    )
    assert (
        _migration_priority(
            "pending", fresh, holding_ids=set(), pending_ids={"pending"}, target=None, now=NOW
        )[0]
        == 94
    )
    assert (
        _migration_priority(
            "target", fresh, holding_ids=set(), pending_ids=set(), target=positive_target, now=NOW
        )[0]
        == 92
    )
    assert (
        _migration_priority(
            "near", fresh, holding_ids=set(), pending_ids=set(), target=near_miss, now=NOW
        )[0]
        == 88
    )
    assert (
        _migration_priority(
            "stale", stale, holding_ids=set(), pending_ids=set(), target=None, now=NOW
        )[0]
        == 84
    )
    assert (
        _migration_priority(
            "watch", fresh, holding_ids=set(), pending_ids=set(), target=None, now=NOW
        )[0]
        == 80
    )


def _security() -> dict[str, str]:
    return {
        "security_id": "sec_revision",
        "issuer_id": "issuer_revision",
        "company_name": "Revision Corp",
        "instrument_name": "Revision Corp common stock",
        "instrument_type": "equity",
        "ticker": "REV",
        "exchange_code": "XETR",
        "venue_mic": "XETR",
        "provider_symbol": "REV.DE",
        "broker_symbol": "",
        "currency": "EUR",
        "country": "DE",
        "sector": "Industrials",
        "industry": "Testing",
        "status": "watching",
        "watchlist_reason": "Revision fixture.",
        "research_summary": "Revision fixture.",
        "research_page": "data/wiki/securities/sec_revision.md",
        "last_research_at": "2026-07-24T21:00:00Z",
        "next_review_at": "2026-08-23T21:00:00Z",
        "created_at": "2026-07-20T00:00:00Z",
        "updated_at": "2026-07-24T21:00:00Z",
        "source": "fixture",
    }


def _source() -> dict[str, str]:
    return {
        "source_id": "source_revision",
        "url": "https://example.test/revision",
        "canonical_url": "https://example.test/revision",
        "source_type": "filing",
        "title": "Revision filing",
        "publisher": "Revision Corp",
        "license": "public-record",
        "status": "available",
        "content_hash": "ab" * 32,
        "first_seen_at": "2026-07-24T20:00:00Z",
        "last_checked_at": "2026-07-24T20:00:00Z",
        "last_changed_at": "2026-07-24T20:00:00Z",
        "related_entity_ids": "sec_revision",
    }


def _assessment(*, assessed_at: str, score: str) -> dict[str, str]:
    return {
        "security_id": "sec_revision",
        "assessed_at": assessed_at,
        "expires_at": "2026-08-23T21:00:00Z",
        "eligibility": "baseline",
        "confidence": "medium",
        "thesis_score": score,
        "business_quality_score": "70",
        "balance_sheet_score": "70",
        "valuation_score": "70",
        "timing_score": "70",
        "liquidity_score": "80",
        "risk_penalty": "5",
        "downside_pct": "-20",
        "base_upside_pct": "25",
        "valuation_horizon_months": "12",
        "hard_blockers": "",
        "soft_gaps": "confidence_medium",
        "evidence_refs": "source_revision",
        "run_id": "revision-run",
    }


def test_assessment_history_is_linked_retrievable_and_retry_idempotent(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    page = sandbox_repository / "data/wiki/securities/sec_revision.md"
    page.write_text("# Revision\n", encoding="utf-8")
    write_table(sandbox_repository, "securities", [_security()])
    write_table(sandbox_repository, "source_registry", [_source()])

    first = _assessment(assessed_at="2026-07-24T21:00:00Z", score="70")
    assert upsert_assessment(sandbox_repository, sandbox_settings, first, now=NOW)
    assert not upsert_assessment(sandbox_repository, sandbox_settings, first, now=NOW)
    history = read_table(sandbox_repository, "security_assessment_history")
    assert len(history) == 1
    assert history[0]["previous_assessment_id"] == ""
    assert assessment_by_id(sandbox_repository, history[0]["assessment_id"]) == history[0]

    page.write_text(
        "# Revision\n\n## Changes since prior review\n\nThe thesis improved.\n", encoding="utf-8"
    )
    second = _assessment(assessed_at="2026-07-24T21:30:00Z", score="80")
    assert upsert_assessment(sandbox_repository, sandbox_settings, second, now=NOW)
    history = read_table(sandbox_repository, "security_assessment_history")
    assert len(history) == 2
    assert history[1]["previous_assessment_id"] == history[0]["assessment_id"]
    context = security_research_context(sandbox_repository, "sec_revision")
    assert context["previous_assessment"] == history[0]
    assert context["current_history_version"] == history[1]
    assert context["previous_page_hash"] == history[1]["research_page_hash"]


def test_legacy_migration_archives_without_inventing_scenarios_and_queues_bounded_refresh(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    page = sandbox_repository / "data/wiki/securities/sec_revision.md"
    page.write_text("# Revision\n", encoding="utf-8")
    write_table(sandbox_repository, "securities", [_security()])
    write_table(sandbox_repository, "source_registry", [_source()])
    write_table(
        sandbox_repository,
        "security_assessments",
        [_assessment(assessed_at="2026-07-24T21:00:00Z", score="70")],
    )

    first = migrate_legacy_assessments(
        sandbox_repository,
        sandbox_settings,
        run_id="assessment-migration-test",
        enqueue_limit=1,
        now=NOW,
    )
    assert first.imported_history_rows == 1
    assert len(first.operations_created) == 1
    history = read_table(sandbox_repository, "security_assessment_history")
    assert history[0]["assessment_schema_version"] == "legacy_v1"
    assert history[0]["downside_pct"] == "-20"
    assert history[0]["base_upside_pct"] == "25"
    assert history[0]["bear_probability_pct"] == ""
    assert history[0]["bull_fair_value"] == ""
    assert history[0]["expected_return_pct"] == ""
    assert history[0]["canonical_rating"] == ""
    current_path = sandbox_repository / "data/tables/security_assessments.csv"
    assert current_path.read_text(encoding="utf-8").splitlines()[0].split(",") == list(
        contract_by_name(sandbox_repository, "security_assessments").columns
    )
    queued = read_table(sandbox_repository, "operations_todo")
    assert len(queued) == 1
    assert queued[0]["operation_type"] == "security_research"
    assert queued[0]["priority"] == "80"

    report_before = (sandbox_repository / first.report_path).read_bytes()
    second = migrate_legacy_assessments(
        sandbox_repository,
        sandbox_settings,
        run_id="assessment-migration-test",
        enqueue_limit=1,
        now=NOW,
    )
    assert second.imported_history_rows == 0
    assert second.existing_history_rows == 1
    assert second.operations_created == ()
    assert len(read_table(sandbox_repository, "security_assessment_history")) == 1
    assert (sandbox_repository / second.report_path).read_bytes() == report_before
