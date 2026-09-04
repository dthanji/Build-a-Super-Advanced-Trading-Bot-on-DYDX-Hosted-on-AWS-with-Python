"""Thin, testable wrapper around the official dYdX Chain Python client."""
from __future__ import annotations

from dataclasses import dataclass

from dydx_v4_client.indexer.rest.indexer_client import IndexerClient
from dydx_v4_client.network import MAINNET, TESTNET
from dydx_v4_client.node.client import NodeClient
from dydx_v4_client.wallet import Wallet


@dataclass
class DydxClient:
    """Holds Indexer, node and optional signing wallet clients."""

    indexer: IndexerClient
    node: NodeClient
    wallet: Wallet | None = None
    address: str | None = None
    subaccount_number: int = 0

    @classmethod
    async def connect(
        cls,
        network: str = "testnet",
        mnemonic: str | None = None,
        address: str | None = None,
        subaccount_number: int = 0,
    ) -> "DydxClient":
        selected = TESTNET if network.lower() == "testnet" else MAINNET
        node = await NodeClient.connect(selected.node)
        indexer = IndexerClient(selected.rest_indexer)

        wallet = None
        if mnemonic:
            if not address:
                raise ValueError("DYDX_ADDRESS is required when using DYDX_MNEMONIC")
            wallet = await Wallet.from_mnemonic(node, mnemonic=mnemonic, address=address)

        return cls(indexer, node, wallet, address, subaccount_number)

    async def close(self) -> None:
        """Close network clients when their implementation exposes close()."""
        for client in (self.indexer, self.node):
            close = getattr(client, "close", None)
            if close is not None:
                result = close()
                if hasattr(result, "__await__"):
                    await result
