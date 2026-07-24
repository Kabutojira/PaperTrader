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

Do not hand-edit structured runtime CSVs. Use the CLI so identity, schema, atomic-write,
paper-only, risk, and audit contracts are enforced. `executions.csv`, `cash_ledger.csv`,
`corporate_actions.csv`, operation history, and run history are append-only.

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
