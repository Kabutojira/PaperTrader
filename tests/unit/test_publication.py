from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from papertrader.publication import (
    PublicationError,
    apply_runtime_bundle,
    create_runtime_bundle,
)


def _git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _initialize(repository: Path) -> str:
    _git(repository, "init", "-b", "main")
    _git(repository, "config", "user.name", "Test")
    _git(repository, "config", "user.email", "test@example.com")
    _git(repository, "add", "--all")
    _git(repository, "commit", "-m", "initial")
    return _git(repository, "rev-parse", "HEAD")


def _runtime_changes(repository: Path, run_id: str) -> None:
    report_path = "data/wiki/daily-reports/daily-report_20260724.md"
    (repository / report_path).write_text("# Committed report\n", encoding="utf-8")
    run_directory = repository / "data" / "runs" / run_id
    run_directory.mkdir()
    (run_directory / "daily_run.json").write_text(
        json.dumps({"run_id": run_id, "report_path": report_path}),
        encoding="utf-8",
    )
    issues = repository / "data" / "issues.md"
    issues.write_text(issues.read_text(encoding="utf-8") + "Runtime change.\n", encoding="utf-8")


def test_runtime_bundle_round_trip_preserves_exact_whitelisted_patch(
    sandbox_repository: Path,
    tmp_path: Path,
) -> None:
    base_sha = _initialize(sandbox_repository)
    run_id = "bundle-test-1"
    _runtime_changes(sandbox_repository, run_id)
    bundle_directory = tmp_path / "bundle"

    created = create_runtime_bundle(
        sandbox_repository,
        bundle_directory,
        run_id=run_id,
        base_sha=base_sha,
    )
    target = tmp_path / "commit-checkout"
    subprocess.run(
        ["git", "clone", "--no-hardlinks", str(sandbox_repository), str(target)],
        check=True,
        capture_output=True,
        text=True,
    )
    applied = apply_runtime_bundle(target, bundle_directory)

    assert applied == created
    assert created.changed is True
    assert created.report_path.endswith("daily-report_20260724.md")
    assert (
        tuple(sorted(_git(target, "diff", "--cached", "--name-only").splitlines()))
        == created.changed_paths
    )
    assert (target / created.report_path).read_text(encoding="utf-8") == "# Committed report\n"


def test_runtime_bundle_rejects_tampering(
    sandbox_repository: Path,
    tmp_path: Path,
) -> None:
    base_sha = _initialize(sandbox_repository)
    run_id = "bundle-test-2"
    _runtime_changes(sandbox_repository, run_id)
    bundle_directory = tmp_path / "bundle"
    create_runtime_bundle(
        sandbox_repository,
        bundle_directory,
        run_id=run_id,
        base_sha=base_sha,
    )
    (bundle_directory / "runtime.patch").write_bytes(
        (bundle_directory / "runtime.patch").read_bytes() + b"tampered"
    )
    target = tmp_path / "commit-checkout"
    target.mkdir()

    with pytest.raises(PublicationError, match="patch hash"):
        apply_runtime_bundle(target, bundle_directory)


def test_runtime_bundle_stages_and_rejects_non_whitelisted_changes(
    sandbox_repository: Path,
    tmp_path: Path,
) -> None:
    base_sha = _initialize(sandbox_repository)
    _runtime_changes(sandbox_repository, "bundle-test-3")
    agents = sandbox_repository / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8") + "\nunsafe runtime edit\n", encoding="utf-8"
    )

    with pytest.raises(PublicationError, match=r"runtime path is not allowed: AGENTS\.md"):
        create_runtime_bundle(
            sandbox_repository,
            tmp_path / "bundle",
            run_id="bundle-test-3",
            base_sha=base_sha,
        )
