"""Validate completed agent changes before any queue terminal transition."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator, FormatChecker

from papertrader.config import ConfigurationError, load_settings
from papertrader.integrity import is_runtime_path_allowed, validate_integrity
from papertrader.portfolio import reconcile_portfolio
from papertrader.queue import Operation
from papertrader.repository_state import RepositoryDelta, RepositorySnapshot
from papertrader.tables import read_table
from papertrader.utils import parse_timestamp, utc_now
from papertrader.wiki import lint_wiki

WIKI_RESEARCH_DOMAINS = frozenset(
    {
        "comparisons",
        "concepts",
        "ideas",
        "queries",
        "relationships",
        "securities",
        "strategies",
    }
)
RAW_EXTENSIONS = frozenset({".md", ".txt", ".pdf", ".png", ".jpg", ".jpeg", ".webp"})
COMMON_STRUCTURED_PATHS = frozenset({"data/issues.md", "data/tables/issues.csv"})


class AgentResultError(RuntimeError):
    """Raised when an agent result or its completed changes violate the contract."""


@dataclass(frozen=True, slots=True)
class AgentValidation:
    """Parsed result plus deterministic post-run errors and actual agent paths."""

    result: Mapping[str, object] | None
    changed_paths: tuple[str, ...]
    errors: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors and self.result is not None


def agent_terminal_reason(result: Mapping[str, object], status: str) -> str:
    """Return an explicit machine reason when the schema-valid result supplies one."""

    reason_code = result.get("reason_code")
    return str(reason_code) if isinstance(reason_code, str) else f"agent_result:{status}"


def result_relative_path(run_id: str, operation_id: str) -> str:
    """Return the only accepted manifest path for an operation attempt."""

    return f"data/runs/{run_id}/{operation_id}/agent_result.json"


def _schema_validator(repository_root: Path) -> Draft202012Validator:
    schema = json.loads(
        (repository_root / "schemas" / "agent_result.schema.json").read_text(encoding="utf-8")
    )
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _load_result(
    repository_root: Path, relative_path: str
) -> tuple[Mapping[str, object] | None, list[str]]:
    path = repository_root.joinpath(*PurePosixPath(relative_path).parts)
    if path.is_symlink() or not path.is_file():
        return None, [f"agent result is missing or a symlink: {relative_path}"]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"cannot read agent result {relative_path}: {exc}"]
    if not isinstance(value, dict):
        return None, ["agent result must be a JSON object"]
    errors = sorted(
        _schema_validator(repository_root).iter_errors(value), key=lambda error: list(error.path)
    )
    return value, [f"agent result schema: {error.message}" for error in errors]


def _strings(result: Mapping[str, object], field: str) -> tuple[str, ...]:
    value = result.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return ()
    return tuple(value)


def _is_wiki_path(path: PurePosixPath, domains: frozenset[str]) -> bool:
    if path in {
        PurePosixPath("data/wiki/index.md"),
        PurePosixPath("data/wiki/log.md"),
        PurePosixPath("data/wiki/research-catalog.md"),
    }:
        return True
    return (
        len(path.parts) >= 4
        and path.parts[:2] == ("data", "wiki")
        and path.parts[2] in domains
        and path.suffix == ".md"
    )


def _is_followup_path(path: PurePosixPath) -> bool:
    if path == PurePosixPath("data/operations/operations_TODO.csv"):
        return True
    return (
        len(path.parts) == 4
        and path.parts[:3] == ("data", "operations", "payloads")
        and path.suffix == ".json"
    )


def _is_operation_artifact(path: PurePosixPath, run_id: str, operation_id: str) -> bool:
    return (
        len(path.parts) == 5
        and path.parts[:4] == ("data", "runs", run_id, operation_id)
        and path.suffix in {".json", ".md"}
    )


def _path_allowed_for_operation(
    operation_type: str,
    raw_path: str,
    *,
    created: bool,
    youtube_video: bool = False,
) -> bool:
    path = PurePosixPath(raw_path)
    if raw_path in COMMON_STRUCTURED_PATHS or _is_followup_path(path):
        return True
    if operation_type == "wiki_ingest":
        if _is_wiki_path(path, WIKI_RESEARCH_DOMAINS):
            return True
        if path in {
            PurePosixPath("data/tables/source_registry.csv"),
            PurePosixPath("data/tables/source_history.csv"),
        }:
            return True
        if youtube_video and path == PurePosixPath("data/tables/securities.csv"):
            return True
        return (
            not youtube_video
            and created
            and len(path.parts) >= 4
            and path.parts[:3] == ("data", "wiki", "raw")
            and path.suffix in RAW_EXTENSIONS
        )
    if operation_type == "opportunity_research":
        return _is_wiki_path(path, WIKI_RESEARCH_DOMAINS)
    if operation_type == "idea_research":
        return raw_path == "data/tables/securities.csv" or _is_wiki_path(path, frozenset({"ideas"}))
    if operation_type == "security_research":
        return raw_path in {
            "data/tables/securities.csv",
            "data/tables/security_assessments.csv",
            "data/tables/source_registry.csv",
            "data/tables/source_history.csv",
        } or _is_wiki_path(path, frozenset({"securities"}))
    if operation_type == "relationship_research":
        return raw_path == "data/tables/relationships.csv" or _is_wiki_path(
            path, frozenset({"relationships"})
        )
    if operation_type == "strategy_research":
        return raw_path in {
            "data/tables/signals.csv",
            "data/tables/strategies.csv",
            "data/tables/strategy_legs.csv",
        } or _is_wiki_path(path, frozenset({"strategies"}))
    if operation_type == "execute_strategy":
        return raw_path in {
            "data/tables/order_legs.csv",
            "data/tables/orders.csv",
            "data/tables/signals.csv",
        } or _is_wiki_path(path, frozenset({"strategies"}))
    return False


def _command_parts(entry: Mapping[str, object]) -> tuple[str, ...]:
    argv = entry.get("argv")
    if not isinstance(argv, list) or not all(isinstance(value, str) for value in argv):
        return ()
    parts = tuple(argv)
    if not parts or parts[0] != "papertrader":
        return ()
    if len(parts) >= 3 and parts[1] == "--repository":
        return (parts[0], *parts[3:])
    return parts


def _command_allowed(
    operation_type: str,
    entry: Mapping[str, object],
    *,
    youtube_video: bool = False,
) -> bool:
    parts = _command_parts(entry)
    if len(parts) < 2:
        return False
    command = parts[1:]
    read_only = (
        command[:2]
        in {
            ("portfolio", "reconcile"),
            ("queue", "validate"),
            ("schema", "validate"),
            ("wiki", "lint"),
            ("allocation", "readiness"),
        }
        or command[:1] == ("integrity",)
        or command[:2] == ("runtime-whitelist", "validate")
    )
    if read_only:
        return True
    if command[:2] in {("issue", "record"), ("queue", "enqueue")}:
        return True
    if command[:2] == ("watchlist", "import"):
        return operation_type == "idea_research" or (
            operation_type == "wiki_ingest" and youtube_video
        )
    if command[:3] == ("research", "source", "record"):
        return operation_type in {"wiki_ingest", "security_research"}
    if command[:3] == ("research", "security", "upsert"):
        return operation_type == "security_research"
    if command[:3] == ("research", "assessment", "upsert"):
        return operation_type == "security_research"
    if command[:3] == ("research", "relationship", "upsert"):
        return operation_type == "relationship_research"
    if command[:3] == ("research", "strategy", "upsert"):
        return operation_type == "strategy_research"
    if command[:2] == ("signal", "create"):
        return operation_type == "strategy_research"
    if command[:2] in {("order", "create"), ("order", "create-baseline")}:
        return operation_type == "execute_strategy"
    if command[:2] == ("order", "cancel"):
        return operation_type == "execute_strategy"
    return False


def _load_command_audit(
    repository_root: Path, run_id: str, operation_id: str
) -> tuple[tuple[Mapping[str, object], ...], list[str]]:
    path = repository_root / "data" / "runs" / run_id / operation_id / "command_audit.json"
    if not path.exists():
        return (), []
    if path.is_symlink() or not path.is_file():
        return (), ["command audit must be a regular file"]
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return (), [f"cannot read command audit: {exc}"]
    if not isinstance(document, dict):
        return (), ["command audit must be an object"]
    if (
        document.get("audit_version") != 1
        or document.get("run_id") != run_id
        or document.get("operation_id") != operation_id
    ):
        return (), ["command audit identity mismatch"]
    raw_entries = document.get("entries")
    if not isinstance(raw_entries, list) or not all(
        isinstance(entry, dict) for entry in raw_entries
    ):
        return (), ["command audit entries must be objects"]
    entries = tuple(entry for entry in raw_entries if isinstance(entry, dict))
    errors: list[str] = []
    for index, entry in enumerate(entries):
        if set(entry) != {
            "command",
            "argv",
            "request",
            "started_at",
            "completed_at",
            "exit_code",
            "changed_paths",
            "changes",
        }:
            errors.append(f"command audit entry {index} has unexpected fields")
            continue
        if not isinstance(entry["command"], str) or not _command_parts(entry):
            errors.append(f"command audit entry {index} has invalid argv")
        if not isinstance(entry["exit_code"], int):
            errors.append(f"command audit entry {index} has invalid exit code")
        request = entry["request"]
        if request is not None:
            if (
                not isinstance(request, dict)
                or set(request) != {"path", "identity"}
                or not isinstance(request.get("path"), str)
            ):
                errors.append(f"command audit entry {index} has invalid request receipt")
            else:
                identity = request.get("identity")
                if identity is not None and (
                    not isinstance(identity, list)
                    or len(identity) != 4
                    or not isinstance(identity[0], str)
                    or not isinstance(identity[1], str)
                    or not isinstance(identity[2], int)
                    or not isinstance(identity[3], int)
                ):
                    errors.append(f"command audit entry {index} has invalid request identity")
        paths = entry["changed_paths"]
        if (
            not isinstance(paths, list)
            or not all(isinstance(value, str) for value in paths)
            or paths != sorted(set(paths))
        ):
            errors.append(f"command audit entry {index} has non-canonical changed paths")
        changes = entry["changes"]
        if not isinstance(changes, list) or not all(isinstance(change, dict) for change in changes):
            errors.append(f"command audit entry {index} has invalid content changes")
        else:
            change_paths: list[str] = []
            for change in changes:
                if set(change) != {"path", "before", "after"} or not isinstance(
                    change.get("path"), str
                ):
                    errors.append(f"command audit entry {index} has malformed content identity")
                    continue
                change_paths.append(str(change["path"]))
                for field in ("before", "after"):
                    identity = change.get(field)
                    if identity is not None and (
                        not isinstance(identity, list)
                        or len(identity) != 4
                        or not isinstance(identity[0], str)
                        or not isinstance(identity[1], str)
                        or not isinstance(identity[2], int)
                        or not isinstance(identity[3], int)
                    ):
                        errors.append(f"command audit entry {index} has invalid {field} identity")
            if isinstance(paths, list) and change_paths != paths:
                errors.append(f"command audit entry {index} paths and identities differ")
        try:
            started = parse_timestamp(str(entry["started_at"]))
            completed = parse_timestamp(str(entry["completed_at"]))
            if started is None or completed is None or completed < started:
                raise ValueError("invalid command chronology")
        except (ValueError, TypeError) as exc:
            errors.append(f"command audit entry {index} timestamp error: {exc}")
    return entries, errors


def _structured_path(path: str) -> bool:
    value = PurePosixPath(path)
    return (
        value.suffix == ".csv"
        or path == "data/issues.md"
        or value.parts[:3] == ("data", "operations", "payloads")
    )


def _validate_commands(
    repository_root: Path,
    run_id: str,
    operation: Operation,
    result: Mapping[str, object],
    changed_paths: Sequence[str],
    before_snapshot: RepositorySnapshot,
    after_snapshot: RepositorySnapshot,
    *,
    youtube_video: bool = False,
) -> list[str]:
    entries, errors = _load_command_audit(repository_root, run_id, operation.operation_id)
    audited_commands = tuple(
        str(entry.get("command", "")) for entry in entries if isinstance(entry.get("command"), str)
    )
    reported = _strings(result, "commands_run")
    if reported != audited_commands:
        errors.append("commands_run does not exactly match deterministic CLI audit receipts")
    for index, entry in enumerate(entries):
        if not _command_allowed(operation.operation_type, entry, youtube_video=youtube_video):
            errors.append(f"command audit entry {index} is outside the operation skill scope")
        request = entry.get("request")
        if request is None:
            continue
        if not isinstance(request, dict):
            continue
        request_path = request.get("path")
        raw_identity = request.get("identity")
        identity = tuple(raw_identity) if isinstance(raw_identity, list) else None
        request_relative = PurePosixPath(request_path) if isinstance(request_path, str) else None
        valid_path = (
            request_relative is not None
            and _is_operation_artifact(request_relative, run_id, operation.operation_id)
            and request_relative.suffix == ".json"
            and request_relative.name
            not in {
                "agent_result.json",
                "command_audit.json",
                "hermes_preflight.json",
                "hermes_run.json",
                "validation_report.json",
            }
        )
        if entry.get("exit_code") == 0 and (not valid_path or identity is None):
            errors.append(f"command audit entry {index} lacks an immutable operation request")
            continue
        if valid_path and identity is not None:
            final = after_snapshot.files.get(str(request_path))
            if final is None or final.content_identity != identity:
                errors.append(f"command request changed after audit entry {index}: {request_path}")
    successful_paths: set[str] = set()
    for entry in entries:
        paths = entry.get("changed_paths")
        if entry.get("exit_code") == 0 and isinstance(paths, list):
            successful_paths.update(path for path in paths if isinstance(path, str))
    for path in changed_paths:
        if _structured_path(path) and path not in successful_paths:
            errors.append(f"structured change lacks a successful CLI receipt: {path}")
    for path in (value for value in changed_paths if _structured_path(value)):
        initial = before_snapshot.files.get(path)
        expected = initial.content_identity if initial else None
        for index, entry in enumerate(entries):
            changes = entry.get("changes")
            if not isinstance(changes, list):
                continue
            matching = next(
                (
                    change
                    for change in changes
                    if isinstance(change, dict) and change.get("path") == path
                ),
                None,
            )
            if matching is None:
                continue
            raw_before = matching.get("before")
            before_identity = tuple(raw_before) if isinstance(raw_before, list) else None
            if before_identity != expected:
                errors.append(
                    f"structured change occurred outside CLI receipt chain before entry {index}: "
                    f"{path}"
                )
            raw_after = matching.get("after")
            expected = tuple(raw_after) if isinstance(raw_after, list) else None
        final = after_snapshot.files.get(path)
        final_identity = final.content_identity if final else None
        if expected != final_identity:
            errors.append(f"structured change occurred after its final CLI receipt: {path}")
    return errors


def _operation_ids(repository_root: Path) -> set[str]:
    return {
        row["operation_id"]
        for table in ("operations_todo", "operations_history")
        for row in read_table(repository_root, table)
    }


def _operation_rows(repository_root: Path) -> dict[str, dict[str, str]]:
    return {
        row["operation_id"]: row
        for table in ("operations_todo", "operations_history")
        for row in read_table(repository_root, table)
    }


def _issue_rows(repository_root: Path) -> dict[str, dict[str, str]]:
    return {row["issue_id"]: row for row in read_table(repository_root, "issues")}


def _security_assessment_result_errors(
    repository_root: Path,
    *,
    operation: Operation,
    status: object,
    run_id: str,
    environment: Mapping[str, str],
) -> list[str]:
    if operation.operation_type != "security_research" or status not in {"succeeded", "skipped"}:
        return []
    assessment = next(
        (
            row
            for row in read_table(repository_root, "security_assessments")
            if row["security_id"] == operation.entity_id
        ),
        None,
    )
    if assessment is None:
        if status == "succeeded":
            return ["completed security research requires this run's comparable assessment"]
        return ["skipped security research requires an existing current assessment"]
    if status == "succeeded" and assessment["run_id"] != run_id:
        return ["completed security research requires this run's comparable assessment"]
    try:
        settings = load_settings(repository_root, environment)
        from papertrader.allocation import _assessment_readiness_errors

        freshness_errors = _assessment_readiness_errors(
            assessment,
            {row["source_id"]: row for row in read_table(repository_root, "source_registry")},
            settings,
            now=utc_now().replace(microsecond=0),
        )
    except ConfigurationError as exc:
        return [f"cannot validate security assessment freshness: {exc}"]
    if freshness_errors:
        prefix = "completed" if status == "succeeded" else "skipped"
        return [
            f"{prefix} security research requires fresh registered assessment evidence: "
            + ",".join(freshness_errors)
        ]
    return []


def _baseline_signal_followup_errors(
    repository_root: Path,
    *,
    run_id: str,
    operation: Operation,
    created_operation_ids: set[str],
    operation_rows_after: Mapping[str, Mapping[str, str]],
) -> list[str]:
    if operation.operation_type != "strategy_research":
        return []
    strategy = next(
        (
            row
            for row in read_table(repository_root, "strategies")
            if row["strategy_id"] == operation.entity_id
        ),
        None,
    )
    if strategy is None or strategy["sleeve"] != "baseline":
        return []
    signals = [
        row
        for row in read_table(repository_root, "signals")
        if row["strategy_id"] == operation.entity_id and row["run_id"] == run_id
    ]
    errors: list[str] = []
    for signal in signals:
        matches = [
            row
            for operation_id, row in operation_rows_after.items()
            if operation_id in created_operation_ids
            and row["operation_type"] == "execute_strategy"
            and row["entity_id"] == operation.entity_id
        ]
        exact: list[Mapping[str, str]] = []
        for row in matches:
            payload_path = repository_root.joinpath(*PurePosixPath(row["payload_path"]).parts)
            try:
                payload = json.loads(payload_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            inputs = payload.get("inputs") if isinstance(payload, dict) else None
            if (
                isinstance(inputs, dict)
                and inputs.get("strategy_id") == operation.entity_id
                and inputs.get("signal_id") == signal["signal_id"]
                and inputs.get("action") == signal["signal_type"]
            ):
                exact.append(row)
        if len(exact) != 1:
            errors.append(
                "baseline signal requires exactly one matching execute_strategy follow-up: "
                f"{signal['signal_id']}"
            )
    return errors


def _payload_inputs(repository_root: Path, row: Mapping[str, str]) -> Mapping[str, object] | None:
    path = PurePosixPath(row["payload_path"])
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.parts[:3] != ("data", "operations", "payloads")
        or path.suffix != ".json"
    ):
        return None
    absolute = repository_root.joinpath(*path.parts)
    if absolute.is_symlink() or not absolute.is_file():
        return None
    try:
        payload = json.loads(absolute.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    inputs = payload.get("inputs") if isinstance(payload, dict) else None
    return inputs if isinstance(inputs, dict) else None


def _security_idea_followup_errors(
    repository_root: Path,
    *,
    run_id: str,
    operation: Operation,
    status: object,
    operation_rows_after: Mapping[str, Mapping[str, str]],
) -> list[str]:
    """Require every completed security review to refresh each directly linked idea."""

    if operation.operation_type != "security_research" or status != "succeeded":
        return []
    source_inputs = _payload_inputs(repository_root, operation.to_row()) or {}
    linked_idea_ids = {
        row["idea_id"]
        for row in read_table(repository_root, "relationships")
        if row["security_id"] == operation.entity_id and row["status"] == "accepted"
    }
    idea_id = source_inputs.get("idea_id")
    if isinstance(idea_id, str) and idea_id:
        linked_idea_ids.add(idea_id)
    idea_ids = source_inputs.get("idea_ids")
    if isinstance(idea_ids, list):
        linked_idea_ids.update(value for value in idea_ids if isinstance(value, str) and value)
    active_operation_ids = {
        row["operation_id"] for row in read_table(repository_root, "operations_todo")
    }
    errors: list[str] = []
    for linked_idea_id in sorted(linked_idea_ids):
        exact: list[str] = []
        for operation_id, row in operation_rows_after.items():
            if (
                operation_id not in active_operation_ids
                or row["operation_type"] != "idea_research"
                or row["entity_id"] != linked_idea_id
                or operation.operation_id not in row["depends_on"].split("|")
            ):
                continue
            inputs = _payload_inputs(repository_root, row)
            if (
                inputs is not None
                and inputs.get("idea_id") == linked_idea_id
                and inputs.get("security_id") == operation.entity_id
                and inputs.get("security_research_operation_id") == operation.operation_id
                and inputs.get("security_research_result_path")
                == result_relative_path(run_id, operation.operation_id)
            ):
                exact.append(operation_id)
        if len(exact) != 1:
            errors.append(
                "completed security research requires exactly one matching idea_research "
                f"follow-up for {linked_idea_id}"
            )
    return errors


def _idea_security_followup_errors(
    repository_root: Path,
    *,
    operation: Operation,
    status: object,
    created_operation_ids: set[str],
    operation_rows_after: Mapping[str, Mapping[str, str]],
) -> list[str]:
    """Keep every idea-created security review causally linked and dependency ordered."""

    if operation.operation_type != "idea_research" or status != "succeeded":
        return []
    errors: list[str] = []
    for operation_id in sorted(created_operation_ids):
        row = operation_rows_after.get(operation_id)
        if row is None or row["operation_type"] != "security_research":
            continue
        inputs = _payload_inputs(repository_root, row)
        if (
            inputs is None
            or inputs.get("idea_id") != operation.entity_id
            or inputs.get("security_id") != row["entity_id"]
            or operation.operation_id not in row["depends_on"].split("|")
        ):
            errors.append(
                "idea-created security research must carry the idea/security identities and "
                f"depend on the idea operation: {operation_id}"
            )
    return errors


def _youtube_wiki_ingest_errors(
    repository_root: Path,
    *,
    run_id: str,
    operation: Operation,
    status: object,
    result: Mapping[str, object],
    changed_paths: Sequence[str],
    created_operation_ids: set[str],
    operation_rows_after: Mapping[str, Mapping[str, str]],
    followup_priority: int,
) -> list[str]:
    """Enforce the stronger no-analysis-without-corroboration YouTube boundary."""

    inputs = _payload_inputs(repository_root, operation.to_row()) or {}
    if operation.operation_type != "wiki_ingest" or inputs.get("source_kind") != "youtube_video":
        return []
    errors: list[str] = []
    video_id = inputs.get("video_id")
    source_id = inputs.get("source_id")
    video_url = inputs.get("video_url")
    channel_handle = inputs.get("channel_handle")
    if (
        not isinstance(video_id, str)
        or source_id != f"youtube_{video_id}"
        or operation.entity_id != source_id
    ):
        errors.append("YouTube wiki ingest payload/source identity mismatch")
    if status == "skipped":
        if result.get("reason_code") != "youtube_transcript_unavailable":
            errors.append(
                "skipped YouTube wiki ingest requires reason_code youtube_transcript_unavailable"
            )
        if changed_paths:
            errors.append("transcript-unavailable YouTube ingest must not mutate repository state")
        if created_operation_ids:
            errors.append("transcript-unavailable YouTube ingest must not enqueue follow-ups")
        return errors
    if status != "succeeded":
        return errors
    if "reason_code" in result:
        errors.append("successful YouTube wiki ingest must not report a terminal reason_code")
    analysis_path = f"data/runs/{run_id}/{operation.operation_id}/youtube_analysis.md"
    if analysis_path not in changed_paths:
        errors.append("successful YouTube wiki ingest requires youtube_analysis.md")
    registry = {row["source_id"]: row for row in read_table(repository_root, "source_registry")}
    source = registry.get(str(source_id))
    if source is None:
        errors.append("successful YouTube wiki ingest requires a registered source")
        transcript_digest = ""
    else:
        transcript_digest = source["content_hash"]
        if (
            source["source_type"] != "youtube_video"
            or source["url"] != video_url
            or source["canonical_url"] != video_url
            or source["publisher"] != channel_handle
            or not re.fullmatch(r"[a-f0-9]{64}", transcript_digest)
        ):
            errors.append("registered YouTube source metadata or transcript hash is invalid")
        matching_history = [
            row
            for row in read_table(repository_root, "source_history")
            if row["source_id"] == source_id
            and row["run_id"] == run_id
            and row["content_hash"] == transcript_digest
        ]
        if len(matching_history) != 1:
            errors.append("YouTube source requires exactly one matching source-history record")
    analysis = repository_root / analysis_path
    if analysis.is_file() and not analysis.is_symlink():
        text = analysis.read_text(encoding="utf-8")
        for required in (str(video_id), str(video_url), transcript_digest):
            if required and required not in text:
                errors.append(
                    "youtube_analysis.md must identify the video URL, ID, and transcript hash"
                )
                break

    for operation_id in sorted(created_operation_ids):
        row = operation_rows_after.get(operation_id)
        if row is None:
            continue
        if row["operation_type"] not in {"idea_research", "security_research"}:
            errors.append(f"YouTube ingest may enqueue only idea/security research: {operation_id}")
        if row["priority"] != str(followup_priority):
            errors.append(
                f"YouTube follow-up must use priority {followup_priority}: {operation_id}"
            )
        if operation.operation_id not in row["depends_on"].split("|"):
            errors.append(f"YouTube follow-up must depend on its ingest operation: {operation_id}")

    imported_security_ids = {
        row["security_id"]
        for row in read_table(repository_root, "securities")
        if row["source"] == video_url
    }
    for security_id in sorted(imported_security_ids):
        matches = []
        for operation_id in created_operation_ids:
            row = operation_rows_after.get(operation_id)
            if (
                row is None
                or row["operation_type"] != "security_research"
                or row["entity_id"] != security_id
            ):
                continue
            followup_inputs = _payload_inputs(repository_root, row)
            if followup_inputs is not None and followup_inputs.get("security_id") == security_id:
                matches.append(operation_id)
        if len(matches) != 1:
            errors.append(
                "YouTube-imported security requires exactly one security_research follow-up: "
                f"{security_id}"
            )
    return errors


def validate_agent_result(
    repository_root: Path,
    *,
    run_id: str,
    operation: Operation,
    before_snapshot: RepositorySnapshot,
    after_snapshot: RepositorySnapshot,
    delta: RepositoryDelta,
    operation_ids_before: set[str],
    operation_rows_before: Mapping[str, Mapping[str, str]],
    issue_rows_before: Mapping[str, Mapping[str, str]],
    environment: Mapping[str, str],
) -> AgentValidation:
    """Validate schema, exact changes, receipts, scope, freshness, and repository state."""

    relative_result = result_relative_path(run_id, operation.operation_id)
    result, errors = _load_result(repository_root, relative_result)
    internal_paths = {
        relative_result,
        f"data/runs/{run_id}/{operation.operation_id}/command_audit.json",
        f"data/runs/{run_id}/{operation.operation_id}/hermes_run.json",
    }
    changed_paths = tuple(path for path in delta.changed if path not in internal_paths)
    source_inputs = _payload_inputs(repository_root, operation.to_row()) or {}
    youtube_video = (
        operation.operation_type == "wiki_ingest"
        and source_inputs.get("source_kind") == "youtube_video"
    )
    created = set(delta.created)
    reserved = {
        f"data/runs/{run_id}/{operation.operation_id}/controller_prompt.md",
        f"data/runs/{run_id}/{operation.operation_id}/harness_preflight.json",
        f"data/runs/{run_id}/{operation.operation_id}/hermes_preflight.json",
        f"data/runs/{run_id}/{operation.operation_id}/validation_report.json",
    }
    touched_reserved = sorted(reserved.intersection(delta.changed))
    if touched_reserved:
        errors.append(f"agent modified controller-owned artifacts: {touched_reserved}")
    if delta.deleted:
        errors.append(f"agent deletions are not permitted: {list(delta.deleted)}")
    for path in delta.changed:
        state = after_snapshot.files.get(path)
        if state is not None and state.kind != "file":
            errors.append(f"agent-created symlink or special file is forbidden: {path}")
        if not is_runtime_path_allowed(path):
            errors.append(f"agent changed a non-runtime path: {path}")
    for path in changed_paths:
        relative = PurePosixPath(path)
        if not _is_operation_artifact(
            relative, run_id, operation.operation_id
        ) and not _path_allowed_for_operation(
            operation.operation_type,
            path,
            created=path in created,
            youtube_video=youtube_video,
        ):
            errors.append(f"path is outside {operation.operation_type} scope: {path}")
    if result is None:
        return AgentValidation(None, changed_paths, tuple(sorted(set(errors))))
    if result.get("operation_id") != operation.operation_id:
        errors.append("agent result operation_id does not match the claimed operation")
    reported_paths = _strings(result, "files_changed")
    if reported_paths != tuple(sorted(set(reported_paths))):
        errors.append("files_changed must be unique and sorted")
    if reported_paths != changed_paths:
        errors.append(
            f"files_changed is stale or incomplete: reported={list(reported_paths)!r}, "
            f"actual={list(changed_paths)!r}"
        )
    for field in ("operations_created", "issues_recorded"):
        values = _strings(result, field)
        if values != tuple(sorted(set(values))):
            errors.append(f"{field} must be unique and sorted")
    result_state = after_snapshot.files.get(relative_result)
    if result_state is not None:
        for path in (
            *changed_paths,
            f"data/runs/{run_id}/{operation.operation_id}/command_audit.json",
        ):
            state = after_snapshot.files.get(path)
            if state is not None and state.modified_ns > result_state.modified_ns:
                errors.append(f"agent result was written before completed change: {path}")
    status = result.get("status")
    evidence = result.get("evidence")
    if status in {"skipped", "blocked", "failed"} and not evidence:
        errors.append(f"{status} result requires evidence")
    if operation.operation_type in {"opportunity_research", "strategy_research"} and not evidence:
        errors.append(f"{operation.operation_type} result must be evidence-linked")
    if (
        operation.operation_type == "security_research"
        and status == "skipped"
        and "data/tables/security_assessments.csv" in changed_paths
    ):
        errors.append("skipped security research must preserve its existing current assessment")
    errors.extend(
        _security_assessment_result_errors(
            repository_root,
            operation=operation,
            status=status,
            run_id=run_id,
            environment=environment,
        )
    )
    validation = result.get("validation")
    if status in {"succeeded", "skipped"} and (
        not isinstance(validation, dict) or validation.get("passed") is not True
    ):
        errors.append("successful or skipped result must report passing validation")
    created_operations = _operation_ids(repository_root) - operation_ids_before
    reported_operations = set(_strings(result, "operations_created"))
    if created_operations != reported_operations:
        errors.append(
            "operations_created does not match newly enqueued operation IDs: "
            f"reported={sorted(reported_operations)!r}, actual={sorted(created_operations)!r}"
        )
    operation_rows_after = _operation_rows(repository_root)
    errors.extend(
        _baseline_signal_followup_errors(
            repository_root,
            run_id=run_id,
            operation=operation,
            created_operation_ids=created_operations,
            operation_rows_after=operation_rows_after,
        )
    )
    errors.extend(
        _security_idea_followup_errors(
            repository_root,
            run_id=run_id,
            operation=operation,
            status=status,
            operation_rows_after=operation_rows_after,
        )
    )
    errors.extend(
        _idea_security_followup_errors(
            repository_root,
            operation=operation,
            status=status,
            created_operation_ids=created_operations,
            operation_rows_after=operation_rows_after,
        )
    )
    try:
        followup_priority = load_settings(repository_root, environment).youtube.followup_priority
    except ConfigurationError as exc:
        errors.append(f"cannot validate YouTube follow-up priority: {exc}")
        followup_priority = 66
    errors.extend(
        _youtube_wiki_ingest_errors(
            repository_root,
            run_id=run_id,
            operation=operation,
            status=status,
            result=result,
            changed_paths=changed_paths,
            created_operation_ids=created_operations,
            operation_rows_after=operation_rows_after,
            followup_priority=followup_priority,
        )
    )
    altered_existing_operations = sorted(
        operation_id
        for operation_id, row in operation_rows_before.items()
        if operation_rows_after.get(operation_id) != row
    )
    if altered_existing_operations:
        errors.append(
            f"agent altered or removed existing queue/history rows: {altered_existing_operations!r}"
        )
    issue_rows_after = _issue_rows(repository_root)
    changed_issues = {
        issue_id
        for issue_id in set(issue_rows_before) | set(issue_rows_after)
        if issue_rows_before.get(issue_id) != issue_rows_after.get(issue_id)
    }
    reported_issues = set(_strings(result, "issues_recorded"))
    if changed_issues != reported_issues:
        errors.append(
            "issues_recorded does not match created or updated issue IDs: "
            f"reported={sorted(reported_issues)!r}, actual={sorted(changed_issues)!r}"
        )
    errors.extend(
        _validate_commands(
            repository_root,
            run_id,
            operation,
            result,
            changed_paths,
            before_snapshot,
            after_snapshot,
            youtube_video=youtube_video,
        )
    )
    errors.extend(
        f"post-run integrity: {error}"
        for error in validate_integrity(
            repository_root,
            environment,
            require_current_publication=False,
        )
    )
    errors.extend(
        f"post-run wiki lint: {error}" for error in lint_wiki(repository_root / "data" / "wiki")
    )
    errors.extend(f"post-run portfolio: {error}" for error in reconcile_portfolio(repository_root))
    # The baseline is deliberately consumed here: an unchanged listed path must not be accepted.
    for path in reported_paths:
        if (
            path in before_snapshot.files
            and path in after_snapshot.files
            and before_snapshot.files[path].content_identity
            == after_snapshot.files[path].content_identity
        ):
            errors.append(f"files_changed contains an unchanged old value: {path}")
    return AgentValidation(result, changed_paths, tuple(sorted(set(errors))))


__all__ = [
    "AgentResultError",
    "AgentValidation",
    "agent_terminal_reason",
    "result_relative_path",
    "validate_agent_result",
]
