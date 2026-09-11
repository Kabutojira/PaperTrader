from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest
from test_execution_accounting import _security_row

from papertrader.evidence import (
    claim_diagnostics,
    claims,
    material_claim,
    record_claim,
    validate_claim,
    validate_evidence_state,
    validate_schema,
)
from papertrader.governance import GovernanceError
from papertrader.research import record_source
from papertrader.tables import write_table

NOW = datetime(2026, 7, 24, 12, tzinfo=UTC)


def claim_fixture(root):
    write_table(root, "securities", [_security_row()])
    source_id, _ = record_source(
        root,
        {
            "source_id": "source_primary",
            "url": "https://example.test/filing",
            "canonical_url": "https://example.test/filing",
            "source_type": "filing",
            "title": "Issuer results",
            "publisher": "Issuer",
            "license": "public-record",
            "status": "available",
            "content_hash": "a" * 64,
            "related_entity_ids": "sec_a",
            "checked_at": "2026-07-24T12:00:00Z",
            "http_status": "200",
            "changed": "true",
            "excerpt": "Segment revenue increased ten percent in fiscal 2025.",
            "summary": "Original synthesis of revenue change.",
            "run_id": "fixture",
        },
        now=NOW,
    )
    return {
        "claim_id": "claim_revenue",
        "security_ids": ["sec_a"],
        "proposition": "Issuer reported ten percent segment revenue growth in fiscal 2025.",
        "state": "supported",
        "kind": "financial",
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
        "unit": "percent",
        "currency": "",
        "scope": "named operating segment",
        "basis": "issuer GAAP period comparison",
        "assumption_ids": ["demand_growth"],
        "assessment_ids": [],
        "uncertainty": "Future growth is not demonstrated by historical results.",
        "evidence": [
            {
                "source_history_id": source_id,
                "locator": "Revenue table, segment row",
                "excerpt": "Segment revenue increased ten percent in fiscal 2025.",
                "role": "supports",
                "rationale": "The table directly reports the historical percentage change.",
                "origin_id": "issuer:results-2025",
                "origin_type": "issuer",
                "underlying_observation_id": "issuer:segment:2025",
                "published_at": "2026-02-01T12:00:00Z",
                "inspected_at": "2026-07-24T12:00:00Z",
                "inspection_status": "observed",
                "applicability_limit": "Not a forecast of 2026 growth.",
            }
        ],
    }


def test_claim_requires_actual_retained_inspection_not_plausible_source_id(sandbox_repository):
    claim = claim_fixture(sandbox_repository)
    validate_claim(sandbox_repository, claim, now=NOW)
    claim["evidence"][0]["excerpt"] = "Revenue doubled without any qualification."
    with pytest.raises(GovernanceError, match="retained inspected"):
        validate_claim(sandbox_repository, claim, now=NOW)


def test_syndicated_issuer_claims_are_one_origin(sandbox_repository):
    claim = claim_fixture(sandbox_repository)
    claim["evidence"] = [deepcopy(claim["evidence"][0]) for _ in range(10)]
    record_claim(sandbox_repository, claim, operation_id="fixture", now=NOW)
    assert claim_diagnostics(sandbox_repository)["independent_origins_by_claim"][
        "claim_revenue"
    ] == ["issuer:results-2025"]


def test_retrieval_does_not_change_observation_period_or_material_support(sandbox_repository):
    claim = claim_fixture(sandbox_repository)
    refreshed = deepcopy(claim)
    refreshed["evidence"][0]["inspected_at"] = "2026-07-25T12:00:00Z"
    assert material_claim(claim) == material_claim(refreshed)
    assert refreshed["period_end"] == "2025-12-31"
    validate_claim(sandbox_repository, refreshed, now=NOW + timedelta(days=1))
    with pytest.raises(GovernanceError, match="future"):
        validate_claim(sandbox_repository, refreshed, now=NOW)


def test_correction_is_append_only_and_changes_material_version(sandbox_repository):
    claim = claim_fixture(sandbox_repository)
    first = record_claim(sandbox_repository, claim, operation_id="first", now=NOW)
    original_material = claims(sandbox_repository)["claim_revenue"]["material_hash"]
    claim["state"] = "disputed"
    claim["uncertainty"] = "Period definitions may differ; investigate a restatement."
    second = record_claim(
        sandbox_repository, claim, operation_id="correction", now=NOW + timedelta(hours=1)
    )
    row = claims(sandbox_repository)["claim_revenue"]
    assert first != second and row["previous_version_id"] == first
    assert row["material_hash"] != original_material
    assert (
        sandbox_repository / f"data/operations/research-governance/claims/{first}.json"
    ).exists()
    assert validate_evidence_state(sandbox_repository) == []


def test_unknown_or_summary_origin_cannot_claim_supported(sandbox_repository):
    claim = claim_fixture(sandbox_repository)
    claim["evidence"][0]["origin_type"] = "research_summary"
    with pytest.raises(GovernanceError, match="original evidence"):
        validate_claim(sandbox_repository, claim, now=NOW)
    claim["state"] = "hypothesis"
    validate_claim(sandbox_repository, claim, now=NOW)


def test_searched_challenge_requires_inspections(sandbox_repository):
    challenge = {
        "status": "searched",
        "favored_hypothesis": "Growth persists",
        "strongest_alternative": "Temporary restocking",
        "falsification_condition": "Organic orders decline",
        "inspection_refs": [],
        "contrary_evidence": [],
        "blind_spots": ["No customer-level data"],
        "effect_on_conclusion": "Retain uncertainty",
        "reason": "Review strongest alternative",
    }
    with pytest.raises(GovernanceError):
        validate_schema(sandbox_repository, "research_challenge", challenge)
    challenge["status"] = "partial"
    validate_schema(sandbox_repository, "research_challenge", challenge)
