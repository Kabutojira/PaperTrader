---
title: Tencent bounded baseline allocation
created: 2026-09-03
updated: 2026-09-10
type: strategy
tags:
  - strategy
  - security
  - idea
  - relationship
sources:
  - source_tencent_q2_2026_results
  - data/tables/security_assessments.csv
  - data/tables/allocation_targets.csv
  - data/market/latest.csv
  - data/market/fx/USD_EUR.csv
confidence: medium
provenance: source_tencent_q2_2026_results
strategy_id: strategy_ef910e9aff5203a0b901
idea_id: idea_digital_attention_gaming_ecosystems
security_id: security_de0d83229b369a426b99
relationship_id: relationship_f625ba3c07d49e1865ff
allocation_plan_id: allocation_plan_4e0ef8323f8d383f6b85
allocation_intent_id: allocation_intent_818e8692a59dfaa00cad
status: ready
---

# Tencent bounded baseline allocation

## Decision

Use one long-equity leg in [[securities/security_de0d83229b369a426b99|TCEHY]] for the current starter allocation. The strategy is ready only against allocation plan `allocation_plan_4e0ef8323f8d383f6b85`, unchanged intent `allocation_intent_818e8692a59dfaa00cad`, assessment `assessment_6e8ef7291ff81b77d900`, and the accepted [[relationships/relationship_f625ba3c07d49e1865ff|digital-attention relationship]]. The persisted target is four shares; deterministic order code, not this research, derives any executable delta.

The structure is baseline rather than conviction. Tencent's gaming, advertising and Weixin ecosystem support cash generation and repurchases, but medium confidence, China policy and governance exposure, investment-portfolio volatility, artificial-intelligence spending, and insufficient diversification prevent conviction treatment. A two percent position ceiling bounds those gaps and is preferable to cash only while the repository's starter frontier remains satisfied.

## Evidence and valuation

Tencent's August 2026 second-quarter release reported year-on-year revenue growth of fifteen percent, gross-profit growth of twenty-two percent and non-IFRS operating-profit growth of eighteen percent. Domestic and international games, marketing services and gross-margin expansion support the maintained mechanism; artificial-intelligence investment and policy-sensitive monetization remain material counterweights. [Primary release](https://www.tencent.com/wp-content/uploads/2026/08/Tencent-Announces-2026-Second-Quarter-Results.pdf)

The current accepted assessment uses a twelve-month USD forty, USD sixty-five and USD ninety bear/base/bull range with probabilities of twenty-five, fifty and twenty-five percent. At the allocator's current USD fifty-four point six nine valuation mark, the stored scenario returns are negative twenty-six point eight six percent, positive eighteen point eight five percent and positive sixty-four point five six percent. The stored expected return is positive eighteen point eight five percent, confidence-adjusted expected return is positive fourteen point one four percent, margin of safety is positive fifteen point eight six percent, base-upside-to-bear-downside is zero point seven zero, and expected-upside-to-bear-downside is zero point five three. These clear the current starter frontier but not the stronger conviction gate.

The refreshed market mark is USD fifty-four point six nine and the USD/EUR rate is zero point eight six zero seven, both retrieved at 2026-09-10T18:10:21Z. They were inside the configured thirty-six-hour freshness window at evaluation. Price and FX freshness authorize review only; they do not override the persisted target.

## Structure comparison

| Structure | Eligibility | Fit | Main limitation |
|---|---|---|---|
| Long equity | Selected | Direct, unlevered exposure to the accepted mechanism and the only baseline-permitted structure | Full bear-case downside remains |
| Short equity | Rejected | Contradicts the positive accepted relationship and current open allocation | Wrong direction for the maintained thesis |
| Call or put | Not eligible | Could reshape payoff in conviction mode | No complete fresh contract identity, bid/ask or liquidity evidence was supplied |
| Bounded multi-leg options | Not eligible | Could cap premium risk in conviction mode | No complete fresh legs or comparable quote set was supplied |

## Entry, sizing, and exit

- Entry: permit only a time-bounded `open` signal while the current plan, intent, assessment and relationship identities remain unchanged, fresh price and FX inputs exist, and deterministic code derives a positive whole-share delta toward four shares.
- Sizing: the risk budget is the starter ceiling of two percent, not a selected order size. The allocation plan remains the sole sizing authority.
- Exit: reduce or close when a current deterministic plan directs it, the canonical starter frontier fails, or a hard blocker appears.
- Invalidation: do not increase exposure if gaming or advertising monetization weakens materially, Weixin engagement ceases to support commercial activity, policy or governance risk impairs shareholder economics, artificial-intelligence investment fails to convert into durable cash generation, portfolio-value volatility dominates operations, or the assessment or relationship is superseded.
- Review: no later than 2026-09-27, or earlier on a material filing, policy change, valuation change, or deterministic alert.

## Visual evidence

The chart shows the stored scenario returns used by the current allocation decision. It is not an order, a forecast path, or a substitute for the canonical assessment.

```echart
{"schema_version":1,"chart_id":"tencent-baseline-scenario-returns","kind":"series","title":"Tencent baseline scenario returns","description":"Twelve-month bear, base and bull returns at the allocator's current USD 54.689998626708984 valuation mark. The bounded starter decision retains the full bear case and does not imply conviction sizing.","as_of":"2026-09-10T18:10:21Z","sources":[{"label":"Current allocation target and accepted Tencent assessment","observed_at":"2026-09-10T18:10:21Z"},{"label":"Tencent 2026 second-quarter results","url":"https://www.tencent.com/wp-content/uploads/2026/08/Tencent-Announces-2026-Second-Quarter-Results.pdf","observed_at":"2026-08-28T19:23:00Z"}],"notes":["Scenario probabilities are bear 25%, base 50%, and bull 25%.","Returns are canonical stored allocation outputs for the accepted assessment."],"x_axis":{"type":"category","label":"Scenario","values":["Bear","Base","Bull"]},"y_axes":[{"label":"Twelve-month return","unit":"percent","format":"percent"}],"series":[{"name":"Scenario return","render":"bar","y_axis":0,"values":["-26.86048454119876587740257908","18.851712620552005449220809","64.5639097823027767758441971"]}]}
```

The scenario spread explains the bounded posture: the base case clears the starter hurdle, but the bear case remains material and confidence is only medium.

## Connections

- [[ideas/idea_digital_attention_gaming_ecosystems|Digital attention, gaming, and consumer ecosystems]]
- [[securities/security_de0d83229b369a426b99|Tencent Holdings Limited sponsored ADR]]
- [[relationships/relationship_f625ba3c07d49e1865ff|Digital attention, gaming, and consumer ecosystems to Tencent]]
