# PaperTrader

PaperTrader is a safety-first paper-trading workspace designed for **Hermes Agent**. Google Sheets remains the central operational registry for configuration, watchlists, theses, signals, positions, orders, executions, risk, errors, and daily snapshots.

> **Important:** this repository does not provide financial advice, does not guarantee profits, and must not be connected to live trading until backtests, integration tests, reconciliation tests, and an extended paper-trading period have passed.

## Status

This repository is an implementation scaffold. The following integrations are intentionally unresolved:

- Broker/API: `[DEFINE]`
- Market-data and options-data source: `[DEFINE]`
- Google Sheets authentication method: `[DEFINE]`
- Initial capital and risk limits: `[DEFINE]`

The default operating posture is:

- mode: `PAPER`
- global kill switch: `ON`
- human approval: required
- naked short options: disabled
- short equities: disabled unless explicitly enabled

## Architecture

```text
Market data source
        |
        v
Google Sheets market-data cache
        |
        v
Hermes qualitative analysis
        |
        v
JSON schema + deterministic validation
        |
        v
Deterministic risk gate
  - fresh data
  - complete instrument metadata
  - max 2 operations/day/instrument
  - position sizing
  - per-trade and daily-loss limits
  - instrument/underlying/global exposure
  - cash and margin preview
  - kill switch
        |
        v
Broker adapter [DEFINE]
        |
        v
Order/fill reconciliation
        |
        v
Google Sheets ledger and dashboard
```

Hermes may produce qualitative analysis, thesis updates, triggers, invalidations, and a structured trade proposal. It must **not** be the authority for quantity, risk limits, P&L, margin, the daily operation count, order state, or final order authorization.

## Repository layout

```text
PaperTrader/
├── Skills/
│   ├── README.md
│   └── papertrader/
│       ├── SKILL.md
│       ├── references/
│       │   ├── google-sheets-contract.md
│       │   └── operating-rules.md
│       ├── scripts/
│       │   └── validate_signal.py
│       └── templates/
│           ├── signal.example.json
│           └── signal.schema.json
├── scripts/
│   ├── check.sh
│   ├── install-local.sh
│   ├── validate_repo.py
│   └── validate_signal.py
├── AGENTS.md
├── INSTALL.md
└── README.md
```

`Skills` is intentionally capitalized to match this repository's requested layout. Configure Hermes with this exact path through `skills.external_dirs`, or install the individual skill directly from its GitHub path.

## Non-negotiable safety boundaries

1. **Fail closed.** Missing, stale, inconsistent, duplicated, or unverifiable data blocks new exposure.
2. **Two-operation limit.** A third broker-bound order for the same exact `InstrumentKey` on the same `Europe/Rome` trading date must be rejected before submission.
3. **Deterministic authorization.** Hermes never authorizes an order. A deterministic risk engine performs the final pre-submit check under a lock.
4. **Idempotency.** Every order intent and broker event has a stable unique identifier; retries reuse the same idempotency key.
5. **Append-only audit.** Order events, fills, thesis versions, errors, and daily snapshots are never silently overwritten.
6. **Costs are mandatory.** Commission, fees, slippage, option multiplier, and liquidity must be included.
7. **Options require contract verification.** Underlying, call/put, strike, expiration, multiplier, bid/ask, open interest, and assignment/exercise risk are verified outside the model.
8. **Kill switch first.** New exposure is blocked whenever the global kill switch is active. Reset requires reconciliation and an audited operator action.
9. **Paper before live.** Live mode is not a documentation change; it is a controlled release requiring explicit approval and passed acceptance criteria.

## Quick start

```bash
python3 scripts/validate_repo.py
./scripts/install-local.sh
```

Then start a new Hermes session and invoke:

```text
/papertrader review system readiness
```

See [INSTALL.md](INSTALL.md) for configuration and verification.

## Expected Google Sheet

The runtime expects these tabs:

- `Configurazione`
- `Dati_Mercato`
- `Watchlist`
- `Tesi`
- `Portafoglio`
- `Segnali`
- `Operazioni`
- `Storico Giornaliero`
- `Dashboard`
- `Eventi_Errori`

The detailed contract is in [`Skills/papertrader/references/google-sheets-contract.md`](Skills/papertrader/references/google-sheets-contract.md).

## Development workflow

1. Keep risk rules and broker-state transitions deterministic.
2. Add or update tests before changing an order or P&L rule.
3. Run `./scripts/check.sh`.
4. Test against fixtures and a paper account.
5. Reconcile positions, orders, cash, equity, commissions, and option contracts against the broker.
6. Review all changes to `AGENTS.md`, `SKILL.md`, validation scripts, and risk configuration as safety-critical.

## Disclaimer

Paper trading can differ materially from live execution. Stops may fill beyond their trigger, options can become illiquid, short options can create very large or unlimited losses, and technical controls can fail. No part of this repository is a promise of profitability or a substitute for professional financial, legal, tax, or compliance advice.
