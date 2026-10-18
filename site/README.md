# Research notebook site

Pinned Quartz5 renders current company and idea research, native-currency
valuation rankings, freshness and current source links. It has no portfolio,
signal, performance, trade-action or media views/downloads.

```sh
npm ci --ignore-scripts
PAPERTRADER_BASE_URL=localhost npm run check
PAPERTRADER_BASE_URL=localhost npm run build
```

Run from site/ after installing the repository's locked Python dependencies.
PAPERTRADER_BASE_URL is a host/path without `https://`. WIKI_PATH defaults to
../data/wiki. PAPERTRADER_SITE_OUTPUT optionally selects the generated artifact
location. Build inputs are validated current CSVs, source-linked Markdown and
research.ini. An isolated temporary closure excludes retired content and keeps
current source assets. Generated public/ and quartz/ are ignored.

Optional analytical JSON ECharts render with the pinned local vendor asset and
visible source/data fallback. No remote chart code, technical-series hydration
or chart requirement blocks research or market updates. The postbuild command
checks internal links. `pages.yml` builds a known committed SHA, with deployment
credentials confined to its independent deployment job.

Quartz5 is pinned to upstream commit3dff48b5df6d84c9544a5ae19c8f2cbb01dc44e5;
community plugins, Apache ECharts and Sharp are locked in package-lock.json.
prepare-quartz.mjs recreates the ignored engine and local brand/vendor assets.
