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
    conn.commit()
    conn.close()

def save_to_db(city_name, weather_info):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''INSERT INTO history (timestamp, city_name, weather_info)
        VALUES (?, ?, ?)
    ''', (timestamp, city_name, weather_info))
    conn.commit()
    conn.close()