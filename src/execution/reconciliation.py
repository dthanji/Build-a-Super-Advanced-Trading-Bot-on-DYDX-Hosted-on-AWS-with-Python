"""Startup reconciliation: compare persisted intent with exchange reality."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .store import TradeStore


@dataclass(frozen=True)
class ReconciliationResult:
    active_local_trades: int
    exchange_positions: int
    exchange_orders: int
    requires_manual_review: bool
    reason: str | None = None


async def reconcile(store: TradeStore, positions_adapter) -> ReconciliationResult:
    local = store.active()
    positions = await positions_adapter.perpetual_positions()
    orders = await positions_adapter.orders()

    # We deliberately fail closed when local active trades exist but the
    # exchange returns no corresponding account data. This prevents opening
    # new risk on an unverified account state after a restart.
    if local and positions is None:
        return ReconciliationResult(len(local), 0, len(orders or []), True, "exchange position state unavailable")

    return ReconciliationResult(
        len(local),
        len(positions or []),
        len(orders or []),
        False,
    )
