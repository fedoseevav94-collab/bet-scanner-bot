from __future__ import annotations

import asyncio
import logging

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

from .config import Settings
from .formatter import format_settings, format_signal
from .models import ArbitrageSignal
from .providers import MockOddsProvider, OddsProvider, TheOddsApiProvider
from .scanner import ArbitrageScanner
from .storage import SignalStorage

logger = logging.getLogger(__name__)


class BetScannerBot:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.provider: OddsProvider = self._build_provider()
        self.scanner = ArbitrageScanner(
            min_profit_percent=settings.min_profit_percent,
            bank=settings.bank,
            max_signal_age_seconds=settings.max_signal_age_seconds,
        )
        self.storage = SignalStorage(settings.database_path)
        self.active_chat_ids: set[int] = set()

    def _build_provider(self) -> OddsProvider:
        if self.settings.odds_api_key:
            return TheOddsApiProvider(
                api_key=self.settings.odds_api_key,
                sports=self.settings.odds_sports,
                regions=self.settings.odds_regions,
                markets=self.settings.odds_markets,
            )
        logger.warning("ODDS_API_KEY is missing. Using mock provider.")
        return MockOddsProvider()

    def build_application(self) -> Application:
        app = ApplicationBuilder().token(self.settings.telegram_bot_token).post_init(self._post_init).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help))
        app.add_handler(CommandHandler("scan", self.scan_once))
        app.add_handler(CommandHandler("settings", self.show_settings))

        return app

    async def _post_init(self, app: Application) -> None:
        app.create_task(self._periodic_scan(app))
        logger.info("Periodic scanner started")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat:
            self.active_chat_ids.add(update.effective_chat.id)

        if update.message:
            await update.message.reply_text(
                "Бот-сканер запущен.\n\n"
                "Команды:\n"
                "/scan — проверить вилки сейчас\n"
                "/settings — настройки\n"
                "/help — помощь\n\n"
                "Бот не делает ставки автоматически, только отправляет аналитические сигналы."
            )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return

        await update.message.reply_text(
            "Это бот для мониторинга коэффициентов и поиска потенциальных вилок.\n\n"
            "Сигнал считается по формуле: сумма 1/коэффициент по всем исходам < 1.\n"
            "Перед ставкой нужно вручную проверить коэффициенты, лимиты и правила рынка."
        )

    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return

        await update.message.reply_text(
            format_settings(
                min_profit_percent=self.settings.min_profit_percent,
                bank=self.settings.bank,
                scan_interval_seconds=self.settings.scan_interval_seconds,
                recheck_delay_seconds=self.settings.recheck_delay_seconds,
                sports=self.settings.odds_sports,
                regions=self.settings.odds_regions,
                markets=self.settings.odds_markets,
                provider_name=type(self.provider).__name__,
            )
        )

    async def scan_once(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat:
            self.active_chat_ids.add(update.effective_chat.id)

        if update.message:
            await update.message.reply_text("Сканирую коэффициенты...")

        signals = await self._find_confirmed_signals()

        if not signals:
            if update.message:
                await update.message.reply_text("Подходящих вилок сейчас не найдено.")
            return

        for signal in signals[:5]:
            if update.message:
                await update.message.reply_text(format_signal(signal), disable_web_page_preview=True)
            self.storage.mark_sent(signal.signal_id, signal.created_at.isoformat())

    async def _find_confirmed_signals(self) -> list[ArbitrageSignal]:
        first_events = await self.provider.fetch_events()
        first_signals = self.scanner.scan(first_events)
        if not first_signals:
            return []

        await asyncio.sleep(self.settings.recheck_delay_seconds)

        second_events = await self.provider.fetch_events()
        second_signals = self.scanner.scan(second_events)

        first_ids = {signal.signal_id for signal in first_signals}
        confirmed = [
            signal
            for signal in second_signals
            if signal.signal_id in first_ids and not self.storage.was_sent(signal.signal_id)
        ]

        return confirmed

    async def _periodic_scan(self, app: Application) -> None:
        while True:
            try:
                await asyncio.sleep(self.settings.scan_interval_seconds)

                if not self.active_chat_ids:
                    continue

                signals = await self._find_confirmed_signals()
                if not signals:
                    continue

                for chat_id in self.active_chat_ids:
                    for signal in signals[:3]:
                        await app.bot.send_message(
                            chat_id=chat_id,
                            text=format_signal(signal),
                            disable_web_page_preview=True,
                        )
                        self.storage.mark_sent(signal.signal_id, signal.created_at.isoformat())

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Periodic scan failed")
