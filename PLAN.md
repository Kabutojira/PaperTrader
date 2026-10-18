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
| M1 | Repeatable dry-run-by-default compact schema migration; preserve identities, current meaning, prose/citations and expiry; schema/reference/wiki tests; no invented evidence | Complete:4e3f8223 tooling,87e7514c active cutover; CI green |
| M2 | Standalone market/cache/indicators/valuation/ratings core; sessions/holidays, bounded batching, per-symbol failure/corrections; no LLM or portfolio paths | Complete: 823efb96; CI 39146545315 green |
| M3 | One-entity bounded queue, deterministic priorities/retries, retire old producers; census-based disposition of all 340 blocks and 13 waiting relationships; <=30 tasks | Complete: 421332ff; CI 39147632827 green |
| M4 | Two single-model operations; bounded context/web/turn/runtime budgets; final staged Markdown and complete result validated before atomic CSV/wiki/source transaction; idempotent and rollback-safe | Complete: 87e7514c; CI 39151401843 green |
| M5 | Weekly bounded discovery/manual import and inline links; validate identity, dedupe issuers/share classes, retain citations/unresearched status; no fan-out | Complete: 94071e34; CI39152747505 green |
| M6 | Deterministic fresh Top 10 Buy/Sell, company/idea catalogs, recent updates and health; optional nonblocking charts; Quartz build and reviewed output/links | Complete:49d9f8b9; CI/Pages green |
| M7 | Independent market/research/Pages workflows, least credentials, compact writes and focused validation; live non-dry market/research smoke; isolate failure cases | Complete:67b650e9 +93f5a5b2; live market and supported execution/unsupported outcome; see evidence |
| M8 | Delete dead modules/CLI/schemas/skills/actions/tests and old data only after migration gates; rewrite actual-product docs/config/CI; prove no live references; report size reduction | Complete:913ff8b9; CI39159628088/Pages39159817503 green |
| M9 | Clean-checkout full schemas/source/link integrity/Ruff/MyPy/tests/Quartz; real company/idea refresh, market cycle, isolated failed research/outage, discovery dry run, exact-commit Pages deployment; before/after evidence | Complete:ac323009 runtime; CI39163037009, live company/idea/market and Pages evidence below |

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

## M4 evidence

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
  responses and do not represent live checks. Milestone commit
  `87e7514c12f550907109bdfd0e02a92fa4926f17` pushed;
  [CI39151401843](https://github.com/Kabutojira/PaperTrader/actions/runs/39151401843)
  passed on the exact final tree, including the complete suite and Quartz build.

## M5 evidence

- Added bounded research_idea discovery mode and manual candidate imports; source
  verification and independent yfinance listing identity checks precede creation.
  Defaults1 new idea/2 companies, weekly attempt cadence, web12 plus identity HTTP8.
- Issuer dedupe handles share classes; explicit import preserves distinct instrument
  IDs under the existing issuer. New sourced pages remain unresearched with no
  assessment dates, valuations or automatic queue tasks. Relationships are inline.
- Manual research selection now preserves an explicitly requested share class while
  deduping company tasks; conflicting distinct manual instrument goals are rejected
  explicitly. Company-level current review suppresses stale-sibling queue storms
  without changing the sibling's old valuation or freshness.
- Discovery keeps only its current status/last attempt under optional status.json;
  failed attempts do not mutate research or retry indefinitely. Dry run is default.
- Local gate passed: 66 discovery, queue, result and migration tests; Ruff lint/format,
  MyPy74, current-data validation and default discovery dry run passed. Dry run made
  zero model calls and changed no active data. Legal-form aliases and distinct
  issuer/share-class identities have explicit regression coverage.
- Commit `94071e34f6f2e25853170f3354d80856d73be802` pushed;
  [CI39152747505](https://github.com/Kabutojira/PaperTrader/actions/runs/39152747505)
  passed on the exact tree. No live model/provider invocation,
  real discovery candidate, active schedule or Pages deployment has occurred.
- Details: [M5 migration](docs/migration/M5.md).

## M6 evidence

- Deterministic Top 10 Buy/Sell, issuer dedupe, confidence-adjusted return,
  current source/price/assessment checks, completeness and explicit blocker checks.
- Generated concise homepage, company/idea catalogs, methodology and small exports.
  Initial rankings are empty, with82 stale assessments clearly counted.
- Quartz input includes current research and linked sources; retired navigation,
  portfolio exports, technical-series hydration and browser action/scaler script
  are absent. Retired referenced pages link to the verified backup ref.
- Local focused gate117 passed; final publication12 passed after source-path and
  generated-page overwrite regressions. Ruff/format, MyPy75 and current-data
  validation passed. Prior full suite711 passed/4 retired-contract failures;
  those four were repaired and covered by the117-test retest. Exact push CI
  must verify the final full tree before M7.
- Reviewed Quartz build:145 Markdown inputs,199 emitted files; TypeScript,
  four TS tests, Prettier, internal links and canonical Open Graph URLs passed.
  Homepage inspected: empty current Top10, accurate82-stale coverage, research
  navigation/downloads and no portfolio/signals/performance downloads.
- Commit `49d9f8b911b1ca0ba04cf056167bc6199e51e0c5` pushed;
  [CI39154597909](https://github.com/Kabutojira/PaperTrader/actions/runs/39154597909)
  passed the exact complete tree. Actual
  [Pages39154872413](https://github.com/Kabutojira/PaperTrader/actions/runs/39154872413)
  deployed that SHA successfully at2026-10-18T18:36:36Z. Public homepage, company
  catalog, idea catalog and rankings JSON each returned HTTP200; empty current
  rankings and research navigation were verified from public responses.

## M7 evidence

- Drafted independent market/research/Pages workflows, daily13:00 America/New_York
  using native GitHub timezone scheduling. Manual market runs do not implicitly
  invoke live research. Scheduled research follows market even on partial failure.
- Default three-operation budget includes weekly discovery; sequential short
  leases and independent phase exit codes/compact health. Closed repeats are no-op.
- Git write token is available only to the post-agent deterministic commit step;
  agent receives inference OAuth only. Runtime path allowlists and remote divergence
  checks precede one commit/push. Ephemeral three-day recovery artifacts preserve
  accepted work on conflicts; no new active research history is created.
- Pages receives the exact controller-committed SHA via a tiny artifact and builds
  without inference credentials; no-op content changes skip deployment. Old
  checkpoint/reporting workflows are removed.
- Local gate97 focused tests passed, followed by19 runtime/workflow checks after
  final allowlist/bootstrap/no-artifact hardening. Ruff/format, MyPy76, current
  validation, zero-call previews and diff checks passed; no active data changed.
  Commit `67b650e9ca27836f5d10b20477e7c7bbdc1b5742` pushed;
  [CI39155683073](https://github.com/Kabutojira/PaperTrader/actions/runs/39155683073)
  passed the exact full tree. Daily13:00 America/New_York schedule is active.
- Actual non-dry [market39155945162](https://github.com/Kabutojira/PaperTrader/actions/runs/39155945162)
  succeeded:13 provider calls,280 HTTP requests,0 failed tickers; one commit
  `e24dbc6de8f0c5ba8765f4fbf885070b6876327a`. Independent
  [Pages39156021647](https://github.com/Kabutojira/PaperTrader/actions/runs/39156021647)
  deployed that exact commit. Manual market did not start live research.
- Actual single Crocs [research39156247805](https://github.com/Kabutojira/PaperTrader/actions/runs/39156247805)
  failed validation withValueError/exit3. No valuation changed; retry/status-only
  commit `2732f9b56388a826130f9424f73c5828acd8edcd`. Pages independently skipped
  deployment because no publication inputs changed. This is a live failed check,
  not a successful valuation refresh.
- Bounded repair adds safe stage/type/project-location codes (no payload/message
  dumps), observed web usage and exact result-contract guidance. Explicit manual
  retry clears failed backoff while retaining attempt count/max2. No financial or
  source validation was weakened.61 affected tests, Ruff/format, MyPy76, current
  validation and diff passed; no active data changed. Final model-packet limits
  regression57 affected/50 final tests passed; configured freshness now reaches
  the model explicitly. The prior discarded result cannot reveal its exact reason.

- Repair1 commit `1b7a34a17fddc80cc1726ff913ab57df617579bb` passed
  [CI39157205413](https://github.com/Kabutojira/PaperTrader/actions/runs/39157205413).
  Actual Crocs retry [39157423259](https://github.com/Kabutojira/PaperTrader/actions/runs/39157423259)
  consumed attempt2/max2 and failed validation at timestamp parser line114;
  12 actual web requests, one model operation. No assessment changed. Commit
  `56ee81ea575d50c3f542106b541ba63a190a1701` records needs_attention; automatic
  scheduling skips it. Independent Pages39157656531 retained the prior site.
- Repair2 adds static field/category codes for model timestamp failures and
  explicit UTC-Z/source-publication-date guidance, keeping all date/freshness
  validation strict.68 affected/61 final tests, Ruff/format, MyPy76, current
  validation and diff passed. No source data or exhausted retry state changed.
  Repair2 push/CI and a different queued manual company (SoFi) live check pending.

- Repair2 commit `93f5a5b202efe84e686d8e9d4958610a17bab3fe` passed
  [CI39158112093](https://github.com/Kabutojira/PaperTrader/actions/runs/39158112093).
  Live SoFi [research39158371221](https://github.com/Kabutojira/PaperTrader/actions/runs/39158371221)
  succeeded with an honest not_supportable outcome, one model operation and10
  web requests. Current source/page/assessment/queue updates committed together
  as `580d16a9ee6dc3a6414cc4ebe41f396a2fa077b9`. No fair values were invented.
  Independent [Pages39158604453](https://github.com/Kabutojira/PaperTrader/actions/runs/39158604453)
  deployed that exact commit. M7's live execution/independence gate passed;
  M9 still requires a supported live company valuation and an idea update.

## M8 evidence

- Deleted unused trading/accounting/allocation/order, alert/classifier, history/
  governance, final-review, media/podcast/translation/TTS modules and skills.
  Supported runtime retains19 modules, with inventory/queue migration isolated
  from active CLI imports. Old migration is no longer a runtime CLI command.
- Current active data:249 files/5,201,146 bytes versus8,236/58,658,418 immediately
  before pruning;7,987 files removed. All92 instruments,29 ideas,47 relationships
  and83 current assessments retained with identical values. Current references
  retain318 source records;50 unreferenced records removed. Current queue28;
  zero legacy blocked/waiting dependency rows remain. Exact stats in
  docs/migration/m8-size.json; the verified pre-migration tag preserves history.
- Kept current sourced wiki closure and analytical ECharts; removed unused technical
  series renderer/schema/CSS, old exports, huge operation/run/report trees and
  obsolete tests. One-time chart cleanup and frontmatter/hash fixtures remain.
- Rewrote AGENTS/README/runbook/environment/configuration/dependencies to describe
  the actual product; focused mocked complete-cycle test covers supported valuation,
  invalid-result preservation, independent market repeat and current rankings.
- Locked installation succeeded with17 obsolete packages uninstalled. Full current
  suite146 passed in73s; Ruff/format, MyPy19, strict current validation, zero-call
  previews and import/reference audit passed. TypeScript/four TS tests/Prettier,
  Quartz145 Markdown/200 emitted files and internal links passed. Public outputs
  contain research navigation and no retired exports. No test/provider/model call
  was misreported as live. Exact push CI and reviewed M8 deployment pending.

- M8 commit `913ff8b98be8f4127ef6f8a34f0b0c1a57d3c58c` passed exact-tree
  [CI39159628088](https://github.com/Kabutojira/PaperTrader/actions/runs/39159628088)
  and reviewed [Pages39159817503](https://github.com/Kabutojira/PaperTrader/actions/runs/39159817503).
  Backup tag still resolves to0ab7ec85. A content-identical CSV index/EOL marker
  was cleared with update-index --refresh; Git diff was empty and values unchanged.

## M9 evidence

- Added artifact-only publication revision/build-date/deployment metadata, without
  granting Pages repository writes or creating a research/history table. Current
  market/research health appears on the homepage. Current company pages receive
  a derived status/rating/expiry banner; stale text cannot appear current when
  navigated to directly. These annotations do not change canonical research facts.
- Two primary NVIDIA release URLs were manually probed successfully (four bounded
  HTTP reads total); this is source-access verification, not a valuation/model run.
- Full local147 tests passed in69.5s; Ruff/format, MyPy19, strict current
  validation and diff passed. TypeScript/four TS tests/Prettier, actual Quartz
 145 Markdown/201 files and internal links passed, including exact-SHA artifact
  metadata and company freshness banner regressions.
- Exact clean-checkout CI, supported live valuation, idea update, closed-market
  repeat, discovery preview and final exact-commit Pages acceptance pending.

- Publication metadata commit `a2620d1495a879c6ecae43dcae846e8102a3a8fc` passed
  [CI39160351950](https://github.com/Kabutojira/PaperTrader/actions/runs/39160351950).
  Actual NVIDIA [research39160516606](https://github.com/Kabutojira/PaperTrader/actions/runs/39160516606)
  accepted a supported earnings-multiple valuation: one model operation,12 web
  requests; commit `fdc8c5afa7e6e35d80c530b049f70f69a64c2c4b`. Native USD
  bear/base/bull198/310.50/448, probabilities30/50/20; weighted304.25. Medium
  confidence and explicit forecast/filing limitations retained. One fresh Buy
  qualifies; no stale Sell padding. Actual independent
  [Pages39160767086](https://github.com/Kabutojira/PaperTrader/actions/runs/39160767086)
  deployed that exact commit.
- Actual idea [research39160893744](https://github.com/Kabutojira/PaperTrader/actions/runs/39160893744)
  failed citation validation after10 web requests; no accepted idea change.
  Retry/status commit `9acecc0ae77312d1fe9406d68421968618af2d61`; independent
  [Pages39161093626](https://github.com/Kabutojira/PaperTrader/actions/runs/39161093626)
  succeeded. The discarded response cannot distinguish the original compound
  missing-source/invalid-status/missing-page-URL branch. Bounded repair preserves
  citation provenance and static field diagnostics and makes the same strict
  contract explicit to the worker. Missing relationship-page URL atomic regression
  and69 affected tests, Ruff/format, MyPy19 and current validation passed. No
  source/evidence validation was weakened or retry count reset. Push/CI precedes
  the single remaining authorized idea attempt.

- Citation repair `3a63bab65f9f0f809c929e939b1fce013785d72e` passed
  [CI39161494875](https://github.com/Kabutojira/PaperTrader/actions/runs/39161494875).
  AI-compute idea final attempt [39161620066](https://github.com/Kabutojira/PaperTrader/actions/runs/39161620066)
  failed stable-source URL identity validation,11 web requests. It is now
  needs_attention, not reset/replayed; prior research remains intact. Compact
  state commit `002a268fd1e1ff8d0cb56f2286798cb785212714`; independent Pages39161860638 succeeded.
- Different existing defensive-consumer idea [39162062924](https://github.com/Kabutojira/PaperTrader/actions/runs/39162062924)
  updated successfully, one model operation/12 web requests; commit
  `3853e72ad921f9ab25f7a876f832528196a73c32`. Independent
  [Pages39162269997](https://github.com/Kabutojira/PaperTrader/actions/runs/39162269997)
  deployed that exact commit. Required live company and idea updates now passed.
- Closed-session market repeats [39162409315](https://github.com/Kabutojira/PaperTrader/actions/runs/39162409315)
  and [39162539432](https://github.com/Kabutojira/PaperTrader/actions/runs/39162539432)
  each made0 provider/HTTP requests and0 failed tickers. First filled two available
  queue slots. Second exposed a timestamp-only status commit caused by Git CSV
  CRLF conversion inside multiline cells; this was a failed no-commit acceptance
  check, despite zero network calls. CSV-only logical newline comparison now
  matches canonical reads, leaves non-CSV byte comparison exact and preserves real
  edits. A fresh-checkout multiline regression proves no data/status write, then
  proves a real text change still applies. Live no-commit repeat awaits push/CI.
- Final local gate:148 tests passed in61.8s (two dependency deprecation warnings),
  Ruff/format, MyPy19, strict data validation, zero-call market/research/discovery
  previews, Quartz check/build144 Markdown/200 files and links passed. Intentional
  invalid research, provider outage, Git conflict and Pages failure were injected
  local fixtures, not actual external outages. Discovery preview returned due=true,
  limits1 idea/2 companies/8 identity requests,0 model calls and no state mutation.

- Final runtime commit `ac3230095e34b2bf349648ced4733d8d73b1eec2` passed exact
  clean-checkout [CI39163037009](https://github.com/Kabutojira/PaperTrader/actions/runs/39163037009).
  Actual final [market39163162212](https://github.com/Kabutojira/PaperTrader/actions/runs/39163162212)
  succeeded in21s:0 provider/HTTP requests,0 failed tickers,changed=[],0 commits;
  local and remote HEAD remainedac323009. Independent Pages runs39163201128 and
  39163205197 skipped build/deploy for unchanged publication inputs.
- M9 acceptance report: [docs/migration/ACCEPTANCE.md](docs/migration/ACCEPTANCE.md),
  including AC01–12 evidence, exact revisions/run links, measured budgets/runtime,
  migration dispositions, before/after counts and explicit actual/injected checks.
  Public homepage/catalogs/company/idea/download/metadata links returnedHTTP200.
  Final report commit/CI and reviewed exact-commit Pages deployment are performed
  as the final delivery step; deployment metadata lives only in the site artifact.

## Watchlist coverage follow-up — 2026-10-18

User requirement: every watchlist stock should have research, a valuation and explicit
bear/base/bull cases. Baseline audit:92 instruments;9 missing assessments,13 unsupported,
70 with supported scenario values (some missing research detail). Only1 current
supported ranking qualifies; baseline coverage is separate from valuation freshness.

Implement coverage-first bounded scheduling, per-instrument gap tracking despite
issuer queue dedupe, visible homepage progress and catalog scenario values. Preserve
scenario/source validation, original dates and max3 scheduled operations/30 queued/
2 attempts; never generate unsupported values or reset exhausted entity attempts.
User explicitly authorized a faster one-time sequential backfill. Use repeated manual
cycles of at most3 operations, preserving the scheduled default and per-operation
budgets; no parallel research or unbounded agent cascade.

Validation/commit/CI/deployment and live backfill evidence will be recorded below.

- Coverage-first local gate passed:152 tests in71.6s, Ruff/format, MyPy19, strict
  data validation, Quartz check/build144 Markdown/200 files and internal links.
  One stale fixture was corrected without weakening dates; an obsolete sibling
  suppression test now proves one bounded uncovered-instrument task, no copied
  valuation and idempotent scheduling. Deterministic current-data update only
  reprioritizes the bounded queue and generates coverage/catalog views; assessment,
  source, research prose and financial facts remain unchanged.
- Baseline complete research22/92; gaps70 =9 missing +13 unsupported +48 missing
  research detail despite scenario values. Coverage-first priority75; material90,
  severe movement80 and explicit manual100 remain higher. Future queue refills
  retain targets outside the cap. Fresh unsupported results avoid daily retry loops.
- Faster backfill is explicit manual work, separate from normal daily3 operations.
  Supported and unsupported accepted outcomes, failed validation and exhausted
  needs_attention cases will be reported distinctly. Feature push/CI and reviewed
  publication precede actual sequential backfill operations.

- Feature commit `93966f977c8c41a86499b6ebb7e68d7ccb368b54` passed exact
  [CI39164471227](https://github.com/Kabutojira/PaperTrader/actions/runs/39164471227)
  and [Pages39164582344](https://github.com/Kabutojira/PaperTrader/actions/runs/39164582344).
  Published coverage22/92 and catalog cases verifiedHTTP200.
- Actual accelerated pilot [39164710193](https://github.com/Kabutojira/PaperTrader/actions/runs/39164710193)
  accepted MP Materials update with11 web requests; next two operation attempts
  failed before inference because the first Hermes process created profile
  directories that the shared-profile guard then rejected. One actual inference
  invocation, three budgeted operation attempts. Accepted/state commit
  `46a10c948a8d3614e2b0ffaa3c12d30868107131`; independent Pages39164945142 passed.
  Baseline complete count stayed22 because MP was already complete; current4,
  stale79. Prior research and failed attempt counts remain intact.
- Runtime repair uses a fresh temporary Hermes profile for each operation, copies
  only bounded valid inference auth/config and safely preserves token refreshes.
  Generated plugin/hook/memory directories are discarded; unmanaged external
  profiles, symlinks, malformed/oversized auth and Git/deployment credentials remain
  rejected. Sequential mock regression plus full160 tests70.7s, Ruff/format,
  MyPy19 and strict data validation passed. Live repaired pilot awaits push/CI.

- Profile fix `c635d1af9714d3bab3902b34fd44608297bb9fdf` passed exact
  [CI39165572235](https://github.com/Kabutojira/PaperTrader/actions/runs/39165572235).
  Repaired live pilot [39165699992](https://github.com/Kabutojira/PaperTrader/actions/runs/39165699992)
  ran all three inference operations,34 web requests: updated,not_supportable,
  retry_scheduled (source alias validation). Accepted/state commit
  `316a6e23444bd4ba25699dc34972b6cd1fa189b2`; Pages39166230122 succeeded.
  Complete22, incomplete47, missing9, unsupported14, current6/stale77.
- Source-identity repair preserves existing same-URL legacy aliases when updating
  their unchanged stable ID/URL/license, while still rejecting genuinely new IDs
  for a known URL. Broker-only bounded identity index exposes no source prose or
  credentials and stays outside model context; each opened source supplies its
  exact registered ID/URL/license or deterministic new link_only ID. Current index
  315 unique URLs/about48.7KB, cap5000 rows/1MB. No citation/evidence math weakened.
  Full163 tests60.6s, Ruff/format, MyPy19 and strict current validation passed;
  source-index, alias-preservation/new-duplicate rejection and request-budget
  regressions included. Live continuation awaits push/CI.
