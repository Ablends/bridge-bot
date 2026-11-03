# storage.py — saves the bot's records in a small database file (bridge.db).
#
# SQLite is a database that lives in one file. It comes with Python,
# so there is nothing to install. The file stays on your computer
# (it's listed in .gitignore, so it is never uploaded to GitHub).

import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

DB_FILE = "bridge.db"
DENVER = ZoneInfo("America/Denver")


def now_denver():
    """The current date and time in Alexander's time zone."""
    return datetime.now(DENVER)


def today():
    """Today's date in Denver, as text like '2026-11-03'."""
    return now_denver().date().isoformat()


def connect():
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row  # lets us read columns by name
    return db


def setup():
    """Create the tables the first time the bot runs."""
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS daily_tasks (
                day     TEXT PRIMARY KEY,   -- '2026-11-03'
                task    TEXT,               -- the one task the bot suggested
                status  TEXT                -- 'sent', later: 'done' or 'skipped'
            )
        """)


def save_daily_task(day, task):
    with connect() as db:
        db.execute(
            "INSERT OR REPLACE INTO daily_tasks (day, task, status) VALUES (?, ?, 'sent')",
            (day, task),
        )


def get_daily_task(day):
    with connect() as db:
        return db.execute("SELECT * FROM daily_tasks WHERE day = ?", (day,)).fetchone()


def recent_tasks(limit=7):
    """The last few suggested tasks, newest first (so the bot doesn't repeat itself)."""
    with connect() as db:
        rows = db.execute(
            "SELECT day, task, status FROM daily_tasks ORDER BY day DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
