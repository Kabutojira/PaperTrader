---
title: Samsung Electronics preferred GDR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-06"
updated: "2026-08-06"
provenance: "source_samsung_preferred_gdr_identity; source_samsung_preferred_q2_2026_results"
security_id: security_d08d763780400dfbffce
issuer_id: issuer_adf6eb6a528f8576f0ed
confidence: medium
next_review: "2026-08-20"
---

# Samsung Electronics preferred GDR

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
  "security_id": "security_d08d763780400dfbffce",
  "currency": "EUR",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_d08d763780400dfbffce.csv",
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

- Immutable security: `security_d08d763780400dfbffce`
- Issuer: `issuer_adf6eb6a528f8576f0ed`
- Instrument: preferred global depositary receipt, Vienna (`XWBO`), EUR
- Provider identity: `SSUN.VI` / `XWBO` / `EUR` / equity
- Underlying issuer identity: Samsung preferred shares, KRX `005935`, ISIN `KR7005931001`
- Issuer-listed preferred GDR identity: LSE `SMSEL`, ISIN `US7960502018`

This is a distinct instrument from the [[securities/security_567d0d575bbd30aaa91d|Samsung common
GDR]]. The issuer reported 815,974,664 preferred shares outstanding at the end of Q1 2026. The
maintained identity is the sparse EUR-traded Vienna provider line and must not be substituted with
the common GDR, Korean preferred share, or London preferred GDR when measuring price or liquidity.

Primary identity evidence: [Samsung listing information](https://www.samsung.com/global/ir/stock-information/listing-Info/)
(`source_samsung_preferred_gdr_identity`).

## Business economics

Samsung combines memory semiconductors, foundry and logic chips, smartphones, displays, appliances,
and Harman. Detailed Q2 2026 results reported KRW 171.5 trillion revenue, KRW 89.5 trillion operating
profit, KRW 71.6 trillion net profit, and KRW 10,899 preferred-share EPS. Device Solutions generated
KRW 127.5 trillion sales and KRW 89.2 trillion operating profit as memory sales reached KRW 120.8
trillion. Cash rose to KRW 190.0 trillion, debt fell to KRW 22.4 trillion, and quarterly operating
cash flow reached KRW 105.1 trillion. Device eXperience nevertheless posted a KRW 0.8 trillion
operating loss as component costs rose.

Primary operating evidence: [Samsung Q2 2026 earnings results](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2026_2Q_conference_eng.pdf)
(`source_samsung_preferred_q2_2026_results`).

## Thesis and contrary evidence

The positive thesis is preferred-share participation in Samsung's AI-led server-memory earnings,
broad device franchises, technology depth, and net financial strength. The preferred instrument
also has a distinct distribution and market-price relationship to common equity. Contrary evidence
is that exceptional memory profitability may normalize, foundry and System LSI execution remains
uneven, Device eXperience was loss-making, and export restrictions, capital intensity, customer
concentration, currency translation, depositary terms, and cross-listing basis can separate the GDR
price from issuer fundamentals.

## 2026-08-04 price-action review

The canonical [[inbox/market-security_d08d763780400dfbffce-macd_cross_above_signal-5f77e49fc4fd|alert]]
period runs from 7 July through 4 August. The adjusted close moved from EUR 2,800 to EUR 2,790, a
**0.36% decline**, while MACD crossed above its signal with strength `0.2143953602`. Only five units
traded on 4 August. The 5 August close was EUR 2,785 on one unit; MACD remained above its signal,
but no new trigger was recorded.

No contemporaneous primary issuer evidence identifies a fundamental event explaining this nearly
flat period. Detailed Q2 results were released on 30 July and strengthened the operating thesis, but
the negligible Vienna turnover and discontinuous local prices prevent attributing the crossover to
fundamentals. The alert is **technical noise with mildly constructive momentum**, not an opportunity,
impairment signal, or paper-trade trigger.

## Valuation

A supportable EUR intrinsic range is unavailable. The repository has a fresh identity-matched EUR
mark and current issuer earnings, but the retained primary evidence does not establish a complete
Vienna-GDR conversion and same-timestamp parity bridge among the Korean preferred share, London GDR,
and Vienna line. It also lacks a fresh KRW/EUR translation series and normalized through-cycle
preferred-share earnings suitable for a downside-aware multiple. Applying a multiple to an
exceptional memory quarter or inferring value from the common GDR would invent precision.

The `mature_compounder` template and `earnings_multiple` method are selected because the issuer is a
profitable diversified technology franchise, but valuation is recorded as unsupported with no
bear, base, or bull values. `valuation_unsupported` and `liquidity_insufficient` are hard blockers.

## Catalysts, risks, and invalidation

Catalysts are sustained HBM4 and server-memory shipments, durable AI-led DRAM and SSD pricing,
advanced-node foundry wins, persistent cash conversion, and primary evidence that closes the
preferred-GDR parity and normalized-earnings gaps. Risks include memory-price normalization, weak
non-memory segment profitability, foundry execution, export restrictions, capital intensity,
currency and depositary effects, preferred/common basis changes, and negligible Vienna turnover.
Invalidate the positive operating thesis if server-memory demand or margins reverse structurally,
technology execution slips, net financial strength deteriorates materially, or cash conversion
fails as memory conditions normalize.

## Changes since prior review

- **Initial review:** the security-context receipt found no prior assessment, research page, linked
  idea, accepted relationship, strategy, or retained source for this immutable security.
- **Facts and evidence established:** issuer identity evidence distinguishes the preferred GDR from
  the common GDR; Q2 evidence establishes record memory-led earnings, cash flow, and net strength,
  alongside a Device eXperience loss.
- **Alert evidence established:** the 4 August bullish MACD crossover followed a 0.36% period decline
  and five-unit session; the next session traded one unit. It is noise with mildly constructive
  momentum rather than a fundamental signal.
- **Valuation and assumptions established:** no prior scenario existed. Preferred-GDR conversion,
  cross-venue parity, KRW/EUR translation, normalized-cycle earnings, and routine local liquidity
  remain unresolved, so no scenario values are invented.
- **Rating and action established:** medium-confidence research is unsupported and allocation is
  ineligible. The action is watch; no strategy, signal, order, or idea refresh is justified.

## Disposition

Status: **watching**, **medium** confidence, and **ineligible** for allocation. Strong issuer
fundamentals do not cure unsupported instrument-level valuation or the Vienna line's negligible
turnover. Review by **2026-08-20**, or earlier if primary parity, conversion, normalized-cycle, FX,
or sustained venue-liquidity evidence becomes available. See the [[research-catalog|research
catalog]] for the wider maintained universe.
