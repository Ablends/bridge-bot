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
        # Added later: small saved values, e.g. where Alexander is in class.
        db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                name       TEXT PRIMARY KEY,  -- e.g. 'class_status', 'template_step'
                value      TEXT,
                updated_at TEXT
            )
        """)
        # Added later: remembers which Slack message was the morning ping,
        # so tapping ✅ or ❌ on it counts as a check-in.
        columns = [row["name"] for row in db.execute("PRAGMA table_info(daily_tasks)")]
        if "ping_ts" not in columns:
            db.execute("ALTER TABLE daily_tasks ADD COLUMN ping_ts TEXT")
        # Added later: the 8pm "did it happen?" message, which also takes ✅ / ❌.
        if "nudge_ts" not in columns:
            db.execute("ALTER TABLE daily_tasks ADD COLUMN nudge_ts TEXT")
        # Added later: the "how long?" question after a ✅ tap, so a time tap can find its check-in.
        checkin_columns = [row["name"] for row in db.execute("PRAGMA table_info(checkins)")]
        if "time_ts" not in checkin_columns:
            db.execute("ALTER TABLE checkins ADD COLUMN time_ts TEXT")
        # Added later: SEVERAL tasks per day (the old daily_tasks table held only one).
        # Each task is its own row, with its own ✅ / ❌ messages.
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                day        TEXT,     -- the day it was on the list, '2026-11-03'
                task       TEXT,
                status     TEXT,     -- 'sent' (open), 'done', 'skipped' (not today),
                                     -- 'dropped' (never mind), 'carried' (moved to a later day)
                origin_day TEXT      -- the FIRST day it was given (same as day unless carried over)
            )
        """)
        # Which Slack messages belong to which task, so a ✅ / ❌ tap on any of them finds it.
        db.execute("""
            CREATE TABLE IF NOT EXISTS task_messages (
                ts      TEXT PRIMARY KEY,  -- Slack ID of the message
                task_id INTEGER,
                kind    TEXT               -- 'morning' or 'evening'
            )
        """)
        # One time only: copy the old one-task-a-day history across, so recaps and the log
        # keep working. The old table is left exactly as it was.
        already = db.execute("SELECT value FROM settings WHERE name = 'multi_task_start'").fetchone()
        if not already:
            for old in db.execute("SELECT * FROM daily_tasks WHERE task IS NOT NULL ORDER BY day").fetchall():
                cur = db.execute(
                    "INSERT INTO tasks (day, task, status, origin_day) VALUES (?, ?, ?, ?)",
                    (old["day"], old["task"], old["status"], old["day"]),
                )
                for ts, kind in ((old["ping_ts"], "morning"), (old["nudge_ts"], "evening")):
                    if ts:
                        db.execute(
                            "INSERT OR REPLACE INTO task_messages (ts, task_id, kind) VALUES (?, ?, ?)",
                            (ts, cur.lastrowid, kind),
                        )
            # Tasks missed BEFORE the day before this upgrade stay in the past (no flood of old ones).
            start = (now_denver().date() - timedelta(days=1)).isoformat()
            db.execute(
                "INSERT INTO settings (name, value, updated_at) VALUES ('multi_task_start', ?, ?)",
                (start, now_denver().date().isoformat()),
            )


def get_setting(name, default=None):
    """Read a saved value. Returns (value, updated_at), or (default, None) if never set."""
    with connect() as db:
        row = db.execute("SELECT value, updated_at FROM settings WHERE name = ?", (name,)).fetchone()
    return (row["value"], row["updated_at"]) if row else (default, None)


def set_setting(name, value):
    with connect() as db:
        db.execute(
            "INSERT OR REPLACE INTO settings (name, value, updated_at) VALUES (?, ?, ?)",
            (name, str(value), now_denver().date().isoformat()),
        )


def recent_checkins(days=7):
    """Check-ins from the last few days, oldest first (so the bot knows where you are)."""
    since = (now_denver().date() - timedelta(days=days)).isoformat()
    with connect() as db:
        rows = db.execute(
            "SELECT day, summary FROM checkins WHERE day >= ? ORDER BY logged_at", (since,)
        ).fetchall()
    return [dict(r) for r in rows]


# ---------- Daily tasks (several per day) ----------

OPEN = "sent"                      # on the list, no answer yet
NOT_FINISHED = ("sent", "skipped")  # these come back tomorrow


def add_task(day, task, origin_day=None):
    """Put a task on a day's list. Returns its id."""
    with connect() as db:
        cur = db.execute(
            "INSERT INTO tasks (day, task, status, origin_day) VALUES (?, ?, 'sent', ?)",
            (day, task, origin_day or day),
        )
        return cur.lastrowid


def get_task(task_id):
    with connect() as db:
        row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row) if row else None


def tasks_for_day(day):
    """Everything on a day's list, in the order it was sent (carried-over ones first)."""
    with connect() as db:
        rows = db.execute("SELECT * FROM tasks WHERE day = ? ORDER BY id", (day,)).fetchall()
    return [dict(r) for r in rows]


def open_tasks(day):
    """Tasks on a day's list with no ✅ / ❌ yet."""
    return [t for t in tasks_for_day(day) if t["status"] == OPEN]


def set_task_status(task_id, status):
    with connect() as db:
        db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))


def save_task_message(task_id, ts, kind):
    """Remember that this Slack message ('morning' or 'evening') is about this task."""
    with connect() as db:
        db.execute(
            "INSERT OR REPLACE INTO task_messages (ts, task_id, kind) VALUES (?, ?, ?)", (ts, task_id, kind)
        )


def find_task_by_message(ts):
    """Find the task a Slack message is about. Returns (task, kind), or (None, None)."""
    with connect() as db:
        row = db.execute("SELECT task_id, kind FROM task_messages WHERE ts = ?", (ts,)).fetchone()
    if not row:
        return None, None
    return get_task(row["task_id"]), row["kind"]


def current_copy(task):
    """If a task was carried over to a later day, the newest copy of it (else the task itself)."""
    if task["status"] != "carried":
        return task
    with connect() as db:
        row = db.execute(
            "SELECT * FROM tasks WHERE origin_day = ? AND task = ? AND id > ? AND status != 'carried' "
            "ORDER BY id DESC LIMIT 1",
            (task["origin_day"], task["task"], task["id"]),
        ).fetchone()
    return dict(row) if row else task


def carry_over_to(day):
    """Move every unfinished task from earlier days onto `day`'s list.

    The old row is marked 'carried' (so it is never carried twice) and a fresh open copy is
    made for `day`, remembering the first day it was given. Returns the new rows, oldest first.
    """
    start, _ = get_setting("multi_task_start", "0000-00-00")
    with connect() as db:
        old = db.execute(
            "SELECT * FROM tasks WHERE day < ? AND day >= ? AND status IN ('sent', 'skipped') ORDER BY origin_day, id",
            (day, start),
        ).fetchall()
        new_ids = []
        for row in old:
            db.execute("UPDATE tasks SET status = 'carried' WHERE id = ?", (row["id"],))
            cur = db.execute(
                "INSERT INTO tasks (day, task, status, origin_day) VALUES (?, ?, 'sent', ?)",
                (day, row["task"], row["origin_day"] or row["day"]),
            )
            new_ids.append(cur.lastrowid)
    return [get_task(i) for i in new_ids]


def recent_tasks(limit=10):
    """The last few tasks, newest first (so the bot doesn't repeat itself)."""
    with connect() as db:
        rows = db.execute(
            "SELECT day, task, status FROM tasks WHERE status != 'carried' ORDER BY day DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def add_checkin(minutes, category, summary, original):
    """Save a check-in. Returns its id."""
    now = now_denver()
    with connect() as db:
        cur = db.execute(
            "INSERT INTO checkins (logged_at, day, minutes, category, summary, original) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (now.isoformat(timespec="minutes"), now.date().isoformat(), minutes, category, summary, original),
        )
        return cur.lastrowid


def save_checkin_time_ts(checkin_id, ts):
    """Remember which Slack message asks "how long?" for this check-in."""
    with connect() as db:
        db.execute("UPDATE checkins SET time_ts = ? WHERE id = ?", (ts, checkin_id))


def find_checkin_by_time_ts(ts):
    with connect() as db:
        row = db.execute("SELECT * FROM checkins WHERE time_ts = ?", (ts,)).fetchone()
    return dict(row) if row else None


def set_checkin_minutes(checkin_id, minutes):
    with connect() as db:
        db.execute("UPDATE checkins SET minutes = ? WHERE id = ?", (minutes, checkin_id))


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


def week_tasks(start):
    """Each task that was on a list that week, once, as it stood when the week ended.

    A task carried over from day to day is one task, not several. If it was still unfinished
    when the week ended (carried into the next week), its status here is 'sent'.
    """
    start, end = _week_range(start)
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM tasks WHERE day >= ? AND day < ? ORDER BY id", (start, end)
        ).fetchall()
    last = {}
    for row in rows:
        last[(row["origin_day"], row["task"])] = dict(row)  # later rows replace earlier copies
    tasks = sorted(last.values(), key=lambda t: t["id"])
    for t in tasks:
        if t["status"] == "carried":
            t["status"] = "sent"
    return tasks


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
