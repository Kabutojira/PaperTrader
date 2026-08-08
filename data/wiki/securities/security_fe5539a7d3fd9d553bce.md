---
title: Strategy Inc Class A common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-08"
updated: "2026-08-08"
provenance: "source_mstr_q2_2026_10q; source_mstr_aug3_2026_8k; deterministic market and FX caches"
security_id: security_fe5539a7d3fd9d553bce
issuer_id: issuer_c09135a9f81a751eb0e3
confidence: medium
next_review: "2026-09-07"
---

# Strategy Inc Class A common stock

## Identity

- Immutable security: `security_fe5539a7d3fd9d553bce`
- Issuer: `issuer_c09135a9f81a751eb0e3`
- Instrument: Class A common stock, Nasdaq Global Select Market (`XNAS`), USD
- Provider identity: `MSTR` / `XNAS` / `USD` / equity

Strategy's SEC filings identify its Class A common stock as trading under MSTR on Nasdaq. The
identity matches canonical state and no duplicate immutable identity was found. No canonical idea,
accepted relationship, strategy, or prior assessment is linked to this security. Related system
context: [[index]] and [[security-catalog]].

## Changes since prior review

- **Facts and evidence:** this is the first full assessment. Mandatory bounded context contained no
  prior assessment, security page, successful research result, retained source, linked idea,
  relationship, or strategy. New evidence is the second-quarter Form 10-Q, the August 3 treasury
  update, and the [[inbox/market-security_fe5539a7d3fd9d553bce-volume_anomaly-1c56259a5e4e|2026-08-07 volume alert]].
- **Assumptions and valuation:** no prior scenarios existed. This review adds a 12-month `other`
  sum-of-parts valuation with USD 52.50/USD 108.16/USD 175.99 bear/base/bull values and
  30%/50%/20% probabilities.
- **Thesis and rating:** no prior thesis, rating, or action existed. Bitcoin scale and capital-market
  access support the treasury mechanism, but structural dilution, preferred and debt claims,
  Bitcoin volatility, and limited software economics establish only medium confidence. The result
  is **Hold / Watch** and allocation ineligible.
- **Catalysts, risks, blockers, and gaps:** higher Bitcoin prices, accretive issuance, USD-reserve
  durability, and software stabilization are new catalysts. Bitcoin downside, common dilution,
  preferred dividends, refinancing, tax, custody, regulation, and premium-to-NAV compression are
  new risks. There is no hard blocker; scenario sensitivity, incomplete fully diluted share
  conversion detail, downside asymmetry, and margin of safety remain soft gaps.

## Alert review: opportunity, risk, or noise?

The canonical packet records entry into a volume anomaly on 2026-08-07 after the adjusted close
rose 5.67% from 2026-07-10 through 2026-08-07 to USD 100.01. Volume reached 28.95 million shares,
and trigger strength was 0.6435 versus zero previously. The close was above the 50-day average of
USD 96.40 but below the 200-day average of USD 152.94; RSI was neutral at 50.37 and MACD remained
negative despite improving relative to its signal.

This is **material attention and event digestion, not an independently actionable catalyst**. The
period included Strategy's August 3 filing: it disclosed continued MSTR issuance, Bitcoin sales,
preferred repurchases, and a larger USD reserve. Those actions improve near-term liquidity but also
confirm the dilution and financing claims that limit common-equity NAV. The volume transition is
therefore mixed timing evidence rather than proof of a durable thesis upgrade.

## Economics and thesis

Strategy combines a small enterprise-analytics software business with a leveraged Bitcoin treasury.
At June 30 it held 846,000 bitcoin, whose USD 49.672 billion fair value was below USD 63.939 billion
cost. By August 2 it held 842,138 bitcoin at USD 63.51 billion aggregate purchase cost after selling
1,638 bitcoin during the latest disclosed week. The company states that Bitcoin is its primary
reserve asset and uses common equity, preferred securities, debt, and occasional Bitcoin sales to
fund acquisitions, dividends, interest, and liquidity.

The treasury thesis is that access to multiple capital markets can increase Bitcoin exposure per
common share when securities are issued on favorable terms. The counter-thesis is that common
shareholders own a volatile residual claim after USD 6.710 billion of debt and roughly USD 15.462
billion preferred liquidation preference at June 30. Preferred dividends and redemptions require
cash; common issuance can transfer value away from existing holders; and Bitcoin itself produces no
cash flow. The six-month software business generated USD 246.7 million revenue but does not offset
treasury-scale volatility.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| 846,000 bitcoin had USD 49.672 billion fair value versus USD 63.939 billion cost at June 30. | Scale creates direct Bitcoin sensitivity, while the gap to cost shows severe downside volatility. |
| Cash plus Treasury investments were USD 2.448 billion; debt was USD 6.710 billion and preferred liquidation preference USD 15.462 billion. | Liquidity was meaningful, but senior and mezzanine claims substantially reduce common NAV. |
| August 2 holdings were 842,138 bitcoin and the USD reserve was USD 4.0 billion. | Current liquidity improved, partly through common issuance and Bitcoin sales rather than operating cash generation. |
| 3,011,361 MSTR shares raised USD 290.6 million during July 27-August 2. | Capital access remains open, but dilution is current and economically material. |
| 1,638 bitcoin were sold and USD 81.2 million STRC was repurchased in the same week. | The capital framework can rebalance claims, but preferred funding now consumes treasury liquidity. |
| Six-month software revenue was USD 246.7 million. | Software has recurring value, but it is immaterial beside Bitcoin and financing claims. |

Registered primary evidence: [second-quarter 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1050446/000105044626000044/mstr-20260630.htm)
(`source_mstr_q2_2026_10q`) and [August 3, 2026 Form 8-K treasury update](https://www.sec.gov/Archives/edgar/data/1050446/000119312526329565/mstr-20260803.htm)
(`source_mstr_aug3_2026_8k`).

## Valuation, catalysts, and risks

The `other` sum-of-parts method is appropriate because no specialized template covers a listed
Bitcoin treasury with a secondary software business. It starts with 842,138 disclosed bitcoin,
USD 4.0 billion current USD reserve, June 30 debt of USD 6.710 billion, and preferred liquidation
preference reduced only for the specifically disclosed USD 106.2 million of subsequent STRC
repurchases. The 387.24 million denominator combines July 24 Class A and Class B shares with the
3.011 million subsequently disclosed MSTR shares sold. Convertible notes are deducted as debt
rather than treated as converted shares; unquantified later issuance and equity-award dilution are
not invented and remain a soft gap.

The 12-month bear value is USD 52.50 (30% probability): Bitcoin at USD 45,000, USD 0.5 billion
software value, unchanged USD reserve, and current disclosed claims. The base value is USD 108.16
(50%): Bitcoin at USD 70,000 and USD 1.0 billion software value. The bull value is USD 175.99 (20%):
Bitcoin at USD 100,000 and USD 2.0 billion software value. Each scenario holds disclosed Bitcoin
quantity and claims constant, so adverse funding needs or further dilution would make it optimistic.

The USD 105.03 probability-weighted fair value implies 5.01% expected return from USD 100.01;
medium confidence reduces that to 3.76%. Bear/base/bull returns are -47.51%/8.15%/75.97%.
The current price is below weighted value but far above the roughly USD 78.77 canonical buy-below
level. Expected return, base upside, bear/base and expected/bear payoff, margin of safety,
confidence, and accepted-relationship requirements therefore fail. This bounded comparison is not
a Bitcoin or stock-price forecast.

Catalysts are sustained Bitcoin appreciation, issuance demonstrably accretive per share, expansion
of the USD reserve without disproportionate dilution, retirement of expensive preferred claims,
and stabilized software cash contribution. Risks are Bitcoin drawdowns, premium-to-NAV
compression, repeated common dilution, preferred dividend escalation, refinancing and conversion,
Bitcoin sales at weak prices, custody or cyber loss, tax changes, regulation, and inability of the
software business to support treasury obligations. Invalidate the constructive treasury thesis if
Bitcoin per fully diluted common share persistently declines, the USD reserve cannot cover planned
claims without adverse issuance or sales, senior claims rise faster than asset value, or capital
markets access closes during a Bitcoin drawdown.

## Disposition

Status: **watching**, confidence **medium**, expected rating **Hold**, portfolio action **Watch**, and
**allocation ineligible**. Deep liquidity and capital access do not overcome downside asymmetry,
financing complexity, dilution, failed economic gates, and the absence of an accepted relationship.
No conviction strategy, signal, order, or paper trade is justified. Review by **2026-09-07**, or
sooner after a material Bitcoin move, treasury issuance or sale, reserve-policy change, quarterly
filing, or evidence that Bitcoin per fully diluted share has changed materially.
