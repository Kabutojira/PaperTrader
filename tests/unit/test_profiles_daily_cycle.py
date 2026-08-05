from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from papertrader.checkpoints import CheckpointError, create_checkpoint
from papertrader.config import Settings
from papertrader.daily import (
    record_cycle_checkpoint,
    record_cycle_operation,
    resume_or_create_daily_cycle,
)
from papertrader.integrity import is_runtime_path_allowed, validate_daily_run_artifacts
from papertrader.profiles import (
    RoutingContext,
    analyst_relationship_gate,
    profile_command_allowed,
    route_profile,
)

NOW = datetime(2026, 8, 4, 15, tzinfo=UTC)
OPERATION_ID = "01K1W0M0000000000000000000"


def test_profile_router_is_deterministic_and_promotes_sensitive_work() -> None:
    assert route_profile("source_discovery", RoutingContext()).profile == "scout"
    assert route_profile("wiki_ingest", RoutingContext()).profile == "analyst"
    assert route_profile("security_research", RoutingContext()).profile == "deep"
    promoted = route_profile("quick_check_research", RoutingContext(current_holding=True))
    assert promoted.profile == "deep"
    assert promoted.route_reason == "portfolio_sensitive_conclusion"
    assert route_profile("daily_podcast", RoutingContext()).profile == "analyst"
    escalation = route_profile(
        "opportunity_research",
        RoutingContext(decision_change=True),
        escalation_source="analyst",
    )
    assert escalation.profile == "deep"
    assert escalation.route_reason.startswith("escalated:analyst:")
    with pytest.raises(ValueError, match="move one way"):
        route_profile("wiki_ingest", RoutingContext(), escalation_source="analyst")


def test_profile_command_authority_blocks_decision_mutations() -> None:
    assessment = ("research", "assessment", "upsert")
    relationship = ("research", "relationship", "upsert")
    signal = ("signal", "create")
    assert profile_command_allowed("scout", assessment) is False
    assert profile_command_allowed("scout", relationship) is False
    assert profile_command_allowed("analyst", assessment) is False
    assert profile_command_allowed("analyst", relationship) is True
    assert profile_command_allowed("analyst", signal) is False
    assert profile_command_allowed("deep", signal) is True


def test_analyst_relationship_gate_allows_only_unchanged_refresh(
    sandbox_repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from papertrader import profiles

    previous = {
        "relationship_id": "relationship_example",
        "idea_id": "idea_example",
        "security_id": "security_example",
        "relationship_type": "beneficiary",
        "direction": "positive",
        "mechanism": "Demand increases.",
        "sensitivity": "medium",
        "confidence": "medium",
        "catalyst": "Adoption",
        "invalidation": "Demand falls.",
        "status": "accepted",
    }
    monkeypatch.setattr(profiles, "read_table", lambda *_: [previous])
    assert analyst_relationship_gate(sandbox_repository, previous) is True
    changed = {**previous, "confidence": "high"}
    assert analyst_relationship_gate(sandbox_repository, changed) is False
    assert (
        analyst_relationship_gate(
            sandbox_repository,
            {**previous, "relationship_id": "relationship_new"},
        )
        is False
    )


def test_daily_cycle_resume_consumes_original_count_and_weighted_budget(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    cycle = resume_or_create_daily_cycle(
        sandbox_repository,
        sandbox_settings,
        trigger="workflow_dispatch",
        source_sha="a" * 40,
        github_run_id="123",
        workflow_attempt="1",
        now=NOW,
    )
    cycle_id = str(cycle["daily_cycle_id"])
    record_cycle_checkpoint(
        sandbox_repository, daily_cycle_id=cycle_id, kind="preparation", now=NOW
    )
    operation_directory = sandbox_repository / "data" / "runs" / cycle_id / OPERATION_ID
    operation_directory.mkdir()
    (operation_directory / "profile_route.json").write_text(
        json.dumps(
            {
                "profile": "analyst",
                "profile_policy_version": "profile-router-v1",
                "route_reason": "routine_research_or_long_form_synthesis",
                "effective_model": "gpt-5.6-terra",
                "reasoning_effort": "medium",
                "maximum_turns": 80,
                "timeout_seconds": 1200,
                "weighted_cost": "2.5",
                "mutation_policy": "routine_research",
                "auxiliary_models": {"web_extract": "openai-codex:gpt-5.6-terra"},
                "escalation_source": "",
            }
        ),
        encoding="utf-8",
    )
    accepted = record_cycle_operation(
        sandbox_repository,
        daily_cycle_id=cycle_id,
        operation_id=OPERATION_ID,
        terminal_status="succeeded",
    )
    assert accepted["checkpoint_index"] == 1
    resumed = resume_or_create_daily_cycle(
        sandbox_repository,
        sandbox_settings,
        trigger="workflow_dispatch",
        source_sha="a" * 40,
        github_run_id="123",
        workflow_attempt="2",
        now=NOW + timedelta(minutes=5),
    )
    assert resumed["daily_cycle_id"] == cycle_id
    assert resumed["remaining_operations"] == resumed["maximum_operations"] - 1
    assert resumed["weighted_model_budget_used"] == "2.5"
    assert len(resumed["workflow_attempts"]) == 2
    assert validate_daily_run_artifacts(sandbox_repository) == []


def test_audio_extensions_are_never_runtime_paths() -> None:
    assert not is_runtime_path_allowed("data/wiki/podcasts/daily-podcast_20260804.mp3")
    assert not is_runtime_path_allowed("data/runs/cycle/chunk-01.wav")
    assert not is_runtime_path_allowed("data/runs/cycle/audio.m4a")
    assert is_runtime_path_allowed("data/wiki/podcasts/daily-podcast_20260804T150000Z.md")


def test_dry_checkpoint_creates_local_trailered_commit_without_push(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=sandbox_repository,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=sandbox_repository, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=sandbox_repository,
        check=True,
    )
    subprocess.run(["git", "add", "--all"], cwd=sandbox_repository, check=True)
    subprocess.run(
        ["git", "commit", "-m", "baseline"],
        cwd=sandbox_repository,
        check=True,
        capture_output=True,
    )
    from papertrader import checkpoints

    monkeypatch.setattr(checkpoints, "validate_checkpoint_state", lambda *_: ())
    issue_page = sandbox_repository / "data" / "issues.md"
    issue_page.write_text(issue_page.read_text() + "\nCheckpoint fixture.\n", encoding="utf-8")
    run_artifact = (
        sandbox_repository / "data" / "runs" / "daily-20260804T150000Z" / "checkpoint.json"
    )
    run_artifact.parent.mkdir(parents=True)
    run_artifact.write_text("{}\n", encoding="utf-8")

    result = create_checkpoint(
        sandbox_repository,
        sandbox_settings,
        daily_cycle_id="daily-20260804T150000Z",
        checkpoint_index=3,
        kind="operation",
        operation_id=OPERATION_ID,
        operation_type="opportunity_research",
        terminal_status="succeeded",
        profile="analyst",
        dry_run=True,
    )

    assert result.dry_run is True
    assert result.pushed is False
    assert "data/runs/daily-20260804T150000Z/checkpoint.json" in result.changed_paths
    assert (
        subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=sandbox_repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        == "papertrader-dry-run-daily-20260804T150000Z"
    )
    message = subprocess.run(
        ["git", "show", "-s", "--format=%B", "HEAD"],
        cwd=sandbox_repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "PaperTrader-Checkpoint: 003" in message
    assert "PaperTrader-Profile: analyst" in message

    media = sandbox_repository / "data" / "wiki" / "podcasts" / "forbidden.mp3"
    media.parent.mkdir(parents=True, exist_ok=True)
    media.write_bytes(b"audio")
    with pytest.raises(CheckpointError, match="runtime path is not allowed"):
        create_checkpoint(
            sandbox_repository,
            sandbox_settings,
            daily_cycle_id="daily-20260804T150000Z",
            checkpoint_index=4,
            kind="operation",
            dry_run=True,
        )
