"""Explicit state machine for two-leg pair execution."""
from __future__ import annotations

from enum import Enum


class TradeState(str, Enum):
    SIGNAL = "SIGNAL"
    RISK_CHECK = "RISK_CHECK"
    LEG_1_SUBMITTED = "LEG_1_SUBMITTED"
    LEG_1_FILLED = "LEG_1_FILLED"
    LEG_2_SUBMITTED = "LEG_2_SUBMITTED"
    HEDGED = "HEDGED"
    LEG_1_FAILED = "LEG_1_FAILED"
    LEG_1_PARTIAL = "LEG_1_PARTIAL"
    LEG_2_FAILED = "LEG_2_FAILED"
    LEG_2_PARTIAL = "LEG_2_PARTIAL"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"
    EMERGENCY_CLOSE = "EMERGENCY_CLOSE"
    CLOSED = "CLOSED"


_ALLOWED: dict[TradeState, set[TradeState]] = {
    TradeState.SIGNAL: {TradeState.RISK_CHECK},
    TradeState.RISK_CHECK: {TradeState.LEG_1_SUBMITTED, TradeState.CLOSED},
    TradeState.LEG_1_SUBMITTED: {TradeState.LEG_1_FILLED, TradeState.LEG_1_PARTIAL, TradeState.LEG_1_FAILED, TradeState.TIMEOUT, TradeState.UNKNOWN},
    TradeState.LEG_1_PARTIAL: {TradeState.LEG_2_SUBMITTED, TradeState.EMERGENCY_CLOSE, TradeState.TIMEOUT},
    TradeState.LEG_1_FILLED: {TradeState.LEG_2_SUBMITTED, TradeState.EMERGENCY_CLOSE},
    TradeState.LEG_2_SUBMITTED: {TradeState.HEDGED, TradeState.LEG_2_PARTIAL, TradeState.LEG_2_FAILED, TradeState.TIMEOUT, TradeState.UNKNOWN},
    TradeState.LEG_2_PARTIAL: {TradeState.EMERGENCY_CLOSE, TradeState.TIMEOUT},
    TradeState.LEG_2_FAILED: {TradeState.EMERGENCY_CLOSE},
    TradeState.LEG_1_FAILED: {TradeState.CLOSED},
    TradeState.TIMEOUT: {TradeState.EMERGENCY_CLOSE, TradeState.UNKNOWN, TradeState.CLOSED},
    TradeState.UNKNOWN: {TradeState.EMERGENCY_CLOSE, TradeState.CLOSED},
    TradeState.HEDGED: {TradeState.CLOSED, TradeState.EMERGENCY_CLOSE},
    TradeState.EMERGENCY_CLOSE: {TradeState.CLOSED, TradeState.UNKNOWN},
    TradeState.CLOSED: set(),
}


class InvalidTransition(ValueError):
    """Raised when execution attempts an unsafe state transition."""


def transition(current: TradeState, target: TradeState) -> TradeState:
    """Validate and return a new trade state."""
    if target not in _ALLOWED.get(current, set()):
        raise InvalidTransition(f"Invalid trade transition: {current.value} -> {target.value}")
    return target
