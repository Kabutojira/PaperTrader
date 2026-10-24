---
title: Albemarle Corporation common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-10-24"
provenance: "source_web_93948c839bd197a2a41eb35e; supplied reconciled ALB market observation"
security_id: security_66cdcf90aac0d83e76f3
issuer_id: issuer_76c4dda166e8f840fb77
confidence: medium
next_review: "2026-11-23"
---

# Albemarle Corporation common stock

## Identity

- **Security ID:** `security_66cdcf90aac0d83e76f3`
- **Issuer ID:** `issuer_76c4dda166e8f840fb77`
- **Instrument:** Albemarle Corporation common stock
- **Symbol and venue:** `ALB` on the New York Stock Exchange (`XNYS`)
- **Native currency:** USD

The supplied identity is internally consistent with the issuer's description of Albemarle Corporation as NYSE-listed under ALB. No identity fields were changed.

## Changes since the prior review

- The normalized bear, base and bull fair values remain **USD 9.93, USD 131.25 and USD 231.62** because the accessible issuer evidence still supports the underlying 2026 price-case framework.
- The valuation reference is updated to the supplied **USD 93.66000366210938 adjusted close for 2026-10-23**, the latest completed XNYS session as of the assessment time.
- Probability-weighted fair value remains **USD 126.0125**, now approximately **34.5% above** the reference price.
- Rubric-v1 scores are now populated: valuation 84.5, business quality 65, thesis 65, balance sheet 80 and risk penalty 70.
- Confidence remains medium. The wider discount does not remove lithium-cycle risk or the uncertainty created by non-recurring cash-flow benefits.

## Current operating evidence

Albemarle's [second-quarter 2026 results release](https://investors.albemarle.com/news-and-events/news/news-details/2026/Albemarle-Reports-Second-Quarter-2026-Results/default.aspx) (`source_web_93948c839bd197a2a41eb35e`) reported USD 1.743 billion of net sales and USD 858.1 million of adjusted EBITDA. Energy Storage generated USD 1.277 billion of sales and USD 723.5 million of adjusted EBITDA, with 65 kt LCE sales volume and an average realized price of USD 19.53/kg LCE. Specialties reported USD 423.5 million of sales and USD 117.7 million of adjusted EBITDA.

The release also reported USD 1.1 billion of first-half operating cash flow and USD 170 million of capital spending. Cash conversion should not be extrapolated mechanically: management attributed part of it to dividend timing and non-recurring working-capital benefits.

For full-year 2026, the issuer framed adjusted EBITDA around approximately USD 0.9-1.0 billion, USD 2.4-2.6 billion and USD 4.2-4.4 billion at observed lithium-price cases near USD 10, USD 20 and USD 30/kg LCE. It expected Energy Storage sales volume of 225-235 kt, approximately USD 500 million of capital spending, USD 660-680 million of depreciation and amortization, USD 120-140 million of interest expense and approximately 136 million diluted shares.

## Business economics

Albemarle combines highly cyclical lithium exposure with a smaller Specialties franchise. Lithium pricing has strong operating leverage: higher realized pricing drove most of the Q2 Energy Storage EBITDA improvement. This creates substantial upside in a tight market but exposes normalized earnings to new supply, contract-price lags and abrupt price reversals.

Specialties provides some diversification through bromine and derivative markets, but it does not eliminate lithium concentration. Productivity improvements and lower planned capital spending strengthen conversion from earnings to cash, subject to working-capital normalization and project execution.

## Balance sheet

At June 30, 2026, management reported approximately USD 3.2 billion of liquidity, comprising USD 1.6 billion of cash, USD 1.5 billion available under its revolver and USD 78 million under other credit lines. Total debt was USD 1.9 billion, and management calculated net debt to adjusted EBITDA at approximately 0.5 times under the credit-agreement definition.

This supports a resilient-liquidity assessment. The ratio nevertheless uses a non-GAAP, cycle-sensitive earnings denominator, so it should not be interpreted as proof that commodity downside is immaterial.

## Valuation

**Method:** 12-month normalized earnings in USD per common share.

| Scenario | Probability | Fair value | Arithmetic and principal assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 9.93 | `(0.95bn EBITDA − 0.67bn D&A − 0.13bn interest) × 75% ÷ 136m shares × 12``; lithium near USD 10/kg LCE and prolonged trough pressure. |
| Base | 50% | USD 131.25 | `(2.50bn − 0.67bn − 0.13bn) × 75% ÷ 136m × 14`; lithium near USD 20/kg LCE with guided volume and controlled costs. |
| Bull | 25% | USD 231.62 | `(4.30bn − 0.67bn − 0.13bn) × 75% ÷ 136m × 12`; lithium near USD 30/kg LCE, successful execution and a cycle-discounted multiple. |

Probability-weighted value is:

`25% × 9.93 + 50% × 131.25 + 25% × 231.62 = USD 126.0125 per share`.

The supplied market observation identifies USD 93.66000366210938 as ALB's adjusted close for the completed 2026-10-23 XNYS session. It matches the common-share identity, native USD currency and per-share quote units; no currency or quote-unit conversion is needed. The deterministic valuation formula therefore produces **84.5**.

## Fundamental rubric v1

| Factor | Score | Interpretation |
| --- | ---: | --- |
| Valuation | 84.5 | Weighted fair value is materially above the verified supplied reference price, with very wide scenario dispersion. |
| Business quality | 65 | Scale, resource position, Specialties diversification and productivity support above-mixed economics, but commodity dependence limits durability. |
| Thesis | 65 | Current operating evidence corroborates recovery, while price-case dispersion and non-recurring cash benefits remain material contrary evidence. |
| Balance sheet | 80 | Liquidity is resilient relative to reported debt, although credit metrics depend on cycle-sensitive adjusted EBITDA. |
| Risk penalty | 70 | Lithium cyclicality, concentration, contract lags, operational disruption, geopolitics and evidence limitations create material-to-high residual risk. |

There is no aggregate score. Balance-sheet risk is assessed in its own factor and is not deducted again through the risk penalty.

## Downside and contrary evidence

The bear value is extremely low because depreciation, interest and fixed costs absorb most EBITDA in the low-price case. Supply restarts, weaker demand or delayed contract repricing could push results toward that outcome. Talison CGP3 disruption, inadequate Wodgina offsets, higher CORFO commissions, geopolitical effects on Jordan Bromine, tax volatility, capital overruns and mandatory-convertible dilution are additional downside mechanisms.

A material portion of first-half operating cash flow benefited from timing and non-recurring working capital. Adjusted EBITDA should therefore not be treated as recurring free cash flow.

## Catalysts

- Lithium realization sustained near or above the base case.
- Delivery of 225-235 kt Energy Storage volume.
- Wodgina production substantially offsetting the Talison CGP3 delay.
- Continued Specialties pricing, volume and productivity gains.
- Capital spending held near USD 500 million.
- Recurring cash generation after working-capital benefits normalize.

## Invalidation conditions

Reassess the valuation if lithium realization remains near the low case, Energy Storage volume materially misses guidance, Talison disruption broadens, Wodgina underperforms, Specialties profitability reverses, recurring cash conversion materially trails normalized earnings, capital intensity rises, taxes change materially or diluted shares exceed the 136 million assumption. Any newer quarterly filing that changes guidance or financing also invalidates the present normalization.

## Idea relationship

The security remains a positive but cyclical beneficiary of [[ideas/idea_critical_minerals_lithium]]. Higher lithium prices can raise Energy Storage revenue and margins, but shareholder value also depends on volume, contract timing, costs, taxes, capital spending and dilution.

## Confidence and limitations

**Confidence: medium.** The issuer release provides detailed operating, outlook and liquidity evidence, but the supplied SEC filing URLs returned HTTP errors through the research broker and were not used as currently opened assessment evidence. Forward adjusted EBITDA is non-GAAP and unreconciled. Multiples, normalized tax and scenario probabilities are analytical assumptions. The reference price is a supplied adjusted close, not an intraday or executable quotation.

## Source

- [Albemarle Reports Second Quarter 2026 Results](https://investors.albemarle.com/news-and-events/news/news-details/2026/Albemarle-Reports-Second-Quarter-2026-Results/default.aspx) — `source_web_93948c839bd197a2a41eb35e`
