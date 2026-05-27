import asyncio

import httpx
import pytest

from bet_scanner.errors import (
    OddsApiAuthError,
    OddsApiNetworkError,
    OddsApiQuotaError,
    OddsApiRequestError,
    OddsApiSportUnavailableError,
)
from bet_scanner.providers import TheOddsApiProvider


class FakeClient:
    def __init__(self, response: httpx.Response | None = None, error: httpx.HTTPError | None = None):
        self.response = response
        self.error = error
        self.params = None

    async def get(self, url, params):
        self.params = params
        if self.error:
            raise self.error
        return self.response


def make_provider() -> TheOddsApiProvider:
    return TheOddsApiProvider(
        api_key="key",
        sports=["soccer_epl"],
        regions=["eu"],
        bookmakers=["pinnacle", "betfair_ex_uk"],
        markets=["h2h"],
    )


def test_provider_sends_bookmaker_filter_instead_of_regions():
    client = FakeClient(httpx.Response(200, json=[]))
    provider = make_provider()

    asyncio.run(provider._fetch_sport(client, "soccer_epl"))

    assert client.params["bookmakers"] == "pinnacle,betfair_ex_uk"
    assert "regions" not in client.params


@pytest.mark.parametrize(
    ("status_code", "error"),
    [
        (401, OddsApiAuthError),
        (403, OddsApiAuthError),
        (429, OddsApiQuotaError),
        (404, OddsApiSportUnavailableError),
        (422, OddsApiRequestError),
    ],
)
def test_provider_maps_odds_api_http_errors(status_code, error):
    client = FakeClient(httpx.Response(status_code, text="boom"))
    provider = make_provider()

    with pytest.raises(error):
        asyncio.run(provider._fetch_sport(client, "soccer_epl"))


def test_provider_maps_network_errors():
    request = httpx.Request("GET", "https://api.the-odds-api.com/v4/sports/soccer_epl/odds/")
    client = FakeClient(error=httpx.ConnectError("offline", request=request))
    provider = make_provider()

    with pytest.raises(OddsApiNetworkError):
        asyncio.run(provider._fetch_sport(client, "soccer_epl"))
