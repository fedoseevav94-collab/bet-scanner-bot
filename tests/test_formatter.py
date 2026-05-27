from bet_scanner.formatter import format_sports, format_status


def test_format_status_contains_runtime_settings():
    text = format_status(
        provider_name="The Odds API",
        sports=["soccer_epl"],
        markets=["h2h"],
        regions=["eu", "uk"],
        bookmakers=["pinnacle"],
        min_profit_percent=1.5,
        scan_interval_seconds=120,
    )

    assert "The Odds API" in text
    assert "soccer_epl" in text
    assert "h2h" in text
    assert "eu, uk" in text
    assert "pinnacle" in text
    assert "1.50%" in text
    assert "120 сек" in text


def test_format_sports_lists_env_sports():
    text = format_sports(["soccer_epl", "basketball_nba"])

    assert "soccer_epl" in text
    assert "basketball_nba" in text
