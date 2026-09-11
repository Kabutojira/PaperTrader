"""Controller-owned, immutable final purchase review and execution clearance."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jsonschema import Draft202012Validator, FormatChecker

from papertrader.atomic_io import atomic_write_json
from papertrader.config import Settings
from papertrader.models import OrderLegSpec, ReferencePrice, RiskState
from papertrader.queue import Operation, enqueue_operation
from papertrader.tables import read_table
from papertrader.utils import (
    content_hash,
    decimal_text,
    format_timestamp,
    parse_timestamp,
    required_decimal,
)

if TYPE_CHECKING:
    from papertrader.orders import PreparedOrder

POLICY = "final-buy-v1"
PACKETS = "data/operations/buy-review-packets"
REVIEWS = "data/operations/buy-review-results"
REVIEW_MODEL = "gpt-6-astra"


class BuyReviewError(RuntimeError):
    """A review or approval cannot be safely used."""


class BuyReviewPending(BuyReviewError):
    """A valid intent has no applicable approval; it is not an order."""

    def __init__(self, review_request_id: str, disposition: str = "awaiting_final_review") -> None:
        self.review_request_id = review_request_id
        self.disposition = disposition
        super().__init__(f"{disposition}:{review_request_id}")


def _json_value(value: object) -> Any:
    return json.loads(
        json.dumps(
            value, default=lambda x: decimal_text(x) if isinstance(x, Decimal) else x.isoformat()
        )
    )


def _load(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_relative_to(root) or ".." in Path(relative).parts:
        raise BuyReviewError("review path escapes repository")
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise BuyReviewError("review path traverses a symlink")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BuyReviewError("review artifact must be an object")
    return value


def _write_once(root: Path, relative: str, value: Mapping[str, object]) -> None:
    path = root / relative
    if path.exists():
        if _load(root, relative) != value:
            raise BuyReviewError(f"immutable review collision: {relative}")
        return
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise BuyReviewError("review path traverses a symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, value, allowed_root=root)


def _validate(root: Path, name: str, value: Mapping[str, object]) -> None:
    schema = _load(root, f"schemas/{name}.schema.json")
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value))
    if errors:
        raise BuyReviewError("; ".join(error.message for error in errors))


def requires_review(legs: Sequence[OrderLegSpec], state: RiskState) -> bool:
    """Classify actual quantities as a package; labels cannot disguise new exposure."""
    available: dict[tuple[str, str, str], Decimal] = defaultdict(Decimal)
    for position in state.positions:
        available[(position.security_id, position.provider_contract_id, position.side)] += (
            position.quantity
        )
    reductions: dict[tuple[str, str, str], Decimal] = defaultdict(Decimal)
    for leg in legs:
        opening = (leg.side == "long" and leg.action == "buy") or (
            leg.side == "short" and leg.action == "sell"
        )
        if opening:
            return True
        reductions[(leg.security_id, leg.provider_contract_id, leg.side)] += leg.quantity
    return any(quantity > available[key] for key, quantity in reductions.items())


def publication_status(
    root: Path,
    *,
    signal_id: str,
    order: Mapping[str, str] | None,
    legs: Sequence[OrderLegSpec],
    now: datetime,
) -> tuple[str, bool, str]:
    """Read-only review display; never an input into execution or financial state."""
    from papertrader.models import RiskPosition

    positions = tuple(
        RiskPosition(
            row["security_id"],
            row["provider_contract_id"],
            row["side"],
            row["instrument_type"],
            Decimal(row["quantity"]),
            Decimal("1"),
            row["currency"],
            "",
            None,
            None,
        )
        for row in read_table(root, "portfolio")
    )
    state = RiskState(
        Decimal("0"),
        Decimal("0"),
        Decimal("0"),
        Decimal("0"),
        Decimal("0"),
        Decimal("0"),
        0,
        positions,
    )
    if not requires_review(legs, state):
        return ("pending_order", True, "") if order else ("awaiting_order_validation", False, "")
    if order is not None:
        try:
            clearance = clearance_for_fill(root, order, legs, state)
            assert clearance is not None
            validate_clearance(root, *clearance, now=now)
            return "approved_order_pending", True, ""
        except BuyReviewError as exc:
            return "awaiting_final_review", False, str(exc)
    matches = []
    for path in (root / PACKETS).glob("*.json"):
        packet = _load(root, path.relative_to(root).as_posix())
        if packet["order"]["signal_id"] == signal_id:
            matches.append(packet)
    if not matches:
        return "awaiting_order_validation", False, "No otherwise-eligible intent prepared"
    packet = max(matches, key=lambda value: (value["created_at"], value["review_request_id"]))
    review_path = f"{REVIEWS}/{packet['review_request_id']}.json"
    if not (root / review_path).exists():
        return "awaiting_final_review", False, "Independent final review pending"
    review = _load(root, review_path)
    status = {
        "REJECT": "final_review_rejected",
        "DEFER": "final_review_deferred",
        "APPROVE": "awaiting_order_validation",
    }[review["decision"]]
    return status, False, str(review["reason"])


def material_state(root: Path, security_ids: set[str], strategy_id: str) -> dict[str, object]:
    """Bind financial substance, excluding incidental run/report/refresh timestamps."""
    selected: dict[str, object] = {}
    incidental = {
        "updated_at",
        "created_at",
        "last_reviewed_at",
        "last_research_at",
        "run_id",
        "allocation_plan_id",
        "research_summary",
        "reference_price",
        "market_data_as_of",
        "fx_rate_to_base",
        "fx_as_of",
        "bear_return_pct",
        "base_return_pct",
        "bull_return_pct",
        "expected_return_pct",
        "confidence_adjusted_expected_return_pct",
        "margin_of_safety_pct",
        "downside_pct",
        "base_upside_pct",
    }
    for table in ("securities", "security_assessments", "relationships", "strategies"):
        rows = [
            row
            for row in read_table(root, table)
            if (
                row.get("strategy_id") == strategy_id
                if table == "strategies"
                else row.get("security_id") in security_ids
            )
        ]
        if table == "strategies":
            for row in rows:
                if row.get("status") in {"ready", "active"}:
                    row["status"] = "executable"
        selected[table] = [
            {key: value for key, value in row.items() if key not in incidental}
            for row in sorted(rows, key=lambda row: json.dumps(row, sort_keys=True))
        ]
    assessments = [
        row
        for row in read_table(root, "security_assessments")
        if row["security_id"] in security_ids
    ]
    source_ids = {
        source
        for row in assessments
        for source in row.get("evidence_refs", "").split("|")
        if source
    }
    selected["sources"] = [
        {
            key: value
            for key, value in row.items()
            if key
            not in {
                "last_checked_at",
                "last_changed_at",
                "content_hash",
                "updated_at",
                "created_at",
                "run_id",
            }
        }
        for row in read_table(root, "source_registry")
        if row["source_id"] in source_ids
    ]
    from papertrader.evidence import material_claims

    selected["claims"] = material_claims(root, security_ids)
    return selected


def build_packet(
    root: Path,
    settings: Settings,
    prepared: PreparedOrder,
    *,
    references: Sequence[ReferencePrice],
    risk_state: RiskState,
    now: datetime,
) -> dict[str, Any]:
    order = prepared.order
    security_ids = {row["security_id"] for row in prepared.legs}
    substance = material_state(root, security_ids, order["strategy_id"])
    reference_map = {(ref.security_id, ref.provider_contract_id): ref for ref in references}
    envelope = []
    for row in prepared.legs:
        reference = reference_map[(row["security_id"], row["provider_contract_id"])]
        maximum = reference.price * (1 + settings.orders.slippage_bps / Decimal("10000"))
        limits = [row["limit_price"], order["limit_price"]]
        maximum = min([maximum, *(Decimal(limit) for limit in limits if limit)])
        envelope.append(
            {
                "leg_id": row["leg_id"],
                "quantity": row["quantity"],
                "max_price": decimal_text(maximum),
                "max_unit_base": decimal_text(maximum * reference.fx_rate_to_base),
            }
        )
    intent = {
        key: value
        for key, value in order.items()
        if key not in {"created_at", "run_id", "status", "not_before", "expires_at"}
    }
    material = {
        "policy": POLICY,
        "intent": intent,
        "legs": list(prepared.legs),
        "state": substance,
        "envelope": envelope,
    }
    request_id = "buy_review_" + content_hash(material)[:32]
    valid_until = parse_timestamp(order["expires_at"])
    assert valid_until is not None
    for row in read_table(root, "security_assessments"):
        if row["security_id"] in security_ids:
            for field in ("expires_at", "next_review_at"):
                if row.get(field):
                    expiry = parse_timestamp(row[field])
                    if expiry is not None:
                        valid_until = min(valid_until, expiry)
    if valid_until <= now:
        raise BuyReviewError("otherwise-eligible review intent has no remaining validity")
    packet: dict[str, Any] = {
        "packet_version": 1,
        "review_request_id": request_id,
        "material": material,
        "material_hash": content_hash(material),
        "created_at": format_timestamp(now),
        "valid_until": format_timestamp(valid_until),
        "order": dict(order),
        "references": [_json_value(asdict(ref)) for ref in references],
        "preflight": _json_value(asdict(prepared.assessment)),
        "portfolio_context": _json_value(asdict(risk_state)),
    }
    packet["packet_hash"] = content_hash(packet)
    _validate(root, "buy_review_packet", packet)
    return packet


def packet_for_operation(root: Path, operation: Operation) -> dict[str, Any]:
    inputs = _load(root, operation.payload_path)["inputs"]
    request_id = inputs["review_request_id"]
    if inputs["packet_path"] != f"{PACKETS}/{request_id}.json":
        raise BuyReviewError("review packet path conflicts with identity")
    packet = _load(root, f"{PACKETS}/{request_id}.json")
    _validate(root, "buy_review_packet", packet)
    if (
        packet["review_request_id"] != request_id
        or packet["order"]["strategy_id"] != operation.entity_id
    ):
        raise BuyReviewError("review operation conflicts with its packet")
    if (
        content_hash({key: value for key, value in packet.items() if key != "packet_hash"})
        != packet["packet_hash"]
    ):
        raise BuyReviewError("review packet hash mismatch")
    return packet


def require_order_clearance(
    root: Path,
    settings: Settings,
    prepared: PreparedOrder,
    *,
    references: Sequence[ReferencePrice],
    risk_state: RiskState,
    now: datetime,
) -> None:
    from papertrader.orders import leg_from_row

    if not prepared.created and prepared.order["status"] in {"filled", "cancelled", "expired"}:
        return  # Historical accounting recovery does not acquire retrospective approval.
    legs = tuple(leg_from_row(row) for row in prepared.legs)
    if not requires_review(legs, risk_state):
        return
    packet = build_packet(
        root, settings, prepared, references=references, risk_state=risk_state, now=now
    )
    request_id = packet["review_request_id"]
    packet_path = f"{PACKETS}/{request_id}.json"
    if (root / packet_path).exists():
        packet = _load(root, packet_path)
    else:
        _write_once(root, packet_path, packet)
    review_path = f"{REVIEWS}/{request_id}.json"
    if (root / review_path).exists():
        review = _load(root, review_path)
        if review["decision"] != "APPROVE":
            raise BuyReviewPending(request_id, "final_review_" + review["decision"].lower())
        validate_clearance(root, packet, review, now=now)
        return
    enqueue_operation(
        root,
        settings,
        operation_type="final_buy_review",
        entity_type="strategy",
        entity_id=prepared.order["strategy_id"],
        dedupe_key=f"final_buy_review:{request_id}",
        prompt="Independently review the exact otherwise-eligible paper purchase packet.",
        inputs={"review_request_id": request_id, "packet_path": packet_path},
        source="controller:final_buy_preflight",
        priority=99,
        freshness_days=0,
        deadline=parse_timestamp(packet["valid_until"]),
        source_refs=(packet_path,),
        now=now,
    )
    raise BuyReviewPending(request_id)


def validate_clearance(
    root: Path,
    packet: Mapping[str, Any],
    review: Mapping[str, Any],
    *,
    now: datetime,
    check_current_state: bool = True,
    require_approval: bool = True,
) -> None:
    """Require trusted invocation evidence, exact material state, and a live time window."""
    if (require_approval and review.get("decision") != "APPROVE") or review.get(
        "packet_hash"
    ) != packet["packet_hash"]:
        raise BuyReviewError("buy approval does not match the packet")
    _validate(root, "buy_review_packet", packet)
    if (
        content_hash({key: value for key, value in packet.items() if key != "packet_hash"})
        != packet["packet_hash"]
    ):
        raise BuyReviewError("review packet hash mismatch")
    if content_hash(packet["material"]) != packet["material_hash"]:
        raise BuyReviewError("review material hash mismatch")
    if (
        review.get("review_request_id") != packet["review_request_id"]
        or review.get("order_id") != packet["order"]["order_id"]
    ):
        raise BuyReviewError("review identity mismatch")
    evidence_directory = f"data/runs/{review['run_id']}/{review['operation_id']}"
    if (
        review["invocation_path"] != f"{evidence_directory}/hermes_run.json"
        or review["result_path"] != f"{evidence_directory}/agent_result.json"
    ):
        raise BuyReviewError("review provenance path mismatch")
    invocation = _load(root, str(review["invocation_path"]))
    if (
        invocation.get("model"),
        invocation.get("provider"),
        invocation.get("reasoning_effort"),
        invocation.get("returncode"),
    ) != (REVIEW_MODEL, "openai-codex", "high", 0):
        raise BuyReviewError("buy approval lacks an authenticated Astra invocation")
    if content_hash(invocation) != review["invocation_hash"]:
        raise BuyReviewError("buy invocation evidence changed")
    for artifact in (invocation, _load(root, f"{evidence_directory}/validation_report.json")):
        if (
            artifact.get("run_id") != review["run_id"]
            or artifact.get("operation_id") != review["operation_id"]
        ):
            raise BuyReviewError("review provenance identity mismatch")
    validation = _load(root, f"{evidence_directory}/validation_report.json")
    if validation.get("passed") is not True or validation.get("profile") != "final_review":
        raise BuyReviewError("review lacks successful controller validation")
    result = _load(root, str(review["result_path"]))
    if content_hash(result) != review["result_hash"]:
        raise BuyReviewError("buy review result evidence changed")
    submitted = result.get("final_buy_review", {})
    _validate(root, "buy_review_result", submitted)
    if result.get("status") != "succeeded" or any(
        review.get(key) != value for key, value in submitted.items()
    ):
        raise BuyReviewError("accepted review differs from validated result")
    accepted = parse_timestamp(str(review["accepted_at"]))
    expiry = parse_timestamp(str(packet["valid_until"]))
    if accepted is None or expiry is None or not accepted <= now <= expiry:
        raise BuyReviewError("buy approval is not active at the execution time")
    completed = parse_timestamp(str(invocation.get("completed_at", "")))
    if completed is None or completed > accepted:
        raise BuyReviewError("approval precedes reviewer completion")
    ids = {row["security_id"] for row in packet["material"]["legs"]}
    if (
        check_current_state
        and material_state(root, ids, packet["order"]["strategy_id"]) != packet["material"]["state"]
    ):
        raise BuyReviewError("buy approval material state changed")


def validate_review_state(root: Path) -> list[str]:
    """Validate durable proof, including expired approvals, without rewriting history."""
    errors = []
    for path in sorted((root / PACKETS).glob("*.json")):
        try:
            packet = _load(root, path.relative_to(root).as_posix())
            _validate(root, "buy_review_packet", packet)
            if (
                path.stem != packet["review_request_id"]
                or content_hash(packet["material"]) != packet["material_hash"]
            ):
                raise BuyReviewError("packet identity or material hash mismatch")
            if (
                content_hash({key: value for key, value in packet.items() if key != "packet_hash"})
                != packet["packet_hash"]
            ):
                raise BuyReviewError("packet content hash mismatch")
        except (BuyReviewError, OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"{path.name}: {exc}")
    for path in sorted((root / REVIEWS).glob("*.json")):
        try:
            review = _load(root, path.relative_to(root).as_posix())
            packet = _load(root, f"{PACKETS}/{path.name}")
            if review["review_request_id"] != path.stem:
                raise BuyReviewError("review filename identity mismatch")
            result = _load(root, review["result_path"])
            _validate(root, "buy_review_result", result["final_buy_review"])
            if content_hash(result) != review["result_hash"]:
                raise BuyReviewError("review result evidence changed")
            accepted = parse_timestamp(review["accepted_at"])
            if accepted is None:
                raise BuyReviewError("missing review acceptance")
            validate_clearance(
                root,
                packet,
                review,
                now=accepted,
                check_current_state=False,
                require_approval=False,
            )
        except (BuyReviewError, OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"{path.name}: {exc}")
    return errors


def accept_review(
    root: Path,
    settings: Settings,
    operation: Operation,
    result: Mapping[str, Any],
    *,
    run_id: str,
    now: datetime,
) -> dict[str, Any]:
    """Parent-only acceptance, called after sandbox result validation; no public CLI."""
    packet = packet_for_operation(root, operation)
    review = result.get("final_buy_review")
    if not isinstance(review, dict):
        raise BuyReviewError("final buy review result is missing")
    _validate(root, "buy_review_result", review)
    if (
        review["packet_hash"] != packet["packet_hash"]
        or review["review_request_id"] != packet["review_request_id"]
    ):
        raise BuyReviewError("final review belongs to a different packet")
    invocation_path = f"data/runs/{run_id}/{operation.operation_id}/hermes_run.json"
    invocation = _load(root, invocation_path)
    if (
        invocation.get("model"),
        invocation.get("provider"),
        invocation.get("reasoning_effort"),
        invocation.get("returncode"),
    ) != (REVIEW_MODEL, "openai-codex", "high", 0):
        raise BuyReviewError("final review requires a successful Astra invocation")
    validation = _load(root, f"data/runs/{run_id}/{operation.operation_id}/validation_report.json")
    if not validation.get("passed"):
        raise BuyReviewError("final buy review did not pass parent validation")
    result_path = f"data/runs/{run_id}/{operation.operation_id}/agent_result.json"
    accepted = {
        **review,
        "accepted_at": format_timestamp(now),
        "run_id": run_id,
        "operation_id": operation.operation_id,
        "invocation_path": invocation_path,
        "invocation_hash": content_hash(invocation),
        "result_path": result_path,
        "result_hash": content_hash(result),
        "order_id": packet["order"]["order_id"],
    }
    path = f"{REVIEWS}/{packet['review_request_id']}.json"
    if (root / path).exists():
        return _load(root, path)
    validate_clearance(
        root,
        packet,
        accepted,
        now=now,
        check_current_state=review["decision"] == "APPROVE",
        require_approval=False,
    )
    _write_once(root, path, accepted)
    return accepted


def submit_approved_packet(
    root: Path, settings: Settings, operation: Operation, *, now: datetime
) -> None:
    """Revalidate current deterministic risk and submit without another model decision."""
    from papertrader.orders import create_paper_order, leg_from_row
    from papertrader.portfolio import build_risk_state

    packet = packet_for_operation(root, operation)
    review = _load(root, f"{REVIEWS}/{packet['review_request_id']}.json")
    if review["decision"] != "APPROVE":
        return
    existing = next(
        (
            row
            for row in read_table(root, "orders")
            if row["order_id"] == packet["order"]["order_id"]
        ),
        None,
    )
    if existing is not None:
        # Admission already completed. Do not replay submission or mutate a later disposition.
        # Every remaining fill still independently validates the immutable approval.
        return
    validate_clearance(root, packet, review, now=now)
    revalidate_packet(root, settings, packet, now=now)
    references = tuple(
        ReferencePrice(
            **{
                **raw,
                "price": Decimal(raw["price"]),
                "fx_rate_to_base": Decimal(raw["fx_rate_to_base"]),
                "as_of": parse_timestamp(raw["as_of"]),
                "bid": Decimal(raw["bid"]) if raw["bid"] is not None else None,
                "ask": Decimal(raw["ask"]) if raw["ask"] is not None else None,
            }
        )
        for raw in packet["references"]
    )
    order = packet["order"]
    existing = next(
        (row for row in read_table(root, "orders") if row["order_id"] == order["order_id"]), None
    )
    create_paper_order(
        root,
        settings,
        signal_id=order["signal_id"],
        strategy_id=order["strategy_id"],
        legs=tuple(leg_from_row(row) for row in packet["material"]["legs"]),
        references=references,
        risk_state=build_risk_state(root, references, as_of=now),
        run_id=review["run_id"],
        fill_policy=order["fill_policy"],
        order_type=order["order_type"],
        limit_price=Decimal(order["limit_price"]) if order["limit_price"] else None,
        not_before=parse_timestamp(existing["not_before"])
        if existing
        else max(parse_timestamp(order["not_before"]) or now, now),
        expires_at=parse_timestamp(order["expires_at"]),
        now=now,
    )


def clearance_for_fill(
    root: Path,
    order: Mapping[str, str],
    legs: Sequence[OrderLegSpec],
    state: RiskState,
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    from papertrader.orders import leg_row

    if not requires_review(legs, state):
        return None
    candidates = []
    for path in sorted((root / REVIEWS).glob("*.json")):
        review = _load(root, path.relative_to(root).as_posix())
        if review.get("order_id") == order["order_id"] and review.get("decision") == "APPROVE":
            packet = _load(root, f"{PACKETS}/{review['review_request_id']}.json")
            if [leg_row(order["order_id"], leg) for leg in legs] != packet["material"]["legs"]:
                raise BuyReviewError("pending order legs differ from approved package")
            if any(order.get(key) != value for key, value in packet["material"]["intent"].items()):
                raise BuyReviewError("pending order intent differs from approval")
            candidates.append((packet, review))
    if candidates:
        return max(
            candidates, key=lambda pair: (pair[1]["accepted_at"], pair[0]["review_request_id"])
        )
    raise BuyReviewError("awaiting_final_review: pending purchase lacks Astra approval")


def revalidate_packet(
    root: Path, settings: Settings, packet: Mapping[str, Any], *, now: datetime
) -> None:
    """No model call for an intent that ceased to pass current deterministic preflight."""
    from papertrader.orders import leg_from_row, prepare_paper_order
    from papertrader.portfolio import build_risk_state

    expiry = parse_timestamp(packet["valid_until"])
    if expiry is None or now >= expiry:
        raise BuyReviewError("final_review_intent_expired")
    order = packet["order"]
    legs = tuple(leg_from_row(row) for row in packet["material"]["legs"])
    if (
        material_state(root, {leg.security_id for leg in legs}, order["strategy_id"])
        != packet["material"]["state"]
    ):
        raise BuyReviewError("final_review_material_state_changed")
    references = tuple(
        ReferencePrice(
            **{
                **raw,
                "price": Decimal(raw["price"]),
                "fx_rate_to_base": Decimal(raw["fx_rate_to_base"]),
                "as_of": parse_timestamp(raw["as_of"]),
                "bid": Decimal(raw["bid"]) if raw["bid"] is not None else None,
                "ask": Decimal(raw["ask"]) if raw["ask"] is not None else None,
            }
        )
        for raw in packet["references"]
    )
    from papertrader.market_data import latest_fx_rate, session_close

    identities = {row["security_id"]: row for row in read_table(root, "securities")}
    current_marks = {row["security_id"]: row for row in read_table(root, "market_latest")}
    for leg in legs:
        reference = next(
            ref
            for ref in references
            if ref.security_id == leg.security_id
            and ref.provider_contract_id == leg.provider_contract_id
        )
        mark = current_marks.get(leg.security_id)
        if leg.instrument_type != "equity" or mark is None:
            continue  # Explicit fresh option quotes retain their existing preflight validation.
        from datetime import date

        marked_at = session_close(
            settings.market_data.calendar_for(identities[leg.security_id]["venue_mic"]),
            date.fromisoformat(mark["price_date"]),
        )
        if marked_at > now or mark["status"] != "ok":
            raise BuyReviewError("final_review_current_market_mark_unavailable")
        if marked_at >= reference.as_of:
            fx = latest_fx_rate(
                root,
                leg.currency,
                settings.portfolio.base_currency,
                now=now,
                maximum_age=settings.market_data.stale_price_after,
            )
            validate_fill_envelope(packet, leg, price=Decimal(mark["close"]), fx=fx)
    prepare_paper_order(
        root,
        settings,
        signal_id=order["signal_id"],
        strategy_id=order["strategy_id"],
        legs=legs,
        references=references,
        risk_state=build_risk_state(root, references, as_of=now),
        run_id=order["run_id"],
        fill_policy=order["fill_policy"],
        order_type=order["order_type"],
        limit_price=Decimal(order["limit_price"]) if order["limit_price"] else None,
        not_before=max(parse_timestamp(order["not_before"]) or now, now),
        expires_at=parse_timestamp(order["expires_at"]),
        now=now,
    )


def validate_fill_envelope(
    packet: Mapping[str, Any], leg: OrderLegSpec, *, price: Decimal, fx: Decimal
) -> None:
    envelope = next(
        (row for row in packet["material"]["envelope"] if row["leg_id"] == leg.leg_id), None
    )
    if envelope is None or leg.quantity > required_decimal(
        envelope["quantity"], label="approved quantity"
    ):
        raise BuyReviewError("fill exceeds approved quantity")
    if leg.action == "buy" and (
        price > Decimal(envelope["max_price"]) or price * fx > Decimal(envelope["max_unit_base"])
    ):
        raise BuyReviewError("fill price or FX exceeds approved envelope")


def finish_review_operation(
    root: Path, settings: Settings, operation: Operation, *, run_id: str, now: datetime
) -> str:
    """Resume the acceptance/submission transaction without invoking another reviewer."""
    from papertrader.issues import record_issue
    from papertrader.orders import OrderError
    from papertrader.portfolio import PortfolioError
    from papertrader.queue import complete_operation
    from papertrader.risk import RiskRejected

    packet = packet_for_operation(root, operation)
    review = _load(root, f"{REVIEWS}/{packet['review_request_id']}.json")
    try:
        submit_approved_packet(root, settings, operation, now=now)
        reason = f"final_review_{review['decision'].lower()}"
    except (BuyReviewError, OrderError, PortfolioError, RiskRejected) as exc:
        reason = "final_review_submission_deferred"
        record_issue(
            root,
            issue_code=reason,
            impact="affects_candidate",
            severity="warning",
            title="Approved paper purchase deferred by deterministic revalidation",
            description=str(exc),
            entity_type="strategy",
            entity_id=operation.entity_id,
            owner="controller",
            related_run_id=run_id,
            related_operation_id=operation.operation_id,
        )
    result_path = f"data/runs/{run_id}/{operation.operation_id}/agent_result.json"
    if result_path != review["result_path"]:
        resumed = _load(root, review["result_path"])
        resumed["summary"] = f"Resumed accepted review from {review['result_path']}: {reason}"
        resumed["reason_code"] = "final_review_acceptance_resumed"
        _write_once(root, result_path, resumed)
    complete_operation(
        root,
        operation_id=operation.operation_id,
        run_id=run_id,
        terminal_status="succeeded",
        result_path=result_path,
        result_summary=reason,
        terminal_reason=reason,
    )
    return "succeeded"
