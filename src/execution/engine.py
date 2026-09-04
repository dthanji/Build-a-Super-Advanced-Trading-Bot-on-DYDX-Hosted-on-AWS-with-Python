"""Fail-closed two-leg execution orchestration."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from .models import Leg, Trade
from .state_machine import TradeState, transition


class ExecutionEngine:
    def __init__(self, risk, store, notifier=None, dry_run: bool = True):
        self.risk = risk
        self.store = store
        self.notifier = notifier
        self.dry_run = dry_run

    async def open_pair(self, market_a: str, side_a: str, market_b: str, side_b: str, size_a: float, size_b: float, zscore: float, hedge_ratio: float, submit):
        trade = Trade.create(
            str(uuid.uuid4()), market_a, market_b, zscore, hedge_ratio,
            Leg(market_a, side_a, size_a), Leg(market_b, side_b, size_b),
        )
        trade.state = transition(trade.state, TradeState.RISK_CHECK)
        self.store.save(trade.trade_id, trade.state.value, trade.to_dict(), datetime.now(timezone.utc).isoformat())

        if not self.risk.approve_trade(size_a, 0, 0, 0).approved:
            trade.state = TradeState.CLOSED
            trade.exit_reason = "risk_check_failed"
            self.store.save(trade.trade_id, trade.state.value, trade.to_dict(), datetime.now(timezone.utc).isoformat())
            return trade

        try:
            if self.dry_run:
                trade.leg_1.status = "PAPER_FILLED"
                trade.leg_1.filled_size = size_a
                trade.state = transition(trade.state, TradeState.LEG_1_SUBMITTED)
                trade.state = transition(trade.state, TradeState.LEG_1_FILLED)
                trade.leg_2.status = "PAPER_FILLED"
                trade.leg_2.filled_size = size_b
                trade.state = transition(trade.state, TradeState.LEG_2_SUBMITTED)
                trade.state = transition(trade.state, TradeState.HEDGED)
            else:
                first = await submit(trade.leg_1)
                trade.leg_1.order_id = str(first.get("order_id"))
                trade.state = transition(trade.state, TradeState.LEG_1_SUBMITTED)
                first_fill = await submit.wait_for_fill(trade.leg_1.order_id)
                if not first_fill.filled:
                    trade.state = transition(trade.state, TradeState.LEG_1_FAILED)
                    raise RuntimeError("first leg did not fill")
                trade.leg_1.filled_size = first_fill.filled_size
                trade.state = transition(trade.state, TradeState.LEG_1_FILLED)

                second = await submit(trade.leg_2)
                trade.leg_2.order_id = str(second.get("order_id"))
                trade.state = transition(trade.state, TradeState.LEG_2_SUBMITTED)
                second_fill = await submit.wait_for_fill(trade.leg_2.order_id)
                if not second_fill.filled:
                    trade.state = transition(trade.state, TradeState.LEG_2_FAILED)
                    raise RuntimeError("second leg did not fill")
                trade.leg_2.filled_size = second_fill.filled_size
                trade.state = transition(trade.state, TradeState.HEDGED)
        except Exception as exc:
            if trade.state not in {TradeState.LEG_1_FAILED, TradeState.LEG_2_FAILED, TradeState.EMERGENCY_CLOSE, TradeState.CLOSED}:
                try:
                    trade.state = transition(trade.state, TradeState.EMERGENCY_CLOSE)
                except ValueError:
                    trade.state = TradeState.UNKNOWN
            trade.exit_reason = str(exc)
            if self.notifier:
                await self.notifier(f"Trade {trade.trade_id} entered {trade.state.value}: {exc}")
        finally:
            self.store.save(trade.trade_id, trade.state.value, trade.to_dict(), datetime.now(timezone.utc).isoformat())
        return trade
