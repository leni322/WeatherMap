import sqlite3
import os
from datetime import datetime

db_path = os.path.join(os.getcwd(), 'weather_history.db')


def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Таблица истории погоды
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        city_name TEXT,
        weather_info TEXT
    )''')

    # Таблица подписок
    cursor.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        city_name TEXT,
        interval INTEGER DEFAULT 24,  -- Интервал в часах
        is_active BOOLEAN DEFAULT 1,  -- Статус подписки (1 = активна, 0 = отключена)
        notifications_sent INTEGER DEFAULT 0 -- Счетчик отправленных уведомлений
    )''')

    # Проверка и добавление новых колонок при необходимости
    cursor.execute("PRAGMA table_info(subscriptions);")
    columns = [column[1] for column in cursor.fetchall()]

    if 'interval' not in columns:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN interval INTEGER DEFAULT 24;")

    if 'city_name' not in columns:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN city_name TEXT;")

    if 'is_active' not in columns:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN is_active BOOLEAN DEFAULT 1;")

    if 'notifications_sent' not in columns:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN notifications_sent INTEGER DEFAULT 0;")

    conn.commit()
    conn.close()

# Функция для добавления подписки
def create_subscription(user_id, city_name, interval=24):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO subscriptions (user_id, city_name, interval, is_active, notifications_sent)
                      VALUES (?, ?, ?, ?, ?)''', (user_id, city_name, interval, 1, 0))

    conn.commit()
    conn.close()

# Обновление статуса подписки
def update_subscription_status(user_id, is_active):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('UPDATE subscriptions SET is_active = ? WHERE user_id = ?', (is_active, user_id))

    conn.commit()
    conn.close()

# Инкремент счетчика отправленных уведомлений
def increment_notification_count(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('UPDATE subscriptions SET notifications_sent = notifications_sent + 1 WHERE user_id = ?', (user_id,))

    conn.commit()
    conn.close()

# Получаем все подписки
def get_subscriptions():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, city_name, interval, is_active, notifications_sent FROM subscriptions')
    subscriptions = cursor.fetchall()
    conn.close()
    return subscriptions

# Сохранение истории погоды
def save_to_db(city_name, weather_info):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''INSERT INTO history (timestamp, city_name, weather_info)
                      VALUES (?, ?, ?)''', (timestamp, city_name, weather_info))
    conn.commit()
    conn.close()

# Проверка существующих таблиц
def check_tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return tables

def unsubscribe_user(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# Подписка пользователя
def subscribe_user(user_id, city_name, interval=24):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверяем, существует ли уже подписка
    cursor.execute("SELECT * FROM subscriptions WHERE user_id = ? AND city_name = ?", (user_id, city_name))
    existing_subscription = cursor.fetchone()

    if existing_subscription:
        print(f"User {user_id} is already subscribed to {city_name}.")
    else:
        cursor.execute(
            "INSERT INTO subscriptions (user_id, city_name, interval, is_active, notifications_sent) VALUES (?, ?, ?, ?, ?)",
            (user_id, city_name, interval, 1, 0))
        print(f"User {user_id} subscribed to {city_name}.")

    conn.commit()
    conn.close()
