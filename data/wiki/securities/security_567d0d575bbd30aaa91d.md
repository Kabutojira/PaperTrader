---
title: Samsung Electronics common GDR
type: security
status: maintained
tags: [security, research, valuation, risk]
created: "2026-07-29"
updated: "2026-10-19"
provenance: "source_web_2891ff45d9f9bfece13125e8; source_web_506a5622765fb567404e6b71; source_web_f7574415d195f86ff8cb28c4; source_samsung_common_gdr_identity; source_web_38c557cf96a6c4117e6fe620"
security_id: security_567d0d575bbd30aaa91d
issuer_id: issuer_adf6eb6a528f8576f0ed
confidence: low
next_review: "2026-11-18"
---

# Samsung Electronics common GDR

## Research conclusion

New depositary and exchange evidence resolves the prior valuation blockers. The specified instrument can now be reconciled to Samsung's common GDR, and a 12-month scenario valuation in EUR is supportable. The resulting values are **EUR 2,401.59 bear**, **EUR 5,003.30 base**, and **EUR 7,961.19 bull** per GDR, with respective probabilities of 30%, 50%, and 20%.

Confidence remains **low** because the normalized earnings assumptions rely heavily on one exceptional, supply-constrained memory quarter rather than a complete through-cycle financial record.

## Identity reconciliation

- Immutable security: `security_567d0d575bbd30aaa91d`
- Immutable issuer: `issuer_adf6eb6a528f8576f0ed`
- Supplied identity: Samsung Electronics common GDR, provider symbol `SSU.VI`, MIC `XWBO`, EUR
- Verified common-GDR ISIN: `US7960508882`
- Vienna exchange symbol: `SSU`
- London exchange symbol: `SMSN`
- Depositary entitlement: 25 ordinary shares per GDR

[Samsung's listing page](https://www.samsung.com/global/ir/stock-information/listing-Info/) (`source_samsung_common_gdr_identity`) identifies the London common GDR as `SMSN`, ISIN `US7960508882`, and the underlying Korean common share as `005930`, ISIN `KR7005930003`. It also reports 5,846,278,608 common shares outstanding at June 30, 2026.

[Citi's active depositary-program page](https://depositaryreceipts.citi.com/adr/guides/pgm_dispaDivd.aspx?Type=D&cusip=796050888&pageId=15&subpageID=113) (`source_web_2891ff45d9f9bfece13125e8`) independently identifies Samsung common GDR CUSIP `796050888`, US ISIN `US7960508882`, London ticker `SMSN`, and an ordinary-share-to-DR ratio of **25:1**.

The [Vienna Stock Exchange page](https://www.wienerborse.at/en/stock-global-market/samsung-electr-gdr-US7960508882/) (`source_web_506a5622765fb567404e6b71`) identifies the traded security as Samsung Electronics GDR, ISIN `US7960508882`, under symbol `SSU`. The ISIN connects the Vienna security to the same common GDR documented by Samsung and Citi. The exchange displays symbol `SSU`, not the provider-form symbol `SSU.VI`; the `.VI` suffix and supplied MIC `XWBO` therefore remain provider and venue metadata rather than text independently displayed on the page. The immutable IDs are unchanged.

## Business economics and current evidence

Samsung combines memory semiconductors, foundry and logic chips, smartphones, displays, appliances, networks, and Harman. Memory creates substantial operating leverage when pricing and high-value server demand rise, while the device businesses provide distribution and diversification. The combination also produces considerable cyclicality and capital intensity.

[Samsung's second-quarter 2026 release](https://news.samsungsemiconductor.com/global/samsung-electronics-announces-second-quarter-2026-results/) (`source_web_f7574415d195f86ff8cb28c4`) reports:

- consolidated revenue of KRW 171.5 trillion and operating profit of KRW 89.5 trillion;
- common- and preferred-share EPS of KRW 10,849;
- Device Solutions revenue of KRW 127.5 trillion and operating profit of KRW 89.2 trillion;
- record memory results supported by server products, HBM4, enterprise SSD demand, limited capacity, and rising industry prices;
- an operating loss of KRW 0.7 trillion in Mobile eXperience and Networks; and
- a slight operating loss in Visual Display and Digital Appliances.

The evidence supports the AI-memory thesis but also supplies important contrary evidence. Device Solutions generated almost all consolidated operating profit, current memory conditions include both shortages and rising prices, and several non-memory operations were unprofitable. Treating the quarter as a permanent earnings rate would therefore be aggressive.

## Valuation method

The model applies scenario P/E multiples to normalized common-share EPS and converts the resulting ordinary-share value into EUR per GDR:

`EUR per GDR = normalized KRW EPS × P/E multiple × 25 ordinary shares per GDR ÷ KRW per EUR`

The [ECB reference-rate sheet for October 16, 2026](https://www.ecb.europa.eu/stats/shared/pdf/eurofxref.pdf?6928fbfb480e2a947b975020269c1b05=) (`source_web_38c557cf96a6c4117e6fe620`) reports **KRW 1,499.01 per EUR**. The 25:1 ratio comes from Citi's active depositary-program record.

The method uses equity earnings multiples directly, so no separate net-cash adjustment is made. The principal uncertainty is normalized earnings rather than the instrument conversion mechanics.

## Bear scenario — EUR 2,401.59, 30%

Assumptions:

- normalized common-share EPS: KRW 18,000;
- P/E multiple: 8.0x;
- severe normalization of memory pricing and supply conditions;
- weaker AI-infrastructure spending or HBM execution;
- continuing weak profitability in device operations; and
- a valuation discount for cyclicality and GDR liquidity.

Arithmetic:

`KRW 18,000 × 8.0 × 25 ÷ 1,499.01 = EUR 2,401.59`

A 30% probability reflects meaningful memory-cycle risk and the extreme concentration of current profit in Device Solutions.

## Base scenario — EUR 5,003.30, 50%

Assumptions:

- normalized common-share EPS: KRW 30,000;
- P/E multiple: 10.0x;
- AI-led server memory, HBM and enterprise SSD demand remains structurally strong;
- shortages and record pricing partially normalize; and
- device profitability improves only gradually.

Arithmetic:

`KRW 30,000 × 10.0 × 25 ÷ 1,499.01 = EUR 5,003.30`

The 50% probability makes this the central case because it preserves substantial AI-memory earnings without assuming that the record second quarter continues indefinitely.

## Bull scenario — EUR 7,961.19, 20%

Assumptions:

- normalized common-share EPS: KRW 43,396, equal to four times second-quarter EPS of KRW 10,849;
- P/E multiple: 11.0x;
- prolonged memory undersupply and strong HBM4, server DRAM and enterprise SSD demand;
- successful foundry ramps and additional advanced-node design wins; and
- recovery in mobile and consumer-device profitability.

Arithmetic:

`KRW 43,396 × 11.0 × 25 ÷ 1,499.01 = EUR 7,961.19`

The probability is limited to 20% because this scenario extrapolates an all-time-high quarter generated under unusually favorable memory conditions.

## Downside and instrument risks

Fundamental downside includes memory-price normalization, weaker AI capital spending, HBM qualification or yield setbacks, foundry underutilization, elevated capital expenditure, export restrictions, customer concentration, and persistent weakness outside Device Solutions.

Instrument-level risks include EUR/KRW movements, changes to depositary terms, custody and fee effects, cross-venue basis differences, and sparse Vienna liquidity. The opened Vienna page showed only seven trades and a last-trade volume of one security on October 16, 2026. A displayed price may therefore be less informative than a liquid primary-market quotation.

## Catalysts

Potential catalysts include:

- sustained HBM4 and enterprise-memory demand after supply expands;
- continued server-product mix gains and successful HBM4E adoption;
- profitable second-generation 2nm and other advanced-node foundry ramps;
- recovery in mobile and consumer-device margins;
- durable cash conversion through less favorable memory pricing; and
- improved Vienna liquidity or tighter parity with the London common GDR.

## Invalidation conditions

The positive operating thesis would be invalidated by a structural reversal in server-memory demand or pricing, loss of competitiveness in HBM or advanced foundry processes, sustained deterioration in cash generation or liquidity, or continuing dependence on one exceptional segment without recovery elsewhere.

The per-GDR valuation must be recalculated if the 25:1 depositary ratio changes, Vienna symbol `SSU` ceases to represent ISIN `US7960508882`, or KRW/EUR moves materially. The earnings framework should be withdrawn if later filings show that reported second-quarter EPS is not comparable with recurring common-share earnings.

## Changes since the prior review

- Citi now verifies the active common-GDR program and the **25 ordinary shares per GDR** entitlement.
- The Vienna Stock Exchange now verifies that symbol `SSU` represents ISIN `US7960508882` and supplies a current EUR quotation.
- These records resolve the prior depositary-ratio and Vienna-line identity gaps.
- A complete bear/base/bull valuation has replaced the prior `valuation_unsupported` conclusion.
- The assessment remains low confidence because normalized earnings are scenario assumptions anchored primarily to one record quarter rather than a full memory cycle.

## Limitations and status

The detailed primary operating evidence examined covers the quarter ended June 30, 2026. The supplied first- and second-quarter PDFs were too large for the available broker, so no inaccessible figures were guessed. No later detailed primary financial statements, multi-year normalized EPS analysis, live London/Vienna arbitrage comparison, depositary fee model, or forward consensus estimates were available.

The valuation therefore resolves the instrument-level coverage gap but retains substantial earnings-cycle uncertainty.

**Research status:** `supported`  
**Confidence:** low  
**Assessment valid through:** 2026-11-18