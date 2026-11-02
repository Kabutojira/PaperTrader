"""Only the supported research-only workflow surfaces are production contracts."""

from __future__ import annotations

import configparser
import json
import re
from pathlib import Path
from typing import Any

import yaml


def workflow(root: Path, name: str) -> dict[str, Any]:
    return dict(yaml.load((root / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader))


def test_scheduled_daily_time_is_1300_eastern_and_research_follows_market(
    repository_root: Path,
) -> None:
    root = repository_root
    assert {p.name for p in (root / ".github/workflows").glob("*.yml")} == {
        "ci.yml",
        "market.yml",
        "research.yml",
        "pages.yml",
    }
    config = configparser.ConfigParser()
    config.read(root / "research.ini")
    schedule = workflow(root, "market.yml")["on"]["schedule"]
    assert schedule == [
        {"cron": config["schedule"]["cron"], "timezone": config["schedule"]["timezone"]}
    ]
    assert schedule == [{"cron": "0 13 * * *", "timezone": "America/New_York"}]
    research = workflow(root, "research.yml")
    assert research["on"]["workflow_run"]["workflows"] == ["Research market refresh"]
    assert "conclusion == 'success'" not in research["jobs"]["research"]["if"]
    assert "workflow_run.event == 'schedule'" in research["jobs"]["research"]["if"]


def test_actions_pinned_checkout_credentials_absent_and_no_parallel_agent_matrix(
    repository_root: Path,
) -> None:
    for name in ("ci.yml", "market.yml", "research.yml", "pages.yml"):
        document = workflow(repository_root, name)
        assert document["permissions"] == {"contents": "read"}
        for job in document["jobs"].values():
            assert "strategy" not in job
            if "container" in job:
                assert re.fullmatch(r".+@sha256:[0-9a-f]{64}", job["container"]["image"])
            for step in job.get("steps", []):
                if "uses" in step:
                    assert re.fullmatch(r"[^@]+@[0-9a-f]{40}", step["uses"])
                if str(step.get("uses", "")).startswith("actions/checkout@"):
                    assert step["with"]["persist-credentials"] == "false"


def test_runtime_scopes_inference_secret_and_git_token_to_separate_steps(
    repository_root: Path,
) -> None:
    for name, phase in (("market.yml", "market"), ("research.yml", "research")):
        document = workflow(repository_root, name)
        assert document["concurrency"] == {
            "group": "papertrader-research-state",
            "cancel-in-progress": "false",
        }
        assert document["on"]["workflow_dispatch"]["inputs"]["dry_run"]["default"] == "true"
        job = document["jobs"][phase]
        assert "GH_TOKEN" not in job.get("env", {}) and "OPENAI_OAUTH_SECRET" not in job.get(
            "env", {}
        )
        phase_step = next(step for step in job["steps"] if step.get("id") == "phase")
        assert not {"GH_TOKEN", "GITHUB_TOKEN", "OPENAI_OAUTH_SECRET"} & set(
            phase_step.get("env", {})
        )
        token_steps = [step for step in job["steps"] if "GH_TOKEN" in step.get("env", {})]
        assert len(token_steps) == 1 and f"commit-runtime {phase}" in token_steps[0]["run"]
        assert "papertrader validate" in str(job)
        assert "pytest" not in str(job) and "ruff" not in str(job)
        assert not any(
            word in str(job).lower() for word in ("telegram", "podcast", "final_buy", "allocation")
        )
    text = (repository_root / ".github/workflows/research.yml").read_text()
    research_inputs = workflow(repository_root, "research.yml")["on"]["workflow_dispatch"]["inputs"]
    assert research_inputs["diagnostic"]["default"] == "false"
    assert "arguments=(research-diagnostic)" in text
    assert "diagnostic_inputs_conflict" in text
    assert "bdc69c09cbdd6cf8b1f333d372a1f58247b3a33146406333e30c0f26e8f51377" in text
    assert "--connect-timeout 15 --max-time 90 --retry 2" in text
    assert "Remove plaintext inference state" in text
    assert "cmp -s" in text and "age --encrypt" in text


def test_pages_uses_committed_manifest_and_independent_deployment_permissions(
    repository_root: Path,
) -> None:
    document = workflow(repository_root, "pages.yml")
    assert set(document["on"]["workflow_run"]["workflows"]) == {
        "Research market refresh",
        "Bounded company and idea research",
    }
    jobs = document["jobs"]
    assert jobs["resolve"]["permissions"] == {"contents": "read", "actions": "read"}
    assert jobs["build"]["permissions"] == {"contents": "read"}
    assert jobs["deploy"]["permissions"] == {"pages": "write", "id-token": "write"}
    build = str(jobs["build"])
    assert (
        "needs.resolve.outputs.sha" in build
        and "merge-base --is-ancestor HEAD origin/main" in build
    )
    assert "workflow_run.head_sha" not in build
    assert "publication-input" in str(jobs["resolve"])
    assert "OPENAI_OAUTH_SECRET" not in str(document) and "papertrader research" not in str(
        document
    )
    assert "npm run build" in build


def test_ci_keeps_full_development_gate_separate_from_runtime(repository_root: Path) -> None:
    text = (repository_root / ".github/workflows/ci.yml").read_text()
    for command in (
        "ruff check",
        "ruff format --check",
        "mypy src",
        "papertrader validate",
        "uv run pytest",
        "npm run check",
        "npm run build",
    ):
        assert command in text
    assert "fetch-depth: 0" in text
    assert "papertrader daily" not in text and "papertrader advice" not in text


def test_quartz_and_local_echarts_sources_are_immutable(repository_root: Path) -> None:
    site = repository_root / "site"
    package = json.loads((site / "package.json").read_text())
    lock = json.loads((site / "package-lock.json").read_text())
    charts = (site / "papertrader/scripts/research-charts.inline.ts").read_text()

    assert package["dependencies"]["@jackyzha0/quartz"] == (
        "https://github.com/jackyzha0/quartz/archive/"
        "3dff48b5df6d84c9544a5ae19c8f2cbb01dc44e5.tar.gz"
    )
    assert package["dependencies"]["echarts"] == "6.1.0"
    assert lock["packages"]["node_modules/echarts"]["version"] == "6.1.0"
    assert 'script.dataset.papertraderEcharts = "6.1.0"' in charts
    assert '"static/vendor/echarts/echarts.min.js"' in charts
    assert "cdn." not in charts and "fetch(" not in charts
