---
title: Vale S.A. sponsored ADR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-13"
updated: "2026-10-24"
provenance: "source_web_94bbb34b959a5e9ffd20856a; source_web_c71b24e973cba7203bf38ab1"
security_id: security_b2116dcf976c96974d7b
issuer_id: issuer_a3cc545e137b5f2e3a04
confidence: low
next_review: "2026-10-31"
---

# Vale S.A. sponsored ADR

## Identity

- Immutable security: `security_b2116dcf976c96974d7b`
- Immutable issuer: `issuer_a3cc545e137b5f2e3a04`
- Supplied instrument identity: Vale S.A. sponsored ADR
- Supplied market identity: `VALE` / New York Stock Exchange (`XNYS`) / USD / equity

The supplied issuer, ticker, venue and currency are internally coherent. The current opened evidence did not independently establish the sponsored ADR-to-common-share conversion ratio. Identity IDs have not been changed, but that entitlement gap prevents reliable per-ADR valuation arithmetic.

## Research conclusion

**Research status: valuation unsupported.**

Vale's operating economics remain supported by current issuer evidence, but the prior per-ADR valuation cannot be independently reconstructed. The latest detailed report available before this review covers 2Q26, while Vale has scheduled its integrated 3Q26 operating and financial report for October 29, 2026. The opened documents also do not establish the ADR ratio and complete per-share denominator needed to translate a normalized enterprise or equity value into fair value for this instrument.

The prior USD 9.00, USD 14.50 and USD 20.00 scenarios are therefore not carried forward. This is a valuation-evidence limitation rather than a conclusion that Vale lacks operating value.

## Business economics

Vale combines large-scale iron-ore production and logistics with copper and nickel operations. Its asset quality and integrated system can generate substantial cash when commodity prices and operating execution are favorable. The principal constraints are iron-ore cyclicality, exposure to Chinese steel demand, capital intensity, Brazilian currency and regulatory conditions, fuel and freight costs, project execution, and environmental and remediation obligations.

Vale's [2Q26 performance report](https://api.mziq.com/mzfilemanager/v2/d/53207d1c-63b4-48f1-96b7-19869fae19fe/69d9def3-395b-67c8-7af2-78cff5924cf2?origin=2&_gl=1*1tokn82*_gcl_au*MTE0ODU3ODYwMi4xNzgxODk0MTA5) (`source_web_94bbb34b959a5e9ffd20856a`) reported:

- Net operating revenue of USD 10.498 billion.
- Pro forma EBITDA of USD 4.066 billion and a 39% margin.
- Recurring free cash flow of USD 1.505 billion.
- Net debt of USD 13.173 billion and expanded net debt of USD 16.677 billion.
- Year-over-year sales growth of 3% for iron ore, 10% for copper and 7% for nickel.
- An average realized iron-ore fines price of USD 95.0 per tonne.
- Iron-ore C1 cash cost of USD 24.1 per tonne and all-in cost of USD 61.6 per tonne, both affected by currency and external cost pressure.
- Continued progress at Serra Sul +20 and Bacaba, with Bacaba then expected to start in 3Q27.

These facts support a viable through-cycle business and improving execution, but one favorable quarter cannot establish normalized cash generation.

## Contrary evidence and risks

The report also prevents an uncomplicated quality conclusion. Iron-ore costs increased, attributable net income declined year over year despite higher revenue, and Vale retained material net debt. Commodity realizations contributed to the quarter's performance. Remediation remained an active cash and execution responsibility, including Brumadinho commitments and the Samarco reparation program.

The resulting risk profile is material to high: weaker iron-ore demand, adverse currency and freight movements, operating interruptions, project delays, tailings obligations or capital-allocation pressure could reduce normalized cash flow. Leverage is treated separately in the balance-sheet assessment rather than counted again as an operating-risk penalty.

## Valuation method and missing evidence

A mid-cycle cash-flow framework remains preferable to a spot multiple. It should normalize commodity prices, volumes, costs, capital expenditure, remediation payments and distributions before subtracting net financial claims and dividing by the correct ADR-equivalent share count.

A supported update requires:

1. Verified sponsored ADR entitlement and quote units.
2. A current applicable diluted-share or ADR-equivalent denominator.
3. A documented bridge from normalized cash flow to equity value per ADR.
4. Updated operating and financial evidence from the integrated 3Q26 report.

Vale's [Q3 2026 release notice](https://www.vale.com/w/vale-3q26-results-release-october-29-1/-/categories) (`source_web_c71b24e973cba7203bf38ab1`) states that the results will be released after market close on October 29 and that operating, sales and financial information will be consolidated in the Performance Report. This makes a short validity period appropriate.

Although the supplied market observation reports a USD 12.399 close for October 23, it is not used for a valuation score. The required ADR entitlement and quote-unit conversion were not verified through an opened source.

## Fundamental scoring

| Factor | Score | Interpretation |
| --- | ---: | --- |
| Business quality | 65 | Between mixed economics and durable profitable advantages: strong assets and cash generation are offset by commodity cyclicality, capital intensity and cost variability. |
| Thesis support | 58 | Operating evidence is modestly favorable, but meaningful contrary evidence remains and 3Q26 information is pending. |
| Balance sheet | 60 | Cash generation supports manageable financing resilience, while material net and expanded net debt constrain the downside buffer. |
| Risk penalty | 70 | Material-to-high commodity, execution, regulatory, environmental and evidence risks; leverage is not double counted. |
| Valuation | Unsupported | ADR entitlement and normalized per-share arithmetic were not verified. |

These scores apply rubric version 1 and are research judgments, not predictions of investment returns.

## Catalysts and invalidation

Potential catalysts are sustained production delivery, successful ramp-up of Serra Sul +20, continued Bacaba progress, higher base-metals volumes, cost control, recurring cash conversion and net-debt reduction.

The operating thesis would weaken materially if iron-ore prices or demand deteriorate without cost offsets, volume growth fails to produce recurring cash flow, production reliability reverses, projects overrun, remediation obligations rise materially or net debt grows persistently. Security-level valuation remains invalid until the ADR entitlement and per-share bridge are verified.

## Changes since the prior review

- Replaced the expired supported valuation with `valuation_unsupported` rather than carrying forward unverified per-ADR scenarios.
- Added rubric-version-1 assessments for business quality, thesis support, balance-sheet resilience and residual risk.
- Confirmed that the latest accessible detailed issuer evidence remains the 2Q26 performance report.
- Added Vale's October 29 schedule for the integrated 3Q26 report.
- Shortened the review horizon to October 31 because the pending report should materially improve the evidence set.
- Removed market-action and portfolio-gating language from the research conclusion.

## Sources

- [Vale investor-relations portal](https://www.vale.com/investors) (`source_web_7a0bc55ef33c0256ceca8907`)
- [Vale's performance in 2Q26](https://api.mziq.com/mzfilemanager/v2/d/53207d1c-63b4-48f1-96b7-19869fae19fe/69d9def3-395b-67c8-7af2-78cff5924cf2?origin=2&_gl=1*1tokn82*_gcl_au*MTE0ODU3ODYwMi4xNzgxODk0MTA5) (`source_web_94bbb34b959a5e9ffd20856a`)
- [Q3 2026 Performance Release Dates](https://www.vale.com/w/vale-3q26-results-release-october-29-1/-/categories) (`source_web_c71b24e973cba7203bf38ab1`)

## Review status

Confidence is **low** for security-level valuation and moderate for the operating observations derived from the 2Q26 issuer report. Review by **2026-10-31**, after the scheduled 3Q26 release, or earlier if a material operating, liability or financing development occurs.
