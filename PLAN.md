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

## Step 17 — Preserve and compare research revisions — Complete (2026-07-30)

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

## Step 18 — Introduce scenario-complete valuation and anchored research rubrics — Complete (2026-07-30)

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

## Step 19 — Recalibrate ratings, eligibility, scoring, and allocation — Complete (2026-07-30)

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

## Step 20 — Publish canonical ratings, actions, near misses, and a research benchmark — Complete (2026-07-30)

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

## Step 21 — Route Hermes Web ExtractPage summarization through OpenRouter Nemotron — Complete (2026-07-30)

### Outcome

Hermes continues to use `openai-codex` and the configured main model for agent reasoning, while the `web_extract` auxiliary task uses OpenRouter model `nvidia/nemotron-3-ultra-550b-a55b:free` during daily runs.

This original Step 21 deployment is superseded by the environment-driven follow-up below; the
historical implementation record remains here for auditability.

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

## Step 22 — Migrate, backfill, test, and roll out safely — Complete (2026-07-30)

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
- Hermes Web `ExtractPage` summarization uses the validated `AUXILIARY_MODEL` selection, defaults
  to `openai-codex:gpt-5.6-terra`, and forwards `OPENROUTER_API_KEY` only for an explicit
  `openrouter:<model>` override without changing the main Codex reasoning provider;
- all migrations, workflows, tests, Pages, reports, Telegram output, and integrity checks pass from a clean checkout.

## Follow-up — Environment-driven discovery and Hermes budgets — Complete (2026-07-30)

- Prefer the YouTube Data API when `YOUTUBE_DATA_API` is nonempty, with anonymous `pytubefix`
  fallback only when the key is absent, a 50-upload bound, live exclusion, and a conservative
  over-180-second regular-video rule.
- Source the Hermes per-invocation turn cap from `MAX_OPERATIONS` with a 180 default while retaining
  the distinct workflow `max_operations` queue-row input.
- Source auxiliary Web ExtractPage provider/model from `AUXILIARY_MODEL`, default to
  `openai-codex:gpt-5.6-terra`, and require OpenRouter credentials only for an explicit override.

## Follow-up — Schedule native llm-wiki maintenance — Complete (2026-07-31)

- Added a native-only `papertrader wiki maintain` boundary with canonical `WIKI_PATH`, exact pinned
  `llm-wiki` version/hash evidence, isolated Hermes configuration, filtered environment, and
  network-disabled `file,terminal` toolsets.
- Added ISO-week success deduplication and active leases, manual and dry-run execution, immutable
  report/result/preflight/run artifacts, a wiki-Markdown-only delta allowlist, and strict
  post-maintenance schema, integrity, wiki, and advice validation.
- Wired maintenance before the normal sequential agent batch. Weekly scheduled execution remains
  disabled by default behind `WIKI_MAINTENANCE_ENABLED` until representative manual results are
  reviewed; failed or expired attempts can retry without creating duplicate successful weeks.


## Step 23 — Add profile-routed, checkpointed daily execution and ephemeral podcast audio — Planned (2026-08-04)

### Outcome

The scheduled controller executes at most `MAX_OPERATIONS` queued research operations as a durable
sequence of independent checkpoints. Every iteration selects the correct Hermes execution profile
for that operation, launches exactly one agent, validates the exact delta, commits and pushes that
accepted state, and only then moves to the next operation. A failure in a later iteration can stop
or degrade the cycle, but it cannot discard already pushed research from earlier iterations.

The final podcast is tied to one immutable timestamped daily cycle rather than to one transient
GitHub Actions attempt or one uncommitted working tree. Its Markdown transcript is committed. Its
MP3 is generated from the exact committed transcript, passed ephemerally to Telegram, and never
added to Git, the wiki, Pages, or a runtime commit.

This step supersedes the hosted daily use of one `agent run-batch` followed by one final runtime
bundle/commit, and supersedes only the committed-audio portion of Step 16. The existing history
remains unchanged for auditability.

### Non-negotiable invariants

- One queue iteration means one claimed operation, one Hermes process, one execution profile, and
  at most one accepted runtime checkpoint commit.
- The target branch is updated only after the operation result, queue transition, repository delta,
  and refreshed OAuth ciphertext have passed their applicable validation gates.
- A later failure never rewrites, squashes, force-pushes, or otherwise removes an earlier checkpoint
  from the same daily cycle.
- Model/profile selection is deterministic controller policy. Payload text, wiki prose, sources, and
  the model itself cannot request a cheaper, stronger, or less restricted profile.
- Scout and analyst profiles have narrower command and mutation permissions than the deep profile;
  model quality is never the only safety boundary.
- The deterministic market, allocation, risk, paper-order, accounting, reconciliation, and
  paper-only boundaries remain authoritative and unchanged.
- Podcast audio bytes and intermediate TTS chunks are forbidden from every staged diff and every
  runtime patch. Of the podcast assets, only the Markdown transcript is committed.

### 1. Replace the single Hermes configuration with three execution profiles

Introduce a validated `HermesExecutionProfile` contract containing at least:

- stable profile name and policy version;
- provider and main model;
- reasoning effort;
- maximum turns;
- timeout;
- weighted budget cost;
- enabled toolsets;
- allowed project-command classes or mutation policy;
- auxiliary model policy;
- escalation targets.

Use repository-owned defaults similar to:

```ini
[hermes_profile_scout]
model = gpt-5.6-luna
reasoning_effort = low
maximum_turns = 32
timeout_seconds = 600
cost_weight = 1
mutation_policy = triage_only

[hermes_profile_analyst]
model = gpt-5.6-terra
reasoning_effort = medium
maximum_turns = 80
timeout_seconds = 1200
cost_weight = 2.5
mutation_policy = routine_research

[hermes_profile_deep]
model = gpt-5.6-sol
reasoning_effort = medium
maximum_turns = 160
timeout_seconds = 1800
cost_weight = 5
mutation_policy = full_research
```

Treat these values as initial benchmark settings rather than permanent limits. Keep
`AUXILIARY_MODEL` separate: it configures bounded Hermes auxiliary work such as Web ExtractPage or
context compression and must never silently become the main model of a research profile.

Resolve the current naming collision as part of the migration:

- `MAX_OPERATIONS` becomes the maximum number of queued research iterations in one daily cycle;
- the current environment variable named `MAX_OPERATIONS` that actually controls Hermes turns is
  removed or renamed;
- turn caps live inside each execution profile, with an optional clearly named override such as
  `HERMES_SCOUT_MAX_TURNS`, `HERMES_ANALYST_MAX_TURNS`, or `HERMES_DEEP_MAX_TURNS`;
- `maximum_llm_operations_per_run` remains the repository hard ceiling and the workflow input may
  select only a value at or below it.

### 2. Route each operation through deterministic profile policy

Add a pure, versioned profile router that receives the validated operation identity, payload
metadata, current portfolio/research state, and operation type, then returns a profile and a
machine-readable reason. Persist the decision before inference and include it in preflight, run,
result, history, and daily-cycle artifacts.

Initial routing policy:

- **Scout / Luna**: cheap classifier decisions, source discovery, stale/duplicate checks, bounded
  alert materiality screening, and quick checks after their write authority is restricted.
- **Analyst / Terra**: ordinary wiki ingestion, opportunity research, routine idea refreshes,
  non-decision-changing relationship refreshes, routine bounded research updates, and the
  long-form text podcast.
- **Deep / Sol**: initial or materially changed security valuation, held or allocated securities,
  broad new idea/value-chain research, relationships whose acceptance changes allocation
  readiness, strategy research, option or multi-leg work, and non-mechanical execution decisions.

The router must promote work to a stronger profile when any of these conditions applies:

- a current holding, approved target, pending order, active strategy, or ready signal depends on the
  conclusion;
- earnings, guidance, capital structure, dilution, accounting, instrument identity, or the business
  model changed materially;
- primary evidence conflicts or the prior valuation is unsupported;
- the proposed result would change valuation method, scenario values materially, canonical rating,
  allocation eligibility, portfolio action, confidence tier, or a hard blocker;
- the selected profile reports insufficient evidence or low confidence.

Escalation is one-way: `scout -> analyst|deep`, `analyst -> deep`, and `deep -> terminal result`.
Do not force every operation through all three models. An operation already known to require a full
scenario-complete review goes directly to the deep profile.

Enforce profile authority in the CLI dispatcher, not only in skill prose. At minimum:

- Scout cannot call assessment, relationship, strategy, signal, or order mutation commands.
- Analyst cannot publish a decision-changing assessment or allocation-enabling relationship without
  a deterministic materiality gate; it must retain an evidence packet and enqueue a deep review.
- Only Deep may perform the existing full security/strategy mutation set.
- All profiles remain unable to edit allocation targets, fills, executions, cash, portfolio, or
  performance directly.

Record `profile`, `profile_policy_version`, `route_reason`, effective model, reasoning effort,
maximum turns, auxiliary models, weighted cost, and any escalation source in
`hermes_preflight.json`, `hermes_run.json`, operation history, and the final daily manifest.

### 3. Introduce one durable timestamped daily-cycle identity

Create the daily cycle before deterministic preparation, with an immutable UTC timestamped ID such
as:

```text
daily-20260804T150000Z
```

Store the Europe/Rome operating date separately for display. The canonical cycle manifest under
`data/runs/<daily_cycle_id>/daily_run.json` must contain at least:

- `daily_cycle_id`, `started_at`, local operating date, trigger, and source SHA;
- originating GitHub run ID and an append-only list of workflow attempts;
- total `MAX_OPERATIONS`, weighted model budget, and per-profile limits;
- operation IDs attempted and terminally accepted for this cycle;
- profile and checkpoint index for every accepted operation;
- preparation, research cutoff, finalization, podcast-text, and completion timestamps;
- current cycle status: `running`, `interrupted`, `degraded`, `succeeded`, or `failed`;
- final report, decision snapshot, podcast transcript, and final commit identities.

Use `daily_cycle_id` as `claimed_by_run_id` for every operation in the cycle. Keep the transient
GitHub execution identity, such as run ID and attempt, in controller artifacts rather than using it
as the investment-operation grouping key.

Add `daily resume-or-create` behavior:

- a rerun of the same GitHub run resumes its already committed open cycle;
- a manual dispatch may explicitly provide `resume_cycle_id`;
- a new scheduled invocation creates a new timestamped cycle;
- two manual cycles on the same date cannot collide because paths use the full timestamp;
- remaining iterations equal the configured cycle total minus operations already claimed and
  checkpointed in prior attempts, so a rerun cannot accidentally receive a second full budget.

Commit messages should carry machine-readable trailers so finalization can map checkpoints to Git
commits without requiring a second commit merely to write the first commit's SHA:

```text
PaperTrader-Cycle: daily-20260804T150000Z
PaperTrader-Checkpoint: 003
PaperTrader-Operation: 01...
PaperTrader-Profile: analyst
```

### 4. Replace `agent run-batch` with a checkpointed workflow loop

Refactor `.github/workflows/reusable-llm.yml` into one serialized checkpointed runtime. Preserve
`checkout.persist-credentials: false`. The job may require `contents: write`, but the GitHub token
must be injected only into the small post-validation push step and must never be job-global or
visible to Hermes, terminal tools, source discovery, TTS, or validation commands.

The hosted flow becomes:

1. Check out and fast-forward/rebase to the current target branch; install pinned dependencies;
   restore and preflight the isolated OAuth/Hermes profile; run the full code/configuration
   preflight once.
2. Create or resume the timestamped daily cycle, run deterministic discovery and `daily prepare`,
   validate that state, and push a **preparation checkpoint** before starting expensive research.
3. Loop from the next checkpoint index until the cycle reaches `MAX_OPERATIONS` or no ready
   operation remains:
   1. fetch and reconcile the current target branch before claiming work;
   2. select exactly one ready operation and its deterministic execution profile;
   3. snapshot the repository and spawn exactly one Hermes agent with that profile, operation skill,
      turn cap, timeout, and mutation policy;
   4. terminalize or fail that one queue operation through the existing deterministic controller;
   5. compare the exact delta and run the scoped checkpoint gates: result schema, command audit,
      queue validation, schema validation, strict integrity, strict wiki lint, advice validation,
      portfolio reconciliation, path whitelist, and profile mutation policy;
   6. compare OAuth state, encrypt and verify a refresh immediately when it changed, and stage only
      the ciphertext beside the validated operation delta;
   7. stage the exact allowlisted paths and create one checkpoint commit naming the cycle,
      checkpoint index, operation ID/type, terminal status, and profile;
   8. fetch/rebase again, repeat the strict data-state gates on the rebased commit, and push it;
   9. advance the cycle's in-memory and committed accounting only after the push succeeds.
4. After the loop, run deterministic fills, reconciliation, allocation, snapshot, publication, and
   `daily finalize` against the final pushed research state. Freeze `research_cutoff_at` and push a
   separate **finalization checkpoint** even when no research operation ran.
5. Build and commit the text podcast as described below, then expose the final commit SHA to
   Telegram reporting and Pages. Deploy Pages only once, after the final text checkpoint.

Remove the hosted dependency on one final runtime patch bundle and one all-or-nothing commit job.
The bundle commands may remain for local harnesses, dry-run fixtures, or forensic replay, but they
are no longer the durability boundary of a scheduled daily run.

Provide one repository-owned command or composite action for checkpoint creation so staging,
trailers, OAuth handling, validation, rebase, and push retry behavior are not duplicated in shell.
Full Ruff, formatting, MyPy, and pytest checks run before the first push and after finalization;
per-operation checkpoints use the strict data/runtime gates because agent operations cannot edit
application code.

In dry-run mode, never expose a write token or push. Simulate the same boundaries with local
throwaway commits on a temporary branch so later iterations consume prior simulated state and the
checkpoint contracts are still exercised.

### 5. Define failure, rollback, and resume semantics

- A schema-valid `succeeded`, `skipped`, `blocked`, or agent-reported `failed` result may be
  checkpointed with its deterministic queue transition and evidence.
- A valid agent-reported failure is committed, the daily cycle becomes degraded, and the initial
  implementation stops claiming further research operations by default before finalization.
- If Hermes exits or validation rejects its delta, restore the worktree to the last pushed
  checkpoint. Retain only controller-owned, schema-valid failure evidence, issue state, and bounded
  queue retry transition; checkpoint that contained failure state when possible, then stop.
- If state cannot pass strict integrity after cleanup, do not finalize or publish from the dirty
  checkout. Mark the cycle interrupted in the next resumable attempt; all earlier pushed
  checkpoints remain valid.
- Rebase/push receives bounded retries. If the current checkpoint cannot be pushed, no later
  operation starts. The existing lease expiry/retry contract makes the unpushed operation
  recoverable, while all previously pushed checkpoints remain available.
- Never amend, squash, reset, or force-push earlier checkpoints from the cycle.
- A resumed workflow starts from target-branch HEAD, validates the committed cycle manifest and
  operation history, skips already terminal operations, calculates the remaining count and weighted
  budget, and continues with the next checkpoint index.
- Finalization may proceed after a contained operation failure so the report describes accepted
  earlier work and the failure. It must not proceed after unresolved repository corruption,
  accounting failure, or an unpushed operation checkpoint.

Persist refreshed OpenAI OAuth ciphertext after every Hermes invocation that changes it. If the
operation itself cannot be accepted, create a credential-only checkpoint when required so a rotated
refresh token is not lost merely because research failed.

### 6. Build the final podcast from the complete timestamped cycle

Refactor the queued `daily_podcast` operation into **text-only podcast synthesis**. It is a final
operation outside the research `MAX_OPERATIONS` allowance and receives its own checkpoint commit.
Use the analyst profile initially because the roughly 3,000-word connected narrative requires more
long-form synthesis than a simple scout task; benchmark Luna later without changing the contract.

After the finalization checkpoint:

1. Run `podcast context build --daily-cycle-id <id> --cutoff <research_cutoff_at>`.
2. Select accepted operation-history rows whose `claimed_by_run_id` matches the cycle and whose
   terminal timestamp falls from `started_at` through the frozen cutoff. This must include operations
   committed by earlier workflow attempts of the resumed cycle and exclude later/unrelated work.
3. Include the cycle's final committed daily report, decision snapshot, fills, allocation outcome,
   portfolio/performance state, operation results, evidence paths, profile metadata, failures, and
   unresolved gaps. Do not derive the podcast from `git diff`, one workflow attempt, or only the
   final operation.
4. Freeze the context under the cycle directory before inference and validate every referenced path,
   operation, timestamp, and snapshot identity.
5. Generate a timestamped Markdown page such as
   `data/wiki/podcasts/daily-podcast_20260804T150000Z.md`, preventing collisions between multiple
   same-day manual cycles.
6. Commit only the text page, its normal operation/result artifacts, and a link from the daily
   report to the transcript. The transcript contains no persistent MP3 link.

Change the podcast skill and result contract accordingly:

- remove MP3 and TTS chunks from allowed repository writes and `files_changed`;
- remove audio existence/duration from the text operation's success criteria;
- preserve the outline, 2,400-3,600-word transcript, provenance, uncertainty, paper-trading label,
  and complete cycle coverage checks;
- make text success independent from later audio rendering or Telegram availability;
- if text synthesis fails, retain all earlier research/finalization checkpoints and deliver the
  normal daily report without audio.

### 7. Render and deliver audio ephemerally after the text commit

Create a post-commit podcast-render boundary that has no investment mutation authority and does not
consume the research operation budget:

1. Read the exact transcript from the pushed text checkpoint, preferably with
   `git show <commit>:<podcast_path>`, and verify its cycle ID and content hash.
2. Extract and split the spoken transcript deterministically at paragraph boundaries.
3. Invoke only the configured TTS backend sequentially. Do not give the renderer Web access,
   project mutation commands, Telegram credentials, or permission to rewrite the script.
4. Write chunks and the final MP3 only beneath a runner-owned temporary directory such as
   `$RUNNER_TEMP/papertrader-podcast/<daily_cycle_id>/`.
5. Assemble and verify duration, non-empty size, format, cycle/script binding, and SHA-256. Produce
   an ephemeral audio manifest containing no secret and no audio content.
6. Pass the MP3 and manifest to the isolated Telegram delivery job through a one-day GitHub Actions
   artifact or an equivalent job-scoped handoff. Never copy the MP3 into `data/`, the wiki, Pages,
   or the Git index.
7. Extend Telegram delivery with bounded multipart `sendAudio` support. Verify the artifact manifest,
   script commit, cycle ID, filename, size limit, and hash before sending. Use a caption that links
   to the committed text podcast and daily report.
8. Remove the downloaded artifact and all temporary media in `always()` cleanup. Do not retain or
   publish audio artifacts longer than the minimum handoff period.

Telegram report delivery and podcast-audio delivery have separate statuses. An audio/TTS/Telegram
failure records or refreshes one stable latest-only delivery issue, but it cannot roll back the
text podcast, daily report, research checkpoints, portfolio state, or finalization commit. A later
retry always regenerates or downloads audio bound to the same committed transcript; it never uses
an uncommitted script.

Add defense in depth:

- explicitly reject `.mp3`, `.wav`, `.m4a`, TTS chunks, and podcast media from the runtime whitelist
  and staged-diff validator;
- keep generated media outside the checkout rather than relying only on `.gitignore`;
- update wiki lint and link checks so podcast pages do not point to nonexistent committed audio;
- prove that Git history and Pages contain the transcript but no audio bytes.

### 8. Preserve credential and token isolation during incremental pushes

- Keep checkout credentials disabled and never place `GITHUB_TOKEN` or a write credential in the
  job environment, Hermes profile, repository, command audit, or child terminal environment.
- Expose the GitHub token only to the bounded checkpoint push command after Hermes has exited and
  the exact staged delta passed validation; remove any temporary credential helper immediately.
- Continue exposing the age identity only to OAuth decrypt/encrypt steps. Hermes receives only its
  private `auth.json`, and plaintext credentials are removed in `always()` cleanup.
- Encrypt and verify refreshed OAuth state before each operation checkpoint or credential-only
  checkpoint.
- Expose Telegram credentials only to the delivery job after the final report/text commit and audio
  artifact validation. The research runtime and TTS renderer never receive them.
- Continue forbidding GitHub, Telegram, deployment, brokerage, age, and unrelated API secrets from
  Hermes and all tool-visible environments.

### 9. Expected implementation touch points

Update at least:

- `config.ini`, `.env.example`, and `src/papertrader/config.py` for profiles, turn limits, weighted
  budgets, and corrected `MAX_OPERATIONS` semantics;
- queue/run schemas, operation history, result/preflight/run artifacts, and integrity checks for
  selected profile and daily-cycle identity;
- `src/papertrader/agent_runner.py` and CLI commands for one-operation execution, profile routing,
  escalation, checkpoint metadata, and resume accounting;
- `.github/workflows/daily.yml` and `.github/workflows/reusable-llm.yml` for the durable loop,
  preparation/operation/finalization checkpoints, and final outputs;
- workflow bundle code so it remains available for local/debug use but is no longer the scheduled
  all-or-nothing commit boundary;
- `src/papertrader/podcast.py`, the podcast skill/schema, wiki paths, and report generation for
  timestamped text-only podcasts and cutoff-based cycle aggregation;
- `src/papertrader/telegram.py` and `.github/workflows/reporting.yml` for verified ephemeral audio
  handoff and `sendAudio` delivery;
- `AGENTS.md`, `README.md`, `docs/OPERATIONS.md`, workflow contracts, and reference outputs.

### 10. Test matrix and fault-injection acceptance

Add unit, integration, workflow-contract, and reference-output tests covering:

- deterministic profile selection, profile-specific commands, reasoning effort, turn limit, timeout,
  weighted budget, and escalation;
- a Scout attempt being unable to publish an assessment, relationship, strategy, signal, or order;
- `MAX_OPERATIONS` as total cycle iterations and profile turn settings as separate values;
- preparation checkpoint followed by several operation checkpoints and one finalization checkpoint;
- injected failure at operation N proving commits 0 through N-1 remain on the target branch;
- rejected agent delta being removed without removing prior checkpoints;
- contained terminal failure being committed and reported without corrupting the cycle;
- push/rebase retry, lease recovery, and resume in a later GitHub workflow attempt;
- resume consuming only the remaining operation count and weighted budget;
- OAuth refresh after an early operation surviving a later operation failure;
- finalization and daily reporting over all accepted checkpoint commits;
- podcast context containing all operations in the timestamped cycle, including prior workflow
  attempts, while excluding operations outside the start/cutoff window;
- unique timestamped podcast paths for multiple same-day manual cycles;
- transcript-only podcast commits and an explicit staged-diff failure for any audio extension;
- audio generation from the exact committed transcript, manifest/hash validation, Telegram audio
  delivery, cleanup, bounded retry, and stable failure issue behavior;
- audio failure leaving the transcript, report, and every prior research checkpoint intact;
- dry-run local checkpoint simulation with no write token and no push;
- final strict schema, integrity, advice, wiki, portfolio, Pages-link, and paper-only validation from
  a clean checkout.

A hosted fault-injection fixture must demonstrate this exact scenario:

1. prepare and push the cycle checkpoint;
2. complete and push at least three heterogeneous operations using at least two profiles;
3. force the next Hermes operation or post-run validation to fail;
4. verify the already pushed operation commits and queue history remain available;
5. rerun the workflow, resume the same timestamped cycle without repeating accepted operations or
   resetting its budget, and complete finalization;
6. commit the timestamped podcast transcript;
7. generate and send its MP3 through Telegram without any audio path appearing in Git history.

### Rollout

1. Add profile routing and audit fields behind a configuration flag while retaining the existing
   single-commit workflow; benchmark Luna/Terra/Sol outputs and mutation-policy rejections.
2. Enable the checkpoint loop with a low operation limit and injected failures on a test branch;
   review commit history, resume behavior, OAuth persistence, and final report parity.
3. Enable timestamped text-only podcast commits and ephemeral audio delivery; verify Telegram and
   Pages independently.
4. Run at least three scheduled cycles with fault injection disabled, no duplicate operations,
   correct profile routing, one commit per accepted operation, and no committed audio.
5. Remove the legacy hosted `agent run-batch` plus single final bundle/commit path after the
   checkpointed controller is the only scheduled path. Retain rollback through a temporary workflow
   feature flag until the new path has completed the acceptance suite.

### Acceptance criteria

- A cycle configured for N operations can produce up to N independently pushed operation commits,
  plus preparation, finalization, and text-podcast checkpoints.
- Failure at operation N cannot remove commits from operations 1 through N-1.
- A rerun resumes the same timestamped cycle, does not repeat terminal operations, and cannot exceed
  the original count or weighted budget.
- Every operation runs with a recorded deterministic Scout, Analyst, or Deep profile and obeys that
  profile's mutation policy.
- No scheduled hosted path uses one uncommitted multi-operation batch as its durability boundary.
- The final report and podcast context include all accepted operations from the cycle across commits
  and workflow attempts.
- The final podcast transcript is committed under a timestamped Markdown path and linked from the
  daily report.
- The MP3 is generated from that exact committed transcript, validated, sent to Telegram, cleaned
  up, and absent from every commit, staged diff, Pages build, and durable repository path.
- Podcast audio or Telegram failure cannot roll back or invalidate accepted research, finalization,
  report, or transcript commits.
- OAuth, GitHub, Telegram, deployment, brokerage, and age secrets remain within their exact existing
  purpose-bound steps and never reach Hermes tools or repository artifacts.
