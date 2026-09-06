---
title: Samsung Electronics preferred GDR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-06"
updated: "2026-09-06"
provenance: "source_samsung_preferred_gdr_identity; source_samsung_preferred_q2_2026_results"
security_id: security_d08d763780400dfbffce
issuer_id: issuer_adf6eb6a528f8576f0ed
confidence: medium
last_researched: "2026-09-06T14:35:49Z"
next_review: "2026-09-20"
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

```echart
{
  "schema_version": 1,
  "chart_id": "samsung-preferred-gdr-alert-window-20260904",
  "kind": "candlestick",
  "title": "Preferred GDR rose on extremely sparse Vienna turnover",
  "description": "The exact August 7 through September 4 alert window shows a 16.7% adjusted-close gain and the September 4 bullish MACD crossover, but only five sessions recorded any units traded.",
  "as_of": "2026-09-04",
  "sources": [
    {
      "label": "Canonical PaperTrader SSUN.VI adjusted-price cache",
      "observed_at": "2026-09-06T13:51:39Z"
    }
  ],
  "currency": "EUR",
  "rows": [
    {"at": "2026-08-07", "open": "2615", "close": "2605", "low": "2605", "high": "2670", "volume": "0"},
    {"at": "2026-08-10", "open": "2640", "close": "2630", "low": "2605", "high": "2645", "volume": "0"},
    {"at": "2026-08-11", "open": "2735", "close": "2790", "low": "2735", "high": "2790", "volume": "0"},
    {"at": "2026-08-12", "open": "2830", "close": "2945", "low": "2830", "high": "2945", "volume": "0"},
    {"at": "2026-08-13", "open": "2865", "close": "2990", "low": "2835", "high": "2990", "volume": "0"},
    {"at": "2026-08-14", "open": "2980", "close": "2990", "low": "2980", "high": "3000", "volume": "4"},
    {"at": "2026-08-17", "open": "3060", "close": "3130", "low": "3060", "high": "3130", "volume": "0"},
    {"at": "2026-08-18", "open": "2920", "close": "2775", "low": "2775", "high": "2920", "volume": "1"},
    {"at": "2026-08-19", "open": "2790", "close": "2800", "low": "2790", "high": "2820", "volume": "1"},
    {"at": "2026-08-20", "open": "2935", "close": "2915", "low": "2875", "high": "2935", "volume": "0"},
    {"at": "2026-08-21", "open": "3110", "close": "2900", "low": "2900", "high": "3110", "volume": "0"},
    {"at": "2026-08-24", "open": "2855", "close": "2835", "low": "2835", "high": "2900", "volume": "2"},
    {"at": "2026-08-25", "open": "2980", "close": "2990", "low": "2980", "high": "3015", "volume": "0"},
    {"at": "2026-08-26", "open": "3015", "close": "3010", "low": "2995", "high": "3015", "volume": "3"},
    {"at": "2026-08-27", "open": "3005", "close": "2950", "low": "2950", "high": "3020", "volume": "0"},
    {"at": "2026-08-28", "open": "2905", "close": "2970", "low": "2905", "high": "2970", "volume": "0"},
    {"at": "2026-08-31", "open": "2950", "close": "2900", "low": "2900", "high": "2950", "volume": "0"},
    {"at": "2026-09-01", "open": "2955", "close": "2930", "low": "2915", "high": "2955", "volume": "0"},
    {"at": "2026-09-02", "open": "2930", "close": "2955", "low": "2910", "high": "2955", "volume": "0"},
    {"at": "2026-09-03", "open": "2905", "close": "2925", "low": "2890", "high": "2925", "volume": "0"},
    {"at": "2026-09-04", "open": "3005", "close": "3040", "low": "3005", "high": "3050", "volume": "0"}
  ],
  "notes": [
    "Prices are adjusted daily OHLC for immutable security security_d08d763780400dfbffce; the provider reported zero volume in sixteen of twenty-one sessions and only eleven units across the full window.",
    "Sparse prints can move discontinuously and make indicator transitions unreliable for execution; this chart is evidence, not a trade input."
  ]
}
```

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

## 2026-09-04 price-action review

The canonical [[inbox/market-security_d08d763780400dfbffce-macd_cross_above_signal-f92ad63c5616|alert]]
period runs from 7 August through 4 September. The adjusted close rose from EUR 2,605 to EUR 3,040,
a **16.70% gain**. On 4 September MACD crossed above its signal with strength `0.60327972`; RSI was
57.80 and the close was above the 20-, 50- and 200-session averages. Yet the provider reported zero
volume on the crossover day, only eleven units across the 21-session window, and nonzero volume on
just five sessions.

No newer detailed issuer earnings release was found in the bounded primary-source check. The
unchanged Q2 results continue to support the operating thesis but do not explain the exact alert
window. The move is **constructive technical momentum but non-actionable market noise**: negligible
Vienna turnover prevents reliable price discovery, valuation remains unsupported, and the evidence
does not justify a strategy or paper order.

## Valuation

A supportable EUR intrinsic range is unavailable. The repository has a fresh identity-matched EUR
mark, a fresh KRW/EUR series, and current issuer earnings, but the retained primary evidence does not
establish a complete Vienna-GDR conversion and same-timestamp parity bridge among the Korean
preferred share, London GDR, and Vienna line. It also lacks normalized through-cycle preferred-share
earnings suitable for a downside-aware multiple. Applying a multiple to an exceptional memory
quarter or inferring value from the common GDR would invent precision.

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

## Idea exposure map

- **Candidate — [[ideas/idea_ai_compute_networking_hyperscaler_monetization|AI compute, networking
  and hyperscaler monetization]]:** positive, medium materiality. Samsung's record memory results
  provide a specific AI-server-memory transmission mechanism, but this immutable preferred GDR has
  no accepted canonical relationship and instrument liquidity remains separate. A dependent
  relationship review must test durable HBM demand, customer qualification and margin attribution;
  reversal of AI-memory demand or sustained qualification losses would invalidate the link.
- **Candidate — [[ideas/idea_terafab_ai_industrial_stack|Terafab AI industrial stack]]:** positive
  near-term and potentially negative long-term, low confidence. Samsung can bridge HBM, memory,
  foundry and packaging needs while internal Terafab capability matures, but no contract is
  disclosed and the accepted graph edge currently belongs only to the distinct common GDR. A
  dependent relationship review must decide whether a second instrument-level edge adds canonical
  information or should be rejected as redundant; competitive internal yield and qualification
  would invalidate the bridge benefit.
- **Rejected-no-link — all other maintained ideas:** the complete catalog was searched, but no
  current primary evidence established another security-specific causal mechanism with material
  exposure. Broad labels such as energy, defence, healthcare, fintech or Japan policy are not enough.

## Changes since prior review

- **Facts and evidence:** the issuer listing still verifies the preferred-share and London preferred-
  GDR identities; its page bytes changed without changing those material fields. The Q2 issuer PDF
  is byte-for-byte unchanged and remains the latest detailed operating baseline found.
- **Alert:** the prior 4 August crossover was nearly flat; the new 4 September crossover followed a
  16.70% gain and stronger trend readings. The conclusion remains non-actionable because the latest
  session had zero reported volume and the full window had only eleven units.
- **Assumptions and valuation:** current KRW/EUR data resolves the prior FX-series gap, but conversion,
  same-time cross-venue parity, normalized cycle earnings and routine Vienna liquidity remain open.
  The `mature_compounder` / `earnings_multiple` selection is unchanged and no bear, base or bull
  value is invented.
- **Thesis, catalysts and risks:** the AI-memory and net-cash thesis, normalization risk, foundry and
  Device eXperience execution risks, catalysts and invalidation are unchanged. The alert adds no
  primary evidence that upgrades or downgrades them.
- **Ideas, rating and action:** two causal candidates are now explicit for separate relationship
  review, but no canonical relationship is accepted. Medium-confidence research remains unsupported,
  allocation-ineligible and **watch**; no strategy, signal or order is justified.

## Disposition

Status: **watching**, **medium** confidence, and **ineligible** for allocation. Strong issuer
fundamentals do not cure unsupported instrument-level valuation or the Vienna line's negligible
turnover. Review by **2026-09-20**, or earlier if primary parity, conversion, normalized-cycle or
sustained venue-liquidity evidence becomes available. See the [[research-catalog|research
catalog]] for the wider maintained universe.
