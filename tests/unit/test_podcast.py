from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.advice import _source_hashes
from papertrader.config import Settings
from papertrader.podcast import (
    PodcastError,
    enqueue_daily_podcast,
    finalize_daily_podcast,
    render_committed_podcast,
)
from papertrader.queue import RunBudget, claim_next, fail_attempt, prepare_queue
from papertrader.tables import read_table

NOW = datetime(2026, 7, 30, 18, tzinfo=UTC)


def test_podcast_skill_excludes_unscoped_advice_validation(repository_root: Path) -> None:
    skill = (
        repository_root / "skills" / "papertrader-daily-podcast" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "`advice validate` is outside the `daily_podcast` command scope" in skill
    assert "never list a rejected or pre-dispatch command" in skill


def _completed_manifest(repository: Path, run_id: str) -> None:
    report = repository / "data" / "wiki" / "daily-reports" / "daily-report_20260730.md"
    report.write_text("---\ntitle: Daily\ntype: daily-report\nstatus: maintained\n---\n")
    run = repository / "data" / "runs" / run_id
    run.mkdir(parents=True)
    (run / "decision_snapshot.json").write_text("{}\n", encoding="utf-8")
    (run / "daily_run.json").write_text(
        json.dumps(
            {
                "daily_run_version": 1,
                "run_id": run_id,
                "trigger": "test",
                "source_sha": "a" * 40,
                "status": "succeeded",
                "started_at": "2026-07-30T17:00:00Z",
                "completed_at": "2026-07-30T18:00:00Z",
                "preparation_errors": [],
                "queue_dispositions": [],
                "operation_count": 0,
                "model_budget_limit": "5.00",
                "model_budget_used": "0",
                "fill_outcomes": [],
                "report_path": "data/wiki/daily-reports/daily-report_20260730.md",
                "snapshot_id": "",
                "podcast_status": "pending",
                "podcast_operation_id": "",
                "podcast_page_path": "",
                "podcast_audio_path": "",
            }
        ),
        encoding="utf-8",
    )


def test_completed_run_enqueues_one_text_only_podcast(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _completed_manifest(sandbox_repository, "podcast-run")
    hashes_before = _source_hashes(sandbox_repository, as_of=NOW)

    result = enqueue_daily_podcast(
        sandbox_repository, sandbox_settings, run_id="podcast-run", now=NOW
    )

    assert result.created is True
    row = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_id"] == result.operation_id
    )
    assert row["operation_type"] == "daily_podcast"
    context = json.loads((sandbox_repository / result.context_path).read_text())
    assert context["target_minutes"] == 20
    assert "audio_path" not in context
    manifest = json.loads(
        (sandbox_repository / "data" / "runs" / "podcast-run" / "daily_run.json").read_text()
    )
    assert manifest["podcast_status"] == "queued"
    assert manifest["podcast_audio_path"] == ""
    assert _source_hashes(sandbox_repository, as_of=NOW) == hashes_before


def test_failed_podcast_is_recorded_without_requiring_audio(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    run_id = "podcast-failed"
    _completed_manifest(sandbox_repository, run_id)
    enqueued = enqueue_daily_podcast(sandbox_repository, sandbox_settings, run_id=run_id, now=NOW)
    prepare_queue(sandbox_repository, now=NOW)
    claimed = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        budget=RunBudget(maximum_operations=1, maximum_cost=5),
        operation_id=enqueued.operation_id,
        operation_type="daily_podcast",
        now=NOW,
    )
    assert claimed is not None
    assert (
        fail_attempt(
            sandbox_repository,
            operation_id=enqueued.operation_id,
            run_id=run_id,
            error="agent_validation_failed:test-issue",
            now=NOW,
        )
        == "failed"
    )
    assert finalize_daily_podcast(sandbox_repository, run_id=run_id, now=NOW) == "failed"
    manifest = json.loads(
        (sandbox_repository / "data" / "runs" / run_id / "daily_run.json").read_text()
    )
    assert manifest["podcast_status"] == "failed"


def test_podcast_render_uses_exact_committed_transcript_and_ephemeral_directory(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    cycle_id = "daily-20260730T180000Z"
    commit = "a" * 40
    script_path = "data/wiki/podcasts/daily-podcast_20260730T180000Z.md"
    paragraphs = [" ".join(["word"] * 750) for _ in range(4)]
    markdown = (
        f"---\ndaily_cycle_id: {cycle_id}\n---\n"
        "<!-- papertrader-spoken-transcript:start -->\n"
        + "\n\n".join(paragraphs)
        + "\n<!-- papertrader-spoken-transcript:end -->\n"
    )

    def fake_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[object]:
        if command[:2] == ["git", "show"]:
            return subprocess.CompletedProcess(command, 0, markdown.encode(), b"")
        if "-show_entries" in command:
            return subprocess.CompletedProcess(command, 0, "1200\n", "")
        output = (
            Path(command[command.index("--write-media") + 1])
            if "--write-media" in command
            else Path(command[-1])
        )
        output.write_bytes(b"assembled-audio")
        return subprocess.CompletedProcess(command, 0, "", "")

    output = tmp_path / "ephemeral"
    result = render_committed_podcast(
        sandbox_repository,
        sandbox_settings,
        daily_cycle_id=cycle_id,
        script_commit=commit,
        script_path=script_path,
        output_directory=output,
        runner=fake_runner,
    )

    assert result.word_count == 3000
    assert result.duration_seconds == 1200
    assert Path(result.audio_path).read_bytes() == b"assembled-audio"
    assert Path(result.manifest_path).is_file()
    assert not list(sandbox_repository.rglob("*.mp3"))
    assert not list(output.glob("chunk-*.mp3"))


def test_repository_podcast_audio_path_is_rejected(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    with pytest.raises(PodcastError, match="outside the checkout"):
        render_committed_podcast(
            sandbox_repository,
            sandbox_settings,
            daily_cycle_id="daily-20260730T180000Z",
            script_commit="a" * 40,
            script_path="data/wiki/podcasts/daily-podcast_20260730T180000Z.md",
            output_directory=sandbox_repository / "data" / "wiki" / "podcasts",
        )


def test_podcast_render_rejects_visible_machine_identity(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    cycle_id = "daily-20260730T180000Z"
    transcript = " ".join(["word"] * 2500)
    markdown = (
        f"---\ndaily_cycle_id: {cycle_id}\n---\n"
        "<!-- papertrader-spoken-transcript:start -->\n"
        "Visible security security_1234567890abcdef1234. "
        f"{transcript}\n"
        "<!-- papertrader-spoken-transcript:end -->\n"
    )

    def fake_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[object]:
        assert command[:2] == ["git", "show"]
        return subprocess.CompletedProcess(command, 0, markdown.encode(), b"")

    with pytest.raises(PodcastError, match="exposes a machine identity"):
        render_committed_podcast(
            sandbox_repository,
            sandbox_settings,
            daily_cycle_id=cycle_id,
            script_commit="a" * 40,
            script_path="data/wiki/podcasts/daily-podcast_20260730T180000Z.md",
            output_directory=tmp_path / "podcast",
            runner=fake_runner,
        )


def test_failed_ephemeral_render_removes_completed_chunks(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    cycle_id = "daily-20260730T180001Z"
    script_path = "data/wiki/podcasts/daily-podcast_20260730T180001Z.md"
    paragraphs = [" ".join(["word"] * 750) for _ in range(4)]
    markdown = (
        f"---\ndaily_cycle_id: {cycle_id}\n---\n"
        "<!-- papertrader-spoken-transcript:start -->\n"
        + "\n\n".join(paragraphs)
        + "\n<!-- papertrader-spoken-transcript:end -->\n"
    )
    attempts = 0

    def failing_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[object]:
        nonlocal attempts
        if command[:2] == ["git", "show"]:
            return subprocess.CompletedProcess(command, 0, markdown.encode(), b"")
        attempts += 1
        if attempts == 1:
            Path(command[command.index("--write-media") + 1]).write_bytes(b"first-chunk")
            return subprocess.CompletedProcess(command, 0, "", "")
        return subprocess.CompletedProcess(command, 1, "", "tts failed")

    output = tmp_path / "failed-render"
    with pytest.raises(PodcastError, match="chunk 2"):
        render_committed_podcast(
            sandbox_repository,
            sandbox_settings,
            daily_cycle_id=cycle_id,
            script_commit="a" * 40,
            script_path=script_path,
            output_directory=output,
            runner=failing_runner,
        )

    assert list(output.iterdir()) == []
