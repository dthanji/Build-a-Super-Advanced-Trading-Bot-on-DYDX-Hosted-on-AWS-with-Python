# dYdX Statistical Arbitrage Bot

Modernized from the original course implementation for the current dYdX Chain architecture.

## Status

**Build in progress — paper/dry-run only.** No live trading credentials belong in this repository.

### Architecture

- `src/strategy/` — cointegration, hedge ratio, half-life and z-score signals
- `src/dydx/` — current dYdX Chain adapter (being implemented)
- `src/execution/` — explicit two-leg execution state machine
- `src/risk/` — pre-trade limits and kill-switch controls
- `src/monitoring/` — Telegram notifications and operational logging
- `tests/` — strategy and execution safety tests

### Safety gates

1. Strategy/unit tests
2. Execution simulation, including partial fills and leg failures
3. dYdX integration tests without live orders
4. Testnet/paper validation where supported
5. Reconciliation and kill-switch validation
6. Only then consider controlled live deployment

The bot defaults to `DRY_RUN=true` and `BOT_ENV=paper`.
