import json
import logging

import requests
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import NetworkError, TimedOut
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler

from config import (
    FASTAPI_URL,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CONNECT_TIMEOUT,
    TELEGRAM_POOL_TIMEOUT,
    TELEGRAM_READ_TIMEOUT,
    TELEGRAM_WRITE_TIMEOUT,
)

try:
    from .db import (
        create_subscription,
        get_subscription,
        get_weather_history,
        init_db,
        unsubscribe_user,
    )
    from .renderers import render_weather_html
    from . import ui_text
    from .weather import CITIES, get_weather_data
except ImportError:
    from db import (
        create_subscription,
        get_subscription,
        get_weather_history,
        init_db,
        unsubscribe_user,
    )
    from renderers import render_weather_html
    import ui_text
    from weather import CITIES, get_weather_data


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

INTERVAL_OPTIONS = [3, 6, 12, 24]


def build_main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(ui_text.BUTTON_GET_WEATHER, callback_data="get_weather")],
        [InlineKeyboardButton(ui_text.BUTTON_SUBSCRIBE, callback_data="subscribe")],
        [InlineKeyboardButton(ui_text.BUTTON_SHOW_SUBSCRIPTION, callback_data="show_subscription")],
        [InlineKeyboardButton(ui_text.BUTTON_HISTORY, callback_data="history")],
        [InlineKeyboardButton(ui_text.BUTTON_UNSUBSCRIBE, callback_data="unsubscribe")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_persistent_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("/menu"), KeyboardButton("/history")],
        [KeyboardButton("/subscriptions"), KeyboardButton("/unsubscribe")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def build_city_keyboard(prefix: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(city, callback_data=f"{prefix}{city}") for city in CITIES[:3]],
        [InlineKeyboardButton(city, callback_data=f"{prefix}{city}") for city in CITIES[3:]],
        [InlineKeyboardButton(ui_text.BUTTON_BACK, callback_data="menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_interval_keyboard(city_name: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                ui_text.PROMPT_INTERVAL_BUTTON.format(interval=interval),
                callback_data=f"interval_{city_name}_{interval}",
            )
        ]
        for interval in INTERVAL_OPTIONS
    ]
    keyboard.append([InlineKeyboardButton(ui_text.BUTTON_BACK, callback_data="subscribe")])
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
                ui_text.SUBSCRIBE_LOCAL.format(
                    user_id=user_id,
                    city_name=city_name,
                    interval=interval,
                )
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
        return {"message": ui_text.UNSUBSCRIBE_LOCAL.format(user_id=user_id)}


def format_subscription(subscription: dict) -> str:
    status = (
        ui_text.SUBSCRIPTION_STATUS_ACTIVE
        if subscription["is_active"]
        else ui_text.SUBSCRIPTION_STATUS_INACTIVE
    )
    return ui_text.SUBSCRIPTION_TEMPLATE.format(
        city_name=subscription["city_name"],
        interval=subscription["interval"],
        status=status,
        notifications_sent=subscription["notifications_sent"],
    )


def format_history(limit: int = 5) -> str:
    history_rows = get_weather_history(limit=limit)
    if not history_rows:
        return ui_text.HISTORY_EMPTY

    lines = [ui_text.HISTORY_TITLE]
    for timestamp, city_name, weather_info in history_rows:
        try:
            payload = json.loads(weather_info)
            summary = payload.get("summary", ui_text.HISTORY_NO_DATA)
            temperature = payload.get("current", {}).get("temperature_c")
            first_line = f"{summary}, {temperature}°C" if temperature else summary
        except (json.JSONDecodeError, TypeError):
            first_line = weather_info.splitlines()[0] if weather_info else ui_text.HISTORY_NO_DATA
        lines.append(f"{timestamp} | {city_name} | {first_line}")
    return "\n".join(lines)


async def send_main_menu(update: Update, text: str) -> None:
    if update.callback_query:
        await update.callback_query.message.reply_text(
            text,
            reply_markup=build_persistent_keyboard(),
        )
        await update.callback_query.edit_message_text(
            ui_text.MAIN_MENU_TITLE,
            reply_markup=build_main_menu(),
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=build_persistent_keyboard(),
        )
        await update.message.reply_text(
            ui_text.MAIN_MENU_TITLE,
            reply_markup=build_main_menu(),
        )


async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Command /start received")
    await send_main_menu(update, ui_text.MAIN_MENU_PINNED)


async def menu_command(update: Update, context: CallbackContext) -> None:
    await send_main_menu(update, ui_text.MAIN_MENU_REFRESHED)


async def history_command(update: Update, context: CallbackContext) -> None:
    message = format_history(limit=5)
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=build_main_menu())
    else:
        await update.message.reply_text(message, reply_markup=build_persistent_keyboard())


async def show_subscription(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    try:
        subscription = api_get_subscription(user_id)
        message = format_subscription(subscription)
    except requests.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            message = ui_text.SUBSCRIPTION_MISSING
        else:
            logger.exception("Failed to load subscription for user %s", user_id)
            message = ui_text.SUBSCRIPTION_LOAD_ERROR.format(error=error)
    except requests.RequestException:
        if get_subscription(user_id):
            subscription = api_get_subscription(user_id)
            message = format_subscription(subscription)
        else:
            logger.exception("Failed to reach API for subscription details")
            message = ui_text.SUBSCRIPTION_MISSING

    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=build_main_menu())
    else:
        await update.message.reply_text(message, reply_markup=build_persistent_keyboard())


async def unsubscribe_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    try:
        payload = api_unsubscribe(user_id)
        message = payload["message"]
    except requests.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            message = ui_text.UNSUBSCRIBE_MISSING
        else:
            logger.exception("Failed to unsubscribe user %s", user_id)
            message = ui_text.UNSUBSCRIBE_ERROR.format(error=error)
    except requests.RequestException:
        if unsubscribe_user(user_id):
            message = ui_text.UNSUBSCRIBE_LOCAL.format(user_id=user_id)
        else:
            logger.exception("Failed to reach API for unsubscribe")
            message = ui_text.UNSUBSCRIBE_MISSING

    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=build_main_menu())
    else:
        await update.message.reply_text(message, reply_markup=build_persistent_keyboard())


async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "get_weather":
        await query.edit_message_text(
            text=ui_text.PROMPT_SELECT_CITY,
            reply_markup=build_city_keyboard("weather_"),
        )
    elif query.data == "subscribe":
        await query.edit_message_text(
            text=ui_text.PROMPT_SELECT_SUBSCRIBE_CITY,
            reply_markup=build_city_keyboard("subscribe_"),
        )
    elif query.data == "show_subscription":
        await show_subscription(update, context)
    elif query.data == "history":
        await history_command(update, context)
    elif query.data == "unsubscribe":
        await unsubscribe_command(update, context)
    elif query.data == "menu":
        await query.edit_message_text(ui_text.MAIN_MENU_TITLE, reply_markup=build_main_menu())
    elif query.data.startswith("weather_"):
        city_name = query.data.removeprefix("weather_")
        weather_data = get_weather_data(city_name)
        weather_html = render_weather_html(weather_data)
        await query.edit_message_text(
            weather_html,
            reply_markup=build_main_menu(),
            parse_mode=ParseMode.HTML,
        )
    elif query.data.startswith("subscribe_"):
        city_name = query.data.removeprefix("subscribe_")
        await query.edit_message_text(
            ui_text.PROMPT_INTERVAL.format(city_name=city_name),
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
                ui_text.SUBSCRIBE_ERROR.format(city_name=city_name, error=error),
                reply_markup=build_main_menu(),
            )


async def error(update: Update, context: CallbackContext) -> None:
    logger.warning("Update %s caused error %s", update, context.error)


def main():
    init_db()
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .connect_timeout(TELEGRAM_CONNECT_TIMEOUT)
        .read_timeout(TELEGRAM_READ_TIMEOUT)
        .write_timeout(TELEGRAM_WRITE_TIMEOUT)
        .pool_timeout(TELEGRAM_POOL_TIMEOUT)
        .get_updates_connect_timeout(TELEGRAM_CONNECT_TIMEOUT)
        .get_updates_read_timeout(TELEGRAM_READ_TIMEOUT)
        .get_updates_write_timeout(TELEGRAM_WRITE_TIMEOUT)
        .get_updates_pool_timeout(TELEGRAM_POOL_TIMEOUT)
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("subscriptions", show_subscription))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error)
    try:
        application.run_polling(
            connect_timeout=TELEGRAM_CONNECT_TIMEOUT,
            read_timeout=TELEGRAM_READ_TIMEOUT,
            write_timeout=TELEGRAM_WRITE_TIMEOUT,
            pool_timeout=TELEGRAM_POOL_TIMEOUT,
        )
    except TimedOut:
        logger.error(
            "Telegram API timed out during startup. Check internet access to api.telegram.org "
            "or increase TELEGRAM_*_TIMEOUT values in .env."
        )
    except NetworkError as network_error:
        logger.error(
            "Telegram network error during startup: %s. Check internet access, proxy/VPN, "
            "firewall, or Telegram API availability.",
            network_error,
        )


if __name__ == "__main__":
    main()
