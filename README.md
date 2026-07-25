# PaperTrader

PaperTrader is a public, Git-native research system for paper trading. The repository is the
source of truth: research, queued work, market snapshots, simulated accounting records, and the
published wiki all live under `data/`.

PaperTrader never places a real order. Every command requires `PAPER_TRADING_ONLY=true`, and the
execution boundary asserts the same invariant again.

## Local setup

Python 3.12 or newer and [uv](https://docs.astral.sh/uv/) are required.

```bash
cp .env.example .env
export PAPER_TRADING_ONLY=true
export WIKI_PATH="$PWD/data/wiki"
uv sync --locked --all-groups
```

The project skills are stored in `skills/`. Hermes should set `skills.external_dirs` to the
checkout's `skills` directory. A local agentic harness can read the same `SKILL.md` files directly
and must follow `AGENTS.md`, use the project CLI for structured state, and run operations
sequentially.

## Run an operation from Codex instead of Hermes

The local harness boundary lets an existing Codex shell execute the repository skills without
starting Hermes or decrypting Hermes OAuth state. It still claims one queue row, records a
content-addressed baseline outside the checkout, audits structured CLI writes, validates the exact
result, and owns the terminal queue transition.

Prepare a daily run and start one already-enqueued operation:

```bash
RUN_ID="local-$(date -u +%Y%m%dT%H%M%SZ)"
OPERATION_ID="<operation ULID>"
BASE_SHA="$(git rev-parse HEAD)"

uv run papertrader daily prepare \
  --run-id "$RUN_ID" \
  --trigger local \
  --source-sha "$BASE_SHA" \
  --offline \
  --skip-classifier

uv run papertrader agent harness start \
  --run-id "$RUN_ID" \
  --operation-id "$OPERATION_ID"
```

The `--offline --skip-classifier` flags make the example reproducible without market or classifier
network access. Omit them when you want the normal daily market retrieval and configured inbox
classification phases.

The start command returns the payload, trusted controller prompt, exact controller/operation skill
paths, result path, and command-audit path. In the Codex shell, read those files completely and
perform exactly one operation. For every agent-side `papertrader` command, set the returned audit
context:

```bash
export PAPERTRADER_AUDIT_RUN_ID="$RUN_ID"
export PAPERTRADER_AUDIT_OPERATION_ID="$OPERATION_ID"
export PAPERTRADER_AUDIT_PATH="data/runs/$RUN_ID/$OPERATION_ID/command_audit.json"
```

Write `data/runs/$RUN_ID/$OPERATION_ID/agent_result.json` last. Then let the deterministic
controller validate and terminalize the operation, and finish the daily phases:

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

When `daily prepare` exists for the run ID, `harness finish` also records the validated outcome in
that run's sequential agent batch. Omit the daily prepare/finalize commands for a standalone
single-operation debug run. A failed finish writes a validation report, records a repository-local
issue, and applies the bounded retry policy; it never silently marks invalid work complete. Run
artifacts are immutable, so fix the cause and use a new `RUN_ID` for a bounded retry rather than
deleting or overwriting the failed attempt.

## Add an investment idea

Adding an idea means queueing one bounded `idea_research` operation; it does not create an
unresearched wiki stub or skip directly to a strategy. Put the substantial seed in repository JSON:

```bash
mkdir -p data/operations/requests
editor data/operations/requests/idea-grid-flexibility.json
```

```json
{
  "operation_type": "idea_research",
  "entity_type": "idea",
  "entity_id": "idea_grid_flexibility",
  "dedupe_key": "idea_research:idea_grid_flexibility:manual:2026-07",
  "prompt": "Research one grid-flexibility investment idea.",
  "inputs": {
    "idea_id": "idea_grid_flexibility",
    "seed_claim": "Load growth and constrained grids may reward selected flexibility suppliers."
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

```bash
uv run papertrader queue enqueue \
  --request data/operations/requests/idea-grid-flexibility.json
uv run papertrader queue prepare
uv run papertrader queue validate
```

The enqueue output contains the immutable operation ULID to pass to `agent harness start`.

## Add a security

Security addition is deterministic and identity-only. It does not invent a thesis or valuation:

```bash
mkdir -p data/operations/requests
editor data/operations/requests/security-enphase.json
```

```json
{
  "watchlist_reason": "Candidate beneficiary of solar-plus-storage normalization; research pending.",
  "source": "https://investor.enphase.com/",
  "securities": [
    {
      "company_name": "Enphase Energy, Inc.",
      "instrument_name": "Enphase Energy, Inc. common stock",
      "instrument_type": "equity",
      "ticker": "ENPH",
      "exchange_code": "NMS",
      "venue_mic": "XNAS",
      "provider_symbol": "ENPH",
      "currency": "USD",
      "country": "US",
      "sector": "Technology",
      "industry": "Solar"
    }
  ]
}
```

```bash
uv run papertrader watchlist import \
  --request data/operations/requests/security-enphase.json
```

Use the returned immutable `security_id` in a separately enqueued `security_research` operation.
Ticker text alone is never an identity, and a new `watchlist` row is not monitored for trading
until validated research changes its status to `watching` or `active`.

## Hermes execution

GitHub Actions uses a dedicated Hermes profile and one controller process per operation. The
controller preloads native `llm-wiki`, `papertrader-controller`, and the selected operation skill;
enables only the `web`, `file`, and `terminal` toolsets; and invokes `hermes chat` with `--yolo`.
Delegation, messaging, memory, hooks, MCP servers, worktrees, and background fan-out are disabled.

Use a dedicated `HERMES_HOME`; configuration intentionally refuses to overwrite a normal personal
profile unless `--replace-unmanaged` is explicit. The native `llm-wiki` skill must already exist
under that profile's `skills/` directory. The official container initializes bundled skills there.

```bash
export HERMES_HOME=/tmp/papertrader-hermes
uv run papertrader agent configure --hermes-home "$HERMES_HOME" --replace-unmanaged
hermes skills opt-in --sync
uv run papertrader agent preflight \
  --hermes-home "$HERMES_HOME" \
  --operation-type opportunity_research
uv run papertrader agent run \
  --hermes-home "$HERMES_HOME" \
  --run-id local-20260724-01
```

The subprocess receives repository paths, safe process settings, and the isolated profile's
`auth.json`. Its provider is fixed to `openai-codex`, while the model remains configurable in
`config.ini`. No inference API key, GitHub, Telegram, deployment, brokerage, Actions OIDC, age
identity, or runtime token is forwarded.

Every agent-side project command creates an operation-scoped receipt in
`data/runs/<run_id>/<operation_id>/command_audit.json`. Post-run validation compares a
content-addressed before/after snapshot with `files_changed`, requires receipts for every structured
change, rejects symlinks/deletions/path escapes and skill-scope violations, verifies newly created
operations/issues, and runs strict integrity, wiki, and portfolio checks before queue completion.

## Deterministic core

The Step 2 core owns every numeric and structured state transition:

- `papertrader market update` retrieves normalized yfinance daily bars, applies exchange
  calendars, and maintains the 365-day price cache and durable corporate-action ledger.
- `papertrader indicators update --classify-opportunities` calculates the pinned TA-Lib
  indicators, writes candidate inbox packets, asks the configured cheap classifier for an
  `ingest` or `ignore` decision, and enqueues deduplicated follow-up work.
- `papertrader queue prepare`, `queue claim`, and the terminal queue commands enforce one live
  lease, dependencies, cooldowns, bounded retries, terminal history, and run budgets.
- `papertrader signal create`, `order create`, and `fills process` accept repository-local JSON
  request files. Signals and pending orders do not affect accounting; only an eligible
  deterministic paper fill appends executions and cash entries.
- `papertrader portfolio reconcile --strict` replays append-only ledgers, verifies cash links and
  exact Decimal arithmetic, and checks the generated portfolio against canonical state.
- `papertrader research source record`, `research security upsert`,
  `research relationship upsert`, and `research strategy upsert` are the only agent-facing routes
  for their structured research tables. They preserve immutable identities and require linked wiki
  pages to exist before the CSV state changes.
- `papertrader watchlist import --request <json>` atomically adds identity-only securities with
  deterministic IDs. It leaves research fields empty until a bounded security-research operation
  creates the linked wiki page and evidence-backed summary.

Do not hand-edit structured runtime CSVs. Use the CLI so identity, schema, atomic-write,
paper-only, risk, and audit contracts are enforced. `executions.csv`, `cash_ledger.csv`,
`corporate_actions.csv`, operation history, and run history are append-only.

## Daily automation and publication

The scheduled controller in `.github/workflows/daily.yml` uses one serialized path for both cron
and manual runs. It prepares market and queue state, executes at most the configured number of
Hermes operations one at a time, processes eligible paper fills, rebuilds accounting, writes the
canonical daily report, and runs the complete validation gate. Manual runs expose
`operation_id`, `operation_type`, `max_operations`, `dry_run`, `publish_pages`, and
`send_telegram`; `dry_run` defaults to true and performs no inference, commit, push, deployment,
or delivery.

Hermes and the commit boundary are separate jobs. The read-only runtime decrypts the repository's
age-encrypted OpenAI Codex OAuth state into its isolated Hermes home, then exports a hash-bound
binary runtime patch and, only after a token refresh, a separate ciphertext-only artifact. A clean
checkout at the exact base commit verifies and applies the allowed artifacts, repeats the gate,
rebases, validates the rebased diff, and pushes only when a non-empty validated change exists. If
inference fails after a refresh, the commit boundary discards all runtime data and may commit only
the exact encrypted OAuth file. The GitHub write token is introduced only for that final push, and
the write job never receives the OAuth secret or plaintext. The post-commit jobs then:

- build the wiki and its canonical daily reports from an exact commit with Quartz;
- deploy the verified `site/public` artifact when Pages publication is enabled;
- read the exact committed report with `git show` and send it to Telegram in escaped, bounded
  chunks;
- retain a failed Telegram chunk cursor in the repository issue ledger so a later dispatch of
  `reporting.yml` can resume delivery without rolling back the runtime commit.

Repository setup requires `OPENAI_OAUTH_SECRET` and the matching
`.papertrader/credentials/openai-oauth-auth.json.age` for non-dry Hermes runs; no OpenAI or
OpenRouter API key is needed for the main path. Delivery additionally requires
`TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. Configure GitHub Pages to use **GitHub Actions** as its
source, and enable repository secret scanning. See the operating runbook for OAuth seeding,
verification, rotation, and revoked-grant recovery. A deployment can be retried independently by
manually dispatching `pages.yml` with the committed SHA. Telegram can be retried by dispatching
`reporting.yml` with the same `commit_sha`, `report_path`, and `run_id`.

The `[classifier]` command and model are deployment settings for the cheap inbox decision. If they
are intentionally left blank, candidate packets remain blocked with a recorded issue;
deterministic code never substitutes a heuristic ingestion decision.

See the [operating runbook](docs/OPERATIONS.md) for queue examples, local skill execution, manual
workflow dispatch, configuration changes, failed-run recovery, replay by run ID, publication
retry, and project-skill maintenance.

## Development architecture

PaperTrader separates deterministic state ownership from agent judgment. The repository is the
database, every durable mutation is reviewable in Git, and no component has a real-order adapter.

```text
request JSON -> validated queue -> one claimed operation -> Hermes or local Codex harness
             -> completed edits + agent_result.json -> deterministic result validator
             -> terminal history -> fills/accounting/report -> write-controlled Git boundary
```

| Layer | Owns | Main implementation |
| --- | --- | --- |
| Contracts and policy | CSV/JSON schemas, IDs, limits, paths, paper-only settings | `AGENTS.md`, `schemas/`, `config.ini`, `src/papertrader/config.py` |
| Deterministic state | Queue transitions, market data, indicators, orders, fills, ledgers, portfolio, reports | `src/papertrader/*.py` through the `papertrader` CLI |
| Agent judgment | Research synthesis, causal theses, bounded follow-ups, strategy decisions | `skills/papertrader-*/SKILL.md` plus native `llm-wiki` in Hermes |
| Agent boundary | One-operation claim, prompt construction, CLI receipts, exact delta/result validation | `agent_runner.py`, `local_harness.py`, `command_audit.py`, `result_validator.py` |
| Persistence | Canonical research/runtime state and immutable history | `data/` |
| Automation | Read-only inference, validated artifact handoff, sole write-enabled commit job | `.github/workflows/reusable-llm.yml` |
| Publication | Canonical report, Quartz Pages, post-commit Telegram delivery | `reports.py`, `site/`, `reporting.yml`, `pages.yml` |

Structured CSVs must never be hand-edited by an agent. Wiki Markdown is the agent's direct write
surface within the selected skill scope; request-bearing CLI commands are the only route to
structured state. `agent_result.json` describes changes already made and is written last. The
validator compares it with a pre-run content snapshot, command receipts, queue/issue identities,
the runtime whitelist, strict wiki lint, integrity, and accounting reconciliation before the queue
can advance.

## Validation

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run papertrader integrity --strict
uv run papertrader wiki lint --strict
uv run papertrader portfolio reconcile --strict
```

Validate paths staged for an automated runtime commit with:

```bash
uv run papertrader runtime-whitelist validate --staged
```

Development changes may touch source, tests, schemas, skills, workflows, and site configuration.
Automated runtime commits are intentionally restricted to the data paths documented in
`AGENTS.md`.
