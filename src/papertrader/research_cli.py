"""Research-only entry point; deterministic validation and isolated staging."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from papertrader.research_discovery import (
    IdentityVerifier,
    discovery_limits,
    prepare_candidates,
    run_discovery,
)
from papertrader.research_publication import publish_views, snapshot
from papertrader.research_queue import admit, queue_limits
from papertrader.research_results import commit_result, context_packet, prepare_result
from papertrader.research_runtime import (
    RuntimeCommitValidationError,
    finalize_commit,
    market_cycle,
    research_cycle,
)
from papertrader.research_state import read_state, validate_state
from papertrader.research_transaction import research_lock
from papertrader.research_web import ResearchWeb


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Current company and idea research")
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    market = commands.add_parser("market")
    market.add_argument("--apply", action="store_true")
    finalize = commands.add_parser("commit-runtime")
    finalize.add_argument("phase", choices=["market", "research"])
    finalize.add_argument("--manifest", type=Path, required=True)
    publication = commands.add_parser("publish")
    publication.add_argument("--apply", action="store_true")
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
    research.add_argument("--discovery", action="store_true")
    research.add_argument(
        "--apply",
        action="store_true",
        help="Run real bounded research; default is read-only preview",
    )
    apply = commands.add_parser("apply-result")
    apply.add_argument("--result", type=Path, required=True)
    apply.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    root = args.repository.resolve()
    now = datetime.now(UTC)
    try:
        if args.command == "market":
            response = market_cycle(root, dry_run=not args.apply)
            print(json.dumps(response, indent=2, sort_keys=True))
            return int(response["exit_code"])
        if args.command == "commit-runtime":
            response = finalize_commit(root, phase=args.phase, token=os.environ.get("GH_TOKEN", ""))
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            args.manifest.write_text(json.dumps(response))
            print(json.dumps(response))
            return 0
        if args.command == "discover":
            response = run_discovery(root, dry_run=not args.apply, force=args.force)
            print(json.dumps(response, indent=2, sort_keys=True))
            return int(response["exit_code"])
        if args.command == "research":
            if bool(args.entity_id) != bool(args.entity_type):
                raise ValueError("both entity identity fields are required")
            response = research_cycle(
                root,
                dry_run=not args.apply,
                entity_type=args.entity_type,
                entity_id=args.entity_id,
                discovery=args.discovery,
            )
            print(json.dumps(response, indent=2, sort_keys=True))
            return int(response["exit_code"])
        with research_lock(root):
            if args.command == "publish":
                response = (
                    {"changed": publish_views(root, now=now)}
                    if args.apply
                    else snapshot(root, now=now)
                )
                print(json.dumps(response, indent=2, sort_keys=True))
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
    except RuntimeCommitValidationError as exc:
        print(json.dumps({"status": "invalid_data", "error": exc.diagnostic_code}))
        return 4
    except RuntimeError as exc:
        print(json.dumps({"status": "infrastructure_error", "error": str(exc)}))
        return 5
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "invalid_data", "error": type(exc).__name__}))
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
