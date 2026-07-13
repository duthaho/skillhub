# Mermaid render checklist — read at Step 3; the table renders, you don't compose

The diagram is a mechanical projection of the verified node/edge table.
Every rule below exists because its violation is a documented breakage
class (gitdiagram and deepwiki-open both shipped fallback error screens
before converging on structure-over-prompt-rules).

## Render rules

1. **Header:** `flowchart TD` — nothing else. (Not `graph LR`; not
   sequence/class diagrams in v1.)
2. **Node IDs:** the table's stable IDs, alphanumeric + hyphens only
   (`comp-auth`), never starting with a digit. IDs are code, not labels.
3. **Labels always quoted:** `comp-auth["Auth service"]`. Inside label
   text: **no raw parentheses, brackets, braces, semicolons, or
   backticks** — reword or use HTML entities (`&#40;`). Labels ≤ 4 words;
   the prose carries nuance, not the box.
4. **Edges:** `from-id -->|"verb"| to-id`, verb from the table's edge row,
   quoted, ≤ 3 words. One edge per table row — no invented arrows.
5. **Click links** for every node with a repo path:
   `click comp-auth "src/auth/" "src/auth/"` — relative paths, so GitHub's
   inline rendering links into the tree.
6. **Subgraphs** only when the table groups nodes (≥ 2 members), titled
   with quoted labels; never nested more than one level.
7. **Size caps:** ≤ 30 nodes, ≤ 45 edges, ≤ 8 subgraphs. Over cap →
   collapse to parent components in the *table* and re-render — never
   squeeze the diagram.
8. **One diagram per fenced block**, ` ```mermaid ` fence, no leading
   whitespace before the fence.

## Self-check before shipping (the failure list)

Scan the rendered block for each item; any hit = a defect to itemize:

- [ ] unquoted label, or label containing `( ) [ ] { } ; ` ` `
- [ ] node ID with spaces, leading digit, or not in the table
- [ ] edge whose from/to pair has no table row (invented arrow)
- [ ] `click` pointing at a path not in the node table
- [ ] caps exceeded (count nodes/edges/subgraphs)
- [ ] `flowchart TD` missing or extra text on the header line

If `npx -y @mermaid-js/mermaid-cli` (or `mmdc`) is available, a parse run
is the strongest check — offer it, don't require it (keyless first).

## Repair protocol (bounded)

On any defect: list the issues as `line: problem`, fix **only those
issues** — no redesign — and re-run the self-check. **Maximum 3 repair
attempts.** Still broken after 3 → degrade: drop subgraphs, then drop
click links, then halve nodes by collapsing to parents. A plain diagram
that renders beats a rich one that doesn't; never attempt a fourth repair.
