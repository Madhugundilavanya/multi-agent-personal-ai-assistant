import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "progress.db"


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DB_PATH), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    return connection


def add_progress(topic: str, notes: str) -> dict:
    connection = connect()
    try:
        with connection:
            cursor = connection.execute(
                "INSERT INTO progress (topic, notes) VALUES (?, ?)",
                (topic, notes),
            )
            record = connection.execute(
                "SELECT * FROM progress WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return dict(record)
    finally:
        connection.close()


def list_progress() -> list[dict]:
    connection = connect()
    try:
        records = connection.execute(
            "SELECT * FROM progress ORDER BY id DESC"
        ).fetchall()
        return [dict(record) for record in records]
    finally:
        connection.close()
