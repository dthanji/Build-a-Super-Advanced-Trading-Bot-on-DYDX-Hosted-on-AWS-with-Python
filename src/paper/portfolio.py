from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Position:
    market: str
    side: str
    size: float
    entry_price: float
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def unrealized_pnl(self, mark_price: float) -> float:
        direction = 1.0 if self.side.upper() == "LONG" else -1.0
        return direction * (mark_price - self.entry_price) * self.size


@dataclass
class PaperPortfolio:
    cash: float
    positions: dict[str, Position] = field(default_factory=dict)
    realized_pnl: float = 0.0

    def gross_exposure(self, marks: dict[str, float] | None = None) -> float:
        marks = marks or {}
        total = 0.0
        for position in self.positions.values():
            price = marks.get(position.market, position.entry_price)
            total += abs(position.size * price)
        return total

    def unrealized_pnl(self, marks: dict[str, float]) -> float:
        return sum(
            position.unrealized_pnl(marks[position.market])
            for position in self.positions.values()
            if position.market in marks
        )

    def equity(self, marks: dict[str, float] | None = None) -> float:
        return self.cash + self.realized_pnl + self.unrealized_pnl(marks or {})

    def open_position(self, market: str, side: str, size: float, price: float) -> Position:
        if size <= 0 or price <= 0:
            raise ValueError("size and price must be positive")
        key = market.upper()
        if key in self.positions:
            raise ValueError(f"position already exists for {key}")
        position = Position(key, side.upper(), size, price)
        self.positions[key] = position
        return position

    def close_position(self, market: str, price: float) -> float:
        key = market.upper()
        position = self.positions.pop(key)
        pnl = position.unrealized_pnl(price)
        self.realized_pnl += pnl
        return pnl
