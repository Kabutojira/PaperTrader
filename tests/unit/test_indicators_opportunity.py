from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.config import Settings
from papertrader.indicators import calculate_series, calculate_snapshot, snapshot_row, technical_row
from papertrader.models import (
    AlertDirection,
    ClassifierDecision,
    IndicatorSnapshot,
    PriceBar,
)
from papertrader.opportunity import (
    ClassifierError,
    alert_direction,
    detect_transitions,
    process_opportunity_transitions,
    retry_unclassified_candidate_packets,
    validate_classifier_decision,
)
from papertrader.queue import prepare_queue
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


def _position_row(*, quantity: str = "1", side: str = "long") -> dict[str, str]:
    return {
        "position_id": "position_test",
        "security_id": "sec_a",
        "provider_contract_id": "",
        "instrument_type": "equity",
        "side": side,
        "quantity": quantity,
        "average_cost": "90",
        "currency": "USD",
        "current_price": "100",
        "market_value_base": "100",
        "unrealized_pnl_base": "10",
        "realized_pnl_base": "0",
        "opened_at": "2026-07-20T00:00:00Z",
        "last_mark_at": "2026-07-24T22:00:00Z",
        "strategy_ids": "",
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


def test_technical_series_uses_adjusted_ohlc_and_matches_latest_snapshot(
    sandbox_settings: Settings,
) -> None:
    bars = list(_bars(220))
    bars[-1] = replace(
        bars[-1],
        open=Decimal("90"),
        high=Decimal("110"),
        low=Decimal("80"),
        close=Decimal("100"),
        adjusted_close=Decimal("50"),
    )

    series = calculate_series("sec_a", bars, sandbox_settings)
    snapshot = calculate_snapshot("sec_a", bars, sandbox_settings)
    final = technical_row(series[-1])

    assert final["adjusted_open"] == "45"
    assert final["adjusted_high"] == "55"
    assert final["adjusted_low"] == "40"
    assert final["adjusted_close"] == "50"
    assert final["date"] == snapshot.as_of_date.isoformat()
    assert final["rsi_14"] == snapshot_row(snapshot)["rsi_14"]
    assert final["macd_histogram"] == snapshot_row(snapshot)["macd_histogram"]


def test_technical_series_preserves_indicator_warmup_as_empty_values(
    sandbox_settings: Settings,
) -> None:
    rows = [technical_row(row) for row in calculate_series("sec_a", _bars(220), sandbox_settings)]

    assert rows[0]["sma_20"] == ""
    assert rows[18]["sma_20"] == ""
    assert rows[19]["sma_20"] != ""
    assert rows[198]["sma_200"] == ""
    assert rows[199]["sma_200"] != ""


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


@pytest.mark.parametrize(
    ("trigger", "expected"),
    [
        ("rsi_oversold", AlertDirection.BULLISH),
        ("bollinger_below_lower", AlertDirection.BULLISH),
        ("sma_50_cross_above_200", AlertDirection.BULLISH),
        ("macd_cross_above_signal", AlertDirection.BULLISH),
        ("rsi_overbought", AlertDirection.BEARISH),
        ("bollinger_above_upper", AlertDirection.BEARISH),
        ("sma_50_cross_below_200", AlertDirection.BEARISH),
        ("macd_cross_below_signal", AlertDirection.BEARISH),
        ("volume_anomaly", AlertDirection.NEUTRAL),
    ],
)
def test_alert_direction_contract(trigger: str, expected: AlertDirection) -> None:
    assert alert_direction(trigger) is expected


def test_unknown_alert_direction_fails_closed() -> None:
    with pytest.raises(ValueError, match="unknown indicator alert trigger"):
        alert_direction("instructions_from_source")


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
        rsi=Decimal("20"),
        trigger_state=("rsi_oversold",),
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
        ("ignore", {"opportunity_research", "security_research"}),
        ("ingest", {"opportunity_research", "security_research", "wiki_ingest"}),
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
        rsi=Decimal("20"),
        trigger_state=("rsi_oversold",),
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
    security_research = next(
        row
        for row in read_table(sandbox_repository, "operations_todo")
        if row["operation_type"] == "security_research"
    )
    assert security_research["priority"] == "96"
    security_payload = json.loads(
        (sandbox_repository / security_research["payload_path"]).read_text(encoding="utf-8")
    )
    assert security_payload["inputs"]["trigger_types"] == ["rsi_oversold"]
    assert (
        sum(
            row["operation_type"] == "opportunity_research"
            for row in read_table(sandbox_repository, "operations_todo")
        )
        == 1
    )
    packet_text = first[0].path.read_text(encoding="utf-8")
    assert "title: EXM — RSI oversold" in packet_text
    assert "# EXM — RSI oversold" in packet_text
    assert "- Security: [[securities/sec_a|EXM — Example common stock]]" in packet_text
    catalog = sandbox_settings.paths.wiki.joinpath("research-catalog.md").read_text(
        encoding="utf-8"
    )
    assert f"[[inbox/{first[0].path.stem}|EXM — RSI oversold]]" in catalog
    assert f"classifier_decision: {decision}" in packet_text
    assert lint_wiki(sandbox_settings.paths.wiki) == []


def test_volume_anomaly_and_sma_macd_crossings_are_price_alert_transitions(
    sandbox_settings: Settings,
) -> None:
    bars = _bars(220)
    previous = replace(
        _snapshot(
            as_of=bars[-2].date,
            rsi=Decimal("50"),
            trigger_state=(),
            source_hash="e" * 64,
        ),
        sma_50=Decimal("99"),
        sma_200=Decimal("100"),
        macd=Decimal("0.9"),
        macd_signal=Decimal("1"),
    )
    current = replace(
        previous,
        as_of_date=bars[-1].date,
        sma_50=Decimal("101"),
        sma_200=Decimal("100"),
        macd=Decimal("1.1"),
        macd_signal=Decimal("1"),
        volume_zscore=Decimal("3"),
        trigger_state=("volume_anomaly",),
        source_price_hash="f" * 64,
    )

    transitions = detect_transitions(previous, current, bars, sandbox_settings)

    assert [(item.trigger, item.transition) for item in transitions] == [
        ("macd_cross_above_signal", "entered"),
        ("sma_50_cross_above_200", "entered"),
        ("volume_anomaly", "entered"),
    ]


def test_unheld_bearish_alert_is_audited_without_classifier_or_research(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    bars = _bars(220)
    current = _snapshot(
        as_of=bars[-1].date,
        rsi=Decimal("80"),
        trigger_state=("rsi_overbought",),
        source_hash="9" * 64,
    )
    write_table(sandbox_repository, "securities", [_security_row()])
    classifier = _Classifier("ingest")

    packets = process_opportunity_transitions(
        sandbox_repository,
        sandbox_settings,
        {},
        {"sec_a": current},
        {"sec_a": bars},
        classifier=classifier,
        now=datetime(2026, 7, 24, 22, tzinfo=UTC),
    )

    assert classifier.calls == 0
    assert packets[0].decision == ClassifierDecision("skipped", "bearish_alert_unowned", ())
    packet = packets[0].path.read_text(encoding="utf-8")
    assert "alert_direction: bearish" in packet
    assert "research_gate: suppressed" in packet
    assert "research_gate_reason: bearish_alert_unowned" in packet
    assert "classifier_decision: skipped" in packet
    assert read_table(sandbox_repository, "operations_todo") == []


@pytest.mark.parametrize(("quantity", "side"), [("1", "long"), ("-2", "short")])
def test_any_nonzero_reconciled_position_keeps_bearish_research_enabled(
    sandbox_repository: Path,
    sandbox_settings: Settings,
    quantity: str,
    side: str,
) -> None:
    bars = _bars(220)
    current = _snapshot(
        as_of=bars[-1].date,
        rsi=Decimal("80"),
        trigger_state=("rsi_overbought",),
        source_hash="8" * 64,
    )
    write_table(sandbox_repository, "securities", [_security_row()])
    write_table(sandbox_repository, "portfolio", [_position_row(quantity=quantity, side=side)])
    classifier = _Classifier("ignore")

    packets = process_opportunity_transitions(
        sandbox_repository,
        sandbox_settings,
        {},
        {"sec_a": current},
        {"sec_a": bars},
        classifier=classifier,
        now=datetime(2026, 7, 24, 22, tzinfo=UTC),
    )

    assert classifier.calls == 1
    assert packets[0].decision is not None
    assert packets[0].decision.decision == "ignore"
    assert {row["operation_type"] for row in read_table(sandbox_repository, "operations_todo")} == {
        "opportunity_research",
        "security_research",
    }


def test_mixed_unheld_alert_filters_bearish_causes_from_every_payload(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    bars = _bars(220)
    current = _snapshot(
        as_of=bars[-1].date,
        rsi=Decimal("80"),
        trigger_state=("rsi_overbought", "volume_anomaly"),
        source_hash="7" * 64,
    )
    current = replace(current, volume_zscore=Decimal("3"))
    write_table(sandbox_repository, "securities", [_security_row()])
    classifier = _Classifier("ignore")

    packets = process_opportunity_transitions(
        sandbox_repository,
        sandbox_settings,
        {},
        {"sec_a": current},
        {"sec_a": bars},
        classifier=classifier,
        now=datetime(2026, 7, 24, 22, tzinfo=UTC),
    )

    assert classifier.calls == 1
    assert [packet.decision.decision if packet.decision else "blocked" for packet in packets] == [
        "skipped",
        "ignore",
    ]
    operations = read_table(sandbox_repository, "operations_todo")
    assert {row["operation_type"] for row in operations} == {
        "opportunity_research",
        "security_research",
    }
    for row in operations:
        payload = json.loads((sandbox_repository / row["payload_path"]).read_text())
        assert "rsi_overbought" not in json.dumps(payload)
    research = next(row for row in operations if row["operation_type"] == "security_research")
    payload = json.loads((sandbox_repository / research["payload_path"]).read_text())
    assert payload["inputs"]["trigger_types"] == ["volume_anomaly"]


def test_queue_cleanup_archives_only_exclusive_unheld_bearish_lineage(
    sandbox_repository: Path,
    sandbox_settings: Settings,
) -> None:
    bars = _bars(220)
    current = _snapshot(
        as_of=bars[-1].date,
        rsi=Decimal("80"),
        trigger_state=("rsi_overbought", "volume_anomaly"),
        source_hash="6" * 64,
    )
    current = replace(current, volume_zscore=Decimal("3"))
    write_table(sandbox_repository, "securities", [_security_row()])
    write_table(sandbox_repository, "portfolio", [_position_row()])
    process_opportunity_transitions(
        sandbox_repository,
        sandbox_settings,
        {},
        {"sec_a": current},
        {"sec_a": bars},
        classifier=_Classifier("ignore"),
        now=datetime(2026, 7, 24, 22, tzinfo=UTC),
    )
    write_table(sandbox_repository, "portfolio", [])

    dispositions = prepare_queue(sandbox_repository, now=datetime(2026, 7, 24, 22, 1, tzinfo=UTC))

    assert sum("bearish_alert_unowned" in value for value in dispositions) == 1
    history = read_table(sandbox_repository, "operations_history")
    skipped = [row for row in history if row["terminal_reason"] == "bearish_alert_unowned"]
    assert len(skipped) == 1
    active = read_table(sandbox_repository, "operations_todo")
    assert any(row["operation_type"] == "security_research" for row in active)
    assert any(
        row["operation_type"] == "opportunity_research"
        and "volume_anomaly" in (sandbox_repository / row["payload_path"]).read_text()
        for row in active
    )
