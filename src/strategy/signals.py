"""Signal generation for mean-reverting pairs."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PairSignal:
    action: str
    zscore: float
    reason: str


def generate_signal(z: float, entry_threshold: float = 1.5, exit_threshold: float = 0.5) -> PairSignal:
    """Generate an entry/exit/hold decision from the latest spread z-score."""
    if z != z:  # NaN
        return PairSignal("HOLD", z, "z-score unavailable")
    if z >= entry_threshold:
        return PairSignal("SHORT_SPREAD", z, "positive deviation")
    if z <= -entry_threshold:
        return PairSignal("LONG_SPREAD", z, "negative deviation")
    if abs(z) <= exit_threshold:
        return PairSignal("EXIT", z, "spread reverted toward mean")
    return PairSignal("HOLD", z, "inside entry band")
