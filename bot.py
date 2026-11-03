# Bridge Bot — Alexander's helper for The Bridge Slack workspace.
#
# STEP 1: the bot connects to Slack, DMs you when it starts,
# and answers when you DM it. More features get added step by step.

import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Read the secret keys from the .env file (never written in the code itself).
load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]   # starts with xoxb-
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]   # starts with xapp-
MY_USER_ID = os.environ["MY_SLACK_USER_ID"]       # your Slack member ID, starts with U

app = App(token=SLACK_BOT_TOKEN)


def dm_me(text):
    """Send Alexander a direct message from the bot."""
    app.client.chat_postMessage(channel=MY_USER_ID, text=text)


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

    text = event.get("text", "")
    say(f"Got it 👋 You said: “{text}”. (I'm only at step 1 — real smarts coming soon.)")


if __name__ == "__main__":
    print("Starting Bridge Bot...")
    dm_me("Hi Alexander! Bridge Bot is online. ✅ Reply to me here to test.")
    print("Bridge Bot is running. Leave this window open. Press Ctrl+C to stop.")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
