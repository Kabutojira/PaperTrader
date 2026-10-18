"""Read-only, revision-pinned census for the research-only migration.

The full export belongs outside the checkout. Git's verified pre-migration ref, rather
than another permanent active history tree, preserves the original source bytes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import tarfile
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any

from papertrader.atomic_io import atomic_write_json


def _git(root: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        timeout=60,
    ).stdout


def baseline_inventory(root: Path, revision: str, *, as_of: date) -> dict[str, Any]:
    """Inventory committed data without reading or modifying working-tree data."""

    sha = _git(root, "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}")
    commit = sha.decode().strip()
    archive = _git(root, "archive", "--format=tar", commit, "data")
    files: dict[str, Any] = {}
    tables: dict[str, Any] = {}
    pages: dict[str, Any] = {}
    current: dict[str, Any] = {}
    queue: list[dict[str, str]] = []
    retained_tables = {
        "data/tables/securities.csv",
        "data/tables/security_assessments.csv",
        "data/tables/source_registry.csv",
        "data/tables/relationships.csv",
    }
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as source:
        for member in source:
            if not member.isfile():
                continue
            stream = source.extractfile(member)
            assert stream is not None
            content = stream.read()
            files[member.name] = {
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
            if member.name.endswith(".csv"):
                reader = csv.DictReader(io.StringIO(content.decode("utf-8"), newline=""))
                rows = list(reader)
                tables[member.name] = {"columns": reader.fieldnames, "rows": len(rows)}
                if member.name in retained_tables:
                    current[member.name] = rows
                if member.name == "data/operations/operations_TODO.csv":
                    queue = rows
            elif member.name.startswith("data/wiki/") and member.name.endswith(".md"):
                text = content.decode("utf-8")
                pages[member.name] = {
                    "wikilinks": sorted(set(re.findall(r"\[\[([^\]|#]+)", text))),
                    "markdown_links": sorted(set(re.findall(r"\[[^\n]*?\]\(([^)\s]+)\)", text))),
                    "source_ids": sorted(set(re.findall(r"\bsource_[A-Za-z0-9_-]+\b", text))),
                }
    securities = current.get("data/tables/securities.csv", [])
    assessments = current.get("data/tables/security_assessments.csv", [])
    blocked = [row for row in queue if row["status"] == "blocked"]
    return {
        "schema_version": 1,
        "revision": commit,
        "as_of": as_of.isoformat(),
        "files": files,
        "csv": tables,
        "wiki": pages,
        "current_research": current,
        "identities": [
            {
                key: row[key]
                for key in ("security_id", "issuer_id", "ticker", "venue_mic", "currency")
            }
            for row in securities
        ],
        "queue": {
            "rows": queue,
            "by_status": dict(sorted(Counter(row["status"] for row in queue).items())),
            "blocked_by_reason": dict(
                sorted(Counter(row["last_error"].split(":", 1)[0] for row in blocked).items())
            ),
            "capacity_blocked_by_type": dict(
                sorted(
                    Counter(
                        row["operation_type"]
                        for row in blocked
                        if row["last_error"] == "scope_deferred_for_capacity"
                    ).items()
                )
            ),
        },
        "assessment_coverage": {
            "total": len(assessments),
            "expired": sum(
                datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")).date() < as_of
                for row in assessments
                if row.get("expires_at")
            ),
        },
    }


def export_inventory(root: Path, revision: str, *, as_of: date, output: Path) -> dict[str, Any]:
    """Explicitly export outside the repo; never add a new active history copy."""

    root = root.resolve()
    output = output.resolve()
    if output.is_relative_to(root):
        raise ValueError("the baseline export must be outside the repository")
    inventory = baseline_inventory(root, revision, as_of=as_of)
    atomic_write_json(output, inventory, allowed_root=output.parent)
    return inventory


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--revision", required=True, help="verified pre-migration Git ref or SHA")
    parser.add_argument("--as-of", required=True, type=date.fromisoformat)
    parser.add_argument(
        "--output", type=Path, help="optional explicit export outside the repository"
    )
    arguments = parser.parse_args()
    if arguments.output:
        inventory = export_inventory(
            arguments.repository,
            arguments.revision,
            as_of=arguments.as_of,
            output=arguments.output,
        )
    else:
        inventory = baseline_inventory(
            arguments.repository, arguments.revision, as_of=arguments.as_of
        )
    print(
        json.dumps(
            {
                "revision": inventory["revision"],
                "files": len(inventory["files"]),
                "csv_files": len(inventory["csv"]),
                "wiki_pages": len(inventory["wiki"]),
                "queue_by_status": inventory["queue"]["by_status"],
                "blocked_by_reason": inventory["queue"]["blocked_by_reason"],
                "assessment_coverage": inventory["assessment_coverage"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
