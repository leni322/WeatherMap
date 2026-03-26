from pathlib import Path

import openmeteo_requests
import requests_cache
from retry_requests import retry

from config import WEATHER_CACHE_SECONDS, WEATHER_TIMEZONE

try:
    from .db import save_to_db
except ImportError:
    from db import save_to_db


CITIES_COORDINATES = {
    "Москва": (55.7558, 37.6173),
    "Санкт-Петербург": (59.9386, 30.3141),
    "Новосибирск": (55.0084, 82.9357),
    "Екатеринбург": (56.8389, 60.6057),
    "Ростов-на-Дону": (47.2357, 39.7015),
    "Новочеркасск": (47.4183, 40.0936),
}

CITIES = list(CITIES_COORDINATES.keys())
CACHE_PATH = Path(__file__).resolve().parent / ".cache"


def get_weather(city_name: str) -> str:
    if city_name not in CITIES_COORDINATES:
        return "Координаты для этого города не найдены."

    latitude, longitude = CITIES_COORDINATES[city_name]
    cache_session = requests_cache.CachedSession(
        str(CACHE_PATH), expire_after=WEATHER_CACHE_SECONDS
    )
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation_probability",
            "precipitation",
            "rain",
            "snowfall",
            "snow_depth",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "timezone": WEATHER_TIMEZONE,
    }

    try:
        response = openmeteo.weather_api(
            "https://api.open-meteo.com/v1/forecast", params=params
        )[0]
        hourly = response.Hourly()

        temperature = round(hourly.Variables(0).ValuesAsNumpy()[0], 1)
        humidity = round(hourly.Variables(1).ValuesAsNumpy()[0], 1)
        feels_like = round(hourly.Variables(2).ValuesAsNumpy()[0], 1)
        precipitation_probability = round(hourly.Variables(3).ValuesAsNumpy()[0], 1)
        rain = round(hourly.Variables(5).ValuesAsNumpy()[0], 1)
        wind_speed = round(hourly.Variables(8).ValuesAsNumpy()[0], 1)

        weather_message = (
            f"Температура: {temperature}°C\n"
            f"Ощущается как: {feels_like}°C\n"
            f"Влажность: {humidity}%\n"
            f"Скорость ветра: {wind_speed} м/с\n"
            f"Вероятность осадков: {precipitation_probability}%\n"
            f"Дождь: {rain} мм"
        )
        save_to_db(city_name, weather_message)
        return weather_message
    except Exception as error:
        return f"Ошибка при получении данных: {error}"
