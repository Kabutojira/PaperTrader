---
title: "Uber bounded baseline allocation"
type: strategy
status: ready
tags: [strategy, research, risk]
created: "2026-09-03"
updated: "2026-09-03"
provenance: "source_uber_q2_2026_10q"
strategy_id: strategy_e4ada1a4934691d1f7ee
idea_id: idea_mobility_platform_autonomy
security_id: security_e4822686f60a96824b6e
relationship_id: relationship_d403f81ae5b27c9643dd
confidence: medium
next_review: "2026-09-27"
sleeve: baseline
allocation_plan_id: allocation_plan_0f41c211cdfa8a9b5dbc
allocation_intent_id: allocation_intent_5988db00b0dab41c4d78
assessment_id: assessment_7fe1690682aa6c66e233
---

# Uber bounded baseline allocation

## Visual evidence

The current allocation plan's scenario returns show why the position belongs only in the starter sleeve: base and probability-weighted returns clear baseline hurdles, while the bear case remains material.

```echart
{
  "schema_version": 1,
  "chart_id": "uber-baseline-scenario-returns",
  "kind": "series",
  "title": "Uber current-plan scenario returns",
  "description": "Bear, base and bull twelve-month returns at the allocation plan's USD 76.45 valuation mark show the asymmetric but still material downside supporting a starter-sized baseline position.",
  "as_of": "2026-09-03T21:08:37Z",
  "sources": [
    {
      "label": "Uber Q2 2026 Form 10-Q",
      "url": "https://www.sec.gov/Archives/edgar/data/1543151/000154315126000032/uber-20260630.htm",
      "observed_at": "2026-08-28T19:27:50Z"
    },
    {
      "label": "PaperTrader allocation plan allocation_plan_0f41c211cdfa8a9b5dbc",
      "observed_at": "2026-09-03T21:08:37Z"
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
      "values": ["-28.05755108501072142780174037", "17.7240073154370012999607885", "56.9653430872493350666143847"]
    }
  ],
  "notes": [
    "Scenario values are USD 55, USD 90 and USD 120 with probabilities of 25%, 50% and 25% over twelve months.",
    "The chart uses the immutable current allocation plan mark; the fresher market mark is considered separately for signal freshness and does not resize the deterministic target."
  ]
}
```

## Decision

**Ready — long common equity in the baseline starter sleeve.** The current deterministic plan assigns a 1.97% target, capped at 2%, and persists a three-share target. That quantity is allocator-owned, is not an agent sizing decision, and is not yet an order or fill. The accepted [[relationships/relationship_d403f81ae5b27c9643dd|mobility-platform relationship]] and [[securities/security_e4822686f60a96824b6e|Uber assessment]] support a bounded position rather than conviction exposure.

The USD 76.45 plan mark implies bear/base/bull returns of -28.06%/17.72%/56.97%, a 16.09% probability-weighted return and a 12.07% confidence-adjusted return. The 15.06% margin of safety, 0.63 bear/base payoff ratio and 0.43 expected/bear payoff ratio clear the starter frontier encoded by the allocator. Cash is therefore less attractive for this bounded tranche, but it remains preferable for the rest of the portfolio allocation.

## Structure review

Baseline mode permits only long equity. Common stock is liquid, directly expresses the accepted network-economics mechanism, has no option expiry or premium loss, and lets deterministic order code derive the exact current-plan delta. Short equity, calls, puts and multi-leg options are not eligible alternatives in this mode; using them would override the allocation mandate, and no fresh contract-specific quote or liquidity evidence was supplied.

This is lower-conviction exposure. Quality is 84, but medium confidence and a 16.09% expected return do not meet the conviction requirement for high confidence and at least 20% expected return. The bear case remains a 28.06% loss, autonomy can disintermediate the marketplace, and insurance, regulation, incentives, stock compensation and partner bargaining can absorb operating progress. The plan also records insufficient diversification, so the 2% risk ceiling must not be treated as a conviction target.

## Entry, exit and risk controls

- **Entry:** open only while allocation plan `allocation_plan_0f41c211cdfa8a9b5dbc`, allocation intent `allocation_intent_5988db00b0dab41c4d78`, assessment `assessment_7fe1690682aa6c66e233` and the accepted relationship remain current; require fresh UBER and USD/EUR inputs and a positive deterministic whole-share delta. The latest observed UBER mark was USD 75.96 and USD/EUR was 0.8598999977111816, both retrieved at 2026-09-03T21:34:54Z. The strategy does not choose or enlarge the persisted three-share target.
- **Exit:** reduce or close when a current deterministic allocation plan says reduce or close, when the canonical starter gates cease to clear, or when a hard blocker appears. Review no later than 2026-09-27 and after material results, autonomy, insurance or regulatory evidence.
- **Risk budget:** 2% maximum position ceiling for the starter tier, not the current rounded target weight.
- **Invalidation:** do not increase exposure if autonomous fleets bypass Uber, trip or bookings growth stops producing free cash flow, insurance or regulation structurally compresses marketplace economics, incentives or dilution absorb value, the assessment or relationship is superseded, or market/FX inputs become stale.

## Evidence and links

Primary evidence is the [Uber Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1543151/000154315126000032/uber-20260630.htm) (`source_uber_q2_2026_10q`, hash `5aa56769ca3e3d8735d1122e85269a5b9cd68fcb4bd2fa58fa6b19b65b019ffa`). The strategy also depends on [[ideas/idea_mobility_platform_autonomy|Mobility-platform network economics and autonomy]], [[relationships/relationship_d403f81ae5b27c9643dd|the accepted Uber relationship]], and the current deterministic allocation target.

[[research-catalog|Research catalog]] · [[index|Today's decision]] · [[log|Research log]]
