from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal


MarketKey = Literal["h2h", "spreads", "totals"]


@dataclass(frozen=True)
class OutcomeOdd:
    bookmaker_key: str
    bookmaker_title: str
    market: str
    outcome: str
    price: float
    point: float | None
    last_update: datetime | None
    source_event_id: str | None = None
    link: str | None = None


@dataclass(frozen=True)
class EventOdds:
    source_event_id: str
    sport_key: str
    sport_title: str
    commence_time: datetime | None
    home_team: str
    away_team: str
    market: str
    outcomes: dict[str, list[OutcomeOdd]]

    @property
    def event_title(self) -> str:
        return f"{self.home_team} — {self.away_team}"


@dataclass(frozen=True)
class ArbitrageSignal:
    signal_id: str
    sport_key: str
    sport_title: str
    event_title: str
    commence_time: datetime | None
    market: str
    best_odds: dict[str, OutcomeOdd]
    probability_sum: float
    profit_percent: float
    stakes: dict[str, float]
    expected_profit: float
    bank: float
    created_at: datetime
    quality: str

    @property
    def is_fresh(self) -> bool:
        now = datetime.now(timezone.utc)
        updates = [odd.last_update for odd in self.best_odds.values() if odd.last_update is not None]
        if not updates:
            return True
        return all((now - update).total_seconds() <= 180 for update in updates)
