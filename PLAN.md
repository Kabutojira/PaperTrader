# PaperTrader implementation plan

## Step 1 — Scaffold repository contracts — Complete (2026-07-24)

Established the paper-only repository structure, configuration and CLI boundaries, canonical schemas and empty data state, atomic writes, integrity checks, runtime commit whi
telist, Hermes-native wiki, project skills, pinned dependencies, workflow scaffolds, and initial test suite.

## Step 2 — Build deterministic market, queue, and accounting core — Complete (2026-07-24)

Implemented normalized market retrieval, rolling price data, indicators and candidate packets, sequential queue processing, deterministic classification, Decimal-safe risk an
d paper execution, append-only accounting ledgers, generated portfolio and performance views, reporting, issues, logs, and replay-safe test coverage.

## Step 3 — Integrate Hermes and reusable project skills — Complete (2026-07-24)

Integrated pinned and isolated Hermes execution with the native `llm-wiki` skill and repository skills, mandatory sequential `--yolo` operation handling, actual-change result
 manifests, command and content auditing, prompt-injection defenses, strict path validation, and evidence-linked terminal outcomes.

## Step 4 — Assemble GitHub workflows, reporting, and publication — Complete (2026-07-24)

Built the serialized daily and reusable workflows for deterministic preparation, bounded Hermes operations, fills and reconciliation, canonical report generation, validated r
untime commits, Quartz publication, and retryable Telegram delivery with isolated credentials and manual-dispatch support.

## Step 5 — Validate the complete operating cycle — Complete (2026-07-24)

Validated a clean-checkout research-to-paper-fill lifecycle covering market normalization, classification, sequential research, wiki and structured-state updates, strategy ex
ecution, next-session fills, accounting reconciliation, report publication, Telegram delivery, Quartz builds, deterministic replay, and idempotence.

## Step 6 — Persist OpenAI Codex OAuth state as age ciphertext — Complete (2026-07-24)

Replaced the Hermes API-key path with isolated `openai-codex` OAuth, restoring plaintext only inside the runtime boundary and persisting verified refreshes as one age-encrypt
ed artifact, with failure-safe credential-only commits, strict cleanup, and no API-key fallback.

## Step 7 — Add the local Codex harness and execute a researched idea — Complete (2026-07-25)

Added a two-phase local Codex harness that preserves queue claims, skill identity, command receipts, exact-delta validation, manifest-last completion, and daily finalization
contracts, then used it to research the solar, storage, and grid-flexibility thesis and enqueue bounded security follow-ups without forcing unsupported trades.

## Step 8 — Add opportunity-cost-aware portfolio allocation — Complete (2026-07-27)

Added evidence-backed security assessments, deterministic Decimal-safe candidate scoring and baseline allocation, FX support, immutable allocation plans, sleeve-aware strateg
ies and order guards, daily reporting and readiness checks, while retaining cash hurdles, diversification limits, staged exposure caps, and the existing conviction and accoun
ting controls.

## Follow-up — Repair daily Hermes execution — Complete (2026-07-27)

Reproduced the hosted failure and fixed the root-to-unprivileged runtime handoff so Hermes can safely read repository data and write its result manifest without receiving sou
rce, Git metadata, or credentials; a fresh pinned-container run then completed and passed all controller validation.

## Follow-up — Enforce GitHub Pages link integrity — Complete (2026-07-27)

Published the linked inbox packets and added a deterministic post-build checker for generated HTML routes, assets, directory indexes, and project Pages base paths, eliminatin
g the dead internal links and making future broken references fail the build.

## Follow-up — Make the Quartz homepage results-first — Complete (2026-07-27)

Made the homepage lead with the latest report, current cash, equity, exposure, P/L, returns, positions, and recent operation conclusions, backed by an idempotent deterministi
c refresh command and canonical tables rather than manually maintained summaries.

## Follow-up — Clarify inbox entries, recover classification, and enrich Telegram delivery — Complete (2026-07-27)

Changed candidate titles to human-readable ticker and indicator labels with security links, added retryable tool-free Hermes classification through the isolated OAuth profile
, and upgraded Telegram delivery to rich Markdown with frontmatter removal, commit-pinned wiki links, block-aware splitting, retries, and secret redaction.

# Step 9 — Publish an investor-facing decision dashboard and copyable model portfolio

## Goal

Turn the public Quartz site from a repository-oriented research catalog into a results-first
paper-investment product that clearly communicates:

* the current PaperTrader stance;
* the current model portfolio;
* the approved target portfolio;
* actionable trade signals;
* research alerts that are not trade signals;
* candidate securities and their blockers;
* portfolio performance and risk;
* research and data coverage;
* the evidence and investment thesis behind every recommendation.

Preserve the existing Git-native, paper-only, deterministic accounting and research architecture.
The publication layer must not invent recommendations, bypass strategy or order gates, mutate
trading state, or introduce a real-execution path.

An all-cash model portfolio is a valid recommendation and must be displayed explicitly whenever
the evidence, valuation, diversification, market-data, relationship, strategy, or risk gates do not
support deployment.

## Fixed architecture decisions

* Existing canonical tables remain the sole authority for research, strategy, signal, order,
  execution, portfolio, performance, allocation, and issue state.
* Add one deterministic decision projection. Do not make the Quartz frontend independently join or
  reinterpret canonical CSV files.
* The generated decision projection is a read-only view and must never become an input to
  allocation, strategy, order, fill, accounting, or reconciliation logic.
* Define the public concepts as follows:
  * `current model portfolio`: reconciled filled paper positions plus cash;
  * `approved target portfolio`: current positions adjusted for validated pending paper orders,
    marked as projected until fills occur;
  * `actionable signal`: a current signal linked to an eligible ready or active strategy;
  * `copy-ready action`: an actionable signal with a validated, non-terminal paper order and
    deterministic order legs;
  * `research alert`: an indicator, market, news, or source-change event requiring investigation;
  * `allocation candidate`: a security considered by the allocator but not necessarily approved
    by strategy, signal, and order gates.
* Raw allocation targets without a validated strategy must appear only in the candidate pipeline.
  They must never be labelled `buy`, `sell`, `trade`, or `copy ready`.
* Technical indicators and Inbox packets remain research alerts. They are never rendered as
  actionable trade signals unless the normal strategy and signal lifecycle later produces one.
* Deterministic Python code owns:
  * all joins;
  * state classification;
  * stance selection;
  * weights;
  * current and projected values;
  * quantity calculations;
  * FX conversion;
  * freshness checks;
  * reason-code translation;
  * portfolio and signal export generation.
* The frontend may scale target weights for a user-entered reference notional, but it must do so
  locally, must not persist the amount, and must not claim that the scaled portfolio passed
  PaperTrader's risk checks.
* Automatic notional scaling is initially limited to long equities. Options, shorts, and multi-leg
  strategies must display their canonical legs without automatic user-notional scaling.
* Human-readable company names and tickers are primary presentation labels. Immutable IDs remain
  available in technical details and audit output.
* Investor-facing pages and operational audit pages are separate views of the same committed state.
* The dashboard must remain complete and readable without client-side JavaScript. JavaScript is
  progressive enhancement for copy, local scaling, filtering, and chart interaction.
* Custom Quartz code must live outside `site/quartz/`, because that directory is regenerated from
  the pinned Quartz dependency during every build.
* No agent may directly edit generated decision snapshots or publication exports.
* No brokerage API, credential, real-order adapter, or real-execution action is introduced.

## Step 9.1 — Build the deterministic decision projection

### Decision projection module

Add:

```text
src/papertrader/advice.py
````

Define immutable typed models for:

```text
DecisionSnapshot
PortfolioSummary
ModelPortfolioRow
ActionableSignalView
CandidateView
ResearchAlertView
CoverageSummary
PerformanceSummary
SystemImpact
```

Add:

```bash
papertrader advice refresh --run-id <run_id>
papertrader advice validate --strict
```

`advice refresh` must:

1. require a reconciled portfolio;
2. read the final state produced by the selected daily run;
3. join canonical state by immutable IDs;
4. calculate the public stance and presentation categories;
5. write an immutable run snapshot;
6. atomically replace the latest generated publication snapshot and exports;
7. validate every generated artifact before returning success;
8. be idempotent for identical authoritative inputs.

### Generated artifacts

Add the JSON schema:

```text
schemas/decision_snapshot.schema.json
```

Add the immutable per-run artifact:

```text
data/runs/<run_id>/decision_snapshot.json
```

Add the latest generated publication view:

```text
data/published/decision_snapshot.json
```

Add generated CSV contracts:

```text
data/published/model_portfolio.csv
data/published/actionable_signals.csv
```

Register the CSV contracts as `generated: true` in:

```text
schemas/csv_contracts.yaml
```

The generated files under `data/published/` must not be used by deterministic trading or research
code as authoritative inputs.

Update repository layout validation, runtime commit whitelists, Git attributes, and generated-path
protection for these exact files.

### Decision snapshot contract

The JSON snapshot must contain:

```text
version
snapshot_id
run_id
as_of
report_date
data_status
stance
stance_reason_codes
base_currency
current_portfolio
approved_target_portfolio
actionable_signals
candidate_pipeline
research_alerts
coverage
performance
system_impacts
source_state_hashes
```

Canonical `data_status` values:

```text
current
degraded
blocked
```

Canonical `stance` values:

```text
hold_cash
maintain
deploy
rebalance
reduce_risk
exit
blocked
```

Stance precedence:

1. `blocked` when accounting, reconciliation, current-position marks, required FX, or pending-order
   state is unsafe or unavailable;
2. `exit` when one or more validated actions close exposure and no opening action is approved;
3. `reduce_risk` when validated reduce or close actions dominate;
4. `deploy` when the portfolio is predominantly cash and validated open actions exist;
5. `rebalance` when validated increases and reductions coexist;
6. `hold_cash` when there are no positions and no actionable opening trade;
7. `maintain` otherwise.

The stance must be derived exclusively from deterministic current state. It must not use an LLM
summary as an input.

### Current and approved target portfolios

The current model portfolio must be derived from:

```text
portfolio.csv
cash_ledger.csv
performance_daily.csv
```

The approved target portfolio must be derived from:

```text
current reconciled positions
non-terminal validated orders
order legs
executions already applied to those orders
fresh price and FX references
fees and committed cash
```

Do not derive the approved target portfolio directly from unvalidated allocation targets.

Every model-portfolio row must expose:

```text
snapshot_id
as_of
holding_type
security_id
ticker
company_name
instrument_type
sleeve
current_weight_pct
approved_target_weight_pct
current_value_base
approved_target_value_base
delta_value_base
current_quantity
approved_target_quantity
mark
mark_currency
fx_rate_to_base
market_data_as_of
action
action_status
strategy_id
signal_id
order_id
confidence
effective_score
downside_pct
base_upside_pct
valuation_horizon_months
thesis_summary
entry_rule
exit_rule
invalidation
review_at
research_page
reason_codes
```

Canonical `holding_type` values:

```text
cash
security
```

Canonical investor-facing `action` values:

```text
buy
add
hold
trim
exit
no_trade
```

Canonical `action_status` values:

```text
filled
pending_order
active_signal
awaiting_order_validation
research_candidate
blocked
no_action
```

Include one explicit cash row.

Enforce:

```text
sum(approved_target_weight_pct) + cash_weight_pct = 100%
```

within a documented Decimal rounding tolerance.

Projected pending-order values must be labelled estimates at the recorded reference mark. Actual
portfolio state changes only after deterministic fills.

### Actionable signal classification

A signal may appear under `actionable_signals` only when:

* the signal has a canonical non-terminal actionable status;
* it is not expired;
* its strategy exists;
* the strategy is `ready` or `active`;
* the strategy identity and normalized legs are valid;
* the strategy is not expired or before `not_before`;
* its linked assessment and relationship requirements remain current where applicable;
* required market and FX inputs are fresh;
* no issue blocks the affected current or proposed exposure.

Set:

```text
copy_ready = true
```

only when a validated non-terminal order exists and its canonical order legs can be exported.

An active signal without a validated order may be displayed as an investment recommendation but
must say `Awaiting deterministic order validation` and must not expose a copy-ready quantity.

### Candidate pipeline

Build the candidate pipeline from:

```text
allocation_targets.csv
security_assessments.csv
securities.csv
relationships.csv
strategies.csv
```

Classify candidates as:

```text
approved
strategy_pending
relationship_pending
assessment_pending
market_data_blocked
valuation_unattractive
risk_blocked
research_blocked
```

A raw allocator disposition does not become an actionable signal.

For excluded candidates with a valid assessment, sort near misses deterministically by:

1. positive candidate edge;
2. effective score;
3. confidence;
4. base-case upside;
5. immutable security ID.

Candidates without a current assessment belong in research-coverage reporting rather than being
ranked as investment near misses.

### Research alerts

Build research alerts from:

```text
indicators.csv
canonical Inbox packets
operation history
```

Expose:

```text
security
ticker
alert type
observed at
market-data date
research status
research conclusion
linked research page
```

Every rendered research alert must include the visible label:

```text
Research alert — not a trade signal
```

### Coverage and system impact

Calculate:

```text
allocation candidate count
current assessment count
fresh-evidence assessment count
current relationship count
ready or active strategy count
active signal count
pending order count
market-data success count
market-data failure count
research backlog count
blocking issue count
non-blocking issue count
last successful daily run
```

Classify every current issue as:

```text
blocks_portfolio
blocks_action
affects_candidate
publication_only
operational_only
```

A Telegram or Pages delivery failure must not be rendered as an investment risk.

### Human-readable reason labels

Add a complete deterministic mapping for canonical reason codes, including:

```text
assessment_missing
assessment_stale
relationship_missing_or_stale
score_below_cash_hurdle
base_upside_not_positive
market_data_not_ok
market_data_stale
fx_unavailable
insufficient_diversification
insufficient_eligible_candidates
minimum_trade_threshold
concentration_cap
deployment_budget_exhausted
hard_blocker:*
```

Primary views use the readable explanation. Raw codes remain available in technical details and the
audit appendix.

Unknown codes must fail validation rather than silently appear untranslated.

### Exit criteria

* [ ] Identical authoritative inputs produce byte-identical publication snapshots and CSV exports.
* [ ] Input row ordering cannot change snapshot results.
* [ ] Every public security reference contains a ticker, company name, and valid research link when
  a research page exists.
* [ ] A raw technical alert cannot appear as an actionable signal.
* [ ] An allocation target without a valid strategy cannot appear as a copy-ready trade.
* [ ] A signal without a validated order cannot expose a copy-ready quantity.
* [ ] Current model-portfolio values reconcile with canonical accounting.
* [ ] Approved target values include pending orders without mutating accounting.
* [ ] Cash and target weights reconcile to 100% within the documented rounding tolerance.
* [ ] Stale or unavailable current-position data produces `data_status=blocked`.
* [ ] Candidate-only data failures produce `data_status=degraded`, not a false portfolio failure.
* [ ] Generated artifacts are rejected as authoritative inputs.
* [ ] Agents cannot directly mutate generated publication artifacts.
* [ ] Schema, integrity, typing, formatting, and focused projection tests pass.

## Step 9.2 — Generate investor-facing pages and reports

### Public page structure

Generate or maintain:

```text
data/wiki/index.md
data/wiki/model-portfolio.md
data/wiki/signals.md
data/wiki/performance.md
data/wiki/system-status.md
data/wiki/research-catalog.md
```

Update:

```text
data/wiki/SCHEMA.md
```

with the required page types and tags.

The homepage must no longer contain the complete research catalog. Move the generated catalog to
`research-catalog.md` and link it from the primary navigation.

### Homepage

The homepage must render, in this order:

1. as-of timestamp and data-status badge;
2. one current stance headline;
3. current and approved target portfolio summary;
4. actionable signals;
5. explicit no-trade state when applicable;
6. top assessed near misses;
7. performance and exposure summary;
8. research and relationship coverage;
9. material data-quality impact;
10. links to model portfolio, signals, research, performance, and system status.

For an all-cash portfolio with no actionable signals, the first visible conclusion must be:

```text
No trade — hold 100% cash
```

followed by the main deterministic reasons.

Do not use recent operation completion order as a proxy for investment importance.

### Model portfolio page

Render:

* current equity and cash;
* current portfolio weights;
* approved target weights;
* current-to-target deltas;
* reference marks and timestamps;
* actions and action states;
* confidence and valuation ranges;
* compact thesis and invalidation;
* review date;
* links to complete research;
* copy and download controls;
* a clear paper-only and non-personalized-research notice.

Provide committed downloads for:

```text
model_portfolio.csv
decision_snapshot.json
```

The CSV and JSON links must resolve to the same committed snapshot rendered by the page.

### Signals page

Render separate sections for:

```text
Actionable trade signals
Pending validated paper orders
Research alerts — not trade signals
Recently expired or completed signals
```

For each actionable signal show:

```text
ticker and company
action
strategy
created and expiry timestamps
market-data timestamp
current and target weights
quantity when copy ready
order type and limit when applicable
entry rule
exit rule
invalidation
rationale
thesis link
```

Empty states must be explicit:

```text
No actionable trade signals.
No pending paper orders.
```

### Performance page

Render from canonical performance and portfolio history:

* equity history;
* cumulative return;
* daily return;
* running drawdown;
* cash versus invested exposure;
* conviction versus baseline exposure;
* realized and unrealized P/L;
* allocation changes;
* position and sector concentration.

Use deterministic committed data only.

Do not introduce an external benchmark in this step.

### System-status page

Render:

* last run and publication status;
* portfolio reconciliation status;
* market and FX freshness;
* assessment coverage;
* relationship coverage;
* strategy and signal counts;
* affected securities with human-readable labels;
* current issues grouped by investment impact;
* bounded operation-queue summaries;
* links to the complete audit artifacts.

Show raw queue IDs and immutable entity IDs only on this page or in expandable technical details.

### Daily report

Refactor `src/papertrader/reports.py` so the canonical daily report starts with the same committed
decision snapshot used by the homepage.

New report order:

1. investor decision summary;
2. model portfolio and approved changes;
3. actionable signals and pending orders;
4. candidates and near misses;
5. performance and risk;
6. research changes;
7. data-quality and coverage impact;
8. audit appendix.

Move the following to the audit appendix:

* complete market-freshness table;
* raw operation IDs;
* raw security IDs;
* complete active queue;
* delivery failures;
* machine reason codes;
* run diagnostics.

The audit appendix remains complete and deterministic.

### Telegram

Generate the Telegram message from the committed investor brief rather than the complete operational
report.

Telegram must include:

* stance;
* current cash and exposure;
* approved target changes;
* actionable signals;
* top blocker or near miss;
* data-status summary;
* commit-pinned link to the full report.

Do not include the full operation queue unless a separate system-status delivery mode is explicitly
selected.

### Exit criteria

* [ ] The homepage answers the current stance, holdings, actions, reasons, and data status before the
  research catalog or operational details.
* [ ] Homepage recommendations come from the decision snapshot rather than recent operation order.
* [ ] Every primary table uses ticker and company name rather than an opaque ID.
* [ ] The all-cash state is represented by an explicit 100% cash model-portfolio row.
* [ ] Actionable signals and research alerts are visibly separate.
* [ ] Machine reason codes are translated in primary views.
* [ ] The full raw state remains available in the audit appendix and system-status page.
* [ ] Model-portfolio CSV and JSON downloads match the rendered committed snapshot.
* [ ] Telegram and the public homepage communicate the same stance and actions.
* [ ] Wiki lint and generated-site link checks pass.

## Step 9.3 — Add the decision-oriented Quartz interface

### Custom source boundary

Add custom Quartz source outside the regenerated engine, for example:

```text
site/papertrader/components/DecisionDashboard.tsx
site/papertrader/components/ModelPortfolioTable.tsx
site/papertrader/components/SignalBoard.tsx
site/papertrader/components/PerformanceChart.tsx
site/papertrader/components/StatusBadge.tsx
site/papertrader/scripts/copy-portfolio.inline.ts
site/papertrader/styles.scss
```

Update:

```text
site/quartz.layout.ts
site/quartz.config.ts
site/tsconfig.json
site/package.json
```

Do not place maintained custom files under:

```text
site/quartz/
```

because `prepare-quartz.mjs` recreates that directory.

### Navigation and layouts

Add a primary navigation bar:

```text
Today
Model portfolio
Signals
Research
Performance
System status
```

Use a dashboard layout for:

```text
index
model-portfolio
signals
performance
system-status
```

Use the existing research layout for idea, security, relationship, strategy, source, and Inbox
pages.

On dashboard pages:

* hide article reading-time metadata;
* hide backlinks from the primary view;
* avoid displaying the generic wiki Explorer before the decision content;
* show the exact snapshot `as_of` timestamp instead of the page creation date;
* retain accessible links to the research catalog and audit views.

### Responsive presentation

Implement:

* status cards for stance, cash, exposure, active signals, and coverage;
* responsive portfolio rows that become cards on narrow screens;
* horizontally scrollable technical tables only in audit views;
* visible text labels in addition to colors;
* keyboard-accessible copy and download controls;
* sufficient contrast in light and dark modes;
* semantic table headings and accessible chart descriptions.

Primary portfolio and signal information must remain readable on a mobile viewport without requiring
horizontal scrolling.

### Copy and local scaling

Add progressive enhancement that can:

* copy portfolio rows as TSV;
* download the committed CSV;
* scale long-equity target weights to a local user-entered notional;
* show whole-share quantities rounded down;
* show residual cash;
* display the price and FX timestamp used by the calculation.

The local scaler must visibly state:

```text
Illustrative scaling only. Your scaled quantities have not passed PaperTrader's portfolio-level
risk checks.
```

It must not:

* write repository state;
* call a brokerage;
* send the notional to a server;
* store the notional in browser persistence;
* scale options, shorts, or multi-leg strategies automatically.

### Publication data

Extend the build wrapper to copy only the exact validated generated files from:

```text
data/published/
```

into the temporary Pages output, for example:

```text
site/public/data/decision_snapshot.json
site/public/data/model_portfolio.csv
site/public/data/actionable_signals.csv
```

The copy step must:

* reject symlinks;
* reject unexpected files;
* validate JSON and CSV before copying;
* preserve the committed content hash;
* operate only inside the temporary build output;
* run before the post-build link and artifact checks.

### Exit criteria

* [ ] Custom code survives `prepare-quartz.mjs` because it is outside the regenerated engine.
* [ ] TypeScript checks include all custom component, script, and style sources.
* [ ] Dashboard pages have purpose-built navigation and omit generic article metadata.
* [ ] The primary decision content is readable without JavaScript.
* [ ] Copy, local scaling, and filtering operate as progressive enhancement.
* [ ] Mobile portfolio and signal views pass responsive tests.
* [ ] Status meaning is not communicated by color alone.
* [ ] Downloaded files have the same hashes as the validated committed publication artifacts.
* [ ] No client action can mutate repository or trading state.
* [ ] Quartz build, link validation, and Pages artifact validation pass.

## Step 9.4 — Integrate daily generation, finish coverage, and validate rollout

### Daily sequence

Extend daily finalization to execute:

1. complete market, research-operation, fill, accounting, portfolio, and performance phases;
2. generate the current allocation plan;
3. prepare bounded follow-up work;
4. build and validate the deterministic decision snapshot;
5. generate publication CSV exports;
6. generate the investor-facing wiki pages;
7. generate the canonical daily report and investor brief;
8. run strict integrity, reconciliation, schema, wiki, and publication checks;
9. commit the exact data and publication views;
10. build and deploy Quartz from that commit;
11. deliver the committed investor brief to Telegram.

The public site, CSV export, JSON snapshot, daily report, and Telegram message must all refer to the
same committed `snapshot_id`.

### Research coverage

Continue the existing sequential assessment and relationship backfill.

The dashboard must show:

```text
assessments complete / allocation candidates
fresh evidence assessments / allocation candidates
current accepted relationships / required relationships
ready or active strategies
active signals
```

Do not fabricate assessments, strategies, or signals to populate the dashboard.

Do not require a non-cash result for Step 9 completion. The live dashboard may correctly remain
100% cash until the canonical research workflow produces eligible diversified candidates.

### Rollout phases

#### Phase A — Projection and content correctness

Implement and merge:

* decision snapshot;
* generated exports;
* investor-first report structure;
* homepage, portfolio, signals, performance, and system-status Markdown;
* golden tests for all-cash and invested fixtures.

Review the rendered information hierarchy before adding interactive styling.

#### Phase B — Quartz presentation

Implement and merge:

* decision dashboard layout;
* navigation;
* responsive portfolio and signal components;
* copy and local-scaling enhancement;
* performance visualization;
* publication-data copy and verification.

#### Phase C — Live research population

Run the existing bounded sequential research backfill until every maintained allocation candidate
has either:

* a current comparable assessment and current relationship disposition; or
* an explicit evidence-backed ineligible state.

Allow the normal strategy, signal, order, and fill lifecycle to populate the first non-cash model
portfolio. Do not manually seed live strategies or positions for presentation purposes.

### Required tests

Add unit and golden tests for:

* current all-cash portfolio;
* one filled long-equity position;
* multiple filled positions and residual cash;
* pending buy order;
* pending sell or reduce order;
* active signal without an order;
* expired signal;
* stale or superseded allocation plan;
* allocation candidate without a strategy;
* research alert without a signal;
* strategy awaiting order validation;
* foreign-currency position and pending order;
* stale price;
* stale FX;
* market failure affecting only an excluded candidate;
* market failure affecting an open position;
* missing assessment;
* missing or stale relationship;
* negative base-case upside;
* score below the cash hurdle;
* concentration and diversification blockers;
* reason-code translation;
* company-name, ticker, and research-link joins;
* Markdown and HTML escaping of untrusted research text;
* portfolio CSV and actionable-signal CSV generation;
* local long-equity scaling and residual cash;
* options and short positions excluded from automatic scaling;
* mobile rendering;
* no-JavaScript rendering;
* deterministic publication under input permutation;
* exact snapshot consistency across homepage, daily report, exports, and Telegram.

Add property tests proving:

```text
current portfolio reconciles with accounting
approved target cash is non-negative
sum(approved target weights) + cash weight = 100% within tolerance
copy_ready implies a valid non-terminal order
copy_ready implies valid canonical order legs
copy_ready implies fresh required price and FX state
research_alert implies not actionable unless a separate canonical signal exists
unvalidated allocation targets cannot become copy-ready actions
current-position data failure produces blocked status
candidate-only data failure cannot fabricate a blocked current portfolio
generated output cannot change authoritative state
snapshot output is deterministic under input permutation
```

### Definition of done

* [ ] The first screen clearly states the current PaperTrader recommendation.
* [ ] The current model portfolio and approved target portfolio are distinct and reconciled.
* [ ] A user can download or copy the committed model portfolio.
* [ ] Every copy-ready action has passed the strategy, signal, order, market-data, FX, and risk
  boundaries already required by PaperTrader.
* [ ] Research alerts cannot be confused with trade signals.
* [ ] Assessed near misses explain why they did not enter the portfolio.
* [ ] Unresearched securities appear as coverage gaps rather than investment rankings.
* [ ] Human-readable labels replace opaque IDs in investor-facing views.
* [ ] Current research, valuation, invalidation, and review links are available from every
  recommendation.
* [ ] Performance, exposure, cash, and concentration are visible without opening the audit report.
* [ ] Operational failures are separated from investment risks and classified by impact.
* [ ] The all-cash state is complete, explicit, and useful rather than an empty table.
* [ ] The public site remains honest when research coverage is incomplete.
* [ ] The full audit trail remains available.
* [ ] The dashboard, daily report, exports, and Telegram message share one committed snapshot.
* [ ] Static publication works without JavaScript; interactive controls are progressive enhancement.
* [ ] Strict schemas, integrity, wiki lint, accounting reconciliation, typing, formatting, unit,
  property, integration, mobile, build, and link checks pass.
* [ ] No real-order adapter, brokerage credential, personalized portfolio storage, or real-execution
  path is introduced.
