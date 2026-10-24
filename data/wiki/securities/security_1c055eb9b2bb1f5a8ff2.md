---
title: Rio Tinto plc sponsored ADR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-10-24"
provenance: "source_web_69a8fabc905a838185a70d71"
security_id: security_1c055eb9b2bb1f5a8ff2
issuer_id: issuer_3f384e36fe805b0fcbea
confidence: medium
next_review: "2026-11-23"
---

# Rio Tinto plc sponsored ADR

## Identity and scope

- Immutable security: `security_1c055eb9b2bb1f5a8ff2`
- Immutable issuer: `issuer_3f384e36fe805b0fcbea`
- Instrument: Rio Tinto plc sponsored ADR
- Market identity: `RIO` / New York Stock Exchange (`XNYS`) / USD / equity

The supplied identity, provider symbol, venue and currency are retained unchanged. No opened issuer evidence contradicted them. The depositary ratio could not be independently verified from an accessible primary source, so the valuation explicitly assumes one RIO ADR has the economic exposure of one Rio Tinto plc ordinary share. A different ratio would invalidate the per-ADR arithmetic.

## Investment thesis

Rio Tinto combines large iron-ore and aluminium cash engines with growing copper exposure. Its long-life assets and portfolio breadth provide some diversification, but earnings remain highly sensitive to commodity prices, Chinese steel demand, energy, currencies, taxes, minority interests and major-project spending.

The [2026 half-year results](https://cdn-rio.dataweavers.io/-/media/content/documents/invest/financial-news-and-performance/results/2026/2026-half-year-results.pdf) (`source_rio_h1_2026_results`) reported:

- Revenue of USD 31.028 billion.
- Underlying EBITDA of USD 14.826 billion.
- Operating cash flow of USD 9.173 billion.
- Free cash flow of USD 3.834 billion.
- Profit attributable to Rio Tinto owners of USD 6.664 billion.
- Underlying ROCE of 17%.
- Net debt of USD 14.061 billion at 30 June 2026.

Copper generated USD 5.7 billion of H1 EBITDA, iron ore USD 6.8 billion, and aluminium and lithium USD 3.3 billion. Operating progress was real: volumes and mix contributed USD 1.2 billion to the year-over-year EBITDA change, while cash-unit-cost improvements contributed USD 0.3 billion. However, stronger prices supplied USD 3.6 billion of the increase, making unadjusted H1 cash generation unsuitable as a mid-cycle run rate.

## Current operating evidence and contrary evidence

The [Third Quarter Operations Review 2026](https://cdn-rio.dataweavers.io/-/media/content/documents/invest/financial-news-and-performance/production/2026/2026-third-qor.pdf?rev=aa4f740bedfc41c6a18b24783c421fc5) (`source_web_69a8fabc905a838185a70d71`) was operationally constructive but not uniformly positive.

| Evidence | Assessment |
| --- | --- |
| Oyu Tolgoi production increased 27% year over year in Q3 and 29% year to date; the operation ran at an approximately 450 kt annualized rate. | Supports the copper-growth thesis. |
| Consolidated copper production was 646 kt through Q3, only 1% above the prior year. | Growth at Oyu Tolgoi was partly offset elsewhere. |
| Group copper-equivalent production increased approximately 1% year to date. | Portfolio growth slowed from the 3% reported at H1. |
| Global iron-ore sales increased 3% year over year in Q3; Simandou reached an approximately 10 Mtpa annualized run rate. | Supports project execution, although Simandou remains early in its ramp. |
| Production, sales and unit-cost guidance remained unchanged. | No broad operational downgrade was disclosed. |
| Lithium production rose 33% year to date, but full-year output was expected near the lower end of guidance. | Growth remains exposed to weather and ramp risk. |
| Higher diesel prices and the stronger Australian dollar pressured Pilbara costs. | Commodity-price gains do not translate one-for-one into cash flow. |
| Copper averaged USD 6.40/lb in Q3, while iron ore averaged about USD 97/dmt. | Current conditions are too favourable to use without normalization. |
| Chinese finished-steel consumption declined by an issuer-estimated 4% quarter over quarter and 2% year over year. | Material contrary evidence for iron-ore demand. |

The relationship to [[ideas/idea_critical_minerals_copper]] remains positive with medium confidence. Oyu Tolgoi gives Rio Tinto direct exposure to constrained copper supply, but the effect on ADR value is diluted by the rest of the portfolio, capital requirements, taxes and non-controlling interests.

## Valuation

A `mid_cycle_cash_flow` method is used because mining cash flow varies sharply with prices, currencies and investment cycles. H1 free cash flow cannot simply be annualized when prices accounted for most of the EBITDA increase and Rio Tinto-share capital investment was USD 5.037 billion.

The scenarios apply equity cash-flow multiples directly to normalized free cash flow per ADR. The multiples incorporate cyclicality and net debt rather than adding a separately estimated enterprise value.

| Scenario | Weight | Normalized FCF per ADR | Multiple | Fair value | Main assumptions |
| --- | ---: | ---: | ---: | ---: | --- |
| Bear | 25% | USD 3.40 | 20x | **USD 68.00** | Commodity normalization, weaker Chinese steel demand, persistent diesel and FX pressure, slower project cash conversion and limited debt reduction. |
| Base | 50% | USD 4.25 | 22x | **USD 93.50** | Continued Oyu Tolgoi and Simandou execution, partial productivity delivery and normalization from unusually strong commodity prices. |
| Bull | 25% | USD 5.50 | 23x | **USD 126.50** | Sustained copper and aluminium strength, successful project execution, productivity delivery, capital-release receipts and declining net debt. |

The scenarios are ordered and their weights total 100%. These are valuation weights, not probabilities of investment profit. Their probability-weighted fair value is **USD 95.375 per ADR**.

### Reference price and valuation score

The supplied market observation reports a USD 83.4000015258789 closing price for `RIO` on XNYS on 23 October 2026, the latest completed exchange session before this assessment. It is attached to this exact security ID and matches the supplied provider symbol, venue and USD currency, so it is treated as a USD-per-ADR quotation with no currency or quote-unit conversion. The observation was not independently reopened as a web source.

Using the required formula:

`50 + 100 × (95.375 / 83.4000015258789 − 1) = 64.4`, rounded to one decimal.

The resulting **valuation score is 64.4**.

## Fundamental scores — rubric version 1

| Factor | Score | Rationale |
| --- | ---: | --- |
| Valuation | **64.4** | The weighted fair value is above the supplied current ADR price, but the result depends on normalized cash-flow assumptions and the unverified ADR ratio. |
| Business quality | **72** | Long-life, diversified assets, 17% underlying ROCE and 62% EBITDA cash conversion approach the durable-advantages anchor. Commodity dependence, concentration and capital intensity keep the score below 75. Price and leverage are excluded. |
| Thesis | **70** | Oyu Tolgoi, Simandou and productivity evidence support the thesis, while slow consolidated copper growth, weaker Chinese steel demand and the price-driven EBITDA uplift are material counterweights. This score measures corroboration, not upside. |
| Balance sheet | **68** | Net debt declined to USD 14.061 billion and cash generation remained strong, but dividends, major capital programs and USD 18.9 billion of closure provisions prevent a full resilient-liquidity score. |
| Risk penalty | **68** | Commodity cyclicality, Chinese demand, simultaneous project execution, energy and FX pressure, tax disagreement, closure exposure, minority-interest leakage and ADR-ratio uncertainty create material-to-high residual risk. Financing leverage is not deducted again here. |

There is no aggregate score and no additional confidence multiplier.

## Downside

The central downside is a combined commodity and execution reversal. Falling copper, gold or aluminium prices, lower iron-ore netbacks, weaker Chinese demand, higher energy or freight costs, adverse currencies, tax or partner disputes and project delays could reduce shareholder cash conversion. Oyu Tolgoi, Simandou, Pilbara replacement mines and lithium developments all require continued execution while closure spending remains significant.

## Catalysts

- Oyu Tolgoi sustaining or exceeding its Q3 annualized rate.
- Simandou advancing from approximately 10 Mtpa toward its stated 2028 target.
- Continued Pilbara reliability and successful replacement-mine execution.
- Productivity benefits reaching the targeted USD 1.8 billion annualized run rate.
- Announced capital-release initiatives converting into cash.
- Future financial results showing higher attributable free cash flow and lower net debt rather than only stronger commodity prices.

## Invalidation conditions

Reassess the base thesis if Oyu Tolgoi fails to sustain its ramp, Simandou or Pilbara projects move materially behind schedule or over budget, consolidated copper production stops growing, productivity cannot offset inflation and energy costs, net debt rises materially without matching durable cash generation, or normalized free cash flow falls below USD 3.40 per ADR. The valuation is also invalid if the assumed one-ADR-to-one-ordinary-share economic mapping is wrong.

## Confidence and limitations

Confidence is **medium**. The H1 release provides current primary financial evidence, and the Q3 review provides current operational evidence. However, no post-H1 income statement, cash-flow statement, balance sheet or share count was available in the opened sources. Free cash flow, underlying EBITDA and net debt are issuer-defined non-IFRS measures. Commodity normalization, currencies, taxes, minority interests, project spending and closure costs remain uncertain. The scenario multiples are analytical assumptions, the ADR ratio remains unverified, and the supplied market quotation was not independently reopened.

Assessment date: **2026-10-24**. Review no later than **2026-11-23**, or sooner following material financial results, project changes or verified changes to the ADR terms.

## Changes in this review

- Reopened and rechecked the H1 2026 financial results and Q3 2026 operations review.
- Retained the USD 68.00/USD 93.50/USD 126.50 scenarios because Q3 supplied operating data but no replacement financial statements supporting different normalized cash flow.
- Completed scoring-rubric version 1 for valuation, business quality, thesis support, balance-sheet resilience and residual risk.
- Added the supplied 23 October 2026 ADR close as the valuation reference and calculated a 64.4 valuation score.
- Kept the ADR ratio as an explicit assumption, limitation and invalidation condition.
- Refreshed the relationship to the structural-copper-scarcity idea without changing its direction or confidence.

## Opened sources

- [Rio Tinto 2026 half-year results](https://cdn-rio.dataweavers.io/-/media/content/documents/invest/financial-news-and-performance/results/2026/2026-half-year-results.pdf) — `source_rio_h1_2026_results`
- [Rio Tinto Third Quarter Operations Review 2026](https://cdn-rio.dataweavers.io/-/media/content/documents/invest/financial-news-and-performance/production/2026/2026-third-qor.pdf?rev=aa4f740bedfc41c6a18b24783c421fc5) — `source_web_69a8fabc905a838185a70d71`
