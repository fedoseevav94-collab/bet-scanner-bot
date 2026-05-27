from __future__ import annotations

from .models import ArbitrageSignal


def format_signal(signal: ArbitrageSignal) -> str:
    lines = [
        "⚡ Найдена потенциальная вилка",
        "",
        f"Спорт: {signal.sport_title}",
        f"Событие: {signal.event_title}",
        f"Рынок: {signal.market}",
        f"Качество: {signal.quality}",
    ]

    if signal.commence_time:
        lines.append(f"Начало: {signal.commence_time:%Y-%m-%d %H:%M UTC}")

    lines.extend(["", "Лучшие коэффициенты:"])

    for outcome, odd in signal.best_odds.items():
        lines.append(f"• {outcome}: {odd.price:.3g} — {odd.bookmaker_title}")

    lines.extend(
        [
            "",
            f"Сумма вероятностей: {signal.probability_sum:.4f}",
            f"Доходность: {signal.profit_percent:.2f}%",
            f"Банк для расчёта: {signal.bank:.2f} ₽",
            "",
            "Распределение ставок:",
        ]
    )

    for outcome, stake in signal.stakes.items():
        lines.append(f"• {outcome}: {stake:.2f} ₽")

    lines.extend(
        [
            "",
            f"Ожидаемая прибыль: {signal.expected_profit:.2f} ₽",
            "",
            "Проверить вручную: коэффициенты, лимиты, правила рынка и доступность ставки.",
        ]
    )

    return "\n".join(lines)


def format_settings(
    min_profit_percent: float,
    bank: float,
    scan_interval_seconds: int,
    recheck_delay_seconds: int,
    sports: list[str],
    regions: list[str],
    markets: list[str],
    provider_name: str,
) -> str:
    return "\n".join(
        [
            "⚙️ Текущие настройки",
            "",
            f"Источник: {provider_name}",
            f"Спорт: {', '.join(sports)}",
            f"Регионы БК: {', '.join(regions)}",
            f"Рынки: {', '.join(markets)}",
            f"Мин. доходность: {min_profit_percent:.2f}%",
            f"Банк: {bank:.2f} ₽",
            f"Интервал сканирования: {scan_interval_seconds} сек.",
            f"Повторная проверка: через {recheck_delay_seconds} сек.",
        ]
    )
