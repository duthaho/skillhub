# Grounded mode — distillate template and probing mechanics

Read when GROUNDED reaches its distill step. Distillation approach adapted
from virgiliojr94/book-to-skill (MIT).

## The flow: distill, then offer

The distillate is a **complete deliverable on its own** — "summarize this
book for learning" ends here, happily. Produce it, show where it landed,
then offer once: *"Want me to turn this into a syllabus and teach it?"*
Yes → NEW with the grounded changes (SKILL.md GROUNDED step 4). No → stop;
don't create a learning log for a summary-only ask.

## Probing mechanics (probe, don't ingest)

For sources over the ~50K-token gate — and for any per-unit lookup later:

- **md/txt:** map structure first — `grep -n '^#' <file>` (or chapter
  markers) gives heading offsets; pull one section with
  `sed -n '<start>,<end>p' <file>`. Never re-read the whole file per
  section: re-reading a 75K-token book once per chapter costs ~2M input
  tokens for nothing.
- **PDF:** `Read` with a page range for the slice you need. If page-level
  reads aren't working for a given file, use `pdftotext` when it's already
  installed (`command -v pdftotext`) to get a greppable text copy in
  `/tmp/`; if it isn't installed, say so honestly and work chapter by
  chapter via page ranges — never install tools for the user.
- **Verify before asserting** (the grounding bar, mechanically): before the
  distillate or a lesson claims "the book says X", `grep -n` the passage
  (md/txt) or re-read the cited pages (PDF). No hit → it doesn't go in.

## Distillate template — `out/learn/<slug>-distillate.md`

Most important content **first** — long files get truncated from the end
when context is tight, so the cheatsheet outranks the map.

```markdown
# Distillate: <Source title>

Source: <path> · ~<N>K tokens · distilled <date +%F>

## Cheatsheet — the author's judgment

<The decision layer, not a synopsis. In descending value:>
- **Decision rules** — "if X, do Y" the author actually commits to
- **Trade-off matrices** — options × criteria the source weighs
- **Thresholds** — numbers with authority ("beyond ~200 LOC, split it")
- **Tells & smells** — signs the author says to watch for

Every line should help the reader *decide* something (§section cited).

## Source map

| § | Section / chapter | Lines/pages | One-line: what it teaches |
|---|---|---|---|
| 1 | <heading> | L12–88 / pp. 1–14 | <claim, verified> |

## Candidate syllabus hooks

<3–6 unit-sized ideas the map suggests, each citing its §. Used if the
learner continues to the loop; harmless if not.>
```

Rules for filling it:

- **Earned depth:** a section with nothing decision-worthy gets one map row
  and no cheatsheet lines — land short rather than pad. Depth is earned
  with content, never with length.
- **The author's exact naming** is preserved ("The 5 Whys", not "asking why
  repeatedly") — the learner will meet these terms again in the source.
- **Quote minimally.** The distillate is your notes on the source, not a
  copy of it — locators point back instead of passages pasted in.

## Grounded syllabus + sessions (deltas only)

When the learner continues, NEW/CONTINUE run as written in SKILL.md, plus:

- Learner section of the log gains: `Source: <path> · distillate:
  out/learn/<slug>-distillate.md`.
- Each syllabus unit cites its coverage: `src: §3, L120–214` (or pages).
- Teaching quotes carry the citation inline; checks may ask the learner to
  apply the *source's* rule, graded against the source's own wording
  (verified per the probing mechanics above).
