from __future__ import annotations

import json
from pathlib import Path

import pytest

import papertrader.repository_state as repository_state
from papertrader.cli import main
from papertrader.oauth_credentials import OAUTH_CIPHERTEXT_PATH


def test_agent_scoped_cli_command_writes_exact_change_receipt(
    monkeypatch,
    sandbox_repository: Path,  # type: ignore[no-untyped-def]
) -> None:
    operation_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    run_id = "audit-run"
    artifact = sandbox_repository / "data" / "runs" / run_id / operation_id
    artifact.mkdir(parents=True)
    request = artifact / "issue-request.json"
    request.write_text(
        json.dumps(
            {
                "issue_code": "primary_evidence_missing",
                "impact": "affects_candidate",
                "severity": "warning",
                "title": "Missing primary filing",
                "description": "The bounded research operation lacks a current filing.",
                "entity_type": "operation",
                "entity_id": operation_id,
                "owner": "research",
                "related_run_id": run_id,
                "related_operation_id": operation_id,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("WIKI_PATH", str(sandbox_repository / "data" / "wiki"))
    monkeypatch.setenv("PAPERTRADER_AUDIT_RUN_ID", run_id)
    monkeypatch.setenv("PAPERTRADER_AUDIT_OPERATION_ID", operation_id)
    monkeypatch.setenv("PAPERTRADER_AUDIT_OPERATION_TYPE", "opportunity_research")
    monkeypatch.setenv(
        "PAPERTRADER_AUDIT_PATH",
        f"data/runs/{run_id}/{operation_id}/command_audit.json",
    )

    assert (
        main(
            [
                "--repository",
                str(sandbox_repository),
                "issue",
                "record",
                "--request",
                str(request),
            ]
        )
        == 0
    )

    audit = json.loads((artifact / "command_audit.json").read_text(encoding="utf-8"))
    entry = audit["entries"][0]
    assert entry["exit_code"] == 0
    assert entry["command"].startswith("papertrader --repository")
    assert entry["request"]["path"] == f"data/runs/{run_id}/{operation_id}/issue-request.json"
    assert entry["request"]["identity"][0] == "file"
    assert entry["changed_paths"] == ["data/issues.md", "data/tables/issues.csv"]
    assert [change["path"] for change in entry["changes"]] == entry["changed_paths"]
    assert all(change["before"] != change["after"] for change in entry["changes"])


def test_agent_scoped_cli_rejects_disallowed_command_before_audit(
    monkeypatch,
    sandbox_repository: Path,  # type: ignore[no-untyped-def]
    capsys,
) -> None:
    operation_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    run_id = "scope-guard"
    artifact = sandbox_repository / "data" / "runs" / run_id / operation_id
    artifact.mkdir(parents=True)
    request = artifact / "watchlist-request.json"
    request.write_text("{}\n", encoding="utf-8")
    monkeypatch.setenv("WIKI_PATH", str(sandbox_repository / "data" / "wiki"))
    monkeypatch.setenv("PAPERTRADER_AUDIT_RUN_ID", run_id)
    monkeypatch.setenv("PAPERTRADER_AUDIT_OPERATION_ID", operation_id)
    monkeypatch.setenv("PAPERTRADER_AUDIT_OPERATION_TYPE", "security_research")
    monkeypatch.setenv(
        "PAPERTRADER_AUDIT_PATH",
        f"data/runs/{run_id}/{operation_id}/command_audit.json",
    )

    assert (
        main(
            [
                "--repository",
                str(sandbox_repository),
                "watchlist",
                "import",
                "--request",
                str(request),
            ]
        )
        == 2
    )

    captured = capsys.readouterr()
    assert "ERROR [command-scope]" in captured.err
    assert "papertrader --repository" in captured.err
    assert "is outside the security_research skill scope" in captured.err
    assert not (artifact / "command_audit.json").exists()


def test_agent_command_audit_excludes_controller_owned_oauth_ciphertext(
    monkeypatch,
    sandbox_repository: Path,  # type: ignore[no-untyped-def]
) -> None:
    operation_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    run_id = "oauth-audit-boundary"
    artifact = sandbox_repository / "data" / "runs" / run_id / operation_id
    artifact.mkdir(parents=True)
    ciphertext = sandbox_repository.joinpath(*OAUTH_CIPHERTEXT_PATH.parts)
    ciphertext.parent.mkdir(parents=True)
    ciphertext.write_bytes(b"public encrypted credential state")
    original_hash_file = repository_state._hash_file

    def reject_ciphertext_read(path: Path) -> str:
        if path == ciphertext:
            raise PermissionError("controller-owned ciphertext is unreadable")
        return original_hash_file(path)

    monkeypatch.setattr(repository_state, "_hash_file", reject_ciphertext_read)
    monkeypatch.setenv("WIKI_PATH", str(sandbox_repository / "data" / "wiki"))
    monkeypatch.setenv("PAPERTRADER_AUDIT_RUN_ID", run_id)
    monkeypatch.setenv("PAPERTRADER_AUDIT_OPERATION_ID", operation_id)
    monkeypatch.setenv("PAPERTRADER_AUDIT_OPERATION_TYPE", "daily_podcast")
    monkeypatch.setenv(
        "PAPERTRADER_AUDIT_PATH",
        f"data/runs/{run_id}/{operation_id}/command_audit.json",
    )

    assert (
        main(
            [
                "--repository",
                str(sandbox_repository),
                "queue",
                "validate",
            ]
        )
        == 0
    )

    audit = json.loads((artifact / "command_audit.json").read_text(encoding="utf-8"))
    assert audit["entries"][0]["exit_code"] == 0
    assert audit["entries"][0]["changed_paths"] == []
    with pytest.raises(PermissionError, match="controller-owned ciphertext is unreadable"):
        repository_state.snapshot_repository(sandbox_repository)
