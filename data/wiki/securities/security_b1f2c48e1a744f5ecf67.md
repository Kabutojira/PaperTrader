---
title: Labcorp Holdings Inc. common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-29"
updated: "2026-08-21"
provenance: "source_lh_q2_2026_results; source_lh_q2_2026_10q; source_lh_aug11_2026_8k; source_lh_aug17_2026_8k; source_lh_sec_submissions_20260821; deterministic market and FX caches"
security_id: security_b1f2c48e1a744f5ecf67
issuer_id: issuer_d0762758c05766ef1ab5
confidence: medium
next_review: "2026-09-04"
---

# Labcorp Holdings Inc. common stock

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
  "security_id": "security_b1f2c48e1a744f5ecf67",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_b1f2c48e1a744f5ecf67.csv",
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

- Immutable security: `security_b1f2c48e1a744f5ecf67`
- Issuer: `issuer_d0762758c05766ef1ab5`, incorporated in Delaware
- Instrument: common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `LH` / `XNYS` / `USD` / equity

The SEC filings confirm Labcorp Holdings Inc. common stock trades as LH on the New York Stock
Exchange. The canonical row, filing, and provider identity agree, no duplicate provider identity
was found, and no accepted canonical idea relationship currently links this security to the
PaperTrader graph.

## Changes since prior review

- **Facts and evidence changed:** the Q2 Form 10-Q now confirms USD 141.8 million cash, USD 5.858
  billion long-term debt, USD 637.0 million first-half operating cash flow, USD 252.6 million capital
  expenditure, and 80.9 million shares outstanding. An August 14 filing disclosed a Biopharma
  Laboratory Services leadership transition, and an August 17 filing scheduled a September 10
  Investor Day covering strategy, capital deployment, and long-term financial outlook.
- **Alert interpretation changed:** after the July results repricing faded, LH rose 4.23% from USD
  319.31 on July 23 to USD 332.81 on August 20 and entered a bullish MACD crossover. Volume was not
  abnormal and the close remained below the upper Bollinger band, so this is improving momentum,
  not evidence of a new fundamental earnings change.
- **Valuation inputs are unchanged, but outputs deteriorated with price:** Q2 guidance still
  supports USD 253.40/USD 311.53/USD 371.00 bear/base/bull fair values. The fresh USD 336.34 mark is
  now above the base and probability-weighted values, versus USD 309.20 at the prior review.
- **Thesis, catalysts, risks, blockers, and gaps:** Q2 growth, margin expansion, and raised guidance
  remain supportive. The leadership transition adds execution risk and Investor Day adds a dated
  catalyst, but neither changes guidance. Leverage, working-capital conversion, acquisition
  integration, reimbursement, medium confidence, inadequate expected return, inadequate base
  upside, weak downside payoff, and a missing accepted relationship remain the relevant gates.
- **Rating and action:** the business-quality conclusion and medium confidence are unchanged, but
  the higher mark moves the valuation conclusion from near fair value to clearly unattractive for
  new exposure. Labcorp remains watching and allocation-ineligible; no conviction strategy is
  justified.

## Alert review: opportunity, risk, or noise?

The payload's exact July 23-August 20 period rose 4.23%, from USD 319.31 to USD 332.81. On August
20 MACD rose to 6.1789 above its 5.7839 signal; RSI was 63.39, the close remained below the USD
336.11 upper Bollinger band, and volume was not abnormal. This confirms the canonical bullish-MACD
transition, observation period, and source-price hash. The next completed bar lifted the mark to
USD 336.34 on August 21.

The latest SEC evidence does not show a new earnings event behind the crossover. The August 14
filing concerns Biopharma leadership and the August 17 filing announces Investor Day without new
financial targets. The alert is therefore **constructive technical momentum but a valuation risk**:
it is not noise, yet it does not independently improve cash flows or create a paper-trade entry.

## Economics and thesis

Labcorp combines a large Diagnostics Laboratories franchise with Biopharma Laboratory Services.
Q2 2026 revenue rose 5.8% to USD 3.731 billion, operating income increased to USD 451.6 million,
and adjusted EPS rose 14.9% to USD 4.99. Diagnostics revenue grew 5.5% and adjusted margin expanded
50 basis points to 18.0%. Biopharma revenue grew 6.5%, including 9.8% Central Labs growth, and
adjusted margin expanded 130 basis points to 17.0%. Biopharma backlog was USD 8.73 billion and
trailing-twelve-month book-to-bill was 1.03.

The thesis is that recurring diagnostic demand, health-system partnerships, specialty testing,
Central Labs scale, and automation support mid-single-digit revenue growth and operating leverage.
The counter-thesis is that reimbursement and payer pressure, labor and input costs, acquisition
integration, customer concentration, working-capital volatility, and a leveraged balance sheet
limit per-share compounding.

At June 30 Labcorp held USD 141.8 million of cash against USD 5.858 billion of long-term debt after
retiring USD 500 million of notes. Q2 operating cash flow was USD 445.5 million, capital expenditure
USD 131.6 million, and free cash flow USD 313.9 million; first-half operating cash flow was USD
637.0 million and capital expenditure USD 252.6 million. During Q2 the company also spent USD 225.7
million on acquisitions and USD 353.8 million on repurchases. Full-year guidance remains 5.4%-6.3%
enterprise revenue growth, USD 18.10-18.55 adjusted EPS, and USD 1.24-1.36 billion free cash flow.
The franchise remains cash-generative, but low cash, acquisitions, and net debt warrant only an
adequate balance-sheet score.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| Q2 revenue grew 5.8%, operating income rose, and adjusted EPS grew 14.9%. | The operating thesis strengthened with current reported evidence. |
| Both segments grew and expanded adjusted margins. | Growth and operating leverage were broad rather than dependent on one segment. |
| Biopharma backlog was USD 8.73 billion with 1.03 book-to-bill. | Demand visibility remains useful, though conversion and cancellations remain risks. |
| USD 141.8 million cash versus USD 5.86 billion debt after note retirement. | Refinancing risk improved, but acquisition spending and leverage reduce downside resilience. |
| Full-year adjusted-EPS guidance increased to USD 18.10-18.55. | The USD 336.34 mark values the midpoint at about 18.4 times. |
| Half-year free cash flow fell despite higher earnings. | Working-capital timing and planned investment require monitoring. |
| Biopharma leadership changes in September. | Continuity is plausible, but backlog conversion and operating execution require monitoring. |
| September 10 Investor Day will address strategy, capital deployment, and long-term outlook. | This is a catalyst, but no undisclosed targets are included in current valuation. |
| The July genetic panel still has no disclosed economics. | Product optionality is positive but insufficient for valuation support. |

Registered primary evidence: [SEC-filed Q2 results](https://www.sec.gov/Archives/edgar/data/920148/000092014826000162/form8-kexhibit9912q26.htm)
(`source_lh_q2_2026_results`), [Q2 Form 10-Q](https://www.sec.gov/Archives/edgar/data/920148/000092014826000175/lh-20260630.htm)
(`source_lh_q2_2026_10q`), [August 11 Form 8-K](https://www.sec.gov/Archives/edgar/data/920148/000092014826000182/lh-20260811.htm)
(`source_lh_aug11_2026_8k`), [August 17 Form 8-K](https://www.sec.gov/Archives/edgar/data/920148/000092014826000185/lh-20260817.htm)
(`source_lh_aug17_2026_8k`), and the [SEC submissions index](https://data.sec.gov/submissions/CIK0000920148.json)
(`source_lh_sec_submissions_20260821`).

## Idea exposure map

- **Accepted canonical relationships:** none. The structured relationship table contains no
  accepted edge for this security.
- **Candidate — [[ideas/idea_precision_biology_healthcare_automation|precision biology and
  healthcare automation]] (positive):** Labcorp's diagnostics, specialty testing, Central
  Laboratories, and advanced-technology investment can transmit validated precision-testing and
  laboratory-workflow adoption into volume, mix, recurring testing revenue, and margins. Current
  Q2 segment growth and margins establish material operating exposure, but they do not isolate the
  economics of automation or precision products. Invalidate the candidate if these offerings remain
  immaterial to organic growth and margins, reimbursement blocks adoption, or implementation costs
  absorb the benefit. A bounded relationship review must accept or reject this edge before it is
  canonical.
- **Rejected-no-link:** the complete maintained idea catalog was searched; no other idea has both a
  specific causal transmission mechanism and material Labcorp exposure in current primary evidence.

## Valuation, catalysts, and risks

The USD 336.34 mark is 18.4 times the midpoint of the issuer's USD 18.10-18.55 2026 adjusted-EPS
guidance. The mature-compounder template uses an earnings-multiple sensitivity because current
revenue, margins, share repurchases, net debt, and issuer guidance are available in primary
evidence. The 25% bear case applies 14 times the low end, giving USD 253.40. The 50% base case
applies 17 times the USD 18.325 midpoint, giving USD 311.53. The 25% bull case applies 20 times the
high end, giving USD 371.00. These are 12-month comparison scenarios, not forecasts; adjusted EPS
is issuer-defined and the multiples remain sensitive to growth, reimbursement, leverage,
acquisitions, cash conversion, and repurchases.

Catalysts are the September 10 Investor Day, continued Diagnostics volume and price/mix growth,
Central Labs backlog conversion, health-system wins, specialty-test adoption, debt reduction, and
delivery of raised guidance. Risks include the Biopharma leadership transition, reimbursement and
government-payer changes, wage and supply inflation,
billing or regulatory disputes, data security, customer and pharmaceutical-cycle exposure,
acquisition integration, working-capital swings, net debt, and multiple compression. Invalidate the
thesis if organic volume and price/mix weaken together, segment margins reverse without productive
investment, backlog conversion deteriorates, free cash flow misses the guided range persistently,
or leverage rises without commensurate earnings and cash generation.

## Disposition

Status: **watching**, confidence **medium**, and **allocation-ineligible**. At USD 336.34, the
25/50/25 scenario set implies about 24.7% bear downside, 7.4% base downside, and 7.3%
probability-weighted downside before confidence adjustment. The bullish MACD crossover improves
timing but cannot clear the expected-return, base-return, downside-payoff, margin-of-safety, or
accepted-relationship gates. No conviction strategy is queued; baseline work belongs to the
deterministic allocator. Review by **2026-09-04**, or earlier if guidance, reimbursement, backlog,
cash conversion, leverage, leadership continuity, or the valuation frontier changes materially;
then revisit after Investor Day. Related system context: [[index]] and
[[ideas/idea_precision_biology_healthcare_automation]].
