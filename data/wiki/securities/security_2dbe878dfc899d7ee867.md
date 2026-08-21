---
title: Freeport-McMoRan Inc. common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-08-21"
provenance: "source_fcx_q2_2026_results_sec|source_fcx_q2_2026_10q|source_fcx_sec_submissions_20260821|deterministic market cache"
security_id: security_2dbe878dfc899d7ee867
issuer_id: issuer_5076f0e0e1dd7cc8bca7
confidence: medium
next_review: "2026-09-20"
---

# Freeport-McMoRan Inc. common stock

## Identity

- Immutable security: `security_2dbe878dfc899d7ee867`
- Issuer: `issuer_5076f0e0e1dd7cc8bca7`
- Instrument: common stock, New York Stock Exchange (`XNYS`), USD
- Provider identity: `FCX` / `XNYS` / `USD` / equity

## Decision

**Sell / Avoid at USD 76.66; no strategy.** The August 21 close is 22.46% above the July 24
close and 7.64% above the prior session, with a newly entered volume anomaly and a close 2.56%
above the upper Bollinger band. The move is material, but current primary evidence does not
validate the rerating: the August 6 Form 10-Q confirms the July results economics and the current
SEC index contains no later issuer operating filing through the market date.

The unchanged USD 32.64/USD 47.36/USD 65.12 cyclical scenarios now all sit further below market.
Their USD 46.496 probability-weighted value implies a 39.35% expected loss at the fresh mark.
Grasberg recovery and structural copper sensitivity remain real, but valuation, payoff asymmetry,
timing, concentration and jurisdictional risk keep the security allocation-ineligible.

## August 21 alert review

The canonical market cache validates the exact July 24-August 21 period and price hash
`32da069b983513fb310a04b088dac01b8d01f09f24de80dc551abe49bd1d6de1`:

- adjusted close increased from USD 62.60 to USD 76.66, a 22.46% period return;
- August 21 volume was 28.485 million shares and its z-score was 2.9649, producing the newly
  entered `volume_anomaly` transition;
- RSI was 69.30, MACD histogram was positive 0.6250, and the close was 2.56% above the USD 74.749
  upper Bollinger band; and
- the same cache therefore also shows an above-band extension, although the routed trigger is the
  newly entered volume anomaly.

This is **valuation and timing risk**, not a new opportunity. The price and volume acceleration
show stronger market conviction, but no current primary filing provides a new production,
cash-flow, license or capital-allocation fact that explains a higher normalized value.

## Business economics and primary evidence

Freeport is one of the largest publicly traded copper producers, with large operations in the
United States, South America and Indonesia and meaningful gold and molybdenum credits. The
[SEC-filed Q2 results exhibit](https://www.sec.gov/Archives/edgar/data/831259/000083125926000033/a2q2026exhibit991.htm)
is byte-for-byte unchanged. It reported USD 984 million of common net income, USD 0.68 diluted EPS
and USD 0.74 adjusted EPS; 786 million pounds of copper production; 710 million pounds of copper
sales; USD 6.17/lb realized copper; USD 1.97/lb unit net cash cost; USD 2.048 billion of operating
cash flow; and USD 1.104 billion of capital spending.

The later [Form 10-Q](https://www.sec.gov/Archives/edgar/data/831259/000083125926000036/fcx-20260630.htm)
confirms rather than overturns those economics:

- consolidated debt was USD 9.4 billion and cash was USD 4.1 billion at June 30; stated net debt
  was USD 2.1 billion excluding USD 3.2 billion of PTFI downstream-processing debt;
- Freeport projected 2026 copper sales of 3.057 billion pounds, including 675 million from
  Indonesia, and third-quarter sales near 750 million pounds;
- 2026 copper unit net cash cost was projected near USD 1.90/lb, excluding approximately USD 1.2
  billion of expected Grasberg idle-facility and restoration costs;
- 2026 operating cash flow was projected near USD 8.3 billion at a USD 6.00/lb second-half copper
  assumption, versus USD 4.3 billion of capital spending; and
- Grasberg Block Cave was still expected at about 65% of capacity in the second half of 2026, 80%
  by mid-2027 and near full capacity by the end of 2027.

The filing also confirms that PTFI submitted its IUPK extension application in June, but amended
rights and definitive agreements remain outstanding. Export-proceeds rules were amended effective
June 1 and applicability remained under clarification. These conditions preserve Indonesian
ownership, liquidity and jurisdictional uncertainty rather than removing it. The
[current SEC submissions index](https://data.sec.gov/submissions/CIK0000831259.json) identifies
the August 6 Form 10-Q as the latest issuer operating filing through August 21.

## Thesis, contrary evidence, catalysts, and invalidation

The positive thesis remains high copper-price operating leverage, long-lived reserve optionality,
safe Grasberg restoration and lower-capital leach growth in the Americas. Higher realized prices
can expand mine margins and cash flow, while gold and molybdenum credits lower reported copper
costs.

Contrary evidence remains equally material. Grasberg copper production and sales are still far
below normal, recovery extends into 2027, idle and restoration costs are large, and current cash
generation relies on elevated commodity prices. Capital spending, PTFI minority ownership and
downstream debt, unresolved post-2041 ownership economics, export-proceeds rules, safety and
project execution can absorb commodity upside.

Catalysts are safe Grasberg ramp execution, Americas leach gains, a disciplined Bagdad decision,
final Indonesian rights and free cash flow after capital needs. Invalidate on renewed mine or
safety disruption, weaker production recovery, rising unit costs or capital intensity, adverse
Indonesian terms, weaker cash conversion, or faster copper-price normalization.

## Valuation and assessment

The selected repository template remains `cyclical_commodity` with `normalized_earnings`. It uses
the latest filing, production evidence, balance sheet and realized prices while avoiding
capitalization of peak commodity earnings:

- **Bear — USD 32.64, 30%:** annualized USD 0.68 reported Q2 EPS at 12x as copper normalizes,
  Grasberg restoration slows and idle or restoration costs persist.
- **Base — USD 47.36, 50%:** annualized USD 0.74 adjusted Q2 EPS at 16x as the stated Grasberg ramp
  proceeds but production remains below normal and Indonesian and minority economics retain a
  discount.
- **Bull — USD 65.12, 20%:** annualized USD 0.74 adjusted Q2 EPS at 22x as copper stays elevated,
  recovery executes safely, costs remain controlled and Indonesian rights advance.

The weighted fair value remains **USD 46.496**. At USD 76.66, bear/base/bull returns are
approximately **negative 57.42% / negative 38.22% / negative 15.05%**. Expected return is
approximately **negative 39.35%**, and the medium-confidence adjustment remains deeply negative.
The buy-below comparison remains USD 37.888. Anchored scores are thesis 60, business quality 60,
balance sheet 60, valuation 20, timing 20, liquidity 100 and risk penalty 80.

## Idea exposure map

- **Accepted-current — positive, high sensitivity:**
  [[ideas/idea_critical_minerals_copper|critical minerals and structural copper scarcity]] transmits
  through realized copper prices, mine margins, cash flow and reserve option value. The canonical
  [[relationships/relationship_def43e5b4e13577e2b99|accepted relationship]] remains current through
  August 26. Production recovery, costs, capex, minority interests, safety and Indonesian terms can
  prevent price strength from reaching common shareholders.
- **Rejected-no-link:** the complete maintained idea catalog was searched. AI power build-out,
  humanoid robotics and wide-bandgap systems mention copper demand, but none adds a distinct,
  issuer-specific material mechanism beyond the accepted structural-copper idea. No candidate edge
  is retained without evidence of material incremental FCX exposure.

The accepted edge is current and neither stale nor contradicted, so this review does not create a
relationship-review duplicate. The linked copper idea requires one dependent refresh to absorb
this security result.

## Changes since prior review

- **Evidence changed:** the August 6 Form 10-Q is now retained as the latest complete filing. It
  confirms the Q2 exhibit, balance sheet, recovery schedule and outlook; the August 21 SEC index
  shows no later operating filing.
- **Market state changed:** the mark rose from USD 69.39 to USD 76.66. A new 2.9649-z-score volume
  anomaly accompanied a 22.46% measured-period rise and above-band extension.
- **Assumptions and scenarios unchanged:** the filing does not justify changing normalized EPS,
  multiples, probabilities or USD 32.64/USD 47.36/USD 65.12 fair values. Every scenario return and
  margin-of-safety measure deteriorates solely because the fresh price is higher.
- **Thesis unchanged:** structural copper sensitivity and recovery progress remain supported;
  normalization, disrupted volumes, costs, capital needs, safety and Indonesian economics remain
  contrary evidence.
- **Catalysts and risks unchanged:** no catalyst was completed and no invalidation fired. The
  current volume move has no primary-evidence confirmation.
- **Blockers and gaps unchanged:** there is no hard research blocker, but concentration,
  medium confidence, cyclicality, weak timing, inadequate margin of safety and unattractive
  valuation remain.
- **Rating and action unchanged:** complete research remains **Sell / Avoid**, allocation-ineligible
  and unsuitable for strategy research. The stronger price move increases rather than resolves the
  valuation gap.

Review by **2026-09-20**, or sooner after material Grasberg, Indonesian-license, cost,
capital-allocation or copper-price evidence. See [[research-catalog|the research catalog]] for the
maintained universe.