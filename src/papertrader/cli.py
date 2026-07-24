"""PaperTrader command-line interface and Step 1 validation commands."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from papertrader.config import ConfigurationError, find_repository_root, load_settings
from papertrader.integrity import (
    changed_paths_from_git,
    validate_csv_files,
    validate_integrity,
    validate_json_schemas,
    validate_runtime_paths,
)
from papertrader.portfolio import reconcile_portfolio
from papertrader.wiki import lint_wiki


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="papertrader")
    parser.add_argument("--repository", type=Path, help="repository root (defaults to discovery)")
    commands = parser.add_subparsers(dest="command", required=True)

    schema = commands.add_parser("schema", help="validate repository schemas")
    schema_commands = schema.add_subparsers(dest="schema_command", required=True)
    schema_validate = schema_commands.add_parser("validate")
    schema_validate.add_argument("--strict", action="store_true")

    integrity = commands.add_parser("integrity", help="run repository integrity checks")
    integrity.add_argument("--strict", action="store_true")

    wiki = commands.add_parser("wiki", help="work with the research wiki")
    wiki_commands = wiki.add_subparsers(dest="wiki_command", required=True)
    wiki_lint = wiki_commands.add_parser("lint")
    wiki_lint.add_argument("--strict", action="store_true")

    portfolio = commands.add_parser("portfolio", help="work with derived portfolio state")
    portfolio_commands = portfolio.add_subparsers(dest="portfolio_command", required=True)
    portfolio_reconcile = portfolio_commands.add_parser("reconcile")
    portfolio_reconcile.add_argument("--strict", action="store_true")

    whitelist = commands.add_parser(
        "runtime-whitelist", help="validate automated runtime commit paths"
    )
    whitelist_commands = whitelist.add_subparsers(dest="whitelist_command", required=True)
    whitelist_validate = whitelist_commands.add_parser("validate")
    whitelist_validate.add_argument("paths", nargs="*")
    whitelist_validate.add_argument("--staged", action="store_true")
    whitelist_validate.add_argument("--base-ref")
    whitelist_validate.add_argument("--head-ref", default="HEAD")
    return parser


def _print_result(name: str, errors: Sequence[str]) -> int:
    if errors:
        for error in errors:
            print(f"ERROR [{name}] {error}", file=sys.stderr)
        return 1
    print(f"OK [{name}]")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command after enforcing repository and paper-only startup settings."""

    arguments = _parser().parse_args(argv)
    try:
        root = find_repository_root(arguments.repository)
        settings = load_settings(root, os.environ)
    except ConfigurationError as exc:
        print(f"ERROR [configuration] {exc}", file=sys.stderr)
        return 2

    if arguments.command == "schema":
        errors = validate_csv_files(root)
        errors.extend(validate_json_schemas(root))
        return _print_result("schema", errors)
    if arguments.command == "integrity":
        return _print_result("integrity", validate_integrity(root, os.environ))
    if arguments.command == "wiki":
        return _print_result("wiki", lint_wiki(settings.paths.wiki))
    if arguments.command == "portfolio":
        return _print_result("portfolio", reconcile_portfolio(root))
    if arguments.command == "runtime-whitelist":
        try:
            paths = tuple(arguments.paths)
            if arguments.staged or arguments.base_ref:
                if paths:
                    raise ValueError("explicit paths cannot be combined with Git diff options")
                paths = changed_paths_from_git(
                    root,
                    staged=arguments.staged,
                    base_ref=arguments.base_ref,
                    head_ref=arguments.head_ref,
                )
            if not paths:
                raise ValueError("provide paths, --staged, or --base-ref")
        except (RuntimeError, ValueError) as exc:
            return _print_result("runtime-whitelist", [str(exc)])
        return _print_result("runtime-whitelist", validate_runtime_paths(paths))
    return _print_result("command", ["unhandled command"])
