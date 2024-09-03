# 🌤️ WeatherMap Telegram Bot

**WeatherMap** is a Telegram bot that provides real-time weather information for various cities. Users can request current weather data or subscribe to daily weather updates. The bot is built using Python and integrates with the OpenWeatherMap API.

## 🚀 Features

- **Weather Information**: Get the current weather for any supported city using the `/weather <city>` command.
- **City Selection**: Easily select a city from a provided keyboard with popular options.
- **Daily Weather Updates**: Automatically receive a daily weather update for Saint Petersburg.
- **Error Handling**: Friendly error messages ensure users know when something goes wrong.

## 🏙️ Supported Cities

- **Москва** (Moscow)
- **Санкт-Петербург** (Saint Petersburg)
- **Новосибирск** (Novosibirsk)
- **Екатеринбург** (Yekaterinburg)
- **Ростов-на-Дону** (Rostov-on-Don)
- **Новочеркасск** (Novocherkassk)

## 📦 Installation

### Prerequisites

- Python 3.7+
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#6-botfather)
- A weather API key from [OpenWeatherMap](https://openweathermap.org/api)

### Setup

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/weathermap-telegram-bot.git
    cd weathermap-telegram-bot/WeatherMap
    ```

2. **Install required packages**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Create a `config.py` file** in the `WeatherMap` directory with your bot token and API key:

    ```python
    TELEGRAM_BOT_TOKEN = 'your-telegram-bot-token'
    API_KEY = 'your-openweathermap-api-key'
    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
    ```

4. **Initialize the SQLite database**:

    ```bash
    python -c "from db import init_db; init_db()"
    ```

5. **Run the bot**:

    ```bash
    python bot.py
    ```

## 📝 Usage

### Commands

- **`/start`**: Start the bot and view available cities.
- **`/weather <city>`**: Get current weather for the specified city.
- **Error Handling**: Friendly error messages ensure users know when something goes wrong.

### Example

1. Start the bot with the `/start` command.
2. Choose a city from the keyboard or use the `/weather <city>` command.
3. Receive current weather information directly in the chat.

## 📂 Project Structure

```bash
WeatherMap/
├── bot.py              # The main bot logic
├── db.py               # Database setup and handling
├── weather.py          # Weather fetching and formatting
├── config.py           # Configuration file for tokens and API keys
├── requirements.txt    # Python dependencies
└── weather_history.db  # SQLite database (auto-generated)
```
## 🛠️ Dependencies

- **[python-telegram-bot](https://python-telegram-bot.readthedocs.io/)**: A comprehensive Python library that simplifies the development of Telegram bots by providing easy-to-use interfaces for interacting with the Telegram Bot API.
- **[requests](https://docs.python-requests.org/)**: A powerful and user-friendly HTTP library for Python, making it easy to send HTTP/1.1 requests and integrate with web services.
- **[APScheduler](https://apscheduler.readthedocs.io/)**: A flexible task scheduling library for Python, allowing you to schedule tasks such as sending periodic messages or running daily jobs.
- **[SQLite](https://www.sqlite.org/index.html)**: A lightweight and easy-to-use relational database management system (RDBMS) that is integrated into Python, used here for storing weather history and user subscriptions.
``

