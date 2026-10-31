"""Dry-run-by-default conversion from pinned legacy data to current research contracts.

An explicit staging directory allows inspection without switching the active reader.
Production cutover uses the validated transaction controller introduced in M4.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import os
import re
import tarfile
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from papertrader.atomic_io import atomic_write_bytes
from papertrader.migration_inventory import _git
from papertrader.research_ratings import valuation_coverage
from papertrader.research_state import (
    ResearchState,
    Row,
    contracts,
    csv_bytes,
    read_state,
    timestamp,
    unscored_fields,
    validate_state,
)


def remove_retired_technicals(text: str) -> str:
    """Pure archive migration: remove retired graphs, preserve analytical evidence."""
    start = "<!-- papertrader:technical-chart:start -->"
    end = "<!-- papertrader:technical-chart:end -->"
    if text.count(start) != text.count(end) or text.count(start) > 1:
        raise ValueError("incomplete or duplicate technical chart markers")
    updated = re.sub(re.escape(start) + ".*?" + re.escape(end), "", text, flags=re.S)
    if start in updated or end in updated:
        raise ValueError("invalid technical chart marker order")

    def fence(match: re.Match[str]) -> str:
        try:
            chart = json.loads(match[1])
        except ValueError:
            return match[0]
        return "" if isinstance(chart, dict) and chart.get("kind") == "technical" else match[0]

    updated = re.sub(r"^```echart[^\n]*\n(.*?)^```[ \t]*$", fence, updated, flags=re.M | re.S)
    if updated != text:
        updated = re.sub(
            r"^## Visual evidence[ \t]*\r?\n\s*(?=^##(?!#)\s|\Z)", "", updated, flags=re.M
        )
    return updated


def _section(text: str, names: tuple[str, ...]) -> str:
    for match in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", text, re.M | re.S):
        heading, body = match.group(1), match.group(2)
        if any(name in heading.lower() for name in names):
            return body.strip().split("\n\n", 1)[0]
    return ""


def _metadata(content: bytes) -> tuple[dict[str, Any], str]:
    text = content.decode("utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("research page lacks frontmatter")
    raw, body = text[4:].split("\n---\n", 1)
    value = yaml.safe_load(raw)
    if not isinstance(value, dict):
        raise ValueError("research frontmatter must be a mapping")
    return value, body


def existing_narratives(body: str) -> dict[str, str]:
    """Extract only explicit company narrative labels, without making new judgments."""
    labels = re.compile(
        r"\b(?P<downside>Contrary evidence (?:is|includes|remains)|The counter-thesis is|"
        r"(?:Key |Downside )?Risks (?:include|are)|Risks:)"
        r"|\b(?P<catalysts>Catalysts (?:are|include)|Catalysts:)"
        r"|\b(?P<invalidation_conditions>Invalidate (?:the (?:(?:constructive treasury|"
        r"constructive|broader quality|broader) )?(?:thesis|case) )?(?:if|on)|"
        r"Invalidate or (?:materially )?downgrade[^.!?]*?\bif|"
        r"The thesis would be invalidated (?:by|if))",
        re.I,
    )
    forbidden = re.compile(
        r"\b(?:portfolio action|allocation (?:ineligible|eligibility|eligible)|"
        r"(?:accepted|pending|canonical) (?:idea )?relationship|"
        r"(?:canonical|trading) signals?|(?:paper|simulated|pending|trade|trading)[- ]orders?|"
        r"paper[- ]trad(?:e|ing)|buy[- ]below|"
        r"RSI|MACD|Bollinger|SMA|cooldown|indicator|crossover)\b",
        re.I,
    )
    choices: dict[str, set[str]] = {}
    body = re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", body)
    for section in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", body, re.M | re.S):
        heading, content = section.groups()
        if not any(
            word in heading.lower()
            for word in ("thesis", "economics", "business", "valuation", "risk", "catalyst")
        ) or any(
            word in heading.lower()
            for word in ("idea", "changes", "decision", "disposition", "history")
        ):
            continue
        for paragraph in re.split(r"\n\s*\n", content):
            text = " ".join(paragraph.replace("**", "").split())
            matches = list(labels.finditer(text))
            for index, match in enumerate(matches):
                end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
                excerpt = text[match.start() : end].strip()
                if len(excerpt) > 12000 or forbidden.search(excerpt):
                    continue
                assert match.lastgroup is not None
                choices.setdefault(match.lastgroup, set()).add(excerpt)
    return {field: next(iter(values)) for field, values in choices.items() if len(values) == 1}


def recover_narratives(
    root: Path, *, apply: bool = False, now: datetime | None = None
) -> dict[str, Any]:
    """One-time current-table repair; expired research stays expired, including dates."""
    from papertrader.research_results import commit_result
    from papertrader.research_transaction import research_lock, safe_path

    now = now or datetime.now(UTC)
    with research_lock(root):
        state = read_state(root)
        if validate_state(root, state):
            raise ValueError("invalid current research data")
        candidate = copy.deepcopy(state)
        securities = {row["security_id"]: row for row in state["securities"]}
        sources = {row["source_id"]: row for row in state["source_registry"]}
        changes, skipped = [], []
        for assessment in candidate["security_assessments"]:
            if valuation_coverage(assessment) != "incomplete_research":
                continue
            identity = securities[assessment["security_id"]]
            path = identity["research_page"]
            content = safe_path(root, path).read_bytes() if path else b""
            if timestamp(assessment["valid_until"]) >= now or len(content) > 80000:
                skipped.append(dict(security_id=identity["security_id"], reason="not_historical"))
                continue
            metadata, body = _metadata(content)
            references = list(filter(None, assessment["source_ids"].split("|")))
            if (
                metadata.get("security_id") != identity["security_id"]
                or metadata.get("issuer_id") != identity["issuer_id"]
                or str(metadata.get("updated", ""))
                != timestamp(assessment["assessed_at"]).date().isoformat()
                or not references
                or any(ref not in body and sources[ref]["url"] not in body for ref in references)
            ):
                skipped.append(
                    dict(security_id=identity["security_id"], reason="page_evidence_mismatch")
                )
                continue
            missing = {
                field
                for field in ("downside", "catalysts", "invalidation_conditions")
                if not assessment[field]
            }
            extracted = existing_narratives(body)
            updates = {field: extracted[field] for field in sorted(missing) if field in extracted}
            trial = {**assessment, **updates}
            if not updates or valuation_coverage(trial) != "complete":
                skipped.append(
                    dict(security_id=identity["security_id"], reason="ambiguous_or_missing_text")
                )
                continue
            assessment.update(updates)
            changes.append(dict(security_id=identity["security_id"], page=path, fields=updates))
        if validate_state(root, candidate):
            raise ValueError("invalid recovered research data")
        changed = commit_result(root, candidate, {}) if apply and changes else []
        return dict(
            mode="apply" if apply else "dry_run", changes=changes, skipped=skipped, changed=changed
        )


def prepare_migration(
    root: Path, revision: str
) -> tuple[ResearchState, dict[str, bytes], dict[str, Any]]:
    commit = _git(root, "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}")
    sha = commit.decode().strip()
    source = _git(root, "archive", "--format=tar", sha, "data")
    legacy: dict[str, list[Row]] = {}
    assets: dict[str, bytes] = {}
    names = {"securities", "relationships", "security_assessments", "source_registry"}
    with tarfile.open(fileobj=io.BytesIO(source), mode="r:") as archive:
        for entry in archive:
            if entry.isdir():
                continue
            if not entry.isfile():
                raise ValueError(f"unsafe migration input: {entry.name}")
            file = archive.extractfile(entry)
            assert file is not None
            content = file.read()
            if entry.name.startswith("data/wiki/"):
                assets[entry.name] = (
                    remove_retired_technicals(content.decode()).encode()
                    if entry.name.startswith("data/wiki/securities/") and entry.name.endswith(".md")
                    else content
                )
            archive_path = Path(entry.name)
            if archive_path.parent.as_posix() == "data/tables" and archive_path.stem in names:
                legacy[archive_path.stem] = list(
                    csv.DictReader(io.StringIO(content.decode(), newline=""))
                )
    if set(legacy) != names:
        raise ValueError("missing legacy current research table")
    schema = contracts(root)
    state: ResearchState = {name: [] for name in schema}
    assessments = {row["security_id"]: row for row in legacy["security_assessments"]}
    securities = {row["security_id"]: row for row in legacy["securities"]}

    def references(entity: str, text: str) -> str:
        return "|".join(
            sorted(
                row["source_id"]
                for row in legacy["source_registry"]
                if entity in row["related_entity_ids"].split("|")
                or row["source_id"] in text
                or (row["url"] and row["url"] in text)
            )
        )

    for row in legacy["securities"]:
        values = {column: row.get(column, "") for column in schema["securities"].columns}
        values["research_role"] = row.get("research_role") or "long"
        values["research_status"] = (
            "researched" if row["security_id"] in assessments else "unresearched"
        )
        values["discovery_provenance"] = row["source"]
        state["securities"].append(values)
    for asset_path, content in assets.items():
        if Path(asset_path).parent.as_posix() != "data/wiki/ideas" or not asset_path.endswith(
            ".md"
        ):
            continue
        metadata, body = _metadata(content)
        idea_id = str(metadata.get("idea_id", Path(asset_path).stem))
        state["ideas"].append(
            {
                "idea_id": idea_id,
                "title": str(metadata.get("title", "")),
                "thesis": _section(body, ("thesis", "mechanism")),
                "status": str(metadata.get("status", "unresearched")),
                "source_ids": references(idea_id, body),
                "research_page": asset_path,
                "last_reviewed_on": str(metadata.get("updated", "")),
                "created_on": str(metadata.get("created", "")),
                "discovery_provenance": str(metadata.get("provenance", "")),
            }
        )
    for row in legacy["relationships"]:
        values = {column: row.get(column, "") for column in schema["relationships"].columns}
        text = assets.get(row["research_page"], b"").decode("utf-8")
        values["source_ids"] = references(row["relationship_id"], text)
        state["relationships"].append(values)
    for row in legacy["source_registry"]:
        values = {column: row.get(column, "") for column in schema["source_registry"].columns}
        values["url"] = row["canonical_url"] or row["url"]
        values["checked_at"] = row["last_checked_at"]
        # published_at remains empty: a retrieval timestamp is not a publication date.
        state["source_registry"].append(values)
    for row in legacy["security_assessments"]:
        security = securities[row["security_id"]]
        text = assets.get(security["research_page"], b"").decode("utf-8")
        supported = row.get("valuation_supported") == "true"
        values = {column: row.get(column, "") for column in schema["security_assessments"].columns}
        # Legacy scores have no current rubric/evidence contract; do not manufacture one.
        values.update(
            unscored_fields("Historical research was not assessed under scoring rubric 1.")
        )
        values.update(
            {
                "valid_until": row["expires_at"],
                "research_status": "supported" if supported else "valuation_unsupported",
                "method": row.get("valuation_method", ""),
                "method_rationale": row.get("valuation_template_rationale", "")
                or _section(text, ("valuation", "scenario")),
                "currency": row.get("reference_currency") or security["currency"],
                "horizon_months": row["valuation_horizon_months"],
                "thesis": security["research_summary"] or _section(text, ("thesis",)),
                "key_assumptions": row.get("base_assumptions", ""),
                "downside": _section(text, ("risk", "downside")),
                "catalysts": _section(text, ("catalyst",)),
                "invalidation_conditions": _section(text, ("invalidation",)),
                "limitations": row.get("research_conclusion", ""),
                "source_ids": row["evidence_refs"],
            }
        )
        if not supported:
            for case in ("bear", "base", "bull"):
                values[f"{case}_fair_value"] = ""
                values[f"{case}_probability_pct"] = ""
            if row.get("assessment_schema_version") == "legacy_v1":
                values["limitations"] = (
                    "Legacy assessment contains no supportable per-share valuation scenarios. "
                    "Original research remains in the page and pre-migration Git ref."
                )
        state["security_assessments"].append(values)
    # Old assessment IDs in prose become explicit Git references, never active version links.
    replacement = (
        "[prior research in Git](https://github.com/Kabutojira/PaperTrader/blob/"
        "pre-research-only-20261018/data/tables/security_assessment_history.csv)"
    )
    rewritten = []
    for asset_path, content in list(assets.items()):
        if Path(asset_path).parent.as_posix() not in {
            "data/wiki/securities",
            "data/wiki/ideas",
        }:
            continue
        updated = re.sub(r"`assessment_[a-f0-9]+`", replacement, content.decode()).encode()
        if updated != content:
            assets[asset_path] = updated
            rewritten.append(asset_path)
    errors = validate_state(root, state, pages=assets)
    if errors:
        raise ValueError("migration validation failed:\n" + "\n".join(errors))
    report = {
        "input_revision": sha,
        "rows": {name: len(rows) for name, rows in state.items()},
        "supported_scenarios": sum(
            row["research_status"] == "supported" for row in state["security_assessments"]
        ),
        "history_references_rewritten": rewritten,
        "wiki_assets_preserved": len(assets),
        "queue_policy": (
            "empty; M3 rebuilds current entity demand without legacy IDs or dependencies"
        ),
        "table_hashes": {
            name: hashlib.sha256(csv_bytes(schema[name], rows)).hexdigest()
            for name, rows in state.items()
        },
    }
    return state, assets, report


def stage_migration(root: Path, revision: str, destination: Path) -> dict[str, Any]:
    root, destination = root.resolve(), destination.resolve()
    if destination == root or destination.is_relative_to(root / "data"):
        raise ValueError("stage outside active data; production cutover requires the M4 controller")
    state, assets, report = prepare_migration(root, revision)
    files = dict(assets)
    files["schemas/research_contracts.yaml"] = (
        root / "schemas/research_contracts.yaml"
    ).read_bytes()
    for name, contract in contracts(root).items():
        files[contract.path] = csv_bytes(contract, state[name])
    if destination.exists():
        actual = {
            path.relative_to(destination).as_posix(): path.read_bytes()
            for path in destination.rglob("*")
            if path.is_file()
        }
        if actual != files:
            raise FileExistsError("staging destination exists with different content")
        return report
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        dir=destination.parent, prefix=".research-migration-"
    ) as temporary:
        staged = Path(temporary) / "state"
        staged.mkdir()
        for relative, content in files.items():
            staged_path = staged / relative
            staged_path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_bytes(staged_path, content, allowed_root=staged)
        os.replace(staged, destination)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--revision")
    mode.add_argument("--recover-narratives", action="store_true")
    parser.add_argument(
        "--apply", action="store_true", help="apply historical narrative recovery only"
    )
    parser.add_argument("--stage", type=Path, help="explicit isolated output; never active data")
    arguments = parser.parse_args()
    if arguments.recover_narratives:
        if arguments.stage:
            parser.error("narrative recovery does not use a legacy staging directory")
        report = recover_narratives(arguments.repository, apply=arguments.apply)
    elif arguments.apply:
        parser.error("legacy conversion requires --stage, not --apply")
    elif arguments.stage:
        report = stage_migration(arguments.repository, arguments.revision, arguments.stage)
    else:
        _, _, report = prepare_migration(arguments.repository, arguments.revision)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
