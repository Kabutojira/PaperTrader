from __future__ import annotations

import json
from pathlib import Path

from papertrader.cli import main
from papertrader.tables import read_table
from papertrader.utils import parse_timestamp


def _set_paper_environment(monkeypatch, repository_root: Path) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("PAPER_TRADING_ONLY", "true")
    monkeypatch.setenv("WIKI_PATH", str(repository_root / "data" / "wiki"))


def test_cli_validation_commands_pass(monkeypatch, repository_root: Path) -> None:  # type: ignore[no-untyped-def]
    _set_paper_environment(monkeypatch, repository_root)
    prefix = ["--repository", str(repository_root)]

    assert main([*prefix, "schema", "validate", "--strict"]) == 0
    assert main([*prefix, "integrity", "--strict"]) == 0
    assert main([*prefix, "wiki", "lint", "--strict"]) == 0
    assert main([*prefix, "portfolio", "reconcile", "--strict"]) == 0


def test_cli_fails_closed_without_paper_environment(monkeypatch, repository_root: Path) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("PAPER_TRADING_ONLY", raising=False)
    monkeypatch.setenv("WIKI_PATH", str(repository_root / "data" / "wiki"))

    assert main(["--repository", str(repository_root), "schema", "validate"]) == 2


def test_cli_runtime_whitelist_rejects_source_path(monkeypatch, repository_root: Path) -> None:  # type: ignore[no-untyped-def]
    _set_paper_environment(monkeypatch, repository_root)

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
    _set_paper_environment(monkeypatch, sandbox_repository)
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
