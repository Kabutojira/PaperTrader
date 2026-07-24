from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

WORKFLOW_NAMES = {
    "ci.yml",
    "daily.yml",
    "pages.yml",
    "reusable-llm.yml",
    "reusable-non-llm.yml",
}
FULL_SHA_ACTION = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
PINNED_CONTAINER = re.compile(r"^[^@\s]+@sha256:[0-9a-f]{64}$")


def test_all_scaffold_workflows_are_manual_and_read_only(repository_root: Path) -> None:
    workflow_root = repository_root / ".github" / "workflows"
    assert {path.name for path in workflow_root.glob("*.yml")} == WORKFLOW_NAMES

    for path in workflow_root.glob("*.yml"):
        document = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        assert "workflow_dispatch" in document["on"], path.name
        assert document["permissions"] == {"contents": "read"}, path.name
        assert "matrix:" not in path.read_text(encoding="utf-8"), path.name


def test_actions_are_pinned_and_checkout_drops_credentials(repository_root: Path) -> None:
    for path in (repository_root / ".github" / "workflows").glob("*.yml"):
        document = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        for job in document["jobs"].values():
            for step in job.get("steps", []):
                action = step.get("uses")
                if action and not action.startswith("./"):
                    assert FULL_SHA_ACTION.fullmatch(action), f"{path.name}: {action}"
                if action and action.startswith("actions/checkout@"):
                    assert step["with"]["persist-credentials"] == "false"


def test_daily_manual_inputs_and_serial_concurrency(repository_root: Path) -> None:
    daily = yaml.load(
        (repository_root / ".github" / "workflows" / "daily.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    inputs = daily["on"]["workflow_dispatch"]["inputs"]

    assert set(inputs) == {
        "operation_id",
        "operation_type",
        "max_operations",
        "dry_run",
        "publish_pages",
        "send_telegram",
    }
    assert daily["concurrency"] == {
        "group": "papertrader-write",
        "cancel-in-progress": "false",
    }


def test_quartz_dependency_is_an_immutable_v4_commit(repository_root: Path) -> None:
    package = json.loads((repository_root / "site" / "package.json").read_text(encoding="utf-8"))
    dependency = package["dependencies"]["@jackyzha0/quartz"]

    assert "4923affa7722dfc751f1074348e6dad214fe0c08" in dependency
    assert dependency.startswith("https://github.com/jackyzha0/quartz/archive/")
    assert (repository_root / "site" / "package-lock.json").is_file()


def test_reusable_llm_uses_pinned_credential_scrubbed_sequential_hermes(
    repository_root: Path,
) -> None:
    path = repository_root / ".github" / "workflows" / "reusable-llm.yml"
    text = path.read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    job = workflow["jobs"]["hermes"]

    assert PINNED_CONTAINER.fullmatch(job["container"]["image"])
    assert job["env"]["PAPER_TRADING_ONLY"] == "true"
    assert job["env"]["WIKI_PATH"] == "${{ github.workspace }}/data/wiki"
    assert "--replace-unmanaged" in text
    assert "hermes skills opt-in --sync" in text
    assert "agent preflight" in text
    assert "agent run" in text
    assert "--yolo" not in text  # enforced by validated config and runner argv
    assert set(workflow["on"]["workflow_call"]["secrets"]) == {"OPENROUTER_API_KEY"}
    assert "secrets.OPENROUTER_API_KEY" in text
    assert "GITHUB_TOKEN" not in text
    assert "matrix:" not in text
