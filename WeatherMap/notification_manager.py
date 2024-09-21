from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import get_subscriptions
from weather import get_weather
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Функция для отправки уведомлений о погоде по подпискам пользователей
async def send_weather_notifications():
    subscriptions = get_subscriptions()  # Получаем все подписки из базы данных

    for user_id, city_name, interval in subscriptions:
        weather_info = get_weather(city_name)  # Получаем данные о погоде для подписанного города
        await bot.send_message(chat_id=user_id, text=weather_info)  # Отправляем сообщение пользователю

def schedule_weather_notifications(application):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_weather_notifications, 'interval', hours=1)  # Запуск каждый час
    scheduler.start()

