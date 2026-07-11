# Refactor brief template

Render in chat, then save to `out/refactor/<slug>-<YYYY-MM-DD>.md`.

```markdown
# Refactor survey — <repo> — <YYYY-MM-DD>

> Commit <short-sha> · test command: `<cmd>` (green / red / none — bootstrap needed)
> Signals: git churn <window> · bugfix log <found/absent> · AGENTS.md <found/absent>

## Since last survey
<!-- Only when tracker.md exists: verdicts due for revisit, evidence that
     changed, executed candidates since. Otherwise: "First survey." -->

## Hotspots

| File / area | Churn (commits, <window>) | Complexity signal | Note |
|---|---|---|---|

## Verdicts

| Candidate | Verdict | Evidence (locator) | Payoff | Effort |
|---|---|---|---|---|
<!-- REFACTOR / PREP / LEAVE / WATCH. LEAVE is the default; every
     REFACTOR/PREP cites churn, a recurring bug, or scheduled work. -->

## REFACTOR / PREP details
<!-- One block per promoted candidate: -->
### <candidate>
- **Problem:** <what hurts, file:line, the evidence>
- **Target shape:** <the simpler interface; if a pattern, why this one and
  what simpler shape was considered first>
- **Move sequence:** <named moves, in order>
- **Risk:** <what could break; test coverage state>
- **Run it:** `/refactor <candidate>`

## Too big to stay behavior-preserving
<!-- Real redesigns, phrased as ready handoffs: -->
- `/feature <item>` — <one line why>

## LEAVE / WATCH
- <candidate> — <reason it stays as-is / revisit trigger>

## Register delta
<!-- Rows added or changed in out/refactor/tracker.md this run. -->
```

Tracker rows (`out/refactor/tracker.md`):

```markdown
| Candidate | Verdict | Evidence | Date | Status |
|---|---|---|---|---|
| <area or goal> | REFACTOR | <locator + signal> | <YYYY-MM-DD> | proposed / in-progress / done (<sha>) |
```
