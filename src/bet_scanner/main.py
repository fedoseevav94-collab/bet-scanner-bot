from __future__ import annotations

import logging

from telegram import Update

from .bot import BetScannerBot
from .config import Settings


def main() -> None:
    settings = Settings.from_env()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = BetScannerBot(settings)
    app = bot.build_application()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
