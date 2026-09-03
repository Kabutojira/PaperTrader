---
title: Corsair Gaming, Inc. common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-05"
updated: "2026-08-08"
provenance: "source_crsr_q1_2026_10q; source_crsr_q1_2026_results; source_crsr_q2_2026_10q; source_crsr_q2_2026_results"
security_id: security_55c9ce2fdcd32dad6b8c
issuer_id: issuer_5ce238383a369ed3467b
confidence: medium
next_review: "2026-08-22"
---

# Corsair Gaming, Inc. common stock

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
  "security_id": "security_55c9ce2fdcd32dad6b8c",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_55c9ce2fdcd32dad6b8c.csv",
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

- Immutable security: `security_55c9ce2fdcd32dad6b8c`
- Issuer: `issuer_5ce238383a369ed3467b`
- Instrument: common stock, Nasdaq Global Select Market (`XNAS`), USD
- Provider identity: `CRSR` / `XNAS` / `USD` / equity

Corsair sells gaming peripherals, streaming and creator equipment, sim-racing products, memory,
power supplies, cooling, cases, and gaming or AI-workstation PCs. Its brands include Corsair,
Elgato, Fanatec, SCUF, Drop, and ORIGIN PC. It is a thematic comparison for
[[ideas/idea_digital_attention_gaming_ecosystems]] and
[[securities/security_c9a37d277445869a8809|Roblox]], but no accepted canonical idea-security
relationship currently exists for this instrument.

## Economics and thesis

The investable thesis is that a premium multi-brand ecosystem, direct engagement with enthusiasts,
and mix shift toward higher-margin peripherals, creator tools, and sim racing can expand gross
margin and recurring cash generation even while PC-component demand cycles. The contrary case is
that Corsair remains exposed to discretionary spending, semiconductor availability and pricing,
tariffs, promotional competition, inventory execution, and acquired-brand integration; its recent
margin recovery has not yet established durable through-cycle growth.

For the quarter ended 30 June 2026, revenue fell 1.8% year over year to USD 314.3 million, but gross
profit rose 21% to USD 104.3 million. Reported gross margin reached 33.2%, including about 500 basis
points from a USD 15.6 million tariff refund. GAAP operating income improved to USD 7.6 million from
a USD 16.9 million loss and net income was USD 9.1 million; excluding the refund, management reports
a USD 5.7 million net loss. Gamer and Creator Peripherals revenue grew 13%, while Gaming Components
and Systems revenue fell 9% as elevated memory pricing delayed DIY builds.

## Evidence and decision gates

| Evidence | Interpretation |
| --- | --- |
| Q2 adjusted EBITDA was USD 30.8 million, but USD 14.3 million came from the now-materially-complete tariff refund; underlying adjusted EBITDA was USD 16.6 million versus USD 12.5-15.5 million guidance. | Product mix and cost discipline beat the operating guide, while the one-time refund must not be capitalized as recurring earnings. |
| Updated 2026 guidance is USD 1.40-1.47 billion revenue, USD 121-131 million adjusted EBITDA, and USD 0.85-0.94 non-GAAP EPS. | The midpoint rose by about USD 35 million of revenue and USD 19 million of adjusted EBITDA, requiring a full normalization of recurring versus refund-related economics. |
| Cash and restricted cash rose to USD 193.9 million against about USD 118.7 million of debt at 30 June. | Liquidity and net cash improved materially, although acquisitions and working-capital seasonality can consume it. |
| Q2 operating cash flow was USD 74.8 million and first-half operating cash flow was USD 104.6 million. | Cash conversion strengthened, but tariff receipts and working-capital movements require normalization before revising long-run value. |
| Gamer and Creator Peripherals grew 13%, while Components and Systems fell 9%; Amazon represented 25.7% of first-half revenue. | Higher-margin ecosystem growth is real, but component cyclicality and customer concentration remain material. |
| Corsair completed the Trak Racer acquisition on 3 August after quarter-end. | Sim-racing breadth can add value, but purchase accounting, consideration, integration and returns need a full review. |

Primary evidence is the [quarterly report filed 6 August 2026](https://www.sec.gov/Archives/edgar/data/1743759/000119312526337981/crsr-20260630.htm)
as `source_crsr_q2_2026_10q` and the [SEC-filed Q2 results release](https://www.sec.gov/Archives/edgar/data/1743759/000119312526337943/crsr-ex99_1.htm)
as `source_crsr_q2_2026_results`, both checked 7 August 2026.

## Valuation

The `mature_compounder` template uses a 12-month `earnings_multiple`. It starts from management's
raised 2026 guide but removes the one-time tariff refund and normalizes stock compensation,
amortization, product-cycle sensitivity, working capital, net cash, acquisition spending, and the
possibility that 2027 profitability differs from non-GAAP guidance. Against the 7 August close of
USD 14.350000381469727:

| Scenario | Probability | Fair value | Assumptions |
| --- | ---: | ---: | --- |
| Bear | 25% | USD 6.60 | USD 0.55 normalized forward EPS at 12x after removing the tariff refund; elevated memory pricing, discretionary weakness, integration costs, customer concentration, or margin reversion suppress recurring earnings and cash conversion. |
| Base | 55% | USD 12.00 | USD 0.80 normalized forward EPS at 15x after removing the tariff refund; peripherals and creator growth, adequate component supply, improved underlying margin, and modest deferred-demand recovery convert raised guidance while acquisition spending and dilution remain controlled. |
| Bull | 20% | USD 18.90 | USD 1.05 normalized forward EPS at 18x as Fanatec, Trak Racer, Elgato, and Stream Deck scale, deferred DIY demand returns, AI workstations add profitable revenue, underlying margins persist, and cash-funded acquisitions earn attractive returns. |

Probability-weighted fair value is USD 12.03, or 16.2% below the mark. The bear/base/bull returns
are approximately -54.0%/-16.4%/+31.7%; medium-confidence adjustment reduces the already negative
expected return to about -12.1%. The base-derived buy-below price is USD 9.60 and current margin of
safety is negative 19.6%. Expected return, base return, bear/base payoff, expected/bear payoff,
margin of safety, and the accepted-relationship requirement all fail. Medium confidence reflects
demand cyclicality, non-GAAP normalization, acquisition and product timing, customer concentration,
and the sensitivity of fair value to modest EPS and multiple changes.

## Alert review, catalysts, and risks

The merged alerts record repeated volume anomalies: a 26.4% rise through 5 August at USD 11.20, a
pullback to USD 10.61 on 6 August, and then a strongly strengthened anomaly at the USD 14.35 close
on 7 August. The canonical 10 July–7 August return is 48.55% and trigger strength is 1.108979875.
The Q2 evidence validates underlying profit progress and raised guidance, but the repricing now
runs materially ahead of normalized base value. This is a material **risk and adverse entry-timing
signal**, not noise, an opportunity at the current mark, or a completed buy signal.

Catalysts are delivery of raised full-year guidance, sustained peripheral and creator growth, easing
semiconductor constraints, durable underlying gross-margin expansion, Fanatec, Trak Racer and Elgato
execution, continued inventory normalization, and cash-backed repurchases below value. Risks
are discretionary-demand weakness, tariffs and trade policy, memory and semiconductor pricing,
product-launch slippage, inventory write-downs, channel concentration, intense competition, acquired-
brand integration, stock compensation, foreign exchange, and valuation compression.

Invalidate the thesis if peripherals growth fails to offset component weakness, gross margin returns
toward prior levels without a temporary explanation, adjusted profit does not convert to GAAP and
free-cash-flow improvement, inventory rebuilds faster than demand, acquired brands require repeated
capital without adequate returns, or dilution overwhelms repurchases and per-share earnings growth.

## Disposition

Status: **watching**, confidence **medium**. Q2 underlying profit, cash generation, net cash, and
raised guidance strengthen operating evidence, but the one-time tariff benefit, cyclicality,
customer concentration, Trak Racer integration, 48.55% repricing, bear downside, and missing
accepted relationship keep the security allocation-ineligible. The revised scenarios at USD 14.35
derive **Hold / Watch**. Review by **2026-08-22**, or sooner after material acquisition terms,
guidance, or price evidence. No conviction strategy, signal, or paper order is justified.

## Changes since prior review

- **Prior state:** this is the first structured security assessment; the mandatory context contained no prior assessment, successful result, retained source, accepted relationship, strategy, idea, or research-page hash.
- **Facts and evidence:** the Q1 filing and SEC-filed results release establish current segment trends, revenue, margin, operating profit, cash flow, liquidity, debt, inventory, share count, repurchases, Q2 outlook, and unchanged full-year guidance.
- **Assumptions and valuation:** a new scenario-complete earnings-multiple assessment sets bear/base/bull values of USD 6.00/USD 11.25/USD 18.00 at 25%/50%/25%; there are no prior values to revise.
- **Thesis, catalysts, and risks:** premium ecosystem breadth, mix, and cost discipline support the thesis, while cyclicality, component availability and pricing, tariffs, inventory, competition, integration, and normalization risk constrain it.
- **Blockers, gaps, rating, and action:** no hard research blocker remains. Modeled return and payoff are not compelling, confidence is medium, and no accepted relationship exists. The initial disposition is watching with no strategy or signal.

### 2026-08-07 quick check

- **Verified change:** Q2 underlying adjusted EBITDA beat guidance, cash generation strengthened,
  full-year revenue and profit guidance rose, and the Q2 filing confirms the results. The reported
  margin and earnings include a material, non-recurring tariff refund, while the post-quarter Trak
  Racer acquisition adds integration and capital-allocation uncertainty.
- **Alert disposition:** repeated volume anomalies accompanied a 26.4% rise through 5 August and a
  pullback to USD 10.61 on 6 August; the exact current source-price hash is
  `507551e0e5f99423191005f2e8a876a1c2cb482fa7b37ad4dd66a44470194023`.
- **Valuation disposition:** holding the prior USD 6.00/USD 11.25/USD 18.00 scenarios for this
  bounded check gives about -43.4%/+6.0%/+69.7% bear/base/bull returns and 9.6% weighted upside.
  Hold / Watch and allocation-ineligible remain unchanged pending full normalization.
- **Escalation:** the changed Q2 evidence, raised guidance and acquisition require exactly one
  dependent full security review. No strategy, signal, order, allocation or accounting state changes.

### 2026-08-08 full Q2 reassessment

- **Facts and evidence changed:** the Q2 Form 10-Q and SEC-filed results release remain unchanged at
  their registered hashes. They confirm stronger underlying adjusted EBITDA and cash conversion,
  raised 2026 guidance, USD 193.9 million cash and restricted cash against USD 118.3 million debt,
  25.7% first-half Amazon concentration, and the post-quarter Trak Racer asset acquisition. The
  market mark changed from USD 10.61 to USD 14.35 and the merged volume-anomaly period return rose
  from 11.1% through 6 August to 48.55% through 7 August.
- **Assumptions and scenarios changed:** normalized forward EPS increases from USD 0.50/USD
  0.75/USD 1.00 to USD 0.55/USD 0.80/USD 1.05 as the raised guide and underlying Q2 beat improve the
  earnings range. Multiples remain 12x/15x/18x. Fair values increase from USD 6.00/USD 11.25/USD
  18.00 to USD 6.60/USD 12.00/USD 18.90, while probabilities shift from 25%/50%/25% to
  25%/55%/20% because acquisition execution and the one-time refund limit bull-case weight.
- **Outputs changed:** at USD 14.35, weighted fair value is USD 12.03 and expected return becomes
  negative 16.2%; bear/base/bull returns become approximately -54.0%/-16.4%/+31.7%. The buy-below
  price increases from USD 9.00 to USD 9.60, but margin of safety deteriorates to negative 19.6%.
- **Thesis and quality changed:** the core ecosystem and mix thesis remains supported rather than
  upgraded. Improved net cash raises the balance-sheet score from 60 to 80. The repricing lowers
  valuation and timing scores from 60/40 to 20/20; thesis, business quality, liquidity, residual
  risk, and medium confidence remain 60/60/80/60 and unchanged.
- **Catalysts and risks changed:** raised guidance and a better underlying Q2 result are now verified
  catalysts. Trak Racer broadens the sim-racing opportunity but adds purchase-accounting,
  integration, and capital-allocation risk. Customer concentration, component pricing, working
  capital, dilution, and through-cycle margin durability remain material risks.
- **Blockers and gaps:** no hard research blocker remains. Concentration, medium confidence,
  cyclical normalization, inadequate margin of safety, unfavorable timing, and uncompelling
  valuation remain soft gaps; the canonical relationship is still pending.
- **Rating and action:** **Hold / Watch** and no paper trade are unchanged, but the reason shifts
  from a pending normalization review at USD 10.61 to a completed, negative-return scenario set at
  USD 14.35. No strategy or idea follow-up is created because the conviction gate fails and no idea
  is named in the payload or linked by an accepted canonical relationship.
