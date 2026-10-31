# Animations

**Motion shows causality, never decoration.** Every animation must answer
"what happens next in the system?" — a request travels, a scan crawls, a
row moves, a lock is held. If removing the motion loses no meaning, use a
plain step reveal.

## The step model

- `data-step="n"` → element appears at step *n* (n ≥ 1). No attribute =
  visible from the start (step 0).
- `data-out="m"` → element leaves at step *m*. Combine with `data-step` to
  show something only during steps n…m-1. Two elements in a `.stack` with
  `data-out="2"` / `data-step="2"` swap in place.
- Steps must be contiguous 1…N per slide (the build fails on gaps). Several
  elements can share a step; stagger them with `style="--d:150ms"`.
- `.notes` paragraphs carry `data-step` too: the narration for that step.
- The engine sets `.is-on` (visible/active), `.is-current` (revealed at this
  exact step) and `data-at="<step>"` on the slide — usable in custom CSS.
- `data-focus` on a `<section class="slide">` dims earlier reveals when a
  new one lands (spotlight). Add `.no-dim` to keep something lit.
- Elements with `.enter` animate once each time the slide is entered.

## Primitives (classes on the stepped element)

**Entrances** (hidden until on):

| Class | Motion | Use for |
|---|---|---|
| *(none)* | fade + rise 16px | default reveal |
| `a-fade` | fade only | overlays, big containers |
| `a-pop` | scale 0.86 → 1 with overshoot | a verdict, a badge, a stat landing |
| `a-left` / `a-right` / `a-down` | slide in from that side | the second column of a comparison |
| `a-grow-x` / `a-grow-y` | scale from the left / bottom | bars, timeline blocks, progress |
| `a-packet` | dot travels along `offset-path`, fades on arrival | a request/message moving between nodes |
| `a-shake` | appears, then shakes once | an error, a rejected request |
| `a-pulse` | appears, then a repeating glow ring (HTML only) | "this is the hot spot" |

Add `a-keep` to any entrance class to make the element visible from the
start and only play the effect at its step (e.g. `a-keep a-shake` shakes a
node that was already on screen). Forgetting it is safe; forgetting the
opposite would leak the answer at step 0.

**State changes** (always visible; change look when on):

| Class | Effect | Use for |
|---|---|---|
| `a-focus` / `a-problem` / `a-fix` / `a-info` | recolor background + border | a row/cell/node becomes the point; a node fails |
| `a-mark` | highlighter sweep behind inline text | the key words of a sentence or token |
| `a-strike` | red strike-through, text dims | ruled-out hypothesis, rejected option |
| `a-dim` | fade to 28% + grayscale | de-emphasize what no longer matters |
| `a-draw` | SVG stroke draws itself (needs `pathLength="1"`) | a wire/edge appearing, a path being traced |
| `a-flow` | dashes march along an SVG wire, looping | live traffic on a connection |
| `a-scan` | width 0 → `--to` linearly over `--t` | a full scan, a progress bar, a queue filling |
| `a-count` | number counts `data-from` → `data-to` | rows read, latency, cost |
| `a-type` | typewriter, `--n` = character count (mono) | a query or command being typed |

Timing knobs (inline style): `--d` delay, `--t` duration (scan/packet/draw/
flow), `--loop` iteration count for packets (`infinite` for steady traffic),
`--to` scan target width, `--n` typed characters. `a-count` also takes
`data-decimals` and `data-ms`.

## Choreography patterns

**Compare (before → after).** Step 1 reveals the left side's cost, step 2
the right side (`a-right`), step 3 both bottom-line callouts (`a-pop`).
Never reveal both sides at once — the viewer reads left first anyway.

**Scan vs seek.** Left: a track with `a-scan` (`--t: 3s`) and an
`a-count` of rows read climbing to 1.999.950. Right: a single `a-packet`
jumping straight to the target, count stops at 50. Same step, so they race.

**Trace a request.** One `a-packet` per hop, consecutive steps, each with
`--d` so the arrow `a-draw`s first and the packet follows. The node it
arrives at gets `a-info` (or `a-problem` if it hurts).

**Interleaving / race.** In `lanes`, step through blocks one by one
across lanes; the conflicting write gets `a-problem` + `a-shake`; a
`lane-mark` drops at the exact instant of the conflict.

**Failure injection.** Healthy topology at step 0 with `a-flow` wires.
Step n: one node `a-problem` + `a-shake`; its wires `a-dim`; retry packets
pile onto the neighbor (`a-problem` on it a step later) — the blast radius
is visible.

**Narrowing (index seek / binary search).** Each step `a-dim`s the half
you rule out and `a-focus`es the remaining range; a `.pin` follows the
cursor.

**Predict then reveal.** `ask` block visible at the last step of slide N;
the answer is slide N+1's step 1, never on the same slide.

**Swap in place.** `.stack` holding the old and new version (`data-out` /
`data-step` on the same number): the query rewrites, the number changes,
the diagram updates — without the layout jumping.

## Timing for video

- Default transition 520ms; never exceed ~1s except scans/packets that
  *are* the point (2–3s).
- One idea per step. If the narration for a step runs > ~20s, split it.
- `R` replays the current step — record a retake without leaving the slide.
- Open the deck once online before recording so the Google Fonts are
  cached — the first open waits on them.
- Record in clean mode (`?clean` or `C`): no progress bar, no counter, no
  cursor. Full screen with `F`.
- Respecting `prefers-reduced-motion` is on by default; add `?motion` to the
  URL when recording on a machine with reduced motion enabled.
