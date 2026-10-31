# Visual language

Load with `archetypes.md` and `animations.md` at render time. Classes named
here are defined in `assets/deck.css`; use them instead of inline styles
so every deck looks like one series.

## The direction: a sheet from an engineering drawing set

Every slide is one sheet of a technical drawing set. Drafting paper with a
24px measurement grid, ink-navy linework, cobalt for anything that moves
(requests, packets, traces), and a **title block** along the bottom edge —
deck name · one tick per step (lit as you advance) · `Tờ 03 / 12`. Dark
theme is a literal blueprint: cobalt-navy paper, white linework, a 48px
line grid. The title block is the series' signature; leave it on (opt out
per slide with `data-plain` only for full-bleed visuals).

## Canvas

- Fixed **1920×1080**, scaled to the window. Content box after padding:
  **1728 wide**, ~850 tall between the header and the title block. Design in
  px against that box — `.diagram` sizes and SVG `viewBox`es use the same
  numbers.
- Nothing scrolls. If it doesn't fit, it's two slides.
- Minimum text size **16px** (mono labels), body **22–28px**, title
  **66px**. At 1080p video compressed by YouTube, smaller is mush.

## Type

| Role | Face | Where |
|---|---|---|
| Display | **Bricolage Grotesque** 800 | titles, card heads, callout titles, stat numbers, node names |
| Body | **Be Vietnam Pro** 400–700 | sentences, labels people read (drawn for Vietnamese diacritics) |
| Utility | **JetBrains Mono** 400–700 | kicker, badges, tags, node types, axis ticks, wire labels, code, IDs |

`deck.css` imports all three from Google Fonts (`display=block`: text waits
for the font instead of flashing a fallback); offline, the system stack
takes over. Don't add other font sources. The rule of thumb: if a human
would *say* it, it's body; if a machine would *print* it (a key, a status,
a timing, a count with a unit), it's mono.

## Tone = meaning

Color is semantic and consistent across the whole deck. Never use a tone
for decoration.

| Tone | Name | Means | Typical use |
|---|---|---|---|
| `info` | trace cobalt `#2747F5` | something moving / a proposal | packets, requests, the kicker rule, a new idea under test |
| `problem` | fault vermilion `#E5452F` | current state, failure, cost | the "before" column, a bad row, an error |
| `fix` | pass green `#0E9F6E` | the improvement, correct, cheap | the "after" column, the winning cell |
| `focus` | probe amber `#FFB020` | **look here** — the focal point | highlighted row/token/cell, the seek target |
| ink | `#0F1B2D` | neutral linework, labels, the question | node borders, `NOW` badges, the `ask` block |

Code always sits on a dark instrument panel (`.code`), in both themes —
the one dark block besides `ask`. Color is never the only signal: pair it
with a word (`✗`, `TRƯỚC/SAU`), a glyph, or position.

## Badges (label every block)

Badges are mono label tags with a square marker — schematic annotations,
not pills. A block without a label makes the viewer guess what they're
looking at. Consistent vocabulary within a deck:

| Meaning | vi | en | class |
|---|---|---|---|
| current state | BÂY GIỜ / HIỆN TẠI | NOW / TODAY | `badge` |
| proposal | ĐỀ XUẤT | PROPOSAL | `badge info` |
| revised proposal | ĐỀ XUẤT LẠI | REVISED | `badge info` |
| fix / added piece | SỬA / THÊM … | FIX / ADD … | `badge fix` |
| problem / bottleneck | VẤN ĐỀ / NÚT THẮT | PROBLEM / BOTTLENECK | `badge problem` |
| before / after | TRƯỚC / SAU | BEFORE / AFTER | `badge problem` / `badge fix` |
| one facet of N | MẶT 1 / MẶT 2 | SIDE 1 / SIDE 2 | `badge soft` |
| known / not yet asked | ĐÃ CÓ / CHƯA HỎI | KNOWN / NOT ASKED | `badge fix` / `badge problem` |
| episode / series | SYSTEM DESIGN · TẬP 07 | SYSTEM DESIGN · EP 07 | `badge info` (cover) |

Questions don't need a badge: the `ask` block's ink panel and amber `?` are
the label.

## Copy rules

- **Title = the claim**, ≤ 12 words, no trailing period. The viewer
  should be able to read *only* titles and follow the argument.
- **Kicker** (above the title, mono on a cobalt rule) = the beat: `Cơ chế`,
  `Root cause`. The sheet number lives in the title block — don't repeat it.
- **≤ ~40 words of prose** visible at the end of a slide (tables/code/labels
  excluded). Explanations belong in the narration (`.notes`).
- **Bottom line**: a `callout` that turns the slide into a sentence the
  viewer keeps. Two side by side when the slide compares.
- **Numbers formatted by locale** (`vi`: `2.000.000`, `4,95 tr`; `en`:
  `2,000,000`). Units always (`ms`, `rows`, `MB/s`).
- Code identifiers in `.chip` inside prose; real code only in `.code`, with
  `data-file="orders.repo.ts"` when a filename helps place it.

## Concrete beats abstract

- Mock data looks real and stays **identical across slides** (same order
  IDs, same customer, same amounts) — take it from the fact sheet.
- Show the system's own artifacts: a real `EXPLAIN` line, an HTTP request
  line, a log line, a metrics graph, the UI the user clicks.
- Prefer one real request traced end to end over five boxes with arrows.

## Focal point

Every slide has exactly one: the amber thing (`focus` tone, `.hl`,
`a-mark`, `a-focus`, a `.pin.focus`). If two things compete, add a step
and move the focus.

## Layout

- Header is left-aligned (kicker, then title); content centers in the
  remaining space; callouts sit just above the title block.
- Comparisons: left = before / naive / A; right = after / better / B.
- Time flows left → right (lanes, flows) and top → bottom (sequences).
- Requests go right, responses return left (`seq-msg back`).
- Keep 40px+ between columns; align columns on a shared baseline (badges
  on one row, callouts on one row).
- Cover slides (`.slide.cover`) get a cobalt registration bar on the left
  edge and a 116px display title; nothing else competes.

## Glyphs & icons

No emoji (they render differently per OS and look cheap on video). Use
text glyphs that ship in the bundled fonts — `✓ ✗ → ← ↑ ↓ … · ≈ ≤ ≥ ×` —
or small inline SVG drawn with `currentColor`. Name infrastructure with a
`.node-type` label (`POSTGRES 16`, `REDIS`, `CDN`, `K8S POD`) instead of
logos; its marker square takes the node's tone automatically.

## Theme

Drafting paper (light) by default — most legible after video compression.
Blueprint (dark) is one attribute away: `<html data-theme="dark">` on every
slide file, or `T` live. Never hard-code colors — use tokens
(`var(--problem)` …) so both work.
