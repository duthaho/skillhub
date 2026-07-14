# Prior-art brief template — rendered in Step 6; read this file when composing.

```markdown
# Prior art: <idea in ≤8 words>

**Checked:** <YYYY-MM-DD> · **Queries used:** <n>/10 · **Verdict: <one of
Build it / Fork X / Contribute to Y / Use Z / Investigate first>**

## The idea, restated
<the one confirmed sentence: what, for whom, distinctive constraint>

## Since last check (<date>)
<status changes and new arrivals only — omit on a first check>

## The landscape
| Name | Link | Status | Relevance |
|---|---|---|---|
**Direct matches** (≤3 rows) · **Adjacent** (≤3) · **Partial** (≤3) ·
**Abandoned** (≤3, with when/why it died)
<empty bucket → "none found; searched: <venues/framings>">
<every Status = fetched signal ("last commit <date>", "<n> dl/mo") or "unknown">

## Standard patterns
- <3–6 bullets: the playbook across matches — architecture, libraries, naming, pricing>

## Differentiator
<one honest paragraph — name it, or say there isn't one>

## Verdict: <repeat the one verdict>
<2–4 sentences of nuance, then the single concrete next step>

## Sources
<flat list: every URL fetched, including the ones that returned nothing>
```

The `checked.md` line appended after saving (append-only, one line per check):

```markdown
| <YYYY-MM-DD> | <idea in ≤8 words> | <verdict> | <brief filename> |
```

(First write creates the file with a `# priorart — checked ideas` heading and
the table header `| Date | Idea | Verdict | Brief |`.)
