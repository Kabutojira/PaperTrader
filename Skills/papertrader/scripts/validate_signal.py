#!/usr/bin/env python3
"""Validate a PaperTrader qualitative signal without external dependencies.

This validates structure and semantic coherence only. It deliberately does not
calculate quantity, risk, margin, exposure, or final order authorization.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

TOP_LEVEL_KEYS = {
    "schema_version",
    "request_id",
    "as_of",
    "instrument",
    "thesis",
    "signal",
    "analysis",
    "data_quality",
}
INSTRUMENT_KEYS = {
    "instrument_key",
    "ticker",
    "type",
    "underlying",
    "call_put",
    "strike",
    "expiration",
    "multiplier",
}
THESIS_KEYS = {"thesis_id", "summary", "trigger", "invalidation", "horizon"}
SIGNAL_KEYS = {
    "action",
    "side",
    "order_type",
    "reference_price",
    "limit_price",
    "levels_basis",
    "stop_loss",
    "target",
    "valid_until",
}
ANALYSIS_KEYS = {"base_case", "bull_case", "bear_case", "key_risks", "confidence"}
DATA_QUALITY_KEYS = {"price_timestamp", "missing_fields", "warnings"}

ACTIONS = {"NO_TRADE", "OPEN_LONG", "OPEN_SHORT", "CLOSE", "REDUCE", "INCREASE"}
SIDES = {"BUY", "SELL", "NONE"}
ORDER_TYPES = {"MARKET", "LIMIT", "STOP", "STOP_LIMIT", "NONE"}
LEVELS_BASES = {"STRUMENTO", "SOTTOSTANTE", None}
FORBIDDEN_KEYS = {
    "quantity",
    "qty",
    "contracts",
    "number_of_contracts",
    "position_size",
    "risk_budget",
    "margin",
    "authorization",
    "authorized",
    "send_order",
    "broker_order",
}


def parse_iso_datetime(value: Any, field: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty ISO-8601 date-time string")
        return None
    candidate = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        errors.append(f"{field} is not a valid ISO-8601 date-time")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{field} must include a UTC offset")
        return None
    return parsed


def parse_iso_date(value: Any, field: str, errors: list[str]) -> date | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty ISO date string")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{field} is not a valid YYYY-MM-DD date")
        return None


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def positive_number(value: Any) -> bool:
    return is_number(value) and float(value) > 0


def canonical_decimal(value: Any) -> str:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal: {value!r}") from exc
    if not number.is_finite():
        raise ValueError(f"non-finite decimal: {value!r}")
    rendered = format(number.normalize(), "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def check_exact_keys(obj: Any, expected: set[str], field: str, errors: list[str]) -> bool:
    if not isinstance(obj, dict):
        errors.append(f"{field} must be an object")
        return False
    actual = set(obj)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"{field} is missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{field} has unsupported keys: {', '.join(extra)}")
    return not missing and not extra


def walk_forbidden(value: Any, path: str = "$") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                yield f"{path}.{key}"
            yield from walk_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_forbidden(child, f"{path}[{index}]")


def non_empty_string(value: Any, field: str, errors: list[str], max_length: int | None = None) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")
    elif max_length is not None and len(value) > max_length:
        errors.append(f"{field} exceeds {max_length} characters")


def string_list(value: Any, field: str, errors: list[str], max_items: int) -> None:
    if not isinstance(value, list):
        errors.append(f"{field} must be an array")
        return
    if len(value) > max_items:
        errors.append(f"{field} may contain at most {max_items} items")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{field}[{index}] must be a non-empty string")


def validate_document(document: Any, max_age_minutes: float | None = None) -> list[str]:
    errors: list[str] = []

    if not isinstance(document, dict):
        return ["root must be a JSON object"]

    check_exact_keys(document, TOP_LEVEL_KEYS, "root", errors)
    forbidden_paths = list(walk_forbidden(document))
    if forbidden_paths:
        errors.append("forbidden model-authority fields found: " + ", ".join(forbidden_paths))

    if document.get("schema_version") != "1.0":
        errors.append("schema_version must be exactly '1.0'")
    non_empty_string(document.get("request_id"), "request_id", errors, 128)
    as_of = parse_iso_datetime(document.get("as_of"), "as_of", errors)

    instrument = document.get("instrument")
    if check_exact_keys(instrument, INSTRUMENT_KEYS, "instrument", errors):
        ticker = instrument["ticker"]
        instrument_type = instrument["type"]
        underlying = instrument["underlying"]
        call_put = instrument["call_put"]
        strike = instrument["strike"]
        expiration = instrument["expiration"]
        multiplier = instrument["multiplier"]

        non_empty_string(ticker, "instrument.ticker", errors, 64)
        non_empty_string(underlying, "instrument.underlying", errors, 32)
        if instrument_type not in {"AZIONE", "OPZIONE"}:
            errors.append("instrument.type must be AZIONE or OPZIONE")
        if not isinstance(multiplier, int) or isinstance(multiplier, bool) or multiplier < 1:
            errors.append("instrument.multiplier must be an integer >= 1")

        if isinstance(ticker, str) and isinstance(underlying, str):
            ticker_upper = ticker.upper()
            underlying_upper = underlying.upper()
            expected_key: str | None = None
            if instrument_type == "AZIONE":
                if call_put is not None or strike is not None or expiration is not None:
                    errors.append("stock call_put, strike, and expiration must be null")
                if multiplier != 1:
                    errors.append("stock multiplier must be 1")
                if underlying_upper != ticker_upper:
                    errors.append("stock underlying must equal ticker")
                expected_key = f"AZIONE|{ticker_upper}"
            elif instrument_type == "OPZIONE":
                if call_put not in {"CALL", "PUT"}:
                    errors.append("option call_put must be CALL or PUT")
                if not positive_number(strike):
                    errors.append("option strike must be a positive number")
                expiry = parse_iso_date(expiration, "instrument.expiration", errors)
                if expiry is not None and as_of is not None and expiry <= as_of.date():
                    errors.append("option expiration must be after as_of date")
                if positive_number(strike) and isinstance(multiplier, int) and multiplier >= 1:
                    expected_key = (
                        f"OPZIONE|{underlying_upper}|{call_put}|"
                        f"{canonical_decimal(strike)}|{expiration}|{multiplier}"
                    )
            if expected_key is not None and instrument.get("instrument_key") != expected_key:
                errors.append(
                    "instrument.instrument_key mismatch: "
                    f"expected {expected_key!r}, got {instrument.get('instrument_key')!r}"
                )

    thesis = document.get("thesis")
    if check_exact_keys(thesis, THESIS_KEYS, "thesis", errors):
        non_empty_string(thesis["thesis_id"], "thesis.thesis_id", errors, 128)
        non_empty_string(thesis["summary"], "thesis.summary", errors, 2000)
        non_empty_string(thesis["trigger"], "thesis.trigger", errors, 1000)
        non_empty_string(thesis["invalidation"], "thesis.invalidation", errors, 1000)
        non_empty_string(thesis["horizon"], "thesis.horizon", errors, 128)

    signal = document.get("signal")
    if check_exact_keys(signal, SIGNAL_KEYS, "signal", errors):
        action = signal["action"]
        side = signal["side"]
        order_type = signal["order_type"]
        reference = signal["reference_price"]
        limit_price = signal["limit_price"]
        levels_basis = signal["levels_basis"]
        stop = signal["stop_loss"]
        target = signal["target"]
        valid_until_value = signal["valid_until"]

        if action not in ACTIONS:
            errors.append(f"signal.action is invalid: {action!r}")
        if side not in SIDES:
            errors.append(f"signal.side is invalid: {side!r}")
        if order_type not in ORDER_TYPES:
            errors.append(f"signal.order_type is invalid: {order_type!r}")
        if levels_basis not in LEVELS_BASES:
            errors.append("signal.levels_basis must be STRUMENTO, SOTTOSTANTE, or null")

        if action == "NO_TRADE":
            if side != "NONE" or order_type != "NONE":
                errors.append("NO_TRADE requires side=NONE and order_type=NONE")
            for key in ("reference_price", "limit_price", "levels_basis", "stop_loss", "target", "valid_until"):
                if signal[key] is not None:
                    errors.append(f"NO_TRADE requires signal.{key}=null")
        elif action in ACTIONS:
            if side == "NONE" or order_type == "NONE":
                errors.append("a trade action requires a concrete side and order_type")
            if not positive_number(reference):
                errors.append("signal.reference_price must be a positive number for a trade action")
            if order_type in {"LIMIT", "STOP_LIMIT"} and not positive_number(limit_price):
                errors.append(f"{order_type} requires a positive signal.limit_price")
            if order_type not in {"LIMIT", "STOP_LIMIT"} and limit_price is not None:
                errors.append(f"{order_type} requires signal.limit_price=null")
            valid_until = parse_iso_datetime(valid_until_value, "signal.valid_until", errors)
            if valid_until is not None and as_of is not None and valid_until <= as_of:
                errors.append("signal.valid_until must be after as_of")

            if action == "OPEN_LONG" and side != "BUY":
                errors.append("OPEN_LONG requires side=BUY")
            if action == "OPEN_SHORT" and side != "SELL":
                errors.append("OPEN_SHORT requires side=SELL")

            if action in {"OPEN_LONG", "OPEN_SHORT", "INCREASE"}:
                if levels_basis not in {"STRUMENTO", "SOTTOSTANTE"}:
                    errors.append(f"{action} requires signal.levels_basis")
                if not positive_number(stop) or not positive_number(target):
                    errors.append(f"{action} requires positive stop_loss and target")
                if positive_number(reference) and positive_number(stop) and positive_number(target):
                    if side == "BUY" and not (float(stop) < float(reference) < float(target)):
                        errors.append("BUY exposure requires stop_loss < reference_price < target")
                    if side == "SELL" and not (float(target) < float(reference) < float(stop)):
                        errors.append("SELL exposure requires target < reference_price < stop_loss")

    analysis = document.get("analysis")
    if check_exact_keys(analysis, ANALYSIS_KEYS, "analysis", errors):
        non_empty_string(analysis["base_case"], "analysis.base_case", errors, 2000)
        non_empty_string(analysis["bull_case"], "analysis.bull_case", errors, 2000)
        non_empty_string(analysis["bear_case"], "analysis.bear_case", errors, 2000)
        string_list(analysis["key_risks"], "analysis.key_risks", errors, 10)
        confidence = analysis["confidence"]
        if not is_number(confidence) or not 0 <= float(confidence) <= 1:
            errors.append("analysis.confidence must be a finite number between 0 and 1")

    data_quality = document.get("data_quality")
    price_timestamp: datetime | None = None
    if check_exact_keys(data_quality, DATA_QUALITY_KEYS, "data_quality", errors):
        price_timestamp = parse_iso_datetime(
            data_quality["price_timestamp"], "data_quality.price_timestamp", errors
        )
        string_list(data_quality["missing_fields"], "data_quality.missing_fields", errors, 50)
        string_list(data_quality["warnings"], "data_quality.warnings", errors, 20)
        if data_quality["missing_fields"] and signal and signal.get("action") != "NO_TRADE":
            errors.append("missing_fields must be empty for a trade action")

    if max_age_minutes is not None:
        if max_age_minutes <= 0:
            errors.append("max_age_minutes must be greater than zero")
        elif price_timestamp is not None:
            now = datetime.now(timezone.utc)
            age_minutes = (now - price_timestamp.astimezone(timezone.utc)).total_seconds() / 60
            if age_minutes < -5:
                errors.append("data_quality.price_timestamp is more than 5 minutes in the future")
            elif age_minutes > max_age_minutes:
                errors.append(
                    f"market data is stale: age={age_minutes:.2f} minutes, "
                    f"limit={max_age_minutes:.2f}"
                )

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("signal", type=Path, help="Path to a signal JSON file")
    parser.add_argument(
        "--max-age-minutes",
        type=float,
        default=None,
        help="Optional maximum age for data_quality.price_timestamp",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        with args.signal.open("r", encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.signal}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: cannot read {args.signal}: {exc}", file=sys.stderr)
        return 2

    errors = validate_document(document, max_age_minutes=args.max_age_minutes)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
