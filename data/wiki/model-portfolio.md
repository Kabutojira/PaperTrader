---
title: "PaperTrader model portfolio"
type: model-portfolio
status: maintained
tags:
  - model-portfolio
created: "2026-09-08"
updated: "2026-09-08"
provenance: deterministic-decision-projection
snapshot_id: "decision_32e713083eb5f50f0166"
as_of: "2026-09-08T18:58:30Z"
---

# Model portfolio

**As of `2026-09-08T18:58:30Z`**

Pending targets are projections; only deterministic fills change the current portfolio.

<div class="model-portfolio-grid" id="model-portfolio-grid">
<article class="portfolio-card" data-scalable="false" data-target-weight="97.09953" data-mark="1" data-fx="1" data-mark-currency="" data-market-data-as-of="2026-09-08T18:58:30Z" data-ticker="CASH" data-company="Cash">
<h3>Cash</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>97.09953%</dd></div>
<div><dt>Target</dt><dd>97.09953%</dd></div>
<div><dt>Action</dt><dd>No trade</dd></div>
<div><dt>State</dt><dd>No action</dd></div>
<div><dt>Research rating</dt><dd>Unrated</dd></div>
<div><dt>Research action</dt><dd>Hold</dd></div>
<div><dt>Reference mark</dt><dd>1 </dd></div>
<div><dt>Base mark</dt><dd>1 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-08T18:58:30Z</dd></div>
<div><dt>As of</dt><dd>2026-09-08T18:58:30Z</dd></div>
</dl>

</article>
<article class="portfolio-card" data-scalable="true" data-target-weight="2.90047" data-mark="36.22999954223633" data-fx="1" data-mark-currency="EUR" data-market-data-as-of="2026-09-08T15:30:00Z" data-ticker="PRX" data-company="Prosus N.V.">
<h3><a href="securities/security_8b703a8adf5f864acaa4">PRX — Prosus N.V.</a></h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>2.90047%</dd></div>
<div><dt>Target</dt><dd>2.90047%</dd></div>
<div><dt>Action</dt><dd>Hold</dd></div>
<div><dt>State</dt><dd>Filled</dd></div>
<div><dt>Research rating</dt><dd>Buy</dd></div>
<div><dt>Research action</dt><dd>Initiate</dd></div>
<div><dt>Reference mark</dt><dd>36.22999954223633 EUR</dd></div>
<div><dt>Base mark</dt><dd>36.22999954223633 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-09-08T18:58:30Z</dd></div>
<div><dt>As of</dt><dd>2026-09-08T15:30:00Z</dd></div>
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
| [PRX — Prosus N.V.](securities/security_8b703a8adf5f864acaa4) | Buy / Initiate | -17.19569312987017928024178556% / 43.5274652415583559142475717% / 93.2100493636362483461025004% | 35.2470345545453738422717503% | 41.6 | 2026-09-27T19:18:00Z | Prosus offers Tencent-dominated look-through value, growing ecommerce exposure and per-share accretion from repurchases below NAV; the current plan's economics justify a bounded long-equity baseline increase because medium confidence, holding-company concentration, private-asset valuation uncertainty, central debt, governance, capital-allocation transmission and insufficient diversification prevent conviction treatment. |

[[index|Back to today's decision]]
