from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceMetrics:
    trades: int
    wins: int
    losses: int
    total_pnl: float
    win_rate: float
    average_pnl: float
    max_drawdown: float


def calculate_metrics(pnls: list[float]) -> PerformanceMetrics:
    if not pnls:
        return PerformanceMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0)
    equity = peak = 0.0
    max_drawdown = 0.0
    for pnl in pnls:
        equity += pnl
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    wins = sum(p > 0 for p in pnls)
    losses = sum(p < 0 for p in pnls)
    total = sum(pnls)
    return PerformanceMetrics(len(pnls), wins, losses, total, wins / len(pnls), total / len(pnls), max_drawdown)
