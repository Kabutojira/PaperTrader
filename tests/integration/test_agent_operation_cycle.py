from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

from papertrader.agent_runner import configure_hermes_home, run_one_operation
from papertrader.config import Settings
from papertrader.queue import enqueue_operation
from papertrader.tables import read_table

NOW = datetime(2026, 7, 24, 12, tzinfo=UTC)


def test_seeded_agent_operation_audits_structured_change_and_terminalizes(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    home = tmp_path / "hermes"
    configure_hermes_home(sandbox_repository, sandbox_settings, home)
    native = home / "skills" / "research" / "llm-wiki" / "SKILL.md"
    native.parent.mkdir(parents=True)
    native.write_text(
        "---\nname: llm-wiki\ndescription: Native.\nversion: 2.1.0\n---\n# Wiki\n",
        encoding="utf-8",
    )
    operation_id, _ = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="opportunity_research",
        entity_type="opportunity",
        entity_id="opp-integration",
        dedupe_key="opportunity_research:opp-integration:fixture:2026-07-24",
        prompt="Classify one bounded integration trigger.",
        inputs={
            "security_id": "sec-integration",
            "trigger_type": "volume_anomaly",
            "market_data_as_of": "2026-07-24T10:00:00Z",
            "period_start": "2026-07-23",
            "period_end": "2026-07-24",
        },
        source="integration-test",
        now=NOW,
    )

    def fake_hermes(
        command: Sequence[str],
        cwd: Path,
        environment: Mapping[str, str],
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        del timeout
        run_id = environment["PAPERTRADER_AUDIT_RUN_ID"]
        selected_operation = environment["PAPERTRADER_AUDIT_OPERATION_ID"]
        artifact = cwd / "data" / "runs" / run_id / selected_operation
        request = artifact / "issue-request.json"
        request.write_text(
            json.dumps(
                {
                    "severity": "warning",
                    "title": "Opportunity lacks a current primary source",
                    "description": "The move is retained as noise pending primary evidence.",
                    "owner": "research",
                    "related_run_id": run_id,
                    "related_operation_id": selected_operation,
                }
            ),
            encoding="utf-8",
        )
        audited = subprocess.run(
            [
                sys.executable,
                "-m",
                "papertrader",
                "--repository",
                str(cwd),
                "issue",
                "record",
                "--request",
                str(request),
            ],
            cwd=cwd,
            env=dict(environment),
            check=False,
            capture_output=True,
            text=True,
        )
        assert audited.returncode == 0, audited.stderr
        assert audited.stdout.strip()
        followup_request = artifact / "followup-request.json"
        followup_request.write_text(
            json.dumps(
                {
                    "operation_type": "idea_research",
                    "entity_type": "idea",
                    "entity_id": "idea-integration",
                    "dedupe_key": "idea_research:idea-integration:opportunity:2026-07-24",
                    "prompt": "Research one bounded integration idea.",
                    "inputs": {
                        "idea_id": "idea-integration",
                        "seed_claim": "A bounded follow-up from the opportunity fixture.",
                    },
                    "source": "integration-test",
                    "priority": 60,
                    "freshness_days": 30,
                    "depends_on": [selected_operation],
                    "not_before": "",
                    "deadline": "",
                    "source_refs": [],
                    "max_attempts": 3,
                }
            ),
            encoding="utf-8",
        )
        enqueued = subprocess.run(
            [
                sys.executable,
                "-m",
                "papertrader",
                "--repository",
                str(cwd),
                "queue",
                "enqueue",
                "--request",
                str(followup_request),
            ],
            cwd=cwd,
            env=dict(environment),
            check=False,
            capture_output=True,
            text=True,
        )
        assert enqueued.returncode == 0, enqueued.stderr
        assert json.loads(enqueued.stdout)["created"] is True
        manifest = {
            "operation_id": selected_operation,
            "status": "succeeded",
            "summary": "The move was noise; one missing-evidence issue was retained.",
            "evidence": [
                {
                    "source": "normalized integration fixture",
                    "claim": "No primary evidence linked the move to a maintained thesis.",
                    "observed_at": "2026-07-24T10:00:00Z",
                }
            ],
            "files_changed": [],
            "operations_created": [],
            "issues_recorded": [],
            "daily_report_items": [],
            "commands_run": [],
            "validation": {"passed": True, "checks": ["evidence-linked no-follow-up"]},
        }
        (artifact / "agent_result.json").write_text(
            json.dumps(manifest, sort_keys=True), encoding="utf-8"
        )
        return subprocess.CompletedProcess(command, 0, "completed", "")

    assert (
        run_one_operation(
            sandbox_repository,
            sandbox_settings,
            run_id="integration-1",
            hermes_home=home,
            environment={"PATH": "/usr/bin", "OPENROUTER_API_KEY": "test-auxiliary-key"},
            operation_id=operation_id,
            executor=fake_hermes,
        )
        == "succeeded"
    )
    todo = read_table(sandbox_repository, "operations_todo")
    assert len(todo) == 1
    assert todo[0]["operation_type"] == "idea_research"
    history = read_table(sandbox_repository, "operations_history")
    assert history[0]["terminal_status"] == "succeeded"
    assert history[0]["result_path"].endswith("/agent_result.json")
    artifact = sandbox_repository / "data" / "runs" / "integration-1" / operation_id
    result = json.loads((artifact / "agent_result.json").read_text(encoding="utf-8"))
    audit = json.loads((artifact / "command_audit.json").read_text(encoding="utf-8"))
    validation = json.loads((artifact / "validation_report.json").read_text(encoding="utf-8"))
    assert result["files_changed"] == validation["changed_paths"]
    assert f"data/runs/integration-1/{operation_id}/issue-request.json" in result["files_changed"]
    followup_request_path = f"data/runs/integration-1/{operation_id}/followup-request.json"
    assert followup_request_path in result["files_changed"]
    assert result["operations_created"] == [todo[0]["operation_id"]]
    assert result["issues_recorded"] == [read_table(sandbox_repository, "issues")[0]["issue_id"]]
    assert result["commands_run"] == [entry["command"] for entry in audit["entries"]]
