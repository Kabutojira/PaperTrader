"""PaperTrader command-line interface for deterministic validated state transitions."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from papertrader.config import ConfigurationError, Settings, find_repository_root, load_settings
from papertrader.corporate_actions import accrue_dividends
from papertrader.execution import ensure_initial_capital, process_order_fill
from papertrader.indicators import update_indicators
from papertrader.integrity import (
    changed_paths_from_git,
    validate_csv_files,
    validate_integrity,
    validate_json_schemas,
    validate_runtime_paths,
)
from papertrader.issues import record_issue, resolve_issue
from papertrader.logs import regenerate_log_tail
from papertrader.market_data import read_price_cache, update_market_data
from papertrader.models import (
    MarketBar,
    OptionQuote,
    PositionMark,
    ReferencePrice,
)
from papertrader.opportunity import process_opportunity_transitions
from papertrader.orders import create_paper_order, create_signal, leg_from_mapping
from papertrader.performance import update_performance
from papertrader.portfolio import build_risk_state, rebuild_portfolio, reconcile_portfolio
from papertrader.queue import (
    RunBudget,
    block_operation,
    claim_next,
    complete_operation,
    enqueue_operation,
    fail_attempt,
    prepare_queue,
    release_expired_leases,
    validate_queue,
)
from papertrader.reports import NarrativeItem, generate_daily_report
from papertrader.utils import (
    CanonicalValueError,
    parse_iso_date,
    parse_timestamp,
    required_decimal,
    utc_now,
)
from papertrader.wiki import lint_wiki


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="papertrader")
    parser.add_argument("--repository", type=Path, help="repository root (defaults to discovery)")
    commands = parser.add_subparsers(dest="command", required=True)

    schema = commands.add_parser("schema", help="validate repository schemas")
    schema_commands = schema.add_subparsers(dest="schema_command", required=True)
    schema_commands.add_parser("validate").add_argument("--strict", action="store_true")

    commands.add_parser("integrity", help="run repository integrity checks").add_argument(
        "--strict", action="store_true"
    )

    wiki = commands.add_parser("wiki", help="work with the research wiki")
    wiki_commands = wiki.add_subparsers(dest="wiki_command", required=True)
    wiki_commands.add_parser("lint").add_argument("--strict", action="store_true")

    market = commands.add_parser("market", help="retrieve and normalize market state")
    market_commands = market.add_subparsers(dest="market_command", required=True)
    market_commands.add_parser("update")

    indicator = commands.add_parser("indicators", help="calculate deterministic indicators")
    indicator_commands = indicator.add_subparsers(dest="indicator_command", required=True)
    indicator_update = indicator_commands.add_parser("update")
    indicator_update.add_argument("--classify-opportunities", action="store_true")

    queue = commands.add_parser("queue", help="operate the sequential LLM queue")
    queue_commands = queue.add_subparsers(dest="queue_command", required=True)
    queue_commands.add_parser("validate")
    queue_commands.add_parser("prepare")
    queue_commands.add_parser("release-expired")
    queue_enqueue = queue_commands.add_parser("enqueue")
    queue_enqueue.add_argument("--request", type=Path, required=True)
    queue_claim = queue_commands.add_parser("claim")
    queue_claim.add_argument("--run-id", required=True)
    queue_claim.add_argument("--operation-id")
    queue_claim.add_argument("--operation-type")
    queue_claim.add_argument("--estimated-cost", default="0")
    queue_complete = queue_commands.add_parser("complete")
    queue_complete.add_argument("--request", type=Path, required=True)
    queue_fail = queue_commands.add_parser("fail-attempt")
    queue_fail.add_argument("--request", type=Path, required=True)
    queue_block = queue_commands.add_parser("block")
    queue_block.add_argument("--request", type=Path, required=True)

    account = commands.add_parser("account", help="initialize paper-only accounting")
    account_commands = account.add_subparsers(dest="account_command", required=True)
    initialize = account_commands.add_parser("initialize")
    initialize.add_argument("--run-id", required=True)

    signal = commands.add_parser("signal", help="create a time-bounded strategy decision")
    signal_commands = signal.add_subparsers(dest="signal_command", required=True)
    signal_create = signal_commands.add_parser("create")
    signal_create.add_argument("--request", type=Path, required=True)

    order = commands.add_parser("order", help="create a normalized pending paper order")
    order_commands = order.add_subparsers(dest="order_command", required=True)
    order_create = order_commands.add_parser("create")
    order_create.add_argument("--request", type=Path, required=True)

    fills = commands.add_parser("fills", help="process eligible deterministic paper fills")
    fills_commands = fills.add_subparsers(dest="fills_command", required=True)
    fills_process = fills_commands.add_parser("process")
    fills_process.add_argument("--request", type=Path, required=True)

    portfolio = commands.add_parser("portfolio", help="work with derived portfolio state")
    portfolio_commands = portfolio.add_subparsers(dest="portfolio_command", required=True)
    portfolio_commands.add_parser("reconcile").add_argument("--strict", action="store_true")
    portfolio_rebuild = portfolio_commands.add_parser("rebuild")
    portfolio_rebuild.add_argument("--request", type=Path, required=True)

    performance = commands.add_parser("performance", help="generate daily performance")
    performance_commands = performance.add_subparsers(dest="performance_command", required=True)
    performance_update = performance_commands.add_parser("update")
    performance_update.add_argument("--run-id", required=True)

    actions = commands.add_parser("corporate-actions", help="apply durable paper cash actions")
    action_commands = actions.add_subparsers(dest="action_command", required=True)
    action_accrue = action_commands.add_parser("accrue")
    action_accrue.add_argument("--request", type=Path, required=True)

    issue = commands.add_parser("issue", help="manage repository-local issue state")
    issue_commands = issue.add_subparsers(dest="issue_command", required=True)
    issue_record = issue_commands.add_parser("record")
    issue_record.add_argument("--request", type=Path, required=True)
    issue_resolve = issue_commands.add_parser("resolve")
    issue_resolve.add_argument("--request", type=Path, required=True)

    report = commands.add_parser("report", help="generate the canonical daily report")
    report_commands = report.add_subparsers(dest="report_command", required=True)
    report_generate = report_commands.add_parser("generate")
    report_generate.add_argument("--request", type=Path, required=True)

    logs = commands.add_parser("logs", help="regenerate human-readable log views")
    logs.add_subparsers(dest="logs_command", required=True).add_parser("tail")

    whitelist = commands.add_parser(
        "runtime-whitelist", help="validate automated runtime commit paths"
    )
    whitelist_commands = whitelist.add_subparsers(dest="whitelist_command", required=True)
    whitelist_validate = whitelist_commands.add_parser("validate")
    whitelist_validate.add_argument("paths", nargs="*")
    whitelist_validate.add_argument("--staged", action="store_true")
    whitelist_validate.add_argument("--base-ref")
    whitelist_validate.add_argument("--head-ref", default="HEAD")
    return parser


def _print_result(name: str, errors: Sequence[str]) -> int:
    if errors:
        for error in errors:
            print(f"ERROR [{name}] {error}", file=sys.stderr)
        return 1
    print(f"OK [{name}]")
    return 0


def _request_object(repository_root: Path, request_path: Path) -> Mapping[str, object]:
    path = request_path if request_path.is_absolute() else repository_root / request_path
    resolved = path.resolve()
    try:
        resolved.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise CanonicalValueError("request JSON must be inside the repository") from exc
    if resolved.is_symlink() or not resolved.is_file():
        raise CanonicalValueError(f"request JSON does not exist: {request_path}")
    value = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CanonicalValueError("request JSON must contain an object")
    return value


def _text(raw: Mapping[str, object], key: str, *, default: str | None = None) -> str:
    value = raw.get(key, default)
    if not isinstance(value, str):
        raise CanonicalValueError(f"request field {key} must be a string")
    return value


def _integer(raw: Mapping[str, object], key: str, *, default: int | None = None) -> int:
    value = raw.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise CanonicalValueError(f"request field {key} must be an integer")
    return value


def _timestamp(raw: Mapping[str, object], key: str, *, required: bool = True) -> datetime | None:
    value = raw.get(key)
    if (value is None or value == "") and not required:
        return None
    if not isinstance(value, str):
        raise CanonicalValueError(f"request field {key} must be an ISO timestamp")
    return parse_timestamp(value)


def _sequence(raw: Mapping[str, object], key: str) -> Sequence[object]:
    value = raw.get(key)
    if not isinstance(value, list):
        raise CanonicalValueError(f"request field {key} must be a list")
    return value


def _reference(raw: object) -> ReferencePrice:
    if not isinstance(raw, dict):
        raise CanonicalValueError("reference must be an object")
    as_of = _timestamp(raw, "as_of")
    assert as_of is not None

    def optional_decimal(key: str) -> Decimal | None:
        value = raw.get(key)
        if value is None or value == "":
            return None
        if isinstance(value, bool) or not isinstance(value, str | int | Decimal):
            raise CanonicalValueError(f"reference field {key} must be decimal-safe")
        return required_decimal(value, label=key)

    def optional_int(key: str) -> int | None:
        value = raw.get(key)
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise CanonicalValueError(f"reference field {key} must be an integer")
        return int(value)

    return ReferencePrice(
        security_id=_text(raw, "security_id"),
        provider_contract_id=_text(raw, "provider_contract_id", default=""),
        price=required_decimal(_text(raw, "price"), label="price"),
        currency=_text(raw, "currency"),
        fx_rate_to_base=required_decimal(_text(raw, "fx_rate_to_base"), label="fx_rate_to_base"),
        as_of=as_of,
        bid=optional_decimal("bid"),
        ask=optional_decimal("ask"),
        open_interest=optional_int("open_interest"),
        volume=optional_int("volume"),
    )


def _mark(raw: object) -> PositionMark:
    reference = _reference(raw)
    return PositionMark(
        security_id=reference.security_id,
        provider_contract_id=reference.provider_contract_id,
        price=reference.price,
        currency=reference.currency,
        fx_rate_to_base=reference.fx_rate_to_base,
        marked_at=reference.as_of,
    )


def _bar(raw: object) -> MarketBar:
    if not isinstance(raw, dict):
        raise CanonicalValueError("market bar must be an object")
    timestamp = _timestamp(raw, "timestamp")
    assert timestamp is not None
    return MarketBar(
        security_id=_text(raw, "security_id"),
        provider_contract_id=_text(raw, "provider_contract_id", default=""),
        timestamp=timestamp,
        open=required_decimal(_text(raw, "open"), label="open"),
        high=required_decimal(_text(raw, "high"), label="high"),
        low=required_decimal(_text(raw, "low"), label="low"),
        close=required_decimal(_text(raw, "close"), label="close"),
        currency=_text(raw, "currency"),
        fx_rate_to_base=required_decimal(_text(raw, "fx_rate_to_base"), label="fx_rate_to_base"),
    )


def _quote(raw: object) -> OptionQuote:
    if not isinstance(raw, dict):
        raise CanonicalValueError("option quote must be an object")
    timestamp = _timestamp(raw, "timestamp")
    assert timestamp is not None
    return OptionQuote(
        provider_contract_id=_text(raw, "provider_contract_id"),
        timestamp=timestamp,
        bid=required_decimal(_text(raw, "bid"), label="bid"),
        ask=required_decimal(_text(raw, "ask"), label="ask"),
        currency=_text(raw, "currency"),
        fx_rate_to_base=required_decimal(_text(raw, "fx_rate_to_base"), label="fx_rate_to_base"),
        open_interest=_integer(raw, "open_interest"),
        volume=_integer(raw, "volume"),
    )


def _run_queue_command(
    arguments: argparse.Namespace, repository_root: Path, settings: Settings
) -> int:
    command = arguments.queue_command
    if command == "validate":
        return _print_result("queue", validate_queue(repository_root))
    if command == "prepare":
        for disposition in prepare_queue(repository_root):
            print(disposition)
        return 0
    if command == "release-expired":
        for disposition in release_expired_leases(repository_root):
            print(disposition)
        return 0
    if command == "enqueue":
        raw = _request_object(repository_root, arguments.request)
        inputs = raw.get("inputs")
        if not isinstance(inputs, dict):
            raise CanonicalValueError("request inputs must be an object")
        dependencies = tuple(str(value) for value in _sequence(raw, "depends_on"))
        source_refs = tuple(str(value) for value in _sequence(raw, "source_refs"))
        operation_id, created = enqueue_operation(
            repository_root,
            settings,
            operation_type=_text(raw, "operation_type"),
            entity_type=_text(raw, "entity_type"),
            entity_id=_text(raw, "entity_id"),
            dedupe_key=_text(raw, "dedupe_key"),
            prompt=_text(raw, "prompt"),
            inputs=inputs,
            source=_text(raw, "source"),
            priority=_integer(raw, "priority", default=50),
            freshness_days=_integer(raw, "freshness_days", default=0),
            depends_on=dependencies,
            not_before=_timestamp(raw, "not_before", required=False),
            deadline=_timestamp(raw, "deadline", required=False),
            source_refs=source_refs,
            max_attempts=_integer(
                raw,
                "max_attempts",
                default=settings.operations.default_max_attempts,
            ),
        )
        print(json.dumps({"operation_id": operation_id, "created": created}, sort_keys=True))
        return 0
    if command == "claim":
        budget = RunBudget.from_settings(settings)
        claimed = claim_next(
            repository_root,
            settings,
            run_id=arguments.run_id,
            budget=budget,
            estimated_cost=required_decimal(arguments.estimated_cost, label="estimated_cost"),
            operation_id=arguments.operation_id,
            operation_type=arguments.operation_type,
        )
        if claimed is None:
            print("null")
            return 0
        print(json.dumps(claimed.to_row(), sort_keys=True))
        return 0
    raw = _request_object(repository_root, arguments.request)
    if command == "complete":
        complete_operation(
            repository_root,
            operation_id=_text(raw, "operation_id"),
            run_id=_text(raw, "run_id"),
            terminal_status=_text(raw, "terminal_status"),
            result_path=_text(raw, "result_path"),
            result_summary=_text(raw, "result_summary"),
            terminal_reason=_text(raw, "terminal_reason"),
        )
    elif command == "fail-attempt":
        print(
            fail_attempt(
                repository_root,
                operation_id=_text(raw, "operation_id"),
                run_id=_text(raw, "run_id"),
                error=_text(raw, "error"),
            )
        )
    elif command == "block":
        block_operation(
            repository_root,
            operation_id=_text(raw, "operation_id"),
            run_id=_text(raw, "run_id"),
            reason=_text(raw, "reason"),
        )
    return 0


def _run_structured_command(
    arguments: argparse.Namespace, repository_root: Path, settings: Settings
) -> int:
    if arguments.command == "account":
        entry_id = ensure_initial_capital(
            repository_root,
            settings,
            run_id=arguments.run_id,
            occurred_at=utc_now(),
        )
        print(entry_id)
        return 0
    raw = _request_object(repository_root, arguments.request)
    if arguments.command == "signal":
        as_of = _timestamp(raw, "market_data_as_of")
        assert as_of is not None
        signal_id, created = create_signal(
            repository_root,
            settings,
            strategy_id=_text(raw, "strategy_id"),
            signal_type=_text(raw, "signal_type"),
            rationale=_text(raw, "rationale"),
            market_data_as_of=as_of,
            run_id=_text(raw, "run_id"),
            order_request_path=_text(raw, "order_request_path", default=""),
            expires_at=_timestamp(raw, "expires_at", required=False),
        )
        print(json.dumps({"signal_id": signal_id, "created": created}, sort_keys=True))
        return 0
    if arguments.command == "order":
        references = tuple(_reference(value) for value in _sequence(raw, "references"))
        now = _timestamp(raw, "now", required=False) or utc_now()
        risk_state = build_risk_state(repository_root, references, as_of=now)
        leg_values = _sequence(raw, "legs")
        if not all(isinstance(value, dict) for value in leg_values):
            raise CanonicalValueError("every order leg must be an object")
        legs = tuple(leg_from_mapping(value) for value in leg_values if isinstance(value, dict))
        limit_raw = raw.get("limit_price")
        limit = (
            required_decimal(_text(raw, "limit_price"), label="limit_price")
            if limit_raw is not None and limit_raw != ""
            else None
        )
        order_id, created, assessment = create_paper_order(
            repository_root,
            settings,
            signal_id=_text(raw, "signal_id"),
            strategy_id=_text(raw, "strategy_id"),
            legs=legs,
            references=references,
            risk_state=risk_state,
            run_id=_text(raw, "run_id"),
            fill_policy=_text(raw, "fill_policy", default=settings.orders.default_fill_policy),
            order_type=_text(raw, "order_type", default=settings.orders.default_order_type),
            limit_price=limit,
            not_before=_timestamp(raw, "not_before", required=False),
            expires_at=_timestamp(raw, "expires_at", required=False),
            now=now,
        )
        print(
            json.dumps(
                {
                    "order_id": order_id,
                    "created": created,
                    "risk_violations": assessment.violations,
                },
                sort_keys=True,
            )
        )
        return 0
    if arguments.command == "fills":
        references = tuple(_reference(value) for value in _sequence(raw, "references"))
        now = _timestamp(raw, "now", required=False) or utc_now()
        risk_state = build_risk_state(repository_root, references, as_of=now)
        status, execution_ids = process_order_fill(
            repository_root,
            settings,
            order_id=_text(raw, "order_id"),
            bars=tuple(_bar(value) for value in _sequence(raw, "bars")),
            quotes=tuple(_quote(value) for value in _sequence(raw, "quotes")),
            risk_state=risk_state,
            risk_references=references,
            run_id=_text(raw, "run_id"),
            now=now,
        )
        print(json.dumps({"status": status, "execution_ids": execution_ids}, sort_keys=True))
        return 0
    if arguments.command == "portfolio":
        as_of = _timestamp(raw, "as_of")
        assert as_of is not None
        rows = rebuild_portfolio(
            repository_root,
            marks=tuple(_mark(value) for value in _sequence(raw, "marks")),
            run_id=_text(raw, "run_id"),
            as_of=as_of,
        )
        print(json.dumps({"position_count": len(rows)}, sort_keys=True))
        return 0
    if arguments.command == "corporate-actions":
        fx_raw = raw.get("fx_rates_to_base", {})
        if not isinstance(fx_raw, dict):
            raise CanonicalValueError("fx_rates_to_base must be an object")
        fx_rates: dict[tuple[str, date], Decimal] = {}
        for key, value in fx_raw.items():
            if not isinstance(key, str) or "@" not in key or not isinstance(value, str):
                raise CanonicalValueError("FX keys must use CURRENCY@YYYY-MM-DD and string values")
            currency, raw_date = key.split("@", maxsplit=1)
            fx_rates[(currency, parse_iso_date(raw_date))] = required_decimal(value, label=key)
        count = accrue_dividends(
            repository_root,
            through=parse_iso_date(_text(raw, "through")),
            fx_rates_to_base=fx_rates,
            base_currency=settings.portfolio.base_currency,
            run_id=_text(raw, "run_id"),
        )
        print(count)
        return 0
    if arguments.command == "issue":
        if arguments.issue_command == "record":
            print(
                record_issue(
                    repository_root,
                    severity=_text(raw, "severity"),
                    title=_text(raw, "title"),
                    description=_text(raw, "description"),
                    owner=_text(raw, "owner", default=""),
                    related_run_id=_text(raw, "related_run_id", default=""),
                    related_operation_id=_text(raw, "related_operation_id", default=""),
                )
            )
        else:
            resolve_issue(
                repository_root,
                _text(raw, "issue_id"),
                _text(raw, "resolution"),
            )
        return 0
    if arguments.command == "report":
        narrative_values = _sequence(raw, "narrative_items")
        narratives: list[NarrativeItem] = []
        for value in narrative_values:
            if not isinstance(value, dict):
                raise CanonicalValueError("narrative item must be an object")
            narratives.append(
                NarrativeItem(
                    text=_text(value, "text"),
                    evidence_refs=tuple(
                        str(reference) for reference in _sequence(value, "evidence_refs")
                    ),
                )
            )
        path = generate_daily_report(
            repository_root,
            run_id=_text(raw, "run_id"),
            run_status=_text(raw, "run_status"),
            report_date=(
                parse_iso_date(_text(raw, "report_date")) if raw.get("report_date") else None
            ),
            narrative_items=narratives,
            github_report_url=_text(raw, "github_report_url", default=""),
        )
        print(path.relative_to(repository_root).as_posix())
        return 0
    raise CanonicalValueError(f"unhandled structured command: {arguments.command}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command after enforcing repository and paper-only startup settings."""

    arguments = _parser().parse_args(argv)
    try:
        root = find_repository_root(arguments.repository)
        settings = load_settings(root, os.environ)
        if arguments.command == "schema":
            errors = validate_csv_files(root)
            errors.extend(validate_json_schemas(root))
            return _print_result("schema", errors)
        if arguments.command == "integrity":
            return _print_result("integrity", validate_integrity(root, os.environ))
        if arguments.command == "wiki":
            return _print_result("wiki", lint_wiki(settings.paths.wiki))
        if arguments.command == "market":
            return _print_result("market", update_market_data(root, settings))
        if arguments.command == "indicators":
            previous, current, indicator_errors = update_indicators(root, settings)
            if not indicator_errors and arguments.classify_opportunities:
                bars = {security_id: read_price_cache(root, security_id) for security_id in current}
                process_opportunity_transitions(
                    root,
                    settings,
                    previous,
                    current,
                    bars,
                )
            return _print_result("indicators", indicator_errors)
        if arguments.command == "queue":
            return _run_queue_command(arguments, root, settings)
        if arguments.command == "portfolio" and arguments.portfolio_command == "reconcile":
            return _print_result("portfolio", reconcile_portfolio(root))
        if arguments.command == "performance":
            row = update_performance(root, settings, run_id=arguments.run_id)
            print(json.dumps(row, sort_keys=True))
            return 0
        if arguments.command == "logs":
            regenerate_log_tail(root)
            return _print_result("logs", [])
        if arguments.command in {
            "account",
            "signal",
            "order",
            "fills",
            "portfolio",
            "corporate-actions",
            "issue",
            "report",
        }:
            return _run_structured_command(arguments, root, settings)
        if arguments.command == "runtime-whitelist":
            paths = tuple(arguments.paths)
            if arguments.staged or arguments.base_ref:
                if paths:
                    raise ValueError("explicit paths cannot be combined with Git diff options")
                paths = changed_paths_from_git(
                    root,
                    staged=arguments.staged,
                    base_ref=arguments.base_ref,
                    head_ref=arguments.head_ref,
                )
            if not paths:
                raise ValueError("provide paths, --staged, or --base-ref")
            return _print_result("runtime-whitelist", validate_runtime_paths(paths))
    except (
        CanonicalValueError,
        ConfigurationError,
        json.JSONDecodeError,
        OSError,
        RuntimeError,
        ValueError,
    ) as exc:
        print(f"ERROR [{arguments.command}] {exc}", file=sys.stderr)
        return 2
    return _print_result("command", ["unhandled command"])
