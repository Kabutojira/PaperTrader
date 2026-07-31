from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
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
SETUP_UV_ACTION = "astral-sh/setup-uv@c771a70e6277c0a99b617c7a806ffedaca235ff9"


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
        "generate_podcast",
        "wiki_maintenance",
        "publish_pages",
        "send_telegram",
    }
    assert inputs["generate_podcast"] == {
        "description": "Generate the final sequential daily podcast",
        "required": "false",
        "default": "false",
        "type": "boolean",
    }
    assert inputs["wiki_maintenance"] == {
        "description": "Run the native llm-wiki weekly maintenance pass",
        "required": "false",
        "default": "false",
        "type": "boolean",
    }
    assert "schedule" in triggers
    assert triggers["schedule"] == [{"cron": "0 17 * * *", "timezone": "Europe/Rome"}]
    assert daily["concurrency"] == {
        "group": "papertrader-write",
        "cancel-in-progress": "false",
    }
    jobs = daily["jobs"]
    assert list(jobs) == ["runtime", "delivery", "pages", "daily_outcome"]
    assert jobs["runtime"]["uses"] == "./.github/workflows/reusable-llm.yml"
    assert jobs["runtime"]["secrets"] == {
        "OPENAI_OAUTH_SECRET": "${{ secrets.OPENAI_OAUTH_SECRET }}",
        "OPENROUTER_API_KEY": "${{ secrets.OPENROUTER_API_KEY }}",
        "YOUTUBE_DATA_API": "${{ secrets.YOUTUBE_DATA_API }}",
    }
    assert jobs["runtime"]["with"]["generate_podcast"] == (
        "${{ inputs.generate_podcast || vars.GENERATE_PODCAST == 'true' }}"
    )
    assert jobs["runtime"]["with"]["wiki_maintenance"] == (
        "${{ (github.event_name == 'workflow_dispatch' && inputs.wiki_maintenance) || "
        "(github.event_name == 'schedule' && vars.WIKI_MAINTENANCE_ENABLED == 'true') }}"
    )
    assert jobs["delivery"]["uses"] == "./.github/workflows/reporting.yml"
    assert jobs["pages"]["uses"] == "./.github/workflows/pages.yml"
    assert jobs["delivery"]["needs"] == "runtime"
    assert jobs["pages"]["needs"] == ["runtime", "delivery"]
    outcome = jobs["daily_outcome"]
    assert outcome["needs"] == ["runtime", "delivery", "pages"]
    assert outcome["if"] == "${{ always() }}"
    outcome_step = outcome["steps"][0]
    assert outcome_step["env"]["GENERATE_PODCAST"] == (
        "${{ inputs.generate_podcast || vars.GENERATE_PODCAST == 'true' }}"
    )
    assert outcome_step["env"]["PODCAST_STATUS"] == "${{ needs.runtime.outputs.podcast_status }}"
    assert "validated research and report state was published" in outcome_step["run"]


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
    assert runtime["defaults"]["run"]["shell"] == "bash"
    assert commit["permissions"] == {"contents": "write"}
    assert runtime["env"] == {
        "AUXILIARY_MODEL": "${{ vars.AUXILIARY_MODEL || 'openai-codex:gpt-5.6-terra' }}",
        "GENERATE_PODCAST": ("${{ inputs.generate_podcast || vars.GENERATE_PODCAST == 'true' }}"),
        "HERMES_HOME": "/tmp/papertrader-hermes",
        "MAX_OPERATIONS": "${{ vars.MAX_OPERATIONS || '180' }}",
    }
    assert "WIKI_PATH" not in runtime["env"]
    assert "hermes skills opt-in --sync" in text
    assert "agent preflight" in text
    assert "agent run-batch" in text
    assert "wiki maintain" in text
    assert "daily prepare" in text
    assert "daily finalize" in text
    assert "podcast enqueue" in text
    assert "--operation-type daily_podcast" in text
    assert "command -v ffmpeg" in text
    assert "workflow bundle create" in text
    assert "workflow bundle apply" in text
    assert "runtime-whitelist validate --staged" in text
    assert "git rebase" in text
    assert "git diff --cached --quiet" in text
    assert "--yolo" not in text  # validated config and runner argv own this flag
    for trigger_name in ("workflow_call", "workflow_dispatch"):
        podcast_input = workflow["on"][trigger_name]["inputs"]["generate_podcast"]
        assert podcast_input["default"] == "false"
        assert podcast_input["type"] == "boolean"
        maintenance_input = workflow["on"][trigger_name]["inputs"]["wiki_maintenance"]
        assert maintenance_input["default"] == "false"
        assert maintenance_input["type"] == "boolean"
    assert set(workflow["on"]["workflow_call"]["secrets"]) == {
        "OPENAI_OAUTH_SECRET",
        "OPENROUTER_API_KEY",
        "YOUTUBE_DATA_API",
    }
    assert "secrets.OPENAI_OAUTH_SECRET" in runtime_text
    assert "github.token" not in runtime_text
    assert "TELEGRAM" not in runtime_text
    assert "github.token" in commit_text
    assert "OPENAI_OAUTH_SECRET" not in commit_text
    run_batch = next(
        step
        for step in runtime["steps"]
        if step["name"] == "Execute due Hermes operations strictly one at a time"
    )
    assert run_batch["env"]["OPENROUTER_API_KEY"] == "${{ secrets.OPENROUTER_API_KEY }}"
    assert run_batch["env"]["BATCH_MAX_OPERATIONS"] == "${{ inputs.max_operations }}"
    assert 'selected_max="$BATCH_MAX_OPERATIONS"' in run_batch["run"]
    assert 'test -n "${OPENROUTER_API_KEY:-}"' not in run_batch["run"]
    hermes_logs = next(
        step
        for step in runtime["steps"]
        if step["name"] == "Print recent redacted Hermes logs after a runtime or podcast failure"
    )
    assert hermes_logs["if"] == (
        "${{ failure() || (!inputs.dry_run && env.GENERATE_PODCAST == 'true' && "
        "steps.podcast.outputs.status != 'succeeded') }}"
    )
    assert "hermes logs errors --since 35m -n 200" in hermes_logs["run"]
    assert "hermes logs agent --since 35m -n 500" in hermes_logs["run"]
    assert workflow["on"]["workflow_call"]["outputs"]["podcast_status"]["value"] == (
        "${{ jobs.runtime.outputs.podcast_status }}"
    )
    podcast_finalize = next(
        step
        for step in runtime["steps"]
        if step["name"] == "Record the terminal daily podcast disposition"
    )
    assert podcast_finalize["id"] == "podcast"
    assert podcast_finalize["if"] == ("${{ !inputs.dry_run && env.GENERATE_PODCAST == 'true' }}")
    assert 'echo "status=$status" >> "$GITHUB_OUTPUT"' in podcast_finalize["run"]
    for step_name in (
        "Collect completed-run changes and enqueue the daily podcast",
        "Generate the daily podcast as the final sequential Hermes operation",
        "Record the terminal daily podcast disposition",
    ):
        step = next(step for step in runtime["steps"] if step["name"] == step_name)
        assert step["if"] == "${{ !inputs.dry_run && env.GENERATE_PODCAST == 'true' }}"
    assert runtime["outputs"]["podcast_status"] == (
        "${{ steps.podcast.outputs.status || 'skipped' }}"
    )
    for step in runtime["steps"]:
        if step is not run_batch:
            assert "OPENROUTER_API_KEY" not in step.get("env", {})
    runtime_steps = [step["name"] for step in runtime["steps"]]
    maintenance_step = next(
        step
        for step in runtime["steps"]
        if step["name"] == "Run weekly native llm-wiki maintenance before queued operations"
    )
    assert maintenance_step["if"] == "${{ inputs.wiki_maintenance }}"
    assert "--dry-run" in maintenance_step["run"]
    assert "--provider" not in maintenance_step["run"]
    assert "--model" not in maintenance_step["run"]
    assert "--skills" not in maintenance_step["run"]
    assert runtime_steps.index(
        "Run weekly native llm-wiki maintenance before queued operations"
    ) < runtime_steps.index("Execute due Hermes operations strictly one at a time")
    assert runtime_steps.index("Discover curated YouTube sources") < (
        runtime_steps.index("Restore encrypted OpenAI OAuth state")
    )
    discovery = next(
        step for step in runtime["steps"] if step["name"] == "Discover curated YouTube sources"
    )
    assert discovery["uses"] == "./.github/actions/scan-youtube"
    assert discovery["with"]["dry_run"] == "${{ inputs.dry_run }}"
    assert discovery["env"] == {"YOUTUBE_DATA_API": "${{ secrets.YOUTUBE_DATA_API }}"}
    for step in runtime["steps"]:
        if step is not discovery:
            assert "YOUTUBE_DATA_API" not in step.get("env", {})
    seekingalpha = next(
        step
        for step in runtime["steps"]
        if step["name"] == "Schedule Seeking Alpha search-index discovery without credentials"
    )
    assert seekingalpha["uses"] == "./.github/actions/schedule-seekingalpha"
    assert seekingalpha["with"]["dry_run"] == "${{ inputs.dry_run }}"
    assert runtime_steps.index(
        "Schedule Seeking Alpha search-index discovery without credentials"
    ) < runtime_steps.index("Restore encrypted OpenAI OAuth state")
    daily = _workflow(repository_root / ".github" / "workflows" / "daily.yml")
    assert daily["jobs"]["runtime"]["with"]["scan_seekingalpha"] == "true"


@pytest.mark.parametrize(
    ("dry_run", "generate_podcast", "runtime_result", "podcast_status", "expected_exit"),
    [
        ("false", "true", "success", "succeeded", 0),
        ("false", "true", "success", "failed", 1),
        ("false", "true", "success", "blocked", 1),
        ("true", "true", "success", "skipped", 0),
        ("false", "true", "failure", "", 0),
        ("false", "false", "success", "skipped", 0),
        ("false", "false", "success", "failed", 0),
    ],
)
def test_daily_outcome_defers_podcast_failure_until_after_publication(
    repository_root: Path,
    dry_run: str,
    generate_podcast: str,
    runtime_result: str,
    podcast_status: str,
    expected_exit: int,
) -> None:
    daily = _workflow(repository_root / ".github" / "workflows" / "daily.yml")
    step = daily["jobs"]["daily_outcome"]["steps"][0]
    environment = os.environ.copy()
    environment.update(
        {
            "DRY_RUN": dry_run,
            "GENERATE_PODCAST": generate_podcast,
            "RUNTIME_RESULT": runtime_result,
            "PODCAST_STATUS": podcast_status,
        }
    )

    completed = subprocess.run(
        ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c", step["run"]],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == expected_exit
    if expected_exit:
        assert "validated research and report state was published" in completed.stdout


def test_openai_oauth_restore_refresh_failure_and_cleanup_contract(
    repository_root: Path,
) -> None:
    path = repository_root / ".github" / "workflows" / "reusable-llm.yml"
    workflow = _workflow(path)
    runtime = workflow["jobs"]["runtime"]
    commit = workflow["jobs"]["commit"]
    steps = {step["name"]: step for step in runtime["steps"]}
    restore = steps["Restore encrypted OpenAI OAuth state"]
    persist = steps["Encrypt refreshed OpenAI OAuth state when changed"]
    upload = steps["Upload only the refreshed OAuth ciphertext"]
    cleanup = steps["Remove all plaintext OAuth credential material"]

    assert "OPENAI_OAUTH_SECRET" not in workflow.get("env", {})
    assert "OPENAI_OAUTH_SECRET" not in runtime["env"]
    assert "OPENAI_OAUTH_SECRET" not in commit["env"]
    assert restore["env"] == {"OPENAI_OAUTH_SECRET": "${{ secrets.OPENAI_OAUTH_SECRET }}"}
    assert "steps.oauth_contract.outputs.oauth_required == 'true'" in restore["if"]
    assert "inputs.dry_run" not in restore["env"]
    assert 'test -s "$CIPHERTEXT"' in restore["run"]
    assert 'test -n "${OPENAI_OAUTH_SECRET:-}"' in restore["run"]
    assert "age --decrypt" in restore["run"]
    assert 'AUTH_FILE="$HERMES_HOME/auth.json"' in restore["run"]
    assert 'AUTH_BEFORE="$RUNNER_TEMP/openai-oauth-auth.before.json"' in restore["run"]
    preflight = steps["Preflight OpenAI Codex OAuth without exposing credential state"]
    assert "hermes auth status openai-codex 2>/dev/null" in preflight["run"]
    assert '"openai-codex: logged in"' in preflight["run"]
    assert "unset oauth_status" in preflight["run"]

    assert "always()" in persist["if"]
    assert 'cmp -s "$AUTH_BEFORE" "$AUTH_FILE"' in persist["run"]
    assert 'age-keygen -y "$IDENTITY_FILE"' in persist["run"]
    assert "age --encrypt" in persist["run"]
    assert 'cmp -s "$AUTH_FILE" "$AUTH_VERIFY"' in persist["run"]
    assert upload["with"]["retention-days"] == "1"
    assert upload["with"]["include-hidden-files"] == "true"
    assert upload["with"]["path"] == "${{ runner.temp }}/papertrader-oauth-artifact"
    assert "always()" in cleanup["if"]
    for required_path in (
        "$HERMES_HOME/auth.json",
        "$RUNNER_TEMP/openai-oauth.agekey",
        "$RUNNER_TEMP/openai-oauth-auth.before.json",
        "$RUNNER_TEMP/openai-oauth-auth.verify.json",
        "$RUNNER_TEMP/openai-oauth-auth.json.age",
    ):
        assert required_path in cleanup["run"]

    assert commit["if"] == "${{ always() }}"
    assert "needs.runtime.result != 'success'" in yaml.safe_dump(commit)
    assert "chore(auth): persist refreshed OpenAI OAuth state" in path.read_text(encoding="utf-8")
    assert ".papertrader/credentials/openai-oauth-auth.json.age" in yaml.safe_dump(commit)
    assert "$HERMES_HOME/auth.json" not in yaml.safe_dump(commit)
    assert "openai-oauth.agekey" not in yaml.safe_dump(commit)


@pytest.mark.parametrize(
    ("status_output", "hermes_exit", "expected_exit"),
    [
        ("openai-codex: logged in\n  client_id: private-test-account\n", 0, 0),
        (
            "openai-codex: logged out (No Codex credentials stored.)\n"
            "  client_id: private-test-account\n",
            0,
            1,
        ),
        ("", 1, 1),
    ],
)
def test_openai_oauth_preflight_requires_logged_in_status_without_leaking_details(
    repository_root: Path,
    tmp_path: Path,
    status_output: str,
    hermes_exit: int,
    expected_exit: int,
) -> None:
    workflow = _workflow(repository_root / ".github" / "workflows" / "reusable-llm.yml")
    runtime = workflow["jobs"]["runtime"]
    preflight = next(
        step
        for step in runtime["steps"]
        if step["name"] == "Preflight OpenAI Codex OAuth without exposing credential state"
    )
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_hermes = fake_bin / "hermes"
    fake_hermes.write_text(
        "#!/usr/bin/env bash\n"
        'test "$*" = "auth status openai-codex" || exit 99\n'
        "printf '%s' \"$FAKE_HERMES_STATUS\"\n"
        'exit "$FAKE_HERMES_EXIT"\n',
        encoding="utf-8",
    )
    fake_hermes.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "FAKE_HERMES_EXIT": str(hermes_exit),
            "FAKE_HERMES_STATUS": status_output,
            "PATH": f"{fake_bin}:{environment['PATH']}",
        }
    )

    completed = subprocess.run(
        ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c", preflight["run"]],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == expected_exit
    assert "private-test-account" not in completed.stdout
    assert "private-test-account" not in completed.stderr


def test_age_install_is_version_and_checksum_pinned(repository_root: Path) -> None:
    workflow = _workflow(repository_root / ".github" / "workflows" / "reusable-llm.yml")
    runtime = workflow["jobs"]["runtime"]
    install = next(
        step for step in runtime["steps"] if step["name"] == "Install checksum-verified age 1.3.1"
    )
    script = install["run"]

    assert "/releases/download/v1.3.1/age-v1.3.1-linux-amd64.tar.gz" in script
    assert "bdc69c09cbdd6cf8b1f333d372a1f58247b3a33146406333e30c0f26e8f51377" in script
    assert "sha256sum --check --status" in script
    assert 'test "$(age --version)" = "v1.3.1"' in script
    assert 'test "$(age-keygen --version)" = "v1.3.1"' in script


def test_hermes_runtime_establishes_container_paths_and_profile_ownership(
    repository_root: Path,
) -> None:
    workflow = _workflow(repository_root / ".github" / "workflows" / "reusable-llm.yml")
    runtime = workflow["jobs"]["runtime"]
    steps = {step["name"]: step for step in runtime["steps"]}
    boundary = steps["Establish the container workspace boundary"]["run"]
    identities = steps["Establish immutable runtime identities"]["run"]
    handoff = steps["Hand the isolated profile to the Hermes user"]["run"]
    oauth_contract = steps["Determine whether OAuth restoration is required"]["run"]

    assert 'workspace="$(pwd -P)"' in boundary
    assert 'git config --system --add safe.directory "$workspace"' in boundary
    assert 'echo "WIKI_PATH=${workspace}/data/wiki" >> "$GITHUB_ENV"' in boundary
    assert "git rev-parse --verify 'HEAD^{commit}'" in identities
    assert handoff == 'chown -R hermes:hermes "$HERMES_HOME"'
    assert 'if [ "$DRY_RUN" != "true" ]; then' in oauth_contract
    assert 'case "$BATCH_MAX_OPERATIONS" in' in oauth_contract
    assert 'case "$MAX_OPERATIONS" in' not in oauth_contract


def test_daily_forwards_scoped_runtime_secrets_and_auth_only_pushes_do_not_retrigger_ci(
    repository_root: Path,
) -> None:
    daily = _workflow(repository_root / ".github" / "workflows" / "daily.yml")
    runtime = daily["jobs"]["runtime"]
    assert runtime["secrets"] == {
        "OPENAI_OAUTH_SECRET": "${{ secrets.OPENAI_OAUTH_SECRET }}",
        "OPENROUTER_API_KEY": "${{ secrets.OPENROUTER_API_KEY }}",
        "YOUTUBE_DATA_API": "${{ secrets.YOUTUBE_DATA_API }}",
    }
    assert runtime["with"]["scan_youtube"] == "true"
    assert daily["concurrency"] == {
        "group": "papertrader-write",
        "cancel-in-progress": "false",
    }

    ci = _workflow(repository_root / ".github" / "workflows" / "ci.yml")
    assert ci["on"]["push"]["paths-ignore"] == [
        ".papertrader/credentials/openai-oauth-auth.json.age"
    ]


def test_hermes_runtime_bootstraps_uv_without_container_pip(repository_root: Path) -> None:
    workflow = _workflow(repository_root / ".github" / "workflows" / "reusable-llm.yml")
    runtime = workflow["jobs"]["runtime"]
    install = next(
        step for step in runtime["steps"] if step["name"] == "Install pinned project runner"
    )

    assert install["uses"] == SETUP_UV_ACTION
    assert install["with"] == {
        "version": "0.8.17",
        "enable-cache": "false",
        "github-token": "",
    }
    assert "python3 -m pip" not in yaml.safe_dump(runtime)


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

    assert package["scripts"]["postbuild"] == "python3 ../scripts/check_site_links.py"
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
