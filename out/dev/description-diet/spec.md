# Spec: description diet + invocation audit

2026-07-14 · from scout verdicts (out/scout/mattpocock-skills-2026-07-13.md;
adapted from writing-great-skills + invocation.md, MIT). Interview: 2
decisions put to user (1a, 2a), defaults accepted.

## Why

- The 1024-char description limit has been hit 5× historically; today
  refactor sits at 1023, scout/learn/jobfit at 1020, tune at 1019 — one
  adjective from breakage, no room to improve any of them.
- All 15 descriptions load into context every turn (~3.5k tokens); context
  tax is this repo's own stated moat concern.
- mattpocock #483 (12👍) shows a skill name colliding with a harness
  built-in; we ship into the same namespace with no check.

## What (observable behavior)

1. **autopilot goes user-invoked-only**: frontmatter gains
   `disable-model-invocation: true`; its description is rewritten
   human-facing and short (~300 chars: what it is, its commands, its safety
   posture — no trigger-phrase lists). Rationale: a skill that signs a
   charter and pushes branches should require a deliberate `/autopilot`,
   never auto-trigger.
2. **Five descriptions dieted** — refactor, scout, learn, jobfit, tune —
   each to ≤900 chars via the 3-check lint: (1) leading word first,
   (2) one trigger per branch (synonyms collapsed), (3) identity already in
   the body cut. Meaning and routing hints preserved; bodies untouched.
3. **validate-skills.py** gains: (a) a name-clash check against a curated
   BUILTINS set (review, code-review, security-review, verify, init, run,
   simplify, loop, schedule — comment: update when the harness adds
   commands), failing on collision; (b) a non-failing WARN for any
   description >950 chars (early smoke before the hard limit).
4. **evals/README.md** gains a short "description authoring lint" section:
   the 3 checks above + the negation rule (every "never X" names its
   replacement) and no-op pruning (delete sentences that don't change
   behavior); plus a note that user-invoked skills
   (`disable-model-invocation: true`) are exempt from trigger evals.
5. **evals/triggers.json**: autopilot's 1 case re-pointed — its prompt now
   expects `feature` (the correct model-side answer once autopilot requires
   explicit invocation).

## Out of scope

- Rewriting the other 10 descriptions (headroom exists; regression risk
  doesn't pay).
- Any body edits, any router skill, AGENTS.md changes.
- Marketplace/README wording (rows unchanged; links stay valid).

## Acceptance criteria

- [ ] `python3 scripts/validate-skills.py` → PASS, including new checks;
      WARN fires on a >950 description only if one exists. [Corrected at
      the done gate: blueprint (1002), map (969), verdict (952) sit in the
      951–1024 band and stay WARNed by design — dieting them is out of
      scope; "(post-diet: none)" was wrong.]
- [ ] Full trigger eval: fresh judge sub-agent, **all cases match** —
      including the re-pointed autopilot prompt and all routing pairs.
- [ ] The 5 dieted descriptions ≤900 chars; autopilot ≤400; all ≥ meaningful
      (no skill's routing hint lost — grep "use X" cross-references still
      resolve).
- [ ] Commit attributes mattpocock/skills (MIT); no AI attribution.

## End-to-end check

Validator PASS quoted + eval run transcript quoted (prompt → picked table),
zero mismatches.

## Decisions

- **D1** Invocation audit result: autopilot only (safety: charter-signing
  skill requires deliberate invocation). Others keep natural-phrase
  triggering — it's the product.
- **D2** Diet scope: the 5 near-limit descriptions only.
- **D3** Name-clash = static curated BUILTINS set in the validator.
- **D4** Authoring lint lives in evals/README.md, not AGENTS.md (which
  loads every session).
- **D5** Length smoke = non-failing WARN at >950.
- **D6** autopilot's eval case re-points to feature rather than being
  deleted (the prompt is still a real user prompt; the model-side answer
  changed).

## Assumptions

- **A1** `disable-model-invocation: true` is honored by current Claude Code
  (mattpocock/skills ships it in production). If a harness ignores it, the
  short human-facing description makes auto-triggering unlikely anyway —
  degradation matches intent.
- **A2** The eval judge approximates the real trigger mechanism (existing
  caveat in evals/README.md); a pass is strong signal, not proof.
