"""Deterministic canonical daily-report generation with evidence-linked narrative slots."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path, PurePosixPath

import yaml

from papertrader.atomic_io import atomic_write_text
from papertrader.tables import read_table
from papertrader.utils import CanonicalValueError, ensure_utc, parse_timestamp, utc_now
from papertrader.wiki import register_wiki_page

RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


@dataclass(frozen=True, slots=True)
class NarrativeItem:
    """One original LLM narrative sentence plus explicit evidence references."""

    text: str
    evidence_refs: tuple[str, ...]


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ") or "—"


def _today(timestamp: str, report_date: date) -> bool:
    if not timestamp:
        return False
    parsed = parse_timestamp(timestamp)
    return parsed is not None and parsed.date() == report_date


def _wiki_changes(wiki_root: Path, report_date: date) -> tuple[str, ...]:
    changes: list[str] = []
    for path in sorted(wiki_root.rglob("*.md")):
        relative = path.relative_to(wiki_root)
        if relative.parts[0] in {"raw", "daily-reports"} or relative.name in {
            "SCHEMA.md",
            "index.md",
            "log.md",
        }:
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            continue
        raw, _ = text[4:].split("\n---\n", maxsplit=1)
        metadata = yaml.safe_load(raw)
        if (
            isinstance(metadata, dict)
            and str(metadata.get("updated", "")) == report_date.isoformat()
        ):
            changes.append(relative.with_suffix("").as_posix())
    return tuple(changes)


def _run_wiki_changes(repository_root: Path, run_id: str) -> tuple[str, ...]:
    """Return maintained wiki pages changed by this run even across UTC dates."""

    changes: set[str] = set()
    run_directory = repository_root / "data" / "runs" / run_id
    for path in sorted(run_directory.glob("*/agent_result.json")):
        try:
            result = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CanonicalValueError(f"cannot read run result {path.name}: {exc}") from exc
        raw_paths = result.get("files_changed") if isinstance(result, dict) else None
        if not isinstance(raw_paths, list) or not all(
            isinstance(raw_path, str) for raw_path in raw_paths
        ):
            raise CanonicalValueError(f"run result has invalid files_changed: {path}")
        for raw_path in raw_paths:
            relative = PurePosixPath(raw_path)
            if (
                len(relative.parts) >= 4
                and relative.parts[:2] == ("data", "wiki")
                and relative.parts[2] not in {"_archive", "_meta", "daily-reports", "inbox", "raw"}
                and relative.suffix == ".md"
            ):
                changes.add(PurePosixPath(*relative.parts[2:]).with_suffix("").as_posix())
    return tuple(sorted(changes))


def _validate_narratives(items: Sequence[NarrativeItem]) -> tuple[NarrativeItem, ...]:
    validated: list[NarrativeItem] = []
    for item in items:
        text = " ".join(item.text.split())
        if not text or len(text) > 1000:
            raise CanonicalValueError("daily narrative item must contain 1 to 1,000 characters")
        if not item.evidence_refs or any(
            not reference or len(reference) > 500 or any(marker in reference for marker in "\r\n")
            for reference in item.evidence_refs
        ):
            raise CanonicalValueError("daily narrative item requires one-line evidence references")
        validated.append(
            NarrativeItem(text=text, evidence_refs=tuple(sorted(set(item.evidence_refs))))
        )
    return tuple(validated)


def _allocation_summary(repository_root: Path, run_id: str) -> Mapping[str, object] | None:
    path = repository_root / "data" / "runs" / run_id / "allocation_plan.json"
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise CanonicalValueError("allocation summary must be a regular run artifact")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CanonicalValueError(f"cannot read allocation summary: {exc}") from exc
    if (
        not isinstance(value, dict)
        or value.get("allocation_plan_version") != 1
        or value.get("run_id") != run_id
        or not isinstance(value.get("unallocated_reasons"), list)
        or not all(isinstance(reason, str) and reason for reason in value["unallocated_reasons"])
    ):
        raise CanonicalValueError("allocation summary identity is invalid")
    return value


def generate_daily_report(
    repository_root: Path,
    *,
    run_id: str,
    run_status: str,
    report_date: date | None = None,
    narrative_items: Sequence[NarrativeItem] = (),
    github_report_url: str = "",
    generated_at: datetime | None = None,
) -> Path:
    """Generate the single canonical numerical report consumed by Quartz and Telegram."""

    instant = ensure_utc(generated_at or utc_now()).replace(microsecond=0)
    normalized_status = " ".join(run_status.split())
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise CanonicalValueError(f"invalid report run_id: {run_id!r}")
    if not normalized_status or len(normalized_status) > 64:
        raise CanonicalValueError("report run status must contain 1 to 64 characters")
    if github_report_url and (
        not github_report_url.startswith("https://github.com/")
        or any(marker in github_report_url for marker in "\r\n")
    ):
        raise CanonicalValueError("GitHub report URL must be an HTTPS github.com URL")
    day = report_date or instant.date()
    narratives = _validate_narratives(narrative_items)
    latest = read_table(repository_root, "market_latest")
    orders = [
        row
        for row in read_table(repository_root, "orders")
        if row["run_id"] == run_id or _today(row["created_at"], day)
    ]
    executions = [
        row
        for row in read_table(repository_root, "executions")
        if row["run_id"] == run_id or _today(row["executed_at"], day)
    ]
    portfolio = read_table(repository_root, "portfolio")
    performance = next(
        (
            row
            for row in read_table(repository_root, "performance_daily")
            if row["date"] == day.isoformat()
        ),
        None,
    )
    history = [
        row
        for row in read_table(repository_root, "operations_history")
        if row["claimed_by_run_id"] == run_id or _today(row["completed_at"], day)
    ]
    active_operations = read_table(repository_root, "operations_todo")
    allocation_summary = _allocation_summary(repository_root, run_id)
    allocation_targets = [
        row for row in read_table(repository_root, "allocation_targets") if row["run_id"] == run_id
    ]
    issues = [row for row in read_table(repository_root, "issues") if row["status"] == "open"]
    wiki_changes = tuple(
        sorted(
            {
                *_wiki_changes(repository_root / "data" / "wiki", day),
                *_run_wiki_changes(repository_root, run_id),
            }
        )
    )
    lines = [
        "---",
        f'title: "PaperTrader daily report — {day.isoformat()}"',
        "type: daily-report",
        "status: maintained",
        "tags:",
        "  - daily-report",
        f'created: "{day.isoformat()}"',
        f'updated: "{day.isoformat()}"',
        "provenance: deterministic-report-generator",
        f'run_id: "{run_id}"',
        "---",
        "",
        f"# PaperTrader daily report — {day.isoformat()}",
        "",
        "## 1. Run status and data freshness",
        "",
        f"- Run: `{run_id}`",
        f"- Status: `{normalized_status}`",
        f"- Generated (UTC): `{instant.isoformat().replace('+00:00', 'Z')}`",
        "",
        "| Security | Price date | Retrieved at | Status | Error |",
        "| --- | --- | --- | --- | --- |",
    ]
    if latest:
        lines.extend(
            f"| {_cell(row['security_id'])} | {_cell(row['price_date'])} | "
            f"{_cell(row['retrieved_at'])} | {_cell(row['status'])} | {_cell(row['error'])} |"
            for row in latest
        )
    else:
        lines.append("| — | — | — | no monitored securities | — |")
    lines.extend(
        [
            "",
            "## 2. Orders and executions",
            "",
            "### Orders created",
            "",
            "| Order | Strategy | Policy | Status | Created |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(
        (
            f"| {_cell(row['order_id'])} | {_cell(row['strategy_id'])} | "
            f"{_cell(row['fill_policy'])} | {_cell(row['status'])} | {_cell(row['created_at'])} |"
            for row in orders
        )
        if orders
        else ["| — | — | — | no orders | — |"]
    )
    lines.extend(
        [
            "",
            "### Executions",
            "",
            "| Execution | Order | Security | Side | Quantity | Fill | Fees |",
            "| --- | --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    lines.extend(
        (
            f"| {_cell(row['execution_id'])} | {_cell(row['order_id'])} | "
            f"{_cell(row['security_id'])} | {_cell(row['side'])} | {_cell(row['quantity'])} | "
            f"{_cell(row['fill_price'])} {_cell(row['currency'])} | {_cell(row['fees'])} |"
            for row in executions
        )
        if executions
        else ["| — | — | — | — | 0 | no executions | 0 |"]
    )
    lines.extend(["", "## 3. Current portfolio, cash, exposure, and P/L", ""])
    if performance:
        base_currency = performance["base_currency"]
        lines.extend(
            [
                f"- Cash: {performance['cash_base']} {base_currency}",
                f"- Equity: {performance['equity_base']} {base_currency}",
                f"- Gross exposure: {performance['gross_exposure_base']} {base_currency}",
                f"- Net exposure: {performance['net_exposure_base']} {base_currency}",
                f"- Realized P/L: {performance['realized_pnl_base']} {base_currency}",
                f"- Unrealized P/L: {performance['unrealized_pnl_base']} {base_currency}",
                f"- Daily return: {performance['daily_return_pct']}%",
                f"- Cumulative return: {performance['cumulative_return_pct']}%",
            ]
        )
    else:
        lines.append("No performance snapshot was generated for this date.")
    lines.extend(
        [
            "",
            "| Position | Security | Instrument | Side | Quantity | Mark | "
            "Market value (base) | Unrealized P/L |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    lines.extend(
        (
            f"| {_cell(row['position_id'])} | {_cell(row['security_id'])} | "
            f"{_cell(row['instrument_type'])} | {_cell(row['side'])} | {_cell(row['quantity'])} | "
            f"{_cell(row['current_price'])} {_cell(row['currency'])} | "
            f"{_cell(row['market_value_base'])} | {_cell(row['unrealized_pnl_base'])} |"
            for row in portfolio
        )
        if portfolio
        else ["| — | — | — | — | 0 | — | 0 | 0 |"]
    )
    lines.extend(
        [
            "",
            "## 4. Opportunity-cost-aware allocation",
            "",
        ]
    )
    if allocation_summary is None:
        lines.append("No allocation plan was generated for this run.")
    else:
        base_currency = performance["base_currency"] if performance else "base currency"
        lines.extend(
            [
                f"- Allocation mode: `{allocation_summary['mode']}`",
                f"- Cash: {allocation_summary['cash_base']} {base_currency}",
                "- Minimum cash reserve: "
                f"{allocation_summary['minimum_cash_reserve_base']} {base_currency}",
                "- Current invested exposure: "
                f"{allocation_summary['current_gross_exposure_base']} {base_currency}",
                "- Target invested exposure: "
                f"{allocation_summary['target_invested_exposure_base']} {base_currency}",
                "- Current conviction exposure: "
                f"{allocation_summary['current_conviction_exposure_base']} {base_currency}",
                "- Current baseline exposure: "
                f"{allocation_summary['current_baseline_exposure_base']} {base_currency}",
                "- Maximum baseline exposure: "
                f"{allocation_summary['maximum_baseline_exposure_base']} {base_currency}",
                f"- Deployment budget: {allocation_summary['deployment_budget_base']} "
                f"{base_currency}",
                f"- Capital allocated this plan: {allocation_summary['capital_allocated_base']} "
                f"{base_currency}",
                f"- Capital left unallocated: {allocation_summary['capital_unallocated_base']} "
                f"{base_currency}",
                f"- Eligible candidate count: {allocation_summary['eligible_candidate_count']}",
                f"- Excluded candidate count: {allocation_summary['excluded_candidate_count']}",
            ]
        )
        unallocated = str(allocation_summary["capital_unallocated_base"])
        if unallocated not in {"0", "0.0", "0.00"}:
            summary_reasons = allocation_summary["unallocated_reasons"]
            assert isinstance(summary_reasons, list)
            reasons = sorted(
                {str(reason) for reason in summary_reasons}
                | {
                    reason
                    for row in allocation_targets
                    for reason in row["reason"].split("|")
                    if reason not in {"", "above_cash_hurdle", "target_unchanged"}
                }
            )
            if not allocation_targets:
                reasons.append("insufficient_eligible_candidates")
            lines.extend(
                [
                    "",
                    "Cash remains unallocated because: "
                    + ", ".join(f"`{reason}`" for reason in sorted(set(reasons))),
                ]
            )
    lines.extend(
        [
            "",
            "| Rank | Security | Sleeve | Effective score | Current weight | Pending weight | "
            "Target weight | Delta | Disposition | Reason | Assessment date |",
            "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    lines.extend(
        (
            f"| {_cell(row['rank'])} | {_cell(row['security_id'])} | {_cell(row['sleeve'])} | "
            f"{_cell(row['effective_score'])} | {_cell(row['current_weight_pct'])}% | "
            f"{_cell(row['pending_weight_pct'])}% | {_cell(row['target_weight_pct'])}% | "
            f"{_cell(row['delta_value_base'])} | {_cell(row['disposition'])} | "
            f"{_cell(row['reason'])} | {_cell(row['assessment_as_of'])} |"
            for row in sorted(
                allocation_targets,
                key=lambda value: (int(value["rank"] or "999999"), value["security_id"]),
            )
        )
        if allocation_targets
        else ["| — | — | baseline | — | 0% | 0% | 0% | 0 | no candidates | — | — |"]
    )
    lines.extend(
        [
            "",
            "## 5. Research operations and dispositions",
            "",
            "| Operation | Type | Entity | Disposition | Reason |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(
        (
            f"| {_cell(row['operation_id'])} | {_cell(row['operation_type'])} | "
            f"{_cell(row['entity_id'])} | {_cell(row['terminal_status'])} | "
            f"{_cell(row['terminal_reason'])} |"
            for row in history
        )
        if history
        else ["| — | — | — | no completed operations | — |"]
    )
    if narratives:
        lines.extend(["", "### Evidence-linked narrative", ""])
        for item in narratives:
            references = ", ".join(f"`{reference}`" for reference in item.evidence_refs)
            lines.append(f"- {item.text} Evidence: {references}.")
    lines.extend(["", "## 6. New or changed research entities", ""])
    lines.extend(
        [f"- [[{page_key}]]" for page_key in wiki_changes]
        if wiki_changes
        else ["No maintained research pages changed today."]
    )
    lines.extend(["", "## 7. Risks, blockers, and scheduled follow-ups", ""])
    if issues:
        lines.extend(
            f"- `{row['severity']}` **{row['issue_id']}** — {row['title']}" for row in issues
        )
    else:
        lines.append("No open issues.")
    if active_operations:
        lines.extend(
            ["", "### Active operation queue", ""]
            + [
                f"- `{row['status']}` {row['operation_id']} — {row['operation_type']} "
                f"for `{row['entity_id']}`"
                for row in active_operations
            ]
        )
    else:
        lines.extend(["", "No scheduled follow-up operations."])
    lines.extend(
        [
            "",
            "## 8. Links",
            "",
            "- [[index|Wiki index]]",
            f"- GitHub report: {github_report_url or 'not published yet'}",
            "",
        ]
    )
    path = (
        repository_root
        / "data"
        / "wiki"
        / "daily-reports"
        / f"daily-report_{day.strftime('%Y%m%d')}.md"
    )
    atomic_write_text(path, "\n".join(lines), allowed_root=repository_root)
    register_wiki_page(
        repository_root / "data" / "wiki",
        page_key=f"daily-reports/{path.stem}",
        label=f"Daily report {day.isoformat()}",
        section="Daily reports",
        event=f"Generated canonical [[daily-reports/{path.stem}]] for run `{run_id}`.",
        event_date=day,
    )
    return path
