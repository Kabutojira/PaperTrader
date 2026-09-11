from __future__ import annotations

from datetime import timedelta

import pytest
from test_evidence import NOW, claim_fixture

from papertrader.evidence import record_claim
from papertrader.governance import GovernanceError
from papertrader.research_calendar import (
    catalyst_records,
    occurrence_window,
    record_catalyst,
    register_forecast,
)


def event(source_id):
    return {
        "event_id": "quarterly_results",
        "occurrence_key": "2026Q3",
        "security_id": "sec_a",
        "status": "scheduled",
        "precision": "date",
        "scheduled_at": None,
        "expected_date": "2026-10-25",
        "expected_month": None,
        "timezone": "Europe/Rome",
        "source_history_id": source_id,
        "summary": "Expected issuer results; occurrence is not yet confirmed.",
    }


def test_date_precision_preserves_dst_and_unknown_time(sandbox_repository):
    claim = claim_fixture(sandbox_repository)
    value = event(claim["evidence"][0]["source_history_id"])
    start, end = occurrence_window(value)
    assert end - start == timedelta(hours=25)
    value.update(precision="unknown", expected_date=None)
    assert occurrence_window(value) == (None, None)


def test_reschedule_and_cancellation_keep_occurrence_identity(sandbox_repository):
    claim = claim_fixture(sandbox_repository)
    value = event(claim["evidence"][0]["source_history_id"])
    first = record_catalyst(sandbox_repository, value, now=NOW)
    occurrence = next(iter(catalyst_records(sandbox_repository)))
    value.update(status="rescheduled", expected_date="2026-10-26")
    second = record_catalyst(sandbox_repository, value, now=NOW + timedelta(hours=1))
    assert first != second and list(catalyst_records(sandbox_repository)) == [occurrence]
    value["status"] = "cancelled"
    record_catalyst(sandbox_repository, value, now=NOW + timedelta(hours=2))
    assert catalyst_records(sandbox_repository)[occurrence]["event"]["status"] == "cancelled"


def test_forecast_is_frozen_before_horizon_and_keeps_rejected_candidates(sandbox_repository):
    claim = claim_fixture(sandbox_repository)
    version = record_claim(sandbox_repository, claim, operation_id="fixture", now=NOW)
    forecast = {
        "forecast_id": "orders_decline",
        "security_id": "sec_a",
        "event_definition": "Reported organic orders decline in the stated quarter.",
        "horizon_at": "2026-10-31T23:59:59Z",
        "probability": "0.3",
        "claim_version_ids": [version],
        "candidate_disposition": "rejected_unattractive_valuation",
        "limitations": "Not an intrinsic fair value or a market price target.",
    }
    assert register_forecast(sandbox_repository, forecast, now=NOW) == "orders_decline"
    forecast["probability"] = "0.9"
    with pytest.raises(GovernanceError, match="cannot be rewritten"):
        register_forecast(sandbox_repository, forecast, now=NOW + timedelta(days=2))
    forecast["forecast_id"] = "late_forecast"
    with pytest.raises(GovernanceError, match="before"):
        register_forecast(sandbox_repository, forecast, now=NOW + timedelta(days=200))
