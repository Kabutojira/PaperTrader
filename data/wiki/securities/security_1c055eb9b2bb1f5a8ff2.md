---
title: Rio Tinto plc sponsored ADR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-10-19"
provenance: "source_web_69a8fabc905a838185a70d71"
security_id: security_1c055eb9b2bb1f5a8ff2
issuer_id: issuer_3f384e36fe805b0fcbea
confidence: medium
next_review: "2026-11-18"
---

# Rio Tinto plc sponsored ADR

## Identity and scope

- Immutable security: `security_1c055eb9b2bb1f5a8ff2`
- Immutable issuer: `issuer_3f384e36fe805b0fcbea`
- Supplied instrument: Rio Tinto plc sponsored ADR
- Supplied market identity: `RIO` / New York Stock Exchange (`XNYS`) / USD / equity

No opened issuer evidence contradicted the supplied issuer, share class, MIC, symbol or currency, so the identifiers are retained unchanged. This review did not independently verify the depositary ratio. The valuation therefore explicitly assumes that one RIO ADR carries the economic exposure of one Rio Tinto plc ordinary share; a different ratio would invalidate the per-ADR arithmetic.

## Business economics and thesis

Rio Tinto is a diversified miner rather than a pure copper producer. Its principal cash engines include Pilbara iron ore, aluminium and copper, with lithium becoming a larger but still developing exposure. This diversification can cushion a single-commodity downturn, but it also means the ADR is materially exposed to Chinese steel demand, iron-ore netbacks, energy, exchange rates and large project spending.

The [2026 half-year results](https://cdn-rio.dataweavers.io/-/media/content/documents/invest/financial-news-and-performance/results/2026/2026-half-year-results.pdf) (`source_rio_h1_2026_results`) reported revenue of USD 31.028 billion, underlying EBITDA of USD 14.826 billion, operating cash flow of USD 9.173 billion and free cash flow of USD 3.834 billion. Copper EBITDA rose to USD 5.7 billion, while iron ore contributed USD 6.8 billion. Net debt was USD 14.061 billion at 30 June.

The quality of that improvement must not be overstated. Rio Tinto attributed USD 3.6 billion of the H1 year-over-year EBITDA uplift to stronger commodity prices, compared with USD 1.2 billion from volume and mix and USD 0.3 billion from operating cash-unit-cost improvement. The result therefore contains both genuine operating progress and a substantial cyclical price benefit.

## Latest operating evidence

The [Third Quarter Operations Review 2026](https://cdn-rio.dataweavers.io/-/media/content/documents/invest/financial-news-and-performance/production/2026/2026-third-qor.pdf?rev=aa4f740bedfc41c6a18b24783c421fc5) (`source_web_69a8fabc905a838185a70d71`) provides mixed but broadly supportive evidence:

| Q3 evidence | Interpretation |
| --- | --- |
| Oyu Tolgoi production rose 27% year over year in Q3 and 29% year to date; the operation ran at an approximately 450 kt annualized rate in the quarter. | The principal copper-growth mechanism continues to operate. |
| Consolidated copper production was 646 kt for nine months, only 1% above the prior year. | Oyu Tolgoi growth is being offset elsewhere, so group copper leverage is weaker than the headline asset growth. |
| Group copper-equivalent production grew approximately 1% year to date, down from 3% in H1. | Portfolio growth moderated during Q3. |
| Global iron-ore sales rose 3% year over year in Q3; Simandou reached an approximately 10 Mtpa annualized production rate. | Iron-ore execution remains constructive, although the project is still early in its ramp. |
| Production and sales guidance and unit-cost guidance were maintained. | No broad operational downgrade was disclosed. |
| Lithium production was up 33% year to date, but full-year output was expected at the lower end of guidance. | Growth continues, with weather and ramp risk still evident. |
| Higher diesel prices and a stronger Australian dollar were identified as Pilbara cost pressures. | Favourable metals prices do not translate one-for-one into cash flow. |
| Copper averaged USD 6.40/lb in Q3, while iron ore averaged about USD 97/dmt. | Current earnings conditions are strong but unsuitable as an unadjusted mid-cycle base. |

The relationship to [[ideas/idea_critical_minerals_copper]] remains positive but medium-confidence. Oyu Tolgoi supplies direct copper-growth exposure, while iron ore, aluminium, lithium, taxes, minority interests, capital spending and leverage dilute transmission from copper prices to ADR value.

## Valuation method

A `mid_cycle_cash_flow` method is used because spot-period mining earnings are highly cyclical. H1 free cash flow of USD 3.834 billion cannot simply be annualized as a durable run rate when prices accounted for most of the EBITDA improvement and capital requirements remain substantial.

The scenario calculation applies equity cash-flow multiples directly to normalized free cash flow per ADR. The multiples are intended to incorporate net debt and cyclicality rather than adding a separate enterprise-value estimate:

| Scenario | Probability | Normalized FCF per ADR | Multiple | Fair value | Principal drivers |
| --- | ---: | ---: | ---: | ---: | --- |
| Bear | 25% | USD 3.40 | 20x | **USD 68.00** | Commodity normalization, weaker Chinese steel demand, persistent diesel and FX pressure, slower project cash conversion and limited debt reduction. |
| Base | 50% | USD 4.25 | 22x | **USD 93.50** | Continued Oyu Tolgoi and Simandou execution, partial productivity delivery and normalization from unusually strong H1/Q3 prices. |
| Bull | 25% | USD 5.50 | 23x | **USD 126.50** | Sustained copper and aluminium strength, higher attributable volumes, successful productivity delivery, capital-release cash receipts and declining net debt. |

The values are arithmetically ordered and the probabilities total 100%. The probability-weighted value is USD 95.375 per ADR. The fair-value range is retained from the prior review because the Q3 publication contains operational data but no updated cash-flow statement, balance sheet or share count that would support a new normalized cash-flow estimate.

## Downside, catalysts and invalidation

### Downside

The central downside is a combined commodity and execution reversal. Copper, gold and aluminium prices materially benefited H1, while weaker Chinese domestic steel consumption, high freight and energy costs, foreign exchange, taxes, minority interests and sustained project capital can reduce shareholder cash conversion. Oyu Tolgoi, Simandou, Pilbara replacement mines and lithium developments also create schedule and cost risk.

### Catalysts

- Oyu Tolgoi sustaining or exceeding its Q3 annualized production rate.
- Simandou advancing from its approximately 10 Mtpa run rate toward the stated 2028 target.
- Productivity benefits reaching the targeted USD 1.8 billion annualized run rate.
- Announced capital-release initiatives converting into cash.
- The next financial results showing higher attributable free cash flow and lower net debt rather than only stronger commodity prices.

### Invalidation conditions

The base thesis must be reassessed if Oyu Tolgoi fails to sustain its ramp, Simandou or Pilbara projects move materially behind schedule or over budget, consolidated copper output stops growing, productivity does not offset inflation and energy costs, net debt rises materially without matching durable cash generation, or normalized free cash flow falls below USD 3.40 per ADR. The per-ADR valuation is also invalid if the assumed one-ADR-to-one-ordinary-share economic mapping is incorrect.

## Confidence and limitations

Confidence is **medium**. H1 provides current primary financial evidence and Q3 supplies current operating evidence, but no post-H1 income statement, cash-flow statement or balance sheet was available. Free cash flow is an issuer-defined non-IFRS measure. Commodity normalization, taxes, foreign exchange, non-controlling interests and project capital are uncertain, while scenario multiples are analytical assumptions rather than reported facts. The ADR depositary ratio also remains an explicit identity limitation.

Assessment date: **2026-10-19**. Review no later than **2026-11-18**, or earlier after material financial results, project changes or a verified change in the ADR terms.

## Changes since the prior review

- Added the 14 October Q3 operations evidence.
- Confirmed continued Oyu Tolgoi and Simandou progress while recognizing slower group copper-equivalent growth and only 1% year-to-date consolidated copper growth.
- Added diesel, foreign-exchange and lower-end lithium guidance as contrary evidence.
- Filled the missing invalidation conditions, resolving the stated valuation-coverage gap.
- Retained the USD 68.00/USD 93.50/USD 126.50 valuation because Q3 did not provide new financial statements sufficient to revise normalized cash flow.
- Made the unverified ADR ratio an explicit assumption and invalidation condition rather than silently changing the immutable identity.

## Opened primary sources

- [Rio Tinto 2026 half-year results](https://cdn-rio.dataweavers.io/-/media/content/documents/invest/financial-news-and-performance/results/2026/2026-half-year-results.pdf) — `source_rio_h1_2026_results`
- [Rio Tinto second-quarter 2026 production results](https://www.riotinto.com/en/news/releases/2026/rio-tinto-releases-second-quarter-2026-production-results) — `source_rio_q2_2026_production`
- [Rio Tinto 2025 full-year results](https://www.riotinto.com/en/news/releases/2026/rio-tinto-solid-results-underpinned-by-8-cueq-production-and-sharper-cost-discipline) — `source_rio_fy2025_results`
- [Rio Tinto production-results index](https://www.riotinto.com/en/invest/financial-news-performance/production) — `source_web_6642284f75adfd58bb38316b`
- [Rio Tinto Third Quarter Operations Review 2026](https://cdn-rio.dataweavers.io/-/media/content/documents/invest/financial-news-and-performance/production/2026/2026-third-qor.pdf?rev=aa4f740bedfc41c6a18b24783c421fc5) — `source_web_69a8fabc905a838185a70d71`
