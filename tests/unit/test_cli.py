from __future__ import annotations

from pathlib import Path

from papertrader.cli import main


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
