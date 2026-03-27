from datetime import datetime
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

WEATHER_CODES = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Изморозь",
    51: "Слабая морось",
    53: "Умеренная морось",
    55: "Сильная морось",
    56: "Слабая ледяная морось",
    57: "Сильная ледяная морось",
    61: "Слабый дождь",
    63: "Умеренный дождь",
    65: "Сильный дождь",
    66: "Слабый ледяной дождь",
    67: "Сильный ледяной дождь",
    71: "Слабый снег",
    73: "Умеренный снег",
    75: "Сильный снег",
    77: "Снежные зерна",
    80: "Слабый ливень",
    81: "Умеренный ливень",
    82: "Сильный ливень",
    85: "Слабый снегопад",
    86: "Сильный снегопад",
    95: "Гроза",
    96: "Гроза с слабым градом",
    99: "Гроза с сильным градом",
}

CITIES = list(CITIES_COORDINATES.keys())
CACHE_PATH = Path(__file__).resolve().parent / ".cache"


def format_number(value, digits: int = 1) -> str:
    return f"{float(value):.{digits}f}"


def wind_direction_to_text(degrees: float) -> str:
    directions = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    index = round(float(degrees) / 45) % len(directions)
    return directions[index]


def format_unix_time(timestamp: int) -> str:
    return datetime.fromtimestamp(int(timestamp)).strftime("%H:%M")


def get_weather_description(code: float) -> str:
    return WEATHER_CODES.get(int(code), "Неизвестные погодные условия")


def build_recommendations(
    temperature: float,
    feels_like: float,
    wind_speed: float,
    wind_gusts: float,
    precipitation_probability_max: float,
    rain: float,
    min_temp: float,
    max_temp: float,
) -> list[str]:
    recommendations = []

    if precipitation_probability_max >= 60 or rain >= 0.5:
        recommendations.append("Возьмите зонт: вероятность осадков высокая.")
    elif precipitation_probability_max <= 20 and rain == 0:
        recommendations.append("Зонт, скорее всего, не понадобится.")

    if wind_speed >= 10 or wind_gusts >= 15:
        recommendations.append("Ожидается сильный ветер, лучше одеться плотнее.")

    if feels_like <= 5:
        recommendations.append("На улице прохладно, стоит одеться теплее.")
    elif temperature >= 25:
        recommendations.append("Будет тепло, выбирайте более легкую одежду.")

    if (temperature - feels_like) >= 4:
        recommendations.append("По ощущениям заметно холоднее, чем показывает термометр.")

    if (max_temp - min_temp) >= 8:
        recommendations.append("В течение дня ожидается заметный перепад температуры.")

    if not recommendations:
        recommendations.append("Погодные условия комфортные, без резких изменений.")

    return recommendations


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
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "rain",
            "weather_code",
            "cloud_cover",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
        ],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "sunrise",
            "sunset",
        ],
        "timezone": WEATHER_TIMEZONE,
    }

    try:
        response = openmeteo.weather_api(
            "https://api.open-meteo.com/v1/forecast", params=params
        )[0]
        current = response.Current()
        daily = response.Daily()

        temperature = current.Variables(0).Value()
        humidity = current.Variables(1).Value()
        feels_like = current.Variables(2).Value()
        precipitation = current.Variables(3).Value()
        rain = current.Variables(4).Value()
        weather_code = current.Variables(5).Value()
        cloud_cover = current.Variables(6).Value()
        pressure = current.Variables(7).Value()
        wind_speed = current.Variables(8).Value()
        wind_direction = current.Variables(9).Value()
        wind_gusts = current.Variables(10).Value()

        max_temp = daily.Variables(0).ValuesAsNumpy()[0]
        min_temp = daily.Variables(1).ValuesAsNumpy()[0]
        precipitation_probability_max = daily.Variables(2).ValuesAsNumpy()[0]
        sunrise = daily.Variables(3).ValuesInt64AsNumpy()[0]
        sunset = daily.Variables(4).ValuesInt64AsNumpy()[0]

        description = get_weather_description(weather_code)
        wind_direction_text = wind_direction_to_text(wind_direction)
        recommendations = build_recommendations(
            temperature=temperature,
            feels_like=feels_like,
            wind_speed=wind_speed,
            wind_gusts=wind_gusts,
            precipitation_probability_max=precipitation_probability_max,
            rain=rain,
            min_temp=min_temp,
            max_temp=max_temp,
        )
        recommendations_block = "\n".join(
            f"- {recommendation}" for recommendation in recommendations
        )

        weather_message = (
            f"Сейчас: {description}\n"
            f"Температура: {format_number(temperature)}°C\n"
            f"Ощущается как: {format_number(feels_like)}°C\n"
            f"Температура за день: от {format_number(min_temp)}°C до {format_number(max_temp)}°C\n"
            f"Влажность: {format_number(humidity, 0)}%\n"
            f"Давление: {format_number(pressure, 0)} гПа\n"
            f"Облачность: {format_number(cloud_cover, 0)}%\n"
            f"Ветер: {format_number(wind_speed)} м/с, {wind_direction_text}\n"
            f"Порывы ветра: до {format_number(wind_gusts)} м/с\n"
            f"Осадки сейчас: {format_number(precipitation)} мм\n"
            f"Дождь сейчас: {format_number(rain)} мм\n"
            f"Вероятность осадков сегодня: {format_number(precipitation_probability_max, 0)}%\n"
            f"Восход: {format_unix_time(sunrise)}\n"
            f"Закат: {format_unix_time(sunset)}\n"
            f"\nРекомендации:\n{recommendations_block}"
        )
        save_to_db(city_name, weather_message)
        return weather_message
    except Exception as error:
        return f"Ошибка при получении данных: {error}"
