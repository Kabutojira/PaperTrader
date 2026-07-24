"""Small shared models for repository contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import PurePosixPath


@dataclass(frozen=True, slots=True)
class CsvContract:
    """The canonical path and ordered columns for one CSV file."""

    name: str
    path: PurePosixPath
    columns: tuple[str, ...]
    append_only: bool = False
    generated: bool = False


@dataclass(frozen=True, slots=True)
class DynamicCsvContract:
    """Canonical columns applied to every file matching one repository-local glob."""

    name: str
    glob: str
    columns: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """A named validation result with deterministic error messages."""

    name: str
    errors: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors


@dataclass(frozen=True, slots=True)
class SecurityIdentity:
    """Stable provider and venue identity for one monitored instrument."""

    security_id: str
    provider_symbol: str
    venue_mic: str
    currency: str
    instrument_type: str


@dataclass(frozen=True, slots=True)
class PriceBar:
    """One normalized, daily, provider-derived OHLCV observation."""

    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adjusted_close: Decimal
    volume: int
    dividends: Decimal
    stock_splits: Decimal
    currency: str
    provider_symbol: str
    retrieved_at: datetime
    source: str


@dataclass(frozen=True, slots=True)
class IndicatorSnapshot:
    """Latest deterministic indicator values for one security."""

    security_id: str
    as_of_date: date
    calculated_at: datetime
    observation_count: int
    sma_20: Decimal | None
    sma_50: Decimal | None
    sma_200: Decimal | None
    rsi_14: Decimal | None
    bollinger_mid: Decimal | None
    bollinger_upper: Decimal | None
    bollinger_lower: Decimal | None
    macd: Decimal | None
    macd_signal: Decimal | None
    macd_histogram: Decimal | None
    return_1d: Decimal | None
    return_5d: Decimal | None
    return_20d: Decimal | None
    volume_zscore: Decimal | None
    volatility_20d: Decimal | None
    trigger_state: tuple[str, ...]
    source_price_hash: str


@dataclass(frozen=True, slots=True)
class OpportunityTransition:
    """One material inactive/active indicator transition."""

    security_id: str
    trigger: str
    transition: str
    as_of_date: date
    strength: Decimal
    previous_strength: Decimal
    source_price_hash: str


@dataclass(frozen=True, slots=True)
class ClassifierDecision:
    """The only accepted cheap-model decision for a candidate wiki packet."""

    decision: str
    reason: str
    related_entity_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MarketBar:
    """Timestamped bar eligible for deterministic paper fills."""

    security_id: str
    provider_contract_id: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    currency: str
    fx_rate_to_base: Decimal


@dataclass(frozen=True, slots=True)
class OptionQuote:
    """Fresh timestamped bid/ask and liquidity for a single option contract."""

    provider_contract_id: str
    timestamp: datetime
    bid: Decimal
    ask: Decimal
    currency: str
    fx_rate_to_base: Decimal
    open_interest: int
    volume: int


@dataclass(frozen=True, slots=True)
class PositionMark:
    """Current deterministic mark and FX conversion for one position identity."""

    security_id: str
    provider_contract_id: str
    price: Decimal
    currency: str
    fx_rate_to_base: Decimal
    marked_at: datetime


@dataclass(frozen=True, slots=True)
class Fill:
    """A validated fill candidate before append-only ledger persistence."""

    order_id: str
    leg_id: str
    executed_at: datetime
    security_id: str
    provider_contract_id: str
    action: str
    side: str
    instrument_type: str
    quantity: Decimal
    fill_price: Decimal
    contract_multiplier: Decimal
    fees: Decimal
    currency: str
    fx_rate_to_base: Decimal
    source_time: datetime


@dataclass(frozen=True, slots=True)
class OrderLegSpec:
    """Validated normalized leg request shared by order, risk, and fill code."""

    leg_id: str
    action: str
    side: str
    instrument_type: str
    security_id: str
    provider_contract_id: str
    option_type: str
    expiry: date | None
    strike: Decimal | None
    quantity: Decimal
    contract_multiplier: Decimal
    limit_price: Decimal | None
    currency: str


@dataclass(frozen=True, slots=True)
class ReferencePrice:
    """Fresh valuation input used before a paper order is accepted."""

    security_id: str
    provider_contract_id: str
    price: Decimal
    currency: str
    fx_rate_to_base: Decimal
    as_of: datetime
    bid: Decimal | None = None
    ask: Decimal | None = None
    open_interest: int | None = None
    volume: int | None = None


@dataclass(frozen=True, slots=True)
class RiskPosition:
    """Existing position quantity and reference notional for pre-order risk."""

    security_id: str
    provider_contract_id: str
    side: str
    instrument_type: str
    quantity: Decimal
    contract_multiplier: Decimal
    currency: str
    option_type: str
    expiry: date | None
    strike: Decimal | None


@dataclass(frozen=True, slots=True)
class RiskState:
    """Reconciled account values used by the pure risk evaluator."""

    equity_base: Decimal
    cash_base: Decimal
    gross_exposure_base: Decimal
    short_exposure_base: Decimal
    options_risk_base: Decimal
    daily_turnover_base: Decimal
    active_strategy_count: int
    positions: tuple[RiskPosition, ...]


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    """Closed risk result; any violation causes order creation to fail closed."""

    violations: tuple[str, ...]
    projected_cash_base: Decimal
    projected_gross_exposure_base: Decimal
    projected_short_exposure_base: Decimal
    projected_options_risk_base: Decimal

    @property
    def passed(self) -> bool:
        return not self.violations
