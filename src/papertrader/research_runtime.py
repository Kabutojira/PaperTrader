"""Independent phase health, bounded operating cycles and deterministic Git commits."""

from __future__ import annotations

import base64
import io
import json
import os
import re
import subprocess
import tarfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from papertrader.research_agent import run_cycle
from papertrader.research_discovery import run_discovery
from papertrader.research_market import (
    YFinanceResearchProvider,
    _read,
    market_limits,
    refresh_market,
)
from papertrader.research_publication import publish_views
from papertrader.research_queue import instant, queue_limits, schedule_attention
from papertrader.research_results import commit_result
from papertrader.research_state import read_state, validate_state
from papertrader.research_transaction import apply_files, research_lock, safe_path

PUBLICATION_FILES = {
    "data/published/research_rankings.json",
    "data/published/top_buys.csv",
    "data/published/top_sells.csv",
}
TABLES = {
    f"data/tables/{name}.csv"
    for name in ("securities", "ideas", "relationships", "security_assessments", "source_registry")
}
OAUTH = ".papertrader/credentials/openai-oauth-auth.json.age"
RUNTIME_COMMIT_CODES = {
    "runtime_commit.credential_missing",
    "runtime_commit.path_invalid",
    "runtime_commit.phase_invalid",
    "runtime_commit.recovery_path_invalid",
    "runtime_commit.state_invalid",
}


class RuntimeCommitValidationError(ValueError):
    """A controller-owned diagnostic code with no repository or source data."""

    def __init__(self, diagnostic_code: str) -> None:
        if diagnostic_code not in RUNTIME_COMMIT_CODES:
            raise ValueError("unknown runtime commit validation code")
        self.diagnostic_code = diagnostic_code
        super().__init__("invalid runtime commit state")


def update_health(
    root: Path, phase: str, outcome: dict[str, Any], *, now: datetime, changed: bool
) -> None:
    path = root / "data/status.json"
    status = json.loads(path.read_text()) if path.exists() else {}
    previous = status.get(phase, {})
    current = {**previous, "status": outcome["status"], "exit_code": outcome["exit_code"]}
    for field in (
        "provider_calls",
        "http_requests",
        "failed_tickers",
        "model_operations",
        "web_requests",
    ):
        if field in outcome:
            current[field] = outcome[field]
    if (
        changed
        or not previous
        or any(current[key] != previous.get(key) for key in ("status", "exit_code"))
    ):
        current["last_attempt_at"] = instant(now)
        if outcome["exit_code"] == 0:
            current["last_success_at"] = instant(now)
        status[phase] = current
        apply_files(
            root,
            {"data/status.json": (json.dumps(status, sort_keys=True, indent=2) + "\n").encode()},
        )


def market_cycle(
    root: Path, *, dry_run: bool = True, now: datetime | None = None, provider: Any = None
) -> dict[str, Any]:
    now = now or datetime.now(UTC)
    with research_lock(root):
        state = read_state(root)
        errors = validate_state(root, state)
        if errors:
            raise ValueError("corrupt research data before market refresh")
        limits = market_limits(root)
        if dry_run:
            return dict(status="dry_run", exit_code=0, provider_calls=0, limits=vars(limits))
        previous = _read(root / "data/market/features.csv")
        result = refresh_market(
            root,
            state["securities"],
            provider or YFinanceResearchProvider(limits),
            now=now,
            limits=limits,
        )
        current_features = _read(root / "data/market/features.csv")
        schedule_attention(state, current_features, previous, now=now, limits=queue_limits(root))
        result["changed"] = sorted(set(result["changed"]) | set(commit_result(root, state, {})))
        update_health(root, "market", result, now=now, changed=bool(result["changed"]))
        # Views fail independently; valid price/cache updates remain available.
        try:
            result["changed"] += publish_views(root, now=now)
        except (ValueError, OSError, KeyError):
            result["publication_input_error"] = "derived_views_failed"
        return result


def research_cycle(
    root: Path,
    *,
    dry_run: bool = True,
    entity_type: str = "",
    entity_id: str = "",
    discovery: bool = False,
) -> dict[str, Any]:
    if dry_run:
        return run_cycle(root, dry_run=True, entity_type=entity_type, entity_id=entity_id)
    discovery_result = run_discovery(root, dry_run=False) if discovery and not entity_id else {}
    spent = int(discovery_result.get("model_calls", 0))
    result = run_cycle(
        root, dry_run=False, entity_type=entity_type, entity_id=entity_id, reserved_operations=spent
    )
    result["model_operations"] = spent + len(result["outcomes"])
    if discovery_result:
        result["discovery"] = discovery_result
        if discovery_result["exit_code"]:
            result.update(status="degraded", exit_code=3)
    with research_lock(root):
        update_health(
            root,
            "research",
            result,
            now=datetime.now(UTC),
            changed=bool(result["outcomes"] or spent),
        )
        try:
            result["changed"] += publish_views(root, now=datetime.now(UTC))
        except (ValueError, OSError, KeyError):
            result["publication_input_error"] = "derived_views_failed"
    return result


def allowed_runtime_path(name: str, phase: str) -> bool:
    if "\\" in name or ".." in Path(name).parts or Path(name).is_absolute():
        return False
    shared = name in PUBLICATION_FILES or name in {"data/status.json", "data/research_queue.csv"}
    if phase == "market":
        return (
            shared
            or name
            in {
                f"data/wiki/{page}.md"
                for page in (
                    "index",
                    "security-catalog",
                    "idea-catalog",
                    "research-catalog",
                    "short-candidates",
                )
            }
            or name == "data/tables/securities.csv"
            or name in {"data/market/latest.csv", "data/market/features.csv"}
            or (name.startswith("data/market/prices/") and name.endswith(".csv"))
        )
    if phase == "research":
        return (
            shared
            or name in TABLES
            or name == OAUTH
            or (name.startswith("data/wiki/") and name.endswith(".md"))
        )
    return False


def _runtime_commit_path(root: Path, name: str) -> Path:
    """Validate the sole non-data runtime path without broadening data writes."""
    if name != OAUTH:
        try:
            return safe_path(root, name)
        except ValueError:
            raise RuntimeCommitValidationError("runtime_commit.path_invalid") from None
    target = root
    for part in Path(name).parts:
        target /= part
        if target.is_symlink():
            raise RuntimeCommitValidationError("runtime_commit.path_invalid")
    return target


def _git(root: Path, *args: str, environment: dict[str, str] | None = None) -> str:
    command = subprocess.run(
        ["git", *args],
        cwd=root,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if command.returncode:
        raise RuntimeError("git_operation_failed")
    return command.stdout.strip()


def finalize_commit(root: Path, *, phase: str, token: str = "") -> dict[str, Any]:
    """Post-agent only: validate allowlist, reject divergence, commit once, push once."""
    if phase not in {"market", "research"}:
        raise RuntimeCommitValidationError("runtime_commit.phase_invalid")
    try:
        errors = validate_state(root, read_state(root))
    except (KeyError, OSError, TypeError, ValueError):
        raise RuntimeCommitValidationError("runtime_commit.state_invalid") from None
    if errors:
        raise RuntimeCommitValidationError("runtime_commit.state_invalid")
    base = _git(root, "rev-parse", "HEAD")
    tracked = _git(root, "diff", "--name-only", "HEAD", "-z").split("\0")
    untracked = _git(root, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
    names = sorted({name for name in tracked + untracked if name})
    if any(not allowed_runtime_path(name, phase) for name in names):
        raise RuntimeCommitValidationError("runtime_commit.path_invalid")
    for name in names:
        _runtime_commit_path(root, name)
    if not token:
        raise RuntimeCommitValidationError("runtime_commit.credential_missing")
    environment = os.environ.copy()
    credential = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    environment.update(
        GIT_CONFIG_COUNT="1",
        GIT_CONFIG_KEY_0="http.https://github.com/.extraheader",
        GIT_CONFIG_VALUE_0=f"AUTHORIZATION: basic {credential}",
        GIT_TERMINAL_PROMPT="0",
    )
    cache = root / ".cache"
    if cache.is_symlink():
        raise RuntimeCommitValidationError("runtime_commit.recovery_path_invalid")
    cache.mkdir(exist_ok=True)
    # Short-lived failure artifact, including new files and explicit deletions.
    # Never a public artifact or growing repository history.
    if names:
        with tarfile.open(cache / "recovery.tar.gz", "w:gz") as archive:
            manifest = json.dumps(
                {
                    "base_sha": base,
                    "changed": names,
                    "deleted": [name for name in names if not (root / name).exists()],
                }
            ).encode()
            info = tarfile.TarInfo("recovery.json")
            info.size = len(manifest)
            archive.addfile(info, io.BytesIO(manifest))
            for name in names:
                if (root / name).is_file():
                    archive.add(root / name, arcname=name, recursive=False)
    _git(root, "fetch", "origin", "main", environment=environment)
    if _git(root, "rev-parse", "origin/main") != base:
        raise RuntimeError("git_conflict_requires_retry")
    if names:
        _git(root, "add", "--", *names)
        _git(
            root,
            "-c",
            "user.name=papertrader-bot",
            "-c",
            "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit",
            "-m",
            f"chore({phase}): refresh current research state",
        )
        _git(root, "push", "origin", "HEAD:main", environment=environment)
    sha = _git(root, "rev-parse", "HEAD")
    publication_changed = any(
        name.startswith("data/wiki/") or name in PUBLICATION_FILES for name in names
    )
    return dict(commit_sha=sha, changed=publication_changed, phase=phase)


def publication_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if (
        set(value) != {"commit_sha", "changed", "phase"}
        or not re.fullmatch(r"[0-9a-f]{40}", value["commit_sha"])
        or type(value["changed"]) is not bool
        or value["phase"] not in {"market", "research"}
    ):
        raise ValueError("invalid publication input manifest")
    return dict(value)
