"""Current-only research contracts, independent of trading and historical ledgers."""

from __future__ import annotations

import csv
import io
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit

import yaml

from papertrader.atomic_io import atomic_write_csv

Row = dict[str, str]
ResearchState = dict[str, list[Row]]


@dataclass(frozen=True)
class ResearchContract:
    path: str
    columns: tuple[str, ...]
    primary_key: tuple[str, ...]


def contracts(root: Path) -> dict[str, ResearchContract]:
    document = yaml.safe_load((root / "schemas/research_contracts.yaml").read_text())
    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError("invalid research contract version")
    result = {}
    for name, entry in document["contracts"].items():
        path = PurePosixPath(entry["path"])
        columns = tuple(entry["columns"])
        keys = tuple(entry["primary_key"])
        if (
            path.is_absolute()
            or ".." in path.parts
            or path.parts[0] != "data"
            or len(columns) != len(set(columns))
            or not set(keys) <= set(columns)
        ):
            raise ValueError(f"unsafe research contract: {name}")
        result[name] = ResearchContract(path.as_posix(), columns, keys)
    return result


def csv_bytes(contract: ResearchContract, rows: list[Row]) -> bytes:
    normalized = [
        {column: _normalize_newlines(value) for column, value in row.items()} for row in rows
    ]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=contract.columns, extrasaction="raise")
    writer.writeheader()
    writer.writerows(
        sorted(normalized, key=lambda row: tuple(row[key] for key in contract.primary_key))
    )
    return buffer.getvalue().encode("utf-8")


def _normalize_newlines(value: str) -> str:
    """Keep logical CSV prose stable across Git's CRLF worktree conversion."""

    return value.replace("\r\n", "\n").replace("\r", "\n")


def read_state(root: Path) -> ResearchState:
    result = {}
    for name, contract in contracts(root).items():
        path = root / contract.path
        if path.is_symlink():
            raise ValueError(f"symlink table: {contract.path}")
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != list(contract.columns):
                raise ValueError(f"header mismatch: {contract.path}")
            rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError(f"malformed CSV: {contract.path}")
        result[name] = [
            {column: _normalize_newlines(value) for column, value in row.items()} for row in rows
        ]
    return result


def write_state(root: Path, state: ResearchState) -> None:
    """Write a previously validated state in an isolated staging directory."""

    for name, contract in contracts(root).items():
        path = root / contract.path
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_csv(
            path,
            contract.columns,
            sorted(
                (
                    {column: _normalize_newlines(value) for column, value in row.items()}
                    for row in state[name]
                ),
                key=lambda row: tuple(row[key] for key in contract.primary_key),
            ),
            allowed_root=root,
        )


def timestamp(value: str) -> datetime:
    instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    offset = instant.utcoffset()
    if not value.endswith("Z") or offset is None or offset.total_seconds():
        raise ValueError("timestamp must be UTC ISO-8601 with Z")
    return instant


def decimal(value: str) -> Decimal:
    if not re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value):
        raise ValueError("expected a finite decimal string")
    number = Decimal(value)
    if not number.is_finite():
        raise ValueError("expected a finite decimal string")
    return number


def source_url(value: str) -> bool:
    parsed = urlsplit(value)
    return bool(
        parsed.scheme in {"http", "https"}
        and parsed.hostname
        and not parsed.username
        and not parsed.password
    )


def validate_state(
    root: Path, state: ResearchState, *, pages: Mapping[str, bytes] | None = None
) -> list[str]:
    """Validate identity, latest-only rows, citations, dates and honest valuation math."""

    errors: list[str] = []
    registry = contracts(root)
    if set(state) != set(registry):
        return ["research state has missing or unknown tables"]
    for name, contract in registry.items():
        seen: set[tuple[str, ...]] = set()
        for row in state[name]:
            if set(row) != set(contract.columns) or any("\x00" in value for value in row.values()):
                errors.append(f"{name}: invalid columns or NUL")
                continue
            key = tuple(row[column] for column in contract.primary_key)
            if not all(key) or key in seen:
                errors.append(f"{name}: missing or duplicate identity {key}")
            seen.add(key)
    if errors:
        return errors
    securities = {row["security_id"]: row for row in state["securities"]}
    ideas = {row["idea_id"]: row for row in state["ideas"]}
    sources = {row["source_id"]: row for row in state["source_registry"]}
    for row in state["source_registry"]:
        if not source_url(row["url"]):
            errors.append(f"source URL invalid: {row['source_id']}")
        if row["content_hash"] and not re.fullmatch(r"[a-f0-9]{64}", row["content_hash"]):
            errors.append(f"source hash invalid: {row['source_id']}")
        for column in ("checked_at", "published_at"):
            if row[column]:
                try:
                    timestamp(row[column])
                except ValueError:
                    errors.append(f"source date invalid: {row['source_id']}:{column}")
    for row in state["securities"]:
        if not row["issuer_id"] or not re.fullmatch(r"[A-Z0-9]{4}", row["venue_mic"]):
            errors.append(f"incomplete security identity: {row['security_id']}")
        if not re.fullmatch(r"[A-Z]{3}", row["currency"]):
            errors.append(f"invalid security currency: {row['security_id']}")
    for name in ("ideas", "relationships", "security_assessments"):
        for row in state[name]:
            for reference in filter(None, row["source_ids"].split("|")):
                if reference not in sources:
                    errors.append(f"{name}: unknown source {reference}")
    for row in state["relationships"]:
        if row["idea_id"] not in ideas or row["security_id"] not in securities:
            errors.append(f"unknown relationship endpoint: {row['relationship_id']}")
        if not row["mechanism"]:
            errors.append(f"unexplained relationship: {row['relationship_id']}")
    for name, directory in (("securities", "securities"), ("ideas", "ideas")):
        for row in state[name]:
            relative = row["research_page"]
            if not relative:
                if row.get("research_status", "unresearched") != "unresearched":
                    errors.append(f"missing research page: {row}")
                continue
            path = PurePosixPath(relative)
            if (
                path.is_absolute()
                or ".." in path.parts
                or path.parts[:3] != ("data", "wiki", directory)
                or path.suffix != ".md"
            ):
                errors.append(f"unsafe research page: {relative}")
                continue
            try:
                content = pages[relative] if pages is not None else (root / relative).read_bytes()
                text = content.decode("utf-8")
                metadata = yaml.safe_load(text[4:].split("\n---\n", 1)[0])
                if not text.startswith("---\n") or not isinstance(metadata, dict):
                    raise ValueError("frontmatter missing")
            except (KeyError, OSError, ValueError, yaml.YAMLError):
                errors.append(f"missing or invalid research page: {relative}")
                continue
            for target in re.findall(r"\[\[(securities/[^\]|#]+|ideas/[^\]|#]+)", text):
                referenced = f"data/wiki/{target.removesuffix('.md')}.md"
                exists = referenced in pages if pages is not None else (root / referenced).is_file()
                if not exists:
                    errors.append(f"broken entity wikilink: {relative} -> {target}")
    for row in state["security_assessments"]:
        security = securities.get(row["security_id"])
        if security is None or row["currency"] != security["currency"]:
            errors.append(f"assessment identity/currency mismatch: {row['security_id']}")
        try:
            if timestamp(row["valid_until"]) <= timestamp(row["assessed_at"]):
                raise ValueError("invalid assessment duration")
            if row["confidence"] not in {"low", "medium", "high"}:
                raise ValueError("invalid confidence")
            if row["research_status"] not in {"supported", "unrated", "valuation_unsupported"}:
                raise ValueError("invalid research status")
            if row["research_status"] == "supported":
                values = [decimal(row[f"{case}_fair_value"]) for case in ("bear", "base", "bull")]
                probabilities = [
                    decimal(row[f"{case}_probability_pct"]) for case in ("bear", "base", "bull")
                ]
                if (
                    values != sorted(values)
                    or min(values) < 0
                    or sum(probabilities) != 100
                    or min(probabilities) < 0
                    or max(probabilities) > 100
                    or not row["method"]
                    or not row["source_ids"]
                    or not row["method_rationale"]
                    or not row["thesis"]
                    or not all(row[f"{case}_assumptions"] for case in ("bear", "base", "bull"))
                    or decimal(row["horizon_months"]) <= 0
                ):
                    raise ValueError("incomplete/inconsistent supported scenarios")
            elif any(
                row[f"{case}_{field}"]
                for case in ("bear", "base", "bull")
                for field in ("fair_value", "probability_pct")
            ):
                raise ValueError("unsupported valuation contains invented scenarios")
        except (ValueError, InvalidOperation) as exc:
            errors.append(f"invalid assessment {row['security_id']}: {exc}")
    from papertrader.research_queue import entity_key, queue_limits

    limits = queue_limits(root)
    if len(state["research_queue"]) > limits.max_pending:
        errors.append("research queue exceeds configured pending cap")
    companies: set[tuple[str, str]] = set()
    for row in state["research_queue"]:
        entities: Mapping[str, Any] = securities if row["entity_type"] == "security" else ideas
        if row["entity_type"] not in {"security", "idea"} or row["entity_id"] not in entities:
            errors.append(f"unknown queued entity: {row['entity_id']}")
        if row["status"] not in {"pending", "running", "failed"}:
            errors.append(f"invalid queue status: {row['entity_id']}")
        try:
            company = entity_key(state, row["entity_type"], row["entity_id"])
            if company in companies:
                raise ValueError("duplicate company work")
            companies.add(company)
            if row["manual"] not in {"true", "false"} or not row["reasons"]:
                raise ValueError("missing queue reason or manual flag")
            if (
                not 0 <= int(row["priority"]) <= 100
                or not 0 <= int(row["attempts"]) <= limits.max_attempts
            ):
                raise ValueError("invalid queue priority or attempts")
            for column in ("created_at", "updated_at", "next_eligible_at"):
                timestamp(row[column])
            if row["status"] == "running":
                timestamp(row["lease_until"])
            elif row["lease_until"]:
                raise ValueError("inactive task has a lease")
        except ValueError as exc:
            errors.append(f"invalid queued entity {row['entity_id']}: {exc}")
    return errors
