# Bridge Bot

A Slack helper for **The Bridge**. It DMs Alexander one task a day, logs check-ins,
tracks decisions and ideas, and posts a weekly recap. It drafts and suggests; Alexander approves.

**Built so far:** step 1 (DMs) ✅ · step 2 (7am morning ping) ✅ · step 3 (check-ins & hours) ✅ · step 4 (ideas & decisions) ✅ · step 5 (weekly recap) ✅ · step 6 (runs 24/7 on Google Cloud) ✅

---

## Files, in plain words

| File | What it is |
|---|---|
| `bot.py` | The main program. Start this to run the bot. |
| `brain.py` | The part that talks to Claude (tasks, check-ins, ideas, defaults, recaps). The model name is at the top. |
| `storage.py` | Saves records to `bridge.db`, a small database file on your computer. |
| `my-focus.txt` | **You edit this.** What you're working on now; the bot reads it every morning. |
| `start-bot.bat` | Double-click to start the bot on Windows. |
| `.env` | **Your secret keys.** Only on your computer, never uploaded. |
| `.env.example` | A blank template for `.env`. |
| `slack-app-manifest.yml` | The Slack app's settings, in case you ever need to recreate the app. |
| `deploy/` | Scripts for running the bot on the Google Cloud server (step 6). |

---

## Where the bot runs

The bot runs **24/7 on a Google Cloud server** called `bridge-bot` (e2-micro, us-central1).
It restarts itself if it crashes or the server reboots. **Don't run it on your PC too**,
or you'll get double messages.

To use the server's terminal: console.cloud.google.com → **VM instances** → `bridge-bot` → **SSH**.
Paste with Ctrl+V. Closing the SSH window does NOT stop the bot.

| I want to... | Do this |
|---|---|
| Update `my-focus.txt` | Edit it on your PC → GitHub Desktop → **Commit** → **Push**. The server downloads it every day at 6:45am, before the 7am task. To apply it right away: SSH → `cd ~/bridge-bot && git pull` |
| Get a new code update from Claude | SSH → `cd ~/bridge-bot && bash deploy/update.sh` |
| Restart the bot | SSH → `sudo systemctl restart bridge-bot` |
| Check it's running | SSH → `sudo systemctl status bridge-bot --no-pager` (look for `active (running)`) |
| See what it's been doing / errors | SSH → `sudo journalctl -u bridge-bot -n 50 --no-pager` |
| Change a key in `.env` | Edit `.env` on your PC → SSH window → **UPLOAD FILE** → then `mv ~/.env ~/bridge-bot/ && chmod 600 ~/bridge-bot/.env && sudo systemctl restart bridge-bot` |
| Stop the bot completely | SSH → `sudo systemctl stop bridge-bot` (start again: `sudo systemctl start bridge-bot`) |

**If the SSH window won't connect:** wait 2 minutes and try again. Still stuck? VM instances →
tick `bridge-bot` → **Reset** (like restarting a computer; files are kept). The bot starts by itself.

**Google Cloud free trial ends about 2 Feb 2027.** Before then, Google will email you. To keep the
server, click **Upgrade** / **Activate full account** (about $3.65/month for the internet address;
the server and disk stay free). If you don't upgrade, the server pauses and the bot stops.

## Running the bot on your PC instead (backup option)

Only if the server is off. Never run both at once.

**Easy way:** open the `bridge-bot` folder and double-click **`start-bot.bat`**.

**Or in PowerShell**, inside the `bridge-bot` folder:
```
py bot.py
```

It's working when you see `Bolt app is running!` and Slack DMs you "Bridge Bot is online ✅".
Keep the window open. On your PC, the bot only runs while that window is open.

## If the bot stops or isn't answering

1. **On the server:** SSH → `sudo journalctl -u bridge-bot -n 50 --no-pager` to see recent errors,
   then `sudo systemctl restart bridge-bot`.
   **On your PC:** look at the PowerShell window for red text, then double-click `start-bot.bat` again.
2. Error text never contains your keys, so it's safe to copy.
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

**Server:** SSH → `cd ~/bridge-bot && bash deploy/update.sh`. That's it.

**PC (backup option only):**
1. Stop the bot (Ctrl+C or close its window).
2. In **GitHub Desktop**: click **Fetch origin**, then **Pull origin**.
3. If the update says new add-ons are needed, run: `py -m pip install -r requirements.txt`
4. Start the bot again.

## DM commands

| Type this to the bot | What happens |
|---|---|
| *(no typing)* tap ✅ or ❌ under the morning task | ✅ marks it done, logs a check-in and posts to #helm. ❌ skips today. |
| *anything you did*, e.g. `did 30 min of module 4` | Logs a check-in, posts it to #helm "via chat", adds to weekly hours. |
| `class: on module 4 quiz` | Saves where you are in class. The morning task starts from there. (`class` shows it.) |
| `step done` | You finished the current portfolio template step. Logs it in #helm and shows the next step. (`step` shows it, `step 3` fixes a mistake.) |
| `what's next` | Today's task, or an optional bonus if you're done. |
| `hours this week` | Time logged since Monday, by category. |
| `skip today` | Marks today skipped. No guilt. |
| `idea: ...` | Tidies the idea and posts it to #ideas. |
| `decision: ...` | Logs it in #helm and starts a DM thread. **Reply in that thread** to answer. |
| `decisions` | Lists open decisions. |
| `decide 3: your answer` | Answers decision #3 without using the thread. |
| `suggest default 3` | Testing: asks for decision #3's default now instead of waiting 3 days. |
| `goal: ...` | Sets your own main goal for the week (`goal` shows it). Morning tasks lean toward it. |
| `recap preview` | DMs you a recap of this week so far. Not posted anywhere. |
| `post recap` | Posts last week's recap to #ship-log right now. |
| `ping me` | Sends today's morning task right now (for testing). |
| `help` | Lists these commands. |

**Schedule (Denver time):** 7:00am daily task · 8:00pm one-tap "did it happen?" check-in
(only if you haven't tapped ✅/❌ yet; anything not done is first up the next morning) · 9:00am check for 3-day-old decisions ·
Monday 7:05am weekly recap in #ship-log (last week's hours, what got done, what's stuck,
one suggested main goal).

**How decision defaults work:** every day at 9am, any decision open for 3+ days gets a
suggested default in your DMs. It only becomes final if **you** react ✅ (❌ keeps it open,
or reply in the thread with a different answer). The bot never decides on its own.

**Channels:** the bot must be invited to a channel before it can post there.
In #helm, #ideas and #ship-log type `/invite @Bridge Bot`.
Never invite it to #design-studio. The code also blocks posting there.

## First-time setup (already done, here for reference)

1. **Slack app:** api.slack.com/apps → Create New App → From a manifest → The Bridge → paste `slack-app-manifest.yml`.
   Then check: Event Subscriptions has `message.im` + `reaction_added`, App Home → Messages Tab is on,
   and OAuth & Permissions lists all 8 scopes from the manifest.
2. **App token (`xapp-`):** Basic Information → App-Level Tokens → Generate, scope `connections:write`.
3. **Bot token (`xoxb-`):** Install App → Install to The Bridge → copy Bot User OAuth Token.
4. **Member ID (`U...`):** Slack → your profile → ⋮ → Copy member ID.
5. **Claude key (`sk-ant-`):** platform.claude.com → Settings → API Keys → Create Key.
6. Install Python (tick "Add python.exe to PATH") and GitHub Desktop, clone this repo.
7. In the folder: `py -m pip install -r requirements.txt`, then `Copy-Item .env.example .env`, `notepad .env`, paste the values.

## Costs

- Slack app: free.
- Claude (Haiku model): roughly $0.30/month at this usage. Set a monthly limit at platform.claude.com → Settings → Limits.
- Hosting (Google Cloud e2-micro): the server and standard disk are free; the internet address is about
  $3.65/month. The $300 new-account trial covers the first 90 days (until about 2 Feb 2027).
  A $5/month budget alert emails you if costs go up. Check actual costs: console → Billing → Reports.

## Safety rules built into the bot

- Never posts in #design-studio unless asked.
- Never spends money, publishes publicly, posts to marketplaces, or emails anyone.
- A suggested default for a decision is never final until Alexander reacts ✅.
- Keys live only in `.env`, which is in `.gitignore` and never uploaded.
