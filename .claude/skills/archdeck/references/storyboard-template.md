# storyboard.md template

The storyboard is the contract the user approves before any HTML exists.
It is cheap to change; a rendered slide is not. Write it to
`out/archdeck/<slug>/storyboard.md` in the deck's language.

```markdown
# <Deck title>
<YYYY-MM-DD> · arc: <arc name> · <N> slides · ~<N> min · lang: <vi|en|…> · theme: <paper|blueprint>

## Brief
- **Problem:** <one sentence, concrete>
- **Audience:** <level + what they already know>
- **Misconception:** <the belief this deck corrects>
- **Aha:** <the one sentence a viewer should repeat to a friend>
- **Decision rule:** <the "use X when …" the deck ends on>
- **Voices:** <narrator only | dialogue: S = learner, J = presenter>

## Fact sheet (single source for every name and number on any slide)
- **Scenario:** <company/screen/system, e.g. "shop admin, CS searches orders">
- **Scale:** <rows, QPS, payload sizes, latencies — each with its arithmetic>
  - 2.000.000 orders/shop · 50/page → 40.000 pages
  - OFFSET page 40.000 reads 1.999.950 + 50 rows
- **Entities & sample data:** <IDs, names, amounts reused on every mock>
  - DH-58213 · Nguyễn Lan · 4.950.000 ₫ · 12/10
- **Environment assumptions:** <engine + version where behavior differs,
  e.g. "MySQL 8.0 InnoDB: secondary index stores the PK">
- **Claims to double-check:** <anything version- or vendor-specific>

## Slides

### 01 · <Title = the claim>
- **Beat:** <arc beat>
- **Archetype:** <archetype name> (+ <secondary>)
- **On screen:** <left/right/center contents, concretely: which rows, which code>
- **Steps:**
  1. <what appears / changes> — `a-<primitive>`
  2. …
- **Focal point:** <the one thing the eye must land on>
- **Bottom line:** <callout text, if any>
- **Narration:**
  - [0] <what is said as the slide lands>
  - [1] <what is said at step 1>
- **Bridge:** <the question this slide leaves for the next one>
```

## Approval view (what to show in chat)

Don't paste the whole file. Show the brief, then one table:

| # | Title (claim) | Archetype | Motion | Bridge |
|---|---|---|---|---|
| 01 | OFFSET counts from the top; keyset seeks | split | scan vs seek | "but are rows unique?" |

Then ask: approve / change slides / reorder / cut. Edits land in the file
before rendering.

## Quality bar for a storyboard

- Every title is a claim a viewer could disagree with — not a topic
  ("Caching" ✗ → "A cache only helps the second reader" ✓).
- Every number on a slide appears in the fact sheet, with arithmetic.
- Every slide has exactly one focal point.
- Steps are causal: each step answers "and then what happens?"
- Bridges chain: reading only the Bridge lines tells the whole story.
