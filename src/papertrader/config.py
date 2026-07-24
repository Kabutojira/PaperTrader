"""Load repository-local settings and enforce the paper-only startup boundary."""

from __future__ import annotations

import configparser
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from string import Template


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
class Settings:
    """Validated application settings needed by the Step 1 command surface."""

    config: configparser.ConfigParser
    paths: RepositoryPaths
    paper_trading_only: bool
    hermes_external_skill_dirs: tuple[Path, ...]


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


def load_settings(
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

    return Settings(
        config=parser,
        paths=RepositoryPaths(root=root, data=data, wiki=wiki, schemas=schemas, skills=skills),
        paper_trading_only=True,
        hermes_external_skill_dirs=external_dirs,
    )
