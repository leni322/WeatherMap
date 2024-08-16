import requests
import sys
import sqlite3
import os
from config import API_KEY, BASE_URL
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

def get_weather(city_name):
    url = f"{BASE_URL}?q={city_name}&appid={API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_info = format_weather_data(data)
        save_to_db(city_name, weather_info)
        return weather_info
    elif response.status_code == 404:
        return f"Город '{city_name}' не найден. Пожалуйста, проверьте название и попробуйте снова."
    else:
        return f"Ошибка при запросе данных. Код ошибки: {response.status_code}"

def format_weather_data(data):
    city = data['name']
    country = data['sys']['country']
    temperature = data['main']['temp']
    description = data['weather'][0]['description']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']

    weather_report = (
        f"Погода в городе {city}, {country}:\n"
        f"Температура: {temperature}°C\n"
        f"Описание: {description.capitalize()}\n"
        f"Влажность: {humidity}%\n"
        f"Скорость ветра: {wind_speed} м/с\n"
    )

    return weather_report

def save_to_db(city_name, weather_info):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''INSERT INTO history (timestamp, city_name, weather_info)
        VALUES (?, ?, ?)
    ''', (timestamp, city_name, weather_info))
    conn.commit()
    conn.close()

def main():
    init_db()  # Инициализация базы данных при запуске программы

    while True:
        city_name = input("Введите название города (или 'выход' для завершения): ")

        if city_name.lower() == 'выход':
            print("Выход из программы.")
            sys.exit()

        weather = get_weather(city_name)
        print(weather)

if __name__ == "__main__":
    main()
