"""Position sizing constrained by configured USD risk."""
from __future__ import annotations


def pair_sizes(price_a: float, price_b: float, hedge_ratio: float, max_notional_usd: float) -> tuple[float, float]:
    if min(price_a, price_b, max_notional_usd) <= 0:
        raise ValueError("prices and max_notional_usd must be positive")
    if hedge_ratio <= 0:
        raise ValueError("hedge_ratio must be positive")
    # Allocate the pair notional across both legs while preserving the hedge
    # ratio in dollar exposure: notional_b = hedge_ratio * notional_a.
    notional_a = max_notional_usd / (1.0 + hedge_ratio)
    notional_b = max_notional_usd - notional_a
    return notional_a / price_a, notional_b / price_b
