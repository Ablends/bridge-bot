# brain.py — everything that talks to Claude lives here.

import os

import anthropic

# The Claude model the bot uses. Haiku is fast and very cheap.
# To try a smarter (pricier) model later, change this one line,
# e.g. to "claude-sonnet-5-5".
MODEL = "claude-haiku-5-5"

TONE = (
    "You are Bridge Bot, a helper for Alexander, who runs a small design-led product "
    "business from a Slack workspace called The Bridge. "
    "Tone: friendly, short, pushes him forward without nagging. No guilt, no lectures. "
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


def suggest_daily_task(is_shift_day, weekday_name, focus, recent):
    """Ask Claude for ONE task for today."""
    if is_shift_day:
        size = (
            "Today is a WORK SHIFT day (he works 8am-7pm). The task must be tiny: about "
            "5 minutes, doable on a break or phone if possible."
        )
    else:
        size = (
            "Today is a PROGRESS day (Mon-Wed, his main work days). Suggest one real "
            "work block of 60-120 minutes with a clear finish line."
        )

    recent_text = "\n".join(f"- {r['day']}: {r['task']} ({r['status']})" for r in recent) or "- none yet"

    instructions = f"""Suggest ONE task for Alexander for today ({weekday_name}).

{size}

Either coursework OR portfolio/template work counts. Pick whichever moves things forward most,
and vary it from recent days when it makes sense.

What he's working on right now:
{focus}

Recent suggested tasks (avoid repeating these exactly):
{recent_text}

Reply with only the task: 1-2 short sentences, starting with a verb, including a rough
time estimate. No greeting, no list, no extra commentary."""

    return ask_claude(instructions)
