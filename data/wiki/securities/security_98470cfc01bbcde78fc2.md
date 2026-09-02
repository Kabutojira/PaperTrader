---
title: SoFi Technologies, Inc. common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-05"
updated: "2026-09-02"
provenance: "source_sofi_q2_2026_10q; source_sofi_q2_2026_results"
security_id: security_98470cfc01bbcde78fc2
issuer_id: issuer_415865699c92fc5218dd
confidence: medium
next_review: "2026-10-02"
---

# SoFi Technologies, Inc. common stock

## Identity

- Immutable security: `security_98470cfc01bbcde78fc2`
- Issuer: `issuer_415865699c92fc5218dd`
- Instrument: common stock, Nasdaq Global Select Market (`XNAS`), USD
- Provider identity: `SOFI` / `XNAS` / `USD` / equity

SoFi combines a regulated digital bank, consumer lending, brokerage and payments products, a loan-platform business, and enterprise financial technology. Its broad financial-services model is comparable in part with [[securities/security_1e8fbdb0f45f2b413e00|PayPal]], while its regulated balance sheet and credit exposure require a financial-company valuation rather than a generic technology revenue multiple. No accepted causal relationship currently links to SoFi; [[ideas/idea_digital_finance_crypto_rails]] is a candidate pending bounded relationship review.

## Economics and thesis

The investable thesis is that low-cost deposits, product cross-buy, member growth, and fee-based services can compound book value and earnings while reducing reliance on warehouse funding. The contrary case is that rapid personal-loan growth, fair-value accounting, credit normalization, equity dilution, regulation, and technology-platform client concentration can make headline growth less durable or less valuable per share.

The SEC-filed second-quarter release reported record GAAP net revenue of about USD 1.2 billion, up 43% year over year, adjusted EBITDA of USD 357.8 million, and GAAP net income of USD 156.6 million or USD 0.12 per diluted share. Members reached 15.8 million, products 24.4 million, and 51% of new products were opened by existing members. Financial Services segment revenue rose 29% to USD 466.3 million, while Technology Platform revenue was USD 84.5 million and remained 23% below the prior-year quarter after a large client transition.

## Evidence and decision gates

| Evidence | Interpretation |
| --- | --- |
| Total deposits reached USD 45.54 billion and represented more than 90% of average liabilities; the average deposit rate was 156 basis points below warehouse funding. | Deposit scale supports funding resilience and net-interest economics, but rate competition remains a risk. |
| CET1 and Tier 1 risk-based capital ratios were an estimated 18.7%, versus stated required minimums of 7.0% and 8.5%. | Regulatory capital is currently strong and provides a buffer against credit normalization. |
| Personal-loan annualized net charge-offs were 2.62%, but the fair-value model's weighted-average annual default assumption rose to 4.77% from 4.57% in the prior quarter. | Reported credit performance improved, while forward model assumptions and rapid loan growth require caution. |
| Quarter-end book value was USD 8.58 per share and tangible book value USD 7.34, up 56% year over year; diluted weighted-average shares were about 1.352 billion. | Book-value growth is material, but the valuation must preserve dilution and intangible-value uncertainty. |
| Management raised 2026 adjusted-net-revenue guidance to USD 4.75-4.85 billion. | Guidance and cross-buy are catalysts; adjusted measures do not replace GAAP earnings, credit, or capital analysis. |

Primary evidence is the [Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1818874/000181887426000054/sofi-20260630.htm) as `source_sofi_q2_2026_10q` and the [SEC-filed Q2 2026 results exhibit](https://www.sec.gov/Archives/edgar/data/1818874/000181887426000050/a2026q2earningsrelease.htm) as `source_sofi_q2_2026_results`, both checked 2 September 2026. The 10-Q confirms USD 1.219 billion of Q2 net revenue, USD 156.6 million of net income, USD 45.54 billion of deposits, a 15.3% SoFi Bank total risk-based capital ratio, and a weighted-average personal-loan default assumption of 4.8% versus 4.5% at year-end.

## Valuation

The `financial_company` template uses a 12-month `price_to_book` method because regulatory capital, funding mix, asset quality, and book-value compounding are central. At the 1 September close of USD 17.049999237060547, the shares traded at about 1.99 times June book value and 2.32 times tangible book value; the latest canonical USD/EUR rate was 0.8623999953269958 on 2 September. Scenarios normalize credit costs, required capital, continuing dilution, and sustainable return on equity:

| Scenario | Probability | Fair value | Assumptions |
| --- | ---: | ---: | --- |
| Bear | 30% | USD 11.25 | Twelve-month book value reaches about USD 9.00 but credit costs rise, personal-loan growth slows, fee growth weakens, and the multiple compresses to 1.25x. |
| Base | 50% | USD 20.90 | Book value reaches about USD 9.50 as profitable growth continues; normalized credit remains manageable and a 2.2x multiple reflects strong growth but only developing through-cycle returns. |
| Bull | 20% | USD 32.00 | Book value reaches about USD 10.00 as cross-buy, deposits, fee revenue, and operating leverage exceed plan; stable credit and stronger sustainable returns support a 3.2x multiple. |

Probability-weighted fair value remains USD 20.225, about 18.62% above the mark. Medium confidence reduces the expected return to about 13.97%. Although the base case offers about 22.58% upside, the approximately 34.02% bear downside leaves the base-upside-to-bear-downside ratio below the configured minimum. The lower price improves value but does not meet the full allocation gate.

## Alert review, catalysts, and risks

From 26 August through 1 September the close fell from USD 18.84 to USD 17.05. The 1 September close breached the USD 17.42 lower Bollinger band; RSI was a neutral 48.4, volume was not anomalous, and no SMA or MACD crossing accompanied the alert. No newer issuer filing or release explained the move. The alert is a **risk / watch** signal rather than a fundamental thesis break or standalone opportunity: the lower mark improves expected return, but bear-case payoff and relationship gates still fail.

Catalysts are delivery of raised 2026 guidance, sustained member and cross-buy growth, further fee-revenue diversification, stable net interest margin, continued book-value growth, and credit performance that remains within modeled assumptions. Risks are personal-loan concentration and recession sensitivity, default and charge-off normalization, fair-value estimation risk, deposit competition, regulation and capital requirements, Technology Platform client concentration, stock compensation and dilution, cyber and operational risk, and premium-multiple compression.

Invalidate the thesis if charge-offs or modeled defaults rise faster than risk-adjusted revenue, regulatory capital approaches required buffers, deposits lose funding advantage, member growth fails to produce durable GAAP earnings and book value per share, Technology Platform economics continue to contract without offsetting diversification, or dilution absorbs operating progress.

## Disposition

Status: **watching**, confidence **medium**. Growth, profitability, deposits, capital, and liquidity are strong enough for complete comparison, but scenario downside, the weak bear/base payoff, valuation sensitivity, and absence of an accepted relationship keep the security allocation-ineligible at Watch. Review by **2026-10-02**, or sooner after a material credit, capital, client, guidance, or scenario-range event. No conviction strategy, signal, or paper order is justified.

## Changes since prior review

- **Facts and evidence changed:** the Q2 Form 10-Q supersedes Q1 as the latest complete filing and confirms the results exhibit. The alert-window mark fell to USD 17.05 and breached its lower Bollinger band without a new issuer event.
- **Assumptions changed:** profitability and deposit assumptions remain supported. The filing confirms Technology Platform contraction, a higher personal-loan default assumption, larger debt, and lower consolidated capital ratios as offsets.
- **Valuation inputs and outputs:** the USD 11.25/USD 20.90/USD 32.00 scenarios and 30%/50%/20% probabilities are unchanged because the complete filing validates both the book-value base and the offsetting risks. The lower mark raises weighted expected return from 8.16% to 18.62% and the confidence-adjusted return to 13.97%; base/bear payoff remains inadequate.
- **Thesis, catalysts, and risks:** the causal thesis and medium confidence are unchanged. The alert is risk/watch rather than evidence of a new fundamental catalyst. Credit, capital, Technology Platform concentration, funding, regulation and dilution remain monitored.
- **Blockers, gaps, rating, and action:** no hard research blocker applies. The weak downside payoff and missing accepted relationship remain. Status stays watching with no strategy or signal.
- **Conclusions unchanged:** strong growth and profitability do not yet provide enough downside protection for a paper position.

## Related ideas

- **Candidate — [[ideas/idea_digital_finance_crypto_rails]]; positive direction:** SoFi's integrated brokerage, crypto, payments, deposits and Galileo infrastructure could convert migration toward digital financial rails into more products per member, fee revenue and infrastructure economics. The filings show newly disaggregated crypto activity and Financial Services growth. Invalidate if adoption fails to improve consolidated per-member economics, regulatory costs overwhelm fee gains, or Technology Platform contraction prevents infrastructure monetization. This is not an accepted edge.
- **Rejected — [[ideas/idea_ai_native_smb_financial_operating_systems]]:** current primary evidence does not establish material exposure to AI-native small-business system-of-record adoption. The association is thematic rather than a demonstrated causal transmission mechanism.

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
  "security_id": "security_98470cfc01bbcde78fc2",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_98470cfc01bbcde78fc2.csv",
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

Filed quarterly results show revenue growth alongside positive but slightly lower sequential net income.

```echart
{
  "schema_version": 1,
  "chart_id": "sofi-quarterly-revenue-and-income",
  "kind": "series",
  "title": "Quarterly GAAP net revenue and net income",
  "description": "Sequential filed results show revenue growth while GAAP profitability remained positive.",
  "as_of": "2026-06-30",
  "sources": [{"label": "SoFi Q2 2026 Form 10-Q", "url": "https://www.sec.gov/Archives/edgar/data/1818874/000181887426000054/sofi-20260630.htm"}],
  "x_axis": {"type": "category", "label": "Quarter", "values": ["2026-Q1", "2026-Q2"]},
  "y_axes": [{"label": "USD millions", "unit": "USD millions", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "GAAP net revenue", "render": "bar", "y_axis": 0, "values": ["1100.368", "1218.676"]},
    {"name": "GAAP net income", "render": "line", "y_axis": 0, "values": ["166.731", "156.592"]}
  ],
  "notes": ["Quarterly values were converted from USD thousands to USD millions."]
}
```

The alert-window candles show the lower-band breach emerging after several declining sessions.

```echart
{
  "schema_version": 1,
  "chart_id": "sofi-bollinger-alert-window",
  "kind": "candlestick",
  "title": "SOFI price action during the Bollinger alert window",
  "description": "Daily unadjusted OHLC data show the four-session decline into the 2026-09-01 lower-band breach.",
  "as_of": "2026-09-01",
  "sources": [{"label": "Canonical PaperTrader yfinance price cache", "observed_at": "2026-09-02T14:26:30Z"}],
  "currency": "USD",
  "rows": [
    {"at": "2026-08-26", "open": "18.97", "close": "18.84", "low": "18.71", "high": "19.32", "volume": "36525600"},
    {"at": "2026-08-27", "open": "19.005", "close": "19.18", "low": "18.59", "high": "19.47", "volume": "37635800"},
    {"at": "2026-08-28", "open": "19.205", "close": "18.06", "low": "18.03", "high": "19.495", "volume": "45674400"},
    {"at": "2026-08-31", "open": "17.75", "close": "17.88", "low": "17.55", "high": "17.96", "volume": "36601500"},
    {"at": "2026-09-01", "open": "17.55", "close": "17.05", "low": "16.98", "high": "17.66", "volume": "41680300"}
  ],
  "notes": ["The deterministic indicator table records a 2026-09-01 lower Bollinger band of USD 17.42 and RSI of 48.4.", "yfinance is used only for paper marks and price monitoring, not fundamental evidence."]
}
```

The valuation remains sensitive to the downside multiple despite the lower reference mark.

```echart
{
  "schema_version": 1,
  "chart_id": "sofi-valuation-scenarios",
  "kind": "composition",
  "title": "Twelve-month price-to-book valuation scenarios",
  "description": "Bear, base and bull fair values retain explicit probabilities around approximately USD 8.58 of June-quarter book value per share.",
  "as_of": "2026-09-01",
  "sources": [{"label": "SoFi Q2 2026 Form 10-Q", "url": "https://www.sec.gov/Archives/edgar/data/1818874/000181887426000054/sofi-20260630.htm"}, {"label": "Canonical PaperTrader SOFI mark", "observed_at": "2026-09-02T14:26:30Z"}],
  "display": "bar",
  "axis": {"label": "Fair value per share", "unit": "USD/share", "format": "currency", "currency": "USD"},
  "items": [
    {"label": "Bear (30%)", "value": "11.25", "entity_id": "security_98470cfc01bbcde78fc2"},
    {"label": "Base (50%)", "value": "20.90", "entity_id": "security_98470cfc01bbcde78fc2"},
    {"label": "Bull (20%)", "value": "32.00", "entity_id": "security_98470cfc01bbcde78fc2"}
  ],
  "notes": ["The 2026-09-01 reference close was USD 17.05; scenario values are assumptions, not observed market prices."]
}
```

Omissions: no peer chart was retained because no like-for-like set with a common instrument scope, date and valuation definition was available in the bounded evidence. Cash-flow charting was omitted because bank-style loan-acquisition cash flows are not comparable to industrial free cash flow.
