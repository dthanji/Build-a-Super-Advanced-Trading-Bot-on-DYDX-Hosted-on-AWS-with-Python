import asyncio

from src.execution.engine import ExecutionEngine
from src.execution.store import TradeStore
from src.risk.limits import RiskLimits, RiskSnapshot, approve_trade


def test_risk_limits_fail_closed():
    limits = RiskLimits(max_trade_usd=100)
    ok, _ = approve_trade(101, RiskSnapshot(0, 0, 0), limits)
    assert not ok


def test_paper_pair_reaches_hedged(tmp_path):
    store = TradeStore(str(tmp_path / "trades.sqlite3"))
    limits = RiskLimits(max_trade_usd=100, max_gross_usd=500, max_pairs=3, max_daily_loss_usd=25)
    snapshot = RiskSnapshot(0, 0, 0)
    risk = lambda notional: approve_trade(notional, snapshot, limits)
    engine = ExecutionEngine(risk, store, dry_run=True)

    trade = asyncio.run(
        engine.open_pair("BTC-USD", "SELL", "ETH-USD", "BUY", 0.001, 0.01, 50, 1.8, 1.2)
    )
    assert trade.state.value == "HEDGED"
    assert store.get(trade.trade_id)["state"] == "HEDGED"
