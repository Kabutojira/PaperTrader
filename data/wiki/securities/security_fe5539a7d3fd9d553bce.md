---
title: Strategy Inc Class A common stock
type: security
status: maintained
tags: [security, research, risk]
created: "2026-08-08"
updated: "2026-08-20"
provenance: "source_mstr_q2_2026_10q; source_mstr_aug3_2026_8k; source_mstr_aug10_2026_8k; source_mstr_aug17_2026_8k; deterministic market and FX caches"
security_id: security_fe5539a7d3fd9d553bce
issuer_id: issuer_c09135a9f81a751eb0e3
confidence: medium
next_review: "2026-09-19"
---

# Strategy Inc Class A common stock

## Identity

- Immutable security: `security_fe5539a7d3fd9d553bce`
- Issuer: `issuer_c09135a9f81a751eb0e3`
- Instrument: Class A common stock, Nasdaq Global Select Market (`XNAS`), USD
- Provider identity: `MSTR` / `XNAS` / `USD` / equity

Strategy's SEC filings identify its Class A common stock as trading under MSTR on Nasdaq. The
identity matches canonical state and no duplicate immutable identity was found. No accepted
relationship or strategy is linked to this security. Related system context: [[index]] and
[[security-catalog]].

## Changes since prior review

- **Facts and evidence changed:** the August 10 and August 17 Forms 8-K supersede the August 3
  treasury snapshot. Strategy sold another 1,690 bitcoin, issued 10,044,548 common shares across
  two weeks, repurchased 2,540,740 STRC preferred shares, and raised the USD reserve from USD 4.0
  billion to USD 4.8 billion. Bitcoin holdings fell from 842,138 to 840,447. The exact new alert is
  [[inbox/market-security_fe5539a7d3fd9d553bce-volume_anomaly-399eb4aca85f|the 2026-08-19 volume anomaly]].
- **Assumptions and valuation changed:** the 12-month `other` sum-of-parts keeps the prior USD
  45,000/USD 70,000/USD 100,000 Bitcoin and USD 0.5/USD 1.0/USD 2.0 billion software assumptions,
  but updates Bitcoin quantity, reserve, preferred claims and common shares. Bear/base/bull values
  move from USD 52.50/USD 108.16/USD 175.99 to USD 53.63/USD 107.78/USD 173.76; probabilities remain
  30%/50%/20%.
- **Thesis, rating, and action:** the treasury mechanism remains supported, but the two-week mix of
  common issuance, Bitcoin sales and preferred repurchases confirms that liquidity protection is
  being purchased with dilution and treasury turnover. Medium confidence, **Hold / Watch**, and
  allocation ineligibility are unchanged.
- **Catalysts, risks, blockers, and gaps:** reserve durability improved modestly and preferred claims
  declined, while common dilution and Bitcoin-per-share pressure increased. Catalysts, invalidation,
  and the absence of a hard blocker are unchanged. Scenario sensitivity, incomplete fully diluted
  share conversion detail, downside asymmetry, low margin of safety, and no accepted relationship
  remain unresolved soft gaps.

## Alert review: opportunity, risk, or noise?

The canonical packet records entry into a volume anomaly on 2026-08-19. Adjusted close rose 4.24%
from USD 100.01 on 2026-07-22 to USD 104.25, while the August 19 session traded 48.67 million
shares. Deterministic indicators report a 3.752 volume z-score, 0.8546 trigger strength, neutral
RSI of 55.74, a close above the USD 96.25 20-day average and still below the USD 145.47 200-day
average. MACD remained negative but above its signal.

This is **material attention and event digestion, but not an independently actionable catalyst**.
The August 19 price and volume spike followed two weekly filings that disclose more common
issuance, a larger reserve, preferred repurchases and a small Bitcoin sale. Those facts improve
liquidity and lower preferred claims but also increase common shares and reduce Bitcoin per share.
No separate primary issuer filing through August 19 establishes a new operating catalyst. The
alert is mixed timing evidence rather than a thesis upgrade or a sufficient margin of safety.

## Economics and thesis

Strategy combines a small enterprise-analytics software business with a leveraged Bitcoin treasury.
At June 30 it held 846,000 bitcoin, whose USD 49.672 billion fair value was below USD 63.939 billion
cost. By August 16 it held 840,447 bitcoin at USD 63.36 billion aggregate purchase cost after
selling 1,690 bitcoin during August 3-9 and making no purchase or sale during August 10-16. The
company states that Bitcoin is its primary
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
| August 16 holdings were 840,447 bitcoin and the USD reserve was USD 4.80 billion. | Liquidity improved, partly through common issuance and Bitcoin sales rather than operating cash generation. |
| 10,044,548 MSTR shares raised USD 986.8 million during August 3-16. | Capital access remains open, but dilution is current and economically material. |
| 1,690 bitcoin were sold for USD 108.6 million and 2,540,740 STRC shares were repurchased for USD 240.8 million during August 3-16. | The capital framework can rebalance claims, but preferred funding consumes treasury liquidity and Bitcoin per common share fell. |
| Six-month software revenue was USD 246.7 million. | Software has recurring value, but it is immaterial beside Bitcoin and financing claims. |

Registered primary evidence: [second-quarter 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1050446/000105044626000044/mstr-20260630.htm)
(`source_mstr_q2_2026_10q`) and [August 3, 2026 Form 8-K treasury update](https://www.sec.gov/Archives/edgar/data/1050446/000119312526329565/mstr-20260803.htm)
(`source_mstr_aug3_2026_8k`), plus the [August 10 Form 8-K](https://www.sec.gov/Archives/edgar/data/1050446/000119312526341297/mstr-20260810.htm)
(`source_mstr_aug10_2026_8k`) and [August 17 Form 8-K](https://www.sec.gov/Archives/edgar/data/1050446/000119312526353240/mstr-20260817.htm)
(`source_mstr_aug17_2026_8k`).

## Idea exposure map

There is no accepted canonical idea relationship. The complete maintained idea catalog was
reviewed against Strategy's products, treasury assets, financing channels and risks.

- **Rejected-no-link:** [[ideas/idea_digital_finance_crypto_rails|Digital finance and crypto rails]].
  Direction would be positive to Bitcoin adoption, but Strategy is a leveraged treasury vehicle,
  not a settlement, custody, stablecoin, payment or tokenization rail. The idea page explicitly
  separates treasury vehicles from operating-rail economics; the two August filings add no rail
  revenue or causal exposure. Reconsider only if Strategy develops material, evidenced operating
  revenue from those rails rather than balance-sheet Bitcoin exposure.
- **Rejected-no-link:** all other maintained ideas lack a specific material transmission mechanism
  to Strategy's software or Bitcoin treasury economics. Broad AI, power, defense, industrial,
  commodity, healthcare and consumer themes are superficial associations without current evidence.

## Valuation, catalysts, and risks

The `other` sum-of-parts method is appropriate because no specialized template covers a listed
Bitcoin treasury with a secondary software business. It starts with 840,447 disclosed bitcoin,
USD 4.8 billion current USD reserve, June 30 debt of USD 6.710 billion, and preferred liquidation
preference reduced for the disclosed STRC shares repurchased through August 16. The 397.28 million
denominator carries forward the prior disclosed Class A and Class B count and adds 10.045 million
subsequently disclosed MSTR shares sold. Convertible notes are deducted as debt
rather than treated as converted shares; unquantified later issuance and equity-award dilution are
not invented and remain a soft gap.

The 12-month bear value is USD 53.63 (30% probability): Bitcoin at USD 45,000, USD 0.5 billion
software value, unchanged USD reserve, and current disclosed claims. The base value is USD 107.78
(50%): Bitcoin at USD 70,000 and USD 1.0 billion software value. The bull value is USD 173.76 (20%):
Bitcoin at USD 100,000 and USD 2.0 billion software value. Each scenario holds disclosed Bitcoin
quantity and claims constant, so adverse funding needs or further dilution would make it optimistic.

The USD 106.967 probability-weighted fair value implies only about 2.61% expected return from USD
104.25; medium confidence reduces it further. Bear/base/bull returns remain sharply asymmetric.
The current price is below weighted value but above the deterministic canonical buy-below
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
No conviction strategy, signal, order, or paper trade is justified. Review by **2026-09-19**, or
sooner after a material Bitcoin move, treasury issuance or sale, reserve-policy change, quarterly
filing, or evidence that Bitcoin per fully diluted share has changed materially.
