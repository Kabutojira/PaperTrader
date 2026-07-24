from __future__ import annotations

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


def test_settings_reject_noncanonical_wiki(
    repository_root: Path, paper_environment: dict[str, str]
) -> None:
    environment = paper_environment | {"WIKI_PATH": str(repository_root / "other-wiki")}

    with pytest.raises(ConfigurationError, match="WIKI_PATH must resolve"):
        load_settings(repository_root, environment)


def test_repository_root_discovery_from_nested_path(repository_root: Path) -> None:
    assert find_repository_root(repository_root / "data" / "wiki") == repository_root
