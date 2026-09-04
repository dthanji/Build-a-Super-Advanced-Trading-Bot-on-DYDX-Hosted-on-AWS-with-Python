"""Read-only account state used by reconciliation and risk checks."""
from __future__ import annotations

from typing import Any

from .client import DydxClient


class Positions:
    def __init__(self, client: DydxClient):
        self.client = client

    def _require_address(self) -> str:
        if not self.client.address:
            raise ValueError("DYDX_ADDRESS is required to read account state")
        return self.client.address

    async def perpetual_positions(self) -> list[dict[str, Any]]:
        response = await self.client.indexer.account.get_subaccount_perpetual_positions(
            self._require_address(), self.client.subaccount_number
        )
        return response.get("positions", [])

    async def orders(self) -> list[dict[str, Any]]:
        response = await self.client.indexer.account.get_subaccount_orders(
            self._require_address(), self.client.subaccount_number
        )
        return response if isinstance(response, list) else response.get("orders", [])

    async def fills(self, limit: int = 100) -> list[dict[str, Any]]:
        response = await self.client.indexer.account.get_subaccount_fills(
            self._require_address(), self.client.subaccount_number
        )
        fills = response.get("fills", []) if isinstance(response, dict) else response
        return list(fills or [])[:limit]
