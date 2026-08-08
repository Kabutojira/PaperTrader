---
title: "PayPal Holdings, Inc. common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-07-29"
updated: "2026-08-08"
provenance: "source_pypl_q2_2026_10q|source_pypl_q2_2026_results|source_pypl_sec_submissions_20260808"
security_id: security_1e8fbdb0f45f2b413e00
issuer_id: issuer_5c3fe75eec62fcc8cb57
ticker: PYPL
venue_mic: XNAS
provider_symbol: PYPL
currency: USD
confidence: medium
next_review: "2026-08-22"
---

# PayPal Holdings, Inc. common stock

## Decision

**Hold / Watch; no paper-trade escalation.** PayPal's unchanged July 28 results remain the latest
operating evidence. Payment volume and free cash flow improved and management raised full-year
non-GAAP EPS guidance, but lower operating income, contracting margins, nearly flat active
accounts, transformation risk, and weak scenario asymmetry still constrain the thesis. The
strengthened overbought alert followed by a MACD cross below signal shows post-results momentum
losing force, not a new fundamental catalyst or an entry condition.

## Changes since prior review

- **Evidence:** Both retained Q2 SEC documents have unchanged content hashes. The SEC submissions
  index shows no new issuer operating filing after July 28 through this August 8 check; only
  ownership Forms 4 and planned-sale Forms 144 followed.
- **Market state:** The alert-time USD 58.54 mark on August 4 strengthened the existing
  `rsi_overbought` state. The USD 57.93 mark on August 5 entered
  `macd_cross_below_signal`. The newer canonical mark is USD 59.07 on August 7; RSI remains
  overbought at 71.05 and MACD remains below signal.
- **Assumptions and thesis:** Q2 guidance, margin, active-account, liquidity, debt, catalyst, risk,
  and invalidation assumptions are unchanged. The technical reversal weakens timing but does not
  invalidate the operating thesis.
- **Valuation and action:** The legacy two-point comparison is replaced by a scenario-complete
  mature-compounder assessment. USD 43.04/USD 64.56/USD 80.70 bear/base/bull values imply a USD
  61.332 probability-weighted value versus USD 59.07. Base upside is only 9.29%, expected return is
  3.83%, and bear downside is 27.14%, so the disposition remains Hold / Watch and allocation
  ineligible.
- **Escalation:** No valuation or buy-zone gate was newly reached, no catalyst or invalidation
  fired, and no material primary evidence changed. A full security review is not warranted.

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

The merged deterministic alert record covers two exact observations:

- From July 7 through August 4, adjusted close rose from USD 45.65 to USD 58.54, a **28.24%**
  return, and the existing `rsi_overbought` state strengthened.
- From July 8 through August 5, adjusted close rose from USD 44.53 to USD 57.93, a **30.09%**
  return, while `macd_cross_below_signal` entered.
- The current August 7 adjusted close is **USD 59.07**. RSI is **71.05**, the USD 62.53 upper
  Bollinger band remains above the mark, MACD is 3.0720 versus a 3.1714 signal, and volume z-score
  is **-0.59**.

The two payload hashes remain exact identities for their August 4 and August 5 alert packets. The
newer current-cache hash incorporates two later sessions and is used for this assessment. The Q2
release remains direct primary evidence for the July repricing, but no new operating filing links
the August technical reversal to a changed fundamental assumption. The combined alerts are timing
risk after an extended advance, not an independent paper-trade signal.

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

The USD 59.07 current mark is about 11.0 times management's approximately USD 5.38 full-year
non-GAAP EPS guidance. A bounded 12-month mature-compounder earnings-multiple assessment uses
30%/50%/20% bear/base/bull probabilities:

- Bear: **USD 43.04** or 8x guided EPS, **-27.14%**, if margin contraction persists and branded
  checkout, transaction-margin growth, or active accounts weaken.
- Base: **USD 64.56** or 12x guided EPS, **+9.29%**, if raised guidance is delivered but durable
  margin and account acceleration remain unproven.
- Bull: **USD 80.70** or 15x guided EPS, **+36.62%**, if branded checkout stabilizes, Venmo
  monetization improves, and transaction-margin and operating-margin growth recover.

The probability-weighted fair value is **USD 61.332**, a **3.83%** expected return before the
medium-confidence adjustment. Base upside is below the configured hurdle, expected return and
margin of safety are not compelling, and bear/base asymmetry remains adverse. This supports Hold /
Watch rather than a new or increased baseline position.

## Sources

- [PayPal Q2 2026 results furnished on Form 8-K](https://www.sec.gov/Archives/edgar/data/1633917/000163391726000080/pypl2q-26earningsrelease.htm)
  (`source_pypl_q2_2026_results`, checked 2026-08-08; unchanged).
- [PayPal Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1633917/000163391726000082/pypl-20260630.htm)
  (`source_pypl_q2_2026_10q`, checked 2026-08-08; unchanged).
- [PayPal SEC submissions index](https://data.sec.gov/submissions/CIK0001633917.json)
  (`source_pypl_sec_submissions_20260808`, checked 2026-08-08).
- Canonical market and indicator state:
  `data/market/latest.csv`, `data/market/indicators.csv`, and
  `data/market/prices/security_1e8fbdb0f45f2b413e00.csv`, current through
  `2026-08-07` and retrieved `2026-08-08T13:47:02Z`.

Next review: **2026-08-22**, or sooner after material guidance, margin, regulatory, credit, or
capital-allocation evidence.

[[research-catalog|Research catalog]] · [[index|Current paper-trading decision]]
