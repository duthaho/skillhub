---
name: pulse
description: >-
  Community-pulse research on any topic — "what are people saying about X right
  now." Fans out parallel sub-agents across web search, Hacker News, Reddit, and
  GitHub; ranks findings by real engagement (points/upvotes/stars/comments);
  flags rumors; and writes a cited brief to chat plus saved .md and .html files.
  Use when the user wants the current community conversation / recent buzz /
  sentiment / "last 30 days" view on a person, product, project, or concept —
  e.g. "/pulse <topic>", "what's the buzz on X", "what are people saying about
  X lately", "research recent discussion on X". For exhaustive, adversarially
  fact-checked web reports, prefer the deep-research skill instead.
---

# pulse — community-pulse research

`/pulse <topic> [window/flags in plain language]`

Answer one question: **what is the community actually saying about this topic right
now, and what's resonating?** You ground every claim in a real source and rank by
real engagement — not by what a search engine's editors surfaced.

This skill is deliberately **keyless**: it uses only the agent's native `WebSearch`
/ `WebFetch` tools plus free public endpoints. Never ask the user for API keys.

## How this differs from `deep-research`

- `deep-research` = exhaustive, adversarially fact-checked, authoritative web report.
- `pulse` = fast, recent, **community/engagement-ranked** snapshot. Optimize for
  "what's being discussed and how much it's resonating," not for proving every claim.

If the user clearly wants an exhaustive verified report, suggest `deep-research`.

## Inputs

- **Topic** (required): a person, product/company, project/repo, or concept/event.
- **Window** (optional, plain language): default **last 30 days**. Honor overrides
  like "last week", "past 6 months", "this year". Record the resolved window.
- Any other plain-language steering ("focus on Reddit", "ELI5", "just the drama").

## Step 0 — Resolve scope (ask only if genuinely ambiguous)

Run immediately for clear topics. Ask **1–2 quick questions only if**:

- the name maps to multiple plausible entities (e.g. a common name, an ambiguous
  product), **or**
- there's no obvious angle and the result would likely research the wrong thing.

Otherwise proceed and state your assumptions in the brief header.

**Auto-detect the topic type** and weight sources accordingly:

| Detected type        | Source emphasis                                      |
| -------------------- | --------------------------------------------------- |
| Person (dev/tech)    | GitHub (velocity) + Hacker News + web + Reddit      |
| Person (non-tech)    | Web + Reddit (skip/deprioritize GitHub)             |
| Product / company    | Reddit + web + Hacker News (GitHub if it's a tool)  |
| Project / repo / tool| GitHub + Hacker News + Reddit + web                 |
| Concept / event      | Web + Hacker News + Reddit (skip GitHub)            |

Do light **entity resolution** first when useful (e.g. the canonical subreddit, the
GitHub `owner/repo` or username, the official site) so sub-agents search the right
handles rather than guessing.

## Step 1 — Fan out: parallel source sub-agents

Spawn the relevant source sub-agents **concurrently** (one message, multiple `Agent`
calls). Skip sources the topic type deprioritizes. Give each the topic, resolved
entities, and the time window. Each sub-agent must return **structured findings**:
for every item — `title`, `url`, `source`, `engagement` (the raw metric + its kind),
`date`, and a 1–2 sentence `snippet`. Then it deepens its **top 2–3** items
(below). Each gathers ~8–10 candidates before deepening.

Use `subagent_type: "Explore"` (read-only, fast) for fetch-heavy sources.

### Web sub-agent

- Use `WebSearch` with several query variations (topic + "news"/"review"/"discussion"
  + recency terms). Prefer results inside the window.
- Engagement proxy: publication prominence + how often a story recurs across results.
- Deepen top 2–3: `WebFetch` the article and extract the core claim + any quotes.

### Hacker News sub-agent (free Algolia API — most reliable signal)

- Search: `WebFetch` →
  `https://hn.algolia.com/api/v1/search?query=<TOPIC>&tags=story&numericFilters=created_at_i>UNIX_START`
  (compute `UNIX_START` from the window; for relevance over recency use
  `/search` instead of `/search_by_date`).
- `engagement` = `points` and `num_comments`.
- Deepen top 2–3: fetch `https://hn.algolia.com/api/v1/items/<objectID>` and pull the
  highest-signal top-level comments (the actual takes).

### Reddit sub-agent (best-effort, keyless)

- Try `WebFetch` on public JSON:
  `https://www.reddit.com/search.json?q=<TOPIC>&sort=top&t=month` (map `t` to the
  window: `week`/`month`/`year`), and/or `https://www.reddit.com/r/<SUB>/search.json?...&restrict_sr=1`.
- `engagement` = `ups` (upvotes) and `num_comments`.
- Deepen top 2–3: fetch the thread JSON (`<permalink>.json`) and pull top comments.
- **Fallback on 403/empty:** use `WebSearch` for `site:reddit.com <topic>` and
  `WebFetch` the threads. **Note in the brief that Reddit was reached via fallback.**

### GitHub sub-agent (keyless REST, 60 req/hr)

- Repo/tool topic: `https://api.github.com/search/repositories?q=<TOPIC>&sort=stars`,
  then for the chosen repo pull recent `commits`, `releases`, and open/closed PR
  counts to gauge shipping velocity.
- Person topic: resolve the username, then `users/<u>` + recent `users/<u>/events`
  (public) to summarize what they're shipping.
- `engagement` = stars, recent commit/PR/release cadence.

If a source returns nothing usable after its fallback, record it as **unreachable**
— do not fabricate.

## Step 2 — Synthesize (main agent)

1. **Dedup & cluster:** merge the same story appearing across sources into one
   cluster; keep the strongest engagement signal and cite all sources in the cluster.
2. **Rank** clusters by engagement (normalize across kinds — treat HN points, Reddit
   upvotes, GitHub stars, and comment volume as comparable "this resonated" signals;
   weight recency within the window).
3. **Flag reliability:** explicitly tag rumors, speculation, single-source claims,
   and contested items as **Disputed/Unconfirmed**. Never let a rumor read as fact.
4. **Pull Best Takes:** 2–5 genuinely notable/clever/viral quotes, each attributed
   with its source and engagement.

## Step 3 — Emit the brief

Render this template **in chat**, then save it as `.md` and a self-contained `.html`
file (see Output files). Cite inline as `([source], <engagement>)` with a linked URL.

```markdown
# Pulse: <Topic>

**Window:** <resolved window> · **Run:** <YYYY-MM-DD> · **Type:** <detected type>
**Sources reached:** Web ✓ · Hacker News ✓ · Reddit ✓/fallback/�—  · GitHub ✓/�—

## TL;DR
- 3–5 bullets: the headline state of the conversation right now.

## Key Developments
For each ranked cluster:
### <Cluster headline>
What happened + why it resonates. Inline citations with engagement metrics and links.
Merge cross-source coverage here.

## Best Takes
> "<quote>" — <author/handle>, <source> (<engagement>) [link]

## Disputed / Unconfirmed
- <claim> — why it's uncertain, who's pushing back. (omit section if empty)

## Sources
Flat list of every cited URL, grouped by source, with engagement metrics.
```

If the user asked for ELI5, prepend a short plain-language summary above TL;DR.

## Output files

Save to `./pulse-briefs/` in the current working directory:

- `pulse-briefs/<slug>-<YYYY-MM-DD>.md` — the markdown brief verbatim.
- `pulse-briefs/<slug>-<YYYY-MM-DD>.html` — a **bespoke, distinctively designed**
  brief (see below). Self-contained: inline `<style>`, **no JavaScript**, links
  preserved, engagement metrics visible, responsive, print-friendly.

`<slug>` = topic lowercased, non-alphanumerics → hyphens. Compute the date with a
shell command (e.g. `date +%F`) — do not guess it. Create `pulse-briefs/` if needed,
and ensure `.gitignore` ignores it (the skill setup adds this once).

Tell the user the two saved paths at the end.

### Designing the HTML brief

Do **not** pour the content into a fixed template — every brief gets its own design.
Invoke the **`frontend-design`** skill (Skill tool) and have it design the HTML for
this specific brief, treating the topic as the design subject:

- **Brief for the designer:** the subject is *this topic and its community
  conversation*; the audience is someone scanning "what's happening now"; the page's
  one job is to make the TL;DR, ranked Key Developments, Best Takes, and
  Disputed/Unconfirmed items instantly scannable, with engagement metrics as
  first-class visual elements. Ground the aesthetic in the topic's own world (a dev
  tool, a person, a cultural event each suggest a different visual identity) so no two
  briefs look alike.
- **Hard constraints (pass these to `frontend-design`):** single self-contained
  `.html` file, **inline CSS only, no JavaScript, no external requests/CDNs/web
  fonts** (system font stack), keep all source links and engagement numbers, must be
  readable on mobile and when printed, and **must include every section** of the
  brief template (header with sources-reached, TL;DR, Key Developments, Best Takes,
  Disputed/Unconfirmed, Sources) with the exact same content as the `.md`.
- Render the markdown brief content faithfully into that design — design changes the
  presentation, never the facts, citations, or engagement metrics.

If the `frontend-design` skill is unavailable, fall back to a clean self-contained
dark-mode, no-JS layout — but prefer the designed output.

## Guardrails

- **Keyless only.** Never request or use API keys. Degrade gracefully.
- **No fabrication.** Every claim → a real fetched source. Mark unreachable sources
  honestly in the header.
- **Recency discipline.** Stay inside the window; if a pivotal item is older, include
  it but label it as background/older context.
- **Engagement is the spine.** Order by what resonated, show the numbers inline.
- **Speed over exhaustiveness.** This is a pulse, not a dossier — for the latter,
  point to `deep-research`.
