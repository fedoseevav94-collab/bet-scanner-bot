from bet_scanner.config import Settings


def test_settings_reads_bookmaker_filter(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("ODDS_BOOKMAKERS", "pinnacle, betfair_ex_uk")
    monkeypatch.setenv("ODDS_SPORTS", "soccer_epl,basketball_nba")

    settings = Settings.from_env()

    assert settings.odds_bookmakers == ["pinnacle", "betfair_ex_uk"]
    assert settings.odds_sports == ["soccer_epl", "basketball_nba"]
