"""Load repository-local settings and enforce the paper-only startup boundary."""

from __future__ import annotations

import configparser
import os
import re
import shlex
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from string import Template

from papertrader.utils import required_decimal


class ConfigurationError(ValueError):
    """Raised when repository configuration violates a required invariant."""


@dataclass(frozen=True, slots=True)
class RepositoryPaths:
    """Resolved paths that must remain inside the checkout."""

    root: Path
    data: Path
    wiki: Path
    schemas: Path
    skills: Path


@dataclass(frozen=True, slots=True)
class MarketDataSettings:
    """Deterministic market retrieval and cache policy."""

    provider: str
    price_retention_days: int
    minimum_sma_200_observations: int
    stale_price_after: timedelta
    retrieval_retries: int
    timezone: str
    display_timezone: str
    calendars: tuple[tuple[str, str], ...]

    def calendar_for(self, venue_mic: str) -> str:
        """Return the configured exchange-calendar name for a venue MIC."""

        calendars = dict(self.calendars)
        try:
            return calendars[venue_mic]
        except KeyError as exc:
            raise ConfigurationError(f"no market calendar configured for {venue_mic}") from exc


@dataclass(frozen=True, slots=True)
class IndicatorSettings:
    """TA-Lib periods, thresholds, and transition policy."""

    rsi_period: int
    rsi_oversold: Decimal
    rsi_overbought: Decimal
    bollinger_period: int
    bollinger_standard_deviations: Decimal
    sma_periods: tuple[int, ...]
    macd_fast: int
    macd_slow: int
    macd_signal: int
    opportunity_cooldown_days: int
    material_strengthening_pct: Decimal


@dataclass(frozen=True, slots=True)
class PortfolioSettings:
    """Base-currency and initial-capital contract."""

    base_currency: str
    initial_capital: Decimal


@dataclass(frozen=True, slots=True)
class RiskSettings:
    """Version-1 exposure, turnover, and instrument limits."""

    margin_of_safety_pct: Decimal
    maximum_single_position_pct: Decimal
    maximum_short_position_pct: Decimal
    maximum_options_premium_risk_pct: Decimal
    maximum_pair_gross_exposure_pct: Decimal
    maximum_total_gross_exposure_pct: Decimal
    maximum_active_strategies: int
    maximum_daily_turnover_pct: Decimal
    allowed_instruments: tuple[str, ...]
    allowed_exchanges: tuple[str, ...]
    allowed_currencies: tuple[str, ...]
    minimum_option_open_interest: int
    minimum_option_volume: int


@dataclass(frozen=True, slots=True)
class OrderSettings:
    """Paper-order fill, slippage, fee, and expiry policy."""

    default_fill_policy: str
    default_order_type: str
    slippage_model: str
    slippage_bps: Decimal
    fee_model: str
    fixed_fee: Decimal
    variable_fee_bps: Decimal
    option_quote_freshness: timedelta
    order_expiry: timedelta


@dataclass(frozen=True, slots=True)
class OperationSettings:
    """Sequential queue lease and per-run budget limits."""

    lease_duration: timedelta
    default_max_attempts: int
    maximum_llm_operations_per_run: int
    maximum_model_budget_usd_per_run: Decimal


@dataclass(frozen=True, slots=True)
class ClassifierSettings:
    """Credential-free cheap-model command boundary for inbox decisions."""

    command: tuple[str, ...]
    model: str
    timeout_seconds: int


@dataclass(frozen=True, slots=True)
class HermesSettings:
    """Pinned one-shot Hermes invocation and credential-forwarding policy."""

    command: tuple[str, ...]
    arguments: tuple[str, ...]
    toolsets: tuple[str, ...]
    required_native_skill: str
    required_native_skill_version: str
    inference_environment: tuple[str, ...]
    maximum_turns: int
    timeout_seconds: int


@dataclass(frozen=True, slots=True)
class TelegramSettings:
    """Bounded post-commit Telegram delivery policy without credentials."""

    maximum_attempts: int
    timeout_seconds: int
    message_limit: int


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated repository settings used by every deterministic subsystem."""

    config: configparser.ConfigParser
    paths: RepositoryPaths
    paper_trading_only: bool
    hermes_external_skill_dirs: tuple[Path, ...]
    market_data: MarketDataSettings
    indicators: IndicatorSettings
    portfolio: PortfolioSettings
    risk: RiskSettings
    orders: OrderSettings
    operations: OperationSettings
    classifier: ClassifierSettings
    hermes: HermesSettings
    telegram: TelegramSettings


def find_repository_root(start: Path | None = None) -> Path:
    """Find the nearest parent containing the repository's two root contracts."""

    candidate = (start or Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / "AGENTS.md").is_file() and (directory / "PLAN.md").is_file():
            return directory
    raise ConfigurationError(f"cannot find PaperTrader repository from {candidate}")


def _resolve_inside(root: Path, value: str, label: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ConfigurationError(f"{label} must resolve inside {root}: {resolved}") from exc
    return resolved


def _require_paper_mode(parser: configparser.ConfigParser, environ: Mapping[str, str]) -> None:
    if not parser.has_option("safety", "paper_trading_only"):
        raise ConfigurationError("config.ini must define safety.paper_trading_only")
    try:
        configured = parser.getboolean("safety", "paper_trading_only")
    except ValueError as exc:
        raise ConfigurationError("safety.paper_trading_only must be a boolean") from exc
    if not configured:
        raise ConfigurationError("safety.paper_trading_only must be true")
    if parser.getboolean("safety", "allow_real_orders", fallback=False):
        raise ConfigurationError("safety.allow_real_orders must remain false")
    if environ.get("PAPER_TRADING_ONLY", "").strip().lower() != "true":
        raise ConfigurationError("PAPER_TRADING_ONLY=true is required at startup")


def _positive_int(
    parser: configparser.ConfigParser,
    section: str,
    option: str,
    *,
    allow_zero: bool = False,
) -> int:
    try:
        value = parser.getint(section, option)
    except (configparser.Error, ValueError) as exc:
        raise ConfigurationError(f"{section}.{option} must be an integer") from exc
    minimum = 0 if allow_zero else 1
    if value < minimum:
        raise ConfigurationError(f"{section}.{option} must be >= {minimum}")
    return value


def _decimal(
    parser: configparser.ConfigParser,
    section: str,
    option: str,
    *,
    minimum: Decimal = Decimal("0"),
    maximum: Decimal | None = None,
) -> Decimal:
    try:
        value = required_decimal(parser.get(section, option), label=f"{section}.{option}")
    except (configparser.Error, ValueError) as exc:
        raise ConfigurationError(str(exc)) from exc
    if value < minimum or (maximum is not None and value > maximum):
        suffix = f" and <= {maximum}" if maximum is not None else ""
        raise ConfigurationError(f"{section}.{option} must be >= {minimum}{suffix}")
    return value


def _csv_values(parser: configparser.ConfigParser, section: str, option: str) -> tuple[str, ...]:
    values = tuple(
        value.strip() for value in parser.get(section, option).split(",") if value.strip()
    )
    if not values or len(values) != len(set(values)):
        raise ConfigurationError(f"{section}.{option} must contain unique comma-separated values")
    return values


def _choice(
    parser: configparser.ConfigParser,
    section: str,
    option: str,
    choices: frozenset[str],
) -> str:
    value = parser.get(section, option).strip()
    if value not in choices:
        raise ConfigurationError(f"{section}.{option} must be one of {sorted(choices)}")
    return value


def _load_runtime_settings(
    parser: configparser.ConfigParser,
) -> tuple[
    MarketDataSettings,
    IndicatorSettings,
    PortfolioSettings,
    RiskSettings,
    OrderSettings,
    OperationSettings,
    ClassifierSettings,
]:
    calendars = tuple(
        sorted((mic.strip().upper(), name.strip()) for mic, name in parser.items("calendars"))
    )
    if not calendars or any(not mic or not name for mic, name in calendars):
        raise ConfigurationError("calendars must map venue MICs to calendar names")
    market = MarketDataSettings(
        provider=_choice(parser, "market_data", "provider", frozenset({"yfinance"})),
        price_retention_days=_positive_int(parser, "market_data", "price_retention_days"),
        minimum_sma_200_observations=_positive_int(
            parser, "market_data", "minimum_sma_200_observations"
        ),
        stale_price_after=timedelta(
            hours=_positive_int(parser, "market_data", "stale_price_hours")
        ),
        retrieval_retries=_positive_int(parser, "market_data", "retrieval_retries"),
        timezone=parser.get("market_data", "timezone").strip(),
        display_timezone=parser.get("market_data", "display_timezone").strip(),
        calendars=calendars,
    )
    if market.price_retention_days != 365:
        raise ConfigurationError("market_data.price_retention_days must be exactly 365")
    if market.minimum_sma_200_observations < 200:
        raise ConfigurationError("market_data.minimum_sma_200_observations must be at least 200")
    if market.timezone != "UTC" or market.display_timezone != "Europe/Rome":
        raise ConfigurationError(
            "market data timezones must be UTC with Europe/Rome display conversion"
        )
    sma_periods = tuple(int(value) for value in _csv_values(parser, "indicators", "sma_periods"))
    if sma_periods != (20, 50, 200):
        raise ConfigurationError("indicators.sma_periods must be exactly 20,50,200")
    indicators = IndicatorSettings(
        rsi_period=_positive_int(parser, "indicators", "rsi_period"),
        rsi_oversold=_decimal(parser, "indicators", "rsi_oversold", maximum=Decimal("100")),
        rsi_overbought=_decimal(parser, "indicators", "rsi_overbought", maximum=Decimal("100")),
        bollinger_period=_positive_int(parser, "indicators", "bollinger_period"),
        bollinger_standard_deviations=_decimal(
            parser, "indicators", "bollinger_standard_deviations"
        ),
        sma_periods=sma_periods,
        macd_fast=_positive_int(parser, "indicators", "macd_fast"),
        macd_slow=_positive_int(parser, "indicators", "macd_slow"),
        macd_signal=_positive_int(parser, "indicators", "macd_signal"),
        opportunity_cooldown_days=_positive_int(
            parser, "indicators", "opportunity_cooldown_days", allow_zero=True
        ),
        material_strengthening_pct=_decimal(parser, "indicators", "material_strengthening_pct"),
    )
    if not Decimal("0") < indicators.rsi_oversold < indicators.rsi_overbought < Decimal("100"):
        raise ConfigurationError("RSI thresholds must satisfy 0 < oversold < overbought < 100")
    if indicators.rsi_period != 14 or indicators.bollinger_period != 20:
        raise ConfigurationError("indicator output contracts require RSI 14 and Bollinger 20")
    if indicators.bollinger_standard_deviations <= 0:
        raise ConfigurationError("Bollinger standard deviations must be positive")
    if indicators.macd_fast >= indicators.macd_slow:
        raise ConfigurationError("MACD fast period must be below slow period")
    base_currency = parser.get("portfolio", "base_currency").strip().upper()
    if len(base_currency) != 3:
        raise ConfigurationError("portfolio.base_currency must be an ISO currency code")
    portfolio = PortfolioSettings(
        base_currency=base_currency,
        initial_capital=_decimal(parser, "portfolio", "initial_capital", minimum=Decimal("0.01")),
    )
    risk = RiskSettings(
        margin_of_safety_pct=_decimal(parser, "risk", "margin_of_safety_pct"),
        maximum_single_position_pct=_decimal(
            parser, "risk", "maximum_single_position_pct", maximum=Decimal("100")
        ),
        maximum_short_position_pct=_decimal(
            parser, "risk", "maximum_short_position_pct", maximum=Decimal("100")
        ),
        maximum_options_premium_risk_pct=_decimal(
            parser, "risk", "maximum_options_premium_risk_pct", maximum=Decimal("100")
        ),
        maximum_pair_gross_exposure_pct=_decimal(
            parser, "risk", "maximum_pair_gross_exposure_pct", maximum=Decimal("200")
        ),
        maximum_total_gross_exposure_pct=_decimal(
            parser, "risk", "maximum_total_gross_exposure_pct", maximum=Decimal("1000")
        ),
        maximum_active_strategies=_positive_int(parser, "risk", "maximum_active_strategies"),
        maximum_daily_turnover_pct=_decimal(
            parser, "risk", "maximum_daily_turnover_pct", maximum=Decimal("1000")
        ),
        allowed_instruments=_csv_values(parser, "risk", "allowed_instruments"),
        allowed_exchanges=_csv_values(parser, "risk", "allowed_exchanges"),
        allowed_currencies=_csv_values(parser, "risk", "allowed_currencies"),
        minimum_option_open_interest=_positive_int(
            parser, "risk", "minimum_option_open_interest", allow_zero=True
        ),
        minimum_option_volume=_positive_int(
            parser, "risk", "minimum_option_volume", allow_zero=True
        ),
    )
    if not set(risk.allowed_instruments).issubset({"equity", "option"}):
        raise ConfigurationError("risk.allowed_instruments contains an unsupported instrument")
    if any(
        len(value) != 4 or not value.isalnum() or value != value.upper()
        for value in risk.allowed_exchanges
    ):
        raise ConfigurationError("risk.allowed_exchanges must contain uppercase venue MICs")
    if any(
        len(value) != 3 or not value.isalpha() or value != value.upper()
        for value in risk.allowed_currencies
    ):
        raise ConfigurationError("risk.allowed_currencies must contain uppercase ISO currencies")
    configured_mics = {mic for mic, _ in market.calendars}
    missing_calendars = sorted(set(risk.allowed_exchanges) - configured_mics)
    if missing_calendars:
        raise ConfigurationError(f"allowed exchanges lack calendars: {missing_calendars}")
    if portfolio.base_currency not in risk.allowed_currencies:
        raise ConfigurationError("portfolio.base_currency must be an allowed risk currency")
    orders = OrderSettings(
        default_fill_policy=_choice(
            parser,
            "orders",
            "default_fill_policy",
            frozenset({"next_open", "limit_touch", "quote_mid"}),
        ),
        default_order_type=_choice(
            parser, "orders", "default_order_type", frozenset({"market", "limit"})
        ),
        slippage_model=_choice(parser, "orders", "slippage_model", frozenset({"fixed_bps"})),
        slippage_bps=_decimal(parser, "orders", "slippage_bps"),
        fee_model=_choice(parser, "orders", "fee_model", frozenset({"fixed_plus_bps"})),
        fixed_fee=_decimal(parser, "orders", "fixed_fee"),
        variable_fee_bps=_decimal(parser, "orders", "variable_fee_bps"),
        option_quote_freshness=timedelta(
            minutes=_positive_int(parser, "orders", "option_quote_freshness_minutes")
        ),
        order_expiry=timedelta(hours=_positive_int(parser, "orders", "order_expiry_hours")),
    )
    if orders.default_fill_policy != "next_open" or orders.default_order_type != "market":
        raise ConfigurationError("version-1 defaults must be next_open and market")
    operations = OperationSettings(
        lease_duration=timedelta(minutes=_positive_int(parser, "operations", "lease_minutes")),
        default_max_attempts=_positive_int(parser, "operations", "default_max_attempts"),
        maximum_llm_operations_per_run=_positive_int(
            parser, "operations", "maximum_llm_operations_per_run"
        ),
        maximum_model_budget_usd_per_run=_decimal(
            parser, "operations", "maximum_model_budget_usd_per_run"
        ),
    )
    raw_command = parser.get("classifier", "command", fallback="").strip()
    classifier = ClassifierSettings(
        command=tuple(shlex.split(raw_command)),
        model=parser.get("classifier", "model", fallback="").strip(),
        timeout_seconds=_positive_int(parser, "classifier", "timeout_seconds"),
    )
    if bool(classifier.command) != bool(classifier.model):
        raise ConfigurationError("classifier.command and classifier.model must be set together")
    return market, indicators, portfolio, risk, orders, operations, classifier


def _load_hermes_settings(parser: configparser.ConfigParser) -> HermesSettings:
    """Validate the non-interactive Hermes command without accepting shell syntax."""

    command = tuple(shlex.split(parser.get("hermes", "command")))
    arguments = tuple(shlex.split(parser.get("hermes", "arguments")))
    toolsets = _csv_values(parser, "hermes", "toolsets")
    required_skill = parser.get("hermes", "require_native_skill").strip()
    required_version = parser.get("hermes", "native_skill_version").strip()
    inference_environment = _csv_values(parser, "hermes", "inference_environment")
    if command != ("hermes", "chat"):
        raise ConfigurationError("hermes.command must be exactly the hermes chat entry point")
    if arguments != ("--quiet", "--yolo"):
        raise ConfigurationError("hermes.arguments must be exactly --quiet --yolo")
    if set(toolsets) != {"file", "terminal", "web"}:
        raise ConfigurationError("hermes.toolsets must be exactly web,file,terminal")
    if required_skill != "llm-wiki" or not required_version:
        raise ConfigurationError("Hermes must require a versioned native llm-wiki skill")
    forbidden_names = {
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "TELEGRAM_BOT_TOKEN",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
        "ACTIONS_RUNTIME_TOKEN",
    }
    if any(
        not re.fullmatch(r"[A-Z][A-Z0-9_]*", name)
        or name in forbidden_names
        or any(marker in name for marker in ("BROKER", "DEPLOY", "TELEGRAM", "GITHUB"))
        for name in inference_environment
    ):
        raise ConfigurationError("hermes.inference_environment contains a forbidden name")
    return HermesSettings(
        command=command,
        arguments=arguments,
        toolsets=toolsets,
        required_native_skill=required_skill,
        required_native_skill_version=required_version,
        inference_environment=inference_environment,
        maximum_turns=_positive_int(parser, "hermes", "maximum_turns"),
        timeout_seconds=_positive_int(parser, "hermes", "timeout_seconds"),
    )


def _load_telegram_settings(parser: configparser.ConfigParser) -> TelegramSettings:
    """Load transport limits while keeping bot credentials outside config.ini."""

    settings = TelegramSettings(
        maximum_attempts=_positive_int(parser, "telegram", "maximum_attempts"),
        timeout_seconds=_positive_int(parser, "telegram", "timeout_seconds"),
        message_limit=_positive_int(parser, "telegram", "message_limit"),
    )
    if settings.maximum_attempts > 10:
        raise ConfigurationError("telegram.maximum_attempts must be <= 10")
    if settings.message_limit > 4096:
        raise ConfigurationError("telegram.message_limit must be <= 4096")
    return settings


def _load_settings_unchecked(
    repository_root: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Settings:
    """Load config.ini, resolve paths, and fail closed unless paper mode is explicit."""

    root = find_repository_root(repository_root)
    environment = os.environ if environ is None else environ
    parser = configparser.ConfigParser(interpolation=None)
    config_path = root / "config.ini"
    if not parser.read(config_path, encoding="utf-8"):
        raise ConfigurationError(f"missing configuration file: {config_path}")
    _require_paper_mode(parser, environment)

    data = _resolve_inside(root, parser.get("paths", "data_dir"), "data_dir")
    schemas = _resolve_inside(root, parser.get("paths", "schemas_dir"), "schemas_dir")
    skills = _resolve_inside(root, parser.get("paths", "skills_dir"), "skills_dir")

    wiki_setting = environment.get("WIKI_PATH", parser.get("paths", "wiki_path"))
    wiki_setting = Template(wiki_setting).safe_substitute(dict(environment))
    wiki = _resolve_inside(root, wiki_setting, "WIKI_PATH")
    expected_wiki = (root / "data" / "wiki").resolve()
    if wiki != expected_wiki:
        raise ConfigurationError(f"WIKI_PATH must resolve to {expected_wiki}, got {wiki}")

    skill_values = parser.get("hermes", "skills_external_dirs").split(",")
    external_dirs = tuple(
        _resolve_inside(root, value.strip(), "skills.external_dirs")
        for value in skill_values
        if value.strip()
    )
    if skills not in external_dirs:
        raise ConfigurationError(
            "Hermes skills.external_dirs must include the repository skills path"
        )

    market, indicators, portfolio, risk, orders, operations, classifier = _load_runtime_settings(
        parser
    )
    hermes = _load_hermes_settings(parser)
    telegram = _load_telegram_settings(parser)

    return Settings(
        config=parser,
        paths=RepositoryPaths(root=root, data=data, wiki=wiki, schemas=schemas, skills=skills),
        paper_trading_only=True,
        hermes_external_skill_dirs=external_dirs,
        market_data=market,
        indicators=indicators,
        portfolio=portfolio,
        risk=risk,
        orders=orders,
        operations=operations,
        classifier=classifier,
        hermes=hermes,
        telegram=telegram,
    )


def load_settings(
    repository_root: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Settings:
    """Load and validate settings with one stable configuration-error boundary."""

    try:
        return _load_settings_unchecked(repository_root, environ)
    except ConfigurationError:
        raise
    except (configparser.Error, ValueError) as exc:
        raise ConfigurationError(f"invalid config.ini: {exc}") from exc
