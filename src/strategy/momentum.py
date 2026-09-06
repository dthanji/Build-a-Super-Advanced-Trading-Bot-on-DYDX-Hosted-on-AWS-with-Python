"""Volatility-adjusted multi-timeframe momentum strategy."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class MomentumConfig:
    fast_ema: int = 20
    slow_ema: int = 50
    trend_fast_ema: int = 20
    trend_slow_ema: int = 50
    breakout_window: int = 20
    atr_window: int = 14
    volume_window: int = 20
    volume_multiplier: float = 1.10
    stop_atr: float = 2.0
    trail_atr: float = 2.5
    risk_fraction: float = 0.01

def _atr(frame: pd.DataFrame, window: int) -> pd.Series:
    previous_close = frame["close"].shift(1)
    true_range = pd.concat([
        frame["high"] - frame["low"],
        (frame["high"] - previous_close).abs(),
        (frame["low"] - previous_close).abs(),
    ], axis=1).max(axis=1)
    return true_range.rolling(window, min_periods=window).mean()

def add_indicators(frame: pd.DataFrame, config: MomentumConfig | None = None) -> pd.DataFrame:
    config = config or MomentumConfig()
    required = {"open", "high", "low", "close", "volume"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("At least one OHLCV row is required")
    data = frame.copy().sort_index()
    data["ema_fast"] = data["close"].ewm(span=config.fast_ema, adjust=False).mean()
    data["ema_slow"] = data["close"].ewm(span=config.slow_ema, adjust=False).mean()
    data["atr"] = _atr(data, config.atr_window)
    data["volume_avg"] = data["volume"].rolling(config.volume_window, min_periods=config.volume_window).mean()
    data["breakout_high"] = data["high"].rolling(config.breakout_window, min_periods=config.breakout_window).max().shift(1)
    data["breakout_low"] = data["low"].rolling(config.breakout_window, min_periods=config.breakout_window).min().shift(1)
    return data

def generate_signals(frame: pd.DataFrame, config: MomentumConfig | None = None) -> pd.DataFrame:
    """Generate LONG/SHORT/FLAT signals without look-ahead."""
    config = config or MomentumConfig()
    data = add_indicators(frame, config)
    four_hour = data[["close"]].resample("4h").last().dropna()
    four_hour["trend_fast"] = four_hour["close"].ewm(span=config.trend_fast_ema, adjust=False).mean().shift(1)
    four_hour["trend_slow"] = four_hour["close"].ewm(span=config.trend_slow_ema, adjust=False).mean().shift(1)
    data["trend_fast"] = four_hour["trend_fast"].reindex(data.index, method="ffill")
    data["trend_slow"] = four_hour["trend_slow"].reindex(data.index, method="ffill")
    volume_ok = data["volume"] >= data["volume_avg"] * config.volume_multiplier
    long = ((data["trend_fast"] > data["trend_slow"]) & (data["ema_fast"] > data["ema_slow"]) &
            (data["close"] > data["breakout_high"]) & volume_ok & data["atr"].notna())
    short = ((data["trend_fast"] < data["trend_slow"]) & (data["ema_fast"] < data["ema_slow"]) &
             (data["close"] < data["breakout_low"]) & volume_ok & data["atr"].notna())
    data["signal"] = np.select([long, short], ["LONG", "SHORT"], default="FLAT")
    return data
