import sqlite3
import os
from datetime import datetime

db_path = os.path.join(os.getcwd(), 'weather_history.db')


def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        city_name TEXT,
        weather_info TEXT
    )''')

    # Создание таблицы подписок, если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        city_name TEXT,
        interval INTEGER DEFAULT 24 -- Интервал в часах
    )''')

    # Проверяем наличие колонки interval и добавляем, если ее нет
    cursor.execute("PRAGMA table_info(subscriptions);")
    columns = [column[1] for column in cursor.fetchall()]
    if 'interval' not in columns:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN interval INTEGER DEFAULT 24;")

    # Проверяем наличие колонки city_name и добавляем, если ее нет
    if 'city_name' not in columns:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN city_name TEXT;")

    conn.commit()
    conn.close()


def create_subscription(user_id, city_name, interval=1):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO subscriptions (user_id, city_name, interval)
                      VALUES (?, ?, ?)''', (user_id, city_name, interval))
    conn.commit()
    conn.close()

def unsubscribe_user(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_subscriptions():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, city_name, interval FROM subscriptions')
    subscriptions = cursor.fetchall()
    conn.close()
    return subscriptions

def save_to_db(city_name, weather_info):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''INSERT INTO history (timestamp, city_name, weather_info)
                      VALUES (?, ?, ?)''', (timestamp, city_name, weather_info))
    conn.commit()
    conn.close()

def check_tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return tables


def subscribe_user(user_id, city_name, interval=24):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверяем, существует ли уже подписка
    cursor.execute("SELECT * FROM subscriptions WHERE user_id = ? AND city_name = ?", (user_id, city_name))
    existing_subscription = cursor.fetchone()

    if existing_subscription:
        print(f"User {user_id} is already subscribed to {city_name}.")
    else:
        cursor.execute("INSERT INTO subscriptions (user_id, city_name, interval) VALUES (?, ?, ?)",
                       (user_id, city_name, interval))
        print(f"User {user_id} subscribed to {city_name}.")

    conn.commit()
    conn.close()
