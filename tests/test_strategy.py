import numpy as np
import pandas as pd

from src.strategy.cointegration import half_life, zscore
from src.strategy.signals import generate_signal


def test_zscore_does_not_use_future_values():
    spread = pd.Series(np.arange(100, dtype=float))
    result = zscore(spread, window=20)
    assert result.iloc[:19].isna().all()
    assert np.isfinite(result.iloc[-1])


def test_signal_entry_and_exit_bands():
    assert generate_signal(2.0).action == "SHORT_SPREAD"
    assert generate_signal(-2.0).action == "LONG_SPREAD"
    assert generate_signal(0.1).action == "EXIT"
    assert generate_signal(1.0).action == "HOLD"


def test_half_life_rejects_non_mean_reverting_series():
    spread = pd.Series(np.arange(100, dtype=float))
    assert half_life(spread) == float("inf")
