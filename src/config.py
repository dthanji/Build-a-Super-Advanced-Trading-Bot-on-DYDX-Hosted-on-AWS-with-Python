"""Environment-backed configuration for the trading bot.

Secrets are intentionally never stored in source control. Production deployments
should inject them from AWS Secrets Manager (or the runtime environment).
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _float(name: str, default: float) -> float:
    return float(os.getenv(name, default))


def _int(name: str, default: int) -> int:
    return int(os.getenv(name, default))


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Runtime configuration with safe defaults for dry-run operation."""

    environment: str = os.getenv("BOT_ENV", "paper")
    dry_run: bool = _bool("DRY_RUN", True)
    poll_seconds: int = _int("POLL_SECONDS", 15)
    candle_resolution: str = os.getenv("CANDLE_RESOLUTION", "1HOUR")
    lookback_candles: int = _int("LOOKBACK_CANDLES", 500)
    min_observations: int = _int("MIN_OBSERVATIONS", 200)
    coint_pvalue: float = _float("COINT_PVALUE", 0.05)
    zscore_entry: float = _float("ZSCORE_ENTRY", 1.5)
    zscore_exit: float = _float("ZSCORE_EXIT", 0.5)
    max_half_life: float = _float("MAX_HALF_LIFE", 24.0)
    max_trade_usd: float = _float("MAX_TRADE_USD", 100.0)
    max_gross_usd: float = _float("MAX_GROSS_USD", 500.0)
    max_pairs: int = _int("MAX_PAIRS", 3)
    max_daily_loss_usd: float = _float("MAX_DAILY_LOSS_USD", 25.0)
    max_holding_hours: float = _float("MAX_HOLDING_HOURS", 24.0)
    subaccount_number: int = _int("DYDX_SUBACCOUNT_NUMBER", 0)
    network: str = os.getenv("DYDX_NETWORK", "testnet")
    dydx_address: str | None = os.getenv("DYDX_ADDRESS")
    dydx_mnemonic: str | None = os.getenv("DYDX_MNEMONIC")
    dydx_private_key: str | None = os.getenv("DYDX_PRIVATE_KEY")
    telegram_token: str | None = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id: str | None = os.getenv("TELEGRAM_CHAT_ID")


settings = Settings()
