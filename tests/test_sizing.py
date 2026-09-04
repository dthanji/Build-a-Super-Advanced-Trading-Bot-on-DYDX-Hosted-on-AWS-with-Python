from src.risk.sizing import pair_sizes


def test_pair_sizes_respect_total_notional():
    a, b = pair_sizes(100, 50, 2, 300)
    assert a * 100 + b * 50 == 300
    assert b * 50 == 2 * (a * 100)
