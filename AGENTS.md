# AGENTS.md
<!-- mapped 2026-07-14 @ f7ff09b · regenerate with /map refresh -->

## What this is

A collection of Claude Code skills (`.claude/skills/<name>/SKILL.md`) for
research, daily work, and a coding loop. No application code, no build system —
every skill is a markdown file with YAML frontmatter that Claude Code loads.
Entry point for a reader is `README.md`; entry point for a user is any skill's
slash command (e.g. `/pulse`).

## Build, test, run

There is nothing to compile and no test suite — this is a docs-only repo.
Validation is by inspection:

- **Validate before committing:** `python3 scripts/validate-skills.py` —
  frontmatter (`name` = folder, no clash with harness built-ins, `description`
  present, hard 1024-char limit with a soft WARN above 950), marketplace
  coverage both ways, README rows, references/ integrity.
  `--descriptions` dumps the model-visible trigger surface (skills with
  `disable-model-invocation: true` excluded) for the eval below.
- **Reworded a description? Re-run the trigger eval** per `evals/README.md`
  (fresh judge sub-agent over `evals/triggers.json`); the authoring lint is
  §3 of that file. A description is a skill's only trigger surface.
- **Install** (from `README.md`): `/plugin marketplace add duthaho/skillhub`
  (plugins defined in `.claude-plugin/marketplace.json` — a new skill must be
  added to a plugin's `skills` list there too), or `cp -r`/symlink the folders.
- **Run** a skill by typing its command in Claude Code; skills lean on
  Claude Code's sub-agents and web tools, no external services.

## Architecture

- **Each skill is self-contained** in `.claude/skills/<name>/`. A user may copy
  one folder alone, so cross-skill conventions (date via `date +%F`, `out/`
  creation, keyless degradation) are **duplicated by design** — don't try to
  factor them into a shared file.
- **Progressive disclosure via `references/`:** heavy output templates and
  design briefs live in `.claude/skills/<name>/references/*.md`, loaded only
  when the skill reaches that step (blueprint, jobfit, pulse, refactor, scout,
  verdict). The `SKILL.md` body loads on every trigger, so keep it lean.
- **State model:** skills write to `out/<skill>/` in whatever project they run
  in (`out/dev/` for the coding loop; shipped change folders move to
  `out/dev/archive/`). See `README.md` "How the memory works".
- **The coding loop composes:** `map` → `feature`/`bugfix`/`refactor` → `done`,
  with `autopilot` wrapping the whole loop, `scout` feeding it candidates, and
  `blueprint` as map's human-facing sibling.

## Conventions & gotchas

- **Adding a skill touches three places** plus the eval: create the folder,
  add one row to the skills table in `README.md`, list it in a plugin's
  `skills` array in `.claude-plugin/marketplace.json`, and add trigger cases
  to `evals/triggers.json` (cases first, TDD-style). Counts and command lists
  were deliberately removed so nothing else drifts.
- **autopilot is user-invoked-only** (`disable-model-invocation: true`): its
  description is human-facing and exempt from trigger evals — don't "fix" it
  by adding trigger phrases back, and don't expect the model to route to it
  (other skills suggest the *user* run `/autopilot`).
- **`out/` is commit-optional**, but `out/jobfit/`, `out/daybrief/`, and
  `out/tune/` stay gitignored — they hold personal data (`.gitignore`).
- **Guardrail voice:** rules are stated once in the body with a short "why",
  not repeated in a MUST-heavy Guardrails block. Keep rationale that changes
  behavior; cut rationale that only restates.
- **Git workflow:** feature branch → PR → merge; history carries both merge
  commits and squashes. Commit messages carry **no AI attribution**; adapted
  techniques credit their source repo + license in the commit body.

## Landmarks

- `README.md` — the front door; failure-mode narrative + skills table.
- `scripts/validate-skills.py` + `evals/` — the whole test story.
- `.claude/skills/map/SKILL.md` — the skill that generates this file.
- `.claude/skills/autopilot/SKILL.md` — the most complex skill (full pipeline).
- `.claude/skills/*/references/` — the progressive-disclosure templates.
- `out/scout/tracker.md` — adoption verdicts + WATCH triggers (if committed).
- `LICENSE` — MIT.
