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
    assert settings.operations.maximum_llm_operations_per_run == 5
    assert settings.hermes.command == ("hermes", "chat")
    assert settings.hermes.arguments == ("--quiet", "--yolo")
    assert set(settings.hermes.toolsets) == {"web", "file", "terminal"}
    assert settings.hermes.required_native_skill == "llm-wiki"
    assert settings.hermes.required_native_skill_version == "2.1.0"
    assert settings.hermes.maximum_turns == 60
    assert settings.telegram.maximum_attempts == 3
    assert settings.telegram.timeout_seconds == 15
    assert settings.telegram.message_limit == 4096


def test_settings_reject_noncanonical_wiki(
    repository_root: Path, paper_environment: dict[str, str]
) -> None:
    environment = paper_environment | {"WIKI_PATH": str(repository_root / "other-wiki")}

    with pytest.raises(ConfigurationError, match="WIKI_PATH must resolve"):
        load_settings(repository_root, environment)


def test_repository_root_discovery_from_nested_path(repository_root: Path) -> None:
    assert find_repository_root(repository_root / "data" / "wiki") == repository_root


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
