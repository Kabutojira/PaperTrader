from __future__ import annotations

import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from papertrader.atomic_io import atomic_write_csv
from papertrader.config import Settings, load_settings
from papertrader.integrity import load_csv_contracts
from papertrader.issues import regenerate_issue_dashboard
from papertrader.logs import regenerate_log_tail

EMPTY_DATA_DIRECTORIES = (
    "logs",
    "market/prices",
    "market/fx",
    "market/snapshots",
    "operations/payloads",
    "operations/prompts",
    "runs",
    "tables",
    "wiki/_archive",
    "wiki/_meta",
    "wiki/comparisons",
    "wiki/concepts",
    "wiki/daily-reports",
    "wiki/ideas",
    "wiki/inbox",
    "wiki/queries",
    "wiki/raw",
    "wiki/relationships",
    "wiki/securities",
    "wiki/strategies",
)


@pytest.fixture
def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def paper_environment(repository_root: Path) -> dict[str, str]:
    return {
        "PAPER_TRADING_ONLY": "true",
        "WIKI_PATH": str(repository_root / "data" / "wiki"),
    }


@pytest.fixture
def sandbox_repository(repository_root: Path, tmp_path: Path) -> Path:
    """Create an empty repository from contracts, independent of live runtime data."""

    target = tmp_path / "PaperTrader"
    target.mkdir()
    for name in (".gitattributes", "AGENTS.md", "PLAN.md", "config.ini"):
        shutil.copy2(repository_root / name, target / name)
    for name in ("schemas", "skills"):
        shutil.copytree(repository_root / name, target / name)

    for relative_path in EMPTY_DATA_DIRECTORIES:
        (target / "data" / relative_path).mkdir(parents=True, exist_ok=True)

    shutil.copy2(
        repository_root / "data" / "wiki" / "SCHEMA.md",
        target / "data" / "wiki" / "SCHEMA.md",
    )
    wiki_seed = repository_root / "tests" / "fixtures" / "repository_seed" / "wiki"
    for name in ("index.md", "log.md"):
        shutil.copy2(wiki_seed / name, target / "data" / "wiki" / name)

    for contract in load_csv_contracts(target):
        destination = target.joinpath(*contract.path.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_csv(destination, contract.columns, [], allowed_root=target)

    regenerate_issue_dashboard(target)
    regenerate_log_tail(target)
    return target


@pytest.fixture
def sandbox_settings(sandbox_repository: Path) -> Settings:
    settings = load_settings(
        sandbox_repository,
        {
            "PAPER_TRADING_ONLY": "true",
            "WIKI_PATH": str(sandbox_repository / "data" / "wiki"),
        },
    )
    # Most deterministic fixtures exercise report generation without operation handoff.
    # Default-active behavior is asserted separately against the versioned config.
    return replace(settings, allocation=replace(settings.allocation, mode="report_only"))
