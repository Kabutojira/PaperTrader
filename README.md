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

## Fundamental score export

`security_assessments.csv` also exports optional 0–100 `valuation_score`,
`business_quality_score`, `thesis_score`, `balance_sheet_score` and `risk_penalty`.
Higher values mean stronger support except `risk_penalty`, where higher means more
risk. For `long` securities these judgments do not alter the existing opinion rules.
Short eligibility uses the additional independently sourced weakness gates.
The [rubric 1 contract](docs/FUNDAMENTAL_SCORING.md) defines anchors, overlap,
source evidence, price/session conventions and consumer expiry checks. The worker
receives the matching `research_security` instructions. `scoring_rubric_version`
identifies the rubric.
`score_details` is JSON keyed by all five factors, each with a nonempty `rationale`
and an array of supporting assessment `source_ids`. Unknown components stay empty
with an explanation; numeric components require verified cited sources.

Valuation uses probability-weighted scenario fair value F and verified per-share
reference price P in the assessment's native `currency`:
`min(100, max(0, 50 + 100 * (F/P - 1)))`, rounded to one decimal, ties to even.
`valuation_reference_price` and `valuation_reference_at` record its price and UTC
timestamp; the rationale documents its source, share class and quote-unit conversion
(for example GBp to GBP). This score describes value at assessment time, not a live
recalculation. Unsupported valuation/reference evidence leaves it blank.

Historical rows gain empty numeric columns and explicit unscored explanations:
no scores, evidence, timestamps or expiry are invented. New bounded research can
populate supported components. Existing
`confidence`, `limitations`, source identities and `valid_until` remain authoritative.
FinanceAlerts reads this export by immutable `security_id` and independently
downloads its own prices and calculates technical indicators.

## Watchlist valuation coverage

Every active/watchlist instrument is a research coverage target: a sourced thesis,
valuation method, explicit bear/base/bull per-share fair values and probabilities,
case assumptions, downside, catalysts and invalidation conditions. Coverage counts
instruments independently; another share class's valuation does not cover a missing
instrument. The company queue still permits only one active task per issuer.

Missing, unsupported or incomplete valuations receive priority75, above ordinary
expiry refreshes60 and below severe price movement80/material evidence90/manual100.
A newly completed unsupported review waits until its next eligible refresh rather
than retrying every day. Exhausted entities remain visibly needs_attention.
The30-task queue refills from the canonical watchlist on subsequent market cycles;
entities outside the queue remain coverage targets in the catalog. The homepage
reports baseline completeness separately from freshness, and the company catalog
shows each instrument's bear/base/bull values and coverage gaps. Historical complete
research never becomes a fresh ranking merely by being counted as baseline coverage.

Existing defaults remain3 sequential research operations per daily cycle, including
weekly discovery. No valuation is fabricated to satisfy a coverage target; unavailable
evidence stays explicit and Unrated until sourced scenarios can be supported.

## Bearish research

Every security exports canonical `research_role`: `long`, `short_candidate`, or
`short_research_only`. Existing instruments default to `long`; explicit manual
imports may supply `research_role` and `sector` (investment theme). These fields
are independent of `status`, `research_status` and valuation conclusions.
FinanceAlerts may consume the column without any PaperTrader dependency on it.

The generated [Shorts catalog](https://kabutojira.github.io/PaperTrader/short-candidates)
separates active and research-only candidates, retains unavailable/stale appraisals,
and links each instrument's research. Both bearish roles stay outside ordinary Buy
rankings even if individually appraised Buy. Sell rankings also admit `short`.
Short requires substantial downside plus sourced weak economics or financial
resilience and high risk; it is never assigned by universe membership. See the
[rating methodology](data/wiki/rating-methodology.md) for configurable defaults.
Company summaries are derived at publication from current canonical assessments
and market observations; expired research becomes Unrated without changing history.

Short is research, not an instruction to short shares or buy puts. No option engine,
trading, portfolio, alerts or FinanceAlerts configuration is part of this application.
