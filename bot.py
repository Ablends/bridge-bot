# Bridge Bot — Alexander's helper for The Bridge Slack workspace.
#
# STEP 1: connects to Slack and can DM you.
# STEP 2: every day at 7:00am Denver time, DMs you ONE task for the day.
# More features get added step by step.

import os
import random

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import brain
import storage

# Read the secret keys from the .env file (never written in the code itself).
load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]   # starts with xoxb-
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]   # starts with xapp-
MY_USER_ID = os.environ["MY_SLACK_USER_ID"]       # your Slack member ID, starts with U

MORNING_PING_HOUR = 7    # 7:00am Denver time
SHIFT_DAYS = ["Thursday", "Friday", "Saturday", "Sunday"]

# Used only if Claude can't be reached, so you still get a task.
BACKUP_TASKS = {
    "shift": [
        "Watch one short lesson video from your Coursera course (~5 min).",
        "Write 3 bullet points about one problem Fernly solves (~5 min).",
        "Jot down one idea for the portfolio template's cover page (~5 min).",
    ],
    "progress": [
        "Work through the next Coursera module and take notes (~90 min).",
        "Draft the 'problem & research' section of one case study (~90 min).",
        "Build one new page of the Figma portfolio template (~90 min).",
    ],
}

app = App(token=SLACK_BOT_TOKEN)


def dm_me(text):
    """Send Alexander a direct message from the bot."""
    app.client.chat_postMessage(channel=MY_USER_ID, text=text)


def read_focus():
    """Read my-focus.txt (what Alexander is working on right now)."""
    try:
        with open("my-focus.txt", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "(no focus file found)"


def send_morning_ping(force=False):
    """Pick today's ONE task and DM it. Runs at 7am, or when you type 'ping me'."""
    day = storage.today()
    if storage.get_daily_task(day) and not force:
        print(f"Morning ping already sent for {day}, skipping.")
        return

    weekday = storage.now_denver().strftime("%A")
    is_shift_day = weekday in SHIFT_DAYS

    task = brain.suggest_daily_task(is_shift_day, weekday, read_focus(), storage.recent_tasks())
    if not task:
        task = random.choice(BACKUP_TASKS["shift" if is_shift_day else "progress"])

    storage.save_daily_task(day, task)

    if is_shift_day:
        header = f"☀️ Morning! It's {weekday}, a shift day, so just one tiny thing:"
    else:
        header = f"☀️ Morning! It's {weekday}, a progress day. Today's one thing:"
    dm_me(f"{header}\n\n👉 {task}\n\nReply here when you've done it (or say “skip today”, no stress).")
    print(f"Sent morning ping for {day}: {task}")


@app.event("message")
def handle_message(event, say):
    # Show in the PowerShell window that a message arrived (handy for spotting problems).
    print(f"Message received: type={event.get('channel_type')} from={event.get('user')}")

    # Only listen to direct messages...
    if event.get("channel_type") != "im":
        return
    # ...that come from you (not from the bot itself, and not edits/deletes).
    if event.get("user") != MY_USER_ID or event.get("bot_id") or event.get("subtype"):
        return

    text = event.get("text", "").strip()

    # Test command: send the morning ping right now instead of waiting for 7am.
    if text.lower() == "ping me":
        send_morning_ping(force=True)
        return

    say(f"Got it 👋 You said: “{text}”. (Logging check-ins comes in step 3. "
        f"For now, try typing “ping me”.)")


def start_scheduler():
    """Set up the daily 7am timer (Denver time)."""
    scheduler = BackgroundScheduler(timezone=storage.DENVER)
    scheduler.add_job(
        send_morning_ping,
        CronTrigger(hour=MORNING_PING_HOUR, minute=0, timezone=storage.DENVER),
        misfire_grace_time=3 * 60 * 60,  # if the computer was asleep at 7am, still send it within 3 hours
        coalesce=True,
    )
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    print("Starting Bridge Bot...")
    storage.setup()
    start_scheduler()
    dm_me("Hi Alexander! Bridge Bot is online. ✅ Type “ping me” to test the morning message.")
    print("Bridge Bot is running. Leave this window open. Press Ctrl+C to stop.")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
