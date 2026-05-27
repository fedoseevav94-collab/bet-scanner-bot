# Bet Scanner Bot

Telegram-бот для мониторинга букмекерских коэффициентов и поиска потенциальных вилок. Бот только анализирует линии и отправляет сигналы. Автопроставления ставок нет.

## Что умеет

- Запускается командой `python run.py`.
- Работает с The Odds API или с mock provider, если `ODDS_API_KEY` не задан.
- Фильтрует The Odds API по спортам, рынкам, регионам и конкретным букмекерам.
- Поддерживает команды `/scan`, `/status`, `/sports`, `/settings`, `/help`.
- Повторно проверяет сигнал перед отправкой.
- Сохраняет отправленные сигналы в SQLite, чтобы не спамить одинаковыми уведомлениями.
- Подходит для локального запуска, BotHost, VPS и Docker.

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `TELEGRAM_BOT_TOKEN` в `.env`. Для локальной проверки без The Odds API оставьте `ODDS_API_KEY` пустым, тогда бот использует mock provider.

```bash
python run.py
```

`run.py` добавляет `src` в `sys.path`, поэтому локально отдельный `PYTHONPATH` не нужен.

## BotHost

1. Загрузите репозиторий на BotHost.
2. Укажите команду запуска:

```bash
python run.py
```

3. Добавьте переменные окружения из `.env.example`.
4. Для реальных коэффициентов задайте `ODDS_API_KEY`. Без ключа бот запустится на mock provider.

## VPS

```bash
git clone https://github.com/fedoseevav94-collab/bet-scanner-bot.git
cd bet-scanner-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Для systemd или process manager используйте рабочую директорию репозитория и команду `python run.py`.

## Docker

```bash
docker build -t bet-scanner-bot .
docker run --env-file .env bet-scanner-bot
```

В Docker задан `PYTHONPATH=/app/src`, а основной запуск всё равно идёт через `python run.py`.

## Команды бота

- `/scan` — проверить вилки сейчас.
- `/status` — показать провайдер, спорты, рынки, регионы, букмекеров, минимальную доходность и интервал сканирования.
- `/sports` — показать текущие виды спорта из `ODDS_SPORTS`.
- `/settings` — показать расширенные настройки расчёта.
- `/help` — краткая справка.

## Переменные окружения

| Переменная | Обязательна | Значение по умолчанию | Описание |
| --- | --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | да | - | Токен Telegram-бота от BotFather. |
| `ODDS_API_KEY` | нет | - | Ключ The Odds API. Если пусто, используется mock provider. |
| `ODDS_REGIONS` | нет | `eu,uk` | Регионы The Odds API. Используются, когда `ODDS_BOOKMAKERS` пустой. |
| `ODDS_BOOKMAKERS` | нет | пусто | Конкретные букмекеры The Odds API через запятую, например `pinnacle,betfair_ex_uk`. Если задано, параметр `regions` не отправляется. |
| `ODDS_SPORTS` | нет | `soccer_epl,soccer_spain_la_liga` | Виды спорта The Odds API через запятую. |
| `ODDS_MARKETS` | нет | `h2h` | Рынки The Odds API через запятую. |
| `MIN_PROFIT_PERCENT` | нет | `1.5` | Минимальная доходность сигнала в процентах. |
| `BANK` | нет | `10000` | Банк для расчёта распределения ставок в сигнале. Это расчёт, бот ставки не делает. |
| `SCAN_INTERVAL_SECONDS` | нет | `120` | Интервал фонового сканирования. |
| `RECHECK_DELAY_SECONDS` | нет | `5` | Пауза перед повторной проверкой найденного сигнала. |
| `MAX_SIGNAL_AGE_SECONDS` | нет | `180` | Максимальный возраст данных букмекера. |
| `DATABASE_PATH` | нет | `bet_scanner.sqlite3` | Путь к SQLite-базе для дедупликации сигналов. |
| `LOG_LEVEL` | нет | `INFO` | Уровень логирования. |

## Ошибки The Odds API

Бот показывает понятные сообщения для типовых проблем:

- неправильный или заблокированный API-ключ;
- превышение квоты;
- недоступный спорт из `ODDS_SPORTS`;
- сетевые ошибки;
- некорректные рынки, регионы или букмекеры.

## Проверка

```bash
pip install -r requirements.txt -r requirements-dev.txt
PYTHONPATH=src ruff check src tests run.py
PYTHONPATH=src pytest -q
```

CI выполняет те же проверки: ruff и pytest.
