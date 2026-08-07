from __future__ import annotations

import json
from pathlib import Path

from papertrader.public_refs import PublicEntityResolver


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


def test_humanize_sanitizes_source_request_filename(sandbox_repository: Path) -> None:
    rendered = PublicEntityResolver(sandbox_repository).humanize(
        "data/runs/example/source_primary_filing_request.json"
    )

    assert rendered == "data/runs/example/recorded source.json"
