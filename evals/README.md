# Skill evals

Two layers, cheapest first. Run both before shipping a new or reworded skill.

## 1. Mechanical validation (seconds, deterministic)

```bash
python3 scripts/validate-skills.py
```

Checks every skill's frontmatter (name matches folder, description present and
≤1024 chars — the hard Claude Code limit this repo has hit five times),
marketplace coverage in both directions with no duplicates, a README table row
per skill, and that every `references/` file a skill mentions exists.

## 2. Trigger eval (one sub-agent, LLM-judged)

The description is a skill's **only** trigger surface; a skill that doesn't
trigger doesn't exist (the official skills repo's eval harness famously caught
a skill with a 0% trigger rate). `triggers.json` holds prompts a user might
actually type, each with the skill that should win — including routing pairs
where two skills plausibly match and the descriptions' routing hints
("for X use Y") must break the tie.

Run it from a Claude Code session in this repo:

1. `python3 scripts/validate-skills.py --descriptions > /tmp/descs.json`
2. Spawn a **fresh sub-agent** (no other context) with `/tmp/descs.json`,
   `evals/triggers.json`, and this instruction: *"For each prompt, pick the
   single skill whose description best matches, or `none`. Judge only from
   the descriptions. Return `prompt → picked` for every case."*
3. Compare picks to `expect`. **Any mismatch is a description bug** — fix the
   description (or the eval if the expectation was wrong), never the judge.

Honest caveat: the judge approximates Claude Code's real trigger mechanism —
same inputs (descriptions only), different code path. Treat a pass as strong
signal, not proof; treat any failure as real.
