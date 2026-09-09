---
title: "NVIDIA bounded baseline allocation"
type: strategy
status: ready
tags: [strategy, research, risk]
created: "2026-09-05"
updated: "2026-09-09"
provenance: "source_nvda_q2_fy2027_10q; source_nvda_q2_fy2027_release; source_nvda_q2_fy2027_cfo; source_nvda_huggingface_20260903_8k"
strategy_id: strategy_7cf884a5530d05afdb99
idea_id: idea_ai_compute_networking_hyperscaler_monetization
security_id: security_33d9c44facc75c726c7d
relationship_id: relationship_ai_compute_nvda
confidence: medium
next_review: "2026-09-18"
sleeve: baseline
allocation_plan_id: allocation_plan_6f7a4f4479899fcd0d91
allocation_intent_id: allocation_intent_b8eab1837513d5191d02
assessment_id: assessment_82fd625a8d93be4bd8f5
---

# NVIDIA bounded baseline allocation

## Visual evidence

The current allocation plan's scenario returns show why long equity is preferable to cash for a bounded baseline position while retaining explicit downside. The chart uses the allocator's fresh valuation mark and does not determine position size.

```echart
{
  "schema_version": 1,
  "chart_id": "nvda-baseline-scenario-returns",
  "kind": "series",
  "title": "NVIDIA current-plan scenario returns",
  "description": "Bear, base and bull twelve-month returns at the allocation plan's USD 225.73 valuation mark show the upside and downside supporting a bounded full-baseline position.",
  "as_of": "2026-09-09T18:24:19Z",
  "sources": [
    {
      "label": "NVIDIA fiscal 2027 second-quarter Form 10-Q",
      "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm",
      "observed_at": "2026-09-04T06:15:57Z"
    },
    {
      "label": "PaperTrader allocation plan allocation_plan_6f7a4f4479899fcd0d91",
      "observed_at": "2026-09-09T18:24:19Z"
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
      "values": ["-12.28458612164674774643077227", "37.5537172183266910340062889", "98.4671990782942273212071415"]
    }
  ],
  "notes": [
    "Scenario fair values are USD 198, USD 310.50 and USD 448 with probabilities of 30%, 50% and 20% over twelve months.",
    "The chart uses the immutable current allocation plan mark; the allocation target is canonical state, not an order, fill or chart-derived input."
  ]
}
```

## Decision

**Ready — long common equity in the full baseline sleeve.** Current plan `allocation_plan_6f7a4f4479899fcd0d91` assigns a 1.94% target, capped at 5%, and persists a one-share target. That quantity is allocator-owned, is not an agent sizing decision, and is not yet an order or fill. The accepted [[relationships/relationship_ai_compute_nvda|AI-compute relationship]] and [[securities/security_33d9c44facc75c726c7d|NVIDIA assessment]] support bounded exposure rather than conviction treatment.

At the USD 225.73 plan mark, bear/base/bull returns are -12.28%/37.55%/98.47%, probability-weighted expected return is 34.78%, and medium-confidence adjusted expected return is 26.09%. The 27.30% margin of safety, 3.06 bear/base payoff ratio and 2.12 expected/bear payoff ratio clear the full-baseline frontier encoded by the allocator. Cash is therefore less attractive for this bounded tranche, but the portfolio's remaining allocation stays under deterministic allocation control.

This remains lower-conviction exposure despite quality score 92 and strong expected return because confidence is medium rather than the configured high-conviction minimum. Customer concentration, USD 279 billion of supply commitments, USD 105 billion of capped guarantees, longer receivable terms, export restrictions, rapid product transitions and customer-designed silicon can impair the path from AI demand to shareholder value. The plan also records insufficient diversification, so the 5% ceiling must not be treated as a conviction target.

## Structure review

Baseline-allocation mode permits only long equity. NVIDIA common stock is liquid, directly expresses the accepted accelerated-compute, networking and software mechanism, has no option expiry or premium loss, and lets deterministic order code derive the exact current-plan delta. Short equity, calls, puts and multi-leg options are ineligible in this mode; using them would override the allocation mandate, and no complete fresh contract quote or contract-level liquidity evidence was supplied.

## Entry, exit and risk controls

- **Entry:** open only while allocation plan `allocation_plan_6f7a4f4479899fcd0d91`, allocation intent `allocation_intent_b8eab1837513d5191d02`, assessment `assessment_82fd625a8d93be4bd8f5` and relationship `relationship_ai_compute_nvda` remain current; require fresh NVDA and USD/EUR inputs and a positive deterministic whole-share delta. The latest observed NVDA mark was USD 225.73 and USD/EUR was 0.8590999841690063, both retrieved at 2026-09-09T18:24:19Z. The strategy does not choose or enlarge the persisted one-share target.
- **Exit:** reduce or close when a current deterministic allocation plan directs it, when the full-baseline eligibility frontier no longer clears, or when a hard blocker appears. Review no later than 2026-09-18 and after material earnings, Rubin, export-control, customer-credit, guarantee or concentration evidence.
- **Risk budget:** 5% maximum-position ceiling for the full baseline tier, not the current rounded target weight.
- **Invalidation:** do not increase exposure if normalized earnings fall below the bear path, gross margin remains below 70%, guarantees or receivables produce material losses, Rubin misses its cycle, export controls intensify, CUDA or networking attachment weakens, the assessment or relationship is superseded, or market/FX inputs become stale.

## Evidence and links

Primary evidence is NVIDIA's [fiscal 2027 second-quarter Form 10-Q](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm) (`source_nvda_q2_fy2027_10q`, hash `e2634e509c241c5f45e3f6c115dc38a85645e5fdbee760b4a04f5e9035f6f7a9`), supplemented by the [results release](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27pr.htm), [CFO commentary](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27cfocommentary.htm), and [Hugging Face acquisition Form 8-K](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000080/nvda-20260902.htm). The strategy also depends on [[ideas/idea_ai_compute_networking_hyperscaler_monetization|AI compute, networking, and hyperscaler monetization]], [[relationships/relationship_ai_compute_nvda|the accepted NVIDIA relationship]], and the current deterministic allocation target.

[[research-catalog|Research catalog]] · [[index|Today's decision]] · [[log|Research log]]
