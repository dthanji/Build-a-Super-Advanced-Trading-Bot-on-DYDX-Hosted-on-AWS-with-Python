from src.execution.reconciliation import reconcile
from src.execution.store import TradeStore
import asyncio


class FakePositions:
    async def perpetual_positions(self):
        return [{"market": "BTC-USD", "size": "1"}]

    async def orders(self):
        return []


def test_reconciliation_reads_local_and_exchange(tmp_path):
    store = TradeStore(str(tmp_path / "trades.sqlite3"))
    store.save("t1", "HEDGED", {"market": "BTC-USD"}, "now")
    result = asyncio.run(reconcile(store, FakePositions()))
    assert result.active_local_trades == 1
    assert result.exchange_positions == 1
    assert not result.requires_manual_review
