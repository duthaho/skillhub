# skillhub

A small collection of [Claude Code](https://claude.com/claude-code) skills I use and maintain.

Each skill teaches Claude Code a repeatable workflow you trigger with a slash command.
They all share the same approach: no API keys, sources are always cited, and nothing is
sent or submitted on your behalf — the skills do the research and drafting, you make the calls.

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

Saves a markdown brief and an HTML version to `pulse-briefs/`.

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
then marked APPLY, MAYBE, or SKIP. Saves a report to `jobfit-reports/`.

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
```

Saves the brief to `verdicts/`.

### /daybrief — morning briefing

One command to start the day: today's calendar and emails that need a reply (if your
Google account is connected), uncommitted and unpushed work across your repos, and a
quick check on a few topics you track. It leads with the three things to focus on,
fits on one screen, and is strictly read-only — it never sends, replies, or pushes.

```
/daybrief
/daybrief skip email, just repos
```

Configure repos and tracked topics in `daybrief-config.md` (it offers to create one).

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

Then type `/pulse`, `/jobfit`, `/verdict`, or `/daybrief` in Claude Code.
That's it — no keys or setup.

## License

MIT — see [LICENSE](LICENSE).
