# PaperTrader operating runbook

This runbook covers version-1 operation from a clean checkout. `AGENTS.md`, the JSON/CSV schemas,
and the repository-local skills remain authoritative if an example here ever conflicts with a
contract.

## Safety and local setup

PaperTrader has no real-execution adapter. Do not add brokerage credentials to the checkout,
GitHub secrets, Hermes profile, or request files. Configure the canonical wiki path before running
project commands:

```bash
cp .env.example .env
set -a
. ./.env
set +a
export WIKI_PATH="$PWD/data/wiki"
uv sync --locked --all-groups
```

The main inference provider is `openai-codex`. GitHub Actions restores only the encrypted OAuth
state described below. Only an explicitly selected OpenRouter auxiliary receives its purpose-bound
key; GitHub write, Telegram, deployment, brokerage credentials, unrelated API keys, and the age
private identity must never enter the Hermes process.

## Seed and maintain OpenAI Codex OAuth

Use a dedicated Hermes profile so the seeded file contains PaperTrader's Codex OAuth state rather
than unrelated provider credentials. Authenticate interactively outside GitHub Actions, for
example with `hermes profile create papertrader`, followed by `hermes -p papertrader model` and the
OpenAI Codex OAuth choice. Hermes stores the default profile at `~/.hermes/auth.json` and a named
profile at `~/.hermes/profiles/<profile-name>/auth.json`.

Generate one age identity and derive its public recipient:

```bash
install -d -m 700 "$HOME/.config/papertrader"
age-keygen -o "$HOME/.config/papertrader/openai-oauth.agekey"
age-keygen -y "$HOME/.config/papertrader/openai-oauth.agekey"
```

Set the complete `AGE-SECRET-KEY-1...` identity as the repository secret without putting it on a
command line, then encrypt the dedicated profile's authenticated state to the exact repository
path:

```bash
gh secret set OPENAI_OAUTH_SECRET < "$HOME/.config/papertrader/openai-oauth.agekey"
gh secret set YOUTUBE_DATA_API
gh variable set MAX_OPERATIONS --body 5
gh variable set AUXILIARY_MODEL --body openai-codex:gpt-5.6-terra
recipient="$(age-keygen -y "$HOME/.config/papertrader/openai-oauth.agekey")"
install -d .papertrader/credentials
age --encrypt \
  --recipient "$recipient" \
  --output .papertrader/credentials/openai-oauth-auth.json.age \
  "$HOME/.hermes/profiles/papertrader/auth.json"
```

For a default Hermes profile, use `$HOME/.hermes/auth.json` as the source. Verify the ciphertext
without printing its contents, and remove the temporary plaintext unconditionally:

```bash
verify_file="$(mktemp)"
trap 'rm -f "$verify_file"' EXIT
age --decrypt \
  --identity "$HOME/.config/papertrader/openai-oauth.agekey" \
  --output "$verify_file" \
  .papertrader/credentials/openai-oauth-auth.json.age
cmp -s "$HOME/.hermes/profiles/papertrader/auth.json" "$verify_file"
```

Commit only `.papertrader/credentials/openai-oauth-auth.json.age`. Never commit `auth.json`, the
age identity, the verification file, or a pre-run snapshot. Non-dry runs decrypt into the isolated
Hermes home, detect byte changes after all operations, re-encrypt only on change, verify the new
ciphertext, and remove plaintext under `if: always()`. An unchanged OAuth file creates no
ciphertext-only commit.

If OpenAI revokes the grant or Hermes no longer recognizes it, authenticate the dedicated local
profile again, re-encrypt its fresh `auth.json` with the same public recipient, replace the exact
repository ciphertext, and commit it. To rotate the encryption identity, generate a new identity,
replace `OPENAI_OAUTH_SECRET`, re-encrypt from a freshly authenticated profile to the new public
recipient, verify it, and commit the replacement ciphertext. Never run an interactive login flow
inside GitHub Actions.

`YOUTUBE_DATA_API` is optional and scoped only to curated discovery. When it is absent or empty,
the scanner uses anonymous `pytubefix`. `OPENROUTER_API_KEY` is also optional unless
`AUXILIARY_MODEL` is explicitly set to `openrouter:<model>`; configure it with
`gh secret set OPENROUTER_API_KEY` only for that override.

## Run one operation from a local Codex shell

Use the two-phase local harness boundary when Codex is already running in the checkout. It does
not invoke Hermes and does not need `OPENAI_OAUTH_SECRET`. First prepare the daily deterministic
state and claim one previously enqueued operation:

```bash
RUN_ID="local-$(date -u +%Y%m%dT%H%M%SZ)"
OPERATION_ID="<operation ULID>"

uv run papertrader daily prepare \
  --run-id "$RUN_ID" \
  --trigger local \
  --source-sha "$(git rev-parse HEAD)" \
  --offline \
  --skip-classifier
uv run papertrader agent harness start \
  --run-id "$RUN_ID" \
  --operation-id "$OPERATION_ID"
```

Keep `--offline --skip-classifier` for a repository-only debug run. Omit them to execute normal
market retrieval and the configured classifier before claiming the operation.

`harness start` fails if another operation is running. It writes a trusted controller prompt and
skill-content identities under `data/runs/<run-id>/<operation-id>/`, then stores the full
content-addressed validation baseline in a private temporary file outside the repository. Read the
returned controller prompt, controller skill, selected operation skill, payload, wiki schema,
results-first homepage, complete research catalog, and recent log before editing anything.

Agent-side structured commands need operation-scoped receipts:

```bash
export PAPERTRADER_AUDIT_RUN_ID="$RUN_ID"
export PAPERTRADER_AUDIT_OPERATION_ID="$OPERATION_ID"
export PAPERTRADER_AUDIT_PATH="data/runs/$RUN_ID/$OPERATION_ID/command_audit.json"
```

Use those variables only while executing the selected skill's allowed `papertrader` commands.
Make direct Markdown edits only where the skill permits, perform its checks, and write
`agent_result.json` last. Then return control to the deterministic boundary:

```bash
unset PAPERTRADER_AUDIT_RUN_ID PAPERTRADER_AUDIT_OPERATION_ID PAPERTRADER_AUDIT_PATH
uv run papertrader agent harness finish \
  --run-id "$RUN_ID" \
  --operation-id "$OPERATION_ID"

REPORT_DATE="$(date -u +%Y%m%d)"
uv run papertrader daily finalize \
  --run-id "$RUN_ID" \
  --github-report-url \
  "https://github.com/Kabutojira/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_${REPORT_DATE}.md"
```

`harness finish` reconstructs the baseline and validates the exact delta, result schema, allowed
paths and commands, immutable request receipts, newly created operations/issues, manifest-last
ordering, integrity, wiki, and portfolio. Only then does it complete, skip, block, or fail the
queue row. If the run was prepared by `daily prepare`, it also appends the outcome to the daily
agent batch so `daily finalize` can run. A validation failure records its report and issue and
uses the normal bounded retry policy. Let an expired abandoned claim recover through
`papertrader queue release-expired`; do not manufacture a completion request.

Every run artifact directory is immutable. After fixing a validation failure, use a new `RUN_ID`
for the retry and retain the failed run as audit evidence; do not delete, rename, or overwrite it.

For a standalone skill debug, omit `daily prepare` and `daily finalize`; start and finish still
enforce exactly one operation. Never start a second Codex agent or process another row before the
first finish returns.

## Migrate legacy assessments and stage v2 refreshes

Run the migration once with a stable run ID and bounded refresh count. Retrying the exact command
is idempotent: immutable history is not duplicated and the rollout report is byte-stable.

```bash
papertrader research migrate-assessments \
  --run-id rollout-step22-YYYYMMDD \
  --enqueue-limit 12 \
  --as-of YYYY-MM-DDTHH:MM:SSZ
```

The command writes the exact current assessment header, archives legacy rows as `legacy_v1`, and
leaves scenario, expected-return, and rating fields unavailable. It reuses or creates only the
highest-priority bounded security refreshes and writes `data/runs/<run_id>/research_rollout.json`.
Do not enable deployment based on legacy rows: allocation remains gated on complete assessment-v2
evidence and the configured diversification threshold.

## Run one operation through local Hermes

Use a dedicated Hermes profile and process one operation at a time:

```bash
export HERMES_HOME=/tmp/papertrader-hermes
export MAX_OPERATIONS="${MAX_OPERATIONS:-5}"
export AUXILIARY_MODEL="${AUXILIARY_MODEL:-openai-codex:gpt-5.6-terra}"
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
post-run validation replace interactive approval.

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
Preparation also archives plan-bound strategy and execution requests as `skipped` when their
`allocation_plan_id` no longer matches the sole current generated allocation plan. This check is
deterministic and occurs before an LLM can claim obsolete work.

When a blocked agent result is later proven obsolete, archive it without hand-editing queue state:

```bash
uv run papertrader queue resolve-blocked --request data/runs/<run-id>/resolve-blocked.json
```

The request identifies the blocked operation and prior run, cites that run's `agent_result.json`,
selects `skipped` or `cancelled`, and supplies a concise summary and machine-readable terminal
reason. The CLI validates the artifact and atomically moves the complete request to history.

An idea enters the system through this `idea_research` queue command. It becomes a maintained wiki
page only after the selected skill supplies evidence, mechanism, catalysts, invalidation,
confidence, and a review date. It cannot create a strategy directly.

Add a security identity separately with `papertrader watchlist import --request <json>`. The
request requires one HTTP(S) identity source, one watchlist reason, and each security's company and
instrument names, instrument type, ticker, exchange code, venue MIC, provider symbol, currency,
country, sector, and industry. The command returns a stable `security_id` and leaves research
fields blank. Queue a bounded `security_research` operation with that ID before promoting the row
to `watching` or `active`. See the complete copyable idea and security request examples in the
README.

## Run and review baseline allocation

Every completed `security_research` operation must write a current comparable assessment through:

```bash
uv run papertrader research assessment upsert \
  --request data/runs/<run-id>/<operation-id>/assessment-request.json
```

The request must use the exact `security_assessments.csv` columns, registered fresh `source_id`
references, canonical scores/blockers/gaps, UTC timestamps, and the current run ID. An unsupported
valuation or other hard failure is represented by `eligibility=ineligible` and an explicit hard
blocker; do not omit the assessment.

Generate a plan only after accounting has reconciled:

```bash
uv run papertrader allocation maintain \
  --run-id "allocation-maintenance-$(date -u +%Y%m%dT%H%M%SZ)" --backfill
uv run papertrader allocation readiness --strict
uv run papertrader portfolio reconcile --strict
uv run papertrader allocation plan --run-id "allocation-$(date -u +%Y%m%dT%H%M%SZ)"
```

Omit `--backfill` during ordinary maintenance; daily preparation already does this in
`report_only` and `active` modes. Backfill and agent execution remain sequential, in configured
batches of at most five. Readiness covers only securities with a non-empty canonical
`research_page`; identity-only watchlist rows are intentionally excluded.

Inspect `data/tables/allocation_targets.csv` and the matching
`data/runs/<run-id>/allocation_plan.json`. The immutable audit rows are in
`data/tables/allocation_history.csv`. Never hand-edit these files. The versioned mode is `active`;
the operator explicitly waived the original five-live-cycle shadow requirement. A diagnostic
`report_only` run must still produce no allocation-generated queue rows, signals, orders, or
accounting changes. Active mode does not override readiness: missing or stale evidence,
assessments, relationships, prices, or FX leaves the affected target at zero and retains cash.

In active mode, material target deltas enqueue ordinary sequential `strategy_research` work for
the next run. Baseline strategies remain long-equity only, must retain the current allocation-plan
ID, and can trade only the deterministic whole-share delta. A superseded/stale plan, changed hard
blocker, stale price/FX rate, reserve breach, risk-budget breach, canonical-leg mismatch, or target
overrun fails closed. `hold` and below-minimum-trade targets create no signal or order.
Allocation-plan identity excludes the controller run ID and publication timestamp: unchanged
economic inputs retain one plan ID, while immutable history distinguishes repeated observations by
plan, run, and security. This keeps a valid in-flight signal current across routine finalization.
Baseline and conviction orders may not share one instrument identity; close or cancel the existing
sleeve exposure before opening the other sleeve so portfolio ownership remains deterministic.
Create baseline orders with `papertrader order create-baseline --request <json>`. Supply current
reference prices and FX but no legs: the command derives the exact whole-share action and delta
from the current plan, holdings, and pending orders. Creating a newer signal cancels any older
un-ordered ready signal for the same strategy so the investor dashboard exposes one current action.
Allocation dispositions `open` and `increase` both normalize to the `open` signal and
`execute_strategy` action. The distinction remains in the current allocation target; the agent
does not translate it into a quantity or submit an `increase` action outside the payload schema.
The baseline strategy's `risk_budget_pct` must equal the configured maximum baseline-position
percentage. Treat it as a stable ceiling; the current plan's exact target value, not its rounded
display weight or the strategy leg's research quantity, owns order sizing.

Committed FX rates are stored at `data/market/fx/<currency>_<base_currency>.csv` and refreshed by
the normal market phase for every allowed non-base currency. Missing or stale FX excludes a new
candidate and defers an existing foreign order. Do not enter a manual substitute rate.

## Validate the investor decision publication

Every completed daily run writes one immutable decision snapshot and refreshes the latest JSON and
CSV exports, investor pages, daily report, and Telegram brief from that same identity. The
publication is a derived projection and must never be used as input to allocation, trading, or
accounting.

```bash
uv run papertrader advice refresh --run-id <completed-run-id>
uv run papertrader advice validate --strict
```

Inspect `data/published/decision_snapshot.json`, `model_portfolio.csv`, and
`actionable_signals.csv`. Filled holdings, validated pending orders, allocation candidates, and
research alerts are distinct states; only a canonical live paper order may be copy ready. The
model-portfolio scaler runs locally in the browser; it does not submit an order or persist the
entered portfolio value. Never overwrite an existing run snapshot with different state;
create and complete a new daily run instead.

Canonical market and research state can advance between daily preparation and finalization. Inside
a controller-created operation for that same `prepared` run, integrity defers only the publication
source-hash freshness comparison; finalization regenerates the snapshot and the ordinary strict
gate requires it to match current state. Snapshot schema, immutable-artifact, CSV, queue, wiki, and
accounting checks are never deferred.
If several manual runs complete on the same date, they intentionally share the single canonical
daily-report path. The latest completed run owns that page, while every run keeps its own immutable
decision snapshot under `data/runs/<run_id>/`.

## Dispatch GitHub workflows

The controller is scheduled for 17:00 `Europe/Rome` every day, including weekends. Scheduled and
manual invocations use the same reusable runtime. Start with a dry run:

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

Telegram delivery verifies the bot and destination, sends Rich Markdown after the report commit,
and retains one latest-only failure issue. A newer report supersedes older missed reports; they are
not replayed or summarized. After committing a local completed run, deliver its report with:

```bash
uv run papertrader telegram deliver-run \
  --commit-sha "$(git rev-parse HEAD)" \
  --run-id <run-id> \
  --repository-url https://github.com/Kabutojira/PaperTrader
```

## Change configuration

`config.ini` is versioned operating policy. Change one bounded setting, review its risk and
accounting effect, and run the complete gate before committing. Secrets do not belong there.
Important coupled checks include:

- indicator periods versus minimum observation counts;
- risk percentages versus current epoch equity and gross exposure;
- instrument, exchange, and currency allowlists;
- allocation mode, cash hurdle/reserve, diversification, deployment, position, sector, and theme
  limits, including minimum base upside, minimum upside/downside, and their cross-checks against
  risk limits;
- operation count and model-cost limits;
- fill expiry, price staleness, slippage, fees, and option quote freshness;
- classifier command/model presence as a pair.

Resize the model account without rewriting its original capital entry by using an auditable JSON
request containing `target_equity_base`, `reason`, `run_id`, and `effective_at`:

```bash
uv run papertrader account rebase --request data/runs/<run-id>/rebase-account.json
uv run papertrader performance update --run-id <run-id>
```

The command requires every order to be terminal, appends a capital contribution or withdrawal,
and starts a new flow-adjusted performance epoch. Earlier epoch rows remain immutable audit data.

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
6. Retry Pages or the latest Telegram report separately with the committed SHA. Older missed
   reports are not replayed, and delivery never rolls back the successful runtime commit.

## Replay by run ID

Run IDs and operation IDs are immutable. Replay never overwrites `data/runs/<run-id>` and never
reuses its artifact directory. Use the retained run to recover exact inputs and create a new
controller run:

1. Read `daily_run.json` for the base SHA/report and `agent_batch.json` for ordered outcomes.
2. Resolve each outcome through `operations_history.csv`, then inspect its immutable
   `payload_path`, `result_path`, command audit, and validation report.
3. Run strict integrity, advice, wiki, and portfolio checks against the retained checkout.
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
signal/order/fill accounting, a reconciled decision snapshot and investor dashboard, a second
idempotent pass, clean-checkout commit handoff, an exact committed Telegram report, and a Quartz
build from that same report.

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
