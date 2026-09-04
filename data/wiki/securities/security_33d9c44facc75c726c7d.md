---
title: NVIDIA Corporation (NVDA)
type: security
status: maintained
tags:
  - security
  - research
  - risk
created: "2026-08-05"
updated: "2026-09-04"
provenance: "NVIDIA fiscal 2027 Q2 Form 10-Q, results release and CFO commentary; NVIDIA Hugging Face acquisition Form 8-K; canonical PaperTrader market data"
security_id: security_33d9c44facc75c726c7d
issuer_id: issuer_7f0f0b334051a9c9a06b
ticker: NVDA
venue_mic: XNAS
currency: USD
confidence: medium
next_review: "2026-09-18"
---

# NVIDIA Corporation (NVDA)

## Visual evidence

Fiscal Q2 extended the revenue and margin trend, while net income growth slowed sequentially because
Q1 included unusually large equity-security gains. The grouped fundamental view therefore separates
revenue from net income rather than treating headline GAAP earnings as recurring.

```echart
{
  "schema_version": 1,
  "chart_id": "nvda-q2-fy27-fundamentals",
  "kind": "series",
  "title": "NVIDIA quarterly revenue and GAAP net income",
  "description": "Reported quarterly results show revenue scale and GAAP earnings conversion; net income includes volatile equity-security gains.",
  "as_of": "2026-08-26",
  "sources": [
    {"label": "NVIDIA fiscal Q2 2027 results", "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27pr.htm"}
  ],
  "x_axis": {"type": "category", "label": "Fiscal quarter", "values": ["Q2 FY2026", "Q1 FY2027", "Q2 FY2027"]},
  "y_axes": [{"label": "USD billions", "unit": "USD bn", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "Revenue", "render": "bar", "y_axis": 0, "values": ["46.743", "81.615", "96.221"]},
    {"name": "GAAP net income", "render": "line", "y_axis": 0, "values": ["26.422", "58.321", "59.688"]}
  ],
  "notes": ["GAAP net income includes gains and losses from equity securities; normalized valuation does not annualize it mechanically."]
}
```

Gross margin expanded despite the rapid scale-up, but Q3 guidance of 74.0% plus or minus 50 basis
points makes sustained margin, not the recent peak alone, the relevant gate.

```echart
{
  "schema_version": 1,
  "chart_id": "nvda-q2-fy27-gross-margin",
  "kind": "series",
  "title": "NVIDIA GAAP gross-margin progression",
  "description": "Reported GAAP gross margin shows whether rapid Data Center growth retains platform economics.",
  "as_of": "2026-08-26",
  "sources": [
    {"label": "NVIDIA fiscal Q2 2027 results", "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27pr.htm"}
  ],
  "x_axis": {"type": "category", "label": "Fiscal quarter", "values": ["Q2 FY2026", "Q1 FY2027", "Q2 FY2027"]},
  "y_axes": [{"label": "GAAP gross margin", "unit": "%", "format": "percent"}],
  "series": [
    {"name": "GAAP gross margin", "render": "line", "y_axis": 0, "values": ["72.4", "74.9", "75.0"]}
  ],
  "notes": ["Fiscal Q3 GAAP guidance is 74.0% plus or minus 50 basis points, so sustained margin rather than the Q2 peak is the valuation gate."]
}
```

The valuation view makes the widened upside and explicit downside visible; fair values are outputs
of stated forward-EPS and multiple assumptions, not price targets imported from an external source.

```echart
{
  "schema_version": 1,
  "chart_id": "nvda-september-2026-scenarios",
  "kind": "series",
  "title": "NVIDIA twelve-month valuation scenarios",
  "description": "Bear, base and bull values from normalized forward EPS and explicit multiples are compared with the current canonical mark.",
  "as_of": "2026-09-03",
  "sources": [
    {"label": "NVIDIA fiscal Q2 2027 Form 10-Q", "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm"},
    {"label": "PaperTrader canonical NVDA mark", "url": "https://finance.yahoo.com/quote/NVDA/history"}
  ],
  "x_axis": {"type": "category", "label": "Scenario", "values": ["Bear (30%)", "Base (50%)", "Bull (20%)"]},
  "y_axes": [{"label": "USD per share", "unit": "USD/share", "format": "currency", "currency": "USD"}],
  "series": [
    {"name": "Scenario fair value", "render": "bar", "y_axis": 0, "values": ["198.00", "310.50", "448.00"]},
    {"name": "Current price", "render": "line", "y_axis": 0, "values": ["228.4499969482422", "228.4499969482422", "228.4499969482422"]}
  ],
  "notes": ["Scenario values equal normalized forward EPS times the stated multiple; probability-weighted fair value is USD 303.65."]
}
```

Peer multiples are omitted because no same-date, definition-consistent peer pack was retained in
this bounded operation. Market share is omitted because no common, independently verified market
definition supports a comparable series. Revenue, net income, gross margin, the alert horizon and
the scenario set are charted; cash, debt, guarantees and commitments are point-in-time observations
and remain in prose.

<!-- papertrader:technical-chart:start -->
This deterministic monitoring chart is derived from the repository-local market cache. Its source CSV remains downloadable and does not feed research scoring or trading state.

```echart
{
  "schema_version": 2,
  "chart_id": "market-technicals",
  "kind": "technical",
  "title": "One-year price, volume, and technical indicators",
  "description": "Adjusted daily OHLC with Bollinger bands and moving averages, followed by volume, RSI, and MACD panels from the deterministic PaperTrader market cache.",
  "security_id": "security_33d9c44facc75c726c7d",
  "currency": "USD",
  "price_basis": "adjusted",
  "window_days": 365,
  "data_path": "data/market/technical/security_33d9c44facc75c726c7d.csv",
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

## Decision snapshot

NVIDIA remains the dominant accelerated-compute platform and fiscal second-quarter evidence
materially raises the earnings base, but the risk structure changed with it. At the canonical
**USD 228.45** close on **2026-09-03**, the revised probability-weighted fair value is **USD
303.65**. The mark is below the **USD 242.92** buy-below price, with positive base-case upside and
acceptable bear/base payoff. The research conclusion is therefore **Buy/Initiate**, subject to
deterministic eligibility calculation rather than an agent allocation decision.

The case is not low risk. NVIDIA disclosed **USD 279 billion** of supply commitments, **USD 105
billion** of capped land, power and shell guarantees related to an OpenAI-serving campus, longer
customer payment terms, higher inventory, and USD 25 billion of new debt. These commitments can
secure multi-generation demand, but they also transfer customer-financing, concentration and
infrastructure risk onto NVIDIA's balance sheet.

## What changed in the alert period

The canonical **2026-08-06 through 2026-09-03** observation rose from **USD 219.00 to USD 228.45**,
or **4.32%**. The 26 August results-day close advanced **8.74%**, followed by a partial retracement.
On 3 September, MACD **3.256** crossed above its **2.787** signal while RSI was **59.21**; the close
was above the 20-, 50- and 200-session averages and below the upper Bollinger band. Volume did not
trigger an anomaly. The crossover is a bullish timing confirmation, not independent valuation
evidence.

Current primary evidence explains the period. Fiscal Q2 revenue of **USD 96.221 billion** exceeded
the prior USD 91 billion outlook midpoint, grew 18% sequentially and 106% annually, while Data
Center reached **USD 89.023 billion**. Fiscal Q3 guidance is **USD 108 billion plus or minus 2%**
and assumes no China Data Center compute revenue. The September Hugging Face agreement adds an
open-model distribution asset but is not large enough by itself to explain the earnings reset.

**Classification: opportunity with material new risk.** Operating evidence supports a higher
valuation range and the current mark now clears the revised bounded entry frontier. The same
evidence requires lower confidence than headline growth alone would suggest because supply,
guarantee, customer-credit and acquisition exposures expanded sharply.

## Business and instrument economics

- **Compute platform:** Accelerators, networking, systems, CUDA and model tooling are sold as an
  integrated platform. Data Center represented about 92.5% of fiscal Q2 revenue.
- **Economics:** GAAP gross margin was 75.0%; operating income reached USD 63.734 billion and GAAP
  net income USD 59.688 billion. Net income included USD 7.8 billion of gains from equity
  securities, so valuation uses normalized forward EPS rather than annualizing GAAP EPS blindly.
- **Cadence:** Blackwell remained the vast majority of revenue and Vera Rubin entered full
  production. Execution across memory, foundry, packaging, systems and customer deployment is the
  principal near-term operating gate.
- **Liquidity and working capital:** Cash, equivalents and marketable debt securities were USD
  56.6 billion. Receivables reached USD 63.1 billion and 60 days sales outstanding versus 45 days
  sequentially; inventory rose to USD 31.6 billion. Operating cash flow was USD 24.1 billion,
  down from USD 50.3 billion sequentially.
- **Capital structure:** NVIDIA issued USD 25.0 billion of senior unsecured notes, while returning
  nearly USD 26 billion to shareholders. Strong earnings support liquidity, but the simultaneous
  debt, commitment and guarantee expansion reduces balance-sheet conservatism.

## Thesis, catalysts, risks and invalidation

The thesis is that demand for useful AI inference, training and physical-AI workloads continues to
compound while NVIDIA retains system-level performance, networking and software advantages. Fiscal
Q2 and Q3 guidance support that mechanism. The strongest contrary evidence is that a growing share
of future demand now depends on highly concentrated customers, customer financing, long-duration
power capacity, third-party manufacturing and rapid product transitions.

**Catalysts:** delivery against USD 108 billion Q3 guidance; Rubin ramp without material margin or
working-capital deterioration; diversification beyond the largest AI labs; durable networking and
software attachment; China-compatible products that comply with export rules; and Hugging Face
closing with measurable developer and enterprise monetization.

**Risks:** custom accelerators and open software reducing platform rents; export controls; foundry,
HBM and packaging constraints; receivable collection and customer concentration; commitment or
guarantee losses; inventory obsolescence; margin compression; Hugging Face regulatory or integration
failure; and customer AI returns failing to justify the infrastructure cycle.

**Invalidation:** downgrade the thesis if normalized EPS falls below the bear-case path, gross
margin remains below 70%, receivables or guarantees produce material losses, Rubin adoption misses
the current cycle, or CUDA and networking attachment weaken enough that platform economics no
longer justify a premium multiple.

## Valuation

Template: **mature compounder** (`mature_compounder`) using the permitted
`earnings_multiple` method. Horizon: **12 months**.
The starting point is normalized fiscal Q2 EPS of USD 2.22, Q3 revenue guidance above Q2, and the
need to exclude volatile equity-security gains. Values are in USD per share and use no FX conversion
because both the instrument and scenarios are USD-denominated.

| Scenario | Probability | Forward normalized EPS | Multiple | Fair value | Key assumptions |
| --- | ---: | ---: | ---: | ---: | --- |
| Bear | 30% | 9.00 | 22x | 198.00 | Growth normalizes sharply; gross margin approaches 70%; customer-credit and supply commitments reduce the justified premium. |
| Base | 50% | 11.50 | 27x | 310.50 | Q3 guidance converts, Rubin extends growth, normalized earnings expand, but infrastructure financing and concentration cap the multiple. |
| Bull | 20% | 14.00 | 32x | 448.00 | Broad inference and physical-AI demand, strong Rubin execution and durable platform rents outweigh financing and export risk. |

The probability-weighted value is **USD 303.65**. Against USD 228.45, scenario returns are
approximately **-13.33%**, **35.92%**, and **96.10%**; the weighted return is approximately
**32.92%** before deterministic confidence adjustment. The 20% margin-of-safety buy-below price is
**USD 242.92**. These outputs must be reproduced by the assessment CLI; the page does not override
its canonical eligibility frontier.

## Idea exposure map

### Canonical accepted relationships

- [[ideas/idea_ai_compute_networking_hyperscaler_monetization]] — **accepted-current, positive,
  high sensitivity.** Revenue, Data Center growth, networking and the Rubin roadmap directly
  transmit the AI-infrastructure cycle; Q2 materially strengthens the evidence. See
  [[relationships/relationship_ai_compute_nvda]].
- [[ideas/idea_humanoid_robotics_embodied_ai_components]] — **accepted-current, positive, medium
  sensitivity.** Simulation, world models, Jetson/Thor, safety tooling and edge compute remain a
  credible enabling channel, but attributable humanoid economics are still undisclosed. See
  [[relationships/relationship_humanoid_nvda]].
- [[ideas/idea_terafab_ai_industrial_stack]] — **accepted-current, positive, medium sensitivity.**
  SpaceXAI's prospective Vera adoption and orbital products support near-term merchant demand;
  no binding Terafab manufacturing economics are disclosed. See
  [[relationships/relationship_terafab_nvda]].

### Candidate requiring relationship review

- [[ideas/idea_ai_infrastructure_power]] — **candidate, mixed-positive, high materiality.** NVIDIA
  can accelerate land-and-power deployment and sell successive compute generations, but its USD
  105 billion capped guarantee and long-duration commitments create direct credit and concentration
  exposure. The edge is material and newly evidenced, but it is not canonical until a separate
  relationship review accepts or rejects it. Invalidate the positive channel if projects slip,
  guarantees crystallize without profitable hardware demand, or customers cannot finance renewal.

### Evaluated but rejected-no-link

- [[ideas/idea_commercial_space_infrastructure]]: Space-1 and SpaceXAI are products/customer leads,
  but no material space-attributable NVIDIA revenue or backlog is disclosed; the specific orbital
  mechanism remains captured by the accepted Terafab edge.
- [[ideas/idea_ai_native_drug_discovery]] and
  [[ideas/idea_precision_biology_healthcare_automation]]: BioNeMo and the Lilly collaboration show
  tool adoption, but they do not establish material NVIDIA economics distinct from general compute.
- [[ideas/idea_wide_bandgap_power_semiconductors]]: NVIDIA's 800 VDC architecture influences
  downstream component demand, but NVIDIA is neither a direct WBG supplier nor a demonstrated
  beneficiary of supplier economics.

The complete 28-page idea catalog was searched across products, customers, suppliers, cost drivers,
constraints and aliases. Other maintained ideas lacked a specific material transmission mechanism;
no thematic-only edge is proposed.

## Changes since prior review

- **Facts and evidence:** fiscal Q2 revenue, Data Center revenue, earnings and Q3 guidance replaced
  the prior Q1 evidence. The Hugging Face agreement, USD 279 billion supply commitments, USD 105
  billion guarantee cap, longer receivables, higher inventory and new debt are new.
- **Valuation:** bear/base/bull values changed from USD 180/USD 252/USD 374 at 25%/50%/25% to USD
  198/USD 310.50/USD 448 at 30%/50%/20%. The earnings base rose; downside probability also rose to
  reflect balance-sheet and customer-financing exposure.
- **Thesis and action:** the platform thesis is strengthened, while financial-risk confidence is
  reduced. The page remains Buy/Initiate, but the current price moves from outside the old buy-below
  frontier to inside the revised one; deterministic code owns the final research and eligibility
  classifications.
- **Catalysts and risks:** Q3 conversion and Rubin replace Q2 reporting as immediate catalysts.
  Guarantees, commitments, DSO, acquisition execution and customer finance are added risks.
- **Graph:** all three accepted edges remain current. AI infrastructure power is added only as a
  candidate requiring separate review. Commercial space, drug-discovery/healthcare automation and
  wide-bandgap associations are explicitly rejected as non-material or duplicative.
- **Blockers and gaps:** the former insufficient-margin-of-safety and downside-payoff gaps are
  expected to resolve under the revised scenarios. Customer concentration, guarantee exposure and
  normalized earnings durability remain monitored risks rather than concealed gaps. No conclusion
  is changed by the MACD signal alone.

## Sources

- [NVIDIA fiscal 2027 second-quarter Form 10-Q](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm)
- [NVIDIA fiscal 2027 second-quarter results](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27pr.htm)
- [NVIDIA fiscal 2027 second-quarter CFO commentary](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27cfocommentary.htm)
- [NVIDIA Hugging Face acquisition Form 8-K](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000080/nvda-20260902.htm)
- [PaperTrader canonical NVDA alert packet](../inbox/market-security_33d9c44facc75c726c7d-macd_cross_above_signal-b5b67bfce931.md)

See the complete [[research-catalog]], results-first [[index]], and append-only [[log]].
