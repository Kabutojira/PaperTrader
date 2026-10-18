# Research-only migration acceptance — 2026-10-18

The research-only runtime is active. The daily market refresh starts at **13:00
America/New_York** (Eastern time, including daylight saving); bounded research
follows the scheduled market workflow. Pages builds and deploys independently.
GitHub cron is best-effort, so 13:00 is the scheduled time, not a start-time SLA.

The verified recovery tag `pre-research-only-20261018` resolves to
`0ab7ec85bf10d55c6a26dcc95511f5c32716a48f`. The retired trading scheduler is
absent. GitHub reports only the new market, research, Pages and CI workflows
active, plus Dependabot. FinanceAlerts remains independent.

## Acceptance evidence

| ID | Result | Evidence |
| --- | --- | --- |
| AC-01 | Passed | Research-only CLI, two research skills, three independent workflows and public navigation; retired trading/alert modules and generated exports removed. Import/reference audit and CI passed. |
| AC-02 | Passed | 83 latest assessments for 83 distinct security IDs; 322 current source rows; no active assessment/source history or revision chain. Current sourced pages retained. |
| AC-03 | Passed live | Final closed-session repeat made zero provider/HTTP requests, changed no paths and created no commit; main remained `ac3230095e34b2bf349648ced4733d8d73b1eec2`. |
| AC-04 | Passed injected | A failed-symbol fixture preserves other quotes and the previous good bar while marking the affected symbol stale. Actual initial market refresh had zero failed tickers; no real provider outage was induced. |
| AC-05 | Passed | Default three sequential operations including discovery, queue cap30, one entity/issuer task, max2 attempts; queue/discovery/full-cycle tests and actual single-entity dispatches. |
| AC-06 | Passed | All648 old rows dispositioned, including340 blocked and13 waiting relationships. Current30 rows are pending, without old IDs, dependencies or capacity blocks. |
| AC-07 | Passed | Atomic validation/rollback/idempotence tests, October15 frontmatter fixture, actual accepted NVIDIA and idea updates; invalid live results preserved prior research. |
| AC-08 | Passed | Actual supported NVIDIA scenarios and honest unsupported SoFi outcome. Numerical/source/confidence/freshness tests remain strict; repricing does not replace research facts. |
| AC-09 | Passed | Deterministic issuer-deduped rankings and empty-list fixtures; actual homepage has1 eligible Buy and0 Sells, with80 stale assessments excluded. |
| AC-10 | Passed | Actual market run with no model operation; research and independent Pages runs; injected Pages failure leaves market/research intact; manual Pages retries execute no research. |
| AC-11 | Passed | Worker privilege/environment/tool allowlist tests, web private-address rejection and commit allowlists; Git and deployment credentials confined to deterministic post-agent/deployment steps. |
| AC-12 | Passed | Rewritten root docs/runbook/config, locked install,19 remaining Python modules, full148-test suite, Ruff/MyPy/schema/link validation and actual Quartz build. |

## Actual external operations

All links below are real GitHub Actions runs, not mocks.

| Operation | Outcome / exact result | Run |
| --- | --- | --- |
| Initial non-dry market | 13 provider calls,280 HTTP requests,0 failed tickers;51s | [39155945162](https://github.com/Kabutojira/PaperTrader/actions/runs/39155945162) |
| SoFi company review | Accepted `not_supportable`;1 model operation,10 web requests; no invented valuation | [39158371221](https://github.com/Kabutojira/PaperTrader/actions/runs/39158371221) |
| NVIDIA company review | Accepted supported valuation;1 model operation,12 web requests;197s; commit `fdc8c5afa7e6e35d80c530b049f70f69a64c2c4b` | [39160516606](https://github.com/Kabutojira/PaperTrader/actions/runs/39160516606) |
| Defensive-consumer idea | Accepted idea/page/source updates;1 model operation,12 web requests;157s; commit `3853e72ad921f9ab25f7a876f832528196a73c32` | [39162062924](https://github.com/Kabutojira/PaperTrader/actions/runs/39162062924) |
| Final closed-market repeat | 0 provider/HTTP calls,0 changed paths,0 commits;21s | [39163162212](https://github.com/Kabutojira/PaperTrader/actions/runs/39163162212) |
| Independent Pages | Exact idea-update commit above; resolve5s/build44s/deploy12s, about66s elapsed | [39162269997](https://github.com/Kabutojira/PaperTrader/actions/runs/39162269997) |
| Clean-checkout CI | Exact final runtime commit `ac3230095e34b2bf349648ced4733d8d73b1eec2`; validate job75s | [39163037009](https://github.com/Kabutojira/PaperTrader/actions/runs/39163037009) |

The [public homepage](https://kabutojira.github.io/PaperTrader/), company and idea
catalogs, NVIDIA research, defensive-consumer idea, ranking JSON and publication
metadata returned HTTP200. The deployed metadata matched exact commit `3853e72a`
and deployment run39162269997. Final documentation publication is additionally
verified after this report commit; the deployed `data/publication.json` identifies
its exact revision, build time and Actions run without a repository history table.

Local final gates:148 tests passed in61.8s, two existing dependency deprecation
warnings; Ruff lint/format, MyPy19, strict current data/source/link validation,
TypeScript/checks and Quartz build passed (144 Markdown inputs,200 emitted files).
The homepage build was reviewed with exact-SHA metadata and company status banners.
The deliberately invalid research attempt, partial market outage, Git divergence
and Pages failure are **injected local fixtures**, not actual external outages.
Discovery was a **dry run**, reporting due=true,0 model calls and no data writes;
its configured limits were1 idea,2 companies and8 identity HTTP requests.

## Failures and bounded dispositions

Two actual Crocs attempts failed timestamp validation and two AI-compute idea
attempts failed citation/source-identity validation. Both entities are now
`needs_attention`, with prior research intact and no endlessly blocked task. The
first discarded responses cannot identify every rejected field; the later
AI-compute failure specifically attempted to change a stable source ID's URL.
The model may still return invalid results; strict rejection and bounded retries
are intended behavior, not permission to weaken evidence checks.

Live checks also exposed a fresh-checkout CSV newline comparison defect: equivalent
multiline CRLF text caused timestamp-only commits despite zero provider calls.
Commit `ac323009` fixes CSV newline equivalence, preserves real edits and leaves
non-CSV comparison byte-exact. Its regression and the final live no-commit repeat
passed. Earlier zero-call runs that made bookkeeping commits are not presented as
successful no-commit checks.

Seven actual single-entity model operations were attempted during cutover: three
accepted (SoFi unsupported, NVIDIA supported, defensive-consumer idea) and four
rejected (Crocs twice, AI-compute idea twice). Six completed responses reported67
web requests in aggregate; the first Crocs count was not instrumented. These are
Hermes research operations, not measured model API-call/turn counts. Four separate
bounded manual NVIDIA source-access probes were not research/model operations.

## Before and after

| Measure | Baseline / before pruning | Current |
| --- | --- | --- |
| Securities / issuers | 92 /91 | 92 /91; instrument IDs preserved |
| Ideas / relationships | 29 /47 | 29 /47 |
| Current assessment rows | 83,82 expired,0 fresh supported | 83,80 expired,1 fresh supported;2 current unsupported |
| Current research sources | 366 at original baseline;368 immediately before pruning | 322 referenced current records after live updates |
| Active queue | 648:340 blocked,295 ready,13 waiting | 30 pending;0 legacy blocked/dependency rows |
| Active data files / bytes | 8,236 /58,658,418 immediately before pruning | 249 /5,207,673 at final runtime acceptance |
| Source modules | 76 before removal;1 manual migration module added | 19;58 obsolete modules deleted |
| Full local suite | Legacy715 tests before pruning | 148 relevant tests,61.8s locally |

M8 removed7,987 data files, about91% of active data bytes, while retaining current
research and its citations. Original baseline data was8,227 files/58,834,441 bytes;
that earlier inventory differs from the immediate pre-pruning measurement because
migration/runtime outputs were added and old generated files changed. Historical
bytes remain retrievable from the verified Git tag rather than the active tree.
The current byte count is a working-tree measurement and can vary with CSV checkout
line endings; the milestone census is in `m8-size.json`.

## Version-controlled budgets and limitations

| Component | Defaults / observed result |
| --- | --- |
| Market | One yfinance provider; batch8,24 provider calls/320 HTTP requests maximum,2 attempts,15s request timeout,600s runtime;365-day cache and weekly7-day correction window. Initial actual13/280; closed repeat0/0. No generative model calls. |
| Research | One configurable model (`gpt-5.6-sol`),3 scheduled operations, sequential;600s/24 turns/12 web requests per operation;30 pending/max2 attempts/30-day freshness. |
| Discovery | At most weekly;1 idea/2 companies;12 research web requests plus8 independent identity HTTP requests; no automatic dependent task cascade. |
| Publication | Deterministic,0 model calls; exact committed input revision; no-op inputs skip build/deploy. Manual retry is independent of research. |

No comparable legacy network-call or elapsed-runtime measurement was captured, so
no speedup or request-reduction ratio is claimed. PDF and JavaScript-only financial
pages can remain inaccessible to the bounded HTML broker; unsupported conclusions
are valid and evidence limitations must remain visible. Forecasts and scenario
probabilities are explicit research assumptions, not issuer guidance. Rankings
contain only supported, fresh coverage and are never padded to ten.

See [PLAN](../../PLAN.md), [operations](../OPERATIONS.md),
[M0 recovery](M0.md), [M3 queue policy](M3.md) and `m8-size.json`.
