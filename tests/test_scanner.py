from datetime import datetime, timezone

from bet_scanner.models import EventOdds, OutcomeOdd
from bet_scanner.scanner import ArbitrageScanner


def test_arbitrage_found_for_three_way_market():
    now = datetime.now(timezone.utc)
    event = EventOdds(
        source_event_id="1",
        sport_key="soccer",
        sport_title="Soccer",
        commence_time=None,
        home_team="A",
        away_team="B",
        market="h2h",
        outcomes={
            "П1": [OutcomeOdd("a", "A", "h2h", "П1", 2.45, None, now)],
            "X": [OutcomeOdd("b", "B", "h2h", "X", 3.80, None, now)],
            "П2": [OutcomeOdd("c", "C", "h2h", "П2", 3.60, None, now)],
        },
    )

    scanner = ArbitrageScanner(min_profit_percent=1.0, bank=10_000, max_signal_age_seconds=180)
    signals = scanner.scan([event])

    assert len(signals) == 1
    assert signals[0].profit_percent > 1
    assert sum(signals[0].stakes.values()) == 10_000
