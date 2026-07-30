---
title: "PayPal Holdings, Inc. common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-07-29"
updated: "2026-07-29"
provenance: "source_pypl_q2_2026_10q|source_pypl_q2_2026_results"
security_id: security_1e8fbdb0f45f2b413e00
issuer_id: issuer_5c3fe75eec62fcc8cb57
ticker: PYPL
venue_mic: XNAS
provider_symbol: PYPL
currency: USD
confidence: medium
next_review: "2026-08-28"
---

# PayPal Holdings, Inc. common stock

## Decision

**Baseline comparison; no conviction strategy.** PayPal's July 28 results provide a current,
primary explanation for the final-session gain that pushed RSI to an overbought reading. Payment
volume and free cash flow improved, management raised full-year non-GAAP EPS guidance, and the
shares remain highly liquid. Those positives are offset by lower operating income, contracting
margins, nearly flat active accounts, transformation risk, and a valuation range whose base upside
is small relative to downside. The alert is therefore post-results momentum and timing risk, not a
paper-trade signal.

## Immutable identity

- Security ID: `security_1e8fbdb0f45f2b413e00`
- Issuer ID: `issuer_5c3fe75eec62fcc8cb57`
- Instrument: PayPal Holdings, Inc. common stock
- Listing: Nasdaq Global Select Market (`XNAS`)
- Provider symbol: `PYPL`
- Currency: `USD`

The Q2 Form 10-Q confirms PayPal common stock and ticker `PYPL` on Nasdaq. No duplicate
issuer-instrument-venue-currency-provider identity exists in the canonical security table.

## Alert review

The canonical market record covers 2026-06-29 through 2026-07-28:

- Adjusted close rose from USD 44.38 to USD 58.3474, a **31.47%** return.
- RSI reached **78.99**, creating the `rsi_overbought` transition.
- The close remained below the USD 62.0162 upper Bollinger band.
- Volume z-score was **0.64**, below the abnormal-volume threshold.
- The July 28 session rose **4.06%** from the prior close on the same date as PayPal's Q2 release.

The Q2 release is direct primary evidence for the final-session repricing: PayPal raised full-year
non-GAAP EPS guidance to about USD 5.38 while reporting 10% TPV growth and strong free cash flow.
It does not prove that one event explains the entire one-month advance. The alert is material
because the higher mark reduces margin of safety while the short-term price signal is extended.

## Business and financial evidence

PayPal operates a two-sided payments platform spanning branded checkout, Venmo, and unbranded
processing. Q2 2026 net revenue increased 5% to USD 8.682 billion and TPV increased 10% to USD
486.4 billion. Transaction-margin dollars increased only 1%; GAAP operating income fell 5%,
non-GAAP operating margin contracted 248 basis points, and active accounts increased only 0.3%
year over year while declining slightly sequentially. Free cash flow was USD 1.775 billion.

At June 30, PayPal reported USD 8.306 billion cash, USD 6.959 billion of short- and long-term
investments, and USD 13.400 billion of short- and long-term debt. That liquidity, positive cash
generation, and continued repurchases support balance-sheet resilience, but do not remove credit,
regulatory, cyber, fraud, network-dependence, or transformation-execution risks.

## Thesis, contrary evidence, and invalidation

The thesis is that disciplined execution can stabilize branded checkout, sustain Venmo and
Braintree growth, convert PayPal's scale into durable free cash flow, and allow buybacks to
compound per-share value. Evidence against the thesis is the Q2 contraction in operating income
and margins, nearly flat active-account growth, and continued dependence on successful
transformation rather than demonstrated durable earnings growth.

Potential catalysts are sustained branded-checkout stabilization, transaction-margin acceleration,
margin recovery, Venmo monetization, and delivery above the raised 2026 EPS outlook. The thesis
would be invalidated by renewed branded-checkout deterioration, persistent transaction-margin or
operating-margin contraction, loss of active accounts, material regulatory or credit deterioration,
or free-cash-flow weakening that undermines capital returns.

## Valuation

The USD 58.3474 mark is about 10.8 times management's approximately USD 5.38 full-year non-GAAP
EPS guidance. A bounded 12-month scenario applies an **8x** downside multiple and a **12x** base
multiple to that same guidance:

- Downside: USD 43.04, or **-26.2%**.
- Base: USD 64.56, or **+10.6%**.

The range is deliberately conservative because Q2 margins contracted and active-account growth was
minimal. The base case narrowly exceeds the configured 10% absolute-upside threshold, but its
upside-to-downside ratio is only about 0.4, below the required 1.0. Medium confidence and
post-results overbought timing further prevent conviction strategy research.

## Sources

- [PayPal Q2 2026 results furnished on Form 8-K](https://www.sec.gov/Archives/edgar/data/1633917/000163391726000080/pypl2q-26earningsrelease.htm)
  (`source_pypl_q2_2026_results`, checked 2026-07-29).
- [PayPal Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1633917/000163391726000082/pypl-20260630.htm)
  (`source_pypl_q2_2026_10q`, checked 2026-07-29).
- Canonical market and indicator state:
  `data/market/latest.csv`, `data/market/indicators.csv`, and
  `data/market/prices/security_1e8fbdb0f45f2b413e00.csv`, retrieved
  `2026-07-29T16:55:24Z`.

Next review: **2026-08-28**, or sooner after material guidance, margin, regulatory, credit, or
capital-allocation evidence.
