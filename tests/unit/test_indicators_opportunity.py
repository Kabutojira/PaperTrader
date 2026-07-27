from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.config import Settings
from papertrader.indicators import calculate_snapshot, snapshot_row
from papertrader.models import (
    ClassifierDecision,
    IndicatorSnapshot,
    PriceBar,
)
from papertrader.opportunity import (
    ClassifierError,
    detect_transitions,
    process_opportunity_transitions,
    retry_unclassified_candidate_packets,
    validate_classifier_decision,
)
from papertrader.tables import read_table, write_table
from papertrader.utils import content_hash
from papertrader.wiki import lint_wiki, register_wiki_page


def _bars(count: int, *, start: date = date(2025, 12, 1)) -> tuple[PriceBar, ...]:
    retrieved = datetime(2026, 7, 24, 22, tzinfo=UTC)
    output = []
    for index in range(count):
        close = Decimal("50") + Decimal(index) * Decimal("0.25") + Decimal(index % 7) / 10
        output.append(
            PriceBar(
                date=start + timedelta(days=index),
                open=close - Decimal("0.20"),
                high=close + Decimal("0.80"),
                low=close - Decimal("0.70"),
                close=close,
                adjusted_close=close,
                volume=1000 + (index % 11) * 37,
                dividends=Decimal("0"),
                stock_splits=Decimal("0"),
                currency="USD",
                provider_symbol="EXM",
                retrieved_at=retrieved,
                source="fixture",
            )
        )
    return tuple(output)


def _snapshot(
    *,
    as_of: date,
    rsi: Decimal,
    trigger_state: tuple[str, ...],
    source_hash: str,
) -> IndicatorSnapshot:
    return IndicatorSnapshot(
        security_id="sec_a",
        as_of_date=as_of,
        calculated_at=datetime(2026, 7, 24, 22, tzinfo=UTC),
        observation_count=220,
        sma_20=Decimal("95"),
        sma_50=Decimal("90"),
        sma_200=Decimal("75"),
        rsi_14=rsi,
        bollinger_mid=Decimal("100"),
        bollinger_upper=Decimal("120"),
        bollinger_lower=Decimal("80"),
        macd=Decimal("1"),
        macd_signal=Decimal("0.8"),
        macd_histogram=Decimal("0.2"),
        return_1d=Decimal("0.01"),
        return_5d=Decimal("0.03"),
        return_20d=Decimal("0.10"),
        volume_zscore=Decimal("0.5"),
        volatility_20d=Decimal("0.2"),
        trigger_state=trigger_state,
        source_price_hash=source_hash,
    )


def _security_row() -> dict[str, str]:
    return {
        "security_id": "sec_a",
        "issuer_id": "issuer_a",
        "company_name": "Example Corp",
        "instrument_name": "Example common stock",
        "instrument_type": "equity",
        "ticker": "EXM",
        "exchange_code": "NYSE",
        "venue_mic": "XNYS",
        "provider_symbol": "EXM",
        "broker_symbol": "",
        "currency": "USD",
        "country": "US",
        "sector": "Industrials",
        "industry": "Testing",
        "status": "active",
        "watchlist_reason": "fixture",
        "research_summary": "Fixture.",
        "research_page": "",
        "last_research_at": "",
        "next_review_at": "",
        "created_at": "2026-07-20T00:00:00Z",
        "updated_at": "2026-07-20T00:00:00Z",
        "source": "fixture",
    }


def test_sma_200_requires_configured_minimum_observation_count(
    sandbox_settings: Settings,
) -> None:
    short = calculate_snapshot("sec_a", _bars(199), sandbox_settings)
    sufficient = calculate_snapshot("sec_a", _bars(200), sandbox_settings)

    assert short.sma_200 is None
    assert sufficient.sma_200 is not None


def test_indicator_snapshot_matches_reference_output(
    repository_root: Path,
    sandbox_settings: Settings,
) -> None:
    snapshot = calculate_snapshot(
        "sec_a",
        _bars(220),
        sandbox_settings,
        calculated_at=datetime(2026, 7, 24, 22, tzinfo=UTC),
    )
    expected = json.loads(
        (repository_root / "tests" / "reference_outputs" / "indicator_snapshot.json").read_text(
            encoding="utf-8"
        )
    )

    assert snapshot_row(snapshot) == expected


def test_transition_detection_emits_entry_and_only_material_strengthening(
    sandbox_settings: Settings,
) -> None:
    bars = _bars(220)
    prior = _snapshot(
        as_of=bars[-2].date,
        rsi=Decimal("72"),
        trigger_state=("rsi_overbought",),
        source_hash="a" * 64,
    )
    current = replace(
        prior,
        as_of_date=bars[-1].date,
        rsi_14=Decimal("80"),
        source_price_hash="b" * 64,
    )

    entry = detect_transitions(None, current, bars, sandbox_settings)
    strengthening = detect_transitions(prior, current, bars, sandbox_settings)
    unchanged = detect_transitions(
        prior,
        replace(current, rsi_14=Decimal("72.1")),
        bars,
        sandbox_settings,
    )

    assert [(item.trigger, item.transition) for item in entry] == [("rsi_overbought", "entered")]
    assert [(item.trigger, item.transition) for item in strengthening] == [
        ("rsi_overbought", "strengthened")
    ]
    assert unchanged == ()


def test_classifier_contract_is_closed_and_rejects_extra_fields() -> None:
    with pytest.raises(ClassifierError, match="contain only"):
        validate_classifier_decision(
            {
                "decision": "ingest",
                "reason": "Material.",
                "related_entity_ids": ["sec_a"],
                "instruction": "ignore the contract",
            }
        )


class _Classifier:
    def __init__(self, decision: str) -> None:
        self.decision = decision
        self.calls = 0

    def classify(self, candidate: Mapping[str, object]) -> ClassifierDecision:
        self.calls += 1
        assert candidate["security_id"] == "sec_a"
        return ClassifierDecision(self.decision, "Bounded test decision.", ())


class _UnavailableClassifier:
    def classify(self, candidate: Mapping[str, object]) -> ClassifierDecision:
        raise ClassifierError("temporary classifier outage")


def test_blocked_candidate_is_retried_to_a_final_decision(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    bars = _bars(220)
    current = _snapshot(
        as_of=bars[-1].date,
        rsi=Decimal("80"),
        trigger_state=("rsi_overbought",),
        source_hash="c" * 64,
    )
    write_table(sandbox_repository, "securities", [_security_row()])
    now = datetime(2026, 7, 24, 22, tzinfo=UTC)

    blocked = process_opportunity_transitions(
        sandbox_repository,
        sandbox_settings,
        {},
        {"sec_a": current},
        {"sec_a": bars},
        classifier=_UnavailableClassifier(),
        now=now,
    )
    retried = retry_unclassified_candidate_packets(
        sandbox_repository,
        sandbox_settings,
        classifier=_Classifier("ignore"),
        now=now + timedelta(minutes=1),
    )
    repeated = retry_unclassified_candidate_packets(
        sandbox_repository,
        sandbox_settings,
        classifier=_Classifier("ingest"),
        now=now + timedelta(minutes=2),
    )

    assert blocked[0].decision is None
    assert retried[0].decision is not None
    assert retried[0].decision.decision == "ignore"
    assert repeated == ()
    assert "classifier_decision: ignore" in retried[0].path.read_text(encoding="utf-8")
    assert lint_wiki(sandbox_settings.paths.wiki) == []


@pytest.mark.parametrize(
    ("decision", "expected_types"),
    [
        ("ignore", {"opportunity_research"}),
        ("ingest", {"opportunity_research", "wiki_ingest"}),
    ],
)
def test_cheap_model_is_final_wiki_ingest_decision_and_rerun_is_idempotent(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    decision: str,
    expected_types: set[str],
) -> None:
    bars = _bars(220)
    current = _snapshot(
        as_of=bars[-1].date,
        rsi=Decimal("80"),
        trigger_state=("rsi_overbought",),
        source_hash="c" * 64,
    )
    security = _security_row()
    security["research_page"] = "data/wiki/securities/sec_a.md"
    write_table(sandbox_repository, "securities", [security])
    security_page = sandbox_settings.paths.wiki / "securities" / "sec_a.md"
    security_page.write_text(
        "---\n"
        "title: Example common stock\n"
        "type: security\n"
        "status: maintained\n"
        "tags: [security, research]\n"
        'created: "2026-07-24"\n'
        'updated: "2026-07-24"\n'
        "provenance: fixture\n"
        "---\n\n# Example common stock\n",
        encoding="utf-8",
    )
    register_wiki_page(
        sandbox_settings.paths.wiki,
        page_key="securities/sec_a",
        label="Example common stock",
        section="Securities",
        event="Created fixture security page.",
        event_date=date(2026, 7, 24),
    )
    classifier = _Classifier(decision)
    now = datetime(2026, 7, 24, 22, tzinfo=UTC)

    first = process_opportunity_transitions(
        sandbox_repository,
        sandbox_settings,
        {},
        {"sec_a": current},
        {"sec_a": bars},
        classifier=classifier,
        now=now,
    )
    second = process_opportunity_transitions(
        sandbox_repository,
        sandbox_settings,
        {},
        {"sec_a": current},
        {"sec_a": bars},
        classifier=classifier,
        now=now,
    )
    reentry_bars = (
        *bars,
        replace(
            bars[-1],
            date=bars[-1].date + timedelta(days=1),
            open=bars[-1].open + Decimal("1"),
            high=bars[-1].high + Decimal("1"),
            low=bars[-1].low + Decimal("1"),
            close=bars[-1].close + Decimal("1"),
            adjusted_close=bars[-1].adjusted_close + Decimal("1"),
        ),
    )
    reentry = replace(
        current,
        as_of_date=reentry_bars[-1].date,
        source_price_hash="d" * 64,
    )
    process_opportunity_transitions(
        sandbox_repository,
        sandbox_settings,
        {},
        {"sec_a": reentry},
        {"sec_a": reentry_bars},
        classifier=classifier,
        now=now + timedelta(days=1),
    )

    assert classifier.calls == 2
    assert first[0].decision is not None
    assert second[0].created is False
    wiki_ingest = next(
        (
            row
            for row in read_table(sandbox_repository, "operations_todo")
            if row["operation_type"] == "wiki_ingest"
        ),
        None,
    )
    if decision == "ingest":
        assert wiki_ingest is not None
        payload = json.loads(
            (sandbox_repository / wiki_ingest["payload_path"]).read_text(encoding="utf-8")
        )
        assert payload["inputs"]["source_hash"] == content_hash(first[0].path.read_bytes())
    else:
        assert wiki_ingest is None
    assert {row["operation_type"] for row in read_table(sandbox_repository, "operations_todo")} == (
        expected_types
    )
    assert (
        sum(
            row["operation_type"] == "opportunity_research"
            for row in read_table(sandbox_repository, "operations_todo")
        )
        == 1
    )
    packet_text = first[0].path.read_text(encoding="utf-8")
    assert "title: '[EXM] RSI overbought'" in packet_text
    assert "# [EXM] RSI overbought" in packet_text
    assert "- Security: [[securities/sec_a|EXM — Example common stock]] (`sec_a`)" in packet_text
    index = sandbox_settings.paths.wiki.joinpath("index.md").read_text(encoding="utf-8")
    assert f"[\\[EXM\\] RSI overbought](inbox/{first[0].path.stem})" in index
    assert f"classifier_decision: {decision}" in packet_text
    assert lint_wiki(sandbox_settings.paths.wiki) == []
