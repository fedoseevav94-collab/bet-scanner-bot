# Bet Scanner Bot

Telegram-бот для мониторинга букмекерских коэффициентов и поиска потенциальных арбитражных ситуаций.

## Что делает

- Получает коэффициенты через The Odds API.
- Сканирует рынки `h2h`, `spreads`, `totals`.
- Ищет потенциальные вилки.
- Делает повторную проверку сигнала перед отправкой.
- Отправляет уведомления в Telegram.
- Сохраняет сигналы в SQLite, чтобы не спамить одинаковыми уведомлениями.
- Работает локально, на VPS, BotHost или Docker-хостинге.

## Важно

Бот не делает ставки автоматически. Он только показывает аналитические сигналы. Перед любой реальной ставкой нужно вручную проверить коэффициенты, лимиты, правила рынка и законность использования сервиса в вашей юрисдикции.

## Быстрый старт

### 1. Установить зависимости

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Создать `.env`

Скопируйте пример:

```bash
cp .env.example .env
```

Заполните:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ODDS_API_KEY=your_the_odds_api_key
```

### 3. Запустить

```bash
python -m bet_scanner.main
```

В Telegram:

```text
/start
/scan
/settings
```

## Настройки

Основные переменные окружения:

```env
TELEGRAM_BOT_TOKEN=
ODDS_API_KEY=
ODDS_REGIONS=eu,uk
ODDS_SPORTS=soccer_epl,soccer_spain_la_liga,tennis_atp_french_open,tennis_wta_french_open
ODDS_MARKETS=h2h
MIN_PROFIT_PERCENT=1.5
BANK=10000
SCAN_INTERVAL_SECONDS=120
RECHECK_DELAY_SECONDS=5
MAX_SIGNAL_AGE_SECONDS=180
DATABASE_PATH=bet_scanner.sqlite3
```

## Деплой на GitHub

```bash
git init
git add .
git commit -m "Initial bet scanner bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bet-scanner-bot.git
git push -u origin main
```

## Деплой на BotHost / VPS

Нужно указать команду запуска:

```bash
python -m bet_scanner.main
```

И добавить переменные окружения из `.env.example`.

## Docker

```bash
docker build -t bet-scanner-bot .
docker run --env-file .env bet-scanner-bot
```

## Структура

```text
src/bet_scanner/
  main.py              # запуск приложения
  bot.py               # Telegram-команды и периодический сканер
  config.py            # настройки из env
  models.py            # модели данных
  providers.py         # The Odds API и mock provider
  scanner.py           # поиск вилок
  formatter.py         # текст уведомлений
  storage.py           # SQLite-дедупликация сигналов
```
