# Orbital Bot — Alexander's helper for The Bridge Slack workspace.
#
# STEP 1: connects to Slack and can DM you.
# STEP 2: every day at 7:00am Denver time, DMs you ONE task for the day.
# STEP 3: understands check-ins ("did 30 min of module 4"), logs them, posts to #helm,
#         tracks weekly hours, and answers "what's next", "hours this week", "skip today".
# STEP 4: "idea: ..." goes to #ideas, tidied. "decision: ..." is logged in #helm; after 3 days
#         with no answer, the bot suggests a default, which only counts once you react ✅.
# STEP 5: every Monday at 7:05am, posts last week's recap in #ship-log with one suggested goal.

import os
import random
import re
from datetime import date, timedelta

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
EVENING_CHECKIN_HOUR = 20  # 8:00pm Denver time: "did today's task happen?" (only if no check-in yet)
SHIFT_DAYS = ["Thursday", "Friday", "Saturday", "Sunday"]

# HARD RULE: the bot never posts here unless Alexander explicitly asks.
OFF_LIMITS_CHANNELS = ["design-studio"]

DECISION_CHECK_HOUR = 9  # each morning at 9am, look for decisions open 3+ days
DEFAULT_AFTER_DAYS = 3
RECAP_DAY, RECAP_HOUR, RECAP_MINUTE = "mon", 7, 5  # Monday 7:05am, right after the morning task
# One-tap time after ✅: these number buttons go under the "how long?" question.
TIME_REACTIONS = {"one": 15, "two": 30, "three": 60, "four": 120}

YES_REACTIONS = ["white_check_mark", "heavy_check_mark", "ballot_box_with_check", "+1", "thumbsup"]
NO_REACTIONS = ["x", "negative_squared_cross_mark", "-1", "thumbsdown"]

# The fixed build path for the Figma portfolio template. Never reorder or skip.
# "step done" moves to the next one.
TEMPLATE_STEPS = [
    "Set up the pages (Cover, Foundations, Components, Desktop, Mobile, Archive) and move the Oct 17 home wireframe onto Desktop",
    "Foundations: colors, fonts, text styles, spacing",
    "Components: buttons, cards, nav, footer, with auto layout",
    "Desktop: home page (finish the Oct 17 wireframe with the components)",
    "Desktop: work overview page",
    "Desktop: one case study page (problem → research → process → solution → outcome)",
    "Desktop: about and contact",
    "Mobile: adapt each screen to phone width",
    "Tidy the file and name layers, ready for Framer",
]

# Kinds of work that count as "done for today".
COUNTS_AS_DONE = ["coursework", "portfolio", "template"]

HELP_TEXT = """Here's what I understand:
• Tap ✅ on the morning task when it's done, or ❌ to skip. No typing needed.
  If you haven't checked in by 8pm, I'll ask once. Anything not done is first up the next day.
• *class: ...*: tell me where you are in class, e.g. “class: on module 4 quiz” (*class* shows it)
• *step done*: you finished the current portfolio template step, move to the next (*step* shows it)
• Tell me what you did, in your own words: “did 30 min of module 4”, “finished the cover page”
• *what's next*: today's task (or a bonus one if you're done)
• *log*: everything you did this week, with times
• *hours this week*: your logged time since Monday
• *skip today*: take the day off, no stress
• *idea: ...*: tidied up and posted to #ideas
• *decision: ...*: logged in #helm. Answer by replying in the thread I start
• *decisions*: list the ones still open
• *decide 3: your answer*: answer decision #3 without using the thread
• *goal: ...*: set your own main goal for the week (or *goal* to see it)
• *recap preview*: DM me a recap of this week so far (not posted anywhere)
• *post recap*: post last week's recap to #ship-log now
• *ping me*: send this morning's task again"""

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


def dm_me(text, thread_ts=None):
    """Send Alexander a direct message from the bot. Returns the message's Slack ID."""
    result = app.client.chat_postMessage(channel=MY_USER_ID, text=text, thread_ts=thread_ts)
    return result["ts"]


def post_to_channel(channel_name, text, alexander_asked=False):
    """Post in a channel, e.g. post_to_channel("helm", "..."). Returns True if it worked.

    Safety: refuses #design-studio unless Alexander explicitly asked.
    """
    channel_name = channel_name.lstrip("#")
    if channel_name in OFF_LIMITS_CHANNELS and not alexander_asked:
        print(f"Blocked: not posting in #{channel_name} (off-limits).")
        return False

    try:
        channel_id = find_channel_id(channel_name)
    except SlackApiError as error:
        problem = error.response.get("error")
        dm_me(f"⚠️ I couldn't look up #{channel_name} (Slack said: `{problem}`).")
        print(f"Channel lookup failed: {problem} {error.response.data}")
        return False
    if not channel_id:
        dm_me(f"⚠️ I couldn't find #{channel_name}. Does it exist, and am I invited? "
              f"(In #{channel_name}, type: /invite @Orbital Bot)")
        return False
    try:
        app.client.chat_postMessage(channel=channel_id, text=text)
        return True
    except SlackApiError as error:
        if error.response.get("error") == "not_in_channel":
            dm_me(f"⚠️ I'm not in #{channel_name} yet, so I couldn't post there. "
                  f"Go to #{channel_name} and type: /invite @Orbital Bot")
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
    """What Alexander is working on: my-focus.txt, plus what he's told the bot lately."""
    try:
        with open("my-focus.txt", encoding="utf-8") as f:
            focus = f.read()
    except FileNotFoundError:
        focus = "(no focus file found)"

    class_status, class_date = storage.get_setting("class_status")
    step = current_step()
    recent = storage.recent_checkins()
    lines = ["", "LATEST FROM ALEXANDER (newer than the file above, so trust this first)"]
    if class_status:
        lines.append(f"- Where I am in class (told the bot on {class_date}): {class_status}")
    if step <= len(TEMPLATE_STEPS):
        lines.append(f"- Portfolio template: CURRENT STEP {step} of {len(TEMPLATE_STEPS)}: "
                     f"{TEMPLATE_STEPS[step - 1]}. Only suggest work on this step.")
    else:
        lines.append("- Portfolio template: all 9 build steps are done.")
    lines.append("- Recent check-ins (what I actually did):")
    lines += [f"  - {c['day']}: {c['summary']}" for c in recent] or ["  - none in the last week"]
    return focus + "\n".join(lines)


def current_step():
    """The portfolio template step Alexander is on (1-9; 10 means all done)."""
    value, _ = storage.get_setting("template_step", "1")
    return int(value)


def step_done(say):
    step = current_step()
    if step > len(TEMPLATE_STEPS):
        say("All 9 template steps are already done 🎉")
        return
    finished = TEMPLATE_STEPS[step - 1]
    storage.set_setting("template_step", step + 1)
    storage.add_checkin(None, "template", f"Finished template step {step}: {finished}", "step done")
    storage.set_daily_status(storage.today(), "done")
    post_to_channel("helm", f"🧱 *Template step {step} of {len(TEMPLATE_STEPS)} done* _(via chat)_: {finished}")
    if step < len(TEMPLATE_STEPS):
        say(f"🧱 Step {step} done! Logged in #helm.\nNext up, *step {step + 1}*: {TEMPLATE_STEPS[step]}")
    else:
        say("🎉 That was the last step. The template build is DONE. Logged in #helm.")


def show_step(say):
    step = current_step()
    if step > len(TEMPLATE_STEPS):
        say("All 9 template steps are done 🎉")
    else:
        say(f"🧱 You're on *step {step} of {len(TEMPLATE_STEPS)}*: {TEMPLATE_STEPS[step - 1]}\n"
            "Type “step done” when it's finished.")


def send_morning_ping(force=False):
    """Pick today's ONE task and DM it. Runs at 7am, or when you type 'ping me'."""
    day = storage.today()
    if storage.get_daily_task(day) and not force:
        print(f"Morning ping already sent for {day}, skipping.")
        return

    weekday = storage.now_denver().strftime("%A")
    is_shift_day = weekday in SHIFT_DAYS

    task = brain.suggest_daily_task(
        is_shift_day, weekday, read_focus(), storage.recent_tasks(), storage.current_goal()
    )
    if not task:
        task = random.choice(BACKUP_TASKS["shift" if is_shift_day else "progress"])

    storage.save_daily_task(day, task)

    if is_shift_day:
        header = f"☀️ Morning! It's {weekday}, a shift day, so just one tiny thing:"
    else:
        header = f"☀️ Morning! It's {weekday}, a progress day. Today's one thing:"
    ping_ts = dm_me(
        f"{header}\n\n👉 {task}\n\n"
        "Tap ✅ below when it's done, or ❌ to skip today (no stress). "
        "Want to log how long it took? Just type it, e.g. “did 30 min”."
    )
    storage.save_ping_ts(day, ping_ts)
    add_buttons(ping_ts)
    print(f"Sent morning ping for {day}: {task}")


def add_buttons(message_ts):
    """Add ✅ and ❌ under a message so checking in is one tap."""
    for emoji in ("white_check_mark", "x"):
        try:
            app.client.reactions_add(channel=dm_channel_id(), timestamp=message_ts, name=emoji)
        except SlackApiError as error:
            print(f"Couldn't add the {emoji} button: {error.response.get('error')}")


def send_evening_checkin():
    """8pm: if today's task has no check-in yet, ask (one tap) whether it happened."""
    day = storage.today()
    daily = storage.get_daily_task(day)
    if not daily or not daily["task"] or daily["status"] != "sent":
        print(f"Evening check-in not needed for {day}.")
        return
    nudge_ts = dm_me(
        f"🌙 Did today's task happen?\n\n👉 {daily['task']}\n\n"
        "Tap ✅ if it's done, ❌ if not. No stress either way."
    )
    storage.save_nudge_ts(day, nudge_ts)
    add_buttons(nudge_ts)
    print(f"Sent evening check-in for {day}.")


_dm_channel = {}


def dm_channel_id():
    """The ID of the DM conversation with Alexander (Slack needs it to add reactions)."""
    if "id" not in _dm_channel:
        _dm_channel["id"] = app.client.conversations_open(users=MY_USER_ID)["channel"]["id"]
    return _dm_channel["id"]


def tap_checkin(daily, reaction, message_ts):
    """Alexander tapped ✅ or ❌ on a morning ping or evening check-in."""
    evening = message_ts == daily.get("nudge_ts")
    if reaction in YES_REACTIONS:
        if daily["status"] == "done":
            return  # already counted, ignore a second tap
        storage.set_daily_status(daily["day"], "done")
        summary = f"Did the daily task: {daily['task']}"
        checkin_id = storage.add_checkin(None, guess_category(daily["task"]), summary, "(tapped ✅)")
        posted = post_to_channel("helm", f"✅ *Check-in* _(one tap)_: {summary}")
        where = "Logged in #helm" if posted else "Saved (but not posted to #helm, see the warning above)"
        ask_ts = dm_me(
            f"🙌 Nice, marked done. {where}.\n⏱️ How long did it take? Tap one: "
            "1️⃣ 15 min · 2️⃣ 30 min · 3️⃣ 1 hour · 4️⃣ 2 hours",
            thread_ts=message_ts,
        )
        storage.save_checkin_time_ts(checkin_id, ask_ts)
        for emoji in TIME_REACTIONS:
            try:
                app.client.reactions_add(channel=dm_channel_id(), timestamp=ask_ts, name=emoji)
            except SlackApiError as error:
                print(f"Couldn't add the {emoji} button: {error.response.get('error')}")
    elif reaction in NO_REACTIONS:
        if daily["status"] != "sent":
            return  # already done or skipped
        storage.set_daily_status(daily["day"], "skipped")
        if evening:
            dm_me("No problem 👍 It'll be first up tomorrow morning.", thread_ts=message_ts)
        else:
            dm_me("Skipped ✅ Rest is part of the plan. It'll be first up tomorrow.", thread_ts=message_ts)


@app.event("message")
def handle_message(event, say):
    try:
        respond_to_message(event, say)
    except Exception as error:
        # If anything breaks, tell Alexander in Slack instead of failing silently.
        print(f"Error while handling a message: {error!r}")
        say(f"⚠️ Something went wrong on my side: `{error}`\n"
            "Copy this message to Claude (your coding helper) and we'll fix it.")


def respond_to_message(event, say):
    # Show in the PowerShell window that a message arrived (handy for spotting problems).
    print(f"Message received: type={event.get('channel_type')} from={event.get('user')}")

    # Only listen to direct messages...
    if event.get("channel_type") != "im":
        return
    # ...that come from you (not from the bot itself, and not edits/deletes).
    if event.get("user") != MY_USER_ID or event.get("bot_id") or event.get("subtype"):
        return

    text = event.get("text", "").strip()

    # A reply inside the thread of a decision DM is your answer to that decision.
    thread_ts = event.get("thread_ts")
    if thread_ts and thread_ts != event.get("ts"):
        decision = storage.find_decision_by_message(thread_ts)
        if decision:
            record_answer(decision, text)
            return

    # A simplified copy for matching commands: lowercase, no apostrophes or end punctuation.
    command = re.sub(r"[’'?!.]", "", text.lower()).strip()

    if command in ("help", "commands"):
        say(HELP_TEXT)
    elif command == "ping me":
        send_morning_ping(force=True)
    elif command in ("whats next", "what next", "next"):
        whats_next(say)
    elif command in ("log", "my log", "what did i do", "this week", "week log"):
        show_log(say)
    elif command in ("hours this week", "hours", "my hours"):
        hours_this_week(say)
    elif command in ("skip today", "skip"):
        skip_today(say)
    elif command.startswith("idea:"):
        handle_idea(text.split(":", 1)[1].strip(), say)
    elif command.startswith("decision:"):
        open_decision(text.split(":", 1)[1].strip(), say)
    elif command in ("decisions", "open decisions"):
        list_decisions(say)
    elif re.match(r"decide #?\d+", command):
        number, answer = re.match(r"decide #?(\d+)\s*:?\s*(.*)", text, re.IGNORECASE | re.DOTALL).groups()
        decision = storage.get_decision(int(number))
        if not decision:
            say(f"I can't find decision #{number}. Type “decisions” to see the open ones.")
        elif not answer.strip():
            say(f"What's your answer for #{number}? e.g. “decide {number}: go with option A”")
        else:
            record_answer(decision, answer.strip())
    elif command.startswith("goal:"):
        goal = text.split(":", 1)[1].strip()
        storage.set_goal(goal)
        say(f"🎯 Got it. This week's main goal: *{goal}*. I'll lean the morning tasks toward it.")
    elif command in ("goal", "my goal"):
        goal = storage.current_goal()
        say(f"🎯 This week's main goal: *{goal}*" if goal else "No goal set yet. Type “goal: ...” to set one.")
    elif command.startswith("class:"):
        status = text.split(":", 1)[1].strip()
        if not status:
            say("Where are you in class? e.g. “class: on module 4 quiz”")
        else:
            storage.set_setting("class_status", status)
            say(f"📚 Got it, you're at: *{status}*. I'll pick tasks from there.")
    elif command in ("class", "my class"):
        status, when = storage.get_setting("class_status")
        say(f"📚 Last you told me ({when}): *{status}*" if status
            else "You haven't told me yet. Type “class: ...”, e.g. “class: on module 4 quiz”")
    elif command in ("step done", "step finished", "done with step"):
        step_done(say)
    elif command in ("step", "my step", "what step"):
        show_step(say)
    elif re.fullmatch(r"step \d+", command):
        # Fix a mistake, e.g. "step 2" puts you back on step 2.
        number = int(command.split()[1])
        if 1 <= number <= len(TEMPLATE_STEPS):
            storage.set_setting("template_step", number)
            show_step(say)
        else:
            say(f"Steps go from 1 to {len(TEMPLATE_STEPS)}.")
    elif command == "recap preview":
        text, _ = build_recap(storage.week_start())
        say("👀 *Preview only, not posted:*\n\n" + text)
    elif command == "post recap":
        post_weekly_recap(force=True)
    elif re.match(r"suggest default #?\d+", command):
        # Testing shortcut: don't wait 3 days.
        decision = storage.get_decision(int(re.search(r"\d+", command).group()))
        if decision and decision["status"] != "decided":
            suggest_default_for(decision)
        else:
            say("That decision doesn't exist or is already decided.")
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
    posted = post_to_channel(
        "helm",
        f"✅ *Check-in* _(via chat)_: {meaning.summary}{time_part} · {meaning.category}\n"
        f"This week so far: {nice_time(total)}",
    )
    where = "Logged in #helm" if posted else "Saved (but not posted to #helm, see the warning above)"
    say(f"{meaning.reply}\n📒 {where}. This week: *{nice_time(total)}*.")


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


def guess_category(task):
    """Best guess of a daily task's category from its words."""
    t = (task or "").lower()
    if "template" in t or "figma" in t or "step " in t:
        return "template"
    if any(w in t for w in ("course", "module", "coursera", "read", "activity", "persona", "journey", "audit", "lesson")):
        return "coursework"
    if any(w in t for w in ("gig", "flyer", "client")):
        return "gig"
    return "other"


def show_log(say):
    """Everything logged since Monday: day, what, category, time."""
    checkins = storage.week_checkins()
    if not checkins:
        say("Nothing logged yet this week (weeks start Monday). Tap ✅ on a task or tell me what you did!")
        return
    lines = ["📒 *This week*"]
    for c in checkins:
        day = date.fromisoformat(c["day"]).strftime("%a")
        time_part = f" · {nice_time(c['minutes'])}" if c["minutes"] else " · no time"
        lines.append(f"• {day}: {c['summary']} _({c['category']})_{time_part}")
    total, _ = storage.week_minutes()
    lines.append(f"*Total: {nice_time(total)}* across {len(checkins)} check-in(s)")
    say("\n".join(lines))


def skip_today(say):
    today = storage.get_daily_task(storage.today())
    if today and today["status"] == "done":
        say("You already did today's thing ✅ No need to skip. Enjoy the rest of the day!")
        return
    storage.set_daily_status(storage.today(), "skipped")
    say("Skipped ✅ Rest is part of the plan. See you tomorrow morning.")


# ---------- Step 4: ideas ----------

def handle_idea(idea_text, say):
    if not idea_text:
        say("What's the idea? e.g. “idea: a free checklist to go with the template”")
        return
    tidy = brain.tidy_idea(idea_text)
    title = tidy.title if tidy else idea_text[:60]
    body = tidy.body if tidy else idea_text
    storage.add_idea(title, body, idea_text)
    posted = post_to_channel("ideas", f"💡 *{title}*\n{body}\n_via chat_")
    where = "Posted to #ideas" if posted else "Saved (but not posted to #ideas, see the warning above)"
    say(f"💡 {where}: *{title}*")


# ---------- Step 4: decisions ----------

def open_decision(question, say):
    if not question:
        say("What's the decision? e.g. “decision: should the template come in light and dark mode?”")
        return
    number = storage.add_decision(question)
    post_to_channel("helm", f"🧭 *Decision #{number} (open)* _(via chat)_: {question}")
    dm_ts = dm_me(
        f"🧭 *Decision #{number}* logged in #helm: {question}\n"
        f"Reply *in this thread* with your answer whenever you're ready. If it's still open in "
        f"{DEFAULT_AFTER_DAYS} days, I'll suggest a default. Nothing is final until you say yes."
    )
    storage.update_decision(number, dm_ts=dm_ts)


def list_decisions(say):
    decisions = storage.open_decisions()
    if not decisions:
        say("No open decisions 🎉 Start one with “decision: ...”")
        return
    lines = ["🧭 *Open decisions:*"]
    for d in decisions:
        opened = d["opened_at"][:10]
        extra = f" (suggested: _{d['suggested_pick']}_, waiting for your ✅)" if d["status"] == "suggested" else ""
        lines.append(f"• *#{d['id']}* {d['question']} · opened {opened}{extra}")
    lines.append("Answer with “decide 3: your answer”, or reply in the decision's thread.")
    say("\n".join(lines))


def record_answer(decision, answer, via="your answer"):
    """Alexander answered: this is the ONLY way a decision becomes final."""
    if decision["status"] == "decided":
        dm_me(f"Decision #{decision['id']} is already decided: *{decision['answer']}*. "
              f"Start a new one with “decision: ...” if you want to change it.",
              thread_ts=decision["dm_ts"])
        return
    storage.update_decision(
        decision["id"], status="decided", answer=answer,
        decided_at=storage.now_denver().isoformat(timespec="minutes"),
    )
    post_to_channel("helm", f"✅ *Decided #{decision['id']}*: {decision['question']}\n→ *{answer}* _({via})_")
    dm_me(f"✅ Decision #{decision['id']} is final: *{answer}*. Logged in #helm.",
          thread_ts=decision["dm_ts"])


def suggest_default_for(decision):
    """Suggest a default answer. It is NOT final until Alexander reacts ✅."""
    pick = brain.suggest_default(decision["question"], read_focus())
    if not pick:
        print(f"Couldn't get a default for decision #{decision['id']}, will try again tomorrow.")
        return
    suggestion_ts = dm_me(
        f"⏰ *Decision #{decision['id']}* has been open a few days: {decision['question']}\n\n"
        f"Suggested default: *{pick.pick}*\n_{pick.why}_\n\n"
        f"React ✅ to go with it, or ❌ to keep it open. Or reply in this thread with a "
        f"different answer. Nothing is final until you say yes."
    )
    storage.update_decision(
        decision["id"], status="suggested", suggested_pick=pick.pick,
        suggested_at=storage.now_denver().isoformat(timespec="minutes"),
        suggestion_ts=suggestion_ts,
    )


def check_old_decisions():
    """Runs every morning: suggest defaults for decisions open 3+ days."""
    for decision in storage.decisions_needing_default(DEFAULT_AFTER_DAYS):
        suggest_default_for(decision)


@app.event("reaction_added")
def handle_reaction(event):
    """✅/❌ on a morning ping is a one-tap check-in.
    ✅ on a decision suggestion confirms it; ❌ keeps the decision open."""
    if event.get("user") != MY_USER_ID:
        return
    message_ts = event.get("item", {}).get("ts")
    reaction = event.get("reaction", "").split("::")[0]  # ignore skin-tone variations

    daily = storage.find_daily_task_by_ping(message_ts)
    if daily:
        tap_checkin(daily, reaction, message_ts)
        return

    checkin = storage.find_checkin_by_time_ts(message_ts)
    if checkin:
        if reaction in TIME_REACTIONS:
            minutes = TIME_REACTIONS[reaction]
            storage.set_checkin_minutes(checkin["id"], minutes)
            total, _ = storage.week_minutes()
            dm_me(f"⏱️ Logged {nice_time(minutes)}. This week: *{nice_time(total)}*.", thread_ts=message_ts)
        return

    decision = storage.find_decision_by_message(message_ts)
    if not decision or decision["status"] != "suggested":
        return
    if reaction in YES_REACTIONS:
        record_answer(decision, decision["suggested_pick"], via="suggested default, confirmed by you")
    elif reaction in NO_REACTIONS:
        storage.update_decision(decision["id"], status="open")
        dm_me("👍 Kept open. Reply in this thread with your answer whenever you're ready.",
              thread_ts=decision["suggestion_ts"])


# ---------- Step 5: weekly recap ----------

def short_date(iso_day):
    d = date.fromisoformat(iso_day)
    return f"{d:%b} {d.day}"  # e.g. "Nov 3" (works on Windows too)


def build_recap(week):
    """Put together the recap for the week starting on Monday `week`. Returns (text, goal)."""
    week_end = (date.fromisoformat(week) + timedelta(days=6)).isoformat()
    total, by_category = storage.week_minutes(week)
    checkins = storage.week_checkins(week)
    days = storage.week_daily_tasks(week)
    decided = storage.week_decided(week)
    still_open = storage.open_decisions()
    ideas = storage.week_ideas(week)

    done = sum(1 for d in days if d["status"] == "done")
    skipped = sum(1 for d in days if d["status"] == "skipped")
    no_checkin = sum(1 for d in days if d["status"] == "sent")
    category_text = ", ".join(f"{c} {nice_time(m)}" for c, m in by_category.items() if m)

    # Plain facts. Counted by the code, so the numbers are always right.
    facts = "\n".join([
        f"Week: {short_date(week)} to {short_date(week_end)}",
        f"Hours logged: {nice_time(total)} ({category_text or 'none'}) across {len(checkins)} check-ins",
        f"Daily tasks: {done} done, {skipped} skipped, {no_checkin} with no check-in",
        "Check-ins:",
        *[f"- {c['day']}: {c['summary']}" + (f" ({nice_time(c['minutes'])})" if c["minutes"] else "")
          for c in checkins],
        "Decisions made: " + ("; ".join(f"#{d['id']} {d['question']} -> {d['answer']}" for d in decided) or "none"),
        "Decisions still open: " + ("; ".join(f"#{d['id']} {d['question']} (opened {d['opened_at'][:10]})"
                                               for d in still_open) or "none"),
        "New ideas: " + (", ".join(i["title"] for i in ideas) or "none"),
    ])

    recap = brain.write_weekly_recap(facts, read_focus())

    lines = [
        f"📦 *Weekly recap: {short_date(week)} – {short_date(week_end)}*",
        f"⏱ *Hours:* {nice_time(total)}" + (f" ({category_text})" if category_text else "")
        + f" · {len(checkins)} check-in(s)",
        f"📅 *Daily tasks:* {done} done · {skipped} skipped · {no_checkin} no check-in",
    ]
    if recap:
        if recap.highlights:
            lines.append("\n✅ *Got done:*")
            lines += [f"• {h}" for h in recap.highlights]
        if decided:
            lines.append("\n🧭 *Decided:*")
            lines += [f"• #{d['id']} {d['question']} → {d['answer']}" for d in decided]
        if recap.stuck:
            lines.append("\n🚧 *Stuck / slipping:*")
            lines += [f"• {s}" for s in recap.stuck]
        if ideas:
            lines.append(f"\n💡 {len(ideas)} new idea(s) in #ideas")
        lines.append(f"\n🎯 *Suggested main goal this week:* {recap.main_goal}")
        lines.append(f"_{recap.note}_")
        goal = recap.main_goal
    else:
        # Claude unavailable: still post the facts.
        lines.append("\n✅ *Check-ins:*")
        lines += [f"• {c['summary']}" for c in checkins] or ["• (none logged)"]
        if still_open:
            lines.append("\n🧭 *Open decisions:* " + ", ".join(f"#{d['id']}" for d in still_open))
        goal = None
    return "\n".join(lines), goal


def post_weekly_recap(force=False):
    """Post LAST week's recap to #ship-log. Runs Mondays at 7:05am, or on 'post recap'."""
    week = storage.last_week_start()
    if storage.get_recap(week) and not force:
        print(f"Recap for week of {week} already posted, skipping.")
        return
    text, goal = build_recap(week)
    if post_to_channel("ship-log", text):
        storage.save_recap(week, goal)
        dm_me("📦 Last week's recap is up in #ship-log." +
              (f"\n🎯 Suggested main goal: *{goal}*. I'll lean the morning tasks toward it. "
               f"(Just a suggestion. To pick your own, type “goal: ...”)" if goal else ""))


def start_scheduler():
    """Set up the timers (Denver time): 7am task, 9am decision check, Monday 7:05am recap."""
    scheduler = BackgroundScheduler(timezone=storage.DENVER)
    scheduler.add_job(
        send_morning_ping,
        CronTrigger(hour=MORNING_PING_HOUR, minute=0, timezone=storage.DENVER),
        misfire_grace_time=3 * 60 * 60,  # if the computer was asleep at 7am, still send it within 3 hours
        coalesce=True,
    )
    scheduler.add_job(
        send_evening_checkin,
        CronTrigger(hour=EVENING_CHECKIN_HOUR, minute=0, timezone=storage.DENVER),
        misfire_grace_time=60 * 60,
        coalesce=True,
    )
    scheduler.add_job(
        check_old_decisions,
        CronTrigger(hour=DECISION_CHECK_HOUR, minute=0, timezone=storage.DENVER),
        misfire_grace_time=3 * 60 * 60,
        coalesce=True,
    )
    scheduler.add_job(
        post_weekly_recap,
        CronTrigger(day_of_week=RECAP_DAY, hour=RECAP_HOUR, minute=RECAP_MINUTE, timezone=storage.DENVER),
        misfire_grace_time=6 * 60 * 60,
        coalesce=True,
    )
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    print("Starting Orbital Bot...")
    storage.setup()
    start_scheduler()
    dm_me("Hi Alexander! Orbital Bot is online. ✅ Type “help” to see what I can do.")
    print("Orbital Bot is running. Leave this window open. Press Ctrl+C to stop.")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
