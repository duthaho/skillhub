# Pulse brief template — the brief rendered in Step 3; read it when composing the brief.

**Pre-render check:** read only the TL;DR — it alone must deliver the
headline state of the conversation, so a reader who stops there leaves
correctly informed. If the real headline sits lower, lift it; don't bolt a
second summary on top.

```markdown
# Pulse: <Topic>

**Window:** <resolved window> · **Run:** <YYYY-MM-DD> · **Type:** <detected type>
**Sources reached:** Web ✓ · Hacker News ✓ · Reddit ✓/fallback/✗ · GitHub ✓/✗

## TL;DR
- 3–5 bullets: the headline state of the conversation right now.

## Since last pulse (<date of previous brief>)
- **New:** <clusters that weren't in the previous brief>
- **Faded:** <previous headline items with no fresh activity>
- **Resolved:** <previously unconfirmed items now confirmed/debunked, with source>
(omit this section entirely on the first pulse for a topic)

## Key Developments
For each ranked cluster:
### <Cluster headline>
What happened + why it resonates. Inline citations with engagement metrics and links.
Merge cross-source coverage here.

## Best Takes
> "<quote>" — <author/handle>, <source> (<engagement>) [link]

## Disputed / Unconfirmed
- <claim> — why it's uncertain, who's pushing back. (omit section if empty)

## Sources
Flat list of every cited URL, grouped by source, with engagement metrics.
```
