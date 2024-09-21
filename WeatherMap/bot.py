import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from weather import get_weather
from db import init_db, check_tables, subscribe_user  # Обновите импорт
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CITIES = {
    'Москва': 'Moscow',
    'Санкт-Петербург': 'Saint Petersburg',
    'Новосибирск': 'Novosibirsk',
    'Екатеринбург': 'Yekaterinburg',
    'Ростов-на-Дону': 'Rostov-on-Don',
    'Новочеркасск': 'Novocherkassk',
}

async def start(update: Update, context: CallbackContext) -> None:
    logger.info('Command /start received')
    keyboard = [
        [InlineKeyboardButton("Получить погоду", callback_data='get_weather')],
        [InlineKeyboardButton("Подписаться на уведомления", callback_data='subscribe')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Привет! Выберите действие:',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'get_weather':
        keyboard = [
            [InlineKeyboardButton(city, callback_data=f"weather_{city}") for city in ['Москва', 'Санкт-Петербург']],
            [InlineKeyboardButton(city, callback_data=f"weather_{city}") for city in ['Новосибирск', 'Екатеринбург']],
            [InlineKeyboardButton("Отмена", callback_data='cancel')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите город:", reply_markup=reply_markup)

    elif query.data == 'subscribe':
        keyboard = [
            [InlineKeyboardButton(city, callback_data=f"subscribe_{city}") for city in ['Москва', 'Санкт-Петербург']],
            [InlineKeyboardButton(city, callback_data=f"subscribe_{city}") for city in ['Новосибирск', 'Екатеринбург']],
            [InlineKeyboardButton("Отмена", callback_data='cancel')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите город для подписки:", reply_markup=reply_markup)

    elif query.data.startswith('weather_'):
        city_name = query.data.split('_')[1]
        weather_info = get_weather(city_name)
        await query.edit_message_text(f"Погода в {city_name}: \n{weather_info}")

    elif query.data.startswith('subscribe_'):
        city_name = query.data.split('_')[1]
        # Здесь вызываем функцию для подписки пользователя
        subscribe_user(query.from_user.id, city_name)
        await query.edit_message_text(f"Вы подписаны на уведомления для города {city_name}!")

    elif query.data == 'cancel':
        await query.edit_message_text("Операция отменена.")

async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

def main():
    init_db()
    tables = check_tables()
    print("Таблицы в базе данных:", tables)

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.add_error_handler(error)

    application.run_polling()

if __name__ == '__main__':
    main()






