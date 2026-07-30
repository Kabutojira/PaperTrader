from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from papertrader.config import Settings
from papertrader.research import assessment_by_id, security_research_context, upsert_assessment
from papertrader.tables import read_table, write_table

NOW = datetime(2026, 7, 24, 22, tzinfo=UTC)


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
