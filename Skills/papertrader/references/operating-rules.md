# Operating and risk rules

## Core principle

The language model proposes and explains. Deterministic software measures, limits, authorizes, submits, and reconciles.

## Maximum two operations per instrument/day

Use the exact instrument key and the local date in `Europe/Rome`.

```text
lock(date, instrument_key)
reconcile broker orders
count distinct order_id where count_in_limit = true
if count >= 2: reject before broker call
reserve order intent and idempotency key
submit once
record outcome
unlock
```

A formula in Google Sheets may display the count, but it cannot prevent a race between simultaneous submissions.

## Position sizing

Risk parameters remain configurable and must be approved. Reasonable paper-test starting ranges are not guarantees or personal recommendations.

For a stock position, the deterministic engine should use the greater of stop distance and a configured gap buffer, then add expected entry/exit slippage and costs.

For a long option, assume the entire premium plus costs can be lost. Do not use a stop as a guaranteed maximum loss.

For a short option, require a deterministic bounded maximum-loss calculation, stress testing, and broker margin preview. Naked short options remain disabled by default.

## Daily loss

Use account equity, not only realized P&L:

```text
daily_pnl = current_equity - start_of_day_equity - deposits + withdrawals
```

When the configured maximum daily loss is reached:

- block new exposure and increases;
- activate `HALT_NEW` or the configured kill-switch policy;
- do not enlarge risk to recover losses;
- permit only a tested risk-reducing path.

Intraday profits must not automatically increase the maximum loss budget.

## Exposure

Check post-trade exposure at four levels:

1. exact instrument;
2. aggregate underlying across stock and options;
3. gross portfolio risk;
4. cash and broker margin.

For options, compare at least market-value exposure, delta-equivalent exposure, and deterministic stress loss; use the most conservative applicable measure.

## Costs and P&L

Unrealized net P&L:

```text
(current_price - average_price)
* signed_quantity
* multiplier
- residual_opening_costs
```

Realized net P&L is calculated sequentially for the closing portion of each fill and includes allocated opening costs, closing commission, and other fees.

Slippage is diagnostic when already embedded in the actual fill price; do not subtract it twice.

## Data quality

Block new exposure when:

- quote timestamp is missing or stale;
- bid/ask are missing or crossed;
- contract metadata is incomplete;
- duplicate market-data rows exist;
- spread or liquidity exceeds configured limits;
- model reference price deviates excessively from the verified quote;
- broker or market-data health is degraded beyond policy.

## Idempotency and unknown states

Every order intent has an idempotency key derived from stable normalized intent fields. A retry reuses the same key.

After a timeout:

1. do not create a new order ID;
2. query the broker;
3. mark `STATO_SCONOSCIUTO` if unresolved;
4. conservatively consume the operation slot;
5. activate the kill switch;
6. reconcile before any further exposure.

## Options-specific controls

Before opening an option position, verify:

- exact contract symbol and multiplier;
- underlying, call/put, strike, and expiration;
- DTE threshold;
- bid/ask spread and depth;
- volume and open interest;
- implied volatility and Greeks when available;
- exercise and assignment behavior;
- expiration and pin-risk procedures;
- corporate-action adjustments.

A short call can have theoretically unlimited loss. A short put can have a very large loss. Never describe these risks as controlled solely by a stop order.

## Kill switch

`HALT_NEW` blocks `OPEN_LONG`, `OPEN_SHORT`, and `INCREASE`. It may allow tested `CLOSE` and `REDUCE` paths.

`EMERGENCY_FLAT` must remain disabled until its liquidation sequence has dedicated tests for illiquidity, partial fills, option positions, order cancellation, and reconciliation.

Automatic kill-switch triggers include:

- daily loss breach;
- broker unavailable or heartbeat timeout;
- unknown order state;
- position/order mismatch;
- critical position-engine error;
- duplicate execution ID with different content;
- negative margin or margin call;
- repeated integration failures;
- unhandled option assignment/exercise event.

Reset requires full reconciliation, an operator identity, a reason, a timestamp, and an append-only audit event.

## Release gate

Live trading is blocked until the paper test plan passes, all `[DA DEFINIRE]` values are approved, and a separate live-release decision documents capital, limits, credentials, monitoring, rollback, and incident response.
