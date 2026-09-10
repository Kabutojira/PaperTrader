from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.cli import main
from papertrader.config import Settings
from papertrader.daily import resume_or_create_daily_cycle
from papertrader.integrity import (
    validate_daily_run_artifacts,
    validate_integrity,
    validate_run_retention_artifacts,
)
from papertrader.retention import (
    RETENTION_MARKER,
    RetentionError,
    protected_run_ids,
    prune_run_artifacts,
)

OPERATION_ID = "01KZ8BGD98T363E1NM8EPYT9TG"


def _finalized_cycle(
    repository_root: Path,
    settings: Settings,
    *,
    at: datetime,
    snapshot_id: str,
    podcast_status: str = "skipped",
) -> Path:
    """Create one finalized version-2 cycle with prunable and protected artifacts."""

    manifest = resume_or_create_daily_cycle(
        repository_root,
        settings,
        trigger="workflow_dispatch",
        source_sha="a" * 40,
        github_run_id=str(int(at.timestamp())),
        workflow_attempt="1",
        now=at,
    )
    run_id = str(manifest["run_id"])
    stamp = at.strftime("%Y-%m-%dT%H:%M:%SZ")
    report_path = f"data/wiki/daily-reports/daily-report_{at.strftime('%Y%m%d')}.md"
    (repository_root / report_path).write_text(
        f'---\nsnapshot_id: "{snapshot_id}"\n---\n', encoding="utf-8"
    )
    run_directory = repository_root / "data" / "runs" / run_id
    manifest.update(
        {
            "status": "degraded",
            "research_cutoff_at": stamp,
            "finalization_at": stamp,
            "finalization_status": "succeeded",
            "completed_at": stamp,
            "completion_at": stamp,
            "report_path": report_path,
            "snapshot_id": snapshot_id,
            "podcast_status": podcast_status,
        }
    )
    (run_directory / "daily_run.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")
    (run_directory / "decision_snapshot.json").write_text(
        json.dumps({"snapshot_id": snapshot_id, "run_id": run_id, "as_of": stamp}) + "\n",
        encoding="utf-8",
    )
    (run_directory / "allocation_plan.json").write_text("{}\n", encoding="utf-8")
    operation = run_directory / OPERATION_ID
    operation.mkdir()
    for name in ("controller_prompt.md", "hermes_run.json", "command_audit.json"):
        (operation / name).write_text(f"{name} evidence\n", encoding="utf-8")
    (operation / "agent_result.json").write_text('{"kept": true}\n', encoding="utf-8")
    (operation / "assessment_upsert_request.json").write_text("{}\n", encoding="utf-8")
    return run_directory


def test_prune_removes_only_aged_evidence_and_records_a_hash_bound_marker(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    old = _finalized_cycle(
        sandbox_repository,
        sandbox_settings,
        at=datetime(2026, 6, 1, 12, tzinfo=UTC),
        snapshot_id="decision_11111111111111111111",
    )
    recent = _finalized_cycle(
        sandbox_repository,
        sandbox_settings,
        at=datetime(2026, 7, 20, 12, tzinfo=UTC),
        snapshot_id="decision_22222222222222222222",
    )
    now = datetime(2026, 7, 27, 12, tzinfo=UTC)
    assert validate_daily_run_artifacts(sandbox_repository) == []

    preview = prune_run_artifacts(sandbox_repository, sandbox_settings, now=now, dry_run=True)
    assert preview.dry_run is True
    assert preview.pruned_run_ids == (old.name,)
    assert (old / "decision_snapshot.json").is_file()

    result = prune_run_artifacts(sandbox_repository, sandbox_settings, now=now)

    assert result.retention_days == 30
    assert result.pruned_run_ids == (old.name,)
    assert recent.name in result.protected_run_ids
    assert set(result.pruned_paths) == {
        f"data/runs/{old.name}/decision_snapshot.json",
        f"data/runs/{old.name}/{OPERATION_ID}/command_audit.json",
        f"data/runs/{old.name}/{OPERATION_ID}/controller_prompt.md",
        f"data/runs/{old.name}/{OPERATION_ID}/hermes_run.json",
    }
    assert not (old / "decision_snapshot.json").exists()
    assert not (old / OPERATION_ID / "hermes_run.json").exists()
    assert (old / OPERATION_ID / "agent_result.json").is_file()
    assert (old / OPERATION_ID / "assessment_upsert_request.json").is_file()
    assert (old / "allocation_plan.json").is_file()
    assert (old / "daily_run.json").is_file()
    assert (recent / "decision_snapshot.json").is_file()
    assert (recent / OPERATION_ID / "hermes_run.json").is_file()

    marker = json.loads((old / RETENTION_MARKER).read_text(encoding="utf-8"))
    assert marker["run_id"] == old.name
    assert marker["retention_days"] == 30
    snapshot_entry = next(
        entry for entry in marker["artifacts"] if entry["path"].endswith("decision_snapshot.json")
    )
    assert snapshot_entry["snapshot_id"] == "decision_11111111111111111111"
    assert len(snapshot_entry["sha256"]) == 64
    assert validate_daily_run_artifacts(sandbox_repository) == []
    assert validate_run_retention_artifacts(sandbox_repository) == []
    integrity = validate_integrity(
        sandbox_repository,
        {"WIKI_PATH": str(sandbox_repository / "data" / "wiki")},
        require_current_publication=False,
    )
    assert not [error for error in integrity if "retention" in error or "snapshot" in error]

    again = prune_run_artifacts(sandbox_repository, sandbox_settings, now=now)
    assert again.pruned_paths == ()
    assert json.loads((old / RETENTION_MARKER).read_text(encoding="utf-8")) == marker


def test_prune_protects_published_unfinished_and_latest_cycles(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    published_cycle = _finalized_cycle(
        sandbox_repository,
        sandbox_settings,
        at=datetime(2026, 5, 1, 12, tzinfo=UTC),
        snapshot_id="decision_33333333333333333333",
    )
    latest = _finalized_cycle(
        sandbox_repository,
        sandbox_settings,
        at=datetime(2026, 5, 2, 12, tzinfo=UTC),
        snapshot_id="decision_44444444444444444444",
    )
    pending_podcast = _finalized_cycle(
        sandbox_repository,
        sandbox_settings,
        at=datetime(2026, 5, 3, 12, tzinfo=UTC),
        snapshot_id="decision_55555555555555555555",
        podcast_status="pending",
    )
    published = sandbox_repository / "data" / "published" / "decision_snapshot.json"
    published.write_text(
        json.dumps({"run_id": published_cycle.name, "snapshot_id": "x"}) + "\n", encoding="utf-8"
    )

    protected = protected_run_ids(sandbox_repository)
    assert set(protected) == {published_cycle.name, latest.name, pending_podcast.name}

    result = prune_run_artifacts(
        sandbox_repository, sandbox_settings, now=datetime(2026, 9, 1, tzinfo=UTC)
    )
    assert result.pruned_run_ids == ()
    for cycle in (published_cycle, latest, pending_podcast):
        assert (cycle / "decision_snapshot.json").is_file()


def test_retention_manifest_integrity_rejects_present_or_foreign_artifacts(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    old = _finalized_cycle(
        sandbox_repository,
        sandbox_settings,
        at=datetime(2026, 6, 1, 12, tzinfo=UTC),
        snapshot_id="decision_11111111111111111111",
    )
    _finalized_cycle(
        sandbox_repository,
        sandbox_settings,
        at=datetime(2026, 7, 20, 12, tzinfo=UTC),
        snapshot_id="decision_22222222222222222222",
    )
    prune_run_artifacts(
        sandbox_repository, sandbox_settings, now=datetime(2026, 7, 27, 12, tzinfo=UTC)
    )
    marker_path = old / RETENTION_MARKER
    marker = json.loads(marker_path.read_text(encoding="utf-8"))

    (old / "decision_snapshot.json").write_text("{}\n", encoding="utf-8")
    assert f"pruned run artifact is still present: data/runs/{old.name}/decision_snapshot.json" in (
        validate_run_retention_artifacts(sandbox_repository)
    )
    (old / "decision_snapshot.json").unlink()

    marker["artifacts"].append(
        {
            "path": f"data/runs/{old.name}/{OPERATION_ID}/agent_result.json",
            "sha256": "0" * 64,
            "size": 1,
            "pruned_at": "2026-07-27T12:00:00Z",
        }
    )
    marker_path.write_text(json.dumps(marker) + "\n", encoding="utf-8")
    foreign = f"data/runs/{old.name}/{OPERATION_ID}/agent_result.json"
    assert f"run retention lists a non-prunable artifact: {foreign}" in (
        validate_run_retention_artifacts(sandbox_repository)
    )

    marker["artifacts"] = [
        {**entry, "snapshot_id": "decision_99999999999999999999"}
        if entry["path"].endswith("decision_snapshot.json")
        else entry
        for entry in marker["artifacts"][:-1]
    ]
    marker_path.write_text(json.dumps(marker) + "\n", encoding="utf-8")
    assert f"completed daily run lacks its decision snapshot: {old.name}" in (
        validate_daily_run_artifacts(sandbox_repository)
    )


def test_prune_refuses_short_windows_and_cli_reports_json(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WIKI_PATH", str(sandbox_repository / "data" / "wiki"))
    with pytest.raises(RetentionError, match="at least 7 days"):
        prune_run_artifacts(sandbox_repository, sandbox_settings, retention_days=3)

    assert main(["--repository", str(sandbox_repository), "runs", "prune", "--dry-run"]) == 0
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert payload["dry_run"] is True
    assert payload["pruned_paths"] == []
    assert payload["retention_days"] == 30
