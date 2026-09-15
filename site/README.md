# PaperTrader website

The site runs Quartz **5.0.0**, pinned to upstream commit
`3dff48b5df6d84c9544a5ae19c8f2cbb01dc44e5`. Community plugins are npm packages
locked by `package-lock.json`. No plugin installer or network access is needed
during a build after dependencies have been installed.

```sh
npm ci --prefix site --ignore-scripts
npm run check --prefix site
PAPERTRADER_BASE_URL=localhost npm run build --prefix site
```

Set `PAPERTRADER_BASE_URL` to the deployment host and path (for example,
`owner.github.io/PaperTrader`) for a production build. `localhost` is for preview.

Quartz 5 reads `quartz.ts`. It imports our typed configuration and conditional
layouts from `quartz.config.ts` and `quartz.layout.ts`. Page plugins are registered
under `pageTypes` and rendered by the v5 `PageTypeDispatcher`. Date selection now
belongs to the `CreatedModifiedDate` plugin. Keep all customizations outside the
generated, ignored `quartz/` directory: `prepare-quartz.mjs` recreates it from the
pinned dependency on each build. The wrapper explicitly copies its prepared static
assets after rendering because the upstream static emitter ignores Git-ignored
engine directories.

## Visual identity

Original, editable vector artwork lives in `papertrader/assets/`:

- `icon.svg`: folded-page P mark, used in navigation and as the SVG favicon.
- `research-garden.svg`: decorative research notebook illustration for the homepage.
- `social-card.svg`: social sharing artwork.

The preparation step copies these local assets and uses locked Sharp to export
the PNG favicon, Apple touch icon, and social preview. The homepage illustration
is decorative and does not represent financial data. Components and styles live
under `papertrader/`; canonical generated wiki pages are never edited for branding.

Quartz's [v5 migration guide](https://github.com/jackyzha0/quartz/blob/3dff48b5df6d84c9544a5ae19c8f2cbb01dc44e5/docs/getting-started/migrating.md)
describes the upstream plugin and page-type changes.
