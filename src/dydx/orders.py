"""Order construction and submission for dYdX Chain.

The adapter refuses live submission unless a signing wallet is explicitly
configured. The application itself remains dry-run by default.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from v4_proto.dydxprotocol.clob.order_pb2 import Order

from dydx_v4_client import MAX_CLIENT_ID, OrderFlags
from dydx_v4_client.indexer.rest.constants import OrderType
from dydx_v4_client.node.market import Market

from .client import DydxClient


@dataclass(frozen=True)
class OrderRequest:
    market: str
    side: str
    size: float
    reduce_only: bool = False
    slippage: float = 0.05


class Orders:
    def __init__(self, client: DydxClient):
        self.client = client

    async def _market(self, ticker: str) -> tuple[Market, dict[str, Any]]:
        response = await self.client.indexer.markets.get_perpetual_markets(ticker)
        data = response.get("markets", response)
        if ticker not in data:
            raise ValueError(f"Unknown perpetual market: {ticker}")
        market_data = data[ticker]
        return Market(market_data), market_data

    async def build_market_order(self, request: OrderRequest):
        if request.size <= 0:
            raise ValueError("Order size must be positive")
        if not 0 <= request.slippage <= 0.25:
            raise ValueError("Slippage must be between 0 and 25%")
        side = request.side.upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError("Order side must be BUY or SELL")

        market, data = await self._market(request.market)
        oracle = float(data["oraclePrice"])
        # Market orders require a protective price in the current client.
        price = oracle * (1 + request.slippage if side == "BUY" else 1 - request.slippage)
        order_side = Order.Side.SIDE_BUY if side == "BUY" else Order.Side.SIDE_SELL
        client_id = random.randint(0, MAX_CLIENT_ID)
        order_id = market.order_id(
            self.client.address or "",
            self.client.subaccount_number,
            client_id,
            OrderFlags.SHORT_TERM,
        )
        current_block = await self.client.node.latest_block_height()
        order = market.order(
            order_id=order_id,
            order_type=OrderType.MARKET,
            side=order_side,
            size=request.size,
            price=price,
            time_in_force=Order.TimeInForce.TIME_IN_FORCE_UNSPECIFIED,
            reduce_only=request.reduce_only,
            good_til_block=current_block + 20,
        )
        return order, {"client_id": client_id, "oracle_price": oracle, "protective_price": price}

    async def submit(self, request: OrderRequest) -> dict[str, Any]:
        if self.client.wallet is None:
            raise RuntimeError("Signing wallet is not configured; live order submission is disabled")
        order, metadata = await self.build_market_order(request)
        tx = await self.client.node.place_order(wallet=self.client.wallet, order=order)
        self.client.wallet.sequence += 1
        return {"transaction": tx, **metadata}
