"""Pure, versioned routing and command authority for Hermes execution profiles."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, replace
from pathlib import Path, PurePosixPath

from papertrader.config import HermesExecutionProfile, Settings
from papertrader.queue import Operation
from papertrader.tables import read_table

PROFILE_POLICY_VERSION = "profile-router-v1"
PROFILE_ORDER = {"scout": 0, "analyst": 1, "deep": 2}


@dataclass(frozen=True, slots=True)
class RoutingContext:
    """Trusted deterministic facts used by the pure profile router."""

    current_holding: bool = False
    target_exposure: bool = False
    pending_order: bool = False
    active_strategy: bool = False
    ready_signal: bool = False
    material_change: bool = False
    conflicting_evidence: bool = False
    unsupported_valuation: bool = False
    decision_change: bool = False
    initial_research: bool = False
    broad_research: bool = False
    option_or_multileg: bool = False

    @property
    def portfolio_sensitive(self) -> bool:
        return any(
            (
                self.current_holding,
                self.target_exposure,
                self.pending_order,
                self.active_strategy,
                self.ready_signal,
            )
        )


@dataclass(frozen=True, slots=True)
class ProfileRoute:
    """Persistable output of one deterministic routing decision."""

    profile: str
    profile_policy_version: str
    route_reason: str
    escalation_source: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def route_profile(
    operation_type: str,
    context: RoutingContext,
    *,
    escalation_source: str = "",
) -> ProfileRoute:
    """Select exactly one profile without consulting untrusted prose or a model."""

    deep_reasons = (
        (context.portfolio_sensitive, "portfolio_sensitive_conclusion"),
        (context.material_change, "material_business_or_instrument_change"),
        (context.conflicting_evidence, "conflicting_primary_evidence"),
        (context.unsupported_valuation, "unsupported_prior_valuation"),
        (context.decision_change, "decision_changing_conclusion"),
        (context.option_or_multileg, "option_or_multileg_work"),
    )
    if operation_type in {"strategy_research", "execute_strategy"}:
        selected = "deep"
        reason = "full_strategy_or_execution_decision"
    elif operation_type == "daily_podcast":
        selected = "deep"
        reason = "strict_long_form_podcast_contract"
    elif operation_type == "security_research":
        # The current security contract is scenario-complete, so it always requires full authority.
        selected = "deep"
        reason = "scenario_complete_security_review"
    elif operation_type == "idea_research" and (context.initial_research or context.broad_research):
        selected = "deep"
        reason = "broad_or_initial_value_chain_research"
    else:
        forced = next((value for condition, value in deep_reasons if condition), "")
        if forced:
            selected, reason = "deep", forced
        elif operation_type == "source_discovery":
            selected, reason = "scout", "bounded_triage_or_quick_check"
        elif operation_type == "quick_check_research":
            # A quick check may need to publish a comparable assessment in the same
            # operation. Only the deep profile has that deterministic command authority.
            selected, reason = "deep", "assessment_capable_quick_check"
        elif operation_type in {
            "wiki_ingest",
            "opportunity_research",
            "idea_research",
            "relationship_research",
        }:
            selected, reason = "analyst", "routine_research_or_long_form_synthesis"
        else:
            selected, reason = "deep", "fail_closed_unknown_or_full_research"
    if escalation_source:
        source_rank = PROFILE_ORDER.get(escalation_source)
        if source_rank is None or PROFILE_ORDER[selected] <= source_rank:
            raise ValueError("profile escalation must move one way to a stronger profile")
        reason = f"escalated:{escalation_source}:{reason}"
    return ProfileRoute(selected, PROFILE_POLICY_VERSION, reason, escalation_source)


def _payload_metadata(repository_root: Path, operation: Operation) -> Mapping[str, object]:
    path = repository_root.joinpath(*PurePosixPath(operation.payload_path).parts)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(value, dict):
        return {}
    inputs = value.get("inputs")
    return inputs if isinstance(inputs, dict) else {}


def routing_context(repository_root: Path, operation: Operation) -> RoutingContext:
    """Collect bounded canonical facts, then return the router's immutable input."""

    metadata = _payload_metadata(repository_root, operation)
    relationships = read_table(repository_root, "relationships")
    relationship = next(
        (row for row in relationships if row["relationship_id"] == operation.entity_id),
        None,
    )
    security_id = (
        operation.entity_id
        if operation.entity_type == "security"
        else (
            relationship["security_id"]
            if relationship is not None
            else metadata.get("security_id", "")
        )
    )
    security_id = security_id if isinstance(security_id, str) else ""
    holdings = read_table(repository_root, "portfolio")
    targets = read_table(repository_root, "allocation_targets")
    orders = read_table(repository_root, "orders")
    order_legs = read_table(repository_root, "order_legs")
    strategies = read_table(repository_root, "strategies")
    signals = read_table(repository_root, "signals")
    pending_order_ids = {
        row["order_id"] for row in orders if row["status"] not in {"filled", "cancelled", "expired"}
    }
    pending_security_ids = {
        row["security_id"] for row in order_legs if row["order_id"] in pending_order_ids
    }
    assessment = next(
        (
            row
            for row in read_table(repository_root, "security_assessments")
            if row["security_id"] == security_id
        ),
        None,
    )
    idea_page = repository_root / "data" / "wiki" / "ideas" / f"{operation.entity_id}.md"
    return RoutingContext(
        current_holding=any(
            row["security_id"] == security_id and row["quantity"] not in {"", "0"}
            for row in holdings
        ),
        target_exposure=any(
            row["security_id"] == security_id and row.get("target_weight_pct", "") not in {"", "0"}
            for row in targets
        ),
        pending_order=security_id in pending_security_ids,
        active_strategy=any(
            row["security_id"] == security_id and row["status"] in {"ready", "active"}
            for row in strategies
        ),
        ready_signal=any(
            row["status"] in {"ready", "open"}
            and any(
                strategy["strategy_id"] == row["strategy_id"]
                and strategy["security_id"] == security_id
                for strategy in strategies
            )
            for row in signals
        ),
        conflicting_evidence=(
            assessment is not None and "conflict" in assessment.get("hard_blockers", "").lower()
        ),
        unsupported_valuation=(
            assessment is not None and assessment.get("valuation_supported") != "true"
        ),
        decision_change=(
            operation.operation_type == "relationship_research"
            and (relationship is None or relationship["status"] != "accepted")
        ),
        initial_research=operation.operation_type == "idea_research" and not idea_page.is_file(),
        broad_research=operation.operation_type == "idea_research" and not idea_page.is_file(),
    )


def select_profile(
    repository_root: Path,
    settings: Settings,
    operation: Operation,
    *,
    escalation_source: str = "",
) -> tuple[HermesExecutionProfile, ProfileRoute]:
    """Route a validated queue operation and resolve its configured profile."""

    route = route_profile(
        operation.operation_type,
        routing_context(repository_root, operation),
        escalation_source=escalation_source,
    )
    profile = settings.hermes.profile(route.profile)
    if operation.operation_type == "daily_podcast":
        profile = replace(
            profile,
            timeout_seconds=settings.podcast.operation_timeout_seconds,
        )
    if profile.policy_version != route.profile_policy_version:
        raise ValueError("profile and router policy versions differ")
    return profile, route


def profile_command_allowed(profile: str, arguments: tuple[str, ...]) -> bool:
    """Enforce the minimum profile mutation boundary at CLI dispatch time."""

    command = arguments
    forbidden_for_scout = (
        ("research", "assessment", "upsert"),
        ("research", "relationship", "upsert"),
        ("research", "strategy", "upsert"),
        ("signal", "create"),
        ("order", "create"),
        ("order", "create-baseline"),
        ("order", "cancel"),
    )
    deep_only = (
        ("research", "assessment", "upsert"),
        ("research", "strategy", "upsert"),
        ("signal", "create"),
        ("order", "create"),
        ("order", "create-baseline"),
        ("order", "cancel"),
    )
    if profile == "scout":
        return not any(command[: len(prefix)] == prefix for prefix in forbidden_for_scout)
    if profile == "analyst":
        return not any(command[: len(prefix)] == prefix for prefix in deep_only)
    return profile == "deep"


def analyst_relationship_gate(repository_root: Path, request: Mapping[str, object]) -> bool:
    """Allow only timestamp/page refreshes of an unchanged canonical relationship."""

    relationship_id = request.get("relationship_id")
    status = request.get("status")
    if not isinstance(relationship_id, str) or not isinstance(status, str):
        return False
    previous = next(
        (
            row
            for row in read_table(repository_root, "relationships")
            if row["relationship_id"] == relationship_id
        ),
        None,
    )
    if previous is None or status != previous["status"]:
        return False
    decision_fields = (
        "idea_id",
        "security_id",
        "relationship_type",
        "direction",
        "mechanism",
        "sensitivity",
        "confidence",
        "catalyst",
        "invalidation",
        "status",
    )
    return all(request.get(field) == previous[field] for field in decision_fields)
