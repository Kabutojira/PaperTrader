"""Git-safe runtime patch handoff between credential-isolated workflow jobs."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from papertrader.atomic_io import atomic_write_bytes, atomic_write_json
from papertrader.integrity import changed_paths_from_git, validate_runtime_paths
from papertrader.utils import content_hash

COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
REPORT_PATH = re.compile(r"^data/wiki/daily-reports/daily-report_[0-9]{8}\.md$")
BUNDLE_FILES = frozenset({"runtime.patch", "runtime_manifest.json"})


class PublicationError(RuntimeError):
    """Raised when a runtime diff cannot cross the commit-job boundary safely."""


@dataclass(frozen=True, slots=True)
class RuntimeBundle:
    """Validated metadata for one runtime patch artifact."""

    base_sha: str
    run_id: str
    patch_sha256: str
    changed_paths: tuple[str, ...]
    report_path: str

    @property
    def changed(self) -> bool:
        return bool(self.changed_paths)


def _git(
    repository_root: Path,
    arguments: list[str],
    *,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repository_root,
        input=input_bytes,
        check=False,
        capture_output=True,
    )
    return result


def _require_git_success(result: subprocess.CompletedProcess[bytes], label: str) -> bytes:
    if result.returncode != 0:
        error = result.stderr.decode("utf-8", errors="replace").strip()
        raise PublicationError(f"{label} failed: {error}")
    return result.stdout


def _head(repository_root: Path) -> str:
    value = _require_git_success(_git(repository_root, ["rev-parse", "HEAD"]), "git rev-parse")
    sha = value.decode("ascii", errors="strict").strip()
    if not COMMIT_SHA.fullmatch(sha):
        raise PublicationError("repository HEAD is not a full commit SHA")
    return sha


def _staged_modes(repository_root: Path) -> dict[str, str]:
    output = _require_git_success(
        _git(repository_root, ["ls-files", "--stage", "-z"]),
        "git ls-files",
    )
    modes: dict[str, str] = {}
    for raw_entry in output.split(b"\0"):
        if not raw_entry:
            continue
        try:
            metadata, raw_path = raw_entry.split(b"\t", maxsplit=1)
            mode = metadata.split(b" ", maxsplit=1)[0].decode("ascii")
            path = raw_path.decode("utf-8", errors="strict")
        except (UnicodeError, ValueError) as exc:
            raise PublicationError("git index contains an unparseable path") from exc
        modes[path] = mode
    return modes


def _validate_staged_state(repository_root: Path, paths: tuple[str, ...]) -> None:
    errors = validate_runtime_paths(paths)
    if errors:
        raise PublicationError("; ".join(errors))
    deleted = _require_git_success(
        _git(
            repository_root,
            ["diff", "--cached", "--name-only", "--diff-filter=D", "-z"],
        ),
        "git deletion scan",
    )
    if deleted:
        names = deleted.decode("utf-8", errors="replace").replace("\0", ", ").strip(", ")
        raise PublicationError(f"runtime file deletion is forbidden: {names}")
    modes = _staged_modes(repository_root)
    invalid_modes = [
        f"{path}:{modes.get(path, '<missing>')}"
        for path in paths
        if modes.get(path) not in {"100644", "100755"}
    ]
    if invalid_modes:
        raise PublicationError(
            "runtime patch contains a symlink or special file: " + ", ".join(invalid_modes)
        )
    check = _git(repository_root, ["diff", "--cached", "--check"])
    _require_git_success(check, "git diff --check")


def _report_path(repository_root: Path, run_id: str) -> str:
    path = repository_root / "data" / "runs" / run_id / "daily_run.json"
    if path.is_symlink() or not path.is_file():
        raise PublicationError("completed daily run manifest is missing")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicationError(f"cannot read completed daily run manifest: {exc}") from exc
    if not isinstance(value, dict) or value.get("run_id") != run_id:
        raise PublicationError("daily run manifest identity is invalid")
    report_path = value.get("report_path")
    if not isinstance(report_path, str) or not REPORT_PATH.fullmatch(report_path):
        raise PublicationError("daily run manifest lacks a canonical report path")
    if not (repository_root / report_path).is_file():
        raise PublicationError("daily run report does not exist")
    return report_path


def create_runtime_bundle(
    repository_root: Path,
    output_directory: Path,
    *,
    run_id: str,
    base_sha: str,
) -> RuntimeBundle:
    """Stage the complete runtime diff, validate it, and export an immutable binary patch."""

    root = repository_root.resolve(strict=True)
    output = output_directory.absolute()
    try:
        output.resolve().relative_to(root)
    except ValueError:
        pass
    else:
        raise PublicationError("runtime bundle output must be outside the repository")
    if not RUN_ID.fullmatch(run_id) or not COMMIT_SHA.fullmatch(base_sha):
        raise PublicationError("runtime bundle identity is invalid")
    if _head(root) != base_sha:
        raise PublicationError("runtime checkout no longer matches the declared base SHA")
    staged_before = _git(root, ["diff", "--cached", "--quiet"])
    if staged_before.returncode not in {0, 1}:
        _require_git_success(staged_before, "git staged-state check")
    if staged_before.returncode == 1:
        raise PublicationError("runtime checkout had pre-staged changes")
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink() or any(output.iterdir()):
        raise PublicationError("runtime bundle output must be an empty regular directory")
    _require_git_success(_git(root, ["add", "--all", "--", "."]), "git add")
    paths = tuple(sorted(changed_paths_from_git(root, staged=True)))
    _validate_staged_state(root, paths)
    patch = _require_git_success(
        _git(root, ["diff", "--cached", "--binary", "--full-index", "--no-ext-diff", "HEAD"]),
        "git runtime patch",
    )
    if bool(paths) != bool(patch):
        raise PublicationError("runtime patch content disagrees with its changed paths")
    report_path = _report_path(root, run_id)
    patch_hash = content_hash(patch)
    bundle = RuntimeBundle(base_sha, run_id, patch_hash, paths, report_path)
    atomic_write_bytes(output / "runtime.patch", patch, allowed_root=output)
    atomic_write_json(
        output / "runtime_manifest.json",
        {
            "runtime_bundle_version": 1,
            "base_sha": base_sha,
            "run_id": run_id,
            "patch_sha256": patch_hash,
            "changed": bundle.changed,
            "changed_paths": list(paths),
            "report_path": report_path,
        },
        allowed_root=output,
    )
    return bundle


def _load_bundle(bundle_directory: Path) -> tuple[RuntimeBundle, bytes]:
    directory = bundle_directory.resolve(strict=True)
    if directory.is_symlink() or not directory.is_dir():
        raise PublicationError("runtime bundle must be a regular directory")
    entries = {path.name for path in directory.iterdir()}
    if entries != BUNDLE_FILES or any(path.is_symlink() for path in directory.iterdir()):
        raise PublicationError("runtime bundle contains unexpected files or symlinks")
    manifest_path = directory / "runtime_manifest.json"
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicationError(f"cannot read runtime bundle manifest: {exc}") from exc
    expected_fields = {
        "runtime_bundle_version",
        "base_sha",
        "run_id",
        "patch_sha256",
        "changed",
        "changed_paths",
        "report_path",
    }
    if not isinstance(raw, dict) or set(raw) != expected_fields:
        raise PublicationError("runtime bundle manifest fields are invalid")
    paths = raw.get("changed_paths")
    if (
        raw.get("runtime_bundle_version") != 1
        or not isinstance(paths, list)
        or any(not isinstance(path, str) for path in paths)
        or paths != sorted(set(paths))
        or raw.get("changed") is not bool(paths)
    ):
        raise PublicationError("runtime bundle manifest values are invalid")
    base_sha = raw.get("base_sha")
    run_id = raw.get("run_id")
    patch_hash = raw.get("patch_sha256")
    report_path = raw.get("report_path")
    if (
        not isinstance(base_sha, str)
        or not COMMIT_SHA.fullmatch(base_sha)
        or not isinstance(run_id, str)
        or not RUN_ID.fullmatch(run_id)
        or not isinstance(patch_hash, str)
        or not re.fullmatch(r"[0-9a-f]{64}", patch_hash)
        or not isinstance(report_path, str)
        or not REPORT_PATH.fullmatch(report_path)
    ):
        raise PublicationError("runtime bundle identity or report path is invalid")
    patch = (directory / "runtime.patch").read_bytes()
    if content_hash(patch) != patch_hash or bool(patch) != bool(paths):
        raise PublicationError("runtime patch hash or changed flag is invalid")
    errors = validate_runtime_paths(paths)
    if errors:
        raise PublicationError("; ".join(errors))
    return RuntimeBundle(base_sha, run_id, patch_hash, tuple(paths), report_path), patch


def apply_runtime_bundle(repository_root: Path, bundle_directory: Path) -> RuntimeBundle:
    """Apply a validated runtime patch only to its exact clean base checkout."""

    root = repository_root.resolve(strict=True)
    bundle, patch = _load_bundle(bundle_directory)
    if _head(root) != bundle.base_sha:
        raise PublicationError("commit checkout does not match the runtime bundle base SHA")
    status = _require_git_success(
        _git(root, ["status", "--porcelain=v1", "-z"]),
        "git status",
    )
    if status:
        raise PublicationError("commit checkout must be clean before applying a runtime bundle")
    if patch:
        patch_path = bundle_directory.resolve(strict=True) / "runtime.patch"
        _require_git_success(
            _git(root, ["apply", "--check", "--index", "--binary", str(patch_path)]),
            "git apply check",
        )
        _require_git_success(
            _git(root, ["apply", "--index", "--binary", str(patch_path)]),
            "git apply",
        )
    actual_paths = tuple(sorted(changed_paths_from_git(root, staged=True)))
    if actual_paths != bundle.changed_paths:
        raise PublicationError("applied runtime paths differ from the bundle manifest")
    _validate_staged_state(root, actual_paths)
    return bundle
