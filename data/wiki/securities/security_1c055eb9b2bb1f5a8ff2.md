---
title: Rio Tinto plc sponsored ADR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-05"
provenance: "source_rio_h1_2026_results"
security_id: security_1c055eb9b2bb1f5a8ff2
issuer_id: issuer_3f384e36fe805b0fcbea
confidence: medium
next_review: "2026-08-19"
---

# Rio Tinto plc sponsored ADR

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
  "security_id": "security_1c055eb9b2bb1f5a8ff2",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_1c055eb9b2bb1f5a8ff2.csv",
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

## Identity

- Immutable security: `security_1c055eb9b2bb1f5a8ff2`
- Issuer: `issuer_3f384e36fe805b0fcbea`
- Instrument: sponsored ADR, New York Stock Exchange (`XNYS`), USD
- Provider identity: `RIO` / `XNYS` / `USD` / equity

This review links the verified depositary instrument to [[ideas/idea_critical_minerals_copper]] and
contrasts its diversified commodity exposure with [[securities/security_2dbe878dfc899d7ee867|Freeport-McMoRan]].

## Economics and thesis

Rio Tinto is a diversified miner whose iron ore, aluminium, copper, and emerging lithium cash flows
make the ADR less sensitive to copper than a pure producer. H1 2026 copper-equivalent output rose 3%,
and copper EBITDA rose 84% to USD 5.7 billion as Oyu Tolgoi ramped and copper, gold, and silver prices
strengthened. Iron ore still produced USD 6.8 billion of EBITDA, so China, steel, and bulk-commodity
economics remain at least as important as the structural-copper thesis.

The Oyu Tolgoi underground ramp can increase low-cost copper exposure, while Resolution and Winu
offer longer-dated options. Simandou, Pilbara renewal, lithium integration, national partnerships,
capex, and commodity diversification can either fund copper growth or dilute its thesis purity.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| H1 revenue was USD 31.0 billion, underlying EBITDA USD 14.8 billion, and underlying earnings USD 6.9 billion. | Earnings strengthened, but favourable commodity prices contributed materially. |
| Free cash flow was USD 3.8 billion, up 75%; operating cash flow was USD 9.2 billion. | Cash conversion improved while group capital investment remained high at USD 5.0 billion. |
| Copper EBITDA rose 84% to USD 5.7 billion; Oyu Tolgoi production rose 31%. | The copper-beneficiary mechanism is operating, though partly price-driven. |
| Iron ore EBITDA was USD 6.8 billion and free cash flow USD 3.0 billion. | Iron ore remains the largest single cash engine and key China sensitivity. |
| Net debt was USD 14.1 billion versus USD 14.4 billion at year-end. | Leverage is manageable but limits downside protection during a commodity reversal. |
| 1,626.8 million combined DLC shares were public at 30 June; ADR holders receive the declared USD dividend rate. | Combined per-share cash flow maps to the sponsored ADR economics. |

Primary evidence: [Rio Tinto 2026 half-year results](https://cdn-rio.dataweavers.io/-/media/content/documents/invest/financial-news-and-performance/results/2026/2026-half-year-results.pdf),
published 29 July and checked 5 August 2026 as `source_rio_h1_2026_results`, supplemented by
[Q2 production results](https://www.riotinto.com/en/news/releases/2026/rio-tinto-releases-second-quarter-2026-production-results)
as `source_rio_q2_2026_production`.

## Valuation, catalysts, and risks

The cyclical-commodity template uses `mid_cycle_cash_flow`, not peak-period earnings. H1 free cash
flow of USD 3.834 billion annualises to USD 4.71 per combined share before normalization; net debt is
USD 8.64 per combined share and is reflected by conservative equity cash-flow multiples rather than
adding an unlevered value. Against the 4 August close of USD 99.01, the 12-month scenarios are:

| Scenario | Probability | Fair value | Assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 68.00 | USD 3.40 normalized FCF/share at 20x as commodity prices weaken, project spend stays elevated, and debt falls slowly. |
| Base | 50% | USD 93.50 | USD 4.25 normalized FCF/share at 22x; Oyu Tolgoi ramps, productivity offsets inflation, and strong H1 pricing partly normalizes. |
| Bull | 25% | USD 126.50 | USD 5.50 normalized FCF/share at 23x as copper and aluminium stay strong, Simandou ramps, and productivity improves conversion. |

Probability-weighted fair value is USD 95.38, below the mark. The base case is 5.6% below the mark,
the bear case is 31.3% below, and the bull case is 27.8% above. Cyclical normalization remains a soft
gap, but current filing, realized-price, balance-sheet, share-count, and production evidence now make
the valuation supportable.

Catalysts are Oyu Tolgoi ramp and cost delivery, productivity savings, and de-risking of Winu,
Resolution, and Simandou. Invalidate if underground ramp slips, copper cost guidance reverses,
iron-ore demand weakens, large projects overrun, or capital allocation prevents higher copper
production from improving per-share cash flow.

## Disposition

Status: **watching**, confidence **medium**. The valuation blocker is resolved, but the assessment
remains economically ineligible: expected and base returns are below the cash hurdle and bear/base
payoff is adverse. The 4 August USD 99.01 close remained above its upper Bollinger band; the breakout
is therefore a timing risk rather than a buy signal. Review by **2026-08-19**, or sooner after a
material commodity-price, Oyu Tolgoi, Simandou, capex, or balance-sheet change. No strategy or signal
is justified.

## Changes since prior review

- **Facts and evidence:** the 29 July half-year filing replaces the prior scheduled-results gap with
  current net debt, combined share count, segment cash flow, realized prices, and maintained guidance.
- **Assumptions and valuation:** unsupported valuation is resolved. New bear/base/bull mid-cycle
  cash-flow values are USD 68.00/USD 93.50/USD 126.50 at 25%/50%/25%; there were no prior supported
  scenario outputs to revise. The weighted value is below the current mark, so no buy zone opens.
- **Thesis and catalysts:** stronger copper EBITDA and Oyu Tolgoi delivery upgrade evidence for the
  copper mechanism; diversification and iron-ore dependence remain unchanged constraints.
- **Risks, blockers, and gaps:** `valuation_unsupported` is resolved. Commodity normalization remains
  uncertain; leverage, project execution, China/iron-ore demand, and favourable H1 metals prices
  remain material risks. No thesis invalidation is verified.
- **Rating and action:** confidence stays medium and status stays watching, but the reason changes
  from incomplete decision support to a definitive preference for cash at USD 99.01. No strategy or
  signal is created because the full economic gate fails.
