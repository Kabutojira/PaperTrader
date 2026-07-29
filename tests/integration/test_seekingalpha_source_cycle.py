from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from papertrader.atomic_io import atomic_write_json, atomic_write_text
from papertrader.config import Settings
from papertrader.queue import Operation, RunBudget, claim_next, enqueue_operation, prepare_queue
from papertrader.reports import _seekingalpha_discovery_lines
from papertrader.research import import_watchlist, record_source
from papertrader.result_validator import (
    _seekingalpha_discovery_errors,
    _seekingalpha_wiki_ingest_errors,
)
from papertrader.seekingalpha import (
    enqueue_seekingalpha_leads,
    schedule_seekingalpha_discovery,
)
from papertrader.tables import read_table

NOW = datetime(2026, 7, 29, 15, tzinfo=UTC)
RUN_ID = "seekingalpha-integration-cycle"


def _security(*, company: str, ticker: str, provider_symbol: str) -> dict[str, str]:
    return {
        "company_name": company,
        "instrument_name": f"{company} common stock",
        "instrument_type": "equity",
        "ticker": ticker,
        "exchange_code": "XNAS",
        "venue_mic": "XNAS",
        "provider_symbol": provider_symbol,
        "currency": "USD",
        "country": "US",
        "sector": "Technology",
        "industry": "Research fixture",
    }


def test_seekingalpha_discovery_and_analysis_cycle_is_bounded_and_exact_once(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    existing = import_watchlist(
        sandbox_repository,
        sandbox_settings,
        {
            "watchlist_reason": "Existing identity for entity-linked news testing.",
            "source": "https://www.sec.gov/edgar/search/",
            "securities": [
                _security(
                    company="Existing News Corporation",
                    ticker="EXNC",
                    provider_symbol="EXNC",
                )
            ],
        },
        now=NOW,
    )
    existing_security_id = existing["created_security_ids"][0]
    schedule = schedule_seekingalpha_discovery(
        sandbox_repository,
        sandbox_settings,
        run_id=RUN_ID,
        now=NOW,
    )
    assert schedule["operation_created"] is True
    prepare_queue(sandbox_repository, now=NOW)
    discovery_operation = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id=RUN_ID,
        budget=RunBudget.from_settings(sandbox_settings),
        now=NOW,
    )
    assert discovery_operation is not None
    assert discovery_operation.operation_type == "source_discovery"

    discovery = {
        "seekingalpha_discovery_version": 1,
        "run_id": RUN_ID,
        "operation_id": discovery_operation.operation_id,
        "discovery_date": "2026-07-29",
        "discovered_at": "2026-07-29T15:05:00Z",
        "status": "succeeded",
        "reason_code": "",
        "access_mode": "search_index",
        "direct_site_access": False,
        "attempt_count": 1,
        "candidate_counts": {"analysis": 1, "news": 1},
        "search_queries": [
            {
                "attempt": 1,
                "provider": "bundled_web_search",
                "query": "site:seekingalpha.com current analysis and market news",
                "result_count": 2,
            }
        ],
        "selected": [
            {
                "content_kind": "analysis",
                "article_id": "4904319",
                "title": "Indexed analysis with a testable causal mechanism",
                "canonical_url": (
                    "https://seekingalpha.com/article/4904319-indexed-causal-analysis"
                ),
                "author": "Example Analyst",
                "published_at": "2026-07-29T12:00:00Z",
                "rank": 1,
                "summary_hash": "a" * 64,
                "related_entity_ids": [],
                "lead_reason": "The metadata supports bounded primary-source research.",
            },
            {
                "content_kind": "news",
                "article_id": "4592633",
                "title": "Indexed news material to an existing watched security",
                "canonical_url": "https://seekingalpha.com/news/4592633-indexed-news",
                "author": "",
                "published_at": "2026-07-29T13:00:00Z",
                "rank": 1,
                "summary_hash": "b" * 64,
                "related_entity_ids": [existing_security_id],
                "lead_reason": "The metadata maps to a maintained security identity.",
            },
        ],
        "rejected": [],
    }
    discovery_relative = (
        f"data/runs/{RUN_ID}/{discovery_operation.operation_id}/seekingalpha_discovery.json"
    )
    (sandbox_repository / discovery_relative).parent.mkdir(parents=True)
    atomic_write_json(
        sandbox_repository / discovery_relative,
        discovery,
        allowed_root=sandbox_repository,
    )
    before_ids = {row["operation_id"] for row in read_table(sandbox_repository, "operations_todo")}
    queued = enqueue_seekingalpha_leads(
        sandbox_repository,
        sandbox_settings,
        discovery,
        now=NOW,
    )
    assert queued["operation_count"] == 2
    rows_after_discovery = {
        row["operation_id"]: row for row in read_table(sandbox_repository, "operations_todo")
    }
    created_leads = set(rows_after_discovery) - before_ids
    assert created_leads == set(queued["operation_ids"])
    assert (
        _seekingalpha_discovery_errors(
            sandbox_repository,
            run_id=RUN_ID,
            operation=discovery_operation,
            status="succeeded",
            result={"status": "succeeded"},
            changed_paths=(discovery_relative,),
            created_operation_ids=created_leads,
            operation_rows_after=rows_after_discovery,
            analysis_priority=67,
            news_priority=66,
        )
        == []
    )
    report_lines = _seekingalpha_discovery_lines(sandbox_repository, RUN_ID)
    assert "### Seeking Alpha search-index leads" in report_lines
    assert "- Interesting leads selected: `2`; rejected: `0`" in report_lines

    analysis_row = next(
        row
        for row in rows_after_discovery.values()
        if row["entity_id"] == "seekingalpha_analysis_4904319"
    )
    analysis_operation = Operation.from_row(analysis_row)
    payload = json.loads(
        (sandbox_repository / analysis_operation.payload_path).read_text(encoding="utf-8")
    )
    inputs = payload["inputs"]
    source_history_id, changed = record_source(
        sandbox_repository,
        {
            "source_id": inputs["source_id"],
            "url": inputs["canonical_url"],
            "canonical_url": inputs["canonical_url"],
            "source_type": "seekingalpha_search_lead",
            "title": inputs["title"],
            "publisher": "Seeking Alpha",
            "license": "copyrighted-article-not-retrieved",
            "status": "available",
            "content_hash": inputs["metadata_hash"],
            "related_entity_ids": "",
            "checked_at": "2026-07-29T15:10:00Z",
            "http_status": "",
            "changed": "true",
            "excerpt": "",
            "summary": "Indexed lead corroborated independently with primary sources.",
            "run_id": RUN_ID,
        },
        now=NOW,
    )
    assert changed and source_history_id
    imported = import_watchlist(
        sandbox_repository,
        sandbox_settings,
        {
            "watchlist_reason": "Primary-source checks retained this indexed causal lead.",
            "source": inputs["canonical_url"],
            "securities": [
                _security(
                    company="Verified Analysis Corporation",
                    ticker="VANC",
                    provider_symbol="VANC",
                )
            ],
        },
        now=NOW,
    )
    imported_security_id = imported["created_security_ids"][0]
    before_followups = set(rows_after_discovery)
    followup_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="security_research",
        entity_type="security",
        entity_id=imported_security_id,
        dedupe_key=f"security_research:{imported_security_id}:seekingalpha:4904319",
        prompt="Verify and value one identity-resolved search-index lead.",
        inputs={"security_id": imported_security_id},
        source=f"seekingalpha_ingest:{analysis_operation.operation_id}",
        priority=68,
        depends_on=(analysis_operation.operation_id,),
        source_refs=(inputs["canonical_url"], "https://www.sec.gov/edgar/search/"),
        now=NOW,
    )
    assert created
    analysis_relative = (
        f"data/runs/{RUN_ID}/{analysis_operation.operation_id}/seekingalpha_analysis.md"
    )
    (sandbox_repository / analysis_relative).parent.mkdir(parents=True)
    atomic_write_text(
        sandbox_repository / analysis_relative,
        (
            "# Seeking Alpha search-index lead analysis\n\n"
            f"Article ID: `{inputs['article_id']}`\n\n"
            f"Canonical URL: {inputs['canonical_url']}\n\n"
            f"Metadata SHA-256: `{inputs['metadata_hash']}`\n\n"
            "No article body was retrieved. Current primary sources independently supported one "
            "identity-only security lead; no strategy, signal, allocation, or order changed.\n"
        ),
        allowed_root=sandbox_repository,
    )
    rows_after_ingest = {
        row["operation_id"]: row for row in read_table(sandbox_repository, "operations_todo")
    }
    created_followups = set(rows_after_ingest) - before_followups
    assert created_followups == {followup_id}
    changed_paths = (
        analysis_relative,
        f"data/operations/payloads/{followup_id}.json",
        "data/operations/operations_TODO.csv",
        "data/tables/securities.csv",
        "data/tables/source_history.csv",
        "data/tables/source_registry.csv",
    )
    assert (
        _seekingalpha_wiki_ingest_errors(
            sandbox_repository,
            run_id=RUN_ID,
            operation=analysis_operation,
            status="succeeded",
            result={"status": "succeeded"},
            changed_paths=changed_paths,
            created_paths={analysis_relative, f"data/operations/payloads/{followup_id}.json"},
            created_operation_ids=created_followups,
            operation_rows_after=rows_after_ingest,
            followup_priority=68,
            maximum_new_securities=2,
        )
        == []
    )
    assert read_table(sandbox_repository, "strategies") == []
    assert read_table(sandbox_repository, "signals") == []
    assert read_table(sandbox_repository, "orders") == []

    repeated = enqueue_seekingalpha_leads(
        sandbox_repository,
        sandbox_settings,
        discovery,
        now=NOW,
    )
    assert repeated["operation_count"] == 0
    assert repeated["duplicate_source_ids"] == [
        "seekingalpha_analysis_4904319",
        "seekingalpha_news_4592633",
    ]
