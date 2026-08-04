"""Repository-owned durable Git checkpoint boundary for daily cycles."""

from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from papertrader.advice import validate_advice
from papertrader.config import Settings
from papertrader.integrity import (
    changed_paths_from_git,
    validate_csv_files,
    validate_integrity,
    validate_json_schemas,
    validate_runtime_paths,
)
from papertrader.portfolio import reconcile_portfolio
from papertrader.wiki import lint_wiki


class CheckpointError(RuntimeError):
    """Raised before a checkpoint can mutate or advance the target branch."""


@dataclass(frozen=True, slots=True)
class CheckpointResult:
    daily_cycle_id: str
    checkpoint_index: int
    commit_sha: str
    changed_paths: tuple[str, ...]
    pushed: bool
    dry_run: bool


def _git(
    repository_root: Path,
    *arguments: str,
    environment: dict[str, str] | None = None,
    strip: bool = True,
) -> str:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=repository_root,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        detail = (completed.stderr or completed.stdout).strip()
        raise CheckpointError(f"git {' '.join(arguments[:2])} failed: {detail}")
    return completed.stdout.strip() if strip else completed.stdout


def _abort_incomplete_rebase(repository_root: Path, environment: dict[str, str]) -> None:
    """Return to the checkpoint commit before retrying a conflicted rebase."""

    for marker_name in ("rebase-merge", "rebase-apply"):
        marker = Path(_git(repository_root, "rev-parse", "--git-path", marker_name))
        if not marker.is_absolute():
            marker = repository_root / marker
        if marker.exists():
            _git(repository_root, "rebase", "--abort", environment=environment)
            return


def validate_checkpoint_state(repository_root: Path, settings: Settings) -> tuple[str, ...]:
    """Run strict runtime gates without invoking project tooling through a shell."""

    errors = [
        *validate_csv_files(repository_root),
        *validate_json_schemas(repository_root),
        *validate_integrity(
            repository_root,
            {"WIKI_PATH": str((repository_root / "data" / "wiki").resolve())},
            require_current_publication=False,
        ),
        *lint_wiki(repository_root / "data" / "wiki"),
        *reconcile_portfolio(repository_root),
    ]
    try:
        errors.extend(validate_advice(repository_root, strict=False, require_current_state=False))
    except Exception as exc:  # stable validation boundary for partially prepared cycles
        errors.append(f"advice validation failed: {exc}")
    return tuple(sorted(set(errors)))


def create_checkpoint(
    repository_root: Path,
    settings: Settings,
    *,
    daily_cycle_id: str,
    checkpoint_index: int,
    kind: str,
    operation_id: str = "",
    operation_type: str = "",
    terminal_status: str = "",
    profile: str = "",
    target_branch: str = "main",
    remote: str = "origin",
    dry_run: bool = False,
    github_token: str = "",
    push_retries: int = 3,
) -> CheckpointResult:
    """Validate, stage, commit, rebase, revalidate, and optionally push one checkpoint."""

    if not daily_cycle_id.startswith("daily-") or checkpoint_index < 0:
        raise CheckpointError("invalid checkpoint identity")
    if not dry_run and not github_token:
        raise CheckpointError("a GitHub token is required only for a real checkpoint push")
    raw_status = _git(repository_root, "status", "--porcelain=v1", "-z", strip=False)
    changed_values: set[str] = set()
    fields = raw_status.split("\0") if raw_status else []
    index = 0
    while index < len(fields):
        field = fields[index]
        if not field:
            index += 1
            continue
        if len(field) < 4:
            raise CheckpointError("cannot parse Git status for checkpoint")
        status, path = field[:2], field[3:]
        changed_values.add(path)
        if status[0] in {"R", "C"} or status[1] in {"R", "C"}:
            index += 1
            if index >= len(fields):
                raise CheckpointError("cannot parse renamed Git path")
            changed_values.add(fields[index])
        index += 1
    changed = tuple(sorted(changed_values))
    if not changed:
        head = _git(repository_root, "rev-parse", "HEAD")
        return CheckpointResult(daily_cycle_id, checkpoint_index, head, (), False, dry_run)
    path_errors = validate_runtime_paths(changed)
    if path_errors:
        raise CheckpointError("; ".join(path_errors))
    errors = validate_checkpoint_state(repository_root, settings)
    if errors:
        raise CheckpointError("; ".join(errors))
    _git(repository_root, "add", "--", *changed)
    staged = changed_paths_from_git(repository_root, staged=True)
    if tuple(changed) != tuple(staged):
        raise CheckpointError("staged checkpoint differs from the validated exact delta")
    title = f"Daily {daily_cycle_id} checkpoint {checkpoint_index:03d}: {kind}"
    trailers = [
        f"PaperTrader-Cycle: {daily_cycle_id}",
        f"PaperTrader-Checkpoint: {checkpoint_index:03d}",
    ]
    if operation_id:
        trailers.append(f"PaperTrader-Operation: {operation_id}")
    if operation_type:
        trailers.append(f"PaperTrader-Operation-Type: {operation_type}")
    if terminal_status:
        trailers.append(f"PaperTrader-Terminal-Status: {terminal_status}")
    if profile:
        trailers.append(f"PaperTrader-Profile: {profile}")
    message = title + "\n\n" + "\n".join(trailers)
    if dry_run:
        branch = f"papertrader-dry-run-{daily_cycle_id}"
        branches = _git(repository_root, "branch", "--list", branch)
        if not branches:
            _git(repository_root, "switch", "--create", branch)
        elif _git(repository_root, "branch", "--show-current") != branch:
            _git(repository_root, "switch", branch)
    _git(repository_root, "commit", "--message", message)
    commit_sha = _git(repository_root, "rev-parse", "HEAD")
    if dry_run:
        return CheckpointResult(
            daily_cycle_id, checkpoint_index, commit_sha, tuple(staged), False, True
        )
    askpass_directory = Path(tempfile.mkdtemp(prefix="papertrader-checkpoint-"))
    askpass = askpass_directory / "askpass.sh"
    try:
        askpass.write_text(
            "#!/bin/sh\n"
            'case "$1" in *Username*) echo x-access-token;; '
            '*) echo "$PAPERTRADER_PUSH_TOKEN";; esac\n',
            encoding="utf-8",
        )
        askpass.chmod(0o700)
        push_environment = {
            **os.environ,
            "GIT_ASKPASS": str(askpass),
            "GIT_TERMINAL_PROMPT": "0",
            "PAPERTRADER_PUSH_TOKEN": github_token,
        }
        last_error = ""
        for _ in range(push_retries):
            try:
                _git(repository_root, "fetch", remote, target_branch, environment=push_environment)
                _git(
                    repository_root,
                    "rebase",
                    f"{remote}/{target_branch}",
                    environment=push_environment,
                )
                rebased_paths = tuple(
                    sorted(
                        changed_paths_from_git(
                            repository_root,
                            base_ref=f"{remote}/{target_branch}",
                        )
                    )
                )
                rebased_path_errors = validate_runtime_paths(rebased_paths)
                if rebased_path_errors:
                    raise CheckpointError("; ".join(rebased_path_errors))
                if rebased_paths != tuple(staged):
                    raise CheckpointError(
                        "rebased checkpoint differs from the validated exact delta"
                    )
                rebased_errors = validate_checkpoint_state(repository_root, settings)
                if rebased_errors:
                    raise CheckpointError("; ".join(rebased_errors))
                _git(
                    repository_root,
                    "push",
                    remote,
                    f"HEAD:{target_branch}",
                    environment=push_environment,
                )
                commit_sha = _git(repository_root, "rev-parse", "HEAD")
                return CheckpointResult(
                    daily_cycle_id,
                    checkpoint_index,
                    commit_sha,
                    tuple(staged),
                    True,
                    False,
                )
            except CheckpointError as exc:
                last_error = str(exc)
                _abort_incomplete_rebase(repository_root, push_environment)
        raise CheckpointError(f"checkpoint push retries exhausted: {last_error}")
    finally:
        try:
            askpass.unlink(missing_ok=True)
            askpass_directory.rmdir()
        except OSError:
            pass
