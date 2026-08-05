---
title: "PaperTrader model portfolio"
type: model-portfolio
status: maintained
tags:
  - model-portfolio
created: "2026-08-05"
updated: "2026-08-05"
provenance: deterministic-decision-projection
snapshot_id: "decision_438a97c488fc7fa4fbc0"
as_of: "2026-08-05T20:06:58Z"
---

# Model portfolio

**Snapshot `decision_438a97c488fc7fa4fbc0` · As of `2026-08-05T20:06:58Z`**

Pending targets are projections; only deterministic fills change the current portfolio.

<div class="model-portfolio-grid" id="model-portfolio-grid">
<article class="portfolio-card" data-scalable="false" data-target-weight="100" data-mark="1" data-fx="1" data-mark-currency="" data-market-data-as-of="2026-08-05T20:06:58Z" data-ticker="CASH" data-company="Cash">
<h3>Cash</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>100%</dd></div>
<div><dt>Approved target</dt><dd>100%</dd></div>
<div><dt>Action</dt><dd>No trade</dd></div>
<div><dt>State</dt><dd>No action</dd></div>
<div><dt>Research rating</dt><dd>Unrated</dd></div>
<div><dt>Research action</dt><dd>Hold</dd></div>
<div><dt>Reference mark</dt><dd>1 </dd></div>
<div><dt>Base mark</dt><dd>1 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-08-05T20:06:58Z</dd></div>
<div><dt>As of</dt><dd>2026-08-05T20:06:58Z</dd></div>
</dl>

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

## Non-approved research benchmark

This deterministic equal-weight benchmark is for research comparison only. It is not an approved allocation, is not copy-ready, and has no path to signals or orders.

| Security | Rating | Weight | Reference price |
| --- | --- | ---: | ---: |
| [NVDA — NVIDIA Corporation](securities/security_33d9c44facc75c726c7d) | Buy | 25% | 211.94000244140625 USD |
| Cash | Unrated | 75% | 1 — |

[[index|Back to today's decision]]
