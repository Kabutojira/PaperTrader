# PaperTrader implementation plan

## Step 1 — Scaffold repository contracts — Complete (2026-07-24)

Established the paper-only repository structure, configuration and CLI boundaries, canonical schemas and empty data state, atomic writes, integrity checks, runtime commit whitelist, Hermes-native wiki, project skills, pinned dependencies, workflow scaffolds, and initial test suite.

## Step 2 — Build deterministic market, queue, and accounting core — Complete (2026-07-24)

Implemented normalized market retrieval, rolling price data, indicators and candidate packets, sequential queue processing, deterministic classification, Decimal-safe risk and paper execution, append-only accounting ledgers, generated portfolio and performance views, reporting, issues, logs, and replay-safe test coverage.

## Step 3 — Integrate Hermes and reusable project skills — Complete (2026-07-24)

Integrated pinned and isolated Hermes execution with the native `llm-wiki` skill and repository skills, mandatory sequential `--yolo` operation handling, actual-change result manifests, command and content auditing, prompt-injection defenses, strict path validation, and evidence-linked terminal outcomes.

## Step 4 — Assemble GitHub workflows, reporting, and publication — Complete (2026-07-24)

Built the serialized daily and reusable workflows for deterministic preparation, bounded Hermes operations, fills and reconciliation, canonical report generation, validated runtime commits, Quartz publication, and retryable Telegram delivery with isolated credentials and manual-dispatch support.

## Step 5 — Validate the complete operating cycle — Complete (2026-07-24)

Validated a clean-checkout research-to-paper-fill lifecycle covering market normalization, classification, sequential research, wiki and structured-state updates, strategy execution, next-session fills, accounting reconciliation, report publication, Telegram delivery, Quartz builds, deterministic replay, and idempotence.

## Step 6 — Persist OpenAI Codex OAuth state as age ciphertext — Complete (2026-07-24)

Replaced the Hermes API-key path with isolated `openai-codex` OAuth, restoring plaintext only inside the runtime boundary and persisting verified refreshes as one age-encrypted artifact, with failure-safe credential-only commits, strict cleanup, and no API-key fallback.

## Step 7 — Add the local Codex harness and execute a researched idea — Complete (2026-07-25)

Added a two-phase local Codex harness that preserves queue claims, skill identity, command receipts, exact-delta validation, manifest-last completion, and daily finalization contracts, then used it to research the solar, storage, and grid-flexibility thesis and enqueue bounded security follow-ups without forcing unsupported trades.

## Step 8 — Add opportunity-cost-aware portfolio allocation — Complete (2026-07-27)

Added evidence-backed security assessments, deterministic Decimal-safe candidate scoring and baseline allocation, FX support, immutable allocation plans, sleeve-aware strategies and order guards, daily reporting and readiness checks, while retaining cash hurdles, diversification limits, staged exposure caps, and the existing conviction and accounting controls.

## Follow-up — Repair daily Hermes execution — Complete (2026-07-27)

Reproduced the hosted failure and fixed the root-to-unprivileged runtime handoff so Hermes can safely read repository data and write its result manifest without receiving source, Git metadata, or credentials; a fresh pinned-container run then completed and passed all controller validation.

## Follow-up — Enforce GitHub Pages link integrity — Complete (2026-07-27)

Published the linked inbox packets and added a deterministic post-build checker for generated HTML routes, assets, directory indexes, and project Pages base paths, eliminating the dead internal links and making future broken references fail the build.

## Follow-up — Make the Quartz homepage results-first — Complete (2026-07-27)

Made the homepage lead with the latest report, current cash, equity, exposure, P/L, returns, positions, and recent operation conclusions, backed by an idempotent deterministic refresh command and canonical tables rather than manually maintained summaries.

## Follow-up — Clarify inbox entries, recover classification, and enrich Telegram delivery — Complete (2026-07-27)

Changed candidate titles to human-readable ticker and indicator labels with security links, added retryable tool-free Hermes classification through the isolated OAuth profile, and upgraded Telegram delivery to rich Markdown with frontmatter removal, commit-pinned wiki links, block-aware splitting, retries, and secret redaction.

## Step 9 — Publish an investor-facing decision dashboard and copyable model portfolio — Complete (2026-07-27)

Added a deterministic, schema-validated decision snapshot and publication exports; results-first portfolio, signal, performance, system-status, and research pages; investor-focused daily and Telegram briefs; and a responsive Quartz dashboard with downloadable data and local-only long-equity scaling. The views distinguish filled holdings, projected validated orders, candidates, and research alerts, preserve an explicit all-cash recommendation when gates are unmet, share one auditable snapshot identity, and cannot feed generated advice back into trading or accounting state.

## Step 10 — Separate investment readiness from operational health — Complete (2026-07-28)

Split the former aggregate data status into investment-data and operations/delivery health, counted current rejected relationships as completed reviews, and kept research backlog and Telegram failures visible without falsely degrading the investment evidence.

## Step 11 — Enforce payoff-aware entries and pending-order discipline — Complete (2026-07-28)

Required at least 10% base-case upside and a 1:1 upside-to-downside ratio in addition to the cash hurdle, enforced the gates across allocation, strategy, signal, order, and pre-fill validation, and prevented repeated deployment tranches while a baseline order remains pending.

## Step 12 — Resize capital and introduce performance epochs — Complete (2026-07-28)

Reduced current model equity to 10,000 EUR through an append-only 90,000 EUR withdrawal, preserved the original capital ledger and historical returns, and added immutable flow-adjusted performance epochs for future contributions or withdrawals.

## Step 13 — Make security and FX evidence directly inspectable — Complete (2026-07-28)

Added a dedicated Securities dashboard and direct ticker-to-security links, exposed native and EUR marks with conversion rates and separate market/FX timestamps, retained distinct strategy links, and removed disclaimer-style prose from investor-facing pages.

## Step 14 — Guarantee latest-only end-of-run Telegram delivery — Complete (2026-07-28)

Kept formatted Rich Markdown delivery after the runtime commit, added bot/destination preflight, consolidated failures into one stable latest-only issue, added committed local-run delivery, and explicitly prevented replay of older missed reports.

## Step 15 — Run daily at 17:00 Europe/Rome and reconcile publication — Complete (2026-07-28)

Changed the seven-day schedule to timezone-aware 17:00 Europe/Rome, migrated live pending ISRG state to cash after the new payoff gates rejected it, regenerated the canonical snapshot and investor pages, and validated the complete application and Quartz publication.

## Step 16 — Merge research alerts, add quick checks, and publish a daily podcast — Complete (2026-07-30)

Merged distinct same-security and repeat-day alert causes into one pre-claim research payload with rising priority; introduced bounded quick checks for securities fully reviewed within ten days, including deterministic escalation back to standard research; and added a final sequential daily podcast operation that collects accepted run changes, writes an evidence-grounded long-form script, uses scoped Hermes TTS, validates and assembles a roughly twenty-minute MP3, and remains one-way from investment decisions.

## Step 17 — Preserve and compare research revisions — Planned

### Outcome

Every security refresh explicitly consumes the previous maintained research and previous assessment, then records what changed and why. Old research remains queryable without depending on manual Git-history inspection.

### Implementation

1. Add an append-only structured assessment history contract, for example `data/tables/security_assessment_history.csv`, keyed by immutable `assessment_id`. Keep `security_assessments.csv` as the current projection.
2. When `papertrader research assessment upsert` accepts a new assessment:
   - append the accepted version to history exactly once;
   - link it to `previous_assessment_id` when one exists;
   - record the source operation, result path, research-page content hash, and assessment schema version;
   - update the current projection only after the history append validates.
3. Add a read-only CLI command such as `papertrader research security-context --security-id <id>` that returns a bounded JSON context containing:
   - current security identity and page;
   - current and previous assessment;
   - latest successful security-research operation and result path;
   - linked ideas, accepted/rejected relationships, strategies, and retained source records;
   - previous page hash and current page hash.
4. Update `papertrader-security-research/SKILL.md` to require a **Changes since prior review** section covering:
   - changed facts and evidence;
   - changed assumptions;
   - changed bear/base/bull valuation inputs and outputs;
   - thesis upgrades or downgrades;
   - catalysts, risks, blockers, and gaps added, resolved, or unchanged;
   - rating and portfolio-action changes;
   - conclusions that remain unchanged and why.
5. Apply the same revision discipline to idea refreshes when a completed security review changes the candidate universe or idea conclusion. Do not overwrite contradictory historical claims without preserving dates, sources, and confidence.
6. Update `AGENTS.md`, `data/wiki/SCHEMA.md`, research catalog generation, integrity checks, and wiki lint for the new history and change-summary contract.

### Acceptance criteria

- A second research run cannot succeed without reading the previous structured assessment and most recent successful research result when they exist.
- The current page contains an explicit delta from the prior review rather than silently replacing it.
- Replaying an identical accepted assessment creates no duplicate history row.
- A historical assessment can be retrieved by immutable ID after any number of later updates.
- Tests cover first research, unchanged refresh, materially changed refresh, contradiction preservation, stale prior evidence, and retry idempotence.

## Step 18 — Introduce scenario-complete valuation and anchored research rubrics — Planned

### Outcome

Security research produces internally consistent bear, base, and bull cases with explicit assumptions, probabilities, fair values, returns, and a probability-weighted conclusion. Unsupported valuation is represented honestly rather than with artificial `-100/0` placeholders.

### Assessment version 2

Replace the ambiguous two-number valuation contract with a versioned scenario contract containing at least:

- `valuation_method` and `valuation_template`;
- current reference price, currency, and market-data timestamp;
- valuation horizon;
- bear fair value, return, probability, and key assumptions;
- base fair value, return, probability, and key assumptions;
- bull fair value, return, probability, and key assumptions;
- probability-weighted fair value and expected return;
- confidence-adjusted expected return;
- buy-below price and margin of safety;
- research completeness state;
- component scores, confidence, hard blockers, soft gaps, evidence references, and run identity.

The CLI must calculate or validate every derived field. The agent supplies scenario assumptions, fair values, and probabilities; it does not hand-calculate canonical returns, expected values, margin of safety, or final ratings.

### Required validation

- Probabilities are integer or canonical decimal percentages, non-negative, and sum exactly to 100.
- `bear_fair_value <= base_fair_value <= bull_fair_value`.
- `bear_return_pct <= base_return_pct <= bull_return_pct` within Decimal tolerance.
- Returns reconcile exactly to the current reference price.
- Expected fair value and expected return reconcile to scenario probabilities.
- The price and FX references are fresh and match the immutable instrument identity.
- A valuation marked unsupported stores no invented fair value or return and receives `Unrated` until the blocker is resolved.
- Rename the old `downside_pct` concept to `bear_return_pct`; a deeply undervalued security may legitimately have a positive bear-case return.

### Valuation templates

Add explicit prompt and validation templates for at least:

- mature compounder;
- cyclical or commodity producer;
- financial company;
- pre-profit growth company;
- biotechnology or binary-outcome company;
- private or illiquid security;
- fallback/other with a required explanation.

Each template defines the minimum primary evidence, acceptable valuation methods, normalization rules, dilution/debt treatment, scenario drivers, and when valuation must remain unsupported.

### Anchored score rubrics

Define repository-owned scoring anchors for thesis, business quality, balance sheet, valuation, timing, liquidity, and risk. A score of 20, 40, 60, 80, or 100 must have a concrete interpretation. Add examples and boundary fixtures so different research runs remain comparable.

### Acceptance criteria

- No assessment can be accepted with unordered scenarios, inconsistent returns, probabilities not totaling 100, stale price/FX inputs, or an unknown valuation template.
- Every completed supported valuation has bear, base, bull, expected, and buy-below outputs.
- Every unsupported valuation explains the exact missing evidence or unsuitable method and is `Unrated` rather than assigned fake extreme returns.
- Golden fixtures cover at least one security from every valuation template.

## Step 19 — Recalibrate ratings, eligibility, scoring, and allocation — Planned

### Outcome

Research quality, security attractiveness, allocation eligibility, and conviction are separate concepts. Attractive synthetic candidates can pass, weak candidates fail for precise reasons, and a zero-position result remains possible without being caused by mathematical double penalties.

### Separate the current overloaded assessment state

Replace the current `ineligible / baseline / conviction` field with independent dimensions:

- `research_status`: `complete | partial | unsupported | stale`;
- `allocation_eligibility`: deterministically derived `eligible | ineligible`;
- `conviction_tier`: `watch | baseline | conviction`.

A security may have complete, comparable research and remain allocation-ineligible. A valuation-unsupported security is not automatically described as merely unattractive.

### Rebuild the decision formula

1. Separate security quality from expected return and from portfolio constraints.
2. Remove accidental double counting where the same risk lowers component scores, lowers confidence, adds a risk penalty, creates a blocker, and fails a payoff gate.
3. Use confidence to shrink uncertain expected returns toward zero or reduce sizing/rank, rather than making broad classes of medium-confidence candidates mathematically unable to clear the cash hurdle.
4. Retain explicit hard blockers for identity, stale research, unsupported valuation, stale market/FX, liquidity, solvency, accounting, thesis invalidation, or unsupported instruments.
5. Replace or supplement the opaque score-only cash hurdle with configurable economic gates based on:
   - confidence-adjusted expected return;
   - base-case return;
   - bear/base and expected/bear payoff ratios;
   - margin of safety;
   - minimum confidence;
   - current accepted relationship;
   - absence of hard blockers.
6. Keep the weighted quality score for ranking and sizing, but publish every component and contribution.
7. Implement the full conviction gate once in deterministic code and reuse it from research, strategy, signal, order, and pre-fill validation. Skills describe the gate; they do not reinterpret it.
8. Add an **eligibility frontier** for every excluded candidate: distance from the expected-return threshold, base-return threshold, payoff ratio, confidence requirement, relationship completion, and each blocker.

### All-cash semantics

Derive one of these evidence states alongside the portfolio stance:

- `definitive_cash_preference`: coverage is complete and no candidate clears the economic gates;
- `provisional_cash_research_incomplete`: potentially relevant assessment or relationship work remains incomplete;
- `provisional_cash_valuation_unsupported`: candidates cannot yet be compared because valuation is unsupported;
- `provisional_cash_strategy_pending`: allocation passed but strategy/signal work is not complete;
- `portfolio_blocked`: accounting, market, or operational state prevents a safe decision.

The headline may still be “No trade — hold 100% cash,” but it must include the evidence state and the most important reason.

### Calibration

- Build a deterministic calibration fixture set containing clearly attractive, fair, unattractive, distressed, incomplete, and illiquid examples.
- Replay the current maintained universe through both the old and new formulas and publish a comparison artifact for review.
- Do not require the live universe to produce a trade. Require only that obviously attractive fixtures can pass and that no group is structurally impossible to qualify solely because of confidence arithmetic.

### Acceptance criteria

- Medium-confidence candidates are not mathematically excluded by construction.
- Hard blockers, valuation unattractiveness, relationship gaps, and strategy gaps produce distinct classifications.
- The allocator can still choose 100% cash, but its reason is definitive or provisional and machine-readable.
- Every allocation, signal, order, and fill gate uses the same canonical eligibility calculation.

## Step 20 — Publish canonical ratings, actions, near misses, and a research benchmark — Planned

### Outcome

Each researched security has a clear investor conclusion, while portfolio actions remain context-aware and the strict approved portfolio remains separate from research exploration.

### Canonical investment rating

Add a deterministic rating enum:

- `strong_buy`;
- `buy`;
- `hold`;
- `sell`;
- `strong_sell`;
- `unrated`.

Store the rating thresholds in configuration and derive the rating from scenario returns, probability-weighted expected return, confidence, thesis state, and explicit risk rules. The LLM writes the evidence and explanation; deterministic code assigns the canonical rating.

### Portfolio action

Derive a separate context-aware action:

- `initiate`;
- `add`;
- `hold`;
- `trim`;
- `exit`;
- `avoid`;
- `watch`;
- `short_candidate` when the strategy and risk mandate explicitly support it.

A `Buy` rating may map to `Hold` when the approved target is already reached. A `Hold` rating may map to `Trim` because of concentration. A `Sell` rating for an unowned security does not automatically authorize a short.

### Required research conclusion

Every security page and investor-facing candidate row must include one concise sentence in this form:

> **Rating: Buy. Portfolio action: Watch for entry below X.** Bear/base/bull returns are A/B/C over N months; probability-weighted expected return is D with medium confidence. Upgrade or downgrade conditions: …

Use `Unrated` when a supportable valuation is unavailable.

### Publication changes

1. Introduce decision snapshot schema version 3 and extend model-portfolio, candidate, security-catalog, daily-report, Telegram, and CSV exports with:
   - bear/base/bull fair values and returns;
   - probabilities and expected return;
   - buy-below price;
   - rating and portfolio action;
   - evidence state;
   - eligibility-frontier distances;
   - “what would change the rating” conditions.
2. Replace broad candidate classifications with precise states such as:
   - `approved`;
   - `valuation_attractive`;
   - `valuation_unattractive`;
   - `valuation_unsupported`;
   - `liquidity_blocked`;
   - `solvency_blocked`;
   - `relationship_pending`;
   - `strategy_pending`;
   - `research_incomplete`;
   - `market_data_blocked`.
3. Always publish the top near misses even when the approved portfolio is all cash. Show failed gates, threshold distances, attractive entry price, decisive catalyst, next review date, and the exact condition needed to become eligible.
4. Add a separately generated **research benchmark portfolio** for measurement only:
   - clearly label it non-approved and non-copy-ready;
   - use a deterministic, simple policy such as equal-weighting the highest-rated supportable candidates within broad diversification caps;
   - create no strategies, signals, orders, fills, or accounting entries;
   - track its hypothetical performance separately from the approved portfolio;
   - prohibit every benchmark output from becoming an allocation input.

### Acceptance criteria

- Every supported security assessment has exactly one rating and one current portfolio action.
- No page uses `Hold` as a substitute for missing research; missing research is `Unrated` plus `Watch` or `Avoid` with a reason.
- An all-cash report still gives useful ranked near misses and exact upgrade conditions.
- Snapshot v3, CSV exports, Pages, Telegram, and reference-output tests agree exactly.
- The research benchmark cannot create or influence an approved target, signal, order, execution, cash entry, position, or approved performance row.

## Step 21 — Route Hermes Web ExtractPage summarization through OpenRouter Nemotron — Planned

### Outcome

Hermes continues to use `openai-codex` and the configured main model for agent reasoning, while the `web_extract` auxiliary task uses OpenRouter model `nvidia/nemotron-3-ultra-550b-a55b:free` during daily runs.

### Hermes configuration

1. Verify the pinned Hermes container supports the current auxiliary model schema. If necessary, update the image by immutable digest and record the Hermes version and native-skill version in preflight artifacts.
2. Add explicit repository settings for the auxiliary task, preferably in a dedicated `[hermes_auxiliary]` section:

   ```ini
   web_extract_provider = openrouter
   web_extract_model = nvidia/nemotron-3-ultra-550b-a55b:free
   web_extract_reasoning_effort = low
   web_extract_api_key_env = OPENROUTER_API_KEY
   ```

3. Extend `HermesSettings`, configuration validation, and `_managed_config()` so the generated isolated `config.yaml` contains:

   ```yaml
   auxiliary:
     web_extract:
       provider: openrouter
       model: nvidia/nemotron-3-ultra-550b-a55b:free
       reasoning_effort: low
   ```

4. Keep the top-level Hermes provider fixed to `openai-codex`. Do not route main research reasoning through OpenRouter.
5. Preserve `terminal.env_passthrough: []`. Add an integration assertion that Hermes terminal-tool commands cannot read `OPENROUTER_API_KEY`, even though Hermes itself can use it for the auxiliary provider.
6. Record auxiliary provider, model, reasoning effort, and configuration hash in `hermes_preflight.json` and run metadata without recording the key or a reversible key fingerprint.

### Daily workflow secret boundary

1. Add optional/required `OPENROUTER_API_KEY` to `.github/workflows/reusable-llm.yml` under `workflow_call.secrets`.
2. Pass it from `.github/workflows/daily.yml`:

   ```yaml
   secrets:
     OPENAI_OAUTH_SECRET: ${{ secrets.OPENAI_OAUTH_SECRET }}
     OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
   ```

3. Expose `OPENROUTER_API_KEY` only to the non-dry `agent run-batch` step that launches Hermes. It must not be job-global, available to discovery actions, commit steps, reporting, Pages, or Telegram.
4. Replace the current “inference environment must be empty” rule with an exact, purpose-bound allowlist that permits only `OPENROUTER_API_KEY` when `auxiliary.web_extract.provider=openrouter`. Keep every other API key, GitHub token, Telegram token, deployment credential, and broker credential forbidden.
5. Add an explicit non-dry preflight for missing/empty key with a redacted error. Dry runs remain credential-free.
6. Update `.env.example` with the variable name only and local setup instructions; never commit a value.

### Reliability and source policy

- The free model endpoint may be rate-limited or unavailable. Configure one bounded fallback to the main provider for `web_extract` if supported by the pinned Hermes version; otherwise surface a stable auxiliary-degradation issue and allow operations not requiring page extraction to continue.
- Never retry indefinitely or silently change the main research model.
- Use the free endpoint only for public, non-confidential webpages. Do not send private Drive documents, authenticated pages, user-owned confidential files, personal data, OAuth state, operation secrets, repository credentials, or unpublished source material.
- Treat every auxiliary summary as untrusted convenience text. Research conclusions still require direct source inspection, citations, and current primary-source verification.

### Acceptance criteria

- A daily non-dry run proves that Web `ExtractPage` summarization selected OpenRouter and the exact Nemotron model, while the main agent remained on `openai-codex`.
- Missing `OPENROUTER_API_KEY` fails with a redacted actionable message before inference; dry-run validation succeeds without it.
- Secret-scanning tests prove the key cannot appear in the checkout, diff, run artifacts, logs, command audit, issues, reports, or tool-visible terminal environment.
- A mocked 401, 429, timeout, and provider outage follow the bounded fallback/degradation policy without leaking the key or corrupting queue state.

## Step 22 — Migrate, backfill, test, and roll out safely — Planned

### Migration

1. Version the assessment and decision snapshot schemas rather than changing them ambiguously in place.
2. Create a deterministic migration command that:
   - imports each current assessment into history as `legacy_v1`;
   - preserves its evidence and run provenance;
   - maps old `downside_pct` and `base_upside_pct` only as legacy fields;
   - marks scenario probabilities, bull case, expected return, and rating unavailable;
   - does not invent missing values.
3. Enqueue bounded security refreshes to produce assessment v2, prioritizing current holdings, approved/pending exposure, previously closest candidates, stale assessments, and major watchlist names.
4. Regenerate allocation plans, snapshot v3, pages, reports, Telegram fixtures, and exports only after enough v2 coverage exists for a meaningful comparison.

### Test matrix

Add or update unit, integration, and reference-output coverage for:

- scenario arithmetic and ordering;
- valuation-template requirements;
- unsupported valuation and `Unrated` behavior;
- assessment history and prior-review comparison;
- score rubrics, confidence adjustment, risk penalties, and eligibility frontier;
- rating thresholds and portfolio-action mapping;
- definitive versus provisional cash stance;
- near-miss ranking;
- research benchmark isolation;
- snapshot v3 and publication parity;
- OpenRouter auxiliary configuration, secret scope, redaction, fallback, and dry-run behavior;
- idempotence, exact-delta validation, sequential operation execution, and paper-only invariants.

### Rollout

1. Run the new assessment and rating pipeline in report-only mode against fixed fixtures and the current repository state.
2. Review the old/new comparison artifact for score distribution, rating distribution, excluded reasons, and candidate eligibility. Adjust configurable thresholds with documented evidence, not to force a desired trade count.
3. Publish at least three successful daily report-only snapshots with no schema, secret, or reproducibility failures.
4. Enable active allocation only after assessment-v2 coverage and relationship coverage meet the configured readiness threshold.
5. Keep rollback limited to configuration and schema-version selection; never delete history, executions, cash entries, or prior snapshots.

## Definition of done

This plan is complete when:

- every new security research explicitly compares itself with the prior revision;
- every supported valuation contains validated bear, base, and bull scenarios plus probability-weighted value;
- every researched security has a deterministic rating or an honest `Unrated` state and a context-aware portfolio action;
- the allocator is calibrated, auditable, and capable of both deploying and correctly retaining cash;
- an all-cash decision clearly states whether it is definitive or provisional and still presents actionable near-miss information;
- the approved portfolio remains strict while the isolated research benchmark provides learning and measurement;
- Hermes Web `ExtractPage` summarization uses OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free` in the daily workflow without exposing `OPENROUTER_API_KEY` or changing the main Codex reasoning provider;
- all migrations, workflows, tests, Pages, reports, Telegram output, and integrity checks pass from a clean checkout.
