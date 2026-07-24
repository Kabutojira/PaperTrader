from __future__ import annotations

import json
import tomllib
from pathlib import Path

from jsonschema.validators import validator_for

from papertrader.integrity import (
    load_csv_contracts,
    validate_csv_files,
    validate_json_schemas,
)


def _schema_validator(repository_root: Path, name: str):  # type: ignore[no-untyped-def]
    schema = json.loads((repository_root / "schemas" / name).read_text(encoding="utf-8"))
    validator_type = validator_for(schema)
    validator_type.check_schema(schema)
    return validator_type(schema)


def test_every_declared_csv_exists_with_exact_header(repository_root: Path) -> None:
    contracts = load_csv_contracts(repository_root)

    assert len(contracts) == 20
    assert validate_csv_files(repository_root) == []
    assert {contract.name for contract in contracts} == {
        "cash_ledger",
        "corporate_actions",
        "executions",
        "indicators",
        "issues",
        "market_latest",
        "operations_history",
        "operations_todo",
        "order_legs",
        "orders",
        "performance_daily",
        "portfolio",
        "relationships",
        "runs",
        "securities",
        "signals",
        "source_history",
        "source_registry",
        "strategies",
        "strategy_legs",
    }


def test_append_only_and_generated_contract_flags(repository_root: Path) -> None:
    contracts = {contract.name: contract for contract in load_csv_contracts(repository_root)}

    assert contracts["executions"].append_only
    assert contracts["cash_ledger"].append_only
    assert contracts["operations_history"].append_only
    assert contracts["portfolio"].generated
    assert not contracts["portfolio"].append_only


def test_json_schemas_are_valid(repository_root: Path) -> None:
    assert validate_json_schemas(repository_root) == []


def test_agent_result_schema_accepts_completed_manifest_and_rejects_proposals(
    repository_root: Path,
) -> None:
    validator = _schema_validator(repository_root, "agent_result.schema.json")
    result = {
        "operation_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "status": "succeeded",
        "summary": "Validated one source.",
        "evidence": [],
        "files_changed": ["data/wiki/index.md"],
        "operations_created": [],
        "issues_recorded": [],
        "daily_report_items": [],
        "commands_run": ["papertrader wiki lint --strict"],
        "validation": {"passed": True, "checks": ["wiki lint"]},
    }

    assert list(validator.iter_errors(result)) == []
    result["proposals"] = []
    assert len(list(validator.iter_errors(result))) == 1


def test_operation_payload_requires_type_specific_input(repository_root: Path) -> None:
    validator = _schema_validator(repository_root, "operation_payload.schema.json")
    payload = {
        "payload_version": 1,
        "operation_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "operation_type": "security_research",
        "entity_type": "security",
        "entity_id": "sec-example",
        "objective": "Refresh one security thesis.",
        "inputs": {"security_id": "sec-example"},
    }

    assert list(validator.iter_errors(payload)) == []
    payload["inputs"] = {}
    assert list(validator.iter_errors(payload))


def test_distribution_has_no_real_execution_dependency_or_adapter(repository_root: Path) -> None:
    project = tomllib.loads((repository_root / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = {
        item.split("[", maxsplit=1)[0].split("=", maxsplit=1)[0].lower()
        for item in project["project"]["dependencies"]
    }
    real_execution_packages = {
        "alpaca-py",
        "ccxt",
        "ibapi",
        "ib-insync",
        "oandapyv20",
        "robin-stocks",
    }

    assert dependencies.isdisjoint(real_execution_packages)
    assert not any((repository_root / "src" / "papertrader").glob("*broker*"))
    config = (repository_root / "config.ini").read_text(encoding="utf-8")
    assert "paper_trading_only = true" in config
    assert "allow_real_orders = false" in config
