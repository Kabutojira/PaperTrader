"""Deterministic investor-first Markdown views over one decision snapshot."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import date
from decimal import Decimal
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
from papertrader.tables import read_table
from papertrader.utils import CanonicalValueError, decimal_text, parse_timestamp, required_decimal
from papertrader.wiki import register_wiki_page

INVESTOR_BRIEF_START = "<!-- papertrader-investor-brief:start -->"
INVESTOR_BRIEF_END = "<!-- papertrader-investor-brief:end -->"
DASHBOARD_PAGES = frozenset({"index", "model-portfolio", "signals", "performance", "system-status"})
STANCE_LABELS = {
    "hold_cash": "No trade — hold 100% cash",
    "maintain": "Maintain the current model portfolio",
    "deploy": "Deploy approved paper capital",
    "rebalance": "Rebalance toward approved paper targets",
    "reduce_risk": "Reduce model-portfolio risk",
    "exit": "Exit the approved model exposure",
    "blocked": "Decision blocked — do not copy actions",
}
STATUS_LABELS = {
    "current": "Current",
    "degraded": "Degraded — review coverage and data gaps",
    "blocked": "Blocked — current exposure cannot be projected safely",
}
CLASSIFICATION_LABELS = {
    "approved": "Approved candidate",
    "strategy_pending": "Strategy research pending",
    "relationship_pending": "Relationship research pending",
    "assessment_pending": "Assessment pending",
    "market_data_blocked": "Market data blocked",
    "valuation_unattractive": "Valuation unattractive",
    "risk_blocked": "Risk blocked",
    "research_blocked": "Research incomplete",
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
    "pending_order": "Pending validated paper order",
    "active_signal": "Active signal",
    "awaiting_order_validation": "Awaiting deterministic order validation",
    "research_candidate": "Research candidate",
    "blocked": "Blocked",
    "no_action": "No action",
}


def _markdown(value: str) -> str:
    normalized = " ".join(value.split())
    escaped = escape(normalized, quote=False).replace("\\", "\\\\")
    return re.sub(r"([`*_\[\]|])", r"\\\1", escaped)


def _html(value: str) -> str:
    return escape(" ".join(value.split()), quote=True)


def _cell(value: str) -> str:
    return _markdown(value) or "—"


def _page_key(research_page: str) -> str:
    if not research_page:
        return ""
    path = PurePosixPath(research_page)
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.parts[:2] != ("data", "wiki")
        or path.suffix != ".md"
    ):
        raise CanonicalValueError(f"invalid public research page: {research_page}")
    return PurePosixPath(*path.parts[2:]).with_suffix("").as_posix()


def _link(label: str, research_page: str) -> str:
    key = _page_key(research_page)
    return f"[{_markdown(label)}]({key})" if key else _markdown(label)


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


def _near_misses(snapshot: DecisionSnapshot, *, limit: int = 5) -> tuple[CandidateView, ...]:
    return tuple(
        candidate
        for candidate in snapshot.candidate_pipeline
        if candidate.classification not in {"assessment_pending", "research_blocked"}
        and candidate.reason_codes
    )[:limit]


def _portfolio_markdown_rows(rows: Sequence[ModelPortfolioRow]) -> list[str]:
    output: list[str] = []
    for row in rows:
        holding = (
            "Cash"
            if row.holding_type == "cash"
            else _link(f"{row.ticker} — {row.company_name}", row.research_page)
        )
        output.append(
            f"| {holding} | {_cell(row.sleeve)} | {row.current_weight_pct}% | "
            f"{row.approved_target_weight_pct}% | {_money(row.current_value_base, '')} | "
            f"{_money(row.approved_target_value_base, '')} | "
            f"{_action_label(row.action)} | {_action_status_label(row.action_status)} |"
        )
    return output


def investor_brief_markdown(snapshot: DecisionSnapshot) -> str:
    """Render the compact committed brief consumed by Telegram."""

    current = snapshot.current_portfolio
    target = snapshot.approved_target_portfolio
    lines = [
        f"# {STANCE_LABELS[snapshot.stance]}",
        "",
        f"- **Data status:** {STATUS_LABELS[snapshot.data_status]}",
        f"- **As of:** `{snapshot.as_of}`",
        f"- **Snapshot:** `{snapshot.snapshot_id}`",
        f"- **Cash:** {current.cash_base} {snapshot.base_currency} ({current.cash_weight_pct}%)",
        f"- **Gross exposure:** {current.gross_exposure_base} {snapshot.base_currency}",
        f"- **Approved target cash:** {target.cash_base} {snapshot.base_currency} "
        f"({target.cash_weight_pct}%)",
        f"- **Actionable signals:** {len(snapshot.actionable_signals)}",
    ]
    changes = [
        row
        for row in target.rows
        if row.holding_type == "security" and row.action in {"buy", "add", "trim", "exit"}
    ]
    lines.extend(["", "## Approved target changes", ""])
    if changes:
        lines.extend(
            f"- **{_markdown(row.ticker)}:** {_action_label(row.action)} to "
            f"{row.approved_target_weight_pct}% (paper estimate)"
            for row in changes[:5]
        )
    else:
        lines.append("No approved target changes.")
    lines.extend(["", "## Actionable signals", ""])
    if snapshot.actionable_signals:
        lines.extend(
            f"- **{_markdown(signal.ticker)}:** {_action_label(signal.action)} — "
            f"{_action_status_label(signal.action_status)}"
            for signal in snapshot.actionable_signals[:5]
        )
    else:
        lines.append("No actionable trade signals.")
    near_miss = next(iter(_near_misses(snapshot, limit=1)), None)
    lines.extend(["", "## Top blocker or near miss", ""])
    if near_miss is None:
        lines.append("No assessed near miss is available; research coverage remains incomplete.")
    else:
        reason = near_miss.reason_labels[0] if near_miss.reason_labels else "No approved trade."
        lines.append(
            f"- **{_markdown(near_miss.ticker)} — {_markdown(near_miss.company_name)}:** "
            f"{_markdown(reason)}"
        )
    return "\n".join(lines)


def investor_report_sections(snapshot: DecisionSnapshot) -> list[str]:
    """Render the investor-facing report sections from the shared snapshot."""

    current = snapshot.current_portfolio
    target = snapshot.approved_target_portfolio
    lines = [
        "## 1. Investor decision summary",
        "",
        INVESTOR_BRIEF_START,
        investor_brief_markdown(snapshot),
        INVESTOR_BRIEF_END,
        "",
        "### Deterministic reasons",
        "",
        *_reason_lines(snapshot.stance_reason_codes),
        "",
        "## 2. Model portfolio and approved changes",
        "",
        f"- Current equity: {current.equity_base} {snapshot.base_currency}",
        f"- Current cash: {current.cash_base} {snapshot.base_currency} "
        f"({current.cash_weight_pct}%)",
        f"- Current gross exposure: {current.gross_exposure_base} {snapshot.base_currency}",
        f"- Approved target cash: {target.cash_base} {snapshot.base_currency} "
        f"({target.cash_weight_pct}%)",
        "- Pending-order targets are estimates at the snapshot mark; only fills change accounting.",
        "",
        "| Holding | Sleeve | Current weight | Approved target | Current value | "
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
                    + _link(f"{signal.ticker} — {signal.company_name}", signal.research_page),
                    "",
                    f"- Action: **{_action_label(signal.action)}**",
                    f"- State: {_action_status_label(signal.action_status)} ({copy})",
                    f"- Strategy: {_markdown(signal.strategy_name)}",
                    f"- Signal window: `{signal.created_at}` to `{signal.expires_at}`",
                    f"- Market data: `{signal.market_data_as_of}`",
                    f"- Rationale: {_markdown(signal.rationale)}",
                    "",
                ]
            )
    else:
        lines.extend(["No actionable trade signals.", "", "No pending paper orders.", ""])
    lines.extend(["## 4. Candidates and near misses", ""])
    near_misses = _near_misses(snapshot)
    if near_misses:
        lines.extend(
            [
                "| Candidate | State | Score | Base upside | Main reason |",
                "| --- | --- | ---: | ---: | --- |",
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
                f"{_markdown(CLASSIFICATION_LABELS[candidate.classification])} | "
                f"{candidate.effective_score or '—'} | {candidate.base_upside_pct or '—'}% | "
                f"{_cell(main_reason)} |"
            )
    else:
        lines.append(
            "No assessed near misses are available; incomplete assessments remain coverage gaps."
        )
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
    target = snapshot.approved_target_portfolio
    lines = [
        _frontmatter(
            title="PaperTrader — today's paper-investment decision",
            page_type="dashboard",
            tag="dashboard",
            day=day,
            snapshot=snapshot,
        ),
        "# PaperTrader",
        "",
        f"**As of `{snapshot.as_of}` · Data status: {STATUS_LABELS[snapshot.data_status]}**",
        "",
        f"## {STANCE_LABELS[snapshot.stance]}",
        "",
        _status_cards(snapshot),
        "",
        "Paper-only model output for research and simulation; it is not personalized "
        "investment advice.",
        "",
        "### Why",
        "",
        *_reason_lines(snapshot.stance_reason_codes),
        "",
        "## Current and approved target portfolio",
        "",
        f"Current equity is **{current.equity_base} {snapshot.base_currency}** with "
        f"**{current.cash_weight_pct}% cash**. The approved target retains "
        f"**{target.cash_weight_pct}% cash**.",
        "",
        "| Holding | Current | Approved target | Action |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in current.rows:
        label = "Cash" if row.holding_type == "cash" else f"{row.ticker} — {row.company_name}"
        linked = label if row.holding_type == "cash" else _link(label, row.research_page)
        lines.append(
            f"| {linked} | {row.current_weight_pct}% | "
            f"{row.approved_target_weight_pct}% | {_action_label(row.action)} |"
        )
    lines.extend(["", "## Actionable trade signals", ""])
    if snapshot.actionable_signals:
        lines.extend(
            f"- **{_link(f'{signal.ticker} — {signal.company_name}', signal.research_page)}:** "
            f"{_action_label(signal.action)} · {_action_status_label(signal.action_status)}"
            for signal in snapshot.actionable_signals
        )
    else:
        lines.append("**No actionable trade signals.**")
    lines.extend(["", "## Top assessed near misses", ""])
    near_misses = _near_misses(snapshot, limit=3)
    if near_misses:
        for candidate in near_misses:
            reason = (
                candidate.reason_labels[0] if candidate.reason_labels else "No approved action."
            )
            lines.append(
                "- **"
                + _link(
                    f"{candidate.ticker} — {candidate.company_name}",
                    candidate.research_page,
                )
                + ":** "
                f"{_markdown(reason)}"
            )
    else:
        lines.append("No assessed near misses; unassessed securities are shown as coverage gaps.")
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
            f"- Current relationships: **{coverage.current_relationship_count}/"
            f"{coverage.required_relationship_count}**",
            f"- Market retrieval failures: **{coverage.market_data_failure_count}**",
            "",
            "## Explore",
            "",
            "- [[model-portfolio|Model portfolio]]",
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
            and required_decimal(row.approved_target_value_base, label="approved target value") > 0
        )
        label = "Cash" if row.holding_type == "cash" else f"{row.ticker} — {row.company_name}"
        output.extend(
            [
                '<article class="portfolio-card" '
                f'data-scalable="{"true" if scalable else "false"}" '
                f'data-target-weight="{_html(row.approved_target_weight_pct)}" '
                f'data-mark="{_html(row.mark)}" data-fx="{_html(row.fx_rate_to_base)}" '
                f'data-mark-currency="{_html(row.mark_currency)}" '
                f'data-market-data-as-of="{_html(row.market_data_as_of)}" '
                f'data-ticker="{_html(row.ticker)}" '
                f'data-company="{_html(row.company_name or "Cash")}">',
                f"<h3>{_html(label)}</h3>",
                '<dl class="portfolio-card-values">',
                f"<div><dt>Current</dt><dd>{_html(row.current_weight_pct)}%</dd></div>",
                "<div><dt>Approved target</dt><dd>"
                f"{_html(row.approved_target_weight_pct)}%</dd></div>",
                f"<div><dt>Action</dt><dd>{_html(_action_label(row.action))}</dd></div>",
                f"<div><dt>State</dt><dd>{_html(_action_status_label(row.action_status))}</dd></div>",
                f"<div><dt>Reference mark</dt><dd>{_html(row.mark)} "
                f"{_html(row.mark_currency)}</dd></div>",
                f"<div><dt>As of</dt><dd>{_html(row.market_data_as_of)}</dd></div>",
                "</dl>",
                (
                    f'<p><a href="{_html(_page_key(row.research_page))}">Complete research</a></p>'
                    if row.research_page
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
        f"**Snapshot `{snapshot.snapshot_id}` · As of `{snapshot.as_of}`**",
        "",
        "This is a paper-only, non-personalized research portfolio. Pending targets are "
        "projections; "
        "only deterministic fills change the current portfolio.",
        "",
        _portfolio_html(current.rows, snapshot.base_currency),
        "",
        '<div class="portfolio-controls" aria-label="Portfolio copy and scaling tools">',
        '<button type="button" id="copy-portfolio">Copy portfolio as TSV</button>',
        '<a class="button-link" href="data/model_portfolio.csv" download>'
        "Download committed CSV</a>",
        '<a class="button-link" href="data/decision_snapshot.json" download>'
        "Download snapshot JSON</a>",
        '<label for="reference-notional">Illustrative reference notional</label>',
        '<input id="reference-notional" type="number" min="0" step="100" inputmode="decimal">',
        '<button type="button" id="scale-portfolio">Scale long-equity targets locally</button>',
        "</div>",
        '<p class="scaler-notice"><strong>Illustrative scaling only.</strong> Your scaled '
        "quantities "
        "have not passed PaperTrader's portfolio-level risk checks.</p>",
        '<div id="scaled-portfolio" aria-live="polite"></div>',
        "",
        "## Valuation and thesis detail",
        "",
        "| Holding | Confidence | Downside | Base upside | Review | Thesis or cash role |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in current.rows:
        label = "Cash" if row.holding_type == "cash" else f"{row.ticker} — {row.company_name}"
        linked = label if row.holding_type == "cash" else _link(label, row.research_page)
        lines.append(
            f"| {linked} | {_cell(row.confidence)} | {row.downside_pct or '—'}% | "
            f"{row.base_upside_pct or '—'}% | {_cell(row.review_at)} | "
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
        f"### {_link(f'{signal.ticker} — {signal.company_name}', signal.research_page)}",
        "",
        f"- **Action:** {_action_label(signal.action)}",
        f"- **State:** {_action_status_label(signal.action_status)}",
        f"- **Strategy:** {_markdown(signal.strategy_name)}",
        f"- **Window:** `{signal.created_at}` to `{signal.expires_at}`",
        f"- **Market data:** `{signal.market_data_as_of}`",
        f"- **Current → target:** {signal.current_weight_pct}% → "
        f"{signal.approved_target_weight_pct}%",
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
        f"**Snapshot `{snapshot.snapshot_id}` · As of `{snapshot.as_of}`**",
        "",
        "## Actionable trade signals",
        "",
    ]
    if snapshot.actionable_signals:
        for signal in snapshot.actionable_signals:
            lines.extend(_signal_detail(signal))
    else:
        lines.extend(["No actionable trade signals.", ""])
    lines.extend(["## Pending validated paper orders", ""])
    if pending:
        lines.extend(
            f"- **{_markdown(signal.ticker)}:** {_action_label(signal.action)} · order "
            f"`{signal.order_id}` · {_action_status_label(signal.action_status)}"
            for signal in pending
        )
    else:
        lines.append("No pending paper orders.")
    lines.extend(["", "## Research alerts — not trade signals", ""])
    if snapshot.research_alerts:
        for alert in snapshot.research_alerts:
            lines.extend(
                [
                    f"### {_link(f'{alert.ticker} — {alert.company_name}', alert.research_page)}",
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
            research_page = (
                completed_strategy["research_page"] or completed_security["research_page"]
            )
            lines.append(
                f"- **{_markdown(completed_row['status'].title())}:** "
                f"{_link(label, research_page)} — "
                f"{_markdown(completed_strategy['name'])} · "
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
        f"**Snapshot `{snapshot.snapshot_id}` · As of `{snapshot.as_of}`**",
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
        "## Approved allocation changes",
        "",
    ]
    changes = [
        row
        for row in snapshot.approved_target_portfolio.rows
        if row.holding_type == "security" and row.action in {"buy", "add", "trim", "exit"}
    ]
    if changes:
        lines.extend(
            f"- **{_link(f'{row.ticker} — {row.company_name}', row.research_page)}:** "
            f"{_action_label(row.action)} from {row.current_weight_pct}% to "
            f"{row.approved_target_weight_pct}%"
            for row in changes
        )
    else:
        lines.append("No approved allocation changes.")
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


def _system_status_page(repository_root: Path, snapshot: DecisionSnapshot, day: date) -> str:
    coverage = snapshot.coverage
    candidate_fx_gaps = sum(
        "fx_unavailable" in candidate.reason_codes for candidate in snapshot.candidate_pipeline
    )
    active_queue = sorted(
        read_table(repository_root, "operations_todo"),
        key=lambda row: (int(row["priority"]), row["created_at"], row["operation_id"]),
    )
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
        f"**Publication snapshot:** `{snapshot.snapshot_id}`",
        f"**As of:** `{snapshot.as_of}`",
        f"**Data status:** {STATUS_LABELS[snapshot.data_status]}",
        "**Publication validation:** Snapshot and exports validated",
        "**Portfolio reconciliation:** Reconciled",
        "",
        "## Coverage",
        "",
        f"- Assessments: {coverage.current_assessment_count}/{coverage.allocation_candidate_count}",
        f"- Fresh-evidence assessments: {coverage.fresh_evidence_assessment_count}/"
        f"{coverage.allocation_candidate_count}",
        f"- Current accepted relationships: {coverage.current_relationship_count}/"
        f"{coverage.required_relationship_count}",
        f"- Ready or active strategies: {coverage.ready_or_active_strategy_count}",
        f"- Active signals: {coverage.active_signal_count}",
        f"- Pending orders: {coverage.pending_order_count}",
        f"- Market success/failure: {coverage.market_data_success_count}/"
        f"{coverage.market_data_failure_count}",
        f"- Candidate FX gaps: {candidate_fx_gaps}",
        f"- Research backlog: {coverage.research_backlog_count}",
        f"- Last successful daily run: `{coverage.last_successful_daily_run or 'none'}`",
        "",
        "## Current issues by investment impact",
        "",
    ]
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
            lines.extend([f"### {_markdown(category.replace('_', ' ').title())}", ""])
            for value in values:
                label = f"{value.ticker} — {value.company_name}: " if value.ticker else ""
                lines.append(
                    f"- `{value.severity}` **{_markdown(label + value.title)}** — "
                    f"{_markdown(value.summary)}"
                )
            lines.append("")
    else:
        lines.extend(["No open issues.", ""])
    lines.extend(
        [
            "## Bounded active operation queue",
            "",
            f"Showing {min(len(active_queue), 20)} of {len(active_queue)} active operations.",
            "",
            "<details><summary>Technical queue identifiers</summary>",
            "",
        ]
    )
    lines.extend(
        f"- `{row['status']}` `{row['operation_id']}` — `{row['operation_type']}` for "
        f"`{row['entity_id']}`"
        for row in active_queue[:20]
    )
    if not active_queue:
        lines.append("No active operations.")
    lines.extend(
        [
            "",
            "</details>",
            "",
            "## Audit links",
            "",
            "- [[research-catalog|Complete research catalog]]",
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

    day = date.fromisoformat(snapshot.report_date)
    wiki_root = repository_root / "data" / "wiki"
    paths = {
        "model-portfolio.md": _model_portfolio_page(snapshot, day),
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
            "signals.md",
            "performance.md",
            "system-status.md",
            "research-catalog.md",
        )
    )
