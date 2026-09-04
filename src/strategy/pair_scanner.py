"""Build a tradable universe and rank statistically related pairs."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import pandas as pd

from .cointegration import calculate_cointegration


@dataclass(frozen=True)
class PairCandidate:
    market_a: str
    market_b: str
    p_value: float
    hedge_ratio: float
    half_life: float
    score: float


async def scan_pairs(market_data, tickers: list[str], resolution: str, limit: int, min_observations: int, pvalue: float, max_half_life: float, max_pairs: int) -> list[PairCandidate]:
    prices: dict[str, pd.Series] = {}
    for ticker in tickers:
        frame = await market_data.candles(ticker, resolution=resolution, limit=limit)
        if len(frame) >= min_observations:
            prices[ticker] = frame.set_index("timestamp")["close"]

    candidates: list[PairCandidate] = []
    for left, right in combinations(sorted(prices), 2):
        result = calculate_cointegration(prices[left], prices[right], pvalue_threshold=pvalue, max_half_life=max_half_life)
        if not result.is_cointegrated:
            continue
        # Lower p-value and shorter half-life rank higher. The small floor
        # prevents division by zero for extremely fast mean reversion.
        score = (-result.p_value) + 1.0 / max(result.half_life, 0.1)
        candidates.append(PairCandidate(left, right, result.p_value, result.hedge_ratio, result.half_life, score))

    return sorted(candidates, key=lambda item: item.score, reverse=True)[:max_pairs]
