---
title: "PayPal Holdings, Inc. common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-07-29"
updated: "2026-08-28"
provenance: "source_pypl_q2_2026_10q|source_pypl_q2_2026_results|source_pypl_sec_submissions_20260828"
security_id: security_1e8fbdb0f45f2b413e00
issuer_id: issuer_5c3fe75eec62fcc8cb57
ticker: PYPL
venue_mic: XNAS
provider_symbol: PYPL
currency: USD
confidence: medium
next_review: "2026-09-11"
---

# PayPal Holdings, Inc. common stock

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
  "security_id": "security_1e8fbdb0f45f2b413e00",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_1e8fbdb0f45f2b413e00.csv",
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

**Buy / Watch; no paper-trade escalation.** PayPal fell 12.71% in the August 28 session on 2.06
times its 20-session average volume and entered below its lower Bollinger band. The current SEC
index contains no new issuer operating filing after July 28, so the selloff is an unexplained risk
event and possible dislocation, not verified fundamental deterioration or a confirmed opportunity.
The lower USD 53.66 mark improves expected and base-case return, but bear/base and expected/bear
payoff, margin of safety, timing, and the pending digital-finance relationship still fail the
canonical gate.

## Changes since prior review

- **Evidence:** Both retained Q2 SEC documents still match their prior content hashes. The August 28
  SEC submissions index shows no issuer operating filing after July 28; later filings remain
  ownership, planned-sale, or beneficial-ownership notices. No current primary fact changes Q2
  guidance, margins, active accounts, liquidity, debt, PYUSD economics, or free cash flow.
- **Market state:** The canonical adjusted close fell from USD 61.47 on August 27 to USD 53.66 on
  August 28, a 12.71% one-session decline, and finished 6.21% below the July 31 close. Volume of
  36.21 million was 2.06 times the 20-session average. The close was 4.11% below the USD 55.9616
  lower Bollinger band; RSI fell to 35.00 and MACD remained below signal.
- **Assumptions and thesis:** The operating thesis, contrary evidence, catalysts, invalidation,
  hard-blocker set, and medium confidence are unchanged because no new operating evidence explains
  the move. Timing remains weak: the oversold transition improves price but the high-volume selloff
  adds event uncertainty and lacks a dated fundamental catalyst.
- **Valuation:** The mature-compounder template, earnings-multiple method, USD 43.04/USD 64.56/USD
  80.70 scenarios, 30%/50%/20% probabilities, and underlying assumptions are unchanged. At USD
  53.66, bear/base/bull returns improve to -19.79%/+20.31%/+50.39%; probability-weighted fair value
  remains USD 61.332 and expected return improves from -1.55% to +14.30%.
- **Rating, action, blockers, and gaps:** The deterministic rating improves from Hold to Buy while
  Watch conviction and allocation ineligibility remain unchanged. No hard blocker was added or
  resolved. Medium confidence, inadequate margin of safety, weak timing, poor payoff asymmetry, an
  unexplained high-volume decline, and the absence of a current accepted relationship remain
  decision-support gaps.
- **Idea graph:** The complete idea catalog now supports one specific candidate edge to
  [[ideas/idea_digital_finance_crypto_rails|digital finance and crypto rails]] through PayPal and
  Venmo distribution of PYUSD. That edge is explicitly pending relationship review and is not
  treated as accepted. Superficial payment adjacency to the SMB operating-system and digital-
  attention ideas was rejected because current evidence does not establish system-of-record or
  material ecosystem exposure.

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

From July 31 through August 28, adjusted close fell **6.21%** to **USD 53.66**. The August 28 session
itself fell **12.71%** from USD 61.47 on volume of **36.21 million**, or **2.06 times** the
20-session average. The mark entered **4.11% below** the **USD 55.9616** lower Bollinger band; RSI
fell to **35.00**, while MACD of **1.4215** remained below its **2.2521** signal. The two exact
packets and canonical indicator row share source-price hash
`c51cc56918d346631627519f12460983d0d56a23d8d339d7bed04ae20d1f26b2`.

No new issuer operating filing explains the decline or changes a valuation assumption. The
lower-band entry makes price more attractive, but the simultaneous high-volume gap-down prevents
treating a technical oversold reading as evidence that fundamental risk is transient. The move is
therefore an **unexplained risk event and possible dislocation**, not noise, but not yet a verified
opportunity or independent paper-trade signal.

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

## Idea exposure map

| Idea | Classification | Direction and mechanism | Evidence and invalidation |
| --- | --- | --- | --- |
| [[ideas/idea_digital_finance_crypto_rails|Digital finance and crypto rails]] | `candidate` — relationship review pending | Positive if PayPal and Venmo distribution, compliance and settlement reach make PYUSD a material source of recurring transaction or reserve-sharing economics. | The Q2 Form 10-Q confirms PYUSD availability and regulatory obligations, but does not quantify material economics. Reject if adoption remains immaterial, partner terms prevent attractive economics, compliance cost offsets revenue, or customers and merchants do not use the rail beyond speculative transfers. |
| [[ideas/idea_ai_native_smb_financial_operating_systems|AI-native SMB financial operating systems]] | `rejected-no-link` | Payments adjacency alone does not make PayPal an authoritative accounting, payroll or tax system of record. | Reconsider only after primary evidence demonstrates material permissioned workflow automation tied to retention, attach rate or lower service cost. |
| [[ideas/idea_digital_attention_gaming_ecosystems|Digital attention, gaming, and consumer ecosystems]] | `rejected-no-link` | Payment acceptance is a generic downstream service, not evidence of material ownership of attention, content or creator economics. | Reconsider only after attributable ecosystem revenue and a specific causal transmission mechanism become material. |

There are no current accepted canonical relationship rows for this security. The digital-finance
candidate must not be used for allocation, strategy, signal, or order work unless a separate
relationship review accepts the edge.

## Valuation

The USD 53.66 current mark is about 9.97 times management's approximately USD 5.38 full-year
non-GAAP EPS guidance. A bounded 12-month mature-compounder earnings-multiple assessment uses
30%/50%/20% bear/base/bull probabilities:

- Bear: **USD 43.04** or 8x guided EPS, **-19.79%**, if margin contraction persists and branded
  checkout, transaction-margin growth, or active accounts weaken.
- Base: **USD 64.56** or 12x guided EPS, **+20.31%**, if raised guidance is delivered but durable
  margin and account acceleration remain unproven.
- Bull: **USD 80.70** or 15x guided EPS, **+50.39%**, if branded checkout stabilizes, Venmo
  monetization improves, and transaction-margin and operating-margin growth recover.

The probability-weighted fair value is **USD 61.332**, a **+14.30%** expected return before the
medium-confidence adjustment. The unchanged buy-below value of USD 51.648 remains 3.75% below the
current mark. Expected and base returns now clear their minimums, but bear/base and expected/bear
payoff, margin of safety, timing, and relationship gates still fail. This supports Buy / Watch
rather than a new or increased position.

## Sources

- [PayPal Q2 2026 results furnished on Form 8-K](https://www.sec.gov/Archives/edgar/data/1633917/000163391726000080/pypl2q-26earningsrelease.htm)
  (`source_pypl_q2_2026_results`, checked 2026-08-28; unchanged).
- [PayPal Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1633917/000163391726000082/pypl-20260630.htm)
  (`source_pypl_q2_2026_10q`, checked 2026-08-28; unchanged).
- [PayPal SEC submissions index](https://data.sec.gov/submissions/CIK0001633917.json)
  (`source_pypl_sec_submissions_20260828`, checked 2026-08-28).
- Canonical market and indicator state:
  `data/market/latest.csv`, `data/market/indicators.csv`, and
  `data/market/prices/security_1e8fbdb0f45f2b413e00.csv`, current through
  `2026-08-28` and retrieved `2026-08-28T21:09:02Z`.

Next review: **2026-09-11**, or sooner after primary evidence explaining the August 28 selloff or
material guidance, margin, stablecoin-economics, regulatory, credit, or capital-allocation evidence.

[[research-catalog|Research catalog]] · [[index|Current paper-trading decision]]
