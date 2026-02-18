import sqlite3
import os
import datetime
from typing import Optional

class Database:
    def __init__(self, db_path: str = ".tmp/overseer.db"):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self):
        dirname = os.path.dirname(self.db_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_usage (
                    date TEXT PRIMARY KEY,
                    seconds_used INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def get_usage(self, date_str: Optional[str] = None) -> int:
        if date_str is None:
            date_str = datetime.date.today().isoformat()
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT seconds_used FROM daily_usage WHERE date = ?", (date_str,))
            row = cursor.fetchone()
            return row[0] if row else 0

    def increment_usage(self, seconds: int = 1, date_str: Optional[str] = None):
        if date_str is None:
            date_str = datetime.date.today().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO daily_usage (date, seconds_used)
                VALUES (?, ?)
                ON CONFLICT(date) DO UPDATE SET seconds_used = seconds_used + ?
            """, (date_str, seconds, seconds))
            conn.commit()

    def reset_usage(self, date_str: Optional[str] = None):
        if date_str is None:
            date_str = datetime.date.today().isoformat()
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE daily_usage SET seconds_used = 0 WHERE date = ?", (date_str,))
            conn.commit()
