---
name: jobfit
description: >-
  Job-fit evaluation and discovery for job seekers — "find roles that fit me" and
  "should I apply to this one, and how do I tailor for it?" Two modes: DISCOVER
  searches job boards for openings matching your profile (title/level/location/
  remote), and EVALUATE takes job URLs/descriptions you provide. Either way it fans
  out parallel sub-agents to research compensation, company signal, and posting
  legitimacy, scores each role A–F across weighted dimensions, and emits a ranked
  decision brief with tailored CV-bullet suggestions. Remembers every role it has
  evaluated in jobfit-tracker.md so repeat runs skip what you already passed on.
  Keyless and human-in-the-loop:
  it never applies for you and discourages low-fit roles. Use when the user wants to
  find/source matching jobs, evaluate/triage job postings, decide whether a role is
  worth applying to, compare several openings, or tailor a CV to a JD — e.g. "find
  jobs that fit my CV", "/jobfit <url>", "is this job worth applying to", "score
  these roles against my CV". For general community buzz on a company, use pulse.
---

# jobfit — job-fit evaluation & tailoring

`/jobfit [url(s) | pasted JD(s)] [profile path/URL or plain-language steering]`

Answer one question per role: **is this worth applying to, and if so, how do I
tailor for it?** You ground every judgment in the actual posting + light research,
score against the user's real profile, and rank by fit — treating job search as a
**filtering problem, not a spray-and-pray volume game.**

## Two modes (auto-detect)

- **EVALUATE** — the user provides one or more job URLs/JDs. Score and tailor those.
- **DISCOVER** — the user provides **no** jobs (e.g. "find jobs that fit my CV").
  Source matching openings from the profile, let the user pick, then evaluate those.

If jobs are given → EVALUATE. If none are given → DISCOVER. If the user gives jobs but
also says "and find more like these," do both: evaluate the given ones and run Step 0b.

Adapted from the career-ops philosophy: *"A well-targeted application to 5 companies
beats a generic blast to 50."* This skill is deliberately **keyless** (native
`WebSearch`/`WebFetch` + free endpoints) and **human-in-the-loop** — it evaluates
and drafts, it **never submits**.

## Source-of-truth boundary (read first)

User-facing content and scores draw **only** from:

1. the **actual job posting(s)** the user provides, points to, or that DISCOVER surfaces,
2. the user's **profile** (see Step 0), and
3. what the user states **in this session**.

**Keywords get reformulated, never fabricated.** Never invent experience, skills,
metrics, titles, or achievements the profile doesn't support. Never pull "facts"
about the user from memory or cross-session inference. Tailoring = surfacing and
rephrasing what's genuinely there to mirror the JD's language.

## The tracker — memory across runs

Job search is a multi-week process; this skill must not start from zero every day.
Maintain `jobfit-tracker.md` in the working directory (**gitignored** — it holds
personal data). One row per role ever evaluated:

```markdown
| Date | Role @ Company | URL | Score | Verdict | Status | Notes |
|------|----------------|-----|-------|---------|--------|-------|
| 2026-07-04 | Senior BE @ Acme | <url> | 4.2/5 (B+) | APPLY | new | |
```

`Status` is the user's to update (`new` / `applied` / `interviewing` / `offer` /
`rejected` / `passed`) — never change it yourself, but read it.

- **At the start of every run:** read the tracker if it exists.
- **DISCOVER:** dedup candidates against the tracker before building the
  shortlist. Drop roles previously verdicted SKIP (mention the count); mark
  previously seen roles as "seen <date>, scored <x>" instead of re-researching
  them — unless the user explicitly asks for a re-evaluation.
- **EVALUATE:** if a role is already in the tracker, note the previous score in
  the brief and call out what changed (reposted? comp updated? profile updated?).
- **At the end of every run:** append the newly evaluated roles to the tracker
  (create the file if missing, keep it sorted newest-first) and tell the user
  it was updated. Never overwrite user-edited `Status`/`Notes` cells.

## Step 0 — Resolve the profile & inputs

**Profile.** In priority order:

1. A `jobfit-profile.md` or `cv.md` in the current working directory (check for it).
2. A source the user gives — a **local path** (`/jobfit <url> ./my-cv.md`) **or a URL**
   (LinkedIn, personal site, a hosted/Google-Doc CV). For a URL, `WebFetch` it, parse
   it into the fields below, and **save the result as `jobfit-profile.md`** in the
   working directory so future runs reuse it (tell the user where you saved it). If the
   URL is login-walled or unfetchable, say so and ask the user to paste it instead.
3. If none of the above, ask the user to paste their CV / a short profile. Offer to
   save it as `jobfit-profile.md` for next time.

When parsing a fetched/pasted profile, extract **only what's actually stated** — never
infer or embellish. From the profile, extract (and confirm if thin): target titles/archetype, seniority,
core skills, notable achievements *with metrics*, comp target (base/total, currency),
location + remote/timezone constraints, visa/work-authorization needs, and any
must-haves / dealbreakers. Record what's **missing** — gaps become scoring inputs and
questions, never fabrications.

**Jobs.** Accept one or many. For each URL, `WebFetch` the posting and extract:
title, company, location/remote, seniority, responsibilities, required vs. nice-to-have
skills, stated comp (if any), and posting date. For pasted JDs, parse directly. If a
posting can't be fetched (login-walled/expired), say so and ask the user to paste it.
**If no jobs were given, go to Step 0b (DISCOVER).**

Ask **1–2 questions only if** genuinely blocking (e.g. no comp target at all, or the
role archetype is ambiguous). Otherwise proceed and state assumptions in the brief.

## Step 0b — Discover roles (DISCOVER mode)

Source openings that match the profile, then let the user choose which to evaluate.
Discovery is **keyless** — `WebSearch`/`WebFetch` only, no scraping behind logins.

**Build the search terms from the profile:** target title(s) + close variants,
seniority/level, location, remote/timezone, and 2–3 signature skills. Honor any
plain-language steering ("only remote", "startups", "in Berlin", "focus on AI infra").

**Fan out discovery sub-agents concurrently** (one message, multiple `Agent` calls,
`subagent_type: "Explore"`) — each searches a different channel so coverage isn't
one search engine's opinion. Suggested channels (skip any that return nothing):

- **ATS boards** (where real reqs live): `WebSearch` with `site:` filters —
  `site:boards.greenhouse.io`, `site:jobs.ashbyhq.com`, `site:jobs.lever.co`,
  `site:*.workday*.com` — combined with `"<title>" <level> <location>`.
- **Aggregators / niche boards:** LinkedIn Jobs, Wellfound (startups), Otta, We Work
  Remotely / remote boards, and role-specific boards (e.g. AI, design, data).
- **General web:** `"<title>" jobs <location> <recency>` to catch careers pages.

Each sub-agent returns **structured candidates** — `title`, `company`, `location/remote`,
`url`, `source`, `posted` (if visible), and a one-line why-it-matches. Gather ~8–15
per channel before returning.

**Consolidate (main agent):** dedup by company+title+URL; drop obvious mismatches and
anything hitting a **hard dealbreaker** (visa/location/comp floor) — note how many were
filtered and why. Rank the survivors by a cheap first-pass fit read (title/level/
location/skill keywords vs. profile) — this is triage, not the full score.

**Confirm before deep research (human-in-the-loop, cost control):** present the ranked
shortlist as a compact table (title @ company · location · source · link · quick-fit
note) and ask the user which to fully evaluate — default to the **top ~5–8**. Only the
confirmed set goes through Steps 1–3; full research on 30 roles is wasteful and slow.
State the shortlist reflects only what these keyless searches surfaced — not the whole
market.

The confirmed roles then flow into Step 1 exactly like user-provided jobs.

## Step 1 — Fan out: parallel research sub-agents (per role)

For each role, spawn the relevant sub-agents **concurrently** (one message, multiple
`Agent` calls). Use `subagent_type: "Explore"` (read-only, fast) for fetch-heavy
research. Give each the company, role, location, and the user's comp/location targets.
Each returns **structured findings** with a `url` + 1–2 sentence `evidence` per claim;
mark anything unverified as such.

With many roles, do a cheap first-pass triage on the JD text alone and only fan out
full research for roles that clear a rough bar (e.g. no hard dealbreaker, plausible
seniority match) — note in the brief which roles were triaged out and why.

### Compensation sub-agent

- Extract stated comp from the JD. If absent, `WebSearch` for the range (levels.fyi,
  Glassdoor, Blind, job-board aggregates) for that title/level/location.
- **Caveat:** most comp sites are login-walled or JS-heavy — direct `WebFetch` of
  levels.fyi/Glassdoor/Blind pages usually fails. Prefer numbers that surface in
  `WebSearch` result snippets and public discussions (HN "who's hiring" threads,
  Reddit salary threads), and lower the confidence label accordingly.
- Return: a best-estimate range + confidence, and how it compares to the user's target.
  Label estimates clearly as estimates.

### Company-signal sub-agent

- `WebSearch` recent signals: funding/stage, growth or layoffs, Glassdoor/Blind
  sentiment, leadership/team stability, product/market position, notable recent news.
- Prefer primary/news sources and real employee threads over SEO content mills
  ("top companies to work for" listicles carry no signal).
- Return: 3–5 signal bullets (positive and negative), each with a source URL.

### Legitimacy sub-agent

- Assess whether the posting is real and actively hiring: posting age, whether it's a
  ghost/evergreen post, reposted-many-times pattern, vague-JD red flags, direct
  careers-page presence vs. only aggregators.
- Return: a legitimacy read (Likely active / Stale / Suspicious) + evidence.

### CV-alignment sub-agent (analysis, not research)

- Diff the JD's required + nice-to-have skills against the profile. Return: matched
  strengths (with the profile evidence), genuine gaps, and JD keywords the profile
  supports but doesn't currently surface (tailoring candidates — never invent).

If a source returns nothing usable, record it as **unknown** — do not fabricate.

## Step 2 — Score (main agent)

Score each role **0–10 per dimension**, then a weighted **/5 overall** mapped to a
letter. Default weights (tell the user they can override in `jobfit-profile.md`):

| Dimension          | Weight | What it measures                                            |
| ------------------ | ------ | ---------------------------------------------------------- |
| Role fit           | 30%    | Archetype/seniority/responsibility match to the profile    |
| CV alignment       | 25%    | Required-skill coverage vs. gaps (from CV-alignment agent)  |
| Compensation       | 20%    | Stated/estimated comp vs. the user's target                 |
| Company signal     | 15%    | Stage, trajectory, sentiment, stability                     |
| Legitimacy/logistics | 10%  | Real & active posting + location/remote/visa feasibility    |

Overall `/5 = (Σ weight × dim/10) × 5`, rounded to one decimal. Letters:
**A ≥ 4.5 · B ≥ 4.0 · C ≥ 3.0 · D ≥ 2.0 · F < 2.0.**

**Hard dealbreakers** (visa impossible, location impossible, comp far below floor)
cap the overall at **C** regardless of other scores, and are called out explicitly.

**Verdict per role:** `APPLY` (≥ 4.0) · `MAYBE` (3.0–3.9, list what would move it) ·
`SKIP` (< 3.0). Mirror career-ops: **discourage applying below 4.0** unless the user
has a specific reason, and say so.

## Step 3 — Emit the brief

Render this template **in chat**, then save it as `.md` and a self-contained `.html`
(see Output files). Cite research inline with linked URLs.

```markdown
# JobFit Report

**Run:** <YYYY-MM-DD> · **Roles evaluated:** <n> · **Profile:** <source>
**Comp target:** <target> · **Location:** <constraints>

## Ranking (best fit first)
| # | Role @ Company | Score | Letter | Verdict |
|---|----------------|-------|--------|---------|
| 1 | ...            | 4.2/5 | B+     | APPLY   |

## <Role> @ <Company> — <Score>/5 (<Letter>) — <VERDICT>
**Link:** <url> · **Location:** <...> · **Posted:** <...> · **Legitimacy:** <...>

**Scorecard**
- Role fit          <x>/10 — <one line>
- CV alignment      <x>/10 — <matched strengths / key gaps>
- Compensation      <x>/10 — <stated/estimated vs target> [source]
- Company signal    <x>/10 — <trajectory/sentiment> [source]
- Legitimacy/logistics <x>/10 — <read>

**Why this score / what would raise it:** <2–3 sentences>

**Tailoring suggestions (reformulate, never fabricate)**
- JD asks "<keyword>" → your profile has "<real evidence>" → surface as: "<bullet>"
- Gaps to acknowledge or address: <...>

(repeat per role, in ranked order)

## Dealbreakers & caveats
- <capped roles, unverifiable comp, stale postings, missing profile info>

## Sources
Flat list of every cited URL, grouped by role.
```

### Cover letter (opt-in)

If the user asks for one (never by default), draft a short cover letter (≤ 200
words) per APPLY-verdict role, built **strictly** from profile evidence under the
same no-fabrication rule — it mirrors the JD's language using only what the
profile supports. Save as `jobfit-reports/<slug>-cover-letter.md`. Drafting only:
it is never sent or submitted anywhere.

## Output files

Save to `./jobfit-reports/` in the current working directory:

- `jobfit-reports/<slug>-<YYYY-MM-DD>.md` — the markdown report verbatim.
- `jobfit-reports/<slug>-<YYYY-MM-DD>.html` — a **bespoke, distinctively designed**
  report. Self-contained: inline `<style>`, **no JavaScript**, links preserved, scores
  and scorecards as first-class visual elements, responsive, print-friendly.

`<slug>` = for one role, `company-role`; for a batch, `batch`. Lowercase,
non-alphanumerics → hyphens. Compute the date with a shell command (`date +%F`) — do
not guess. Create `jobfit-reports/` if needed and ensure `.gitignore` ignores it (the
report may contain personal salary/CV data — never commit it).

Tell the user the two saved paths at the end.

### Designing the HTML report

Invoke the **`frontend-design`** skill (Skill tool) to design the HTML for this
report:

- **Brief for the designer:** the subject is *a job seeker's apply/skip decision*; the
  audience is the candidate scanning "which of these is worth my effort"; the page's
  one job is to make the ranking, per-role scorecards, verdicts, and tailoring
  suggestions instantly scannable, with scores and verdicts as first-class visual
  elements (e.g. score meters, APPLY/MAYBE/SKIP badges).
- **Hard constraints (pass these to `frontend-design`):** single self-contained
  `.html`, **inline CSS only, no JavaScript, no external requests/CDNs/web fonts**
  (system font stack), keep all source links and scores, readable on mobile and when
  printed, and **must include every section** with the same content as the `.md`.
- Design changes presentation only — never the scores, evidence, or citations.

If `frontend-design` is unavailable, fall back to a clean self-contained no-JS layout.

## Guardrails

- **Human-in-the-loop.** Evaluate and draft only — **never submit an application**,
  never fill a form, never send an email on the user's behalf.
- **Filtering over volume.** Discourage applying below 4.0/5; a well-targeted 5 beats a
  generic 50. Say so when a role scores low.
- **No fabrication.** Every score → posting text, profile evidence, or a cited source.
  Reformulate keywords; never invent experience, skills, or metrics. In DISCOVER,
  never invent job listings — every candidate is a real fetched URL.
- **Honest coverage.** DISCOVER surfaces only what keyless searches return; say so and
  note how many candidates were filtered/dropped — never imply it's the whole market.
- **Keyless.** Native `WebSearch`/`WebFetch` + free endpoints only. Never ask for API
  keys. Degrade gracefully and mark unknowns honestly.
- **Privacy.** Reports and the tracker hold personal comp/CV data — save under
  `jobfit-reports/` / `jobfit-tracker.md`, keep both gitignored, and never post
  them externally.
- **Tracker is memory, not authority.** Read it to avoid rework; never let an old
  score silently override fresh evidence, and never edit the user's Status column.
- **Estimates are labeled.** Comp ranges pulled from the web are estimates with
  confidence, not the employer's offer.
