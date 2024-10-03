from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from db import get_subscriptions, unsubscribe_user, create_subscription
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

    for user_id, city_name, interval, is_active, notifications_sent in subscriptions:
        if is_active:
            weather_info = get_weather(city_name)
            await bot.send_message(chat_id=user_id, text=f"Погода в {city_name}:\n{weather_info}")
            increment_notification_count(user_id)  # Отправляем сообщение пользователю

# Планировщик для отправки уведомлений о погоде раз в час (для теста)
def schedule_weather_notifications():
    scheduler.add_job(send_weather_notifications, 'interval', hours=1)  # Для теста раз в час
    scheduler.start()

# Запуск планировщика при старте FastAPI
@app.on_event("startup")
async def on_startup():
    schedule_weather_notifications()

# Маршрут для проверки работы приложения
@app.get("/")
async def root():
    return {"message": "Weather notification bot is running!"}

@app.post("/subscribe")
async def subscribe(user_id: int, city_name: str, interval: int = 24):
    try:
        # Создание подписки в базе данных
        create_subscription(user_id, city_name, interval)
        return {"message": f"User {user_id} subscribed to weather updates for {city_name} every {interval} hours."}
    except Exception as e:
        return {"message": f"Failed to subscribe: {e}"}

# Маршрут для удаления подписки
@app.delete("/unsubscribe")
async def unsubscribe(user_id: int, city_name: str):
    remove_subscription(user_id, city_name)
    return {"message": f"User {user_id} unsubscribed from weather updates for {city_name}."}

@app.get("/weather/{city_name}")
async def get_weather_info(city_name: str):
    weather_info = get_weather(city_name)
    return {"weather": weather_info}
