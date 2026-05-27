from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from .models import ArbitrageSignal, EventOdds, OutcomeOdd


class ArbitrageScanner:
    def __init__(
        self,
        min_profit_percent: float,
        bank: float,
        max_signal_age_seconds: int,
    ) -> None:
        self.min_profit_percent = min_profit_percent
        self.bank = bank
        self.max_signal_age_seconds = max_signal_age_seconds

    def scan(self, events: list[EventOdds]) -> list[ArbitrageSignal]:
        signals: list[ArbitrageSignal] = []

        for event in events:
            best_odds = self._best_odds(event)
            if len(best_odds) != len(event.outcomes):
                continue

            probability_sum = sum(1 / item.price for item in best_odds.values())
            if probability_sum >= 1:
                continue

            profit_percent = (1 / probability_sum - 1) * 100
            if profit_percent < self.min_profit_percent:
                continue

            stakes = self._calculate_stakes(best_odds)
            guaranteed_payout = min(stakes[outcome] * odd.price for outcome, odd in best_odds.items())
            expected_profit = guaranteed_payout - self.bank

            if not self._is_data_fresh(best_odds):
                continue

            signals.append(
                ArbitrageSignal(
                    signal_id=self._signal_id(event, best_odds),
                    sport_key=event.sport_key,
                    sport_title=event.sport_title,
                    event_title=event.event_title,
                    commence_time=event.commence_time,
                    market=event.market,
                    best_odds=best_odds,
                    probability_sum=probability_sum,
                    profit_percent=profit_percent,
                    stakes=stakes,
                    expected_profit=expected_profit,
                    bank=self.bank,
                    created_at=datetime.now(timezone.utc),
                    quality=self._quality_label(profit_percent),
                )
            )

        return sorted(signals, key=lambda item: item.profit_percent, reverse=True)

    @staticmethod
    def _best_odds(event: EventOdds) -> dict[str, OutcomeOdd]:
        best: dict[str, OutcomeOdd] = {}
        for outcome, odds in event.outcomes.items():
            valid = [item for item in odds if item.price > 1.0]
            if valid:
                best[outcome] = max(valid, key=lambda item: item.price)
        return best

    def _calculate_stakes(self, best_odds: dict[str, OutcomeOdd]) -> dict[str, float]:
        inverse_sum = sum(1 / item.price for item in best_odds.values())
        raw = {
            outcome: self.bank * (1 / item.price) / inverse_sum
            for outcome, item in best_odds.items()
        }
        rounded = {outcome: round(stake, 2) for outcome, stake in raw.items()}
        difference = round(self.bank - sum(rounded.values()), 2)
        if rounded and difference != 0:
            first_key = next(iter(rounded))
            rounded[first_key] = round(rounded[first_key] + difference, 2)
        return rounded

    def _is_data_fresh(self, best_odds: dict[str, OutcomeOdd]) -> bool:
        now = datetime.now(timezone.utc)
        updates = [odd.last_update for odd in best_odds.values() if odd.last_update is not None]
        if not updates:
            return True

        return all((now - update).total_seconds() <= self.max_signal_age_seconds for update in updates)

    @staticmethod
    def _quality_label(profit_percent: float) -> str:
        if profit_percent >= 3:
            return "🟢 сильный сигнал"
        if profit_percent >= 1.5:
            return "🟡 средний сигнал"
        return "🔴 слабый сигнал"

    @staticmethod
    def _signal_id(event: EventOdds, best_odds: dict[str, OutcomeOdd]) -> str:
        raw = "|".join(
            [
                event.source_event_id,
                event.sport_key,
                event.market,
                *[
                    f"{outcome}:{odd.bookmaker_key}:{odd.price}"
                    for outcome, odd in sorted(best_odds.items())
                ],
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
