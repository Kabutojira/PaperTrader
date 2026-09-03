from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.logs import record_completed_run
from papertrader.public_refs import PublicEntityResolver
from papertrader.tables import write_table
from papertrader.utils import CanonicalValueError


def test_humanize_resolves_prefixed_daily_run_id(sandbox_repository: Path) -> None:
    run_id = "local-daily-20260807T161139Z"
    report_path = "data/wiki/daily-reports/daily-report_20260807.md"
    run_directory = sandbox_repository / "data" / "runs" / run_id
    run_directory.mkdir(parents=True)
    (run_directory / "daily_run.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "completed_at": "2026-08-07T16:49:41Z",
                "report_path": report_path,
            }
        ),
        encoding="utf-8",
    )

    rendered = PublicEntityResolver(sandbox_repository).humanize(
        f"See data/runs/{run_id}/operation/agent_result.json."
    )

    assert run_id not in rendered
    assert "[[daily-reports/daily-report_20260807|Daily report for 2026-08-07]]" in rendered


def test_humanize_falls_back_to_completed_run_while_manifest_is_open(
    sandbox_repository: Path,
) -> None:
    run_id = "daily-20260808T155913Z"
    completed_at = datetime(2026, 8, 8, 15, 59, 13, tzinfo=UTC)
    run_directory = sandbox_repository / "data" / "runs" / run_id
    run_directory.mkdir(parents=True)
    (run_directory / "daily_run.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "completed_at": "",
                "research_cutoff_at": "",
                "report_path": "",
            }
        ),
        encoding="utf-8",
    )
    record_completed_run(
        sandbox_repository,
        run_id=run_id,
        started_at=datetime(2026, 8, 8, 13, 46, 54, tzinfo=UTC),
        completed_at=completed_at,
        status="degraded",
        trigger="workflow_dispatch",
        operation_count=3,
        model_budget_limit=Decimal("100"),
        model_budget_used=Decimal("15"),
    )

    rendered = PublicEntityResolver(sandbox_repository).humanize(
        f"Daily finalization issue for {run_id}."
    )

    assert run_id not in rendered
    assert "[[daily-reports/daily-report_20260808|Daily report for 2026-08-08]]" in rendered


def test_humanize_sanitizes_source_request_filename(sandbox_repository: Path) -> None:
    rendered = PublicEntityResolver(sandbox_repository).humanize(
        "data/runs/example/source_primary_filing_request.json"
    )

    assert rendered == "data/runs/example/recorded source.json"


def test_humanize_sanitizes_rejected_operation_without_weakening_explicit_resolution(
    sandbox_repository: Path,
) -> None:
    rejected_operation_id = "01M08H8C5RMJXFBKN97QDDMFRF"
    resolver = PublicEntityResolver(sandbox_repository)

    rendered = resolver.humanize(
        f"Rejected data/operations/payloads/{rejected_operation_id}.json during validation."
    )

    assert rejected_operation_id not in rendered
    assert "unaccepted operation" in rendered
    with pytest.raises(CanonicalValueError, match="required public operation reference"):
        resolver.markdown("operation", rejected_operation_id)


def test_humanize_sanitizes_rejected_signal_without_weakening_explicit_resolution(
    sandbox_repository: Path,
) -> None:
    rejected_signal_id = "signal_89444cee010c1a0e5ad2"
    resolver = PublicEntityResolver(sandbox_repository)

    rendered = resolver.humanize(f"Signal identity is invalid: {rejected_signal_id}.")

    assert rejected_signal_id not in rendered
    assert rendered == "Signal identity is invalid: unaccepted signal."
    with pytest.raises(CanonicalValueError, match="required public signal reference"):
        resolver.markdown("signal", rejected_signal_id)


def test_humanize_resolves_pending_strategy_operation_through_security(
    sandbox_repository: Path,
) -> None:
    operation_id = "01M14ZK4R0MKRN5KGFDGVXV3MB"
    security_id = "security_8b703a8adf5f864acaa4"
    strategy_id = "strategy_8caa208dfc702a2584a7"
    write_table(
        sandbox_repository,
        "securities",
        [
            {
                "security_id": security_id,
                "issuer_id": "issuer_prosus_fixture",
                "company_name": "Prosus N.V.",
                "instrument_name": "Prosus N.V. ordinary shares",
                "instrument_type": "equity",
                "ticker": "PRX",
                "exchange_code": "AMS",
                "venue_mic": "XAMS",
                "provider_symbol": "PRX.AS",
                "broker_symbol": "",
                "currency": "EUR",
                "country": "NL",
                "sector": "Communication Services",
                "industry": "Internet Content & Information",
                "status": "watching",
                "watchlist_reason": "Fixture.",
                "research_summary": "Fixture.",
                "research_page": "",
                "last_research_at": "",
                "next_review_at": "",
                "created_at": "2026-08-28T20:04:48Z",
                "updated_at": "2026-08-28T20:04:48Z",
                "source": "fixture",
            }
        ],
    )
    payload_path = f"data/operations/payloads/{operation_id}.json"
    payload = sandbox_repository / payload_path
    payload.parent.mkdir(parents=True, exist_ok=True)
    payload.write_text(
        json.dumps(
            {
                "operation_id": operation_id,
                "operation_type": "strategy_research",
                "entity_type": "strategy",
                "entity_id": strategy_id,
                "inputs": {"security_id": security_id, "strategy_id": strategy_id},
            }
        ),
        encoding="utf-8",
    )
    write_table(
        sandbox_repository,
        "operations_todo",
        [
            {
                "operation_id": operation_id,
                "created_at": "2026-08-28T20:04:48Z",
                "updated_at": "2026-08-28T20:04:48Z",
                "status": "ready",
                "priority": "55",
                "operation_type": "strategy_research",
                "entity_type": "strategy",
                "entity_id": strategy_id,
                "not_before": "",
                "deadline": "",
                "depends_on": "",
                "dedupe_key": "strategy-fixture",
                "freshness_days": "0",
                "skill_names": "llm-wiki|papertrader-strategy-research",
                "prompt": "Research the bounded baseline allocation target.",
                "payload_path": payload_path,
                "source": "fixture",
                "attempt_count": "0",
                "max_attempts": "3",
                "claimed_by_run_id": "",
                "lease_expires_at": "",
                "last_error": "",
            }
        ],
    )

    resolver = PublicEntityResolver(sandbox_repository)
    rendered = resolver.humanize(f"Queued {operation_id} after allocation planning.")
    direct_strategy = resolver.humanize(f"Pending {strategy_id} remains research-only.")

    assert operation_id not in rendered
    assert strategy_id not in rendered
    assert "Strategy research for strategy for PRX" in rendered
    assert "security-catalog#security-security_8b703a8adf5f864acaa4" in rendered
    assert strategy_id not in direct_strategy
    assert "strategy for PRX" in direct_strategy
    assert "security-catalog#security-security_8b703a8adf5f864acaa4" in direct_strategy
