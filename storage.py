# storage.py — saves the bot's records in a small database file (bridge.db).
#
# SQLite is a database that lives in one file. It comes with Python,
# so there is nothing to install. The file stays on your computer
# (it's listed in .gitignore, so it is never uploaded to GitHub).

import sqlite3
from datetime import date, datetime, timedelta
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
                status  TEXT                -- 'sent', 'done' or 'skipped'
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                logged_at TEXT,     -- date and time, Denver
                day       TEXT,     -- '2026-11-03'
                minutes   INTEGER,  -- how long (empty if you didn't say)
                category  TEXT,     -- 'coursework', 'portfolio', 'template' or 'other'
                summary   TEXT,     -- short tidy description
                original  TEXT      -- exactly what you typed
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


def set_daily_status(day, status):
    """Mark today's task 'done' or 'skipped' (creates a row if no ping was sent)."""
    with connect() as db:
        db.execute(
            "INSERT INTO daily_tasks (day, task, status) VALUES (?, NULL, ?) "
            "ON CONFLICT(day) DO UPDATE SET status = excluded.status",
            (day, status),
        )


def add_checkin(minutes, category, summary, original):
    now = now_denver()
    with connect() as db:
        db.execute(
            "INSERT INTO checkins (logged_at, day, minutes, category, summary, original) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (now.isoformat(timespec="minutes"), now.date().isoformat(), minutes, category, summary, original),
        )


def week_start(day=None):
    """The Monday of the week (weeks run Monday to Sunday)."""
    d = day or now_denver().date()
    return (d - timedelta(days=d.weekday())).isoformat()


def week_checkins(start=None):
    """All check-ins from Monday of this week until now (or a given week's Monday)."""
    start = start or week_start()
    end = (date.fromisoformat(start) + timedelta(days=7)).isoformat()
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM checkins WHERE day >= ? AND day < ? ORDER BY logged_at", (start, end)
        ).fetchall()
    return [dict(r) for r in rows]


def week_minutes(start=None):
    """Total minutes logged this week, and minutes per category."""
    total, by_category = 0, {}
    for c in week_checkins(start):
        m = c["minutes"] or 0
        total += m
        by_category[c["category"]] = by_category.get(c["category"], 0) + m
    return total, by_category
