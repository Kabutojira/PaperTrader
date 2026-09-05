---
title: "PaperTrader model portfolio"
type: model-portfolio
status: maintained
tags:
  - model-portfolio
created: "2026-09-05"
updated: "2026-09-05"
provenance: deterministic-decision-projection
snapshot_id: "decision_103f08004374f00ba869"
as_of: "2026-09-05T20:37:23Z"
---

# Model portfolio

**As of `2026-09-05T20:37:23Z`**

Pending targets are projections; only deterministic fills change the current portfolio.

<div class="model-portfolio-grid" id="model-portfolio-grid">
<article class="portfolio-card" data-scalable="false" data-target-weight="91.950122" data-mark="1" data-fx="1" data-mark-currency="" data-market-data-as-of="2026-09-05T20:37:23Z" data-ticker="CASH" data-company="Cash">
<h3>Cash</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>97.030007%</dd></div>
<div><dt>Target</dt><dd>91.950122%</dd></div>
<div><dt>Action</dt><dd>Trim</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Unrated</dd></div>
<div><dt>Research action</dt><dd>Hold</dd></div>
<div><dt>Reference mark</dt><dd>1 </dd></div>
<div><dt>Base mark</dt><dd>1 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-05T20:37:23Z</dd></div>
<div><dt>As of</dt><dd>2026-09-05T20:37:23Z</dd></div>
</dl>

</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="3.9653" data-mark="230.36000061035156" data-fx="0.8604999780654907" data-mark-currency="USD" data-market-data-as-of="2026-09-05T20:09:19Z" data-ticker="NVDA" data-company="NVIDIA Corporation">
<h3><a href="securities/security_33d9c44facc75c726c7d">NVDA — NVIDIA Corporation</a></h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>0%</dd></div>
<div><dt>Target</dt><dd>3.9653%</dd></div>
<div><dt>Action</dt><dd>Buy</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Buy</dd></div>
<div><dt>Research action</dt><dd>Initiate</dd></div>
<div><dt>Reference mark</dt><dd>230.36000061035156 USD</dd></div>
<div><dt>Base mark</dt><dd>198.2247754723739416442380309 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>0.8604999780654907 · 2026-09-05T20:09:19Z</dd></div>
<div><dt>As of</dt><dd>2026-09-05T20:09:19Z</dd></div>
</dl>
<p><a href="strategies/strategy_7cf884a5530d05afdb99">Strategy research</a></p>
</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="4.084578" data-mark="37.125" data-fx="1" data-mark-currency="EUR" data-market-data-as-of="2026-09-04T15:30:00Z" data-ticker="PRX" data-company="Prosus N.V.">
<h3><a href="securities/security_8b703a8adf5f864acaa4">PRX — Prosus N.V.</a></h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>2.969993%</dd></div>
<div><dt>Target</dt><dd>4.084578%</dd></div>
<div><dt>Action</dt><dd>Add</dd></div>
<div><dt>State</dt><dd>Pending validated order</dd></div>
<div><dt>Research rating</dt><dd>Buy</dd></div>
<div><dt>Research action</dt><dd>Initiate</dd></div>
<div><dt>Reference mark</dt><dd>37.125 EUR</dd></div>
<div><dt>Base mark</dt><dd>37.125 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-05T20:37:23Z</dd></div>
<div><dt>As of</dt><dd>2026-09-04T15:30:00Z</dd></div>
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
| [NVDA — NVIDIA Corporation](securities/security_33d9c44facc75c726c7d) | Buy / Initiate | -14.04757793219827615411185935% / 34.7890255154163396674154933% / 94.4782075069453145603933687% | 32.0758808794377498995528626% | 248.4 | 2026-09-18T06:22:45Z | NVIDIA's accelerated-compute, networking and software platform converts current AI infrastructure demand into exceptional revenue and cash-generation potential; the current plan supports bounded long-equity baseline exposure because medium confidence, customer concentration, supply commitments, guarantees, export controls, product-transition risk and insufficient diversification prevent conviction treatment. |
| [PRX — Prosus N.V.](securities/security_8b703a8adf5f864acaa4) | Buy / Initiate | -19.19191919191919191919191919% / 40.0673400673400673400673401% / 88.5521885521885521885521886% | 31.986531986531986531986532% | 41.6 | 2026-09-27T19:18:00Z | Prosus offers Tencent-dominated look-through value, growing ecommerce exposure and per-share accretion from repurchases below NAV; the current plan's economics justify a bounded long-equity baseline increase because medium confidence, holding-company concentration, private-asset valuation uncertainty, central debt, governance, capital-allocation transmission and insufficient diversification prevent conviction treatment. |

[[index|Back to today's decision]]
