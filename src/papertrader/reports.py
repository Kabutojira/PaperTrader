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
from papertrader.public_refs import PublicEntityResolver
from papertrader.tables import read_table
from papertrader.utils import CanonicalValueError, ensure_utc, parse_timestamp, utc_now
from papertrader.wiki import register_wiki_page

RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
DAILY_REPORT_STEM_PATTERN = re.compile(r"^daily-report_(\d{4})(\d{2})(\d{2})$")
HOME_RESULTS_START = "<!-- papertrader-current-results:start -->"
HOME_RESULTS_END = "<!-- papertrader-current-results:end -->"
HOME_SUGGESTION_LIMIT = 3
HOME_SUGGESTION_MAX_CHARS = 400
REPORT_NARRATIVE_TEXT_MAX_CHARS = 350
REPORT_NARRATIVE_EVIDENCE_LIMIT = 3
REPORT_ISSUE_DESCRIPTION_MAX_CHARS = 500


@dataclass(frozen=True, slots=True)
class NarrativeItem:
    """One original LLM narrative sentence plus explicit evidence references."""

    text: str
    evidence_refs: tuple[str, ...]


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ") or "—"


def _allocation_security(resolver: PublicEntityResolver, row: Mapping[str, str]) -> str:
    return resolver.markdown("security", row["security_id"]) if row["security_id"] else "Cash"


def _bounded_text(value: str, maximum_chars: int) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= maximum_chars:
        return normalized
    return normalized[: maximum_chars - 1].rstrip() + "…"


def _today(timestamp: str, report_date: date) -> bool:
    if not timestamp:
        return False
    parsed = parse_timestamp(timestamp)
    return parsed is not None and parsed.date() == report_date


def _wiki_changes(wiki_root: Path, report_date: date) -> tuple[str, ...]:
    changes: list[str] = []
    for path in sorted(wiki_root.rglob("*.md")):
        relative = path.relative_to(wiki_root)
        if relative.parts[0] in {
            "_archive",
            "_meta",
            "daily-reports",
            "inbox",
            "raw",
        } or relative.name in {
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


def _youtube_discovery_lines(repository_root: Path, run_id: str) -> list[str]:
    """Render the validated run-level discovery outcome without publishing video content."""

    path = repository_root / "data" / "runs" / run_id / "youtube_scan.json"
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        raise CanonicalValueError("YouTube scan summary must be a regular run artifact")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CanonicalValueError(f"cannot read YouTube scan summary: {exc}") from exc
    channels = value.get("channels") if isinstance(value, dict) else None
    if not isinstance(channels, list) or not all(isinstance(item, dict) for item in channels):
        raise CanonicalValueError("YouTube scan summary has invalid channel outcomes")
    lines = [
        "### Curated YouTube discovery",
        "",
        f"- Status: `{_markdown_text(str(value.get('status', 'unknown')))}`",
        f"- Operations queued: `{value.get('operation_count', 0)}`",
        f"- Channel failures: `{value.get('failure_count', 0)}`",
        "",
        "| Channel | Status | Discovered | Queued | Reason |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for channel in channels:
        discovered = channel.get("discovered_video_ids", [])
        operations = channel.get("operation_ids", [])
        lines.append(
            f"| {_cell(str(channel.get('handle', '')))} | "
            f"{_cell(str(channel.get('status', '')))} | "
            f"{len(discovered) if isinstance(discovered, list) else 0} | "
            f"{len(operations) if isinstance(operations, list) else 0} | "
            f"{_cell(str(channel.get('reason', '')))} |"
        )
    lines.append("")
    return lines


def _seekingalpha_discovery_lines(repository_root: Path, run_id: str) -> list[str]:
    """Render search-index lead discovery without reproducing provider summaries."""

    schedule_path = repository_root / "data" / "runs" / run_id / "seekingalpha_schedule.json"
    if not schedule_path.exists():
        return []
    if schedule_path.is_symlink() or not schedule_path.is_file():
        raise CanonicalValueError("Seeking Alpha schedule must be a regular run artifact")
    try:
        schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CanonicalValueError(f"cannot read Seeking Alpha schedule: {exc}") from exc
    if not isinstance(schedule, dict) or schedule.get("run_id") != run_id:
        raise CanonicalValueError("Seeking Alpha schedule identity is invalid")
    lines = [
        "### Seeking Alpha search-index leads",
        "",
        f"- Schedule status: `{_markdown_text(str(schedule.get('status', 'unknown')))}`",
        "- Access mode: `search_index`; Seeking Alpha pages and article bodies were not fetched.",
    ]
    resolver = PublicEntityResolver(repository_root)
    operation_id = schedule.get("operation_id")
    if not isinstance(operation_id, str) or not operation_id:
        lines.append("")
        return lines
    discovery_path = (
        repository_root / "data" / "runs" / run_id / operation_id / "seekingalpha_discovery.json"
    )
    if not discovery_path.exists():
        lines.extend(["- Discovery status: `pending`", ""])
        return lines
    if discovery_path.is_symlink() or not discovery_path.is_file():
        raise CanonicalValueError("Seeking Alpha discovery must be a regular artifact")
    try:
        discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CanonicalValueError(f"cannot read Seeking Alpha discovery: {exc}") from exc
    if (
        not isinstance(discovery, dict)
        or discovery.get("run_id") != run_id
        or discovery.get("operation_id") != operation_id
    ):
        raise CanonicalValueError("Seeking Alpha discovery identity is invalid")
    counts = discovery.get("candidate_counts")
    selected = discovery.get("selected")
    rejected = discovery.get("rejected")
    if (
        not isinstance(counts, dict)
        or not isinstance(selected, list)
        or not all(isinstance(item, dict) for item in selected)
        or not isinstance(rejected, list)
    ):
        raise CanonicalValueError("Seeking Alpha discovery summary is malformed")
    lines.extend(
        [
            f"- Discovery status: `{_markdown_text(str(discovery.get('status', 'unknown')))}`",
            f"- Candidates examined: analysis `{counts.get('analysis', 0)}`, "
            f"news `{counts.get('news', 0)}`",
            f"- Interesting leads selected: `{len(selected)}`; rejected: `{len(rejected)}`",
        ]
    )
    if discovery.get("reason_code"):
        lines.append(f"- Reason: `{_markdown_text(str(discovery.get('reason_code', '')))}`")
    if selected:
        lines.extend(
            [
                "",
                "| Kind | Indexed title | Related entities |",
                "| --- | --- | --- |",
            ]
        )
        for lead in selected:
            related = lead.get("related_entity_ids")
            related_text = "new-lead candidate"
            if isinstance(related, list) and related:
                references: list[str] = []
                for value in related:
                    if not isinstance(value, str) or "_" not in value:
                        raise CanonicalValueError(
                            "Seeking Alpha lead has an invalid public entity reference"
                        )
                    references.append(resolver.markdown(value.split("_", 1)[0], value))
                related_text = ", ".join(references)
            title = _markdown_text(str(lead.get("title", "")))
            url = str(lead.get("canonical_url", ""))
            lines.append(
                f"| {_cell(str(lead.get('content_kind', '')))} | "
                f"[{title}]({url}) | {_cell(related_text)} |"
            )
    lines.append("")
    return lines


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
    del securities, aliased
    return PublicEntityResolver(wiki_root.parent.parent).markdown(entity_type, entity_id)


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


def _public_page_link(repository_root: Path, page_key: str) -> str:
    """Render one wiki page with a required human title as its visible label."""

    path = repository_root / "data" / "wiki" / f"{page_key}.md"
    try:
        text = path.read_text(encoding="utf-8")
        raw, _ = text[4:].split("\n---\n", maxsplit=1)
        metadata = yaml.safe_load(raw)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        raise CanonicalValueError(f"cannot resolve public wiki reference: {page_key}") from exc
    title = metadata.get("title") if isinstance(metadata, dict) else None
    if not isinstance(title, str) or not title.strip():
        raise CanonicalValueError(f"public wiki reference has no title: {page_key}")
    return f"[[{page_key}|{_wikilink_label(' '.join(title.split()))}]]"


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
        lines.append("No open positions; the portfolio is currently held in cash.")
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
    resolver = PublicEntityResolver(repository_root)
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
        summary = _markdown_text(_summary_excerpt(resolver.human_label(row["result_summary"])))
        lines.append(f"- **{completed} — {operation} for {entity}:** {summary}")
    if len(lines) == 2:
        lines.append("No completed research suggestions are available yet.")
    return lines


def refresh_wiki_homepage(repository_root: Path, *, report_date: date | None = None) -> Path:
    """Regenerate every investor view from the latest validated decision snapshot."""

    from papertrader.advice import load_published_snapshot
    from papertrader.investor_pages import refresh_investor_pages

    snapshot = load_published_snapshot(repository_root)
    if report_date is not None and snapshot.report_date != report_date.isoformat():
        raise CanonicalValueError("homepage report date differs from the decision snapshot")
    refresh_investor_pages(repository_root, snapshot)
    return repository_root / "data" / "wiki" / "index.md"


def _generate_legacy_daily_report(
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
    performance = max(
        (
            row
            for row in read_table(repository_root, "performance_daily")
            if row["date"] == day.isoformat()
        ),
        key=lambda row: (row["generated_at"], row["performance_epoch_id"]),
        default=None,
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
    issues = []
    for row in read_table(repository_root, "issues"):
        first_seen = parse_timestamp(row["first_seen_at"])
        resolved = parse_timestamp(row["resolved_at"], allow_empty=True)
        if (
            first_seen is not None
            and first_seen <= instant
            and (resolved is None or resolved > instant)
        ):
            issues.append(row)
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
    """Generate the investor-first report and complete deterministic audit appendix."""

    from papertrader.advice import load_published_snapshot, reason_label
    from papertrader.investor_pages import investor_report_sections, research_decisions_for_run

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
    snapshot = load_published_snapshot(repository_root, expected_run_id=run_id)
    day = report_date or instant.date()
    if snapshot.report_date != day.isoformat() or snapshot.as_of != instant.isoformat().replace(
        "+00:00", "Z"
    ):
        raise CanonicalValueError("daily report time differs from its decision snapshot")
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
    issues = []
    for row in read_table(repository_root, "issues"):
        first_seen = parse_timestamp(row["first_seen_at"])
        resolved = parse_timestamp(row["resolved_at"], allow_empty=True)
        if (
            first_seen is not None
            and first_seen <= instant
            and (resolved is None or resolved > instant)
        ):
            issues.append(row)
    wiki_changes = tuple(
        sorted(
            {
                *_wiki_changes(repository_root / "data" / "wiki", day),
                *_run_wiki_changes(repository_root, run_id),
            }
        )
    )
    research_decisions = research_decisions_for_run(repository_root, run_id)
    resolver = PublicEntityResolver(repository_root)

    def public_allocation_reason(raw: str) -> str:
        codes = [code for code in raw.split("|") if code]
        return "; ".join(reason_label(code) for code in codes) if codes else "—"

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
        f'snapshot_id: "{snapshot.snapshot_id}"',
        "---",
        "",
        f"# PaperTrader daily report — {day.isoformat()}",
        "",
        *investor_report_sections(repository_root, snapshot, research_decisions),
        "",
        "## 6. Research changes",
        "",
    ]
    if narratives:
        lines.extend(["### Evidence-linked narrative", ""])
        for item in narratives:
            lines.append(
                f"- {resolver.humanize(_bounded_text(item.text, REPORT_NARRATIVE_TEXT_MAX_CHARS))} "
                "Evidence is retained in the canonical run artifacts."
            )
        lines.append("")
    lines.extend(
        [f"- {_public_page_link(repository_root, page_key)}" for page_key in wiki_changes]
        if wiki_changes
        else ["No maintained research pages changed during this run."]
    )
    coverage = snapshot.coverage
    lines.extend(
        [
            "",
            "## 7. Data-quality and coverage impact",
            "",
            f"- Investment data status: **{_markdown_text(snapshot.investment_data_status)}**",
            f"- Operations status: **{_markdown_text(snapshot.operations_status)}**",
            f"- Assessments: {coverage.current_assessment_count}/"
            f"{coverage.allocation_candidate_count}",
            f"- Fresh-evidence assessments: {coverage.fresh_evidence_assessment_count}/"
            f"{coverage.allocation_candidate_count}",
            f"- Relationship reviews: {coverage.reviewed_relationship_count}/"
            f"{coverage.required_relationship_review_count}",
            f"- Accepted relationships: {coverage.accepted_relationship_count}",
            f"- Ready or active strategies: {coverage.ready_or_active_strategy_count}",
            f"- Active signals: {coverage.active_signal_count}",
            f"- Pending orders: {coverage.pending_order_count}",
            f"- Market-data success/failure: {coverage.market_data_success_count}/"
            f"{coverage.market_data_failure_count}",
            f"- Research alerts (not trade signals): {len(snapshot.research_alerts)}",
            "",
        ]
    )
    if snapshot.system_impacts:
        lines.extend(["### Current system impacts", ""])
        for impact in snapshot.system_impacts:
            affected = (
                f" — {_markdown_text(impact.ticker)} {_markdown_text(impact.company_name)}"
                if impact.ticker
                else ""
            )
            lines.append(
                f"- **{_markdown_text(impact.impact.replace('_', ' '))}**{affected}: "
                f"{resolver.humanize(impact.title)}"
            )
    else:
        lines.append("No current system impacts.")
    lines.extend(
        [
            "",
            "## 8. Audit appendix",
            "",
            "### Run diagnostics",
            "",
            f"- Report date: {day.isoformat()}",
            f"- Run status: {normalized_status}",
            f"- Generated (UTC): `{snapshot.as_of}`",
            "",
            "### Complete market freshness",
            "",
            "| Security | Price date | Retrieved at | Status | Error |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(
        (
            f"| {resolver.markdown('security', row['security_id'])} | {_cell(row['price_date'])} | "
            f"{_cell(row['retrieved_at'])} | {_cell(row['status'])} | "
            f"{_cell(resolver.human_label(row['error']))} |"
            for row in latest
        )
        if latest
        else ["| — | — | — | no monitored securities | — |"]
    )
    lines.extend(
        [
            "",
            "### Orders and executions",
            "",
            "| Order | Strategy | Fill policy | Status | Created |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(
        (
            f"| {resolver.markdown('order', row['order_id'])} | "
            f"{resolver.markdown('strategy', row['strategy_id'])} | "
            f"{_cell(row['fill_policy'])} | {_cell(row['status'])} | "
            f"{_cell(row['created_at'])} |"
            for row in orders
        )
        if orders
        else ["| — | — | — | no orders | — |"]
    )
    lines.extend(
        [
            "",
            "| Fill | Order | Security | Side | Quantity | Fill price | Fees |",
            "| --- | --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    lines.extend(
        (
            f"| {resolver.markdown('execution', row['execution_id'])} | "
            f"{resolver.markdown('order', row['order_id'])} | "
            f"{resolver.markdown('security', row['security_id'])} | {_cell(row['side'])} | "
            f"{_cell(row['quantity'])} | {_cell(row['fill_price'])} "
            f"{_cell(row['currency'])} | {_cell(row['fees'])} |"
            for row in executions
        )
        if executions
        else ["| — | — | — | — | 0 | no executions | 0 |"]
    )
    lines.extend(["", "### Allocation audit", ""])
    if allocation_summary is None:
        lines.append("No allocation plan was generated for this run.")
    else:
        lines.extend(
            [
                f"- Mode: `{allocation_summary['mode']}`",
                f"- Deployment budget: {allocation_summary['deployment_budget_base']} "
                f"{snapshot.base_currency}",
                f"- Capital allocated: {allocation_summary['capital_allocated_base']} "
                f"{snapshot.base_currency}",
                f"- Capital unallocated: {allocation_summary['capital_unallocated_base']} "
                f"{snapshot.base_currency}",
            ]
        )
    lines.extend(
        [
            "",
            "| Rank | Security | Target weight | Disposition | Reasons |",
            "| ---: | --- | ---: | --- | --- |",
        ]
    )
    lines.extend(
        (
            f"| {_cell(row['rank'])} | "
            f"{_allocation_security(resolver, row)} "
            "| "
            f"{_cell(row['target_weight_pct'])}% | {_cell(row['disposition'])} | "
            f"{_cell(public_allocation_reason(row['reason']))} |"
            for row in sorted(
                allocation_targets,
                key=lambda value: (int(value["rank"] or "999999"), value["security_id"]),
            )
        )
        if allocation_targets
        else ["| — | — | 0% | no candidates | — |"]
    )
    youtube_lines = _youtube_discovery_lines(repository_root, run_id)
    if youtube_lines:
        lines.extend(["", *youtube_lines])
    seekingalpha_lines = _seekingalpha_discovery_lines(repository_root, run_id)
    if seekingalpha_lines:
        lines.extend(["", *seekingalpha_lines])
    lines.extend(
        [
            "",
            "### Research-operation audit",
            "",
            "| Research operation | Entity | Disposition | Reason |",
            "| --- | --- | --- | --- |",
        ]
    )
    lines.extend(
        (
            f"| {resolver.markdown('operation', row['operation_id'])} | "
            f"{resolver.markdown(row['entity_type'], row['entity_id'])} | "
            f"{_cell(row['terminal_status'])} | "
            f"{_cell(resolver.human_label(row['terminal_reason']).replace('_', ' '))} |"
            for row in history
        )
        if history
        else ["| — | — | no completed operations | — |"]
    )
    lines.extend(["", "### Complete active queue", ""])
    lines.extend(
        (
            f"- {row['status'].capitalize()} — "
            f"{resolver.markdown('operation', row['operation_id'])}"
            for row in active_operations
        )
        if active_operations
        else ["No scheduled follow-up operations."]
    )
    lines.extend(["", "### Open issues and delivery failures", ""])
    if issues:
        for row in issues:
            description = _bounded_text(
                resolver.human_label(row["description"]), REPORT_ISSUE_DESCRIPTION_MAX_CHARS
            )
            lines.append(
                f"- {row['severity'].capitalize()} — "
                f"{resolver.markdown('issue', row['issue_id'])}: "
                f"{_markdown_text(description)}"
            )
    else:
        lines.append("No open issues.")
    lines.extend(["", "### Decision provenance", ""])
    for code in snapshot.stance_reason_codes:
        lines.append(f"- {_markdown_text(reason_label(code))}")
    lines.extend(
        [
            "",
            "### Links",
            "",
            "- [[index|Investor dashboard]]",
            "- [[model-portfolio|Model portfolio]]",
            "- [[signals|Signals]]",
            "- [[system-status|System status]]",
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
