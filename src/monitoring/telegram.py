"""Minimal Telegram notifier with safe HTTP handling."""
from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


def send_message(token: str | None, chat_id: str | None, message: str) -> bool:
    """Send a Telegram message; return False rather than crashing the bot."""
    if not token or not chat_id:
        logger.info("Telegram is not configured")
        return False
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        logger.exception("Telegram notification failed")
        return False
