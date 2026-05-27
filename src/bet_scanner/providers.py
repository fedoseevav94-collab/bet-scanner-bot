from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Protocol

import httpx

from .models import EventOdds, OutcomeOdd

logger = logging.getLogger(__name__)


class OddsProvider(Protocol):
    async def fetch_events(self) -> list[EventOdds]:
        ...


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class TheOddsApiProvider:
    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(
        self,
        api_key: str,
        sports: list[str],
        regions: list[str],
        markets: list[str],
        timeout_seconds: float = 20,
    ) -> None:
        self.api_key = api_key
        self.sports = sports
        self.regions = regions
        self.markets = markets
        self.timeout_seconds = timeout_seconds

    async def fetch_events(self) -> list[EventOdds]:
        events: list[EventOdds] = []

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            for sport in self.sports:
                events.extend(await self._fetch_sport(client, sport))

        return events

    async def _fetch_sport(self, client: httpx.AsyncClient, sport: str) -> list[EventOdds]:
        params = {
            "apiKey": self.api_key,
            "regions": ",".join(self.regions),
            "markets": ",".join(self.markets),
            "oddsFormat": "decimal",
            "dateFormat": "iso",
        }

        url = f"{self.BASE_URL}/sports/{sport}/odds/"
        response = await client.get(url, params=params)

        remaining = response.headers.get("x-requests-remaining")
        used = response.headers.get("x-requests-used")
        last = response.headers.get("x-requests-last")
        logger.info(
            "Odds API sport=%s status=%s quota_remaining=%s quota_used=%s quota_last=%s",
            sport,
            response.status_code,
            remaining,
            used,
            last,
        )

        response.raise_for_status()
        payload = response.json()
        return self._parse_payload(payload)

    def _parse_payload(self, payload: list[dict[str, Any]]) -> list[EventOdds]:
        parsed: list[EventOdds] = []

        for event in payload:
            by_market: dict[str, dict[str, list[OutcomeOdd]]] = {}

            bookmakers = event.get("bookmakers", [])
            for bookmaker in bookmakers:
                bookmaker_key = bookmaker.get("key", "")
                bookmaker_title = bookmaker.get("title", bookmaker_key)
                last_update = parse_datetime(bookmaker.get("last_update"))

                for market in bookmaker.get("markets", []):
                    market_key = market.get("key")
                    if market_key not in self.markets:
                        continue

                    market_outcomes = by_market.setdefault(market_key, {})

                    for outcome in market.get("outcomes", []):
                        name = str(outcome.get("name", "")).strip()
                        price = outcome.get("price")
                        if not name or price is None:
                            continue

                        try:
                            decimal_price = float(price)
                        except (TypeError, ValueError):
                            continue

                        point = outcome.get("point")
                        point_float = float(point) if point is not None else None
                        outcome_key = name if point_float is None else f"{name} {point_float:+g}"

                        market_outcomes.setdefault(outcome_key, []).append(
                            OutcomeOdd(
                                bookmaker_key=bookmaker_key,
                                bookmaker_title=bookmaker_title,
                                market=market_key,
                                outcome=outcome_key,
                                price=decimal_price,
                                point=point_float,
                                last_update=last_update,
                                source_event_id=event.get("id"),
                            )
                        )

            for market_key, outcomes in by_market.items():
                if len(outcomes) < 2:
                    continue

                parsed.append(
                    EventOdds(
                        source_event_id=str(event.get("id", "")),
                        sport_key=str(event.get("sport_key", "")),
                        sport_title=str(event.get("sport_title", event.get("sport_key", ""))),
                        commence_time=parse_datetime(event.get("commence_time")),
                        home_team=str(event.get("home_team", "")),
                        away_team=str(event.get("away_team", "")),
                        market=market_key,
                        outcomes=outcomes,
                    )
                )

        return parsed


class MockOddsProvider:
    async def fetch_events(self) -> list[EventOdds]:
        now = datetime.now(timezone.utc)
        outcomes = {
            "П1": [
                OutcomeOdd("book_a", "Book A", "h2h", "П1", 2.45, None, now),
                OutcomeOdd("book_b", "Book B", "h2h", "П1", 2.31, None, now),
            ],
            "X": [
                OutcomeOdd("book_a", "Book A", "h2h", "X", 3.30, None, now),
                OutcomeOdd("book_b", "Book B", "h2h", "X", 3.80, None, now),
            ],
            "П2": [
                OutcomeOdd("book_a", "Book A", "h2h", "П2", 3.60, None, now),
                OutcomeOdd("book_b", "Book B", "h2h", "П2", 3.25, None, now),
            ],
        }

        return [
            EventOdds(
                source_event_id="mock-1",
                sport_key="soccer_mock",
                sport_title="Football Mock",
                commence_time=None,
                home_team="Arsenal",
                away_team="Chelsea",
                market="h2h",
                outcomes=outcomes,
            )
        ]
