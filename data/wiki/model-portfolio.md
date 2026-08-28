---
title: "PaperTrader model portfolio"
type: model-portfolio
status: maintained
tags:
  - model-portfolio
created: "2026-08-28"
updated: "2026-08-28"
provenance: deterministic-decision-projection
snapshot_id: "decision_835c8431827585c591dd"
as_of: "2026-08-28T20:24:48Z"
---

# Model portfolio

**As of `2026-08-28T20:24:48Z`**

Pending targets are projections; only deterministic fills change the current portfolio.

<div class="model-portfolio-grid" id="model-portfolio-grid">
<article class="portfolio-card" data-scalable="false" data-target-weight="100" data-mark="1" data-fx="1" data-mark-currency="" data-market-data-as-of="2026-08-28T20:24:48Z" data-ticker="CASH" data-company="Cash">
<h3>Cash</h3>
<dl class="portfolio-card-values">
<div><dt>Current</dt><dd>100%</dd></div>
<div><dt>Target</dt><dd>100%</dd></div>
<div><dt>Action</dt><dd>No trade</dd></div>
<div><dt>State</dt><dd>No action</dd></div>
<div><dt>Research rating</dt><dd>Unrated</dd></div>
<div><dt>Research action</dt><dd>Hold</dd></div>
<div><dt>Reference mark</dt><dd>1 </dd></div>
<div><dt>Base mark</dt><dd>1 EUR</dd></div>
<div><dt>FX to EUR</dt><dd>1 · 2026-08-28T20:24:48Z</dd></div>
<div><dt>As of</dt><dd>2026-08-28T20:24:48Z</dd></div>
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

## Comparison-only research benchmark

This deterministic equal-weight benchmark is for research comparison only. It is comparison-only, is not copy-ready, and has no path to signals or orders.

| Security | Rating | Weight | Reference price |
| --- | --- | ---: | ---: |
| [PRX — Prosus N.V.](securities/security_8b703a8adf5f864acaa4) | Buy | 10% | 38.689998626708984 EUR |
| [DLO — DLocal Limited](securities/security_715bde20b6e1e1320c1a) | Buy | 10% | 15.529999732971191 USD |
| [NVDA — NVIDIA Corporation](securities/security_33d9c44facc75c726c7d) | Buy | 10% | 218.99000549316406 USD |
| [NOMD — Nomad Foods Limited](securities/security_98a1943771da875efed5) | Buy | 10% | 11.989999771118164 USD |
| [DPZ — Domino's Pizza, Inc.](securities/security_f34181f3df32080a91d1) | Buy | 10% | 332.05999755859375 USD |
| [TCEHY — Tencent Holdings Limited](securities/security_de0d83229b369a426b99) | Buy | 10% | 56.88999938964844 USD |
| Cash | Unrated | 40% | 1 — |

[[index|Back to today's decision]]
