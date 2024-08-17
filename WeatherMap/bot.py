import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from weather import get_weather
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> None:
    logger.info('Command /start received')
    await update.message.reply_text('Привет! Введите /weather <город>, чтобы получить погоду.')



async def weather(update: Update, context: CallbackContext) -> None:
    logger.info('Command /weather received')
    if len(context.args) > 0:
        city_name = ' '.join(context.args)
        logger.info(f'Fetching weather for city: {city_name}')
        weather_info = get_weather(city_name)
        logger.info(f'Weather info: {weather_info}')
        await update.message.reply_text(weather_info)
    else:
        await update.message.reply_text('Пожалуйста, укажите город после команды /weather.')


async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather))

    application.add_error_handler(error)

    application.run_polling()


if __name__ == '__main__':
    main()





