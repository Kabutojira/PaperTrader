from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from papertrader.agent_runner import AgentRunError, configure_hermes_home, run_one_operation
from papertrader.atomic_io import atomic_write_csv
from papertrader.config import Settings
from papertrader.queue import Operation, enqueue_operation
from papertrader.result_validator import (
    _baseline_signal_followup_errors,
    _command_allowed,
    _daily_podcast_text_errors,
    _idea_security_followup_errors,
    _path_allowed_for_operation,
    _research_visualization_errors,
    _security_assessment_result_errors,
    _security_idea_followup_errors,
    _youtube_wiki_ingest_errors,
)
from papertrader.tables import contract_by_name, read_table, write_table

NOW = datetime(2026, 7, 24, 12, tzinfo=UTC)


def _podcast_script(cycle_id: str) -> str:
    paragraphs = [" ".join(["word"] * 375) for _ in range(8)]
    return (
        f"---\ndaily_cycle_id: {cycle_id}\npaper_trading: true\n---\n"
        "<!-- papertrader-spoken-transcript:start -->\n"
        + "\n\n".join(paragraphs)
        + "\n<!-- papertrader-spoken-transcript:end -->\n"
    )


def test_agent_operation_scopes_never_own_generated_allocation_state() -> None:
    protected = (
        "data/tables/allocation_targets.csv",
        "data/tables/allocation_history.csv",
        "data/published/decision_snapshot.json",
        "data/published/model_portfolio.csv",
        "data/published/actionable_signals.csv",
        "data/published/research_benchmark.csv",
    )
    for operation_type in ("security_research", "strategy_research", "execute_strategy"):
        assert all(
            not _path_allowed_for_operation(operation_type, path, created=False)
            for path in protected
        )
    assert _path_allowed_for_operation(
        "security_research",
        "data/tables/security_assessments.csv",
        created=False,
    )
    for source_path in (
        "data/tables/source_registry.csv",
        "data/tables/source_history.csv",
    ):
        assert _path_allowed_for_operation("security_research", source_path, created=False)
    assert _command_allowed(
        "security_research",
        {"argv": ["papertrader", "research", "source", "record"]},
    )
    assert _command_allowed(
        "security_research",
        {"argv": ["papertrader", "allocation", "readiness"]},
    )
    assert _command_allowed(
        "security_research",
        {"argv": ["papertrader", "wiki", "sync-technical-charts"]},
    )
    assert not _command_allowed(
        "idea_research",
        {"argv": ["papertrader", "wiki", "sync-technical-charts"]},
    )
    assert _path_allowed_for_operation(
        "idea_research",
        "data/tables/securities.csv",
        created=False,
    )
    assert _command_allowed(
        "idea_research",
        {"argv": ["papertrader", "watchlist", "import", "--request", "request.json"]},
    )
    assert not _command_allowed(
        "security_research",
        {"argv": ["papertrader", "watchlist", "import", "--request", "request.json"]},
    )
    assert _command_allowed(
        "wiki_ingest",
        {"argv": ["papertrader", "watchlist", "import", "--request", "request.json"]},
        seekingalpha_lead=True,
    )
    assert _command_allowed(
        "source_discovery",
        {"argv": ["papertrader", "seekingalpha", "enqueue-leads", "--request", "lead.json"]},
    )
    assert not _command_allowed(
        "source_discovery",
        {"argv": ["papertrader", "queue", "enqueue", "--request", "lead.json"]},
    )
    assert _command_allowed(
        "wiki_ingest",
        {"argv": ["papertrader", "watchlist", "import", "--request", "request.json"]},
        youtube_video=True,
    )
    assert not _command_allowed(
        "wiki_ingest",
        {"argv": ["papertrader", "watchlist", "import", "--request", "request.json"]},
    )
    assert _path_allowed_for_operation(
        "wiki_ingest",
        "data/tables/securities.csv",
        created=False,
        youtube_video=True,
    )
    assert not _path_allowed_for_operation(
        "wiki_ingest",
        "data/wiki/raw/transcript.txt",
        created=True,
        youtube_video=True,
    )
    assert _path_allowed_for_operation(
        "wiki_ingest",
        "data/tables/securities.csv",
        created=False,
        seekingalpha_lead=True,
    )
    assert not _path_allowed_for_operation(
        "wiki_ingest",
        "data/wiki/raw/seekingalpha-article.txt",
        created=True,
        seekingalpha_lead=True,
    )
    assert _command_allowed(
        "execute_strategy",
        {"argv": ["papertrader", "order", "create-baseline", "--request", "request.json"]},
    )
    assert _command_allowed(
        "daily_podcast",
        {
            "argv": [
                "papertrader",
                "podcast",
                "validate-script",
                "--daily-cycle-id",
                "daily-20260724T120000Z",
            ]
        },
        profile="deep",
    )
    assert _command_allowed(
        "daily_podcast",
        {
            "argv": [
                "papertrader",
                "podcast",
                "render-draft",
                "--daily-cycle-id",
                "daily-20260724T120000Z",
            ]
        },
        profile="deep",
    )
    assert not _command_allowed(
        "security_research",
        {"argv": ["papertrader", "podcast", "validate-script"]},
    )
    assert not _command_allowed(
        "security_research",
        {"argv": ["papertrader", "podcast", "render-draft"]},
    )
    for operation_type in (
        "wiki_ingest",
        "opportunity_research",
        "idea_research",
        "security_research",
        "relationship_research",
        "strategy_research",
        "execute_strategy",
    ):
        assert _path_allowed_for_operation(
            operation_type,
            "data/wiki/research-catalog.md",
            created=False,
        )
    assert not _path_allowed_for_operation(
        "source_discovery",
        "data/wiki/research-catalog.md",
        created=False,
    )


def test_successful_podcast_preflight_must_pass_before_the_single_render(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    cycle_id = "daily-20260724T120000Z"
    page_path = "data/wiki/podcasts/daily-podcast_20260724T120000Z.md"
    report_path = "data/wiki/daily-reports/daily-report_20260724.md"
    operation_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="daily_podcast",
        entity_type="run",
        entity_id=cycle_id,
        dedupe_key=f"daily_podcast:{cycle_id}:research-v3",
        prompt="Create the completed run's daily podcast.",
        inputs={
            "run_id": cycle_id,
            "context_path": f"data/runs/{cycle_id}/podcast_context.json",
            "report_path": report_path,
            "page_path": page_path,
            "target_minutes": 20,
            "target_words": 3000,
        },
        source="test",
        max_attempts=1,
        now=NOW,
    )
    assert created
    operation = replace(
        Operation.from_row(read_table(sandbox_repository, "operations_todo")[0]),
        claimed_by_run_id=cycle_id,
    )
    assert operation.operation_id == operation_id
    page = sandbox_repository / page_path
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(_podcast_script(cycle_id), encoding="utf-8")
    report = sandbox_repository / report_path
    report.write_text(f"Podcast: {page.stem}\n", encoding="utf-8")
    preflight_command = (
        f"papertrader podcast validate-script --daily-cycle-id {cycle_id} --script-path {page_path}"
    )
    render_command = (
        f"papertrader podcast render-draft --daily-cycle-id {cycle_id} --script-path {page_path}"
    )

    def audit_entry(command: str, *, exit_code: int) -> dict[str, object]:
        return {
            "command": command,
            "argv": command.split(),
            "request": None,
            "started_at": "2026-07-24T12:00:00Z",
            "completed_at": "2026-07-24T12:00:01Z",
            "exit_code": exit_code,
            "changed_paths": [],
            "changes": [],
            "profile": "deep",
        }

    audit_path = (
        sandbox_repository / "data" / "runs" / cycle_id / operation_id / "command_audit.json"
    )
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit = {
        "audit_version": 1,
        "run_id": cycle_id,
        "operation_id": operation_id,
        "entries": [
            audit_entry(preflight_command, exit_code=0),
            audit_entry(render_command, exit_code=2),
        ],
        "profile": "deep",
        "profile_policy_version": "profile-router-v1",
        "route_reason": "strict_long_form_podcast_contract",
    }
    audit_path.write_text(json.dumps(audit), encoding="utf-8")

    assert (
        _daily_podcast_text_errors(
            sandbox_repository,
            operation=operation,
            status="succeeded",
            changed_paths=(report_path, page_path),
        )
        == []
    )

    audit["entries"] = list(reversed(audit["entries"]))
    audit_path.write_text(json.dumps(audit), encoding="utf-8")
    errors = _daily_podcast_text_errors(
        sandbox_repository,
        operation=operation,
        status="succeeded",
        changed_paths=(report_path, page_path),
    )
    assert "daily podcast script preflight must pass before draft rendering" in errors


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


def test_youtube_transcript_unavailable_is_a_clean_terminal_skip(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    video_id = "abcdefghijk"
    channel_id = "UCESLZhusAkFfsNsApnjF_Cg"
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    operation_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="wiki_ingest",
        entity_type="source",
        entity_id=f"youtube_{video_id}",
        dedupe_key=f"wiki_ingest:youtube:{channel_id}:{video_id}:v1",
        prompt="Analyze one curated YouTube transcript as an untrusted lead source.",
        inputs={
            "source_kind": "youtube_video",
            "source_id": f"youtube_{video_id}",
            "video_id": video_id,
            "video_title": "Example",
            "video_url": video_url,
            "channel_id": channel_id,
            "channel_handle": "@allin",
            "channel_url": f"https://www.youtube.com/channel/{channel_id}/videos",
            "discovered_at": "2026-07-29T08:00:00Z",
            "transcript_languages": ["en", "en-US", "en-GB"],
            "prefer_human": True,
            "discovery_mode": "bootstrap",
        },
        source="youtube_scan:test",
        priority=60,
        source_refs=(video_url,),
        now=datetime(2026, 7, 29, 8, tzinfo=UTC),
    )
    assert created
    row = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_id"] == operation_id
    )
    operation = Operation.from_row(row)
    result = {
        "status": "skipped",
        "reason_code": "youtube_transcript_unavailable",
    }

    assert (
        _youtube_wiki_ingest_errors(
            sandbox_repository,
            run_id="youtube-skip",
            operation=operation,
            status="skipped",
            result=result,
            changed_paths=(),
            created_operation_ids=set(),
            operation_rows_after={operation_id: row},
            followup_priority=66,
        )
        == []
    )
    result["reason_code"] = "metadata_only"
    assert "requires reason_code youtube_transcript_unavailable" in " ".join(
        _youtube_wiki_ingest_errors(
            sandbox_repository,
            run_id="youtube-skip",
            operation=operation,
            status="skipped",
            result=result,
            changed_paths=(),
            created_operation_ids=set(),
            operation_rows_after={operation_id: row},
            followup_priority=66,
        )
    )


def _enqueue_security(repository: Path, settings: Settings, *, idea_id: str = "") -> str:
    inputs = {"security_id": "sec-test"}
    if idea_id:
        inputs["idea_id"] = idea_id
    operation_id, _ = enqueue_operation(
        repository,
        settings,
        operation_type="security_research",
        entity_type="security",
        entity_id="sec-test",
        dedupe_key="security_research:sec-test:fixture:2026-07-24",
        prompt="Research one bounded security.",
        inputs=inputs,
        source="test",
        now=NOW,
    )
    return operation_id


def test_completed_security_research_requires_exact_linked_idea_refresh(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    idea_id = "idea-linked"
    operation_id = _enqueue_security(
        sandbox_repository,
        sandbox_settings,
        idea_id=idea_id,
    )
    security_row = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_id"] == operation_id
    )
    operation = Operation.from_row(security_row)

    assert _security_idea_followup_errors(
        sandbox_repository,
        run_id="research-run",
        operation=operation,
        status="succeeded",
        operation_rows_after={operation_id: security_row},
    ) == [
        "completed security research requires exactly one matching idea_research follow-up "
        f"for {idea_id}"
    ]

    _followup_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="idea_research",
        entity_type="idea",
        entity_id=idea_id,
        dedupe_key=f"idea_research:{idea_id}:security-result:{operation_id}",
        prompt="Update the linked idea from one completed security review.",
        inputs={
            "idea_id": idea_id,
            "seed_claim": "The completed security review may change the linked idea.",
            "security_id": "sec-test",
            "security_research_operation_id": operation_id,
            "security_research_result_path": (
                f"data/runs/research-run/{operation_id}/agent_result.json"
            ),
        },
        source="security-research-followup",
        depends_on=(operation_id,),
        now=NOW,
    )
    assert created
    rows_after = {
        row["operation_id"]: row for row in read_table(sandbox_repository, "operations_todo")
    }

    assert (
        _security_idea_followup_errors(
            sandbox_repository,
            run_id="research-run",
            operation=operation,
            status="succeeded",
            operation_rows_after=rows_after,
        )
        == []
    )


def test_idea_created_security_research_is_identity_linked_and_dependency_ordered(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    idea_id = "idea-linked"
    idea_operation_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="idea_research",
        entity_type="idea",
        entity_id=idea_id,
        dedupe_key=f"idea_research:{idea_id}:fixture:2026-07-24",
        prompt="Research one bounded idea and its investable candidates.",
        inputs={"idea_id": idea_id, "seed_claim": "A bounded evidence-backed idea."},
        source="test",
        now=NOW,
    )
    assert created
    idea_row = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_id"] == idea_operation_id
    )
    idea_operation = Operation.from_row(idea_row)
    security_operation_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="security_research",
        entity_type="security",
        entity_id="sec-candidate",
        dedupe_key="security_research:sec-candidate:idea-linked:2026-07-24",
        prompt="Research one evidence-backed idea candidate.",
        inputs={"security_id": "sec-candidate", "idea_id": idea_id},
        source="idea-research-followup",
        depends_on=(idea_operation_id,),
        now=NOW,
    )
    assert created
    rows_after = {
        row["operation_id"]: row for row in read_table(sandbox_repository, "operations_todo")
    }

    assert (
        _idea_security_followup_errors(
            sandbox_repository,
            operation=idea_operation,
            status="succeeded",
            created_operation_ids={security_operation_id},
            operation_rows_after=rows_after,
        )
        == []
    )
    invalid_rows = {key: dict(value) for key, value in rows_after.items()}
    invalid_rows[security_operation_id]["depends_on"] = ""
    assert _idea_security_followup_errors(
        sandbox_repository,
        operation=idea_operation,
        status="succeeded",
        created_operation_ids={security_operation_id},
        operation_rows_after=invalid_rows,
    ) == [
        "idea-created security research must carry the idea/security identities and depend on "
        f"the idea operation: {security_operation_id}"
    ]


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
        "visualization_review": {
            "completed": True,
            "charts": [],
            "omissions": [
                {
                    "dataset": "bounded trigger evidence",
                    "reason_code": "no_page_change",
                    "reason": "The fixture changes no primary research page.",
                }
            ],
        },
        "validation": {"passed": True, "checks": ["bounded no-op"]},
    }


def test_research_visualization_manifest_matches_changed_page_chart_ids(
    sandbox_repository: Path, sandbox_settings: Settings
) -> None:
    operation_id = _enqueue(sandbox_repository, sandbox_settings)
    operation = Operation.from_row(read_table(sandbox_repository, "operations_todo")[0])
    page_path = "data/wiki/queries/chart-fixture.md"
    chart = {
        "schema_version": 1,
        "chart_id": "trigger-comparison",
        "kind": "composition",
        "title": "Trigger comparison",
        "description": "Three comparable trigger observations.",
        "as_of": "2026-07-24T10:00:00Z",
        "sources": [{"label": "Normalized market fixture"}],
        "display": "bar",
        "axis": {"label": "Return", "unit": "%", "format": "percent"},
        "items": [
            {"label": "Day 1", "value": "-1.2"},
            {"label": "Day 2", "value": "0.4"},
            {"label": "Day 3", "value": "2.1"},
        ],
    }
    page = sandbox_repository / page_path
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        "## Visual evidence\n\n```echart\n" + json.dumps(chart) + "\n```\n",
        encoding="utf-8",
    )
    result = _manifest(operation_id, [page_path])
    result["visualization_review"] = {
        "completed": True,
        "charts": [{"page_path": page_path, "chart_id": "trigger-comparison"}],
        "omissions": [],
    }

    assert (
        _research_visualization_errors(
            sandbox_repository,
            operation=operation,
            status="succeeded",
            result=result,
            changed_paths=(page_path,),
        )
        == []
    )


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
            environment={"PATH": "/usr/bin", "OPENROUTER_API_KEY": "test-auxiliary-key"},
            operation_id=operation_id,
            executor=_executor_with_change(change, ["src/papertrader/malicious.py"]),
        )


def test_out_of_scope_command_error_names_rejected_command(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    operation_id = _enqueue(sandbox_repository, sandbox_settings)
    home = _home(sandbox_repository, sandbox_settings, tmp_path)
    rejected_command = "papertrader watchlist import --request unexpected.json"

    def execute(
        command: Sequence[str],
        cwd: Path,
        environment: Mapping[str, str],
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        del timeout
        run_id = environment["PAPERTRADER_AUDIT_RUN_ID"]
        selected_operation = environment["PAPERTRADER_AUDIT_OPERATION_ID"]
        artifact = cwd / "data" / "runs" / run_id / selected_operation
        (artifact / "command_audit.json").write_text(
            json.dumps(
                {
                    "audit_version": 1,
                    "run_id": run_id,
                    "operation_id": selected_operation,
                    "entries": [
                        {
                            "command": rejected_command,
                            "argv": [
                                "papertrader",
                                "watchlist",
                                "import",
                                "--request",
                                "unexpected.json",
                            ],
                            "request": None,
                            "started_at": "2026-07-24T12:00:00Z",
                            "completed_at": "2026-07-24T12:00:01Z",
                            "exit_code": 0,
                            "changed_paths": [],
                            "changes": [],
                        }
                    ],
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        result = _manifest(selected_operation, [])
        result["commands_run"] = [rejected_command]
        (artifact / "agent_result.json").write_text(
            json.dumps(result, sort_keys=True), encoding="utf-8"
        )
        return subprocess.CompletedProcess(command, 0, "", "")

    with pytest.raises(AgentRunError, match=rejected_command):
        run_one_operation(
            sandbox_repository,
            sandbox_settings,
            run_id="bad-command-scope",
            hermes_home=home,
            environment={"PATH": "/usr/bin", "OPENROUTER_API_KEY": "test-auxiliary-key"},
            operation_id=operation_id,
            executor=execute,
        )


def test_completed_security_research_without_assessment_fails_closed(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    operation_id = _enqueue_security(sandbox_repository, sandbox_settings)
    home = _home(sandbox_repository, sandbox_settings, tmp_path)

    with pytest.raises(AgentRunError, match="requires this run's comparable assessment"):
        run_one_operation(
            sandbox_repository,
            sandbox_settings,
            run_id="missing-assessment",
            hermes_home=home,
            environment={"PATH": "/usr/bin", "OPENROUTER_API_KEY": "test-auxiliary-key"},
            operation_id=operation_id,
            executor=_executor_with_change(lambda root: None, []),
        )


def test_skipped_security_research_without_current_assessment_is_safe_noop(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    paper_environment: dict[str, str],
) -> None:
    operation_id = _enqueue_security(sandbox_repository, sandbox_settings)
    row = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_id"] == operation_id
    )
    operation = Operation.from_row(row)

    errors = _security_assessment_result_errors(
        sandbox_repository,
        operation=operation,
        status="skipped",
        run_id="skipped-assessment",
        environment={
            **paper_environment,
            "WIKI_PATH": str(sandbox_repository / "data" / "wiki"),
        },
    )
    assert errors == []


def test_unchanged_quick_check_can_reuse_fresh_existing_assessment(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    paper_environment: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    operation_id = _enqueue_security(sandbox_repository, sandbox_settings)
    row = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_id"] == operation_id
    )
    operation = replace(Operation.from_row(row), operation_type="quick_check_research")
    contract = contract_by_name(sandbox_repository, "security_assessments")
    assessment = {column: "" for column in contract.columns}
    assessment.update({"security_id": "sec-test", "run_id": "prior-research"})
    write_table(sandbox_repository, "security_assessments", [assessment])
    monkeypatch.setattr(
        "papertrader.allocation._assessment_readiness_errors",
        lambda *_args, **_kwargs: [],
    )
    environment = {
        **paper_environment,
        "WIKI_PATH": str(sandbox_repository / "data" / "wiki"),
    }

    assert (
        _security_assessment_result_errors(
            sandbox_repository,
            operation=operation,
            status="succeeded",
            run_id="quick-check-noop",
            environment=environment,
            changed_paths=(),
        )
        == []
    )
    assert _security_assessment_result_errors(
        sandbox_repository,
        operation=operation,
        status="succeeded",
        run_id="quick-check-with-delta",
        environment=environment,
        changed_paths=("data/wiki/securities/sec-test.md",),
    ) == ["completed security research requires this run's comparable assessment"]


def test_state_changing_research_assessment_must_belong_to_current_operation(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    paper_environment: dict[str, str],
) -> None:
    operation_id = _enqueue_security(sandbox_repository, sandbox_settings)
    operation = Operation.from_row(
        next(
            row
            for row in read_table(sandbox_repository, "operations_todo")
            if row["operation_id"] == operation_id
        )
    )
    contract = contract_by_name(sandbox_repository, "security_assessments")
    assessment = {column: "" for column in contract.columns}
    assessment.update(
        {
            "security_id": "sec-test",
            "run_id": "same-run",
        }
    )
    write_table(sandbox_repository, "security_assessments", [assessment])
    history_contract = contract_by_name(sandbox_repository, "security_assessment_history")
    history = {column: "" for column in history_contract.columns}
    history.update(
        {
            "assessment_id": "assessment_other_operation",
            "security_id": "sec-test",
            "run_id": "same-run",
            "source_operation_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "source_result_path": (
                "data/runs/same-run/01ARZ3NDEKTSV4RRFFQ69G5FAV/agent_result.json"
            ),
        }
    )
    atomic_write_csv(
        sandbox_repository.joinpath(*history_contract.path.parts),
        history_contract.columns,
        [history],
        allowed_root=sandbox_repository,
    )

    assert _security_assessment_result_errors(
        sandbox_repository,
        operation=operation,
        status="succeeded",
        run_id="same-run",
        environment={
            **paper_environment,
            "WIKI_PATH": str(sandbox_repository / "data" / "wiki"),
        },
    ) == ["completed security research assessment source operation mismatch"]


def test_baseline_signal_requires_one_exact_execute_strategy_followup(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    strategy_id = "strategy_baseline_test"
    strategy_operation_id, _ = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="strategy_research",
        entity_type="strategy",
        entity_id=strategy_id,
        dedupe_key="strategy_research:strategy_baseline_test:plan:test",
        prompt="Review one baseline strategy target.",
        inputs={"strategy_id": strategy_id, "relationship_id": "relationship_test"},
        source="test",
        now=NOW,
    )
    operation = Operation.from_row(
        next(
            row
            for row in read_table(sandbox_repository, "operations_todo")
            if row["operation_id"] == strategy_operation_id
        )
    )
    write_table(
        sandbox_repository,
        "strategies",
        [
            {
                "strategy_id": strategy_id,
                "idea_id": "idea_test",
                "security_id": "sec-test",
                "relationship_id": "relationship_test",
                "name": "Baseline test",
                "status": "ready",
                "direction": "long",
                "instrument_type": "equity",
                "thesis": "Fixture",
                "entry_rule": "Fixture",
                "exit_rule": "Fixture",
                "invalidation": "Fixture",
                "risk_budget_pct": "1",
                "sleeve": "baseline",
                "allocation_plan_id": "allocation_plan_test",
                "not_before": "",
                "expires_at": "",
                "research_page": "data/wiki/strategies/strategy_baseline_test.md",
                "created_at": "2026-07-24T12:00:00Z",
                "updated_at": "2026-07-24T12:00:00Z",
            }
        ],
    )
    signal_id = "signal_baseline_test"
    write_table(
        sandbox_repository,
        "signals",
        [
            {
                "signal_id": signal_id,
                "strategy_id": strategy_id,
                "signal_type": "open",
                "created_at": "2026-07-24T12:00:00Z",
                "expires_at": "2026-07-25T12:00:00Z",
                "status": "ready",
                "rationale": "Fixture",
                "market_data_as_of": "2026-07-24T12:00:00Z",
                "order_request_path": "",
                "telegram_sent_at": "",
                "run_id": "baseline-followup",
            }
        ],
    )
    rows_before = {
        row["operation_id"]: row for row in read_table(sandbox_repository, "operations_todo")
    }
    assert _baseline_signal_followup_errors(
        sandbox_repository,
        run_id="baseline-followup",
        operation=operation,
        created_operation_ids=set(),
        operation_rows_after=rows_before,
    ) == [
        "baseline signal requires exactly one matching execute_strategy follow-up: "
        "signal_baseline_test"
    ]

    execute_id, created = enqueue_operation(
        sandbox_repository,
        sandbox_settings,
        operation_type="execute_strategy",
        entity_type="strategy",
        entity_id=strategy_id,
        dedupe_key="execute_strategy:strategy_baseline_test:signal_baseline_test",
        prompt="Review the baseline paper signal for execution.",
        inputs={"strategy_id": strategy_id, "signal_id": signal_id, "action": "open"},
        source="strategy-research:test",
        now=NOW,
    )
    assert created
    rows_after = {
        row["operation_id"]: row for row in read_table(sandbox_repository, "operations_todo")
    }
    assert (
        _baseline_signal_followup_errors(
            sandbox_repository,
            run_id="baseline-followup",
            operation=operation,
            created_operation_ids={execute_id},
            operation_rows_after=rows_after,
        )
        == []
    )


def test_manifest_cannot_claim_an_unchanged_file(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    operation_id = _enqueue(sandbox_repository, sandbox_settings)
    home = _home(sandbox_repository, sandbox_settings, tmp_path)

    with pytest.raises(AgentRunError, match="claims paths absent from the actual delta"):
        run_one_operation(
            sandbox_repository,
            sandbox_settings,
            run_id="stale-result",
            hermes_home=home,
            environment={"PATH": "/usr/bin", "OPENROUTER_API_KEY": "test-auxiliary-key"},
            operation_id=operation_id,
            executor=_executor_with_change(lambda root: None, ["data/wiki/index.md"]),
        )


def test_controller_reconciles_omitted_bookkeeping_from_authoritative_state(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    tmp_path: Path,
) -> None:
    operation_id = _enqueue(sandbox_repository, sandbox_settings)
    home = _home(sandbox_repository, sandbox_settings, tmp_path)
    changed_path = "data/wiki/log.md"
    audited_command = "papertrader wiki lint --strict"

    def execute(
        command: Sequence[str],
        cwd: Path,
        environment: Mapping[str, str],
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        del timeout
        run_id = environment["PAPERTRADER_AUDIT_RUN_ID"]
        selected_operation = environment["PAPERTRADER_AUDIT_OPERATION_ID"]
        artifact = cwd / "data" / "runs" / run_id / selected_operation
        log = cwd / changed_path
        log.write_text(
            log.read_text(encoding="utf-8") + "\nReconciled fixture.\n",
            encoding="utf-8",
        )
        (artifact / "agent_result.json").write_text(
            json.dumps(_manifest(selected_operation, [])), encoding="utf-8"
        )
        (artifact / "command_audit.json").write_text(
            json.dumps(
                {
                    "audit_version": 1,
                    "run_id": run_id,
                    "operation_id": selected_operation,
                    "entries": [
                        {
                            "command": audited_command,
                            "argv": audited_command.split(),
                            "request": None,
                            "started_at": "2026-07-24T12:00:00Z",
                            "completed_at": "2026-07-24T12:00:01Z",
                            "exit_code": 0,
                            "changed_paths": [],
                            "changes": [],
                            "profile": "",
                        }
                    ],
                    "profile": "",
                    "profile_policy_version": "profile-router-v1",
                    "route_reason": "fixture",
                }
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 0, "", "")

    run_one_operation(
        sandbox_repository,
        sandbox_settings,
        run_id="reconciled-result",
        hermes_home=home,
        environment={"PATH": "/usr/bin", "OPENROUTER_API_KEY": "test-auxiliary-key"},
        operation_id=operation_id,
        executor=execute,
    )

    result_path = (
        sandbox_repository
        / "data"
        / "runs"
        / "reconciled-result"
        / operation_id
        / "agent_result.json"
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["files_changed"] == [changed_path]
    assert result["commands_run"] == [audited_command]


def test_manifest_cannot_claim_an_unaudited_command(
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
        selected_operation = environment["PAPERTRADER_AUDIT_OPERATION_ID"]
        artifact = (
            cwd / "data" / "runs" / environment["PAPERTRADER_AUDIT_RUN_ID"] / selected_operation
        )
        result = _manifest(selected_operation, [])
        result["commands_run"] = ["papertrader issue record --request invented.json"]
        (artifact / "agent_result.json").write_text(json.dumps(result), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    with pytest.raises(AgentRunError, match="without deterministic CLI audit receipts"):
        run_one_operation(
            sandbox_repository,
            sandbox_settings,
            run_id="invented-command",
            hermes_home=home,
            environment={"PATH": "/usr/bin", "OPENROUTER_API_KEY": "test-auxiliary-key"},
            operation_id=operation_id,
            executor=execute,
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
            environment={"PATH": "/usr/bin", "OPENROUTER_API_KEY": "test-auxiliary-key"},
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
            environment={"PATH": "/usr/bin", "OPENROUTER_API_KEY": "test-auxiliary-key"},
            operation_id=operation_id,
            executor=execute,
        )
    assert (sandbox_repository / "data" / "tables" / "issues.csv").is_file()
