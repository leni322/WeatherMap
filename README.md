# 🌤️ WeatherMap Telegram Bot

**WeatherMap** — это Telegram-бот, который предоставляет актуальную информацию о погоде для различных городов. Пользователи могут запрашивать данные о текущей погоде или подписаться на ежедневные обновления. Бот написан на Python, интегрирован с API OpenWeatherMap, и использует **FastAPI** для создания RESTful API.

## 🚀 Возможности

- **Информация о погоде**: Получите текущую погоду для любого поддерживаемого города с помощью команды `/weather <город>`.
- **Выбор города**: Легко выберите город с помощью клавиатуры с популярными вариантами.
- **Ежедневные обновления погоды**: Автоматически получайте ежедневное обновление погоды для Санкт-Петербурга.
- **Обработка ошибок**: Дружелюбные сообщения об ошибках помогут пользователю, если что-то пошло не так.

## 🏙️ Поддерживаемые города

- **Москва**
- **Санкт-Петербург**
- **Новосибирск**
- **Екатеринбург**
- **Ростов-на-Дону**
- **Новочеркасск**

## 📦 Установка

### Требования

- Python 3.7+
- Токен Telegram-бота от [BotFather](https://core.telegram.org/bots#6-botfather)
- API-ключ погоды от [OpenWeatherMap](https://openweathermap.org/api)

### Настройка

1. **Склонируйте репозиторий**:

    ```bash
    git clone https://github.com/yourusername/weathermap-telegram-bot.git
    cd weathermap-telegram-bot/WeatherMap
    ```

2. **Установите необходимые пакеты**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Создайте файл `config.py`** в директории `WeatherMap` с вашим токеном бота и API-ключом:

    ```python
    TELEGRAM_BOT_TOKEN = 'ваш-токен-telegram-бота'
    API_KEY = 'ваш-api-ключ-openweathermap'
    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
    ```

4. **Инициализируйте базу данных SQLite**:

    ```bash
    python -c "from db import init_db; init_db()"
    ```

5. **Запустите бота**:

    ```bash
    python bot.py
    ```

6. **Запустите сервер FastAPI**:

    ```bash
    uvicorn main:app --reload
    ```

## 📝 Использование

### Команды

- **`/start`**: Запустить бота и увидеть доступные города.
- **`/weather <город>`**: Получить текущую погоду для указанного города.
- **Обработка ошибок**: Дружелюбные сообщения об ошибках помогут пользователю понять, что пошло не так.

### Пример

1. Запустите бота командой `/start`.
2. Выберите город из клавиатуры или используйте команду `/weather <город>`.
3. Получите информацию о текущей погоде прямо в чате.

## 📂 Структура проекта

```bash
WeatherMap/
├── bot.py              # Основная логика бота
├── db.py               # Настройка и управление базой данных
├── weather.py          # Получение и форматирование данных о погоде
├── config.py           # Конфигурационный файл для токенов и API-ключей
├── main.py             # Основной файл FastAPI для создания API
├── requirements.txt    # Зависимости Python
└── weather_history.db  # База данных SQLite (автогенерируемая)
```
## 🛠️ Зависимости
- **[python-telegram-bot](https://python-telegram-bot.readthedocs.io/)**: Полная библиотека для Python, которая упрощает разработку ботов Telegram и предоставляет удобные интерфейсы для взаимодействия с API бота.
- **[requests](https://docs.python-requests.org/)**: Мощная и удобная HTTP-библиотека для Python, которая упрощает отправку HTTP-запросов и интеграцию с веб-сервисами.
- **[APScheduler](https://apscheduler.readthedocs.io/)**: Гибкая библиотека планирования задач для Python, позволяющая планировать задачи, такие как отправка периодических сообщений или выполнение ежедневных заданий.
- **[FastAPI](https://fastapi.tiangolo.com/)**: Современный, высокопроизводительный веб-фреймворк для создания API на Python с автоматической документацией.
- **[SQLite](https://www.sqlite.org/index.html)**: Легкая в использовании система управления реляционными базами данных (СУБД), интегрированная в Python, используется для хранения истории погоды и подписок пользователей.


