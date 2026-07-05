# skillhub

A small collection of [Claude Code](https://claude.com/claude-code) skills I use and maintain.

Each skill teaches Claude Code a repeatable workflow you trigger with a slash command.
They all share the same approach: no API keys, sources are always cited, and nothing is
sent or submitted on your behalf — the skills do the research and drafting, you make the calls.

Everything the skills write — briefs, reports, trackers, learning logs — lands under a
single gitignored `out/` folder (`out/pulse/`, `out/verdicts/`, `out/jobfit/`,
`out/daybrief/`, `out/teach/`), so personal data never gets committed and there's one
folder to browse, back up, or serve.

## Skills

### /pulse — community research

Find out what people are actually saying about a topic right now. It searches the web,
Hacker News, Reddit, and GitHub in parallel, ranks what it finds by real engagement
(upvotes, points, stars, comments), and writes up a short brief with the best takes and
any rumors flagged as unconfirmed.

```
/pulse ollama
/pulse "claude code" last week, focus on Reddit
```

Saves a markdown brief and an HTML version to `out/pulse/`. Run it again on
the same topic later and it opens with a "Since last pulse" delta — what's new,
what faded, and which rumors got confirmed or debunked.

### /jobfit — job evaluation and discovery

Two ways to use it:

- Give it your CV or profile and it finds matching roles on job boards.
- Give it a job posting and it tells you whether it's worth applying to.

Either way it researches the pay, the company, and whether the posting is real, scores
each role A–F, and suggests how to tailor your CV — without ever applying for you.

```
/jobfit find senior backend roles that fit my CV, remote only
/jobfit https://boards.greenhouse.io/acme/jobs/123 ./cv.md
```

Roles are scored on fit, CV match, pay, company health, and how legitimate the posting is,
then marked APPLY, MAYBE, or SKIP. Saves a report to `out/jobfit/` and keeps a
tracker of everything it has evaluated, so tomorrow's search skips
what you already passed on and remembers what you applied to.

### /verdict — technology decisions

Choosing between two databases, frameworks, or build-vs-buy? Give it the options and
your context (scale, team, constraints) and it researches each one the same way —
project health, what practitioners report after adopting it, benchmarks, licensing —
then scores them on weighted criteria and writes an ADR-style recommendation you can
bring to a design review. Vendor claims are labeled as such, and close calls are
called ties, not false winners.

```
/verdict postgres vs mongodb for an event-sourced order system, team knows SQL
/verdict kafka vs nats, ops burden matters most
/verdict revisit verdicts/postgres-vs-mongodb-2026-07-04.md
```

Saves the brief to `out/verdicts/`. Every brief ends with "revisit when" triggers —
and `revisit` cheaply re-checks just those triggers later and tells you whether
the verdict still stands.

### /daybrief — morning briefing

One command to start the day: today's calendar and emails that need a reply (if your
Google account is connected), uncommitted and unpushed work across your repos, your
open todos (a `TODO.md` and/or GitHub issues assigned to you), and a quick check on
a few topics you track. It leads with the three things to focus on, fits on one
screen, and is strictly read-only — it never sends, replies, or pushes.

```
/daybrief
/daybrief skip email, just repos
```

With `save: on` it also remembers yesterday's brief: unfinished focus items carry
over to today, and it tells you how much of yesterday actually got done.

Configure repos, tasks, and tracked topics in `daybrief-config.md` (it offers to
create one).

### /teach — personal tutor

Learn anything in short, remembered sessions. The first run interviews you (what do
you want to be able to *do*, where are you starting from, how long per session) and
proposes a syllabus you can edit. Every session after that opens with a quick recall
quiz on what you learned before, teaches exactly one new unit with examples hooked
onto your background, and ends with a check — what you miss comes back in a later
session until you get it right.

```
/teach rust ownership
/teach                 # list topics in progress and what's due
/teach quiz sql        # recall-only session, no new material
```

Progress, quiz scores, and weak spots live in `out/teach/<topic>.md` — a plain
markdown file you can read and edit yourself. Fast-moving topics get a web check
before the syllabus is drafted, so you're not taught last year's API.

## Installing

These are standard Claude Code skills — copy the ones you want into your skills folder.

For a single project:

```bash
git clone https://github.com/duthaho/skillhub.git
cp -r skillhub/.claude/skills/jobfit your-project/.claude/skills/
```

Or make them available everywhere:

```bash
cp -r skillhub/.claude/skills/* ~/.claude/skills/
```

Prefer staying up to date? Symlink instead of copying, and a `git pull` in the
clone updates every install:

```bash
for s in skillhub/.claude/skills/*; do ln -s "$(realpath "$s")" ~/.claude/skills/; done
```

Then type `/pulse`, `/jobfit`, `/verdict`, `/daybrief`, or `/teach` in Claude Code.
That's it — no keys or setup.

## License

MIT — see [LICENSE](LICENSE).
