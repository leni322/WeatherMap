import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from weather import get_weather
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Определяем доступные города и их координаты
CITIES = {
    'Москва': 'Moscow',
    'Санкт-Петербург': 'Saint Petersburg',
    'Новосибирск': 'Novosibirsk',
    'Екатеринбург': 'Yekaterinburg',
}


async def start(update: Update, context: CallbackContext) -> None:
    logger.info('Command /start received')

    keyboard = [
        ['Москва', 'Санкт-Петербург'],
        ['Новосибирск', 'Екатеринбург'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        'Привет! Выберите город для получения погоды или введите /weather <город>, чтобы получить погоду.',
        reply_markup=reply_markup
    )


async def weather(update: Update, context: CallbackContext) -> None:
    logger.info('Command /weather received')

    city_name = ' '.join(context.args) if context.args else update.message.text

    if city_name in CITIES.keys() or city_name in CITIES.values():
        city_name_en = CITIES.get(city_name, city_name)
        logger.info(f'Fetching weather for city: {city_name_en}')
        weather_info = get_weather(city_name_en)
        logger.info(f'Weather info: {weather_info}')
        await update.message.reply_text(weather_info)
    else:
        await update.message.reply_text(
            'Пожалуйста, выберите город из предложенных или укажите правильное название города после команды /weather.')


async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, weather))

    application.add_error_handler(error)

    application.run_polling()


if __name__ == '__main__':
    main()






