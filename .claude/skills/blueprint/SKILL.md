---
name: blueprint
description: >-
  Human-facing documentation, architecture docs, and mermaid diagrams for a
  codebase, a module, or a feature — "draw me the architecture, with
  receipts." Fans out read-only sub-agents to build a grounded component
  graph first: every node is a real path, every edge backed by a
  grep-verified import or call — unverifiable edges are dropped, not drawn.
  Diagrams render from that verified table per a fixed checklist (never
  freehand mermaid), capped at 5–8 top-level components with drill-down
  pages; every doc section cites its sources as file:line. Drafts in chat,
  writes docs/blueprint/ only on your yes, and stamps a manifest with date +
  commit so /blueprint refresh regenerates only what the diff touched. Use
  for "generate an architecture diagram", "document this codebase or module
  for people", "create a mermaid diagram of this feature" — e.g.
  "/blueprint", "/blueprint the payment flow", "/blueprint refresh". For
  agent-facing orientation (AGENTS.md) use map; blueprint is the
  human-facing sibling.
---

# blueprint — architecture the team can read, with receipts

`/blueprint` — whole-repo architecture doc + top-level mermaid diagram
`/blueprint <module|feature>` — scoped doc + diagram for one area
`/blueprint refresh` — regenerate only what the diff since the stamp touched

Answer one question: **what does a person need to see to understand how this
code is put together — and can every box and arrow be defended?** The
documented failure mode of AI-generated architecture docs is confident
fiction: diagrams with components that don't exist and arrows nobody can
trace. The countermeasure is structural, not stylistic — no edge without a
locator, no mermaid the checklist didn't render, no write without a yes.
