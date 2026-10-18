"""One research model, read-only tools, credential isolation and a bounded cycle."""

from __future__ import annotations

import configparser
import json
import os
import shutil
import signal
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from papertrader.atomic_io import atomic_write_text
from papertrader.research_queue import admit, claim, entity_key, finish, queue_limits
from papertrader.research_results import commit_result, context_packet, prepare_result
from papertrader.research_state import contracts, read_state, validate_state
from papertrader.research_transaction import research_lock


@dataclass(frozen=True)
class ResearchLimits:
    model: str = "gpt-5.6-sol"
    timeout_seconds: int = 600
    max_turns: int = 24
    max_web_calls: int = 12
    assessment_freshness_days: int = 30


HERMES_UID = 10_000
HERMES_GID = 10_000
SAFE_EXCEPTION_TYPES = {
    "FileNotFoundError",
    "JSONDecodeError",
    "KeyError",
    "OSError",
    "PermissionError",
    "RuntimeError",
    "TimeoutError",
    "TypeError",
    "UnicodeDecodeError",
    "ValueError",
}
FAILURE_STAGES = {"context", "model", "validation", "commit"}
WORKER_FILES = (
    "__init__.py",
    "atomic_io.py",
    "research_state.py",
    "research_web.py",
    "research_worker.py",
)


def _failure_diagnostic(exc: Exception, stage: str) -> dict[str, str]:
    """Return a useful failure location without exception text or external paths."""
    safe_stage = stage if stage in FAILURE_STAGES else "validation"
    exception_type = type(exc).__name__
    if exception_type not in SAFE_EXCEPTION_TYPES:
        exception_type = "Exception"
    package = Path(__file__).resolve().parent
    location = "papertrader.unknown:0"
    traceback = exc.__traceback__
    while traceback is not None:
        code = traceback.tb_frame.f_code
        try:
            relative = Path(code.co_filename).resolve().relative_to(package)
        except ValueError:
            traceback = traceback.tb_next
            continue
        module = ".".join(("papertrader", *relative.with_suffix("").parts))
        function = code.co_name
        if function.isidentifier():
            location = f"{module}.{function}:{traceback.tb_lineno}"
        traceback = traceback.tb_next
    return {"stage": safe_stage, "error": exception_type, "location": location}


def _bounded_usage(response: dict[str, Any], limits: ResearchLimits) -> dict[str, str]:
    """Expose only trustworthy bounded counters from a completed worker response."""
    usage = response.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("invalid worker usage")
    calls = usage.get("web_requests")
    if calls is None:
        return {}
    if type(calls) is int and 0 <= calls <= limits.max_web_calls:
        return {"web_requests": str(calls)}
    raise ValueError("invalid worker web usage")


def research_limits(root: Path) -> ResearchLimits:
    config = configparser.ConfigParser()
    config.read(root / "research.ini")
    defaults = ResearchLimits()
    values = {
        key: config.getint("research", key, fallback=getattr(defaults, key))
        for key in ("timeout_seconds", "max_turns", "max_web_calls", "assessment_freshness_days")
    }
    if not all(1 <= value <= 3600 for value in values.values()):
        raise ValueError("invalid research budget")
    model = config.get("research", "model", fallback=defaults.model)
    if not model or len(model) > 120:
        raise ValueError("invalid research model")
    return ResearchLimits(model=model, **values)


def agent_environment(home: Path, code_roots: list[Path]) -> dict[str, str]:
    """Inference authentication is confined to home/auth.json, never Git credentials."""
    allowed = {"PATH", "LANG", "LC_ALL", "LC_CTYPE", "TZ", "SSL_CERT_FILE", "SSL_CERT_DIR"}
    environment = {key: value for key, value in os.environ.items() if key in allowed}
    environment.update(
        HOME=str(home),
        HERMES_HOME=str(home),
        PYTHONPATH=os.pathsep.join(str(path) for path in code_roots),
        PYTHONUNBUFFERED="1",
        PYTHONDONTWRITEBYTECODE="1",
        HERMES_NON_INTERACTIVE="1",
    )
    return environment


def _agent_access(path: Path, mode: int) -> None:
    path.chmod(mode)
    if os.geteuid() == 0:
        os.chown(path, HERMES_UID, HERMES_GID)


def _stage_worker(root: Path, directory: Path) -> Path:
    """Copy only the broker/worker modules; never expose the repository or .git."""
    package = directory / "worker-code" / "papertrader"
    package.mkdir(parents=True)
    for name in WORKER_FILES:
        target = package / name
        shutil.copyfile(root / "src/papertrader" / name, target)
        _agent_access(target, 0o400)
    _agent_access(package.parent, 0o700)
    _agent_access(package, 0o700)
    return package.parent


def run_model(root: Path, packet: dict[str, Any], limits: ResearchLimits) -> dict[str, Any]:
    """Run inside the pinned Hermes image; no repository-write token in child env."""
    home_path = Path(os.environ.get("HERMES_HOME", "/tmp/papertrader-hermes"))
    if home_path.is_symlink():
        raise RuntimeError("symlink research profile forbidden")
    home = home_path.resolve()
    python = Path(os.environ.get("PAPERTRADER_HERMES_PYTHON", "/opt/hermes/.venv/bin/python"))
    hermes_code = Path(os.environ.get("PAPERTRADER_HERMES_CODE", "/opt/hermes"))
    if (
        not python.is_file()
        or not (home / "auth.json").is_file()
        or (home / "auth.json").is_symlink()
    ):
        raise RuntimeError("isolated_research_inference_unavailable")
    for name in ("plugins", "hooks", "memories"):
        if (home / name).exists():
            raise RuntimeError("unmanaged_research_profile")
    configuration = {
        "model": {"default": limits.model, "provider": "openai-codex"},
        "agent": {"max_turns": limits.max_turns, "api_max_retries": 1},
        "mcp_servers": {},
        "skills": {"external_dirs": []},
        "worktree": False,
    }
    atomic_write_text(home / "config.yaml", yaml.safe_dump(configuration), allowed_root=home)
    _agent_access(home, 0o700)
    _agent_access(home / "auth.json", 0o600)
    _agent_access(home / "config.yaml", 0o600)
    with tempfile.TemporaryDirectory(prefix="papertrader-research-") as work:
        directory = Path(work)
        _agent_access(directory, 0o700)
        worker_code = _stage_worker(root, directory)
        request = directory / "request.json"
        request.write_text(json.dumps(dict(context=packet, limits=vars(limits))))
        _agent_access(request, 0o600)
        environment = agent_environment(home, [worker_code, hermes_code])
        credentials: dict[str, Any] = {}
        if os.geteuid() == 0:
            credentials = {"user": HERMES_UID, "group": HERMES_GID, "extra_groups": ()}
        process = subprocess.Popen(
            [str(python), "-m", "papertrader.research_worker", str(request)],
            cwd=directory,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            start_new_session=True,
            **credentials,
        )
        try:
            stdout, _ = process.communicate(timeout=limits.timeout_seconds)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
            raise RuntimeError("research_timeout") from None
        if process.returncode or len(stdout.encode()) > 300000:
            raise RuntimeError("research_model_failed")
        document = json.loads(stdout)
        if not isinstance(document, dict) or set(document) != {"result", "observations", "usage"}:
            raise ValueError("invalid research worker response")
        return document


def run_cycle(
    root: Path,
    *,
    dry_run: bool = True,
    entity_type: str = "",
    entity_id: str = "",
    reserved_operations: int = 0,
    executor: Callable[[Path, dict[str, Any], ResearchLimits], dict[str, Any]] = run_model,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> dict[str, Any]:
    limits, queue_budget = research_limits(root), queue_limits(root)
    if not 0 <= reserved_operations <= queue_budget.max_daily_operations:
        raise ValueError("invalid reserved research budget")
    outcomes: list[dict[str, str]] = []
    changed: set[str] = set()
    total_web_requests = 0
    with research_lock(root):
        state = read_state(root)
        errors = validate_state(root, state)
        if errors:
            raise ValueError("; ".join(errors[:8]))
        if entity_id:
            entity_key(state, entity_type, entity_id)
            requested_key = (entity_type, entity_id)
            admit(
                state,
                entity_type,
                entity_id,
                reasons={"explicit_manual_request"},
                priority=100,
                manual=True,
                now=clock(),
                limits=queue_budget,
            )
        if dry_run:
            return dict(
                status="dry_run",
                exit_code=0,
                maximum_operations=1 if entity_id else queue_budget.max_daily_operations,
                queue=state["research_queue"],
                model=limits.model,
            )
        excluded: set[tuple[str, str]] = set()
        for _ in range(1 if entity_id else queue_budget.max_daily_operations - reserved_operations):
            if entity_id:
                # Isolate the explicit entity while claiming so global queue age
                # cannot redirect a manual single-entity run. Restore unrelated
                # rows byte-for-byte before any state commit.
                queue = state["research_queue"]
                unrelated = [
                    row for row in queue if (row["entity_type"], row["entity_id"]) != requested_key
                ]
                if any(row["status"] == "running" for row in unrelated):
                    task = None
                else:
                    state["research_queue"] = [
                        row
                        for row in queue
                        if (row["entity_type"], row["entity_id"]) == requested_key
                    ]
                    try:
                        task = claim(state, now=clock(), excluded=excluded, limits=queue_budget)
                    finally:
                        state["research_queue"].extend(unrelated)
            else:
                task = claim(state, now=clock(), excluded=excluded, limits=queue_budget)
            if task is None:
                break
            excluded.add((task["entity_type"], task["entity_id"]))
            # Persist a recoverable short lease, without an inner Git checkpoint.
            changed.update(commit_result(root, state, {}))
            operation = (
                "research_security" if task["entity_type"] == "security" else "research_idea"
            )
            stage = "context"
            operation_usage: dict[str, str] = {}
            try:
                packet = context_packet(
                    root, state, operation=operation, entity_id=task["entity_id"]
                )
                packet["as_of"] = clock().isoformat().replace("+00:00", "Z")
                packet["contracts"] = {
                    name: list(contract.columns) for name, contract in contracts(root).items()
                }
                packet["limits"] = vars(limits)
                packet["skill"] = (root / "skills" / operation / "SKILL.md").read_text()
                stage = "model"
                response = executor(root, packet, limits)
                stage = "validation"
                operation_usage = _bounded_usage(response, limits)
                total_web_requests += int(operation_usage.get("web_requests", "0"))
                candidate, pages = prepare_result(
                    root,
                    state,
                    response["result"],
                    operation=operation,
                    entity_id=task["entity_id"],
                    now=clock(),
                    observations=response["observations"],
                    freshness_days=limits.assessment_freshness_days,
                )
                stage = "commit"
                finish(candidate, task, now=clock(), limits=queue_budget)
                changed.update(commit_result(root, candidate, pages))
                state = candidate
                outcomes.append(
                    dict(
                        entity_id=task["entity_id"],
                        status=response["result"]["outcome"],
                        **operation_usage,
                    )
                )
            except Exception as exc:
                # Diagnostics use only a fixed stage, allowlisted type and project source location.
                diagnostic = _failure_diagnostic(exc, stage)
                failure_code = ":".join(
                    (diagnostic["stage"], diagnostic["error"], diagnostic["location"])
                )
                disposition = finish(
                    state, task, now=clock(), error=failure_code, limits=queue_budget
                )
                changed.update(commit_result(root, state, {}))
                outcomes.append(
                    dict(
                        entity_id=task["entity_id"],
                        status=disposition,
                        **diagnostic,
                        **operation_usage,
                    )
                )
    failed = any("error" in outcome for outcome in outcomes)
    return dict(
        status="degraded" if failed else "succeeded",
        exit_code=3 if failed else 0,
        outcomes=outcomes,
        changed=sorted(changed),
        model=limits.model,
        web_requests=total_web_requests,
    )
