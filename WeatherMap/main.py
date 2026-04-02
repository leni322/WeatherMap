from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from telegram import Bot
from telegram.constants import ParseMode

from config import TELEGRAM_BOT_TOKEN

try:
    from .dashboard_renderer import render_dashboard
    from .db import (
        create_subscription,
        get_subscription,
        get_subscriptions,
        get_weather_history,
        increment_notification_count,
        init_db,
        unsubscribe_user,
    )
    from .renderers import render_weather_html
    from .weather import CITIES, get_weather_data
except ImportError:
    from dashboard_renderer import render_dashboard
    from db import (
        create_subscription,
        get_subscription,
        get_subscriptions,
        get_weather_history,
        increment_notification_count,
        init_db,
        unsubscribe_user,
    )
    from renderers import render_weather_html
    from weather import CITIES, get_weather_data


app = FastAPI(title="WeatherMap API")
bot = Bot(token=TELEGRAM_BOT_TOKEN)
scheduler = AsyncIOScheduler()


async def send_weather_notifications():
    subscriptions = get_subscriptions(active_only=True)
    for user_id, city_name, interval, is_active, notifications_sent in subscriptions:
        weather_data = get_weather_data(city_name)
        weather_html = render_weather_html(weather_data)
        await bot.send_message(
            chat_id=user_id,
            text=weather_html,
            parse_mode=ParseMode.HTML,
        )
        increment_notification_count(user_id)


def schedule_weather_notifications():
    if not scheduler.running:
        scheduler.add_job(send_weather_notifications, "interval", hours=1, id="weather_notifications")
        scheduler.start()


@app.on_event("startup")
async def on_startup():
    init_db()
    schedule_weather_notifications()


@app.get("/")
async def root():
    return {"message": "Weather notification bot is running!"}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(city: str = CITIES[0]):
    try:
        weather_data = get_weather_data(city)
        history_rows = get_weather_history(limit=6, city_name=city)
        html = render_dashboard(weather_data, history_rows, CITIES)
        return HTMLResponse(content=html)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Failed to render dashboard: {error}") from error


@app.post("/subscribe")
async def subscribe(user_id: int, city_name: str, interval: int = 24):
    try:
        create_subscription(user_id, city_name, interval)
        return {
            "message": (
                f"Подписка сохранена: пользователь {user_id} будет получать погоду "
                f"для {city_name} каждые {interval} ч."
            )
        }
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Failed to subscribe: {error}") from error


@app.delete("/unsubscribe")
async def unsubscribe(user_id: int):
    removed = unsubscribe_user(user_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Subscription for user {user_id} not found.")
    return {"message": f"Подписка пользователя {user_id} удалена."}


@app.get("/subscriptions/{user_id}")
async def subscription_details(user_id: int):
    subscription = get_subscription(user_id)
    if not subscription:
        raise HTTPException(status_code=404, detail=f"Subscription for user {user_id} not found.")

    response_user_id, city_name, interval, is_active, notifications_sent = subscription
    return {
        "user_id": response_user_id,
        "city_name": city_name,
        "interval": interval,
        "is_active": bool(is_active),
        "notifications_sent": notifications_sent,
    }


@app.get("/weather/{city_name}")
async def get_weather_info(city_name: str):
    try:
        return get_weather_data(city_name)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Failed to get weather: {error}") from error
