import requests
import sys
from config import API_KEY, BASE_URL


def get_weather(city_name):
    # Формируем полный URL с параметрами
    url = f"{BASE_URL}?q={city_name}&appid={API_KEY}&units=metric&lang=ru"

    # Делаем запрос к API
    response = requests.get(url)

    # Проверяем статус-код ответа
    if response.status_code == 200:
        data = response.json()
        return format_weather_data(data)  # Передаем data в функцию
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


def main():
    while True:
        city_name = input("Введите название города (или 'выход' для завершения): ")

        if city_name.lower() == 'выход':
            print("Выход из программы.")
            sys.exit()

        weather = get_weather(city_name)
        print(weather)


if __name__ == "__main__":
    main()
