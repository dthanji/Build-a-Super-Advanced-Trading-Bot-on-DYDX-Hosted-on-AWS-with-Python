# dYdX Statistical Arbitrage Bot

A modernized research and paper-trading implementation of the statistical-arbitrage approach taught in the original course.

## Current status

**Paper/dry-run only.** This repository is not a promise of profitability and is not configured for unattended live financial trading.

The original course used the legacy dYdX v3 stack. This implementation separates the strategy from exchange infrastructure so the quantitative logic can be tested independently.

## Architecture

- `src/strategy/` — cointegration, OLS hedge ratio, half-life, rolling z-score and signals
- `src/dydx/` — current dYdX Chain Indexer/node adapter
- `src/execution/` — trade state machine, persistence and startup reconciliation
- `src/risk/` — exposure, pair-count, daily-loss and kill-switch limits
- `src/paper/` — deterministic paper exchange, portfolio accounting and research backtests
- `src/monitoring/` — Telegram notification and health state
- `tests/` — quantitative, paper execution, metrics, health and reconciliation tests

## Safety gates

1. Unit-test quantitative calculations.
2. Run deterministic paper simulations.
3. Test execution failure and restart scenarios.
4. Validate market-data freshness and reconciliation.
5. Run dYdX connectivity checks without placing orders.
6. Review performance including costs, slippage and drawdown before drawing conclusions.

The default configuration is `DRY_RUN=true`, `BOT_ENV=paper`, and `DYDX_NETWORK=testnet`.

## Configuration

Copy `.env.example` to `.env` for local development. Never commit `.env`, seed phrases, private keys, API keys or Telegram credentials. Production secrets should be injected by the deployment environment or a secrets manager.

## Paper research

The paper exchange is deliberately deterministic and makes no network requests. The backtest engine is a research aid, not a production performance guarantee. Results should be extended with realistic fees, funding, slippage, latency and execution assumptions before being used for evaluation.

## Deployment

The repository includes a Dockerfile and can be run on a Linux host such as AWS EC2. Continuous operation should use a process supervisor such as systemd, with logs forwarded to an operational monitoring system.

## Disclaimer

This software is for education and research. Trading digital assets involves substantial risk, including loss of capital. Historical or simulated performance does not predict future results.
