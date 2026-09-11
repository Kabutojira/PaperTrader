from __future__ import annotations

import json
import os
import shutil
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from papertrader.atomic_io import atomic_write_csv, atomic_write_json
from papertrader.buy_review import BuyReviewPending, accept_review, packet_for_operation
from papertrader.config import Settings, load_settings
from papertrader.integrity import load_csv_contracts
from papertrader.issues import regenerate_issue_dashboard
from papertrader.logs import regenerate_log_tail
from papertrader.models import RiskAssessment
from papertrader.orders import create_paper_order
from papertrader.queue import Operation
from papertrader.tables import read_table
from papertrader.utils import format_timestamp

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


def accept_test_buy_review(
    root: Path,
    settings: Settings,
    operation: Operation,
    *,
    accepted_at: datetime,
    decision: str = "APPROVE",
    model: str = "gpt-6-astra",
) -> dict[str, Any]:
    """Simulate authenticated parent acceptance for an explicit test-only review."""
    packet = packet_for_operation(root, operation)
    review = {
        "review_request_id": packet["review_request_id"],
        "packet_hash": packet["packet_hash"],
        "decision": decision,
        "reason": "Independent fixture review",
        "examined_evidence": ["fixture:primary"],
        "counterevidence": "Competing explanation examined",
        "material_issues": [],
        "uncertainty": "Demand may miss assumptions",
        "reconsideration_conditions": [],
    }
    result = {
        "operation_id": operation.operation_id,
        "status": "succeeded",
        "summary": "Independent fixture review approved the exact purchase packet.",
        "evidence": [
            {
                "source": "test-only authenticated reviewer fixture",
                "claim": "The exact immutable purchase packet was independently reviewed.",
                "url": "https://example.test/papertrader/final-buy-review",
                "observed_at": format_timestamp(accepted_at),
            }
        ],
        "files_changed": [],
        "operations_created": [],
        "issues_recorded": [],
        "daily_report_items": [],
        "commands_run": [],
        "validation": {
            "passed": True,
            "checks": ["test-only authenticated final review completed"],
        },
        "final_buy_review": review,
    }
    run_id = "test-reviewer"
    directory = root / "data" / "runs" / run_id / operation.operation_id
    directory.mkdir(parents=True, exist_ok=True)
    provenance = {
        "run_id": run_id,
        "operation_id": operation.operation_id,
        "profile": "final_review",
        "completed_at": format_timestamp(accepted_at),
    }
    for filename, value in {
        "hermes_run.json": {
            **provenance,
            "model": model,
            "provider": "openai-codex",
            "reasoning_effort": "high",
            "returncode": 0,
        },
        "validation_report.json": {**provenance, "passed": True},
        "agent_result.json": result,
    }.items():
        atomic_write_json(directory / filename, value, allowed_root=root)
    return accept_review(root, settings, operation, result, run_id=run_id, now=accepted_at)


def create_reviewed_paper_order(
    root: Path,
    settings: Settings,
    *,
    order_factory: Callable[..., tuple[str, bool, RiskAssessment]] = create_paper_order,
    **kwargs: Any,
) -> tuple[str, bool, RiskAssessment]:
    """Exercise the mandatory review round trip before creating a test purchase."""
    with pytest.raises(BuyReviewPending) as pending:
        order_factory(root, settings, **kwargs)
    operation = next(
        Operation.from_row(row)
        for row in read_table(root, "operations_todo")
        if row["dedupe_key"] == f"final_buy_review:{pending.value.review_request_id}"
    )
    accepted_at = kwargs.get("now")
    if not isinstance(accepted_at, datetime):
        raise AssertionError("reviewed paper-order fixtures require an explicit now timestamp")
    accept_test_buy_review(root, settings, operation, accepted_at=accepted_at)
    return order_factory(root, settings, **kwargs)


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
