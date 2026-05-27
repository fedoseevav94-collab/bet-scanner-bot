from __future__ import annotations

import sqlite3
from pathlib import Path


class SignalStorage:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        Path(database_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sent_signals (
                    signal_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def was_sent(self, signal_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM sent_signals WHERE signal_id = ?",
                (signal_id,),
            ).fetchone()
        return row is not None

    def mark_sent(self, signal_id: str, created_at: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO sent_signals(signal_id, created_at) VALUES (?, ?)",
                (signal_id, created_at),
            )
            connection.commit()
