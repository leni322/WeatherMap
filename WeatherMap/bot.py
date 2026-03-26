import logging

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler

from config import FASTAPI_URL, TELEGRAM_BOT_TOKEN

try:
    from .db import create_subscription, get_subscription, init_db, unsubscribe_user
    from .weather import CITIES, get_weather
except ImportError:
    from db import create_subscription, get_subscription, init_db, unsubscribe_user
    from weather import CITIES, get_weather


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

INTERVAL_OPTIONS = [3, 6, 12, 24]


def build_main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Получить погоду", callback_data="get_weather")],
        [InlineKeyboardButton("Подписаться на уведомления", callback_data="subscribe")],
        [InlineKeyboardButton("Моя подписка", callback_data="show_subscription")],
        [InlineKeyboardButton("Отписаться", callback_data="unsubscribe")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_city_keyboard(prefix: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(city, callback_data=f"{prefix}{city}") for city in CITIES[:3]],
        [InlineKeyboardButton(city, callback_data=f"{prefix}{city}") for city in CITIES[3:]],
        [InlineKeyboardButton("Назад", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_interval_keyboard(city_name: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                f"Каждые {interval} ч.",
                callback_data=f"interval_{city_name}_{interval}",
            )
        ]
        for interval in INTERVAL_OPTIONS
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="subscribe")])
    return InlineKeyboardMarkup(keyboard)


def api_get_subscription(user_id: int) -> dict:
    try:
        response = requests.get(f"{FASTAPI_URL}/subscriptions/{user_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        subscription = get_subscription(user_id)
        if not subscription:
            raise
        response_user_id, city_name, interval, is_active, notifications_sent = subscription
        return {
            "user_id": response_user_id,
            "city_name": city_name,
            "interval": interval,
            "is_active": bool(is_active),
            "notifications_sent": notifications_sent,
        }


def api_subscribe(user_id: int, city_name: str, interval: int = 24) -> dict:
    try:
        response = requests.post(
            f"{FASTAPI_URL}/subscribe",
            params={"user_id": user_id, "city_name": city_name, "interval": interval},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        create_subscription(user_id, city_name, interval)
        return {
            "message": (
                f"Подписка сохранена локально: пользователь {user_id} будет получать погоду "
                f"для {city_name} каждые {interval} ч."
            )
        }


def api_unsubscribe(user_id: int) -> dict:
    try:
        response = requests.delete(
            f"{FASTAPI_URL}/unsubscribe",
            params={"user_id": user_id},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        removed = unsubscribe_user(user_id)
        if not removed:
            raise
        return {"message": f"Подписка пользователя {user_id} удалена локально."}


def format_subscription(subscription: dict) -> str:
    status = "активна" if subscription["is_active"] else "отключена"
    return (
        "Текущая подписка:\n"
        f"Город: {subscription['city_name']}\n"
        f"Интервал: каждые {subscription['interval']} ч.\n"
        f"Статус: {status}\n"
        f"Уведомлений отправлено: {subscription['notifications_sent']}"
    )


async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Command /start received")
    await update.message.reply_text(
        "Привет! Выберите действие:",
        reply_markup=build_main_menu(),
    )


async def show_subscription(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    try:
        subscription = api_get_subscription(user_id)
        message = format_subscription(subscription)
    except requests.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            message = "У вас пока нет активной подписки."
        else:
            logger.exception("Failed to load subscription for user %s", user_id)
            message = f"Не удалось получить данные о подписке. Ошибка: {error}"
    except requests.RequestException:
        if get_subscription(user_id):
            subscription = api_get_subscription(user_id)
            message = format_subscription(subscription)
        else:
            logger.exception("Failed to reach API for subscription details")
            message = "У вас пока нет активной подписки."

    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=build_main_menu())
    else:
        await update.message.reply_text(message, reply_markup=build_main_menu())


async def unsubscribe_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    try:
        payload = api_unsubscribe(user_id)
        message = payload["message"]
    except requests.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            message = "У вас нет подписки, которую можно удалить."
        else:
            logger.exception("Failed to unsubscribe user %s", user_id)
            message = f"Не удалось удалить подписку. Ошибка: {error}"
    except requests.RequestException:
        if unsubscribe_user(user_id):
            message = f"Подписка пользователя {user_id} удалена локально."
        else:
            logger.exception("Failed to reach API for unsubscribe")
            message = "У вас нет подписки, которую можно удалить."

    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=build_main_menu())
    else:
        await update.message.reply_text(message, reply_markup=build_main_menu())


async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "get_weather":
        await query.edit_message_text(
            text="Выберите город:",
            reply_markup=build_city_keyboard("weather_"),
        )

    elif query.data == "subscribe":
        await query.edit_message_text(
            text="Выберите город для подписки:",
            reply_markup=build_city_keyboard("subscribe_"),
        )

    elif query.data == "show_subscription":
        await show_subscription(update, context)

    elif query.data == "unsubscribe":
        await unsubscribe_command(update, context)

    elif query.data == "menu":
        await query.edit_message_text("Главное меню:", reply_markup=build_main_menu())

    elif query.data.startswith("weather_"):
        city_name = query.data.removeprefix("weather_")
        weather_info = get_weather(city_name)
        await query.edit_message_text(
            f"Погода в {city_name}:\n{weather_info}",
            reply_markup=build_main_menu(),
        )

    elif query.data.startswith("subscribe_"):
        city_name = query.data.removeprefix("subscribe_")
        context.user_data["selected_city"] = city_name
        await query.edit_message_text(
            f"Выбран город: {city_name}\nТеперь выберите интервал уведомлений:",
            reply_markup=build_interval_keyboard(city_name),
        )

    elif query.data.startswith("interval_"):
        _, city_name, interval_text = query.data.rsplit("_", 2)
        interval = int(interval_text)
        user_id = query.from_user.id

        try:
            payload = api_subscribe(user_id, city_name, interval)
            await query.edit_message_text(payload["message"], reply_markup=build_main_menu())
        except requests.RequestException as error:
            logger.exception(
                "Failed to subscribe user %s to %s with interval %s",
                user_id,
                city_name,
                interval,
            )
            await query.edit_message_text(
                f"Не удалось оформить подписку для {city_name}. Ошибка: {error}",
                reply_markup=build_main_menu(),
            )


async def error(update: Update, context: CallbackContext) -> None:
    logger.warning("Update %s caused error %s", update, context.error)


def main():
    init_db()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscriptions", show_subscription))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error)
    application.run_polling()


if __name__ == "__main__":
    main()
