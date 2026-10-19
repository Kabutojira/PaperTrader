---
title: SoFi Technologies, Inc. common stock
type: security
status: maintained
tags: [security, research, supported-valuation]
created: "2026-08-05"
updated: "2026-10-19"
provenance: "source_web_88eeb0fd80049ab692b75785; source_sofi_ir_quarterly_results_20261018; source_web_7ae11d88d3de9458d8f05a7c"
security_id: security_98470cfc01bbcde78fc2
issuer_id: issuer_415865699c92fc5218dd
confidence: low
next_review: "2026-11-18"
---

# SoFi Technologies, Inc. common stock

## Research conclusion

**Supported, low-confidence 12-month valuation as of 2026-10-19:** bear **USD 8.75** (30%), base **USD 16.00** (50%), and bull **USD 24.75** (20%).

The valuation is restored after an accessible issuer-authored [Q2 2026 results release](https://markets.financialcontent.com/stocks/article/bizwire-2026-7-29-sofi-reports-second-quarter-2026-with-record-net-revenue-of-12-billion-record-member-and-product-growth-net-income-of-157-million) (`source_web_88eeb0fd80049ab692b75785`) provided current earnings, tangible book value, funding, growth, and guidance evidence. SoFi's official [quarterly-results page](https://investors.sofi.com/financials/quarterly-results/default.aspx) (`source_sofi_ir_quarterly_results_20261018`) was also reopened, although its dynamically populated report list was absent from the retrieved text.

Confidence remains low because direct retrieval of the supplied Form 10-Q and SEC earnings-release exhibit returned HTTP 403 errors. The accessible release does not substitute for detailed filing disclosures on credit performance, regulatory capital, fair-value assumptions, or dilution.

## Identity reconciliation

- Immutable security ID: `security_98470cfc01bbcde78fc2`
- Immutable issuer ID: `issuer_415865699c92fc5218dd`
- Supplied instrument: SoFi Technologies, Inc. common stock
- Supplied ticker and provider symbol: `SOFI`
- Supplied venue MIC: `XNAS`
- Supplied currency: `USD`

The release identifies SoFi Technologies, Inc. and NASDAQ ticker SOFI, reports dollar-denominated results, and reports earnings attributable to common stockholders. This is consistent with the supplied identity. The accessible evidence does not independently state the `XNAS` MIC code, so that field is retained without claiming new verification. No identity change is proposed.

## Business economics and evidence

SoFi combines consumer lending and deposit-funded banking with consumer financial products and enterprise financial technology. The economic thesis is that deposits lower funding costs, while an integrated product set increases engagement, cross-buy, fee revenue, and customer lifetime value.

The Q2 release reports:

- GAAP net revenue of USD 1.219 billion, up 43% year over year.
- GAAP net income of USD 156.6 million and diluted EPS of USD 0.12.
- Equity of USD 11.1 billion and book value per share of USD 8.58.
- Tangible book value of USD 9.5 billion and tangible book value per share of USD 7.34, up 56% year over year.
- Average deposits representing more than 90% of average liabilities.
- An average deposit rate 156 basis points below warehouse-facility funding.
- Fee-based revenue of USD 472.3 million, or 39% of quarterly revenue.
- Members of 15.8 million and products of 24.4 million, with 51% of new products opened by existing members.
- Raised 2026 adjusted net revenue guidance of USD 4.75 billion to USD 4.85 billion.

These facts support improving profitability, funding economics, and diversification. They do not establish that current growth or credit performance is sustainable through a weaker consumer cycle.

## Contrary evidence and unresolved risks

The same release reports USD 14.8 billion of total quarterly originations, including USD 10.7 billion of personal-loan originations. That scale makes unsecured-consumer credit a central risk even though management characterized credit as strong and consistent with expectations.

The accessible evidence did not provide detailed delinquency, net charge-off, vintage, expected-default, regulatory-capital, or loan fair-value tables. It also did not permit a full reconciliation of diluted shares, stock compensation, or subsequent issuance. Other downside mechanisms include loss of the deposit funding advantage, adverse fair-value revisions, higher capital requirements, dilution, Technology Platform weakness, and multiple compression.

## Valuation method

Price-to-tangible-book is used because credit outcomes, funding costs, capital intensity, dilution, and sustainable returns on tangible equity drive SoFi's per-share economics. The reported USD 7.34 tangible book value per share at June 30, 2026 is the starting point.

The scenarios project tangible book value per share over 12 months and apply a multiple reflecting growth, capital, credit, and return quality:

| Scenario | Probability | Forward TBV/share | P/TBV | Fair value |
|---|---:|---:|---:|---:|
| Bear | 30% | USD 7.00 | 1.25x | USD 8.75 |
| Base | 50% | USD 8.00 | 2.00x | USD 16.00 |
| Bull | 20% | USD 9.00 | 2.75x | USD 24.75 |

The mechanical calculations were independently executed at the [scenario arithmetic endpoint](https://api.mathjs.org/v4/?expr=%5B7*1.25%2C8*2%2C9*2.75%5D) (`source_web_7ae11d88d3de9458d8f05a7c`): USD 7.00 × 1.25 = USD 8.75; USD 8.00 × 2.00 = USD 16.00; and USD 9.00 × 2.75 = USD 24.75.

The probabilities total 100%. The base case receives the greatest weight because current profitability and funding progress are verified, while the bear receives a substantial 30% weight because filing-level credit and capital evidence is missing. The bull is limited to 20% because recent tangible-book growth should not be extrapolated without evidence of sustainable through-cycle returns.

## Scenario assumptions

### Bear — USD 8.75, 30%

Tangible book value per share falls to USD 7.00 as credit normalization, dilution, or adverse fair-value changes offset retained earnings. A 1.25x multiple reflects weaker growth, uncertain through-cycle returns, and a diminished funding advantage.

### Base — USD 16.00, 50%

Tangible book value per share reaches USD 8.00 as continued profitability exceeds dilution and normalized credit costs. A 2.00x multiple assumes that deposit funding remains advantageous and that cross-buy and fee revenue make earnings more durable, without extrapolating the reported 56% tangible-book growth rate.

### Bull — USD 24.75, 20%

Tangible book value per share reaches USD 9.00 as earnings remain strong, credit stays controlled, and fee diversification improves. A 2.75x multiple requires durable high growth and improving returns on tangible equity.

## Catalysts

- Continued GAAP profitability and tangible-book-value-per-share growth.
- Credit outcomes that remain within disclosed underwriting assumptions.
- Preservation of the deposit funding advantage.
- Execution against raised 2026 revenue guidance.
- Greater fee-revenue diversification and productive member cross-buy.
- An accessible filing showing strong regulatory-capital headroom, stable delinquencies and charge-offs, and a reconciled diluted share count.

## Invalidation conditions

Invalidate the base thesis if subsequent primary filings show:

- Tangible book value per share falling materially below the USD 7.00 bear assumption.
- Delinquencies, charge-offs, or expected defaults rising faster than risk-adjusted revenue.
- Regulatory capital constraining growth.
- Deposits losing their meaningful cost advantage over warehouse funding.
- Dilution persistently absorbing retained earnings.
- Member and product growth failing to produce durable GAAP earnings.

The numerical valuation must also be withdrawn if the USD 7.34 starting tangible book value per share cannot be reconciled to an accessible filing.

## Confidence and limitations

Confidence is **low**. The issuer-authored release supports a transparent scenario valuation, but the underlying Form 10-Q was inaccessible. Regulatory capital ratios, credit vintages, delinquencies, charge-offs, fair-value assumptions, stock compensation, and subsequent issuance remain insufficiently verified. Forward tangible-book values and valuation multiples are analyst assumptions, not company guidance.

## Changes since prior review

- Preserved the immutable security and issuer IDs.
- Reopened the supplied Q2 2026 SEC leads; both returned HTTP 403 errors and are not cited as current evidence.
- Opened an accessible issuer-authored Business Wire release carrying the Q2 results.
- Verified current earnings, tangible book value per share, funding economics, operating growth, and guidance from that release.
- Filled all missing bear/base/bull fair values and probabilities with explicit per-share arithmetic.
- Changed research status from `valuation_unsupported` to `supported` while retaining low confidence because filing-level evidence remains incomplete.
- Added no relationship because no valid counterpart entity was supplied.
