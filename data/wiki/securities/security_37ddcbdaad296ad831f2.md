---
title: Coinbase Global, Inc. Class A common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-21"
provenance: "source_coin_q1_2026_10q; source_coin_july_2026_management_8k; source_coin_q2_2026_10q; source_coin_sec_submissions_20260819"
security_id: security_37ddcbdaad296ad831f2
issuer_id: issuer_3584c0cf729606c65538
confidence: medium
next_review: "2026-09-04"
---

# Coinbase Global, Inc. Class A common stock

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
  "security_id": "security_37ddcbdaad296ad831f2",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_37ddcbdaad296ad831f2.csv",
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

- Immutable security: `security_37ddcbdaad296ad831f2`
- Issuer: `issuer_3584c0cf729606c65538`
- Instrument: Class A common stock, Nasdaq (`XNAS`), USD
- Provider identity: `COIN` / `XNAS` / `USD` / equity

Coinbase is a direct platform exposure within [[ideas/idea_digital_finance_crypto_rails]].

## Economics and thesis

The SEC-filed Q2 2026 Form 10-Q supersedes the Q1 operating baseline. Q2 net revenue was USD 1.154
billion: transaction revenue was USD 599 million and subscription and services revenue was USD 555
million. Stablecoin revenue of USD 292 million still supports the payment-rails mechanism in
[[ideas/idea_digital_finance_crypto_rails]], but transaction revenue fell 22% year over year,
subscription and services revenue fell 12%, and net loss was USD 359 million. Six-month operating
cash flow remained positive at USD 380 million, down from USD 1.093 billion a year earlier.

At June 30 Coinbase reported USD 8.614 billion of cash and cash equivalents, including payment
stablecoins, against USD 539 million of short-term borrowings and USD 5.944 billion of long-term
debt. Six-month stock-based compensation expense was USD 486 million. One counterparty produced 26%
of Q2 revenue, up from the 23% Q1 concentration cited in the baseline review. The mix confirms a
real diversified platform but not durable through-cycle economics or a decision-ready buy zone.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| Q2 stablecoin revenue was USD 292 million. | Stablecoin rails remain material, but did not offset broader declines. |
| Q2 transaction revenue fell 22%; subscription/services fell 12%. | Diversification has not removed crypto-cycle sensitivity. |
| Six-month operating cash flow was USD 380 million despite a USD 754 million net loss. | Liquidity held, but GAAP profitability and cash conversion remain volatile. |
| One counterparty generated 26% of Q2 revenue. | Stablecoin/counterparty concentration increased from the Q1 baseline. |
| Six-month stock compensation expense was USD 486 million. | Per-share economics differ materially from adjusted results. |
| COIN fell 11.61% from July 2 through July 31 to USD 146.26 on 20.87 million shares. | The earlier alert combined a lower-Bollinger breach, bearish MACD cross and volume anomaly. |
| COIN closed at USD 186.49 on August 21, up 17.82% from July 24, while 22.495 million shares traded at a 2.507 volume z-score; the close was also above the upper Bollinger band. | The strengthened volume anomaly confirms a sharp rerating, but the higher price worsens the valuation frontier rather than establishing a buy zone. |
| The SEC submissions index and Q2 filing hashes remained unchanged when rechecked on August 21; the index contains no periodic or current report newer than the July 30 Q2 filings. | No new issuer evidence explains the rerating or changes the Q2 operating and scenario assumptions. |

Primary evidence: [Coinbase Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000088/coin-20260630.htm),
[Coinbase Q1 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000054/coin-20260331.htm),
and [Coinbase July 2026 Form 8-K](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000080/coin-20260722.htm).
The [current SEC submissions index](https://data.sec.gov/submissions/CIK0001679788.json) was checked
again on August 21 and shows no newer issuer operating filing.

## Changes since prior review

- **Evidence:** The Q2 Form 10-Q and SEC submissions-index hashes are unchanged, and the August 21
  index check shows no newer issuer operating filing. The exact July 24 through August 21 market
  period now records a 17.82% rise to USD 186.49, with 22.495 million shares at a 2.507 volume
  z-score and an upper-Bollinger breach, but no fresh issuer catalyst.
- **Assumptions and scenarios:** Cycle-normalized transaction and recurring revenue, segment
  multiples, the conservative balance-sheet deductions, 282 million diluted shares and the
  30%/50%/20% probabilities are unchanged. Bear/base/bull fair values remain USD 28/USD 87/USD 191.
- **Valuation outputs:** The reference mark increased from USD 160.20 to USD 186.49 while the
  USD 28/USD 87/USD 191 scenarios remain unchanged. The USD 90.10 probability-weighted fair value
  now implies about -51.69% expected return, with about -84.99%/-53.35%/2.42% bear/base/bull
  returns. Every decisive valuation gate remains failed by a wider margin.
- **Thesis, catalysts and risks:** The stablecoin-rails mechanism, medium confidence, catalysts,
  invalidation and severe residual risks are unchanged. The strengthened volume anomaly and upper-
  Bollinger breach confirm elevated market attention but are risk, not opportunity, because no
  operating evidence supports the rerating and margin of safety deteriorated.
- **Blockers, gaps, rating and action:** No hard blocker is added. Concentration, cycle
  normalization, medium confidence, weak timing and absent margin of safety remain soft gaps.
  Complete research, Strong Sell / Avoid and allocation ineligibility are unchanged; no strategy
  or signal is justified.

## Idea exposure map

- **Accepted — needs review:** [[ideas/idea_digital_finance_crypto_rails|Digital finance and crypto
  rails]] has a positive, high-sensitivity mechanism through regulated trading, custody, USDC,
  subscriptions, institutional products and Base. Q2 evidence still supports the mechanism, but the
  canonical relationship review date has passed and the edge needs a separate refresh for lower
  revenue, higher counterparty concentration and the completed valuation.
- **Candidates:** None. The complete maintained idea catalog contains no additional pairing with a
  specific material causal transmission mechanism.
- **Rejected — no link:** AI infrastructure and monetization, biology and healthcare, defense and
  aerospace, digital attention and gaming, energy and critical minerals, industrial reshoring,
  macro hedges, robotics, semiconductors, solar, space and related maintained themes are superficial
  thematic or technology adjacency. Current primary evidence does not show material Coinbase
  product, customer, supplier or cost-driver exposure to those mechanisms.

## Scenario valuation

The repository `other` template and permitted `sum_of_parts` method fit Coinbase better than a bank
or mature-compounder template because transaction, stablecoin, staking, custody, financing,
derivatives and crypto-asset economics have distinct drivers. Each case capitalizes normalized
transaction and recurring revenue separately, deducts a conservative balance-sheet amount to avoid
treating payment-stablecoin cash or customer assets as distributable corporate cash, and divides by
282 million diluted shares. That share count is above the Q2 six-month basic weighted average of
264.1 million to recognize dilution risk.

| Case | Probability | Assumptions | Fair value |
| --- | ---: | --- | ---: |
| Bear | 30% | USD 2.0bn transaction revenue at 2x plus USD 2.0bn recurring revenue at 4x, less USD 4.0bn; weak volume, rates and take rates with persistent dilution. | USD 28 |
| Base | 50% | USD 2.7bn transaction revenue at 4x plus USD 2.4bn recurring revenue at 7x, less USD 3.0bn; Deribit supports mix, but cycle and concentration persist. | USD 87 |
| Bull | 20% | USD 4.0bn transaction revenue at 6x plus USD 3.2bn recurring revenue at 10x, less USD 2.0bn; volume and stablecoin growth, margin recovery and moderated dilution. | USD 191 |

At the current USD 186.49 mark, the probability-weighted value remains USD 90.10. The approximately
-51.69% expected return, -53.35% base return and -84.99% bear return fail the expected-return,
base-return, downside-payoff and margin-of-safety gates. The August 21 strengthened volume anomaly
is therefore risk for allocation: it prompted useful research but the unsupported rerating widened
the valuation shortfall instead of identifying an opportunity.

## Catalysts, risks, and invalidation

Catalysts are sustained USDC growth despite lower rates, recurring subscription growth, derivatives
and institutional share gains, and GAAP profitability. Invalidate if crypto activity contracts,
stablecoin revenue or counterparty economics weaken, fees compress, custody or credit losses occur,
regulation limits products, or equity compensation absorbs per-share cash generation.

## Disposition

Status: **watching**, confidence **medium**, rating **Strong Sell**, portfolio action **Avoid**, and
allocation eligibility **ineligible**. Review by **2026-09-04**, or earlier after material results,
rate or stablecoin-partner changes, custody or regulatory events, or a price move that materially
changes the scenario frontier. No strategy or signal is created because expected, base and bear
returns and margin of safety fail the canonical gate. See [[research-catalog]] for the maintained
research graph.
