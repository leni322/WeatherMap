import requests
from unittest.mock import patch
from weather import get_weather_data

@patch('weather.requests.get')
def test_get_weather_data(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'weather': [{'description': 'clear sky'}],
        'main': {'temp': 22.5}
    }
    mock_get.return_value = mock_response

    city_name = 'Moscow'
    weather = get_weather_data(city_name)

    assert weather['description'] == 'clear sky'
    assert weather['temperature'] == 22.5
