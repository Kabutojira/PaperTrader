# PaperTrader operating runbook

This runbook covers version-1 operation from a clean checkout. `AGENTS.md`, the JSON/CSV schemas,
and the repository-local skills remain authoritative if an example here ever conflicts with a
contract.

## Safety and local setup

PaperTrader has no real-execution adapter. Do not add brokerage credentials to the checkout,
GitHub secrets, Hermes profile, or request files. Every project command requires:

```bash
export PAPER_TRADING_ONLY=true
export WIKI_PATH="$PWD/data/wiki"
uv sync --locked --all-groups
```

Keep provider credentials in the parent process or the GitHub secret store. Only inference
credentials may cross into Hermes. GitHub write, Telegram, deployment, and brokerage credentials
must not.

## Run a project skill locally

Use a dedicated Hermes profile and process one operation at a time:

```bash
export HERMES_HOME=/tmp/papertrader-hermes
uv run papertrader agent configure --hermes-home "$HERMES_HOME" --replace-unmanaged
hermes skills opt-in --sync
uv run papertrader agent preflight \
  --hermes-home "$HERMES_HOME" \
  --operation-type opportunity_research
uv run papertrader agent run \
  --hermes-home "$HERMES_HOME" \
  --run-id local-20260724-01 \
  --operation-type opportunity_research
```

The native `llm-wiki` skill, `papertrader-controller`, and exactly one operation skill are loaded.
Hermes is always invoked with `--yolo`; the path allowlist, command receipts, result schema, and
post-run validation replace interactive approval. A local harness such as Codex must read those
same skill files, must not delegate to a sub-agent, and must use the project CLI for structured
state.

## Enqueue bounded work

Put the request under `data/operations/` or the current operation artifact directory. Example:

```json
{
  "operation_type": "idea_research",
  "entity_type": "idea",
  "entity_id": "idea_example",
  "dedupe_key": "idea_research:idea_example:manual-seed:2026-07",
  "prompt": "Research one evidence-linked investment idea.",
  "inputs": {
    "idea_id": "idea_example",
    "seed_claim": "Demand may exceed the maintained base case."
  },
  "source": "manual",
  "priority": 50,
  "freshness_days": 30,
  "depends_on": [],
  "not_before": "now",
  "deadline": "",
  "source_refs": [],
  "max_attempts": 3
}
```

Then enqueue and prepare it:

```bash
uv run papertrader queue enqueue --request data/operations/enqueue-idea.json
uv run papertrader queue prepare
uv run papertrader queue validate
```

The CLI converts `now` to a concrete UTC timestamp, validates the operation payload, creates an
immutable ULID and payload, and applies exact deduplication. Never paste a long prompt or nested
payload directly into a CSV cell.

## Dispatch GitHub workflows

The scheduled and manual controller use the same reusable runtime. Start with a dry run:

```bash
gh workflow run daily.yml \
  -f operation_id= \
  -f operation_type=opportunity_research \
  -f max_operations=1 \
  -f dry_run=true \
  -f publish_pages=false \
  -f send_telegram=false
```

After diagnosing the dry run, use `dry_run=false` for bounded execution. Manual dispatch is a
debugging and replay surface, not an approval gate. Scheduled runs use the same code path with the
configured maximum operation count, Pages publication, and Telegram delivery enabled.

Retry publication independently when runtime state is already committed:

```bash
gh workflow run pages.yml -f ref=<commit-sha> -f publish_pages=true
gh workflow run reporting.yml \
  -f commit_sha=<commit-sha> \
  -f report_path=data/wiki/daily-reports/daily-report_YYYYMMDD.md \
  -f run_id=<run-id> \
  -f send_telegram=true
```

## Change configuration

`config.ini` is versioned operating policy. Change one bounded setting, review its risk and
accounting effect, and run the complete gate before committing. Secrets do not belong there.
Important coupled checks include:

- indicator periods versus minimum observation counts;
- risk percentages versus initial capital and gross exposure;
- instrument, exchange, and currency allowlists;
- operation count and model-cost limits;
- fill expiry, price staleness, slippage, fees, and option quote freshness;
- classifier command/model presence as a pair.

Validate a configuration change with:

```bash
uv run papertrader schema validate --strict
uv run papertrader integrity --strict
uv run pytest tests/unit/test_config.py
```

## Recover a failed run

1. Read `data/runs/<run-id>/daily_run.json`, `agent_batch.json`, the operation's
   `validation_report.json`, and the latest structured log entries.
2. Check `data/tables/issues.csv` and `data/issues.md`; do not create a GitHub Issue.
3. If a lease expired, run `papertrader queue release-expired`, then `queue prepare`. A row returns
   to `ready` only while attempts remain; exhausted attempts are retained in history as failed.
4. Fix the deterministic cause. Do not delete history, edit an execution/cash row, or hand-edit the
   generated portfolio.
5. Manually dispatch `daily.yml` with the retained `operation_id` and `max_operations=1`, first as
   a dry run and then, if valid, as a normal run.
6. Retry Pages or Telegram separately with the committed SHA. A Telegram retry resumes at its
   recorded chunk and never rolls back the successful runtime commit.

## Replay by run ID

Run IDs and operation IDs are immutable. Replay never overwrites `data/runs/<run-id>` and never
reuses its artifact directory. Use the retained run to recover exact inputs and create a new
controller run:

1. Read `daily_run.json` for the base SHA/report and `agent_batch.json` for ordered outcomes.
2. Resolve each outcome through `operations_history.csv`, then inspect its immutable
   `payload_path`, `result_path`, command audit, and validation report.
3. Run strict integrity, wiki, and portfolio checks against the retained checkout.
4. Dispatch a new dry run targeted at the original `operation_id`; use a new workflow/run ID.
5. Execute normally only if needed. Exact source hashes and dedupe keys make an already-completed
   source, operation, signal, order, fill, or wiki registration a no-op rather than a duplicate.

The network-free reference replay used by development and CI is:

```bash
PAPERTRADER_VALIDATE_QUARTZ=true \
  uv run pytest tests/integration/test_complete_operating_cycle.py
```

It starts from canonical empty data plus one manually seeded security, then validates market
normalization, cheap classification, five sequential agent operations, research graph creation,
signal/order/fill accounting, a second idempotent pass, clean-checkout commit handoff, an exact
committed Telegram report, and a Quartz build from that same report.

## Add or revise a project skill

Revise the narrowest `skills/papertrader-*/SKILL.md`. Preserve frontmatter with only `name` and
`description`, and keep all required sections: activation, allowed scope, required input,
procedure, source hierarchy, untrusted content, output contract, verification, and failure policy.
Each invocation remains bounded to one operation.

Adding a new operation type is an architecture change, not just a new Markdown file. Update the
closed operation set, payload schema, skill mapping, result path/command allowlists, queue tests,
prompt-injection fixtures, and workflow contract coverage together. Then run:

```bash
uv run papertrader agent preflight \
  --hermes-home "$HERMES_HOME" \
  --operation-type <operation-type>
uv run papertrader integrity --strict
uv run pytest tests/unit/test_agent_runner.py tests/unit/test_result_validator.py
```

Never fork or modify Hermes's native `llm-wiki` skill inside this repository.
