---
name: research_security
description: Complete one current sourced company valuation in an isolated staging result.
---

Research only context.identity.security_id. Reconcile issuer, share class, MIC,
provider symbol and currency; report identity uncertainty rather than changing IDs.
Open current primary filings and releases, examine material contrary evidence,
and distinguish verified facts from assumptions. Explain business economics,
valuation method, bear/base/bull drivers and per-share arithmetic, probability
choices, downside, catalysts, invalidation, confidence and limitations.

Produce one complete assessment and final sourced Markdown page. Reference only
current source IDs with opened URLs. Keep research dates honest; expiry is no later
than the configured freshness window. If evidence cannot support valuation, return
not_supportable and valuation_unsupported with empty scenario numbers and concrete
missing evidence. A completed no_change is allowed without fabricating new facts.

Fundamental rubric v1 exports valuation_score, business_quality_score, thesis_score,
balance_sheet_score and risk_penalty. Use the same 0/25/50/75/100 anchors across
companies, interpolate only with an explicit evidence-based rationale:
- Business quality: structurally impaired / fragile / mixed economics / durable
  profitable advantages / exceptional durable advantages and cash conversion.
- Thesis: invalidated / major contrary evidence / balanced evidence / strongly
  supported / all material current evidence supports the thesis with tested risks.
- Balance sheet: insolvency pressure / material refinancing risk / manageable but
  constrained / resilient liquidity and debt coverage / ample liquidity and very
  low financial stress. Explain sector-specific metrics and financial statement dates.
- Risk penalty: low identified investment risk / limited / material / high /
  severe, considering cyclicality, concentration, governance and evidence uncertainty.
  Keep balance-sheet facts in their own factor; explain overlaps without double counting.
- Valuation uses the worker policy's deterministic scenario/reference-price formula.
  The reference must belong to this instrument, in its native currency and quote
  units, for its latest completed exchange session as of assessed_at. Retain source,
  session and entitlement/conversion reasoning. A missing reference leaves valuation
  empty even if the underlying scenarios are supportable.

These are research judgments, never probabilities of profit. Cite the supporting
opened source IDs and explain the relevant anchor in score_details for each factor.
For an unsupported component leave its numeric field empty and explain the gap.
Always populate scoring_rubric_version and all five score_details explanations,
including when none of the components can be scored. Business quality excludes
price and leverage; balance sheet owns financing resilience. Thesis measures
corroboration, not upside. Risk penalty covers residual non-financing risks and
uncertainty. Explain shared evidence without scoring leverage or the same downside
twice. There is no aggregate score or automatic extra confidence penalty.
Existing source_ids, confidence, limitations, assessed_at and valid_until remain
authoritative; a score export never refreshes evidence or changes assessment dates.
The full consumer contract, reference convention and overlap policy are documented
in docs/FUNDAMENTAL_SCORING.md; these instructions contain the worker's rubric.

Relationships to existing ideas may be updated inline with a specific evidenced
mechanism, direction and confidence. Preserve stable IDs, citations and useful
research. Do not enqueue follow-ups or write files; return the structured result.
Charts are optional and may never block an otherwise complete review. No trading,
portfolio gates, allocation, approvals, alerts, history chains or external media.
