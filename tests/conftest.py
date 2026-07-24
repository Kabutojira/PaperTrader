from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def paper_environment(repository_root: Path) -> dict[str, str]:
    return {
        "PAPER_TRADING_ONLY": "true",
        "WIKI_PATH": str(repository_root / "data" / "wiki"),
    }
