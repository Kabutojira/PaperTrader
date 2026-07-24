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

## Hermes and local harness execution

Step 3 uses a dedicated Hermes profile and one controller process per operation. The controller
preloads native `llm-wiki`, `papertrader-controller`, and the selected operation skill; enables
only the `web`, `file`, and `terminal` toolsets; and invokes `hermes chat` with `--yolo`. Delegation,
messaging, memory, hooks, MCP servers, worktrees, and background fan-out are disabled.

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

The subprocess receives repository paths, safe process settings, and only explicitly configured
inference-provider environment variables. GitHub, Telegram, deployment, brokerage, Actions OIDC,
and runtime tokens are never forwarded. Provider credentials must come from the parent process,
not files in the dedicated Hermes profile.

A local harness such as Codex uses the same contract without inventing alternate instructions:
read `papertrader-controller/SKILL.md` and exactly one operation `SKILL.md`, claim one queue row,
make wiki edits directly, invoke only the documented `papertrader` structured commands, write the
schema-valid completed-change manifest last, and run the validation gate below. Never use a
sub-agent or process a second operation in the same run.

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

Hermes and the commit boundary are separate jobs. The credential-free runtime exports a
hash-bound binary patch containing only runtime-whitelisted paths. A clean checkout at the exact
base commit verifies and applies that patch, repeats the gate, rebases, validates the rebased diff,
and pushes only when a non-empty validated change exists. The GitHub write token is introduced
only for that final push. The post-commit jobs then:

- build the wiki and its canonical daily reports from an exact commit with Quartz;
- deploy the verified `site/public` artifact when Pages publication is enabled;
- read the exact committed report with `git show` and send it to Telegram in escaped, bounded
  chunks;
- retain a failed Telegram chunk cursor in the repository issue ledger so a later dispatch of
  `reporting.yml` can resume delivery without rolling back the runtime commit.

Repository setup requires an inference-only `OPENROUTER_API_KEY` for non-dry Hermes runs and
`TELEGRAM_BOT_TOKEN` plus `TELEGRAM_CHAT_ID` when delivery is enabled. Configure GitHub Pages to
use **GitHub Actions** as its source, and enable repository secret scanning. These secrets are not
placed in the Hermes profile or passed to validation, build, or commit steps. A deployment can be
retried independently by manually dispatching `pages.yml` with the committed SHA. Telegram can be
retried by dispatching `reporting.yml` with the same `commit_sha`, `report_path`, and `run_id`.

The `[classifier]` command and model are deployment settings for the cheap inbox decision. If they
are intentionally left blank, candidate packets remain blocked with a recorded issue;
deterministic code never substitutes a heuristic ingestion decision.

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
