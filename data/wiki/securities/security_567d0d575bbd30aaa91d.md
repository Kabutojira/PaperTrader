---
title: Samsung Electronics common GDR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-29"
updated: "2026-08-10"
provenance: "source_samsung_common_gdr_identity; source_samsung_q1_2026_results; source_samsung_q2_2026_guidance; source_samsung_q2_2026_results"
security_id: security_567d0d575bbd30aaa91d
issuer_id: issuer_adf6eb6a528f8576f0ed
confidence: medium
next_review: "2026-09-02"
---

# Samsung Electronics common GDR

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
  "security_id": "security_567d0d575bbd30aaa91d",
  "currency": "EUR",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_567d0d575bbd30aaa91d.csv",
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

- Immutable security: `security_567d0d575bbd30aaa91d`
- Issuer: `issuer_adf6eb6a528f8576f0ed`
- Instrument: common global depositary receipt, Vienna MTF (`XWBO`), EUR
- Provider identity: `SSU.VI` / `XWBO` / `EUR` / equity
- Underlying: Samsung common shares; one GDR represents 25 Korean common shares

Samsung identifies the common GDR as London symbol `SMSN`, ISIN `US7960508882`; Vienna identifies
`SSU` with the same ISIN. This review concerns the EUR-traded Vienna line and does not substitute
the preferred GDR or a Korean ordinary-share ticker.

## Business economics

Samsung combines memory semiconductors, foundry and logic chips, smartphones, displays, appliances,
and Harman. Memory drove the latest step-change: first-quarter Device Solutions sales were KRW 81.7
trillion and operating profit KRW 53.7 trillion as server DRAM, SSD, HBM4, and AI-infrastructure
demand strengthened. Diversified device franchises and a large balance sheet cushion the cycle,
but memory pricing, leading-edge execution, foundry utilization, export policy, capital intensity,
and mobile demand remain material swing factors.

Detailed second-quarter results confirmed KRW 171.5 trillion of sales, KRW 89.5 trillion of
operating profit, KRW 71.6 trillion of net profit, and common-share EPS of KRW 10,849. Device
Solutions generated KRW 127.5 trillion of sales and KRW 89.2 trillion of operating profit as memory
sales reached KRW 120.8 trillion. Cash rose to KRW 190.0 trillion while debt fell to KRW 22.4
trillion, and quarterly operating cash flow reached KRW 105.1 trillion. The concentration is also a
risk: Device eXperience produced a KRW 0.8 trillion operating loss as component costs rose.

Primary evidence: [Samsung's Q1 earnings release](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2026_1Q_conference_eng.pdf),
[Q2 pre-earnings guidance](https://www.samsung.com/global/ir/reports-disclosures/public-disclosure-view.84695/),
[detailed Q2 results](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2026_2Q_conference_eng.pdf),
and [issuer listing information](https://www.samsung.com/global/ir/stock-information/listing-Info/).

## Thesis and contrary evidence

The positive thesis is operating leverage to AI-led server memory demand, broad device distribution,
technology depth, and net liquidity. Contrary evidence is that exceptional current memory profit may
normalize, foundry and System LSI economics lag the memory franchise, geopolitical and export rules
can constrain the supply chain, and a GDR investor also bears currency, depositary, venue-liquidity,
and cross-listing-basis risk.

## 2026-07-30 price-action review

The canonical alert period runs from July 2 through July 30. SSU.VI closed at EUR 3,550, down
**11.47%** over that period but up **10.25%** from the prior session. Volume rose to 56 units and
entered the configured anomaly state at 1.047 times its threshold. The results-day volume was large
only relative to this exceptionally sparse Vienna line; it does not establish investable liquidity.
On July 31 the close rose to EUR 3,650 on only eight units, while the current indicator cache showed
no active trigger.

Samsung released its detailed record Q2 results on July 30, making the announcement the most direct
primary-evidence explanation for that session's volume and rebound. The release strengthened rather
than impaired the memory thesis, but it did not explain the full negative period return. Sparse
local turnover, currency translation, and cross-venue basis remain plausible contributors. The
alert is therefore **a results-driven volume event within a liquidity and valuation risk**, not a
confirmed fundamental entry opportunity.

## 2026-08-10 quick check

The payload-bound August 4 bullish MACD crossover followed a **15.53%** decline from the July 7
adjusted close to EUR 3,800. By August 7 the canonical mark was EUR 3,580: MACD remained above its
signal, but RSI was neutral, volume was not anomalous, and no configured threshold trigger remained
active. This is early technical stabilization, not an independently verified operating catalyst.

A fresh retrieval of Samsung's detailed Q2 results PDF was byte-for-byte unchanged. Record
memory-led earnings, cash generation, net-liquidity strength, cycle risks, and Device eXperience
weakness therefore remain the latest operating evidence. The move did not establish same-timestamp
common-share/GDR parity, KRW/EUR translation, normalized through-cycle earnings, a valuation range,
or routine Vienna liquidity. No buy zone is supportable, no catalyst or invalidation fired, and no
full review is warranted.

## Valuation

A supportable EUR intrinsic range remains unavailable. The GDR represents 25 KRW-denominated common
shares, while the canonical repository still has neither a fresh KRW/EUR series nor a same-timestamp
LSE GDR reference. Detailed Q2 evidence removes the prior results-timing gap, but applying an
earnings multiple to an extraordinary memory quarter without a normalized cycle, cross-venue basis,
and currency bridge would invent precision. The assessment therefore records
`valuation_unsupported` and contains no scenario values.

## Catalysts, risks, and invalidation

Catalysts are sustained HBM4/server-memory shipments, continued AI-led DRAM and SSD demand,
advanced-node foundry wins, and evidence that cash earnings persist through the cycle. Risks include
memory-price normalization, the loss-making Device eXperience quarter, foundry execution, export
restrictions, customer concentration, capital intensity, currency and depositary effects, and the
Vienna line's negligible turnover. Invalidate the positive case if server-memory demand or margins
reverse structurally, technology execution slips, net liquidity deteriorates materially, or cash
conversion fails to persist as memory conditions normalize.

## Changes since prior review

- **Facts and evidence changed:** detailed Q2 results replaced preliminary guidance as the newest
  primary operating evidence. Revenue, operating profit, EPS, Device Solutions profit, cash, and
  operating cash flow all strengthened; Device eXperience's operating loss adds contrary evidence.
- **Alert evidence changed:** the prior lower-Bollinger review ended July 29. The new July 30 event
  is a results-day volume anomaly with a EUR 3,550 close, 56-unit volume, a 10.25% daily rebound,
  and an 11.47% decline over the canonical July 2-July 30 period. By July 31 no trigger remained.
- **Assumptions and valuation changed:** the pre-results timing gap is resolved, but cyclical
  normalization, fresh KRW/EUR translation, and same-timestamp cross-venue parity remain absent.
  Bear, base, and bull values remain unsupported rather than unchanged numerical estimates.
- **Thesis, catalysts, and risks changed:** record AI-server-memory economics and stronger net cash
  reinforce the thesis; weak Device eXperience profitability and dependence on peak memory
  conditions increase concentration and normalization risk. Detailed Q2 results move from catalyst
  to evidence; sustained HBM4 demand and cash conversion remain catalysts.
- **Blockers and gaps:** `valuation_unsupported` and `liquidity_insufficient` remain hard blockers.
  The results-timing gap is resolved; currency, parity, normalized-cycle, and local-liquidity gaps
  remain unresolved.
- **Rating and action:** research becomes current under schema version 2, but allocation remains
  ineligible and the action remains watch. No strategy is justified.
- **Unchanged conclusion:** Samsung's operating evidence is strong, yet the Vienna GDR cannot be
  valued or entered responsibly from the available instrument-specific evidence.

## Disposition

Status: **watching**, **medium** confidence, and **ineligible** for allocation. Record Q2 earnings,
cash flow, and net liquidity do not cure the missing valuation bridge or the instrument's
insufficient local liquidity. The August 10 quick check reaffirms this `Unrated / Watch` conclusion
at the fresh EUR 3,580 mark. No conviction strategy or paper signal is justified. Review by
**2026-09-02**, or earlier if fresh cross-venue, KRW/EUR, normalized-cycle, or venue-liquidity
evidence becomes available.
