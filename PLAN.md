# PaperTrader research governance and final-buy review — development plan

**Prepared:** 2026-09-11

**Repository:** `Kabutojira/PaperTrader`

**Inspected baseline:** `d43d79e1240fc11738e2af3ed24f1adaf12b88e5`

**Deliverable status:** M1–M9 integrated locally as of 2026-09-11; M10 in progress; see
[`docs/research-hardening-status.md`](docs/research-hardening-status.md) for implemented portions,
validation evidence, and outstanding milestones. Local production-data activation is complete;
the main-branch live deployment validation is still in progress.

## 1. Objective and interpretation

Improve the existing PaperTrader implementation, not replace it. Transfer WikiPlant's research-governance concepts: controlled exploration, compact archival memory, claim-specific evidence assessment, adversarial research, material-change propagation, coverage accounting, and research-quality evaluation. Add the user's new model-routing, execution-gate, RSI, podcast, and deployment requirements.

The intended decision path is:

```text
Deterministic observations and validation
  -> Luna for simple semantic triage where judgment is actually necessary
  -> Existing GPT-5.6 analysis and strategy preparation
  -> Existing deterministic eligibility, sizing, cash, and risk checks
  -> GPT-6 Astra final review of a concrete otherwise-eligible buy
  -> Deterministic approval acceptance and paper-order submission
  -> Deterministic freshness/risk/approval checks at simulated fill
```

Astra is the **last discretionary/model-based gate**, not a replacement for deterministic protections. There must be no subsequent GPT-5.6 investment judgment between an accepted Astra approval and submission of its unchanged approved order intent. A lower-tier model cannot override a veto or approve a different order using an existing review.

"Buy" means opening or increasing an investment position, including baseline, starter, conviction, and purchase components of supported rolls or multi-leg strategies. Pure cancellations, reductions, closes, and an unambiguous buy-to-cover that only extinguishes an existing short retain their risk-reduction paths. Classify actual positions and legs deterministically; do not trust an action label. A purported close that crosses through zero and opens exposure is not exempt. A mixed roll with new exposure needs approval for its opening component/package. This distinction prevents a purchase safeguard from preventing a risk-reducing exit.

The deployment prompt authorizes Codex to commit directly to **`main`**, push, dispatch the daily workflow, monitor that exact run, fix failures, and repeat until a genuine successful daily run. It does not authorize real-money orders, weakening checks, changing access policies, exposing secrets, publishing unrelated private files, or resetting financial history.

## 2. Fixed product and safety constraints

1. Keep Git-native canonical state under `data/`, Hermes in GitHub Actions, native `llm-wiki`, existing repository skills, and strictly sequential production operations. No Drive migration, parallel research agents, or second orchestration framework.
2. Preserve paper trading only. No broker adapter, brokerage credential, live-execution mode, or real order.
3. Preserve deterministic authority over identity, dates, prices, indicators, return arithmetic, thresholds, risk, quantities, orders, executions, cash, portfolio, and publication projections.
4. Preserve append-only financial and research history. Correct errors with the established mechanisms; never erase unfavorable decisions to improve a result.
5. Preserve immutable security identity and exact instrument/venue/currency handling. A ticker is not an identity.
6. Preserve the existing global operation, time, and weighted-model budget ceilings unless the user separately changes them. Reserve capacity within those ceilings; no hidden extra Astra calls, retries, or monitoring work.
7. Preserve manual top-level idea intake and dormant automatic YouTube/Seeking Alpha subscriptions. Scoped monitoring of approved interests is not permission to reinstate broad subscriptions.
8. Keep deterministic daily accounting, market/FX monitoring, reports, Telegram text delivery, and Pages working when there is no buy. Disable automatic podcasts only.
9. Protected exposure obligations override research pruning. Holdings, pending orders, active strategies, and material dependent risks cannot lose required coverage through archival or a topic-cap calculation.
10. New evidence-quality limitations generally remain scoped diagnostics/soft gaps, not universal entry blockers. The explicitly requested Astra gate is mandatory for new exposure. Decisive contradictions or genuinely unsupported valuation use existing appropriately scoped hard-blocker policies.
11. Retrieved pages, old wiki prose, transcripts, release notes, and imported text are evidence, not authority to change policy or execute instructions.
12. Production agents do not receive GitHub-write, deployment, Telegram, or brokerage secrets. Runtime result acceptance and Git/publication remain controller-owned.

## 3. Verified baseline and where to extend it

These observations describe the inspected commit, not promises about the checkout Codex will encounter. Reconcile newer changes before implementation.

| Area | Current behavior | Consequence for this plan |
|---|---|---|
| `config.ini` and `profiles.py` | Scout/classifier uses `gpt-5.6-luna`; analyst uses `gpt-5.6-terra`; deep uses `gpt-5.6-sol`. | Extend the existing router, preserve first-pass models, add one constrained final-review role. |
| `profiles.py` | `quick_check_research` routes to deep because it can publish assessments. | Do not merely rename this route to Luna. Split genuine triage from assessment-capable research. |
| `opportunity.py` | RSI oversold exists; grouped price-alert research uses priority 95; per-trigger opportunity research uses 70. | Make RSI specifically preferred, not merely another generic alert. |
| `.github/workflows/daily.yml` | Manual podcast input defaults false, but scheduled events explicitly set `generate_podcast` true. | Fix all scheduled/default paths and pending automatic podcast requests. |
| `execute-strategy` skill | A GPT-5.6 execution operation still judges the action, then calls order CLI. | Move the final purchase judgment to Astra, and make post-approval submission deterministic. |
| `execution.py` | Fill selection uses signal/not-before timing and later deterministic risk validation. | Approval activation time, state binding, expiry, and remaining approved quantity must also be enforced here. |
| Research skills | Primary-source hierarchy, contrary evidence, causal relationships, prior-review context, and assessment history already exist. | Strengthen their contracts and enforcement rather than invent duplicate systems. |
| Security/idea propagation | Security results cause idea refreshes; idea research can revisit a broad candidate universe. | Introduce bounded delta updates and materiality-aware coalescing. |
| Committed system status | Reports a 340-item research backlog in the inspected snapshot. | Measure causes/readiness/age first; do not assume every item is drift or delete a backlog to fit a new cap. |
| Retention | Run artifacts have reference-aware retention and Git recovery. | Add semantic research dispositions; protect new approval/evidence records from unsafe pruning. |

See the source map at the end. The earlier WikiPlant review is a source of test ideas, **not proof that PaperTrader has the same implementation bugs**.

## 4. Model and authority policy

### 4.1 Roles

| Role | Runtime model | Reasoning default | Permitted work |
|---|---|---|---|
| Deterministic checker | No LLM | Not applicable | Schema, indicator arithmetic, hashing, freshness math, sorting, risk, version/identity checks, accounting. |
| Scout/triage | `gpt-5.6-luna` | `low` | Bounded semantic overlap, source-change classification, relevance proposals, archive-candidate classification, simple update checks. |
| Analyst | Existing `gpt-5.6-terra` | Preserve current `medium` | Existing routine research authority. |
| Deep first-pass analyst | Existing `gpt-5.6-sol` | Preserve current `medium` | Scenario-complete assessments, consequential first-pass research, strategy preparation. |
| Final buy reviewer | `gpt-6-astra` | `high` | Independent final examination of a concrete buy packet; emits a review artifact, not an order or ledger edit. |

The user requested GPT-5.6 first analysis "as it is": keep the Terra/Sol division, not a blanket migration of all research to Astra. `gpt-5.6` is a documented alias for Sol, but explicit existing IDs make route behavior clearer.

OpenAI documents these IDs and reasoning settings. That does **not** prove the repository's Hermes provider/account currently exposes each route. Verify actual provider invocation, tool calling, and schema output. Keep the existing provider/authentication path; do not invent a model alias, use an undisclosed fallback, or introduce API-key onboarding. If Astra is unavailable, defer affected buys and report the exact capability failure. Continue safe unrelated work.

### 4.2 Genuine cheap checks

Introduce a narrowly scoped `research_triage` operation, or an equivalently strict mode supported by the current queue, with outputs such as `no_material_change`, `needs_analysis`, `duplicate`, `defer`, and `uncertain`. Its receipt is a check result, not a new financial assessment.

A Luna check may not create/refresh valuation, increase confidence, accept a causal relationship, change portfolio eligibility, create a strategy/order, or submit final approval. Checking a source without new evidence must not extend the financial assessment's expiration. Use deterministic current-price repricing where appropriate without a gratuitous LLM call.

Escalation produces one deduplicated GPT-5.6 operation with exact reasons and evidence. Retries keep the same investigation identity. Material or portfolio-sensitive uncertainty cannot be dismissed by cheap triage. Luna failures never silently discard a deterministic RSI alert or protected risk obligation.

Do not give the Astra role every command allowed to `deep` merely because it uses a larger model. Define an explicit deny-by-default command capability for its result path and bounded evidence access. The trusted parent records actual model/provider/reasoning/attempt identifiers; agent-supplied model labels cannot authenticate a review.

## 5. Mandatory Astra final-buy gate

This is a cross-cutting execution feature and must ship before any new-exposure path is enabled under the new policy.

### 5.1 Concrete trigger, not every bullish rating

Trigger only when the existing system has produced a concrete buy intent and all current deterministic preflight checks pass: supported identity/instrument, valid research, allocation or conviction strategy, live signal, exact intended legs, permissible sizing, cash/reserve, liquidity, concentration, turnover, price/FX, and existing economic gates.

A `BUY` rating in a wiki page or dashboard alone does not trigger Astra. An otherwise ineligible candidate does not consume a final-review slot. A sell, hold, zero delta, superseded request, or no-trade result does not cause an unnecessary Astra call.

Cover both `order create` and `order create-baseline`, supported options/multi-leg entry paths, retries, manually invoked repository execution, and already pending orders at deployment. Do not introduce a bypass through another CLI, a baseline path, a dry-run flag, or an import path.

### 5.2 Controller-owned review packet

Create the packet with deterministic code after preflight. Suggested contents:

- Stable `review_request_id`, `intent_id`, security/issuer/venue/currency/contract identity, strategy/signal/allocation-intent identity, and policy/schema versions.
- Immutable assessment version, source-observation/evidence versions, accepted relationship version, and material claim/assumption versions.
- GPT-5.6 conclusion, scenarios and declared probabilities, risks, invalidation, previous-review delta, contrary evidence, challenge gaps, and template/method.
- Current validated price/FX/indicator timestamps, RSI trigger/episode where relevant, the full deterministic preflight result, and proposed exact legs/quantity/risk budget.
- Holdings/pending-exposure context and material common-assumption exposure; no credentials or unnecessary personal information.
- A finite validity interval and a **controller-set price/size/risk envelope**, all derived from current limits and the concrete intent rather than chosen freely by the model.
- References to canonical evidence that Astra may inspect read-only when checking decisive claims.

Separate identity fields and economically material hashes from incidental metadata. Do not invalidate a review merely because a new run ID, report, wiki timestamp, or price-only allocation plan ID was created. Conversely, a changed thesis, evidence version, underlying observation, proposed instrument, strategy intent, or increased requested risk cannot reuse old approval.

No arbitrary "plus 5%" price tolerance. Compute any allowed execution range from the same existing valuation/risk/price rules, bounded by the reviewed intent. Initially exact quantity is simplest; a lower unfilled quantity may be accepted only when the existing allocation intent and deterministic limits permit it. Increases and changed leg composition require a new packet.

### 5.3 Astra review contract

Use a fresh, bounded reviewer context. Astra checks original decisive evidence and the reasoning chain; it must not simply endorse the first analyst's conclusion. Consider source dependence, stale financial periods, contradictory evidence, demand versus value capture, what may already be priced in, scenario assumptions, downside, timing, RSI false-positive explanations, and fit of the exact proposed purchase.

Emit one structured disposition:

| Decision | Meaning | System response |
|---|---|---|
| `APPROVE` | Exact packet is defensible under its recorded limits. | Parent validates/authenticates the result, binds approval, and may submit deterministically. |
| `REJECT` | A substantive reason contradicts proceeding on this unchanged intent. | Block this buy intent; report reason and reconsideration conditions. |
| `DEFER` | Specific decisive information is missing, conflicting, or unavailable. | Keep this intent pending review; enqueue bounded corrective research when justified. |

A runtime timeout, schema error, unavailable model, or missing result is an **operational failure**, never an approval or a reason to pretend the investment was substantively rejected.

Required result fields include packet identity/hash, disposition, concise reasoning, examined evidence references, counterevidence/alternative explanation, material issues, uncertainty, and reconsideration conditions. Forbid silent mutation of first-pass assumptions, valuation, quantities, or policy. If any must change, route a correction through GPT-5.6/deterministic state, recompute preflight, and produce a new material packet.

Astra cannot enlarge the approval envelope. It cannot override a hard gate. `APPROVE` with conditions requiring new information is invalid; use `DEFER` instead. Do not repeatedly ask for a different answer on unchanged inputs. A veto is reconsidered only with new material evidence, a new qualified intent, or an explicit recorded user-requested review—never a bypass.

This gate is not a guarantee of correctness or profit. It adds a documented challenge at the decision boundary; the assessment still contains uncertainty.

### 5.4 Persistence and enforcement

Recommended additions, adapted to existing schema conventions:

```text
src/papertrader/buy_review.py
skills/papertrader-final-buy-review/SKILL.md
schemas/buy_review_packet.schema.json
schemas/buy_review_result.schema.json
data/tables/buy_review_history.csv       # append-only accepted review history
data/tables/buy_reviews.csv              # current projection
data/tables/order_buy_approvals.csv      # order/intent -> approved review binding
data/runs/<cycle>/<operation>/final_buy_packet.json
data/runs/<cycle>/<operation>/final_buy_review.json
```

A separate binding table can avoid rewriting historical executions. New data contracts still require explicit versioning and reconciliation. Persist accepted review evidence and model provenance so retention does not delete the only proof supporting an executed purchase.

Enforce clearance in both order admission and the deterministic fill path. The parent, not a general research CLI caller, authenticates the reviewer invocation and records its accepted outcome. A fabricated JSON file with `model=gpt-6-astra` must fail.

Use a logical transaction for approval binding and order creation. A crash after review acceptance resumes the same intent; it does not buy twice or repeatedly pay for identical review. Replays return original receipts and preserve later valid state. Rejection/defer cancels no legitimate protective exit.

### 5.5 No stale or retroactive approval

For new exposure, effective execution eligibility must start no earlier than:

```text
max(signal activation, order not-before, accepted approval activation)
```

The filled market event must follow that boundary. A review completed after an already observed opening price cannot authorize a retroactive fill at that opening. Update `next_open`, `limit_touch`, and `quote_mid` tests accordingly; use only time-resolution the data can support. A daily OHLC bar must not infer a touch occurred after an intraday approval without evidence.

Use approval validity at the simulated execution time plus current known disqualifying changes under the established conservative fill policy. Expiry alone at a later processing time need not erase an otherwise demonstrably valid historical event, but no review may contain information unavailable at the event it authorizes. Record both event time and processing/acceptance time. Unknown ordering must defer, not invent contemporaneous clearance.

Cap validity by the intent/order expiry, evidence/assessment validity, and market session constraints. Use the current default 24-hour order expiry only where applicable; do not create a long-lived company-wide approval. Pre-fill deterministic cash/exposure and pricing checks remain mandatory, particularly across multiple approved purchases. Track total approved and remaining quantity so approvals cannot be reused beyond their scope.

Old unfilled buy orders without approval must be held/reviewed or terminalized using a recorded migration disposition. Completed historical executions remain untouched and are labeled pre-policy, not backfilled with fictional approval. Replay/repair of already recorded executions must remain possible without retroactive review.

### 5.6 Operation budget and avoiding starvation

Add `final_buy_review` to the existing sequential operation routing. It consumes a real slot, timeout, and model budget, including failures. Allocate a configurable reserved slot from the existing cycle capacity when an eligible intent exists; unused reserved capacity returns to research. Do not add this after an already exhausted budget and pretend it is free.

The final review should be the last model operation **for its buy intent**. Following acceptance, trusted code submits the exact intent without a second execution-agent opinion. Other unrelated sequential research can still run. If an ordinary batch produces a newly eligible intent too late, persist it and prioritize it next cycle unless reserved capacity is available.

Review deferral/veto is a legitimate business outcome; no purchase is required for a successful daily run. Operational malfunction must remain visible as malfunction.

## 6. Stronger RSI-oversold research priority

Preserve the existing RSI computation, period, configured oversold threshold, data provenance, and trigger semantics. The inspected defaults are RSI(14) with oversold level 30. This requirement changes **attention**, not the indicator formula or a buy rule.

### 6.1 Scheduling policy

PaperTrader uses higher numeric priorities for more urgent work, unlike WikiPlant's inverse example. Preserve and regression-test the actual scheduler ordering; do not reverse it during migration.

Proposed defaults:

| Class | Suggested priority | Notes |
|---|---:|---|
| Non-deferrable exposure/risk obligation | 100 | Genuine current exposure/cash/expiry urgency, not a popularity label. |
| Ready final-buy review | 99 | Only with valid preflight; no manufactured candidate. |
| Fresh eligible RSI oversold investigation | 98 | Explicitly above existing generic price-alert research at 95. |
| Other material price-alert research | Existing 95 | Preserve current behavior unless deduplicated. |
| Ordinary monitoring/maintenance/research | Existing policy | Age/fairness still apply. |

Numeric boosts alone are insufficient because existing merge logic can push routine rows toward 100. Add a validated scheduling class/tie-breaker or equivalent policy so fresh RSI research is not buried by accumulated incidental boosts. Urgency class is controller-derived, not arbitrary payload prose.

Reserve at least one available research slot for eligible RSI-oversold work per normal cycle when present, after genuinely non-deferrable risk and ready final approvals. Record a reason when it cannot run. Reuse unused reserves. Avoid fixed partitions that waste a five-operation cycle when some lanes are empty.

### 6.2 End-to-end propagation

Carry the exact RSI value, threshold, observation/session time, indicator source hash, episode ID, transition, freshness, cause, and original queue age through candidate, triage, security research, escalation, and reporting.

A pending ordinary review for that security should absorb the RSI cause and move up without creating redundant full-review work. Preserve running/blocked immutable requests and existing dependency rules; record a new observation separately for incorporation when safe. Don't delete unresolved obligations to simplify a merge.

Luna can assess novelty and help assemble a focused question. It cannot erase a valid priority cause because it dislikes the investment. If existing deterministic alert creation bypasses the ingestion classifier, preserve that reliability.

### 6.3 Episode and validity rules

Use entered/strengthened episodes and existing cooldown semantics to avoid one investigation per bar. Material worsening, genuinely new evidence, recovery/re-entry, or an explicit bounded recheck policy can justify another attempt. Preserve first-seen queue age and causal lineage on merges. Detect stale snapshots, holidays, missing history, corrected bars, or indicator recalculation; never synthesize an RSI observation.

If the oversold condition no longer holds before execution, re-evaluate the cause without discarding still-material risk/thesis research. Downgrade or expire only the obsolete urgency and explain it.

A completed RSI investigation distinguishes valuation opportunity, deterioration, event risk, and noise. RSI oversold neither raises confidence automatically nor bypasses existing financial gates or Astra. Evaluate the preference later with point-in-time data; do not claim it improves returns merely because it is prioritized.

## 7. Research scope, workload governance, and compact memory

### 7.1 Single canonical scope representation

Extend canonical tables through validated CLI transitions; render human-readable wiki views. Recommended fields in `research_topics.csv` include topic ID, class, anchor IDs, parent IDs, user-request reference, relevance rationale, lifecycle, review/expiry time, and policy version. Do not maintain an independently editable parallel topic list.

Classes are user-directed, directly adjacent, and peripheral. Operational protection is a separate deterministic overlay derived from holdings/orders/active strategies and their material risk dependencies. User-requested tracking is distinct from a one-off research or saved note.

An adjacent topic must justify its own direct economic relevance to the original anchor. Peripheral investigations are terminal; no subresearch, recurring refresh, maintenance relabeling, priority reset, or archive/reactivation reset. Promotion requires an actual newly established direct connection. Contrary evidence is classified by relevance, not agreement.

Map thesis/claim contributions, not just graph hop counts or ticker tags. A remote supplier with material exposure can qualify; a nearby buzzword association need not. Keep manual top-level idea policy.

### 7.2 Distinguish discovery, propagation, and repricing

Add an explicit research change classification:

```text
price_only | no_material_change | entity_delta
relationship_change | thesis_change | new_material_exposure | source_correction
```

Code owns exact factual/version comparisons; the analyst explains semantic materiality with evidence. A changed timestamp or paragraph does not itself prove new information.

Price-only changes use existing deterministic repricing. Unchanged results record a check without generating a broad research tree. Several security deltas for one idea coalesce into one bounded idea update with all immutable result references and a processed-cause ledger. Broad idea discovery runs only when scope or material mechanism changes justify it.

Preserve a comprehensive retained candidate slate where the current skill requires it; **do not impose WikiPlant's literal three-child quota on PaperTrader's value-chain research**. Instead admit expensive investigations selectively under capacity, novelty, and decision relevance. Deferred ideas are not discarded or mislabeled invalid.

### 7.3 Backpressure and semantic deduplication

Census active work by root, operation kind, ready/waiting/blocked state, age, cause, dependency, and estimated effort. Select capacity defaults from measured throughput and documented service goals. Existing overload is a migration state, not a schema error.

Cap automatic active obligations, not historical knowledge. Protect explicit user requests, risk reduction, material contradictions, final-review prerequisites, and RSI attention under their scheduling rules. Enforce capacity across calendar, discovery, maintenance, and research producers.

Re-evaluate old automatic questions; resolve obsolete blocked rows through the existing audited commands. Semantic deduplication should compare identity, purpose, evidence version, and time window—not collapse a legitimate later refresh. No arbitrary root reset through a new operation type or run ID.

### 7.4 Compact archival dispositions

Retain a 100–200-word summary target plus stable metadata, original evidence/version references, previous scope, actual conclusion, uncertainty, date, reason for stopping, lineage, and reactivation conditions. Merge duplicates rather than appending a capsule for every rediscovery.

Separate at least: no material exposure, unsupported thesis, invalidated thesis, unattractive valuation, catalyst expired, and deferred-for-capacity. A supported but expensive company is eligible for low-cost deterministic price-triggered reconsideration; it does not need daily broad research. An archived note is not an independent evidence source.

Save and verify the capsule before reducing active material. Preserve accounting, identities, assessment/source histories, cited evidence, user notes, unreported findings, and reproducible historical evaluations. Pruning working-tree context does not mean Git history becomes smaller or total storage stops growing.

Archived topics are retrieved selectively, do not spawn work, and have no automatic full-review obligation. A real new catalyst or user request can reactivate them after admission checks without resetting old causal limits. Protected operational entities never become unmonitored simply because their originating idea is archived.

## 8. Evidence assessment and adversarial research

### 8.1 Extend existing source and assessment history

Start with decision-driving claims rather than every sentence. Cover material revenue/margin/dilution/debt assumptions, actual exposure to a theme, thesis invalidation, and major catalysts.

Record stable claim versions and evidence links with source-observation IDs, exact locator or permitted extract, support/contradiction/qualification role, observation period, publication/retrieval times, methodology/directness, underlying evidence origin, applicability limits, and assessment rationale. Financial figures also need unit/currency, fiscal period, consolidated/segment scope, and accounting/normalization basis. Trace the relevant valuation assumption to the accepted claim version and to the assessment version that uses it.

Prefer additions that extend `source_registry`, `source_history`, and immutable assessment histories; introduce `research_claims`, `claim_history`, and `claim_evidence` only with explicit schemas and a single canonical owner. Do not use source ID existence, recent re-fetching, publisher prestige, or number of URLs as proof of the exact proposition.

Separate research urgency, evidence quality, and confidence. Different publications repeating one issuer claim are not independent confirmation. An issuer presentation hosted by a regulator remains an issuer statement. Unknown origin dependence stays unknown. Research summaries and archived wiki capsules cannot confirm their own underlying evidence.

Use states such as reported, supported, disputed, uncertain, hypothesis, user-note, superseded; preserve legacy status provenance during migration. Do not invent missing historical passages or automatically mark old assessments high quality.

Keep most new quality findings as candidate-scoped diagnostics/soft gaps initially. Calibrate stricter rules with fixtures and shadow comparisons before enforcing them. Existing decisive evidence/identity/valuation hard blockers remain. No generic requirement for perfect corroboration, a universal increase to margin of safety, or an added arbitrary return hurdle.

### 8.2 Observable challenge, not a bearish paragraph

Add a structured adversarial-review section to existing idea/security/relationship research results. For consequential conclusions, record favored hypothesis, strongest plausible alternative, falsification condition, search/inspection receipts, relevant contrary evidence, blind spots, and effect on assumptions/confidence/scenarios.

Distinguish `not_searched`, `searched`, `partial`, `blocked`, and justified `not_required`. A bear case containing smaller numbers does not prove disconfirmation was attempted. Evaluate theme truth, issuer economic capture, and market pricing separately. No artificial equal-weight treatment for weak criticism; evidence merit is claim-specific.

A small challenge fits the existing operation budget. Deeper missing validation is one deduplicated queued operation, scheduled with fairness and protected risk priority. Peripheral research remains terminal even when a deeper unresolved issue is interesting. Use sequential passes only. Astra reuses the prior challenge record as input but independently checks decisive points rather than treating the first model as authority.

### 8.3 Corrections and correlated assumptions

Represent source -> claim -> assumption -> assessment -> relationship/strategy dependencies. A correction creates scoped impact tasks, marks uncertainty appropriately, invalidates materially affected outstanding Astra clearances, and updates the user report. Formatting changes do not invalidate financial conclusions. An unsubstantiated rumor may warrant investigation without automatically canceling every related investment.

Report shared thesis dependence across candidates/holdings, such as multiple exposures relying on the same demand assumption or origin of evidence. Start with visibility, not a new hard concentration rule. Existing sector/theme risk limits stay authoritative.

## 9. Monitoring, calendar, semantic maintenance, reporting, and evaluation

### 9.1 Protected monitoring, not unlimited daily full reviews

Maintain deterministic market/FX/indicator checks for the configured universe. Introduce bounded primary-evidence monitoring for holdings, pending/active exposure, selected user themes, major catalysts, and invalidation conditions. Keep its capacity separate from expensive deep investigations for accounting, but include its real model/time cost in the global cycle ceiling.

Record coverage windows, topics actually checked, search successes/failures, observation/source hashes, and discovered material deltas. A reserved or failed search is not evidence of "no update." Do not promise complete monitoring of every watchlist name within a small daily budget.

A source hash change is a candidate change; cheap triage and materiality review determine what follows. New reporting about an older event may contain new evidence. Preserve publication, event, fiscal period, and retrieval times separately.

### 9.2 Catalysts and dates

Use normalized events with immutable occurrence IDs, evidence, relevant claims/entities, date precision, timezone, status, expected window, pre/post-event questions, and rescheduling history. Integrate with existing operation `not_before`, deadlines, and review dates instead of building a separate scheduler.

Process overdue unhandled occurrences without creating unlimited historical catch-up jobs. Current same-day events may appear in reports even when deeper research cannot run. Test weekends, market holidays, non-UTC deadlines, daylight saving changes, partial dates, cancellations, and event amendments. A peripheral item cannot create a recurring research obligation through the calendar.

### 9.3 Weekly semantic maintenance

Extend the existing native wiki maintenance integration. Keep structural lint deterministic and separate from semantic audit. Maintain a rotating inventory plus priority for changed evidence, material common assumptions, unresolved contradictions, stale important claims, unsupported promotions, redundant broad refreshes, and expired exploratory topics.

Audit contradictions across pages, with entity aliases, periods, units, instrument/segment scope, and assumptions. Do not label a temporal update a contradiction. Do not consider a nonempty historical `last_checked_at` sufficient freshness.

Record exact inventory/page/claim coverage; never call a bounded subset a full audit. Model failure on one source must not suppress independent safe operations or the partial report. Preserve open questions with state, not recurring weekly duplicates.

### 9.4 Reporting and portfolio displays

Add structured finding IDs, material change class, supporting claim/evidence versions, affected assessments/assumptions, confidence/limitations, and report coverage state. Distinguish price-only repricing, new facts, hypothesis, correction, and unresolved risk. Include explicit RSI-oversold attention and final-buy-review status/reasons.

Separate a research `BUY` rating from `awaiting_final_review`, `final_review_rejected`, `approved_order_pending`, and `filled`. Only a canonical live approved order can support a new-exposure copy-ready action. Do not conceal a buy veto by rewriting the original research conclusion to match it; display both and their reasons.

Reports should cover completed but unreported research across cycles/manual operations. Mark a finding represented only when it actually appears in the report or an explicit linked appendix. Saving, publishing, Telegram delivery, and user observation are different receipts. Retry delivery without repeating completed research or fabricating notification receipt.

### 9.5 Learning without hindsight

Add point-in-time research evaluation alongside current portfolio performance and the comparison benchmark. Keep rejected/archived candidates and their original reasons so the dataset is not filtered to successes.

Measure queue latency/admissions/completions, expensive calls per useful conclusion, unchanged-result propagation, evidence dependence, correction latency, challenge effectiveness, final-gate approval/defer/veto rates and reasons, repeated-review rate, time from deterministic eligibility to submission, and RSI investigation latency/yield.

Where forecasts are falsifiable, register their horizon, event definition, probability, and frozen input versions. An intrinsic fair value is not automatically a forecast of market price on a fixed date. A profitable paper fill does not prove the thesis or final reviewer was correct. Replay datasets must use only information available at the decision time, including the Astra approval time.

## 10. Disable automatic podcasts; keep manual generation intact

### 10.1 Required behavior

- Scheduled daily runs never generate a podcast transcript, audio, translation, or podcast delivery.
- Ordinary manual daily dispatch also defaults to no podcast.
- Podcast production occurs only from an explicit manual request, e.g. `workflow_dispatch` with `generate_podcast=true`, or the established explicit manual podcast operation.
- Historical podcast transcripts and manual tools remain. Do not remove TTS or translation functionality just to make daily automation pass.
- Text report generation/delivery, decision snapshots, Pages, ordinary research, and accounting are unchanged.

### 10.2 Implementation boundaries

Audit `.github/workflows/daily.yml`, `reusable-llm.yml`, reporting/final outcome jobs, CLI defaults, daily-cycle manifests, podcast queue producers, direct operation filters, scheduled reusable callers, and resume logic.

Replace scheduled-event expressions that force `generate_podcast=true`. Centralize a deterministic podcast-origin policy so stale queued podcast operations cannot be executed by a normal research batch. Explicit manual work can be processed only under a matching recorded manual authorization/cycle. Do not infer authorization from a filename or any arbitrary `source` string.

Migrate unfinished cycles deliberately: preserve their original audit, record the policy transition, and mark no-longer-authorized automatic podcast obligations as `skipped/disabled_by_policy` or the established equivalent. Do not leave cycles forever waiting for audio, falsely mark it succeeded, or destroy already published transcripts. Manual requests still pending remain visible for manual processing.

A disabled automatic podcast is a normal outcome; it must not fail `daily_outcome`. A genuinely requested manual podcast failure remains observable. Update documentation, examples, generated reports, and tests that previously assumed daily audio.

## 11. Development milestones and order

Implement within the existing code organization. Proposed module names are contracts to cover, not a demand for needless micro-modules or a new framework. Reuse working code and validate assumptions on the actual checkout.

| Milestone | Implementation | Principal files/areas | Exit evidence |
|---|---|---|---|
| M0 | Baseline, queue census, contract/authority inventory, test reproduction, migration design. | `AGENTS.md`, `PLAN.md`, config, tables, current tests and prior analysis. | Recorded baseline SHA, test commands/results, root-cause taxonomy, call graph for every order/fill path. |
| M1 | Manual-only podcasts and consistent runtime/docs policy. | Daily/reusable workflows, `daily.py`, `podcast.py`, queue, CLI, cycle status. | Schedule/default/manual/resume behavior tested; normal reports preserved. |
| M2 | Constrained Luna triage; preserve GPT-5.6; add Astra role/capability metadata. | `profiles.py`, `config.py`, `agent_runner.py`, command scope/audit, schemas/skills. | Route and denied-command tests; actual provider availability recorded separately. |
| M3 | Final-buy packet, authentic review receipt, durable history, all-path order/fill enforcement. | `buy_review.py`, `orders.py`, `execution.py`, `risk.py`, allocation/strategy flows, runner, result validator. | Positive and negative integration matrix; no bypass; no lookahead; safe legacy pending-order migration. |
| M4 | RSI preferred attention, cause-preserving merges, capacity reservation and episode rules. | `indicators.py`, `opportunity.py`, `queue.py`, `dedupe.py`, triage/research skills, reports. | RSI outranks ordinary alerts, dedupes, and never bypasses final purchase requirements. |
| M5 | Scope graph, protected obligations, admission backpressure, delta propagation/coalescing. | Research/relationship skills, `research.py`, `queue.py`, scope contracts. | Migration retains obligations; unchanged results stop broad cascades; comprehensive candidates remain accessible. |
| M6 | Compact archives and explicit research dispositions. | `wiki.py`, `retention.py`, tables, catalog, maintenance/query views. | Reference-safe compaction, no protected pruning, no autonomous archived-topic growth. |
| M7 | Claim/evidence schema, origin dependence, adversarial reviews, correction impacts. | `research.py`, rubrics/templates, evidence tables, result validator, Astra packet builder. | Source laundering/correction/challenge fixtures; diagnostic effect separated from financial gates. |
| M8 | Protected monitoring, catalyst occurrences, semantic weekly audit, finding coverage and metrics. | `daily.py`, wiki maintenance, reports/publication/advice, operation payloads. | Honest coverage, failure isolation, no omitted-but-reported findings, point-in-time metrics. |
| M9 | Cross-cutting migration, offline replay, behavioral/security evaluations, preflight for deployment. | Integrity, atomic IO, tests, migration CLI, schema versions, docs. | Reconstructed-state tests, no ledger changes except expected paper transitions, validated rollback. |
| M10 | Main commit/push, live daily run, inspect results, fix and repeat until success. | Git/Actions + same validation workflow. | Exact successful run and tested source SHA plus post-run data validation and candid unexercised-path list. |

M3 depends on M2 and uses current first-pass evidence at first; enrich its packet in M7 without delaying basic fail-closed enforcement. M5-M8 changes must preserve M3's state binding. Build and test each milestone before integrating the next. Production activation of the final gate, podcast change, and RSI priority is required; do not leave them silently disabled behind a feature flag after claiming completion.

New topic/evidence policies may begin in diagnostic mode to inspect legacy effects. Promote them deliberately after scoped fixtures, migration reconciliation, and recorded review, never by rewriting historical assessments to make the migration pass. Evidence diagnostics must not accidentally become new blanket cash-only rules.

## 12. Acceptance test matrix

Use the existing test framework and repository fixtures. Add regression assertions about persisted state, effective permissions, and mathematical invariants, not just phase labels or helper method calls. All statuses below are **NOT RUN in this planning task**.

### A. Models and authority

- [ ] A01: Deterministic checks do not invoke a model.
- [ ] A02: Simple semantic triage actually selects Luna; existing full assessments stay on GPT-5.6.
- [ ] A03: Luna cannot upsert assessments, elevate confidence, accept material relationships, approve a buy, or create an order.
- [ ] A04: Material/uncertain triage escalates once without losing the original cause, freshness, or queue age.
- [ ] A05: Final review selects actual Astra; a model-name field in arbitrary JSON cannot authenticate it.
- [ ] A06: Astra unavailable/malformed/timeout leaves no approval; no fallback to Luna or GPT-5.6 can authorize purchase.
- [ ] A07: The final-review role cannot mutate original assessment, quantity, limits, ledgers, or unrelated files.
- [ ] A08: Profile/reasoning/provider routing and attempt/budget receipts survive restart and audit pruning.

### B. Final buy review and execution

- [ ] B01: Ineligible/hold/no-quantity/no-strategy cases never call Astra.
- [ ] B02: Otherwise-eligible baseline open/increase and conviction buys require final approval.
- [ ] B03: Supported option purchases and mixed rolls cannot bypass clearance; legs are bound as a package.
- [ ] B04: Pure reductions/closes/cancels and strictly risk-reducing buy-to-cover remain available; crossing zero is not exempt.
- [ ] B05: Direct/manual CLI order creation enforces the same production gate.
- [ ] B06: Valid approval produces at most one canonical order for its intent, with no later lower-tier model purchase judgment.
- [ ] B07: Rejected/deferred unchanged packets are not repeatedly reviewed in search of approval.
- [ ] B08: Changed assessment, relationship, decisive source observation, strategy intent, instrument, or increased quantity invalidates approval.
- [ ] B09: Incidental report/run timestamps and permitted price-only plan changes do not trigger unnecessary repeat review.
- [ ] B10: Quote/FX/fill price outside the approved envelope or stale validity defers execution without overriding existing risk checks.
- [ ] B11: Approval is bound to remaining authorized quantity; partial fills and retries cannot overconsume it.
- [ ] B12: Acceptance interrupted before order creation resumes without a second purchase or repeated identical model call.
- [ ] B13: Post-review concurrent/material state change is rejected or deterministically rebased before submission.
- [ ] B14: A next-open/limit/quote event before approval acceptance can never be filled using that approval.
- [ ] B15: Daily OHLC timing cannot backfill an unknowable intraday post-approval touch.
- [ ] B16: Independent approved buys still obey aggregate current cash, exposure, concentration, and turnover at fill.
- [ ] B17: Existing unfilled legacy buys are reviewed/held; completed historical executions are not retroactively changed.
- [ ] B18: Recovery of already recorded executions/cash is not blocked by missing historical final review.
- [ ] B19: Unsupported model/credential failure is operationally visible; a valid business veto is not treated as a coding failure.
- [ ] B20: A full daily run may succeed with zero buys, without faking exercise of the positive live gate.

### C. RSI scheduling

- [ ] C01: Current configured RSI formula/threshold and source dates are unchanged by priority work.
- [ ] C02: Eligible oversold research outranks ordinary generic alerts even when legacy merge boosts inflate their raw priority.
- [ ] C03: Non-deferrable current risk and ready final reviews keep their precedence; available RSI reserve prevents routine starvation.
- [ ] C04: Depth/recency/age tiebreaking is deterministic, unit-tested, and documented.
- [ ] C05: Pending ordinary research absorbs RSI reason and retains original queue age/history; no redundant full analysis.
- [ ] C06: Running/blocked immutable requests and their dependency contracts are not overwritten by alert merging.
- [ ] C07: Sustained oversold bars do not flood the queue; genuine strengthening/re-entry can be reconsidered under policy.
- [ ] C08: Corrected, stale, missing-history, holiday, and duplicate snapshots cannot invent events or urgency.
- [ ] C09: Luna failure/ignore cannot silently erase the policy-required deterministic RSI research cause.
- [ ] C10: RSI recovery downgrades obsolete urgency while retaining still-material thesis/risk work.
- [ ] C11: RSI improves attention only; no valuation, cash, risk, or Astra bypass.

### D. Research scope, propagation, archives

- [ ] D01: Only explicit tracking creates a user anchor; one-off save/research does not.
- [ ] D02: Adjacent topics demonstrate direct contribution to a user anchor; chains cannot rebase their own scope.
- [ ] D03: Material distant suppliers/risks are admitted; superficial popular associations can be rejected.
- [ ] D04: Peripheral research cannot spawn through research, calendar, maintenance, discovery, urgency, or archive/reactivation.
- [ ] D05: Holdings/orders/strategies retain required monitoring when an originating idea is archived.
- [ ] D06: Opposing evidence remains relevant; disagreement cannot be used to prune a critique.
- [ ] D07: Multiple security deltas coalesce into one bounded idea update without losing a result reference.
- [ ] D08: Price-only/unchanged updates do not repeatedly launch broad value-chain discovery.
- [ ] D09: Candidate slates stay comprehensive while expensive work admission is bounded; user requests are not silently dropped.
- [ ] D10: Legacy backlog migration preserves ready/waiting/blocked obligations and original disposition reasons.
- [ ] D11: Archive compaction preserves cited evidence, manual notes, unreported findings, and evaluation records.
- [ ] D12: Reading an archive does not reactivate it; material new evidence can reactivate without a lineage reset.
- [ ] D13: Capacity deferral, no exposure, unsupported thesis, invalidation, and unattractive valuation remain distinct.
- [ ] D14: Reactivation after a price change uses deterministic repricing when sufficient, not a fabricated new root.

### E. Evidence, challenge, monitoring, and reports

- [ ] E01: Ten syndicated articles do not count as ten independent sources.
- [ ] E02: An issuer statement's hosting domain does not change the origin of its forecast.
- [ ] E03: A fresh retrieval of old financial-period data does not make it a current-period observation.
- [ ] E04: Source existence and a plausible hash cannot fabricate inspected support for a material claim.
- [ ] E05: Claim versions retain exact period/unit/currency/scope, evidence locator, uncertainty, and assessment linkage.
- [ ] E06: Adversarial review seeks the strongest relevant alternative; a boilerplate bear paragraph is not sufficient.
- [ ] E07: Unavailable counterevidence search remains partial/blocked; lack of a contrary result is not proof of correctness.
- [ ] E08: A correction identifies downstream assessments/approvals; purely cosmetic source changes do not invalidate everything.
- [ ] E09: Common-assumption exposure is reported without silently changing existing portfolio limits.
- [ ] E10: Cross-page conflicts account for entities, time intervals, units, and conditional statements.
- [ ] E11: Semantic freshness is elapsed-time/materiality aware, not just a nonempty timestamp.
- [ ] E12: Monitoring is counted and bounded; a failed/reserved query cannot be logged as successful no-update coverage.
- [ ] E13: Date precision, timezone/DST, late events, recurrence, rescheduling, and cancellations preserve stable occurrences.
- [ ] E14: A stage/model/source exception does not discard independently completed work or prevent a possible partial report.
- [ ] E15: Findings omitted from a limited report remain reportable; manual and prior-cycle findings are included once.
- [ ] E16: Notification/delivery retry does not rerun research or claim the user read a report.
- [ ] E17: Output distinguishes research BUY, awaiting Astra, veto, approved pending order, and filled position.
- [ ] E18: Point-in-time evaluation includes rejected/archived candidates, actual review time, and no future evidence.

### F. Podcast, migration, and deployment

- [ ] F01: Scheduled daily, reusable scheduled caller, and default manual daily perform no transcript/TTS/audio/podcast translation.
- [ ] F02: Explicit manual request still produces a podcast using the supported manual path.
- [ ] F03: Queued automatic podcasts and unfinished legacy cycles cannot restart automatic generation.
- [ ] F04: Disabled-by-policy is not failed and not fabricated success; explicit manual failure remains visible.
- [ ] F05: Text report, Telegram text, snapshot validation, and Pages still run normally.
- [ ] F06: Repeated migration is idempotent; later bot/user data is preserved across rebase and recovery.
- [ ] F07: New tables/artifacts are in validated schemas, allowlists, publication filters, and retention protection.
- [ ] F08: Prompt-injected source text cannot change models, RSI priorities, risk gates, approval records, commands, or scheduling policy.
- [ ] F09: Negated/quoted/hypothetical user text cannot create a new research anchor or manual podcast authorization.
- [ ] F10: Full non-dry-run daily dispatch is identified by exact run/source; child jobs and post-run invariants are checked.
- [ ] F11: Green with no eligible buys is labeled correctly; final positive live review is not claimed unless observed.
- [ ] F12: A failing required job is not hidden through skipped jobs, removed tests, weakened assertions, or `continue-on-error`.

## 13. Deployment and testing/fixing loop on main

### 13.1 Preparation

Read this plan and the current checkout. Inspect the working tree, remotes, branch, dependency locks, existing CI commands, credential availability, and workflow inputs. Preserve unrelated user edits. Work on `main` as requested; do not open a feature branch/PR instead. Never force-push, delete history, change protection, or use destructive cleanup.

Use pinned project dependencies and the existing test/lint/type/schema/integrity/publication commands. Discover actual CLI syntax; do not invent validation subcommands. Run locally on fixtures first. Public production data migrations require dry-run diffs and reconciliation before applying the requested repository changes.

Verify actual model routing through the existing provider without revealing credentials. Unavailable access is a real blocker, not permission to substitute another final reviewer. The user authorizes a real paper daily validation run, not a real financial trade.

### 13.2 Repeat until a successful daily run

1. Implement/fix a coherent change and add the relevant regression tests.
2. Run targeted tests, then the required broader local suite and integrity/publication checks. Record exact commands, outcomes, and unrun checks.
3. Review the diff for unintended data/policy changes, secrets, and generated clutter.
4. Fetch `origin/main`; reconcile bot or user commits without overwriting canonical ledgers. Commit the intended changes on `main`, synchronize safely, rerun affected checks after reconciliation, and push normally. If main protection forbids the requested push, report it rather than bypassing it.
5. Dispatch `.github/workflows/daily.yml` on **`main`** with `dry_run=false`, `generate_podcast=false`, no artificial operation filter, and the normal configured operation budget. Keep research/accounting/report/publication validation enabled. Do not use `max_operations=0`, a dry run, or disabled final review to obtain green.
6. Capture the returned run URL/ID when available. Otherwise identify the dispatch through workflow, branch, trigger, requested SHA, and creation window; require an unambiguous match. Do not watch whichever run happens to be newest. Main may advance through bot data commits—record the source the run actually used and require it to include the intended code/policy change.
7. Watch that exact run until completion, including the reusable runtime, delivery, Pages, and aggregate outcome jobs. Read failed-job logs and artifacts. A dispatch receipt or a successful single job is not completion.
8. On a code/config/schema/integration failure, identify the cause, add a regression when practical, fix it, and return to step 1. On a genuine transient service failure, apply bounded backoff and the project's supported resume/recovery logic instead of resetting accounting or blindly creating overlapping cycles.
9. After a green run, fetch its data commits and validate canonical reconciliation, accepted reviews, queue dispositions, disabled podcast behavior, report/snapshot consistency, and the lack of unauthorized fills. Confirm the code revision actually exercised.
10. Finish only with a real successful daily workflow **and** clean applicable post-run invariants. A valid no-buy outcome or Astra veto does not mean the implementation failed. Report any live scenario that did not naturally occur.

Continue the loop while meaningful fixes or safe retries are available. Do not set an arbitrary three-iteration success claim. Conversely, do not run an uncontrolled tight loop against exhausted quota, missing permissions, revoked credentials, a persistent external outage, or a hard session/tool boundary. Stop truthfully with the last commit/run, diagnostics, and minimum unresolved action when those cannot be repaired within authority. Never claim background monitoring or eventual success.

Respect runtime leases, sequential execution, budgets, and attempt records across every repeat. A rerun after a fix must contain the fix; re-running an old failed workflow attempt may use the old source. Choose a fresh dispatch or a supported checkpoint resume deliberately. Do not cancel unrelated scheduled work just to simplify validation.

### 13.3 GitHub CLI command shapes

These are command examples to adapt to the inspected input schema, not an unattended shell loop to copy without error handling:

```bash
gh workflow view daily.yml -R Kabutojira/PaperTrader --ref main --yaml

git fetch origin main
# Preserve/reconcile user and bot changes, stage explicit paths, and run tests.
git commit -m "feat: harden research governance and require Astra buy review"
git push origin main

gh workflow run daily.yml -R Kabutojira/PaperTrader --ref main \
  -f dry_run=false \
  -f generate_podcast=false

# Capture/resolve the run that belongs to this dispatch before watching it.
gh run watch "$RUN_ID" -R Kabutojira/PaperTrader --exit-status
gh run view "$RUN_ID" -R Kabutojira/PaperTrader \
  --json databaseId,headSha,event,status,conclusion,jobs,url
# For failures:
gh run view "$RUN_ID" -R Kabutojira/PaperTrader --log-failed
```

Use paginated API polling if the authenticated environment cannot support `gh run watch`, verifying the same exact run to its terminal result. This is a tooling fallback, not permission to weaken checks.

### 13.4 Final development report

Return completed milestones; changed code/policy/data contracts; migration reconciliation; local test commands/counts/results; actual effective model routing; RSI scheduling examples; Astra approved/vetoed/deferred cases and unavailable live cases; proof automatic podcast did not run; code and bot-state commits; exact final workflow URL/ID/SHA/conclusion; post-run integrity findings; and remaining blockers. Never equate no-trade with a missing implementation or a complete approval-path test.

## 14. Definition of done

- The implementation covers all mandatory user requirements and the adopted PaperTrader-specific governance improvements, with traceability in `docs/research-hardening-status.md`.
- Current `AGENTS.md`, `PLAN.md`, wiki schema, examples, model settings, workflows, CLI contracts, and actual runtime agree.
- Cheap semantic checks use Luna without financial authority; first-pass research remains GPT-5.6; eligible new buys require authenticated Astra approval at admission and valid clearance at fill.
- Existing deterministic gates and accounting remain authoritative; no real-order capability is introduced.
- RSI oversold has demonstrably stronger timely research attention, not automatic buy power.
- Podcast generation is exclusively explicit manual work; daily text/publication behavior remains.
- Scope control, backpressure, delta propagation, compact archival, evidence/challenge/correction workflows, monitoring, reporting coverage, and evaluation are implemented incrementally without deleting protected obligations.
- Schema migrations, restart/replay, pending legacy orders, report delivery, and bot-commit reconciliation are tested. Legacy missing evidence is labeled, not fabricated.
- A main-branch live daily run finishes successfully with unchanged safety requirements, and post-run state validates. Unobserved live branches of behavior are explicitly identified.

## 15. Source map and verification limits

Repository observations refer to the pinned baseline. The existing comparison analysis is useful context, but Codex must inspect its actual checkout and not apply stale assumptions blindly.

- [Baseline commit](https://github.com/Kabutojira/PaperTrader/commit/d43d79e1240fc11738e2af3ed24f1adaf12b88e5)
- [Current architecture and invariants](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/AGENTS.md)
- [Model, indicator, budget configuration](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/config.ini)
- [Profile routing and authority](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/src/papertrader/profiles.py)
- [Scheduled podcast behavior and daily inputs](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/.github/workflows/daily.yml)
- [Indicator transitions and existing 70/95 priorities](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/src/papertrader/opportunity.py)
- [Execution-agent decision path](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/skills/papertrader-execute-strategy/SKILL.md)
- [Simulated fill timing and persistence](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/src/papertrader/execution.py)
- [Security research and propagation](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/skills/papertrader-security-research/SKILL.md)
- [Idea research and candidate universe](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/skills/papertrader-idea-research/SKILL.md)
- [Research/source state validation](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/src/papertrader/research.py)
- [Result schema](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/schemas/agent_result.schema.json)
- [Daily preparation and report collection](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/src/papertrader/daily.py)
- [Retention](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/src/papertrader/retention.py)
- [Committed backlog/status snapshot](https://github.com/Kabutojira/PaperTrader/blob/d43d79e1240fc11738e2af3ed24f1adaf12b88e5/data/wiki/system-status.md)
- [OpenAI model catalog](https://developers.openai.com/api/docs/models)
- [GPT-6 Astra model and reasoning settings](https://developers.openai.com/api/docs/models/gpt-6-astra)
- [GPT-5.6 Sol alias](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [Workflow dispatch](https://cli.github.com/manual/gh_workflow_run)
- [Watching exact runs](https://cli.github.com/manual/gh_run_watch)
- [Run list identity filters](https://cli.github.com/manual/gh_run_list)
- [Run/job inspection](https://cli.github.com/manual/gh_run_view)

Official model documentation establishes identifiers and API features, not availability through a particular Hermes account or comparative effectiveness on this project. The RSI preference and proposed scheduling/effort defaults are implementation policies, not proven investing performance. No remote write, daily dispatch, trading operation, or software test was performed while drafting this plan.

## Implementation log

### 2026-09-11 — initial local M1/M2 work (not shipped)

Implemented manual-only daily/reusable podcast behavior, default media queue exclusion, an audited
legacy scheduled-podcast retirement command, read-only Luna triage with controller escalation, and
the constrained Astra profile groundwork. Preserved Terra/Sol first-pass routing and all existing
investment gates. Full local verification passed 557 tests before two final restart/identity
regressions were added; see the status document for the final verification result. One report
snapshot identity was regenerated because it includes the intentional configuration hash change.

At that initial checkpoint, the authenticated order/fill gate and milestones M3–M10 remained outstanding. There had been no
production data migration, commit, push, or live daily dispatch. These changes do not satisfy the
overall definition of done.

### 2026-09-11 — integrated implementation and migration rehearsal

Implemented the authenticated order/fill gate, shared RSI scheduling, scope/backpressure and
delta propagation, protected archives, immutable evidence/challenges/corrections, bounded
monitoring/calendar/forecast/finding coverage, and hash-bound hardening migration. Full pytest:
598 passed; Ruff and MyPy pass. A disposable production-data migration/finalization passed strict
schema/integrity/advice/wiki/reconciliation without changing executions, cash or portfolio bytes.
The zero-model offline migration rehearsal does not satisfy M10. Production activation, source
commit/push, normal-budget live workflow and post-run validation are the remaining deployment steps.
