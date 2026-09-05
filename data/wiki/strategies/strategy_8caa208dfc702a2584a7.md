---
title: Prosus bounded baseline allocation
created: 2026-09-03
updated: 2026-09-05
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
allocation_plan_id: allocation_plan_e9ff34dda455150b7366
allocation_intent_id: allocation_intent_3e3d6793d5aacc3843e8
status: active
---

# Prosus bounded baseline allocation

## Decision

Retain one long-equity leg in [[securities/security_8b703a8adf5f864acaa4|PRX]] and permit a bounded increase under the current baseline allocation. The active strategy is bound only to allocation plan `allocation_plan_e9ff34dda455150b7366`, intent `allocation_intent_3e3d6793d5aacc3843e8`, assessment `assessment_7f28dfd9240d6099400b`, and the accepted [[relationships/relationship_e514a92bf6c38d0754ee|digital-attention relationship]]. The allocator persists an eleven-share target versus eight filled shares; deterministic order code, not this research, derives whether a positive executable delta remains.

The structure remains baseline rather than conviction. Prosus offers Tencent-dominated look-through value, growing ecommerce exposure and per-share accretion from repurchases below NAV, but medium confidence, holding-company concentration, private-asset valuation uncertainty, central debt, governance and capital-allocation transmission prevent conviction treatment. A five percent maximum-position ceiling bounds the baseline exposure; the current 2.97% weight and 4.10% target are allocator-owned and must not be mistaken for that ceiling or for an order.

## Evidence and valuation

Prosus's 27 August 2026 NAV disclosure reported USD 157.4 billion of assets, USD 7.0 billion of pro-forma net debt, USD 150.4 billion of NAV and EUR 61.5 of NAV per share. Tencent represented USD 117.0 billion, while USD 32.8 billion of unlisted values relied on analyst or post-money inputs that Prosus explicitly did not endorse. Repurchases had reduced roughly thirty percent of free float and added about eighteen percent to NAV per share, supporting the transmission mechanism while leaving a wide holding-company discount. [Primary NAV disclosure](https://www.prosus.com/investors/investing-in-prosus/net-asset-value?locale=en)

The current accepted assessment uses a twelve-month EUR 30, EUR 52 and EUR 70 bear/base/bull range with probabilities of thirty, fifty and twenty percent. At the current plan's canonical EUR 37.310001 mark, stored scenario returns are -19.59%, 39.37% and 87.62%. The stored probability-weighted return is 31.33%, confidence-adjusted expected return is 23.50%, margin of safety is 28.25%, base-upside-to-bear-downside is 2.01, and expected-upside-to-bear-downside is 1.20. These clear the current full-baseline frontier, so the bounded increase is preferable to cash while the accepted relationship and evidence remain current.

The refreshed PRX mark is EUR 37.310001, retrieved at 2026-09-05T09:19:19Z. It was inside the configured thirty-six-hour freshness window at evaluation. No FX conversion is required because both the security and portfolio base currency are EUR. The 4 September technical projection showed RSI 43.30, price below its twenty-, fifty- and two-hundred-day moving averages, and no active trigger; this tempers timing but does not defeat the stored baseline frontier. Price freshness authorizes review only; it does not override the persisted target.

## Structure comparison

| Structure | Eligibility | Fit | Main limitation |
|---|---|---|---|
| Long equity | Selected for bounded increase | Direct, unlevered exposure to look-through NAV and repurchase accretion; the only baseline-permitted structure | Full holding-company, Tencent and private-asset downside remains |
| Short equity | Rejected | Would oppose the accepted positive relationship and current open allocation | Wrong direction for the maintained thesis |
| Call or put | Not eligible | Could reshape payoff in conviction mode | No complete fresh contract identity, bid/ask or liquidity evidence was supplied |
| Bounded multi-leg options | Not eligible | Could cap premium risk in conviction mode | No complete fresh legs or comparable quote set was supplied |

Prosus does not qualify for conviction treatment despite attractive current-plan economics: quality is 70, below the configured conviction threshold of 80, and confidence remains medium rather than high. Tencent concentration, private marks, governance and capital-allocation transmission leave material non-operating risk, while the plan records insufficient diversification. The five percent ceiling therefore remains a risk maximum, not a target selected by this strategy.

## Entry, sizing, and exit

- Entry: permit only a time-bounded `open` signal while the current plan, intent, assessment and relationship identities remain current, the fresh EUR price is available, and deterministic code derives a positive whole-share delta toward eleven shares after accounting for holdings and pending orders.
- Sizing: the risk budget is the baseline ceiling of five percent, not the current 4.10% target weight and not an agent-selected order size. The allocation plan remains the sole sizing authority.
- Exit: reduce or close when a current deterministic plan directs it, the canonical baseline frontier fails, or a hard blocker appears.
- Invalidation: do not increase exposure if Tencent or private-platform economics deteriorate materially, private marks prove unreliable, central net debt rises, governance or cross-holding complexity blocks value transmission, repurchases lose accretion, the holding discount widens persistently despite operating value creation, or the assessment or relationship is superseded.
- Review: no later than 2026-09-27, or earlier after material NAV, Tencent, ecommerce, debt, repurchase, governance or deterministic market evidence.

## Visual evidence

The chart shows the stored scenario returns used by the current allocation decision. It is not an order, a forecast path, or a substitute for the canonical assessment.

```echart
{"schema_version":1,"chart_id":"prosus-baseline-scenario-returns","kind":"series","title":"Prosus baseline scenario returns","description":"Twelve-month bear, base and bull returns at the current allocation plan's canonical EUR 37.310001 mark. The bounded baseline increase retains holding-company and look-through NAV downside and does not imply conviction sizing.","as_of":"2026-09-05T09:19:19Z","sources":[{"label":"Current allocation target and accepted Prosus assessment","observed_at":"2026-09-05T09:19:19Z"},{"label":"Prosus net asset value at 27 August 2026","url":"https://www.prosus.com/investors/investing-in-prosus/net-asset-value?locale=en","observed_at":"2026-08-28T19:18:00Z"}],"notes":["Scenario probabilities are bear 30%, base 50%, and bull 20%.","Returns are canonical stored current-plan outputs; the chart does not select quantity or authorize execution."],"x_axis":{"type":"category","label":"Scenario","values":["Bear","Base","Bull"]},"y_axes":[{"label":"Twelve-month return","unit":"percent","format":"percent"}],"series":[{"name":"Scenario return","render":"bar","y_axis":0,"values":["-19.59260547903383853150504381","39.3728171696746798787245907","87.6172538822543767598215644"]}]}
```

The scenario spread explains the bounded posture: expected and base returns clear the baseline hurdles, but look-through asset values and shareholder transmission remain uncertain and confidence is only medium.

## Connections

- [[ideas/idea_digital_attention_gaming_ecosystems|Digital attention, gaming, and consumer ecosystems]]
- [[securities/security_8b703a8adf5f864acaa4|Prosus N.V. ordinary shares N]]
- [[relationships/relationship_e514a92bf6c38d0754ee|Digital attention, gaming, and consumer ecosystems to Prosus]]
