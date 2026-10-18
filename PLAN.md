# PaperTrader research-only migration

The product is autonomous public-company discovery, investment research and
valuation. This plan, supplied on 2026-10-18, supersedes the retired trading and
research-governance plans preserved in the pre-migration Git ref. Implement one
milestone at a time; validate, commit, push and inspect CI before advancing.

**Schedule update from the user:** launch the research-only daily task at
13:00 Eastern, expressed as `0 13 * * *` with IANA timezone
`America/New_York`. This replaces the former daily time and follows daylight
saving time. Keep the retired trading scheduler frozen; activate this schedule
with the new independent workflows at M7.

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

- Replacement daily research schedule: **13:00 ET (`America/New_York`)** every
  day, three hours before the regular 16:00 ET US market close. M7 must use
  `cron: '0 13 * * *'` with `timezone: America/New_York` so daylight saving is
  automatic. Preserve the legacy workflow freeze until the replacement is ready.
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
| M0 | Freeze scheduler, verified backup, exact inventory, reproduce/repair retired technical charts, capture assessment/frontmatter ordering failure; dry run changes no source data | Complete: 9056d3df; CI 39142564182 green |
| M1 | Repeatable dry-run-by-default compact schema migration; preserve identities, current meaning, prose/citations and expiry; schema/reference/wiki tests; no invented evidence | Staged tooling gate passed: 4e3f8223; CI green; active cutover M4 |
| M2 | Standalone market/cache/indicators/valuation/ratings core; sessions/holidays, bounded batching, per-symbol failure/corrections; no LLM or portfolio paths | Complete: 823efb96; CI 39146545315 green |
| M3 | One-entity bounded queue, deterministic priorities/retries, retire old producers; census-based disposition of all 340 blocks and 13 waiting relationships; <=30 tasks | Complete: 421332ff; CI 39147632827 green |
| M4 | Two single-model operations; bounded context/web/turn/runtime budgets; final staged Markdown and complete result validated before atomic CSV/wiki/source transaction; idempotent and rollback-safe | Local gate passed; push/CI pending |
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
- Milestone commit: `9056d3dff03740a6c3310e086a240186bca4527a`, pushed to main.
- CI: [39142564182](https://github.com/Kabutojira/PaperTrader/actions/runs/39142564182)
  completed successfully at that exact SHA. M0 gate complete. No live inference,
  market refresh or deployment was performed. M1 is next.

## Acceptance tracking

Schedule update (2026-10-18): recorded the user-requested 13:00 ET replacement
target; legacy scheduling and runtime remain disabled during migration.

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

## M1 evidence (in progress)

- New compact contracts and independent validator implemented; default migration
  is read-only against a pinned Git revision. Explicit staged output is atomic and
  repeatable. Active data/reader switch is deferred until M4's transaction path;
  the old scheduler remains frozen, with no half-migrated publication.
- Staging input: M0 commit `9056d3dff03740a6c3310e086a240186bca4527a`.
- Staged at `/tmp/papertrader-research-m1-stage`: 92 securities, 29 ideas, 47 links,
  83 assessments, 366 sources, empty new queue. 71 historical supported valuations,
  12 unsupported; 82 expired and zero fresh supported valuations on October18.
- Identity, scenario, date, source-reference, unsafe-path, duplicate-row and
  share-class tests added. Local gates passed: ten focused tests, 626 full-suite
  tests, Ruff check/format, MyPy (64 source files), and all strict legacy state
  gates. Active data remains unchanged. M0 Quartz build/link evidence remains
  applicable because no active site input changed. Milestone commit
  `4e3f822365465fe7de24efb94901beff74466e5d` pushed to main; CI
  [39144296402](https://github.com/Kabutojira/PaperTrader/actions/runs/39144296402)
  completed successfully. Active schema cutover remains M4.
- Details: [M1 migration](docs/migration/M1.md).

## M2 evidence (in progress)

- Independent market/repricing modules and versioned request/model defaults in
  `research.ini`; no trading/account/FX imports. Active reader still frozen.
- Session cache, small sequential batches, failed-symbol retries, HTTP/provider/
  runtime caps, correction windows, per-symbol corporate-action reconciliation,
  compact features and native-price research opinions implemented.
- Tests cover closed-session no-op, holiday/exchange differences, partial failure,
  correction, split, request budgets and pure unchanged-fact repricing.
- Local gates: 22 focused tests and all 648 tests passed; Ruff check/format,
  MyPy (66 source files), and strict schema/integrity/wiki/advice/reconciliation
  passed. Active data and publication inputs remain unchanged. No live Yahoo
  request performed; metadata/HTTP behavior is mocked and budgeted, not measured
  live. Milestone commit `823efb96fe670f36b47abca36addf32c3109b4a2` pushed;
  [CI 39146545315](https://github.com/Kabutojira/PaperTrader/actions/runs/39146545315)
  passed, including the seeded publication cycle and Quartz build.
- User's new daily time recorded in `research.ini`: 13:00 America/New_York,
  daylight-saving aware. It becomes active at workflow cutover; legacy runtime
  remains disabled.

## M3 evidence (in progress)

- Replacement company/idea queue and deterministic attention producer implemented;
  issuer dedupe preserves instrument identities, merged reasons are idempotent,
  capacity admits no blocked rows, and manual requests displace automatic backlog.
- Short self-expiring sequential lease, six-hour bounded retry, completion removal,
  and exhausted entity needs_attention preserve the last accepted research.
- Real pinned census: all 648 legacy rows accounted for; 320 capacity blocks never
  replayed; 15 agent-result and five dependency blocks counted without preserving
  their old tasks; 89 relationship rows become optional inline work, including all
  13 waiting rows. Three current manual companies retained; new queue capped at30.
- Local verification: 43 relevant research/queue/migration/inventory tests passed;
  Ruff check/format and MyPy (67 files) passed; strict legacy schema, integrity,
  advice, wiki and reconciliation gates passed. Read-only CLI produced the verified
  census and no changes under data/. Full legacy suite deferred to push-triggered
  CI because active data, site and consumers remain unchanged.
- Two regression fixes: normalize detailed error suffixes into canonical blocked
  reasons, and recognize the 83 existing watching-status companies. No evidence
  validation or expected baseline count was relaxed.
- Active reader switch remains M4 and workflow activation M7. Old producer/queue
  code is frozen until deletion at M8. No live LLM/provider call or deployment.
- Details: [M3 migration](docs/migration/M3.md). Commit `421332ffe0a1af67e2febba9541e19fd6ca4ecb1` pushed;
  [CI39147632827](https://github.com/Kabutojira/PaperTrader/actions/runs/39147632827)
  completed successfully, including the complete legacy suite and Quartz build.

## M4 evidence (in progress)

- Added two staged operations, one model configuration and a small bounded
  read-only web broker. The worker receives inference OAuth only; Git/deployment
  tokens are absent from its environment and no shell/file tools are exposed.
- Complete result validation checks target identity, final frontmatter, current
  fetched citations, numerical scenarios, source dates, freshness, safe paths and
  optional charts. No immutable assessment/page hash or research history writes.
- Recoverable logical transaction stages Markdown before CSVs; one ignored
  temporary rollback journal supports exception and restart recovery. The cycle
  continues unrelated tasks after failure, with at most three attempts per day.
- First local gate: 61 relevant tests passed, Ruff check/format and MyPy73 passed.
  These were mocked tests; no live model/research provider invocation occurred.
- Canonical compact schema cut over from pinned M0 revision9056d3df: 92 security
  identities, 29 ideas, 47 relationships, 83 latest assessments, 366 current source
  records and 30 new entity tasks. All historical fair values/dates remain as
  migrated; no assessment was made fresh. All1307 wiki assets preserved; one page
  has obsolete assessment-ID tokens replaced by backup-ref links. Seven active
  files changed. Repeating the exact migration changed zero files; validation
  passed. Migration refuses to overwrite subsequent current research.
- Supported CLI now routes to research-only commands. CI uses current research
  contracts instead of retired portfolio/advice/reconciliation gates. Legacy
  modules, old tables and fixture tests remain only until M8 deletion. Their
  workflow is frozen and the public site has not been republished.
- Post-cutover gate passed: 94 focused checks and all686 repository tests;
  Ruff lint/format, MyPy73, current-data validation, research-only CLI help and
  diff checks passed. Quartz check/build/link validation passed with1292 Markdown
  inputs. Six legacy audit fixtures now explicitly use the retired internal
  fixture CLI; one purely retired allocation-readiness test was removed. No old
  commands were restored to the supported entry point.
- Hardening regressions cover current citation metadata refresh and URL identity,
  immutable trusted license metadata, copied-source rejection, semantic validation
  before model/queue writes, an isolated five-module worker bundle and configured
  UID/GID10000 with no supplementary groups, exact manual entity selection, and
  actual retired-chart markers without rejecting innocent prose mentions.
- Final serialization correction normalizes logical CRLF/CR/LF in CSV values;
  a pinned migration regression simulates Git checkout conversion inside quoted
  prose. After this correction49 affected tests, Ruff/format, MyPy73, current CLI
  validation and migration preview passed. The686-test full gate predates only
  this covered newline correction; push CI will run the entire final tree.
- Hermes integration/OS identity, live research network availability and deployment
  remain to be verified live in M7/M9. Current checks use mocked worker/network
  responses and do not represent live checks. Commit/push/CI pending.
