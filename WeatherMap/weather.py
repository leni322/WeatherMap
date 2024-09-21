import requests
from config import API_KEY, BASE_URL

def get_weather(city_name):
    url = f"{BASE_URL}?q={city_name}&appid={API_KEY}&units=metric&lang=ru"
    try:
        response = requests.get(url, timeout=10)  # Указываем тайм-аут в 10 секунд
        response.raise_for_status()
        data = response.json()
        return format_weather_data(data)
    except requests.exceptions.HTTPError as errh:
        return f"Http Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return f"Error Connecting: {errc}"
    except requests.exceptions.Timeout as errt:
        return "Сервер не ответил вовремя. Попробуйте позже."
    except requests.exceptions.RequestException as err:
        return f"Oops: {err}"

def format_weather_data(data):
    try:
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
    except KeyError as e:
        return f"Ошибка в данных: {e}"



