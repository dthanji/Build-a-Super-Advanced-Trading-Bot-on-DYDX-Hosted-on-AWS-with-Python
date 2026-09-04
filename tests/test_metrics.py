from src.paper.metrics import calculate_metrics


def test_metrics():
    metrics = calculate_metrics([10, -5, 15, -20])
    assert metrics.trades == 4
    assert metrics.wins == 2
    assert metrics.losses == 2
    assert metrics.total_pnl == 0
    assert metrics.max_drawdown == 20


def test_empty_metrics():
    assert calculate_metrics([]).trades == 0
