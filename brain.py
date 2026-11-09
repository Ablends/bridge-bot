# brain.py — everything that talks to Claude lives here.

import os
from typing import Literal, Optional

import anthropic
from pydantic import BaseModel

# The Claude model the bot uses. Haiku is fast and very cheap.
# To try a smarter (pricier) model later, change this one line,
# e.g. to "claude-sonnet-5-5".
MODEL = "claude-haiku-5-5"

TONE = (
    "You are Bridge Bot, a helper for Alexander, who runs a small design-led product "
    "business called Orbital Roots, run from a Slack workspace. "
    "Tone: friendly, short, pushes Alexander forward without nagging. No guilt, no lectures. "
    "Never suggest spending money, publishing anything publicly, posting to a marketplace, "
    "or emailing anyone. You draft and suggest; Alexander approves."
)

def ask_claude(instructions, max_tokens=2000):
    """Send one request to Claude and return its text reply (or None if it failed)."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("No ANTHROPIC_API_KEY in .env, so using a backup message instead of Claude.")
        return None
    try:
        # The client reads ANTHROPIC_API_KEY from the .env file automatically.
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            output_config={"effort": "low"},  # short, simple jobs: keep it quick and cheap
            system=TONE,
            messages=[{"role": "user", "content": instructions}],
        )
    except anthropic.APIError as error:
        print(f"Claude request failed: {error}")
        return None

    text = "".join(block.text for block in response.content if block.type == "text").strip()
    return text or None


def suggest_daily_task(is_shift_day, weekday_name, focus, recent, weekly_goal=None):
    """Ask Claude for ONE task for today."""
    if is_shift_day:
        size = (
            "Today is a WORK SHIFT day (Alexander works 8am-7pm). The task must be tiny: about "
            "5 minutes, doable on a break or phone if possible."
        )
    else:
        size = (
            "Today is a PROGRESS day (Mon-Wed, Alexander's main work days). Suggest one real "
            "work block of 60-120 minutes with a clear finish line."
        )

    recent_text = "\n".join(f"- {r['day']}: {r['task']} ({r['status']})" for r in recent) or "- none yet"

    instructions = f"""Suggest ONE task for Alexander for today ({weekday_name}).

{size}

Either coursework OR portfolio/template work counts. Pick whichever moves things forward most,
and vary it from recent days when it makes sense.

What Alexander is working on right now:
{focus}

This week's suggested main goal (lean toward it when it fits): {weekly_goal or "(none set)"}

Recent suggested tasks, newest first. Status "done" = finished; "skipped" or "sent" = NOT done:
{recent_text}

If the newest task above was NOT done, give that same task again today (make it smaller if
today is a shift day). Otherwise, don't repeat recent tasks.

Reply with only the task: 1-2 short sentences, starting with a verb, including a rough
time estimate. No greeting, no list, no extra commentary."""

    return ask_claude(instructions)


# ---------- Step 3: understanding your DMs ----------

class MessageMeaning(BaseModel):
    """What Claude decides your DM means. Claude must fill in exactly these fields."""
    is_checkin: bool                 # did you report doing some work?
    minutes: Optional[int]           # how long, ONLY if you said (e.g. "30 min", "2 hours")
    category: Literal["coursework", "portfolio", "template", "gig", "other"]
    summary: str                     # short tidy version for the #helm log
    reply: str                       # a short friendly reply to you


def understand_message(text, todays_task):
    """Ask Claude whether a DM is a check-in, and pull out the details."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None

    instructions = f"""Alexander sent you this DM:
"{text}"

Today's suggested task was: {todays_task or "(none sent today)"}

Decide if this is a CHECK-IN, meaning Alexander is reporting work they did (even small, even vague,
e.g. "did 30 min of module 4", "finished the cover page", "done!" when a task was suggested).

Fill in:
- is_checkin: true or false.
- minutes: how long they worked, converted to minutes, ONLY if they stated a time. Otherwise null.
  Never guess a time.
- category: "coursework" (Coursera course), "portfolio" (case studies: Fernly, budgeting app,
  Command Hub Lite), "template" (the Figma portfolio template product), "gig" (a paid design job
  for a client: flyers, social posts, menus), or "other" (planning, business admin, anything else).
- summary: for a check-in, a short past-tense log line like "Did 30 min of Coursera module 4".
  Otherwise an empty string.
- reply: 1 short friendly sentence back to Alexander. For a check-in, a quick, genuine
  well-done (no over-the-top praise). If it's not a check-in, reply naturally and briefly.
  If they seem to be asking for something, mention they can type "help" to see what you can do."""

    try:
        client = anthropic.Anthropic()
        response = client.messages.parse(
            model=MODEL,
            max_tokens=2000,
            output_config={"effort": "low"},
            system=TONE,
            messages=[{"role": "user", "content": instructions}],
            output_format=MessageMeaning,
        )
        return response.parsed_output
    except anthropic.APIError as error:
        print(f"Claude request failed: {error}")
        return None
    except Exception as error:  # e.g. Claude's answer didn't fit the form
        print(f"Couldn't understand Claude's answer: {error}")
        return None



# ---------- Step 4: ideas and decision defaults ----------

class TidyIdea(BaseModel):
    title: str   # short headline, max ~8 words
    body: str    # 1-3 tidy sentences


class DefaultPick(BaseModel):
    pick: str    # the suggested answer
    why: str     # one short sentence explaining why


def ask_claude_form(instructions, form):
    """Like ask_claude, but Claude must answer by filling in a form (a Pydantic model)."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        client = anthropic.Anthropic()
        response = client.messages.parse(
            model=MODEL,
            max_tokens=2000,
            output_config={"effort": "low"},
            system=TONE,
            messages=[{"role": "user", "content": instructions}],
            output_format=form,
        )
        return response.parsed_output
    except anthropic.APIError as error:
        print(f"Claude request failed: {error}")
        return None
    except Exception as error:
        print(f"Couldn't understand Claude's answer: {error}")
        return None


def tidy_idea(text):
    return ask_claude_form(
        f"""Alexander jotted down this idea for the business:
"{text}"

Tidy it up for the #ideas channel. Keep Alexander's meaning and voice; don't add new
ideas or plans of your own. Give a short title (max 8 words) and a body of 1-3 clear sentences.""",
        TidyIdea,
    )


def suggest_default(question, focus):
    return ask_claude_form(
        f"""Alexander logged this decision 3 days ago and hasn't answered it yet:
"{question}"

What Alexander is working on right now:
{focus}

Suggest a sensible DEFAULT answer: the simplest, lowest-risk, cheapest option that keeps
things moving. It must not involve spending money, publishing anything publicly,
posting to a marketplace, or emailing anyone. This is only a suggestion; Alexander confirms.
Give the pick (short, a few words to one sentence) and one short sentence on why.""",
        DefaultPick,
    )



# ---------- Step 5: weekly recap ----------

class WeeklyRecap(BaseModel):
    highlights: list[str]   # up to 5 short bullets of what got done
    stuck: list[str]        # up to 3 short bullets of what's stuck or slipping (can be empty)
    main_goal: str          # ONE suggested main goal for the coming week
    note: str               # one short, encouraging closing line


def write_weekly_recap(facts, focus):
    return ask_claude_form(
        f"""Write Alexander's weekly recap for the #ship-log channel.

Facts from last week (these numbers are correct; don't change or recalculate them):
{facts}

What Alexander is working on right now:
{focus}

Fill in:
- highlights: up to 5 short bullets of what actually got done, based on the check-ins.
  Group small related items. If nothing was logged, return an empty list.
- stuck: up to 3 short bullets on what's stuck or slipping (open decisions, projects with
  no progress, deadlines coming up). Be matter-of-fact, never guilt-trippy. Skipped shift
  days are NOT a problem; don't mention them as one.
- main_goal: ONE concrete main goal for this coming week, that Alexander could finish on the
  Mon-Wed progress days. Prefer whatever unblocks the nearest deadline.
- note: one short, warm closing line that pushes forward without nagging.""",
        WeeklyRecap,
    )
