---
name: bugfix
description: >-
  Lightweight bug-fixing loop — reproduce → root-cause → fix test-first →
  verify — deliberately separate from the heavyweight feature workflow so
  small fixes don't drag a spec-and-plan process behind them. Demands a
  deterministic reproduction before any code changes, a stated root-cause
  hypothesis confirmed with evidence (never a shotgun fix), a failing test
  that captures the bug, and the original repro re-run as proof. Keeps a
  one-line-per-bug log in out/dev/bugfix-log.md and checks it first, so
  recurring bugs get recognized instead of re-diagnosed. Use when the user
  reports something broken, failing, throwing, or flaky, or asks to fix a
  bug — e.g. "/bugfix login 500s on empty password", "fix this error",
  "this test is flaky", "why is X crashing". If the fix turns out to need
  real design work, hand off to feature; the shipping gate is done.
---

# bugfix — reproduce, root-cause, fix, prove

`/bugfix <symptom / error / failing thing>`

Answer one question: **why does this actually happen, and what's the minimal
fix that provably removes it?** The order is non-negotiable — reproduce
before diagnosing, diagnose before fixing, prove after fixing. A fix without
a confirmed root cause is a guess wearing a commit message.

## Step 0 — Check the log

Read `out/dev/bugfix-log.md` if it exists. A similar symptom fixed before is
the best diagnostic head start there is — past root causes cluster ("we've
had three timezone bugs in this module"). Mention any match. Also skim recent
`git log` — a bug that appeared recently usually shipped recently.

## Step 1 — Reproduce (before touching any code)

Turn the report into a **deterministic reproduction**: a command, a failing
test invocation, a curl, a click path — something that fails on demand and
will pass when the bug is dead.

- Capture the exact error output now; it's the baseline the fix is judged
  against.
- **Can't reproduce it?** Stop. Report what was tried, what extra information
  would help (versions, data, environment, timing), and ask. Do not fix code
  you can't watch fail — "fixed" without a repro is unfalsifiable.
- Flaky bug? Reproduce the *flakiness* (run N times, note the failure rate)
  so the fix can be judged the same way.

## Step 2 — Root-cause (hypothesis, then evidence)

Work from symptom back to cause; don't pattern-match a fix onto the error
message.

1. Read the failing path — the actual code, not just the stack trace.
2. **State a hypothesis out loud**: "X fails because Y, so Z should show W."
3. Confirm it with evidence: a log line, a debugger/print probe, a minimal
   experiment that isolates the suspect. The hypothesis must *predict*
   something you then observe.
4. Wrong? Say so, log what was ruled out, form the next hypothesis.
   **Two dead hypotheses → step back**: re-read the repro, question an
   assumption, or bring the user the map of what's been ruled out. Grinding
   the same theory harder is not investigation.

**No shotgun fixes**: changing several things at once until the symptom stops
proves nothing and usually hides a second bug. One hypothesis, one change,
one observation.

## Step 3 — Fix, test-first

1. **Write the failing test that captures the bug** — it should fail for the
   bug's exact reason, at the root-cause layer (unit test at the broken
   function beats an end-to-end flake).
2. Apply the **minimal fix** for the root cause. Not the refactor the code
   deserves, not the defensive `try/except` around the symptom — the cause.
3. Test green, then the **full suite** green (the fix must not buy one green
   at the cost of another).

If the minimal fix keeps growing — touching many files, changing behavior,
demanding design decisions — stop and say so: this is a **feature** wearing a
bug costume. Hand off to `/feature` with the diagnosis as its input; the
root-cause work is not wasted, it's the spec's first paragraph.

## Step 4 — Prove and record

- Re-run the **original reproduction** from Step 1 — show before/after
  output. This is the proof; the new test alone is not (it might test the
  wrong thing).
- Quick blast-radius check: who else calls the changed code? Any caller
  relying on the old (broken) behavior gets flagged, not silently re-broken.
- Append one line to `out/dev/bugfix-log.md`
  (create it if missing; date via `date +%F`):

```markdown
| Date | Symptom | Root cause | Fix | Test |
|------|---------|-----------|-----|------|
| 2026-07-05 | login 500 on empty password | None reaches bcrypt in auth.py | guard + 400 | test_auth.py::test_empty_password |
```

- Commit per the repo's convention, with a message naming the root cause,
  not just the symptom. For anything beyond a
  trivial diff, offer the **done** gate before shipping.

## Guardrails

- **Repro first, always.** No reproduction → no code changes, no exceptions.
- **Cause, not symptom.** Never suppress the error (swallowed exception,
  widened timeout, retry loop) unless the user explicitly chooses that
  trade-off — and then log it as suppression, not a fix.
- **Never weaken tests.** Deleting/loosening an assertion to get green is a
  new bug. An existing test blocking the fix is information for the user.
- **Minimal diff.** Improvements spotted along the way are mentioned, not
  bundled — a bugfix diff should read as exactly one repair.
- **Honest log.** The bugfix log records what the cause *was*, even when
  embarrassing — it's the cross-run memory that makes bug #3 in the same
  module a 5-minute fix.
