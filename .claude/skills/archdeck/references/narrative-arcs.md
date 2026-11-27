# Narrative arcs

A deck is a story with a mechanism at its center. Pick **one** arc per deck;
the arc decides the order of slides, so choose it before drawing anything.
Every arc below names its beats — map each beat to 1–3 slides.

## Universal rules (all arcs)

- **Open on stakes, not on a definition.** Slide 1 shows the cost of getting
  it wrong — a number, a failure, a scan that takes forever — and the
  proposal on the table. "What is caching?" loses the viewer; "this query
  reads 2 million rows to show 50" keeps them.
- **Name the misconception.** Every good explainer corrects a belief the
  viewer probably holds. Write it down in the storyboard header; one slide
  states it fairly before taking it apart.
- **One pivot.** Somewhere in the middle the frame changes — the problem
  turns out to be about something else (the user's intent, the index, the
  network, not the algorithm). The pivot is the deck's reason to exist.
- **Predict beats every 3–4 slides.** An `ask` slide (or an `ask` block at
  the end of a slide) poses a concrete question and the *next* slide answers
  it. In a video this is where the viewer pauses and thinks — label it so
  (`Dừng video, thử đoán`).
- **Side quests come back.** At most one detour per deck, and the slide
  after it explicitly returns ("Lag fixed — but…").
- **End on a decision rule, not a summary.** The last content slide answers
  "so when do I use what?" in one sentence; the recap after it is optional.
- **Pace:** ~45–75 s of narration per slide, 2–5 steps per slide. A 12-slide
  deck ≈ a 12-minute video.

## 1. The Pivot (proposal → doubt → reframe → root cause)

Best when the "obvious" technical fix is right but beside the point.
The demo deck that inspired this skill (pagination for a CS order screen)
follows this arc.

| Beat | Purpose | Typical archetypes |
|---|---|---|
| Proposal | The confident first answer, shown working | `split`, `walkthrough` |
| Hidden trap | A correctness bug in the proposal and its fix | `walkthrough`, `code` |
| Pivot | "Technically right — but we never asked the user" | `checklist`, `dialogue` |
| Reframe | What the user actually does with this | `split`, `dialogue` |
| Revised proposal | The design the reframe implies | `split`, `mapping` |
| Limits | Where the technique stops working / where it fits | `split`, `list` |
| Root cause | The thing that actually decides performance | `ask` → `walkthrough` → `pipeline` |
| Decision rule | One sentence + the trade-off | `matrix` or a `callout` |

## 2. Scale ladder (1 → 10k → 1M → 100M)

Best for system design: "design a URL shortener / chat / feed / rate limiter".
Each rung multiplies load by 10–100×, something breaks, the fix adds one box.

| Beat | Purpose | Archetypes |
|---|---|---|
| Rung 0 | Simplest thing that works (1 server, 1 DB) | `trace` |
| Numbers | Back-of-envelope: QPS, storage, bandwidth | `numbers` |
| Rung n: break | Show *where* it breaks — the hot box turns red | `failure`, `bars` |
| Rung n: fix | Add one component; replay the request | `trace` |
| Rung n: new cost | What the fix costs (consistency, ops, money) | `matrix`, `split` |
| Final picture | The whole topology, every box earned | `trace` |
| Decision rule | Which rung most teams actually need | `callout`, `recap` |

Rule: never add a box the viewer hasn't seen the need for. The diagram
grows by exactly one idea per rung.

## 3. Incident autopsy (symptom → hypotheses → evidence → cause → fix → guard)

Best for debugging stories: race conditions, memory leaks, cache stampedes,
N+1, deadlocks, flaky deploys.

| Beat | Purpose | Archetypes |
|---|---|---|
| Symptom | What the user/on-call saw, with the graph | `bars`, `numbers`, UI mock |
| Hypotheses | 2–4 plausible causes, each with how to test it | `list` |
| Evidence | Ruling out, one by one (strike them) | `list` + `a-strike`, `code` |
| Mechanism | The actual interleaving, step by step | `lanes`, `sequence` |
| Fix | The change, as a diff | `code` (diff) |
| Proof | The same timeline, now safe | `lanes`, `bars` |
| Guard | Test / alert / invariant that stops a repeat | `checklist`, `callout` |

The `lanes`/`sequence` slide is the heart — spend steps there.

## 4. Build the mental model (naive → why it fails → primitive → composed)

Best for "how does X work": B-trees, consistent hashing, Raft, event loop,
React reconciliation, TCP congestion control, LSM trees, CDN caching.

| Beat | Purpose | Archetypes |
|---|---|---|
| The job | What X must achieve, in one concrete scenario | `split`, `cover` |
| Naive attempt | The obvious approach, run on real data | `walkthrough` |
| Failure | Where naive breaks (cost, correctness) | `numbers`, `failure` |
| Primitive | The one idea that makes X work | `walkthrough`, `state` |
| Composition | Primitives assembled into the real thing | `trace`, `pipeline` |
| Edge case | The case that makes X's design look the way it does | `lanes`, `ask` |
| In the wild | Where you meet X in real systems (versions named) | `list` |

## 5. Trade-off duel (A vs B → it depends → made concrete)

Best for "REST vs gRPC", "SQL vs NoSQL", "SSR vs CSR", "monolith vs services",
"polling vs websockets vs SSE".

| Beat | Purpose | Archetypes |
|---|---|---|
| The fight | Why people argue; the scenario we'll judge on | `split` |
| Mechanism A | How A works, traced once | `trace`/`sequence` |
| Mechanism B | How B works, same request | `trace`/`sequence` |
| Dimension × N | One slide per dimension that matters (latency, cost, ops, DX) with numbers | `bars`, `numbers`, `split` |
| Matrix | All dimensions at once, winner per row | `matrix` |
| Decision rule | "Pick B when …, otherwise A" | `callout` |

Never let the duel end "it depends" without saying *on what*, with a
threshold.

## Choosing

| Prompt shape | Arc |
|---|---|
| "X vs Y", "should I use …" | Trade-off duel |
| "design a …", "scale …", "system design for …" | Scale ladder |
| "why does … happen", "bug", "outage", "race" | Incident autopsy |
| "how does … work", "explain …" | Mental model |
| a proposal/technique with a context question behind it | Pivot |

Arcs combine: a Mental-model deck can end on a mini Trade-off duel; a Scale
ladder can contain one Incident beat. Keep one spine.
