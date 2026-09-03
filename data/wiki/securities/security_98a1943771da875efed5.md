---
title: "Nomad Foods Limited ordinary shares"
type: security
status: watching
tags: [security, research, risk]
created: "2026-08-28"
updated: "2026-08-28"
provenance: "source_nomd_q2_2026_results"
security_id: security_98a1943771da875efed5
issuer_id: issuer_d41b84ca1e93a852d33c
ticker: NOMD
venue_mic: XNYS
provider_symbol: NOMD
currency: USD
confidence: medium
next_review: "2026-09-27"
---

# Nomad Foods Limited ordinary shares

## Visual evidence

<!-- papertrader:technical-chart:start -->
This deterministic monitoring chart is derived from the repository-local market cache. Its source CSV remains downloadable and does not feed research scoring or trading state.

```echart
{
  "schema_version": 2,
  "chart_id": "market-technicals",
  "kind": "technical",
  "title": "One-year price, volume, and technical indicators",
  "description": "Adjusted daily OHLC with Bollinger bands and moving averages, followed by volume, RSI, and MACD panels from the deterministic PaperTrader market cache.",
  "security_id": "security_98a1943771da875efed5",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_98a1943771da875efed5.csv",
  "sources": [
    {
      "label": "Canonical PaperTrader price cache and deterministic TA-Lib projection"
    }
  ],
  "notes": [
    "Adjusted OHLC aligns price history with indicators calculated from adjusted close.",
    "Technical indicators are research alerts, not trade signals."
  ]
}
```
<!-- papertrader:technical-chart:end -->

## Decision

**Buy / Initiate research rating; allocation ineligible; no strategy.** Q2 revenue fell 3.1%,
organic revenue 2.9% and volume 5.9%, partly offset by 3.0% price/mix. USD9/USD15/USD20 scenarios at
USD11.99 imply USD14.20 weighted value. The value is conditional on a turnaround; volume, leverage,
execution, downside and the pending relationship prevent allocation.

## Thesis, evidence and valuation

`security_98a1943771da875efed5` is NOMD ordinary shares at XNYS in USD. Branded frozen food may
support recurring demand and pricing, while restructuring and working capital can restore cash
conversion. Current volume is clear contrary evidence. Catalysts are stabilization, margin delivery,
deleveraging and covered dividends. Invalidate if volume remains weak, brand pricing fails,
restructuring misses or cash returns raise leverage.

The `mature_compounder` free-cash-flow-yield cases are **USD9 / USD15 / USD20**, weighted
30%/50%/20%, for **USD14.20** weighted value.

## Idea exposure map

- [[ideas/idea_defensive_consumer_cash_return|Defensive consumer cash-return resilience]] —
  **candidate**, positive but sensitive: brands and restructuring can preserve cash only if volume
  stabilizes and leverage falls. The existing relationship review
  `relationship_b2e1d6f8c3905a7421bb` remains queued.
- Rejected: AI, crypto, commodity and mobility ideas lack direct material transmission.

## Changes since prior review

First completed review: corrected identity, issuer evidence, scenarios, candidate edge, Buy /
Initiate economics and allocation ineligibility are newly established.

## Sources and review

- [Nomad Foods Q2 2026 results](https://www.nomadfoods.com/news/nomad-foods-reports-second-quarter-2026-financial-results/) (`source_nomd_q2_2026_results`).
- Market state: NOMD USD11.99 and USD/EUR 0.8632000089, retrieved 2026-08-28T19:01:02Z.

Review by **2026-09-27** or after results, restructuring, leverage or dividend evidence.

[[security-catalog|Tracked securities]] · [[research-catalog|Research catalog]] · [[index|Today's decision]]
