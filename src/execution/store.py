"""Small SQLite persistence layer; exchange state remains authoritative."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class TradeStore:
    def __init__(self, path: str = "data/trades.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init(self) -> None:
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS trades (trade_id TEXT PRIMARY KEY, state TEXT NOT NULL, payload TEXT NOT NULL, updated_at TEXT NOT NULL)")
            db.commit()

    def save(self, trade_id: str, state: str, payload: dict[str, Any], updated_at: str) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO trades(trade_id,state,payload,updated_at) VALUES(?,?,?,?) "
                "ON CONFLICT(trade_id) DO UPDATE SET state=excluded.state,payload=excluded.payload,updated_at=excluded.updated_at",
                (trade_id, state, json.dumps(payload, default=str), updated_at),
            )
            db.commit()

    def get(self, trade_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT trade_id,state,payload,updated_at FROM trades WHERE trade_id=?", (trade_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["payload"] = json.loads(result["payload"])
        return result

    def active(self) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT trade_id,state,payload,updated_at FROM trades WHERE state != 'CLOSED'").fetchall()
        return [{**dict(row), "payload": json.loads(row["payload"])} for row in rows]
