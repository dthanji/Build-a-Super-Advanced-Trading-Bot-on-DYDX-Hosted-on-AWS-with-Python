from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class HealthState:
    last_market_data_at: datetime | None = None
    last_loop_at: datetime | None = None
    consecutive_errors: int = 0
    kill_switch: bool = False

    def mark_market_data(self) -> None:
        self.last_market_data_at = datetime.now(timezone.utc)
        self.consecutive_errors = 0

    def mark_loop(self) -> None:
        self.last_loop_at = datetime.now(timezone.utc)

    def mark_error(self) -> None:
        self.consecutive_errors += 1

    def healthy(self, max_staleness_seconds: int = 120, max_errors: int = 3) -> bool:
        if self.kill_switch or self.consecutive_errors >= max_errors:
            return False
        if self.last_loop_at is None or self.last_market_data_at is None:
            return False
        now = datetime.now(timezone.utc)
        return (
            (now - self.last_loop_at).total_seconds() <= max_staleness_seconds
            and (now - self.last_market_data_at).total_seconds() <= max_staleness_seconds
        )
