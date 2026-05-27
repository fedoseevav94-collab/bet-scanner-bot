from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    odds_api_key: str | None
    odds_regions: list[str]
    odds_bookmakers: list[str]
    odds_sports: list[str]
    odds_markets: list[str]
    min_profit_percent: float
    bank: float
    scan_interval_seconds: int
    recheck_delay_seconds: int
    max_signal_age_seconds: int
    database_path: str
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

        return cls(
            telegram_bot_token=token,
            odds_api_key=os.getenv("ODDS_API_KEY", "").strip() or None,
            odds_regions=_split_csv(os.getenv("ODDS_REGIONS", "eu,uk")),
            odds_bookmakers=_split_csv(os.getenv("ODDS_BOOKMAKERS", "")),
            odds_sports=_split_csv(os.getenv("ODDS_SPORTS", "soccer_epl,soccer_spain_la_liga")),
            odds_markets=_split_csv(os.getenv("ODDS_MARKETS", "h2h")),
            min_profit_percent=float(os.getenv("MIN_PROFIT_PERCENT", "1.5")),
            bank=float(os.getenv("BANK", "10000")),
            scan_interval_seconds=int(os.getenv("SCAN_INTERVAL_SECONDS", "120")),
            recheck_delay_seconds=int(os.getenv("RECHECK_DELAY_SECONDS", "5")),
            max_signal_age_seconds=int(os.getenv("MAX_SIGNAL_AGE_SECONDS", "180")),
            database_path=os.getenv("DATABASE_PATH", "bet_scanner.sqlite3"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    @property
    def database_dir(self) -> Path:
        return Path(self.database_path).expanduser().resolve().parent
