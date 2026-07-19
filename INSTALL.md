# Installation

This guide installs the PaperTrader skill for Hermes Agent without enabling live trading.

## 1. Prerequisites

- Hermes Agent installed and available as `hermes`
- Git
- Bash for the helper installer
- Python 3.10 or newer
- Access to the PaperTrader Google Sheet
- A paper-trading broker account or simulator: `[DA DEFINIRE]`
- A market-data/options-data source: `[DA DEFINIRE]`

Verify the local tools:

```bash
hermes --version
python3 --version
git --version
```

## 2. Clone the repository

```bash
git clone https://github.com/Kabutojira/PaperTrader.git
cd PaperTrader
```

Do not place API keys, service-account JSON, OAuth refresh tokens, broker credentials, or private certificates in this repository.

## 3. Validate the checkout

```bash
./scripts/check.sh
```

The check validates the repository shape, Hermes skill frontmatter, JSON templates, and the deterministic example-signal validator.

## 4. Expose the skill to Hermes

### Option A — safe local symlink

```bash
./scripts/install-local.sh
```

This links:

```text
~/.hermes/skills/papertrader -> <repository>/Skills/papertrader
```

The script refuses to overwrite an existing skill directory.

To install a copy instead of a symlink:

```bash
./scripts/install-local.sh --copy
```

### Option B — Hermes external skill directory

Add the exact absolute path to `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - /absolute/path/to/PaperTrader/Skills
```

The directory is writable by Hermes if filesystem permissions allow it. Use read-only permissions or a review workflow when agent-authored skill changes must not modify the checkout.

### Option C — direct GitHub skill install

For a repository visible to Hermes/GitHub credentials:

```bash
hermes skills install Kabutojira/PaperTrader/Skills/papertrader
```

A private repository requires an appropriate `GITHUB_TOKEN` configured locally. Never paste that token into chat or commit it.

## 5. Configure non-secret skill settings

The skill declares these settings:

| Key | Initial value |
|---|---|
| `papertrader.sheet_id` | `[DA DEFINIRE]` |
| `papertrader.mode` | `PAPER` |
| `papertrader.timezone` | `Europe/Rome` |
| `papertrader.broker` | `[DA DEFINIRE]` |
| `papertrader.market_data_source` | `[DA DEFINIRE]` |

Run the Hermes migration/configuration flow:

```bash
hermes config migrate
hermes config show
```

Keep mode set to `PAPER` during implementation and acceptance testing.

## 6. Configure Google Sheets access

Choose and document one authentication method:

- service account with least-privilege access;
- OAuth with a dedicated integration identity;
- an approved MCP/connector integration.

Required controls:

1. Grant access only to the target spreadsheet.
2. Keep credentials outside the repository.
3. Verify the spreadsheet time zone is `Europe/Rome`.
4. Protect formula and runtime-control columns from manual edits.
5. Ensure `Operazioni`, `Tesi`, `Storico Giornaliero`, and `Eventi_Errori` are treated as append-only logs.

Authentication implementation: `[DA DEFINIRE]`.

## 7. Configure market data and broker adapters

Before any order workflow is enabled, define:

```text
Broker/API                         [DA DEFINIRE]
Market-data/options-data source    [DA DEFINIRE]
Account/equity source of truth     [DA DEFINIRE]
Idempotency support                [DA DEFINIRE]
Order-status reconciliation        [DA DEFINIRE]
Margin preview                     [DA DEFINIRE]
Market calendar/session source     [DA DEFINIRE]
```

The adapter must verify option contract metadata and must return authoritative order and fill identifiers.

## 8. Verify Hermes discovery

Start a new session, or reset the current session so the skill index is refreshed. Then verify:

```bash
hermes skills list | grep -i papertrader
```

In chat:

```text
/papertrader review system readiness
```

A correct first response must identify unresolved placeholders, preserve `PAPER` mode, and leave the kill switch active.

## 9. Paper-trading acceptance gate

Do not enable live mode until all of the following are true:

- no duplicate orders or fills;
- no violation of the two-operations-per-day-per-instrument rule;
- all fill quantities and commissions reconcile;
- stock and option P&L independently verified;
- stale and missing data block new exposure;
- broker timeout produces `STATO_SCONOSCIUTO` and activates the kill switch;
- partial fills, cancellations, rejections, and reversals tested;
- option expiration, exercise, assignment, and pin-risk procedures tested;
- at least 30 paper-trading sessions completed;
- at least 100 order lifecycles completed;
- explicit human approval of every `[DA DEFINIRE]` risk parameter.

## 10. Uninstall the local skill

For a symlink installation:

```bash
rm ~/.hermes/skills/papertrader
```

Confirm it is a symlink before removal:

```bash
ls -ld ~/.hermes/skills/papertrader
```

For a copied installation, archive any local changes before deleting the directory.
