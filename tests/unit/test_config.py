from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from papertrader.config import ConfigurationError, find_repository_root, load_settings


def test_settings_load_without_a_mode_environment_switch(repository_root: Path) -> None:
    settings = load_settings(
        repository_root,
        {"WIKI_PATH": str(repository_root / "data" / "wiki")},
    )

    assert settings.paths.root == repository_root


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
    assert settings.indicators.volume_zscore_threshold == Decimal("2")
    assert settings.orders.default_fill_policy == "next_open"
    assert settings.portfolio.initial_capital == Decimal("10000.00")
    assert settings.allocation.mode == "active"
    assert settings.allocation.target_invested_pct == Decimal("60")
    assert settings.allocation.minimum_cash_reserve_pct == Decimal("25")
    assert settings.allocation.maximum_baseline_sleeve_pct == Decimal("30")
    assert settings.allocation.maximum_baseline_position_pct == Decimal("5")
    assert settings.allocation.minimum_base_upside_pct == Decimal("10")
    assert settings.allocation.minimum_upside_downside_ratio == Decimal("1")
    assert settings.allocation.minimum_confidence == "medium"
    assert settings.allocation.research_refresh_lead_days == 7
    assert settings.operations.maximum_llm_operations_per_run == 20
    assert settings.classifier.command == ("python", "-m", "papertrader.classifier_command")
    assert settings.classifier.model == "gpt-5.6-luna"
    assert settings.youtube.enabled is True
    assert settings.youtube.scan_bound == 50
    assert settings.youtube.seed_count == 5
    assert settings.youtube.bootstrap_priority == 60
    assert settings.youtube.discovery_priority == 65
    assert settings.youtube.followup_priority == 66
    assert settings.youtube.transcript_languages == ("en", "en-US", "en-GB")
    assert settings.youtube.transcript_attempts == 3
    assert settings.seekingalpha.enabled is True
    assert settings.seekingalpha.analysis_candidate_limit == 12
    assert settings.seekingalpha.news_candidate_limit == 12
    assert settings.seekingalpha.lookback_days == 3
    assert settings.seekingalpha.search_attempts == 3
    assert settings.seekingalpha.maximum_leads_per_day == 5
    assert settings.seekingalpha.maximum_new_securities_per_analysis == 2
    assert settings.seekingalpha.discovery_priority == 69
    assert settings.seekingalpha.analysis_priority == 67
    assert settings.seekingalpha.news_priority == 66
    assert settings.seekingalpha.followup_priority == 68
    assert settings.seekingalpha.direct_site_access is False
    assert settings.hermes.command == ("hermes", "chat")
    assert settings.hermes.arguments == ("--quiet", "--yolo")
    assert settings.hermes.provider == "openai-codex"
    assert settings.hermes.model == "gpt-5.6-sol"
    assert settings.hermes.inference_environment == ()
    assert set(settings.hermes.toolsets) == {"web", "file", "terminal"}
    assert settings.hermes.required_native_skill == "llm-wiki"
    assert settings.hermes.required_native_skill_version == "2.1.0"
    assert settings.hermes.maximum_turns == 180
    assert settings.hermes_auxiliary.web_extract_provider == "openai-codex"
    assert settings.hermes_auxiliary.web_extract_model == "gpt-5.6-terra"
    assert settings.hermes_auxiliary.web_extract_reasoning_effort == "low"
    assert settings.hermes_auxiliary.web_extract_api_key_env == ""
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


def test_settings_accept_environment_hermes_overrides(
    repository_root: Path, paper_environment: dict[str, str]
) -> None:
    settings = load_settings(
        repository_root,
        paper_environment
        | {
            "MAX_OPERATIONS": "240",
            "AUXILIARY_MODEL": "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
        },
    )

    assert settings.hermes.maximum_turns == 240
    assert settings.hermes.inference_environment == ("OPENROUTER_API_KEY",)
    assert settings.hermes_auxiliary.web_extract_provider == "openrouter"
    assert settings.hermes_auxiliary.web_extract_model == ("nvidia/nemotron-3-ultra-550b-a55b:free")
    assert settings.hermes_auxiliary.web_extract_api_key_env == "OPENROUTER_API_KEY"


@pytest.mark.parametrize("value", ["0", "-1", "many"])
def test_settings_reject_invalid_max_operations(
    repository_root: Path,
    paper_environment: dict[str, str],
    value: str,
) -> None:
    with pytest.raises(ConfigurationError, match="MAX_OPERATIONS must be a positive integer"):
        load_settings(repository_root, paper_environment | {"MAX_OPERATIONS": value})


@pytest.mark.parametrize(
    "value",
    ["gpt-5.6-terra", "anthropic:claude", "openai-codex:", "openai-codex:gpt terra"],
)
def test_settings_reject_invalid_auxiliary_model(
    repository_root: Path,
    paper_environment: dict[str, str],
    value: str,
) -> None:
    with pytest.raises(ConfigurationError, match="AUXILIARY_MODEL"):
        load_settings(repository_root, paper_environment | {"AUXILIARY_MODEL": value})


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


def test_settings_require_exactly_three_youtube_transcript_attempts(
    sandbox_repository: Path,
    paper_environment: dict[str, str],
) -> None:
    path = sandbox_repository / "config.ini"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "transcript_attempts = 3", "transcript_attempts = 4"
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="must be exactly 3"):
        load_settings(
            sandbox_repository,
            paper_environment | {"WIKI_PATH": str(sandbox_repository / "data" / "wiki")},
        )


def test_settings_forbid_seekingalpha_direct_site_access(
    sandbox_repository: Path,
    paper_environment: dict[str, str],
) -> None:
    path = sandbox_repository / "config.ini"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "direct_site_access = false", "direct_site_access = true"
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="direct_site_access must remain false"):
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
