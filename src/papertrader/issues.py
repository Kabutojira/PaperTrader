"""Repository-local issue lifecycle and generated human-readable dashboard."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path

from papertrader.atomic_io import atomic_write_text
from papertrader.tables import read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    format_timestamp,
    stable_id,
    utc_now,
)

ISSUE_STATUSES = frozenset({"open", "resolved"})
ISSUE_SEVERITIES = frozenset({"info", "warning", "error", "critical"})


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _dashboard(rows: Sequence[Mapping[str, str]]) -> str:
    open_rows = sorted(
        (row for row in rows if row["status"] == "open"),
        key=lambda row: (
            {"critical": 0, "error": 1, "warning": 2, "info": 3}.get(row["severity"], 4),
            row["issue_id"],
        ),
    )
    lines = ["# PaperTrader issues", "", "Generated from `data/tables/issues.csv`.", ""]
    if not open_rows:
        lines.extend(["No open issues.", ""])
        return "\n".join(lines)
    lines.extend(
        [
            "| Severity | Issue | Last seen | Owner | Related operation |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in open_rows:
        title = _cell(row["title"])
        lines.append(
            f"| {_cell(row['severity'])} | **{_cell(row['issue_id'])}** — {title} | "
            f"{_cell(row['last_seen_at'])} | {_cell(row['owner'])} | "
            f"{_cell(row['related_operation_id'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def regenerate_issue_dashboard(repository_root: Path) -> None:
    """Regenerate ``data/issues.md`` from canonical issue state."""

    content = _dashboard(read_table(repository_root, "issues"))
    atomic_write_text(
        repository_root / "data" / "issues.md",
        content,
        allowed_root=repository_root,
    )


def record_issue(
    repository_root: Path,
    *,
    severity: str,
    title: str,
    description: str,
    owner: str = "",
    related_run_id: str = "",
    related_operation_id: str = "",
    now: datetime | None = None,
) -> str:
    """Create or refresh one stable open issue and regenerate its dashboard."""

    if severity not in ISSUE_SEVERITIES:
        raise CanonicalValueError(f"unknown issue severity: {severity!r}")
    title = " ".join(title.split())
    description = " ".join(description.split())
    owner = " ".join(owner.split())
    related_run_id = " ".join(related_run_id.split())
    related_operation_id = " ".join(related_operation_id.split())
    if not title or not description:
        raise CanonicalValueError("issue title and description are required")
    issue_id = stable_id("issue", title.casefold(), related_operation_id)
    timestamp = format_timestamp(now or utc_now())
    rows = read_table(repository_root, "issues")
    previous = next((row for row in rows if row["issue_id"] == issue_id), None)
    row = {
        "issue_id": issue_id,
        "status": "open",
        "severity": severity,
        "title": title,
        "description": description,
        "owner": owner,
        "first_seen_at": previous["first_seen_at"] if previous else timestamp,
        "last_seen_at": timestamp,
        "related_run_id": previous["related_run_id"] if previous else related_run_id,
        "related_operation_id": related_operation_id,
        "resolution": "",
        "resolved_at": "",
    }
    output = [candidate for candidate in rows if candidate["issue_id"] != issue_id]
    output.append(row)
    output.sort(key=lambda candidate: candidate["issue_id"])
    write_table(repository_root, "issues", output)
    regenerate_issue_dashboard(repository_root)
    return issue_id


def resolve_issue(
    repository_root: Path,
    issue_id: str,
    resolution: str,
    *,
    now: datetime | None = None,
) -> None:
    """Resolve an existing issue without deleting its canonical history row."""

    resolution = " ".join(resolution.split())
    if not resolution:
        raise CanonicalValueError("issue resolution is required")
    rows = read_table(repository_root, "issues")
    timestamp = format_timestamp(now or utc_now())
    found = False
    for row in rows:
        if row["issue_id"] != issue_id:
            continue
        found = True
        if row["status"] == "resolved":
            if row["resolution"] != resolution:
                raise CanonicalValueError(f"issue {issue_id} is already resolved differently")
            return
        row["status"] = "resolved"
        row["resolution"] = resolution
        row["resolved_at"] = timestamp
        row["last_seen_at"] = timestamp
    if not found:
        raise CanonicalValueError(f"unknown issue: {issue_id}")
    write_table(repository_root, "issues", rows)
    regenerate_issue_dashboard(repository_root)
