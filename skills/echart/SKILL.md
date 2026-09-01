---
name: echart
description: Design accessible Apache ECharts visualizations for quantitative research. Use when chartable evidence should be embedded in PaperTrader wiki research or when an ECharts chart is explicitly requested.
---

# Apache ECharts research visualizations

Turn decision-relevant quantitative evidence into clear, sourceable charts. Choose the chart that
best exposes the comparison, trend, composition, distribution, price action, or relationship; do
not chart a number merely because it exists.

This skill is adapted from `nealepetrillo/claude-skills-echart` at commit
`c466b46736a338f0916299f7fb2b5b4117062bb8`. The copied upstream material is MIT-licensed; see
`LICENSE`.

## PaperTrader mode

When working in the PaperTrader repository, read
[`references/papertrader-embedding.md`](references/papertrader-embedding.md) and follow it as the
authoritative output contract. Emit only validated, non-executable `echart` JSON fences inside the
research Markdown page. Never add inline JavaScript, standalone HTML, remote data requests, or CDN
references to research content. Quartz owns rendering and the Markdown fence remains the portable
data fallback.

Use a chartability pass after the research conclusion is supported. Include every
decision-relevant dataset that has enough comparable observations to improve understanding, within
the bounded core dataset defined by the operation skill. Record a concise omission when material
data is unavailable, incomparable, too sparse, or not decision-relevant. A chart never substitutes
for prose interpretation, canonical state, or source citations.

## Design decisions

Read [`references/design-principles.md`](references/design-principles.md) when selecting chart
families, colors, axes, labels, or accessibility treatment. Prefer:

- line/area for ordered time series;
- bars for entity or category comparison;
- scatter for two-variable relationships;
- stacked bars or a small donut for composition;
- candlesticks only for useful price-action analysis;
- heatmaps for a bounded two-dimensional matrix;
- graph or Sankey views only when relationships or flows are the evidence.

Avoid decorative gauges, 3D effects, misleading truncated value axes, dual axes without explicit
units, and pies with many slices. Keep the no-JavaScript data table and prose interpretation useful
on their own.

## Generic ECharts work

Outside PaperTrader, use Apache ECharts v6 and the locally installed dependency when one exists.
Read [`references/chart-examples.md`](references/chart-examples.md) only when implementation details
for a selected chart family are needed. Prefer accessible local assets; use a CDN only when the user
explicitly asks for one.
