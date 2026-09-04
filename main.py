"""Safe runtime entry point for the research/paper-trading build.

The default process performs a deterministic paper smoke test and then stays
alive as a health/heartbeat process. It never places live orders.
"""
from __future__ import annotations

import argparse
import asyncio
import logging

from src.config import settings
from src.execution.engine import ExecutionEngine
from src.execution.store import TradeStore
from src.risk.limits import RiskLimits


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOGGER = logging.getLogger("dydx-bot")


def run_smoke_test() -> None:
    if not settings.dry_run or settings.environment.lower() not in {"paper", "test", "development"}:
        raise RuntimeError("The bundled smoke test requires paper/dry-run configuration")

    store = TradeStore("data/trades.sqlite3")
    limits = RiskLimits(
        max_trade_usd=settings.max_trade_usd,
        max_gross_usd=settings.max_gross_usd,
        max_pairs=settings.max_pairs,
        max_daily_loss_usd=settings.max_daily_loss_usd,
    )
    snapshot = {"gross_exposure_usd": 0.0, "open_pairs": 0, "daily_loss_usd": 0.0, "kill_switch": False}

    engine = ExecutionEngine(
        risk_check=lambda notional: limits.approve_trade(notional, snapshot),
        store=store,
        dry_run=True,
    )

    async def smoke() -> None:
        trade = await engine.open_pair(
            "BTC-USD", "SELL", "ETH-USD", "BUY", 0.01, 0.10,
            100.0, 1.75, 1.0,
        )
        if trade.state.value != "HEDGED":
            raise RuntimeError(f"paper smoke test ended in {trade.state.value}")
        LOGGER.info("paper smoke test passed: trade=%s state=%s", trade.trade_id, trade.state.value)

    asyncio.run(smoke())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="run the paper smoke test and exit")
    args = parser.parse_args()

    run_smoke_test()
    if args.once:
        return

    LOGGER.info(
        "safe runtime started: environment=%s dry_run=%s network=%s",
        settings.environment,
        settings.dry_run,
        settings.network,
    )
    try:
        while True:
            asyncio.run(asyncio.sleep(settings.poll_seconds))
            LOGGER.info("heartbeat: paper runtime healthy")
    except KeyboardInterrupt:
        LOGGER.info("shutdown requested")


if __name__ == "__main__":
    main()
