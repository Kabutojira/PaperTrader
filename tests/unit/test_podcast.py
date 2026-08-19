from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.advice import _source_hashes
from papertrader.config import Settings
from papertrader.podcast import (
    PodcastError,
    enqueue_daily_podcast,
    finalize_daily_podcast,
    render_draft_podcast,
    seal_podcast_render,
    validate_podcast_context,
    validate_podcast_script,
    validate_podcast_script_file,
)
from papertrader.queue import RunBudget, claim_next, fail_attempt, prepare_queue
from papertrader.tables import append_unique, read_table

NOW = datetime(2026, 7, 30, 18, tzinfo=UTC)


def test_podcast_skill_excludes_unscoped_advice_validation(repository_root: Path) -> None:
    skill = (repository_root / "skills" / "papertrader-daily-podcast" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "`advice validate` is outside the `daily_podcast` command scope" in skill
    assert "never list a rejected or pre-dispatch command" in skill
    assert "paper_trading: true" in skill
    assert "invoke exactly once" in skill
    assert "podcast validate-script" in skill
    assert "renderer before one preflight has passed" in skill
    assert "Do not retry a failed render" in skill
    assert "do not independently recompute hashes" in skill
    assert "`podcast context validate` has verified" in skill
    assert "derived only from the immutable cycle ID" in skill
    assert "Never replace its timestamp with the current clock" in skill
    assert "agent-authored path error is not a frozen-input conflict" in skill


def _script(cycle_id: str, *, extra_body: str = "") -> str:
    paragraphs = [" ".join(["word"] * 375) for _ in range(8)]
    return (
        f"---\ndaily_cycle_id: {cycle_id}\npaper_trading: true\n---\n"
        f"{extra_body}"
        "<!-- papertrader-spoken-transcript:start -->\n"
        + "\n\n".join(paragraphs)
        + "\n<!-- papertrader-spoken-transcript:end -->\n"
    )


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


def _cycle_manifest(
    repository: Path,
    cycle_id: str,
    *,
    started_at: str,
    cutoff: str,
    podcast_status: str = "pending",
    operations: list[dict[str, object]] | None = None,
) -> None:
    stamp = cycle_id.removeprefix("daily-")
    report_date = cutoff[:10].replace("-", "")
    report_path = f"data/wiki/daily-reports/daily-report_{report_date}.md"
    report = repository / report_path
    report.write_text("---\ntitle: Daily\ntype: daily-report\nstatus: maintained\n---\n")
    run = repository / "data" / "runs" / cycle_id
    run.mkdir(parents=True, exist_ok=True)
    (run / "decision_snapshot.json").write_text("{}\n", encoding="utf-8")
    page_path = (
        f"data/wiki/podcasts/daily-podcast_{stamp}.md" if podcast_status == "succeeded" else ""
    )
    if page_path:
        page = repository / page_path
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(f"---\ndaily_cycle_id: {cycle_id}\n---\n", encoding="utf-8")
        (run / "podcast_context.json").write_text(
            json.dumps(
                {
                    "podcast_context_version": 2,
                    "daily_cycle_id": cycle_id,
                    "research_cutoff_at": cutoff,
                    "page_path": page_path,
                }
            ),
            encoding="utf-8",
        )
    (run / "daily_run.json").write_text(
        json.dumps(
            {
                "daily_run_version": 2,
                "run_id": cycle_id,
                "daily_cycle_id": cycle_id,
                "status": "succeeded" if podcast_status == "succeeded" else "running",
                "started_at": started_at,
                "research_cutoff_at": cutoff,
                "finalization_at": cutoff,
                "report_path": report_path,
                "operations_accepted": operations or [],
                "fill_outcomes": [],
                "snapshot_id": "",
                "podcast_status": podcast_status,
                "podcast_operation_id": "",
                "podcast_page_path": page_path,
                "podcast_audio_path": "",
            }
        ),
        encoding="utf-8",
    )


def _accepted_research(
    repository: Path,
    *,
    cycle_id: str,
    operation_id: str,
    completed_at: str,
    page_path: str,
    summary: str,
) -> None:
    append_unique(
        repository,
        "operations_history",
        [
            {
                "operation_id": operation_id,
                "created_at": completed_at,
                "updated_at": completed_at,
                "status": "succeeded",
                "priority": "50",
                "operation_type": "idea_research",
                "entity_type": "idea",
                "entity_id": f"idea-{operation_id[-4:]}",
                "not_before": "",
                "deadline": "",
                "depends_on": "",
                "dedupe_key": f"idea:{operation_id}",
                "freshness_days": "0",
                "skill_names": "llm-wiki|papertrader-idea-research",
                "prompt": "Research one idea.",
                "payload_path": f"data/operations/payloads/{operation_id}.json",
                "source": "test",
                "attempt_count": "1",
                "max_attempts": "1",
                "claimed_by_run_id": cycle_id,
                "lease_expires_at": "",
                "last_error": "",
                "terminal_status": "succeeded",
                "completed_at": completed_at,
                "result_path": f"data/runs/{cycle_id}/{operation_id}/agent_result.json",
                "result_summary": summary,
                "terminal_reason": "agent_result:succeeded",
            }
        ],
        key_columns=("operation_id",),
    )
    artifact = repository / "data" / "runs" / cycle_id / operation_id
    artifact.mkdir(parents=True, exist_ok=True)
    (artifact / "agent_result.json").write_text(
        json.dumps(
            {
                "summary": summary,
                "evidence": [{"source": page_path, "claim": summary}],
                "daily_report_items": [summary],
                "files_changed": [page_path],
            }
        ),
        encoding="utf-8",
    )
    (artifact / "hermes_run.json").write_text(
        json.dumps({"completed_at": completed_at}), encoding="utf-8"
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
    assert context["podcast_context_version"] == 3
    assert context["window_mode"] == "seven_day_bootstrap"
    assert context["target_minutes"] == 20
    assert "audio_path" not in context
    validation = validate_podcast_context(sandbox_repository, daily_cycle_id="podcast-run")
    assert validation.context_path == result.context_path
    assert validation.referenced_file_count == 2
    manifest = json.loads(
        (sandbox_repository / "data" / "runs" / "podcast-run" / "daily_run.json").read_text()
    )
    assert manifest["podcast_status"] == "queued"
    assert manifest["podcast_audio_path"] == ""
    assert _source_hashes(sandbox_repository, as_of=NOW) == hashes_before


def test_version_two_podcast_path_is_bound_to_cycle_not_enqueue_time(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    cycle_id = "daily-20260729T100000Z"
    expected = "data/wiki/podcasts/daily-podcast_20260729T100000Z.md"
    enqueue_time_path = "data/wiki/podcasts/daily-podcast_20260730T180000Z.md"
    _cycle_manifest(
        sandbox_repository,
        cycle_id,
        started_at="2026-07-29T09:00:00Z",
        cutoff="2026-07-29T10:30:00Z",
    )

    result = enqueue_daily_podcast(
        sandbox_repository,
        sandbox_settings,
        run_id=cycle_id,
        now=NOW,
    )
    context = json.loads((sandbox_repository / result.context_path).read_text())
    payload = json.loads(
        (
            sandbox_repository / "data" / "operations" / "payloads" / f"{result.operation_id}.json"
        ).read_text()
    )
    manifest = json.loads(
        (sandbox_repository / "data" / "runs" / cycle_id / "daily_run.json").read_text()
    )

    assert context["page_path"] == expected
    assert payload["inputs"]["page_path"] == expected
    assert manifest["podcast_page_path"] == expected
    assert context["generated_at"] == "2026-07-30T18:00:00Z"
    assert expected != enqueue_time_path


def test_context_validation_rejects_page_not_bound_to_cycle(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    cycle_id = "daily-20260729T100000Z"
    _cycle_manifest(
        sandbox_repository,
        cycle_id,
        started_at="2026-07-29T09:00:00Z",
        cutoff="2026-07-29T10:30:00Z",
    )
    result = enqueue_daily_podcast(
        sandbox_repository,
        sandbox_settings,
        run_id=cycle_id,
        now=NOW,
    )
    wrong_page = "data/wiki/podcasts/daily-podcast_20260730T180000Z.md"
    context_path = sandbox_repository / result.context_path
    context = json.loads(context_path.read_text())
    context["page_path"] = wrong_page
    context_path.write_text(json.dumps(context), encoding="utf-8")
    manifest_path = sandbox_repository / "data" / "runs" / cycle_id / "daily_run.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["podcast_page_path"] = wrong_page
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(PodcastError, match="page path is not bound to the timestamped cycle"):
        validate_podcast_context(sandbox_repository, daily_cycle_id=cycle_id)


def test_context_selects_latest_successful_same_day_podcast_and_ignores_failures(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _cycle_manifest(
        sandbox_repository,
        "daily-20260729T080000Z",
        started_at="2026-07-29T07:00:00Z",
        cutoff="2026-07-29T08:30:00Z",
        podcast_status="succeeded",
    )
    _cycle_manifest(
        sandbox_repository,
        "daily-20260729T100000Z",
        started_at="2026-07-29T09:00:00Z",
        cutoff="2026-07-29T10:30:00Z",
        podcast_status="succeeded",
    )
    _cycle_manifest(
        sandbox_repository,
        "daily-20260729T120000Z",
        started_at="2026-07-29T11:00:00Z",
        cutoff="2026-07-29T12:30:00Z",
        podcast_status="failed",
    )
    _completed_manifest(sandbox_repository, "podcast-current")

    result = enqueue_daily_podcast(
        sandbox_repository, sandbox_settings, run_id="podcast-current", now=NOW
    )
    context = json.loads((sandbox_repository / result.context_path).read_text())

    assert context["window_mode"] == "since_previous_successful_podcast"
    assert context["window_start_exclusive"] == "2026-07-29T10:30:00Z"
    assert context["previous_successful_podcast"]["daily_cycle_id"] == ("daily-20260729T100000Z")


def test_context_validation_rejects_tampered_prior_context(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    prior_id = "daily-20260729T100000Z"
    _cycle_manifest(
        sandbox_repository,
        prior_id,
        started_at="2026-07-29T09:00:00Z",
        cutoff="2026-07-29T10:30:00Z",
        podcast_status="succeeded",
    )
    _completed_manifest(sandbox_repository, "podcast-current")
    result = enqueue_daily_podcast(
        sandbox_repository,
        sandbox_settings,
        run_id="podcast-current",
        now=NOW,
    )

    validation = validate_podcast_context(sandbox_repository, daily_cycle_id="podcast-current")
    assert validation.context_path == result.context_path
    assert validation.referenced_file_count == 4

    context = json.loads((sandbox_repository / result.context_path).read_text(encoding="utf-8"))
    prior_context = sandbox_repository / context["previous_successful_podcast"]["context_path"]
    prior_context.write_text(prior_context.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(PodcastError, match="previous successful podcast context hash conflicts"):
        validate_podcast_context(sandbox_repository, daily_cycle_id="podcast-current")


def test_context_aggregates_intervening_cycles_with_exclusive_inclusive_boundaries(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    prior_id = "daily-20260727T090000Z"
    first_id = "daily-20260728T090000Z"
    current_id = "daily-20260730T180000Z"
    first_operation = "01ARZ3NDEKTSV4RRFFQ69G5FAA"
    current_operation = "01ARZ3NDEKTSV4RRFFQ69G5FAB"
    _cycle_manifest(
        sandbox_repository,
        prior_id,
        started_at="2026-07-27T08:00:00Z",
        cutoff="2026-07-27T09:30:00Z",
        podcast_status="succeeded",
    )
    idea = sandbox_repository / "data" / "wiki" / "ideas" / "idea_story.md"
    idea.write_text("---\ntitle: Story\ntype: idea\nstatus: maintained\n---\n", encoding="utf-8")
    concept = sandbox_repository / "data" / "wiki" / "concepts" / "concept_scale.md"
    concept.write_text(
        "---\ntitle: Scale\ntype: concept\nstatus: maintained\n---\n", encoding="utf-8"
    )
    security = sandbox_repository / "data" / "wiki" / "securities" / "security_story.md"
    security.write_text(
        "---\ntitle: Security\ntype: security\nstatus: maintained\n---\n"
        "Background: [[ideas/idea_story]] and [[concepts/concept_scale]].\n",
        encoding="utf-8",
    )
    _cycle_manifest(
        sandbox_repository,
        first_id,
        started_at="2026-07-28T08:00:00Z",
        cutoff="2026-07-28T10:00:00Z",
        operations=[{"operation_id": first_operation, "terminal_status": "succeeded"}],
    )
    _accepted_research(
        sandbox_repository,
        cycle_id=first_id,
        operation_id=first_operation,
        completed_at="2026-07-28T09:00:00Z",
        page_path="data/wiki/securities/security_story.md",
        summary="A first accepted research development.",
    )
    _cycle_manifest(
        sandbox_repository,
        current_id,
        started_at="2026-07-30T17:00:00Z",
        cutoff="2026-07-30T18:00:00Z",
        operations=[{"operation_id": current_operation, "terminal_status": "succeeded"}],
    )
    _accepted_research(
        sandbox_repository,
        cycle_id=current_id,
        operation_id=current_operation,
        completed_at="2026-07-30T18:00:00Z",
        page_path="data/wiki/ideas/idea_story.md",
        summary="An inclusive-cutoff accepted development.",
    )

    result = enqueue_daily_podcast(sandbox_repository, sandbox_settings, run_id=current_id, now=NOW)
    context = json.loads((sandbox_repository / result.context_path).read_text())

    assert context["window_start_exclusive"] == "2026-07-27T09:30:00Z"
    assert [item["operation_id"] for item in context["research_developments"]] == [
        first_operation,
        current_operation,
    ]
    assert [item["path"] for item in context["changed_wiki_pages"]] == [
        "data/wiki/ideas/idea_story.md",
        "data/wiki/securities/security_story.md",
    ]
    assert [item["path"] for item in context["background_wiki_pages"]] == [
        "data/wiki/concepts/concept_scale.md"
    ]


def test_context_uses_attempt_provenance_when_operation_is_retried_later(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    attempted_cycle = "daily-20260729T120000Z"
    later_cycle = "daily-20260730T120000Z"
    current_cycle = "daily-20260730T180000Z"
    operation_id = "01ARZ3NDEKTSV4RRFFQ69G5FAC"
    _cycle_manifest(
        sandbox_repository,
        attempted_cycle,
        started_at="2026-07-29T11:00:00Z",
        cutoff="2026-07-29T12:30:00Z",
        operations=[{"operation_id": operation_id, "terminal_status": "failed"}],
    )
    _accepted_research(
        sandbox_repository,
        cycle_id=later_cycle,
        operation_id=operation_id,
        completed_at="2026-07-30T12:00:00Z",
        page_path="data/wiki/ideas/retried_story.md",
        summary="The later retry succeeded.",
    )
    attempt = sandbox_repository / "data" / "runs" / attempted_cycle / operation_id
    attempt.mkdir(parents=True)
    (attempt / "operation_history.json").write_text(
        json.dumps(
            {
                "operation_history_version": 1,
                "daily_cycle_id": attempted_cycle,
                "operation_id": operation_id,
                "operation_type": "idea_research",
                "cycle_disposition": "failed",
            }
        ),
        encoding="utf-8",
    )
    (attempt / "validation_report.json").write_text(
        json.dumps({"errors": ["The first attempt failed validation."]}),
        encoding="utf-8",
    )
    (attempt / "hermes_run.json").write_text(
        json.dumps({"completed_at": "2026-07-29T12:15:00Z"}),
        encoding="utf-8",
    )
    _cycle_manifest(
        sandbox_repository,
        current_cycle,
        started_at="2026-07-30T17:00:00Z",
        cutoff="2026-07-30T18:00:00Z",
    )
    unfinished = sandbox_repository / "data" / "runs" / "daily-unfinished"
    unfinished.mkdir()
    (unfinished / "daily_run.json").write_text(
        json.dumps({"daily_cycle_id": "daily-unfinished", "status": "running"}),
        encoding="utf-8",
    )

    result = enqueue_daily_podcast(
        sandbox_repository, sandbox_settings, run_id=current_cycle, now=NOW
    )
    context = json.loads((sandbox_repository / result.context_path).read_text())

    assert context["research_developments"] == []
    assert [item["operation_id"] for item in context["unresolved_research_gaps"]] == [operation_id]
    gap = context["unresolved_research_gaps"][0]
    assert gap["daily_cycle_id"] == attempted_cycle
    assert gap["result_path"] == (
        f"data/runs/{attempted_cycle}/{operation_id}/validation_report.json"
    )
    assert gap["failure_errors"] == ["The first attempt failed validation."]


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


def test_podcast_render_draft_uses_only_audited_runner_temp(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    cycle_id = "daily-20260730T180000Z"
    script_path = "data/wiki/podcasts/daily-podcast_20260730T180000Z.md"
    markdown = _script(cycle_id)
    page = sandbox_repository / script_path
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(markdown, encoding="utf-8")
    commands: list[list[str]] = []

    def fake_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[object]:
        commands.append(command)
        if "-show_entries" in command:
            return subprocess.CompletedProcess(command, 0, "1200\n", "")
        output = (
            Path(command[command.index("--write-media") + 1])
            if "--write-media" in command
            else Path(command[-1])
        )
        output.write_bytes(b"assembled-audio")
        return subprocess.CompletedProcess(command, 0, "", "")

    output = tmp_path / "papertrader-podcast" / cycle_id
    result = render_draft_podcast(
        sandbox_repository,
        sandbox_settings,
        daily_cycle_id=cycle_id,
        script_path=script_path,
        output_directory=output,
        audit_run_id=cycle_id,
        audit_operation_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
        audit_operation_type="daily_podcast",
        runner=fake_runner,
    )

    assert result.word_count == 3000
    assert result.duration_seconds == 1200
    assert Path(result.audio_path).read_bytes() == b"assembled-audio"
    assert Path(result.manifest_path).is_file()
    assert not list(sandbox_repository.rglob("*.mp3"))
    assert not list(output.glob("chunk-*.mp3"))
    tts_commands = [command for command in commands if "--write-media" in command]
    assert len(tts_commands) == 4
    assert all(command[:3] == [sys.executable, "-m", "edge_tts"] for command in tts_commands)


def test_podcast_script_preflight_uses_the_renderers_exact_text_gates(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    cycle_id = "daily-20260730T180000Z"
    script_path = "data/wiki/podcasts/daily-podcast_20260730T180000Z.md"
    page = sandbox_repository / script_path
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(_script(cycle_id), encoding="utf-8")

    result = validate_podcast_script_file(
        sandbox_repository,
        sandbox_settings,
        daily_cycle_id=cycle_id,
        script_path=script_path,
    )

    assert result.daily_cycle_id == cycle_id
    assert result.script_path == script_path
    assert result.word_count == 3000
    assert 2 <= result.chunk_count <= 12
    assert len(result.script_sha256) == 64


def test_repository_podcast_audio_path_is_rejected(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    with pytest.raises(PodcastError, match="outside the checkout"):
        render_draft_podcast(
            sandbox_repository,
            sandbox_settings,
            daily_cycle_id="daily-20260730T180000Z",
            script_path="data/wiki/podcasts/daily-podcast_20260730T180000Z.md",
            output_directory=sandbox_repository / "data" / "wiki" / "podcasts",
            audit_run_id="daily-20260730T180000Z",
            audit_operation_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            audit_operation_type="daily_podcast",
        )


def test_podcast_render_rejects_visible_machine_identity(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    cycle_id = "daily-20260730T180000Z"
    script_path = "data/wiki/podcasts/daily-podcast_20260730T180000Z.md"
    page = sandbox_repository / script_path
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(_script(cycle_id, extra_body="# security_1234567890abcdef1234\n\n"))

    with pytest.raises(PodcastError, match="exposes a machine identity"):
        render_draft_podcast(
            sandbox_repository,
            sandbox_settings,
            daily_cycle_id=cycle_id,
            script_path=script_path,
            output_directory=tmp_path / "papertrader-podcast" / cycle_id,
            audit_run_id=cycle_id,
            audit_operation_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            audit_operation_type="daily_podcast",
        )


def test_failed_ephemeral_render_removes_completed_chunks(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    cycle_id = "daily-20260730T180001Z"
    script_path = "data/wiki/podcasts/daily-podcast_20260730T180001Z.md"
    markdown = _script(cycle_id)
    page = sandbox_repository / script_path
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(markdown, encoding="utf-8")
    attempts = 0

    def failing_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[object]:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            Path(command[command.index("--write-media") + 1]).write_bytes(b"first-chunk")
            return subprocess.CompletedProcess(command, 0, "", "")
        return subprocess.CompletedProcess(command, 1, "", "tts failed")

    output = tmp_path / "papertrader-podcast" / cycle_id
    delays: list[float] = []
    with pytest.raises(PodcastError, match="chunk 2"):
        render_draft_podcast(
            sandbox_repository,
            sandbox_settings,
            daily_cycle_id=cycle_id,
            script_path=script_path,
            output_directory=output,
            audit_run_id=cycle_id,
            audit_operation_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            audit_operation_type="daily_podcast",
            runner=failing_runner,
            sleeper=delays.append,
        )

    assert attempts == 4
    assert delays == [1.0, 2.0]
    assert list(output.iterdir()) == []


def test_transient_tts_chunk_failure_retries_within_one_draft_render(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    cycle_id = "daily-20260730T180004Z"
    script_path = "data/wiki/podcasts/daily-podcast_20260730T180004Z.md"
    page = sandbox_repository / script_path
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(_script(cycle_id), encoding="utf-8")
    tts_attempts = 0
    delays: list[float] = []

    def flaky_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[object]:
        nonlocal tts_attempts
        if "-show_entries" in command:
            return subprocess.CompletedProcess(command, 0, "1200\n", "")
        if "--write-media" in command:
            tts_attempts += 1
            target = Path(command[command.index("--write-media") + 1])
            if tts_attempts == 1:
                target.write_bytes(b"partial-audio")
                raise FileNotFoundError("bare TTS entrypoint is unavailable")
            assert not target.exists()
            target.write_bytes(b"chunk-audio")
            return subprocess.CompletedProcess(command, 0, b"", b"")
        Path(command[-1]).write_bytes(b"assembled-audio")
        return subprocess.CompletedProcess(command, 0, b"", b"")

    output = tmp_path / "papertrader-podcast" / cycle_id
    result = render_draft_podcast(
        sandbox_repository,
        sandbox_settings,
        daily_cycle_id=cycle_id,
        script_path=script_path,
        output_directory=output,
        audit_run_id=cycle_id,
        audit_operation_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
        audit_operation_type="daily_podcast",
        runner=flaky_runner,
        sleeper=delays.append,
    )

    assert tts_attempts == 5
    assert delays == [1.0]
    assert Path(result.audio_path).read_bytes() == b"assembled-audio"
    assert Path(result.manifest_path).is_file()
    assert not list(output.glob("chunk-*.mp3"))


def test_seal_detects_committed_script_hash_mismatch_without_tts(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    cycle_id = "daily-20260730T180002Z"
    script_path = "data/wiki/podcasts/daily-podcast_20260730T180002Z.md"
    page = sandbox_repository / script_path
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(_script(cycle_id), encoding="utf-8")
    output = tmp_path / "papertrader-podcast" / cycle_id

    def draft_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[object]:
        if "-show_entries" in command:
            return subprocess.CompletedProcess(command, 0, "1200\n", "")
        target = (
            Path(command[command.index("--write-media") + 1])
            if "--write-media" in command
            else Path(command[-1])
        )
        target.write_bytes(b"audio")
        return subprocess.CompletedProcess(command, 0, "", "")

    render_draft_podcast(
        sandbox_repository,
        sandbox_settings,
        daily_cycle_id=cycle_id,
        script_path=script_path,
        output_directory=output,
        audit_run_id=cycle_id,
        audit_operation_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
        audit_operation_type="daily_podcast",
        runner=draft_runner,
    )
    calls: list[list[str]] = []

    def seal_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[object]:
        calls.append(command)
        assert command[:2] == ["git", "show"]
        changed = _script(cycle_id).replace("word word", "changed word", 1)
        return subprocess.CompletedProcess(command, 0, changed.encode(), b"")

    with pytest.raises(PodcastError, match="exact committed transcript"):
        seal_podcast_render(
            sandbox_repository,
            sandbox_settings,
            daily_cycle_id=cycle_id,
            script_commit="a" * 40,
            script_path=script_path,
            output_directory=output,
            runner=seal_runner,
        )
    assert len(calls) == 1
    assert all("edge-tts" not in command for command in calls)


@pytest.mark.parametrize(
    "replacement,error",
    [
        ("word two", "numeric glyphs"),
        ("This is paper trading, not live trading.", "disclaimers"),
        ("- listed prose", "Markdown lists"),
    ],
)
def test_spoken_script_rejects_machine_style_prose(replacement: str, error: str) -> None:
    cycle_id = "daily-20260730T180003Z"
    markdown = _script(cycle_id).replace("word word", replacement, 1)
    if replacement == "word two":
        markdown = markdown.replace("word two", "word 2", 1)
    with pytest.raises(PodcastError, match=error):
        validate_podcast_script(markdown, daily_cycle_id=cycle_id)
