import numpy as np
import pandas as pd

from src.paper.momentum_backtest import run_momentum_backtest
from src.strategy.momentum import MomentumConfig, generate_signals


def _frame(n=300):
    idx = pd.date_range("2026-01-01", periods=n, freq="h")
    close = 100 + np.linspace(0, 30, n) + np.sin(np.arange(n) / 8)
    return pd.DataFrame({
        "open": close,
        "high": close + 1,
        "low": close - 1,
        "close": close,
        "volume": np.full(n, 1000.0),
    }, index=idx)


def test_signals_have_no_future_breakout_values():
    frame = _frame()
    result = generate_signals(frame, MomentumConfig())
    assert result["breakout_high"].iloc[20] == frame["high"].iloc[:20].max()
    assert result["breakout_high"].iloc[19] != result["breakout_high"].iloc[19]


def test_backtest_returns_valid_metrics():
    result = run_momentum_backtest(_frame())
    assert result.ending_equity > 0
    assert result.max_drawdown_pct >= 0
    assert isinstance(result.trades, list)
