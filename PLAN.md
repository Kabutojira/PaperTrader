# PLAN.md

## Goal

Implement PaperTrader as a public Git-native, Hermes-maintained paper-trading system that converts market monitoring and research into auditable simulated strategies, orders, executions, portfolio results, a compounding Hermes-native LLM wiki, a daily Telegram report, and a Quartz GitHub Pages site.

## Fixed architecture decisions

- The repository is the source of truth and all persistent project data lives under `data/`.
- Legacy data will be imported manually once. Migration and import tooling are outside this plan.
- Hermes uses its bundled native `llm-wiki` skill together with repository-local PaperTrader skills.
- Operations and agents always run sequentially. Parallel agents, fan-out, workflow matrices for LLM work, and future parallelization are out of scope.
- Hermes always runs with `--yolo`; there is no human approval step.
- Project skills are usable both by Hermes and by local agentic harnesses such as Codex for debugging.
- An agent completes every allowed change before finishing. `agent_result.json` records actual changed files, created operations, recorded issues, commands, and validation results; it contains no deferred proposal array.
- Wiki Markdown may be edited directly. Structured CSVs are changed through the project CLI. Fills, executions, cash, portfolio, and performance remain deterministic state transitions.
- Ideas map to securities through explicit many-to-many relationships before strategies are created.
- Signals, orders, executions, cash, portfolio, and performance remain separate states. A signal is not a fill.
- The rolling daily-price cache is committed under `data/market/prices/` and retains only the most recent 365 calendar days.
- A cheap LLM decides whether a validated market or research diff is meaningful enough to enqueue wiki ingestion.
- `portfolio.csv`, reports, `issues.md`, and the 1,000-line `log.txt` are generated views. Append-only ledgers and structured logs retain the audit trail.
- Issues remain entirely in `data/tables/issues.csv` and `data/issues.md`; there is no GitHub Issues synchronization.
- Every GitHub workflow supports manual execution with `workflow_dispatch`.

## Step 1 — Scaffold repository contracts — Complete (2026-07-24)

Create the repository layout from `AGENTS.md`, including package configuration, CLI skeleton, `config.ini`, atomic I/O helpers, CSV and JSON schemas, Hermes-native wiki structure, project skills, tests, and Quartz source configuration.

Initialize `data/wiki/SCHEMA.md`, `data/wiki/index.md`, `data/wiki/log.md`, required domain folders, empty canonical CSVs with validated headers, operation directories, logs, and run directories. Add the automated runtime commit whitelist and a validator that fails when a runtime workflow changes any path outside it.

**Exit criteria**

- [x] A clean checkout installs from pinned dependencies.
- [x] Every canonical CSV exists with the exact schema-defined header.
- [x] Hermes and a local harness can discover the project skills.
- [x] `WIKI_PATH` resolves to `data/wiki`.
- [x] CI runs formatting, typing, schema validation, unit tests, and wiki lint.

Implemented the paper-only CLI and configuration boundary, atomic writers, schema and integrity
validators, runtime commit whitelist, canonical empty data state, Hermes-native wiki, eight
sequential project skills, pinned Python and Quartz dependencies, workflow scaffolds, and Step 1
tests. The full Step 1 validation gate passes locally.

## Step 2 — Build deterministic market, queue, and accounting core — Complete (2026-07-24)

Implement:

- yfinance retrieval with provider-symbol mapping, retries, freshness checks, market calendars, corporate actions, and normalized daily bars;
- committed rolling price files at `data/market/prices/<security_id>.csv`, merged and truncated to the latest 365 calendar days on each successful update;
- TA-Lib indicators and transition-aware RSI/Bollinger opportunity triggers;
- structured candidate-change packets under `data/wiki/inbox/`, followed by deterministic no-op filtering and a cheap-LLM `ingest|ignore` decision;
- operation enqueueing, dependencies, dedupe keys, cooldowns, claims, leases, retries, terminal history, and run budgets;
- risk checks, signals, normalized order legs, next-open and limit-touch fills, fees, slippage, options multipliers, FX, cash ledger, executions, portfolio, and performance;
- deterministic report scaffolds, structured logs, `log.txt` tail generation, issue state, and `issues.md` generation.

**Exit criteria**

- [x] Repeated runs are idempotent.
- [x] Price files never contain a bar older than the one-year retention boundary.
- [x] One indicator transition creates at most one opportunity within its cooldown.
- [x] The cheap LLM is the final decision maker for whether a validated `data/wiki/inbox/` packet creates `wiki_ingest`.
- [x] A signal cannot mutate the portfolio before a valid deterministic fill.
- [x] Equity, short, and option reference-output tests reconcile cash and P/L exactly.

Implemented normalized yfinance market retrieval, exchange calendars, rolling price caches,
durable corporate actions, pinned TA-Lib indicators, transition-aware candidate packets and
classifier decisions, a leased sequential queue, Decimal-safe risk and paper execution, immutable
execution/cash ledgers, generated portfolio/performance/report views, issues, and structured logs.
Golden, property, unit, and full-cycle replay tests cover no-look-ahead fills, options and FX,
cooldowns, recovery, reconciliation, and idempotence. The complete Step 2 validation gate passes
locally.

## Step 3 — Integrate Hermes and reusable project skills — Complete (2026-07-24)

Configure Hermes for GitHub Actions and local execution. Set `WIKI_PATH` to `data/wiki`, register `skills/` as an external skill directory, verify the native `llm-wiki` skill before each run, and always invoke Hermes with `--yolo`.

Implement sequential controller and operation skills for:

- wiki ingest;
- opportunity research;
- idea research;
- security research;
- relationship research;
- strategy research;
- execute strategy.

Agents may edit allowlisted wiki files directly and use the project CLI to update allowed structured state or enqueue follow-ups. Replace the staged approval/applier design with an actual-change manifest in `agent_result.json`. Implement result-schema validation, command auditing, prompt-injection defenses, changed-path validation, and strict post-run integrity checks.

**Exit criteria**

- [x] Hermes completes one seeded operation with `--yolo` in a credential-free container.
- [x] Codex or another local harness can run the same skill against a local checkout.
- [x] Operations run strictly one at a time.
- [x] The agent performs permitted changes before writing its result manifest.
- [x] Invalid, stale, malicious, or out-of-scope writes fail the validation gate.
- [x] A no-opportunity or no-strategy outcome is retained as an evidence-linked terminal result.

Implemented a digest-pinned, isolated Hermes boundary with explicit bundled-skill synchronization,
native `llm-wiki` version and content-hash checks before and after each operation, exact controller
and operation skill selection, mandatory `--yolo`, and one-operation execution bounds. Added
actual-change manifest validation, content and command audit chains, request-file binding,
path/symlink/source-hash and prompt-injection defenses, validated research-state commands,
deterministic order cancellation, evidence-linked no-op terminal results, local-run documentation,
and unit and integration coverage. The hermetic seeded-operation test exercises the complete
one-shot subprocess boundary; a live provider-backed run requires the configured OpenAI Codex
OAuth state and was intentionally not invoked by the offline test suite.

## Step 4 — Assemble GitHub workflows, reporting, and publication — Complete (2026-07-24)

Implement `ci.yml`, `daily.yml`, deterministic, LLM, Pages, and reporting workflows. Every workflow must expose `workflow_dispatch`; reusable workflows may also expose `workflow_call`.

The daily/manual controller executes sequentially:

1. retrieve and normalize market data;
2. update and truncate committed one-year price CSVs;
3. calculate indicators and create candidate change packets;
4. run cheap-LLM ingestion decisions and enqueue material opportunities or wiki ingestion;
5. triage and execute due Hermes operations one at a time with `--yolo`;
6. process eligible paper fills and rebuild portfolio/performance;
7. lint the wiki and run strict integrity checks;
8. generate the canonical daily report;
9. validate the runtime commit whitelist, commit, and push only validated changes;
10. build/deploy Quartz and send the committed report to Telegram.

Manual inputs must include bounded operation selection and debugging controls such as `operation_id`, `operation_type`, `max_operations`, `dry_run`, `publish_pages`, and `send_telegram`. Manual execution is not an approval gate.

**Exit criteria**

- [x] Scheduled and manual runs use the same code paths and validation gates.
- [x] No LLM operation runs in parallel with another.
- [x] Empty runs do not create empty commits.
- [x] A runtime commit fails if it includes a non-whitelisted path.
- [x] Telegram failure is recorded and retryable without corrupting repository state.
- [x] GitHub Pages renders the canonical wiki and daily reports.

Implemented a schema-backed daily run controller, shared sequential Hermes count/cost budget,
market-session-aware fill finalization, deterministic accounting/report publication, and exact
committed-report Telegram delivery with Markdown escaping, bounded retries, redaction, and a
durable resume cursor. The workflow graph uses digest/SHA-pinned dependencies, isolated runtime,
commit, delivery, and Pages boundaries, a hash-verified runtime patch handoff, post-rebase
whitelist validation, and no-empty-commit behavior. Contract tests exercise workflow permissions
and secret partitioning; integration tests cover daily no-op and next-open fill cycles; the full
Python gate and a local Quartz check/build pass. Live inference, push, Pages deployment, and
Telegram delivery require repository secrets/settings and were intentionally not invoked locally.

## Step 5 — Validate the complete operating cycle — Complete (2026-07-24)

Exercise the complete system from a clean checkout using manually seeded data: market update, cheap-LLM ingestion decision, opportunity research, wiki update, relationship research, strategy creation, signal, paper order, deterministic fill, portfolio reconciliation, report, commit, Pages build, and Telegram delivery.

Document local skill execution, manual workflow dispatch, queue entry, configuration changes, failed-run recovery, deterministic replay by run ID, and how to add or revise a project skill.

**Exit criteria**

- [x] At least one complete research-to-paper-fill lifecycle succeeds.
- [x] The following rerun creates no duplicate source, operation, signal, order, execution, or wiki page.
- [x] Strict integrity, wiki lint, schema checks, and portfolio reconciliation pass from a clean checkout.
- [x] The public site and Telegram report link to the same committed daily report.
- [x] Both scheduled and manually dispatched workflows succeed.
- [x] No real-trading credential or execution path exists.

Implemented a clean-checkout, manually seeded operating-cycle integration test that exercises
recorded market normalization, the cheap ingestion decision, five sequential bounded research and
execution operations, wiki/source/relationship/strategy state, signal and pending paper order
creation, a next-session deterministic fill, accounting reconciliation, the canonical report, a
runtime-whitelisted commit handoff, exact committed-report Telegram delivery, and an actual Quartz
build. The same test replays every source, queue request, research upsert, signal, order, fill, and
wiki write and proves their row and page counts remain unchanged. CI and the reusable deterministic
workflow run this publication cycle with Quartz enabled; workflow contract tests cover both the
scheduled and manual controller entry points. Added the operating runbook, completed-session market
filtering, cross-midnight run reporting, replay-safe strategy status handling, canonical CSV Git
attributes, and a safe configurable Quartz build wrapper. Exact locked Python and Node installs,
all 128 tests, strict schema/integrity/wiki/portfolio gates, and the canonical site build pass.
Hosted inference, push, Pages deployment, and Telegram network calls still require repository
settings and secrets; their credential boundaries and deterministic handoffs are validated locally
without exposing a real-trading credential or adding any real-execution adapter.

## Step 6 — Persist OpenAI Codex OAuth state as age ciphertext — Complete (2026-07-24)

Replace the main Hermes API-key path with the `openai-codex` OAuth provider while retaining the
read-only runtime and sole write-enabled commit boundary. Restore `auth.json` only inside the
isolated Hermes home, persist refreshes as one verified age ciphertext artifact, and permit a
credential-only commit after a failed inference without admitting agent-generated data.

**Exit criteria**

- [x] The managed Hermes config and one-shot command force `openai-codex` with a configurable,
  non-empty model and no API-key fallback.
- [x] Non-dry runs restore the exact repository ciphertext with `OPENAI_OAUTH_SECRET`; dry runs do
  not require, decrypt, re-encrypt, upload, or commit OAuth state.
- [x] Changed OAuth plaintext is re-encrypted and byte-verified; unchanged plaintext produces no
  randomized ciphertext churn.
- [x] Runtime failures can cross the write boundary with only the exact encrypted credential path,
  while the failed runtime remains the workflow result.
- [x] Plaintext, private identities, snapshots, symlinks, path traversal, extra artifact files, and
  broad credential-directory writes fail closed.
- [x] Workflow contracts, disposable-age cryptographic tests, the complete Python suite, strict
  integrity/wiki/accounting gates, formatting, lint, and typing pass locally.

Implemented checksum-pinned age installation, isolated restore/status/refresh/cleanup steps, an
exact ciphertext artifact validator, failure-safe commit/rebase behavior, repository ignore and
binary-diff controls, an auth-only CI path filter, operator seeding/recovery documentation, and
focused coverage for wrong identities, invalid ciphertext, no-op refreshes, staging isolation,
secret partitioning, serialization, and cleanup. The repository ciphertext is present but remains
opaque to local validation; a hosted non-dry inference and push still require the repository's
configured `OPENAI_OAUTH_SECRET` and were not invoked from the development checkout.

The 2026-07-25 follow-up corrected the pinned age release assertion to the binary's exact
`v1.3.1` output after verifying the official archive against the pinned SHA-256 checksum.

The 2026-07-27 follow-up corrected the OAuth preflight for Hermes v0.19.0, whose
`hermes auth status openai-codex` command exits successfully even when it reports `logged out`.
The workflow now requires the exact non-sensitive `logged in` status line without logging the
remaining status details, and the configured Codex OAuth model is `gpt-5.6-sol`.

## Step 7 — Add the local Codex harness and execute a researched idea — Complete (2026-07-25)

Add a first-class two-phase boundary for running one repository skill from an existing Codex shell
without Hermes. Preserve the same queue claim, skill identity, command receipt, exact-delta,
manifest-last, post-run validation, and deterministic terminal-transition contracts. Connect a
validated local result to the normal daily finalization path and document copyable idea/security
commands and the implementation architecture.

Exercise that path with the user-supplied solar, storage, and grid-flexibility reset. Retain dated
primary evidence, explicit confirmation and invalidation tests, immutable entity identities, and
only bounded follow-up work; do not force a strategy or paper order without security-specific
valuation and risk evidence.

**Exit criteria**

- [x] `agent harness start` claims at most one operation, records project-skill identities, and
  stores its content-addressed baseline in a private temporary file outside the repository.
- [x] `agent harness finish` validates the exact result and command receipts before the controller
  applies a queue transition; controller artifacts and out-of-scope changes fail closed.
- [x] A prepared local daily run receives the validated outcome and completes the same deterministic
  accounting, report, integrity, wiki, and portfolio phases as the hosted path.
- [x] README and the operating runbook contain copyable local Codex, idea-enqueue, and
  security-identity commands plus a concise development architecture.
- [x] The solar/storage/grid-flexibility idea is maintained with a dated evidence dashboard,
  measurable monitoring gates, contrary evidence, confidence, and a concrete review date.
- [x] Fluence, Atkore, and Enphase research is queued by immutable security ID; no unsupported
  relationship, strategy, signal, order, or fill is created.
- [x] Formatting, lint, typing, all 155 tests, strict schema/integrity/wiki/portfolio checks, and
  workflow contract validation pass locally.

Implemented the local harness CLI and private baseline lifecycle, shared project-skill preflight,
daily batch recording, controller-artifact protections, and safe read-only queue validation. The
first deliberately retained attempt exposed a missing read-only command classification; the
follow-up regression fix passed and the bounded retry completed. The successful daily run
`local-20260725-solar-reset-02` generated the canonical 2026-07-25 report with zero orders or fills
and three ready security-research follow-ups. All validation gates pass without network-dependent
inference or any real-execution path.

# Step 8 — Add opportunity-cost-aware portfolio allocation

## Goal

Prevent PaperTrader from remaining indefinitely at 100% cash whenever no security passes the full high-conviction screening threshold.

Add a separate **baseline allocation sleeve** that invests a bounded portion of available cash in the strongest acceptable candidates, while preserving the existing high-conviction research, strategy, signal, risk, order, fill, and accounting workflow.

Cash remains a valid portfolio allocation rather than an error condition. The allocator must compare candidate securities against the configured cash hurdle and may retain more cash whenever evidence quality, diversification, valuation, market data, or risk constraints are insufficient.

## Fixed architecture decisions

* Do not weaken the existing high-conviction security or strategy gate.
* Divide portfolio exposure into:

  * `conviction`: positions originating from securities that pass the complete strategy gate;
  * `baseline`: smaller positions selected primarily through relative ranking and opportunity-cost management.
* Only securities with fresh research, a defensible valuation range, adequate liquidity, and no hard blocker may enter the baseline sleeve.
* Securities failing because of missing evidence, unsupported valuation, solvency risk, accounting uncertainty, stale prices, stale FX, identity ambiguity, or thesis invalidation remain ineligible.
* Agent research may produce evidence-backed assessment inputs, but deterministic code owns:

  * score aggregation;
  * candidate filtering;
  * ranking;
  * portfolio sizing;
  * caps;
  * cash-reserve enforcement;
  * target generation;
  * quantity calculation;
  * order-risk enforcement.
* The allocation engine does not create executions, fills, cash entries, or portfolio rows.
* Allocation targets enqueue normal `strategy_research` work and continue through the existing signal, `execute_strategy`, order, fill, and reconciliation pipeline.
* Baseline positions must be traceable to an immutable allocation plan.
* All structured mutations use the project CLI.
* Roll out first in `report_only` mode and activate paper allocation only after deterministic and integration tests pass.

## Step 8.1 — Add comparable assessments and complete market inputs

### Configuration

Add an `[allocation]` section to `config.ini` and the matching typed configuration in `src/papertrader/config.py`.

Initial defaults:

```ini
[allocation]
mode = report_only

target_invested_pct = 60
minimum_cash_reserve_pct = 25

maximum_baseline_sleeve_pct = 30
maximum_baseline_position_pct = 5
maximum_sector_pct = 20
maximum_theme_pct = 20

cash_hurdle_score = 60
minimum_confidence = medium
minimum_diversified_candidates = 6
maximum_assessment_age_days = 30

maximum_deployment_per_run_pct = 15
minimum_trade_pct = 1
rebalance_band_pct = 1
```

Supported modes:

* `disabled`
* `report_only`
* `active`

All percentages must use `Decimal`, remain within `[0, 100]`, and satisfy cross-field validation:

* cash reserve must be below 100%;
* baseline sleeve must not exceed target invested exposure;
* baseline position size must not exceed the existing single-position limit;
* deployment per run must not exceed the daily-turnover limit;
* minimum trade size must not exceed the baseline position cap.

### Security assessment contract

Add:

```text
data/tables/security_assessments.csv
```

Columns:

```text
security_id
assessed_at
expires_at
eligibility
confidence
thesis_score
business_quality_score
balance_sheet_score
valuation_score
timing_score
liquidity_score
risk_penalty
downside_pct
base_upside_pct
valuation_horizon_months
hard_blockers
soft_gaps
evidence_refs
run_id
```

Canonical values:

```text
eligibility = ineligible | baseline | conviction
confidence  = low | medium | high
```

Scores and penalties must be integer decimal text within `0–100`.

`downside_pct` and `base_upside_pct` may be negative but must be finite decimal text. `valuation_horizon_months` must be a positive integer.

Add:

```bash
papertrader research assessment upsert --request <json>
```

The command must:

* validate the exact request schema;
* require an existing immutable `security_id`;
* require fresh evidence references;
* reject future-dated assessments;
* reject expiration before assessment;
* validate score ranges;
* validate canonical blocker and gap values;
* prevent an older assessment from replacing a newer one;
* write only through the canonical table layer;
* be idempotent for an identical retry.

### Hard blockers

Use canonical machine-readable blocker values, including:

```text
identity_uncertain
research_stale
valuation_unsupported
market_data_stale
fx_unavailable
liquidity_insufficient
solvency_risk
accounting_uncertain
thesis_invalidated
instrument_unsupported
exchange_unsupported
currency_unsupported
```

A non-empty hard-blocker set always forces `eligibility=ineligible`.

### Soft gaps

Canonical soft-gap examples:

```text
margin_of_safety_below_target
timing_unfavorable
catalyst_missing
valuation_not_compelling
confidence_medium
concentration_sensitive
cyclical_normalization_uncertain
```

Soft gaps may reduce rank or position size but do not automatically disqualify the security.

### Deterministic aggregate score

Add a pure scoring function:

```text
raw_score =
    thesis_score            × 0.25
  + business_quality_score  × 0.20
  + balance_sheet_score     × 0.15
  + valuation_score         × 0.25
  + timing_score            × 0.10
  + liquidity_score         × 0.05
```

Apply confidence:

```text
high   = 1.00
medium = 0.80
low    = 0.50
```

Then calculate:

```text
effective_score =
    raw_score × confidence_multiplier − risk_penalty
```

Candidate edge over cash:

```text
candidate_edge = max(effective_score − cash_hurdle_score, 0)
```

All calculations must use deterministic `Decimal` arithmetic with documented rounding.

### Security research skill

Update `skills/papertrader-security-research/SKILL.md`.

Every completed security research operation must either:

1. write a complete current assessment; or
2. write an ineligible assessment with explicit hard blockers.

The skill must not leave a researched security with no comparable disposition.

A baseline-eligible assessment requires:

* current primary evidence;
* supportable downside and base-case valuation;
* explicit horizon;
* liquidity review;
* balance-sheet review;
* confidence;
* invalidation conditions;
* fresh market data;
* no hard blocker.

### Foreign-exchange market data

Extend the deterministic market-data layer to maintain fresh FX rates for every allowed non-base currency.

Add committed rolling FX data under:

```text
data/market/fx/<currency>_<base_currency>.csv
```

The daily controller must provide `fx_rate_to_base` for:

* open foreign-currency positions;
* pending foreign-currency orders;
* candidate allocation sizing;
* portfolio marks;
* risk references;
* fees and cash effects.

A missing or stale FX rate must exclude a new candidate and defer an existing foreign-currency order without corrupting accounting state.

### Exit criteria

* [ ] Every researched security has a current comparable assessment or an explicit ineligible assessment.
* [x] Hard blockers deterministically exclude a security.
* [x] Assessment updates are idempotent and reject older data.
* [x] Score aggregation produces exact reproducible `Decimal` results.
* [x] All allowed currencies can produce fresh base-currency market references.
* [x] Foreign-currency positions and pending orders no longer fail merely because their currency differs from the portfolio base currency.
* [x] Existing high-conviction research behavior remains valid.
* [x] Schema, integrity, lint, typing, and focused assessment/FX tests pass.

## Step 8.2 — Implement the deterministic allocation engine and order guards

### Allocation engine

Add:

```text
src/papertrader/allocation.py
```

Add the CLI command:

```bash
papertrader allocation plan --run-id <run_id>
```

The engine must read:

* reconciled accounting replay;
* current portfolio marks;
* cash and equity;
* open and pending exposure;
* current strategies and their sleeves;
* securities;
* fresh assessments;
* accepted idea-security relationships;
* sector and theme exposure;
* allocation settings.

It must never read generated allocation output as authoritative input.

### Generated allocation targets

Add:

```text
data/tables/allocation_targets.csv
```

Mark it as a generated table.

Columns:

```text
allocation_plan_id
run_id
as_of
security_id
strategy_id
sleeve
rank
effective_score
candidate_edge
current_weight_pct
pending_weight_pct
target_weight_pct
target_value_base
delta_value_base
disposition
reason
assessment_as_of
```

Canonical dispositions:

```text
open
increase
hold
reduce
close
excluded
below_minimum_trade
```

Add append-only history:

```text
data/tables/allocation_history.csv
```

The history row must preserve the finalized target and reason for every candidate considered in each allocation plan.

### Deployment budget

Calculate:

```text
cash_reserve =
    equity × minimum_cash_reserve_pct / 100

available_cash =
    max(cash − committed_pending_cash − cash_reserve, 0)

target_exposure_gap =
    max(
        equity × target_invested_pct / 100
        − current_gross_exposure
        − pending_gross_exposure,
        0
    )

remaining_baseline_capacity =
    max(
        equity × maximum_baseline_sleeve_pct / 100
        − current_baseline_exposure
        − pending_baseline_exposure,
        0
    )

deployment_limit =
    equity × maximum_deployment_per_run_pct / 100

deployment_budget =
    min(
        available_cash,
        target_exposure_gap,
        remaining_baseline_capacity,
        deployment_limit
    )
```

### Candidate filtering

A security is baseline eligible only when:

* assessment eligibility is `baseline` or `conviction`;
* assessment is not expired or older than the configured age;
* confidence meets the configured minimum;
* hard blockers are empty;
* effective score exceeds the cash hurdle;
* base-case upside is positive;
* downside is finite and explicitly assessed;
* market and FX inputs are fresh;
* security status permits monitoring or trading;
* exchange, currency, and instrument are allowed;
* a current accepted relationship or equivalent evidence-linked thesis exists.

### Diversification rule

The allocator must not concentrate the full baseline sleeve into too few candidates.

Define:

```text
diversification_factor =
    min(
        eligible_candidate_count
        / minimum_diversified_candidates,
        1
    )
```

Then:

```text
diversified_budget =
    deployment_budget × diversification_factor
```

The per-position cap remains authoritative, so fewer eligible securities naturally leave more capital in cash.

### Weight allocation

Allocate the diversified budget proportionally to positive candidate edge.

Use deterministic capped redistribution:

1. calculate each candidate’s provisional share from candidate edge;
2. apply the baseline position cap;
3. apply total security exposure cap;
4. apply sector cap;
5. apply theme cap;
6. apply currency cap when configured;
7. redistribute remaining budget among uncapped candidates;
8. repeat until no budget can be allocated without violating a constraint;
9. round target quantities downward so the cash reserve cannot be breached.

The algorithm must be deterministic regardless of input-row ordering.

Ties must be broken by immutable `security_id`.

### Existing positions

The allocator may control only positions linked exclusively to baseline strategies.

For baseline positions:

* a still-eligible candidate may be held or resized;
* a candidate inside the rebalance band produces `hold`;
* a hard blocker, expired assessment, or thesis invalidation produces target weight zero;
* a lower rank may produce a reduction;
* a position may be closed when its capital has a better eligible use.

The allocator must not automatically reduce or close a conviction position. Conviction positions remain governed by their strategy signals and risk rules.

### Queue handoff

In `active` mode, a non-zero material target delta must enqueue a normal `strategy_research` operation.

The payload must include:

```json
{
  "mode": "baseline_allocation",
  "allocation_plan_id": "<immutable plan id>",
  "security_id": "<security id>",
  "strategy_id": "<stable baseline strategy id>",
  "current_weight_pct": "<decimal>",
  "target_weight_pct": "<decimal>",
  "maximum_weight_pct": "<decimal>",
  "selection_rank": "<integer>",
  "effective_score": "<decimal>",
  "assessment_as_of": "<UTC timestamp>"
}
```

Use a stable baseline strategy identity per security so repeated plans update one strategy rather than creating unlimited strategies.

Queue requests must use deterministic dedupe keys containing the strategy, allocation plan, and desired disposition.

In `report_only` mode, write targets and history but enqueue no strategy, signal, or execution work.

### Strategy metadata

Extend `strategies.csv` with:

```text
sleeve
allocation_plan_id
```

Canonical sleeve values:

```text
conviction
baseline
```

Existing strategies migrate to `conviction`.

A baseline strategy must retain the allocation plan that most recently established its target.

### Order guards

Strengthen `papertrader order create`.

Before an order is accepted:

* submitted legs must match the canonical strategy legs;
* the strategy must be orderable;
* strategy `risk_budget_pct` must be enforced against current equity;
* a baseline strategy must have a current allocation target;
* the allocation plan must not be stale;
* projected baseline exposure must not exceed its target plus rounding tolerance;
* the baseline position cap must be enforced;
* the minimum cash reserve must remain intact;
* current pending orders must be included;
* concentration, turnover, gross exposure, and existing risk limits must still pass.

Deterministic code must calculate equity quantity from target value and fresh reference price.

The LLM may recommend structure and explain the decision, but it must not choose an unconstrained final quantity.

### Exit criteria

* [x] Allocation results are identical for identical inputs regardless of row ordering.
* [x] Total target exposure never exceeds the configured limits.
* [x] Target cash never falls below the minimum reserve.
* [x] Baseline exposure never exceeds the baseline sleeve cap.
* [x] Per-security, sector, theme, turnover, and gross-exposure caps are enforced.
* [x] Fewer eligible candidates result in partial deployment rather than forced concentration.
* [x] Hard-blocked securities receive zero target allocation.
* [x] Conviction positions are not managed by the baseline allocator.
* [x] Pending orders are included in projected cash and exposure.
* [x] Strategy risk budgets and canonical legs are enforced at order creation.
* [x] `report_only` mode cannot create operations, signals, orders, fills, or accounting changes.
* [x] Unit, property, and golden allocation tests pass.

## Step 8.3 — Integrate baseline strategy research and execution

### Strategy research skill

Update `skills/papertrader-strategy-research/SKILL.md` to support:

```text
mode = conviction | baseline_allocation
```

For baseline allocation, require:

* valid allocation-plan identity;
* current target weight;
* current assessment;
* fresh price and FX inputs;
* explicit soft gaps;
* explicit reason the security did not qualify as a conviction strategy;
* thesis;
* downside case;
* base case;
* invalidation;
* review date;
* exit conditions;
* target-size limit.

The strategy page must explain why the candidate is preferable to retaining that portion of the portfolio in cash.

A baseline strategy must use equity in the first implementation. Options, shorts, leverage, and multi-leg structures remain reserved for conviction strategies.

The skill may create a signal only when:

* the allocation plan remains current;
* target delta exceeds the minimum-trade threshold;
* no new hard blocker exists;
* market and FX data remain fresh;
* all normalized strategy fields are complete.

### Execute-strategy skill

Update `skills/papertrader-execute-strategy/SKILL.md`.

For a baseline action, the skill must:

* read the latest allocation target;
* verify the plan has not been superseded;
* use the deterministic target quantity;
* refuse any quantity above the target;
* preserve the minimum cash reserve;
* create only the action indicated by the target:

  * `open`;
  * `increase`;
  * `reduce`;
  * `close`;
  * `hold`.
* skip without mutation when the target is within the rebalance band.

The deterministic order command remains the final authority.

### Controller and result validation

Update the controller skill and result validator so allocation-linked strategy operations may change only:

* the relevant strategy page;
* strategy and strategy-leg state through the CLI;
* one eligible signal through the CLI;
* bounded issue and follow-up state;
* the operation result artifact.

They may not directly change:

* allocation targets;
* allocation history;
* portfolio;
* cash;
* executions;
* fills;
* performance.

### Exit criteria

* [x] Baseline strategy research uses the same evidence and identity boundaries as conviction research.
* [x] Baseline strategies explicitly document their lower-conviction status.
* [x] Baseline strategies are equity-only.
* [x] No agent can override the deterministic target quantity.
* [x] Superseded allocation plans cannot create new orders.
* [x] Hold targets create no signal or order churn.
* [x] Reduce and close targets use the normal signal and execution lifecycle.
* [x] Existing conviction strategy behavior and tests remain unchanged.
* [x] Skill preflight, manifest validation, command auditing, and changed-path validation pass.

## Step 8.4 — Add daily orchestration, reporting, and staged activation

### Daily sequence

Extend the daily controller to execute:

1. initialize accounting;
2. update securities and FX market data;
3. update indicators and opportunity packets;
4. run bounded sequential research operations;
5. process previously eligible pending orders;
6. accrue actions and rebuild the reconciled portfolio;
7. update performance;
8. generate the current allocation plan;
9. enqueue baseline strategy work only when allocation mode is `active`;
10. prepare the queue for the next run;
11. generate the daily report;
12. run strict validation and publication.

Allocation planning occurs after fills and portfolio rebuild so it uses the final reconciled end-of-run state.

New allocation work normally executes in the next daily run. Do not combine fresh assessment, allocation, strategy creation, signal creation, order creation, and fill into one uncontrolled operation chain.

### Daily report

Add an allocation section showing:

```text
Allocation mode
Cash
Minimum cash reserve
Current invested exposure
Target invested exposure
Current conviction exposure
Current baseline exposure
Maximum baseline exposure
Deployment budget
Capital allocated this plan
Capital left unallocated
Eligible candidate count
Excluded candidate count
```

Candidate table:

```text
Rank
Security
Sleeve
Effective score
Current weight
Pending weight
Target weight
Delta
Disposition
Reason
Assessment date
```

The report must explicitly state why cash remains unallocated, including:

* insufficient eligible candidates;
* candidate scores below cash hurdle;
* hard blockers;
* stale assessments;
* stale prices or FX;
* concentration caps;
* deployment limit;
* turnover limit;
* minimum-trade threshold.

### Shadow rollout

#### Phase A — Report only

Run at least five completed daily cycles with:

```ini
mode = report_only
```

Requirements:

* no allocation-generated queue rows;
* no allocation-generated signals or orders;
* stable results for identical inputs;
* no cash-reserve or concentration violations;
* reports explain every unallocated amount;
* strict reconciliation passes.

#### Phase B — Active paper allocation

Enable:

```ini
mode = active
```

Initially retain:

```text
maximum_baseline_sleeve_pct = 30
maximum_baseline_position_pct = 5
maximum_deployment_per_run_pct = 15
minimum_cash_reserve_pct = 25
```

Review these only through explicit configuration changes after observing paper performance and behavior. Do not let an agent modify the limits.

### Required tests

Add focused tests for:

* assessment schema and lifecycle;
* hard and soft blockers;
* score aggregation;
* FX freshness and conversion;
* no eligible candidates;
* one eligible candidate;
* fewer than minimum diversified candidates;
* tied candidate scores;
* capped proportional redistribution;
* sector and theme concentration;
* existing conviction exposure;
* existing baseline exposure;
* pending orders;
* stale plans;
* stale assessments;
* minimum trade threshold;
* reserve enforcement;
* strategy risk-budget enforcement;
* canonical strategy-leg matching;
* report-only non-mutation;
* baseline open, increase, hold, reduce, and close;
* deterministic reruns;
* full daily integration from 100% cash to staged baseline exposure.

Add property tests proving:

```text
cash_after_targets >= required_cash_reserve
baseline_exposure <= maximum_baseline_sleeve
security_exposure <= maximum_single_position
sum(target_values) <= deployment_budget
targets are deterministic under input permutation
all excluded or hard-blocked candidates have target zero
```

### Reference integration scenario

Using €100,000 initial paper equity, no positions, no pending orders, at least six eligible candidates, and the initial configuration:

* required cash reserve: at least €25,000;
* maximum baseline sleeve: €30,000;
* maximum position: €5,000;
* maximum first-run deployment: €15,000;
* first active plan allocates no more than €15,000;
* subsequent plans may increase baseline exposure toward €30,000;
* unused capital remains cash until conviction strategies or additional eligible baseline candidates are available.

The exact selected securities must depend only on current assessments and deterministic ranking, not on hard-coded ticker preferences.

## Definition of done

* [x] PaperTrader distinguishes conviction and baseline portfolio exposure.
* [x] The existing screening threshold is not weakened.
* [x] Cash is an explicit portfolio alternative with a configurable hurdle and reserve.
* [ ] Every researched security has a comparable current assessment or an explicit blocker.
* [x] Foreign-currency securities can be marked, sized, risk-checked, filled, and reconciled with fresh FX data.
* [x] The allocation engine is deterministic, Decimal-safe, idempotent, and order-independent.
* [x] Allocation sizing is owned by code rather than the LLM.
* [x] Baseline orders cannot exceed their allocation targets or strategy risk budgets.
* [x] Baseline allocation cannot bypass existing risk, order, fill, accounting, or reconciliation boundaries.
* [x] Report-only mode is deterministically covered without creating trading state; the operator
  explicitly waived five live shadow cycles for this rollout.
* [x] The daily report explains both invested and intentionally uninvested cash.
* [x] A clean-checkout integration cycle can move from 100% cash to staged diversified baseline paper exposure.
* [x] A repeated cycle creates no duplicate assessment, allocation plan, strategy, signal, order, execution, or history record.
* [x] Formatting, lint, strict typing, schemas, integrity, wiki lint, all tests, portfolio reconciliation, and workflow contract validation pass.
* [x] No real-order adapter, brokerage credential, or real-execution path is introduced.

## Step 8 implementation status — 2026-07-27

The deterministic implementation, contracts, skills, daily integration, reference output, and
validation gates are complete. Security research may now register bounded source metadata and is
required to leave a current evidence-backed assessment even when skipped. Allocation maintenance
derives its universe from canonical researched security pages, enqueues stable assessment and
relationship refresh work, and exposes strict readiness coverage. Allocation reports include
researched securities that lack assessments while excluding identity-only watchlist rows.

The operator explicitly waived the original five-live-cycle shadow requirement. Accordingly, the
versioned default is `active` without changing the 25% cash reserve, 30% baseline sleeve, 5%
position cap, or 15% per-run deployment limit. Active mode remains fail-closed: a security without
a current registered-evidence assessment and current accepted relationship receives a zero target,
so activation cannot force an investment.

The repository's 24-security live assessment/source/relationship backfill remains an operational
data task rather than a code-completion shortcut. It must be processed sequentially through the
configured inference harness; no score or valuation may be inferred from legacy prose. Strict
`allocation readiness` remains red until that evidence-backed work and every backfill terminal
state are complete. Hosted inference, publish, push, and Telegram delivery still require their
configured external credential and post-commit boundaries.

## Daily Hermes execution follow-up — Complete (2026-07-27)

The failed hosted daily run was reproduced with the workflow's pinned Hermes v0.19.0 image,
isolated OAuth state, and one sequential operation. The container launcher deliberately drops the
Hermes subprocess from the root controller to UID/GID 10000, but controller-created repository
data used owner-only modes. Hermes therefore could not read the queue, payload, or wiki inputs and
could not create `agent_result.json`, even though its launcher returned zero.

Before taking the repository snapshot, the controller now hands off only the repository-local
`data/` tree to the non-root Hermes profile owner when the controller itself is root. The handoff
rejects symlinks and non-regular filesystem entries and does not expose `.git`, source code, the
encrypted age identity, or other controller-owned credential state. Hermes remains unprivileged.
The configured turn bound is 90 so a valid result manifest can still be written after bounded
integrity repair, and controller/operation instructions require a new immutable JSON request file
for every corrected CLI retry. Allocation readiness is recognized as an allowed read-only
verification command without weakening mutation-scope validation.

A fresh pinned-container run then completed exactly one operation with exit code zero and a
`succeeded` result. The controller accepted the manifest with no validation errors, including the
repository diff, command audit, distinct corrected request artifacts, strict schema/queue/wiki/
integrity checks, and unchanged accounting state.

## GitHub Pages link-integrity follow-up — Complete (2026-07-27)

The deployed Pages artifact contained 15 dead internal references from the homepage, wiki log, and
daily report to five canonical `inbox/` packets. Those Markdown packets were public and linked from
the complete wiki catalog, but Quartz excluded the entire folder from its emitted artifact. Quartz
now publishes `inbox/` while continuing to exclude `_archive/` and `.gitkeep` files.

Every site build now runs a deterministic post-build link check across generated HTML `href` and
`src` attributes. It understands extensionless Quartz routes, directory indexes, assets, and both
root and project GitHub Pages base URLs; same-host links that escape the configured project subpath
or resolve to missing artifacts fail the build. The rebuilt canonical wiki emits all five packet
targets and passes the link check with no dead internal links.

## Results-first Quartz homepage — Complete (2026-07-27)

The canonical wiki index now starts with a deterministic current-results block before the content
catalog. It links the latest daily report, shows the newest generated cash, equity, exposure,
realized and unrealized P/L, daily and cumulative return snapshot, and lists every current paper
position with marks and valuation. An all-cash portfolio is stated explicitly rather than implied
by an empty table.

The same block shows the three newest successful or skipped operation-history conclusions with
bounded summaries and links to maintained entity pages where available. Daily report generation
refreshes the block after registering the new report, and `papertrader wiki refresh-homepage`
provides an idempotent deterministic rebuild from canonical tables and history. The current live
index has been regenerated, strict wiki lint passes, and Quartz renders the results before the Meta
and catalog sections with no broken generated-site links.

## Inbox clarity, classifier recovery, and rich Telegram delivery — Complete (2026-07-27)

Candidate packet generation now resolves each immutable security ID through `securities.csv`.
Quartz catalog entries and page titles use the human-readable `[TICKER] Indicator state` form, and
each packet links the ticker and instrument name to its maintained security page. Existing packets
were reproducibly regenerated with their canonical facts embedded in frontmatter so blocked or
pending decisions can be retried without reconstructing old market bars. Strict wiki lint now
recognizes the generated internal Markdown catalog links, and the complete Quartz build verifies
that the rendered homepage and security links resolve.

The classifier is configured as a closed stdin/stdout bridge to one tool-free, `--yolo` Hermes
turn using the isolated `openai-codex` OAuth profile and the cost-sensitive `gpt-5.6-luna` model.
Every non-dry runtime restores OAuth even when no full Hermes operations were selected. Daily
preparation retries old blocked or pending candidates sequentially, validates the exact
`ingest|ignore` result contract, resolves recovered classifier issues, and enqueues wiki ingestion
only after a final `ingest` decision. The pinned container's CLI flags and Luna model catalog were
verified locally; live transmission of the existing packets was denied by the execution boundary,
so their first authorized non-dry daily run remains responsible for recording their final model
decisions.

Post-commit delivery now calls Telegram's rich-message endpoint and passes the canonical report as
GitHub-compatible Rich Markdown. YAML frontmatter is omitted, headings, lists, emphasis, code, and
tables remain formatted, wiki references become commit-pinned links, and complete Markdown blocks
are kept together when a report must be split. Delivery retry cursors and secret redaction remain
unchanged. Unit, integration, strict wiki, generated-site link, typing, lint, and full test gates
cover the new behavior.
