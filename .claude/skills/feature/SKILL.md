---
name: feature
description: >-
  End-to-end feature workflow around the agent — spec by interview, a plan of
  2–5-minute tasks, test-first execution with checkpoint commits, then an
  evidence-gated finish. Effort-scaled: a one-sentence diff skips straight to
  implementation; a real feature gets spec.md → plan.md → task-by-task TDD,
  with all state in out/dev/<change>/ so any later session resumes at the
  first unchecked task. Human-in-the-loop: the spec and the plan are approved
  (and editable) before any code is written, and nothing ships without the
  done gate. Use when the user wants to build, add, or implement a feature or
  start non-trivial coding work — e.g. "/feature add rate limiting",
  "implement X", "build a Y that Z", "resume the <change> feature". For
  fixing something broken use bugfix; for just the end-of-session shipping
  gate use done; to run this whole loop end-to-end without approval stops
  use autopilot.
---

# feature — spec → plan → build, effort-scaled

`/feature <description>` — start (or resume) a piece of work
`/feature` — list changes in flight under `out/dev/`

Answer one question: **what is the smallest process that gets THIS change
built correctly?** The two documented failure modes of workflow suites are
opposite: heavyweight gates firing on typo-sized changes, and freestyle
sessions shipping unverified scope creep. This skill scales the process to
the change — never the other way around.

## Step 0 — Size the change (the escape hatch comes first)

Classify before doing anything else, and say which tier you picked:

- **Trivial** — you could describe the exact diff in one sentence (typo, rename,
  config value, one-line fix). → No spec, no plan, no folder. Make the change,
  then run the **done** gate's evidence checklist inline. Stop here.
- **Small** — one focused change, ≤ ~3 files, design obvious. → Skip the spec
  interview; write the plan directly **in chat** for approval, execute with the
  Step 3 rules, finish with **done**. No folder unless the user wants to pause
  and resume.
- **Standard** — anything multi-file, multi-session, or with real design
  decisions. → Full loop below.

If the user explicitly asks for the full treatment ("spec this out"), honor it
regardless of size. When genuinely unsure between tiers, pick the smaller one
and say so — the plan contract (Step 3) catches scope growth and upgrades the
tier if needed.

## The change folder — state across sessions

`out/dev/<change-slug>/` (`<slug>` = short change name, lowercased, hyphens;
committing the folder is the user's call — it makes good shared history):

- `spec.md` — what & why, agreed acceptance criteria. Written once, then stable.
- `plan.md` — the task checklist. Checkboxes are flipped as tasks complete;
  never delete a task, strike it with a reason instead.
- `log.md` — **append-only** progress journal: one line per task/session
  (`date · task · result · commit`). Decisions and surprises go here too.

**Resume ritual (any session, before touching code):** read `log.md`, then
`plan.md`, then `git log --oneline -10`; run the project's test command as a
smoke check; continue at the first unchecked task. Never trust residual
conversation memory over the files. When the change ships, move the folder to
`out/dev/archive/` — done changes are history, not clutter.

## Step 1 — Spec by interview (standard tier)

Interview the user with **one compact question set** (`AskUserQuestion`) —
only what the request leaves genuinely open: the goal as observable behavior,
what's explicitly **out of scope**, acceptance criteria, and the **end-to-end
check** that will prove it works (a command, a flow to click through, a curl).
Read the repo's `CLAUDE.md`/`AGENTS.md` (the map skill writes the latter) and
nearby code first so questions are informed, not generic.

Write `spec.md` — short, self-contained, someone-else-could-build-from-it —
and get explicit approval. **The spec is the contract for the review in
done**; vagueness here becomes an argument later.

## Step 2 — Plan as executable tasks

Explore first (read the relevant code; use Explore sub-agents for unfamiliar
areas so the main context stays clean), then write `plan.md`:

- Each task is **2–5 minutes of work**, names the **exact files** it touches,
  and carries its **own verification step** (the command that proves this task
  done). Small enough that a fresh sub-agent with no context could execute one
  from its text alone.
- Order by dependency; put the riskiest/unknown-most task first, not last.
- End with the spec's end-to-end check as the final task.

Show the plan, invite edits, get approval. Human edits to `plan.md` are
welcome at any point — re-read it at every task boundary.

## Step 3 — Execute: test-first, checkpoint, log

Per task, in order:

1. **Red:** write the failing test that captures this task's behavior. Run it;
   confirm it fails for the right reason.
2. **Green:** the minimal code to pass. Run the task's verification step.
3. **Commit:** checkpoint with a descriptive message following the repo's
   convention. Tick the checkbox, append to `log.md`.

Hard rules for the whole phase:

- **The plan is the scope contract.** Discovered a needed change outside the
  current task? Add it to `plan.md` as a new task (say so) — don't just do it.
  If additions start reshaping the design, stop and revisit the spec with the
  user.
- **Never edit or delete an existing test to make it pass.** A test blocking
  you is information — bring it to the user.
- **No new TODOs, skipped tests, or commented-out code** as a way of getting
  to green.
- **Two failed attempts at the same task → stop.** Log what was tried, pick a
  different approach or ask — don't grind the same wall.

Long plan and the user wants speed? Offer **sub-agent execution**: dispatch a
fresh agent per task (the plan's task text is its full briefing), review each
diff as it lands. Default remains main-agent execution — it's simpler and
usually right.

## Auto mode — under autopilot

When the **autopilot** skill drives this loop (or the user explicitly asks
for auto mode), the approval gates become self-approvals **on the record**:
Step 1 interviews the codebase instead of the user — questions it can't
answer become stated assumptions in `spec.md` — and Step 2's approval is a
bounded critique loop of parallel critics instead of a human yes. Every
gate decision lands in `log.md` with its reason. Everything else — sizing,
TDD, the scope contract, the hard rules — is unchanged.

## Step 4 — Finish

Run the **done** skill: evidence checklist, fresh-context two-stage review,
then the commit/PR proposal. A feature is not finished because the last
checkbox is ticked — it's finished when done says ship and the user agrees.
Then archive the change folder.

## Guardrails

- **Process serves the change.** State the tier; never make a one-line fix
  wait for a spec, and never let a multi-file change skip the plan.
- **Approval gates are real.** Spec and plan wait for an explicit yes —
  they're the user's cheapest chance to steer. (In auto mode the gate is a
  critic loop plus a logged rationale — the wait is removed, not the gate.)
- **Evidence over claims** at every level: failing test seen failing, passing
  test seen passing, verification commands actually run.
- **Files over memory.** `plan.md`/`log.md` are the truth; re-read at task
  boundaries, update the moment reality changes.
- **Honest logging.** `log.md` records failures and reversals too — the next
  session needs the real story, not a highlight reel.
