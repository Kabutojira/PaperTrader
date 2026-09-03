---
title: Nebius Group N.V. Class A ordinary shares
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-05"
updated: "2026-08-18"
provenance: "source_nbis_q1_2026_financials; source_nbis_july_2026_secured_financing; source_nbis_q2_2026_results; source_nbis_q2_2026_financials"
security_id: security_47a0b06f6c6c478d7c1e
issuer_id: issuer_489b0bfd13a06e7d7874
confidence: medium
next_review: "2026-09-17"
---

# Nebius Group N.V. Class A ordinary shares

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
  "security_id": "security_47a0b06f6c6c478d7c1e",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_47a0b06f6c6c478d7c1e.csv",
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

- Immutable security: `security_47a0b06f6c6c478d7c1e`
- Issuer: `issuer_489b0bfd13a06e7d7874`
- Instrument: Class A ordinary shares, Nasdaq Global Select Market (`XNAS`), USD
- Provider identity: `NBIS` / `XNAS` / `USD` / equity

Nebius is an Amsterdam-headquartered full-stack AI cloud operator. It combines GPU compute,
networking, storage, managed services, and software, while the group also owns Avride and TripleTen
and holds investments in ClickHouse and Toloka. Its capacity buildout competes for the same AI
infrastructure demand served by [[securities/security_33d9c44facc75c726c7d|NVIDIA]] and the same
large-customer cloud budgets represented by [[securities/security_204be2a44063993de1a8|Microsoft]],
but no accepted canonical idea-security relationship currently exists for this instrument.

## Economics and thesis

The investable thesis is that scarcity of deployable AI infrastructure, a purpose-built software
stack, and long-duration contracts can let Nebius scale revenue faster than its capital base while
moving from capacity construction to durable positive cash economics. The contrary case is that the
market already capitalizes years of successful deployment: revenue remains concentrated, reported
cash generation is supported by customer advances, capacity is expensive and technologically
perishable, and debt, convertibles, warrants, and equity compensation can transfer growth away from
existing shares.

For the quarter ended 30 June 2026, group revenue rose 454% year over year to USD 582.3 million and
Nebius AI cloud revenue rose 514% to USD 574.9 million. Group adjusted EBITDA improved from a USD
21.0 million loss to positive USD 236.2 million, but continuing operations still lost USD 190.4
million. The business demonstrated exceptional utilization and operating leverage while remaining
capital-intensive: quarterly purchases of property, equipment, and intangible assets reached USD
5.6574 billion.

## Evidence and decision gates

| Evidence | Interpretation |
| --- | --- |
| Q2 group revenue reached USD 582.3 million and adjusted EBITDA reached positive USD 236.2 million. | Capacity and utilization are converting into revenue and operating leverage much faster than the Q1 scenario inputs assumed. |
| Cash was USD 8.0421 billion at 30 June against USD 8.5457 billion of current and non-current debt. | Liquidity remains substantial, but reported debt now exceeds cash and the capacity program still requires a financing-sensitive model. |
| Q2 operating cash flow was USD 2.2461 billion while purchases of property, equipment, and intangible assets were USD 5.6574 billion. | Customer funding helps liquidity, but the quarterly investment outlay far exceeded operating cash flow and is not mature free-cash-flow evidence. |
| Deferred revenue reached USD 5.9752 billion and Q2 share-based compensation reached USD 102.5 million. | Contract funding supports visibility, while delivery obligations and dilution remain economically material. |
| Issued and outstanding shares were 271,855,218 at 30 June, excluding 50,185,726 treasury shares. | The old roughly 309 million diluted denominator cannot simply be carried forward without reconciling current convertibles, warrants, awards, treasury shares, and diluted share count. |
| The 17 July facility provides about USD 775 million at SOFR plus 2.50%, due 31 October 2030, backed by deployed GPUs and contracted cash flow. | Asset-level funding can recycle capital, but adds secured leverage and depends on customer cash flows and GPU residual value. |
| Management cited more than USD 40 billion of additional contracted revenue and delivery progress to Microsoft. | Backlog supports growth visibility, but duration, capex intensity, delivery milestones, and customer concentration prevent treating contract value as current profit. |

Current primary evidence is the [SEC-filed Q2 results release](https://www.sec.gov/Archives/edgar/data/1513845/000110465926094568/tm2622968d1_ex99-1.htm)
as `source_nbis_q2_2026_results` and the [SEC-filed Q2 statements and notes](https://www.sec.gov/Archives/edgar/data/1513845/000110465926094844/nbis-20260812xex99d2.htm)
as `source_nbis_q2_2026_financials`, both checked 18 August 2026. The earlier Q1 statements and 17
July financing release remain historical context.

## Valuation

The refreshed `pre_profit_growth` revenue-multiple valuation uses Q2 operating scale, USD 8.0421
billion cash, USD 8.5457 billion current and non-current debt, and a conservative approximately 350
million fully diluted denominator. That denominator starts with 271.9 million issued and outstanding
shares and allows for the filing's 65.4 million anti-dilutive convertible-note shares, 10.0 million
anti-dilutive share awards, and 2.7 million unvested Eigen AI shares. It is deliberately more
conservative than both the reported basic share count and the old approximately 309 million Q1
diluted weighted average.

The twelve-month bear case assigns USD 75 per share to USD 4.5 billion forward revenue at about six
times enterprise value/revenue, modest net debt and approximately 350 million diluted shares. It
assumes deployment slippage, weaker utilization or pricing, continuing heavy capex and customer-
advance dependence, and full modeled dilution. The USD 165 base case uses USD 6.5 billion revenue at
about nine times, the same net-debt and diluted-share normalization, on-schedule contract conversion,
positive adjusted EBITDA but still negative free cash flow, and no major customer diversification.
The USD 325 bull case uses USD 10 billion revenue at about 11.5 times with the same conservative
capital structure; it requires timely capacity delivery, sustained utilization and margins,
efficient asset-backed funding, and improving customer breadth.

Probabilities of 25% / 50% / 25% produce USD 182.50 probability-weighted fair value. Against the
18 August USD 248.43 mark, deterministic bear/base/bull returns are -69.81% / -33.58% / 30.82%,
expected return is -26.54%, and medium-confidence-adjusted expected return is -19.90%. The USD 132
buy-below level applies the configured 20% discount to the USD 165 base case. This scenario set is
supportable but highly assumption-sensitive; it values operating acceleration while explicitly
normalizing capital intensity, net debt and dilution rather than treating contracted revenue as
current earnings.

## Alert review, catalysts, and risks

The payload-bound 14 July through 12 August period ended at USD 257.89, up 26.51%, with volume at
1.907 times its rolling baseline on the Q2-results date. By 18 August the close had eased 3.67% to
USD 248.43. RSI was a neutral 56.58 and MACD remained above its signal, so the alert is an
earnings-linked repricing with elevated expectation risk, not an independent buy signal. The Q2
evidence materially improves the operating checklist but also confirms extraordinary capital
intensity, leverage, customer-funding dependence, and dilution inputs that require full revaluation.

Catalysts are on-schedule capacity delivery, conversion of contracted revenue into recognized
revenue and cash margin, improved customer diversification, continued positive AI-cloud adjusted
EBITDA, disciplined asset-backed financing, and lower dilution than modeled. Risks are Microsoft
and Meta concentration, GPU and data-center construction execution, customer-credit and advance
accounting, rapid hardware obsolescence, power availability, competition and pricing, secured and
convertible debt, interest rates, share dilution, non-core venture exposure, and valuation-multiple
compression.

Invalidate the thesis if contracted deployments are delayed or repriced, utilization and gross
profit fail to scale with installed capacity, customer advances reverse without matching operating
cash generation, capex and financing outpace durable unit economics, secured claims materially erode
financial flexibility, dilution accelerates, or customers internalize workloads faster than Nebius
can broaden its base.

## Disposition

Status: **watching**, confidence **medium**, rating **Strong Sell / Avoid**. Q2 supports exceptional
growth and improving adjusted operating economics, but USD 182.50 probability-weighted value and a
USD 165 base case remain well below the USD 248.43 mark. Negative expected and base returns, poor
bear/base and expected/bear payoff, negative margin of safety, and the absence of an accepted
canonical relationship keep the security allocation-ineligible. Review by **2026-09-17**, or sooner
after material delivery, financing, customer-concentration or dilution evidence. No conviction
strategy, signal, or paper order is justified.

## Changes since prior review

- **Prior state:** the 18 August quick check withdrew stale Q1 scenarios, recorded Unrated / Watch at USD 248.43, and required this full review; the older 5 August review was Sell / Avoid at USD 225.74.
- **Facts and evidence:** the full review confirms Q2 revenue of USD 582.3 million, adjusted EBITDA of USD 236.2 million, a USD 190.4 million continuing-operations loss, USD 5.6574 billion quarterly capital purchases, USD 8.0421 billion cash, USD 8.5457 billion debt, USD 5.9752 billion deferred revenue, and 271.9 million basic shares plus material convertible and award dilution.
- **Assumptions and valuation:** valuation support is restored with conservative Q2-normalized USD 75 / USD 165 / USD 325 scenarios, replacing the old USD 75 / USD 170 / USD 340 Q1 set. The refreshed expected value is USD 182.50 and expected return is -26.54%; full modeled dilution and net debt offset faster operating growth.
- **Thesis, catalysts, and risks:** the thesis remains that scarce AI capacity and software can support rapid growth; the evidence upgrade is real, but customer concentration, extraordinary capital intensity, customer-advance dependence, hardware obsolescence, leverage and dilution remain decisive. Catalysts and invalidation conditions are unchanged because Q2 strengthened both the growth case and its financing risks.
- **Alert and action:** the August 12 volume anomaly remains an earnings-linked repricing rather than a buy signal. The USD 248.43 close exceeds the USD 165 base value and USD 132 buy-below level.
- **Blockers, gaps, rating, and conclusion:** the valuation-unsupported blocker is resolved, while concentration sensitivity, medium confidence, unfavorable timing and the missing accepted relationship remain. Rating changes from Unrated / Watch to Strong Sell / Avoid, but allocation ineligibility and the conclusion that no strategy or signal is justified are unchanged.
