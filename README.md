# WeatherMap

`WeatherMap` это Python-проект с двумя интерфейсами:
- Telegram-бот для получения погоды и оформления подписки.
- FastAPI API для подписок, просмотра текущей погоды и фоновой рассылки уведомлений.

Проект использует Open-Meteo для погодных данных и SQLite для хранения истории и подписок.

## Возможности

- Получение текущей погоды по выбранному городу.
- Подписка пользователя на регулярные уведомления.
- Просмотр текущей подписки и быстрая отписка прямо из Telegram.
- REST API для подписки, отписки и просмотра состояния подписки.
- Сохранение истории погодных запросов в SQLite.
- Планировщик уведомлений на базе APScheduler.

## Стек

- Python 3.12
- FastAPI
- python-telegram-bot
- APScheduler
- SQLite
- Open-Meteo
- requests-cache

## Структура

```text
.
├── .env.example
├── config.py
├── requirements.txt
└── WeatherMap
    ├── bot.py
    ├── db.py
    ├── main.py
    └── weather.py
```

## Подготовка

1. Установите зависимости:

```powershell
pip install -r requirements.txt
```

2. Создайте `.env` на основе `.env.example`.

Пример:

```env
TELEGRAM_BOT_TOKEN=replace-with-your-telegram-bot-token
FASTAPI_URL=http://localhost:8000
WEATHER_TIMEZONE=Europe/Moscow
WEATHER_CACHE_SECONDS=3600
DATABASE_PATH=C:\Python\InfoWeather\WeatherMap\weather.db
```

3. Инициализируйте базу данных:

```powershell
python -c "from WeatherMap.db import init_db; init_db()"
```

## Запуск

Запуск FastAPI:

```powershell
uvicorn WeatherMap.main:app --reload
```

Запуск Telegram-бота:

```powershell
python WeatherMap\bot.py
```

Команды в Telegram:

- `/start` открыть главное меню.
- `/subscriptions` показать текущую подписку.
- `/unsubscribe` удалить текущую подписку.

## API

`GET /`
- Проверка, что API запущен.

`POST /subscribe?user_id=123&city_name=Москва&interval=24`
- Создать или обновить подписку пользователя.

`DELETE /unsubscribe?user_id=123`
- Удалить подписку пользователя.

`GET /subscriptions/123`
- Получить текущую подписку пользователя.

`GET /weather/Москва`
- Получить текущую погодную сводку по городу.

## Ближайшие улучшения

- Добавить несколько подписок на одного пользователя.
- Выбор времени уведомлений, а не только интервала.
- Команды `/unsubscribe` и `/subscriptions` прямо в Telegram.
- Тесты и контейнеризация.
- Веб-панель для просмотра подписок и истории.
