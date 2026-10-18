"""Research-only entry point; deterministic validation and isolated staging."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from datetime import UTC, datetime
from pathlib import Path

from papertrader.migration_inventory import _git
from papertrader.research_agent import run_cycle
from papertrader.research_discovery import (
    IdentityVerifier,
    discovery_limits,
    prepare_candidates,
    run_discovery,
)
from papertrader.research_migration import prepare_migration
from papertrader.research_queue import admit, queue_limits, rebuild_legacy_queue
from papertrader.research_results import commit_result, context_packet, prepare_result
from papertrader.research_state import contracts, csv_bytes, read_state, timestamp, validate_state
from papertrader.research_transaction import research_lock
from papertrader.research_web import ResearchWeb


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Current company and idea research")
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    discovery = commands.add_parser("discover")
    discovery.add_argument("--apply", action="store_true")
    discovery.add_argument("--force", action="store_true", help="Explicit manual cadence override")
    imports = commands.add_parser("import-candidates")
    imports.add_argument("--request", type=Path, required=True)
    imports.add_argument("--apply", action="store_true")
    for name in ("context", "enqueue"):
        child = commands.add_parser(name)
        child.add_argument("entity_type", choices=["security", "idea"])
        child.add_argument("entity_id")
    research = commands.add_parser("research")
    research.add_argument("--entity-type", choices=["security", "idea"], default="")
    research.add_argument("--entity-id", default="")
    research.add_argument(
        "--apply",
        action="store_true",
        help="Run real bounded research; default is read-only preview",
    )
    apply = commands.add_parser("apply-result")
    apply.add_argument("--result", type=Path, required=True)
    apply.add_argument("--apply", action="store_true")
    migration = commands.add_parser("migrate")
    migration.add_argument("--revision", required=True)
    migration.add_argument(
        "--as-of", required=True, help="Fixed UTC migration timestamp ending in Z"
    )
    migration.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    root = args.repository.resolve()
    now = datetime.now(UTC)
    try:
        if args.command == "discover":
            response = run_discovery(root, dry_run=not args.apply, force=args.force)
            print(json.dumps(response, indent=2, sort_keys=True))
            return int(response["exit_code"])
        if args.command == "research":
            if bool(args.entity_id) != bool(args.entity_type):
                raise ValueError("both entity identity fields are required")
            response = run_cycle(
                root, dry_run=not args.apply, entity_type=args.entity_type, entity_id=args.entity_id
            )
            print(json.dumps(response, indent=2, sort_keys=True))
            return int(response["exit_code"])
        with research_lock(root):
            if args.command == "migrate":
                state, pages, report = prepare_migration(root, args.revision)
                sha = report["input_revision"]
                raw = _git(root, "show", f"{sha}:data/operations/operations_TODO.csv")
                report["queue"] = rebuild_legacy_queue(
                    state,
                    list(csv.DictReader(io.StringIO(raw.decode()))),
                    now=timestamp(args.as_of),
                    limits=queue_limits(root),
                )
                report["queue_policy"] = (
                    "current company/idea demand only; no legacy tasks or dependencies"
                )
                report["rows"] = {name: len(rows) for name, rows in state.items()}
                report["table_hashes"] = {
                    name: hashlib.sha256(csv_bytes(contract, state[name])).hexdigest()
                    for name, contract in contracts(root).items()
                }
                errors = validate_state(root, state, pages=pages)
                if errors:
                    raise ValueError("; ".join(errors[:8]))
                # Keep all current prose/assets, writing only actual changed bytes.
                if args.apply:
                    if (root / "data/tables/ideas.csv").exists():
                        current = read_state(root)
                        if any(
                            csv_bytes(contract, current[name]) != csv_bytes(contract, state[name])
                            for name, contract in contracts(root).items()
                        ) or any(
                            not (root / name).is_file() or (root / name).read_bytes() != content
                            for name, content in pages.items()
                        ):
                            raise ValueError(
                                "compact data already exists; migration cannot overwrite "
                                "subsequent research"
                            )
                    report["changed"] = commit_result(root, state, pages)
                print(json.dumps(report, indent=2, sort_keys=True))
                return 0
            state = read_state(root)
            if args.command == "validate":
                errors = validate_state(root, state)
                print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
                return 4 if errors else 0
            if args.command == "context":
                operation = (
                    "research_security" if args.entity_type == "security" else "research_idea"
                )
                print(
                    json.dumps(
                        context_packet(root, state, operation=operation, entity_id=args.entity_id),
                        indent=2,
                    )
                )
                return 0
            if args.command == "enqueue":
                outcome = admit(
                    state,
                    args.entity_type,
                    args.entity_id,
                    reasons={"explicit_manual_request"},
                    priority=100,
                    manual=True,
                    now=now,
                    limits=queue_limits(root),
                )
                changed = commit_result(root, state, {})
                print(json.dumps(dict(status=outcome, changed=changed)))
                return 0
            if args.command == "import-candidates":
                document = json.loads(args.request.read_text())
                if not args.apply:
                    print(
                        json.dumps(
                            {
                                "status": "dry_run",
                                "limits": vars(discovery_limits(root)),
                                "network_calls": 0,
                            }
                        )
                    )
                    return 0
                limits = discovery_limits(root)
                broker = ResearchWeb()
                if (
                    not isinstance(document, dict)
                    or not isinstance(document.get("ideas"), list)
                    or not isinstance(document.get("companies"), list)
                    or len(document["ideas"]) > limits.weekly_max_ideas
                    or len(document["companies"]) > limits.weekly_max_companies
                ):
                    raise ValueError("bounded import required before network access")
                for value in document["ideas"] + document["companies"]:
                    for url in value["source_urls"]:
                        broker.open(url)
                candidate, pages, created = prepare_candidates(
                    root,
                    state,
                    document,
                    now=datetime.now(UTC),
                    observations=broker.observations,
                    verify_identity=IdentityVerifier(root, limits),
                    limits=limits,
                    manual=True,
                )
                print(
                    json.dumps(
                        {"created": created, "changed": commit_result(root, candidate, pages)}
                    )
                )
                return 0
            result = json.loads(args.result.read_text())
            if not args.apply:
                print(
                    json.dumps(
                        {"status": "dry_run", "entity_id": result["entity_id"], "network_calls": 0}
                    )
                )
                return 0
            broker = ResearchWeb()
            for row in result["sources"]:
                broker.open(row["url"])
            candidate, pages = prepare_result(
                root,
                state,
                result,
                operation=result["operation"],
                entity_id=result["entity_id"],
                now=datetime.now(UTC),
                observations=broker.observations,
            )
            print(json.dumps({"changed": commit_result(root, candidate, pages)}))
            return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "invalid_data", "error": type(exc).__name__}))
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
