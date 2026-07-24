"""TA-Lib indicator calculations with deterministic Decimal-facing snapshots."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

import numpy as np
import talib
from talib._ta_lib import MA_Type

from papertrader.config import Settings
from papertrader.market_data import load_security_identities, price_content_hash, read_price_cache
from papertrader.models import IndicatorSnapshot, PriceBar
from papertrader.tables import read_table, write_table
from papertrader.utils import (
    CanonicalValueError,
    decimal_text,
    ensure_utc,
    format_timestamp,
    parse_iso_date,
    parse_timestamp,
    required_decimal,
    utc_now,
)

INDICATOR_QUANTUM = Decimal("0.00000001")


def _decimal_output(value: float | np.float64) -> Decimal | None:
    numeric = float(value)
    if math.isnan(numeric) or math.isinf(numeric):
        return None
    return Decimal(format(numeric, ".15g")).quantize(INDICATOR_QUANTUM, rounding=ROUND_HALF_EVEN)


def _last(values: np.ndarray) -> Decimal | None:
    if not len(values):
        return None
    return _decimal_output(values[-1])


def _return(bars: Sequence[PriceBar], periods: int) -> Decimal | None:
    if len(bars) <= periods:
        return None
    current = bars[-1].adjusted_close
    prior = bars[-1 - periods].adjusted_close
    if prior == 0:
        return None
    return ((current / prior) - Decimal("1")).quantize(INDICATOR_QUANTUM, rounding=ROUND_HALF_EVEN)


def calculate_snapshot(
    security_id: str,
    bars: Sequence[PriceBar],
    settings: Settings,
    *,
    calculated_at: datetime | None = None,
) -> IndicatorSnapshot:
    """Calculate the latest configured indicator set for one normalized price series."""

    if not bars:
        raise CanonicalValueError(f"cannot calculate indicators without prices for {security_id}")
    if any(bars[index - 1].date >= bars[index].date for index in range(1, len(bars))):
        raise CanonicalValueError("indicator input bars must be strictly ascending")
    if any(
        not bar.adjusted_close.is_finite() or bar.adjusted_close <= 0 or bar.volume < 0
        for bar in bars
    ):
        raise CanonicalValueError("indicator input contains invalid prices or volume")
    closes = np.asarray([float(bar.adjusted_close) for bar in bars], dtype=np.float64)
    volumes = np.asarray([float(bar.volume) for bar in bars], dtype=np.float64)
    configured = settings.indicators
    sma_values = {
        period: _last(talib.SMA(closes, timeperiod=period)) for period in configured.sma_periods
    }
    sma_200 = sma_values.get(200)
    if len(bars) < settings.market_data.minimum_sma_200_observations:
        sma_200 = None
    rsi = _last(talib.RSI(closes, timeperiod=configured.rsi_period))
    upper, middle, lower = talib.BBANDS(
        closes,
        timeperiod=configured.bollinger_period,
        nbdevup=float(configured.bollinger_standard_deviations),
        nbdevdn=float(configured.bollinger_standard_deviations),
        matype=MA_Type.SMA,
    )
    macd, macd_signal, macd_histogram = talib.MACD(
        closes,
        fastperiod=configured.macd_fast,
        slowperiod=configured.macd_slow,
        signalperiod=configured.macd_signal,
    )
    volume_mean = talib.SMA(volumes, timeperiod=20)
    volume_std = talib.STDDEV(volumes, timeperiod=20, nbdev=1)
    volume_zscore: Decimal | None = None
    if len(volume_mean) and not np.isnan(volume_mean[-1]) and volume_std[-1] > 0:
        volume_zscore = _decimal_output((volumes[-1] - volume_mean[-1]) / volume_std[-1])
    returns = np.full(len(closes), np.nan, dtype=np.float64)
    if len(closes) > 1:
        returns[1:] = closes[1:] / closes[:-1] - 1
    volatility = _last(talib.STDDEV(returns, timeperiod=20, nbdev=1))
    if volatility is not None:
        volatility = (volatility * Decimal("252").sqrt()).quantize(
            INDICATOR_QUANTUM, rounding=ROUND_HALF_EVEN
        )
    band_upper = _last(upper)
    band_middle = _last(middle)
    band_lower = _last(lower)
    close = bars[-1].adjusted_close
    trigger_state: list[str] = []
    if rsi is not None and rsi <= configured.rsi_oversold:
        trigger_state.append("rsi_oversold")
    if rsi is not None and rsi >= configured.rsi_overbought:
        trigger_state.append("rsi_overbought")
    if band_lower is not None and close < band_lower:
        trigger_state.append("bollinger_below_lower")
    if band_upper is not None and close > band_upper:
        trigger_state.append("bollinger_above_upper")
    instant = ensure_utc(calculated_at or utc_now())
    return IndicatorSnapshot(
        security_id=security_id,
        as_of_date=bars[-1].date,
        calculated_at=instant,
        observation_count=len(bars),
        sma_20=sma_values.get(20),
        sma_50=sma_values.get(50),
        sma_200=sma_200,
        rsi_14=rsi,
        bollinger_mid=band_middle,
        bollinger_upper=band_upper,
        bollinger_lower=band_lower,
        macd=_last(macd),
        macd_signal=_last(macd_signal),
        macd_histogram=_last(macd_histogram),
        return_1d=_return(bars, 1),
        return_5d=_return(bars, 5),
        return_20d=_return(bars, 20),
        volume_zscore=volume_zscore,
        volatility_20d=volatility,
        trigger_state=tuple(sorted(trigger_state)),
        source_price_hash=price_content_hash(bars),
    )


def _optional_decimal(value: str, *, label: str) -> Decimal | None:
    if not value:
        return None
    return required_decimal(value, label=label)


def snapshot_from_row(row: Mapping[str, str]) -> IndicatorSnapshot:
    """Parse a canonical indicator table row."""

    calculated = parse_timestamp(row["calculated_at"])
    assert calculated is not None
    try:
        count = int(row["observation_count"])
    except ValueError as exc:
        raise CanonicalValueError("indicator observation_count must be an integer") from exc
    return IndicatorSnapshot(
        security_id=row["security_id"],
        as_of_date=parse_iso_date(row["as_of_date"]),
        calculated_at=calculated,
        observation_count=count,
        sma_20=_optional_decimal(row["sma_20"], label="sma_20"),
        sma_50=_optional_decimal(row["sma_50"], label="sma_50"),
        sma_200=_optional_decimal(row["sma_200"], label="sma_200"),
        rsi_14=_optional_decimal(row["rsi_14"], label="rsi_14"),
        bollinger_mid=_optional_decimal(row["bollinger_mid"], label="bollinger_mid"),
        bollinger_upper=_optional_decimal(row["bollinger_upper"], label="bollinger_upper"),
        bollinger_lower=_optional_decimal(row["bollinger_lower"], label="bollinger_lower"),
        macd=_optional_decimal(row["macd"], label="macd"),
        macd_signal=_optional_decimal(row["macd_signal"], label="macd_signal"),
        macd_histogram=_optional_decimal(row["macd_histogram"], label="macd_histogram"),
        return_1d=_optional_decimal(row["return_1d"], label="return_1d"),
        return_5d=_optional_decimal(row["return_5d"], label="return_5d"),
        return_20d=_optional_decimal(row["return_20d"], label="return_20d"),
        volume_zscore=_optional_decimal(row["volume_zscore"], label="volume_zscore"),
        volatility_20d=_optional_decimal(row["volatility_20d"], label="volatility_20d"),
        trigger_state=tuple(filter(None, row["trigger_state"].split("|"))),
        source_price_hash=row["source_price_hash"],
    )


def snapshot_row(snapshot: IndicatorSnapshot) -> dict[str, object]:
    """Serialize one indicator snapshot for the generated table."""

    def optional(value: Decimal | None) -> str:
        return decimal_text(value) if value is not None else ""

    return {
        "security_id": snapshot.security_id,
        "as_of_date": snapshot.as_of_date.isoformat(),
        "calculated_at": format_timestamp(snapshot.calculated_at),
        "observation_count": str(snapshot.observation_count),
        "sma_20": optional(snapshot.sma_20),
        "sma_50": optional(snapshot.sma_50),
        "sma_200": optional(snapshot.sma_200),
        "rsi_14": optional(snapshot.rsi_14),
        "bollinger_mid": optional(snapshot.bollinger_mid),
        "bollinger_upper": optional(snapshot.bollinger_upper),
        "bollinger_lower": optional(snapshot.bollinger_lower),
        "macd": optional(snapshot.macd),
        "macd_signal": optional(snapshot.macd_signal),
        "macd_histogram": optional(snapshot.macd_histogram),
        "return_1d": optional(snapshot.return_1d),
        "return_5d": optional(snapshot.return_5d),
        "return_20d": optional(snapshot.return_20d),
        "volume_zscore": optional(snapshot.volume_zscore),
        "volatility_20d": optional(snapshot.volatility_20d),
        "trigger_state": "|".join(snapshot.trigger_state),
        "source_price_hash": snapshot.source_price_hash,
    }


def update_indicators(
    repository_root: Path,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> tuple[
    Mapping[str, IndicatorSnapshot],
    Mapping[str, IndicatorSnapshot],
    tuple[str, ...],
]:
    """Recalculate all active identities, avoiding timestamp-only generated changes."""

    previous_rows = read_table(repository_root, "indicators")
    previous = {row["security_id"]: snapshot_from_row(row) for row in previous_rows}
    current: dict[str, IndicatorSnapshot] = {}
    errors: list[str] = []
    calculated_at = ensure_utc(now or utc_now())
    for identity in load_security_identities(repository_root):
        bars = read_price_cache(repository_root, identity.security_id)
        if not bars:
            errors.append(f"{identity.security_id}: price cache is empty")
            continue
        snapshot = calculate_snapshot(
            identity.security_id, bars, settings, calculated_at=calculated_at
        )
        old = previous.get(identity.security_id)
        if (
            old is not None
            and old.source_price_hash == snapshot.source_price_hash
            and old.as_of_date == snapshot.as_of_date
        ):
            snapshot = old
        current[identity.security_id] = snapshot
    write_table(
        repository_root,
        "indicators",
        [snapshot_row(current[key]) for key in sorted(current)],
    )
    return previous, current, tuple(errors)
