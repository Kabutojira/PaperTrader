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

from papertrader.atomic_io import atomic_write_csv
from papertrader.config import Settings
from papertrader.market_data import (
    SAFE_SECURITY_ID,
    load_security_identities,
    price_content_hash,
    read_price_cache,
)
from papertrader.models import IndicatorSnapshot, PriceBar, TechnicalSeriesRow
from papertrader.tables import read_csv, read_table, write_table
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
TECHNICAL_COLUMNS = (
    "date",
    "adjusted_open",
    "adjusted_high",
    "adjusted_low",
    "adjusted_close",
    "volume",
    "observation_count",
    "sma_20",
    "sma_50",
    "sma_200",
    "rsi_14",
    "bollinger_mid",
    "bollinger_upper",
    "bollinger_lower",
    "macd",
    "macd_signal",
    "macd_histogram",
    "return_1d",
    "return_5d",
    "return_20d",
    "volume_zscore",
    "volatility_20d",
    "trigger_state",
)


def _decimal_output(value: float | np.float64) -> Decimal | None:
    numeric = float(value)
    if math.isnan(numeric) or math.isinf(numeric):
        return None
    return Decimal(format(numeric, ".15g")).quantize(INDICATOR_QUANTUM, rounding=ROUND_HALF_EVEN)


def _return_at(bars: Sequence[PriceBar], index: int, periods: int) -> Decimal | None:
    if index < periods:
        return None
    current = bars[index].adjusted_close
    prior = bars[index - periods].adjusted_close
    if prior == 0:
        return None
    return ((current / prior) - Decimal("1")).quantize(INDICATOR_QUANTUM, rounding=ROUND_HALF_EVEN)


def _array_value(values: np.ndarray, index: int) -> Decimal | None:
    return _decimal_output(values[index])


def _annualized_volatility(values: np.ndarray, index: int) -> Decimal | None:
    volatility = _array_value(values, index)
    if volatility is None:
        return None
    return (volatility * Decimal("252").sqrt()).quantize(
        INDICATOR_QUANTUM, rounding=ROUND_HALF_EVEN
    )


def calculate_series(
    security_id: str,
    bars: Sequence[PriceBar],
    settings: Settings,
) -> tuple[TechnicalSeriesRow, ...]:
    """Calculate a complete adjusted-OHLC technical series in one TA-Lib pass."""

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
    sma_arrays = {period: talib.SMA(closes, timeperiod=period) for period in configured.sma_periods}
    rsi = talib.RSI(closes, timeperiod=configured.rsi_period)
    band_upper, band_middle, band_lower = talib.BBANDS(
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
    returns = np.full(len(closes), np.nan, dtype=np.float64)
    if len(closes) > 1:
        returns[1:] = closes[1:] / closes[:-1] - 1
    volatility = talib.STDDEV(returns, timeperiod=20, nbdev=1)

    output: list[TechnicalSeriesRow] = []
    for index, bar in enumerate(bars):
        observation_count = index + 1
        sma_200 = (
            _array_value(sma_arrays[200], index)
            if 200 in sma_arrays
            and observation_count >= settings.market_data.minimum_sma_200_observations
            else None
        )
        current_rsi = _array_value(rsi, index)
        current_upper = _array_value(band_upper, index)
        current_middle = _array_value(band_middle, index)
        current_lower = _array_value(band_lower, index)
        current_volume_zscore: Decimal | None = None
        if not np.isnan(volume_mean[index]) and volume_std[index] > 0:
            current_volume_zscore = _decimal_output(
                (volumes[index] - volume_mean[index]) / volume_std[index]
            )
        trigger_state: list[str] = []
        if current_rsi is not None and current_rsi <= configured.rsi_oversold:
            trigger_state.append("rsi_oversold")
        if current_rsi is not None and current_rsi >= configured.rsi_overbought:
            trigger_state.append("rsi_overbought")
        if current_lower is not None and bar.adjusted_close < current_lower:
            trigger_state.append("bollinger_below_lower")
        if current_upper is not None and bar.adjusted_close > current_upper:
            trigger_state.append("bollinger_above_upper")
        if (
            current_volume_zscore is not None
            and current_volume_zscore >= configured.volume_zscore_threshold
        ):
            trigger_state.append("volume_anomaly")

        adjustment_factor = bar.adjusted_close / bar.close
        adjusted_open = (bar.open * adjustment_factor).quantize(
            INDICATOR_QUANTUM, rounding=ROUND_HALF_EVEN
        )
        adjusted_high = (bar.high * adjustment_factor).quantize(
            INDICATOR_QUANTUM, rounding=ROUND_HALF_EVEN
        )
        adjusted_low = (bar.low * adjustment_factor).quantize(
            INDICATOR_QUANTUM, rounding=ROUND_HALF_EVEN
        )
        adjusted_close = bar.adjusted_close.quantize(INDICATOR_QUANTUM, rounding=ROUND_HALF_EVEN)
        output.append(
            TechnicalSeriesRow(
                date=bar.date,
                adjusted_open=adjusted_open,
                adjusted_high=adjusted_high,
                adjusted_low=adjusted_low,
                adjusted_close=adjusted_close,
                volume=bar.volume,
                observation_count=observation_count,
                sma_20=(_array_value(sma_arrays[20], index) if 20 in sma_arrays else None),
                sma_50=(_array_value(sma_arrays[50], index) if 50 in sma_arrays else None),
                sma_200=sma_200,
                rsi_14=current_rsi,
                bollinger_mid=current_middle,
                bollinger_upper=current_upper,
                bollinger_lower=current_lower,
                macd=_array_value(macd, index),
                macd_signal=_array_value(macd_signal, index),
                macd_histogram=_array_value(macd_histogram, index),
                return_1d=_return_at(bars, index, 1),
                return_5d=_return_at(bars, index, 5),
                return_20d=_return_at(bars, index, 20),
                volume_zscore=current_volume_zscore,
                volatility_20d=_annualized_volatility(volatility, index),
                trigger_state=tuple(sorted(trigger_state)),
            )
        )
    return tuple(output)


def _snapshot_from_series(
    security_id: str,
    bars: Sequence[PriceBar],
    series: Sequence[TechnicalSeriesRow],
    *,
    calculated_at: datetime,
) -> IndicatorSnapshot:
    if not bars or not series or len(bars) != len(series):
        raise CanonicalValueError("indicator snapshot requires aligned price and technical rows")
    row = series[-1]
    return IndicatorSnapshot(
        security_id=security_id,
        as_of_date=row.date,
        calculated_at=ensure_utc(calculated_at),
        observation_count=row.observation_count,
        sma_20=row.sma_20,
        sma_50=row.sma_50,
        sma_200=row.sma_200,
        rsi_14=row.rsi_14,
        bollinger_mid=row.bollinger_mid,
        bollinger_upper=row.bollinger_upper,
        bollinger_lower=row.bollinger_lower,
        macd=row.macd,
        macd_signal=row.macd_signal,
        macd_histogram=row.macd_histogram,
        return_1d=row.return_1d,
        return_5d=row.return_5d,
        return_20d=row.return_20d,
        volume_zscore=row.volume_zscore,
        volatility_20d=row.volatility_20d,
        trigger_state=row.trigger_state,
        source_price_hash=price_content_hash(bars),
    )


def calculate_snapshot(
    security_id: str,
    bars: Sequence[PriceBar],
    settings: Settings,
    *,
    calculated_at: datetime | None = None,
) -> IndicatorSnapshot:
    """Calculate the latest configured indicator set for one normalized price series."""

    return _snapshot_from_series(
        security_id,
        bars,
        calculate_series(security_id, bars, settings),
        calculated_at=ensure_utc(calculated_at or utc_now()),
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


def technical_series_path(repository_root: Path, security_id: str) -> Path:
    """Return the safe generated technical-series path for one security."""

    if not SAFE_SECURITY_ID.fullmatch(security_id):
        raise CanonicalValueError(f"unsafe security_id for technical path: {security_id!r}")
    return repository_root / "data" / "market" / "technical" / f"{security_id}.csv"


def technical_row(row: TechnicalSeriesRow) -> dict[str, object]:
    """Serialize one technical observation without timestamp-only churn."""

    def optional(value: Decimal | None) -> str:
        return decimal_text(value) if value is not None else ""

    return {
        "date": row.date.isoformat(),
        "adjusted_open": decimal_text(row.adjusted_open),
        "adjusted_high": decimal_text(row.adjusted_high),
        "adjusted_low": decimal_text(row.adjusted_low),
        "adjusted_close": decimal_text(row.adjusted_close),
        "volume": str(row.volume),
        "observation_count": str(row.observation_count),
        "sma_20": optional(row.sma_20),
        "sma_50": optional(row.sma_50),
        "sma_200": optional(row.sma_200),
        "rsi_14": optional(row.rsi_14),
        "bollinger_mid": optional(row.bollinger_mid),
        "bollinger_upper": optional(row.bollinger_upper),
        "bollinger_lower": optional(row.bollinger_lower),
        "macd": optional(row.macd),
        "macd_signal": optional(row.macd_signal),
        "macd_histogram": optional(row.macd_histogram),
        "return_1d": optional(row.return_1d),
        "return_5d": optional(row.return_5d),
        "return_20d": optional(row.return_20d),
        "volume_zscore": optional(row.volume_zscore),
        "volatility_20d": optional(row.volatility_20d),
        "trigger_state": "|".join(row.trigger_state),
    }


def write_technical_series(
    repository_root: Path,
    security_id: str,
    rows: Sequence[TechnicalSeriesRow],
) -> None:
    """Atomically replace one generated per-security technical series."""

    directory = repository_root / "data" / "market" / "technical"
    directory.mkdir(parents=True, exist_ok=True)
    atomic_write_csv(
        technical_series_path(repository_root, security_id),
        TECHNICAL_COLUMNS,
        (technical_row(row) for row in rows),
        allowed_root=repository_root,
    )


def validate_technical_series(repository_root: Path, settings: Settings) -> list[str]:
    """Prove that every generated chart series is an exact price-derived projection."""

    errors: list[str] = []
    try:
        identities = load_security_identities(repository_root)
    except (CanonicalValueError, OSError, ValueError) as exc:
        return [f"cannot load technical-series identities: {exc}"]
    expected_ids = {identity.security_id for identity in identities}
    directory = repository_root / "data" / "market" / "technical"
    if directory.exists() and (directory.is_symlink() or not directory.is_dir()):
        return ["technical-series path must be a regular directory"]
    actual_paths = sorted(directory.glob("*.csv")) if directory.is_dir() else []
    for path in actual_paths:
        if path.stem not in expected_ids:
            errors.append(f"orphan technical series: {path.name}")

    current_rows = {row["security_id"]: row for row in read_table(repository_root, "indicators")}
    for identity in identities:
        bars = read_price_cache(repository_root, identity.security_id)
        if not bars:
            continue
        path = technical_series_path(repository_root, identity.security_id)
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing technical series: {identity.security_id}")
            continue
        try:
            actual = read_csv(path, TECHNICAL_COLUMNS)
            expected = [
                {key: str(value) for key, value in technical_row(row).items()}
                for row in calculate_series(identity.security_id, bars, settings)
            ]
        except (CanonicalValueError, OSError, ValueError) as exc:
            errors.append(f"invalid technical series {identity.security_id}: {exc}")
            continue
        if actual != expected:
            errors.append(f"technical series differs from canonical prices: {identity.security_id}")
            continue
        current = current_rows.get(identity.security_id)
        if current is None:
            errors.append(
                f"technical series lacks latest indicator snapshot: {identity.security_id}"
            )
            continue
        final = actual[-1]
        latest_pairs = {
            "date": current["as_of_date"],
            "observation_count": current["observation_count"],
            "sma_20": current["sma_20"],
            "sma_50": current["sma_50"],
            "sma_200": current["sma_200"],
            "rsi_14": current["rsi_14"],
            "bollinger_mid": current["bollinger_mid"],
            "bollinger_upper": current["bollinger_upper"],
            "bollinger_lower": current["bollinger_lower"],
            "macd": current["macd"],
            "macd_signal": current["macd_signal"],
            "macd_histogram": current["macd_histogram"],
            "return_1d": current["return_1d"],
            "return_5d": current["return_5d"],
            "return_20d": current["return_20d"],
            "volume_zscore": current["volume_zscore"],
            "volatility_20d": current["volatility_20d"],
            "trigger_state": current["trigger_state"],
        }
        if any(final[key] != value for key, value in latest_pairs.items()):
            errors.append(
                f"technical series latest row differs from indicators: {identity.security_id}"
            )
        if current["source_price_hash"] != price_content_hash(bars):
            errors.append(f"indicator source hash differs from prices: {identity.security_id}")
    return errors


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
    series_by_security: dict[str, tuple[TechnicalSeriesRow, ...]] = {}
    errors: list[str] = []
    calculated_at = ensure_utc(now or utc_now())
    for identity in load_security_identities(repository_root):
        bars = read_price_cache(repository_root, identity.security_id)
        if not bars:
            errors.append(f"{identity.security_id}: price cache is empty")
            continue
        series = calculate_series(identity.security_id, bars, settings)
        snapshot = _snapshot_from_series(
            identity.security_id,
            bars,
            series,
            calculated_at=calculated_at,
        )
        old = previous.get(identity.security_id)
        if (
            old is not None
            and old.source_price_hash == snapshot.source_price_hash
            and old.as_of_date == snapshot.as_of_date
        ):
            snapshot = old
        current[identity.security_id] = snapshot
        series_by_security[identity.security_id] = series
    technical_directory = repository_root / "data" / "market" / "technical"
    technical_directory.mkdir(parents=True, exist_ok=True)
    active_ids = {identity.security_id for identity in load_security_identities(repository_root)}
    for path in sorted(technical_directory.glob("*.csv")):
        if path.stem not in active_ids:
            path.unlink()
    for security_id in sorted(series_by_security):
        write_technical_series(repository_root, security_id, series_by_security[security_id])
    write_table(
        repository_root,
        "indicators",
        [snapshot_row(current[key]) for key in sorted(current)],
    )
    return previous, current, tuple(errors)
