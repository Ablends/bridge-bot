# Notes for Claude (read before helping)

## Who this is for
- Alexander, who runs a small design-led product business called **Orbital Roots** (renamed from "The Bridge" on 9 Nov 2026;
  the Slack workspace may still show the old name). Public-facing work goes under his own name.
- New to design and new to programming: explain things in plain language, and say exactly what to click or type.
- Works long shifts Thu–Sun (one task of up to ~15 minutes those days; raised from 5 on 12 Nov, his call:
  the 5-minute limit came from Claude, not from him). Mon–Wed are the main work days.

## Current priorities (in order, updated 12 Nov 2026)
1. Keep this bot running (it's live on a Google Cloud e2-micro server, see README).
2. **Money this month (12 Nov, his top priority).** He needs extra income and can't add work shifts (school, kids,
   Mondays are for his grandma), so never suggest more shifts. Side income now comes from local business work:
   a $100 website audit offer plus flyers and posters. Old hardware gets sold on eBay and Craigslist. He is not on
   Facebook: never suggest it. Dates and details are in my-focus.txt ("LOCAL BUSINESS GIGS").
3. Weekly rhythm: Mon 6:35-7:35am class homework hour (then Grandma's all day); Tue/Wed mornings = audits and
   flyer gigs (changed 12 Nov; was the template); Tue 1-3pm / Wed 12-1:30pm = a gig or a Fernly interview;
   Thu-Sun shifts = ONE item of up to ~15 min, never more.
4. Coursera Course 2: PAUSED at the value proposition (10 Nov) until real research is done (recruit, 15-min chats,
   empathy maps, personas, journey maps; see my-focus.txt). Then Course 3. Fernly moves at the class's pace
   and has NO target date (Oct 14 decision; Nov 30 is only for the portfolio shell and case-study template in
   Figma). Don't add a Fernly date until he sets one himself.
5. Figma portfolio template: PAUSED for a few weeks (12 Nov). Step 1 is done (fresh file, six pages); Step 2 is next
   when he says it resumes. Don't suggest template work. YouTube Shorts recording is paused with it (when it resumes:
   record every template session in OBS, Figma window only; edit and post only after the template is done).
   Broken-buttons practice file is still saved for Step 3.
6. Book "The Bloodline" (added 12 Nov): only goal is finishing chapter 4. Low pressure; never nag.
7. Parked: art store (tablet files may be lost), budgeting app + Command Hub Lite case studies, biweekly zero-based
   budget template in Google Sheets (to build with Claude Code later), Jarvis (see ROADMAP.md).
- The big-picture plan: "Orbital Roots — Business Roadmap" doc (https://claude.ai/artifact/6ijMsf4deXz5n7gDuSCohL)
  and the Command Hub (https://claude.ai/artifact/5bf2WRi8FG1SwNzsGgvx99). my-focus.txt drives the daily task.

## Where we left off (handoff, saved Sat 21 Nov 2026, ~8:50pm)
**How handoffs work:** a new chat sees ONLY what is saved in this repo. This section IS the handoff; don't create a
separate handoff document (his call, 12 Nov). When he says "save the handoff", rewrite this section, push it, and
tell him exactly what was saved.

**Where he works with Claude (agreed 12 Nov; he asked for a clearer system)**
- Home base = a Claude Code session with THIS repo attached. Anything about the plan, the bot, tasks or decisions
  happens here, because only here can Claude read and save the notes. The 🕐 timestamp at the top of a reply is his
  sign that he's in the right place.
- Any other Claude chat = scratch paper. Nothing there is remembered unless he pastes it here. A message sent here
  from another Claude chat with his Allow counts as his request (as on 18 Nov).
- Voice planning happens in Chat; it ends with a summary he pastes here. Treat it as his decision.
- One session per work day or topic. Start with "Read CLAUDE.md and my-focus.txt. Start with what's next." and end
  with "save the handoff". He is on a usage limit: keep replies short, no long tables or repeated summaries, but
  always full click-by-click steps for anything he has to do.
- Money has its own home: the `/anthropic-skills:money` daily check and his Thursday Envelope page. Never write
  money figures, bills or pay into this repo.
- Private things (job situation, health, money) are NOT in this repo. If he pastes private context at the start of
  a chat, use it for that chat only. If he says he's unwell, tasks slide a day at a time without blame.

**Next up, in order (shift days Thu-Sun = ONE item of up to ~15 min; none of these confirmed done yet)**
- Red Rooster Cafe call (406-839-2884): offer the $100 website audit, mention flyers, then send the written pitch
  (written in another chat; Claude here hasn't seen it).
- Photograph the RX 580, check eBay SOLD prices, list it. Then the same for the Saitek X52.
- Mon 23 Nov: 6:35-7:35am homework hour (next real-research item, R1 recruiting), then Grandma's.
- Huion (was Tue 17 Nov; ask whether done): (1) copy art to Google Drive > My-Art, (2) note specs, (3) reset Windows
  with "Remove everything"; 2-3 sample flyers in Canva (folder "Samples") while it resets. Then photograph and list
  it (eBay boxed and insured, plus Craigslist) and photograph the smaller items.
- In-person visits to Hog Wild Cafe and Cajun Phatty's (was Wed 18 Nov; ask whether done).
- After that: one listing per shift day (motherboard + memory bundle, HD 7950, cooler). Behance profile once
  samples exist.

**Done 15-21 Nov**
- Instagram: Orbital Bot post PUBLISHED (16 Nov), with a two-tone icon made in his Canva (navy gear, white robot;
  Canva media MAHbGMMALq0; the first, colorful version is MAHbGE5uuL8).
- LinkedIn About section rewritten with him (16-17 Nov). He chose NOT to claim a studio or Orbital Roots, because no
  local work is done yet. Final text: student intro, Fernly (with survey link https://forms.gle/imywAMaeBzHXZFzSA),
  Orbital Bot, what he cares about, "happy to connect". Not confirmed saved on LinkedIn.
- LinkedIn skills reviewed: keep Design Thinking, Ideation, Human Factors, User Centered Design, User Experience,
  UX Design, UI, Usability; drop Sprint Retrospectives and Cross Platform Development (can't defend them yet);
  add User Research, Personas, User Journey Mapping, Competitive Analysis, Figma. Not confirmed applied.
- 18 Nov (other chat): Fernly has NO target date; plan files and brain.py fixed; deploy/fix-fernly-recaps.py written.
- 19 Nov: new rule "SERVER UPDATE WAITING" in my-focus.txt (see About this repo). 21 Nov: he ran the server update;
  nothing is waiting now. Not confirmed he ran the recap fix script (he was told how to check #ship-log).

**The bot**
- Sends today's whole list, one message per task with ✅ / ❌. Up to 3 new tasks Tue/Wed, 1 on other days
  (`MAX_NEW_TASKS` in bot.py). Unfinished tasks return marked 🔁 until ✅ or 🗑️. 8pm asks about open tasks.
  `today` shows the list. Records in `tasks` / `task_messages` in bridge.db (server only, not backed up; he knows).
- Timing gap: the server pulls my-focus.txt at 6:45am, after the 6:35am list, so file changes show a day later
  unless he runs `git pull` or `deploy/update.sh` himself.
- Command Hub as homepage = ROADMAP.md #7 (Jarvis), still locked. Don't start it without his go-ahead.

**Hardware being sold (eBay and Craigslist only; never Facebook)**
- Huion Kamvas Studio 22 (KS2201): full Windows pen computer, likely the most valuable item; has pen, adapter, stand,
  original box. Art rescue MUST come before the wipe. Selling because it's too heavy and bulky.
- ASUS ROG Strix RX 580 8GB (ROG-STRIX-RX580-O8G-GAMING); Saitek X52 stick + throttle (PS28), complete;
  ASUS M5A97 LE R2.0 motherboard (AM3+, no CPU) + Corsair Vengeance DDR3 8GB (2x4GB 1600MHz, CMZ8GX3M2A1600C9B) as a
  bundle; Sapphire HD 7950 3GB (SKU 11196-16); Cooler Master MasterLiquid Lite 240 (new, boxed).
- WD Blue 640GB (WD6400AAKS): Claude advised not selling. Not decided.
- Listings say "working when last used", never "tested". Drafts in drafts/hardware-listings.md (no prices); still
  write them out in full when he asks. Check eBay SOLD prices first; keep amounts out of this repo.

**Unknown (ask him once, don't nag)**
- Whether the Huion work and the two cafe visits happened.
- Whether the LinkedIn bot post, TikTok, Instagram Story and Discord survey posts went out.
- Whether the bot's morning lists have looked right since the 14 Nov fix.
- How many survey responses are in. Whether he DM'd the bot `step done` for template Step 1.

**Open questions**
- Survey only, or survey plus three 15-minute calls? Claude recommended both; not decided.
- Sell or keep the WD hard drive?

**Waiting on**
- Survey responses (unlocks the survey response watcher, ROADMAP.md #1).

**How he's doing**
- A hard stretch with a lot going on. Keep each day to its list, keep replies short and plain, push back when new
  things get added, and don't keep him up late on shift days.

**Reference**
- Drafts: drafts/ (LinkedIn bot post, LinkedIn survey post, TikTok survey post, hardware listings).
- Docs: Houseplant Follow-up Interview (15 min) https://claude.ai/artifact/GJZdEprt7jeesouKenBUqg
- Privacy: this repo is public. Keep pay figures, bill details and money amounts out of every file here.
- Cloud sessions: `docs.google.com` is allowed in the "Life Vison" environment so Claude can read the live survey form
  (https://forms.gle/imywAMaeBzHXZFzSA).

## How to work with Alexander
- Tends to start lots of things and not finish them: help finish, and push back on new scope.
- Checking in must be as easy as possible (one tap, no typing).
- Always write out the full click-by-click steps in every reply (his request, 10 Nov), including the text to
  paste. Never shorten to "see my last message" or "it's in the drafts file".
- Give a short plan before writing code. Build in small, testable steps.
- Ask before choosing anything that costs money. Prefer free or cheap.
- Never put keys in code: they live in `.env` (gitignored). **This repo is public.**
- Keep it simple. Working and finished beats clever.

## AI vs. Alexander's own work (his rule, 7 Nov 2026)
**AI drafts and coaches. Alexander decides, researches and designs.**

| Let AI do it | Alexander does it himself |
|---|---|
| Code, bots, setup | Figma work: every template step |
| First drafts of posts and plans | Talking to real people (interviews, usability tests) |
| Checklists, reminders, research summaries | Case study writing, in his own words |
| Feedback on his work | Design decisions and the reasons for them |

- Target for portfolio and career work: about **70% his own work, 30% AI** (AI as coach and reviewer).
- When he asks for design, research or case study work: coach, ask questions and review. Don't do it for him.
  Offer to give feedback on what he makes instead.
- Never present simulated research (the practice "sessions") as real. Label it practice.
- His test for any piece of work: "Could I explain and defend this in an interview, without notes?"
- Fewer new plans and documents; more hands-on progress. Push back when planning replaces doing.

## About this repo
- `bot.py` (Slack + schedule), `brain.py` (Claude calls), `storage.py` (SQLite `bridge.db`).
- Updates reach the server when Alexander runs `bash deploy/update.sh` over SSH (README has the steps).
- Whenever you save a bot update, add a WAITING line under "SERVER UPDATE WAITING" in my-focus.txt so the bot
  puts it on his list; remove the line when he says the update is run (his rule, 19 Nov).
- The server also runs `git pull` daily at 6:45am Denver time, but that does NOT restart the bot.
- Orbital Bot is the ONLY source of the daily task list. A separate Claude scheduled task
  ("Bridge daily check", 6:30am) only answers "Claude:" requests in Slack. Don't give it the task job back.
- Alexander tells the bot where he is with `class: ...` and `step done` (portfolio template's 9 fixed steps, in `bot.py`).
- Logging: everything goes in the bot (`log` shows the week). After a work session with Claude, if Alexander asks,
  DM the bot from his Slack account: "did: <what we did> · <time>" so it lands in his log.
- Timestamps (his request, 8 Nov): start every reply with the current Denver time, e.g. "🕐 Sun Nov 8, 2:45pm".
  Get it by running `TZ=America/Denver date "+%a %b %-d, %-I:%M%p"` (never guess the time).
  When he wraps up a session, add up the time from the first to the last timestamp, skipping any gap
  over 30 minutes as a break, and offer to log it to the bot as a check-in.
- Helper tools are added one at a time per ROADMAP.md (unlock-based). Push back on building one early.
- Safety rules: never post in #design-studio, never spend money/publish/email. Decisions are only final when Alexander confirms.
