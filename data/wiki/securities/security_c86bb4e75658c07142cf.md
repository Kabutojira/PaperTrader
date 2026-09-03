---
title: "Alphabet Inc. Class A common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-08-01"
updated: "2026-08-01"
provenance: "source_alphabet_q2_2026_10q|source_alphabet_q2_2026_results"
security_id: security_c86bb4e75658c07142cf
issuer_id: issuer_b25c5419eee7ff55e0d4
ticker: GOOGL
venue_mic: XNAS
provider_symbol: GOOGL
currency: USD
confidence: medium
next_review: "2026-08-31"
---

# Alphabet Inc. Class A common stock

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
  "security_id": "security_c86bb4e75658c07142cf",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_c86bb4e75658c07142cf.csv",
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

**Watch; no conviction strategy.** Q2 revenue, Search, YouTube, Cloud, operating income, and margins
all grew strongly, supporting Alphabet's advertising and AI-cloud economics. The July 31 bullish
MACD crossover accompanied a 6.73% one-session rebound, but its recorded strength was weak and the
20-session return remained negative. At USD 356.13, a bounded 12-month earnings-multiple valuation
has a USD 360 base case and USD 354 probability-weighted value. The mark offers almost no base-case
upside or margin of safety, while record AI infrastructure spending, equity issuance, and unresolved
antitrust remedies constrain risk-adjusted entry appeal.

## Immutable identity

- Security ID: `security_c86bb4e75658c07142cf`
- Issuer ID: `issuer_b25c5419eee7ff55e0d4`
- Instrument: Alphabet Inc. Class A common stock
- Listing: Nasdaq Global Select Market (`XNAS`)
- Provider symbol: `GOOGL`
- Currency: `USD`

Alphabet's SEC filing identifies Class A common stock under `GOOGL`, matching the canonical issuer,
instrument, venue, provider, and currency identity. The Class C `GOOG` shares are a different
instrument and are not interchangeable with this immutable Class A identity. No duplicate canonical
Class A identity exists.

## Alert review

The payload's canonical observation period is 2026-07-02 through 2026-07-31:

- The adjusted close ended at USD 356.13, down **1.05%** over the period.
- The recorded `macd_cross_above_signal` entered on July 31 with strength **0.0723**.
- MACD was **-6.1312** against a **-6.6089** signal line, leaving a positive **0.4777** histogram.
- The July 31 close rose **6.73%** from USD 333.66 on July 30, on 46.43 million shares.
- RSI was neutral at **54.31** and the close remained below the USD 358.68 upper Bollinger band.

The alert is **a weak technical rebound, not an independent opportunity catalyst**. The crossover
followed strong Q2 evidence already public on July 22, yet the full observation-period return was
negative and the deterministic classifier also judged the signal too weak for durable ingestion.
Fundamental results improve the operating thesis, but the rebound worsened entry valuation and does
not resolve capital-intensity, dilution, or regulatory risks.

## Business and financial evidence

Alphabet combines Google Search and other advertising, YouTube, subscriptions and devices, Google
Cloud, and Other Bets. Distribution, user scale, advertiser demand, proprietary data and models,
full-stack AI infrastructure, and a deeply embedded developer and enterprise ecosystem support
exceptional economics. Rapid AI substitution, infrastructure requirements, regulation, and customer
alternatives mean those advantages require continued reinvestment.

Q2 revenue rose 24% to USD 119.796 billion. Google Services revenue rose 15% to USD 94.540 billion:
Search and other grew 17%, YouTube ads grew 13%, and subscriptions, platforms and devices grew 15%.
Google Cloud revenue accelerated 82% to USD 24.768 billion, while Cloud operating income rose to USD
8.814 billion from USD 2.826 billion. Consolidated operating income rose 30% to USD 40.770 billion
and operating margin expanded to 34% from 32%.

Reported quarterly net income of USD 112.193 billion and diluted EPS of USD 9.11 are not suitable
run-rate earnings anchors. Alphabet states that net equity-security gains increased quarterly net
income by USD 77.1 billion and diluted EPS by USD 6.26. The valuation therefore normalizes operating
earnings rather than capitalizing that unrealized gain.

At June 30, cash, cash equivalents and marketable securities were USD 242.474 billion, long-term
debt was USD 98.165 billion, mandatory-convertible preferred equity was USD 18.023 billion, and
12.230 billion common shares were outstanding. The resulting USD 126.286 billion balance after debt
and preferred equity is substantial, but both debt and dilution rose as infrastructure spending
expanded.

TTM operating cash flow was USD 185.675 billion, capital expenditures were USD 132.402 billion, and
free cash flow was USD 53.273 billion. Q2 free cash flow was negative USD 5.855 billion as quarterly
capital expenditures reached USD 44.924 billion. At the current mark and period-end common share
count, TTM free-cash-flow yield is only about **1.22%**. In June Alphabet raised USD 49.6 billion
through common and mandatory-convertible preferred equity, issued USD 20.3 billion of senior notes,
and established an up-to-USD 40.0 billion common-stock ATM program primarily for employee-equity tax
obligations. Those actions fund AI capacity but raise the per-share return hurdle.

## Thesis, contrary evidence, catalysts, and invalidation

The thesis is that Search and YouTube cash generation can fund AI investment while Cloud growth,
enterprise AI adoption, model efficiency, and new monetization compound operating income per share.
Current Search, Cloud, operating-margin, and cash-flow evidence strongly supports demand and
monetization, while the large liquid-asset balance provides resilience.

Contrary evidence includes AI products changing search behavior and monetization, heavy and rapidly
rising capital expenditures, electricity and capacity constraints, model and infrastructure
competition, stock-based compensation and equity issuance, investment-value volatility, privacy and
AI regulation, and antitrust proceedings that seek restrictions, business-practice changes, fines,
or structural remedies. Network revenue was roughly flat, Other Bets losses widened, and the latest
free-cash-flow conversion was compressed by infrastructure investment.

Potential catalysts are sustained Search query and monetization growth, Cloud growth with durable
margin expansion, improving AI serving economics, capex translating into operating cash flow, and
clarity on antitrust remedies. The thesis would be invalidated by sustained Search or advertising
share loss, Cloud growth or margins failing to justify infrastructure spend, persistently weak free
cash flow, material per-share dilution without commensurate returns, or regulatory remedies that
structurally impair distribution or monetization.

## Valuation

A 12-month `mature_compounder` earnings-multiple valuation uses the latest filing and release,
period-end share count, liquid assets, debt and preferred equity, and normalized operating earnings.
It excludes the unusually large unrealized equity-security gain from run-rate EPS and treats AI
capital intensity, dilution, and regulatory outcomes explicitly:

- Bear, 30%: USD **260**, using USD 10 normalized EPS at 26x as AI competition, antitrust remedies,
  capex pressure, and dilution slow per-share growth and compress the multiple.
- Base, 50%: USD **360**, using USD 12 normalized EPS at 30x as Search remains resilient, Cloud
  scales, operating margins stay strong, and elevated infrastructure spending earns adequate but
  not exceptional incremental returns.
- Bull, 20%: USD **480**, using USD 15 normalized EPS at 32x as AI products expand Search usage,
  Cloud growth remains unusually strong, margins improve, and infrastructure investment converts
  into durable per-share cash flow.

Against USD 356.13, the cases imply **-26.99%**, **+1.09%**, and **+34.78%**. Probability-weighted
fair value is USD 354, or **-0.60%** before the medium-confidence adjustment and **-0.45%** after it.
The base-upside-to-bear-downside ratio is only **0.04**, and the 20% margin-of-safety buy zone is USD
288. The current mark therefore fails confidence-adjusted return, base-case upside, bear/base payoff,
expected/bear payoff, and margin-of-safety gates. No accepted canonical idea relationship exists, so
the relationship gate is also pending.

## Sources

- [Alphabet Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000071/goog-20260630.htm)
  (`source_alphabet_q2_2026_10q`, checked 2026-08-01).
- [Alphabet Q2 2026 results](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm)
  (`source_alphabet_q2_2026_results`, checked 2026-08-01).
- Canonical market and indicator state: `data/market/latest.csv`, `data/market/indicators.csv`, and
  `data/market/prices/security_c86bb4e75658c07142cf.csv`, market date 2026-07-31 and retrieved
  2026-08-01.

Next review: **2026-08-31**, or sooner after a material Search, Cloud, AI monetization, capex,
free-cash-flow, equity issuance, or antitrust-remedy development.

Related navigation: [[security-catalog|Securities]], [[signals|Signals and research alerts]], and
[[research-catalog|Research catalog]].
