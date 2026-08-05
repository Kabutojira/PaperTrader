from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from papertrader.advice import refresh_advice
from papertrader.config import Settings
from papertrader.execution import ensure_initial_capital
from papertrader.integrity import (
    load_csv_contracts,
    prepared_daily_cycle_for_github_run,
    publication_requires_current_state,
    validate_daily_run_artifacts,
    validate_integrity,
    validate_skills,
)
from papertrader.issues import record_issue
from papertrader.tables import read_csv


def test_clean_scaffold_passes_integrity(
    sandbox_repository: Path,
) -> None:
    environment = {
        "WIKI_PATH": str((sandbox_repository / "data" / "wiki").resolve()),
    }
    assert validate_integrity(sandbox_repository, environment) == []


def test_all_project_skills_are_discoverable(repository_root: Path) -> None:
    assert validate_skills(repository_root) == []


def test_prepared_agent_operation_defers_publication_freshness_until_finalization(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    paper_environment: dict[str, str],
) -> None:
    now = datetime(2026, 7, 27, 12, tzinfo=UTC)
    run_id = "prepared-publication-fixture"
    operation_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    ensure_initial_capital(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        occurred_at=now - timedelta(hours=1),
    )
    refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        as_of=now,
        render_pages=False,
    )
    record_issue(
        sandbox_repository,
        severity="warning",
        title="Research input changed during the prepared run",
        description="A canonical input advanced after the previous publication snapshot.",
        owner="deterministic-controller",
        related_run_id=run_id,
        now=now + timedelta(minutes=1),
    )
    assert "published decision snapshot does not match current authoritative state" in (
        validate_integrity(sandbox_repository, paper_environment)
    )

    run_directory = sandbox_repository / "data" / "runs" / run_id
    (run_directory / operation_id).mkdir()
    (run_directory / "daily_run.json").write_text(
        json.dumps(
            {
                "daily_run_version": 1,
                "run_id": run_id,
                "trigger": "local",
                "source_sha": "a" * 40,
                "status": "prepared",
                "started_at": now.isoformat().replace("+00:00", "Z"),
                "completed_at": "",
                "preparation_errors": [],
                "queue_dispositions": [],
                "operation_count": 0,
                "model_budget_limit": "5",
                "model_budget_used": "0",
                "fill_outcomes": [],
                "report_path": "",
                "snapshot_id": "",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    controller_environment = {
        **paper_environment,
        "WIKI_PATH": str((sandbox_repository / "data" / "wiki").resolve()),
    }
    assert not publication_requires_current_state(
        sandbox_repository,
        controller_environment,
        prepared_daily_cycle_id=run_id,
    )
    assert (
        validate_integrity(
            sandbox_repository,
            controller_environment,
            require_current_publication=publication_requires_current_state(
                sandbox_repository,
                controller_environment,
                prepared_daily_cycle_id=run_id,
            ),
        )
        == []
    )

    operation_environment = {
        **controller_environment,
        "PAPERTRADER_AUDIT_RUN_ID": run_id,
        "PAPERTRADER_AUDIT_OPERATION_ID": operation_id,
    }

    assert validate_integrity(sandbox_repository, operation_environment) == []


def test_github_rerun_resolves_its_unique_unfinalized_daily_cycle(
    sandbox_repository: Path,
) -> None:
    run_id = "daily-20260805T065913Z"
    github_run_id = "30982821493"
    run_directory = sandbox_repository / "data" / "runs" / run_id
    run_directory.mkdir()
    manifest_path = run_directory / "daily_run.json"
    manifest = {
        "daily_run_version": 2,
        "run_id": run_id,
        "daily_cycle_id": run_id,
        "originating_github_run_id": github_run_id,
        "status": "running",
        "finalization_at": "",
    }
    manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

    assert prepared_daily_cycle_for_github_run(sandbox_repository, github_run_id) == run_id
    assert prepared_daily_cycle_for_github_run(sandbox_repository, "not-a-run-id") == ""

    manifest["finalization_at"] = "2026-08-05T08:00:00Z"
    manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
    assert prepared_daily_cycle_for_github_run(sandbox_repository, github_run_id) == ""


def test_latest_completed_run_owns_shared_canonical_daily_report(
    sandbox_repository: Path,
) -> None:
    report_path = "data/wiki/daily-reports/daily-report_20260727.md"
    report = sandbox_repository / report_path
    report.write_text('---\nsnapshot_id: "decision_22222222222222222222"\n---\n', encoding="utf-8")
    for index, (run_id, completed_at, snapshot_id) in enumerate(
        (
            ("same-day-early", "2026-07-27T10:00:00Z", "decision_11111111111111111111"),
            ("same-day-latest", "2026-07-27T12:00:00Z", "decision_22222222222222222222"),
        )
    ):
        run_directory = sandbox_repository / "data" / "runs" / run_id
        run_directory.mkdir()
        (run_directory / "daily_run.json").write_text(
            json.dumps(
                {
                    "daily_run_version": 1,
                    "run_id": run_id,
                    "trigger": "local",
                    "source_sha": str(index + 1) * 40,
                    "status": "succeeded",
                    "started_at": "2026-07-27T09:00:00Z",
                    "completed_at": completed_at,
                    "preparation_errors": [],
                    "queue_dispositions": [],
                    "operation_count": 0,
                    "model_budget_limit": "5",
                    "model_budget_used": "0",
                    "fill_outcomes": [],
                    "report_path": report_path,
                    "snapshot_id": snapshot_id,
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (run_directory / "agent_batch.json").write_text(
            json.dumps(
                {
                    "agent_batch_version": 1,
                    "run_id": run_id,
                    "started_at": "2026-07-27T09:00:00Z",
                    "completed_at": completed_at,
                    "maximum_operations": 0,
                    "maximum_model_budget": "5",
                    "estimated_cost_per_operation": "1",
                    "operation_count": 0,
                    "estimated_model_budget_used": "0",
                    "outcomes": [],
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (run_directory / "decision_snapshot.json").write_text(
            json.dumps(
                {
                    "snapshot_id": snapshot_id,
                    "run_id": run_id,
                    "as_of": completed_at,
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    assert validate_daily_run_artifacts(sandbox_repository) == []

    report.write_text('---\nsnapshot_id: "decision_11111111111111111111"\n---\n', encoding="utf-8")
    assert "daily report snapshot identity mismatch: same-day-latest" in (
        validate_daily_run_artifacts(sandbox_repository)
    )


def test_sandbox_repository_excludes_mutable_runtime_state(sandbox_repository: Path) -> None:
    for contract in load_csv_contracts(sandbox_repository):
        path = sandbox_repository.joinpath(*contract.path.parts)
        assert read_csv(path, contract.columns) == []

    data = sandbox_repository / "data"
    assert list((data / "market" / "prices").glob("*.csv")) == []
    assert list((data / "logs").glob("operations-*.ndjson")) == []
    assert list((data / "runs").iterdir()) == []
    assert list((data / "wiki" / "daily-reports").iterdir()) == []
