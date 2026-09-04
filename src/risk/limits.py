"""Pre-trade risk checks."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskLimits:
    max_trade_usd: float = 100.0
    max_gross_usd: float = 500.0
    max_pairs: int = 3
    max_daily_loss_usd: float = 25.0


@dataclass(frozen=True)
class RiskSnapshot:
    gross_exposure_usd: float
    open_pairs: int
    daily_pnl_usd: float
    kill_switch: bool = False


def approve_trade(notional_usd: float, snapshot: RiskSnapshot, limits: RiskLimits) -> tuple[bool, str]:
    """Return whether a proposed pair trade passes all configured limits."""
    if snapshot.kill_switch:
        return False, "kill switch is active"
    if notional_usd <= 0:
        return False, "trade notional must be positive"
    if notional_usd > limits.max_trade_usd:
        return False, "trade exceeds per-trade limit"
    if snapshot.gross_exposure_usd + notional_usd > limits.max_gross_usd:
        return False, "trade exceeds gross exposure limit"
    if snapshot.open_pairs >= limits.max_pairs:
        return False, "maximum simultaneous pairs reached"
    if snapshot.daily_pnl_usd <= -limits.max_daily_loss_usd:
        return False, "daily loss limit reached"
    return True, "approved"
