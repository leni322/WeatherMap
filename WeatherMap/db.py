import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from config import DATABASE_PATH


DB_PATH = Path(DATABASE_PATH)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                city_name TEXT NOT NULL,
                weather_info TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY,
                city_name TEXT NOT NULL,
                interval INTEGER DEFAULT 24,
                is_active INTEGER DEFAULT 1,
                notifications_sent INTEGER DEFAULT 0
            )
            """
        )

        cursor.execute("PRAGMA table_info(subscriptions)")
        columns = {column[1] for column in cursor.fetchall()}

        if "city_name" not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN city_name TEXT")
        if "interval" not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN interval INTEGER DEFAULT 24")
        if "is_active" not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN is_active INTEGER DEFAULT 1")
        if "notifications_sent" not in columns:
            cursor.execute(
                "ALTER TABLE subscriptions ADD COLUMN notifications_sent INTEGER DEFAULT 0"
            )

        conn.commit()


def create_subscription(user_id: int, city_name: str, interval: int = 24):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO subscriptions (user_id, city_name, interval, is_active, notifications_sent)
            VALUES (?, ?, ?, 1, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                city_name = excluded.city_name,
                interval = excluded.interval,
                is_active = 1
            """,
            (user_id, city_name, interval),
        )
        conn.commit()


def update_subscription_status(user_id: int, is_active: bool):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE subscriptions SET is_active = ? WHERE user_id = ?",
            (1 if is_active else 0, user_id),
        )
        conn.commit()


def increment_notification_count(user_id: int):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE subscriptions
            SET notifications_sent = notifications_sent + 1
            WHERE user_id = ?
            """,
            (user_id,),
        )
        conn.commit()


def get_subscriptions(active_only: bool = False):
    query = """
        SELECT user_id, city_name, interval, is_active, notifications_sent
        FROM subscriptions
    """
    params = ()
    if active_only:
        query += " WHERE is_active = 1"

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def get_subscription(user_id: int):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT user_id, city_name, interval, is_active, notifications_sent
            FROM subscriptions
            WHERE user_id = ?
            """,
            (user_id,),
        )
        return cursor.fetchone()


def save_to_db(city_name: str, weather_info: str):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO history (timestamp, city_name, weather_info)
            VALUES (?, ?, ?)
            """,
            (timestamp, city_name, weather_info),
        )
        conn.commit()


def get_weather_history(limit: int = 20):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, city_name, weather_info
            FROM history
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()


def check_tables():
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return cursor.fetchall()


def unsubscribe_user(user_id: int):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
        deleted_rows = cursor.rowcount
        conn.commit()
        return deleted_rows > 0

