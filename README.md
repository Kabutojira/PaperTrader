# PaperTrader

Autonomous investment research, company discovery and valuation, published as a
[searchable research notebook](https://kabutojira.github.io/PaperTrader/).

PaperTrader maintains immutable company/instrument identities, current sourced
research, bear/base/bull valuations where evidence supports them, and deterministic
research-only Buy/Hold/Sell opinions. Unsupported and stale research stays readable
but cannot enter current Top10 Buy/Sell lists. It has no portfolio, allocations,
orders, executions, market alerts, Telegram pipeline or broker integration.

## Operating model

1. Daily market refresh at **13:00 America/New_York**, including DST. One bounded
   yfinance provider updates completed-session prices and internal research priority.
2. Sequential research follows scheduled market completion: up to three operations
   per cycle, one company or idea each. Weekly discovery shares that budget and may
   propose at most one idea/two companies. It creates no mandatory task cascade.
3. The controller validates a completed result and commits current CSV/wiki/source
   changes atomically. Failure preserves prior research and affects only that task.
4. Independent Quartz/Pages publication consumes an exact committed revision.
   Publication can retry with research and market offline.

Queue cap30, attempts2 and assessment freshness30 days are versioned defaults in
[research.ini](research.ini). One task aggregates each company's current reasons.
Exhausted tasks become needs_attention and are not automatically requeued.
FinanceAlerts remains independent and supplies no market data to PaperTrader.

## Start locally

Requires Python3.12–3.14 and Node24.4.1 for Quartz; locked dependencies are used.

```sh
uv sync --locked --all-groups
uv run papertrader validate
uv run papertrader market                # preview: no requests/writes
uv run papertrader research              # preview: no model/writes
uv run papertrader discover              # preview: no model/writes
uv run papertrader publish               # deterministic current rankings preview
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
npm ci --prefix site --ignore-scripts
PAPERTRADER_BASE_URL=localhost npm run check --prefix site
PAPERTRADER_BASE_URL=localhost npm run build --prefix site
```

Real research runs in the pinned Hermes container with isolated inference OAuth.
It has one read-only web tool and no Git/Pages write credentials. Do not place
plaintext credentials in this public checkout. GitHub Actions handles encrypted
OAuth restoration and deterministic post-agent commits.

## Data and documentation

Current CSV contracts are in [schemas/research_contracts.yaml](schemas/research_contracts.yaml).
Canonical tables live under data/tables/, the bounded queue in data/research_queue.csv,
market observations in data/market/, and current research in data/wiki/. Source
registry and Markdown citations remain authoritative; there are no active research
history or revision-chain tables. Git retains history.

See [operations](docs/OPERATIONS.md), [implementation and acceptance evidence](PLAN.md),
[migration dispositions](docs/migration/M3.md) and
[rating methodology](data/wiki/rating-methodology.md). The verified
`pre-research-only-20261018` tag preserves all removed legacy data/code.

The initial migrated coverage had82 expired assessments and no supported current
valuation. Refresh is deliberately bounded; rankings remain empty until fresh,
supportable research qualifies. Honest unsupported results do not manufacture prices
or fair values to fill the lists.
