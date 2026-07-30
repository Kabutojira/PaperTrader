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

    assert len(contracts) == 29
    assert validate_csv_files(repository_root) == []
    assert {contract.name for contract in contracts} == {
        "allocation_history",
        "allocation_targets",
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
        "performance_epochs",
        "portfolio",
        "published_actionable_signals",
        "published_model_portfolio",
        "published_research_benchmark",
        "relationships",
        "runs",
        "securities",
        "security_assessments",
        "security_assessment_history",
        "signals",
        "source_history",
        "source_registry",
        "youtube_channels",
        "strategies",
        "strategy_legs",
    }


def test_append_only_and_generated_contract_flags(repository_root: Path) -> None:
    contracts = {contract.name: contract for contract in load_csv_contracts(repository_root)}

    assert contracts["executions"].append_only
    assert contracts["cash_ledger"].append_only
    assert contracts["operations_history"].append_only
    assert contracts["allocation_history"].append_only
    assert contracts["performance_epochs"].append_only
    assert contracts["allocation_targets"].generated
    assert contracts["portfolio"].generated
    assert contracts["published_model_portfolio"].generated
    assert contracts["published_actionable_signals"].generated
    assert not contracts["published_model_portfolio"].append_only
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


def test_operation_payload_accepts_closed_youtube_variant_and_local_compatibility(
    repository_root: Path,
) -> None:
    validator = _schema_validator(repository_root, "operation_payload.schema.json")
    base = {
        "payload_version": 1,
        "operation_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "operation_type": "wiki_ingest",
        "entity_type": "source",
        "entity_id": "youtube_abcdefghijk",
        "objective": "Analyze one curated transcript.",
        "source_refs": ["https://www.youtube.com/watch?v=abcdefghijk"],
        "inputs": {
            "source_kind": "youtube_video",
            "source_id": "youtube_abcdefghijk",
            "video_id": "abcdefghijk",
            "video_title": "Example",
            "video_url": "https://www.youtube.com/watch?v=abcdefghijk",
            "channel_id": "UCESLZhusAkFfsNsApnjF_Cg",
            "channel_handle": "@allin",
            "channel_url": ("https://www.youtube.com/channel/UCESLZhusAkFfsNsApnjF_Cg/videos"),
            "discovered_at": "2026-07-29T08:00:00Z",
            "transcript_languages": ["en", "en-US", "en-GB"],
            "prefer_human": True,
            "discovery_mode": "bootstrap",
        },
    }

    assert list(validator.iter_errors(base)) == []
    base["inputs"]["unexpected"] = "forbidden"
    assert list(validator.iter_errors(base))

    local = {
        **base,
        "entity_id": "source_local",
        "source_refs": [],
        "inputs": {"source_path": "data/wiki/inbox/example.md", "source_hash": "a" * 64},
    }
    assert list(validator.iter_errors(local)) == []


def test_operation_payload_normalizes_baseline_increase_to_open_lifecycle_action(
    repository_root: Path,
) -> None:
    validator = _schema_validator(repository_root, "operation_payload.schema.json")
    baseline = {
        "payload_version": 1,
        "operation_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "operation_type": "strategy_research",
        "entity_type": "strategy",
        "entity_id": "strategy_baseline",
        "objective": "Research one deterministic baseline target.",
        "inputs": {
            "mode": "baseline_allocation",
            "allocation_plan_id": "allocation_plan_example",
            "strategy_id": "strategy_baseline",
            "relationship_id": "relationship_example",
            "security_id": "sec_example",
            "current_weight_pct": "0",
            "target_weight_pct": "2.5",
            "maximum_weight_pct": "5",
            "selection_rank": 1,
            "effective_score": "80",
            "assessment_as_of": "2026-07-24T12:00:00Z",
            "disposition": "increase",
        },
    }
    hold = {
        "payload_version": 1,
        "operation_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "operation_type": "execute_strategy",
        "entity_type": "strategy",
        "entity_id": "strategy_baseline",
        "objective": "Confirm a baseline hold without order churn.",
        "inputs": {
            "strategy_id": "strategy_baseline",
            "signal_id": "signal_baseline",
            "action": "hold",
        },
    }

    assert list(validator.iter_errors(baseline)) == []
    assert list(validator.iter_errors(hold)) == []
    hold["inputs"]["action"] = "open"
    assert list(validator.iter_errors(hold)) == []
    hold["inputs"]["action"] = "increase"
    assert list(validator.iter_errors(hold))
    del baseline["inputs"]["allocation_plan_id"]
    assert list(validator.iter_errors(baseline))


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
