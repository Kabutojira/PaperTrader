from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

import pytest

import papertrader.wiki_maintenance as maintenance
from papertrader.agent_runner import configure_hermes_home
from papertrader.config import Settings
from papertrader.integrity import (
    validate_json_schemas,
    validate_wiki_maintenance_artifacts,
)
from papertrader.utils import content_hash
from papertrader.wiki_maintenance import (
    REPORT_VALIDATION_PLACEHOLDER,
    REQUIRED_REPORT_HEADINGS,
    VALIDATION_COMMANDS,
    ValidationCheck,
    WikiMaintenanceError,
    maintain_wiki,
)

NOW = datetime(2026, 7, 31, 12, tzinfo=UTC)


def _hermes_home(
    repository: Path,
    settings: Settings,
    tmp_path: Path,
    *,
    profile_name: str = "deep",
) -> Path:
    home = tmp_path / "hermes-profile"
    configure_hermes_home(
        repository,
        settings,
        home,
        execution_profile=settings.hermes.profile(profile_name),
    )
    skill = home / "skills" / "research" / "llm-wiki" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: llm-wiki\ndescription: Native wiki.\nversion: 2.1.0\n---\n\n# Native wiki\n",
        encoding="utf-8",
    )
    return home


def _passing_checks() -> tuple[ValidationCheck, ...]:
    return tuple(ValidationCheck(command, True, ()) for command in VALIDATION_COMMANDS)


def _report(identity: str, native_version: str, native_sha256: str) -> str:
    sections = {heading: "None." for heading in REQUIRED_REPORT_HEADINGS[:-1]}
    sections[REQUIRED_REPORT_HEADINGS[0]] = (
        f"- maintenance identity: {identity}\n- execution date: 2026-07-31"
    )
    sections[REQUIRED_REPORT_HEADINGS[1]] = (
        f"- native llm-wiki version: {native_version}\n- native llm-wiki sha256: {native_sha256}"
    )
    sections[REQUIRED_REPORT_HEADINGS[2]] = "- data/wiki/SCHEMA.md\n- data/wiki/index.md"
    sections[REQUIRED_REPORT_HEADINGS[3]] = "None."
    lines = ["# PaperTrader wiki maintenance report", ""]
    for heading in REQUIRED_REPORT_HEADINGS[:-1]:
        lines.extend((heading, "", sections[heading], ""))
    lines.extend((REPORT_VALIDATION_PLACEHOLDER, ""))
    return "\n".join(lines)


def test_native_only_maintenance_records_report_result_and_exact_command(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _hermes_home(
        sandbox_repository,
        sandbox_settings,
        tmp_path,
        profile_name="analyst",
    )
    native_path = home / "skills" / "research" / "llm-wiki" / "SKILL.md"
    native_sha256 = content_hash(native_path.read_bytes())
    captured: dict[str, object] = {}
    monkeypatch.setattr(maintenance, "_validation_checks", lambda root: _passing_checks())

    def execute(
        command: Sequence[str],
        cwd: Path,
        environment: Mapping[str, str],
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        captured.update(command=tuple(command), environment=dict(environment), timeout=timeout)
        report = (
            cwd
            / "data"
            / "runs"
            / "maintenance-run-1"
            / "wiki-maintenance"
            / "wiki_maintenance_report.md"
        )
        noncanonical = (
            _report("wiki-maintenance:2026-W31", "2.1.0", native_sha256)
            .replace("- maintenance identity:", "- Maintenance identity:")
            .replace("- execution date:", "- Execution date:")
            .replace("- native llm-wiki version:", "- Native llm-wiki version:")
            .replace("- native llm-wiki sha256:", "- Native llm-wiki sha256:")
            .replace(
                REPORT_VALIDATION_PLACEHOLDER,
                "## Exact validation results\nPending deterministic controller validation.",
            )
        )
        report.write_text(noncanonical, encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "complete", "")

    outcome = maintain_wiki(
        sandbox_repository,
        sandbox_settings,
        run_id="maintenance-run-1",
        hermes_home=home,
        environment={"PATH": "/usr/bin", "GITHUB_TOKEN": "never-forward"},
        executor=execute,
        now=lambda: NOW,
    )

    assert outcome.status == "succeeded"
    command = captured["command"]
    assert isinstance(command, tuple)
    assert command.count("--skills") == 1
    assert command[command.index("--skills") + 1] == "llm-wiki"
    assert command[command.index("--toolsets") + 1] == "file,terminal"
    assert command[command.index("--provider") + 1] == sandbox_settings.hermes.deep.provider
    assert command[command.index("--model") + 1] == sandbox_settings.hermes.deep.model
    assert "papertrader-controller" not in command
    prompt = command[command.index("--query") + 1]
    assert "Follow the complete built-in llm-wiki lint procedure" in prompt
    assert "do not enqueue operations" in prompt
    assert "data/wiki/SCHEMA.md" in prompt
    assert not (sandbox_repository / "skills" / "papertrader-wiki-maintenance").exists()
    child_environment = captured["environment"]
    assert isinstance(child_environment, dict)
    assert child_environment["WIKI_PATH"] == str((sandbox_repository / "data" / "wiki").resolve())
    assert "GITHUB_TOKEN" not in child_environment
    assert not any(name.startswith("PAPERTRADER_AUDIT_") for name in child_environment)

    result_path = sandbox_repository / outcome.result_path
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["maintenance_identity"] == "wiki-maintenance:2026-W31"
    assert result["native_skill"]["version"] == "2.1.0"
    assert result["native_skill"]["sha256"] == native_sha256
    assert result["loaded_skills"] == ["llm-wiki"]
    assert result["changed_paths"] == [outcome.report_path]
    assert [check["command"] for check in result["validation"]] == list(VALIDATION_COMMANDS)
    finalized_report = (sandbox_repository / outcome.report_path).read_text(encoding="utf-8")
    assert "Pending deterministic controller validation." not in finalized_report
    assert "- maintenance identity: wiki-maintenance:2026-W31" in finalized_report
    assert "- native llm-wiki version: 2.1.0" in finalized_report
    assert finalized_report.count("— PASSED") == 4
    assert validate_json_schemas(sandbox_repository) == []
    assert validate_wiki_maintenance_artifacts(sandbox_repository) == []


def test_success_and_active_lease_deduplicate_but_dry_run_does_not(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _hermes_home(sandbox_repository, sandbox_settings, tmp_path)
    monkeypatch.setattr(maintenance, "_validation_checks", lambda root: _passing_checks())

    dry = maintain_wiki(
        sandbox_repository,
        sandbox_settings,
        run_id="maintenance-dry",
        hermes_home=home,
        environment={"PATH": "/usr/bin"},
        dry_run=True,
        executor=lambda *args: (_ for _ in ()).throw(AssertionError("executor called")),
        now=lambda: NOW,
    )
    assert dry.status == "dry_run"

    native = home / "skills" / "research" / "llm-wiki" / "SKILL.md"
    native_sha256 = content_hash(native.read_bytes())

    def execute(
        command: Sequence[str], cwd: Path, environment: Mapping[str, str], timeout: int
    ) -> subprocess.CompletedProcess[str]:
        del environment, timeout
        report = (
            cwd
            / "data"
            / "runs"
            / "maintenance-live"
            / "wiki-maintenance"
            / "wiki_maintenance_report.md"
        )
        report.write_text(
            _report("wiki-maintenance:2026-W31", "2.1.0", native_sha256),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 0, "", "")

    live = maintain_wiki(
        sandbox_repository,
        sandbox_settings,
        run_id="maintenance-live",
        hermes_home=home,
        environment={"PATH": "/usr/bin"},
        executor=execute,
        now=lambda: NOW,
    )
    assert live.status == "succeeded"

    skipped = maintain_wiki(
        sandbox_repository,
        sandbox_settings,
        run_id="maintenance-duplicate",
        hermes_home=tmp_path / "missing-profile",
        environment={"PATH": "/usr/bin"},
        executor=lambda *args: (_ for _ in ()).throw(AssertionError("executor called")),
        now=lambda: NOW,
    )
    assert skipped.status == "skipped"
    assert skipped.reason == "successful_result_exists"
    assert not (sandbox_repository / "data" / "runs" / "maintenance-duplicate").exists()


def test_forbidden_raw_source_change_fails_and_retains_machine_result(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _hermes_home(sandbox_repository, sandbox_settings, tmp_path)
    native = home / "skills" / "research" / "llm-wiki" / "SKILL.md"
    native_sha256 = content_hash(native.read_bytes())
    monkeypatch.setattr(maintenance, "_validation_checks", lambda root: _passing_checks())

    def execute(
        command: Sequence[str], cwd: Path, environment: Mapping[str, str], timeout: int
    ) -> subprocess.CompletedProcess[str]:
        del environment, timeout
        report = (
            cwd
            / "data"
            / "runs"
            / "maintenance-forbidden"
            / "wiki-maintenance"
            / "wiki_maintenance_report.md"
        )
        report.write_text(
            _report("wiki-maintenance:2026-W31", "2.1.0", native_sha256),
            encoding="utf-8",
        )
        (cwd / "data" / "wiki" / "raw" / "forbidden.md").write_text(
            "raw sources are immutable\n", encoding="utf-8"
        )
        return subprocess.CompletedProcess(command, 0, "", "")

    with pytest.raises(WikiMaintenanceError, match="forbidden path"):
        maintain_wiki(
            sandbox_repository,
            sandbox_settings,
            run_id="maintenance-forbidden",
            hermes_home=home,
            environment={"PATH": "/usr/bin"},
            executor=execute,
            now=lambda: NOW,
        )

    retained = maintain_wiki(
        sandbox_repository,
        sandbox_settings,
        run_id="maintenance-forbidden",
        hermes_home=tmp_path / "missing-profile",
        environment={"PATH": "/usr/bin"},
        executor=lambda *args: (_ for _ in ()).throw(AssertionError("executor called")),
        now=lambda: NOW,
    )
    assert retained.status == "skipped"
    assert retained.reason == "retained_failed_attempt"

    result = json.loads(
        (
            sandbox_repository
            / "data"
            / "runs"
            / "maintenance-forbidden"
            / "wiki-maintenance"
            / "wiki_maintenance_result.json"
        ).read_text(encoding="utf-8")
    )
    assert result["status"] == "failed"
    assert "data/wiki/raw/forbidden.md" in result["changed_paths"]


def test_active_lease_skips_without_profile_or_artifact_creation(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    home = _hermes_home(sandbox_repository, sandbox_settings, tmp_path)
    preflight = maintenance.preflight_wiki_maintenance(
        sandbox_repository,
        sandbox_settings,
        home,
        environment={"PATH": "/usr/bin"},
        check_command=False,
    )
    artifact = sandbox_repository / "data" / "runs" / "leased" / "wiki-maintenance"
    artifact.mkdir(parents=True)
    (artifact / "wiki_maintenance_preflight.json").write_text(
        json.dumps(
            maintenance._preflight_payload(
                preflight,
                run_id="leased",
                identity="wiki-maintenance:2026-W31",
                execution_date="2026-07-31",
            )
        ),
        encoding="utf-8",
    )
    result = maintenance._result_payload(
        run_id="leased",
        identity="wiki-maintenance:2026-W31",
        iso_year=2026,
        iso_week=31,
        status="running",
        reason="lease_acquired",
        dry_run=False,
        started_at=NOW,
        completed_at=None,
        lease_expires_at=datetime(2026, 7, 31, 13, tzinfo=UTC),
        preflight=preflight,
        report_relative=("data/runs/leased/wiki-maintenance/wiki_maintenance_report.md"),
        changed_paths=(),
        checks=(),
        report_sha256="",
    )
    (artifact / "wiki_maintenance_result.json").write_text(json.dumps(result), encoding="utf-8")

    outcome = maintain_wiki(
        sandbox_repository,
        sandbox_settings,
        run_id="lease-duplicate",
        hermes_home=tmp_path / "missing",
        environment={"PATH": "/usr/bin"},
        executor=lambda *args: (_ for _ in ()).throw(AssertionError("executor called")),
        now=lambda: NOW,
    )

    assert outcome.status == "skipped"
    assert outcome.reason == "active_lease_exists"
