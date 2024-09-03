 Weather
This project is a Telegram bot that provides weather information for various cities. Users can request current weather conditions or subscribe to daily weather updates for selected cities. The bot is built using Python, the Telegram Bot API, and integrates with a weather API to fetch real-time weather data.

 Features
• Weather Information: Users can get the current weather for cities by sending the /weather <city> command.
• City Selection: A keyboard with a list of available cities is provided for easy selection.
• Daily Weather Updates: Users can subscribe to daily weather updates for Saint Petersburg. The bot will automatically send the weather forecast each morning.
• Error Handling: The bot gracefully handles errors and informs users if something goes wrong.

 Available Cities
• Москва (Moscow)
• Санкт-Петербург (Saint Petersburg)
• Новосибирск (Novosibirsk)
• Екатеринбург (Yekaterinburg)
• Ростов-на-Дону (Rostov-on-Don)
• Новочеркасск (Novocherkassk)

 Installation
Prerequisites
• Python 3.7+
• A Telegram bot token (obtained from BotFather)
• A weather API key (from OpenWeatherMap)

 Setup
 1. Clone the repository:
git clone https://github.com/yourusername/weathermap-telegram-bot.git
cd weathermap-telegram-bot/WeatherMap

 2. Install required packages:
pip install -r requirements.txt

 3. Create a config.py file in the WeatherMap directory with your bot token and API key:
TELEGRAM_BOT_TOKEN = 'your-telegram-bot-token'
API_KEY = 'your-openweathermap-api-key'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

 4. Initialize the SQLite database:
python -c "from db import init_db; init_db()"

 5. Run the bot:
python bot.py

 Usage
Commands
• /start: Starts the bot and shows the available cities.
• /weather <city>: Provides the current weather for the specified city.

 Example
1. Start the bot with the /start command.
2. Choose a city from the keyboard or use the /weather <city> command.
3. eceive current weather information directly in the chat.

 Project Structure
WeatherMap/
├── bot.py            # The main bot logic
├── db.py             # Database setup and handling
├── weat ig.py         # Configuration file for tokens and API keys
├── requirements.txt  # Python dependencies
└── weather_history.db # SQLite database (auto-generated)

 Dependencies
• python-telegram-bot: Python library for the Telegram Bot API.
• requests: Library for making HTTP requests. 
• APScheduler: Library for scheduling tasks in Python.

 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for review.


