---
title: Freeport-McMoRan Inc. common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-06"
provenance: "source_fcx_q2_2026_results_sec|source_fcx_sec_submissions_20260806|deterministic market cache"
security_id: security_2dbe878dfc899d7ee867
issuer_id: issuer_5076f0e0e1dd7cc8bca7
confidence: medium
next_review: "2026-08-20"
---

# Freeport-McMoRan Inc. common stock

## Identity

- Immutable security: `security_2dbe878dfc899d7ee867`
- Issuer: `issuer_5076f0e0e1dd7cc8bca7`
- Instrument: common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `FCX` / `XNYS` / `USD` / equity

This review links the verified instrument to [[ideas/idea_critical_minerals_copper]].

## Decision

**Sell / Avoid at USD 69.39; no full review or strategy.** FCX advanced 20.97% over the July
8-August 5 alert period and strengthened above its upper Bollinger band. The SEC submissions index
contains only insider Forms 4 and planned-sale notices after the July 23 results filing, so no new
operating disclosure explains or validates the rerating. The same Q2 production, Grasberg recovery,
Indonesian-rights and copper-price assumptions remain current.

The required v2 cyclical valuation makes the unchanged economic conclusion explicit. USD
32.64/USD 47.36/USD 65.12 bear/base/bull cases produce a USD 46.496 probability-weighted value,
well below the current mark; even the bull case remains below market. The accepted structural-copper
relationship remains current, but valuation, payoff asymmetry and timing fail. The move is a
valuation and timing risk, not a new entry condition.

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

## August 4-5 above-band quick check

The merged alerts are valid. FCX closed at **USD 67.30** on August 4, entering above its upper
Bollinger band, then strengthened to **USD 69.39** on August 5. The latest 20-session return is
**20.97%**, five-session return **15.67%**, RSI **64.30**, and MACD histogram **0.8724**. The close
is 2.56% above the USD 67.657 upper band. Volume was 17.110 million shares with a 0.713 z-score, so
the current transition is price extension rather than another volume anomaly.

The alert packets retain hashes
`20148936c2398c913c238be6bb07fdac8e83aed2ef01fe580354124fb4f64ea8` and
`2a73bd71f08cdb23c9499ec33cd9b2f0304a12790e8d69154772efff69db482b`. The refreshed indicator
calculation preserves the same August 5 mark and trigger under current price-cache hash
`c4f5743cea60e8fb668f35caab456950cf99899720b0cb6c053e08962c62af57`.

The August 6 SEC submissions index contains Forms 4 dated August 3 and 5 and Forms 144 dated July
30 and August 5, but no issuer operating filing after the July 23 Q2 results. Those ownership and
sale notices do not change production, valuation, catalysts or invalidation. The above-band move is
therefore **valuation/timing risk and an unconfirmed rerating**, not a standalone opportunity.

Filing recency evidence: [SEC company submissions index](https://data.sec.gov/submissions/CIK0000831259.json),
registered as `source_fcx_sec_submissions_20260806`.

## Valuation, catalysts, and risks

The selected repository template is `cyclical_commodity` with a `normalized_earnings` method. The
bounded 12-month cases use only the SEC-filed Q2 earnings base and explicitly vary the multiple for
copper, recovery and jurisdictional risk:

- **Bear — USD 32.64, 30%:** annualized USD 0.68 reported Q2 EPS at 12x as copper normalizes,
  Grasberg restoration slows and idle/restoration costs persist.
- **Base — USD 47.36, 50%:** annualized USD 0.74 adjusted Q2 EPS at 16x as the stated Grasberg ramp
  proceeds but production remains below normal and Indonesian/minority economics retain a discount.
- **Bull — USD 65.12, 20%:** annualized USD 0.74 adjusted Q2 EPS at 22x as copper pricing stays
  elevated, recovery executes safely, costs remain controlled and Indonesian rights advance.

The weighted value is **USD 46.496**, implying a **33.0% expected loss** from USD 69.39. The base
case implies **31.7% downside** and the bear case **53.0% downside**; even the bull case is about
6.2% below the mark. These are deliberately bounded comparisons rather than a precise intrinsic-
value claim. They do not capitalize unapproved expansion options and retain normalization,
minority-interest, net-debt and jurisdictional risk.

Catalysts are safe Grasberg restoration, Americas leach gains, El Abra progress, final Indonesian
rights, and cash generation after capex. Invalidate if ramp delays recur, unit costs rise, operating
terms worsen, project capex overruns, safety incidents repeat, or copper prices normalize faster
than production recovers.

## Disposition

Status: **watching**, confidence **medium**, canonical rating **Sell**, and portfolio action
**Avoid**. Reserve life, current cash generation, balance-sheet capacity and market liquidity
support comparison, but all weighted, base and bear economic gates fail despite the accepted
copper-scarcity relationship. Review by **2026-08-20**, or sooner for a material Grasberg,
Indonesian-license, cost, capital-allocation or copper-price change. No full security review,
strategy or signal is justified because no primary operating assumption changed and valuation and
timing deteriorated.

## Changes since prior review

- **Evidence:** the Q2 exhibit is byte-for-byte unchanged. The refreshed SEC index adds only Forms
  4 and 144 after July 23, not an operating filing or catalyst.
- **Market state:** the prior USD 59.99 volume-risk mark rose to USD 69.39; the 20-session return is
  now 20.97% and the upper-band transition strengthened. This increases valuation/timing risk.
- **Valuation:** the legacy USD 32.64 downside and USD 47.36 base comparisons are preserved as v2
  bear/base cases. A bounded USD 65.12 bull case and 30%/50%/20% probabilities complete the
  required cyclical scenario set. All three cases remain below market.
- **Thesis and contrary evidence:** structural copper sensitivity, reserve optionality and recovery
  progress remain; disrupted Grasberg volumes, normalization, Indonesian terms and minority/capex
  economics remain contrary evidence. No thesis gate changed.
- **Catalysts, risks, blockers and gaps:** all catalysts and invalidations remain. No hard blocker is
  needed because valuation is supported, but confidence, concentration, cyclicality, margin of
  safety, timing and valuation gaps remain exact.
- **Rating and action:** the legacy non-actionable baseline is normalized to explicit Sell / Avoid,
  complete but allocation-ineligible. This makes the same economic conclusion machine-readable.
- **Escalation:** no full review is warranted because no valuation assumption, catalyst,
  invalidation or material primary evidence changed. The existing accepted idea relationship remains
  current, and this quick check does not edit or requeue the idea.

See [[research-catalog|the research catalog]] for the maintained security set and
[[ideas/idea_critical_minerals_copper|the linked copper thesis]] for the causal context.
