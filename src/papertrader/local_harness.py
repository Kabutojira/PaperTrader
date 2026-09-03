"""Two-phase local agentic-harness boundary for one validated queue operation."""

from __future__ import annotations

import json
import os
import re
import stat
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from papertrader.agent_runner import (
    AgentRunError,
    build_controller_prompt,
    project_skill_identities,
    prompt_injection_flags,
)
from papertrader.atomic_io import atomic_write_json, atomic_write_text
from papertrader.config import Settings
from papertrader.issues import (
    operation_validation_impact,
    record_issue,
    resolve_matching_issues,
)
from papertrader.queue import (
    Operation,
    RunBudget,
    allocation_operation_binding,
    block_operation,
    claim_next,
    complete_operation,
    fail_attempt,
    prepare_queue,
)
from papertrader.repository_state import (
    FileState,
    RepositorySnapshot,
    compare_snapshots,
    snapshot_repository,
)
from papertrader.result_validator import (
    agent_terminal_reason,
    result_relative_path,
    validate_agent_result,
)
from papertrader.tables import read_table
from papertrader.utils import content_hash, format_timestamp, utc_now

SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
STATE_VERSION = 1


@dataclass(frozen=True, slots=True)
class HarnessStart:
    """Paths and audit context needed by one local harness operation."""

    run_id: str
    operation_id: str
    operation_type: str
    payload_path: str
    controller_prompt_path: str
    result_path: str
    audit_path: str
    controller_skill_path: str
    operation_skill_path: str
    auxiliary_skill_paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HarnessFinish:
    """Validated local harness disposition and exact completed-change paths."""

    run_id: str
    operation_id: str
    status: str
    changed_paths: tuple[str, ...]
    validation_path: str


def _operation_rows(repository_root: Path) -> dict[str, dict[str, str]]:
    return {
        row["operation_id"]: row
        for table in ("operations_todo", "operations_history")
        for row in read_table(repository_root, table)
    }


def _issue_rows(repository_root: Path) -> dict[str, dict[str, str]]:
    return {row["issue_id"]: row for row in read_table(repository_root, "issues")}


def _state_path(repository_root: Path, run_id: str, operation_id: str) -> Path:
    repository_key = content_hash(str(repository_root.resolve(strict=True)))[:16]
    operation_key = content_hash([run_id, operation_id])[:16]
    return Path(tempfile.gettempdir()) / (
        f"papertrader-local-harness-{repository_key}-{operation_key}.json"
    )


def _snapshot_value(snapshot: RepositorySnapshot) -> dict[str, dict[str, object]]:
    return {
        path: {
            "kind": state.kind,
            "sha256": state.sha256,
            "size": state.size,
            "mode": state.mode,
            "modified_ns": state.modified_ns,
        }
        for path, state in snapshot.files.items()
    }


def _snapshot_from_value(value: object) -> RepositorySnapshot:
    if not isinstance(value, dict):
        raise AgentRunError("local harness baseline snapshot must be an object")
    files: dict[str, FileState] = {}
    for path, raw_state in value.items():
        if not isinstance(path, str) or not isinstance(raw_state, dict):
            raise AgentRunError("local harness baseline contains an invalid file entry")
        if set(raw_state) != {"kind", "sha256", "size", "mode", "modified_ns"}:
            raise AgentRunError(f"local harness baseline fields differ for {path}")
        kind = raw_state["kind"]
        sha256 = raw_state["sha256"]
        size = raw_state["size"]
        mode = raw_state["mode"]
        modified_ns = raw_state["modified_ns"]
        if (
            not isinstance(kind, str)
            or not isinstance(sha256, str)
            or isinstance(size, bool)
            or not isinstance(size, int)
            or isinstance(mode, bool)
            or not isinstance(mode, int)
            or isinstance(modified_ns, bool)
            or not isinstance(modified_ns, int)
        ):
            raise AgentRunError(f"local harness baseline types differ for {path}")
        files[path] = FileState(kind, sha256, size, mode, modified_ns)
    return RepositorySnapshot(files)


def _row_mapping(value: object, *, label: str) -> dict[str, dict[str, str]]:
    if not isinstance(value, dict):
        raise AgentRunError(f"local harness {label} must be an object")
    result: dict[str, dict[str, str]] = {}
    for identifier, raw_row in value.items():
        string_row = isinstance(raw_row, dict) and all(
            isinstance(key, str) and isinstance(item, str) for key, item in raw_row.items()
        )
        if not isinstance(identifier, str) or not isinstance(raw_row, dict) or not string_row:
            raise AgentRunError(f"local harness {label} contains an invalid row")
        result[identifier] = dict(raw_row)
    return result


def _write_state(
    repository_root: Path,
    operation: Operation,
    *,
    run_id: str,
    before_snapshot: RepositorySnapshot,
    operation_rows_before: Mapping[str, Mapping[str, str]],
    issue_rows_before: Mapping[str, Mapping[str, str]],
) -> None:
    path = _state_path(repository_root, run_id, operation.operation_id)
    if path.exists():
        raise AgentRunError(
            "local harness state already exists; finish the operation or release its expired lease"
        )
    atomic_write_json(
        path,
        {
            "state_version": STATE_VERSION,
            "repository": str(repository_root.resolve(strict=True)),
            "run_id": run_id,
            "operation_id": operation.operation_id,
            "operation_row": operation.to_row(),
            "operation_rows_before": dict(operation_rows_before),
            "issue_rows_before": dict(issue_rows_before),
            "before_snapshot": _snapshot_value(before_snapshot),
        },
        allowed_root=Path(tempfile.gettempdir()),
    )
    os.chmod(path, 0o600)


def _load_state(
    repository_root: Path, run_id: str, operation_id: str
) -> tuple[
    Operation,
    RepositorySnapshot,
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    Path,
]:
    path = _state_path(repository_root, run_id, operation_id)
    if path.is_symlink() or not path.is_file():
        raise AgentRunError("local harness baseline is missing or is a symlink")
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise AgentRunError("local harness baseline permissions must be private")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AgentRunError(f"cannot read local harness baseline: {exc}") from exc
    if not isinstance(value, dict):
        raise AgentRunError("local harness baseline must contain an object")
    expected_keys = {
        "state_version",
        "repository",
        "run_id",
        "operation_id",
        "operation_row",
        "operation_rows_before",
        "issue_rows_before",
        "before_snapshot",
    }
    if set(value) != expected_keys:
        raise AgentRunError("local harness baseline fields differ from the contract")
    if (
        value["state_version"] != STATE_VERSION
        or value["repository"] != str(repository_root.resolve(strict=True))
        or value["run_id"] != run_id
        or value["operation_id"] != operation_id
    ):
        raise AgentRunError("local harness baseline identity mismatch")
    raw_operation = value["operation_row"]
    if not isinstance(raw_operation, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in raw_operation.items()
    ):
        raise AgentRunError("local harness operation row is invalid")
    operation = Operation.from_row(raw_operation)
    if operation.status != "running" or operation.claimed_by_run_id != run_id:
        raise AgentRunError("local harness baseline does not describe this running claim")
    return (
        operation,
        _snapshot_from_value(value["before_snapshot"]),
        _row_mapping(value["operation_rows_before"], label="operation rows"),
        _row_mapping(value["issue_rows_before"], label="issue rows"),
        path,
    )


def start_local_harness_operation(
    repository_root: Path,
    settings: Settings,
    *,
    run_id: str,
    operation_id: str | None = None,
    operation_type: str | None = None,
    estimated_cost: Decimal = Decimal("0"),
) -> HarnessStart | None:
    """Claim one operation and persist its validation baseline outside the checkout."""

    if not SAFE_RUN_ID.fullmatch(run_id):
        raise AgentRunError(f"invalid run_id: {run_id!r}")
    batch_path = repository_root / "data" / "runs" / run_id / "agent_batch.json"
    if batch_path.exists():
        if batch_path.is_symlink() or not batch_path.is_file():
            raise AgentRunError("local daily agent batch must be a regular file")
        try:
            batch = json.loads(batch_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AgentRunError("local daily agent batch is invalid") from exc
        maximum = batch.get("maximum_operations") if isinstance(batch, dict) else None
        count = batch.get("operation_count") if isinstance(batch, dict) else None
        if (
            isinstance(maximum, bool)
            or not isinstance(maximum, int)
            or isinstance(count, bool)
            or not isinstance(count, int)
        ):
            raise AgentRunError("local daily agent batch budget is invalid")
        if maximum != settings.operations.cycle_maximum_operations:
            raise AgentRunError("local daily MAX_OPERATIONS changed during the cycle")
        if count >= maximum:
            return None
    prepare_queue(repository_root)
    budget = RunBudget(
        maximum_operations=1,
        maximum_cost=settings.operations.maximum_model_budget_usd_per_run,
    )
    operation = claim_next(
        repository_root,
        settings,
        run_id=run_id,
        budget=budget,
        estimated_cost=estimated_cost,
        operation_id=operation_id,
        operation_type=operation_type,
    )
    if operation is None:
        return None

    run_directory = repository_root / "data" / "runs" / run_id
    artifact_directory = run_directory / operation.operation_id
    if run_directory.is_symlink() or artifact_directory.is_symlink():
        raise AgentRunError("local harness artifact path must not traverse a symlink")
    if artifact_directory.exists() and (
        not artifact_directory.is_dir() or any(artifact_directory.iterdir())
    ):
        raise AgentRunError(f"local harness artifact directory is not empty: {artifact_directory}")
    artifact_directory.mkdir(parents=True, exist_ok=True)

    controller, selected, auxiliary = project_skill_identities(
        repository_root, operation.operation_type
    )
    injection_flags = prompt_injection_flags(repository_root, operation)
    prompt = build_controller_prompt(
        operation,
        run_id=run_id,
        injection_flags=injection_flags,
        allocation_binding=allocation_operation_binding(repository_root, operation),
    )
    support_skill_requirements = "".join(
        f"- Read required support skill {skill.relative_path} completely.\n" for skill in auxiliary
    )
    prompt += (
        "\n\nLocal harness boundary:\n"
        "- The parent controller already started and claimed this operation. Do not run agent "
        "harness start or any other queue lifecycle command.\n"
        f"- Read {controller.relative_path} and {selected.relative_path} completely.\n"
        f"{support_skill_requirements}"
        "- Read data/wiki/SCHEMA.md, data/wiki/index.md, and the latest data/wiki/log.md entries.\n"
        "- Prefix every agent-side papertrader CLI command with "
        f"PAPERTRADER_AUDIT_RUN_ID={run_id} "
        f"PAPERTRADER_AUDIT_OPERATION_ID={operation.operation_id} "
        f"PAPERTRADER_AUDIT_OPERATION_TYPE={operation.operation_type} "
        f"PAPERTRADER_AUDIT_PATH=data/runs/{run_id}/{operation.operation_id}/command_audit.json.\n"
        "- Invoke the project CLI through scripts/papertrader; do not use a system or Snap uv "
        "launcher.\n"
        "- Write agent_result.json only after every permitted edit and audited command.\n"
        "- Do not run agent harness finish; stop after agent_result.json exists so the parent "
        "controller can validate and terminalize the operation.\n"
    )
    prompt_path = artifact_directory / "controller_prompt.md"
    preflight_path = artifact_directory / "harness_preflight.json"
    atomic_write_text(prompt_path, prompt, allowed_root=repository_root)
    atomic_write_json(
        preflight_path,
        {
            "preflight_version": 2,
            "harness": "local",
            "run_id": run_id,
            "operation_id": operation.operation_id,
            "operation_type": operation.operation_type,
            "controller_skill": {
                "name": controller.name,
                "version": controller.version,
                "path": controller.relative_path,
                "sha256": controller.sha256,
            },
            "operation_skill": {
                "name": selected.name,
                "version": selected.version,
                "path": selected.relative_path,
                "sha256": selected.sha256,
            },
            "auxiliary_skills": [
                {
                    "name": skill.name,
                    "version": skill.version,
                    "path": skill.relative_path,
                    "sha256": skill.sha256,
                }
                for skill in auxiliary
            ],
            "prompt_injection_flags": list(injection_flags),
            "sequential": True,
        },
        allowed_root=repository_root,
    )
    before_snapshot = snapshot_repository(repository_root)
    _write_state(
        repository_root,
        operation,
        run_id=run_id,
        before_snapshot=before_snapshot,
        operation_rows_before=_operation_rows(repository_root),
        issue_rows_before=_issue_rows(repository_root),
    )
    return HarnessStart(
        run_id=run_id,
        operation_id=operation.operation_id,
        operation_type=operation.operation_type,
        payload_path=operation.payload_path,
        controller_prompt_path=prompt_path.relative_to(repository_root).as_posix(),
        result_path=result_relative_path(run_id, operation.operation_id),
        audit_path=(artifact_directory / "command_audit.json")
        .relative_to(repository_root)
        .as_posix(),
        controller_skill_path=controller.relative_path,
        operation_skill_path=selected.relative_path,
        auxiliary_skill_paths=tuple(skill.relative_path for skill in auxiliary),
    )


def _terminalize_result(
    repository_root: Path,
    operation: Operation,
    *,
    run_id: str,
    result: Mapping[str, object],
) -> str:
    status = str(result["status"])
    summary = str(result["summary"])
    result_path = result_relative_path(run_id, operation.operation_id)
    if status in {"succeeded", "skipped"}:
        complete_operation(
            repository_root,
            operation_id=operation.operation_id,
            run_id=run_id,
            terminal_status=status,
            result_path=result_path,
            result_summary=summary,
            terminal_reason=agent_terminal_reason(result, status),
        )
    elif status == "blocked":
        block_operation(
            repository_root,
            operation_id=operation.operation_id,
            run_id=run_id,
            reason=f"agent_result:blocked:{summary}",
        )
    else:
        fail_attempt(
            repository_root,
            operation_id=operation.operation_id,
            run_id=run_id,
            error=f"agent_result:failed:{summary}",
            result_path=result_path,
            result_summary=summary,
        )
    return status


def finish_local_harness_operation(
    repository_root: Path,
    *,
    run_id: str,
    operation_id: str,
) -> HarnessFinish:
    """Validate completed local-agent work and apply its deterministic queue disposition."""

    operation, before, operation_rows_before, issue_rows_before, state_path = _load_state(
        repository_root, run_id, operation_id
    )
    current_row = _operation_rows(repository_root).get(operation_id)
    if current_row != operation.to_row():
        raise AgentRunError("claimed operation row changed during the local harness run")
    after = snapshot_repository(repository_root)
    delta = compare_snapshots(before, after)
    validation = validate_agent_result(
        repository_root,
        run_id=run_id,
        operation=operation,
        before_snapshot=before,
        after_snapshot=after,
        delta=delta,
        operation_ids_before=set(operation_rows_before),
        operation_rows_before=operation_rows_before,
        issue_rows_before=issue_rows_before,
        environment={
            "WIKI_PATH": str((repository_root / "data" / "wiki").resolve()),
        },
    )
    if validation.passed and validation.result is not None:
        atomic_write_json(
            repository_root / result_relative_path(run_id, operation_id),
            dict(validation.result),
            allowed_root=repository_root,
        )
    validation_relative = Path("data") / "runs" / run_id / operation_id / "validation_report.json"
    atomic_write_json(
        repository_root / validation_relative,
        {
            "validation_version": 1,
            "harness": "local",
            "run_id": run_id,
            "operation_id": operation_id,
            "passed": validation.passed,
            "changed_paths": list(validation.changed_paths),
            "errors": list(validation.errors),
            "completed_at": format_timestamp(utc_now()),
        },
        allowed_root=repository_root,
    )
    state_path.unlink(missing_ok=True)
    if validation.errors:
        issue_id = record_issue(
            repository_root,
            issue_code="agent_result_validation_failed",
            impact=operation_validation_impact(operation.operation_type),
            severity="error",
            title=f"Local harness operation validation failed: {operation_id}",
            description="; ".join(validation.errors),
            entity_type="operation",
            entity_id=operation_id,
            owner="controller",
            related_run_id=run_id,
            related_operation_id=operation_id,
        )
        disposition = fail_attempt(
            repository_root,
            operation_id=operation_id,
            run_id=run_id,
            error=f"agent_validation_failed:{issue_id}",
        )
        raise AgentRunError(
            f"{'; '.join(validation.errors)}; recorded {issue_id}; queue disposition={disposition}"
        )
    assert validation.result is not None
    status = _terminalize_result(
        repository_root,
        operation,
        run_id=run_id,
        result=validation.result,
    )
    if status in {"succeeded", "skipped"}:
        resolve_matching_issues(
            repository_root,
            issue_code="agent_result_validation_failed",
            entity_type="operation",
            entity_id=operation_id,
            resolution=f"operation_validation_recovered: {operation_id}",
        )
    return HarnessFinish(
        run_id=run_id,
        operation_id=operation_id,
        status=status,
        changed_paths=validation.changed_paths,
        validation_path=validation_relative.as_posix(),
    )


__all__ = [
    "HarnessFinish",
    "HarnessStart",
    "finish_local_harness_operation",
    "start_local_harness_operation",
]
