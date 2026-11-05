# Notes for Claude (read before helping)

## Who this is for
- Alexander, who runs a small design-led product business from a Slack workspace called **The Bridge**.
- New to design and new to programming: explain things in plain language, and say exactly what to click or type.
- Works long shifts Thu–Sun (only ~5-minute tasks those days). Mon–Wed are the main work days.

## Current priorities (in order)
1. Keep this bot running (it's live on a Google Cloud e2-micro server, see README).
2. Finish the Coursera UX course project (Course 2) before starting Course 3.
3. Fernly case study (target: publish 30 Nov 2026).
4. Figma portfolio template product, one step at a time (fixed 9-step plan).
5. Budgeting app + Command Hub Lite case studies are **parked**.

## How to work with Alexander
- Tends to start lots of things and not finish them: help finish, and push back on new scope.
- Checking in must be as easy as possible (one tap, no typing).
- Give a short plan before writing code. Build in small, testable steps.
- Ask before choosing anything that costs money. Prefer free or cheap.
- Never put keys in code: they live in `.env` (gitignored). **This repo is public.**
- Keep it simple. Working and finished beats clever.

## About this repo
- `bot.py` (Slack + schedule), `brain.py` (Claude calls), `storage.py` (SQLite `bridge.db`).
- Updates reach the server when Alexander runs `bash deploy/update.sh` over SSH (README has the steps).
- The server also runs `git pull` daily at 6:45am Denver time, but that does NOT restart the bot.
- Bridge Bot is the ONLY source of the daily task. A separate Claude scheduled task
  ("Bridge daily check", 6:30am) only answers "Claude:" requests in Slack. Don't give it the task job back.
- Alexander tells the bot where he is with `class: ...` and `step done` (portfolio template's 9 fixed steps, in `bot.py`).
- Safety rules: never post in #design-studio, never spend money/publish/email. Decisions are only final when Alexander confirms.
