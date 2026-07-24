"""Validated CLI-owned structured research state transitions."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

from papertrader.config import Settings
from papertrader.models import OrderLegSpec
from papertrader.orders import leg_from_mapping
from papertrader.tables import append_unique, contract_by_name, read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    decimal_text,
    ensure_utc,
    format_timestamp,
    parse_timestamp,
    required_decimal,
    stable_id,
    utc_now,
)

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
STRATEGY_STATUSES = frozenset(
    {"draft", "researching", "ready", "active", "paused", "closed", "rejected", "expired"}
)
IMMUTABLE_SECURITY_FIELDS = (
    "issuer_id",
    "instrument_name",
    "instrument_type",
    "venue_mic",
    "provider_symbol",
    "currency",
)


class ResearchStateError(RuntimeError):
    """Raised when a research-state mutation violates identity or schema rules."""


def _exact_strings(
    raw: Mapping[str, object], expected: Sequence[str], *, label: str
) -> dict[str, str]:
    actual = set(raw)
    required = set(expected)
    if actual != required:
        raise ResearchStateError(
            f"{label} fields differ; missing={sorted(required - actual)}, "
            f"extra={sorted(actual - required)}"
        )
    values: dict[str, str] = {}
    for field in expected:
        value = raw[field]
        if not isinstance(value, str):
            raise ResearchStateError(f"{label}.{field} must be a string")
        if "\x00" in value or "\r" in value or "\n" in value:
            raise ResearchStateError(f"{label}.{field} must be a single safe CSV value")
        values[field] = value.strip()
    return values


def _required(values: Mapping[str, str], fields: Sequence[str], *, label: str) -> None:
    missing = [field for field in fields if not values[field]]
    if missing:
        raise ResearchStateError(f"{label} requires non-empty fields: {missing}")


def _identifier(value: str, *, label: str) -> None:
    if not SAFE_ID.fullmatch(value):
        raise ResearchStateError(f"{label} is not a safe immutable identifier: {value!r}")


def _canonical_timestamp(value: str, *, label: str, allow_empty: bool = False) -> str:
    if not value and allow_empty:
        return ""
    parsed = parse_timestamp(value)
    assert parsed is not None
    canonical = format_timestamp(parsed)
    if canonical != value:
        raise ResearchStateError(f"{label} must use canonical UTC form {canonical}")
    return canonical


def _wiki_page(repository_root: Path, value: str, domain: str) -> str:
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or len(relative.parts) < 4
        or relative.parts[:3] != ("data", "wiki", domain)
        or relative.suffix != ".md"
    ):
        raise ResearchStateError(f"research_page must be Markdown under data/wiki/{domain}/")
    path = repository_root.joinpath(*relative.parts)
    if path.is_symlink() or not path.is_file():
        raise ResearchStateError(f"research_page must exist before structured upsert: {value}")
    return relative.as_posix()


def _replace_row(
    repository_root: Path,
    table: str,
    row: Mapping[str, str],
    *,
    key: str,
) -> bool:
    existing = read_table(repository_root, table)
    previous = next((candidate for candidate in existing if candidate[key] == row[key]), None)
    if previous == row:
        return False
    output = [candidate for candidate in existing if candidate[key] != row[key]]
    output.append(dict(row))
    output.sort(key=lambda candidate: candidate[key])
    write_table(repository_root, table, output)
    return True


def upsert_security(
    repository_root: Path,
    settings: Settings,
    raw: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> bool:
    """Insert or update one security while preserving its immutable provider identity."""

    columns = contract_by_name(repository_root, "securities").columns
    input_columns = tuple(
        column for column in columns if column not in {"created_at", "updated_at"}
    )
    values = _exact_strings(raw, input_columns, label="security")
    _required(
        values,
        (
            "security_id",
            "issuer_id",
            "company_name",
            "instrument_name",
            "instrument_type",
            "ticker",
            "exchange_code",
            "venue_mic",
            "provider_symbol",
            "currency",
            "country",
            "status",
            "research_summary",
            "research_page",
            "last_research_at",
            "next_review_at",
            "source",
        ),
        label="security",
    )
    _identifier(values["security_id"], label="security_id")
    _identifier(values["issuer_id"], label="issuer_id")
    if values["instrument_type"] not in settings.risk.allowed_instruments:
        raise ResearchStateError("security instrument_type is not allowed")
    if values["venue_mic"] not in settings.risk.allowed_exchanges:
        raise ResearchStateError("security venue_mic is not allowed")
    if values["currency"] not in settings.risk.allowed_currencies:
        raise ResearchStateError("security currency is not allowed")
    if len(values["research_summary"]) > 500:
        raise ResearchStateError("security research_summary exceeds 500 characters")
    values["research_page"] = _wiki_page(repository_root, values["research_page"], "securities")
    values["last_research_at"] = _canonical_timestamp(
        values["last_research_at"], label="last_research_at"
    )
    values["next_review_at"] = _canonical_timestamp(
        values["next_review_at"], label="next_review_at"
    )
    if values["next_review_at"] <= values["last_research_at"]:
        raise ResearchStateError("security next_review_at must follow last_research_at")
    rows = read_table(repository_root, "securities")
    previous = next((row for row in rows if row["security_id"] == values["security_id"]), None)
    if previous and any(previous[field] != values[field] for field in IMMUTABLE_SECURITY_FIELDS):
        raise ResearchStateError("security update conflicts with immutable identity")
    if (
        previous
        and previous["last_research_at"]
        and values["last_research_at"] < previous["last_research_at"]
    ):
        raise ResearchStateError("security update is older than current research state")
    identity = tuple(values[field] for field in IMMUTABLE_SECURITY_FIELDS)
    duplicate = next(
        (
            row
            for row in rows
            if row["security_id"] != values["security_id"]
            and tuple(row[field] for field in IMMUTABLE_SECURITY_FIELDS) == identity
        ),
        None,
    )
    if duplicate:
        raise ResearchStateError(f"security identity duplicates {duplicate['security_id']}")
    if previous and all(previous[field] == values[field] for field in input_columns):
        return False
    instant = format_timestamp(ensure_utc(now or utc_now()).replace(microsecond=0))
    row = {
        **values,
        "created_at": previous["created_at"] if previous else instant,
        "updated_at": instant,
    }
    return _replace_row(repository_root, "securities", row, key="security_id")


def upsert_relationship(
    repository_root: Path,
    raw: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> bool:
    """Insert or update one explicit idea-security causal edge."""

    columns = contract_by_name(repository_root, "relationships").columns
    input_columns = tuple(
        column for column in columns if column not in {"created_at", "updated_at"}
    )
    values = _exact_strings(raw, input_columns, label="relationship")
    _required(values, input_columns, label="relationship")
    for field in ("relationship_id", "idea_id", "security_id"):
        _identifier(values[field], label=field)
    if not any(
        row["security_id"] == values["security_id"]
        for row in read_table(repository_root, "securities")
    ):
        raise ResearchStateError("relationship references an unknown security_id")
    idea_page = repository_root / "data" / "wiki" / "ideas" / f"{values['idea_id']}.md"
    if idea_page.is_symlink() or not idea_page.is_file():
        raise ResearchStateError("relationship references an idea without its canonical wiki page")
    values["research_page"] = _wiki_page(repository_root, values["research_page"], "relationships")
    values["last_reviewed_at"] = _canonical_timestamp(
        values["last_reviewed_at"], label="last_reviewed_at"
    )
    values["next_review_at"] = _canonical_timestamp(
        values["next_review_at"], label="next_review_at"
    )
    if values["next_review_at"] <= values["last_reviewed_at"]:
        raise ResearchStateError("relationship next_review_at must follow last_reviewed_at")
    rows = read_table(repository_root, "relationships")
    previous = next(
        (row for row in rows if row["relationship_id"] == values["relationship_id"]), None
    )
    if previous and any(previous[field] != values[field] for field in ("idea_id", "security_id")):
        raise ResearchStateError("relationship update conflicts with immutable endpoints")
    if (
        previous
        and previous["last_reviewed_at"]
        and values["last_reviewed_at"] < previous["last_reviewed_at"]
    ):
        raise ResearchStateError("relationship update is older than current research state")
    duplicate = next(
        (
            row
            for row in rows
            if row["relationship_id"] != values["relationship_id"]
            and row["idea_id"] == values["idea_id"]
            and row["security_id"] == values["security_id"]
            and row["relationship_type"] == values["relationship_type"]
        ),
        None,
    )
    if duplicate:
        raise ResearchStateError(f"relationship duplicates {duplicate['relationship_id']}")
    if previous and all(previous[field] == values[field] for field in input_columns):
        return False
    instant = format_timestamp(ensure_utc(now or utc_now()).replace(microsecond=0))
    row = {
        **values,
        "created_at": previous["created_at"] if previous else instant,
        "updated_at": instant,
    }
    return _replace_row(repository_root, "relationships", row, key="relationship_id")


def _strategy_leg(raw: Mapping[str, object]) -> tuple[OrderLegSpec, str]:
    expected = {
        "leg_id",
        "action",
        "side",
        "instrument_type",
        "security_id",
        "provider_contract_id",
        "option_type",
        "expiry",
        "strike",
        "quantity",
        "contract_multiplier",
        "order_type",
        "limit_price",
        "currency",
    }
    if set(raw) != expected:
        raise ResearchStateError("strategy leg fields differ from the canonical contract")
    order_type = raw["order_type"]
    if order_type not in {"market", "limit"}:
        raise ResearchStateError("strategy leg order_type must be market or limit")
    order_raw = {key: value for key, value in raw.items() if key != "order_type"}
    try:
        leg = leg_from_mapping(order_raw)
    except (CanonicalValueError, RuntimeError, ValueError) as exc:
        raise ResearchStateError(str(exc)) from exc
    if order_type == "limit" and leg.limit_price is None:
        raise ResearchStateError("limit strategy leg requires limit_price")
    return leg, str(order_type)


def _strategy_leg_row(strategy_id: str, leg: OrderLegSpec, order_type: str) -> dict[str, str]:
    return {
        "strategy_id": strategy_id,
        "leg_id": leg.leg_id,
        "action": leg.action,
        "side": leg.side,
        "instrument_type": leg.instrument_type,
        "security_id": leg.security_id,
        "provider_contract_id": leg.provider_contract_id,
        "option_type": leg.option_type,
        "expiry": leg.expiry.isoformat() if leg.expiry else "",
        "strike": decimal_text(leg.strike) if leg.strike is not None else "",
        "quantity": decimal_text(leg.quantity),
        "contract_multiplier": decimal_text(leg.contract_multiplier),
        "order_type": order_type,
        "limit_price": decimal_text(leg.limit_price) if leg.limit_price is not None else "",
        "currency": leg.currency,
    }


def upsert_strategy(
    repository_root: Path,
    settings: Settings,
    raw: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> bool:
    """Upsert one evidence-linked strategy and its normalized deterministic legs."""

    if (
        set(raw) != {"strategy", "legs"}
        or not isinstance(raw["strategy"], dict)
        or not isinstance(raw["legs"], list)
    ):
        raise ResearchStateError("strategy request requires one strategy object and a legs array")
    columns = contract_by_name(repository_root, "strategies").columns
    input_columns = tuple(
        column for column in columns if column not in {"created_at", "updated_at"}
    )
    values = _exact_strings(raw["strategy"], input_columns, label="strategy")
    _required(
        values,
        tuple(column for column in input_columns if column not in {"not_before", "expires_at"}),
        label="strategy",
    )
    for field in ("strategy_id", "idea_id", "security_id", "relationship_id"):
        _identifier(values[field], label=field)
    if values["status"] not in STRATEGY_STATUSES:
        raise ResearchStateError("strategy status is not canonical")
    if values["instrument_type"] not in settings.risk.allowed_instruments:
        raise ResearchStateError("strategy instrument_type is not allowed")
    risk_budget = required_decimal(values["risk_budget_pct"], label="risk_budget_pct")
    if not Decimal("0") < risk_budget <= Decimal("100"):
        raise ResearchStateError("strategy risk_budget_pct must be within (0, 100]")
    values["risk_budget_pct"] = decimal_text(risk_budget)
    values["not_before"] = _canonical_timestamp(
        values["not_before"], label="not_before", allow_empty=True
    )
    values["expires_at"] = _canonical_timestamp(
        values["expires_at"], label="expires_at", allow_empty=True
    )
    if (
        values["not_before"]
        and values["expires_at"]
        and values["not_before"] >= values["expires_at"]
    ):
        raise ResearchStateError("strategy not_before must precede expires_at")
    relationship = next(
        (
            row
            for row in read_table(repository_root, "relationships")
            if row["relationship_id"] == values["relationship_id"]
        ),
        None,
    )
    if (
        relationship is None
        or relationship["idea_id"] != values["idea_id"]
        or relationship["security_id"] != values["security_id"]
    ):
        raise ResearchStateError("strategy identity does not match its relationship endpoints")
    values["research_page"] = _wiki_page(repository_root, values["research_page"], "strategies")
    raw_legs = raw["legs"]
    if not all(isinstance(value, dict) for value in raw_legs):
        raise ResearchStateError("every strategy leg must be an object")
    parsed = [_strategy_leg(value) for value in raw_legs if isinstance(value, dict)]
    if values["status"] in {"ready", "active"} and not parsed:
        raise ResearchStateError("ready or active strategy requires at least one normalized leg")
    leg_ids = [leg.leg_id for leg, _ in parsed]
    if len(leg_ids) != len(set(leg_ids)):
        raise ResearchStateError("strategy leg_id values must be unique")
    securities = {row["security_id"] for row in read_table(repository_root, "securities")}
    if any(leg.security_id not in securities for leg, _ in parsed):
        raise ResearchStateError("strategy leg references an unknown security")
    if any(
        leg.instrument_type not in settings.risk.allowed_instruments
        or leg.currency not in settings.risk.allowed_currencies
        for leg, _ in parsed
    ):
        raise ResearchStateError("strategy leg violates instrument or currency allowlists")
    rows = read_table(repository_root, "strategies")
    previous = next((row for row in rows if row["strategy_id"] == values["strategy_id"]), None)
    if previous and any(
        previous[field] != values[field] for field in ("idea_id", "security_id", "relationship_id")
    ):
        raise ResearchStateError("strategy update conflicts with immutable research identity")
    existing_legs = read_table(repository_root, "strategy_legs")
    leg_rows = [
        _strategy_leg_row(values["strategy_id"], leg, order_type) for leg, order_type in parsed
    ]
    leg_rows.sort(key=lambda candidate: (candidate["strategy_id"], candidate["leg_id"]))
    current_strategy_legs = [
        candidate
        for candidate in existing_legs
        if candidate["strategy_id"] == values["strategy_id"]
    ]
    if (
        previous
        and all(previous[field] == values[field] for field in input_columns)
        and current_strategy_legs == leg_rows
    ):
        return False
    instant = format_timestamp(ensure_utc(now or utc_now()).replace(microsecond=0))
    row = {
        **values,
        "created_at": previous["created_at"] if previous else instant,
        "updated_at": instant,
    }
    strategy_changed = _replace_row(repository_root, "strategies", row, key="strategy_id")
    output_legs = [
        candidate
        for candidate in existing_legs
        if candidate["strategy_id"] != values["strategy_id"]
    ]
    output_legs.extend(leg_rows)
    output_legs.sort(key=lambda candidate: (candidate["strategy_id"], candidate["leg_id"]))
    legs_changed = output_legs != existing_legs
    if legs_changed:
        write_table(repository_root, "strategy_legs", output_legs)
    return strategy_changed or legs_changed


def record_source(
    repository_root: Path,
    raw: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> tuple[str, bool]:
    """Record one source observation in the mutable registry and immutable history."""

    expected = (
        "source_id",
        "url",
        "canonical_url",
        "source_type",
        "title",
        "publisher",
        "license",
        "status",
        "content_hash",
        "related_entity_ids",
        "checked_at",
        "http_status",
        "changed",
        "excerpt",
        "summary",
        "run_id",
    )
    values = _exact_strings(raw, expected, label="source")
    _required(
        values,
        (
            "source_id",
            "url",
            "canonical_url",
            "source_type",
            "title",
            "publisher",
            "status",
            "content_hash",
            "checked_at",
            "changed",
            "summary",
            "run_id",
        ),
        label="source",
    )
    _identifier(values["source_id"], label="source_id")
    for field in ("url", "canonical_url"):
        parsed = urlsplit(values[field])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ResearchStateError(f"source {field} must be an HTTP(S) URL")
    if not re.fullmatch(r"[a-f0-9]{64}", values["content_hash"]):
        raise ResearchStateError("source content_hash must be lowercase SHA-256")
    if values["changed"] not in {"true", "false"}:
        raise ResearchStateError("source changed must be true or false")
    if len(values["excerpt"]) > 1000 or len(values["summary"]) > 2000:
        raise ResearchStateError("source excerpt or summary exceeds its bounded length")
    checked = _canonical_timestamp(values["checked_at"], label="checked_at")
    instant = format_timestamp(ensure_utc(now or utc_now()).replace(microsecond=0))
    registry = read_table(repository_root, "source_registry")
    previous = next((row for row in registry if row["source_id"] == values["source_id"]), None)
    if previous and previous["canonical_url"] != values["canonical_url"]:
        raise ResearchStateError("source update conflicts with immutable canonical_url")
    if previous and checked < previous["last_checked_at"]:
        raise ResearchStateError("source observation is older than the current registry state")
    registry_row = {
        "source_id": values["source_id"],
        "url": values["url"],
        "canonical_url": values["canonical_url"],
        "source_type": values["source_type"],
        "title": values["title"],
        "publisher": values["publisher"],
        "license": values["license"],
        "status": values["status"],
        "content_hash": values["content_hash"],
        "first_seen_at": previous["first_seen_at"] if previous else instant,
        "last_checked_at": checked,
        "last_changed_at": (
            checked
            if values["changed"] == "true"
            else (previous["last_changed_at"] if previous else "")
        ),
        "related_entity_ids": values["related_entity_ids"],
    }
    history_id = stable_id("source_history", values["source_id"], checked, values["content_hash"])
    history_row = {
        "source_history_id": history_id,
        "source_id": values["source_id"],
        "checked_at": checked,
        "status": values["status"],
        "http_status": values["http_status"],
        "content_hash": values["content_hash"],
        "changed": values["changed"],
        "excerpt": values["excerpt"],
        "summary": values["summary"],
        "run_id": values["run_id"],
    }
    previous_history = next(
        (
            row
            for row in read_table(repository_root, "source_history")
            if row["source_history_id"] == history_id
        ),
        None,
    )
    if previous_history is not None and previous_history != history_row:
        raise ResearchStateError(f"source history identity collision: {history_id}")
    registry_changed = _replace_row(
        repository_root, "source_registry", registry_row, key="source_id"
    )
    appended = append_unique(
        repository_root,
        "source_history",
        [history_row],
        key_columns=("source_history_id",),
    )
    return history_id, registry_changed or bool(appended)


__all__ = [
    "ResearchStateError",
    "record_source",
    "upsert_relationship",
    "upsert_security",
    "upsert_strategy",
]
