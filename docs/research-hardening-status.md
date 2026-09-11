# Research hardening implementation status

Updated 2026-09-11. **M1–M9 implemented and activated locally; M10 deployment is in progress.**
The specification in PLAN.md remains the acceptance contract. Unchecked criteria must not be
represented as implemented or exercised by a live model.

## Current integrated result (supersedes the initial M1/M2 notes below)

- M3: `buy_review.py` owns immutable preflight packets and accepted parent-authenticated review
  receipts under `data/operations/buy-review-{packets,results}/`. Both baseline and explicit-leg
  order admission require clearance. Fills independently bind the exact package, quantity,
  material state, validity and price/FX envelope. Recorded accounting recovery precedes this gate.
  Astra approval submits deterministically; interruption resumes without another model judgment.
  Rejected/deferred packets retain their reasons. Current ineligible intents stop before inference.
- M4: shared scheduler classes rank protective exits, final reviews, current RSI oversold research,
  then ordinary work. Selection reserves available capacity without expanding cycle limits.
  RSI formula/threshold is unchanged; depth, recency, priority, original age and immutable ID are
  deterministic tiebreakers. Contiguous oversold observations retain one episode identity.
- M5/M6: immutable scope revisions, explicit manual anchors, direct original-anchor contributions,
  protected exposure overlay, terminal peripheral/archive boundaries and retained 100–200-word
  capsules. Security deltas coalesce with every result reference; unchanged/price-only deltas
  terminate deterministically. Audited CLI follow-ups retain their actual parent. Capacity deferral
  retains the request and reason; legacy overload is not deleted or reclassified as user intent.
- M7: immutable claim/evidence versions bind exact periods, units, scope, source observations,
  origin and retained excerpts. Source syndication is not independent confirmation. Structured
  challenges report actual inspection, partial/blocked/not-searched gaps. Material corrections
  change review substance and enqueue scoped refreshes; source transport/cosmetic hashes alone
  do not become financial verdicts. Common-assumption exposure is diagnostic, not a new risk limit.
- M8: bounded primary monitoring (at most two checks/day) and weekly semantic subsets share the
  global budget. Actual target receipts distinguish checked/failed/partial/reserved coverage.
  Stable catalyst occurrences preserve date precision, DST and amendments, with one bounded due
  admission. Frozen forecasts retain rejected/archived dispositions and post-horizon outcomes.
  Findings from manual/prior cycles remain reportable until included in a linked appendix;
  saved coverage never asserts delivery or user observation. Metrics expose retained-call coverage,
  review dispositions/reasons, latency, RSI investigations, challenge coverage and forecast outcomes.
- M9: `research migrate-hardening` previews by default; `--apply` writes one hash-bound activation
  record, legacy queue census, pre-policy execution IDs, pending-order hold dispositions and ledger
  hashes. Replays retain the original record. Integrity checks all retained research revisions and
  finding appendices. Governance artifacts participate in snapshot source hashes and the existing
  runtime JSON allowlist; accepted review evidence is protected from retention pruning.

### Integrated verification and migration rehearsal

`UV_CACHE_DIR=/tmp/papertrader-uv-cache uv run pytest`: **598 passed**. Ruff format/check and
MyPy (61 source files) pass. Locked Quartz check/build previously passed, emitting 894 files.
The full operating-cycle integration includes the positive mocked Astra review and replay path.

A disposable production-data copy was activated and finalized offline through the supported
daily lifecycle. Strict schema, integrity, advice, wiki and reconciliation passed. Executions,
cash ledger and portfolio bytes were unchanged; no fills occurred. This zero-model migration
rehearsal is **not** the required normal-budget live daily run.

Production preview: 340 legacy operations (307 ready, 14 waiting, 19 blocked), 294 entities,
one pre-policy execution, no pending orders. Measured throughput: 108 successful completions over
14 days; a five-day admission service goal produces a cap of 40 new automatic active obligations.
Existing overload remains auditable. The scheduled podcast retirement preview selects only
`01M1PV87N00M38FCWEWS8A4SD6`; the two manual blocked requests are preserved.

### Deployment boundary and limitations

Activation applied at `2026-09-11T10:31:33Z`, immutable migration ID
`86fd9c49ac06684552b9197b5b2327e914ecab9bc0639dd1a60611694fd55db3`.
The dedicated offline `migration` cycle `daily-20260911T103301Z` completed with snapshot
`decision_c575d716ba6095bc68f0`, zero model operations and no fills. Executions, cash ledger and
portfolio SHA-256 values exactly match the pre-migration record. One scheduled podcast request
was archived with `disabled_by_policy`; manual requests and original evidence remain.
This regenerated the latest publication without rewriting the earlier immutable run snapshot.
After the Quartz privacy regression was fixed, a second offline migration cycle
`daily-20260911T104617Z` produced `decision_8412fbcce9e21ff250ba` using the opaque public findings
slug. It also had no model calls, no fills and identical financial hashes. The exact
`PAPERTRADER_VALIDATE_QUARTZ=true ... pytest tests/integration/test_complete_operating_cycle.py`
gate passed independently; standalone site output now includes the findings appendices.

No positive live Astra review is claimed. Routing is pinned to Astra/high with no fallback;
actual account availability still requires the real workflow. Monitoring is a bounded subset,
legacy missing evidence remains unknown, and metrics cannot infer correctness, causal challenge
effectiveness, historic missing token costs, or user observation. No investment threshold or
paper-only invariant was relaxed. The acceptance checklist remains a conservative scenario-level
record, not an assertion that every possible live branch occurred.

## Historical initial checkpoint (M1/M2 only)

The notes below describe the earlier partial checkpoint, before the integrated implementation
above. Their then-outstanding work is not the current implementation status.

## Baseline and ownership

- Local and remote `main`: `d43d79e1240fc11738e2af3ed24f1adaf12b88e5` at inspection.
- Existing user changes in AGENTS.md, PLAN.md, README.md, docs/OPERATIONS.md, `.agents/`, and
  `.codex/` were retained.
- Queue census: 340 active requests, 307 ready, 14 waiting, 19 blocked. The oldest request was
  created at `2026-07-29T16:55:24Z`. Kinds: 89 relationship, 66 opportunity, 62 ingestion,
  58 security, 54 idea, 7 quick-check, 3 podcast, and 1 execution operation.
- Important producers: 76 allocation-maintenance requests, 66 indicator-transition requests,
  62 ingestion-classifier requests, 16 grouped price alerts, and research propagation.
- Both baseline and explicit-leg order admission converge in `orders.create_paper_order`.
  Fills converge in `execution.process_order_fill`; recorded executions/cash recovery precedes
  selection of remaining legs. The future approval check must preserve that recovery order.
- GitHub authentication and public repository access work with network permission. HTTPS remote
  inspection confirmed the baseline SHA. Sandbox-only network failures were not credential
  failures. No credentials were displayed. No local Hermes executable or OAuth file was found at
  the documented default/named-profile paths. Actual model access is unverified.

## Implemented locally

### M1: manual-only podcast paths and migration

Scheduled and default daily workflows suppress podcast production. The reusable workflow checks
the actual GitHub event even if a caller passes `generate_podcast=true`. General queue selection
excludes podcast/translation operations, and daily research checkpoints exclude both media kinds.
Explicitly selected manual media work remains supported. The runner rejects scheduled media
execution. Disabled completed cycles retain the machine-readable reason `disabled_by_policy`.

`papertrader podcast retire-automatic` previews migration without changing data; `--apply` archives
eligible scheduled legacy requests, preserving the original request and prior result references.
Daily preparation invokes the same deterministic migration. It requires matching cycle identity,
operation identity, and `schedule` provenance; source text alone is insufficient. Manual requests
and live leases are preserved. Cycle transition receipts retain the previous podcast status and
support restart after archival or after writing the transition.

The actual three legacy podcasts comprise two manual blocked requests and one scheduled blocked
request. Production migration has **not** been applied. Historical transcripts and ledgers have
not changed. Broader manual authorization receipts and every F-series adversarial case have not
been exhaustively exercised.

### M2: read-only triage and final-review profile groundwork

`research_triage` is a schema-validated operation on one immutable security/investigation. It
routes to Luna with low reasoning even when its subject has portfolio exposure; that exposure
does not grant the check financial authority. Its only permitted write is its result manifest.
CLI and observed-diff checks prohibit research, queue, issue, order, and accounting mutations.

Accepted material/uncertain/deferred checks cause the parent to enqueue or merge one full GPT-5.6
security investigation. The payload retains the original cause, investigation identity, creation
time, evidence references, and triage result. An inspected no-change result cannot refresh an
assessment. Existing deterministic RSI alerts have not been routed through this new check.
Automatic monitoring producers, stronger origin receipts, and all restart/attempt/budget cases
remain part of the unfinished plan.

Terra/Sol first-pass routes are unchanged. A separate `final_review` profile pins
`openai-codex:gpt-6-astra`, high reasoning, review-only command authority, no escalation fallback,
and a weighted cost of 10 within existing cycle ceilings. Cycle schemas support the new profile
without requiring it in historical manifests. This is **not an implemented buy approval gate**:
final-buy operation admission, packets, authenticated acceptance, durable approval history,
automatic submission, and pre-fill enforcement remain M3 work.

Official model identity/reasoning reference:
[GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra). Documentation confirms
the identifier and high reasoning; it does not prove this Hermes account can invoke the model.

## Validation evidence

With `UV_CACHE_DIR=/tmp/papertrader-uv-cache`:

- Full `uv run pytest`: **557 passed** before the final restart/identity regression additions.
- Final targeted `test_podcast.py`, `test_triage.py`, and `test_queue.py`: **63 passed**, including
  the added restart/identity regressions. Final Ruff check/format and MyPy passed again.
- `uv run ruff check .`, `uv run ruff format --check src tests`, and `uv run mypy src`: passed.
- Strict schema, integrity, advice, wiki lint, and portfolio reconciliation: passed.
- `npm run check` and `PAPERTRADER_BASE_URL=localhost npm run build` in `site/`: passed;
  Quartz emitted 894 files and site link validation passed.
- Runtime triage skill passed the skill frontmatter/scaffold validator.
- One golden report snapshot ID changed solely because snapshots bind the intentional
  `config.ini` profile addition. It was regenerated through the documented reference-update
  command; the full diff was one ID replacement and no report-content change.

No live model run, deployment dispatch, commit, push, or production migration has occurred.
The read-only production migration preview selected exactly `01M1PV87N00M38FCWEWS8A4SD6`;
the two legacy manual podcast requests remain outside its target set.

## Remaining milestones

M3 is the next implementation dependency: build concrete preflight packets; authenticate Astra
results in the trusted parent; persist immutable review/binding evidence; enforce admission,
remaining quantity, material identity, validity, and non-retroactive fill timing; deterministically
submit approved intents; migrate pending legacy buys; distinguish review and execution states in
publications. No existing buy path currently requires Astra clearance.

M4 RSI class ordering/reservation and episode propagation; M5 scope/admission/delta coalescing;
M6 protected compact archives; M7 versioned claims/evidence/challenges/corrections; M8 bounded
monitoring/calendar/audits/finding coverage/evaluation; M9 integrated migration/replay/security
matrix; and M10 commit/push/live daily validation and post-run reconciliation are outstanding.

Do not dispatch the plan's live daily validation as proof of completion until these required
implementation milestones and their acceptance tests are complete. No business veto, model
approval, filled trade, or live final-review scenario is claimed here.
