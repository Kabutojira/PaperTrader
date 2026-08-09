---
title: Coinbase Global, Inc. Class A common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-09"
provenance: "source_coin_q1_2026_10q; source_coin_july_2026_management_8k; source_coin_q2_2026_10q"
security_id: security_37ddcbdaad296ad831f2
issuer_id: issuer_3584c0cf729606c65538
confidence: medium
next_review: "2026-08-23"
---

# Coinbase Global, Inc. Class A common stock

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
| COIN fell 11.61% from July 2 through July 31 to USD 146.26 on 20.87 million shares. | The alert combined a lower-Bollinger breach, bearish MACD cross and volume anomaly. |
| COIN closed at USD 153.60 on August 7 with no active deterministic trigger. | The partial recovery does not resolve the valuation bridge or establish a buy zone. |

Primary evidence: [Coinbase Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000088/coin-20260630.htm),
[Coinbase Q1 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000054/coin-20260331.htm),
and [Coinbase July 2026 Form 8-K](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000080/coin-20260722.htm).

## Changes since prior review

- **Evidence:** No filing newer than the Q2 Form 10-Q was needed for this dependent review. The full
  review consumes its revenue mix, cash, debt, custody, stock-compensation, share-count and
  concentration disclosures rather than leaving Q2 as an unresolved escalation item.
- **Assumptions and scenarios:** The prior review had no supportable scenario values. This review
  introduces an explicit sum-of-parts framework with cycle-normalized transaction and recurring
  revenue, segment multiples, a conservative net balance-sheet deduction and 282 million diluted
  shares. Bear/base/bull fair values are USD 28/USD 87/USD 191 with 30%/50%/20% probabilities.
- **Valuation outputs:** Probability-weighted fair value is USD 90.10 versus the USD 153.60 mark.
  Expected, base and bear returns are all materially negative; the bull case alone is positive. The
  `valuation_unsupported` hard blocker is resolved, but overvaluation and absent margin of safety
  replace it as decisive economic exclusions.
- **Thesis, catalysts and risks:** The stablecoin-rails mechanism and medium thesis confidence are
  unchanged. Lower transaction and subscription revenue, 26% counterparty concentration, stock
  compensation, custody obligations and debt keep residual risk severe. Catalysts and invalidation
  conditions remain substantively unchanged and are now bounded by explicit scenarios.
- **Gaps, rating and action:** Corporate-cash classification, cycle normalization and counterparty
  economics remain soft gaps. Research completeness moves from unsupported to complete, while the
  investment conclusion moves from Unrated / Watch to Sell / Avoid. Allocation remains ineligible;
  no strategy or signal is justified.

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

At the current USD 153.60 mark, the probability-weighted value is USD 90.10. The approximately -41%
expected return, -43% base return and -82% bear return fail the expected-return, base-return,
downside-payoff and margin-of-safety gates. The alert cluster was therefore noise for allocation:
it prompted useful research but did not identify an opportunity.

## Catalysts, risks, and invalidation

Catalysts are sustained USDC growth despite lower rates, recurring subscription growth, derivatives
and institutional share gains, and GAAP profitability. Invalidate if crypto activity contracts,
stablecoin revenue or counterparty economics weaken, fees compress, custody or credit losses occur,
regulation limits products, or equity compensation absorbs per-share cash generation.

## Disposition

Status: **watching**, confidence **medium**, rating **Sell**, portfolio action **Avoid**, and
allocation eligibility **ineligible**. Review by **2026-08-23**, or earlier after material results,
rate or stablecoin-partner changes, custody or regulatory events, or a price move that materially
changes the scenario frontier. No strategy or signal is created because expected, base and bear
returns and margin of safety fail the canonical gate. See [[research-catalog]] for the maintained
research graph.
