# Bridge Bot

A Slack helper for **The Bridge**. It DMs Alexander one task a day, logs check-ins,
tracks decisions and ideas, and posts a weekly recap. It drafts and suggests; Alexander approves.

**Built so far:** step 1 (DMs) ✅ · step 2 (7am morning ping) ✅ · step 3 (check-ins & hours) ✅ · step 4 (ideas & decisions) ✅

---

## Files, in plain words

| File | What it is |
|---|---|
| `bot.py` | The main program. Start this to run the bot. |
| `brain.py` | The part that talks to Claude (writes tasks). The model name is at the top. |
| `storage.py` | Saves records to `bridge.db`, a small database file on your computer. |
| `my-focus.txt` | **You edit this.** What you're working on now; the bot reads it every morning. |
| `start-bot.bat` | Double-click to start the bot on Windows. |
| `.env` | **Your secret keys.** Only on your computer, never uploaded. |
| `.env.example` | A blank template for `.env`. |
| `slack-app-manifest.yml` | The Slack app's settings, in case you ever need to recreate the app. |

---

## Starting the bot (Windows)

**Easy way:** open the `bridge-bot` folder and double-click **`start-bot.bat`**.

**Or in PowerShell**, inside the `bridge-bot` folder:
```
py bot.py
```

It's working when you see `Bolt app is running!` and Slack DMs you "Bridge Bot is online ✅".
Keep the window open. The bot only runs while it's open (until it's moved to a server in step 6).

## If the bot stops or isn't answering

1. Look at the PowerShell window. If it shows red error text, copy it (it never contains your keys).
2. Close the window, then double-click **`start-bot.bat`** again.
3. Still broken? Check the table below, or paste the error to Claude.

| Error contains | Fix |
|---|---|
| `KeyError: 'SLACK_BOT_TOKEN'` | `.env` is missing or saved as `.env.txt`. Run `notepad .env` and save. |
| `invalid_auth` | The `xoxb-` token in `.env` is wrong. Re-copy it from api.slack.com → your app → OAuth & Permissions. |
| `not_allowed_token_type` | The `xoxb-` and `xapp-` tokens are swapped in `.env`. |
| `messages_tab_disabled` | api.slack.com → your app → App Home → turn on Messages Tab. |
| `ModuleNotFoundError` | Run `py -m pip install -r requirements.txt` |
| `Claude request failed` | Check `ANTHROPIC_API_KEY` in `.env` and your credit at platform.claude.com. The bot still sends a backup task. |
| Bot runs but never replies | api.slack.com → your app → Event Subscriptions → make sure `message.im` is listed. |

## Getting new code updates

1. Stop the bot (Ctrl+C or close its window).
2. In **GitHub Desktop**: click **Fetch origin**, then **Pull origin**.
3. If the update says new add-ons are needed, run: `py -m pip install -r requirements.txt`
4. Start the bot again.

## DM commands

| Type this to the bot | What happens |
|---|---|
| *anything you did*, e.g. `did 30 min of module 4` | Logs a check-in, posts it to #helm "via chat", adds to weekly hours. |
| `what's next` | Today's task, or an optional bonus if you're done. |
| `hours this week` | Time logged since Monday, by category. |
| `skip today` | Marks today skipped. No guilt. |
| `idea: ...` | Tidies the idea and posts it to #ideas. |
| `decision: ...` | Logs it in #helm and starts a DM thread. **Reply in that thread** to answer. |
| `decisions` | Lists open decisions. |
| `decide 3: your answer` | Answers decision #3 without using the thread. |
| `suggest default 3` | Testing: asks for decision #3's default now instead of waiting 3 days. |
| `help` | Lists these commands. |

**How decision defaults work:** every day at 9am, any decision open for 3+ days gets a
suggested default in your DMs. It only becomes final if **you** react ✅ (❌ keeps it open,
or reply in the thread with a different answer). The bot never decides on its own.
| `ping me` | Sends today's morning task right now (for testing). |

**Channels:** the bot must be invited to a channel before it can post there.
In #helm and #ideas (and later #ship-log) type `/invite @Bridge Bot`.
Never invite it to #design-studio. The code also blocks posting there.

## First-time setup (already done, here for reference)

1. **Slack app:** api.slack.com/apps → Create New App → From a manifest → The Bridge → paste `slack-app-manifest.yml`.
2. **App token (`xapp-`):** Basic Information → App-Level Tokens → Generate, scope `connections:write`.
3. **Bot token (`xoxb-`):** Install App → Install to The Bridge → copy Bot User OAuth Token.
4. **Member ID (`U...`):** Slack → your profile → ⋮ → Copy member ID.
5. **Claude key (`sk-ant-`):** platform.claude.com → Settings → API Keys → Create Key.
6. Install Python (tick "Add python.exe to PATH") and GitHub Desktop, clone this repo.
7. In the folder: `py -m pip install -r requirements.txt`, then `Copy-Item .env.example .env`, `notepad .env`, paste the values.

## Costs

- Slack app: free.
- Claude (Haiku model): roughly $0.30/month at this usage. Set a monthly limit at platform.claude.com → Settings → Limits.
- Hosting: free (step 6 will use Google Cloud's free tier).

## Safety rules built into the bot

- Never posts in #design-studio unless asked.
- Never spends money, publishes publicly, posts to marketplaces, or emails anyone.
- Keys live only in `.env`, which is in `.gitignore` and never uploaded.
