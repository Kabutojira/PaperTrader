---
title: Prosus bounded baseline allocation
created: 2026-09-03
updated: 2026-09-10
type: strategy
tags:
  - strategy
  - security
  - idea
  - relationship
sources:
  - source_prosus_nav_20260827
  - data/tables/security_assessments.csv
  - data/tables/allocation_targets.csv
  - data/market/latest.csv
confidence: medium
provenance: source_prosus_nav_20260827
strategy_id: strategy_8caa208dfc702a2584a7
idea_id: idea_digital_attention_gaming_ecosystems
security_id: security_8b703a8adf5f864acaa4
relationship_id: relationship_e514a92bf6c38d0754ee
allocation_plan_id: allocation_plan_cf731760648bb43b2e47
allocation_intent_id: allocation_intent_b8f1131f2221ca6c0fec
status: active
---

# Prosus bounded baseline allocation

## Decision

Close the existing long-equity exposure in [[securities/security_8b703a8adf5f864acaa4|PRX]] under the current baseline allocation. The active strategy is bound only to allocation plan `allocation_plan_cf731760648bb43b2e47`, intent `allocation_intent_b8f1131f2221ca6c0fec`, assessment `assessment_7f28dfd9240d6099400b`, and the accepted [[relationships/relationship_e514a92bf6c38d0754ee|digital-attention relationship]]. The allocator persists a zero-share, zero-weight target against eight filled shares because `market_data_not_ok`; deterministic execution code, not this research, derives the exact sell quantity and must revalidate executable market data before creating a paper order.

This is an exit-only watch-tier decision, not a reversal of the underlying positive relationship and not a fresh fundamental downgrade. Prosus retains Tencent-dominated look-through value, ecommerce exposure and potential per-share accretion from repurchases below NAV, but the current plan fails closed when its deterministic market retrieval is unusable. The plan therefore sets both target and position cap to zero; no opening, increase or retained allocation is authorized.

## Evidence and valuation

Prosus's 27 August 2026 NAV disclosure reported USD 157.4 billion of assets, USD 7.0 billion of pro-forma net debt, USD 150.4 billion of NAV and EUR 61.5 of NAV per share. Tencent represented USD 117.0 billion, while USD 32.8 billion of unlisted values relied on analyst or post-money inputs that Prosus explicitly did not endorse. Repurchases had reduced roughly thirty percent of free float and added about eighteen percent to NAV per share, supporting the transmission mechanism while leaving a wide holding-company discount. [Primary NAV disclosure](https://www.prosus.com/investors/investing-in-prosus/net-asset-value?locale=en)

The accepted assessment retains a twelve-month EUR 30, EUR 52 and EUR 70 bear/base/bull range with probabilities of thirty, fifty and twenty percent, medium confidence, and a quality score of 70. Those dated valuation assumptions explain the prior bounded baseline case but are not live decision metrics in the current plan: the plan carries no valuation mark or scenario returns because its market-data gate failed. The canonical zero target overrides the prior entry case without converting unavailable inputs into invented returns.

The last successful PRX mark remains EUR 35.294998, retrieved at 2026-09-10T18:10:21Z, and the reconciled portfolio records eight shares marked at that value. The later allocation evaluation at 2026-09-10T19:43:26Z nevertheless records `market_data_not_ok`, so this research does not treat the earlier mark as a valid current valuation input. No FX conversion is required because both the security and portfolio base currency are EUR. A close signal can express the risk-reducing decision, but a separate deterministic execution operation must fail closed unless its own price and identity checks pass.

## Structure comparison

| Structure | Eligibility | Fit | Main limitation |
|---|---|---|---|
| Long equity close | Selected | Removes the existing baseline exposure toward the allocator-owned zero-share target | Execution still requires deterministic market-data validation |
| Retain or increase long equity | Rejected | Would preserve the prior look-through NAV exposure | Current plan is watch tier with zero target and `market_data_not_ok` |
| Short equity | Rejected | Would reverse rather than close the maintained positive exposure | Baseline mode permits only long equity and the plan asks only for an exit |
| Options or bounded multi-leg options | Not eligible | Could reshape payoff only in conviction mode | No complete fresh contract identity, bid/ask, liquidity evidence or mandate was supplied |

Prosus does not qualify for conviction treatment: quality is 70, below the configured conviction threshold of 80, and confidence remains medium rather than high. Tencent concentration, private marks, governance and capital-allocation transmission remain material non-operating risks. More importantly for this operation, the current watch-tier plan permits only a zero-risk-budget close; it supplies no current economics from which an entry structure could be justified.

## Entry, sizing, and exit

- Entry: none. Do not open, increase or retain exposure under this watch-tier plan.
- Sizing: the risk budget, position cap, target weight and target quantity are all zero. Deterministic code derives the close quantity from current holdings; this research does not select it.
- Exit: permit one time-bounded `close` signal while the current plan, intent, assessment and relationship identities remain current. A signal is not an order or fill.
- Invalidation: the prior bounded-entry case is invalid while canonical market data is unusable. Independent thesis invalidations remain material Tencent or private-platform deterioration, unreliable private marks, rising central net debt, blocked value transmission, lost repurchase accretion or destructive capital allocation.
- Review: after valid market inputs return and a new allocation plan is generated, or earlier after material NAV, Tencent, ecommerce, debt, repurchase or governance evidence.

## Visual evidence

No analytical chart is supportable for this decision. The current plan intentionally carries no valuation mark or comparable bear/base/bull returns after `market_data_not_ok`; charting the prior plan's scenario returns would misrepresent them as inputs to the current zero-target close. The two available allocation observations—eight current shares and zero target shares—are also below the three-observation chartability threshold.

## Connections

- [[ideas/idea_digital_attention_gaming_ecosystems|Digital attention, gaming, and consumer ecosystems]]
- [[securities/security_8b703a8adf5f864acaa4|Prosus N.V. ordinary shares N]]
- [[relationships/relationship_e514a92bf6c38d0754ee|Digital attention, gaming, and consumer ecosystems to Prosus]]
