# skillhub

[Claude Code](https://claude.com/claude-code) skills I use every day — to research
like a skeptic, run my mornings, learn things properly, and ship code I can defend.

They started as prompts I kept retyping — research that trusted whatever ranked,
job hunts and briefings that started from zero. So I wrote each workflow down
once, gave it memory, and made it show its sources.

No API keys. No accounts. Nothing is sent, submitted, or pushed on your behalf —
except an `autopilot` run, which executes only the itemized charter you sign
(failure mode #7 below).

## Quickstart

```bash
git clone https://github.com/duthaho/skillhub.git
cp -r skillhub/.claude/skills/* ~/.claude/skills/    # or copy just the ones you want
```

Prefer staying current? Symlink instead — a `git pull` in the clone updates every install:

```bash
for s in skillhub/.claude/skills/*; do ln -s "$(realpath "$s")" ~/.claude/skills/; done
```

Then type any skill's command in Claude Code — pick one from [the skills](#the-skills)
below. That's the whole setup.

## Why these skills exist

I built these against the failure modes I kept hitting with coding agents.

### #1 — The agent believes the internet

Ask an agent what the community thinks of a tool and it returns the top of the
search results: SEO listicles, vendor marketing, "X vs Y in 2026" content farms.
That isn't what practitioners think; it's what ranks.

**The fix** is ranking by real engagement and citing everything:

- [`/pulse`](./.claude/skills/pulse/SKILL.md) — what people are actually saying
  about a topic, ranked by upvotes/points/stars, rumors flagged as unconfirmed.
- [`/verdict`](./.claude/skills/verdict/SKILL.md) — X-vs-Y technology decisions
  scored on weighted criteria, where one real post-adoption thread outweighs ten
  listicles and vendor claims are labeled as vendor claims.
- [`/jobfit`](./.claude/skills/jobfit/SKILL.md) — job postings scored against
  your actual CV, with the pay researched and ghost postings called out.
- [`/factcheck`](./.claude/skills/factcheck/SKILL.md) — the audit for documents
  that already *claim* to be cited: does each linked source actually assert the
  claim? A resolving link is not verification.

Every claim in every brief links to a real fetched source. If a source was
unreachable, the brief says so instead of improvising.

### #2 — Every session starts from zero

Run the same research next month and a stock agent re-discovers everything.
Ask it to continue yesterday's work and it has no yesterday.

**The fix** is cross-run memory in plain markdown — files you can read and edit
yourself:

- `/pulse` opens repeat runs with a **"Since last pulse"** delta: what's new,
  what faded, which rumors got confirmed.
- `/jobfit` keeps a tracker of every role it has scored, so tomorrow's search
  skips what you already passed on.
- `/verdict revisit` re-checks only a past decision's "revisit when" triggers
  and tells you whether it still stands.
- [`/daybrief`](./.claude/skills/daybrief/SKILL.md) carries yesterday's
  unfinished focus items into today and scores the follow-through.
- [`/learn`](./.claude/skills/learn/SKILL.md) remembers what you got wrong and
  re-drills it sessions later, spaced-repetition style.

### #3 — "Looks done" isn't done

Agents stop when the work *looks* finished. Tests get edited into passing,
TODOs stand in for behavior, and nobody ever actually ran the thing.

**The fix** is a coding loop where evidence gates every exit:

- [`/feature`](./.claude/skills/feature/SKILL.md) — sizes the change first (a
  one-sentence diff skips the ceremony), then spec by interview → a plan of
  2–5-minute tasks you approve → test-first execution with a checkpoint commit
  per task. State lives in `out/dev/<change>/`, so any later session resumes at
  the first unchecked task.
- [`/bugfix`](./.claude/skills/bugfix/SKILL.md) — deliberately lighter: no code
  until the bug reproduces on demand, no fix until the root-cause hypothesis is
  confirmed with evidence, and the original repro re-run as proof.
- [`/done`](./.claude/skills/done/SKILL.md) — the shipping gate. An evidence
  checklist with quoted output (including *actually running the change*),
  fake-green tripwires, and a fresh-context review by sub-agents that see only
  the diff and the spec. Verdict: SHIP, FIX FIRST, or NEEDS HUMAN.

### #4 — The agent acts on your behalf

The scariest failure mode isn't wrong output — it's an agent that applies to
the job, sends the email, or pushes the branch while you were getting coffee.

**The fix** is structural, not politeness: `/jobfit` evaluates and drafts but
never submits, `/daybrief` reads email and calendar but never replies,
`/done` commits locally but never pushes without an explicit yes, `/feature`
writes no code before you've approved the spec and the plan. You make the
calls; the skills make them informed. The one deliberate exception is
[`/autopilot`](./.claude/skills/autopilot/SKILL.md), which acts only on the
itemized charter you sign — the difference between an agent acting behind
your back and one executing a mandate is the mandate (see #7).

### #5 — You fix the agent, never the harness

Every session, the same corrections: don't use that command, run the linter
first, stop touching that folder. The agent apologizes, complies — and the
next session starts from the same blank slate. The corrections live in your
patience instead of your config.

**The fix** is a retro for the setup itself:
[`/tune`](./.claude/skills/tune/SKILL.md) mines your recent session
transcripts for repeated corrections, permission friction, and rules that get
ignored anyway, then proposes the one-line fix — a `CLAUDE.md` rule, an
allowlist entry, a script replacing re-derived steps — one finding at a time,
each with quoted evidence, applied only on your yes. It proposes deletions as
readily as additions, because a bloated config degrades the agent too.

### #6 — The agent edits before it understands

Point an agent at an unfamiliar repo and it starts changing code before it knows
where the entry points are, which layer owns what, or which conventions are
load-bearing. So it hallucinates an internal API, edits the wrong module, or
quietly breaks an invariant nobody wrote down.

**The fix** is to map the territory first:
[`/map`](./.claude/skills/map/SKILL.md) fans out read-only explorers along the
order that matters — entry points, build/test commands, architecture,
conventions, test layout — then distills a lean `AGENTS.md` at the repo root
where every claim points to a real file and nothing survives that isn't
load-bearing. It lands where Claude Code and other agents auto-load it, so the
next session — including `feature` and `bugfix` — starts oriented instead of
cold. You approve the file before it's written — a wrong map is worse than none.

### #7 — Autonomy without an arbiter

Let an agent run a whole task unsupervised and the failure isn't that it
stops — it's that it doesn't: reviewers rubber-stamp the implementer and
"done" becomes whatever the last model said it was. Removing the human
without installing another arbiter just makes the loop confident.

**The fix** is `/autopilot` — the whole
coding loop on one yes: map → spec (interviewing the codebase, not
you) → a plan hardened by a bounded critique loop of diverse critics →
GitHub issues → parallel worktree implementers → fresh-context review loops
— with the **test suite as the arbiter** at every gate (a repo without
tests gets a testing-bootstrap phase first). Every loop is bounded; a task
the pipeline can't settle honestly is **parked and reported**, never
guessed through. By default it stops at an open PR — merging stays yours —
and `--merge` hands over that last step too.

### #8 — The project builds in a vacuum

The five projects solving your same problem have already run the
experiments: their users' top-reacted feature requests are public demand
data, their changelogs are shipped answers, their gaps are open lanes.
Never looking sideways means re-learning all of it the slow way — or worse,
copying whatever a peer ships just because they shipped it.

**The fix** is [`/scout`](./.claude/skills/scout/SKILL.md) — reconnaissance
with a parity gate: find the peer repos, mine what their users actually
love (issue reactions, not stars), lay out the gap both ways — including
the moat you must not dilute — and verdict every candidate feature
ADOPT/ADAPT/SKIP/WATCH, where SKIP is the default and every ADOPT needs
evidence from *your* side. Ready ADOPTs hand off straight to `feature` or
`autopilot`.

## The skills

**Research** — outward-looking, cited, engagement-ranked
| Skill | One line | Try |
|---|---|---|
| [pulse](./.claude/skills/pulse/SKILL.md) | What the community is saying about anything, right now | `/pulse ollama last week` |
| [verdict](./.claude/skills/verdict/SKILL.md) | ADR-style tech decisions you can defend in review | `/verdict kafka vs nats, ops burden matters most` |
| [jobfit](./.claude/skills/jobfit/SKILL.md) | Find and score roles against your real CV | `/jobfit find senior backend roles, remote only` |
| [factcheck](./.claude/skills/factcheck/SKILL.md) | Do the cited sources actually say that? | `/factcheck report.md` |
| [scout](./.claude/skills/scout/SKILL.md) | What peer projects ship, and what's worth adopting | `/scout` |

**Day to day** — memory-first, read-only where it counts
| Skill | One line | Try |
|---|---|---|
| [daybrief](./.claude/skills/daybrief/SKILL.md) | Your day in one scan, priorities first | `/daybrief skip email` |
| [learn](./.claude/skills/learn/SKILL.md) | A tutor that remembers what you got wrong | `/learn rust ownership` |
| [tune](./.claude/skills/tune/SKILL.md) | Turn recurring agent mistakes into one-line fixes | `/tune` |

**The coding loop** — effort-scaled, evidence-gated
| Skill | One line | Try |
|---|---|---|
| [map](./.claude/skills/map/SKILL.md) | Orient the agent to an unfamiliar repo, as a lean AGENTS.md | `/map` |
| [feature](./.claude/skills/feature/SKILL.md) | Spec → plan → test-first build, resumable | `/feature add rate limiting` |
| [bugfix](./.claude/skills/bugfix/SKILL.md) | Reproduce → root-cause → prove, minimal diff | `/bugfix login 500s on empty password` |
| [done](./.claude/skills/done/SKILL.md) | The gate: prove it works, then ship | `/done` |
| [autopilot](./.claude/skills/autopilot/SKILL.md) | The whole loop on one yes — issues, parallel agents, review loops, PR | `/autopilot add rate limiting` |

## How the memory works

Everything the skills write lands in one folder in whatever project you run
them from:

```
out/
├── <skill>/    one folder per skill — its briefs, trackers, logs, and memory
│               (e.g. jobfit/tracker.md, learn/<topic>.md, tune/learnings.md)
└── dev/        the coding loop's per-change spec, plan, and log + bugfix-log.md
```

Plain markdown, human-readable, yours — to edit *and to commit*. The skills
read these files at the start of every run and update them at the end.
Whether they enter version control is your call: `out/dev/` plans and logs,
verdict briefs, and the bugfix log make good shared history; ephemeral
briefs don't need to. The exception is personal data — the skills that
write it (`jobfit`, `daybrief`, `tune`) keep their own folders gitignored,
so salary, email, and transcript quotes never land in a commit by accident.
(`/map` and `/autopilot` also write outside `out/`: a committed `AGENTS.md`
at your repo root, and issues, branches, and one PR per its charter.)

## What these skills won't do

- Apply to a job, send an email, accept an invite, or reply to anything.
- Push, open a PR, or publish without an explicit yes — a single
  `/autopilot` invocation is that yes, for exactly what its charter lists
  and nothing more.
- Use an API key, a paid service, or anything behind a login.
- Present a rumor as a fact, a vendor claim as a benchmark, or an estimate as
  an offer.
- Mark work "done" without having run it.

## FAQ

**Why keyless?** Setup friction kills daily-use tools. Everything here runs on
the agent's native web search/fetch plus free public endpoints (HN Algolia,
Reddit JSON, GitHub REST) — clone and go. The trade-off is honest degradation:
when a source is blocked, the brief says "unreachable" instead of pretending.

**Where does my data go?** Nowhere. Everything is local markdown in `out/` —
commit-optional, personal-data folders gitignored by default (see *How the
memory works*). Nothing is uploaded anywhere.

**Do these work outside Claude Code?** They're written as standard `SKILL.md`
files. The research skills lean on Claude Code's sub-agents and web tools;
other harnesses that support agent skills should run them with minor friction.

**Why not one big workflow framework?** Frameworks that own your whole loop are
hard to leave and harder to debug. These are independent skills that share
conventions — use one, use all, delete the ones you don't like.

## License

MIT — see [LICENSE](LICENSE).
