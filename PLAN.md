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

## Step 2 — Build deterministic market, queue, and accounting core

Implement:

- yfinance retrieval with provider-symbol mapping, retries, freshness checks, market calendars, corporate actions, and normalized daily bars;
- committed rolling price files at `data/market/prices/<security_id>.csv`, merged and truncated to the latest 365 calendar days on each successful update;
- TA-Lib indicators and transition-aware RSI/Bollinger opportunity triggers;
- structured candidate-change packets under `data/wiki/inbox/`, followed by deterministic no-op filtering and a cheap-LLM `ingest|ignore` decision;
- operation enqueueing, dependencies, dedupe keys, cooldowns, claims, leases, retries, terminal history, and run budgets;
- risk checks, signals, normalized order legs, next-open and limit-touch fills, fees, slippage, options multipliers, FX, cash ledger, executions, portfolio, and performance;
- deterministic report scaffolds, structured logs, `log.txt` tail generation, issue state, and `issues.md` generation.

**Exit criteria**

- Repeated runs are idempotent.
- Price files never contain a bar older than the one-year retention boundary.
- One indicator transition creates at most one opportunity within its cooldown.
- The cheap LLM is the final decision maker for whether a validated `data/wiki/inbox/` packet creates `wiki_ingest`.
- A signal cannot mutate the portfolio before a valid deterministic fill.
- Equity, short, and option reference-output tests reconcile cash and P/L exactly.

## Step 3 — Integrate Hermes and reusable project skills

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

- Hermes completes one seeded operation with `--yolo` in a credential-free container.
- Codex or another local harness can run the same skill against a local checkout.
- Operations run strictly one at a time.
- The agent performs permitted changes before writing its result manifest.
- Invalid, stale, malicious, or out-of-scope writes fail the validation gate.
- A no-opportunity or no-strategy outcome is retained as an evidence-linked terminal result.

## Step 4 — Assemble GitHub workflows, reporting, and publication

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

- Scheduled and manual runs use the same code paths and validation gates.
- No LLM operation runs in parallel with another.
- Empty runs do not create empty commits.
- A runtime commit fails if it includes a non-whitelisted path.
- Telegram failure is recorded and retryable without corrupting repository state.
- GitHub Pages renders the canonical wiki and daily reports.

## Step 5 — Validate the complete operating cycle

Exercise the complete system from a clean checkout using manually seeded data: market update, cheap-LLM ingestion decision, opportunity research, wiki update, relationship research, strategy creation, signal, paper order, deterministic fill, portfolio reconciliation, report, commit, Pages build, and Telegram delivery.

Document local skill execution, manual workflow dispatch, queue entry, configuration changes, failed-run recovery, deterministic replay by run ID, and how to add or revise a project skill.

**Exit criteria**

- At least one complete research-to-paper-fill lifecycle succeeds.
- The following rerun creates no duplicate source, operation, signal, order, execution, or wiki page.
- Strict integrity, wiki lint, schema checks, and portfolio reconciliation pass from a clean checkout.
- The public site and Telegram report link to the same committed daily report.
- Both scheduled and manually dispatched workflows succeed.
- No real-trading credential or execution path exists.
