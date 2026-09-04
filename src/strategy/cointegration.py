"""Cointegration and spread statistics used by the stat-arb engine."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
from statsmodels.tsa.stattools import coint


@dataclass(frozen=True)
class CointegrationResult:
    """Diagnostics for one candidate pair."""

    p_value: float
    t_stat: float
    critical_5pct: float
    hedge_ratio: float
    intercept: float
    half_life: float
    is_cointegrated: bool


def _aligned(a: pd.Series, b: pd.Series) -> tuple[pd.Series, pd.Series]:
    frame = pd.concat([a, b], axis=1).dropna()
    if frame.empty:
        raise ValueError("No overlapping observations after removing missing data")
    return frame.iloc[:, 0].astype(float), frame.iloc[:, 1].astype(float)


def hedge_ratio_and_spread(a: pd.Series, b: pd.Series) -> tuple[float, float, pd.Series]:
    """Fit a regression with an intercept and return hedge ratio and spread."""
    a, b = _aligned(a, b)
    model = OLS(a.to_numpy(), add_constant(b.to_numpy())).fit()
    intercept = float(model.params[0])
    hedge_ratio = float(model.params[1])
    spread = a - (intercept + hedge_ratio * b)
    return hedge_ratio, intercept, spread


def half_life(spread: pd.Series) -> float:
    """Estimate mean-reversion half-life from an AR(1)-style regression."""
    values = pd.Series(spread, dtype=float).dropna()
    lagged = values.shift(1).dropna()
    delta = values.diff().dropna()
    lagged, delta = lagged.align(delta, join="inner")
    if len(delta) < 3:
        return float("inf")
    model = OLS(delta.to_numpy(), add_constant(lagged.to_numpy())).fit()
    coef = float(model.params[1])
    if coef >= 0:
        return float("inf")
    return float(-np.log(2.0) / coef)


def zscore(spread: pd.Series, window: int = 48) -> pd.Series:
    """Return a rolling z-score without using future observations."""
    mean = spread.rolling(window=window, min_periods=window).mean()
    std = spread.rolling(window=window, min_periods=window).std(ddof=0)
    return (spread - mean) / std.replace(0, np.nan)


def calculate_cointegration(
    a: pd.Series,
    b: pd.Series,
    pvalue_threshold: float = 0.05,
    max_half_life: float = 24.0,
) -> CointegrationResult:
    """Run Engle-Granger testing and apply explicit strategy filters."""
    a, b = _aligned(a, b)
    if len(a) < 30:
        raise ValueError("At least 30 overlapping observations are required")

    t_stat, p_value, critical_values = coint(a.to_numpy(), b.to_numpy())
    hedge_ratio, intercept, spread = hedge_ratio_and_spread(a, b)
    hl = half_life(spread)
    critical_5 = float(critical_values[1])

    return CointegrationResult(
        p_value=float(p_value),
        t_stat=float(t_stat),
        critical_5pct=critical_5,
        hedge_ratio=hedge_ratio,
        intercept=intercept,
        half_life=hl,
        is_cointegrated=(float(p_value) < pvalue_threshold and hl <= max_half_life),
    )
