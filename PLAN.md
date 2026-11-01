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

- Source identity fix `7361375aa6a4aff3ec3bf1ca3701c52b9929ac11` passed exact
  [CI39166889532](https://github.com/Kabutojira/PaperTrader/actions/runs/39166889532).
  Bulk cycle [39167105129](https://github.com/Kabutojira/PaperTrader/actions/runs/39167105129)
  ran3 operations/32 web requests: DDD validation retry, Twist unsupported,
  Arista supported update; commit `e9d8acd2729b9b9e27032d4030d4182f4967b28c`,
  independent Pages39167580075 passed. Market refill39167686187 made0 requests.
  Next [39167856012](https://github.com/Kabutojira/PaperTrader/actions/runs/39167856012)
  ran3/36: RocketLab and Ginkgo validation retries for missing narrative fields,
  CrowdStrike unsupported due source access; commit
  `121ec98a628c103d2c65af1f691e6d0c568c9209`, Pages39168270304 passed.
  Coverage remains22 complete,45 incomplete,9 missing,16 unsupported; current9.
- Final contract/diagnostic repair keeps required explanations nonempty even for
  unsupported conclusions, with explicit unknowns and no invented scenario numbers.
  Static codes identify missing fields and invalid source metadata. Broker errors
  distinguish numeric HTTP status, PDF unsupported, empty/oversized content and
  request-budget exhaustion without response bodies or secrets. Primary evidence
  is preferred; trustworthy attributed secondary reporting may fill identified
  gaps with explicit limitations, matching the product source policy. Generic
  homepages and unverified prior figures are not financial evidence.
  Full180 tests74.4s, Ruff/format, MyPy19 and current validation passed; no request
  limit or financial/evidence validation was weakened. Push/CI precedes resuming
  the one-time backfill; remaining individual failures use bounded retries.

- Contract/diagnostic commit `b8c890a83fb2f73e077dfea482ac83ddadc285e9` passed
  [CI39168835285](https://github.com/Kabutojira/PaperTrader/actions/runs/39168835285).
  Live [39169015991](https://github.com/Kabutojira/PaperTrader/actions/runs/39169015991)
  ran3/33 web requests: Planet unsupported, LUNR skip_as_stale, Fluence no_change;
  commit `ec11e2297f2189a738d57eb318c959f6258cfc12`, Pages39169370606 passed.
  Coverage22 complete/44 incomplete/9 missing/17 unsupported, current10/stale73.
  Accepted unchanged/unsupported results are not counted as completed valuations.
- Source-access diagnosis: public RSS search returned unrelated results for exact
  company/financial queries; native source lookup found direct issuer releases
  that the broker could open. Ten bounded diagnostic HTTP reads tested this; a
  separate12-request source-lead qualification opened7 issuer links for6 of the9
  never-assessed instruments, with5 explicit HTTP failures. Native source URL
  lookup used18 search queries; these manual intake/engineering requests are
  separate from Hermes operation counters. No valuations were inferred in intake.
  Only current URL/title/publisher/hash/check-time/issuer metadata was registered;
  no raw article, financial fact, scenario, assessment or research prose changed.
- First-pass context now supplies canonical target_page for an empty prior page,
  explicit missing valuation/research fields, compact queue reasons and recently
  checked source leads within the12-source cap. Financial excerpts omit large
  navigation/header/footer blocks while retaining20 bounded IR/source locators;
  source/model/request/content ceilings remain unchanged. Locator links and search
  results are not citation evidence until opened. A stale company review now uses
  the existing7-day review cooldown without changing assessment dates or numbers,
  preventing immediate stale-trigger replay.
  Full183 tests63s, Ruff/format, MyPy19 and strict current validation passed.
  Targeted first-time company verification follows exact push/CI.
- Issuer-source/context commit `1d0195542b0148e210af6b3f19dcb52b9d108df8`
  passed [CI39170579526](https://github.com/Kabutojira/PaperTrader/actions/runs/39170579526).
  Targeted Stratasys [39170697396](https://github.com/Kabutojira/PaperTrader/actions/runs/39170697396)
  attempted1 model operation/12 web requests; validation rejected an unresolved
  assessment source reference (`assessment.source_ids.missing`, prepare_result383).
  No valuation/page was accepted. Retry state commit
  `a03fc96a77f6c3ae7f62fc86ffb74bfd7fafb597`, Pages39170965264 succeeded.
  This does not establish that valuation is unsupported. Clarified the result
  instructions: reference lists use exact source IDs joined by pipes, and every
  token must match a supplied source row or existing context source. Existing
  evidence validation and the two-attempt ceiling remain unchanged.
- Source-format clarification `6dd807981e4a1922d01dd7e5c58ebc89f736f6fc`
  initially failed CI39171140306 on one stale prompt-text assertion (182 passed).
  Mechanical correction `41c152e15567f6165d5583f980090dab9d33bb77` passed
  [CI39171287075](https://github.com/Kabutojira/PaperTrader/actions/runs/39171287075).
- Actual Stratasys second attempt [39171413149](https://github.com/Kabutojira/PaperTrader/actions/runs/39171413149)
  used1 model operation/9 web requests. Source-reference checks passed, but global
  candidate validation rejected the result; no valuation was accepted. Exhaustion
  exposed a separate persistence bug: an unassessed needs_attention company with
  no page made state invalid. Commit-runtime refused that state (exit4); automatic
  Pages39171630508 retained the prior site and skipped build/deployment.
- Repair permits a blank page only for unassessed unresearched/needs_attention
  securities; assessed/researched companies still require valid pages. Added safe
  static global page/assessment diagnostics and explicit model confidence/status
  enum instructions. Full186 tests78s, Ruff/format, MyPy19 and strict validation
  passed. Regression proves exhausted failure persists, prior research survives,
  unrelated review continues and publication remains valid.
- Recovered the already-observed second attempt through admit/claim/finish and
  atomic controller writes: zero new model/web calls, queue item removed, Stratasys
  needs_attention, all83 assessments unchanged. This records the spent attempt;
  no retry reset. Regenerated views:22 complete/44 incomplete/9 missing/17
  unsupported,2 needs_attention. Reviewed Quartz build143 Markdown/198 outputs
  and link check passed; push/CI precedes deployment and further company reviews.
- Failure-state repair/recovery `7335525bb496c5436fb3bc5e6da7b46f707d998d`
  passed [CI39172215125](https://github.com/Kabutojira/PaperTrader/actions/runs/39172215125)
  and reviewed Pages39172344053; public catalogs/metadata returned200.
- Actual first-time BASF [39172450504](https://github.com/Kabutojira/PaperTrader/actions/runs/39172450504)
  accepted supported scenarios (1 model/9 web), commit
  `43c0747d67b6d5768bcafd2938a3eebd24f8dada`, Pages39172711091 passed.
  Coverage increased22->23 complete. Actual first-time Arkema
  [39172856987](https://github.com/Kabutojira/PaperTrader/actions/runs/39172856987)
  accepted supported scenarios (1 model/11 web), commit
  `29d51ffb057cd734d43dd23b2eddd5b1bdb061c7`, Pages39173070262 passed.
  Coverage increased23->24; the canonical extensionless research link returned200.
- Actual Evonik [39173152265](https://github.com/Kabutojira/PaperTrader/actions/runs/39173152265)
  failed the existing copied-source-text guard (1 model/11 web); bounded retry
  retained, commit `e54bb78292d86e34a9704de8add6f5046f65f01c`, Pages39173400602
  passed. No evidence or copyright check was relaxed.
- Actual Lemonade [39173497599](https://github.com/Kabutojira/PaperTrader/actions/runs/39173497599)
  accepted explicitly unsupported research (1 model/12 web), commit
  `3c05e5f0d978cbf1e015392ce28ded322ce19b04`, Pages39173702552 triggered.
  Its stated blocker was inaccessible PDF-only shareholder letter/10-Q, not a
  demonstrated absence of public financial evidence. Coverage24 complete/44
  incomplete/6 missing/18 unsupported;86 current assessment records.
- Added bounded primary-PDF reading using pinned pypdf6.21.1, verified against
  official security documentation and PyPI. The isolated worker stages only that
  pure-Python package alongside its existing allowlist, never full site-packages.
  At most3 pages/window,250 pages/file,2MB response,1MB decoded stream,4MB decode
  work,2000 root-recovery objects; no OCR, decryption, images, attachments, scripts
  or external PDF renderer. Later page reads consume the existing12-request cap;
  600s/24-turn limits remain unchanged. PDF positioning whitespace is compacted
  while retaining rows/column separators. Every seen window remains available to
  the existing copy guard; the model receives only one12k-character excerpt.
- Six actual engineering HTTP reads successfully opened the35-page Lemonade
  letter and53-page10-Q, including later statement pages. Native lookup used2
  search queries plus3 page opens and3 link opens (official docs and issuer PDFs).
  Only2 verified source metadata leads were added; no raw PDF/text, financial
  fact, valuation or assessment changed. These requests are separate from Hermes
  operation counters. Full194 tests77.2s, focused99, Ruff/format, MyPy19, strict
  current validation and diff check passed. Push/CI precedes model-backed retry.
- PDF feature `34869bdc2c02116bb30ed3e7bd4c861725df1491` passed
  [CI39174340576](https://github.com/Kabutojira/PaperTrader/actions/runs/39174340576).
  Actual PDF-backed Lemonade re-review
  [39174468118](https://github.com/Kabutojira/PaperTrader/actions/runs/39174468118)
  accepted supported bear/base/bull scenarios (1 model/12 web), using both issuer
  PDFs; commit `3aaf62d864063dcee43bd4ee647c7ba75f7d2eb3`, Pages39174714383
  passed, canonical research link/metadata returned200. Coverage25/92 complete,
  86 assessed,13 current. This live result resolved the demonstrated PDF-access
  blocker without changing any evidence or numerical validation.
- Next missing-company source qualification used7 bounded HTTP requests: issuer
  Materialise financial release, Agronomics issuer-authored RNS via Investegate,
  ECB reference PDF and Protolabs distributed release opened successfully;
  Protolabs issuer/SEC PDFs returned403 and its distributed release returned503
  before one successful bounded retry. No bypass or
  whole-pass retry. Native lookup used7 queries (three company, two Protolabs,
  one ECB, one newer Agronomics NAV) plus explicit issuer/document link lookup;
  no unrelated search hit was accepted as evidence. Only4 current metadata leads
  registered, zero assessment/value changes. ECB is relevant solely to the
  Materialise EUR-reporting/USD-instrument valuation conversion; no portfolio FX
  process, rate cache or exposure table was created. Strict validation passed.
- Source intake `2d7559a228d92bc16b13fc8249e9b6f1a205fe8b` passed CI39175050377.
  Four actual sequential company reviews accepted supported bear/base/bull cases:
  DDD39175166326 (1 model/11 web), commit e78cd7d0801d256683685e9743c87b53ff36cb95,
  Pages39175406039; MTLS39175506251 (1/11), commit
  7d121112af596b5e2f4c329be9ec20f73190e293, Pages39175726598;
  PRLB39175811333 (1/12), commit 4aee401352f735ec9c5f0e50173d2eca2aaae33d,
  Pages39176024781; ANIC39176118344 (1/12), commit
  c1add9543e2d319d0e188ba7a5418436d80c2c80, Pages39176371037.
  All four Pages deployments succeeded and canonical research URLs returned200.
  Total4 actual model operations/46 web requests; coverage25->29 complete,
  90 assessed/17 current. Default scheduled limit remains3 operations.
- Historical narrative recovery: dry-run-by-default manual migration fills only
  missing downside/catalyst/invalidation fields from explicit, unambiguous text in
  the same company's same-date current page, with all existing assessment source
  references present. Ambiguity, page-date/identity/source mismatch, current or
  unsupported assessments are refused. No model, external request or new valuation.
  Reviewed33 records applied atomically; coverage29->62 complete,44->11 incomplete,
  17 unsupported and2 missing unchanged. All original fair values, probabilities,
  methods, confidence, assessed/expiry dates, citations, pages and queue unchanged.
  Current17/stale73 and exact Buy/Sell ranking rows unchanged; historical research
  remains expired. Repeated apply made no changes. Full196 tests, targeted89,
  Ruff/format/MyPy19 and strict validation passed before apply. Final data/site
  checks, exact commit, CI and reviewed deployment evidence follow after push.
- Narrative recovery `8f92b50d9b9cd1daf8b6591a7c90a7ad2c22c633` passed
  [CI39177542295](https://github.com/Kabutojira/PaperTrader/actions/runs/39177542295).
  Reviewed Quartz150 Markdown/205 outputs and internal links passed; actual
  Pages39177645476 succeeded, public homepage/catalog/metadata returned200 and
  exact revision matched. Baseline coverage62/92, current17, stale73.
- Actual remaining Evonik retry
  [39177725559](https://github.com/Kabutojira/PaperTrader/actions/runs/39177725559)
  accepted supported EUR scenarios (1 model/12 web), commit
  51138d32c302b87554df4d79cf9dd829698c765a; automatic Pages39177975040 triggered.
  Coverage63 complete,11 incomplete,17 unsupported,1 missing;91 assessed/18 current.
  No attempt counter reset or copied-source-text validation exception.
- Twelve bounded engineering broker requests across two source-qualification
  passes opened direct Planet, Nomad Foods and Eaton financial releases plus a
  PayPal navigation locator. Six endpoint attempts failed (timeout/403); the request total includes redirects;
  only the3 financial-release metadata leads were registered. No raw source text,
  financial facts, scenarios or assessments changed during intake. These calls are
  separate from model operation counters. Native lookup used8 queries,2 page
  opens and2 document-link opens to identify issuer endpoints; search snippets
  and navigation were not treated as financial evidence. Strict validation follows.
- Qualified-source intake `2e26b56d559b8b7ab93da6f550f6a52a61903ef0` passed
  CI39178034524. Evonik Pages39177975040 succeeded; canonical research page and
  publication metadata returned200 with exact51138d32 revision.
- Actual Planet re-review39178154636 accepted supported USD bear/base/bull cases
  (1 model/12 web), commit03669deb5e5fa9159d766e9199e9524c9731fc9f;
  Pages39178369524 triggered. Coverage64 complete/11 incomplete/16 unsupported/
  1 missing;91 assessed/18 current. Direct issuer financial evidence resolved its
  earlier retrieval blocker without weakening valuation validation.
- Seven engineering broker requests qualified a Nebius issuer financial PDF and
  issuer-authored SoFi release distributed by Business Wire/FinancialContent.
  Twist/CrowdStrike issuer and Business Wire endpoints and Nasdaq returned403 or
  timed out (5 failed attempts). Only2 verified source metadata records added,
  no source text or financial/assessment changes. Native source lookup used7
  queries,3 page opens and2 document-link opens; unrelated proxy/search hits were
  rejected. Existing per-operation source/time/turn limits remain unchanged.
- Source intake a20280efa1aca17039c03b3bd999dda2abdead32 passed
  [CI39178452137](https://github.com/Kabutojira/PaperTrader/actions/runs/39178452137).
  Planet Pages39178369524 succeeded; exact03669deb metadata and canonical page200.
- Actual sequential refreshes: Nomad39178555848 accepted supported cases
  (1 model/11 web), commitac1a53113266ed3876179e9b519e80b6f4e8166f,
  Pages39178797169 succeeded and exact metadata/canonical page200; Eaton39178914303
  accepted supported cases (1/10), commit5e400a7b62e710ef35ed5340d09f4c807fbfd064,
  Pages39179196670 succeeded; Nebius39179216761 accepted supported cases (1/12),
  commitfb155701b95f29189219e9aa3544e909c8741078, Pages39179517327 triggered.
  Three actual model operations/33 web requests; coverage64->67 complete,
  9 incomplete/15 unsupported/1 missing,91 assessed/20 current. Nebius has low
  confidence and remains ineligible for current Buy/Sell rankings.
- Next source qualification used16 broker HTTP requests across bounded passes:
  8 usable financial documents/releases (including2 already registered),1 unusable
  MercadoLibre redirect shell,7 denied endpoints. The embedded issuer document
  locator resolved to MercadoLibre's actual19-page shareholder letter; Rio Tinto's
  74-page results also opened within the existing PDF limits. Six new metadata-only
  references added for MercadoLibre, Atkore(two), AbCellera, Fiserv and RTX. Rio and
  Prosus existing references preserved. No raw content, financial fact, assessment,
  page or queue was modified during intake. ASML/SQM/TI/Recursion/Enphase denied
  endpoints were not registered as verified evidence. Native lookups covered
  issuer and issuer-distributed releases; unrelated proxy hits were rejected.
  Strict validation passed. Research proceeds sequentially; Pages remains an
  independently recoverable phase and does not gate another accepted review.
- Source intake `9f1dcf1330482445076442284eab5d534c814967` passed
  CI39179605492. Subsequent actual sequential reviews:

  | Company | Research run | Model/web | Accepted revision | Pages run |
  | --- | --- | --- | --- | --- |
  | SoFi | 39179710741 | 1/12 | eed5e6f2ce0146aae54fdf1af2b3c81be949a1c4 | 39179983548 |
  | MercadoLibre | 39180065252 | 1/9 | f2b40eb5fbb33e633ef2f43745c9d5cab9c5da25 | 39180290554 |
  | Rio Tinto | 39180326233 | 1/11 | 54045d2be07ae1eda3e5a7a3a56cb5cbb1d33b7f | 39180594056 |
  | Prosus | 39180612820 | 1/10 | 05106d46f58447739e895cbf12501c01600fda94 | 39180871603 |
  | Atkore | 39180931175 | 1/11 | 4a7c50a92e2c2d9ab504f94ea619be710c963339 | 39181202538 |
  | RTX | 39181257576 | 1/10 | 237605c7ee8d1fa2fd889c3931eb9fe86cc95fb8 | 39181495165 |
  | Fiserv | 39181600317 | 1/11 | 717f616e0af9a468f581be5ccf31785b157586fa | 39181873301 |
  | AbCellera | 39181902603 | 1/12 | 1dc3df3d5160fe4e34865f952688ec58fabb08a5 | 39182142499 |

  All eight research runs and listed independent Pages deployments succeeded.
  Seven accepted complete supported cases; AbCellera remains honestly unsupported
  because the risk-adjusted pipeline/commercial assumptions are insufficient.
  No numerical, evidence or copied-text gate was relaxed. Eight actual model
  operations/86 web requests. Coverage67->74 complete,4 incomplete,13 unsupported,
  1 missing;91 assessed/27 current/64 stale. SoFi and Nebius low-confidence cases
  remain excluded from current Buy/Sell rankings. Freshness counts use the actual
  committed snapshots: replacing already-current unsupported research improves
  completeness without adding another current record.
- Next bounded intake registered7 metadata-only financial references:6 issuer
  releases (some publicly redistributed),1 secondary S&P Capital IQ summary for
  Twist, explicitly labeled financial_reporting. Nine engineering broker requests
  yielded7 usable opens; LUNR403 and an oversized CrowdStrike endpoint were
  refused. A different public CrowdStrike release endpoint opened within existing
  limits. No source text or scenarios were imported. Native document lookups
  supplied locators; unrelated SQM search results were discarded. Existing ECB
  reference linked to ASML only for an explicit EUR-reporting/USD valuation bridge;
  no FX subsystem or portfolio process was added.
- Seven explicit user-requested coverage goals merged/admitted with preserved
  attempts into26 queue rows (cap30): PYPL, ISRG, TXN, ASML, LAC, CRWD, TWST.
  No other manual request was displaced. Controller validation confirms all
  assessments, values, dates, current citations, research pages and market state
  unchanged. Preview selection is PYPL/ISRG/TWST; execute through the existing
  three-operation sequential cycle, discovery disabled. Scheduled defaults remain
  unchanged. Strict validation and exact CI evidence follow before live dispatch.
- Verified coverage intake `ff839ec6f4b64de7c3791f5100e0e962ad2ac7bc` passed
  [CI39182376493](https://github.com/Kabutojira/PaperTrader/actions/runs/39182376493).
  Actual max-three queue cycle
  [39182554342](https://github.com/Kabutojira/PaperTrader/actions/runs/39182554342)
  completed3 sequential model operations/25 web requests. PayPal and Intuitive
  Surgical accepted complete supported USD scenarios; Twist remains unsupported.
  Accepted revision `8ea1792d9674fe70a0800c79882115fec2b95610`, independent
  Pages39183041860 triggered. Coverage76/92 complete,2 incomplete,13 unsupported,
  1 missing;91 assessed/29 current/62 stale. Discovery disabled, scheduled defaults
  and all evidence/numerical gates unchanged.
- Final source-qualification pass used19 bounded engineering broker requests
  across company-specific passes:11 usable opens and8 refused responses
  (access/timeout, excessive size, encrypted or unextractable PDF). Registered10
  new metadata-only references and retained Stratasys's existing source identity.
  Usable issuer financial evidence covers Sigma Lithium, Yaskawa, Intuitive
  Machines, Recursion (including October financing/clinical updates), SQM,
  Samsung, Enphase and Stratasys. Nidec's usable source is only its current audit
  disclosure index; its encrypted financial PDFs remain unavailable to the broker.
  Native search/document-link lookups identified public originals or attributed
  issuer redistributions; snippets were not imported as facts. No raw source text,
  financial values, dates, pages or current assessment citations changed.
- Nine explicit coverage requests merged/admitted, retaining every pre-existing
  attempt count;28 queue rows/13 manual tasks, no evictions. Samsung common's
  remaining attempt is preserved; preferred GDR remains a separate instrument and
  waits until the common request finishes. ECB reference links are solely optional
  explicit native-currency valuation bridges, with no market FX subsystem.
  Stratasys gets a new bounded manual review after the documented source-identity,
  diagnostics and result-contract repairs and a fresh successful issuer financial
  source open. Its two earlier failed attempts remain recorded in Git; no existing
  queue counter or needs_attention flag was reset, no automatic replay was enabled.
  This renewed manual work is limited to the normal per-task attempt budget.
- Presentation-only precision repair separates money from percentage formatting:
  subunit prices/fair values retain useful decimals instead of rounding to zero or
  materially distorting displayed comparisons. All stored financial values and
  rating/return calculations remain unchanged. Full202 tests,20 focused publication
  tests, Ruff/format/MyPy/strict validation and diff checks passed. Deterministic
  publication changed only homepage and security catalog Markdown. Reviewed Quartz
  build148 pages/205 files and internal link checks passed; actual ANIC.L row shows
  GBP0.0446 price,0.0710/0.0800 weighted/base fair value,59.19%/41.43% returns.
  Exact commit/CI/deployment evidence follows after push; no live check is inferred
  from these local tests.
- Precision/source-intake revision `07b7008b8a42a01fcdf4bbe2af91eb0482ba6300`
  passed [CI39183479096](https://github.com/Kabutojira/PaperTrader/actions/runs/39183479096).
  Reviewed exact-revision Pages39183585182 succeeded; public metadata/homepage
  returned200 and displayed ANIC0.0446/0.0710. Prior Pages39183041860 also succeeded.
- Actual queue cycle39183589551 accepted current unsupported reviews for Samsung
  common GDR, Recursion and Nidec:3 model operations/29 web requests, revision
  `9cb8ca52924c45f3081c31e20e674d94e4e40a2a`, Pages39184313559 succeeded.
  Coverage remains76 complete;91 assessed/32 current/59 stale. These are valid
  research outcomes, not invented valuations or failed task retries. Missing GDR
  entitlement/venue evidence, uncertain clinical cash flows and unreliable corrected
  financial inputs remain explicit limitations.
- Actual queue cycle39184455494 accepted complete supported cases for Texas
  Instruments (medium confidence) and CrowdStrike (low confidence), while Sigma
  Lithium remains unsupported. Three model operations/27 web requests, revision
  `a83d18b34af8273412562c2ccd5ad2f77b1a25c7`, Pages39185006506 triggered.
  Coverage78 complete/1 incomplete/12 unsupported/1 missing;91 assessed/34 current/
  57 stale. CrowdStrike remains excluded from current Buy/Sell rankings.
- Targeted GDR identity intake opened5 primary references in6 broker requests:
  both Vienna ISIN/ticker listing pages, both current Citibank depositary program
  pages, and Samsung's preferred-GDR prospectus (first3 pages and historical
  financial pages5-7). Only metadata is registered; exchange prices were not
  imported into market state. The document serves historical financial context,
  not a current financial forecast. New evidence addresses the common review's
  missing entitlement and venue questions without changing any instrument ID,
  currency, quote, assessment, source citation or page. Preferred GDR admitted as
  its own manual target after common task completion:23 queue rows/8 manual tasks,
  with all existing attempts preserved. Common and preferred tasks never coexist.
- GDR intake revision `3b16e6f671a8d7003253a5e5a96e5b908b4b9f59` passed
  [CI39185173960](https://github.com/Kabutojira/PaperTrader/actions/runs/39185173960).
  Actual cycle39185320906 completed3 model operations/30 web requests: ASML and
  Stratasys accepted complete USD scenarios; Lithium Americas remains unsupported.
  Revision `664088b7e6545d71b1fcae186b04fd46694dd2c6`, Pages39185895532 succeeded.
  All92 instruments now have an assessment;80 complete/11 unsupported/1 incomplete,
  36 current/56 stale. Stratasys's accepted new bounded review resolves its attention
  state; the two historical failures remain in Git. Crocs remains needs_attention.
- Actual cycle39185932394 completed3 model operations/30 web requests: Yaskawa
  accepted complete EUR scenarios (low confidence), SQM complete USD scenarios
  (medium), and Intuitive Machines remains unsupported. Revision
  `b0804f62b5fb560c2ae3bd654ccff7e8d5c00530`, Pages39186552227 succeeded.
  Coverage82/92 complete,10 unsupported,0 incomplete/missing;39 current/53 stale.
  Actual Enphase single39186596487 used1 model operation/9 web requests and remained
  unsupported, revision `a336e95f31f8f7b2fd00442850b67d81654215f9`;
  Pages39186839806 succeeded. Coverage is now40 current/52 stale; this Enphase
  review replaced expired research. Currency remains USD; no invented scenario values.
- Source-access regression: long HTML releases exposed only their first12,000
  characters, hiding later financial tables. Added overlapping bounded windows via
  the existing page argument and explicit window metadata/tool instructions.
  Each window still costs one request;12-request/600-second/24-turn operation,
  2MB body/12k excerpt/15-second HTTP limits and all-seen-excerpt copy guard remain.
  PDF semantics and financial validation are unchanged; no raw text is persisted.
  Focused87 tests passed; full verification and exact pushed CI evidence follow.
- Finite actual engineering qualification used12 broker requests:10 usable windows
  across LUNR/ENPH/SGML/LAC and2 refused Twist full-report sources (403). ENPH's
  third window and LUNR's second expose missing balance-sheet/cash-flow/share tables.
  Only those2 entities receive new bounded manual reviews; SGML/LAC's later prose
  does not resolve their substantive valuation blockers. No citations, financial
  facts, dates or pages were imported by this qualification. Queue18/manual3,
  including existing Samsung preferred request; original attempts preserved and
  no new source rows. Live research paused until source repair passes pushed CI.
- Reader repair verification:101 focused HTML/PDF/results/runtime tests and full204
  tests passed (2 warnings); Ruff, formatting, MyPy, strict current data validation,
  worker staging/policy checks and diff checks passed. No site implementation or
  current research content changed, so no redundant local Quartz build was needed.
- HTML-window repair revision `d5cf104e761986b51e52c1d06c9c57bfb0b95093`
  passed [CI39187410174](https://github.com/Kabutojira/PaperTrader/actions/runs/39187410174).
  Actual preferred-GDR single39187518603 used1 model operation/12 web requests,
  accepted supported EUR970/2000/3720 scenarios at low confidence, revision
  `9abb66734e4791e416634c792a4053ce5ad882be`; independent Pages39187847092 triggered.
  Coverage83/92 complete,9 unsupported; all92 assessed,41 current/51 stale.
  Low confidence remains excluded from current Buy/Sell rankings.
- Additional finite Twist qualification used6 engineering broker requests:2 usable
  full-exhibit windows via the public FAST-EDGAR filing archive,1 request curtailed
  by the test broker's redirect budget, and2 refused financing-release/filing
  routes. The first usable archived read required a redirect (2 HTTP requests).
  Registered1 metadata-only issuer-filing reference with financial tables available
  in HTML window2; no snippets, raw text or financial assumptions imported.
  One new bounded Twist review is warranted by the full company exhibit replacing
  the previous secondary summary/announcement locator.
- Samsung common gets one new bounded manual review after primary depositary/venue
  evidence resolved its earlier identity blocker and the preferred review validated
  shared current issuer financial evidence. No previous attempts or assessment are
  reset; common and preferred instruments keep separate identities and valuations.
  Queue19/manual4; next default3 tasks are LUNR/ENPH/TWST, then a common-GDR single.
  Strict current data validation passed; financial assessment/page changes remain
  solely the responsibility of accepted isolated research results.
- Source-intake revision `00fdd18b5428cdc7057a8d7658080cdc4832e183` passed
  [CI39188021655](https://github.com/Kabutojira/PaperTrader/actions/runs/39188021655).
  Preferred-GDR Pages39187847092 succeeded; public metadata, homepage and company
  page returned200 with exact accepted9abb revision.
- Actual three-company cycle39188210514 completed3 model operations/31 web requests:
  LUNR10, ENPH11, TWST10. Enphase accepted supported USD8.03/19.28/38.22 cases,
  low confidence; LUNR/TWST remain honestly unsupported after accessing full tables.
  Accepted revision `3c9c904f574cd4baa8e8e2b3c659a5cadde6ccf9`, exact-revision
  Pages39188908016 succeeded. Coverage84/92 complete,8 unsupported;41 current/51 stale.
  LUNR still lacks post-acquisition diluted-claim/debt reconciliation; Twist lacks
  verified subsequent financing terms. No failure, timeout or case invention.
- Actual common-GDR single39189070501 completed1 model operation/10 web requests,
  accepted supported EUR2401.59/5003.30/7961.19 scenarios at low confidence,
  revision `a1d9369f8ab8530ad2db8b07feee954441befcec`; Pages39189391786 triggered.
  Coverage85/92 complete,7 unsupported; all92 assessed,41 current/51 stale.
  Each Samsung instrument keeps its own entitlement bridge and current valuation;
  neither low-confidence instrument enters Buy/Sell rankings.
- Final capitalization-source qualification used7 bounded engineering requests:
  3 usable primary documents (Twist offering8-K and issuer pricing release; LUNR
  acquisition8-K),3 refused issuer routes and1 oversized LUNR quarterly filing.
  No body/request/financial-validation limits were relaxed. Register only Twist's
  2 newly verified financing references and admit1 new bounded review addressing
  its specific failed-source limitation. LUNR receives no further immediate review
  because the full diluted-claim evidence remains inaccessible within the caps.
  All other assessments/pages/citations remain unchanged; queue16/manual1, existing
  attempts preserved. Strict data validation passed; exact intake CI follows.
- Financing intake `938505dc3a154041ef1f4a520bbf9113b9d93f4e` passed
  [CI39189491333](https://github.com/Kabutojira/PaperTrader/actions/runs/39189491333).
  Common-GDR Pages39189391786 succeeded. Final qualified Twist single
  [39189589800](https://github.com/Kabutojira/PaperTrader/actions/runs/39189589800)
  completed1 model operation/8 web requests and accepted supported USD51/78/107
  scenarios, low confidence, with3 current sources. Revision
  `3b1bf57ab05af6c2ef5de78784687cd2eb18259d`; independent Pages39189879362 triggered.

### Faster watchlist backfill: final coverage and remaining evidence limits

The user-authorized sequential acceleration is finished. All92 instruments retain
stable identities and current assessment records;86 have complete sourced
bear/base/bull valuation cases, up from22 at the start of the coverage follow-up.
This includes the documented33 historical narrative recoveries, which changed no
fair values or research dates. It does not mean every valuation was newly refreshed:
41 assessments are in date and51 remain stale. Expired valuations, unsupported
cases and insufficient-confidence cases do not populate current rankings.

Six companies remain explicitly `valuation_unsupported`; they have current sourced
research with limitations, rather than fabricated scenario values:

| Company | Evidence needed before a supportable per-share valuation |
| --- | --- |
| Nidec (NIB.F) | Reliable corrected financial statements, quantified accounting/quality exposures and verified Frankfurt instrument conversion |
| Sigma Lithium (SGML) | Detailed financial/debt/share notes, current operating restart evidence and normalized cash conversion |
| AbCellera (ABCL) | Verifiable clinical/program detail and defensible risk-adjusted commercial cash-flow assumptions |
| Intuitive Machines (LUNR) | Complete diluted economic claims, debt/senior claims and post-acquisition reconciliation; full quarterly filing exceeds the reader cap |
| Recursion (RXRX) | Clinical/commercial probability inputs and reconciled post-financing capitalization |
| Lithium Americas (LAC) | Current project operating/capital model, financing waterfall and diluted capitalization |

There are0 missing research records and0 incomplete supported cases. Crocs retains
its existing needs_attention state after exhausted historical attempts; its complete
historical valuation is preserved. No attempts were reset to hide failures. There
are15 compact queue rows (11 pending and4 failed with bounded retry state),0 manual
requests,0 legacy blocked rows/dependencies. Remaining ordinary stale coverage
continues through the scheduled bounded queue; unsupported cases await substantive
new evidence or normal eligible review, without automatic task cascades.

Final local data/publication gate: strict schema/source/reference validation passed,
100 targeted publication/result/link tests passed, deterministic publication preview
made no writes, and reviewed Quartz output built148 pages/205 files with valid links.
Current rankings contain4 Buys and3 Sells with unique issuers and no stale padding.
The source repair's full204-test gate and subsequent clean Actions CI passed; the
final documentation push will receive another exact-revision CI check.

Measured current footprint:258 tracked data files/5,493,701 bytes versus the frozen
pre-migration tag8,227 files/58,834,441 bytes (about91% smaller by bytes);19 Python modules
remain. Current catalogs preserve92 instruments/91 issuers,29 ideas and446 source
metadata rows. Active work fell from648 legacy rows to15. Research uses one model
configuration, sequentially; the scheduled default stays3 operations,12 web requests
per operation and30 queued entities. Market remains LLM-free; actual completed-session
repeat evidence is0 provider requests/0 changes/0 commits. Engineering source
qualification and mocked tests are separately identified above; none is claimed as
live company research. Daily market starts13:00 America/New_York and scheduled
research follows, with weekly discovery still bounded independently within its cycle.

Final reviewed documentation revision `39e743f4b8e25baca71379440b210b4446920bb4`
passed [CI39190145118](https://github.com/Kabutojira/PaperTrader/actions/runs/39190145118)
with complete tests/static/schema/reference/Quartz gates. Actual
[Pages39189879362](https://github.com/Kabutojira/PaperTrader/actions/runs/39189879362)
succeeded from accepted research revision `3b1bf57ab05af6c2ef5de78784687cd2eb18259d`.
Public metadata verifies that exact SHA; coverage JSON, homepage, catalog and9
company pages all returned200 in13 bounded live HTTP checks. Served coverage is86
complete/6 unsupported/41 in date/51 stale, with4 Buys and3 Sells. Subsequent changes
are documentation-only, so publication is not repeated for unchanged research inputs.
No further research operation is pending from the explicit faster-backfill request.

## Explicit analysis of the15 active-queue companies —2026-10-19

User requested analysis of every company in the active queue. Fixed scope captured
outside active data: AMAT, ROBOTIS108490, KTOS, SPOT, MSFT, AMZN, TX, FCX, QCOM,
PWR, CRSR, RKLB, DNA, XMTR and MSTR. All15 currently have complete historical
valuations whose validity has expired. This is a fresh research request, distinct
from restoring baseline narrative completeness. Accepted results will replace the
current assessment and page only through the existing staged/validated transaction.

All15 existing rows are now explicit manual priority100, with no new task rows or
counter resets. AMAT/ROBOTIS/RKLB/DNA retain their one previous failed attempt and
one remaining retry. Manual admission bypasses their elapsed backoff through the
existing supported policy. The next3 claims are AMAT, ROBOTIS and KTOS. Execute
sequential default3-operation cycles with discovery disabled; continue through the
fixed scope, with any additional retries bounded by each row's original maximum2.
Preserve accepted prior valuations on failed validation; unsupported is an honest
research outcome. Scheduled defaults remain unchanged.

Bounded engineering source preflight used24 broker requests:20 readable opens and4
refusals (2 HTTP403,2 oversized bodies). Register15 new metadata-only primary
references: readable issuer results, archived company filing exhibits, FCX's40-page
Q2 results PDF and October2 operations update, and Strategy's October12 capital/
Bitcoin update. ROBOTIS retains its existing DART identities; the existing report
and balance/income pages were read without replacing their source metadata. The
ECB reference is linked to Spotify solely for an explicit EUR-to-native-USD
valuation bridge; no market FX subsystem is added. No excerpts, facts, forecasts,
assessment dates or wiki research changed during this preflight. Strict current
data validation and transaction invariants passed. Commit/CI precede live dispatch;
record each actual cycle's outcomes, request counts, revision and Pages evidence.

## Market lifecycle repair — 2026-10-24

Scheduled market run [40016812945](https://github.com/Kabutojira/PaperTrader/actions/runs/40016812945)
preserved accepted prices but degraded on ATKR and ANIC.L after both caches ended on
October16. Atkore's [October19 Form 8-K](https://www.sec.gov/Archives/edgar/data/1666138/000166613826000041/atkr-20261019.htm)
confirms the merger closed, each common share became a right to USD95 cash, and NYSE
trading was halted for delisting. ATKR is therefore retained under its immutable
security and issuer IDs with its last good bar, but its lifecycle is now `acquired`
and market refreshes no longer demand nonexistent later sessions.

ANIC.L remains active: the [London Stock Exchange instrument page](https://www.londonstockexchange.com/en/quote/equity/ANIC/agronomics-limited)
reported normal trading through October23. A bounded read-only yfinance check on
October24 used5 HTTP requests and returned valid ANIC.L sessions for October19–23;
ATKR's post-October16 rows were NaN. ANIC.L stays on the watchlist and keeps strict
completed-session freshness. No assessment, fair value, research date, identity or
historical price was changed by this repair.

## Fundamental scoring export — rubric 1

Implement the five optional source-backed assessment components for FinanceAlerts,
joined only by immutable security_id, with canonical assessed_at/valid_until and
no price, technical-indicator, trading or credential dependency on that consumer.
The contract is [docs/FUNDAMENTAL_SCORING.md](docs/FUNDAMENTAL_SCORING.md).

The schema, deterministic CSV serialization, final-result validation, research
worker/skill, migration and fixtures change together. Numeric values require
component rationale and valid instrument-linked citations; unsupported components
remain empty with explicit explanations. Valuation is a checked scenario/price
snapshot for a recorded completed-session native-currency reference. Other
components do not reprice with market data, and there is no aggregate score.

The initial92 assessment rows gain unscored metadata only; their pre-existing
fields, identities, currencies, scenarios, sources and research/expiry dates are
preserved. No live research or numeric score backfill is part of this change.
VLTO and XYL already have priority75 missing-coverage queue rows and no assessment;
preserve those bounded requests. Samsung common/preferred GDRs remain separate
EUR per-instrument records. Queue size30, two attempts and three sequential daily
operations remain unchanged. Verification must include complete/partial/unsupported
scores, range/source/reference failures, expiry, immutable joins, deterministic
exports, original-date migration, full current validation and exact-revision CI.

Local verification passed171 focused tests and235 full tests (two existing exchange
calendar warnings), locked dependency sync, Ruff/formatting, MyPy and strict current
validation. Quartz check/build emitted149 pages/210 files with valid internal links.
A direct comparison against the prior committed CSV confirms all92 rows and every
original field are unchanged; every numeric score/reference remains empty. These
are local/mock checks, not live research or a score backfill. Exact pushed CI and
publication evidence follow through the normal independent workflows.

## Remote research failure and controller repair — 2026-10-25

Actual scheduled research [40225678968](https://github.com/Kabutojira/PaperTrader/actions/runs/40225678968)
ran revision `17b19102eef1986b44b13069aa7d3e03d1ecd23b`. Discovery was not due;
one Domino's operation used12 web requests and failed final assessment validation
with `state.assessment.invalid`. Its prior accepted research remained intact. The
controller scheduled a retry, but the subsequent commit failed with a generic
ValueError before producing a recovery artifact. No attempt or health update
reached main, and the follow-on Pages jobs skipped build/deployment. Their green
resolve jobs do not establish that a new site was deployed.

Reproduced controller defect: `finalize_commit` explicitly allows the existing
encrypted OAuth file, then passes it to a destination guard that accepts only
`data/`. Any actual credential refresh therefore prevents the whole phase commit,
including its retry state, before recovery archive creation. The observed failure
matches this path; the remote log does not expose the credential diff. The fix
permits only that exact encrypted path, checks every parent for symlinks, and
leaves the research transaction's data-only destination guard unchanged. Tests
cover the exact exception, adjacent forbidden paths and symlink parents.

Commit preflight failures now expose static `runtime_commit.*` categories; scoring
rejections expose `state.assessment.scoring.invalid` without rejected values or
source text. Validation remains strict. The rejected Domino's payload was not
retained, so its precise invalid assessment field cannot be reconstructed or
claimed to have been repaired. The spent attempt must be recovered through the
deterministic queue controller after exact-SHA CI, without another model call or
an attempt reset. Focused verification passed124 tests, strict validation, Ruff,
formatting and MyPy; these are local/mock checks, not live inference/OAuth refresh.

Current catalog audit:94 instruments have94 assessments,82 in date and12 stale.
The93 active/watchlist coverage targets have67 complete valuations and26 explicitly
unsupported cases, with no missing research records or incomplete supported cases.
Crocs retains needs_attention; Domino's is the sole queued company. Numeric scores
exist for19 valuation,25 business-quality,25 thesis,23 balance-sheet and24 risk
components; empty components retain their evidence-gap explanations. The core
M0–M9 implementation is complete. Next work should prioritize verified accessible
issuer releases/filing mirrors and useful source leads within existing request
budgets, then ordinary bounded refreshes and source-backed scoring. Several
current unsupported reviews specifically report SEC HTTP403, empty dynamic IR
pages, oversized reports or missing instrument/capitalization evidence. More model
operations or weaker evidence checks would not resolve those documented gaps.

Full local Python gates passed239 tests (two existing exchange-calendar warnings),
locked dependency sync, strict validation, Ruff/formatting and MyPy on19 modules.
Local Quartz verification is blocked: installed Node25.8.1 cannot import sharp's
missing optional `@img/colour` package after locked npm installation. The official
Node24.4.1 download timed out; no unchecked archive or lock-file change was used.
The exact-SHA CI gate must verify Quartz under its pinned Node24.4.1 before recovery.
No live research retry is part of this repair.

Repair revision `7e6192bd24e6f91579f8d79cbbca1f5ad9e6b2b7` passed
[CI40227659848](https://github.com/Kabutojira/PaperTrader/actions/runs/40227659848),
including the full Python gate and Quartz check/build with pinned Node24.4.1.
After this gate, deterministic `claim`/`finish` recovery recorded Domino's actual
spent attempt using the observed run times, with no new model or web request:
attempts1, failed/retry_scheduled, next eligible2026-10-26T01:35:24Z. Compact health
now records the observed degraded phase and retains the prior success timestamp;
derived health views were regenerated. All225 protected canonical-table, market,
company-page and idea-page files remained byte-identical. No rejected valuation,
score, source or credential was imported. Recovery strict validation and38 focused
runtime/publication tests passed; the protected-path Git diff is empty. A temporary
fixture-quota failure was resolved by removing only this session's disposable
verification directories and using workspace basetemp for the rerun. Exact-SHA CI
and independent Pages deployment are checked before closing this follow-up.

## Bearish research extension — feature/short-research (2026-10-31)

This is one extension milestone after M0–M9, based on latest main
`c1a4f3a1b9013af38ec249adfae6739d55ca3190`. Adds canonical research roles,
configurable evidence-gated Short opinions, bearish-universe Buy exclusion,
Short inclusion in the existing Sell ranking, prominent derived company summaries,
and a generated Shorts catalog/navigation. Market may regenerate that catalog
through its explicit page allowlist; assessment and company-prose writes remain
forbidden in market. Existing long rating arithmetic and issuer dedupe are retained.

Actual intake: eight sequential two-company CLI batches imported all16 requested
instruments after primary URL and independent yfinance reconciliation. A narrow
lazy-Mapping compatibility fix was needed in identity verification; no listing or
source gate was weakened. Actual market refresh succeeded (2 provider batches,
33 HTTP requests) with2026-10-30 completed-session USD prices for all16. All94
baseline identities/fields and94 assessments are preserved. Full identity/action
review, import requests, blockers and per-company status: docs/short-research/README.md.

Actual research execution:16 explicit sequential single-security attempts, active
candidates first, all failed isolated-worker preflight before inference/web research
because the pinned Hermes executable is absent. Zero completed new assessments;
all16 pages remain unresearched/Unrated with empty fair values, scores and confidence.
Normal retries are retained (1/2 attempts), queue<=30; scheduled daily defaults
remain3 operations. The user explicitly chose to keep workflows unchanged and
document this blocker. No feature data was written to main or publicly deployed.
Full research and the user's public acceptance criterion remain incomplete.

Initial local verification:228 targeted tests passed; Mapping repair23 tests
passed; MyPy19 modules and canonical validation passed. Complete local checks,
reviewed Quartz output and exact-SHA CI evidence follow before delivery. Test
fixtures may demonstrate Short rendering; they must never be described as real
Short recommendations. Pages still requires the exact SHA to belong to main.

Extension local gate:276 full-suite tests passed (two existing calendar warnings),
Ruff lint/format, MyPy19 and strict validation passed. Locked npm install and Quartz
check/build passed under local Node25.8.1 (162 Markdown pages,225 emitted files,
internal links valid). Reviewed desktop/mobile Shorts and actual Unrated/Strong Sell
company summaries; a synthetic fixture verified Short rendering without adding a
real recommendation. Repaired mobile grid/search intrinsic-width overflow;390px
viewport summary fits x16–374 with zero horizontal scroll range. Site checks/build
passed again after the CSS-only fix. All94 original security fields and94 assessment
rows remain preserved. Exact-SHA CI under pinned Node24.4.1 follows the feature push;
research completion and deployment remain explicitly blocked, not accepted.

## AI Agent Economy intake reconciliation — 2026-11-01

Reconciled the seed from `Stell0:research/ai-agent-economy-stocks-20261101`
(`93e94ac775fd5fd6bc8910fc70504174e1a5803f`) onto upstream main
`789be6febb7777fbd1dae6e53f609cabf2fbadff`. Fork PR1 had merged only into
the temporary comparison base; it had not updated upstream main.

Append exactly27 instruments selected by provenance
`user_seed:ai-agent-productivity-loop:2026-11-01`, one idea,40 relationships
(including13 existing instruments) and15 sources. Preserve all110 existing
security rows,94 assessments and27 queue rows, including three later
needs_attention states. ABBN.SW remains a distinct CHF instrument sharing
the existing ABB issuer; add its XSWX exchange calendar. The intake test
validates exact membership and canonical integrity while allowing subsequent
accepted research and relationship changes.

Local validation, Ruff/formatting, MyPy and all277 tests passed (two existing
calendar warnings). Local Quartz execution is blocked by missing sharp/runtime
dependencies under Node25.8.1; exact-SHA CI must check the pinned Node24.4.1
build. All27 additions remain unassessed. No campaign company research or
inference call has been executed. Upstream merge, isolated runtime diagnosis,
canary research, full batch and verified publication remain outstanding.

## Isolated Hermes runtime diagnostic — 2026-11-01

Run41351798426 restored and re-encrypted OAuth successfully inside the pinned
Hermes container, but all three bounded operations stopped at the model stage with
zero observed web requests. The existing sanitized controller output did not expose
whether the child failed during import, initialization, provider access or final
transport; its three operation counters are budgeted attempts, not proof of three
provider calls. None targeted the27 AI Agent Economy instruments.

Add a manual, dry-run-by-default diagnostic using the same staged worker, UID10000,
fresh profile, pinned Python/code and OAuth refresh boundary. An applied diagnostic
receives no company/source/queue context, exposes no tools, and permits one generic
inference turn. Static categories distinguish import, initialization, auth/model
access, rate limit, network/timeout, exit and serialization without child stderr,
provider bodies, prompts or responses. Local tests use mocks only; no local provider
call or pinned-image probe was completed. Exact-SHA CI and one actual applied Actions
diagnostic are required before the issue can be classified or company research can
resume.

The intake is now merged through upstream PR33 at
`bb867102082616d78d2b1d3810dccd6a8bbfd88b`; CI41355368058 and41355390946
passed, including pinned Quartz checks/build. Pages41355666176 serves that exact
revision: homepage, company catalog and idea page returned HTTP200; both catalogs
contain all27 target links. This publishes coverage gaps, not completed valuations.

Diagnostic local verification passed129 focused tests and all295 tests (two
existing calendar warnings), Ruff/formatting, MyPy20 modules and strict canonical
validation. Canonical research/queue contents remain unchanged. These are mocked
runtime checks; actual account/model access and all27 company reviews are pending.
