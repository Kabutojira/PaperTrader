---
title: Samsung Electronics common GDR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-29"
updated: "2026-10-19"
provenance: "source_web_f7574415d195f86ff8cb28c4; source_samsung_common_gdr_identity; source_web_38c557cf96a6c4117e6fe620"
security_id: security_567d0d575bbd30aaa91d
issuer_id: issuer_adf6eb6a528f8576f0ed
confidence: low
next_review: "2026-11-18"
---

# Samsung Electronics common GDR

## Research conclusion

Samsung's operating thesis is supported by exceptional memory-led earnings, but a defensible EUR valuation for the specified `SSU.VI` instrument is not. Current evidence resolves the foreign-exchange bridge and current share count but does not verify the GDR-to-ordinary-share entitlement, the Vienna line, or normalized through-cycle earnings. Research status is therefore **valuation unsupported**, with no bear, base, or bull values.

## Identity reconciliation

- Immutable security: `security_567d0d575bbd30aaa91d`
- Immutable issuer: `issuer_adf6eb6a528f8576f0ed`
- Supplied instrument identity: Samsung Electronics common GDR, `SSU.VI`, MIC `XWBO`, EUR
- Issuer-confirmed common GDR: London symbol `SMSN`, ISIN `US7960508882`
- Issuer-confirmed Korean common share: `005930`, ISIN `KR7005930003`

[Samsung's listing information](https://www.samsung.com/global/ir/stock-information/listing-Info/) (`source_samsung_common_gdr_identity`) confirms that Samsung common GDRs are listed in London under `SMSN` and reports 5,846,278,608 common shares and 802,371,203 preferred shares outstanding at June 30, 2026. The accessible issuer page does **not** state the number of ordinary shares represented by one GDR and does not corroborate ticker `SSU.VI` or MIC `XWBO`. The supplied IDs are retained unchanged, but instrument-level identity uncertainty remains material.

## Business economics

Samsung combines memory semiconductors, foundry and logic chips, smartphones, displays, appliances, networks, and Harman. The semiconductor portfolio creates substantial operating leverage when memory prices and high-value server demand rise, while the device businesses provide distribution and diversification. The same structure creates cyclicality, capital intensity, and periods in which record memory profit can conceal weak economics elsewhere.

[Samsung's second-quarter release](https://news.samsungsemiconductor.com/global/samsung-electronics-announces-second-quarter-2026-results/) (`source_web_f7574415d195f86ff8cb28c4`) reports:

- consolidated revenue of KRW 171.5 trillion;
- operating profit of KRW 89.5 trillion;
- common- and preferred-share EPS of KRW 10,849;
- Device Solutions revenue of KRW 127.5 trillion and operating profit of KRW 89.2 trillion;
- record memory results supported by server products, HBM4, enterprise SSD demand, supply constraints, and rising industry prices; and
- an operating loss of KRW 0.7 trillion in Mobile eXperience and Networks, plus a slight loss in Visual Display and Digital Appliances.

These facts support strong AI-memory exposure but also provide contrary evidence: almost all consolidated operating profit came from Device Solutions, current supply constraints are unusually favorable, and important consumer-device operations were unprofitable.

## Valuation method and unresolved coverage

An earnings-multiple method is conceptually appropriate for an equity GDR, but three inputs are essential:

1. normalized common-share earnings across the memory cycle;
2. the legally effective number of common shares represented by each GDR; and
3. contemporaneous KRW/EUR translation.

The third input is now available. The [ECB reference-rate sheet for October 16, 2026](https://www.ecb.europa.eu/stats/shared/pdf/eurofxref.pdf?6928fbfb480e2a947b975020269c1b05=) (`source_web_38c557cf96a6c4117e6fe620`) reports KRW 1,499.01 per EUR. That permits currency conversion but cannot resolve the missing depositary ratio or cross-venue basis.

The earnings input also remains unsuitable for a scenario-complete valuation. Annualizing the record second-quarter EPS would assume that supply-constrained memory pricing and segment profitability persist unchanged. Selecting a lower normalized EPS without a verified cycle framework would be equally arbitrary. Samsung's [financial-highlights page](https://www.samsung.com/global/ir/financial-information/financial-valuation-snapshot/) (`source_web_c21c4c600fcccd918973340e`) states that its snapshot is updated after business reports and directs readers to earnings releases for the latest results, but the accessible page provides no normalized or forward earnings measure.

Because the instrument ratio and normalized earnings are both unresolved, no per-GDR arithmetic can be completed honestly. Bear, base, and bull fair values, assumptions, and probabilities are intentionally empty rather than carried forward or inferred from the market price.

## Thesis and assumptions

The positive thesis is exposure to AI-led server DRAM, HBM, enterprise SSDs, advanced foundry demand, broad device distribution, and substantial operating leverage. The principal assumption requiring future verification is that a meaningful portion of current memory earnings can persist after shortages ease.

A supportable valuation would additionally require verified depositary documentation for `US7960508882`, independent confirmation that the Vienna `SSU.VI` line is the same fungible common GDR, a current cross-venue comparison, and normalized earnings built from more than one exceptionally favorable quarter.

## Downside and contrary evidence

Downside mechanisms include memory-price normalization, weaker AI-infrastructure spending, HBM qualification or yield problems, advanced-node foundry execution risk, high capital requirements, export restrictions, customer concentration, and persistent consumer-device margin pressure. For this security, EUR/KRW movements, depositary terms, cross-venue basis, and sparse Vienna turnover may cause returns to diverge from the Korean ordinary shares.

The strongest contrary evidence is concentration: second-quarter Device Solutions operating profit was nearly equal to consolidated operating profit, while mobile/network and consumer-electronics groupings reported losses. This makes extrapolation of one record memory quarter particularly hazardous.

## Catalysts and invalidation

Potential catalysts are sustained HBM4 and enterprise-memory demand after supply expands, durable cash conversion through a less favorable pricing environment, profitable advanced-node foundry ramps, recovery in device margins, and publication of verifiable depositary and Vienna-listing terms.

The positive operating thesis would be invalidated by a structural reversal in server-memory demand or pricing, loss of HBM or foundry technology competitiveness, sustained deterioration in cash generation or liquidity, or continued dependence on one exceptional segment. Any future instrument valuation must also be invalidated if its assumed GDR ratio, fungibility, or currency treatment cannot be confirmed.

## Changes since the prior review

- A current ECB rate now resolves the previously missing KRW/EUR translation input.
- Samsung's refreshed listing page provides the June 2026 share count and confirms the London common GDR's symbol and ISIN.
- The same listing evidence exposes an unresolved identity limitation: it does not corroborate `SSU.VI` on `XWBO` or state the GDR ratio.
- The accessible second-quarter issuer release confirms record memory-led results and weak profitability in several device businesses.
- The valuation-coverage gap remains unresolved because normalized earnings and the instrument conversion ratio are still missing.
- Prior claims that one GDR represents 25 common shares are not carried forward because that ratio was not verified in a source opened for this review.

## Limitations and status

The latest detailed operating evidence examined covers the quarter ended June 30, 2026. A supplied first-quarter PDF could not be read through the available broker, and no inaccessible figures were guessed or reused. No later detailed primary financial statements were available in the opened evidence.

**Research status:** `valuation_unsupported`  
**Confidence:** low  
**Assessment valid through:** 2026-11-18

The operating case remains credible, but a scenario-complete EUR valuation for `SSU.VI` is not supportable from the verified evidence.