"""Sequential deterministic orchestration around bounded Hermes operation batches."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from papertrader.agent_runner import AgentBatchResult, Executor, run_sequential_operations
from papertrader.allocation import (
    AllocationError,
    maintain_allocation_research,
    plan_allocation,
)
from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.corporate_actions import accrue_dividends
from papertrader.execution import ExecutionError, ensure_initial_capital, process_order_fill
from papertrader.indicators import update_indicators
from papertrader.issues import record_issue
from papertrader.logs import append_event, record_completed_run
from papertrader.market_data import (
    MarketDataProvider,
    daily_bar_to_market_bar,
    fx_rates_for_actions,
    latest_fx_rate,
    read_price_cache,
    session_close,
    session_open,
    update_market_data,
)
from papertrader.models import MarketBar, PositionMark, ReferencePrice
from papertrader.opportunity import CandidateClassifier, process_opportunity_transitions
from papertrader.orders import leg_from_row
from papertrader.performance import update_performance
from papertrader.portfolio import (
    PortfolioError,
    build_risk_state,
    rebuild_portfolio,
    reconcile_portfolio,
    replay_accounting,
)
from papertrader.queue import prepare_queue, release_expired_leases
from papertrader.reports import NarrativeItem, generate_daily_report
from papertrader.risk import RiskRejected
from papertrader.tables import read_table
from papertrader.utils import (
    CanonicalValueError,
    decimal_text,
    ensure_utc,
    format_timestamp,
    parse_timestamp,
    required_decimal,
    utc_now,
)

RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
SOURCE_SHA = re.compile(r"^[0-9a-f]{40}$")
TRIGGER = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


class DailyRunError(RuntimeError):
    """Raised when a deterministic daily phase cannot safely continue."""


@dataclass(frozen=True, slots=True)
class DailyPreparation:
    """Deterministic state produced before any Hermes operation."""

    run_id: str
    started_at: datetime
    errors: tuple[str, ...]
    queue_dispositions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DailyFinalization:
    """Final report and accounting disposition for one daily run."""

    run_id: str
    status: str
    report_path: str
    operation_count: int
    fill_outcomes: tuple[str, ...]


def _run_directory(repository_root: Path, run_id: str) -> Path:
    if not RUN_ID.fullmatch(run_id):
        raise DailyRunError(f"invalid daily run_id: {run_id!r}")
    path = repository_root / "data" / "runs" / run_id
    if path.is_symlink():
        raise DailyRunError("daily run directory must not be a symlink")
    path.mkdir(parents=True, exist_ok=True)
    return path


def _daily_manifest_path(repository_root: Path, run_id: str) -> Path:
    return _run_directory(repository_root, run_id) / "daily_run.json"


def _batch_path(repository_root: Path, run_id: str) -> Path:
    return _run_directory(repository_root, run_id) / "agent_batch.json"


def _load_object(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise DailyRunError(f"required run artifact is unavailable: {path.name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DailyRunError(f"cannot read run artifact {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise DailyRunError(f"run artifact {path.name} must contain an object")
    return value


def _record_phase_issue(
    repository_root: Path,
    *,
    run_id: str,
    phase: str,
    error: str,
    now: datetime,
) -> str:
    subject = error.split(":", maxsplit=1)[0][:120]
    return record_issue(
        repository_root,
        severity="warning",
        title=f"Daily {phase} degraded: {subject}",
        description=error,
        owner="deterministic-controller",
        related_run_id=run_id,
        now=now,
    )


def prepare_daily_run(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    trigger: str,
    source_sha: str,
    now: datetime | None = None,
    retrieve_market: bool = True,
    classify_opportunities: bool = True,
    provider: MarketDataProvider | None = None,
    classifier: CandidateClassifier | None = None,
) -> DailyPreparation:
    """Run market, indicators, actions discovery, and queue preparation sequentially."""

    if not TRIGGER.fullmatch(trigger):
        raise DailyRunError(f"invalid daily trigger: {trigger!r}")
    if not SOURCE_SHA.fullmatch(source_sha):
        raise DailyRunError("daily source SHA must contain 40 lowercase hex characters")
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    manifest_path = _daily_manifest_path(repository_root, run_id)
    if manifest_path.exists():
        raise DailyRunError(f"daily run already exists: {run_id}")
    append_event(
        repository_root,
        event_type="daily_run_started",
        message="Started sequential deterministic daily preparation.",
        run_id=run_id,
        data={"trigger": trigger, "source_sha": source_sha},
        occurred_at=instant,
    )
    ensure_initial_capital(repository_root, settings, run_id=run_id, occurred_at=instant)
    release_dispositions = release_expired_leases(repository_root, now=instant)
    errors: list[str] = []
    if retrieve_market:
        errors.extend(
            update_market_data(
                repository_root,
                settings,
                provider=provider,
                now=instant,
            )
        )
    previous, current, indicator_errors = update_indicators(
        repository_root,
        settings,
        now=instant,
    )
    errors.extend(indicator_errors)
    if classify_opportunities:
        bars = {
            security_id: read_price_cache(repository_root, security_id) for security_id in current
        }
        packets = process_opportunity_transitions(
            repository_root,
            settings,
            previous,
            current,
            bars,
            classifier=classifier,
            now=instant,
        )
        errors.extend(
            f"classifier blocked for {packet.path.relative_to(repository_root).as_posix()}"
            for packet in packets
            if packet.decision is None
        )
    maintenance_dispositions: tuple[str, ...] = ()
    if settings.allocation.mode in {"report_only", "active"}:
        try:
            maintenance = maintain_allocation_research(
                repository_root,
                settings,
                run_id=run_id,
                now=instant,
            )
            maintenance_dispositions = tuple(
                f"allocation_maintenance:{operation_id}"
                for operation_id in maintenance.operations_created
            )
        except (AllocationError, CanonicalValueError) as exc:
            errors.append(f"allocation maintenance failed closed: {exc}")
    for error in errors:
        _record_phase_issue(
            repository_root,
            run_id=run_id,
            phase="preparation",
            error=error,
            now=instant,
        )
    queue_dispositions = (
        *release_dispositions,
        *maintenance_dispositions,
        *prepare_queue(repository_root, now=instant),
    )
    atomic_write_json(
        manifest_path,
        {
            "daily_run_version": 1,
            "run_id": run_id,
            "trigger": trigger,
            "source_sha": source_sha,
            "status": "prepared",
            "started_at": format_timestamp(instant),
            "completed_at": "",
            "preparation_errors": sorted(set(errors)),
            "queue_dispositions": list(queue_dispositions),
            "operation_count": 0,
            "model_budget_limit": decimal_text(
                settings.operations.maximum_model_budget_usd_per_run
            ),
            "model_budget_used": "0",
            "fill_outcomes": [],
            "report_path": "",
        },
        allowed_root=repository_root,
    )
    return DailyPreparation(
        run_id=run_id,
        started_at=instant,
        errors=tuple(sorted(set(errors))),
        queue_dispositions=tuple(queue_dispositions),
    )


def execute_agent_batch(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    hermes_home: Path,
    environment: Mapping[str, str],
    maximum_operations: int,
    operation_id: str | None = None,
    operation_type: str | None = None,
    executor: Executor | None = None,
    now: datetime | None = None,
) -> AgentBatchResult:
    """Execute and persist one shared-budget, strictly sequential Hermes batch."""

    manifest = _load_object(_daily_manifest_path(repository_root, run_id))
    if manifest.get("run_id") != run_id or manifest.get("status") != "prepared":
        raise DailyRunError("agent batch requires this run's prepared daily manifest")
    started = ensure_utc(now or utc_now()).replace(microsecond=0)
    if executor is None:
        result = run_sequential_operations(
            repository_root,
            settings,
            run_id=run_id,
            hermes_home=hermes_home,
            environment=environment,
            maximum_operations=maximum_operations,
            operation_id=operation_id,
            operation_type=operation_type,
        )
    else:
        result = run_sequential_operations(
            repository_root,
            settings,
            run_id=run_id,
            hermes_home=hermes_home,
            environment=environment,
            maximum_operations=maximum_operations,
            operation_id=operation_id,
            operation_type=operation_type,
            executor=executor,
        )
    completed = utc_now().replace(microsecond=0) if now is None else started
    atomic_write_json(
        _batch_path(repository_root, run_id),
        {
            "agent_batch_version": 1,
            "run_id": run_id,
            "started_at": format_timestamp(started),
            "completed_at": format_timestamp(completed),
            "maximum_operations": result.maximum_operations,
            "maximum_model_budget": decimal_text(result.maximum_cost),
            "estimated_cost_per_operation": decimal_text(result.estimated_cost_per_operation),
            "operation_count": result.operation_count,
            "estimated_model_budget_used": decimal_text(result.estimated_cost_used),
            "outcomes": [
                {"operation_id": outcome.operation_id, "status": outcome.status}
                for outcome in result.outcomes
            ],
        },
        allowed_root=repository_root,
    )
    return result


def record_local_agent_outcome(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    operation_id: str,
    status: str,
    now: datetime | None = None,
) -> None:
    """Append one validated local-harness outcome to a prepared daily run."""

    manifest = _load_object(_daily_manifest_path(repository_root, run_id))
    if manifest.get("run_id") != run_id or manifest.get("status") != "prepared":
        raise DailyRunError("local harness outcome requires this run's prepared daily manifest")
    if status not in {"succeeded", "skipped", "blocked", "failed"}:
        raise DailyRunError(f"invalid local harness status: {status}")
    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    path = _batch_path(repository_root, run_id)
    if path.exists():
        document = _load_object(path)
        raw_outcomes = document.get("outcomes")
        if not isinstance(raw_outcomes, list) or not all(
            isinstance(outcome, dict) for outcome in raw_outcomes
        ):
            raise DailyRunError("existing agent batch outcomes are invalid")
        outcomes = [dict(outcome) for outcome in raw_outcomes]
        existing = next(
            (outcome for outcome in outcomes if outcome.get("operation_id") == operation_id),
            None,
        )
        if existing is not None:
            if existing.get("status") != status:
                raise DailyRunError("local harness outcome conflicts with the recorded status")
            return
        maximum = document.get("maximum_operations")
        if isinstance(maximum, bool) or not isinstance(maximum, int):
            raise DailyRunError("existing agent batch maximum is invalid")
        if len(outcomes) >= maximum:
            raise DailyRunError("local harness operation count exceeds the daily run budget")
        outcomes.append({"operation_id": operation_id, "status": status})
        updated = {
            **document,
            "completed_at": format_timestamp(instant),
            "operation_count": len(outcomes),
            "outcomes": outcomes,
        }
    else:
        updated = {
            "agent_batch_version": 1,
            "run_id": run_id,
            "started_at": format_timestamp(instant),
            "completed_at": format_timestamp(instant),
            "maximum_operations": settings.operations.maximum_llm_operations_per_run,
            "maximum_model_budget": decimal_text(
                settings.operations.maximum_model_budget_usd_per_run
            ),
            "estimated_cost_per_operation": "0",
            "operation_count": 1,
            "estimated_model_budget_used": "0",
            "outcomes": [{"operation_id": operation_id, "status": status}],
        }
    atomic_write_json(path, updated, allowed_root=repository_root)


def _research_narratives(repository_root: Path, run_id: str) -> tuple[NarrativeItem, ...]:
    run_directory = _run_directory(repository_root, run_id)
    narratives: list[NarrativeItem] = []
    for path in sorted(run_directory.glob("*/agent_result.json")):
        result = _load_object(path)
        raw_evidence = result.get("evidence", [])
        raw_items = result.get("daily_report_items", [])
        if not isinstance(raw_evidence, list) or not isinstance(raw_items, list):
            raise DailyRunError(f"invalid narrative fields in {path.relative_to(repository_root)}")
        references: set[str] = set()
        for evidence in raw_evidence:
            if not isinstance(evidence, dict):
                raise DailyRunError("agent narrative evidence must contain objects")
            reference = evidence.get("url") or evidence.get("source_hash") or evidence.get("source")
            if isinstance(reference, str) and reference.strip():
                references.add(" ".join(reference.split()))
        for item in raw_items:
            if not isinstance(item, str) or not item.strip() or not references:
                raise DailyRunError("every agent daily report item requires retained evidence")
            narratives.append(
                NarrativeItem(
                    text=" ".join(item.split()),
                    evidence_refs=tuple(sorted(references)),
                )
            )
    return tuple(narratives)


def _base_equity_market_inputs(
    repository_root: Path,
    settings: Settings,
    *,
    now: datetime,
) -> tuple[tuple[ReferencePrice, ...], tuple[PositionMark, ...], tuple[MarketBar, ...]]:
    replay = replay_accounting(repository_root)
    open_positions = [position for position in replay.positions if position.quantity != 0]
    pending_order_ids = {
        row["order_id"]
        for row in read_table(repository_root, "orders")
        if row["status"] in {"pending", "partially_filled"}
    }
    pending_legs = [
        leg_from_row(row)
        for row in read_table(repository_root, "order_legs")
        if row["order_id"] in pending_order_ids
    ]
    open_equities = {
        position.security_id for position in open_positions if position.instrument_type == "equity"
    }
    pending_equities = {leg.security_id for leg in pending_legs if leg.instrument_type == "equity"}
    required_equities = open_equities | pending_equities
    if any(position.instrument_type == "option" for position in open_positions):
        raise DailyRunError("fresh option marks are required for open option positions")
    securities = {row["security_id"]: row for row in read_table(repository_root, "securities")}
    references: list[ReferencePrice] = []
    marks: list[PositionMark] = []
    bars: list[MarketBar] = []
    for security_id in sorted(required_equities):
        identity = securities.get(security_id)
        if identity is None:
            raise DailyRunError(f"market input references unknown security {security_id}")
        try:
            cached = read_price_cache(repository_root, security_id)
            if not cached:
                raise DailyRunError(f"price cache is empty for required security {security_id}")
            calendar_name = settings.market_data.calendar_for(identity["venue_mic"])
            latest = cached[-1]
            retrieval_age = now - ensure_utc(latest.retrieved_at)
            if (
                retrieval_age < timedelta(0)
                or retrieval_age > settings.market_data.stale_price_after
            ):
                raise DailyRunError(f"price cache is stale for required security {security_id}")
            marked_at = session_close(calendar_name, latest.date)
            if marked_at > now:
                raise DailyRunError(f"latest bar for {security_id} closes in the future")
            fx_rate = latest_fx_rate(
                repository_root,
                identity["currency"],
                settings.portfolio.base_currency,
                now=now,
                maximum_age=settings.market_data.stale_price_after,
            )
        except RuntimeError as exc:
            if security_id not in open_equities:
                # Pending orders are deferred below when their reference is absent. Open
                # positions still fail closed because accounting cannot be rebuilt unmarked.
                continue
            raise DailyRunError(
                f"fresh market/FX mark is required for {security_id}: {exc}"
            ) from exc
        reference = ReferencePrice(
            security_id=security_id,
            provider_contract_id="",
            price=latest.close,
            currency=latest.currency,
            fx_rate_to_base=fx_rate,
            as_of=marked_at,
        )
        references.append(reference)
        marks.append(
            PositionMark(
                security_id=security_id,
                provider_contract_id="",
                price=latest.close,
                currency=latest.currency,
                fx_rate_to_base=fx_rate,
                marked_at=marked_at,
            )
        )
        bars.extend(
            daily_bar_to_market_bar(
                security_id,
                bar,
                session_open=session_open(calendar_name, bar.date),
                fx_rate_to_base=fx_rate,
            )
            for bar in cached
        )
    return tuple(references), tuple(marks), tuple(bars)


def _process_pending_orders(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    now: datetime,
    references: tuple[ReferencePrice, ...],
    bars: tuple[MarketBar, ...],
) -> tuple[str, ...]:
    outcomes: list[str] = []
    leg_rows = read_table(repository_root, "order_legs")
    for order in sorted(
        (
            row
            for row in read_table(repository_root, "orders")
            if row["status"] in {"pending", "partially_filled"}
        ),
        key=lambda row: (row["created_at"], row["order_id"]),
    ):
        legs = [leg_from_row(row) for row in leg_rows if row["order_id"] == order["order_id"]]
        reference_keys = {
            (reference.security_id, reference.provider_contract_id) for reference in references
        }
        missing_equity_references = sorted(
            {
                leg.security_id
                for leg in legs
                if leg.instrument_type == "equity"
                and (leg.security_id, leg.provider_contract_id) not in reference_keys
            }
        )
        if missing_equity_references:
            error = f"order {order['order_id']} lacks fresh market/FX references for " + ",".join(
                missing_equity_references
            )
            _record_phase_issue(
                repository_root,
                run_id=run_id,
                phase="fill",
                error=error,
                now=now,
            )
            outcomes.append(f"{order['order_id']}:deferred:market_or_fx_unavailable")
            continue
        try:
            risk_state = build_risk_state(repository_root, references, as_of=now)
            status, execution_ids = process_order_fill(
                repository_root,
                settings,
                order_id=order["order_id"],
                bars=bars,
                quotes=(),
                risk_state=risk_state,
                risk_references=references,
                run_id=run_id,
                now=now,
            )
        except RiskRejected as exc:
            error = f"order {order['order_id']} rejected at fill risk gate: {exc}"
            _record_phase_issue(
                repository_root,
                run_id=run_id,
                phase="fill",
                error=error,
                now=now,
            )
            outcomes.append(f"{order['order_id']}:deferred:risk_rejected")
            continue
        if status == "pending" and any(leg.instrument_type == "option" for leg in legs):
            _record_phase_issue(
                repository_root,
                run_id=run_id,
                phase="fill",
                error=f"fresh option quote unavailable for order {order['order_id']}",
                now=now,
            )
        outcomes.append(
            f"{order['order_id']}:{status}:{'|'.join(execution_ids) if execution_ids else '-'}"
        )
    return tuple(outcomes)


def finalize_daily_run(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    github_report_url: str,
    now: datetime | None = None,
) -> DailyFinalization:
    """Process fills, rebuild accounting, and generate the single canonical report."""

    instant = ensure_utc(now or utc_now()).replace(microsecond=0)
    manifest_path = _daily_manifest_path(repository_root, run_id)
    manifest = _load_object(manifest_path)
    batch = _load_object(_batch_path(repository_root, run_id))
    if manifest.get("run_id") != run_id or manifest.get("status") != "prepared":
        raise DailyRunError("daily finalization requires this run's prepared manifest")
    if batch.get("run_id") != run_id:
        raise DailyRunError("agent batch identity does not match the daily run")
    started_at = parse_timestamp(str(manifest.get("started_at", "")))
    if started_at is None or started_at > instant:
        raise DailyRunError("daily manifest contains an invalid start time")
    references, marks, bars = _base_equity_market_inputs(
        repository_root,
        settings,
        now=instant,
    )
    fill_outcomes = _process_pending_orders(
        repository_root,
        settings,
        run_id=run_id,
        now=instant,
        references=references,
        bars=bars,
    )
    try:
        accrue_dividends(
            repository_root,
            through=instant.date(),
            fx_rates_to_base=fx_rates_for_actions(
                repository_root,
                tuple(row["currency"] for row in read_table(repository_root, "securities")),
                settings.portfolio.base_currency,
                through=instant.date(),
            ),
            base_currency=settings.portfolio.base_currency,
            run_id=run_id,
        )
        rebuild_portfolio(repository_root, marks=marks, run_id=run_id, as_of=instant)
    except (CanonicalValueError, ExecutionError, PortfolioError) as exc:
        raise DailyRunError(f"accounting finalization failed closed: {exc}") from exc
    reconciliation_errors = reconcile_portfolio(repository_root)
    if reconciliation_errors:
        raise DailyRunError("; ".join(reconciliation_errors))
    update_performance(repository_root, settings, run_id=run_id, generated_at=instant)
    try:
        plan_allocation(repository_root, settings, run_id=run_id, now=instant)
    except (AllocationError, CanonicalValueError) as exc:
        raise DailyRunError(f"allocation planning failed closed: {exc}") from exc
    prepare_queue(repository_root, now=instant)
    raw_outcomes = batch.get("outcomes", [])
    if not isinstance(raw_outcomes, list):
        raise DailyRunError("agent batch outcomes must be a list")
    agent_statuses = {
        str(outcome.get("status", "")) for outcome in raw_outcomes if isinstance(outcome, dict)
    }
    preparation_errors = manifest.get("preparation_errors", [])
    if not isinstance(preparation_errors, list):
        raise DailyRunError("daily preparation errors must be a list")
    degraded = (
        bool(preparation_errors)
        or bool(agent_statuses.intersection({"blocked", "failed"}))
        or any(":deferred:" in outcome for outcome in fill_outcomes)
    )
    status = "degraded" if degraded else "succeeded"
    operation_count = batch.get("operation_count")
    budget_used = batch.get("estimated_model_budget_used")
    if isinstance(operation_count, bool) or not isinstance(operation_count, int):
        raise DailyRunError("agent batch operation count must be an integer")
    if not isinstance(budget_used, str):
        raise DailyRunError("agent batch budget used must be decimal text")
    used = required_decimal(budget_used, label="agent batch budget used")
    record_completed_run(
        repository_root,
        run_id=run_id,
        started_at=started_at,
        completed_at=instant,
        status=status,
        trigger=str(manifest["trigger"]),
        operation_count=operation_count,
        model_budget_limit=settings.operations.maximum_model_budget_usd_per_run,
        model_budget_used=used,
        summary=(
            f"Daily run {status}; {operation_count} agent operations; "
            f"{len(fill_outcomes)} pending-order dispositions."
        ),
    )
    report = generate_daily_report(
        repository_root,
        run_id=run_id,
        run_status=status,
        report_date=instant.date(),
        narrative_items=_research_narratives(repository_root, run_id),
        github_report_url=github_report_url,
        generated_at=instant,
    )
    report_path = report.relative_to(repository_root).as_posix()
    completed_manifest = {
        **manifest,
        "status": status,
        "completed_at": format_timestamp(instant),
        "operation_count": operation_count,
        "model_budget_used": decimal_text(used),
        "fill_outcomes": list(fill_outcomes),
        "report_path": report_path,
    }
    atomic_write_json(manifest_path, completed_manifest, allowed_root=repository_root)
    append_event(
        repository_root,
        event_type="daily_run_completed",
        message=f"Completed deterministic daily run with status {status}.",
        run_id=run_id,
        data={"report_path": report_path, "operation_count": operation_count},
        occurred_at=instant,
    )
    return DailyFinalization(
        run_id=run_id,
        status=status,
        report_path=report_path,
        operation_count=operation_count,
        fill_outcomes=fill_outcomes,
    )
