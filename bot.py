# Bridge Bot — Alexander's helper for The Bridge Slack workspace.
#
# STEP 1: connects to Slack and can DM you.
# STEP 2: every day at 7:00am Denver time, DMs you ONE task for the day.
# STEP 3: understands check-ins ("did 30 min of module 4"), logs them, posts to #helm,
#         tracks weekly hours, and answers "what's next", "hours this week", "skip today".

import os
import random
import re

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

import brain
import storage

# Read the secret keys from the .env file (never written in the code itself).
load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]   # starts with xoxb-
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]   # starts with xapp-
MY_USER_ID = os.environ["MY_SLACK_USER_ID"]       # your Slack member ID, starts with U

MORNING_PING_HOUR = 7    # 7:00am Denver time
SHIFT_DAYS = ["Thursday", "Friday", "Saturday", "Sunday"]

# HARD RULE: the bot never posts here unless Alexander explicitly asks.
OFF_LIMITS_CHANNELS = ["design-studio"]

# Kinds of work that count as "done for today".
COUNTS_AS_DONE = ["coursework", "portfolio", "template"]

HELP_TEXT = """Here's what I understand:
• Tell me what you did, in your own words: “did 30 min of module 4”, “finished the cover page”
• *what's next*: today's task (or a bonus one if you're done)
• *hours this week*: your logged time since Monday
• *skip today*: take the day off, no stress
• *ping me*: send this morning's task again
Coming soon: *idea: ...* and *decision: ...*"""

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


def post_to_channel(channel_name, text, alexander_asked=False):
    """Post in a channel, e.g. post_to_channel("helm", "..."). Returns True if it worked.

    Safety: refuses #design-studio unless Alexander explicitly asked.
    """
    channel_name = channel_name.lstrip("#")
    if channel_name in OFF_LIMITS_CHANNELS and not alexander_asked:
        print(f"Blocked: not posting in #{channel_name} (off-limits).")
        return False

    channel_id = find_channel_id(channel_name)
    if not channel_id:
        dm_me(f"⚠️ I couldn't find #{channel_name}. Does it exist, and am I invited? "
              f"(In #{channel_name}, type: /invite @Bridge Bot)")
        return False
    try:
        app.client.chat_postMessage(channel=channel_id, text=text)
        return True
    except SlackApiError as error:
        if error.response.get("error") == "not_in_channel":
            dm_me(f"⚠️ I'm not in #{channel_name} yet, so I couldn't post there. "
                  f"Go to #{channel_name} and type: /invite @Bridge Bot")
        else:
            dm_me(f"⚠️ Couldn't post in #{channel_name}: {error.response.get('error')}")
        return False


_channel_ids = {}


def find_channel_id(channel_name):
    """Look up a channel's ID from its name (Slack needs the ID to post)."""
    if channel_name not in _channel_ids:
        cursor = None
        while True:
            result = app.client.conversations_list(
                types="public_channel,private_channel", exclude_archived=True,
                limit=200, cursor=cursor,
            )
            for ch in result["channels"]:
                _channel_ids[ch["name"]] = ch["id"]
            cursor = result.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
    return _channel_ids.get(channel_name)


def nice_time(minutes):
    """150 -> '2h 30m'."""
    hours, mins = divmod(minutes or 0, 60)
    if hours and mins:
        return f"{hours}h {mins}m"
    return f"{hours}h" if hours else f"{mins}m"


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
    # A simplified copy for matching commands: lowercase, no apostrophes or end punctuation.
    command = re.sub(r"[’'?!.]", "", text.lower()).strip()

    if command in ("help", "commands"):
        say(HELP_TEXT)
    elif command == "ping me":
        send_morning_ping(force=True)
    elif command in ("whats next", "what next", "next"):
        whats_next(say)
    elif command in ("hours this week", "hours", "my hours"):
        hours_this_week(say)
    elif command in ("skip today", "skip"):
        skip_today(say)
    elif command.startswith(("idea:", "decision:")):
        say("Ideas and decisions arrive in step 4, coming soon! I haven't saved this one yet.")
    else:
        handle_checkin_or_chat(text, say)


def handle_checkin_or_chat(text, say):
    """Use Claude to decide if this is a check-in. If yes, log it and post to #helm."""
    today = storage.get_daily_task(storage.today())
    todays_task = today["task"] if today else None

    meaning = brain.understand_message(text, todays_task)
    if meaning is None:
        say("Hmm, I couldn't reach Claude just now, so I didn't log that. "
            "Try again in a minute? (Type “help” to see what I can do.)")
        return

    if not meaning.is_checkin:
        say(meaning.reply)
        return

    storage.add_checkin(meaning.minutes, meaning.category, meaning.summary, text)
    if meaning.category in COUNTS_AS_DONE:
        storage.set_daily_status(storage.today(), "done")

    total, _ = storage.week_minutes()
    time_part = f" ({nice_time(meaning.minutes)})" if meaning.minutes else ""
    post_to_channel(
        "helm",
        f"✅ *Check-in* _(via chat)_: {meaning.summary}{time_part} · {meaning.category}\n"
        f"This week so far: {nice_time(total)}",
    )
    say(f"{meaning.reply}\n📒 Logged in #helm. This week: *{nice_time(total)}*.")


def whats_next(say):
    today = storage.get_daily_task(storage.today())
    if today and today["task"] and today["status"] == "sent":
        say(f"Today's one thing:\n👉 {today['task']}")
        return

    # Today's task is done or skipped (or none was sent): offer an optional bonus.
    weekday = storage.now_denver().strftime("%A")
    bonus = brain.suggest_daily_task(weekday in SHIFT_DAYS, weekday, read_focus(), storage.recent_tasks())
    if today and today["status"] == "done":
        intro = "You've already done today's thing 🙌 If you feel like more, here's a bonus:"
    else:
        intro = "Here's a good next step, only if you feel like it:"
    say(f"{intro}\n👉 {bonus or random.choice(BACKUP_TASKS['shift'])}")


def hours_this_week(say):
    total, by_category = storage.week_minutes()
    checkins = storage.week_checkins()
    if not checkins:
        say("Nothing logged yet this week (weeks start Monday). Tell me what you did anytime!")
        return
    lines = [f"⏱ *This week: {nice_time(total)}* across {len(checkins)} check-in(s)"]
    for category, minutes in sorted(by_category.items(), key=lambda x: -x[1]):
        if minutes:
            lines.append(f"• {category}: {nice_time(minutes)}")
    untimed = sum(1 for c in checkins if not c["minutes"])
    if untimed:
        lines.append(f"_(+ {untimed} check-in(s) with no time given)_")
    say("\n".join(lines))


def skip_today(say):
    today = storage.get_daily_task(storage.today())
    if today and today["status"] == "done":
        say("You already did today's thing ✅ No need to skip. Enjoy the rest of the day!")
        return
    storage.set_daily_status(storage.today(), "skipped")
    say("Skipped ✅ Rest is part of the plan. See you tomorrow morning.")


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
    dm_me("Hi Alexander! Bridge Bot is online. ✅ Type “help” to see what I can do.")
    print("Bridge Bot is running. Leave this window open. Press Ctrl+C to stop.")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
