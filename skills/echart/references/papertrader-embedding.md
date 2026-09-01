# PaperTrader chart embedding contract

Use this reference only for PaperTrader research pages.

## Chartability pass

Review the bounded evidence gathered by the active research skill after reaching the research
conclusion. A dataset is chartable when it is decision-relevant and contains either at least three
comparable observations, or at least two periods for each of at least two comparable series.
Single values and incomparable measurements remain prose or tables. Do not fetch extra data solely
to make a chart and do not expand the operation's research scope.

Typical security-research charts include revenue and GAAP operating or net income history, margins
or free cash flow, scenario values, price context, and like-for-like peer valuation, market
capitalization, or market share. Use only the subsets that materially illuminate the decision.
Represent an unavailable or meaningless multiple, including P/E for negative earnings, as `null`.

## Markdown output

Place a `## Visual evidence` section in every successfully changed primary research page. Embed each
chart as strict JSON in a fenced block whose language is exactly `echart`:

````markdown
```echart
{
  "schema_version": 1,
  "chart_id": "revenue-and-net-income",
  "kind": "series",
  "title": "Revenue and GAAP net income",
  "description": "Annual results show operating scale and earnings conversion.",
  "as_of": "2026-06-30",
  "sources": [{"label": "Issuer FY 2025 annual report", "url": "https://example.com/filing"}],
  "x_axis": {"type": "category", "label": "Fiscal year", "values": ["2023", "2024", "2025"]},
  "y_axes": [{"label": "USD", "unit": "USD", "format": "currency"}],
  "series": [
    {"name": "Revenue", "render": "bar", "y_axis": 0, "values": ["100", "115", "130"]},
    {"name": "GAAP net income", "render": "line", "y_axis": 0, "values": ["8", "10", "13"]}
  ]
}
```
````

The canonical schema is `schemas/research_chart.schema.json`; it overrides examples. Numeric data
must be decimal strings or `null`, never binary floating-point JSON numbers. Use ISO dates and
timestamps, ISO currency codes, immutable entity IDs where supported, and explicit units. Align
series to the same categories and use the same measurement definition, period, currency, and FX
basis for comparisons. State material caveats in `notes`.

Chart blocks are derived presentation data. They may summarize canonical tables and cited public
evidence but never become inputs to allocation, signals, orders, fills, cash, positions, or
performance.

## Result manifest

For a successful applicable operation, add `visualization_review` to `agent_result.json` with
`completed: true`, every emitted `{page_path, chart_id}`, and any bounded omissions. If a successful
operation changes no primary research page, record the `no_page_change` omission. If no chart is
warranted, leave `charts` empty and give at least one specific omission; never manufacture data.

Quartz renders valid blocks with its pinned local Apache ECharts asset. GitHub, feeds, and
JavaScript-disabled browsers retain the JSON plus the surrounding prose, so descriptions, sources,
units, and interpretation must remain understandable without the interactive view.
