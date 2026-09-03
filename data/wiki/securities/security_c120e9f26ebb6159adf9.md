---
title: ABB Ltd sponsored ADR
type: security
status: maintained
tags: [security, research, risk]
created: "2026-07-26"
updated: "2026-09-03"
provenance: "source_abb_q2_2026_results; source_abb_share_listing_2026"
security_id: security_c120e9f26ebb6159adf9
issuer_id: issuer_e60cfde16e515ef00e35
confidence: medium
next_review: "2026-10-03"
---

# ABB Ltd sponsored ADR

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
  "security_id": "security_c120e9f26ebb6159adf9",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_c120e9f26ebb6159adf9.csv",
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

```echart
{
  "schema_version": 1,
  "chart_id": "abb-scenario-values-20260903",
  "kind": "series",
  "title": "Scenario fair values versus the current ADR mark",
  "description": "ABB's lower-Bollinger price reset leaves the ADR above both probability-weighted and base fair value; only the bull case exceeds the current mark.",
  "as_of": "2026-09-02",
  "sources": [
    {
      "label": "ABB Q2 2026 results",
      "url": "https://search.abb.com/library/Download.aspx?DocumentID=9AKK108472A9735&LanguageCode=en&DocumentPartId=&Action=Launch",
      "observed_at": "2026-09-03T18:26:50Z"
    },
    {
      "label": "Canonical PaperTrader market mark",
      "observed_at": "2026-09-03T18:24:03Z"
    }
  ],
  "notes": [
    "Bear, base and bull probabilities are 30%, 50% and 20%; their probability-weighted fair value is USD 83.12.",
    "Scenario values apply 24x, 28x and 30x to USD 2.60, USD 3.10 and USD 3.50 normalized EPS, respectively."
  ],
  "x_axis": {"type": "category", "label": "Case", "values": ["Bear", "Weighted value", "Base", "Current mark", "Bull"]},
  "y_axes": [{"label": "USD per ADR", "unit": "USD/share", "format": "currency", "currency": "USD"}],
  "series": [{"name": "Value", "render": "bar", "y_axis": 0, "values": ["62.40", "83.12", "86.80", "95.1500015258789", "105.00"]}]
}
```

```echart
{
  "schema_version": 1,
  "chart_id": "abb-alert-returns-20260901",
  "kind": "series",
  "title": "Returns into the lower-Bollinger breach",
  "description": "The September 1 lower-band breach was dominated by a one-session decline rather than a sustained multi-horizon selloff.",
  "as_of": "2026-09-01",
  "sources": [
    {
      "label": "Canonical PaperTrader technical projection",
      "observed_at": "2026-09-03T18:24:03Z"
    }
  ],
  "notes": [
    "Returns use adjusted closes over one, five and twenty trading sessions through September 1, 2026.",
    "The close was below the lower Bollinger band while RSI was 47.00, MACD remained above signal and volume was not anomalous."
  ],
  "x_axis": {"type": "category", "label": "Lookback", "values": ["1 session", "5 sessions", "20 sessions"]},
  "y_axes": [{"label": "Return", "unit": "%", "format": "percent"}],
  "series": [{"name": "Adjusted-close return", "render": "bar", "y_axis": 0, "values": ["-4.171496", "-2.134924", "-0.188714"]}]
}
```

## Changes since prior review

- **Facts and primary evidence:** unchanged. Fresh downloads of ABB's Q2 results and share-listing
  page match the retained hashes. No newer retained issuer evidence changes orders, margins, cash
  conversion, leverage, outstanding shares, the Robotics disposal, the Rotork proposal, or ADR
  identity.
- **Alert and timing:** the canonical 1 September close of USD 95.16 was 4.17% lower for the session,
  2.13% lower over five sessions and 0.19% lower over twenty sessions. It closed below the USD 95.83
  lower Bollinger band; RSI was neutral at 47.00, MACD remained above signal and volume was not
  anomalous. The 2 September close was USD 95.15 and the lower-band trigger had cleared. This was a
  short-lived valuation recheck, not evidence of changed business economics.
- **Valuation assumptions and scenarios:** unchanged at USD 62.40/USD 86.80/USD 105.00 with
  30%/50%/20% probabilities. The lower mark improves the raw returns, but weighted value remains
  12.64% below market, base value 8.78% below market and bear value 34.42% below market; only the
  bull case has 10.35% upside.
- **Thesis, catalysts, risks, blockers and gaps:** unchanged. Strong group operating quality and
  cash conversion remain offset by the Robotics exit, Rotork integration and capital-allocation
  risk, OTC liquidity, medium confidence, weak timing, inadequate expected/base returns and the
  rejected embodied-AI edge.
- **Rating and portfolio action:** the lower mark improves the deterministic disposition from
  **Sell / Avoid** to **Hold / Watch**, while allocation remains ineligible. No strategy, signal,
  order or paper trade is justified.

## Alert review: opportunity, risk, or noise?

The 1 September lower-Bollinger breach is **a bounded valuation opportunity to recheck, but noise
for the operating thesis and not an action signal**. The next-session trigger clearance, neutral RSI,
non-anomalous volume and still-positive MACD signal do not establish a persistent technical break.
More importantly, the price remains above probability-weighted and base fair value, so the decline
does not repair the expected-return, base-upside, payoff or margin-of-safety gates.

## Identity

- Immutable security: `security_c120e9f26ebb6159adf9`
- Issuer: `issuer_e60cfde16e515ef00e35`
- Instrument: non-listed Level I ADR traded over the counter (`XOTC`), USD
- Provider identity: `ABBNY` / `XOTC` / `USD` / equity

ABB's current listing page confirms that ABBNY is a non-listed Level I ADR and reports
1,814,919,203 ABB shares outstanding at June 30, 2026. The instrument distinction matters for
venue and liquidity controls. The bounded review tests exposure to
[[ideas/idea_humanoid_robotics_embodied_ai_components]].

## Economics and thesis

ABB's current operating business is performing strongly. Q2 2026 orders were USD 12.042 billion,
up 30%, revenue was USD 9.475 billion, up 14%, operational EBITA margin was 20.2%, and continuing-
operations operating cash flow rose 34% to USD 1.303 billion. First-half free cash flow was USD
2.131 billion, up 42%. Net debt was USD 2.320 billion and net debt to EBITDA was 0.3. This supports
ABB as a high-quality electrification and industrial-automation company.

It does not support ABB as a durable public robotics proxy. ABB still expects about USD 4.8 billion
of net proceeds from the Robotics divestment in the second half of 2026 and plans to redeploy those
proceeds toward the roughly USD 5.5 billion Rotork acquisition. Shareholders therefore lose the
direct Robotics exposure while assuming acquisition and integration risk. ABB still does not
separately disclose recurring RobotStudio revenue or installed-base service economics.

## Evidence and gates

| Evidence | Interpretation |
| --- | --- |
| Q2 orders rose 30%, revenue 14%, and backlog 27%. | Electrification and automation demand is converting, with book-to-bill of 1.27. |
| Continuing-operations operating cash flow rose 34%; first-half free cash flow rose 42%. | Group cash conversion is strong. |
| Net debt was USD 2.320 billion and net debt/EBITDA was 0.3. | The balance sheet has capacity, although the planned transaction consumes it. |
| Robotics net proceeds are expected in the second half of 2026. | ABB is a temporary, not durable, direct robotics exposure. |
| ABB proposes a roughly USD 5.5 billion Rotork acquisition. | Actuator exposure expands, but integration and capital-allocation risk rise. |
| The current ADR mark is USD 95.15 with 169,300 shares of provider volume. | Price and trading data are fresh through 2 September, though OTC liquidity is weaker than a primary exchange listing. |

Primary evidence: [ABB Q2 2026 results](https://search.abb.com/library/Download.aspx?DocumentID=9AKK108472A9735&LanguageCode=en&DocumentPartId=&Action=Launch)
and [ABB share listing data](https://global.abb/group/en/investors/investor-and-shareholder-resources/share-listing).

## Valuation, catalysts, and risks

ABBNY closed at USD 95.15 on 2026-09-02. The mature-compounder earnings-multiple assessment uses
ABB's USD 1.41 first-half basic EPS, approximately 1.815 billion outstanding shares and USD 2.320
billion net debt, with the disclosed approximately USD 4.8 billion Robotics proceeds and USD 5.5
billion Rotork purchase price treated explicitly. The 12-month cases are:

| Case | Probability | EPS / multiple | Fair value | Interpretation |
| --- | ---: | --- | ---: | --- |
| Bear | 30% | USD 2.60 / 24x | USD 62.40 | Orders and margins normalize; transaction costs weigh on per-share earnings; indicative net debt rises to about USD 3.02 billion before fees and closing adjustments. |
| Base | 50% | USD 3.10 / 28x | USD 86.80 | Operating growth continues from USD 2.82 annualized first-half EPS, but Robotics leaves and Rotork integration consumes capital. |
| Bull | 20% | USD 3.50 / 30x | USD 105.00 | Book-to-bill, roughly 20% class margins and cash conversion persist; both transactions close near disclosed terms without material dilution or balance-sheet strain. |

These are scenarios rather than price targets. Multiples remain judgmental, and disposal taxes and
fees, separation, Rotork integration, capital returns and ADR mechanics can change per-share
outcomes. The probability-weighted fair value is USD 83.12, 12.64% below the current mark; the base
value is 8.78% below market, the bear case is 34.42% below market, and the bull case offers 10.35%
upside. The complete range therefore still fails the expected-return, base-return, downside-payoff
and 20% margin-of-safety gates.

Catalysts are disposal completion at expected net proceeds, disciplined redeployment, sustained
positive book-to-bill, and margin/cash conversion. Invalidate the physical-AI relationship on the
Robotics sale; invalidate the broader quality thesis if large acquisitions dilute returns, data-
centre and industrial orders reverse, margins normalize sharply, or cash conversion weakens.

## Disposition

Status: **watching**, **Hold / Watch**, confidence **medium**, and **allocation-ineligible**.
The complete valuation is below market on a probability-weighted and base-case basis, and the sole
canonical embodied-AI relationship is rejected. The Robotics exit, proposed Rotork integration,
OTC instrument and unfavorable timing remain material constraints. Review by **2026-10-03**, or
sooner on disposal or acquisition completion, a material transaction-term change, or evidence that
orders, margins or cash conversion have weakened. No conviction strategy or paper signal is
justified.

## Idea exposure map

- **Canonical rejected edge — [[ideas/idea_humanoid_robotics_embodied_ai_components|Humanoid
  robotics and embodied-AI components]], formerly positive direction:** ABB's disclosed Robotics
  disposal removes the direct transmission mechanism, while the retained group does not separately
  disclose durable RobotStudio or installed-base service economics. The existing canonical edge is
  rejected, not accepted; its already queued dependent relationship review must confirm or revise
  that status. Invalidate this rejection only if retained ABB disclosures establish material,
  durable embodied-AI economics after the disposal.
- **Rejected-no-link — [[ideas/idea_ai_infrastructure_power|AI infrastructure and power
  bottlenecks]]:** ABB's electrification portfolio is superficially relevant, but the retained Q2
  evidence does not isolate data-centre orders, backlog, revenue, margins or cash conversion. The
  idea page already declined to retain ABB for another review on this exact evidence gap; no new
  causal edge is proposed.
- **Rejected-no-link — [[ideas/idea_nearshoring_friendshoring_manufacturing|Nearshoring and
  friendshoring manufacturing capacity]]:** ABB can supply factory automation, but no retained
  primary evidence attributes material orders or cash flow to relocated regional capacity rather
  than the broad industrial cycle.
- **Rejected-no-link — [[ideas/idea_wide_bandgap_power_semiconductors|Wide-bandgap power
  semiconductors]]:** ABB is a downstream electrical-equipment and automation supplier; retained
  evidence does not establish material SiC or GaN device economics for the issuer.

No current accepted relationship exists for ABB, and no additional plausible candidate survives
the materiality and evidence tests. The complete maintained idea catalog was searched; the other
ideas lack a specific issuer-level transmission mechanism.

## 2026-08-09 bullish-MACD quick check

The bounded checklist from the 28 July review remains strong orders, margins, cash conversion and
low leverage; the expected Robotics disposal and proposed Rotork acquisition; transaction and
integration risk; and invalidation on weakening orders, margins, cash conversion or acquisition
returns. Fresh downloads of the issuer Q2 results and share-listing page match their retained
SHA-256 hashes. There is no changed primary evidence in those retained sources through the exact
4 August alert period.

The deterministic alert-period cache records a **USD 101.57** adjusted close on 4 August, down
**1.35%** from 7 July but up **4.74%** from the 27 July baseline mark. MACD crossed above its signal
with modest positive strength of **0.2090**. By 7 August the adjusted close was **USD 100.86**;
MACD remained above signal, RSI was neutral at **51.20**, volume was not anomalous, and no threshold
trigger was active. This is technical timing evidence, not proof of improved transaction economics
or a newly reached buy zone. At the alert-period mark, the old USD 64.80 bear and USD 85.40 base
cases imply approximately **36.20%** and **15.92%** downside respectively.

### Changes since prior review

- **Primary evidence, thesis, catalysts, risks and invalidation:** unchanged; both retained issuer
  sources are available and hash-identical.
- **Market state and timing:** changed to a modest bullish-MACD crossover, but the period return was
  negative and the later cache has no active threshold trigger.
- **Valuation and buy zone:** no buy zone was reached. The old two-case sensitivity remains below
  market, but it cannot support a current canonical decision because it lacks the complete scenario,
  probability and transaction-adjusted inputs required by assessment schema version 2.
- **Assessment:** migrated from legacy baseline fields to an explicit schema-v2 unsupported
  assessment. The unchanged economic conclusion is to watch rather than allocate.
- **Escalation:** exactly one dependent full review is required because the prior valuation can no
  longer support the current decision contract; it must incorporate a complete bull case,
  probabilities, current diluted-share and transaction inputs, and the rejected relationship.

## 2026-08-10 full scenario review

Fresh downloads of both registered issuer sources are hash-identical to the evidence used in the
quick check. The full review resolves the prior canonical-valuation gap with the ordered
USD 62.40 / USD 86.80 / USD 105.00 bear, base and bull cases above and 30% / 50% / 20%
probabilities. It does not resolve the economic gate: at the fresh USD 100.86 mark, the range remains
uncompetitive with cash and the rejected idea relationship independently blocks allocation.

### Changes since prior review

- **Facts and evidence:** unchanged. The Q2 release and listing page remain available and
  hash-identical; no newer issuer evidence changes orders, margins, cash conversion, leverage,
  outstanding shares, transaction terms or ADR identity.
- **Assumptions and scenario inputs:** changed from an unsupported two-case sensitivity to a complete
  mature-compounder earnings-multiple set. Bear/base/bull EPS are USD 2.60/USD 3.10/USD 3.50,
  multiples are 24x/28x/30x, and probabilities are 30%/50%/20%. The scenarios explicitly account
  for the Robotics disposal, Rotork purchase price, current net debt and outstanding shares.
- **Scenario outputs and buy zone:** changed to USD 62.40/USD 86.80/USD 105.00 and a USD 83.12
  probability-weighted fair value. Base and expected returns remain negative and no buy zone is
  reached.
- **Thesis:** unchanged at the group level: operating quality is strong. The embodied-AI thesis
  remains impaired because Robotics is being sold and retained idea-specific economics are not
  quantified.
- **Catalysts, risks and invalidation:** unchanged. Disposal completion, disciplined Rotork
  integration, sustained book-to-bill and cash conversion are catalysts; weaker orders, margins,
  cash conversion, acquisition returns or balance-sheet capacity would weaken the broader thesis.
- **Blockers and gaps:** the valuation-unsupported blocker is resolved. Negative expected and base
  returns, inadequate downside payoff and margin of safety, medium confidence, weak timing, OTC
  liquidity and the rejected relationship remain.
- **Rating and action:** changed from Unrated / Watch to Strong Sell / Avoid at the research layer;
  watching status, zero allocation and no paper trade remain unchanged.
- **Unchanged conclusion:** the August MACD crossover remains technical timing evidence rather than
  proof of improved transaction economics or a trade signal.

See [[index]] for the current paper-only investor decision.
