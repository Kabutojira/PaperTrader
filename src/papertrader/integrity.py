"""Repository schemas, layout, skill discovery, and runtime path-policy validation."""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath
from typing import cast

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.validators import validator_for

from papertrader.config import ConfigurationError, Settings, load_settings
from papertrader.models import CsvContract, DynamicCsvContract

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
    "schemas/decision_snapshot.schema.json",
    "schemas/operation_payload.schema.json",
    "schemas/youtube_scan.schema.json",
    "schemas/csv_contracts.yaml",
    "data/wiki/SCHEMA.md",
    "data/wiki/index.md",
    "data/wiki/log.md",
    "data/operations/operations_TODO.csv",
    "data/operations/operations_history.csv",
    "data/tables/youtube_channels.csv",
    "data/logs/log.txt",
    "data/published/actionable_signals.csv",
    "data/published/model_portfolio.csv",
    "data/issues.md",
)

RAW_WIKI_EXTENSIONS = frozenset({".md", ".txt", ".pdf", ".png", ".jpg", ".jpeg", ".webp"})
RUN_ARTIFACT_EXTENSIONS = frozenset({".json", ".md"})
LOG_EXTENSIONS = frozenset({".ndjson", ".txt"})
SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
ULID = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")


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


def load_dynamic_csv_contracts(repository_root: Path) -> tuple[DynamicCsvContract, ...]:
    """Load glob-based CSV contracts such as per-security rolling price files."""

    contract_path = repository_root / "schemas" / "csv_contracts.yaml"
    raw = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    root = _mapping(raw, "csv contract document")
    entries = _mapping(root.get("dynamic_contracts", {}), "dynamic_contracts")
    contracts: list[DynamicCsvContract] = []
    for raw_name, raw_entry in entries.items():
        if not isinstance(raw_name, str):
            raise ContractError("dynamic contract names must be strings")
        entry = _mapping(raw_entry, f"dynamic contract {raw_name}")
        raw_glob = entry.get("glob")
        raw_columns = entry.get("columns")
        if not isinstance(raw_glob, str):
            raise ContractError(f"dynamic contract {raw_name} glob must be a string")
        glob_path = PurePosixPath(raw_glob)
        if (
            glob_path.is_absolute()
            or ".." in glob_path.parts
            or not glob_path.parts
            or glob_path.parts[0] != "data"
            or not raw_glob.endswith(".csv")
        ):
            raise ContractError(
                f"dynamic contract {raw_name} glob must be repository-local under data/"
            )
        if not isinstance(raw_columns, list) or not all(
            isinstance(column, str) and column for column in raw_columns
        ):
            raise ContractError(f"dynamic contract {raw_name} columns must be non-empty strings")
        columns = cast(list[str], raw_columns)
        if len(columns) != len(set(columns)):
            raise ContractError(f"dynamic contract {raw_name} contains duplicate columns")
        contracts.append(DynamicCsvContract(name=raw_name, glob=raw_glob, columns=tuple(columns)))
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
    try:
        dynamic_contracts = load_dynamic_csv_contracts(repository_root)
    except (ContractError, OSError, yaml.YAMLError) as exc:
        errors.append(f"cannot load dynamic CSV contracts: {exc}")
        return errors
    for dynamic_contract in dynamic_contracts:
        for path in sorted(repository_root.glob(dynamic_contract.glob)):
            try:
                with path.open("r", encoding="utf-8", newline="") as handle:
                    header = next(csv.reader(handle), None)
            except (OSError, UnicodeError, csv.Error) as exc:
                errors.append(f"cannot read {path.relative_to(repository_root)}: {exc}")
                continue
            if header != list(dynamic_contract.columns):
                errors.append(
                    f"header mismatch for {path.relative_to(repository_root)}: "
                    f"expected {list(dynamic_contract.columns)!r}, got {header!r}"
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


def validate_agent_run_artifacts(repository_root: Path) -> list[str]:
    """Validate every retained agent manifest and every history reference to one."""

    errors: list[str] = []
    schema_path = repository_root / "schemas" / "agent_result.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return [f"cannot load agent result schema: {exc}"]
    seen: set[str] = set()
    for path in sorted((repository_root / "data" / "runs").glob("*/*/agent_result.json")):
        relative = path.relative_to(repository_root).as_posix()
        parts = path.relative_to(repository_root).parts
        if (
            len(parts) != 5
            or not SAFE_RUN_ID.fullmatch(parts[2])
            or not ULID.fullmatch(parts[3])
            or path.is_symlink()
        ):
            errors.append(f"invalid agent result path: {relative}")
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read agent result {relative}: {exc}")
            continue
        schema_errors = sorted(validator.iter_errors(value), key=lambda error: list(error.path))
        errors.extend(f"agent result {relative}: {error.message}" for error in schema_errors)
        if isinstance(value, dict) and value.get("operation_id") != parts[3]:
            errors.append(f"agent result identity does not match path: {relative}")
        seen.add(relative)
    try:
        history = read_csv_contract_rows(repository_root, "operations_history")
    except (ContractError, OSError, ValueError) as exc:
        return [*errors, f"cannot validate agent history result paths: {exc}"]
    for row in history:
        result_path = row["result_path"]
        if result_path and result_path not in seen:
            errors.append(f"history references a missing agent result: {result_path}")
    return errors


def validate_daily_run_artifacts(repository_root: Path) -> list[str]:
    """Validate retained daily/batch manifests and their canonical report links."""

    errors: list[str] = []
    validators: dict[str, Draft202012Validator] = {}
    for name in ("daily_run", "agent_batch"):
        path = repository_root / "schemas" / f"{name}.schema.json"
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            validators[name] = Draft202012Validator(schema, format_checker=FormatChecker())
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            return [f"cannot load {name} schema: {exc}"]
    daily_by_run: dict[str, Mapping[str, object]] = {}
    batch_runs: set[str] = set()
    report_owners: dict[str, tuple[str, str, str]] = {}
    for name in ("daily_run", "agent_batch"):
        for path in sorted((repository_root / "data" / "runs").glob(f"*/{name}.json")):
            relative = path.relative_to(repository_root).as_posix()
            run_id = path.parent.name
            if not SAFE_RUN_ID.fullmatch(run_id) or path.is_symlink():
                errors.append(f"invalid {name} path: {relative}")
                continue
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"cannot read {name} {relative}: {exc}")
                continue
            schema_errors = sorted(
                validators[name].iter_errors(value), key=lambda error: list(error.path)
            )
            errors.extend(f"{name} {relative}: {error.message}" for error in schema_errors)
            if not isinstance(value, dict) or value.get("run_id") != run_id:
                errors.append(f"{name} identity does not match path: {relative}")
                continue
            if name == "daily_run":
                daily_by_run[run_id] = value
            else:
                batch_runs.add(run_id)
    for run_id, manifest in daily_by_run.items():
        status = manifest.get("status")
        report_path = manifest.get("report_path")
        if status in {"succeeded", "degraded"}:
            if run_id not in batch_runs:
                errors.append(f"completed daily run lacks agent batch: {run_id}")
            if not isinstance(report_path, str) or not (repository_root / report_path).is_file():
                errors.append(f"completed daily run lacks canonical report: {run_id}")
            snapshot_id = manifest.get("snapshot_id")
            if isinstance(snapshot_id, str) and snapshot_id:
                snapshot_path = (
                    repository_root / "data" / "runs" / run_id / "decision_snapshot.json"
                )
                if snapshot_path.is_symlink() or not snapshot_path.is_file():
                    errors.append(f"completed daily run lacks its decision snapshot: {run_id}")
                else:
                    try:
                        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError) as exc:
                        errors.append(f"cannot read daily decision snapshot {run_id}: {exc}")
                    else:
                        if not isinstance(snapshot, dict) or (
                            snapshot.get("snapshot_id") != snapshot_id
                            or snapshot.get("run_id") != run_id
                            or snapshot.get("as_of") != manifest.get("completed_at")
                        ):
                            errors.append(f"daily decision snapshot identity mismatch: {run_id}")
                completed_at = manifest.get("completed_at")
                if isinstance(report_path, str) and isinstance(completed_at, str):
                    owner = report_owners.get(report_path)
                    candidate = (completed_at, run_id, snapshot_id)
                    if owner is None or candidate[:2] > owner[:2]:
                        report_owners[report_path] = candidate
    for report_path, (_, run_id, snapshot_id) in report_owners.items():
        path = repository_root / report_path
        if not path.is_file():
            continue
        try:
            report = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read daily report {run_id}: {exc}")
        else:
            if f'snapshot_id: "{snapshot_id}"' not in report:
                errors.append(f"daily report snapshot identity mismatch: {run_id}")
    try:
        run_rows = read_csv_contract_rows(repository_root, "runs")
    except (ContractError, OSError, ValueError) as exc:
        return [*errors, f"cannot validate daily run history: {exc}"]
    for row in run_rows:
        if row["run_id"] not in daily_by_run:
            errors.append(f"run history references a missing daily manifest: {row['run_id']}")
    return errors


def validate_youtube_scan_artifacts(repository_root: Path) -> list[str]:
    """Validate retained curated-source scans and every referenced queue identity."""

    errors: list[str] = []
    schema_path = repository_root / "schemas" / "youtube_scan.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return [f"cannot load youtube_scan schema: {exc}"]
    try:
        operation_rows = {
            row["operation_id"]: row
            for table in ("operations_todo", "operations_history")
            for row in read_csv_contract_rows(repository_root, table)
        }
    except (ContractError, OSError, ValueError) as exc:
        return [f"cannot validate YouTube scan operations: {exc}"]
    for path in sorted((repository_root / "data" / "runs").glob("*/youtube_scan.json")):
        relative = path.relative_to(repository_root).as_posix()
        run_id = path.parent.name
        if not SAFE_RUN_ID.fullmatch(run_id) or path.is_symlink():
            errors.append(f"invalid youtube_scan path: {relative}")
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read youtube_scan {relative}: {exc}")
            continue
        schema_errors = sorted(validator.iter_errors(value), key=lambda error: list(error.path))
        errors.extend(f"youtube_scan {relative}: {error.message}" for error in schema_errors)
        if not isinstance(value, dict) or value.get("run_id") != run_id:
            errors.append(f"youtube_scan identity does not match path: {relative}")
            continue
        channels = value.get("channels")
        if not isinstance(channels, list) or not all(isinstance(row, dict) for row in channels):
            continue
        operation_ids = [
            operation_id
            for channel in channels
            for operation_id in channel.get("operation_ids", [])
            if isinstance(operation_id, str)
        ]
        failures = sum(channel.get("status") == "failed" for channel in channels)
        if len(operation_ids) != len(set(operation_ids)):
            errors.append(f"youtube_scan contains duplicate operation IDs: {run_id}")
        if value.get("operation_count") != len(operation_ids):
            errors.append(f"youtube_scan operation count mismatch: {run_id}")
        if value.get("failure_count") != failures:
            errors.append(f"youtube_scan failure count mismatch: {run_id}")
        expected_status = "degraded" if failures else "succeeded"
        if (
            value.get("status") in {"succeeded", "degraded"}
            and value.get("status") != expected_status
        ):
            errors.append(f"youtube_scan status/failure mismatch: {run_id}")
        for channel in channels:
            if channel.get("status") == "failed" and channel.get("previous_cursor") != channel.get(
                "next_cursor"
            ):
                errors.append(
                    f"failed youtube_scan channel advanced its cursor: {channel.get('channel_id')}"
                )
            discovered = channel.get("discovered_video_ids", [])
            if not isinstance(discovered, list):
                continue
            for operation_id in channel.get("operation_ids", []):
                if not isinstance(operation_id, str):
                    continue
                row = operation_rows.get(operation_id)
                if row is None:
                    errors.append(f"youtube_scan references unknown operation: {operation_id}")
                    continue
                try:
                    payload_path = repository_root.joinpath(
                        *PurePosixPath(row["payload_path"]).parts
                    )
                    payload = json.loads(payload_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError, KeyError) as exc:
                    errors.append(
                        f"cannot read youtube_scan operation payload {operation_id}: {exc}"
                    )
                    continue
                inputs = payload.get("inputs") if isinstance(payload, dict) else None
                if (
                    row["operation_type"] != "wiki_ingest"
                    or not isinstance(inputs, dict)
                    or inputs.get("source_kind") != "youtube_video"
                    or inputs.get("channel_id") != channel.get("channel_id")
                    or inputs.get("video_id") not in discovered
                ):
                    errors.append(f"youtube_scan operation identity mismatch: {operation_id}")
    return errors


def read_csv_contract_rows(repository_root: Path, name: str) -> list[dict[str, str]]:
    """Read a canonical table locally without importing the circular table module."""

    contract = next(
        (candidate for candidate in load_csv_contracts(repository_root) if candidate.name == name),
        None,
    )
    if contract is None:
        raise ContractError(f"unknown CSV contract: {name}")
    path = repository_root.joinpath(*contract.path.parts)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(contract.columns):
            raise ContractError(f"header mismatch for {contract.path}")
        rows = list(reader)
    if any(None in row for row in rows):
        raise ContractError(f"surplus values in {contract.path}")
    return rows


def publication_requires_current_state(
    repository_root: Path, environment: Mapping[str, str]
) -> bool:
    """Return whether publication hashes must match the current canonical state.

    Only a controller-created operation directory inside its matching prepared daily run may
    defer freshness until finalization regenerates the publication. Invalid, completed, or
    standalone contexts fail closed and require the current-state comparison.
    """

    run_id = environment.get("PAPERTRADER_AUDIT_RUN_ID", "")
    operation_id = environment.get("PAPERTRADER_AUDIT_OPERATION_ID", "")
    if not SAFE_RUN_ID.fullmatch(run_id) or not ULID.fullmatch(operation_id):
        return True
    run_directory = repository_root / "data" / "runs" / run_id
    operation_directory = run_directory / operation_id
    manifest_path = run_directory / "daily_run.json"
    if (
        run_directory.is_symlink()
        or operation_directory.is_symlink()
        or not operation_directory.is_dir()
        or manifest_path.is_symlink()
        or not manifest_path.is_file()
    ):
        return True
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True
    return not (
        isinstance(manifest, dict)
        and manifest.get("run_id") == run_id
        and manifest.get("status") == "prepared"
        and manifest.get("completed_at") == ""
    )


def validate_integrity(
    repository_root: Path,
    environment: Mapping[str, str],
    *,
    require_current_publication: bool | None = None,
) -> list[str]:
    """Run repository contracts plus deterministic queue/accounting checks."""

    errors: list[str] = []
    settings: Settings | None = None
    try:
        settings = load_settings(repository_root, environment)
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
    errors.extend(validate_agent_run_artifacts(repository_root))
    errors.extend(validate_daily_run_artifacts(repository_root))
    errors.extend(validate_youtube_scan_artifacts(repository_root))
    # Imported lazily because canonical table access resolves contracts from this module.
    from papertrader.advice import validate_advice
    from papertrader.allocation import validate_allocation_state
    from papertrader.market_data import validate_fx_data
    from papertrader.orders import validate_order_state
    from papertrader.portfolio import reconcile_portfolio
    from papertrader.queue import validate_queue

    errors.extend(validate_queue(repository_root))
    errors.extend(validate_order_state(repository_root))
    if settings is not None:
        errors.extend(validate_allocation_state(repository_root, settings))
        errors.extend(validate_fx_data(repository_root, settings))
    publication_is_current = (
        publication_requires_current_state(repository_root, environment)
        if require_current_publication is None
        else require_current_publication
    )
    errors.extend(validate_advice(repository_root, require_current_state=publication_is_current))
    errors.extend(reconcile_portfolio(repository_root))
    return errors


def is_runtime_path_allowed(raw_path: str) -> bool:
    """Return whether a repository-relative path is in the automated commit whitelist."""

    if not raw_path or "\\" in raw_path or "\x00" in raw_path:
        return False
    raw_parts = raw_path.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        return False
    path = PurePosixPath(raw_path)
    if path == PurePosixPath(".papertrader/credentials/openai-oauth-auth.json.age"):
        return True
    if path.is_absolute() or not path.parts or path.parts[0] != "data":
        return False

    if path.suffix == ".csv":
        return True
    if path == PurePosixPath("data/issues.md"):
        return True
    if path == PurePosixPath("data/published/decision_snapshot.json"):
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
    command = ["git", "diff", "--name-only", "--diff-filter=ACDMRTUXB", "-z"]
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
