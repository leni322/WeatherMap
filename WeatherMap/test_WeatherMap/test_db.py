import sqlite3
import os
import pytest
from db import init_db, create_subscription, get_subscriptions, unsubscribe_user, save_to_db

@pytest.fixture
def setup_db():
    """Создаем тестовую БД перед каждым тестом и удаляем ее после."""
    db_path = 'test_weather_history.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db()
    yield
    if os.path.exists(db_path):
        os.remove(db_path)

def test_create_subscription(setup_db):
    create_subscription(123, 'Moscow', 24)
    subscriptions = get_subscriptions()
    assert len(subscriptions) == 1
    assert subscriptions[0] == (123, 'Moscow', 24)

def test_unsubscribe_user(setup_db):
    create_subscription(123, 'Moscow', 24)
    unsubscribe_user(123)
    subscriptions = get_subscriptions()
    assert len(subscriptions) == 0

def test_save_to_db(setup_db):
    save_to_db('Moscow', 'Sunny 25°C')
    conn = sqlite3.connect('test_weather_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history')
    history = cursor.fetchall()
    assert len(history) == 1
    assert history[0][2] == 'Moscow'
    assert history[0][3] == 'Sunny 25°C'
    conn.close()
