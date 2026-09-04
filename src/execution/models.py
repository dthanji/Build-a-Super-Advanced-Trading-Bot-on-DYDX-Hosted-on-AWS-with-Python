"""Serializable trade records used by the execution engine."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from .state_machine import TradeState


@dataclass
class Leg:
    market: str
    side: str
    requested_size: float
    order_id: str | None = None
    filled_size: float = 0.0
    average_price: float | None = None
    status: str = "PENDING"


@dataclass
class Trade:
    trade_id: str
    pair_a: str
    pair_b: str
    signal_zscore: float
    hedge_ratio: float
    entry_timestamp: str
    leg_1: Leg
    leg_2: Leg
    state: TradeState = TradeState.SIGNAL
    exit_reason: str | None = None

    @classmethod
    def create(cls, trade_id: str, pair_a: str, pair_b: str, zscore: float, hedge_ratio: float, leg_1: Leg, leg_2: Leg) -> "Trade":
        return cls(trade_id, pair_a, pair_b, zscore, hedge_ratio, datetime.now(timezone.utc).isoformat(), leg_1, leg_2)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data
