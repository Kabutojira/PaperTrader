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
    assemble_podcast,
    enqueue_daily_podcast,
    finalize_daily_podcast,
)
from papertrader.queue import RunBudget, claim_next, fail_attempt, prepare_queue
from papertrader.tables import read_table

NOW = datetime(2026, 7, 30, 18, tzinfo=UTC)


def _completed_manifest(repository: Path, run_id: str) -> None:
    report = repository / "data" / "wiki" / "daily-reports" / "daily-report_20260730.md"
    report.write_text(
        """---
title: Daily
type: daily-report
status: maintained
tags:
  - daily-report
created: '2026-07-30'
updated: '2026-07-30'
provenance: test
---
""",
        encoding="utf-8",
    )
    run = repository / "data" / "runs" / run_id
    run.mkdir(parents=True)
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


def test_completed_run_enqueues_one_final_podcast(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _completed_manifest(sandbox_repository, "podcast-run")
    hashes_before = _source_hashes(sandbox_repository, as_of=NOW)

    result = enqueue_daily_podcast(
        sandbox_repository,
        sandbox_settings,
        run_id="podcast-run",
        now=NOW,
    )

    assert result.created is True
    row = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_id"] == result.operation_id
    )
    assert row["operation_type"] == "daily_podcast"
    assert row["priority"] == "100"
    assert row["max_attempts"] == "1"
    context = json.loads((sandbox_repository / result.context_path).read_text())
    assert context["target_minutes"] == 20
    manifest = json.loads(
        (sandbox_repository / "data" / "runs" / "podcast-run" / "daily_run.json").read_text()
    )
    assert manifest["podcast_status"] == "queued"
    assert manifest["podcast_operation_id"] == result.operation_id
    assert _source_hashes(sandbox_repository, as_of=NOW) == hashes_before


def test_failed_podcast_is_recorded_on_the_completed_daily_manifest(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    run_id = "podcast-failed"
    _completed_manifest(sandbox_repository, run_id)
    enqueued = enqueue_daily_podcast(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        now=NOW,
    )
    prepare_queue(sandbox_repository, now=NOW)
    claimed = claim_next(
        sandbox_repository,
        sandbox_settings,
        run_id=run_id,
        budget=RunBudget(
            maximum_operations=1,
            maximum_cost=sandbox_settings.operations.maximum_model_budget_usd_per_run,
        ),
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
    issues = read_table(sandbox_repository, "issues")
    assert any(
        row["owner"] == "delivery" and row["related_operation_id"] == enqueued.operation_id
        for row in issues
    )


def test_podcast_assembly_validates_length_and_removes_tts_chunks(
    sandbox_repository: Path,
) -> None:
    run_id = "podcast-assembly"
    operation_id = "01K11M5T80JQDRKHZJ5XA8NY1R"
    operation_root = sandbox_repository / "data" / "runs" / run_id / operation_id
    operation_root.mkdir(parents=True)
    chunks = [operation_root / "chunk-01.mp3", operation_root / "chunk-02.mp3"]
    for chunk in chunks:
        chunk.write_bytes(b"audio-chunk")
    page = sandbox_repository / "data" / "wiki" / "podcasts" / "daily-podcast_20260730.md"
    page.parent.mkdir(parents=True)
    page.write_text(" ".join(["word"] * 3000), encoding="utf-8")

    def fake_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        if "-show_entries" in command:
            return subprocess.CompletedProcess(command, 0, stdout="1200\n", stderr="")
        Path(command[-1]).write_bytes(b"assembled-audio")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    result = assemble_podcast(
        sandbox_repository,
        {
            "run_id": run_id,
            "operation_id": operation_id,
            "script_path": "data/wiki/podcasts/daily-podcast_20260730.md",
            "output_path": "data/wiki/podcasts/daily-podcast_20260730.mp3",
            "chunk_paths": [path.relative_to(sandbox_repository).as_posix() for path in chunks],
        },
        runner=fake_runner,
    )

    assert result.word_count == 3000
    assert result.duration_seconds == 1200
    assert (sandbox_repository / result.output_path).read_bytes() == b"assembled-audio"
    assert not any(path.exists() for path in chunks)


def test_failed_podcast_assembly_removes_intermediate_audio(
    sandbox_repository: Path,
) -> None:
    run_id = "podcast-failed-assembly"
    operation_id = "01K11M5T80JQDRKHZJ5XA8NY1S"
    operation_root = sandbox_repository / "data" / "runs" / run_id / operation_id
    operation_root.mkdir(parents=True)
    chunks = [operation_root / "chunk-01.mp3", operation_root / "chunk-02.mp3"]
    for chunk in chunks:
        chunk.write_bytes(b"audio-chunk")
    page = sandbox_repository / "data" / "wiki" / "podcasts" / "daily-podcast_20260730.md"
    page.parent.mkdir(parents=True)
    page.write_text(" ".join(["word"] * 3000), encoding="utf-8")

    def fake_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        if "-show_entries" in command:
            return subprocess.CompletedProcess(command, 0, stdout="100\n", stderr="")
        Path(command[-1]).write_bytes(b"assembled-audio")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    with pytest.raises(PodcastError, match="between 16 and 24 minutes"):
        assemble_podcast(
            sandbox_repository,
            {
                "run_id": run_id,
                "operation_id": operation_id,
                "script_path": "data/wiki/podcasts/daily-podcast_20260730.md",
                "output_path": "data/wiki/podcasts/daily-podcast_20260730.mp3",
                "chunk_paths": [path.relative_to(sandbox_repository).as_posix() for path in chunks],
            },
            runner=fake_runner,
        )

    assert not any(path.exists() for path in chunks)
