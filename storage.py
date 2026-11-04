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
        db.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                question       TEXT,
                opened_at      TEXT,    -- when you asked
                dm_ts          TEXT,    -- Slack ID of the bot's DM about it (its thread)
                status         TEXT,    -- 'open', 'suggested' or 'decided'
                suggested_pick TEXT,    -- the bot's default suggestion (never final on its own)
                suggested_at   TEXT,
                suggestion_ts  TEXT,    -- Slack ID of the suggestion DM (you react ✅ to it)
                answer         TEXT,    -- YOUR final answer
                decided_at     TEXT
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS recaps (
                week_start TEXT PRIMARY KEY,  -- Monday of the week the recap covers
                posted_at  TEXT,
                main_goal  TEXT              -- the suggested goal for the following week
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                title      TEXT,
                body       TEXT,
                original   TEXT
            )
        """)
        # Added later: remembers which Slack message was the morning ping,
        # so tapping ✅ or ❌ on it counts as a check-in.
        columns = [row["name"] for row in db.execute("PRAGMA table_info(daily_tasks)")]
        if "ping_ts" not in columns:
            db.execute("ALTER TABLE daily_tasks ADD COLUMN ping_ts TEXT")


def save_ping_ts(day, ping_ts):
    """Remember the Slack ID of the morning ping message."""
    with connect() as db:
        db.execute("UPDATE daily_tasks SET ping_ts = ? WHERE day = ?", (ping_ts, day))


def find_daily_task_by_ping(ping_ts):
    """Find the day whose morning ping has this Slack message ID."""
    with connect() as db:
        row = db.execute("SELECT * FROM daily_tasks WHERE ping_ts = ?", (ping_ts,)).fetchone()
    return dict(row) if row else None


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


# ---------- Step 4: decisions and ideas ----------

def add_decision(question):
    with connect() as db:
        cur = db.execute(
            "INSERT INTO decisions (question, opened_at, status) VALUES (?, ?, 'open')",
            (question, now_denver().isoformat(timespec="minutes")),
        )
        return cur.lastrowid


def update_decision(decision_id, **fields):
    """Change some fields of a decision, e.g. update_decision(3, status='decided')."""
    columns = ", ".join(f"{name} = ?" for name in fields)
    with connect() as db:
        db.execute(f"UPDATE decisions SET {columns} WHERE id = ?", (*fields.values(), decision_id))


def get_decision(decision_id):
    with connect() as db:
        row = db.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,)).fetchone()
    return dict(row) if row else None


def find_decision_by_message(ts):
    """Find the decision whose DM (or suggestion DM) has this Slack message ID."""
    with connect() as db:
        row = db.execute(
            "SELECT * FROM decisions WHERE dm_ts = ? OR suggestion_ts = ?", (ts, ts)
        ).fetchone()
    return dict(row) if row else None


def open_decisions():
    """Decisions you haven't answered yet (including ones with a suggested default)."""
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM decisions WHERE status != 'decided' ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


def decisions_needing_default(days=3):
    """Open decisions older than `days` that haven't had a suggested default yet."""
    cutoff = (now_denver() - timedelta(days=days)).isoformat(timespec="minutes")
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM decisions WHERE status = 'open' AND suggested_at IS NULL AND opened_at <= ?",
            (cutoff,),
        ).fetchall()
    return [dict(r) for r in rows]


def add_idea(title, body, original):
    with connect() as db:
        db.execute(
            "INSERT INTO ideas (created_at, title, body, original) VALUES (?, ?, ?, ?)",
            (now_denver().isoformat(timespec="minutes"), title, body, original),
        )



# ---------- Step 5: weekly recap ----------

def last_week_start():
    """Monday of LAST week."""
    return week_start(now_denver().date() - timedelta(days=7))


def _week_range(start):
    end = (date.fromisoformat(start) + timedelta(days=7)).isoformat()
    return start, end


def week_daily_tasks(start):
    start, end = _week_range(start)
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM daily_tasks WHERE day >= ? AND day < ? ORDER BY day", (start, end)
        ).fetchall()
    return [dict(r) for r in rows]


def week_decided(start):
    """Decisions that were made during that week."""
    start, end = _week_range(start)
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM decisions WHERE status = 'decided' AND decided_at >= ? AND decided_at < ?",
            (start, end),
        ).fetchall()
    return [dict(r) for r in rows]


def week_ideas(start):
    start, end = _week_range(start)
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM ideas WHERE created_at >= ? AND created_at < ?", (start, end)
        ).fetchall()
    return [dict(r) for r in rows]


def get_recap(week):
    with connect() as db:
        row = db.execute("SELECT * FROM recaps WHERE week_start = ?", (week,)).fetchone()
    return dict(row) if row else None


def save_recap(week, main_goal):
    with connect() as db:
        db.execute(
            "INSERT OR REPLACE INTO recaps (week_start, posted_at, main_goal) VALUES (?, ?, ?)",
            (week, now_denver().isoformat(timespec="minutes"), main_goal),
        )


def current_goal():
    """The main goal suggested in the most recent recap (or None)."""
    with connect() as db:
        row = db.execute(
            "SELECT main_goal FROM recaps WHERE week_start >= ? ORDER BY week_start DESC LIMIT 1",
            (last_week_start(),),
        ).fetchone()
    return row["main_goal"] if row else None


def set_goal(goal):
    """Alexander chose their own main goal for this week."""
    with connect() as db:
        db.execute(
            "INSERT INTO recaps (week_start, posted_at, main_goal) VALUES (?, NULL, ?) "
            "ON CONFLICT(week_start) DO UPDATE SET main_goal = excluded.main_goal",
            (last_week_start(), goal),
        )
