from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.config import ConfigurationError, find_repository_root, load_settings


def test_settings_require_explicit_paper_mode(repository_root: Path) -> None:
    with pytest.raises(ConfigurationError, match="PAPER_TRADING_ONLY=true"):
        load_settings(repository_root, {})


def test_settings_resolve_canonical_wiki_and_skills(
    repository_root: Path, paper_environment: dict[str, str]
) -> None:
    settings = load_settings(repository_root, paper_environment)

    assert settings.paper_trading_only is True
    assert settings.paths.wiki == (repository_root / "data" / "wiki").resolve()
    assert settings.hermes_external_skill_dirs == ((repository_root / "skills").resolve(),)
    assert settings.market_data.price_retention_days == 365
    assert settings.market_data.minimum_sma_200_observations == 200
    assert settings.indicators.sma_periods == (20, 50, 200)
    assert settings.orders.default_fill_policy == "next_open"
    assert settings.portfolio.initial_capital == Decimal("100000.00")
    assert settings.allocation.mode == "active"
    assert settings.allocation.target_invested_pct == Decimal("60")
    assert settings.allocation.minimum_cash_reserve_pct == Decimal("25")
    assert settings.allocation.maximum_baseline_sleeve_pct == Decimal("30")
    assert settings.allocation.maximum_baseline_position_pct == Decimal("5")
    assert settings.allocation.minimum_confidence == "medium"
    assert settings.allocation.research_refresh_lead_days == 7
    assert settings.operations.maximum_llm_operations_per_run == 5
    assert settings.classifier.command == ("python", "-m", "papertrader.classifier_command")
    assert settings.classifier.model == "gpt-5.6-luna"
    assert settings.hermes.command == ("hermes", "chat")
    assert settings.hermes.arguments == ("--quiet", "--yolo")
    assert settings.hermes.provider == "openai-codex"
    assert settings.hermes.model == "gpt-5.6-sol"
    assert settings.hermes.inference_environment == ()
    assert set(settings.hermes.toolsets) == {"web", "file", "terminal"}
    assert settings.hermes.required_native_skill == "llm-wiki"
    assert settings.hermes.required_native_skill_version == "2.1.0"
    assert settings.hermes.maximum_turns == 90
    assert settings.telegram.maximum_attempts == 3
    assert settings.telegram.timeout_seconds == 15
    assert settings.telegram.message_limit == 32768


def test_settings_reject_noncanonical_wiki(
    repository_root: Path, paper_environment: dict[str, str]
) -> None:
    environment = paper_environment | {"WIKI_PATH": str(repository_root / "other-wiki")}

    with pytest.raises(ConfigurationError, match="WIKI_PATH must resolve"):
        load_settings(repository_root, environment)


def test_repository_root_discovery_from_nested_path(repository_root: Path) -> None:
    assert find_repository_root(repository_root / "data" / "wiki") == repository_root


def test_settings_reject_api_key_fallback_for_main_hermes_provider(
    sandbox_repository: Path,
    paper_environment: dict[str, str],
) -> None:
    path = sandbox_repository / "config.ini"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "inference_environment =", "inference_environment = OPENAI_API_KEY"
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="must be empty for openai-codex OAuth"):
        load_settings(
            sandbox_repository,
            paper_environment | {"WIKI_PATH": str(sandbox_repository / "data" / "wiki")},
        )


def test_settings_reject_contract_incompatible_price_retention(
    sandbox_repository: Path,
    paper_environment: dict[str, str],
) -> None:
    path = sandbox_repository / "config.ini"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "price_retention_days = 365", "price_retention_days = 364"
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="exactly 365"):
        load_settings(
            sandbox_repository,
            paper_environment | {"WIKI_PATH": str(sandbox_repository / "data" / "wiki")},
        )


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        (
            "minimum_cash_reserve_pct = 25",
            "minimum_cash_reserve_pct = 100",
            "must be below 100",
        ),
        (
            "maximum_baseline_sleeve_pct = 30",
            "maximum_baseline_sleeve_pct = 61",
            "must not exceed target_invested_pct",
        ),
        (
            "maximum_baseline_position_pct = 5",
            "maximum_baseline_position_pct = 11",
            "must not exceed the single-position limit",
        ),
        (
            "maximum_total_gross_exposure_pct = 100",
            "maximum_total_gross_exposure_pct = 59",
            "target_invested_pct must not exceed the total gross-exposure limit",
        ),
        (
            "maximum_deployment_per_run_pct = 15",
            "maximum_deployment_per_run_pct = 21",
            "must not exceed daily turnover",
        ),
        (
            "minimum_trade_pct = 1",
            "minimum_trade_pct = 6",
            "must not exceed the baseline position cap",
        ),
        ("mode = active", "mode = automatic", "allocation.mode"),
    ],
)
def test_settings_reject_unsafe_allocation_cross_limits(
    sandbox_repository: Path,
    paper_environment: dict[str, str],
    old: str,
    new: str,
    message: str,
) -> None:
    path = sandbox_repository / "config.ini"
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    with pytest.raises(ConfigurationError, match=message):
        load_settings(
            sandbox_repository,
            paper_environment | {"WIKI_PATH": str(sandbox_repository / "data" / "wiki")},
        )
