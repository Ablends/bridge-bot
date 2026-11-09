# Notes for Claude (read before helping)

## Who this is for
- Alexander, who runs a small design-led product business called **Orbital Roots** (renamed from "The Bridge" on 9 Nov 2026;
  the Slack workspace may still show the old name). Public-facing work goes under his own name.
- New to design and new to programming: explain things in plain language, and say exactly what to click or type.
- Works long shifts Thu–Sun (only ~5-minute tasks those days). Mon–Wed are the main work days.

## Current priorities (in order, updated 7 Nov 2026)
1. Keep this bot running (it's live on a Google Cloud e2-micro server, see README).
2. Weekly rhythm: Mon 6:35-7:35am Course 2 homework (then Grandma's all day); Tue/Wed mornings = template step + Course 2;
   Tue 1-3pm / Wed 12-1:30pm = design gig or Fernly interview; Thu-Sun shifts = one ~5 min class item.
   Side income: small design gigs (one at a time), see the roadmap doc's Design Gigs tab.
3. Figma portfolio template = first income bet (fixed 9-step plan). Nov 30 goal: through Step 4 (realistic pace). YouTube Shorts paused until the template is done.
4. Coursera Course 2 done (~Nov 17), then Course 3. Fernly moves at the class's pace:
   Problem, Research and Process by Nov 30; full publish after later courses.
5. Parked: art store (tablet files may be lost), budgeting app + Command Hub Lite case studies, Jarvis (see ROADMAP.md).
- The big-picture plan: "Orbital Roots — Business Roadmap" doc (https://claude.ai/artifact/6ijMsf4deXz5n7gDuSCohL)
  and the Command Hub (https://claude.ai/artifact/5bf2WRi8FG1SwNzsGgvx99). my-focus.txt drives the daily task.

## Where we left off (handoff, 9 Nov 2026)
- Done: bot upgrades live on the server (one-tap ✅/❌, 8pm check-in, `log`, time buttons, gig category, class:/step done).
  Survey posted on LinkedIn (7 Nov). Calendar matches the weekly rhythm. Roadmap doc has 8 tabs + a timeline.
- Not yet done by Alexander: Slack app rename to "Orbital Bot" (api.slack.com) + one server update for the new name;
  Slack workspace rename to "Orbital Roots"; Google Cloud bill check; reply + DM to the plant-app person who
  commented on the LinkedIn survey post (drafts were given in chat; keep Fernly/app ideas private).
- Next up: Tue 10 Nov 9:15am template Step 1; Tue 1-3pm survey recruiting push (TikTok, Instagram Story, texts to 5
  friends); Tue: Orbital Bot LinkedIn post (drafts/linkedin-bot-post.md); Thu: message 3 people about design gigs.
- Drafts: drafts/ (LinkedIn bot post, LinkedIn survey post with link, TikTok survey post).
- Docs: Houseplant Follow-up Interview (15 min) https://claude.ai/artifact/GJZdEprt7jeesouKenBUqg
- Waiting on: survey responses (unlocks the survey response watcher, ROADMAP.md #1); team lead role decision.

## How to work with Alexander
- Tends to start lots of things and not finish them: help finish, and push back on new scope.
- Checking in must be as easy as possible (one tap, no typing).
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
- The server also runs `git pull` daily at 6:45am Denver time, but that does NOT restart the bot.
- Orbital Bot is the ONLY source of the daily task. A separate Claude scheduled task
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
