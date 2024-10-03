import openmeteo_requests
import requests_cache
from retry_requests import retry

# Координаты городов
CITIES_COORDINATES = {
    'Москва': (55.7558, 37.6173),
    'Санкт-Петербург': (59.9386, 30.3141),
    'Новосибирск': (55.0084, 82.9357),
    'Екатеринбург': (56.8389, 60.6057),
    'Ростов-на-Дону': (47.2357, 39.7015),
    'Новочеркасск': (47.4183, 40.0936),
}


def get_weather(city_name: str) -> str:
    """Получает погоду для указанного города с помощью Open-Meteo API."""
    if city_name not in CITIES_COORDINATES:
        return "Координаты для этого города не найдены."

    latitude, longitude = CITIES_COORDINATES[city_name]

    # Настройка сессии с кешированием и повторными запросами
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Параметры для запроса
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "precipitation_probability", "precipitation", "rain", "snowfall",
            "snow_depth", "wind_speed_10m", "wind_direction_10m"
        ],
        "timezone": "Europe/Moscow"
    }

    try:
        response = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)[0]
        hourly = response.Hourly()

        # Извлечение параметров
        temperature = round(hourly.Variables(0).ValuesAsNumpy()[0], 1)
        humidity = round(hourly.Variables(1).ValuesAsNumpy()[0], 1)
        wind_speed = round(hourly.Variables(8).ValuesAsNumpy()[0], 1)
        precipitation_probability = round(hourly.Variables(3).ValuesAsNumpy()[0], 1)
        rain = round(hourly.Variables(5).ValuesAsNumpy()[0], 1)

        # Красивое форматирование
        weather_message = (
            f"Погода в {city_name}:\n"
            f"Температура: {temperature}°C\n"
            f"Влажность: {humidity}%\n"
            f"Скорость ветра: {wind_speed}% м/с\n"
            f"Вероятность осадков: {precipitation_probability}%\n"
            f"Дождь: {rain} мм"
        )

        return weather_message

    except Exception as e:
        return f"Ошибка при получении данных: {e}"




