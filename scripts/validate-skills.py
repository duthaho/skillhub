#!/usr/bin/env python3
"""Validate every skill's frontmatter and the repo's registration files.

Run from the repo root:  python3 scripts/validate-skills.py
Exit code 0 = all checks pass; 1 = failures (listed).

--descriptions  print {name: description} as JSON (input for evals/README.md's
                trigger eval) and exit.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
README = ROOT / "README.md"
DESCRIPTION_LIMIT = 1024  # hard Claude Code limit; hit 5x in this repo's history
DESCRIPTION_WARN = 950  # soft limit: room to edit before the hard wall
# Harness built-in slash commands — a skill named like one is shadowed or
# shadowing (see mattpocock/skills#483). Update when the harness adds commands.
BUILTINS = {
    "review", "code-review", "security-review", "verify", "init", "run",
    "simplify", "loop", "schedule",
}


def load_frontmatter(skill_md: Path):
    parts = skill_md.read_text().split("---")
    if len(parts) < 3:
        raise ValueError("no frontmatter block")
    return yaml.safe_load(parts[1])


def main() -> int:
    skills = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    frontmatters = {}
    failures = []
    warnings = []

    def check(ok: bool, msg: str):
        if not ok:
            failures.append(msg)

    # Per-skill frontmatter checks
    for skill in skills:
        skill_md = skill / "SKILL.md"
        label = skill.name
        if not skill_md.is_file():
            check(False, f"{label}: SKILL.md missing")
            continue
        try:
            fm = load_frontmatter(skill_md)
        except Exception as e:
            check(False, f"{label}: frontmatter unparseable ({e})")
            continue
        if not isinstance(fm, dict):
            check(False, f"{label}: frontmatter is not a mapping")
            continue
        frontmatters[label] = fm
        check(isinstance(fm.get("name"), str) and fm["name"],
              f"{label}: frontmatter 'name' missing")
        check(fm.get("name") == label,
              f"{label}: name '{fm.get('name')}' != folder name")
        check(label not in BUILTINS,
              f"{label}: name collides with a harness built-in command")
        desc = fm.get("description")
        check(isinstance(desc, str) and desc,
              f"{label}: frontmatter 'description' missing")
        if isinstance(desc, str):
            check(len(desc) <= DESCRIPTION_LIMIT,
                  f"{label}: description {len(desc)} chars > {DESCRIPTION_LIMIT}")
            if DESCRIPTION_WARN < len(desc) <= DESCRIPTION_LIMIT:
                warnings.append(f"{label}: description {len(desc)} chars "
                                f"> {DESCRIPTION_WARN} (soft limit — thin ice)")

        # Every references/ file the body mentions must exist
        body = skill_md.read_text()
        for ref in set(re.findall(r"references/[\w.-]+\.md", body)):
            check((skill / ref).is_file(), f"{label}: {ref} mentioned but missing")

    if "--descriptions" in sys.argv:
        if failures:  # an incomplete dump would silently corrupt the trigger eval
            print("refusing to dump: frontmatter failures first —", file=sys.stderr)
            for f in failures:
                print(f"  - {f}", file=sys.stderr)
            return 1
        print(json.dumps({k: v.get("description", "") for k, v in frontmatters.items()},
                         indent=2, ensure_ascii=False))
        return 0

    # Marketplace coverage, both directions, no duplicates
    try:
        market = json.loads(MARKETPLACE.read_text())
        listed = [s for p in market["plugins"] for s in p["skills"]]
        names = [Path(s).name for s in listed]
        skill_names = {s.name for s in skills}
        for s in listed:
            check((ROOT / s).is_dir(), f"marketplace: path {s} does not exist")
            check(Path(s).name in skill_names,
                  f"marketplace: {s} is not a skill under .claude/skills/")
        for n in set(names):
            check(names.count(n) == 1, f"marketplace: {n} listed {names.count(n)}x")
        for skill in skills:
            check(skill.name in names, f"marketplace: {skill.name} not in any plugin")
    except Exception as e:
        check(False, f"marketplace.json unreadable ({e})")

    # Every skill has a README table row (a prose mention doesn't count)
    table_rows = [l for l in README.read_text().splitlines() if l.startswith("|")]
    for skill in skills:
        link = f"./.claude/skills/{skill.name}/SKILL.md"
        check(any(link in row for row in table_rows),
              f"README: no table row links {skill.name}")

    for w in warnings:
        print(f"WARN: {w}")

    n_checks = f"{len(skills)} skills"
    if failures:
        print(f"FAIL ({n_checks}, {len(failures)} problem(s)):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS — {n_checks}: frontmatter valid, descriptions <= {DESCRIPTION_LIMIT}, "
          "marketplace coverage exact, README rows present, references intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
