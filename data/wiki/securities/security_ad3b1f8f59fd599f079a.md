---
title: "Robinhood Markets, Inc. Class A common stock"
type: security
status: watching
tags:
  - security
  - research
  - risk
created: "2026-08-01"
updated: "2026-08-01"
provenance: "source_hood_q2_2026_10q|source_hood_q2_2026_results"
security_id: security_ad3b1f8f59fd599f079a
issuer_id: issuer_5deb5665eaa22bd5dbbe
ticker: HOOD
venue_mic: XNAS
provider_symbol: HOOD
currency: USD
confidence: medium
next_review: "2026-08-31"
---

# Robinhood Markets, Inc. Class A common stock

## Decision

**Avoid at the current price; no conviction strategy.** Robinhood's Q2 evidence shows rapid asset,
deposit, customer, subscription, transaction-revenue, and adjusted-EBITDA growth. It also shows
material cyclicality and valuation risk: cryptocurrency revenue fell, expenses and credit-loss
provisions increased, quarterly earnings included a large deconsolidation gain, and the stock still
trades at about 8.2 times June book value after its decline. A bounded price-to-book valuation has a
USD 69 base case and USD 73.23 probability-weighted value versus the USD 86.56 mark.

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

The payload's canonical observation period is 2026-07-01 through 2026-07-30:

- The adjusted close fell from USD 108.65 to USD 86.60, a **20.29%** decline.
- The July 30 close was only **0.0238%** below the lower Bollinger band, creating the recorded
  `bollinger_below_lower` entry.
- Robinhood released Q2 results after the July 29 close. The first post-results session fell **3.61%**
  to USD 86.60, so the filing is relevant to the last part of the move but cannot explain the full
  month-long decline.
- The subsequent July 31 close was USD 86.56, above the recalculated USD 84.02 lower band. RSI was
  **35.97**, MACD remained below its signal line, and volume was not anomalous.

The alert is **risk**, not an oversold opportunity. The band breach was marginal and did not persist,
while Q2 disclosed a weaker crypto contribution, higher costs, a doubled credit-loss provision, and
a material non-operating gain inside reported earnings. Those facts plausibly contributed to the
post-results reset, but the broader decline also reflects prior elevated valuation and cannot be
assigned to one current primary-source event.

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

Against USD 86.56, the cases imply **-51.0%**, **-20.3%**, and **+30.0%**. Probability-weighted fair
value is USD 73.23, approximately **15.4% below** the mark before the deterministic confidence
adjustment. The 20% margin-of-safety buy zone is USD 55.20. The current mark therefore fails expected
return, base return, downside payoff, and margin-of-safety gates.

## Sources

- [Robinhood Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1783879/000178387926000114/hood-20260630.htm)
  (`source_hood_q2_2026_10q`, checked 2026-08-01).
- [Robinhood Q2 2026 results](https://www.sec.gov/Archives/edgar/data/1783879/000178387926000113/q22026robinhoodexhibit991.htm)
  (`source_hood_q2_2026_results`, checked 2026-08-01).
- Canonical market and indicator state: `data/market/latest.csv`, `data/market/indicators.csv`, and
  `data/market/prices/security_ad3b1f8f59fd599f079a.csv`, market date 2026-07-31 and retrieved
  2026-08-01.

Next review: **2026-08-31**, or sooner after a material regulatory, custody, credit, net-deposit,
capital, acquisition, product-economics, or market-structure development.

Related navigation: [[security-catalog|Securities]], [[signals|Signals and research alerts]], and
[[research-catalog|Research catalog]].
