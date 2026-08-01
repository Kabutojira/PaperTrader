---
title: "Amazon.com, Inc. common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-08-01"
updated: "2026-08-01"
provenance: "source_amzn_q2_2026_10q|source_amzn_q2_2026_results"
security_id: security_2433a056eb0c55961fcc
issuer_id: issuer_85fa8ff84ea190add8f0
ticker: AMZN
venue_mic: XNAS
provider_symbol: AMZN
currency: USD
confidence: medium
next_review: "2026-08-31"
---

# Amazon.com, Inc. common stock

## Decision

**Watch; no conviction strategy.** Amazon's Q2 2026 operating evidence is strong: consolidated
sales grew 20%, operating income grew 43%, and AWS sales grew 37%. The July 31 repricing is
consistent with the prior evening's results, but the USD 271.58 mark is already slightly above the
USD 270 base case. Trailing free cash flow turned negative as AI infrastructure investment surged,
long-term debt increased, and the scenario-weighted return is only about 1.3%. The breakout is a
positive fundamental repricing and adverse entry timing, not a paper-trade opportunity.

## Immutable identity

- Security ID: `security_2433a056eb0c55961fcc`
- Issuer ID: `issuer_85fa8ff84ea190add8f0`
- Instrument: Amazon.com, Inc. common stock
- Listing: Nasdaq Global Select Market (`XNAS`)
- Provider symbol: `AMZN`
- Currency: `USD`

The SEC filing cover identifies Amazon common stock as `AMZN` on Nasdaq, consistent with the
canonical issuer, instrument, venue, currency, and provider identity. No duplicate immutable
identity is present in the security table.

## Alert review

The deterministic alerts comprise two distinct market dates:

- On July 30, volume reached **101,839,800 shares**, entering a volume anomaly while the adjusted
  close was USD 235.50 and the July 1–30 return was **-2.57%**. The earnings release followed that
  session's close, so it cannot explain the same-session volume anomaly; no contemporaneous primary
  filing establishes a cause. This earlier signal is unexplained attention rather than a trade case.
- On July 31, the first regular session after results, the adjusted close rose **15.32%** to
  **USD 271.58** on **128,881,300 shares**. The July 2–31 return reached **11.91%**, the close ended
  **2.99% above** the upper Bollinger band, and MACD crossed above its signal.
- The canonical July 31 indicator row reports RSI **67.88**, a **3.42** volume z-score, and source
  price hash `b81fd0db00c2f4206bc6e0d6d5704687c29289da6da636fee699dffb9269df93`.

The July 31 move is materially explained by the July 30 after-close release: sales and operating
income exceeded the prior-year quarter, AWS accelerated, and Q3 operating-income guidance remained
well above the prior-year comparator. The repricing supports the business thesis, but it moved the
shares beyond the base fair value and therefore increases valuation and timing risk.

## Business and financial evidence

Q2 net sales rose 20% to USD 200.606 billion and operating income rose 43% to USD 27.461 billion.
North America, International, and AWS sales grew 16%, 15%, and 37%; segment operating income was
USD 9.1 billion, USD 1.7 billion, and USD 16.6 billion. AWS supplied about 60% of segment operating
income, demonstrating both attractive economics and material concentration in the highest-margin
engine. Third-quarter guidance calls for USD 197–202 billion of sales and USD 22.5–26.5 billion of
operating income.

Reported Q2 net income of USD 62.647 billion is not a suitable recurring earnings anchor because it
included USD 53.4 billion of non-operating pre-tax income, primarily an observable-value increase
in Amazon's Anthropic investment. The scenario valuation therefore normalizes from operating
income, recurring taxes, financing costs, stock compensation, and diluted shares rather than
capitalizing that investment mark.

Trailing-twelve-month operating cash flow rose 33% to USD 161.403 billion, but property purchases
net of proceeds and incentives increased to USD 169.007 billion, producing a USD 7.604 billion free-
cash-flow outflow. Cash capital expenditure was USD 96.3 billion in the first half, primarily for
technology infrastructure supporting AWS and fulfillment capacity, and management expects these
investments to increase in 2026. The reinvestment runway is substantial, but cash returns must
follow.

At June 30, cash and marketable securities totaled USD 122.988 billion versus USD 128.894 billion of
long-term debt and USD 94.338 billion of long-term lease liabilities. Liquidity remains supported by
large operating cash flow, but net financial strength is no longer a clear downside cushion.
Amazon had 10.783 billion common shares outstanding at quarter-end and 244.4 million restricted
stock units outstanding, making dilution an explicit per-share consideration.

## Thesis, contrary evidence, catalysts, and invalidation

The constructive thesis is that Amazon combines high-frequency consumer distribution, third-party
seller services, advertising, subscriptions, and cloud infrastructure. AWS growth and margin,
retail operating leverage, advertising monetization, delivery speed, and a broad customer base can
compound operating earnings while AI services extend the cloud runway. Current segment sales and
operating-income growth strongly support that mechanism.

Contrary evidence is that AWS now contributes most segment operating profit while the company is
funding a very large, long-lived AI capacity build before utilization and pricing are fully proven.
Negative trailing free cash flow, higher debt and lease obligations, energy-contract valuation,
competition, regulation, labor and logistics costs, cybersecurity, third-party seller quality,
foreign exchange, and stock compensation can impair per-share conversion. The Anthropic mark makes
reported net income unusually non-recurring and should not be treated as operating quality.

Catalysts are sustained AWS growth, stronger retail margins, advertising growth, successful AI-chip
and model monetization, improving utilization, and a return to positive free cash flow without
slowing the business. Invalidate or materially downgrade the thesis if AWS growth or margins weaken
without lower investment, retail margins reverse, AI capacity remains underutilized, operating cash
conversion deteriorates, leverage or dilution rises materially, or regulatory, security, labor,
energy, or capital-allocation failures impair per-share economics.

## Valuation

The selected repository template is `mature_compounder`, using an `earnings_multiple` method. It
normalizes the non-cash Anthropic gain, recurring taxes, financing costs, stock compensation,
capital intensity, debt, and diluted shares. At USD 271.58, the shares represent roughly USD 2.93
trillion of equity value using the July 22 share count. The 12-month scenarios are:

- **Bear (25%): USD 200.00.** USD 8.00 normalized forward EPS at 25x; AWS growth slows, retail costs
  rise, and AI depreciation and financing costs pressure per-share earnings. Return: **-26.4%**.
- **Base (50%): USD 270.00.** USD 9.00 normalized forward EPS at 30x; AWS and advertising remain
  strong while AI investment absorbs cash and limits multiple expansion. Return: **-0.6%**.
- **Bull (25%): USD 360.00.** USD 10.00 normalized forward EPS at 36x; AWS growth and retail margins
  persist and AI infrastructure converts rapidly into durable revenue and cash flow. Return:
  **+32.6%**.

The probability-weighted value is USD 275.00, for about **1.3% expected return** and **0.9%
confidence-adjusted expected return**. The configured 20% margin-of-safety buy-below price is USD
216.00. Base upside, expected return, margin of safety, timing, and the absent accepted canonical
relationship fail the full strategy gate. The assessment is therefore ineligible for allocation and
does not justify conviction strategy research.

## Changes since prior review

This is the first completed security review and first scenario-complete assessment; no prior
security page, assessment version, rating, or portfolio action exists to overwrite or contradict.

- **Evidence:** newly establishes the Q2 Form 10-Q, Q2 results release, July 30 and July 31 alert
  states, fresh USD mark, and fresh USD/EUR identity.
- **Assumptions and valuation:** newly establishes the mature-compounder earnings-multiple method,
  operating-earnings normalization, USD 200/270/360 scenarios, 25%/50%/25% probabilities, and USD
  216 buy zone.
- **Thesis and contrary evidence:** newly establishes strong AWS, retail, and advertising economics,
  offset by AI capital intensity, concentration, leverage, negative free cash flow, and dilution.
- **Catalysts, risks, blockers, and gaps:** no hard blocker is asserted; medium confidence, weak
  entry timing, low expected return, inadequate base upside, cash conversion, and absent accepted
  relationship are explicit gaps.
- **Rating and action:** the initial disposition is watch/ineligible with no paper-trade action and
  no conviction strategy follow-up.
- **Unchanged conclusions:** none, because there is no prior accepted review.

## Sources

- [Amazon Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm)
  (`source_amzn_q2_2026_10q`, checked 2026-08-01).
- [Amazon Q2 2026 results](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000024/amzn-20260630xex991.htm)
  (`source_amzn_q2_2026_results`, checked 2026-08-01).
- Canonical market and indicator state: `data/market/latest.csv`, `data/market/indicators.csv`, and
  `data/market/prices/security_2433a056eb0c55961fcc.csv`, retrieved `2026-08-01T09:07:38Z`;
  USD/EUR FX was retrieved at the same time.
- Alert packets: [[inbox/market-security_2433a056eb0c55961fcc-volume_anomaly-e61b5356f36f|AMZN volume anomaly]],
  [[inbox/market-security_2433a056eb0c55961fcc-bollinger_above_upper-0d1101e5c09b|AMZN upper-Bollinger transition]],
  and [[inbox/market-security_2433a056eb0c55961fcc-macd_cross_above_signal-f8b94c946cb3|AMZN bullish MACD transition]].

Next review: **2026-08-31**, or sooner after material AWS growth, retail-margin, AI utilization,
capital-spending, free-cash-flow, leverage, dilution, regulatory, security, or capital-allocation
evidence.

[[security-catalog|Tracked securities]] · [[research-catalog|Research catalog]] · [[index|Today's decision]]
