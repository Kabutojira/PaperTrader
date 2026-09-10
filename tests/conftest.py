from __future__ import annotations

import json
import os
import shutil
from dataclasses import replace
from decimal import Decimal
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
    "published",
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
    for name in ("index.md", "research-catalog.md", "log.md"):
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
            "WIKI_PATH": str(sandbox_repository / "data" / "wiki"),
        },
    )
    # Most deterministic fixtures exercise report generation without operation handoff.
    # Default-active behavior is asserted separately against the versioned config.
    return replace(
        settings,
        allocation=replace(settings.allocation, mode="report_only"),
        # Accounting scenario fixtures intentionally retain a large round-number balance;
        # production account size is asserted directly in test_config.py.
        portfolio=replace(settings.portfolio, initial_capital=Decimal("100000.00")),
    )


class ReferenceOutputs:
    """Golden files under tests/reference_outputs, regenerable on demand.

    Run ``PAPERTRADER_UPDATE_REFERENCES=1 uv run pytest <test>`` to rewrite a golden file from
    the current behaviour after an intentional change (for example a ``config.ini`` edit, which
    changes every decision snapshot identity). Review the resulting diff before committing.
    """

    def __init__(self, repository_root: Path) -> None:
        self.directory = repository_root / "tests" / "reference_outputs"
        self.update = os.environ.get("PAPERTRADER_UPDATE_REFERENCES", "") == "1"

    def text(self, name: str, actual: str) -> str:
        path = self.directory / name
        if self.update:
            path.write_text(actual, encoding="utf-8")
        return path.read_text(encoding="utf-8")

    def json(self, name: str, actual: object, *, key: str | None = None) -> object:
        path = self.directory / name
        raw = path.read_text(encoding="utf-8") if path.is_file() else "{}\n"
        document = json.loads(raw)
        if self.update:
            if key is None:
                document = actual
            else:
                document[key] = actual
            sort_keys = json.dumps(json.loads(raw), indent=2, sort_keys=True) + "\n" == raw
            path.write_text(
                json.dumps(document, indent=2, sort_keys=sort_keys, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        return document if key is None else document[key]


@pytest.fixture
def reference_outputs(repository_root: Path) -> ReferenceOutputs:
    return ReferenceOutputs(repository_root)
