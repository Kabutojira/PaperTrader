"""Deterministic investor-first Markdown views over one decision snapshot."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal
from html import escape
from pathlib import Path, PurePosixPath

import yaml

from papertrader.advice import (
    ActionableSignalView,
    CandidateView,
    DecisionSnapshot,
    ModelPortfolioRow,
    SystemImpact,
    reason_label,
)
from papertrader.atomic_io import atomic_write_text
from papertrader.market_data import read_fx_cache
from papertrader.public_refs import PublicEntityResolver
from papertrader.tables import read_table
from papertrader.utils import (
    CanonicalValueError,
    decimal_text,
    format_timestamp,
    parse_timestamp,
    required_decimal,
)
from papertrader.wiki import register_wiki_page

INVESTOR_BRIEF_START = "<!-- papertrader-investor-brief:start -->"
INVESTOR_BRIEF_END = "<!-- papertrader-investor-brief:end -->"
DASHBOARD_PAGES = frozenset(
    {
        "index",
        "model-portfolio",
        "security-catalog",
        "signals",
        "performance",
        "system-status",
    }
)
STANCE_LABELS = {
    "hold_cash": "No trade — hold 100% cash",
    "maintain": "Maintain the current model portfolio",
    "deploy": "Deploy model capital",
    "rebalance": "Rebalance toward model targets",
    "reduce_risk": "Reduce model-portfolio risk",
    "exit": "Exit the model exposure",
    "blocked": "Decision blocked — do not copy actions",
}
INVESTMENT_STATUS_LABELS = {
    "current": "Current",
    "degraded": "Portfolio state safe — research gaps remain",
    "blocked": (
        "Unsafe to publish — portfolio, accounting, or active-order state requires attention"
    ),
}
OPERATIONS_STATUS_LABELS = {
    "current": "Current",
    "degraded": "Attention required",
    "blocked": "Action controls blocked",
}
CLASSIFICATION_LABELS = {
    "strategy_ready": "Strategy-ready candidate",
    "valuation_attractive": "Valuation attractive",
    "strategy_pending": "Strategy research pending",
    "allocation_constrained": "Allocation constrained",
    "relationship_pending": "Relationship research pending",
    "assessment_pending": "Assessment pending",
    "market_data_blocked": "Market data blocked",
    "valuation_unattractive": "Valuation unattractive",
    "valuation_unsupported": "Valuation unsupported",
    "liquidity_blocked": "Liquidity blocked",
    "solvency_blocked": "Solvency blocked",
    "research_incomplete": "Research incomplete",
    "risk_blocked": "Risk blocked",
    "research_blocked": "Research incomplete",
}
RATING_LABELS = {
    "strong_buy": "Strong Buy",
    "buy": "Buy",
    "hold": "Hold",
    "sell": "Sell",
    "strong_sell": "Strong Sell",
    "unrated": "Unrated",
}
PORTFOLIO_ACTION_LABELS = {
    "initiate": "Initiate",
    "add": "Add",
    "hold": "Hold",
    "trim": "Trim",
    "exit": "Exit",
    "avoid": "Avoid",
    "watch": "Watch",
    "short_candidate": "Short candidate",
}
ACTION_LABELS = {
    "buy": "Buy",
    "add": "Add",
    "hold": "Hold",
    "trim": "Trim",
    "exit": "Exit",
    "no_trade": "No trade",
}
ACTION_STATUS_LABELS = {
    "filled": "Filled",
    "pending_order": "Pending validated order",
    "active_signal": "Active signal",
    "awaiting_order_validation": "Awaiting deterministic order validation",
    "research_candidate": "Research candidate",
    "blocked": "Blocked",
    "no_action": "No action",
}
RESEARCH_DECISION_CONCLUSION_MAX_CHARS = 350
SECURITY_TABLE_COLUMNS = (
    (
        "security",
        "Security",
        "Ticker and company name. Opens the maintained security research page.",
        "---",
    ),
    (
        "price",
        "Price",
        "Latest committed daily market price in the security's listing currency; "
        "this is not a live quote.",
        "---:",
    ),
    (
        "rating-action",
        "Rating / action",
        "Canonical research rating and the context-aware model-portfolio action.",
        "---",
    ),
    (
        "decision",
        "Decision",
        "Current deterministic classification for portfolio eligibility.",
        "---",
    ),
    (
        "main-reason",
        "Main reason",
        "Primary reason or blocker behind the current decision.",
        "---",
    ),
    (
        "scenarios",
        "Bear / base / bull",
        "Estimated returns for the three valuation scenarios, rounded to whole percentage points.",
        "---:",
    ),
    (
        "expected-return",
        "Expected return",
        "Probability-weighted scenario return over the assessment horizon, before "
        "confidence adjustment, rounded to a whole percentage point.",
        "---:",
    ),
    (
        "buy-below",
        "Buy below",
        "Base-case fair value less the configured margin of safety, in the security's "
        "listing currency.",
        "---:",
    ),
    (
        "last-update",
        "Last data/FX update",
        "UTC dates when market data and, after the slash, the FX rate were last "
        "retrieved. The dates match when no currency conversion is required.",
        "---",
    ),
    (
        "next-review",
        "Next review",
        "UTC date when the assessment should be reviewed again.",
        "---",
    ),
)


def _markdown(value: str) -> str:
    normalized = " ".join(value.split())
    escaped = escape(normalized, quote=False).replace("\\", "\\\\")
    return re.sub(r"([`*_\[\]|])", r"\\\1", escaped)


def _bounded_text(value: str, maximum_chars: int) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= maximum_chars:
        return normalized
    return normalized[: maximum_chars - 1].rstrip() + "…"


def _html(value: str) -> str:
    return escape(" ".join(value.split()), quote=True)


def _cell(value: str) -> str:
    return _markdown(value) or "—"


def _column_header(key: str, label: str, description: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9-]*", key):
        raise CanonicalValueError(f"invalid security table column key: {key}")
    tooltip_id = f"security-column-help-{key}"
    return (
        f'<span class="column-heading">{_html(label)} '
        f'<button type="button" class="column-help" aria-label="{_html(f"About {label}")}" '
        f'aria-describedby="{tooltip_id}"><span aria-hidden="true">?</span>'
        f'<span id="{tooltip_id}" class="column-help-tooltip" role="tooltip">'
        f"{_html(description)}</span></button></span>"
    )


def _rounded_percentage(value: str) -> str:
    if not value:
        return "—"
    percentage = required_decimal(value, label="security dashboard return")
    rounded = percentage.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)
    return f"{decimal_text(rounded)}%"


def _utc_day(value: str) -> str:
    instant = parse_timestamp(value, allow_empty=True)
    return instant.date().isoformat() if instant is not None else "—"


def _data_fx_update(data_as_of: str, fx_as_of: str) -> str:
    return f"{_utc_day(data_as_of)} / {_utc_day(fx_as_of)}"


def _currency_amount(value: str, currency: str, *, label: str) -> str:
    if not value:
        return "—"
    amount = required_decimal(value, label=label)
    return f"{decimal_text(amount)} {_cell(currency)}"


def _page_key(research_page: str) -> str:
    if not research_page:
        return ""
    raw_path, separator, fragment = research_page.partition("#")
    if separator and (not fragment or not re.fullmatch(r"[A-Za-z0-9_.-]+", fragment)):
        raise CanonicalValueError(f"invalid public research page fragment: {research_page}")
    path = PurePosixPath(raw_path)
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.parts[:2] != ("data", "wiki")
        or path.suffix != ".md"
    ):
        raise CanonicalValueError(f"invalid public research page: {research_page}")
    key = PurePosixPath(*path.parts[2:]).with_suffix("").as_posix()
    return f"{key}#{fragment}" if fragment else key


def _link(label: str, research_page: str) -> str:
    key = _page_key(research_page)
    return f"[{_markdown(label)}]({key})" if key else _markdown(label)


def _security_public_page(security: Mapping[str, str]) -> str:
    return security["research_page"] or (
        f"data/wiki/security-catalog.md#security-{security['security_id']}"
    )


@dataclass(frozen=True, slots=True)
class ResearchDecisionView:
    operation_id: str
    operation_type: str
    label: str
    research_page: str
    status: str
    conclusion: str


def _wiki_title(repository_root: Path, research_page: str, fallback: str) -> str:
    raw_path = research_page.partition("#")[0]
    path = repository_root / raw_path
    if path.is_symlink() or not path.is_file():
        return fallback
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return fallback
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return fallback
    raw, _ = text[4:].split("\n---\n", maxsplit=1)
    metadata = yaml.safe_load(raw)
    title = metadata.get("title") if isinstance(metadata, dict) else None
    return " ".join(title.split()) if isinstance(title, str) and title.strip() else fallback


def research_decisions_for_run(
    repository_root: Path, run_id: str
) -> tuple[ResearchDecisionView, ...]:
    """Project every completed research operation in one run into a public linked decision."""

    resolver = PublicEntityResolver(repository_root)
    output: list[ResearchDecisionView] = []
    for row in read_table(repository_root, "operations_history"):
        if row["claimed_by_run_id"] != run_id or not row["operation_type"].endswith("_research"):
            continue
        reference = resolver.resolve(row["entity_type"], row["entity_id"])
        conclusion = resolver.human_label(
            " ".join((row["result_summary"] or row["terminal_reason"]).split())
        )
        output.append(
            ResearchDecisionView(
                operation_id=row["operation_id"],
                operation_type=row["operation_type"],
                label=reference.label,
                research_page=reference.target,
                status=row["terminal_status"],
                conclusion=conclusion or "No research conclusion was recorded.",
            )
        )
    return tuple(output)


def _public_snapshot(repository_root: Path, snapshot: DecisionSnapshot) -> DecisionSnapshot:
    """Humanize machine identities before rendering snapshot narratives to Markdown."""

    resolver = PublicEntityResolver(repository_root)
    signals = tuple(
        replace(
            signal,
            entry_rule=resolver.human_label(signal.entry_rule),
            exit_rule=resolver.human_label(signal.exit_rule),
            invalidation=resolver.human_label(signal.invalidation),
            rationale=resolver.human_label(signal.rationale),
        )
        for signal in snapshot.actionable_signals
    )
    alerts = tuple(
        replace(
            alert,
            research_conclusion=resolver.human_label(alert.research_conclusion),
        )
        for alert in snapshot.research_alerts
    )
    impacts = tuple(
        replace(
            impact,
            title=resolver.human_label(impact.title),
            summary=resolver.human_label(impact.summary),
        )
        for impact in snapshot.system_impacts
    )
    return replace(
        snapshot,
        actionable_signals=signals,
        research_alerts=alerts,
        system_impacts=impacts,
    )


def _frontmatter(
    *, title: str, page_type: str, tag: str, day: date, snapshot: DecisionSnapshot
) -> str:
    return "\n".join(
        [
            "---",
            f'title: "{title}"',
            f"type: {page_type}",
            "status: maintained",
            "tags:",
            f"  - {tag}",
            f'created: "{day.isoformat()}"',
            f'updated: "{day.isoformat()}"',
            "provenance: deterministic-decision-projection",
            f'snapshot_id: "{snapshot.snapshot_id}"',
            f'as_of: "{snapshot.as_of}"',
            "---",
            "",
        ]
    )


def _money(value: str, currency: str) -> str:
    return f"{value} {_markdown(currency)}"


def _reason_lines(codes: Sequence[str]) -> list[str]:
    return [f"- {_markdown(reason_label(code))}" for code in codes]


def _action_label(action: str) -> str:
    try:
        return ACTION_LABELS[action]
    except KeyError as exc:
        raise CanonicalValueError(f"unknown public action: {action}") from exc


def _action_status_label(status: str) -> str:
    try:
        return ACTION_STATUS_LABELS[status]
    except KeyError as exc:
        raise CanonicalValueError(f"unknown public action status: {status}") from exc


def _buy_initiate_candidates(
    snapshot: DecisionSnapshot, *, limit: int | None = None
) -> tuple[CandidateView, ...]:
    candidates = tuple(
        candidate
        for candidate in snapshot.candidate_pipeline
        if candidate.canonical_rating in {"buy", "strong_buy"}
        and candidate.portfolio_action == "initiate"
    )
    return candidates if limit is None else candidates[:limit]


def _candidate_state_label(candidate: CandidateView) -> str:
    tier = {"full": "Full baseline", "starter": "Starter"}.get(candidate.tier)
    state = CLASSIFICATION_LABELS[candidate.classification]
    return f"{tier} — {state}" if tier else state


def _homepage_reason_lines(snapshot: DecisionSnapshot) -> list[str]:
    lines = [
        f"- {_markdown(reason_label(code))}"
        for code in snapshot.stance_reason_codes
        if code != "portfolio_issue_open"
    ]
    blockers = [impact for impact in snapshot.system_impacts if impact.impact == "blocks_portfolio"]
    for blocker in blockers:
        lines.append(
            f"- **Portfolio publication blocker:** {_markdown(blocker.title)} — "
            f"{_markdown(blocker.summary)} [[system-status|Review System Status]]."
        )
    if snapshot.stance == "hold_cash" and not snapshot.actionable_signals:
        lines.insert(0, "- No validated copy-ready signal or pending paper order exists.")
        candidates = _buy_initiate_candidates(snapshot)
        if candidates:
            counts: defaultdict[str, int] = defaultdict(int)
            for candidate in candidates:
                label = (
                    candidate.reason_labels[0]
                    if candidate.reason_labels
                    else "Further research required"
                )
                counts[label] += 1
            gates = "; ".join(
                f"{_markdown(label)} ({count})"
                for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:4]
            )
            lines.append(
                f"- {len(candidates)} Buy / Initiate research candidates remain non-actionable. "
                f"Leading gates: {gates}."
            )
    return lines or ["- No additional decision constraint was recorded."]


def _portfolio_markdown_rows(rows: Sequence[ModelPortfolioRow]) -> list[str]:
    output: list[str] = []
    for row in rows:
        holding = (
            "Cash"
            if row.holding_type == "cash"
            else _link(f"{row.ticker} — {row.company_name}", row.security_research_page)
        )
        output.append(
            f"| {holding} | {_cell(row.sleeve)} | {row.current_weight_pct}% | "
            f"{row.target_weight_pct}% | {_money(row.current_value_base, '')} | "
            f"{_money(row.target_value_base, '')} | "
            f"{_action_label(row.action)} | {_action_status_label(row.action_status)} |"
        )
    return output


def investor_brief_markdown(
    snapshot: DecisionSnapshot,
    research_decisions: Sequence[ResearchDecisionView] = (),
) -> str:
    """Render the compact committed brief consumed by Telegram."""

    current = snapshot.current_portfolio
    target = snapshot.target_portfolio
    lines = [
        f"# {STANCE_LABELS[snapshot.stance]}",
        "",
        f"- **Investment data:** {INVESTMENT_STATUS_LABELS[snapshot.investment_data_status]}",
        f"- **Operations:** {OPERATIONS_STATUS_LABELS[snapshot.operations_status]}",
        f"- **As of:** `{snapshot.as_of}`",
        f"- **Cash:** {current.cash_base} {snapshot.base_currency} ({current.cash_weight_pct}%)",
        f"- **Gross exposure:** {current.gross_exposure_base} {snapshot.base_currency}",
        f"- **Target cash:** {target.cash_base} {snapshot.base_currency} "
        f"({target.cash_weight_pct}%)",
        f"- **Actionable signals:** {len(snapshot.actionable_signals)}",
        f"- **Evidence state:** {_markdown(snapshot.evidence_state.replace('_', ' '))}",
    ]
    changes = [
        row
        for row in target.rows
        if row.holding_type == "security" and row.action in {"buy", "add", "trim", "exit"}
    ]
    lines.extend(["", "## Target changes", ""])
    if changes:
        lines.extend(
            f"- **{_link(row.ticker, row.security_research_page)}:** "
            f"{_action_label(row.action)} to "
            f"{row.target_weight_pct}% (target estimate)"
            for row in changes[:5]
        )
    else:
        lines.append("No target changes.")
    lines.extend(["", "## Actionable signals", ""])
    if snapshot.actionable_signals:
        lines.extend(
            f"- **{_link(signal.ticker, signal.security_research_page)}:** "
            f"{_action_label(signal.action)} — "
            f"{_action_status_label(signal.action_status)}"
            for signal in snapshot.actionable_signals[:5]
        )
    else:
        lines.append("No actionable trade signals.")
    if snapshot.research_alerts:
        lines.extend(["", "## Price action alerts", ""])
        for alert in snapshot.research_alerts:
            label = _link(f"{alert.ticker} — {alert.company_name}", alert.research_page)
            alert_name = _markdown(alert.alert_type.replace("_", " ").title())
            lines.extend(
                [
                    f"- **{label}: {alert_name}** (`{alert.market_data_date}`)",
                    f"  - Research: **{_markdown(alert.research_status)}**",
                    f"  - Decision: {_markdown(alert.research_conclusion)}",
                ]
            )
    if research_decisions:
        lines.extend(["", "## Research decisions this run", ""])
        for decision in research_decisions:
            label = _link(decision.label, decision.research_page)
            conclusion = _bounded_text(decision.conclusion, RESEARCH_DECISION_CONCLUSION_MAX_CHARS)
            lines.append(f"- **{label} — {_markdown(decision.status)}:** {_markdown(conclusion)}")
    near_miss = next(iter(_buy_initiate_candidates(snapshot, limit=1)), None)
    lines.extend(["", "## Leading Buy / Initiate research candidate", ""])
    if near_miss is None:
        lines.append("No security currently has both a Buy rating and an Initiate action.")
    else:
        reason = near_miss.reason_labels[0] if near_miss.reason_labels else "No current trade."
        lines.append(
            f"- **{_markdown(near_miss.ticker)} — {_markdown(near_miss.company_name)}:** "
            f"{RATING_LABELS[near_miss.canonical_rating]} / "
            f"{PORTFOLIO_ACTION_LABELS[near_miss.portfolio_action]}; "
            f"expected return {_rounded_percentage(near_miss.expected_return_pct)}; "
            f"{_markdown(reason)}"
        )
    lines.extend(
        [
            "",
            "## Comparison-only research benchmark",
            "",
            "This equal-weight research benchmark is analytical only, not copy-ready, and cannot "
            "create signals, orders, or allocation targets.",
        ]
    )
    benchmark_names = [
        f"{row.ticker} {row.weight_pct}% ({RATING_LABELS[row.rating]})"
        for row in snapshot.research_benchmark.rows
    ]
    lines.append("- " + "; ".join(benchmark_names))
    return "\n".join(lines)


def investor_report_sections(
    repository_root: Path,
    snapshot: DecisionSnapshot,
    research_decisions: Sequence[ResearchDecisionView] = (),
) -> list[str]:
    """Render the investor-facing report sections from the shared snapshot."""

    snapshot = _public_snapshot(repository_root, snapshot)
    current = snapshot.current_portfolio
    target = snapshot.target_portfolio
    lines = [
        "## 1. Investor decision summary",
        "",
        INVESTOR_BRIEF_START,
        investor_brief_markdown(snapshot, research_decisions),
        INVESTOR_BRIEF_END,
        "",
        "### Deterministic reasons",
        "",
        *_homepage_reason_lines(snapshot),
        "",
        "## 2. Model portfolio and target changes",
        "",
        f"- Current equity: {current.equity_base} {snapshot.base_currency}",
        f"- Current cash: {current.cash_base} {snapshot.base_currency} "
        f"({current.cash_weight_pct}%)",
        f"- Current gross exposure: {current.gross_exposure_base} {snapshot.base_currency}",
        f"- Target cash: {target.cash_base} {snapshot.base_currency} ({target.cash_weight_pct}%)",
        "- Pending-order targets are estimates at the snapshot mark; only fills change accounting.",
        "",
        "| Holding | Sleeve | Current weight | Target | Current value | "
        "Target value | Action | State |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
        *_portfolio_markdown_rows(current.rows),
        "",
        "## 3. Actionable signals and pending orders",
        "",
    ]
    if snapshot.actionable_signals:
        for signal in snapshot.actionable_signals:
            copy = "copy ready" if signal.copy_ready else "awaiting deterministic order validation"
            lines.extend(
                [
                    "### "
                    + _link(
                        f"{signal.ticker} — {signal.company_name}",
                        signal.security_research_page,
                    ),
                    "",
                    f"- Action: **{_action_label(signal.action)}**",
                    f"- State: {_action_status_label(signal.action_status)} ({copy})",
                    f"- Strategy: {_markdown(signal.strategy_name)}",
                    "- Strategy research: "
                    + _link("Open strategy page", signal.strategy_research_page),
                    f"- Signal window: `{signal.created_at}` to `{signal.expires_at}`",
                    f"- Market data: `{signal.market_data_as_of}`",
                    f"- Rationale: {_markdown(signal.rationale)}",
                    "",
                ]
            )
    else:
        lines.extend(["No actionable trade signals.", "", "No pending orders.", ""])
    lines.extend(["## 4. Buy / Initiate research candidates", ""])
    near_misses = _buy_initiate_candidates(snapshot)
    if near_misses:
        lines.extend(
            [
                "| Candidate | Rating / action | State | Bear / base / bull | Expected | "
                "Buy below | Exact gate |",
                "| --- | --- | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for candidate in near_misses:
            main_reason = candidate.reason_labels[0] if candidate.reason_labels else "—"
            lines.append(
                "| "
                + _link(
                    f"{candidate.ticker} — {candidate.company_name}",
                    candidate.research_page,
                )
                + " | "
                f"{RATING_LABELS[candidate.canonical_rating]} / "
                f"{PORTFOLIO_ACTION_LABELS[candidate.portfolio_action]} | "
                f"{_markdown(_candidate_state_label(candidate))} | "
                f"{candidate.bear_return_pct or '—'}% / {candidate.base_return_pct or '—'}% / "
                f"{candidate.bull_return_pct or '—'}% | "
                f"{_rounded_percentage(candidate.expected_return_pct)} | "
                f"{candidate.buy_below_price or '—'} | "
                f"{_cell(main_reason)} |"
            )
    else:
        lines.append("No security currently has both a Buy rating and an Initiate action.")
    lines.extend(
        [
            "",
            "## 5. Performance and risk",
            "",
            f"- Daily return: {snapshot.performance.daily_return_pct}%",
            f"- Cumulative return: {snapshot.performance.cumulative_return_pct}%",
            f"- Running drawdown: {snapshot.performance.running_drawdown_pct}%",
            f"- Realized P/L: {snapshot.performance.realized_pnl_base} {snapshot.base_currency}",
            f"- Unrealized P/L: {snapshot.performance.unrealized_pnl_base} "
            f"{snapshot.base_currency}",
            f"- Largest position weight: {snapshot.performance.largest_position_weight_pct}%",
            f"- Largest sector weight: {snapshot.performance.largest_sector_weight_pct}%",
            "",
        ]
    )
    return lines


def _status_cards(snapshot: DecisionSnapshot) -> str:
    current = snapshot.current_portfolio
    coverage = snapshot.coverage
    equity = required_decimal(current.equity_base, label="dashboard equity")
    gross = required_decimal(current.gross_exposure_base, label="dashboard gross exposure")
    gross_weight = Decimal("0") if equity == 0 else gross / equity * Decimal("100")
    cards = (
        ("Stance", STANCE_LABELS[snapshot.stance], snapshot.stance),
        ("Cash", f"{current.cash_weight_pct}%", "cash"),
        (
            "Gross exposure",
            f"{decimal_text(gross_weight.quantize(Decimal('0.000001')))}%",
            "exposure",
        ),
        ("Actionable signals", str(len(snapshot.actionable_signals)), "signals"),
        (
            "Assessment coverage",
            f"{coverage.current_assessment_count}/{coverage.allocation_candidate_count}",
            "coverage",
        ),
    )
    body = "".join(
        f'<article class="decision-card" data-status="{_html(status)}">'
        f'<span class="decision-card-label">{_html(label)}</span>'
        f"<strong>{_html(value)}</strong></article>"
        for label, value, status in cards
    )
    return f'<section class="decision-cards" aria-label="Decision summary">{body}</section>'


def _homepage(snapshot: DecisionSnapshot, day: date, latest_report: str) -> str:
    current = snapshot.current_portfolio
    target = snapshot.target_portfolio
    lines = [
        _frontmatter(
            title="PaperTrader — today's investment decision",
            page_type="dashboard",
            tag="dashboard",
            day=day,
            snapshot=snapshot,
        ),
        "# PaperTrader",
        "",
        f"**As of `{snapshot.as_of}` · Investment data: "
        f"{INVESTMENT_STATUS_LABELS[snapshot.investment_data_status]} · Operations: "
        f"{OPERATIONS_STATUS_LABELS[snapshot.operations_status]}**",
        "",
        f"## {STANCE_LABELS[snapshot.stance]}",
        "",
        _status_cards(snapshot),
        "",
        "### Why",
        "",
        *_homepage_reason_lines(snapshot),
        "",
        "## Current and target portfolio",
        "",
        f"Current equity is **{current.equity_base} {snapshot.base_currency}** with "
        f"**{current.cash_weight_pct}% cash**. The target retains "
        f"**{target.cash_weight_pct}% cash**.",
        "",
        "| Holding | Current | Target | Action | Strategy |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for row in current.rows:
        label = "Cash" if row.holding_type == "cash" else f"{row.ticker} — {row.company_name}"
        linked = label if row.holding_type == "cash" else _link(label, row.security_research_page)
        strategy = _link("Open", row.strategy_research_page) if row.strategy_research_page else "—"
        lines.append(
            f"| {linked} | {row.current_weight_pct}% | "
            f"{row.target_weight_pct}% | {_action_label(row.action)} | {strategy} |"
        )
    lines.extend(["", "## Actionable trade signals", ""])
    if snapshot.actionable_signals:
        lines.extend(
            "- **"
            + _link(
                f"{signal.ticker} — {signal.company_name}",
                signal.security_research_page,
            )
            + ":** "
            f"{_action_label(signal.action)} · {_action_status_label(signal.action_status)}"
            for signal in snapshot.actionable_signals
        )
    else:
        lines.append("**No actionable trade signals.**")
    lines.extend(["", "## Buy / Initiate research candidates", ""])
    near_misses = _buy_initiate_candidates(snapshot)
    if near_misses:
        for candidate in near_misses:
            reason = candidate.reason_labels[0] if candidate.reason_labels else "No current action."
            lines.append(
                "- **"
                + _link(
                    f"{candidate.ticker} — {candidate.company_name}",
                    candidate.research_page,
                )
                + ":** "
                f"{RATING_LABELS[candidate.canonical_rating]} / "
                f"{PORTFOLIO_ACTION_LABELS[candidate.portfolio_action]} · "
                f"{_markdown(_candidate_state_label(candidate))} · "
                f"expected return {_rounded_percentage(candidate.expected_return_pct)} · "
                f"{_markdown(reason)}"
            )
    else:
        lines.append("No security currently has both a Buy rating and an Initiate action.")
    coverage = snapshot.coverage
    lines.extend(
        [
            "",
            "## Performance, risk, and coverage",
            "",
            f"- Cumulative return: **{snapshot.performance.cumulative_return_pct}%**",
            f"- Running drawdown: **{snapshot.performance.running_drawdown_pct}%**",
            f"- Largest position: **{snapshot.performance.largest_position_weight_pct}%**",
            f"- Current assessments: **{coverage.current_assessment_count}/"
            f"{coverage.allocation_candidate_count}**",
            f"- Relationship reviews: **{coverage.reviewed_relationship_count}/"
            f"{coverage.required_relationship_review_count}**",
            f"- Accepted relationships: **{coverage.accepted_relationship_count}**",
            f"- Market retrieval failures: **{coverage.market_data_failure_count}**",
            "",
            "## Explore",
            "",
            "- [[model-portfolio|Model portfolio]]",
            "- [[security-catalog|Securities]]",
            "- [[signals|Signals and research alerts]]",
            "- [[performance|Performance and risk]]",
            "- [[research-catalog|Research catalog]]",
            "- [[system-status|System status and audit]]",
            f"- {latest_report}" if latest_report else "- No daily report is available yet.",
            "",
        ]
    )
    return "\n".join(lines)


def _portfolio_html(rows: Sequence[ModelPortfolioRow], currency: str) -> str:
    output = [
        '<div class="model-portfolio-grid" id="model-portfolio-grid">',
    ]
    for row in rows:
        scalable = (
            row.holding_type == "security"
            and row.instrument_type == "equity"
            and required_decimal(row.target_value_base, label="target value") > 0
        )
        label = "Cash" if row.holding_type == "cash" else f"{row.ticker} — {row.company_name}"
        output.extend(
            [
                '<article class="portfolio-card" '
                f'data-scalable="{"true" if scalable else "false"}" '
                f'data-target-weight="{_html(row.target_weight_pct)}" '
                f'data-mark="{_html(row.mark)}" data-fx="{_html(row.fx_rate_to_base)}" '
                f'data-mark-currency="{_html(row.mark_currency)}" '
                f'data-market-data-as-of="{_html(row.market_data_as_of)}" '
                f'data-ticker="{_html(row.ticker)}" '
                f'data-company="{_html(row.company_name or "Cash")}">',
                (
                    f'<h3><a href="{_html(_page_key(row.security_research_page))}">'
                    f"{_html(label)}</a></h3>"
                    if row.security_research_page
                    else f"<h3>{_html(label)}</h3>"
                ),
                '<dl class="portfolio-card-values">',
                f"<div><dt>Current</dt><dd>{_html(row.current_weight_pct)}%</dd></div>",
                f"<div><dt>Target</dt><dd>{_html(row.target_weight_pct)}%</dd></div>",
                f"<div><dt>Action</dt><dd>{_html(_action_label(row.action))}</dd></div>",
                f"<div><dt>State</dt><dd>{_html(_action_status_label(row.action_status))}</dd></div>",
                "<div><dt>Research rating</dt><dd>"
                f"{_html(RATING_LABELS[row.canonical_rating])}</dd></div>",
                "<div><dt>Research action</dt><dd>"
                f"{_html(PORTFOLIO_ACTION_LABELS[row.portfolio_action])}</dd></div>",
                f"<div><dt>Reference mark</dt><dd>{_html(row.mark)} "
                f"{_html(row.mark_currency)}</dd></div>",
                f"<div><dt>Base mark</dt><dd>{_html(row.mark_base)} {_html(currency)}</dd></div>",
                f"<div><dt>FX to {_html(currency)}</dt><dd>{_html(row.fx_rate_to_base)}"
                f" · {_html(row.fx_as_of)}</dd></div>",
                f"<div><dt>As of</dt><dd>{_html(row.market_data_as_of)}</dd></div>",
                "</dl>",
                (
                    '<p><a href="'
                    + _html(_page_key(row.strategy_research_page))
                    + '">Strategy research</a></p>'
                    if row.strategy_research_page
                    else ""
                ),
                "</article>",
            ]
        )
    output.append("</div>")
    output.append(
        f'<p class="portfolio-base">Values use the committed {_html(currency)} snapshot.</p>'
    )
    return "\n".join(output)


def _model_portfolio_page(snapshot: DecisionSnapshot, day: date) -> str:
    current = snapshot.current_portfolio
    lines = [
        _frontmatter(
            title="PaperTrader model portfolio",
            page_type="model-portfolio",
            tag="model-portfolio",
            day=day,
            snapshot=snapshot,
        ),
        "# Model portfolio",
        "",
        f"**As of `{snapshot.as_of}`**",
        "",
        "Pending targets are projections; only deterministic fills change the current portfolio.",
        "",
        _portfolio_html(current.rows, snapshot.base_currency),
        "",
        '<div class="portfolio-controls" aria-label="Portfolio copy and scaling tools">',
        '<button type="button" id="copy-portfolio">Copy portfolio as TSV</button>',
        '<a class="button-link" href="data/model_portfolio.csv" download>'
        "Download committed CSV</a>",
        '<a class="button-link" href="data/decision_snapshot.json" download>'
        "Download snapshot JSON</a>",
        '<label for="reference-notional">Reference portfolio value</label>',
        '<input id="reference-notional" type="number" min="0" step="100" inputmode="decimal">',
        '<button type="button" id="scale-portfolio">Calculate whole-share quantities</button>',
        "</div>",
        '<p class="scaler-notice">The calculation runs only in this browser and does not '
        "write portfolio state.</p>",
        '<div id="scaled-portfolio" aria-live="polite"></div>',
        "",
        "## Valuation and thesis detail",
        "",
        "| Holding | Rating / action | Bear / base / bull | Expected | Buy below | "
        "Review | Thesis or cash role |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in current.rows:
        label = "Cash" if row.holding_type == "cash" else f"{row.ticker} — {row.company_name}"
        linked = label if row.holding_type == "cash" else _link(label, row.security_research_page)
        lines.append(
            f"| {linked} | {RATING_LABELS[row.canonical_rating]} / "
            f"{PORTFOLIO_ACTION_LABELS[row.portfolio_action]} | "
            f"{row.bear_return_pct or '—'}% / {row.base_return_pct or '—'}% / "
            f"{row.bull_return_pct or '—'}% | {row.expected_return_pct or '—'}% | "
            f"{row.buy_below_price or '—'} | {_cell(row.review_at)} | "
            f"{_cell(row.thesis_summary)} |"
        )
    lines.extend(["", "[[index|Back to today's decision]]", ""])
    return "\n".join(lines)


def _signal_detail(signal: ActionableSignalView) -> list[str]:
    quantity = (
        signal.quantity
        if signal.quantity
        else "See canonical legs in snapshot JSON"
        if signal.copy_ready
        else "Awaiting deterministic order validation"
    )
    order_description = _markdown(signal.order_type or "not yet validated")
    if signal.limit_price:
        order_description = f"{order_description} {_markdown(signal.limit_price)}"
    return [
        f"### {_link(f'{signal.ticker} — {signal.company_name}', signal.security_research_page)}",
        "",
        f"- **Action:** {_action_label(signal.action)}",
        f"- **State:** {_action_status_label(signal.action_status)}",
        f"- **Strategy:** {_markdown(signal.strategy_name)}",
        f"- **Strategy research:** {_link('Open strategy page', signal.strategy_research_page)}",
        f"- **Window:** `{signal.created_at}` to `{signal.expires_at}`",
        f"- **Market data:** `{signal.market_data_as_of}`",
        f"- **Current → target:** {signal.current_weight_pct}% → {signal.target_weight_pct}%",
        f"- **Copy-ready quantity:** {_markdown(quantity)}",
        f"- **Order:** {order_description}",
        f"- **Entry:** {_markdown(signal.entry_rule)}",
        f"- **Exit:** {_markdown(signal.exit_rule)}",
        f"- **Invalidation:** {_markdown(signal.invalidation)}",
        f"- **Rationale:** {_markdown(signal.rationale)}",
        "",
    ]


def _signals_page(repository_root: Path, snapshot: DecisionSnapshot, day: date) -> str:
    pending = tuple(signal for signal in snapshot.actionable_signals if signal.order_id)
    strategies = {row["strategy_id"]: row for row in read_table(repository_root, "strategies")}
    securities = {row["security_id"]: row for row in read_table(repository_root, "securities")}
    snapshot_as_of = parse_timestamp(snapshot.as_of)
    assert snapshot_as_of is not None
    completed: list[tuple[Mapping[str, str], Mapping[str, str], Mapping[str, str]]] = []
    for row in read_table(repository_root, "signals"):
        created = parse_timestamp(row["created_at"])
        if (
            row["status"] not in {"filled", "cancelled", "expired"}
            or created is None
            or created > snapshot_as_of
        ):
            continue
        strategy = strategies.get(row["strategy_id"])
        security = securities.get(strategy["security_id"]) if strategy else None
        if strategy is None or security is None:
            raise CanonicalValueError(f"completed signal lacks public identity: {row['signal_id']}")
        completed.append((row, strategy, security))
    lines = [
        _frontmatter(
            title="PaperTrader signals and research alerts",
            page_type="signals",
            tag="signals",
            day=day,
            snapshot=snapshot,
        ),
        "# Signals",
        "",
        f"**As of `{snapshot.as_of}`**",
        "",
        "## Actionable trade signals",
        "",
    ]
    if snapshot.actionable_signals:
        for signal in snapshot.actionable_signals:
            lines.extend(_signal_detail(signal))
    else:
        lines.extend(["No actionable trade signals.", ""])
    lines.extend(["## Pending validated orders", ""])
    if pending:
        lines.extend(
            f"- **{_markdown(signal.ticker)}:** {_action_label(signal.action)} · "
            f"{_action_status_label(signal.action_status)}"
            for signal in pending
        )
    else:
        lines.append("No pending orders.")
    lines.extend(["", "## Research alerts — not trade signals", ""])
    if snapshot.research_alerts:
        for alert in snapshot.research_alerts:
            alert_security = securities.get(alert.security_id)
            security_page = (
                alert_security["research_page"]
                if alert_security is not None
                else alert.research_page
            )
            lines.extend(
                [
                    f"### {_link(f'{alert.ticker} — {alert.company_name}', security_page)}",
                    "",
                    f"**{alert.visible_label}**",
                    "",
                    f"- Alert: `{_markdown(alert.alert_type)}`",
                    f"- Market date: `{alert.market_data_date}`",
                    f"- Research status: `{_markdown(alert.research_status)}`",
                    f"- Conclusion: {_markdown(alert.research_conclusion)}",
                    "",
                ]
            )
    else:
        lines.append("No current research alerts.")
    lines.extend(["", "## Recently expired or completed signals", ""])
    if completed:
        for completed_row, completed_strategy, completed_security in sorted(
            completed,
            key=lambda value: (value[0]["created_at"], value[0]["signal_id"]),
            reverse=True,
        )[:20]:
            label = f"{completed_security['ticker']} — {completed_security['company_name']}"
            lines.append(
                f"- **{_markdown(completed_row['status'].title())}:** "
                f"{_link(label, completed_security['research_page'])} — "
                f"{_link(completed_strategy['name'], completed_strategy['research_page'])} · "
                f"created `{completed_row['created_at']}`"
            )
    else:
        lines.append("No recently expired or completed signals.")
    lines.extend(["", "[[index|Back to today's decision]]", ""])
    return "\n".join(lines)


def _performance_svg(history: Sequence[Mapping[str, str]]) -> str:
    if not history:
        return '<p role="img" aria-label="No equity history is available.">No equity history.</p>'
    equities = [required_decimal(row["equity_base"], label="chart equity") for row in history]
    low, high = min(equities), max(equities)
    span = high - low
    points: list[str] = []
    for index, value in enumerate(equities):
        x = Decimal(index) / Decimal(max(len(equities) - 1, 1)) * Decimal("100")
        y = Decimal("45") if span == 0 else Decimal("90") - ((value - low) / span * Decimal("80"))
        points.append(f"{x.quantize(Decimal('0.01'))},{y.quantize(Decimal('0.01'))}")
    description = (
        f"Equity history from {history[0]['date']} to {history[-1]['date']}; "
        f"latest equity {history[-1]['equity_base']}."
    )
    return (
        '<svg class="performance-chart" viewBox="0 0 100 100" role="img" '
        f'aria-label="{_html(description)}"><title>Model equity history</title>'
        f"<desc>{_html(description)}</desc>"
        '<polyline fill="none" stroke="currentColor" stroke-width="2" '
        f'points="{" ".join(points)}" />'
        "</svg>"
    )


def _performance_page(snapshot: DecisionSnapshot, day: date) -> str:
    performance = snapshot.performance
    lines = [
        _frontmatter(
            title="PaperTrader performance and risk",
            page_type="performance",
            tag="performance",
            day=day,
            snapshot=snapshot,
        ),
        "# Performance and risk",
        "",
        f"**As of `{snapshot.as_of}`**",
        "",
        f"Current performance epoch started `{performance.epoch_started_at}` at "
        f"**{performance.epoch_opening_equity_base} {snapshot.base_currency}**. "
        f"Prior audit epochs retained: **{performance.prior_epoch_count}**.",
        "",
        _performance_svg(performance.history),
        "",
        "| Daily return | Cumulative return | Drawdown | Realized P/L | Unrealized P/L |",
        "| ---: | ---: | ---: | ---: | ---: |",
        f"| {performance.daily_return_pct}% | {performance.cumulative_return_pct}% | "
        f"{performance.running_drawdown_pct}% | {performance.realized_pnl_base} "
        f"{snapshot.base_currency} | {performance.unrealized_pnl_base} "
        f"{snapshot.base_currency} |",
        "",
        "## Exposure and concentration",
        "",
        f"- Cash: {snapshot.current_portfolio.cash_weight_pct}%",
        f"- Invested exposure: {snapshot.current_portfolio.invested_weight_pct}%",
        f"- Conviction exposure: {performance.conviction_exposure_base} {snapshot.base_currency}",
        f"- Baseline exposure: {performance.baseline_exposure_base} {snapshot.base_currency}",
        f"- Largest position: {performance.largest_position_weight_pct}%",
        f"- Largest sector: {performance.largest_sector_weight_pct}%",
        "",
        "## Target allocation changes",
        "",
    ]
    changes = [
        row
        for row in snapshot.target_portfolio.rows
        if row.holding_type == "security" and row.action in {"buy", "add", "trim", "exit"}
    ]
    if changes:
        lines.extend(
            f"- **{_link(f'{row.ticker} — {row.company_name}', row.security_research_page)}:** "
            f"{_action_label(row.action)} from {row.current_weight_pct}% to "
            f"{row.target_weight_pct}%"
            for row in changes
        )
    else:
        lines.append("No target allocation changes.")
    lines.extend(
        [
            "",
            "## Committed history",
            "",
            "| Date | Equity | Cash | Gross exposure | Daily return | "
            "Cumulative return | Drawdown |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    lines.extend(
        f"| {row['date']} | {row['equity_base']} | {row['cash_base']} | "
        f"{row['gross_exposure_base']} | {row['daily_return_pct']}% | "
        f"{row['cumulative_return_pct']}% | {row['drawdown_pct']}% |"
        for row in performance.history
    )
    lines.extend(
        ["", "No external benchmark is used.", "", "[[index|Back to today's decision]]", ""]
    )
    return "\n".join(lines)


def _securities_page(repository_root: Path, snapshot: DecisionSnapshot, day: date) -> str:
    """Render every tracked instrument with readable valuation and freshness context."""

    as_of = parse_timestamp(snapshot.as_of)
    assert as_of is not None
    latest = {row["security_id"]: row for row in read_table(repository_root, "market_latest")}
    assessments = {
        row["security_id"]: row
        for row in read_table(repository_root, "security_assessments")
        if (parse_timestamp(row["assessed_at"]) or as_of) <= as_of
    }
    candidates = {candidate.security_id: candidate for candidate in snapshot.candidate_pipeline}
    lines = [
        _frontmatter(
            title="PaperTrader tracked securities",
            page_type="securities-dashboard",
            tag="security",
            day=day,
            snapshot=snapshot,
        ),
        "# Securities",
        "",
        f"**As of `{snapshot.as_of}`**",
        "",
        "Ticker links open the maintained security analysis. Prices and buy-below levels "
        "use each security's listing currency. Return estimates are rounded to whole "
        "percentage points, and update dates are shown in UTC.",
        "",
        "| "
        + " | ".join(
            _column_header(key, label, description)
            for key, label, description, _alignment in SECURITY_TABLE_COLUMNS
        )
        + " |",
        "| "
        + " | ".join(alignment for _key, _label, _description, alignment in SECURITY_TABLE_COLUMNS)
        + " |",
    ]
    for security in sorted(
        read_table(repository_root, "securities"),
        key=lambda row: (row["ticker"], row["venue_mic"], row["security_id"]),
    ):
        market = latest.get(security["security_id"])
        assessment = assessments.get(security["security_id"])
        candidate = candidates.get(security["security_id"])
        mark_text = "—"
        data_as_of = "— / —"
        if market is not None and market["status"] == "ok":
            raw_mark = market["adjusted_close"] or market["close"]
            mark = required_decimal(raw_mark, label="security dashboard mark")
            fx_as_of = ""
            if security["currency"] == snapshot.base_currency:
                fx_as_of = market["retrieved_at"]
            else:
                rates = [
                    rate
                    for rate in read_fx_cache(
                        repository_root, security["currency"], snapshot.base_currency
                    )
                    if rate.retrieved_at <= as_of and rate.date <= as_of.date()
                ]
                if rates:
                    fx = max(rates, key=lambda value: (value.date, value.retrieved_at))
                    fx_as_of = format_timestamp(fx.retrieved_at)
            display_mark = mark.quantize(Decimal("0.0001"))
            mark_text = f"{decimal_text(display_mark)} {security['currency']}"
            data_as_of = _data_fx_update(market["retrieved_at"], fx_as_of)
        decision = "Unassessed"
        reason = "—"
        scenario = "— / — / —"
        expected_return = "—"
        buy_below = "—"
        rating_action = "Unrated / Watch"
        review = security["next_review_at"]
        if assessment is not None:
            bear_return = (
                candidate.bear_return_pct
                if candidate is not None
                else assessment.get("bear_return_pct") or assessment["downside_pct"]
            )
            base_return = (
                candidate.base_return_pct
                if candidate is not None
                else assessment.get("base_return_pct") or assessment["base_upside_pct"]
            )
            bull_return = (
                candidate.bull_return_pct
                if candidate is not None
                else assessment.get("bull_return_pct") or ""
            )
            scenario = " / ".join(
                _rounded_percentage(value) for value in (bear_return, base_return, bull_return)
            )
            expected_return = _rounded_percentage(
                candidate.expected_return_pct
                if candidate is not None
                else assessment.get("expected_return_pct") or ""
            )
            buy_below_price = assessment.get("buy_below_price") or ""
            buy_below = _currency_amount(
                buy_below_price, security["currency"], label="buy-below price"
            )
            rating = (
                candidate.canonical_rating
                if candidate is not None
                else assessment.get("canonical_rating") or "unrated"
            )
            action = (
                candidate.portfolio_action
                if candidate is not None
                else assessment.get("portfolio_action") or "watch"
            )
            rating_action = f"{RATING_LABELS[rating]} / {PORTFOLIO_ACTION_LABELS[action]}"
            review = assessment["expires_at"] or review
        if candidate is not None:
            decision = _candidate_state_label(candidate)
            if candidate.reason_labels:
                reason = candidate.reason_labels[0]
        label = f"{security['ticker']} — {security['company_name']}"
        anchor = f'<span id="security-{security["security_id"]}"></span>'
        lines.append(
            f"| {anchor}{_link(label, _security_public_page(security))} | "
            f"{mark_text} | {_cell(rating_action)} | {_cell(decision)} | "
            f"{_cell(reason)} | {scenario} | {expected_return} | {buy_below} | "
            f"{_cell(data_as_of)} | {_cell(_utc_day(review))} |"
        )
    lines.extend(["", "[[index|Back to today's decision]]", ""])
    return "\n".join(lines)


def _system_status_page(repository_root: Path, snapshot: DecisionSnapshot, day: date) -> str:
    coverage = snapshot.coverage
    remediation_operations = sorted(
        (
            operation
            for operation in read_table(repository_root, "operations_todo")
            if operation["source"].startswith("issue-remediation:")
        ),
        key=lambda operation: (-int(operation["priority"]), operation["operation_id"]),
    )
    candidate_fx_gaps = sum(
        "fx_unavailable" in candidate.reason_codes for candidate in snapshot.candidate_pipeline
    )
    last_success = parse_timestamp(coverage.last_successful_daily_run, allow_empty=True)
    latest_run = last_success.date().isoformat() if last_success is not None else "none"
    lines = [
        _frontmatter(
            title="PaperTrader system status and audit",
            page_type="system-status",
            tag="system-status",
            day=day,
            snapshot=snapshot,
        ),
        "# System status and audit",
        "",
        f"**As of:** `{snapshot.as_of}`",
        f"**Investment data:** {INVESTMENT_STATUS_LABELS[snapshot.investment_data_status]}",
        f"**Operations:** {OPERATIONS_STATUS_LABELS[snapshot.operations_status]}",
        "**Publication validation:** Snapshot and exports validated",
        "**Portfolio reconciliation:** Reconciled",
        "",
        "Publication validation confirms that this generated artifact is internally consistent. "
        "Investment and operations health below describe the current canonical inputs.",
        "",
        "## Current investment health",
        "",
        f"- Assessments: {coverage.current_assessment_count}/{coverage.allocation_candidate_count}",
        f"- Fresh-evidence assessments: {coverage.fresh_evidence_assessment_count}/"
        f"{coverage.allocation_candidate_count}",
        f"- Relationship reviews: {coverage.reviewed_relationship_count}/"
        f"{coverage.required_relationship_review_count}",
        f"- Accepted relationships: {coverage.accepted_relationship_count}",
        f"- Market success/failure: {coverage.market_data_success_count}/"
        f"{coverage.market_data_failure_count}",
        f"- Candidate FX gaps: {candidate_fx_gaps}",
        f"- Last successful daily run: {latest_run}",
        "",
        "## Queue and execution health",
        "",
        f"- Ready or active strategies: {coverage.ready_or_active_strategy_count}",
        f"- Active signals: {coverage.active_signal_count}",
        f"- Pending orders: {coverage.pending_order_count}",
        f"- Queued remediation operations: {len(remediation_operations)}",
        "- Operations are claimed and executed strictly sequentially.",
    ]
    lines.extend(
        f"  - {operation['operation_type'].replace('_', ' ').title()} "
        f"({operation['status']}, priority {operation['priority']}) — "
        f"{_markdown(operation['prompt'])}"
        for operation in remediation_operations
    )
    lines.extend(
        [
            "",
            "## Sequential research backlog",
            "",
            f"- Research backlog: {coverage.research_backlog_count}",
            "",
            "## Publication health",
            "",
            "- Snapshot schema and derived CSV equality: validated",
            "- Portfolio accounting reconciliation: validated",
            "",
            "## Current issues by investment impact",
            "",
            f"Current unresolved issues: **{len(snapshot.system_impacts)}**.",
            "Resolved and superseded issues remain in the canonical audit but are not current "
            "health.",
            "",
        ]
    )
    if snapshot.system_impacts:
        grouped: defaultdict[str, list[SystemImpact]] = defaultdict(list)
        for impact in snapshot.system_impacts:
            grouped[impact.impact].append(impact)
        for category in (
            "blocks_portfolio",
            "blocks_action",
            "affects_candidate",
            "publication_only",
            "operational_only",
        ):
            values = grouped.get(category, [])
            if not values:
                continue
            lines.extend(
                [
                    f"### {_markdown(category.replace('_', ' ').title())} ({len(values)})",
                    "",
                ]
            )
            for value in values:
                label = f"{value.ticker} — {value.company_name}: " if value.ticker else ""
                public_title = _markdown(label + value.title)
                lines.append(
                    f"- {value.severity.capitalize()} **{public_title}** — "
                    f"{_markdown(value.summary)}"
                )
            lines.append("")
    else:
        lines.extend(["No open issues.", ""])
    lines.extend(
        [
            "## Historical audit health",
            "",
            "- Resolved and superseded incidents remain visible in canonical issue and operation "
            "history.",
            "- No unresolved issue is hidden or aged out.",
        ]
    )
    lines.extend(
        [
            "",
            "## Audit links",
            "",
            "- [[research-catalog|Complete research catalog]]",
            "- [[security-catalog|Tracked securities]]",
            "- [[SCHEMA|Wiki schema]]",
            "- [[log|Append-only research log]]",
            "- [Decision snapshot JSON](data/decision_snapshot.json)",
            "- [Model portfolio CSV](data/model_portfolio.csv)",
            "- [Actionable signals CSV](data/actionable_signals.csv)",
            "",
            "[[index|Back to today's decision]]",
            "",
        ]
    )
    return "\n".join(lines)


def _read_frontmatter(path: Path) -> Mapping[object, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise CanonicalValueError(f"maintained wiki page lacks frontmatter: {path}")
    raw, _ = text[4:].split("\n---\n", maxsplit=1)
    value = yaml.safe_load(raw)
    if not isinstance(value, Mapping):
        raise CanonicalValueError(f"maintained wiki page has invalid frontmatter: {path}")
    return value


def _catalog(repository_root: Path, snapshot: DecisionSnapshot, day: date) -> str:
    wiki_root = repository_root / "data" / "wiki"
    grouped: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    for path in sorted(wiki_root.rglob("*.md")):
        relative = path.relative_to(wiki_root)
        if "raw" in relative.parts or "_archive" in relative.parts or relative.name == "index.md":
            continue
        metadata = _read_frontmatter(path)
        title = str(metadata.get("title", path.stem))
        page_type = str(metadata.get("type", "other"))
        key = PurePosixPath(relative).with_suffix("").as_posix()
        grouped[page_type].append((title, key))
    lines = [
        _frontmatter(
            title="PaperTrader research catalog",
            page_type="research-catalog",
            tag="research",
            day=day,
            snapshot=snapshot,
        ),
        "# Research catalog",
        "",
        "This is the complete maintained research and audit catalog. The homepage remains "
        "focused on "
        "the current investor decision.",
        "",
    ]
    assessment_history = read_table(repository_root, "security_assessment_history")
    lines.extend(
        [
            "## Assessment revision audit",
            "",
            f"- Immutable assessment versions: **{len(assessment_history)}**",
            "- Securities with retained revisions: "
            f"**{len({row['security_id'] for row in assessment_history})}**",
            "",
        ]
    )
    for page_type in sorted(grouped):
        lines.extend([f"## {_markdown(page_type.replace('-', ' ').title())}", ""])
        for title, key in sorted(
            grouped[page_type], key=lambda value: (value[0].lower(), value[1])
        ):
            safe_title = _markdown(title)
            lines.append(f"- [{safe_title}]({key})")
        lines.append("")
    lines.extend(["[[index|Back to today's decision]]", ""])
    return "\n".join(lines)


def _latest_report_link(repository_root: Path) -> str:
    reports = sorted(
        (repository_root / "data" / "wiki" / "daily-reports").glob("daily-report_*.md")
    )
    if not reports:
        return ""
    path = reports[-1]
    raw_date = path.stem.removeprefix("daily-report_")
    label = (
        f"Daily report {raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
        if len(raw_date) == 8
        else path.stem
    )
    return f"[[daily-reports/{path.stem}|{label}]]"


def refresh_investor_pages(repository_root: Path, snapshot: DecisionSnapshot) -> tuple[Path, ...]:
    """Atomically regenerate every investor page from one committed-state snapshot."""

    snapshot = _public_snapshot(repository_root, snapshot)
    day = date.fromisoformat(snapshot.report_date)
    wiki_root = repository_root / "data" / "wiki"
    paths = {
        "model-portfolio.md": _model_portfolio_page(snapshot, day),
        "security-catalog.md": _securities_page(repository_root, snapshot, day),
        "performance.md": _performance_page(snapshot, day),
        "system-status.md": _system_status_page(repository_root, snapshot, day),
    }
    for name, text in paths.items():
        atomic_write_text(wiki_root / name, text, allowed_root=wiki_root)
    signal_text = _signals_page(repository_root, snapshot, day)
    atomic_write_text(wiki_root / "signals.md", signal_text, allowed_root=wiki_root)
    catalog_path = wiki_root / "research-catalog.md"
    atomic_write_text(
        catalog_path, _catalog(repository_root, snapshot, day), allowed_root=wiki_root
    )
    register_wiki_page(
        wiki_root,
        page_key="model-portfolio",
        label="Model portfolio",
        section="Dashboards",
        event=f"Published investor decision snapshot `{snapshot.snapshot_id}`.",
        event_date=day,
    )
    # Rebuild after the log mutation so the complete catalog points at its current version.
    atomic_write_text(
        catalog_path, _catalog(repository_root, snapshot, day), allowed_root=wiki_root
    )
    index_path = wiki_root / "index.md"
    atomic_write_text(
        index_path,
        _homepage(snapshot, day, _latest_report_link(repository_root)),
        allowed_root=wiki_root,
    )
    return tuple(
        wiki_root / name
        for name in (
            "index.md",
            "model-portfolio.md",
            "security-catalog.md",
            "signals.md",
            "performance.md",
            "system-status.md",
            "research-catalog.md",
        )
    )
