# Verdict ADR template — the brief rendered in Step 3; read it when composing the brief.

**Pre-render check:** read only the brief's opening block and its closing
pre-Sources lines — together they must say what matters most and what to do
next. If they don't, reshape the brief; don't bolt a second summary on top.

```markdown
# Verdict: <Option A> vs <Option B>[ vs <Option C>] — <context, one line>

**Run:** <YYYY-MM-DD> · **Status:** Proposed (advisory)
**Context & assumptions:** <what's being built, scale, team, constraints — including assumptions you made>
**Weights:** <the weights used and any overrides>

## Recommendation
**<Option>** — <2–3 sentences: the decisive factors>. <If a tie: say it's a tie and name the human tiebreaker.>

## Scorecard
| Criterion (weight) | A | B | C |
|---|---|---|---|
| Fit for requirements (30%) | x | x | x |
| ... rows per criterion, weighted total last, dealbreakers row if any |

## <Option A> — <score>/10
Strengths / weaknesses for THIS context, each with citation. Health snapshot
(commits/releases/issues). Notable practitioner reports. Vendor claims labeled.

(repeat per option)

## Consequences & risks of the recommendation
- What we accept by choosing it; migration/exit cost if we're wrong.

## Suggested spike
- The cheapest experiment (ideally ≤ 1 day) that would de-risk this decision
  before committing — what to build, what to measure, and what result would
  overturn the recommendation.

## Revisit when
- Concrete triggers that would change this verdict (e.g. "X ships native Y",
  "license changes", "we exceed N QPS").

## Sources
Every cited URL, grouped by option; vendor sources marked.
```
