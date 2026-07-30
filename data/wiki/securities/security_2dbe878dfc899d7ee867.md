---
title: Freeport-McMoRan Inc. common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-07-30"
provenance: "source_fcx_q2_2026_results_sec; source_fcx_sec_submissions_20260730; deterministic market cache"
security_id: security_2dbe878dfc899d7ee867
issuer_id: issuer_5076f0e0e1dd7cc8bca7
confidence: medium
next_review: "2026-08-29"
---

# Freeport-McMoRan Inc. common stock

## Identity

- Immutable security: `security_2dbe878dfc899d7ee867`
- Issuer: `issuer_5076f0e0e1dd7cc8bca7`
- Instrument: common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `FCX` / `XNYS` / `USD` / equity

This review links the verified instrument to [[ideas/idea_critical_minerals_copper]].

## Economics and thesis

Freeport owns large copper operations in the United States, South America, and Indonesia, with
meaningful gold and molybdenum credits. The SEC-filed Q2 2026 results reported net income attributable
to common shareholders of USD 984 million, or USD 0.68 per share, and adjusted net income of USD 1.1
billion, or USD 0.74 per share. Copper production fell to 786 million pounds from 963 million and
sales to 710 million from 1,016 million, while the realized copper price rose to USD 6.17/lb. Unit
net cash cost was USD 1.97/lb. Operating cash flow was USD 2.048 billion and capex USD 1.104 billion.

The equity provides high copper-price sensitivity, but Q2 earnings were price-led while Grasberg
recovered from the 2025 mud-rush incident. PTFI achieved its planned Q2 ramp rate, but management
expects only about 65% of normal production in the second half of 2026, 80% by mid-2027, and near-full
capacity by the end of 2027. Full-year capex is expected near USD 4.3 billion and net debt was USD
2.1 billion excluding USD 3.2 billion of PTFI downstream debt. Indonesian operating rights,
minority interests, tax, downstream assets, safety, and ramp execution materially shape the
common-share economics.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| Grasberg Block Cave achieved its planned Q2 ramp rate, with 65% of normal production expected in the second half. | Recovery is progressing but remains a multi-quarter execution risk. |
| Copper output and sales fell sharply year over year. | High realized prices masked volume disruption. |
| USD 1.97/lb net cash cost versus USD 6.17/lb realization; costs exclude USD 284 million of Q2 idle-facility and restoration costs. | Strong current margin has meaningful commodity and normalization sensitivity. |
| 2026 capex forecast is USD 4.3 billion, including USD 3.0 billion for major projects. | Growth options require sustained execution and funding. |
| PTFI submitted its IUPK extension application after the February MOU. | Reduces tail risk only when final terms and approvals are secured. |

Primary evidence: [SEC-filed Q2 2026 results exhibit](https://www.sec.gov/Archives/edgar/data/831259/000083125926000033/a2q2026exhibit991.htm),
registered as `source_fcx_q2_2026_results_sec`.

## 2026-07-29 volume review

The deterministic alert is valid. From 2026-06-30 through 2026-07-29, adjusted close fell 4.38%
from USD 62.74 to USD 59.99. July 29 volume was 22.669 million shares, producing a 2.0004 volume
z-score and a newly entered volume-anomaly state. The shares fell 2.68% that session. RSI was
44.82, the close was below the 50-day and 200-day moving averages, and neither RSI nor Bollinger
Bands generated a concurrent trigger. The source-price hash matches the operation payload.

The SEC submissions index showed no filing after the 2026-07-23 Q2 results filing through the
alert's market date. The volume event therefore has no independently verified contemporaneous
company filing as a causal explanation. It may reflect continued post-results repricing, copper
sensitivity, or unrelated trading flow, but the evidence does not distinguish among them. Treat it
as a **risk and monitoring signal**, not a standalone opportunity or trade catalyst.

Filing recency evidence: [SEC company submissions index](https://data.sec.gov/submissions/CIK0000831259.json),
registered as `source_fcx_sec_submissions_20260730`.

## Valuation, catalysts, and risks

The deterministic 2026-07-29 close is USD 59.99. A bounded 12-month downside comparison annualizes
reported Q2 EPS of USD 0.68 and applies 12 times earnings, producing USD 32.64, or 48.0% below the
prior mark and 45.6% below the current mark. A base comparison annualizes adjusted Q2 EPS of USD
0.74 and applies 16 times earnings, producing USD 47.36, or 21.1% below the current mark. These
scenarios are deliberately simple rather than a
precise intrinsic-value claim: they do not capitalize unapproved expansion options and retain a
discount for peak copper pricing, Grasberg normalization, minority interests, and Indonesian terms.

Catalysts are safe Grasberg restoration, Americas leach gains, El Abra progress, final Indonesian
rights, and cash generation after capex. Invalidate if ramp delays recur, unit costs rise, operating
terms worsen, project capex overruns, safety incidents repeat, or copper prices normalize faster
than production recovers.

## Disposition

Status: **watching**, confidence **medium**, and comparable eligibility **baseline**. Reserve life,
current cash generation, balance-sheet capacity, and market liquidity support comparison, but both
bounded values remain below the mark. Review by **2026-08-29**, or sooner for a material Grasberg,
Indonesian-license, cost, capital-allocation, or copper-price change. No conviction strategy is
proposed because valuation and timing fail the full gate. The accepted copper-scarcity relationship
requires a separate sequential idea refresh so this alert disposition can be absorbed without
editing the idea here.

See [[research-catalog|the research catalog]] for the maintained security set and
[[ideas/idea_critical_minerals_copper|the linked copper thesis]] for the causal context.
