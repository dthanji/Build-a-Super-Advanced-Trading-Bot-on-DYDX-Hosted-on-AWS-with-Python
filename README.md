# dYdX Volatility-Adjusted Momentum Bot

A modernized research and paper-trading implementation of a volatility-adjusted, multi-timeframe crypto momentum strategy for dYdX.

## Current status

**Paper/dry-run only.** This repository is not a promise of profitability and is not configured for unattended live financial trading.

The original course used legacy dYdX v3 statistical arbitrage. The current primary research strategy is momentum/trend following, while the original cointegration implementation remains available as a research baseline.

## Strategy

The primary strategy combines:

- 4-hour EMA trend filter
- 1-hour EMA confirmation
- 20-bar breakout confirmation
- ATR volatility measurement
- volume confirmation
- ATR-based initial stop and trailing stop
- risk-based position sizing
- next-bar execution in the research backtester to avoid same-candle look-ahead
- configurable fees and slippage

The strategy is deliberately conservative about claims: historical or simulated profitability is not assumed to persist out of sample. Recent academic work reports evidence of momentum/trend-following effects in cryptocurrency markets, but that does not guarantee profitability for this implementation. See the research references in the project documentation.

## Architecture

- `src/strategy/momentum.py` — primary momentum/trend strategy and indicators
- `src/strategy/cointegration.py` — original statistical-arbitrage baseline
- `src/dydx/` — current dYdX Chain Indexer/node adapter
- `src/execution/` — trade state machine, persistence and startup reconciliation
- `src/risk/` — exposure, pair-count, daily-loss and kill-switch limits
- `src/paper/` — deterministic paper exchange, portfolio accounting and backtests
- `src/paper/momentum_backtest.py` — momentum-specific trade ledger and cost-aware P&L
- `src/monitoring/` — Telegram notification and health state
- `tests/` — quantitative, paper execution and strategy tests

## Research gates

1. Validate indicators and signal timing with unit tests.
2. Run the same backtest across multiple markets and regimes.
3. Include fees, slippage and realistic execution timing.
4. Inspect every trade and its signal reason, not only aggregate P&L.
5. Use walk-forward/out-of-sample testing before considering deployment.
6. Run dYdX connectivity checks without placing orders.
7. Keep live trading disabled until the strategy survives independent validation.

The default configuration remains `DRY_RUN=true`, `BOT_ENV=paper`, and `DYDX_NETWORK=testnet`.

## Paper research

The paper exchange makes no network requests. The momentum backtester records entry/exit prices, direction, size, P&L and exit reason, and models configurable fee/slippage assumptions. Results remain research estimates, not a performance guarantee.

## Deployment

The repository includes a Dockerfile and can be run on a Linux host such as AWS EC2. Continuous operation should use a process supervisor such as systemd, with logs forwarded to an operational monitoring system.

## Disclaimer

This software is for education and research. Trading digital assets involves substantial risk, including loss of capital. Historical or simulated performance does not predict future results.
