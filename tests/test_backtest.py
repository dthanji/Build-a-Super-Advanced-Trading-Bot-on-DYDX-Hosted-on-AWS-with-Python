from src.paper.backtest import BacktestPoint, run_mean_reversion_backtest


def test_backtest_closes_when_zscore_reverts():
    points = [
        BacktestPoint(1, 0.0, 100, 100),
        BacktestPoint(2, 1.8, 100, 100),
        BacktestPoint(3, 0.9, 100, 100),
        BacktestPoint(4, 0.4, 100, 100),
    ]
    trades = run_mean_reversion_backtest(points)
    assert len(trades) == 1
    assert trades[0].direction == "SHORT_SPREAD"
    assert trades[0].pnl > 0
