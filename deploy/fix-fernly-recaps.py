# One-time fix (18 Nov 2026): remove the wrong Fernly date (30 Nov) from three old
# weekly recaps in #ship-log. Fernly has no target date (Alexander's Oct 14 decision).
# The bot can only edit its OWN messages, which these are.
#
# Run once on the server, inside the bridge-bot folder:
#   .venv/bin/python deploy/fix-fernly-recaps.py

import os

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
SHIP_LOG = "C0C7U0SK07Q"

FIXED = {
    # Recap "Oct 26 – Nov 1" (first post, Nov 3)
    "1793758523.520419": (
        "📦 *Weekly recap: Oct 26 – Nov 1*\n"
        "⏱ *Hours:* 0m · 0 check-in(s)\n"
        "📅 *Daily tasks:* 0 done · 0 skipped · 0 no check-in\n"
        "\n🚧 *Stuck / slipping:*\n"
        "• Fernly real interviews haven't started yet; the screener still needs posting\n"
        "\n🎯 *Suggested main goal this week:* Post the Fernly screener and get one pilot interview "
        "scheduled so the Stage 1 case study has real research behind it.\n"
        "_Nothing logged last week is fine; a single screener post this week gets Fernly moving again. "
        "You've got this._"
    ),
    # Recap "Oct 26 – Nov 1" (second post, Nov 3)
    "1793758698.410009": (
        "📦 *Weekly recap: Oct 26 – Nov 1*\n"
        "⏱ *Hours:* 0m · 0 check-in(s)\n"
        "📅 *Daily tasks:* 0 done · 0 skipped · 0 no check-in\n"
        "\n🚧 *Stuck / slipping:*\n"
        "• Fernly real interviews haven't started yet; the screener still needs to be posted\n"
        "• No check-ins or logged hours last week, so there's no progress to report yet on the Figma "
        "portfolio template or Command Hub Lite\n"
        "\n🎯 *Suggested main goal this week:* Post the Fernly screener so the first pilot interview "
        "can be scheduled.\n"
        "_Last week was quiet, and a fresh start this week is all it takes. Looking forward to seeing "
        "what you ship._"
    ),
    # Recap "Nov 2 – Nov 8" (Nov 9)
    "1794233109.306609": (
        "📦 *Weekly recap: Nov 2 – Nov 8*\n"
        "⏱ *Hours:* 1h (coursework 1h) · 8 check-in(s)\n"
        "📅 *Daily tasks:* 3 done · 2 skipped · 1 no check-in\n"
        "\n✅ *Got done:*\n"
        "• Finished 3 Coursera sessions (1h of coursework) across the week\n"
        "• Set a 90-minute block for Course 2's remaining graded items\n"
        "• Read the second half of the empathizing guide and jotted Fernly persona ideas\n"
        "• Updated the HOUSEPLANT CARE SURVEY form with an optional follow-up chat question and anonymity note\n"
        "• Copied the survey link into the Fernly recruiting post and shared the survey on LinkedIn\n"
        "\n🧭 *Decided:*\n"
        "• #1 light and dark mode for the template? → light only for v1\n"
        "• #2 test decision → Post the Fernly screener as a draft in your own workspace, then book one "
        "pilot interview with a friend-of-a-friend who fits the screener.\n"
        "\n🚧 *Stuck / slipping:*\n"
        "• Course 2 still has about 4 hours of Module 4 work left\n"
        "• Portfolio template is on step 1 of 9 (set up the pages and move the Oct 17 wireframe to Desktop)\n"
        "• Fernly case study: Problem, Research and Process sections still to fill in, at class pace\n"
        "\n💡 3 new idea(s) in #ideas\n"
        "\n🎯 *Suggested main goal this week:* Finish the Course 2 items planned for Mon 9 and Tue 10 Nov, "
        "starting from your Fernly personas and journey map\n"
        "_Solid week of getting the Fernly survey live. Small steady blocks next week will keep Course 2 moving._"
    ),
}

for ts, text in FIXED.items():
    try:
        client.chat_update(channel=SHIP_LOG, ts=ts, text=text)
        print(f"Fixed recap {ts}")
    except SlackApiError as error:
        print(f"Could not fix recap {ts}: {error.response.get('error')}")
