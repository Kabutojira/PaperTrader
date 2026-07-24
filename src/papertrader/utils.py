"""Pure helpers for canonical time, decimal, hashing, and stable identities."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Final

CROCKFORD32: Final = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
ULID_PATTERN: Final = re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")
ZERO: Final = Decimal("0")
ONE_HUNDRED: Final = Decimal("100")


class CanonicalValueError(ValueError):
    """Raised when external state is not in a canonical form."""


def utc_now() -> datetime:
    """Return a timezone-aware current UTC timestamp."""

    return datetime.now(UTC)


def ensure_utc(value: datetime) -> datetime:
    """Normalize an aware timestamp to UTC and reject ambiguous naive values."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise CanonicalValueError("timestamp must include a timezone")
    return value.astimezone(UTC)


def parse_timestamp(value: str, *, allow_empty: bool = False) -> datetime | None:
    """Parse one ISO-8601 timestamp and require an explicit UTC offset."""

    if not value:
        if allow_empty:
            return None
        raise CanonicalValueError("timestamp is required")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise CanonicalValueError(f"invalid ISO-8601 timestamp: {value}") from exc
    return ensure_utc(parsed)


def format_timestamp(value: datetime) -> str:
    """Render a UTC timestamp with seconds and a trailing ``Z``."""

    normalized = ensure_utc(value).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def parse_iso_date(value: str) -> date:
    """Parse a canonical ISO date."""

    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise CanonicalValueError(f"invalid ISO date: {value}") from exc
    if parsed.isoformat() != value:
        raise CanonicalValueError(f"date is not canonical: {value}")
    return parsed


def decimal_value(
    value: str | int | Decimal,
    *,
    label: str = "value",
    allow_empty: bool = False,
) -> Decimal | None:
    """Convert text or an integer to a finite Decimal without binary floats."""

    if value == "" and allow_empty:
        return None
    if isinstance(value, float):
        raise CanonicalValueError(f"{label} must not be a binary float")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise CanonicalValueError(f"{label} must be a decimal: {value!r}") from exc
    if not result.is_finite():
        raise CanonicalValueError(f"{label} must be finite")
    return result


def required_decimal(value: str | int | Decimal, *, label: str = "value") -> Decimal:
    """Typed convenience wrapper for required decimals."""

    result = decimal_value(value, label=label)
    assert result is not None
    return result


def decimal_text(value: Decimal, *, places: int | None = None) -> str:
    """Render a finite Decimal without exponent notation or negative zero."""

    if not value.is_finite():
        raise CanonicalValueError("cannot serialize a non-finite decimal")
    normalized = value
    if places is not None:
        normalized = value.quantize(Decimal(1).scaleb(-places))
    if normalized == ZERO:
        normalized = ZERO
    rendered = format(normalized, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def canonical_json(value: object) -> str:
    """Serialize JSON in the stable form used for hashes and dedupe keys."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def content_hash(value: str | bytes | object) -> str:
    """Return a lowercase SHA-256 content hash."""

    if isinstance(value, bytes):
        payload = value
    elif isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def stable_id(prefix: str, *parts: object, length: int = 20) -> str:
    """Create a readable immutable ID from canonical identity components."""

    if not prefix or not re.fullmatch(r"[a-z][a-z0-9_]*", prefix):
        raise CanonicalValueError(f"invalid ID prefix: {prefix!r}")
    digest = content_hash([str(part) for part in parts])[:length]
    return f"{prefix}_{digest}"


def _base32(number: int, width: int) -> str:
    characters = ["0"] * width
    for index in range(width - 1, -1, -1):
        characters[index] = CROCKFORD32[number & 31]
        number >>= 5
    if number:
        raise CanonicalValueError("number exceeds encoded width")
    return "".join(characters)


def deterministic_ulid(timestamp: datetime, *identity_parts: object) -> str:
    """Build a deterministic ULID using time plus an 80-bit identity hash."""

    instant = ensure_utc(timestamp)
    milliseconds = int(instant.timestamp() * 1000)
    if milliseconds < 0 or milliseconds >= 2**48:
        raise CanonicalValueError("timestamp is outside the ULID range")
    digest = hashlib.sha256(
        canonical_json([str(part) for part in identity_parts]).encode()
    ).digest()
    randomness = int.from_bytes(digest[:10], "big")
    return _base32(milliseconds, 10) + _base32(randomness, 16)


def validate_ulid(value: str) -> None:
    """Reject malformed operation identities."""

    if not ULID_PATTERN.fullmatch(value):
        raise CanonicalValueError(f"invalid ULID: {value!r}")


def require_columns(row: Mapping[str, object], columns: Sequence[str], *, label: str) -> None:
    """Require exactly the canonical field names in one structured row."""

    actual = set(row)
    expected = set(columns)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise CanonicalValueError(f"{label} fields differ; missing={missing}, extra={extra}")


def require_choice(value: str, choices: set[str] | frozenset[str], *, label: str) -> str:
    """Return a value only when it belongs to the explicit allowlist."""

    if value not in choices:
        raise CanonicalValueError(f"{label} must be one of {sorted(choices)}, got {value!r}")
    return value
