import pytest
from unittest.mock import MagicMock
from bot import start, get_weather

@pytest.fixture
def mock_update():
    return MagicMock()

@pytest.fixture
def mock_context():
    return MagicMock()

def test_start_command(mock_update, mock_context):
    start(mock_update, mock_context)
    mock_context.bot.send_message.assert_called_once_with(
        chat_id=mock_update.effective_chat.id,
        text="Привет! Выберите город."
    )

def test_get_weather(mock_update, mock_context):
    get_weather(mock_update, mock_context)
    mock_context.bot.send_message.assert_called()
