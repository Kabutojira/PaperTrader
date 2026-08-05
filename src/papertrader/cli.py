"""PaperTrader command-line interface for deterministic validated state transitions."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from papertrader.advice import refresh_advice, validate_advice
from papertrader.agent_runner import (
    configure_hermes_home,
    preflight_hermes,
    run_cycle_operation,
    run_one_operation,
)
from papertrader.allocation import (
    allocation_readiness,
    maintain_allocation_research,
    plan_allocation,
    write_calibration_report,
)
from papertrader.checkpoints import create_checkpoint
from papertrader.command_audit import audit_context, canonical_command, record_command
from papertrader.command_scope import command_allowed, normalized_command
from papertrader.config import ConfigurationError, Settings, find_repository_root, load_settings
from papertrader.corporate_actions import accrue_dividends
from papertrader.daily import (
    complete_daily_cycle,
    execute_agent_batch,
    finalize_daily_run,
    prepare_daily_run,
    record_cycle_checkpoint,
    record_local_agent_outcome,
    resume_or_create_daily_cycle,
)
from papertrader.execution import ensure_initial_capital, process_order_fill
from papertrader.indicators import update_indicators
from papertrader.integrity import (
    changed_paths_from_git,
    prepared_daily_cycle_for_github_run,
    publication_requires_current_state,
    validate_csv_files,
    validate_integrity,
    validate_json_schemas,
    validate_runtime_paths,
)
from papertrader.issues import record_issue, resolve_issue
from papertrader.local_harness import (
    finish_local_harness_operation,
    start_local_harness_operation,
)
from papertrader.logs import regenerate_log_tail
from papertrader.market_data import read_price_cache, update_market_data
from papertrader.models import (
    MarketBar,
    OptionQuote,
    PositionMark,
    ReferencePrice,
)
from papertrader.oauth_credentials import apply_oauth_ciphertext_artifact
from papertrader.opportunity import (
    process_opportunity_transitions,
    refresh_candidate_packet_display,
    retry_unclassified_candidate_packets,
)
from papertrader.orders import (
    cancel_paper_order,
    create_baseline_paper_order,
    create_paper_order,
    create_signal,
    leg_from_mapping,
)
from papertrader.performance import rebase_performance, update_performance
from papertrader.podcast import (
    build_podcast_context,
    enqueue_daily_podcast,
    finalize_daily_podcast,
    render_committed_podcast,
)
from papertrader.portfolio import build_risk_state, rebuild_portfolio, reconcile_portfolio
from papertrader.profiles import analyst_relationship_gate
from papertrader.publication import apply_runtime_bundle, create_runtime_bundle
from papertrader.queue import (
    OPERATION_SKILLS,
    RunBudget,
    block_operation,
    claim_next,
    complete_operation,
    enqueue_operation,
    fail_attempt,
    prepare_queue,
    release_expired_leases,
    resolve_blocked_operation,
    validate_queue,
)
from papertrader.reports import NarrativeItem, generate_daily_report, refresh_wiki_homepage
from papertrader.repository_state import snapshot_repository
from papertrader.research import (
    import_watchlist,
    migrate_legacy_assessments,
    record_source,
    upsert_assessment,
    upsert_relationship,
    upsert_security,
    upsert_strategy,
)
from papertrader.seekingalpha import (
    enqueue_seekingalpha_leads,
    schedule_seekingalpha_discovery,
)
from papertrader.tables import read_table
from papertrader.telegram import (
    committed_run_report_path,
    deliver_committed_report,
    deliver_podcast_audio,
    record_podcast_audio_failure,
)
from papertrader.utils import (
    CanonicalValueError,
    decimal_text,
    parse_iso_date,
    parse_timestamp,
    required_decimal,
    utc_now,
)
from papertrader.wiki import lint_wiki
from papertrader.wiki_maintenance import maintain_wiki
from papertrader.youtube import backfill_youtube, scan_youtube


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="papertrader")
    parser.add_argument("--repository", type=Path, help="repository root (defaults to discovery)")
    commands = parser.add_subparsers(dest="command", required=True)

    schema = commands.add_parser("schema", help="validate repository schemas")
    schema_commands = schema.add_subparsers(dest="schema_command", required=True)
    schema_commands.add_parser("validate").add_argument("--strict", action="store_true")

    integrity = commands.add_parser("integrity", help="run repository integrity checks")
    integrity.add_argument("--strict", action="store_true")
    integrity_context = integrity.add_mutually_exclusive_group()
    integrity_context.add_argument(
        "--prepared-daily-cycle-id",
        default="",
        help="defer only publication freshness for a verified unfinalized daily cycle",
    )
    integrity_context.add_argument(
        "--prepared-github-run-id",
        default="",
        help="defer only publication freshness for this GitHub run's unique unfinalized cycle",
    )

    wiki = commands.add_parser("wiki", help="work with the research wiki")
    wiki_commands = wiki.add_subparsers(dest="wiki_command", required=True)
    wiki_commands.add_parser("lint").add_argument("--strict", action="store_true")
    wiki_commands.add_parser("refresh-homepage")
    wiki_commands.add_parser("refresh-inbox")
    wiki_maintain = wiki_commands.add_parser(
        "maintain", help="run the bundled native llm-wiki maintenance procedure"
    )
    wiki_maintain.add_argument("--run-id", required=True)
    wiki_maintain.add_argument("--hermes-home", type=Path, required=True)
    wiki_maintain.add_argument("--dry-run", action="store_true")

    classifier = commands.add_parser("classifier", help="run bounded inbox classification")
    classifier_commands = classifier.add_subparsers(dest="classifier_command", required=True)
    classifier_commands.add_parser("retry")

    youtube = commands.add_parser("youtube", help="scan curated secret-free video sources")
    youtube_commands = youtube.add_subparsers(dest="youtube_command", required=True)
    youtube_scan = youtube_commands.add_parser("scan")
    youtube_scan.add_argument("--run-id", required=True)
    youtube_scan.add_argument("--dry-run", action="store_true")
    youtube_backfill = youtube_commands.add_parser("backfill")
    youtube_backfill.add_argument("--run-id", required=True)
    youtube_backfill.add_argument("--channel-id", required=True)
    youtube_backfill.add_argument("--count", type=int, required=True)

    seekingalpha = commands.add_parser(
        "seekingalpha", help="schedule and validate search-index-only article leads"
    )
    seekingalpha_commands = seekingalpha.add_subparsers(dest="seekingalpha_command", required=True)
    seekingalpha_schedule = seekingalpha_commands.add_parser("schedule")
    seekingalpha_schedule.add_argument("--run-id", required=True)
    seekingalpha_schedule.add_argument("--dry-run", action="store_true")
    seekingalpha_enqueue = seekingalpha_commands.add_parser("enqueue-leads")
    seekingalpha_enqueue.add_argument("--request", type=Path, required=True)

    market = commands.add_parser("market", help="retrieve and normalize market state")
    market_commands = market.add_subparsers(dest="market_command", required=True)
    market_commands.add_parser("update")

    daily = commands.add_parser("daily", help="run sequential deterministic daily phases")
    daily_commands = daily.add_subparsers(dest="daily_command", required=True)
    daily_cycle = daily_commands.add_parser("resume-or-create")
    daily_cycle.add_argument("--trigger", required=True)
    daily_cycle.add_argument("--source-sha", required=True)
    daily_cycle.add_argument("--github-run-id", required=True)
    daily_cycle.add_argument("--workflow-attempt", required=True)
    daily_cycle.add_argument("--resume-cycle-id", default="")
    daily_prepare = daily_commands.add_parser("prepare")
    daily_prepare.add_argument("--run-id", required=True)
    daily_prepare.add_argument("--trigger", required=True)
    daily_prepare.add_argument("--source-sha", required=True)
    daily_prepare.add_argument("--offline", action="store_true")
    daily_prepare.add_argument("--skip-classifier", action="store_true")
    daily_finalize = daily_commands.add_parser("finalize")
    daily_finalize.add_argument("--run-id", required=True)
    daily_finalize.add_argument("--github-report-url", required=True)
    daily_complete = daily_commands.add_parser("complete")
    daily_complete.add_argument("--daily-cycle-id", required=True)
    daily_checkpoint = daily_commands.add_parser("record-checkpoint")
    daily_checkpoint.add_argument("--daily-cycle-id", required=True)
    daily_checkpoint.add_argument(
        "--kind",
        choices=(
            "preparation",
            "operation",
            "failure",
            "finalization",
            "podcast_text",
            "credential",
        ),
        required=True,
    )
    daily_checkpoint.add_argument("--operation-id", default="")
    daily_checkpoint.add_argument("--operation-type", default="")
    daily_checkpoint.add_argument("--terminal-status", default="")
    daily_checkpoint.add_argument("--profile", default="")

    podcast = commands.add_parser("podcast", help="generate the final sequential daily podcast")
    podcast_commands = podcast.add_subparsers(dest="podcast_command", required=True)
    podcast_enqueue = podcast_commands.add_parser("enqueue")
    podcast_enqueue.add_argument("--run-id", required=True)
    podcast_context = podcast_commands.add_parser("context")
    podcast_context_commands = podcast_context.add_subparsers(
        dest="podcast_context_command", required=True
    )
    podcast_context_build = podcast_context_commands.add_parser("build")
    podcast_context_build.add_argument("--daily-cycle-id", required=True)
    podcast_context_build.add_argument("--cutoff", required=True)
    podcast_render = podcast_commands.add_parser("render")
    podcast_render.add_argument("--daily-cycle-id", required=True)
    podcast_render.add_argument("--script-commit", required=True)
    podcast_render.add_argument("--script-path", required=True)
    podcast_render.add_argument("--output-directory", type=Path, required=True)
    podcast_finalize = podcast_commands.add_parser("finalize")
    podcast_finalize.add_argument("--run-id", required=True)

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
    queue_resolve_blocked = queue_commands.add_parser("resolve-blocked")
    queue_resolve_blocked.add_argument("--request", type=Path, required=True)

    account = commands.add_parser("account", help="initialize paper-only accounting")
    account_commands = account.add_subparsers(dest="account_command", required=True)
    initialize = account_commands.add_parser("initialize")
    initialize.add_argument("--run-id", required=True)
    rebase = account_commands.add_parser("rebase")
    rebase.add_argument("--request", type=Path, required=True)

    signal = commands.add_parser("signal", help="create a time-bounded strategy decision")
    signal_commands = signal.add_subparsers(dest="signal_command", required=True)
    signal_create = signal_commands.add_parser("create")
    signal_create.add_argument("--request", type=Path, required=True)

    order = commands.add_parser("order", help="create or cancel a normalized paper order")
    order_commands = order.add_subparsers(dest="order_command", required=True)
    order_create = order_commands.add_parser("create")
    order_create.add_argument("--request", type=Path, required=True)
    order_create_baseline = order_commands.add_parser("create-baseline")
    order_create_baseline.add_argument("--request", type=Path, required=True)
    order_cancel = order_commands.add_parser("cancel")
    order_cancel.add_argument("--request", type=Path, required=True)

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

    allocation = commands.add_parser("allocation", help="plan bounded baseline allocation")
    allocation_commands = allocation.add_subparsers(dest="allocation_command", required=True)
    allocation_plan = allocation_commands.add_parser("plan")
    allocation_plan.add_argument("--run-id", required=True)
    allocation_maintain = allocation_commands.add_parser("maintain")
    allocation_maintain.add_argument("--run-id", required=True)
    allocation_maintain.add_argument("--backfill", action="store_true")
    allocation_readiness_command = allocation_commands.add_parser("readiness")
    allocation_readiness_command.add_argument("--strict", action="store_true")
    allocation_calibrate = allocation_commands.add_parser("calibrate")
    allocation_calibrate.add_argument("--run-id", required=True)

    advice = commands.add_parser("advice", help="publish the investor decision projection")
    advice_commands = advice.add_subparsers(dest="advice_command", required=True)
    advice_refresh = advice_commands.add_parser("refresh")
    advice_refresh.add_argument("--run-id", required=True)
    advice_refresh.add_argument("--as-of")
    advice_commands.add_parser("validate").add_argument("--strict", action="store_true")

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

    research = commands.add_parser("research", help="update validated structured research state")
    research_commands = research.add_subparsers(dest="research_command", required=True)
    for research_name in ("source", "security", "assessment", "relationship", "strategy"):
        research_group = research_commands.add_parser(research_name)
        action = "record" if research_name == "source" else "upsert"
        research_action = research_group.add_subparsers(
            dest="research_action", required=True
        ).add_parser(action)
        research_action.add_argument("--request", type=Path, required=True)
    security_context = research_commands.add_parser("security-context")
    security_context.add_argument("--security-id", required=True)
    security_context.add_argument("--history-limit", type=int, default=2)
    assessment_get = research_commands.add_parser("assessment-get")
    assessment_get.add_argument("--assessment-id", required=True)
    assessment_migrate = research_commands.add_parser("migrate-assessments")
    assessment_migrate.add_argument("--run-id", required=True)
    assessment_migrate.add_argument("--enqueue-limit", type=int, default=20)
    assessment_migrate.add_argument("--as-of")

    watchlist = commands.add_parser("watchlist", help="manage identity-only monitored securities")
    watchlist_commands = watchlist.add_subparsers(dest="watchlist_command", required=True)
    watchlist_import = watchlist_commands.add_parser("import")
    watchlist_import.add_argument("--request", type=Path, required=True)

    report = commands.add_parser("report", help="generate the canonical daily report")
    report_commands = report.add_subparsers(dest="report_command", required=True)
    report_generate = report_commands.add_parser("generate")
    report_generate.add_argument("--request", type=Path, required=True)

    logs = commands.add_parser("logs", help="regenerate human-readable log views")
    logs.add_subparsers(dest="logs_command", required=True).add_parser("tail")

    agent = commands.add_parser("agent", help="configure and run one credential-scrubbed agent")
    agent_commands = agent.add_subparsers(dest="agent_command", required=True)
    agent_configure = agent_commands.add_parser("configure")
    agent_configure.add_argument("--hermes-home", type=Path, required=True)
    agent_configure.add_argument("--replace-unmanaged", action="store_true")
    agent_preflight = agent_commands.add_parser("preflight")
    agent_preflight.add_argument("--hermes-home", type=Path, required=True)
    agent_preflight.add_argument(
        "--operation-type", default="wiki_ingest", choices=sorted(OPERATION_SKILLS)
    )
    agent_run = agent_commands.add_parser("run")
    agent_run.add_argument("--hermes-home", type=Path, required=True)
    agent_run.add_argument("--run-id", required=True)
    agent_run.add_argument("--operation-id")
    agent_run.add_argument("--operation-type", choices=sorted(OPERATION_SKILLS))
    agent_run.add_argument("--estimated-cost", default="0")
    agent_batch = agent_commands.add_parser("run-batch")
    agent_batch.add_argument("--hermes-home", type=Path, required=True)
    agent_batch.add_argument("--run-id", required=True)
    agent_batch.add_argument("--max-operations", type=int, required=True)
    agent_batch.add_argument("--operation-id")
    agent_batch.add_argument("--operation-type", choices=sorted(OPERATION_SKILLS))
    agent_checkpoint = agent_commands.add_parser("run-checkpoint")
    agent_checkpoint.add_argument("--hermes-home", type=Path, required=True)
    agent_checkpoint.add_argument("--daily-cycle-id", required=True)
    agent_checkpoint.add_argument("--operation-id")
    agent_checkpoint.add_argument("--operation-type", choices=sorted(OPERATION_SKILLS))
    agent_harness = agent_commands.add_parser(
        "harness", help="run one operation through a local agentic harness"
    )
    harness_commands = agent_harness.add_subparsers(dest="harness_command", required=True)
    harness_start = harness_commands.add_parser("start")
    harness_start.add_argument("--run-id", required=True)
    harness_start.add_argument("--operation-id")
    harness_start.add_argument("--operation-type", choices=sorted(OPERATION_SKILLS))
    harness_start.add_argument("--estimated-cost", default="0")
    harness_finish = harness_commands.add_parser("finish")
    harness_finish.add_argument("--run-id", required=True)
    harness_finish.add_argument("--operation-id", required=True)

    telegram = commands.add_parser("telegram", help="deliver an exact committed report")
    telegram_commands = telegram.add_subparsers(dest="telegram_command", required=True)
    telegram_deliver = telegram_commands.add_parser("deliver")
    telegram_deliver.add_argument("--commit-sha", required=True)
    telegram_deliver.add_argument("--report-path", required=True)
    telegram_deliver.add_argument("--repository-url", required=True)
    telegram_deliver.add_argument("--run-id", required=True)
    telegram_deliver_run = telegram_commands.add_parser("deliver-run")
    telegram_deliver_run.add_argument("--commit-sha", required=True)
    telegram_deliver_run.add_argument("--repository-url", required=True)
    telegram_deliver_run.add_argument("--run-id", required=True)
    telegram_audio = telegram_commands.add_parser("deliver-audio")
    telegram_audio.add_argument("--manifest-path", type=Path, required=True)
    telegram_audio.add_argument("--audio-path", type=Path, required=True)
    telegram_audio.add_argument("--repository-url", required=True)
    telegram_audio_failure = telegram_commands.add_parser("record-audio-failure")
    telegram_audio_failure.add_argument("--daily-cycle-id", required=True)
    telegram_audio_failure.add_argument("--script-commit", required=True)
    telegram_audio_failure.add_argument("--error", required=True)

    workflow = commands.add_parser("workflow", help="handoff validated runtime patches")
    workflow_commands = workflow.add_subparsers(dest="workflow_command", required=True)
    bundle = workflow_commands.add_parser("bundle")
    bundle_commands = bundle.add_subparsers(dest="bundle_command", required=True)
    bundle_create = bundle_commands.add_parser("create")
    bundle_create.add_argument("--output-directory", type=Path, required=True)
    bundle_create.add_argument("--run-id", required=True)
    bundle_create.add_argument("--base-sha", required=True)
    bundle_apply = bundle_commands.add_parser("apply")
    bundle_apply.add_argument("--bundle-directory", type=Path, required=True)
    oauth_artifact = workflow_commands.add_parser(
        "oauth-artifact", help="apply one verified encrypted OAuth artifact"
    )
    oauth_commands = oauth_artifact.add_subparsers(dest="oauth_artifact_command", required=True)
    oauth_apply = oauth_commands.add_parser("apply")
    oauth_apply.add_argument("--artifact-directory", type=Path, required=True)
    oauth_apply.add_argument("--expected-sha256", required=True)
    checkpoint = workflow_commands.add_parser("checkpoint")
    checkpoint.add_argument("--daily-cycle-id", required=True)
    checkpoint.add_argument("--checkpoint-index", type=int, required=True)
    checkpoint.add_argument("--kind", required=True)
    checkpoint.add_argument("--operation-id", default="")
    checkpoint.add_argument("--operation-type", default="")
    checkpoint.add_argument("--terminal-status", default="")
    checkpoint.add_argument("--profile", default="")
    checkpoint.add_argument("--target-branch", default="main")
    checkpoint.add_argument("--remote", default="origin")
    checkpoint.add_argument("--dry-run", action="store_true")

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
    lexical = path.absolute()
    try:
        relative = lexical.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise CanonicalValueError("request JSON must be inside the repository") from exc
    if ".." in relative.parts:
        raise CanonicalValueError("request JSON path traversal is forbidden")
    current = repository_root.resolve()
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise CanonicalValueError(f"request JSON must not traverse a symlink: {request_path}")
    resolved = lexical.resolve()
    try:
        resolved.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise CanonicalValueError("request JSON must be inside the repository") from exc
    if not resolved.is_file():
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


def _timestamp(
    raw: Mapping[str, object],
    key: str,
    *,
    required: bool = True,
    allow_now: bool = False,
) -> datetime | None:
    value = raw.get(key)
    if (value is None or value == "") and not required:
        return None
    if not isinstance(value, str):
        raise CanonicalValueError(f"request field {key} must be an ISO timestamp")
    if allow_now and value == "now":
        return utc_now().replace(microsecond=0)
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
            not_before=_timestamp(raw, "not_before", required=False, allow_now=True),
            deadline=_timestamp(raw, "deadline", required=False, allow_now=True),
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
                result_path=_text(raw, "result_path", default=""),
                result_summary=_text(raw, "result_summary", default=""),
            )
        )
    elif command == "block":
        block_operation(
            repository_root,
            operation_id=_text(raw, "operation_id"),
            run_id=_text(raw, "run_id"),
            reason=_text(raw, "reason"),
        )
    elif command == "resolve-blocked":
        resolve_blocked_operation(
            repository_root,
            operation_id=_text(raw, "operation_id"),
            run_id=_text(raw, "run_id"),
            terminal_status=_text(raw, "terminal_status"),
            result_path=_text(raw, "result_path"),
            result_summary=_text(raw, "result_summary"),
            terminal_reason=_text(raw, "terminal_reason"),
        )
    return 0


def _run_structured_command(
    arguments: argparse.Namespace, repository_root: Path, settings: Settings
) -> int:
    if arguments.command == "account":
        if arguments.account_command == "initialize":
            entry_id = ensure_initial_capital(
                repository_root,
                settings,
                run_id=arguments.run_id,
                occurred_at=utc_now(),
            )
            print(entry_id)
            return 0
        raw = _request_object(repository_root, arguments.request)
        expected = {"target_equity_base", "reason", "run_id", "effective_at"}
        if set(raw) != expected:
            raise CanonicalValueError(
                "account rebase request fields differ; "
                f"missing={sorted(expected - set(raw))}, extra={sorted(set(raw) - expected)}"
            )
        effective_at = _timestamp(raw, "effective_at")
        assert effective_at is not None
        epoch_id, cash_entry_id = rebase_performance(
            repository_root,
            settings,
            target_equity_base=required_decimal(
                _text(raw, "target_equity_base"), label="target_equity_base"
            ),
            reason=_text(raw, "reason"),
            run_id=_text(raw, "run_id"),
            effective_at=effective_at,
        )
        print(
            json.dumps(
                {"performance_epoch_id": epoch_id, "cash_entry_id": cash_entry_id},
                sort_keys=True,
            )
        )
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
        if arguments.order_command == "cancel":
            if set(raw) != {"order_id"}:
                raise CanonicalValueError("order cancel request requires exactly order_id")
            order_id = _text(raw, "order_id")
            cancel_paper_order(repository_root, order_id)
            print(json.dumps({"order_id": order_id, "status": "cancelled"}, sort_keys=True))
            return 0
        references = tuple(_reference(value) for value in _sequence(raw, "references"))
        now = _timestamp(raw, "now", required=False) or utc_now()
        risk_state = build_risk_state(repository_root, references, as_of=now)
        limit_raw = raw.get("limit_price")
        limit = (
            required_decimal(_text(raw, "limit_price"), label="limit_price")
            if limit_raw is not None and limit_raw != ""
            else None
        )
        signal_id = _text(raw, "signal_id")
        strategy_id = _text(raw, "strategy_id")
        run_id = _text(raw, "run_id")
        fill_policy = _text(raw, "fill_policy", default=settings.orders.default_fill_policy)
        order_type = _text(raw, "order_type", default=settings.orders.default_order_type)
        not_before = _timestamp(raw, "not_before", required=False)
        expires_at = _timestamp(raw, "expires_at", required=False)
        if arguments.order_command == "create-baseline":
            if "legs" in raw:
                raise CanonicalValueError("baseline order quantity and legs are code-owned")
            order_id, created, assessment = create_baseline_paper_order(
                repository_root,
                settings,
                signal_id=signal_id,
                strategy_id=strategy_id,
                references=references,
                risk_state=risk_state,
                run_id=run_id,
                fill_policy=fill_policy,
                order_type=order_type,
                limit_price=limit,
                not_before=not_before,
                expires_at=expires_at,
                now=now,
            )
        else:
            leg_values = _sequence(raw, "legs")
            if not all(isinstance(value, dict) for value in leg_values):
                raise CanonicalValueError("every order leg must be an object")
            legs = tuple(leg_from_mapping(value) for value in leg_values if isinstance(value, dict))
            order_id, created, assessment = create_paper_order(
                repository_root,
                settings,
                signal_id=signal_id,
                strategy_id=strategy_id,
                legs=legs,
                references=references,
                risk_state=risk_state,
                run_id=run_id,
                fill_policy=fill_policy,
                order_type=order_type,
                limit_price=limit,
                not_before=not_before,
                expires_at=expires_at,
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
        run_id = _text(raw, "run_id")
        generated_at = _timestamp(raw, "generated_at", required=False)
        completed = [row for row in read_table(repository_root, "runs") if row["run_id"] == run_id]
        if len(completed) != 1:
            raise CanonicalValueError("report run is not present exactly once in run history")
        if generated_at is None:
            generated_at = parse_timestamp(completed[0]["completed_at"])
        if generated_at is None:
            raise CanonicalValueError("report run has no completed timestamp")
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
        refresh_advice(
            repository_root,
            settings,
            run_id=run_id,
            as_of=generated_at,
        )
        path = generate_daily_report(
            repository_root,
            run_id=run_id,
            run_status=_text(raw, "run_status"),
            report_date=(
                parse_iso_date(_text(raw, "report_date")) if raw.get("report_date") else None
            ),
            narrative_items=narratives,
            github_report_url=_text(raw, "github_report_url", default=""),
            generated_at=generated_at,
        )
        print(path.relative_to(repository_root).as_posix())
        return 0
    raise CanonicalValueError(f"unhandled structured command: {arguments.command}")


def _run_research_command(
    arguments: argparse.Namespace, repository_root: Path, settings: Settings
) -> int:
    if arguments.research_command == "security-context":
        from papertrader.research import security_research_context

        print(
            json.dumps(
                security_research_context(
                    repository_root,
                    arguments.security_id,
                    history_limit=arguments.history_limit,
                ),
                sort_keys=True,
            )
        )
        return 0
    if arguments.research_command == "assessment-get":
        from papertrader.research import assessment_by_id

        print(
            json.dumps(assessment_by_id(repository_root, arguments.assessment_id), sort_keys=True)
        )
        return 0
    if arguments.research_command == "migrate-assessments":
        migrated = migrate_legacy_assessments(
            repository_root,
            settings,
            run_id=arguments.run_id,
            enqueue_limit=arguments.enqueue_limit,
            now=parse_timestamp(arguments.as_of, allow_empty=True),
        )
        print(json.dumps(asdict(migrated), sort_keys=True))
        return 0
    raw = _request_object(repository_root, arguments.request)
    if arguments.research_command == "source":
        history_id, changed = record_source(repository_root, raw)
        print(json.dumps({"source_history_id": history_id, "changed": changed}, sort_keys=True))
    elif arguments.research_command == "security":
        print(json.dumps({"changed": upsert_security(repository_root, settings, raw)}))
    elif arguments.research_command == "assessment":
        print(json.dumps({"changed": upsert_assessment(repository_root, settings, raw)}))
    elif arguments.research_command == "relationship":
        print(json.dumps({"changed": upsert_relationship(repository_root, raw)}))
    elif arguments.research_command == "strategy":
        print(json.dumps({"changed": upsert_strategy(repository_root, settings, raw)}))
    else:
        raise CanonicalValueError(f"unhandled research command: {arguments.research_command}")
    return 0


def _dispatch(arguments: argparse.Namespace, root: Path, settings: Settings) -> int:
    if arguments.command == "schema":
        errors = validate_csv_files(root)
        errors.extend(validate_json_schemas(root))
        return _print_result("schema", errors)
    if arguments.command == "integrity":
        prepared_daily_cycle_id = arguments.prepared_daily_cycle_id
        if arguments.prepared_github_run_id:
            prepared_daily_cycle_id = prepared_daily_cycle_for_github_run(
                root,
                arguments.prepared_github_run_id,
            )
        require_current_publication = (
            publication_requires_current_state(
                root,
                os.environ,
                prepared_daily_cycle_id=prepared_daily_cycle_id,
            )
            if prepared_daily_cycle_id
            else None
        )
        return _print_result(
            "integrity",
            validate_integrity(
                root,
                os.environ,
                require_current_publication=require_current_publication,
            ),
        )
    if arguments.command == "wiki":
        if arguments.wiki_command == "lint":
            return _print_result("wiki", lint_wiki(settings.paths.wiki))
        if arguments.wiki_command == "maintain":
            outcome = maintain_wiki(
                root,
                settings,
                run_id=arguments.run_id,
                hermes_home=arguments.hermes_home.absolute(),
                environment=os.environ,
                dry_run=arguments.dry_run,
            )
            print(json.dumps(asdict(outcome), sort_keys=True))
            return 0
        if arguments.wiki_command == "refresh-homepage":
            path = refresh_wiki_homepage(root)
            print(path.relative_to(root).as_posix())
            return 0
        candidate_paths = refresh_candidate_packet_display(root, settings)
        print(json.dumps([path.relative_to(root).as_posix() for path in candidate_paths]))
        return 0
    if arguments.command == "classifier":
        packets = retry_unclassified_candidate_packets(root, settings)
        print(
            json.dumps(
                [
                    {
                        "path": packet.path.relative_to(root).as_posix(),
                        "decision": packet.decision.decision if packet.decision else "blocked",
                    }
                    for packet in packets
                ],
                sort_keys=True,
            )
        )
        return 0
    if arguments.command == "youtube":
        if arguments.youtube_command == "backfill":
            result = backfill_youtube(
                root,
                settings,
                run_id=arguments.run_id,
                channel_id=arguments.channel_id,
                count=arguments.count,
            )
        else:
            result = scan_youtube(
                root,
                settings,
                run_id=arguments.run_id,
                dry_run=arguments.dry_run,
            )
        print(json.dumps(result, sort_keys=True))
        return 0
    if arguments.command == "seekingalpha":
        if arguments.seekingalpha_command == "schedule":
            result = schedule_seekingalpha_discovery(
                root,
                settings,
                run_id=arguments.run_id,
                dry_run=arguments.dry_run,
            )
        else:
            result = enqueue_seekingalpha_leads(
                root,
                settings,
                _request_object(root, arguments.request),
            )
        print(json.dumps(result, sort_keys=True))
        return 0
    if arguments.command == "market":
        return _print_result("market", update_market_data(root, settings))
    if arguments.command == "daily":
        if arguments.daily_command == "resume-or-create":
            cycle = resume_or_create_daily_cycle(
                root,
                settings,
                trigger=arguments.trigger,
                source_sha=arguments.source_sha,
                github_run_id=arguments.github_run_id,
                workflow_attempt=arguments.workflow_attempt,
                resume_cycle_id=arguments.resume_cycle_id,
            )
            print(json.dumps(cycle, sort_keys=True))
            return 0
        if arguments.daily_command == "prepare":
            daily_preparation = prepare_daily_run(
                root,
                settings,
                run_id=arguments.run_id,
                trigger=arguments.trigger,
                source_sha=arguments.source_sha,
                retrieve_market=not arguments.offline,
                classify_opportunities=not arguments.skip_classifier,
            )
            print(
                json.dumps(
                    {
                        "run_id": daily_preparation.run_id,
                        "started_at": daily_preparation.started_at.isoformat(),
                        "errors": daily_preparation.errors,
                        "queue_dispositions": daily_preparation.queue_dispositions,
                    },
                    sort_keys=True,
                )
            )
            return 0
        if arguments.daily_command == "record-checkpoint":
            checkpoint = record_cycle_checkpoint(
                root,
                daily_cycle_id=arguments.daily_cycle_id,
                kind=arguments.kind,
                operation_id=arguments.operation_id,
                operation_type=arguments.operation_type,
                terminal_status=arguments.terminal_status,
                profile=arguments.profile,
            )
            print(json.dumps(checkpoint, sort_keys=True))
            return 0
        if arguments.daily_command == "complete":
            print(
                json.dumps(
                    complete_daily_cycle(root, daily_cycle_id=arguments.daily_cycle_id),
                    sort_keys=True,
                )
            )
            return 0
        daily_finalization = finalize_daily_run(
            root,
            settings,
            run_id=arguments.run_id,
            github_report_url=arguments.github_report_url,
        )
        print(json.dumps(asdict(daily_finalization), sort_keys=True))
        return 0
    if arguments.command == "podcast":
        if arguments.podcast_command == "enqueue":
            print(
                json.dumps(
                    asdict(enqueue_daily_podcast(root, settings, run_id=arguments.run_id)),
                    sort_keys=True,
                )
            )
            return 0
        if arguments.podcast_command == "context":
            cutoff = parse_timestamp(arguments.cutoff)
            if cutoff is None:
                raise CanonicalValueError("podcast cutoff must be a UTC timestamp")
            print(
                build_podcast_context(
                    root,
                    settings,
                    daily_cycle_id=arguments.daily_cycle_id,
                    cutoff=cutoff,
                )
            )
            return 0
        if arguments.podcast_command == "render":
            print(
                json.dumps(
                    asdict(
                        render_committed_podcast(
                            root,
                            settings,
                            daily_cycle_id=arguments.daily_cycle_id,
                            script_commit=arguments.script_commit,
                            script_path=arguments.script_path,
                            output_directory=arguments.output_directory,
                        )
                    ),
                    sort_keys=True,
                )
            )
            return 0
        print(finalize_daily_podcast(root, run_id=arguments.run_id))
        return 0
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
    if arguments.command == "research":
        return _run_research_command(arguments, root, settings)
    if arguments.command == "watchlist":
        raw = _request_object(root, arguments.request)
        print(json.dumps(import_watchlist(root, settings, raw), sort_keys=True))
        return 0
    if arguments.command == "agent":
        if arguments.agent_command == "harness":
            if arguments.harness_command == "start":
                started = start_local_harness_operation(
                    root,
                    settings,
                    run_id=arguments.run_id,
                    operation_id=arguments.operation_id,
                    operation_type=arguments.operation_type,
                    estimated_cost=required_decimal(
                        arguments.estimated_cost, label="estimated_cost"
                    ),
                )
                print("null" if started is None else json.dumps(asdict(started), sort_keys=True))
                return 0
            finished = finish_local_harness_operation(
                root,
                run_id=arguments.run_id,
                operation_id=arguments.operation_id,
            )
            if (root / "data" / "runs" / arguments.run_id / "daily_run.json").is_file():
                record_local_agent_outcome(
                    root,
                    settings,
                    run_id=arguments.run_id,
                    operation_id=arguments.operation_id,
                    status=finished.status,
                )
            print(json.dumps(asdict(finished), sort_keys=True))
            return 0
        home = arguments.hermes_home.absolute()
        if arguments.agent_command == "configure":
            path = configure_hermes_home(
                root,
                settings,
                home,
                replace_unmanaged=arguments.replace_unmanaged,
            )
            print(path)
            return 0
        if arguments.agent_command == "preflight":
            report = preflight_hermes(
                root,
                settings,
                home,
                operation_type=arguments.operation_type,
                environment=os.environ,
            )
            document = asdict(report)
            document["weighted_cost"] = decimal_text(report.weighted_cost)
            print(json.dumps(document, sort_keys=True))
            return 0
        if arguments.agent_command == "run-batch":
            batch_result = execute_agent_batch(
                root,
                settings,
                run_id=arguments.run_id,
                hermes_home=home,
                environment=os.environ,
                maximum_operations=arguments.max_operations,
                operation_id=arguments.operation_id,
                operation_type=arguments.operation_type,
            )
            print(
                json.dumps(
                    {
                        "operation_count": batch_result.operation_count,
                        "estimated_model_budget_used": str(batch_result.estimated_cost_used),
                        "outcomes": [asdict(outcome) for outcome in batch_result.outcomes],
                    },
                    sort_keys=True,
                )
            )
            return 0
        if arguments.agent_command == "run-checkpoint":
            checkpoint_outcome = run_cycle_operation(
                root,
                settings,
                daily_cycle_id=arguments.daily_cycle_id,
                hermes_home=home,
                environment=os.environ,
                operation_id=arguments.operation_id,
                operation_type=arguments.operation_type,
            )
            print(
                "null"
                if checkpoint_outcome is None
                else json.dumps(asdict(checkpoint_outcome), sort_keys=True, default=str)
            )
            return 0
        disposition = run_one_operation(
            root,
            settings,
            run_id=arguments.run_id,
            hermes_home=home,
            environment=os.environ,
            operation_id=arguments.operation_id,
            operation_type=arguments.operation_type,
            estimated_cost=required_decimal(arguments.estimated_cost, label="estimated_cost"),
        )
        print(disposition)
        return 0
    if arguments.command == "telegram":
        if arguments.telegram_command == "record-audio-failure":
            failure_result = record_podcast_audio_failure(
                root,
                daily_cycle_id=arguments.daily_cycle_id,
                script_commit=arguments.script_commit,
                error=arguments.error,
            )
            print(json.dumps(asdict(failure_result), sort_keys=True))
            return 0
        if arguments.telegram_command == "deliver-audio":
            audio_delivery_result = deliver_podcast_audio(
                root,
                settings,
                manifest_path=arguments.manifest_path,
                audio_path=arguments.audio_path,
                repository_url=arguments.repository_url,
                token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
                chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
            )
            print(json.dumps(asdict(audio_delivery_result), sort_keys=True))
            return 0
        report_path = (
            committed_run_report_path(
                root,
                commit_sha=arguments.commit_sha,
                run_id=arguments.run_id,
            )
            if arguments.telegram_command == "deliver-run"
            else arguments.report_path
        )
        report_delivery_result = deliver_committed_report(
            root,
            settings,
            commit_sha=arguments.commit_sha,
            report_path=report_path,
            repository_url=arguments.repository_url,
            run_id=arguments.run_id,
            token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
            chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
        )
        print(json.dumps(asdict(report_delivery_result), sort_keys=True))
        return 0
    if arguments.command == "workflow":
        if arguments.workflow_command == "bundle":
            if arguments.bundle_command == "create":
                bundle = create_runtime_bundle(
                    root,
                    arguments.output_directory,
                    run_id=arguments.run_id,
                    base_sha=arguments.base_sha,
                )
            else:
                bundle = apply_runtime_bundle(root, arguments.bundle_directory)
            print(
                json.dumps(
                    {
                        "base_sha": bundle.base_sha,
                        "run_id": bundle.run_id,
                        "patch_sha256": bundle.patch_sha256,
                        "changed": bundle.changed,
                        "changed_paths": bundle.changed_paths,
                        "report_path": bundle.report_path,
                    },
                    sort_keys=True,
                )
            )
        elif arguments.workflow_command == "oauth-artifact":
            path = apply_oauth_ciphertext_artifact(
                root,
                arguments.artifact_directory,
                expected_sha256=arguments.expected_sha256,
            )
            print(path.relative_to(root).as_posix())
        else:
            checkpoint_result = create_checkpoint(
                root,
                settings,
                daily_cycle_id=arguments.daily_cycle_id,
                checkpoint_index=arguments.checkpoint_index,
                kind=arguments.kind,
                operation_id=arguments.operation_id,
                operation_type=arguments.operation_type,
                terminal_status=arguments.terminal_status,
                profile=arguments.profile,
                target_branch=arguments.target_branch,
                remote=arguments.remote,
                dry_run=arguments.dry_run,
                github_token=os.environ.get("GITHUB_TOKEN", ""),
            )
            print(json.dumps(asdict(checkpoint_result), sort_keys=True))
        return 0
    if arguments.command == "portfolio" and arguments.portfolio_command == "reconcile":
        return _print_result("portfolio", reconcile_portfolio(root))
    if arguments.command == "performance":
        row = update_performance(root, settings, run_id=arguments.run_id)
        print(json.dumps(row, sort_keys=True))
        return 0
    if arguments.command == "allocation":
        if arguments.allocation_command == "plan":
            plan_result = plan_allocation(root, settings, run_id=arguments.run_id)
            print(json.dumps(asdict(plan_result), sort_keys=True))
            return 0
        elif arguments.allocation_command == "maintain":
            maintenance_result = maintain_allocation_research(
                root,
                settings,
                run_id=arguments.run_id,
                backfill=arguments.backfill,
            )
            print(json.dumps(asdict(maintenance_result), sort_keys=True))
            return 0
        elif arguments.allocation_command == "calibrate":
            path = write_calibration_report(root, settings, run_id=arguments.run_id)
            print(path.relative_to(root).as_posix())
            return 0
        readiness = allocation_readiness(root, settings)
        print(json.dumps(asdict(readiness), sort_keys=True))
        return int(arguments.strict and not readiness.ready)
    if arguments.command == "advice":
        if arguments.advice_command == "refresh":
            snapshot = refresh_advice(
                root,
                settings,
                run_id=arguments.run_id,
                as_of=parse_timestamp(arguments.as_of) if arguments.as_of else None,
            )
            print(json.dumps(asdict(snapshot), sort_keys=True))
            return 0
        return _print_result(
            "advice",
            validate_advice(
                root,
                strict=arguments.strict,
                require_current_state=publication_requires_current_state(root, os.environ),
            ),
        )
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
    return _print_result("command", ["unhandled command"])


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command and emit an operation-scoped CLI audit receipt when requested."""

    raw_arguments = tuple(argv) if argv is not None else tuple(sys.argv[1:])
    arguments = _parser().parse_args(raw_arguments)
    root: Path | None = None
    context = None
    before = None
    started_at = utc_now()
    exit_code = 2
    try:
        root = find_repository_root(arguments.repository)
        local_harness_boundary = (
            arguments.command == "agent" and arguments.agent_command == "harness"
        )
        context = None if local_harness_boundary else audit_context(root, os.environ)
        if context is not None:
            if context.operation_type and not command_allowed(
                context.operation_type,
                raw_arguments,
                pre_dispatch=True,
                profile=context.profile,
            ):
                print(
                    "ERROR [command-scope] "
                    f"{canonical_command(raw_arguments)} is outside the "
                    f"{context.operation_type} skill scope",
                    file=sys.stderr,
                )
                return 2
            if context.profile == "analyst" and normalized_command(raw_arguments)[:3] == (
                "research",
                "relationship",
                "upsert",
            ):
                request_path = getattr(arguments, "request", None)
                if request_path is None or not analyst_relationship_gate(
                    root, _request_object(root, request_path)
                ):
                    print(
                        "ERROR [profile-scope] analyst relationship change requires a "
                        "deep allocation-enablement review",
                        file=sys.stderr,
                    )
                    return 2
            before = snapshot_repository(root)
        settings = load_settings(root, os.environ)
        exit_code = _dispatch(arguments, root, settings)
    except (
        CanonicalValueError,
        ConfigurationError,
        json.JSONDecodeError,
        OSError,
        RuntimeError,
        ValueError,
    ) as exc:
        print(f"ERROR [{arguments.command}] {exc}", file=sys.stderr)
        exit_code = 2
    if context is not None and root is not None and before is not None:
        try:
            record_command(
                root,
                context,
                arguments=raw_arguments,
                exit_code=exit_code,
                started_at=started_at,
                completed_at=utc_now(),
                before=before,
                after=snapshot_repository(root),
            )
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
            print(f"ERROR [command-audit] {exc}", file=sys.stderr)
            return 2
    return exit_code
