# PaperTrader research-only migration

The product is autonomous public-company discovery, investment research and
valuation. This plan, supplied on 2026-10-18, supersedes the retired trading and
research-governance plans preserved in the pre-migration Git ref. Implement one
milestone at a time; validate, commit, push and inspect CI before advancing.

## Product contract

Retain immutable instrument `security_id` and company `issuer_id`, curated
companies/ideas, sourced current Markdown research, a current source registry,
market caches, supportable scenarios and research-only ratings. Deterministic
code owns tables, pricing arithmetic, validation, scheduling and publication.
One sequential configurable research model stages complete company/idea results;
it never receives GitHub-write or deployment credentials. Untrusted sources are
data, not instructions. Preserve citations and copyright precautions.

Remove the active portfolio, capital, accounting, allocation, strategies, signals,
orders/fills, options, performance, alerts/Telegram, final-buy/router/classifier,
YouTube/Seeking Alpha, podcasts, automated wiki maintenance, dependency cascades,
immutable research revision/history tables, old runs and daily decision snapshots.
No broker/live trading, holdings advice, second market provider or FinanceAlerts
dependency. History belongs in Git, not growing active history tables.

Three independent workflows: bounded LLM-free market refresh; sequential company
or idea research with weekly discovery mode; Pages build/deploy from a known
commit. Each phase has independent status and exit code. Preserve good data on
partial failure. Keep the current published site until the reviewed replacement
is ready. Final acceptance requires real non-dry Actions and Pages checks; never
label mocked/local checks as live.

## Defaults and data

- `research.max_daily_operations = 3`, `max_pending = 30`, `max_attempts = 2`,
  `assessment_freshness_days = 30`.
- Discovery defaults: at most weekly, one new idea and two new companies. Catalog
  creation never creates mandatory research cascades.
- One pending/running/failed task per company or idea, merged reasons and priority;
  completed tasks leave the queue, exhausted entities need attention. No blocked
  capacity rows, dependencies, semantic classifier or growing operation history.
- Authoritative: `securities.csv`, new `ideas.csv`, compact `relationships.csv`,
  latest-only `security_assessments.csv`, current `source_registry.csv`, new
  `data/research_queue.csv`, OHLCV caches and `market/latest.csv`, current company
  and idea pages. Optional compact `data/status.json` stores only latest outcomes.
- Assessments retain dates/expiry, status, method/rationale, currency/horizon,
  supported scenarios/probabilities, thesis/assumptions, risks/catalysts,
  invalidation, confidence, limitations and current sources. Unsupported is
  honestly Unrated; no trade eligibility or portfolio action columns.
- Price freshness follows completed exchange sessions. Bounded requests/retries,
  individual failed-symbol fallback and periodic corrections; preserve last good
  bars. Repricing never changes research dates or underlying fair values.
- Top 10 Buy/Sell: up to ten fresh supported entries, per-issuer deduped, current
  native price, fair value, derived return, confidence, dates and research link.
  No stale padding. Initially 82/83 assessments are expired and the other is
  unsupported. Preserve browseable stale research without current recommendations.

## Milestones and completion gates

| Milestone | Scope and gate | Status |
| --- | --- | --- |
| M0 | Freeze scheduler, verified backup, exact inventory, reproduce/repair retired technical charts, capture assessment/frontmatter ordering failure; dry run changes no source data | Local gates passed; commit/push and CI pending |
| M1 | Repeatable dry-run-by-default compact schema migration; preserve identities, current meaning, prose/citations and expiry; schema/reference/wiki tests; no invented evidence | Pending |
| M2 | Standalone market/cache/indicators/valuation/ratings core; sessions/holidays, bounded batching, per-symbol failure/corrections; no LLM or portfolio paths | Pending |
| M3 | One-entity bounded queue, deterministic priorities/retries, retire old producers; census-based disposition of all 340 blocks and 13 waiting relationships; <=30 tasks | Pending |
| M4 | Two single-model operations; bounded context/web/turn/runtime budgets; final staged Markdown and complete result validated before atomic CSV/wiki/source transaction; idempotent and rollback-safe | Pending |
| M5 | Weekly bounded discovery/manual import and inline links; validate identity, dedupe issuers/share classes, retain citations/unresearched status; no fan-out | Pending |
| M6 | Deterministic fresh Top 10 Buy/Sell, company/idea catalogs, recent updates and health; optional nonblocking charts; Quartz build and reviewed output/links | Pending |
| M7 | Independent market/research/Pages workflows, least credentials, compact writes and focused validation; live non-dry market/research smoke; isolate failure cases | Pending |
| M8 | Delete dead modules/CLI/schemas/skills/actions/tests and old data only after migration gates; rewrite actual-product docs/config/CI; prove no live references; report size reduction | Pending |
| M9 | Clean-checkout full schemas/source/link integrity/Ruff/MyPy/tests/Quartz; real company/idea refresh, market cycle, isolated failed research/outage, discovery dry run, exact-commit Pages deployment; before/after evidence | Pending |

## M0 evidence

- Verified main baseline: `0ab7ec85bf10d55c6a26dcc95511f5c32716a48f`.
- Remote annotated backup: `pre-research-only-20261018`, tag object
  `2b39cd27d480125e15c68ecf979f401042c050bb`; resolves to the baseline.
- Existing 8,563 data deletions restored with explicit user authorization, then
  local main fast-forwarded by 59 commits. Clean before implementation.
- Legacy daily workflow disabled on GitHub. Source schedule removed and runtime
  unconditionally frozen. No runtime dispatch or site publication performed.
- Census: 8,227 data files, 218 CSVs, 1,295 wiki Markdown pages, 92 securities,
  83 assessments (82 expired), 366 sources; queue 648 = 340 blocked + 295 ready +
  13 waiting. Block reasons: 320 capacity, 15 agent, five unavailable dependency.
- Full read-only inventory exported outside repository:
  `/tmp/papertrader-pre-research-only-20261018.json`; regenerate from the tag using
  `python -m papertrader.migration_inventory`. Committed compact census and recovery
  procedure: [docs/migration/M0.md](docs/migration/M0.md).
- Chart baseline reproduced: 83 integrity errors; dry run changed zero data bytes.
  Cleanup removes only retired technical blocks, preserves 39 analytical charts
  and research frontmatter/dates, and is a no-op when repeated.
- October 15 actual mismatch operation/hash coordinates captured in
  `tests/fixtures/migration/assessment_page_ordering.json`; legacy ordering
  reproducer added. M4 owns eliminating the faulty write sequence.
- Last successful Pages run: [38771728304](https://github.com/Kabutojira/PaperTrader/actions/runs/38771728304),
  revision `6399463e7bfb91888da28a15ee4100a369a9a2df`. Public site remains there.
- Local gates: 50 focused tests and all 617 tests passed; Ruff lint/format, MyPy,
  strict schema/integrity/wiki/advice/reconciliation, Quartz check/build/link checks
  passed. Seeded complete publication integration: one passed with Quartz enabled.
  These are local/mock checks, not live market/research/deployment operations.
- Environment corrections: full pytest required workspace `--basetemp` to avoid
  `/tmp` fixture quota. Quartz subprocess staging must keep `TMPDIR=/tmp`; putting
  it under ignored `.cache` makes Quartz see zero input pages. No validation was
  relaxed and no source fix was needed for that invocation failure.
- Milestone commit/push and CI: pending.

## Acceptance tracking

AC-01 research-only entry points; AC-02 one current assessment and retained sources;
AC-03 session caching; AC-04 partial market failure; AC-05 <=3 daily/<=30 pending,
no duplicates/fan-out; AC-06 blocked/dependent backlog retired with useful goals
retained; AC-07 atomic safe agent writes; AC-08 honest consistent valuation and
mechanical repricing; AC-09 fresh per-issuer deterministic rankings; AC-10 independent
phases; AC-11 isolated credentials and untrusted-source handling; AC-12 coherent
clean-install code/docs/schema/tests/CI with obsolete product removed.

No acceptance criterion is marked complete merely because code exists. Record
exact tested commit SHA, local vs mocked vs live result, Actions URLs and remaining
blockers with each milestone. Preserve unrelated changes; never weaken evidence
or financial validation to satisfy retired tests.
