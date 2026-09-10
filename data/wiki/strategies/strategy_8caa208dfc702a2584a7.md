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
allocation_plan_id: allocation_plan_6271cd1bd15ef73f7441
allocation_intent_id: allocation_intent_451ca921751ca6e57921
status: active
---

# Prosus bounded baseline allocation

## Decision

Maintain only bounded long-equity baseline exposure in [[securities/security_8b703a8adf5f864acaa4|PRX]] under the current allocation. The active strategy is bound only to allocation plan `allocation_plan_6271cd1bd15ef73f7441`, intent `allocation_intent_451ca921751ca6e57921`, assessment `assessment_7f28dfd9240d6099400b`, and the accepted [[relationships/relationship_e514a92bf6c38d0754ee|digital-attention relationship]]. The allocator persists a six-share, 2.120777% target with a 5% position ceiling. Its normalized `open` disposition reflects movement from projected exposure after the prior pending close, not permission to choose six additional shares; deterministic execution code must recompute the exact delta from current holdings, pending orders, price and cash and may create no order when no positive open delta remains.

This is a lower-conviction full-baseline decision, not a conviction allocation. Prosus retains Tencent-dominated look-through value, ecommerce exposure and potential per-share accretion from repurchases below NAV. Medium confidence, holding-company concentration, private-asset marks, governance and capital-allocation transmission remain material soft gaps, while weak momentum reinforces the need for bounded sizing. The six-share target is preferable to cash only within the allocator's diversified baseline budget because the current scenario economics clear every canonical full-baseline gate without a hard blocker.

## Evidence and valuation

Prosus's 27 August 2026 NAV disclosure reported USD 157.4 billion of assets, USD 7.0 billion of pro-forma net debt, USD 150.4 billion of NAV and EUR 61.5 of NAV per share. Tencent represented USD 117.0 billion, while USD 32.8 billion of unlisted values relied on analyst or post-money inputs that Prosus explicitly did not endorse. Repurchases had reduced roughly thirty percent of free float and added about eighteen percent to NAV per share, supporting the transmission mechanism while leaving a wide holding-company discount. [Primary NAV disclosure](https://www.prosus.com/investors/investing-in-prosus/net-asset-value?locale=en)

The accepted assessment retains a twelve-month EUR 30, EUR 52 and EUR 70 bear/base/bull range with probabilities of thirty, fifty and twenty percent, medium confidence, and a quality score of 70. Repriced at the current EUR 35.294998 mark, the plan records bear, base and bull returns of -15.002124%, 47.330929% and 98.328289%, a 38.829870% probability-weighted expected return, a 29.122402% confidence-adjusted expected return and 32.600960% margin of safety. These clear the stored full-baseline frontier: 10% base upside, 1:1 bear/base payoff, 10% confidence-adjusted expected return, 0.75 expected/bear payoff, non-negative margin of safety, medium confidence, an accepted relationship and no hard blocker.

The latest PRX mark is EUR 35.294998, retrieved at 2026-09-10T20:48:19Z inside the configured 36-hour freshness window. The same-date indicator projection has 256 observations, RSI 32.573547, a negative MACD histogram and an active lower-Bollinger-band trigger; this is weak timing context rather than an override of the canonical eligibility calculation. No FX conversion is required because both the security and portfolio base currency are EUR. The current plan records eight filled shares and a negative pending weight associated with the preceding close path, so the separate execution operation must revalidate current pending-order state and derive the exact whole-share delta rather than treating the persisted target as an order quantity.

## Structure comparison

| Structure | Eligibility | Fit | Main limitation |
|---|---|---|---|
| Long equity | Selected | Preserves bounded participation in look-through NAV and repurchase accretion under the six-share target | Holding-company concentration, private marks, governance and weak momentum |
| Short equity | Rejected | Would contradict the accepted positive relationship and current positive-return scenarios | Baseline mode permits only long equity |
| Options or bounded multi-leg options | Not eligible | Could reshape payoff only in conviction mode | No complete fresh contract identity, bid/ask, liquidity evidence or mandate was supplied |

Prosus does not qualify for conviction treatment: quality is 70, below the configured conviction threshold of 80, and confidence remains medium rather than high. Tencent concentration, private marks, governance and capital-allocation transmission remain material non-operating risks. Long common equity is therefore the only eligible structure and remains bounded by the 5% tier-specific position ceiling; the current target is 2.120777%, not a redefinition of that stable risk budget.

## Entry, sizing, and exit

- Entry: permit only a time-bounded normalized `open` signal while the current plan, intent, assessment and relationship identities remain current, PRX market data remains fresh, and deterministic code derives a positive whole-share delta toward the persisted six-share target after holdings and pending orders.
- Sizing: retain the allocator-owned six-share target and the stable 5% maximum-position risk budget. This research does not choose or enlarge quantity.
- Exit: reduce or close only when a current deterministic plan directs it, the full-baseline frontier no longer clears, a hard blocker appears, or material thesis evidence invalidates the bounded exposure. A signal is not an order or fill.
- Invalidation: do not increase exposure if Tencent or private-platform economics deteriorate, private marks become unreliable, central net debt rises, value transmission or repurchase accretion is blocked, capital allocation destroys per-share NAV, the assessment or relationship is superseded, or market inputs become stale.
- Review: by the assessment expiry on 2026-09-27, or earlier after material NAV, Tencent, ecommerce, debt, repurchase, governance, market-data or allocation-plan evidence.

## Visual evidence

The scenario spread shows why only bounded baseline exposure is justified: the base and bull cases offer substantial upside from the current mark, but the bear case remains a material loss and medium confidence prevents conviction treatment.

```echart
{
  "schema_version": 1,
  "chart_id": "prosus-baseline-scenario-returns",
  "kind": "series",
  "title": "Prosus baseline scenario returns",
  "description": "Canonical twelve-month scenario and probability-weighted returns at the current allocation-plan valuation mark.",
  "as_of": "2026-09-10T20:48:19Z",
  "sources": [
    {
      "label": "PaperTrader allocation target for security_8b703a8adf5f864acaa4",
      "observed_at": "2026-09-10T20:48:19Z"
    }
  ],
  "x_axis": {
    "type": "category",
    "label": "Scenario",
    "values": ["Bear", "Base", "Bull", "Probability weighted"]
  },
  "y_axes": [
    {
      "label": "Return",
      "unit": "%",
      "format": "percent"
    }
  ],
  "series": [
    {
      "name": "Twelve-month return",
      "render": "bar",
      "y_axis": 0,
      "values": ["-15.00212416934538489116473969", "47.33092877313466618864778454", "98.32828873306687256164124842", "38.8298697890659920486923207"]
    }
  ],
  "notes": [
    "Bear, base and bull fair values are EUR 30, EUR 52 and EUR 70 with probabilities of 30%, 50% and 20%.",
    "The chart summarizes canonical allocation evidence and does not authorize or size an order."
  ]
}
```

## Connections

- [[ideas/idea_digital_attention_gaming_ecosystems|Digital attention, gaming, and consumer ecosystems]]
- [[securities/security_8b703a8adf5f864acaa4|Prosus N.V. ordinary shares N]]
- [[relationships/relationship_e514a92bf6c38d0754ee|Digital attention, gaming, and consumer ecosystems to Prosus]]
