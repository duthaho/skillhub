# skillhub

A collection of [Claude Code](https://claude.com/claude-code) skills for research,
daily work, and shipping code. They started as prompts I kept retyping, so I wrote each
one down once, gave it memory, and made it cite its sources.

Keyless: no API keys, no signups. Skills run on Claude Code's own web and
sub-agent tools plus free public endpoints. Nothing is sent, submitted, or pushed
on your behalf. (One skill, `/autopilot`, can push branches and open a PR, but only
the specific actions you authorize when you start it. See #7.)

Written and refined with Claude's help; the design opinions are mine.

## Quickstart

Inside Claude Code, as plugins (pick the groups you want):

```
/plugin marketplace add duthaho/skillhub
/plugin install coding-loop@skillhub     # map, feature, bugfix, refactor, done, autopilot
/plugin install research@skillhub        # pulse, verdict, jobfit, factcheck, scout
/plugin install daily@skillhub           # daybrief, learn, tune
```

Or copy the files, if you'd rather own and edit them:

```bash
git clone https://github.com/duthaho/skillhub.git
cp -r skillhub/.claude/skills/* ~/.claude/skills/    # or copy just the ones you want
```

Prefer to stay current? Symlink instead, so a `git pull` updates every install:

```bash
for s in skillhub/.claude/skills/*; do ln -s "$(realpath "$s")" ~/.claude/skills/; done
```

Then type a skill's command in Claude Code. **New here?** Run [`/map`](./.claude/skills/map/SKILL.md)
on a repo you know or [`/done`](./.claude/skills/done/SKILL.md) on an uncommitted
change. Both are read-mostly and show you the style in about a minute. The
[`AGENTS.md`](AGENTS.md) in this repo is a real example of what `/map` produces.
Full list is [below](#the-skills).

## Why these skills exist

Each one answers a problem I kept hitting with coding agents.

### #1 — Agents trust whatever ranks

Ask an agent what people think of a tool and it hands back the top search results:
SEO listicles, vendor pages, "X vs Y in 2026" content farms. That's what ranks,
not what practitioners actually say.

The fix is to rank by real engagement and cite every claim:

- [`/pulse`](./.claude/skills/pulse/SKILL.md): what people are saying about a
  topic, ranked by upvotes/points/stars, with rumors flagged as unconfirmed.
- [`/verdict`](./.claude/skills/verdict/SKILL.md): X-vs-Y technology decisions
  scored on weighted criteria, where one real post-adoption thread outweighs ten
  listicles and vendor claims are labeled as such.
- [`/jobfit`](./.claude/skills/jobfit/SKILL.md): job postings scored against your
  actual CV, with the pay researched and ghost postings called out.
- [`/factcheck`](./.claude/skills/factcheck/SKILL.md): the audit for documents that
  already *claim* to be cited. Does each linked source actually assert the claim?
  A resolving link is not verification.

Every claim in every brief links to a source that was actually fetched. If a source
was unreachable, the brief says so instead of improvising.

### #2 — Every session starts from zero

Run the same research next month and a stock agent re-discovers everything. Ask it
to continue yesterday's work and it has no yesterday.

The fix is cross-run memory in plain markdown you can read and edit:

- `/pulse` opens repeat runs with a **"Since last pulse"** delta: what's new, what
  faded, which rumors got confirmed.
- `/jobfit` keeps a tracker of every role it has scored, so tomorrow's search skips
  what you already passed on.
- `/verdict revisit` re-checks a past decision's "revisit when" triggers and tells
  you whether it still stands.
- [`/daybrief`](./.claude/skills/daybrief/SKILL.md) carries yesterday's unfinished
  focus items into today and scores the follow-through.
- [`/learn`](./.claude/skills/learn/SKILL.md) remembers what you got wrong and
  re-drills it sessions later, spaced-repetition style.

### #3 — "Looks done" isn't done

Agents stop when the work *looks* finished. Tests get edited into passing, TODOs
stand in for behavior, and often nobody actually ran the thing.

The fix is a coding loop where evidence gates every exit:

- [`/feature`](./.claude/skills/feature/SKILL.md): sizes the change first (a
  one-sentence diff skips the ceremony), then spec by interview, a plan of
  2–5-minute tasks you approve, and test-first execution with a checkpoint commit
  per task. State lives in `out/dev/<change>/`, so a later session resumes at the
  first unchecked task.
- [`/bugfix`](./.claude/skills/bugfix/SKILL.md): deliberately lighter. No code until
  the bug reproduces on demand, no fix until the root cause is confirmed with
  evidence, and the original repro re-run as proof.
- [`/done`](./.claude/skills/done/SKILL.md): the shipping gate. An evidence checklist
  with quoted output (including *actually running the change*), fake-green tripwires,
  and a fresh-context review by sub-agents that see only the diff and the spec.
  Verdict: SHIP, FIX FIRST, or NEEDS HUMAN.

### #4 — Agents act on your behalf

The worst failure isn't a wrong answer. It's an agent that applies to the job, sends
the email, or pushes the branch while you were getting coffee.

The fix is structural. `/jobfit` evaluates and drafts but never submits. `/daybrief`
reads email and calendar but never replies. `/done` commits locally but never pushes
without a yes. `/feature` writes no code before you approve the spec and the plan.
The one exception is [`/autopilot`](./.claude/skills/autopilot/SKILL.md), which acts
only on the checklist you sign when you start it (see #7).

### #5 — You fix the agent, never the setup

Every session, the same corrections: don't use that command, run the linter first,
stop touching that folder. The agent complies, and the next session starts from the
same blank slate. The corrections live in your patience instead of your config.

The fix is a retro for the setup itself. [`/tune`](./.claude/skills/tune/SKILL.md)
mines your recent session transcripts for repeated corrections, permission friction,
and rules that get ignored anyway, then proposes a one-line fix (a `CLAUDE.md` rule,
an allowlist entry, a script) one finding at a time, each with quoted evidence,
applied only on your yes. It proposes deletions as readily as additions, since a
bloated config degrades the agent too.

### #6 — Agents edit before they understand

Point an agent at an unfamiliar repo and it changes code before it knows where the
entry points are, which layer owns what, or which conventions are load-bearing. So
it invents an internal API, edits the wrong module, or breaks an invariant nobody
wrote down.

The fix is to map the repo first. [`/map`](./.claude/skills/map/SKILL.md) fans out
read-only explorers along the order that matters (entry points, build and test
commands, architecture, conventions, test layout), then writes a lean `AGENTS.md`
where every claim points to a real file. Claude Code and other agents auto-load it,
so the next session starts oriented. You approve the file before it's written. This
repo's own [`AGENTS.md`](AGENTS.md) was generated this way.

### #7 — Autonomy with no arbiter

Let an agent run a whole task unsupervised and the risk isn't that it stops. It's
that it doesn't: reviewers rubber-stamp the implementer, and "done" becomes whatever
the last model said. Removing the human without adding another check just makes the
loop confident.

The fix is [`/autopilot`](./.claude/skills/autopilot/SKILL.md), the coding loop on
one yes: map, then spec (by interviewing the codebase), then a plan hardened by a
bounded critique loop, then GitHub issues, then parallel worktree implementers, then
fresh-context review loops. The **test suite is the arbiter** at every gate; a repo
without tests gets a testing-bootstrap phase first. Every loop is bounded, and a task
the pipeline can't settle honestly is parked and reported rather than guessed
through. By default it stops at an open PR so you merge; `--merge` hands over that
step too. (This is the newest and most ambitious skill, and the one to try last.)

### #8 — Building in a vacuum

The projects solving your same problem have already run the experiments. Their users'
top-reacted feature requests are public demand data, their changelogs are shipped
answers, their gaps are open lanes. Never looking sideways means re-learning it the
slow way, or copying whatever a peer ships just because they shipped it.

The fix is [`/scout`](./.claude/skills/scout/SKILL.md), reconnaissance with a parity
gate: find the peer repos, mine what their users actually want (issue reactions, not
stars), lay out the gap both ways (including the strengths you should keep), and
verdict each candidate feature ADOPT/ADAPT/SKIP/WATCH. SKIP is the default, and every
ADOPT needs evidence from your side, not just "a peer has it." Ready ADOPTs hand off
to `feature` or `autopilot`. And for the vacuum *before* a project exists,
[`/priorart`](./.claude/skills/priorart/SKILL.md) asks the upstream question — does
this idea already exist? — and answers with a locator-backed landscape and exactly one
verdict: Build / Fork / Contribute / Use / Investigate first.

## The skills

**Research** — outward-looking, cited, engagement-ranked
| Skill | One line | Try |
|---|---|---|
| [pulse](./.claude/skills/pulse/SKILL.md) | What the community is saying about anything, right now | `/pulse ollama last week` |
| [verdict](./.claude/skills/verdict/SKILL.md) | ADR-style tech decisions you can defend in review | `/verdict kafka vs nats, ops burden matters most` |
| [jobfit](./.claude/skills/jobfit/SKILL.md) | Find and score roles against your real CV | `/jobfit find senior backend roles, remote only` |
| [factcheck](./.claude/skills/factcheck/SKILL.md) | Do the cited sources actually say that? | `/factcheck report.md` |
| [scout](./.claude/skills/scout/SKILL.md) | What peer projects ship, and what's worth adopting | `/scout` |
| [priorart](./.claude/skills/priorart/SKILL.md) | Does your idea already exist? Landscape + one verdict | `/priorart a CLI that syncs dotfiles` |
| [ideate](./.claude/skills/ideate/SKILL.md) | Generate ideas worth pursuing, then verdict each EXPLORE/PARK/DROP | `/ideate` |

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
| [blueprint](./.claude/skills/blueprint/SKILL.md) | Human-facing architecture docs + mermaid diagrams, every arrow verified | `/blueprint the payment flow` |
| [feature](./.claude/skills/feature/SKILL.md) | Spec → plan → test-first build, resumable | `/feature add rate limiting` |
| [bugfix](./.claude/skills/bugfix/SKILL.md) | Reproduce → root-cause → prove, minimal diff | `/bugfix login 500s on empty password` |
| [refactor](./.claude/skills/refactor/SKILL.md) | Evidence-picked refactors in small behavior-preserving steps | `/refactor` |
| [done](./.claude/skills/done/SKILL.md) | The gate: prove it works, then ship | `/done` |
| [autopilot](./.claude/skills/autopilot/SKILL.md) | The whole loop on one yes: issues, parallel agents, review loops, PR | `/autopilot add rate limiting` |
| [newskill](./.claude/skills/newskill/SKILL.md) | Add or repair a skill across all four registration surfaces, validator-green | `/newskill fix ideate` |

## How the memory works

Everything the skills write lands in one folder in whatever project you run them from:

```
out/
├── <skill>/    one folder per skill: its briefs, trackers, logs, and memory
│               (e.g. jobfit/tracker.md, learn/<topic>.md, tune/learnings.md)
└── dev/        the coding loop's per-change spec, plan, and log + bugfix-log.md
```

Plain markdown, human-readable, yours to edit and to commit. The skills read these
files at the start of every run and update them at the end. Whether they enter
version control is your call: `out/dev/` plans and logs, verdict briefs, and the
bugfix log make good shared history; ephemeral briefs don't need to. Personal data is
the exception. The skills that write it (`jobfit`, `daybrief`, `tune`) keep their own
folders gitignored, so salary, email, and transcript quotes never land in a commit by
accident. (`/map` and `/autopilot` also write outside `out/`: a committed `AGENTS.md`
at the repo root, and issues, branches, and one PR per its charter.)

## What these skills won't do

- Apply to a job, send an email, accept an invite, or reply to anything.
- Push, open a PR, or publish without an explicit yes. A single `/autopilot`
  invocation is that yes, for exactly what its charter lists and nothing more.
- Require an API key or a paid service. (`/daybrief` can optionally read a connected
  Google account for calendar and email, but works without one and degrades
  gracefully.)
- Present a rumor as a fact, a vendor claim as a benchmark, or an estimate as an offer.
- Mark work "done" without having run it.

## FAQ

**Are these tested, or just written?** They're prompt-and-convention skills, not
compiled code, so "testing" means running them and reading the output. The
coding-loop skills (`map`, `feature`, `done`) were used to build this repo itself;
the [`AGENTS.md`](AGENTS.md) here is real `/map` output. The research skills degrade
honestly when a source is blocked (they say "unreachable" rather than inventing one),
which is the main thing to check when you run them. Try one on a topic you know well
and judge the sourcing yourself.

**Why keyless?** Setup friction kills daily-use tools. Everything runs on the agent's
native web search/fetch plus free public endpoints (HN Algolia, Reddit JSON, GitHub
REST), so you clone and go. The trade-off is honest degradation: when a source is
blocked, the brief says "unreachable" instead of pretending.

**Where does my data go?** Nowhere. Everything is local markdown in `out/`,
commit-optional, with personal-data folders gitignored by default (see *How the
memory works*). Nothing is uploaded.

**Do these work outside Claude Code?** They're standard `SKILL.md` files. The research
skills lean on Claude Code's sub-agents and web tools; other harnesses that support
agent skills should run them with minor friction.

**Why not one big workflow framework?** Frameworks that own your whole loop are hard
to leave and harder to debug. These are independent skills that share conventions:
use one, use all, delete the ones you don't like.

## License

MIT — see [LICENSE](LICENSE).
