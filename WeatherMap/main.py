from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from db import get_subscriptions, unsubscribe_user
from weather import get_weather
from config import TELEGRAM_BOT_TOKEN

# Инициализация FastAPI
app = FastAPI()

# Инициализация Telegram Bot API
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Инициализация планировщика задач
scheduler = AsyncIOScheduler()

# Функция для отправки уведомлений о погоде по подпискам пользователей
async def send_weather_notifications():
    subscriptions = get_subscriptions()  # Получаем все подписки из базы данных

    for user_id, city_name, interval in subscriptions:
        weather_info = get_weather(city_name)  # Получаем данные о погоде для подписанного города
        await bot.send_message(chat_id=user_id, text=weather_info)  # Отправляем сообщение пользователю

# Планировщик для отправки уведомлений о погоде раз в час (для теста)
def schedule_weather_notifications():
    scheduler.add_job(send_weather_notifications, 'interval', hours=1)  # Каждый час
    scheduler.start()

# Запуск планировщика при старте FastAPI
@app.on_event("startup")
async def on_startup():
    schedule_weather_notifications()

# Маршрут для проверки работы приложения
@app.get("/")
async def root():
    return {"message": "Weather notification bot is running!"}

# Маршрут для добавления подписки на уведомления о погоде
@app.post("/subscribe")
async def subscribe(user_id: int, city_name: str, interval: int):
    add_subscription(user_id, city_name, interval)
    return {"message": f"User {user_id} subscribed to weather updates for {city_name} every {interval} hours."}

# Маршрут для удаления подписки
@app.delete("/unsubscribe")
async def unsubscribe(user_id: int, city_name: str):
    remove_subscription(user_id, city_name)
    return {"message": f"User {user_id} unsubscribed from weather updates for {city_name}."}
