---
name: daybrief
description: >-
  Morning work briefing — "what does my day look like, in one scan?" Gathers
  today's calendar and emails needing attention (via connected Google MCP tools
  when available), recent git activity and unfinished work across your local
  repos, and a quick radar check on topics you track — all in parallel — and
  renders one compact, prioritized brief in chat. Every source is optional and
  degrades gracefully; strictly read-only (never sends email, never touches the
  calendar, never pushes). Use at the start of a workday or when the user asks
  "what's on today", "morning brief", "daybrief", "catch me up", "what should I
  focus on today". For deep research on one topic use pulse instead.
---

# daybrief — morning work briefing

`/daybrief [plain-language steering, e.g. "skip email", "just repos", "save it"]`

Answer one question in one scan: **what needs my attention today, in what
order?** Pull every source in parallel, compress hard, and lead with the
priorities — not the raw data. Target: the user reads it in under two minutes.

**Strictly read-only.** This skill never sends or replies to email, never
labels or archives anything, never accepts/declines invites, never commits or
pushes. It reports; the user acts.

## Step 0 — Config

Look for `daybrief-config.md` in the current working directory. It defines:

```markdown
# daybrief config
## Repos            # local paths, or workspace roots to scan one level deep
- D:\hop\code
## Radar topics     # 2–4 topics to check for movement
- claude code
- postgres
## Preferences
- timezone: Asia/Ho_Chi_Minh
- email: on        # on / off
- calendar: on     # on / off
- save: off        # on = also write brief to daybriefs/
```

If missing, **don't block**: run with what's inferable (current repo, no radar
topics) and offer to create the config at the end from what you learned. Honor
one-off steering from the arguments over the config.

## Step 1 — Gather all sources in parallel

Launch everything concurrently. Each source is independent and optional — if
its tools aren't connected or it errors, mark it "unavailable" in the brief
footer and move on. Never let one dead source stall the brief.

### Calendar (Google Calendar MCP, if connected)

- Load the tools via ToolSearch (e.g. `+calendar list events`) only if
  available; otherwise skip.
- Today's events in the user's timezone: time, title, attendees count, video
  link. Flag: the next event and minutes until it, overlaps, meetings with no
  agenda/description (prep risk), and the largest free block (deep-work slot).

### Email (Gmail MCP, if connected)

- Load via ToolSearch (e.g. `+gmail search threads`) only if available.
- Search unread + recent important (last ~48h). Bucket into: **needs reply**
  (direct questions/requests to the user), **FYI worth knowing**, and count the
  rest as noise (report the number only). Quote nothing sensitive at length —
  one line per thread, sender + ask.

### Repos (local git — always available)

- For each configured repo/workspace root (`Bash`, read-only commands only):
  commits since yesterday morning (`git log --since`), dirty working trees
  (`git status --short`), unpushed branches (`git log @{u}..` where an upstream
  exists), and — if `gh` is authenticated — open PRs awaiting the user's review
  or with fresh comments.
- Surface **unfinished work first**: dirty trees and unpushed commits are
  today's loose ends.

### Radar (keyless web — if topics configured)

- One Explore sub-agent for all topics together: HN Algolia last-24h search per
  topic + one web search pass. Return only items with real traction (points/
  comments) — **max 2–3 items total across all topics**, each one line + link.
  This is a glance, not a pulse; suggest `/pulse <topic>` if something is hot.

## Step 2 — Synthesize: priorities first

From all sources, derive **Top 3 focus items** for today. Ranking instinct:

1. Hard deadlines/meetings needing prep that is not done
2. Loose ends blocking others (unpushed work, PRs awaiting the user, unreplied
   direct asks)
3. The most important deep-work task, matched to the largest free block

Everything else is detail below the fold.

## Step 3 — Render the brief (chat-first)

Compact, scannable, in chat — this is the product. Skeleton:

```markdown
# Daybrief — <weekday> <YYYY-MM-DD>

## Focus today
1. <item — why it's #1, and when to do it (e.g. "in the 9–11 free block")>
2. ...
3. ...

## Calendar        (omit section if empty/unavailable)
- 10:00–10:30 <event> — <flag if no agenda / prep needed>
- Free block: 13:00–16:00 → deep work
## Inbox           (needs-reply first; omit if unavailable)
- <sender>: <one-line ask> → reply today?
- FYI: <one-liners> · <N> other unread (noise)
## Repos
- <repo>: <n> uncommitted files · branch <x> 2 commits unpushed
- PR #<n> awaiting your review (<repo>)
## Radar           (omit if no topics)
- <topic>: <headline> (<engagement>) [link]

Sources: calendar ✓ · email ✓ · repos ✓ · radar ✓/— <note any unavailable>
```

Dates/times from real commands (`date`), never guessed. If config `save: on`
(or the user asks), also write `daybriefs/<YYYY-MM-DD>.md` — no HTML for this
skill; a daybrief is ephemeral by design. Ensure `daybriefs/` and
`daybrief-config.md` are gitignored (personal data).

## Guardrails

- **Read-only, always.** No sending, replying, labeling, archiving, RSVP-ing,
  committing, or pushing — even if asked mid-brief; finish the brief first,
  then treat any action as a separate, explicit request.
- **Degrade gracefully.** A missing source is one footer note, not a failure.
- **Compress hard.** One line per item; counts instead of lists for noise. If
  the brief doesn't fit on one screen, it's too long.
- **Privacy.** Email/calendar contents stay in chat and local files only;
  saved briefs are gitignored. Never include message bodies at length.
- **Fast.** All sources in parallel; if a source hangs, drop it and note it.
  The brief should land in a couple of minutes, not ten.
