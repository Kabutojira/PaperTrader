from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.agent_runner import AgentRunError, configure_hermes_home, run_one_operation
from papertrader.config import Settings
from papertrader.queue import enqueue_operation

NOW = datetime(2026, 7, 24, 12, tzinfo=UTC)


def _home(repository: Path, settings: Settings, tmp_path: Path) -> Path:
    home = tmp_path / "hermes"
    configure_hermes_home(repository, settings, home)
    skill = home / "skills" / "research" / "llm-wiki" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: llm-wiki\ndescription: Native.\nversion: 2.1.0\n---\n# Wiki\n",
        encoding="utf-8",
    )
    return home


def _enqueue(repository: Path, settings: Settings) -> str:
    operation_id, _ = enqueue_operation(
        repository,
        settings,
        operation_type="opportunity_research",
        entity_type="opportunity",
        entity_id="opp-test",
        dedupe_key="opportunity_research:opp-test:fixture:2026-07-24",
        prompt="Research one bounded trigger.",
        inputs={
            "security_id": "sec-test",
            "trigger_type": "rsi_oversold",
            "market_data_as_of": "2026-07-24T10:00:00Z",
            "period_start": "2026-07-01",
            "period_end": "2026-07-24",
        },
        source="test",
        now=NOW,
    )
    return operation_id


def _manifest(operation_id: str, files: list[str]) -> dict[str, object]:
    return {
        "operation_id": operation_id,
        "status": "succeeded",
        "summary": "Evidence did not justify a follow-up.",
        "evidence": [{"source": "fixture", "claim": "No thesis changed."}],
        "files_changed": files,
        "operations_created": [],
        "issues_recorded": [],
        "daily_report_items": [],
        "commands_run": [],
        "validation": {"passed": True, "checks": ["bounded no-op"]},
    }


def _executor_with_change(
    change: callable,
    files: list[str],  # type: ignore[valid-type]
):
    def execute(
        command: Sequence[str],
        cwd: Path,
        environment: Mapping[str, str],
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        del timeout
        change(cwd)
        operation_id = environment["PAPERTRADER_AUDIT_OPERATION_ID"]
        path = (
            cwd
            / "data"
            / "runs"
            / environment["PAPERTRADER_AUDIT_RUN_ID"]
            / operation_id
            / "agent_result.json"
        )
        path.write_text(json.dumps(_manifest(operation_id, files)), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    return execute


def test_out_of_scope_source_write_fails_closed(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    operation_id = _enqueue(sandbox_repository, sandbox_settings)
    home = _home(sandbox_repository, sandbox_settings, tmp_path)

    def change(root: Path) -> None:
        path = root / "src" / "papertrader" / "malicious.py"
        path.parent.mkdir(parents=True)
        path.write_text("REAL_ORDER = True\n", encoding="utf-8")

    with pytest.raises(AgentRunError, match="non-runtime path"):
        run_one_operation(
            sandbox_repository,
            sandbox_settings,
            run_id="bad-scope",
            hermes_home=home,
            environment={"PATH": "/usr/bin"},
            operation_id=operation_id,
            executor=_executor_with_change(change, ["src/papertrader/malicious.py"]),
        )


def test_stale_unchanged_file_in_manifest_fails_closed(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    operation_id = _enqueue(sandbox_repository, sandbox_settings)
    home = _home(sandbox_repository, sandbox_settings, tmp_path)

    with pytest.raises(AgentRunError, match="stale or incomplete"):
        run_one_operation(
            sandbox_repository,
            sandbox_settings,
            run_id="stale-result",
            hermes_home=home,
            environment={"PATH": "/usr/bin"},
            operation_id=operation_id,
            executor=_executor_with_change(lambda root: None, ["data/wiki/index.md"]),
        )


def test_symlink_write_fails_closed(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    operation_id = _enqueue(sandbox_repository, sandbox_settings)
    home = _home(sandbox_repository, sandbox_settings, tmp_path)

    def change(root: Path) -> None:
        (root / "data" / "wiki" / "ideas" / "evil.md").symlink_to("../index.md")

    with pytest.raises(AgentRunError, match="symlink or special file"):
        run_one_operation(
            sandbox_repository,
            sandbox_settings,
            run_id="symlink-result",
            hermes_home=home,
            environment={"PATH": "/usr/bin"},
            operation_id=operation_id,
            executor=_executor_with_change(change, ["data/wiki/ideas/evil.md"]),
        )


def test_audited_request_cannot_change_after_structured_command(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    operation_id = _enqueue(sandbox_repository, sandbox_settings)
    home = _home(sandbox_repository, sandbox_settings, tmp_path)

    def execute(
        command: Sequence[str],
        cwd: Path,
        environment: Mapping[str, str],
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        del timeout
        run_id = environment["PAPERTRADER_AUDIT_RUN_ID"]
        artifact = cwd / "data" / "runs" / run_id / operation_id
        request = artifact / "issue-request.json"
        request.write_text(
            json.dumps(
                {
                    "severity": "warning",
                    "title": "Missing primary evidence",
                    "description": "The trigger lacks a current primary source.",
                    "owner": "research",
                    "related_run_id": run_id,
                    "related_operation_id": operation_id,
                }
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
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
        assert completed.returncode == 0, completed.stderr
        issue_id = completed.stdout.strip()
        audit = json.loads((artifact / "command_audit.json").read_text(encoding="utf-8"))
        request.write_text('{"tampered": true}\n', encoding="utf-8")
        result = _manifest(
            operation_id,
            [
                "data/issues.md",
                f"data/runs/{run_id}/{operation_id}/issue-request.json",
                "data/tables/issues.csv",
            ],
        )
        result["issues_recorded"] = [issue_id]
        result["commands_run"] = [audit["entries"][0]["command"]]
        (artifact / "agent_result.json").write_text(json.dumps(result), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    with pytest.raises(AgentRunError, match="command request changed after audit"):
        run_one_operation(
            sandbox_repository,
            sandbox_settings,
            run_id="request-tamper",
            hermes_home=home,
            environment={"PATH": "/usr/bin"},
            operation_id=operation_id,
            executor=execute,
        )
