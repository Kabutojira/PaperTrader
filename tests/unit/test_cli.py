from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from papertrader.advice import refresh_advice
from papertrader.agent_runner import HermesPreflight, SkillIdentity
from papertrader.cli import main
from papertrader.config import Settings
from papertrader.execution import ensure_initial_capital
from papertrader.tables import read_table
from papertrader.utils import parse_timestamp


def _set_repository_environment(monkeypatch, repository_root: Path) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("WIKI_PATH", str(repository_root / "data" / "wiki"))


def test_cli_validation_commands_pass(monkeypatch, repository_root: Path) -> None:  # type: ignore[no-untyped-def]
    _set_repository_environment(monkeypatch, repository_root)
    prefix = ["--repository", str(repository_root)]

    assert main([*prefix, "schema", "validate", "--strict"]) == 0
    assert main([*prefix, "integrity", "--strict"]) == 0
    assert main([*prefix, "wiki", "lint", "--strict"]) == 0
    assert main([*prefix, "portfolio", "reconcile", "--strict"]) == 0


def test_cli_refreshes_results_first_wiki_homepage(
    monkeypatch,  # type: ignore[no-untyped-def]
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    _set_repository_environment(monkeypatch, sandbox_repository)
    as_of = datetime(2026, 7, 24, 12, tzinfo=UTC)
    ensure_initial_capital(
        sandbox_repository,
        sandbox_settings,
        run_id="homepage-test",
        occurred_at=as_of,
    )
    refresh_advice(
        sandbox_repository,
        sandbox_settings,
        run_id="homepage-test",
        as_of=as_of,
    )

    assert (
        main(
            [
                "--repository",
                str(sandbox_repository),
                "wiki",
                "refresh-homepage",
            ]
        )
        == 0
    )
    homepage = (sandbox_repository / "data" / "wiki" / "index.md").read_text(encoding="utf-8")
    assert homepage.index("No trade — hold 100% cash") < homepage.index("## Explore")
    assert "**No actionable trade signals.**" in homepage
    assert "| Cash | 100% | 100% |" in homepage


def test_cli_strict_allocation_readiness_fails_for_unbackfilled_universe(
    monkeypatch, repository_root: Path
) -> None:  # type: ignore[no-untyped-def]
    _set_repository_environment(monkeypatch, repository_root)

    assert (
        main(
            [
                "--repository",
                str(repository_root),
                "allocation",
                "readiness",
                "--strict",
            ]
        )
        == 1
    )


def test_cli_starts_without_a_mode_environment_switch(monkeypatch, repository_root: Path) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("WIKI_PATH", str(repository_root / "data" / "wiki"))

    assert main(["--repository", str(repository_root), "schema", "validate"]) == 0


def test_cli_agent_preflight_serializes_profile_weighted_cost(
    monkeypatch, repository_root: Path, tmp_path: Path, capsys
) -> None:  # type: ignore[no-untyped-def]
    _set_repository_environment(monkeypatch, repository_root)
    skill = SkillIdentity("skill", "1", "skills/skill/SKILL.md", "a" * 64)
    report = HermesPreflight(
        native_skill=skill,
        controller_skill=skill,
        operation_skill=skill,
        config_sha256="b" * 64,
        provider="openai-codex",
        model="gpt-5.6-terra",
        web_extract_provider="openai-codex",
        web_extract_model="gpt-5.6-terra",
        web_extract_reasoning_effort="low",
        maximum_turns=80,
        profile="analyst",
        profile_policy_version="profile-router-v1",
        route_reason="routine_research_or_long_form_synthesis",
        reasoning_effort="medium",
        timeout_seconds=1200,
        weighted_cost=Decimal("2.5"),
        mutation_policy="routine_research",
        escalation_source="",
    )
    monkeypatch.setattr("papertrader.cli.preflight_hermes", lambda *args, **kwargs: report)

    assert (
        main(
            [
                "--repository",
                str(repository_root),
                "agent",
                "preflight",
                "--hermes-home",
                str(tmp_path / "hermes"),
                "--operation-type",
                "wiki_ingest",
            ]
        )
        == 0
    )
    output = json.loads(capsys.readouterr().out)
    assert output["weighted_cost"] == "2.5"


def test_cli_runtime_whitelist_rejects_source_path(monkeypatch, repository_root: Path) -> None:  # type: ignore[no-untyped-def]
    _set_repository_environment(monkeypatch, repository_root)

    assert (
        main(
            [
                "--repository",
                str(repository_root),
                "runtime-whitelist",
                "validate",
                "data/wiki/index.md",
                "src/papertrader/cli.py",
            ]
        )
        == 1
    )


def test_queue_enqueue_converts_literal_now_to_canonical_utc(
    monkeypatch,  # type: ignore[no-untyped-def]
    sandbox_repository: Path,
) -> None:
    _set_repository_environment(monkeypatch, sandbox_repository)
    request = sandbox_repository / "data" / "operations" / "enqueue-now.json"
    request.write_text(
        json.dumps(
            {
                "operation_type": "idea_research",
                "entity_type": "idea",
                "entity_id": "idea_now",
                "dedupe_key": "idea_research:idea_now:manual:2026-07-24",
                "prompt": "Research one manually queued idea.",
                "inputs": {"idea_id": "idea_now", "seed_claim": "Synthetic claim."},
                "source": "manual",
                "priority": 50,
                "freshness_days": 0,
                "depends_on": [],
                "not_before": "now",
                "deadline": "",
                "source_refs": [],
                "max_attempts": 3,
            }
        ),
        encoding="utf-8",
    )

    assert (
        main(
            [
                "--repository",
                str(sandbox_repository),
                "queue",
                "enqueue",
                "--request",
                str(request),
            ]
        )
        == 0
    )
    not_before = read_table(sandbox_repository, "operations_todo")[0]["not_before"]
    assert not_before != "now"
    assert parse_timestamp(not_before) is not None
