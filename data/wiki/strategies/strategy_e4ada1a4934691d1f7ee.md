---
title: "Uber bounded baseline allocation"
type: strategy
status: ready
tags: [strategy, research, risk]
created: "2026-09-03"
updated: "2026-09-10"
provenance: "source_uber_q2_2026_10q"
strategy_id: strategy_e4ada1a4934691d1f7ee
idea_id: idea_mobility_platform_autonomy
security_id: security_e4822686f60a96824b6e
relationship_id: relationship_d403f81ae5b27c9643dd
confidence: medium
next_review: "2026-09-27"
sleeve: baseline
allocation_plan_id: allocation_plan_4e0ef8323f8d383f6b85
allocation_intent_id: allocation_intent_ae3d5bc9b6efe4a816f1
assessment_id: assessment_7fe1690682aa6c66e233
---

# Uber bounded baseline allocation

## Visual evidence

The current allocation plan's scenario returns support a bounded full-baseline position: base and probability-weighted returns clear the canonical hurdles, while the bear case remains material.

```echart
{
  "schema_version": 1,
  "chart_id": "uber-baseline-scenario-returns",
  "kind": "series",
  "title": "Uber current-plan scenario returns",
  "description": "Bear, base and bull twelve-month returns at the allocation plan's USD 71.08000183105469 valuation mark show the upside and material downside behind a bounded full-baseline position.",
  "as_of": "2026-09-10T18:10:21Z",
  "sources": [
    {
      "label": "Uber Q2 2026 Form 10-Q",
      "url": "https://www.sec.gov/Archives/edgar/data/1543151/000154315126000032/uber-20260630.htm",
      "observed_at": "2026-08-28T19:27:50Z"
    },
    {
      "label": "PaperTrader allocation plan allocation_plan_4e0ef8323f8d383f6b85",
      "observed_at": "2026-09-10T18:10:21Z"
    }
  ],
  "x_axis": {
    "type": "category",
    "label": "Scenario",
    "values": ["Bear", "Base", "Bull"]
  },
  "y_axes": [
    {
      "label": "Twelve-month return",
      "unit": "%",
      "format": "percent"
    }
  ],
  "series": [
    {
      "name": "Scenario return",
      "render": "bar",
      "y_axis": 0,
      "values": ["-22.62239929210211982475708407", "26.617892067469258468579317", "68.8238560899590112914390893"]
    }
  ],
  "notes": [
    "Scenario values are USD 55, USD 90 and USD 120 with probabilities of 25%, 50% and 25% over twelve months.",
    "The chart uses the immutable current allocation plan mark; neither the chart nor the strategy resizes the deterministic target."
  ]
}
```

## Decision

**Ready — long common equity in the full baseline sleeve.** The current deterministic plan assigns a 3.06% target, capped at 5%, and persists a five-share target. Current and pending weights are both zero, so the positive delta exceeds the 1% minimum-trade threshold. The quantity is allocator-owned, is not an agent sizing decision, and is not yet an order or fill. The accepted [[relationships/relationship_d403f81ae5b27c9643dd|mobility-platform relationship]] and [[securities/security_e4822686f60a96824b6e|Uber assessment]] support a bounded position rather than conviction exposure.

The USD 71.08000183105469 plan mark implies bear/base/bull returns of -22.62%/26.62%/68.82%, a 24.86% probability-weighted return and an 18.64% confidence-adjusted return. The 21.02% margin of safety, 1.18 bear/base payoff ratio and 0.82 expected/bear payoff ratio clear the full-baseline frontier encoded by the allocator. Cash is therefore less attractive for this bounded tranche, but it remains preferable for the rest of the portfolio allocation.

The refreshed plan preserves assessment `assessment_7fe1690682aa6c66e233` and the accepted relationship while binding allocation intent `allocation_intent_ae3d5bc9b6efe4a816f1`. Rank three, effective score 84 and the `open` disposition support processing the current positive delta. The target value is EUR 305.89279187938700370255965 using the current USD/EUR observation; refreshed plan identity, weight and quantity do not authorize the strategy to resize itself.

## Structure review

Baseline mode permits only long equity. Common stock is liquid, directly expresses the accepted network-economics mechanism, has no option expiry or premium loss, and lets deterministic order code derive the exact current-plan delta. Short equity, calls, puts and multi-leg options are not eligible alternatives in this mode; using them would override the allocation mandate, and no fresh contract-specific quote or liquidity evidence was supplied.

This remains lower-conviction exposure even though quality 84 and the current 24.86% expected return clear their numerical conviction thresholds. The assessment and accepted relationship carry only medium confidence rather than the required high confidence; the assessment also records a margin-of-safety soft gap at its older USD 76.95 reference mark. The current lower mark clears the allocation margin frontier, but it does not erase the evidence uncertainty. The bear case remains a 22.62% loss, autonomy can disintermediate the marketplace, and insurance, regulation, incentives, stock compensation and partner bargaining can absorb operating progress. The plan also records insufficient diversification, so the 5% ceiling must not be treated as a conviction target.

## Entry, exit and risk controls

- **Entry:** open only while allocation plan `allocation_plan_4e0ef8323f8d383f6b85`, allocation intent `allocation_intent_ae3d5bc9b6efe4a816f1`, assessment `assessment_7fe1690682aa6c66e233` and the accepted relationship remain current; require fresh UBER and USD/EUR inputs and a positive deterministic whole-share delta. The latest observed UBER mark was USD 71.08000183105469 and USD/EUR was 0.8607000112533569, both retrieved at 2026-09-10T18:10:21Z. The strategy does not choose or enlarge the persisted five-share target.
- **Exit:** reduce or close when a current deterministic allocation plan says reduce or close, when the canonical full-baseline gates cease to clear, or when a hard blocker appears. Review no later than 2026-09-27 and after material results, autonomy, insurance or regulatory evidence.
- **Risk budget:** 5% maximum position ceiling for the full baseline tier, not the current rounded target weight.
- **Invalidation:** do not increase exposure if autonomous fleets bypass Uber, trip or bookings growth stops producing free cash flow, insurance or regulation structurally compresses marketplace economics, incentives or dilution absorb value, the assessment or relationship is superseded, or market/FX inputs become stale.

## Evidence and links

Primary evidence is the [Uber Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1543151/000154315126000032/uber-20260630.htm) (`source_uber_q2_2026_10q`, hash `5aa56769ca3e3d8735d1122e85269a5b9cd68fcb4bd2fa58fa6b19b65b019ffa`). The strategy also depends on [[ideas/idea_mobility_platform_autonomy|Mobility-platform network economics and autonomy]], [[relationships/relationship_d403f81ae5b27c9643dd|the accepted Uber relationship]], and the current deterministic allocation target. The 2026-09-09 technical projection showed RSI 38.91, negative MACD momentum and an active lower-Bollinger-band condition; this is adverse timing context, not an allocation or order input.

[[research-catalog|Research catalog]] · [[index|Today's decision]] · [[log|Research log]]
