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
