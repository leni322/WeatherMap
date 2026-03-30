import json
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


def get_weather_data(city_name: str) -> dict:
    if city_name not in CITIES_COORDINATES:
        raise ValueError("Координаты для этого города не найдены.")

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

    weather_data = {
        "city_name": city_name,
        "summary": get_weather_description(weather_code),
        "current": {
            "temperature_c": format_number(temperature),
            "feels_like_c": format_number(feels_like),
            "humidity_percent": format_number(humidity, 0),
            "pressure_hpa": format_number(pressure, 0),
            "cloud_cover_percent": format_number(cloud_cover, 0),
            "wind_speed_ms": format_number(wind_speed),
            "wind_direction": wind_direction_to_text(wind_direction),
            "wind_gusts_ms": format_number(wind_gusts),
            "precipitation_mm": format_number(precipitation),
            "rain_mm": format_number(rain),
        },
        "daily": {
            "temp_min_c": format_number(min_temp),
            "temp_max_c": format_number(max_temp),
            "precipitation_probability_percent": format_number(
                precipitation_probability_max, 0
            ),
            "sunrise": format_unix_time(sunrise),
            "sunset": format_unix_time(sunset),
        },
        "recommendations": build_recommendations(
            temperature=temperature,
            feels_like=feels_like,
            wind_speed=wind_speed,
            wind_gusts=wind_gusts,
            precipitation_probability_max=precipitation_probability_max,
            rain=rain,
            min_temp=min_temp,
            max_temp=max_temp,
        ),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_to_db(city_name, json.dumps(weather_data, ensure_ascii=False))
    return weather_data


def get_weather(city_name: str) -> str:
    try:
        weather_data = get_weather_data(city_name)
        return json.dumps(weather_data, ensure_ascii=False)
    except Exception as error:
        return json.dumps(
            {"city_name": city_name, "error": f"Ошибка при получении данных: {error}"},
            ensure_ascii=False,
        )
