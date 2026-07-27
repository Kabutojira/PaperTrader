"""Deterministic canonical daily-report generation with evidence-linked narrative slots."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from pathlib import Path, PurePosixPath

import yaml

from papertrader.atomic_io import atomic_write_text
from papertrader.tables import read_table
from papertrader.utils import CanonicalValueError, ensure_utc, parse_timestamp, utc_now
from papertrader.wiki import register_wiki_page

RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
DAILY_REPORT_STEM_PATTERN = re.compile(r"^daily-report_(\d{4})(\d{2})(\d{2})$")
HOME_RESULTS_START = "<!-- papertrader-current-results:start -->"
HOME_RESULTS_END = "<!-- papertrader-current-results:end -->"
HOME_SUGGESTION_LIMIT = 3
HOME_SUGGESTION_MAX_CHARS = 400


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


def _markdown_text(value: str) -> str:
    """Render canonical data as inert one-line Markdown text."""

    normalized = " ".join(value.split())
    escaped = escape(normalized, quote=False).replace("\\", "\\\\")
    return re.sub(r"([`*_\[\]])", r"\\\1", escaped)


def _wikilink_label(value: str) -> str:
    return " ".join(value.split()).replace("|", " / ").replace("[", "").replace("]", "")


def _summary_excerpt(value: str) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= HOME_SUGGESTION_MAX_CHARS:
        return normalized
    clipped = normalized[: HOME_SUGGESTION_MAX_CHARS - 3].rsplit(" ", maxsplit=1)[0]
    return f"{clipped}..."


def _security_references(
    repository_root: Path,
) -> tuple[Path, Mapping[str, Mapping[str, str]]]:
    wiki_root = repository_root / "data" / "wiki"
    securities = {row["security_id"]: row for row in read_table(repository_root, "securities")}
    return wiki_root, securities


def _entity_reference(
    wiki_root: Path,
    securities: Mapping[str, Mapping[str, str]],
    *,
    entity_type: str,
    entity_id: str,
    aliased: bool = True,
) -> str:
    prefixes = {
        "idea": "ideas",
        "relationship": "relationships",
        "security": "securities",
        "strategy": "strategies",
    }
    prefix = prefixes.get(entity_type)
    if entity_type == "security" and entity_id in securities:
        security = securities[entity_id]
        ticker = f" ({security['ticker']})" if security["ticker"] else ""
        label = _wikilink_label(f"{security['company_name']}{ticker}")
    else:
        label = _wikilink_label(entity_id)
    safe_entity_id = re.fullmatch(r"[A-Za-z0-9_.:-]+", entity_id) is not None
    if prefix and safe_entity_id:
        page = wiki_root / prefix / f"{entity_id}.md"
        if page.is_file() and not page.is_symlink():
            link = f"[[{prefix}/{entity_id}]]"
            return f"[[{prefix}/{entity_id}|{label}]]" if aliased else f"{link} - {label}"
    if safe_entity_id:
        return f"`{entity_id}`"
    return _markdown_text(entity_id)


def _latest_report_page_key(wiki_root: Path) -> tuple[str, date] | None:
    candidates: list[tuple[str, date]] = []
    for path in sorted((wiki_root / "daily-reports").glob("daily-report_*.md")):
        if path.is_symlink() or not path.is_file():
            continue
        match = DAILY_REPORT_STEM_PATTERN.fullmatch(path.stem)
        if match is None:
            continue
        report_date = date(*(int(value) for value in match.groups()))
        candidates.append((f"daily-reports/{path.stem}", report_date))
    return (
        max(candidates, key=lambda candidate: (candidate[1], candidate[0])) if candidates else None
    )


def _homepage_portfolio_lines(repository_root: Path) -> list[str]:
    performance_rows = read_table(repository_root, "performance_daily")
    performance = (
        max(
            performance_rows,
            key=lambda row: (row["date"], row["generated_at"], row["run_id"]),
        )
        if performance_rows
        else None
    )
    portfolio = sorted(read_table(repository_root, "portfolio"), key=lambda row: row["position_id"])
    wiki_root, securities = _security_references(repository_root)
    lines = ["### Current portfolio", ""]
    if performance is None:
        lines.append("No current performance snapshot is available.")
        base_currency = "base"
    else:
        base_currency = performance["base_currency"]
        lines.extend(
            [
                f"Snapshot date: **{performance['date']}**",
                "",
                "| Cash | Equity | Gross exposure | Realized P/L | Unrealized P/L | "
                "Daily return | Cumulative return |",
                "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
                f"| {performance['cash_base']} {base_currency} | "
                f"{performance['equity_base']} {base_currency} | "
                f"{performance['gross_exposure_base']} {base_currency} | "
                f"{performance['realized_pnl_base']} {base_currency} | "
                f"{performance['unrealized_pnl_base']} {base_currency} | "
                f"{performance['daily_return_pct']}% | "
                f"{performance['cumulative_return_pct']}% |",
            ]
        )
    lines.append("")
    if not portfolio:
        lines.append("No open paper positions; the portfolio is currently held in cash.")
        return lines
    lines.extend(
        [
            "| Security | Instrument | Side | Quantity | Average cost | Mark | "
            f"Market value ({base_currency}) | Unrealized P/L ({base_currency}) |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in portfolio:
        security = _entity_reference(
            wiki_root,
            securities,
            entity_type="security",
            entity_id=row["security_id"],
            aliased=False,
        )
        lines.append(
            f"| {_cell(security)} | {_cell(row['instrument_type'])} | {_cell(row['side'])} | "
            f"{_cell(row['quantity'])} | {_cell(row['average_cost'])} {_cell(row['currency'])} | "
            f"{_cell(row['current_price'])} {_cell(row['currency'])} | "
            f"{_cell(row['market_value_base'])} | {_cell(row['unrealized_pnl_base'])} |"
        )
    return lines


def _homepage_suggestion_lines(repository_root: Path) -> list[str]:
    history = [
        row
        for row in read_table(repository_root, "operations_history")
        if row["terminal_status"] in {"succeeded", "skipped"} and row["result_summary"].strip()
    ]
    history.sort(key=lambda row: (row["completed_at"], row["operation_id"]), reverse=True)
    wiki_root, securities = _security_references(repository_root)
    lines = ["### Latest suggestions and research conclusions", ""]
    for row in history[:HOME_SUGGESTION_LIMIT]:
        entity = _entity_reference(
            wiki_root,
            securities,
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
        )
        operation = _markdown_text(row["operation_type"].replace("_", " "))
        completed = _markdown_text(row["completed_at"])
        summary = _markdown_text(_summary_excerpt(row["result_summary"]))
        lines.append(f"- **{completed} — {operation} for {entity}:** {summary}")
    if len(lines) == 2:
        lines.append("No completed research suggestions are available yet.")
    return lines


def refresh_wiki_homepage(repository_root: Path, *, report_date: date | None = None) -> Path:
    """Regenerate the results-first block in the canonical wiki homepage."""

    wiki_root = repository_root / "data" / "wiki"
    index_path = wiki_root / "index.md"
    index_text = index_path.read_text(encoding="utf-8")
    latest_report = _latest_report_page_key(wiki_root)
    effective_date = report_date or (latest_report[1] if latest_report else None)
    lines = [HOME_RESULTS_START, "## Current results", ""]
    if latest_report:
        page_key, latest_date = latest_report
        lines.append(f"Latest full result: [[{page_key}|Daily report {latest_date.isoformat()}]].")
    else:
        lines.append("No canonical daily report is available yet.")
    lines.extend(["", *_homepage_portfolio_lines(repository_root), ""])
    lines.extend(_homepage_suggestion_lines(repository_root))
    lines.extend(["", HOME_RESULTS_END])
    block = "\n".join(lines)

    start_count = index_text.count(HOME_RESULTS_START)
    end_count = index_text.count(HOME_RESULTS_END)
    if start_count != end_count or start_count > 1:
        raise CanonicalValueError("wiki homepage has an incomplete generated-results block")
    if start_count == 1:
        start = index_text.index(HOME_RESULTS_START)
        end = index_text.index(HOME_RESULTS_END, start) + len(HOME_RESULTS_END)
        updated = index_text[:start] + block + index_text[end:]
    else:
        anchor = "\n## Meta\n"
        if anchor not in index_text:
            raise CanonicalValueError("wiki homepage is missing the Meta section")
        updated = index_text.replace(anchor, f"\n{block}\n\n## Meta\n", 1)
    if effective_date is not None:
        updated, count = re.subn(
            r'^updated: "\d{4}-\d{2}-\d{2}"$',
            f'updated: "{effective_date.isoformat()}"',
            updated,
            count=1,
            flags=re.M,
        )
        if count != 1:
            raise CanonicalValueError("wiki homepage must contain one updated frontmatter date")
    if updated != index_text:
        atomic_write_text(index_path, updated, allowed_root=wiki_root)
    return index_path


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
    refresh_wiki_homepage(repository_root, report_date=day)
    return path
