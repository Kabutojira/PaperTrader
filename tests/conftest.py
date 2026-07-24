from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from papertrader.config import Settings, load_settings


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
    """Copy only persistent contracts needed by mutating, network-free tests."""

    target = tmp_path / "PaperTrader"
    target.mkdir()
    for name in (".gitattributes", "AGENTS.md", "PLAN.md", "config.ini"):
        shutil.copy2(repository_root / name, target / name)
    for name in ("schemas", "data", "skills"):
        shutil.copytree(repository_root / name, target / name)
    return target


@pytest.fixture
def sandbox_settings(sandbox_repository: Path) -> Settings:
    return load_settings(
        sandbox_repository,
        {
            "PAPER_TRADING_ONLY": "true",
            "WIKI_PATH": str(sandbox_repository / "data" / "wiki"),
        },
    )
