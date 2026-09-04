from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class BacktestPoint:
    timestamp: object
    zscore: float
    spread_price_a: float
    spread_price_b: float


@dataclass(frozen=True)
class BacktestTrade:
    entry_timestamp: object
    exit_timestamp: object
    direction: str
    entry_zscore: float
    exit_zscore: float
    pnl: float


def run_mean_reversion_backtest(
    points: Iterable[BacktestPoint],
    entry: float = 1.5,
    exit: float = 0.5,
    notional: float = 100.0,
) -> list[BacktestTrade]:
    """Simple research backtest; deliberately excludes fees/slippage until supplied."""
    if entry <= exit or notional <= 0:
        raise ValueError("entry must exceed exit and notional must be positive")
    open_trade = None
    trades: list[BacktestTrade] = []
    for point in points:
        z = point.zscore
        if open_trade is None and abs(z) >= entry:
            open_trade = point
            continue
        if open_trade is None or abs(z) > exit:
            continue
        direction = "SHORT_SPREAD" if open_trade.zscore > 0 else "LONG_SPREAD"
        pnl = notional * (abs(open_trade.zscore) - abs(z))
        trades.append(BacktestTrade(open_trade.timestamp, point.timestamp, direction, open_trade.zscore, z, pnl))
        open_trade = None
    return trades
