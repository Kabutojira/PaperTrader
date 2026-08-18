from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.agent_runner import AgentRunError
from papertrader.config import Settings
from papertrader.daily import prepare_daily_run, record_local_agent_outcome
from papertrader.local_harness import (
    finish_local_harness_operation,
    start_local_harness_operation,
)
from papertrader.queue import enqueue_operation
from papertrader.tables import read_table

NOW = datetime(2026, 7, 25, 8, tzinfo=UTC)


def _enqueue_opportunity(repository: Path, settings: Settings) -> str:
    operation_id, created = enqueue_operation(
        repository,
        settings,
        operation_type="opportunity_research",
        entity_type="opportunity",
        entity_id="opp-local-harness",
        dedupe_key="opportunity_research:opp-local-harness:fixture:2026-07-25",
        prompt="Assess one local harness opportunity.",
        inputs={
            "security_id": "security_fixture",
            "trigger_type": "manual_review",
            "market_data_as_of": "2026-07-25T09:00:00Z",
            "period_start": "2026-07-01",
            "period_end": "2026-07-25",
        },
        source="test",
        now=NOW,
    )
    assert created
    return operation_id


def _result(operation_id: str, *, files_changed: list[str] | None = None) -> dict[str, object]:
    return {
        "operation_id": operation_id,
        "status": "skipped",
        "summary": "The fixture provides no evidence for a follow-up.",
        "evidence": [
            {
                "source": "local harness fixture",
                "claim": "No material transition was present in the bounded fixture.",
                "observed_at": "2026-07-25T09:00:00Z",
            }
        ],
        "files_changed": files_changed or [],
        "operations_created": [],
        "issues_recorded": [],
        "daily_report_items": [],
        "commands_run": [],
        "validation": {"passed": True, "checks": ["bounded fixture reviewed"]},
    }


def test_local_harness_claims_validates_and_terminalizes_one_operation(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    operation_id = _enqueue_opportunity(sandbox_repository, sandbox_settings)
    started = start_local_harness_operation(
        sandbox_repository,
        sandbox_settings,
        run_id="local-codex-1",
        operation_id=operation_id,
    )

    assert started is not None
    assert started.operation_id == operation_id
    prompt = (sandbox_repository / started.controller_prompt_path).read_text(encoding="utf-8")
    assert "skills/papertrader-controller/SKILL.md" in prompt
    assert "skills/papertrader-opportunity-research/SKILL.md" in prompt
    assert "already started and claimed this operation" in prompt
    assert "Do not run agent harness start" in prompt
    assert "Do not run agent harness finish" in prompt
    assert "PAPERTRADER_AUDIT_RUN_ID=local-codex-1" in prompt
    assert f"PAPERTRADER_AUDIT_OPERATION_ID={operation_id}" in prompt
    assert "PAPERTRADER_AUDIT_OPERATION_TYPE=opportunity_research" in prompt
    assert "scripts/papertrader" in prompt
    assert "stop after agent_result.json exists" in prompt

    result_path = sandbox_repository / started.result_path
    result_path.write_text(json.dumps(_result(operation_id)), encoding="utf-8")
    finished = finish_local_harness_operation(
        sandbox_repository,
        run_id="local-codex-1",
        operation_id=operation_id,
    )

    assert finished.status == "skipped"
    assert finished.changed_paths == ()
    assert read_table(sandbox_repository, "operations_todo") == []
    history = read_table(sandbox_repository, "operations_history")
    assert history[0]["operation_id"] == operation_id
    assert history[0]["terminal_status"] == "skipped"
    validation = json.loads(
        (sandbox_repository / finished.validation_path).read_text(encoding="utf-8")
    )
    assert validation["passed"] is True
    assert validation["harness"] == "local"


def test_local_harness_allows_audited_read_only_queue_validation(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    operation_id = _enqueue_opportunity(sandbox_repository, sandbox_settings)
    started = start_local_harness_operation(
        sandbox_repository,
        sandbox_settings,
        run_id="local-codex-queue-validation",
        operation_id=operation_id,
    )
    assert started is not None
    environment = dict(os.environ)
    environment.update(
        {
            "PAPERTRADER_AUDIT_RUN_ID": started.run_id,
            "PAPERTRADER_AUDIT_OPERATION_ID": started.operation_id,
            "PAPERTRADER_AUDIT_PATH": started.audit_path,
            "WIKI_PATH": str(sandbox_repository / "data" / "wiki"),
        }
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "papertrader",
            "--repository",
            str(sandbox_repository),
            "queue",
            "validate",
        ],
        cwd=sandbox_repository,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "OK [queue]"

    result = _result(operation_id)
    audit = json.loads((sandbox_repository / started.audit_path).read_text(encoding="utf-8"))
    (sandbox_repository / started.result_path).write_text(json.dumps(result), encoding="utf-8")
    finished = finish_local_harness_operation(
        sandbox_repository,
        run_id=started.run_id,
        operation_id=operation_id,
    )

    assert finished.status == "skipped"
    canonical = json.loads((sandbox_repository / started.result_path).read_text(encoding="utf-8"))
    assert canonical["commands_run"] == [audit["entries"][0]["command"]]


@pytest.mark.parametrize("artifact_name", ["harness_preflight.json", "validation_report.json"])
def test_local_harness_rejects_controller_artifact_changes_and_fails_closed(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    artifact_name: str,
) -> None:
    operation_id = _enqueue_opportunity(sandbox_repository, sandbox_settings)
    started = start_local_harness_operation(
        sandbox_repository,
        sandbox_settings,
        run_id="local-codex-invalid",
        operation_id=operation_id,
    )
    assert started is not None
    controller_artifact = (
        sandbox_repository / "data" / "runs" / "local-codex-invalid" / operation_id
    )
    controller_artifact /= artifact_name
    controller_artifact.write_text("{}\n", encoding="utf-8")
    result_path = sandbox_repository / started.result_path
    result_path.write_text(
        json.dumps(
            _result(
                operation_id,
                files_changed=[controller_artifact.relative_to(sandbox_repository).as_posix()],
            )
        ),
        encoding="utf-8",
    )

    with pytest.raises(AgentRunError, match="controller-owned artifacts"):
        finish_local_harness_operation(
            sandbox_repository,
            run_id="local-codex-invalid",
            operation_id=operation_id,
        )

    active = read_table(sandbox_repository, "operations_todo")
    assert active[0]["status"] == "waiting"
    assert active[0]["attempt_count"] == "1"
    assert read_table(sandbox_repository, "issues")[0]["related_operation_id"] == operation_id


def test_local_harness_outcome_can_complete_a_prepared_daily_batch(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    limited_settings = replace(
        sandbox_settings,
        operations=replace(sandbox_settings.operations, cycle_maximum_operations=1),
    )
    prepare_daily_run(
        sandbox_repository,
        limited_settings,
        run_id="local-daily-1",
        trigger="local",
        source_sha="a" * 40,
        now=NOW,
        retrieve_market=False,
        classify_opportunities=False,
    )

    record_local_agent_outcome(
        sandbox_repository,
        limited_settings,
        run_id="local-daily-1",
        operation_id="01K11M5T80JQDRKHZJ5XA8NY1R",
        status="succeeded",
        now=NOW,
    )

    batch = json.loads(
        (sandbox_repository / "data" / "runs" / "local-daily-1" / "agent_batch.json").read_text(
            encoding="utf-8"
        )
    )
    assert batch["operation_count"] == 1
    assert batch["maximum_operations"] == 1
    assert batch["estimated_model_budget_used"] == "0"
    assert batch["outcomes"] == [
        {"operation_id": "01K11M5T80JQDRKHZJ5XA8NY1R", "status": "succeeded"}
    ]
    queued = _enqueue_opportunity(sandbox_repository, limited_settings)
    assert (
        start_local_harness_operation(
            sandbox_repository,
            limited_settings,
            run_id="local-daily-1",
            operation_id=queued,
        )
        is None
    )
