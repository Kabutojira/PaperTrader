---
title: "PaperTrader model portfolio"
type: model-portfolio
status: maintained
tags:
  - model-portfolio
created: "2026-09-09"
updated: "2026-09-09"
provenance: deterministic-decision-projection
snapshot_id: "decision_8b115dd5f9f91ae3d705"
as_of: "2026-09-09T19:22:57Z"
---

# Model portfolio

**As of `2026-09-09T19:22:57Z`**

Pending targets are projections; only deterministic fills change the current portfolio.

<div class="model-portfolio-grid" id="model-portfolio-grid">
<article class="portfolio-card" data-scalable="false" data-target-weight="95.196133" data-mark="1" data-fx="1" data-mark-currency="" data-market-data-as-of="2026-09-09T19:22:57Z" data-ticker="CASH" data-company="Cash">
<h3>Cash</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>97.138024%</dd></div>
<div><dt>Target</dt><dd>95.196133%</dd></div>
<div><dt>Action</dt><dd>Trim</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Unrated</dd></div>
<div><dt>Research action</dt><dd>Hold</dd></div>
<div><dt>Reference mark</dt><dd>1 </dd></div>
<div><dt>Base mark</dt><dd>1 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-09T19:22:57Z</dd></div>
<div><dt>As of</dt><dd>2026-09-09T19:22:57Z</dd></div>
</dl>

</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="1.941599" data-mark="225.72999572753906" data-fx="0.8590999841690063" data-mark-currency="USD" data-market-data-as-of="2026-09-09T18:24:19Z" data-ticker="NVDA" data-company="NVIDIA Corporation">
<h3><a href="securities/security_33d9c44facc75c726c7d">NVDA — NVIDIA Corporation</a></h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>0%</dd></div>
<div><dt>Target</dt><dd>1.941599%</dd></div>
<div><dt>Action</dt><dd>Buy</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Buy</dd></div>
<div><dt>Research action</dt><dd>Initiate</dd></div>
<div><dt>Reference mark</dt><dd>225.72999572753906 USD</dd></div>
<div><dt>Base mark</dt><dd>193.9246357559986661823022246 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>0.8590999841690063 · 2026-09-09T18:24:19Z</dd></div>
<div><dt>As of</dt><dd>2026-09-09T18:24:19Z</dd></div>
</dl>
<p><a href="strategies/strategy_7cf884a5530d05afdb99">Strategy research</a></p>
</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="2.862268" data-mark="35.73500061035156" data-fx="1" data-mark-currency="EUR" data-market-data-as-of="2026-09-09T15:30:00Z" data-ticker="PRX" data-company="Prosus N.V.">
<h3><a href="securities/security_8b703a8adf5f864acaa4">PRX — Prosus N.V.</a></h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>2.861976%</dd></div>
<div><dt>Target</dt><dd>2.862268%</dd></div>
<div><dt>Action</dt><dd>Hold</dd></div>
<div><dt>State</dt><dd>Filled</dd></div>
<div><dt>Research rating</dt><dd>Buy</dd></div>
<div><dt>Research action</dt><dd>Initiate</dd></div>
<div><dt>Reference mark</dt><dd>35.73500061035156 EUR</dd></div>
<div><dt>Base mark</dt><dd>35.73500061035156 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-09T19:22:57Z</dd></div>
<div><dt>As of</dt><dd>2026-09-09T15:30:00Z</dd></div>
</dl>
<p><a href="strategies/strategy_8caa208dfc702a2584a7">Strategy research</a></p>
</article>
</div>
<p class="portfolio-base">Values use the committed EUR snapshot.</p>

<div class="portfolio-controls" aria-label="Portfolio copy and scaling tools">
<button type="button" id="copy-portfolio">Copy portfolio as TSV</button>
<a class="button-link" href="data/model_portfolio.csv" download>Download committed CSV</a>
<a class="button-link" href="data/decision_snapshot.json" download>Download snapshot JSON</a>
<label for="reference-notional">Reference portfolio value</label>
<input id="reference-notional" type="number" min="0" step="100" inputmode="decimal">
<button type="button" id="scale-portfolio">Calculate whole-share quantities</button>
</div>
<p class="scaler-notice">The calculation runs only in this browser and does not write portfolio state.</p>
<div id="scaled-portfolio" aria-live="polite"></div>

## Valuation and thesis detail

| Holding | Rating / action | Bear / base / bull | Expected | Buy below | Review | Thesis or cash role |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Cash | Unrated / Hold | —% / —% / —% | —% | — | — | Capital retained as the configured portfolio alternative. |
| [NVDA — NVIDIA Corporation](securities/security_33d9c44facc75c726c7d) | Buy / Initiate | -12.28458612164674774643077227% / 37.5537172183266910340062889% / 98.4671990782942273212071415% | 34.7849225883281666573153411% | 248.4 | 2026-09-18T06:22:45Z | NVIDIA's accelerated-compute, networking and software platform converts current AI infrastructure demand into exceptional revenue and cash-generation potential; the current plan supports bounded long-equity baseline exposure because medium confidence, customer concentration, supply commitments, guarantees, export controls, product-transition risk and insufficient diversification prevent conviction treatment. |
| [PRX — Prosus N.V.](securities/security_8b703a8adf5f864acaa4) | Buy / Initiate | -16.04869319266296554909132287% / 45.5155984660508597149083737% / 95.88638255045308038545358% | 37.120467785317156269817506% | 41.6 | 2026-09-27T19:18:00Z | Prosus offers Tencent-dominated look-through value, growing ecommerce exposure and per-share accretion from repurchases below NAV; the current plan's economics justify a bounded long-equity baseline increase because medium confidence, holding-company concentration, private-asset valuation uncertainty, central debt, governance, capital-allocation transmission and insufficient diversification prevent conviction treatment. |

[[index|Back to today's decision]]
