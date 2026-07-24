"""Repository schemas, layout, skill discovery, and runtime path-policy validation."""

from __future__ import annotations

import csv
import json
import os
import subprocess
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath
from typing import cast

import yaml
from jsonschema.validators import validator_for

from papertrader.config import ConfigurationError, Settings, load_settings
from papertrader.models import CsvContract

EXPECTED_SKILLS = (
    "papertrader-controller",
    "papertrader-wiki-ingest",
    "papertrader-opportunity-research",
    "papertrader-idea-research",
    "papertrader-security-research",
    "papertrader-relationship-research",
    "papertrader-strategy-research",
    "papertrader-execute-strategy",
)

REQUIRED_SKILL_SECTIONS = (
    "## Activation",
    "## Allowed scope",
    "## Required input",
    "## Procedure",
    "## Source hierarchy",
    "## Untrusted content",
    "## Output contract",
    "## Verification",
    "## Failure policy",
)

REQUIRED_LAYOUT = (
    "config.ini",
    "schemas/agent_result.schema.json",
    "schemas/operation_payload.schema.json",
    "schemas/csv_contracts.yaml",
    "data/wiki/SCHEMA.md",
    "data/wiki/index.md",
    "data/wiki/log.md",
    "data/operations/operations_TODO.csv",
    "data/operations/operations_history.csv",
    "data/logs/log.txt",
    "data/issues.md",
)

RAW_WIKI_EXTENSIONS = frozenset({".md", ".txt", ".pdf", ".png", ".jpg", ".jpeg", ".webp"})
RUN_ARTIFACT_EXTENSIONS = frozenset({".json", ".md"})
LOG_EXTENSIONS = frozenset({".ndjson", ".txt"})


class ContractError(ValueError):
    """Raised when a repository contract cannot be parsed."""


def _mapping(value: object, label: str) -> Mapping[object, object]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{label} must be a mapping")
    return value


def load_csv_contracts(repository_root: Path) -> tuple[CsvContract, ...]:
    """Load and structurally validate the canonical CSV registry."""

    contract_path = repository_root / "schemas" / "csv_contracts.yaml"
    raw = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    root = _mapping(raw, "csv contract document")
    if root.get("version") != 1:
        raise ContractError("csv contract version must be 1")
    entries = _mapping(root.get("contracts"), "contracts")

    contracts: list[CsvContract] = []
    seen_paths: set[PurePosixPath] = set()
    for raw_name, raw_entry in entries.items():
        if not isinstance(raw_name, str):
            raise ContractError("contract names must be strings")
        entry = _mapping(raw_entry, f"contract {raw_name}")
        raw_path = entry.get("path")
        raw_columns = entry.get("columns")
        if not isinstance(raw_path, str):
            raise ContractError(f"contract {raw_name} path must be a string")
        if not isinstance(raw_columns, list) or not all(
            isinstance(column, str) and column for column in raw_columns
        ):
            raise ContractError(f"contract {raw_name} columns must be non-empty strings")
        columns = cast(list[str], raw_columns)
        if len(columns) != len(set(columns)):
            raise ContractError(f"contract {raw_name} contains duplicate columns")
        path = PurePosixPath(raw_path)
        if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "data":
            raise ContractError(f"contract {raw_name} path must be repository-local under data/")
        if path.suffix != ".csv":
            raise ContractError(f"contract {raw_name} path must end in .csv")
        if path in seen_paths:
            raise ContractError(f"duplicate CSV contract path: {path}")
        seen_paths.add(path)
        contracts.append(
            CsvContract(
                name=raw_name,
                path=path,
                columns=tuple(columns),
                append_only=entry.get("append_only") is True,
                generated=entry.get("generated") is True,
            )
        )
    return tuple(contracts)


def validate_csv_files(repository_root: Path) -> list[str]:
    """Return errors for missing canonical CSVs or headers that differ byte-for-field."""

    errors: list[str] = []
    try:
        contracts = load_csv_contracts(repository_root)
    except (ContractError, OSError, yaml.YAMLError) as exc:
        return [f"cannot load CSV contracts: {exc}"]

    for contract in contracts:
        path = repository_root.joinpath(*contract.path.parts)
        if not path.is_file():
            errors.append(f"missing canonical CSV: {contract.path}")
            continue
        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle)
                header = next(reader, None)
        except (OSError, UnicodeError, csv.Error) as exc:
            errors.append(f"cannot read {contract.path}: {exc}")
            continue
        if header != list(contract.columns):
            errors.append(
                f"header mismatch for {contract.path}: expected {list(contract.columns)!r}, "
                f"got {header!r}"
            )
    return errors


def validate_json_schemas(repository_root: Path) -> list[str]:
    """Check that every JSON schema parses and is valid for its declared dialect."""

    errors: list[str] = []
    paths = sorted((repository_root / "schemas").glob("*.schema.json"))
    if not paths:
        return ["no JSON schemas found"]
    for path in paths:
        relative = path.relative_to(repository_root)
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            validator_type = validator_for(schema)
            validator_type.check_schema(schema)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            errors.append(f"invalid JSON schema {relative}: {exc}")
    return errors


def _load_skill_frontmatter(path: Path) -> Mapping[object, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ContractError("missing YAML frontmatter")
    frontmatter, _ = text[4:].split("\n---\n", maxsplit=1)
    metadata = _mapping(yaml.safe_load(frontmatter), "skill frontmatter")
    if set(metadata) != {"name", "description"}:
        raise ContractError("frontmatter must contain only name and description")
    if not isinstance(metadata.get("name"), str) or not isinstance(
        metadata.get("description"), str
    ):
        raise ContractError("skill name and description must be strings")
    return metadata


def validate_skills(repository_root: Path) -> list[str]:
    """Validate discovery metadata and required PaperTrader operating sections."""

    errors: list[str] = []
    for skill_name in EXPECTED_SKILLS:
        path = repository_root / "skills" / skill_name / "SKILL.md"
        if not path.is_file():
            errors.append(f"missing project skill: skills/{skill_name}/SKILL.md")
            continue
        try:
            metadata = _load_skill_frontmatter(path)
            text = path.read_text(encoding="utf-8")
        except (ContractError, OSError, UnicodeError, yaml.YAMLError) as exc:
            errors.append(f"invalid skill {skill_name}: {exc}")
            continue
        if metadata["name"] != skill_name:
            errors.append(f"skill folder/name mismatch for {skill_name}")
        for section in REQUIRED_SKILL_SECTIONS:
            if section not in text:
                errors.append(f"skill {skill_name} is missing {section}")
    return errors


def validate_layout(repository_root: Path) -> list[str]:
    """Check required files and reject symlinks anywhere in persistent data."""

    errors = [
        f"missing required path: {path}"
        for path in REQUIRED_LAYOUT
        if not (repository_root / path).exists()
    ]
    data_root = repository_root / "data"
    if data_root.exists():
        for current, directories, files in os.walk(data_root, followlinks=False):
            current_path = Path(current)
            for name in (*directories, *files):
                path = current_path / name
                if path.is_symlink():
                    errors.append(
                        f"symlink forbidden under data/: {path.relative_to(repository_root)}"
                    )
    return errors


def validate_integrity(repository_root: Path, environment: Mapping[str, str]) -> list[str]:
    """Run every repository-level Step 1 integrity check."""

    errors: list[str] = []
    try:
        settings: Settings = load_settings(repository_root, environment)
        if not settings.paths.wiki.is_dir():
            errors.append(f"WIKI_PATH does not exist: {settings.paths.wiki}")
        for skill_dir in settings.hermes_external_skill_dirs:
            if not skill_dir.is_dir():
                errors.append(f"Hermes external skill directory does not exist: {skill_dir}")
    except ConfigurationError as exc:
        errors.append(str(exc))
    errors.extend(validate_layout(repository_root))
    errors.extend(validate_csv_files(repository_root))
    errors.extend(validate_json_schemas(repository_root))
    errors.extend(validate_skills(repository_root))
    return errors


def is_runtime_path_allowed(raw_path: str) -> bool:
    """Return whether a repository-relative path is in the automated commit whitelist."""

    if not raw_path or "\\" in raw_path or "\x00" in raw_path:
        return False
    raw_parts = raw_path.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        return False
    path = PurePosixPath(raw_path)
    if path.is_absolute() or not path.parts or path.parts[0] != "data":
        return False

    if path.suffix == ".csv":
        return True
    if path == PurePosixPath("data/issues.md"):
        return True
    if len(path.parts) >= 3 and path.parts[1] == "wiki":
        if path.suffix == ".md":
            return True
        if path.parts[2] == "raw" and path.suffix in RAW_WIKI_EXTENSIONS:
            return True
    if len(path.parts) >= 3 and path.parts[1] in {"operations", "runs"}:
        return path.suffix in RUN_ARTIFACT_EXTENSIONS
    if len(path.parts) >= 3 and path.parts[1] == "logs":
        return path.suffix in LOG_EXTENSIONS
    return False


def validate_runtime_paths(paths: Iterable[str]) -> list[str]:
    """Return one deterministic error for every changed path outside the whitelist."""

    return [
        f"runtime path is not allowed: {path}"
        for path in paths
        if not is_runtime_path_allowed(path)
    ]


def changed_paths_from_git(
    repository_root: Path,
    *,
    staged: bool = False,
    base_ref: str | None = None,
    head_ref: str = "HEAD",
) -> tuple[str, ...]:
    """Read changed paths from Git using NUL delimiters so unusual names fail safely."""

    if staged and base_ref is not None:
        raise ValueError("--staged and --base-ref are mutually exclusive")
    command = ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", "-z"]
    if staged:
        command.append("--cached")
    elif base_ref is not None:
        command.append(f"{base_ref}..{head_ref}")
    else:
        raise ValueError("select --staged or provide --base-ref")
    result = subprocess.run(
        command,
        cwd=repository_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git diff failed: {message}")
    decoded = result.stdout.decode("utf-8", errors="surrogateescape")
    return tuple(path for path in decoded.split("\x00") if path)
