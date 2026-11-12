# Build status

Written Thu 12 Nov 2026. A plain-language summary of what Alexander and Claude have built, and where each piece stands.

**How to read this:** anything marked *(from notes)* was built in earlier sessions and is recorded in the project notes; it was not re-tested this week. Anything marked *(unknown)* is something only Alexander can confirm.

---

## 1. Orbital Bot (the Slack accountability bot)

**What it does:** sends Alexander one task every morning in Slack, lets him check in with one tap, keeps a log of what he did, and posts a weekly recap.

**Finished and working** *(from notes)*
- Morning task at 7am, chosen from `my-focus.txt`
- One-tap ✅ / ❌ check-in, plus an 8pm check-in
- `log`, `hours this week`, time buttons, weekly goal
- `class: ...` to say where he is in the course; `step` and `step done` for the template steps
- `idea: ...` posts to #ideas; `decision: ...` is logged in #helm
- Monday recap posted to #ship-log
- Runs 24/7 on a Google Cloud server and restarts itself if it crashes

**Half-done**
- The template step wording was changed on 10 Nov (start fresh, no old wireframe). The change is on GitHub but **not yet live on the server**.
- The bot was renamed from "Bridge Bot" to "Orbital Bot" in the code. The Slack app itself still shows the old name.

**Left to do**
- Run one server update so the bot picks up the new step wording and name
- Rename the Slack app to "Orbital Bot" at api.slack.com
- Rename the Slack workspace to "Orbital Roots"

---

## 2. The daily plan file (`my-focus.txt`)

**What it does:** tells the bot what Alexander is working on, in what order, so it can pick the right task each day.

**Finished and working**
- Weekly rhythm: Monday homework hour, Tue/Wed main work blocks, Thu–Sun one 5-minute item
- Rewritten 10 Nov: Course 2 is paused at the value proposition; real research comes first (recruit, 15-minute chats, empathy maps, user groups, personas, journey maps, bias check)
- Recording rule: record every template session; editing and posting wait

**Left to do**
- Nothing to build. It needs updating whenever plans change.

---

## 3. Houseplant Care Survey (Fernly research)

**What it does:** a Google Form that collects real plant owners' stories, to feed the Fernly case study and the Course 2 class work.

**Finished and working**
- Live, with 14 questions, about 10 minutes long
- Improved on 10 Nov: three new questions added (how it felt, why they keep plants, what tools they use) and three typos fixed
- Optional last question collects contact details for a follow-up chat
- Posted on LinkedIn on 7 Nov

**Half-done**
- Recruiting push: TikTok carousel, Instagram Story, Discord post and direct messages *(unknown whether any were posted)*
- TikTok carousel: Alexander has his own four-slide file; Claude made a rough four-slide draft in Canva on 11 Nov for him to take apart

**Left to do**
- Get responses, then hold three to five 15-minute chats
- Optional: mark the four quick questions as required; add a "what's hard?" follow-up to the accessibility question

---

## 4. Figma portfolio template (first income bet)

**What it does:** a portfolio file for junior UX designers, to sell once it's finished. Built by Alexander in nine fixed steps; Claude coaches and reviews.

**Finished**
- Step 1: fresh Figma file with six pages (done 10 Nov)

**Left to do**
- Steps 2 to 9. Step 2 is next: colors, fonts, text styles and spacing.
- Goal: through Step 4 by 30 Nov
- Saved for Step 3: Claude makes a "five broken buttons" practice file, but only after Step 2 is done

---

## 5. Planning documents and drafts

**What they do:** hold the big-picture plan and ready-to-post text.

**Finished** *(from notes)*
- Orbital Roots Business Roadmap (8 tabs and a timeline)
- Command Hub
- Houseplant Follow-up Interview guide (15 minutes)
- Post drafts: Orbital Bot LinkedIn post, LinkedIn survey post, TikTok survey post

**Left to do**
- Orbital Bot LinkedIn post *(unknown whether posted)*

---

## 6. Helper tools roadmap (not built yet, on purpose)

Seven helper tools are planned, one at a time, each only when its unlock is reached. **None is built.**

| # | Tool | Unlocks when |
|---|---|---|
| 1 | Survey response watcher | The first survey response with contact details arrives |
| 2 | Case study review buddy | Alexander starts writing the Fernly case study |
| 3 | LinkedIn post drafter | The template reaches Step 4 |
| 4 | Job scout | Fernly plus one more case study are finished |
| 5 | Interview practice | The first job application is sent |
| 6 | Template buyer helper | The template is selling |
| 7 | Jarvis coordinator | The template is selling and three or more tools run |

---

## Deploying, connecting and paying

| Item | Where it stands |
|---|---|
| Bot server (Google Cloud) | Running *(from notes)*. One update is waiting: sign in to the server and run the update script. |
| Google Cloud cost | Free trial ends about 2 Feb 2027. After that, roughly $3.65 a month to keep it. The bill check is still not done. |
| Slack app and workspace names | Still to be renamed by Alexander |
| Claude's access to the survey | `docs.google.com` was allowed on 10 Nov so Claude can read the live form. It stays allowed in the "Life Vison" environment. |
| Canva | One free trial resize was used for the TikTok draft; one is left. Nothing was charged. |
| OBS (screen recording) | Installed and set up on Alexander's computer. Free. |

---

## Decisions made

- **AI drafts and coaches; Alexander decides, researches and designs.** Target is about 70% his own work.
- **One task a day, one tap to check in.** The bot is the only source of the daily task.
- **Finish before starting.** Helper tools unlock one at a time; nothing is built early.
- **Template starts fresh** in a new Figma file, with nothing brought over from the old project (10 Nov).
- **Record every template session; edit and post only after the template is done** (10 Nov).
- **Real research before class work.** Course 2 is paused until interviews and the redone personas and journey maps are in (10 Nov).
- **Full steps in every reply,** including the text to paste (10 Nov).
- **Ask before anything that costs money.** Never post, publish or email on Alexander's behalf.
- **Parked:** art store, budgeting app case study, Command Hub Lite case study.

---

## Open questions

1. **Survey only, or survey plus three short calls?** Claude recommends both. Not decided.
2. **How many survey responses are in?** Not yet checked.
3. **Team lead role:** answer expected this week. It decides how much side income is needed.
4. **Which recruiting posts went out?** TikTok, Instagram Story, Discord and the LinkedIn bot post are all unconfirmed.
5. **Did the bot get `step done` for Step 1?** If not, it still thinks he's on Step 1.
6. **Keep `docs.google.com` allowed for future sessions?**

## Next steps, in order

1. Prepare for the team lead conversation: know the per-hour raise needed before hearing their number.
2. Run the server update so the bot shows the new step wording.
3. Check the survey's Responses tab and report the count.
4. Template Step 2 in the next Tue/Wed morning block.
5. Shift days (Thu–Sun): one 5-minute item only.
