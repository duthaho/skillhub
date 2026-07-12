# AGENTS.md
<!-- mapped 2026-07-10 @ 68994a9 · regenerate with /map refresh -->

## What this is

A collection of 14 Claude Code skills (`.claude/skills/<name>/SKILL.md`) for
research, daily work, and a coding loop. No application code, no build system —
every skill is a markdown file with YAML frontmatter that Claude Code loads.
Entry point for a reader is `README.md`; entry point for a user is any skill's
slash command (e.g. `/pulse`).

## Build, test, run

There is nothing to compile and no test suite — this is a docs-only repo.
Validation is by inspection:

- **Skill frontmatter** must have `name` and `description`. The `description`
  has a **hard 1024-character limit** (measure it before committing — we've
  hit the limit twice: see `jobfit` and `scout` history). Check with:
  `python3 -c "import yaml; print(len(yaml.safe_load(open('.claude/skills/<s>/SKILL.md').read().split('---')[1])['description']))"`
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
  when the skill reaches that step (see `pulse`, `jobfit`, `verdict`, `scout`).
  The `SKILL.md` body loads on every trigger, so keep it lean.
- **State model:** skills write to `out/<skill>/` in whatever project they run
  in (`out/dev/` for the coding loop). See `README.md` "How the memory works".
- **The coding loop composes:** `map` → `feature`/`bugfix`/`refactor` → `done`,
  with `autopilot` wrapping the whole loop and `scout` feeding it candidates.

## Conventions & gotchas

- **Adding a skill touches two places:** create the folder, add one row to
  the skills table in `README.md`, and list it in a plugin's `skills` array in
  `.claude-plugin/marketplace.json`. Counts and command lists were deliberately
  removed so nothing else drifts (see README history around the map skill).
- **`out/` is commit-optional**, but `out/jobfit/`, `out/daybrief/`, and
  `out/tune/` stay gitignored — they hold personal data (`.gitignore`).
- **Guardrail voice:** rules are stated once in the body with a short "why",
  not repeated in a MUST-heavy Guardrails block. Keep rationale that changes
  behavior; cut rationale that only restates.
- **Git workflow:** feature branch → PR → merge (merge commits, not squash).
  Commit messages carry **no AI attribution**.

## Landmarks

- `README.md` — the front door; failure-mode narrative + skills table.
- `.claude/skills/map/SKILL.md` — the skill that generates this file.
- `.claude/skills/autopilot/SKILL.md` — the most complex skill (full pipeline).
- `.claude/skills/*/references/` — the progressive-disclosure templates.
- `LICENSE` — MIT.
