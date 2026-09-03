---
title: "Robinhood Markets, Inc. Class A common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-08-01"
updated: "2026-08-22"
provenance: "source_hood_q2_2026_10q|source_hood_q2_2026_results|source_hood_sec_submissions_20260822"
security_id: security_ad3b1f8f59fd599f079a
issuer_id: issuer_5deb5665eaa22bd5dbbe
ticker: HOOD
venue_mic: XNAS
provider_symbol: HOOD
currency: USD
confidence: medium
next_review: "2026-09-21"
---

# Robinhood Markets, Inc. Class A common stock

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
  "security_id": "security_ad3b1f8f59fd599f079a",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_ad3b1f8f59fd599f079a.csv",
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

**Avoid at the current price; no conviction strategy.** Robinhood's Q2 evidence still shows rapid
asset, deposit, customer, subscription, transaction-revenue, and adjusted-EBITDA growth. It also
shows material cyclicality and valuation risk: cryptocurrency revenue fell, expenses and
credit-loss provisions increased, and quarterly earnings included a large deconsolidation gain.
The 21 August volume surge carried the shares to USD 108.13, above the unchanged USD 69 base case
and USD 73.23 probability-weighted value and close to the USD 112.50 bull case.

## Changes since prior review

- **Evidence:** a current SEC submissions index shows no operating filing after the Q2 Form 10-Q;
  filings from 3 through 21 August are Forms 3, 4, and 144. The Q2 filing and results release remain
  the latest primary operating evidence.
- **Market evidence:** the canonical alert period changed to 24 July through 21 August. The close
  rose 13.93% from USD 94.91 to USD 108.13, and the final session rose 13.70% on 50.23 million
  shares, entering the configured volume anomaly. Current indicators also place the close above the
  upper Bollinger band.
- **Assumptions and scenarios:** June book value, normalized credit costs, funding, dilution, and
  the USD 42.40/USD 69.00/USD 112.50 scenarios with 25%/50%/25% probabilities are unchanged because
  no later operating filing provides a sound basis to revise them.
- **Thesis, catalysts, risks, blockers, and gaps:** the asset-gathering and product-expansion thesis,
  catalysts, invalidation conditions, and principal trading, crypto, credit, regulatory, custody,
  concentration, debt, and dilution risks are unchanged. Valuation and timing gaps worsened; there
  is still no hard blocker.
- **Rating and action:** Sell / Avoid and allocation ineligibility are unchanged. The rally is
  valuation and timing risk rather than primary-evidence confirmation, so no strategy is justified.

## Immutable identity

- Security ID: `security_ad3b1f8f59fd599f079a`
- Issuer ID: `issuer_5deb5665eaa22bd5dbbe`
- Instrument: Robinhood Markets, Inc. Class A common stock
- Listing: Nasdaq Global Select Market (`XNAS`)
- Provider symbol: `HOOD`
- Currency: `USD`

The SEC filing matches Robinhood Markets, Inc., its Class A common shares and the canonical `HOOD`
Nasdaq identity. No duplicate issuer-instrument-venue-currency-provider identity exists in the
canonical security table.

## Alert review

The payload's canonical observation period is 2026-07-24 through 2026-08-21:

- The adjusted close rose from USD 94.91 to USD 108.13, a **13.93%** increase.
- On 21 August the close rose **13.70%** from the prior session on 50,228,800 shares. The configured
  volume-anomaly strength entered at 0.732882585 from zero.
- The current deterministic indicator row records the close above the USD 102.88 upper Bollinger
  band, RSI at 62.50, and a positive MACD histogram. These measurements describe strong momentum;
  they do not establish a change in intrinsic value.
- The SEC submissions index contains no operating filing after the Q2 Form 10-Q. It therefore does
  not provide current primary evidence that explains the rally or changes the operating outlook.

The alert is **risk**, not an opportunity. Price and volume accelerated without a newer operating
filing, while the mark moved materially farther above base and probability-weighted value. A market
move alone cannot support higher book-value assumptions or multiples.

## Business and financial evidence

Robinhood combines self-directed brokerage, options, cryptocurrency, futures and event contracts,
margin and securities lending, cash products, subscriptions, retirement, advisory custody, credit,
and expanding international services. Scale and product breadth can lower customer acquisition cost,
increase wallet share, and diversify revenue beyond episodic equity trading.

Q2 total net revenue rose 32% year over year to USD 1.308 billion. Transaction revenue rose 44% to
USD 776 million, including USD 156 million from event contracts, USD 342 million from options and
USD 129 million from equities. Cryptocurrency revenue fell 38% to USD 100 million, demonstrating
that rapid product expansion has not removed cycle and mix sensitivity. Net interest revenue rose 9%
to USD 389 million.

Funded customers rose 7% to 28.4 million, total platform assets rose 32% to USD 368.7 billion, Q2 net
deposits were USD 21.7 billion, Gold subscribers rose 39% to 4.84 million, and ARPU rose 24% to USD
187. These are strong indicators of customer acquisition, asset gathering, and monetization.

Quarterly net income attributable to Robinhood was USD 561 million and diluted EPS was USD 0.62,
but USD 129 million, or USD 0.14 per diluted share, came primarily from deconsolidating Robinhood
Ventures Fund I. Operating expenses rose 33% to USD 734 million, provision for credit losses doubled
to USD 56 million, and Q2 stock compensation was USD 105 million. Adjusted EBITDA rose 35% to USD
741 million, though that measure excludes stock compensation and restructuring charges.

At June 30 Robinhood held USD 5.362 billion of cash, USD 2.170 billion of long-term borrowings and USD
9.541 billion of stockholders' equity. The convertible-note proceeds increased both cash and debt.
The broker-dealer and futures subsidiaries reported substantial excess regulatory capital and were
in compliance, supporting balance-sheet resilience. Customer-related assets, segregation balances,
securities lending, margin receivables, and payables make consolidated cash flow and leverage less
comparable with a non-financial company.

## Thesis, contrary evidence, catalysts, and invalidation

The thesis is that Robinhood can compound per-share value by attracting assets faster than the
market, converting more customers to subscriptions and adjacent products, and spreading technology
and compliance costs across a larger platform. Current deposit, platform-asset, customer, Gold,
transaction-revenue, and adjusted-EBITDA growth support that mechanism.

Contrary evidence includes crypto and trading cyclicality, interest-rate sensitivity, market-maker
and exchange concentration, credit losses, customer and counterparty exposures, regulatory capital
constraints, product and international execution risk, stock compensation, and the risk that fast
product launches increase compliance or operational failures. Citadel Securities represented 16%
of Q2 revenue, while 47% of total revenue came from all market makers and exchanges collectively.
Robinhood also reduced its workforce by about 10% in June while accelerating product launches.

Potential catalysts are sustained net deposits, Gold and advisory adoption, profitable international
expansion, durable event-contract economics, normalized crypto activity, and repurchases below
intrinsic value. The thesis would be invalidated by persistent net outflows, material customer loss,
regulatory-capital pressure, a major custody, clearing or cybersecurity failure, adverse restrictions
on payment-for-order-flow, crypto or event-contract activities, structurally higher credit losses,
or dilution and acquisition spending that prevent operating growth from compounding book value per
share.

## Valuation

A 12-month `financial_company` price-to-book valuation uses June stockholders' equity of USD 9.541
billion and 899 million basic shares, or about USD 10.61 book value per share. Scenario book value
and multiples normalize the USD 129 million RVI deconsolidation gain, credit costs, rate sensitivity,
trading and crypto cyclicality, regulatory capital, convertible debt, acquisitions, repurchases, and
stock compensation:

- Bear, 25%: USD **42.40**, or 4.0x USD 10.60 forward book value, as net-deposit growth slows,
  trading and crypto weaken, credit and compliance costs rise, and premium returns normalize.
- Base, 50%: USD **69.00**, or 6.0x USD 11.50 forward book value, as deposits and subscriptions grow,
  normalized profitability remains strong, and book value compounds despite stock compensation.
- Bull, 25%: USD **112.50**, or 9.0x USD 12.50 forward book value, as product breadth, international
  scale, asset gathering, and capital returns sustain unusually high growth and returns on equity.

At the prior review's USD 86.56 mark, the cases implied **-51.0%**, **-20.3%**, and **+30.0%**.
Probability-weighted fair value was USD 73.23, approximately **15.4% below** that mark before the
deterministic confidence adjustment. The 20% margin-of-safety buy zone was USD 55.20.

Against the current USD 108.13 mark, those unchanged cases imply approximately **-60.8%**, **-36.2%**,
and **+4.0%**. Probability-weighted value is **32.3% below** the mark before confidence adjustment,
and the USD 55.20 buy zone remains unreached. The higher price worsens expected return, base return,
downside payoff, margin of safety, and timing.

## Idea exposure map

- **Candidate — positive but cyclical:** [[ideas/idea_digital_finance_crypto_rails|Digital finance
  and crypto rails]]. Robinhood's cryptocurrency, custody, brokerage, transaction, subscription,
  and adjacent financial-product distribution create a specific transmission mechanism from wider
  regulated digital-finance adoption to customer activity and monetization. Q2 cryptocurrency
  revenue fell 38%, however, showing material cycle sensitivity. This is not a canonical accepted
  relationship; a separate relationship review must test materiality, regulation, custody controls,
  take-rate durability, and invalidation.
- Other maintained ideas were evaluated and rejected as thematic rather than causal: Robinhood has
  no evidenced material operating transmission from AI infrastructure, power, defense, space,
  minerals, energy, healthcare, manufacturing, nuclear, solar, or semiconductor mechanisms.

## Sources

- [Robinhood Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1783879/000178387926000114/hood-20260630.htm)
  (`source_hood_q2_2026_10q`, checked 2026-08-01).
- [Robinhood Q2 2026 results](https://www.sec.gov/Archives/edgar/data/1783879/000178387926000113/q22026robinhoodexhibit991.htm)
  (`source_hood_q2_2026_results`, checked 2026-08-01).
- [Robinhood SEC submissions index](https://data.sec.gov/submissions/CIK0001783879.json)
  (`source_hood_sec_submissions_20260822`, checked 2026-08-22); no operating filing after the Q2
  Form 10-Q through the 21 August index update.
- Canonical market and indicator state: `data/market/latest.csv`, `data/market/indicators.csv`, and
  `data/market/prices/security_ad3b1f8f59fd599f079a.csv`, market date 2026-08-21 and retrieved
  2026-08-22.

Next review: **2026-09-21**, or sooner after a material regulatory, custody, credit, net-deposit,
capital, acquisition, product-economics, or market-structure development.

Related navigation: [[security-catalog|Securities]], [[signals|Signals and research alerts]], and
[[research-catalog|Research catalog]].
