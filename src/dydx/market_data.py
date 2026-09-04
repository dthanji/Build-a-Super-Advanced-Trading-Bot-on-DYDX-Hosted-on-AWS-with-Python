"""Market-data access through the dYdX Chain Indexer."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from .client import DydxClient


class MarketData:
    def __init__(self, client: DydxClient):
        self.client = client

    async def markets(self, market: str | None = None) -> dict[str, Any]:
        response = await self.client.indexer.markets.get_perpetual_markets(market)
        return response.get("markets", response)

    async def candles(
        self,
        market: str,
        resolution: str = "1HOUR",
        limit: int = 500,
        from_iso: str | None = None,
        to_iso: str | None = None,
    ) -> pd.DataFrame:
        """Return normalized OHLCV candles, oldest first, with UTC timestamps."""
        response = await self.client.indexer.markets.get_candles(
            market,
            resolution,
            from_iso,
            to_iso,
            limit,
        )
        candles = response.get("candles", response) if isinstance(response, dict) else response
        rows: list[dict[str, Any]] = []
        for item in candles or []:
            timestamp = item.get("startedAt") or item.get("startedAtTime") or item.get("time")
            if timestamp is None:
                continue
            rows.append(
                {
                    "timestamp": pd.to_datetime(timestamp, utc=True),
                    "open": float(item["open"]),
                    "high": float(item["high"]),
                    "low": float(item["low"]),
                    "close": float(item["close"]),
                    "volume": float(item.get("usdVolume", item.get("volume", 0))),
                }
            )

        frame = pd.DataFrame(rows)
        if frame.empty:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
        frame = frame.drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
        now = datetime.now(timezone.utc)
        frame = frame[frame["timestamp"] <= now]
        return frame
