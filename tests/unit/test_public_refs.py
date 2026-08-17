from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.logs import record_completed_run
from papertrader.public_refs import PublicEntityResolver
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
