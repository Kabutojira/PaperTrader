"""Claim-specific evidence revisions, origin dependence, and correction impacts.

Diagnostics do not change financial thresholds or manufacture historical inspection.
The trusted parent accepts these records after the operation's result is validated.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jsonschema import Draft202012Validator, FormatChecker

from papertrader.atomic_io import atomic_write_json
from papertrader.governance import ROOT, GovernanceError, load_record
from papertrader.tables import read_table
from papertrader.utils import content_hash, format_timestamp, parse_timestamp, utc_now

if TYPE_CHECKING:
    from papertrader.config import Settings
    from papertrader.queue import Operation


def validate_schema(root: Path, name: str, value: Mapping[str, Any]) -> None:
    validator = Draft202012Validator(
        load_record(root, root / f"schemas/{name}.schema.json"), format_checker=FormatChecker()
    )
    errors = list(validator.iter_errors(value))
    if errors:
        raise GovernanceError("; ".join(error.message for error in errors))


def claims(root: Path, *, as_of: datetime | None = None) -> dict[str, dict[str, Any]]:
    records = [load_record(root, path) for path in sorted((root / ROOT / "claims").glob("*.json"))]
    current: dict[str, dict[str, Any]] = {}
    visible: dict[str, dict[str, Any]] = {}
    pending = {row["version_id"]: row for row in records}
    while pending:
        progressed = False
        for version_id, row in list(pending.items()):
            previous = current.get(row["claim"]["claim_id"])
            if row["previous_version_id"] != (previous["version_id"] if previous else ""):
                continue
            if (
                content_hash({key: value for key, value in row.items() if key != "version_id"})
                != version_id
            ):
                raise GovernanceError("claim revision hash mismatch")
            current[row["claim"]["claim_id"]] = row
            recorded = parse_timestamp(row["recorded_at"])
            if as_of is None or (recorded is not None and recorded <= as_of):
                visible[row["claim"]["claim_id"]] = row
            del pending[version_id]
            progressed = True
        if not progressed:
            raise GovernanceError("claim history has a missing predecessor or fork")
    return visible


def validate_claim(root: Path, claim: Mapping[str, Any], *, now: datetime) -> None:
    validate_schema(root, "research_claim", claim)
    securities = {row["security_id"] for row in read_table(root, "securities")}
    if not set(claim["security_ids"]) <= securities:
        raise GovernanceError("claim references an unknown immutable security")
    assessments = {
        row["assessment_id"]: row for row in read_table(root, "security_assessment_history")
    }
    if any(
        key not in assessments or assessments[key]["security_id"] not in claim["security_ids"]
        for key in claim["assessment_ids"]
    ):
        raise GovernanceError("claim references a missing or unrelated assessment version")
    if (
        claim["period_start"]
        and claim["period_end"]
        and claim["period_start"] > claim["period_end"]
    ):
        raise GovernanceError("claim observation period is reversed")
    history = {row["source_history_id"]: row for row in read_table(root, "source_history")}
    inspected_support = False
    for evidence in claim["evidence"]:
        source = history.get(evidence["source_history_id"])
        if source is None:
            raise GovernanceError(
                "claim requires an immutable source observation, not source ID existence"
            )
        inspected = parse_timestamp(evidence["inspected_at"])
        retrieved = parse_timestamp(source["checked_at"])
        published = parse_timestamp(evidence["published_at"]) if evidence["published_at"] else None
        if (
            inspected is None
            or retrieved is None
            or not retrieved <= inspected <= now
            or (published and published > inspected)
        ):
            raise GovernanceError("claim evidence has unavailable or future inspection provenance")
        excerpt = evidence["excerpt"]
        if len(excerpt.split()) > 25:
            raise GovernanceError("claim excerpt exceeds the bounded public-source quote allowance")
        observed = evidence["inspection_status"] == "observed"
        if observed and (not excerpt or excerpt not in source["excerpt"]):
            raise GovernanceError(
                "observed claim support must match the retained inspected source excerpt"
            )
        if (
            observed
            and evidence["role"] == "supports"
            and evidence["origin_type"] not in {"unknown", "research_summary"}
        ):
            inspected_support = True
    if claim["state"] == "supported" and not inspected_support:
        raise GovernanceError("supported claim lacks inspected, applicable original evidence")


def material_claim(claim: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **{key: value for key, value in claim.items() if key not in {"assessment_ids", "evidence"}},
        "evidence": [
            {
                key: value
                for key, value in evidence.items()
                if key not in {"source_history_id", "inspected_at"}
            }
            for evidence in claim["evidence"]
        ],
    }


def record_claim(
    root: Path, claim: Mapping[str, Any], *, operation_id: str, now: datetime | None = None
) -> str:
    instant = now or utc_now()
    validate_claim(root, claim, now=instant)
    previous = claims(root).get(claim["claim_id"])
    if previous and previous["claim"] == claim:
        return str(previous["version_id"])
    record = {
        "schema_version": 1,
        "claim": dict(claim),
        "material_hash": content_hash(material_claim(claim)),
        "previous_version_id": previous["version_id"] if previous else "",
        "recorded_at": format_timestamp(instant),
        "source_operation_id": operation_id,
    }
    version_id = content_hash(record)
    path = root / ROOT / "claims" / f"{version_id}.json"
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise GovernanceError("claim destination traverses a symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, {**record, "version_id": version_id}, allowed_root=root)
    return version_id


def material_claims(root: Path, security_ids: set[str]) -> list[dict[str, Any]]:
    return [
        {
            "claim_id": key,
            "material_hash": row["material_hash"],
            "claim": material_claim(row["claim"]),
        }
        for key, row in sorted(claims(root).items())
        if set(row["claim"]["security_ids"]) & security_ids
    ]


def claim_diagnostics(root: Path, *, as_of: datetime | None = None) -> dict[str, Any]:
    indexed = claims(root, as_of=as_of)
    origin_groups: dict[str, list[str]] = {}
    assumptions: dict[str, set[str]] = {}
    for claim_id, row in indexed.items():
        claim = row["claim"]
        origins = {
            item["origin_id"]
            for item in claim["evidence"]
            if item["origin_type"] not in {"unknown", "research_summary"}
        }
        origin_groups[claim_id] = sorted(origins)
        for assumption in claim["assumption_ids"]:
            assumptions.setdefault(assumption, set()).update(claim["security_ids"])
    return {
        "quality_mode": "candidate_scoped_diagnostic",
        "claim_count": len(indexed),
        "independent_origins_by_claim": origin_groups,
        "shared_assumption_security_ids": {
            key: sorted(ids) for key, ids in assumptions.items() if len(ids) > 1
        },
    }


def accept_claims(
    root: Path,
    settings: Settings,
    operation: Operation,
    values: Sequence[Mapping[str, Any]],
    *,
    now: datetime,
) -> None:
    from papertrader.queue import enqueue_operation

    previous = claims(root)
    for claim in values:
        validate_claim(root, claim, now=now)
    for claim in values:
        old = previous.get(claim["claim_id"])
        version_id = record_claim(root, claim, operation_id=operation.operation_id, now=now)
        if old and old["material_hash"] != content_hash(material_claim(claim)):
            for security_id in sorted(
                set(claim["security_ids"]) | set(old["claim"]["security_ids"])
            ):
                if operation.entity_type == "security" and security_id == operation.entity_id:
                    continue
                enqueue_operation(
                    root,
                    settings,
                    operation_type="security_research",
                    entity_type="security",
                    entity_id=security_id,
                    dedupe_key=f"claim-correction:{claim['claim_id']}:{version_id}:{security_id}",
                    prompt=(
                        "Review the scoped impact of a material claim correction; "
                        "preserve prior conclusions and uncertainty."
                    ),
                    inputs={
                        "security_id": security_id,
                        "claim_id": claim["claim_id"],
                        "claim_version_id": version_id,
                        "previous_claim_version_id": old["version_id"],
                    },
                    source="controller:claim-correction",
                    depends_on=(operation.operation_id,),
                    priority=96,
                    freshness_days=0,
                    now=now,
                )


def validate_evidence_state(root: Path) -> list[str]:
    try:
        for row in claims(root).values():
            recorded = parse_timestamp(row["recorded_at"])
            if recorded is None:
                raise GovernanceError("claim lacks acceptance time")
            validate_claim(root, row["claim"], now=recorded)
            if content_hash(material_claim(row["claim"])) != row["material_hash"]:
                raise GovernanceError("claim material hash mismatch")
        return []
    except (GovernanceError, KeyError, ValueError, TypeError, OSError) as exc:
        return [f"research_evidence: {exc}"]
