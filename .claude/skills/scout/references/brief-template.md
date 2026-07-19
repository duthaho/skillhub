# Scout brief template — the report rendered in Step 5; read it when composing the brief.

**Pre-render check:** read only the brief's opening block and its closing
pre-Sources lines — together they must say what matters most and what to do
next. If they don't, reshape the brief; don't bolt a second summary on top.

```markdown
# Scout: <project> vs the field

**Run:** <YYYY-MM-DD> · **Our job:** <one sentence> · **Our axis:** <differentiation>
**Peers:** <owner/repo (why it qualifies)> · … · **Mode:** survey / deep on <peer>

## Since last scout (<date of previous brief>)
- <new releases among peers, new high-reaction requests, verdicts due for revisit>
(omit this section on the first scout)

## Verdicts
| Feature / lane | Verdict | Evidence (locator) | Why (our side) | Effort |
|---|---|---|---|---|
| <name> | ADOPT | <issue URL, 👍 n / release tag> | <demand or axis fit> | S/M/L |
| <name> | ADAPT | … | <what transfers, what changes; peer license> | … |
| <name> | WATCH | … | <revisit trigger> | — |
| <name> | SKIP | … | <why parity isn't a reason here> | — |

## The gap, both ways
**They have, we lack:** <ranked, demand-weighted>
**We have, they lack (the moat):** <what not to break or dilute>
**Nobody has, their users want (open lanes):** <from reaction mining>

## Peer notes
### <owner/repo> (<license> · last release <tag/date> · cadence <n/quarter>)
What their users beg for (top-reacted open requests, with counts and URLs).
What they shipped recently (release tags). What they claim (docs).

## Ready handoffs
- `/feature <ADOPT item>` — <one-line spec seed from the sketch>
- `/autopilot <ADOPT item>` — <when it's well-bounded enough to hand over>

## Sources
Flat list of every cited URL: issues (with reaction counts), releases, docs.
```
