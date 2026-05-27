from __future__ import annotations


class OddsProviderError(Exception):
    user_message = "Ошибка при получении коэффициентов."


class OddsApiAuthError(OddsProviderError):
    user_message = "The Odds API отклонил ключ. Проверьте ODDS_API_KEY."


class OddsApiQuotaError(OddsProviderError):
    user_message = "Квота The Odds API исчерпана. Проверьте тариф или дождитесь обновления лимита."


class OddsApiSportUnavailableError(OddsProviderError):
    user_message = "Один из выбранных спортов недоступен в The Odds API. Проверьте ODDS_SPORTS."


class OddsApiNetworkError(OddsProviderError):
    user_message = "Не удалось связаться с The Odds API. Проверьте сеть и повторите позже."


class OddsApiRequestError(OddsProviderError):
    user_message = "The Odds API вернул ошибку запроса. Проверьте рынки, регионы и букмекеров."
