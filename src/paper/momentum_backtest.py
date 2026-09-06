"""Realistic-ish paper backtest for the momentum strategy."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from src.strategy.momentum import MomentumConfig, generate_signals

@dataclass(frozen=True)
class MomentumTrade:
    entry_timestamp: object
    exit_timestamp: object
    direction: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    return_pct: float
    exit_reason: str

@dataclass(frozen=True)
class BacktestResult:
    trades: list[MomentumTrade]
    ending_equity: float
    total_return_pct: float
    max_drawdown_pct: float


def run_momentum_backtest(frame: pd.DataFrame, starting_equity: float = 1_000.0,
                          config: MomentumConfig | None = None,
                          fee_bps: float = 5.0, slippage_bps: float = 2.0) -> BacktestResult:
    """Backtest with next-bar entries, ATR stop/trailing exits and costs."""
    if starting_equity <= 0 or fee_bps < 0 or slippage_bps < 0:
        raise ValueError("starting_equity must be positive and costs cannot be negative")
    config = config or MomentumConfig()
    data = generate_signals(frame, config)
    equity = starting_equity
    peak = equity
    max_dd = 0.0
    position = None
    trades: list[MomentumTrade] = []

    for i in range(len(data) - 1):
        row = data.iloc[i]
        nxt = data.iloc[i + 1]
        if position is None:
            if row["signal"] not in {"LONG", "SHORT"} or pd.isna(row["atr"]):
                continue
            direction = row["signal"]
            entry = float(nxt["open"]) * (1 + (slippage_bps / 10000 if direction == "LONG" else -slippage_bps / 10000))
            stop_distance = float(row["atr"]) * config.stop_atr
            size = (equity * config.risk_fraction) / stop_distance
            if size <= 0:
                continue
            position = {"direction": direction, "entry": entry, "size": size,
                        "entry_time": nxt.name, "stop": entry - stop_distance if direction == "LONG" else entry + stop_distance,
                        "trail": entry - stop_distance if direction == "LONG" else entry + stop_distance,
                        "bars": 0}
            continue

        position["bars"] += 1
        direction = position["direction"]
        if direction == "LONG":
            position["trail"] = max(position["trail"], float(row["high"]) - float(row["atr"]) * config.trail_atr)
            stop = max(position["stop"], position["trail"])
            hit = float(row["low"]) <= stop
            exit_signal = row["signal"] == "SHORT"
            if hit or exit_signal:
                raw_exit = stop if hit else float(nxt["open"])
                exit_price = raw_exit * (1 - slippage_bps / 10000)
                reason = "TRAIL_STOP" if hit else "TREND_REVERSAL"
            else:
                continue
            pnl = (exit_price - position["entry"]) * position["size"]
        else:
            position["trail"] = min(position["trail"], float(row["low"]) + float(row["atr"]) * config.trail_atr)
            stop = min(position["stop"], position["trail"])
            hit = float(row["high"]) >= stop
            exit_signal = row["signal"] == "LONG"
            if hit or exit_signal:
                raw_exit = stop if hit else float(nxt["open"])
                exit_price = raw_exit * (1 + slippage_bps / 10000)
                reason = "TRAIL_STOP" if hit else "TREND_REVERSAL"
            else:
                continue
            pnl = (position["entry"] - exit_price) * position["size"]

        costs = (position["entry"] + exit_price) * position["size"] * fee_bps / 10000
        pnl -= costs
        equity += pnl
        peak = max(peak, equity)
        max_dd = max(max_dd, (peak - equity) / peak * 100)
        trades.append(MomentumTrade(position["entry_time"], row.name, direction,
                                     position["entry"], exit_price, position["size"], pnl,
                                     pnl / (position["entry"] * position["size"]) * 100, reason))
        position = None

    return BacktestResult(trades, equity, (equity / starting_equity - 1) * 100, max_dd)
