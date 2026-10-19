---
title: Samsung Electronics preferred GDR
type: security
status: maintained
tags: [security, research, risk, valuation]
created: "2026-08-06"
updated: "2026-10-19"
provenance: "source_web_7e5bd96010ca77baf3d125f7; source_web_39106ef9cbf4a822cd7b8d5c; source_web_5f5f11357334f115e2cacc71; source_web_f7574415d195f86ff8cb28c4; source_samsung_preferred_gdr_identity; source_web_38c557cf96a6c4117e6fe620; source_web_720ab212d49148d89149f884"
security_id: security_d08d763780400dfbffce
issuer_id: issuer_adf6eb6a528f8576f0ed
confidence: low
last_researched: "2026-10-19T01:56:11.907430Z"
next_review: "2026-11-18"
---

# Samsung Electronics preferred GDR

## Identity and instrument reconciliation

- Immutable security: `security_d08d763780400dfbffce`
- Immutable issuer: `issuer_adf6eb6a528f8576f0ed`
- Maintained provider identity: `SSUN.VI` / `XWBO` / EUR
- Vienna identity: `SSUN`, preferred registered GDR, ISIN `US7960502018`
- Underlying preferred share: KRX `005935`, ISIN `KR7005931001`
- Depositary ratio: one GDR represents 25 non-voting preferred shares

The [Vienna Stock Exchange listing](https://www.wienerborse.at/aktien-global-market/samsung-electro-regs-gdr-pfd-US7960502018/) (`source_web_39106ef9cbf4a822cd7b8d5c`) identifies the maintained security as ticker SSUN and ISIN US7960502018. Samsung's [listing information](https://www.samsung.com/global/ir/stock-information/listing-Info/) (`source_samsung_preferred_gdr_identity`) links that ISIN to its preferred GDR and the Korean preferred share.

The [2025 GDR prospectus](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/Samsung_Final_Prospectus_20250210.pdf) (`source_web_7e5bd96010ca77baf3d125f7`) and [Citi depositary record](https://depositaryreceipts.citi.com/adr/guides/pgm_dispaDivd.aspx?cusip=796050201&pageId=15&subpageID=113) (`source_web_5f5f11357334f115e2cacc71`) independently establish the 25:1 underlying-share-to-GDR ratio. The Vienna line trades in EUR even though the prospectus describes the GDR as USD-denominated.

There is unresolved London-ticker inconsistency. Samsung's listing page says `SMSEL`, while the prospectus and Citi identify `SMSD LI`. The preferred class, ISIN and depositary ratio agree, so the immutable Vienna security and issuer IDs are retained without alteration.

## Business economics

Samsung combines memory semiconductors, foundry and logic products, displays, smartphones and networks, consumer electronics and Harman. Its economics are highly cyclical because memory selling prices, utilization and product mix can move consolidated profit substantially even when the broader franchise remains intact.

Samsung's [Q2 2026 release](https://news.samsungsemiconductor.com/global/samsung-electronics-announces-second-quarter-2026-results/) (`source_web_f7574415d195f86ff8cb28c4`) reported quarterly revenue of KRW 171.5 trillion, operating profit of KRW 89.5 trillion and preferred-share EPS of KRW 10,849. Device Solutions supplied almost all operating profit, supported by AI-server memory, HBM4 and industry-wide price increases. This concentration is both the principal catalyst and the principal normalization risk. Mobile and networks recorded an operating loss, while visual display and appliances were slightly loss-making.

The prospectus provides useful cycle evidence: consolidated profit was KRW 39.9 trillion in 2021, KRW 55.7 trillion in 2022 and KRW 15.5 trillion in 2023; the first nine months of 2024 produced KRW 26.7 trillion. That range argues against treating one exceptional 2026 quarter as a permanent earnings run rate. The prospectus also identifies semiconductor and display cyclicality, selling-price pressure, competition, manufacturing complexity and supplier dependence as material risks.

## Valuation

### Method

A normalized earnings multiple is applied to preferred-share EPS. For each scenario:

`fair value in EUR = normalized preferred EPS in KRW × P/E multiple × 25 underlying shares ÷ KRW per EUR`

The 25:1 conversion is now supported by primary depositary evidence, resolving the prior conversion gap. The [ECB reference-rate sheet for 16 October 2026](https://www.ecb.europa.eu/stats/shared/pdf/eurofxref.pdf?6928fbfb480e2a947b975020269c1b05=) (`source_web_38c557cf96a6c4117e6fe620`) reports KRW 1,499.01 per EUR. Scenario rates bracket that observation rather than assuming currency is fixed.

| Scenario | Probability | Normalized EPS | Multiple | FX assumption | Per-GDR arithmetic | Fair value |
|---|---:|---:|---:|---:|---|---:|
| Bear | 30% | KRW 7,500 | 8× | KRW 1,550/EUR | 7,500 × 8 × 25 ÷ 1,550 | **EUR 970** |
| Base | 50% | KRW 12,000 | 10× | KRW 1,500/EUR | 12,000 × 10 × 25 ÷ 1,500 | **EUR 2,000** |
| Bull | 20% | KRW 18,000 | 12× | KRW 1,450/EUR | 18,000 × 12 × 25 ÷ 1,450 | **EUR 3,720** |

The probabilities total 100%. The base case receives the highest weight because AI-server memory can remain structurally stronger than the last trough while current quarterly profitability still normalizes. The bear case receives more weight than the bull case because the current profit mix is unusually concentrated in memory and non-memory divisions showed weak profitability.

### Interpretation

The Vienna page displayed EUR 2,740 on 16 October 2026, above the EUR 2,000 base value and between the base and bull outcomes. It showed no bid or ask, and the exchange notes that displayed prices can be turnoverless. Consequently, the mark is useful as an observed reference but not as proof of executable value or cross-venue parity.

This valuation is scenario-complete but low confidence. It does not use the Vienna price as fair value, annualize Q2 EPS, or infer preferred value from the common GDR.

## Thesis and contrary evidence

The positive thesis is exposure to Samsung's technology breadth, AI-led server-memory demand, HBM4 product momentum, advanced-node opportunities and financial resilience. Sustained memory scarcity could support normalized EPS materially above prior-cycle levels.

Contrary evidence is substantial. Record Q2 profit depended heavily on memory pricing and mix; several non-memory businesses were loss-making. Semiconductor cycles, foundry execution, export restrictions, customer qualification, capital intensity and won depreciation could all reduce intrinsic EUR value. Depositary fees and a persistent Korea-London-Vienna basis add instrument-specific uncertainty.

## Catalysts

- Sustained HBM4 and server-memory shipments.
- Successful HBM4E customer qualification.
- Continued DRAM and enterprise-SSD supply tightness.
- Advanced-node foundry design wins and improved utilization.
- Recovery in mobile and consumer-device profitability.
- Strong cash conversion and a firmer won.
- Narrower preferred-GDR pricing differences across Korea, London and Vienna.

## Downside and invalidation

Downside would follow a structural reversal in server-memory demand or pricing, HBM qualification losses, delayed advanced-node execution, persistent losses outside memory, weaker cash generation or balance-sheet deterioration. A weaker won reduces translated EUR value.

Rebuild the valuation if the 25:1 ratio changes, if ISIN US7960502018 ceases to represent the maintained Vienna instrument, or if preferred EPS cannot be reconciled with Samsung's capital structure. The base case is invalid if sustainable preferred EPS settles materially below KRW 12,000 or the warranted multiple remains below 10×.

## Evidence limitations

Samsung's [earnings-release index](https://www.samsung.com/global/ir/financial-information/earnings-release/) (`source_web_720ab212d49148d89149f884`) displays a Q3 2026 entry, but its detailed contents were not inspected in this operation. The latest detailed operating evidence actually examined was Q2 2026. Historical evidence supplies consolidated profit but not a complete through-cycle preferred-EPS series. Normalized EPS, multiples and scenario exchange rates are therefore explicit analyst assumptions rather than issuer guidance.

Vienna liquidity remains an additional limitation. Sparse or turnoverless observations can diverge from executable prices, and the model does not separately quantify depositary fees, tax, preferred/common basis or timing differences.

## Changes since prior review

- Verified the missing 25:1 preferred-share-to-GDR conversion through both the prospectus and depositary record.
- Reconciled the Vienna line to ISIN US7960502018 and EUR trading while preserving the immutable security and issuer IDs.
- Identified, rather than silently resolving, the conflicting London ticker references.
- Used historical issuer profit variability and current Q2 preferred EPS to construct normalized bear, base and bull assumptions.
- Replaced `valuation_unsupported` with a low-confidence, scenario-complete EUR valuation of EUR 970 / EUR 2,000 / EUR 3,720.
- Retained explicit liquidity, cross-venue basis, currency and earnings-normalization limitations.

## Sources

- [Samsung preferred GDR prospectus](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/Samsung_Final_Prospectus_20250210.pdf) — `source_web_7e5bd96010ca77baf3d125f7`
- [Vienna preferred GDR listing](https://www.wienerborse.at/aktien-global-market/samsung-electro-regs-gdr-pfd-US7960502018/) — `source_web_39106ef9cbf4a822cd7b8d5c`
- [Citi depositary program](https://depositaryreceipts.citi.com/adr/guides/pgm_dispaDivd.aspx?cusip=796050201&pageId=15&subpageID=113) — `source_web_5f5f11357334f115e2cacc71`
- [Samsung Q2 2026 results](https://news.samsungsemiconductor.com/global/samsung-electronics-announces-second-quarter-2026-results/) — `source_web_f7574415d195f86ff8cb28c4`
- [Samsung listing information](https://www.samsung.com/global/ir/stock-information/listing-Info/) — `source_samsung_preferred_gdr_identity`
- [ECB exchange rates for 16 October 2026](https://www.ecb.europa.eu/stats/shared/pdf/eurofxref.pdf?6928fbfb480e2a947b975020269c1b05=) — `source_web_38c557cf96a6c4117e6fe620`
- [Samsung earnings-release index](https://www.samsung.com/global/ir/financial-information/earnings-release/) — `source_web_720ab212d49148d89149f884`
