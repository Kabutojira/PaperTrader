"""Canonical CSV access with stable columns and atomic repository-local writes."""

from __future__ import annotations

import csv
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from papertrader.atomic_io import atomic_write_csv
from papertrader.integrity import load_csv_contracts
from papertrader.models import CsvContract
from papertrader.utils import CanonicalValueError, require_columns


def contract_by_name(repository_root: Path, name: str) -> CsvContract:
    """Load one named CSV contract."""

    matches = [
        contract for contract in load_csv_contracts(repository_root) if contract.name == name
    ]
    if len(matches) != 1:
        raise CanonicalValueError(f"unknown CSV contract: {name}")
    return matches[0]


def contract_path(repository_root: Path, contract: CsvContract) -> Path:
    """Resolve a canonical CSV contract beneath the repository root."""

    return repository_root.joinpath(*contract.path.parts)


def read_csv(
    path: Path,
    columns: Sequence[str],
    *,
    legacy_columns: Sequence[Sequence[str]] = (),
    legacy_renames: Mapping[str, str] | None = None,
) -> list[dict[str, str]]:
    """Read an RFC 4180 CSV and require its exact ordered header."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        legacy_assessment_prefix = (
            path.name == "security_assessments.csv"
            and reader.fieldnames is not None
            and list(columns[: len(reader.fieldnames)]) == reader.fieldnames
            and reader.fieldnames[-1:] == ["run_id"]
        )
        legacy_header = reader.fieldnames is not None and tuple(reader.fieldnames) in {
            tuple(candidate) for candidate in legacy_columns
        }
        if (
            reader.fieldnames != list(columns)
            and not legacy_assessment_prefix
            and not legacy_header
        ):
            raise CanonicalValueError(
                f"header mismatch for {path}: expected {list(columns)!r}, got {reader.fieldnames!r}"
            )
        rows = list(reader)
    aliases = legacy_renames or {}
    if legacy_header:
        rows = [
            {aliases.get(column, column): value for column, value in row.items()} for row in rows
        ]
    for index, row in enumerate(rows, start=2):
        if None in row:
            raise CanonicalValueError(f"row {index} in {path} has surplus values")
        for column in columns:
            row.setdefault(column, "")
        require_columns(row, columns, label=f"row {index} in {path}")
        if any("\x00" in value for value in row.values()):
            raise CanonicalValueError(f"row {index} in {path} contains a NUL byte")
    return rows


def read_table(repository_root: Path, name: str) -> list[dict[str, str]]:
    """Read one canonical table by contract name."""

    contract = contract_by_name(repository_root, name)
    return read_csv(
        contract_path(repository_root, contract),
        contract.columns,
        legacy_columns=contract.legacy_columns,
        legacy_renames=dict(contract.legacy_renames),
    )


def _normalized_rows(
    rows: Iterable[Mapping[str, object]], columns: Sequence[str], *, label: str
) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        source = dict(row)
        legacy_assessment = (
            label == "security_assessments"
            and "run_id" in columns
            and set(source) == set(columns[: columns.index("run_id") + 1])
        )
        if legacy_assessment:
            for column in columns:
                source.setdefault(column, "")
            source["assessment_schema_version"] = "legacy_v1"
        require_columns(source, columns, label=f"{label} row {index}")
        converted: dict[str, object] = {}
        for column in columns:
            value = source[column]
            if value is None:
                value = ""
            if isinstance(value, float):
                raise CanonicalValueError(
                    f"{label} row {index} field {column} must not be a binary float"
                )
            converted[column] = value
        normalized.append(converted)
    return normalized


def write_table(
    repository_root: Path,
    name: str,
    rows: Iterable[Mapping[str, object]],
) -> None:
    """Validate and atomically replace one mutable or generated table."""

    contract = contract_by_name(repository_root, name)
    if contract.append_only:
        raise CanonicalValueError(f"cannot replace append-only table {name}")
    normalized = _normalized_rows(rows, contract.columns, label=name)
    atomic_write_csv(
        contract_path(repository_root, contract),
        contract.columns,
        normalized,
        allowed_root=repository_root,
    )


def append_unique(
    repository_root: Path,
    name: str,
    rows: Iterable[Mapping[str, object]],
    *,
    key_columns: Sequence[str],
) -> int:
    """Append immutable rows, treating identical retries as idempotent conflicts as errors."""

    contract = contract_by_name(repository_root, name)
    if not contract.append_only:
        raise CanonicalValueError(f"{name} is not an append-only contract")
    if not key_columns or any(column not in contract.columns for column in key_columns):
        raise CanonicalValueError(f"invalid append key columns for {name}: {tuple(key_columns)!r}")
    existing = read_table(repository_root, name)
    additions = _normalized_rows(rows, contract.columns, label=name)
    by_key: dict[tuple[str, ...], Mapping[str, object]] = {}
    for existing_row in existing:
        key = tuple(existing_row[column] for column in key_columns)
        if key in by_key:
            raise CanonicalValueError(f"duplicate immutable {name} key {key!r}")
        by_key[key] = existing_row
    accepted: list[Mapping[str, object]] = []
    for addition in additions:
        key = tuple(str(addition[column]) for column in key_columns)
        if any(not value for value in key):
            raise CanonicalValueError(f"immutable {name} key contains an empty value: {key!r}")
        previous = by_key.get(key)
        if previous is not None:
            if {column: str(previous[column]) for column in contract.columns} != {
                column: str(addition[column]) for column in contract.columns
            }:
                raise CanonicalValueError(f"immutable {name} row conflicts at key {key!r}")
            continue
        by_key[key] = addition
        accepted.append(addition)
    if accepted:
        atomic_write_csv(
            contract_path(repository_root, contract),
            contract.columns,
            [*existing, *accepted],
            allowed_root=repository_root,
        )
    return len(accepted)


def replace_keyed_row(
    repository_root: Path,
    name: str,
    row: Mapping[str, object],
    *,
    key_columns: Sequence[str],
    sort_columns: Sequence[str] = (),
) -> None:
    """Insert or replace one mutable reference row and preserve deterministic ordering."""

    contract = contract_by_name(repository_root, name)
    if contract.append_only:
        raise CanonicalValueError(f"cannot replace rows in append-only table {name}")
    normalized = _normalized_rows([row], contract.columns, label=name)[0]
    key = tuple(str(normalized[column]) for column in key_columns)
    existing = read_table(repository_root, name)
    output: list[Mapping[str, object]] = [
        candidate
        for candidate in existing
        if tuple(candidate[column] for column in key_columns) != key
    ]
    output.append(normalized)
    if sort_columns:
        output.sort(key=lambda candidate: tuple(str(candidate[column]) for column in sort_columns))
    write_table(repository_root, name, output)
