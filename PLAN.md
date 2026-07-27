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
