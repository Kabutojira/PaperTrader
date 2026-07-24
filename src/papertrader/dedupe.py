"""Pure operation-key, freshness-bucket, and semantic-disposition contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

from papertrader.utils import CanonicalValueError, content_hash, ensure_utc

DEDUPE_COMPONENT = re.compile(r"^[A-Za-z0-9_.-]+$")
SEMANTIC_DISPOSITIONS = frozenset({"execute", "merge", "defer", "skip"})


def freshness_bucket(value: date | datetime, freshness_days: int) -> str:
    """Return a stable date bucket for catalyst/source-aware dedupe keys."""

    if freshness_days <= 0:
        raise CanonicalValueError("freshness_days must be positive")
    day = ensure_utc(value).date() if isinstance(value, datetime) else value
    bucket_start = date.fromordinal(day.toordinal() - (day.toordinal() % freshness_days))
    return bucket_start.isoformat()


def source_fingerprint(value: str | bytes | object) -> str:
    """Return the compact source/catalyst hash component used in operation keys."""

    return content_hash(value)[:20]


def build_dedupe_key(
    operation_type: str,
    entity_id: str,
    catalyst_or_source_hash: str,
    bucket: str,
) -> str:
    """Build and validate the recommended four-part deterministic key."""

    parts = (operation_type, entity_id, catalyst_or_source_hash, bucket)
    if any(not part or not DEDUPE_COMPONENT.fullmatch(part) for part in parts):
        raise CanonicalValueError(f"invalid dedupe-key component in {parts!r}")
    key = ":".join(parts)
    if len(key) > 500:
        raise CanonicalValueError("dedupe key exceeds 500 characters")
    return key


@dataclass(frozen=True, slots=True)
class SemanticDisposition:
    """Closed cheap-model overlap-review result."""

    decision: str
    reason: str
    target_operation_id: str = ""

    def validate(self) -> None:
        if self.decision not in SEMANTIC_DISPOSITIONS:
            raise CanonicalValueError(
                f"semantic decision must be one of {sorted(SEMANTIC_DISPOSITIONS)}"
            )
        if not self.reason.strip() or len(self.reason) > 500:
            raise CanonicalValueError("semantic reason must contain 1 to 500 characters")
        if self.decision == "merge" and not self.target_operation_id:
            raise CanonicalValueError("merge disposition requires target_operation_id")
        if self.decision != "merge" and self.target_operation_id:
            raise CanonicalValueError("only merge may specify target_operation_id")


class SemanticOverlapReviewer(Protocol):
    """Optional cheap-model boundary used only after exact queue rules are exhausted."""

    def review(
        self, candidate: dict[str, str], existing: tuple[dict[str, str], ...]
    ) -> SemanticDisposition:
        """Return execute, merge, defer, or skip with a reason."""
