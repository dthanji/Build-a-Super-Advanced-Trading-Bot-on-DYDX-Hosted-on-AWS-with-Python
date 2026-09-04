from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .portfolio import PaperPortfolio


@dataclass(frozen=True)
class PaperFill:
    order_id: str
    market: str
    side: str
    size: float
    price: float
    timestamp: datetime


class PaperExchange:
    """Deterministic, no-network execution venue for safe strategy testing."""

    def __init__(self, starting_cash: float = 1_000.0) -> None:
        if starting_cash <= 0:
            raise ValueError("starting_cash must be positive")
        self.portfolio = PaperPortfolio(starting_cash)

    def market_order(self, market: str, side: str, size: float, price: float) -> PaperFill:
        if size <= 0 or price <= 0:
            raise ValueError("size and price must be positive")
        side = side.upper()
        if side == "BUY":
            position_side = "LONG"
        elif side == "SELL":
            position_side = "SHORT"
        else:
            raise ValueError("side must be BUY or SELL")
        fill = PaperFill(str(uuid4()), market.upper(), side, size, price, datetime.now(timezone.utc))
        self.portfolio.open_position(fill.market, position_side, size, price)
        return fill

    def close(self, market: str, price: float) -> float:
        return self.portfolio.close_position(market, price)
