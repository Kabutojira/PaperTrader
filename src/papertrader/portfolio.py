"""Portfolio generation and reconciliation boundary."""

from __future__ import annotations

import csv
from pathlib import Path


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def reconcile_portfolio(repository_root: Path) -> list[str]:
    """Reconcile the empty Step 1 ledger scaffold and fail closed on populated state."""

    executions = _rows(repository_root / "data" / "tables" / "executions.csv")
    cash_entries = _rows(repository_root / "data" / "tables" / "cash_ledger.csv")
    positions = _rows(repository_root / "data" / "tables" / "portfolio.csv")
    if positions and not executions:
        return ["portfolio contains positions without executions"]
    if executions or cash_entries or positions:
        return ["non-empty accounting reconciliation is unavailable until Step 2"]
    return []
