from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

WORKFLOW_NAMES = {
    "ci.yml",
    "daily.yml",
    "pages.yml",
    "reporting.yml",
    "reusable-llm.yml",
    "reusable-non-llm.yml",
}
FULL_SHA_ACTION = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
PINNED_CONTAINER = re.compile(r"^[^@\s]+@sha256:[0-9a-f]{64}$")


def _workflow(path: Path) -> dict[str, object]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert isinstance(value, dict)
    return value


def test_all_workflows_are_manual_default_read_only_and_never_use_matrices(
    repository_root: Path,
) -> None:
    workflow_root = repository_root / ".github" / "workflows"
    assert {path.name for path in workflow_root.glob("*.yml")} == WORKFLOW_NAMES

    for path in workflow_root.glob("*.yml"):
        document = _workflow(path)
        triggers = document["on"]
        assert isinstance(triggers, dict)
        assert "workflow_dispatch" in triggers, path.name
        assert document["permissions"] == {"contents": "read"}, path.name
        assert "matrix:" not in path.read_text(encoding="utf-8"), path.name


def test_actions_are_pinned_and_every_checkout_drops_credentials(
    repository_root: Path,
) -> None:
    for path in (repository_root / ".github" / "workflows").glob("*.yml"):
        document = _workflow(path)
        jobs = document["jobs"]
        assert isinstance(jobs, dict)
        for job in jobs.values():
            assert isinstance(job, dict)
            for step in job.get("steps", []):
                action = step.get("uses")
                if action and not action.startswith("./"):
                    assert FULL_SHA_ACTION.fullmatch(action), f"{path.name}: {action}"
                if action and action.startswith("actions/checkout@"):
                    assert step["with"]["persist-credentials"] == "false"


def test_daily_manual_inputs_schedule_and_serialized_reusable_graph(
    repository_root: Path,
) -> None:
    daily = _workflow(repository_root / ".github" / "workflows" / "daily.yml")
    triggers = daily["on"]
    assert isinstance(triggers, dict)
    inputs = triggers["workflow_dispatch"]["inputs"]

    assert set(inputs) == {
        "operation_id",
        "operation_type",
        "max_operations",
        "dry_run",
        "publish_pages",
        "send_telegram",
    }
    assert "schedule" in triggers
    assert daily["concurrency"] == {
        "group": "papertrader-write",
        "cancel-in-progress": "false",
    }
    jobs = daily["jobs"]
    assert list(jobs) == ["runtime", "delivery", "pages"]
    assert jobs["runtime"]["uses"] == "./.github/workflows/reusable-llm.yml"
    assert jobs["delivery"]["uses"] == "./.github/workflows/reporting.yml"
    assert jobs["pages"]["uses"] == "./.github/workflows/pages.yml"
    assert jobs["delivery"]["needs"] == "runtime"
    assert jobs["pages"]["needs"] == ["runtime", "delivery"]


def test_runtime_workflow_is_sequential_whitelisted_and_secret_partitioned(
    repository_root: Path,
) -> None:
    path = repository_root / ".github" / "workflows" / "reusable-llm.yml"
    text = path.read_text(encoding="utf-8")
    workflow = _workflow(path)
    jobs = workflow["jobs"]
    runtime = jobs["runtime"]
    commit = jobs["commit"]
    runtime_text = yaml.safe_dump(runtime)
    commit_text = yaml.safe_dump(commit)

    assert PINNED_CONTAINER.fullmatch(runtime["container"]["image"])
    assert runtime["permissions"] == {"contents": "read"}
    assert commit["permissions"] == {"contents": "write"}
    assert runtime["env"]["PAPER_TRADING_ONLY"] == "true"
    assert runtime["env"]["WIKI_PATH"] == "${{ github.workspace }}/data/wiki"
    assert "hermes skills opt-in --sync" in text
    assert "agent preflight" in text
    assert "agent run-batch" in text
    assert "daily prepare" in text
    assert "daily finalize" in text
    assert "workflow bundle create" in text
    assert "workflow bundle apply" in text
    assert "runtime-whitelist validate --staged" in text
    assert "git rebase" in text
    assert "git diff --cached --quiet" in text
    assert "--yolo" not in text  # validated config and runner argv own this flag
    assert set(workflow["on"]["workflow_call"]["secrets"]) == {"OPENROUTER_API_KEY"}
    assert "secrets.OPENROUTER_API_KEY" in runtime_text
    assert "github.token" not in runtime_text
    assert "TELEGRAM" not in runtime_text
    assert "github.token" in commit_text
    assert "OPENROUTER_API_KEY" not in commit_text


def test_reporting_failure_state_and_pages_deployment_use_post_commit_boundaries(
    repository_root: Path,
) -> None:
    reporting_path = repository_root / ".github" / "workflows" / "reporting.yml"
    reporting_text = reporting_path.read_text(encoding="utf-8")
    reporting = _workflow(reporting_path)
    delivery = reporting["jobs"]["delivery"]
    delivery_text = yaml.safe_dump(delivery)
    assert delivery["permissions"] == {"contents": "write"}
    assert set(reporting["on"]["workflow_call"]["secrets"]) == {
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
    }
    assert "telegram deliver" in reporting_text
    assert "runtime-whitelist validate --staged" in reporting_text
    assert "git rebase" in reporting_text
    assert "TELEGRAM_BOT_TOKEN" in delivery_text
    assert "OPENROUTER_API_KEY" not in delivery_text

    pages_path = repository_root / ".github" / "workflows" / "pages.yml"
    pages = _workflow(pages_path)
    pages_text = pages_path.read_text(encoding="utf-8")
    assert pages["jobs"]["build"]["permissions"] == {"contents": "read"}
    assert pages["jobs"]["deploy"]["permissions"] == {
        "pages": "write",
        "id-token": "write",
    }
    assert "npm run build --prefix site" in pages_text
    assert "actions/upload-pages-artifact@" in pages_text
    assert "actions/deploy-pages@" in pages_text
    assert "site/public" in pages_text


def test_quartz_and_dependency_update_sources_are_immutable(repository_root: Path) -> None:
    package = json.loads((repository_root / "site" / "package.json").read_text(encoding="utf-8"))
    dependency = package["dependencies"]["@jackyzha0/quartz"]

    assert "4923affa7722dfc751f1074348e6dad214fe0c08" in dependency
    assert dependency.startswith("https://github.com/jackyzha0/quartz/archive/")
    assert (repository_root / "site" / "package-lock.json").is_file()
    dependabot = yaml.safe_load(
        (repository_root / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    )
    ecosystems = {entry["package-ecosystem"] for entry in dependabot["updates"]}
    assert ecosystems == {"pip", "npm", "github-actions"}


def test_ci_gates_execute_the_seeded_publication_cycle(repository_root: Path) -> None:
    for name in ("ci.yml", "reusable-non-llm.yml"):
        text = (repository_root / ".github" / "workflows" / name).read_text(encoding="utf-8")
        assert 'PAPERTRADER_VALIDATE_QUARTZ: "true"' in text
        assert "pytest tests/integration/test_complete_operating_cycle.py" in text
