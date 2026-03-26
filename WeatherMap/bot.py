import logging

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler

from config import FASTAPI_URL, TELEGRAM_BOT_TOKEN

try:
    from .weather import CITIES, get_weather
except ImportError:
    from weather import CITIES, get_weather


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Command /start received")
    keyboard = [
        [InlineKeyboardButton("Получить погоду", callback_data="get_weather")],
        [InlineKeyboardButton("Подписаться на уведомления", callback_data="subscribe")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! Выберите действие:",
        reply_markup=reply_markup,
    )


async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "get_weather":
        keyboard = [
            [InlineKeyboardButton(city, callback_data=f"weather_{city}") for city in CITIES[:3]],
            [InlineKeyboardButton(city, callback_data=f"weather_{city}") for city in CITIES[3:]],
            [InlineKeyboardButton("Отмена", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите город:", reply_markup=reply_markup)

    elif query.data == "subscribe":
        keyboard = [
            [InlineKeyboardButton(city, callback_data=f"subscribe_{city}") for city in CITIES[:3]],
            [InlineKeyboardButton(city, callback_data=f"subscribe_{city}") for city in CITIES[3:]],
            [InlineKeyboardButton("Отмена", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Выберите город для подписки:", reply_markup=reply_markup
        )

    elif query.data.startswith("weather_"):
        city_name = query.data.removeprefix("weather_")
        weather_info = get_weather(city_name)
        await query.edit_message_text(f"Погода в {city_name}:\n{weather_info}")

    elif query.data.startswith("subscribe_"):
        city_name = query.data.removeprefix("subscribe_")
        user_id = query.from_user.id

        try:
            response = requests.post(
                f"{FASTAPI_URL}/subscribe",
                params={"user_id": user_id, "city_name": city_name},
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
            await query.edit_message_text(payload["message"])
        except requests.RequestException as error:
            logger.exception("Failed to subscribe user %s to %s", user_id, city_name)
            await query.edit_message_text(
                f"Не удалось оформить подписку для {city_name}. Ошибка: {error}"
            )

    elif query.data == "cancel":
        await query.edit_message_text("Операция отменена.")


async def error(update: Update, context: CallbackContext) -> None:
    logger.warning("Update %s caused error %s", update, context.error)


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error)
    application.run_polling()


if __name__ == "__main__":
    main()
