---
title: Research rating methodology
---

# Research ratings

Valuations are sourced research opinions in the instrument's native currency.
They do not imply a position, allocation, order or short trade.

Weighted fair value is the sum of scenario fair value times probability; probabilities total 100%.
Implied return is 100 × (weighted fair value / latest completed-session price − 1).
Confidence adjusts return toward zero: high ×1, medium ×0.7, low ×0.4.
Rankings use this adjusted prospective return, descending for Buy and ascending for Sell,
with issuer ID and security ID as deterministic tie-breaks. Each list contains at most
one instrument per issuer and up to ten entries. It can be empty.

Default adjusted-return thresholds: Strong Buy ≥40%, Buy ≥20%, Sell ≤−10%,
Strong Sell ≤−25%; otherwise Hold. Buy also requires base return ≥10%; Strong Buy
requires base return ≥20% and high confidence. These thresholds are configured in research.ini.
At least medium confidence is required for a rating.

A supported valuation needs ordered bear/base/bull values, probabilities, cited scenario
assumptions, method/rationale, thesis, key assumptions, downside, catalysts, invalidation
conditions and a valuation horizon. A material unresolved valuation blocker requires an
unsupported outcome; an explicit `BLOCKER:` limitation also forces Unrated.
Source references must remain valid and must have been checked during the assessment.
Expired or future research, incomplete evidence, stale/invalid prices, identity/currency
mismatches and subsequent splits cannot enter current rankings. Missing charts never
make a valuation incomplete. Price changes never rewrite assessed fair values or dates.

Historical research remains browseable with freshness visible in the company catalog.
Unrated and stale records are excluded from both ranking lists.

## Bearish research universe and Short

`research_role` is independent of catalog status and research completion:
`long` (Long interest), `short_candidate` (Short candidate), and
`short_research_only` (Research only). Membership describes why an instrument is
researched, never its conclusion. Both bearish roles are excluded from ordinary
Top 10 Buy rankings even when their individual appraisal is Buy or Hold.

Sell denotes researched prospective downside. Strong Sell denotes substantial
researched prospective downside. Short adds independently evidenced business or
financial weakness to substantial downside. Default Short gates, configured in
`research.ini` under `[ratings]`, are all required:

- `short_candidate` role, complete supported current research, current completed-session
  native-currency price and every existing identity, scenario and source gate.
- `short_minimum_confidence = medium` (medium or high only).
- `short_return_pct = -30`: adjusted expected return at most −30%.
- `short_maximum_base_return = -20`: base case return at most −20%.
- `short_maximum_business_quality = 25` or `short_maximum_balance_sheet = 25`.
- `short_minimum_risk_penalty = 75`.

All three fundamental components must be populated under rubric 1 with valid,
current, instrument-linked source IDs and rationales. Missing evidence prevents
Short. Other cases use the unchanged ordinary rating calculation; a strong but
expensive leader can receive Strong Sell without qualifying for Short.
Research-only candidates cannot receive Short. Short joins the current Sell list,
ordered by adjusted expected return with the same issuer deduplication and ten-issuer
cap. Unrated, expired and unsupported cases remain visible outside current rankings.

Short is a fundamental research opinion, not an instruction to sell short or buy
a put today. None of Sell, Strong Sell or Short automatically establishes an
actionable options trade; liquidity, spreads, volatility, catalysts, timing and
corporate actions require separate verified analysis. Options remain informational.
