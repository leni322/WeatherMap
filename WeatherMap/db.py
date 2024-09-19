import sqlite3
import os
from datetime import datetime

db_path = os.path.join(os.getcwd(), 'weather_history.db')

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            city_name TEXT,
            weather_info TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        city_name TEXT,
        interval INTEGER DEFAULT 24 -- Интервал в часах, по умолчанию раз в сутки
        )
    ''')
    conn.commit()
    conn.close()

def subscribe_user(user_id, city_name, interval=24):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO subscriptions (user_id, city_name, interval)
        VALUES (?, ?, ?)
    ''',(user_id,city_name,interval))
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
        VALUES (?, ?, ?)
    ''', (timestamp, city_name, weather_info))
    conn.commit()
    conn.close()