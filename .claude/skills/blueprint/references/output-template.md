# Output layout — read at Step 4; the exact shape of docs/blueprint/

Three file kinds, all markdown, all rendered natively by GitHub/GitLab.
Placeholders in angle brackets are filled at write time — `<date>` from
`date +%F`, `<short-sha>` from `git rev-parse --short HEAD`, never typed
from memory.

## `docs/blueprint/README.md` — the front door

````markdown
# Architecture: <project name>
<!-- blueprint <date> @ <short-sha> · regenerate with /blueprint refresh -->

<One paragraph: what the system does and its overall shape — verb-first,
no filler.>

Sources: <file>:<lines>, …

## System overview

```mermaid
<top-level diagram, rendered per the checklist>
```

## Components

| Component | Path | Job |
|---|---|---|
| [<display name>](<component-slug>.md) | `<path>` | <one line> |
<!-- link column only for components that earned a drill-down page;
     the Path column is this section's source citation -->

## How a <core operation> flows

<Numbered walk of the main path through the boxes, each step citing its
file. This is the section a new team member actually reads.>

Sources: <file>:<lines>, <file>:<lines>, …
````

## `docs/blueprint/<component-slug>.md` — one per drill-down

Written for SCOPED runs and for components too big for one table row.

````markdown
# <Display name>
<!-- blueprint <date> @ <short-sha> · component: <comp-id> -->

<What it does and why the boundary sits here — the "why" the code can't
say.>

Sources: <file>:<lines>, …

## Inside

```mermaid
<component-level diagram, same checklist, drill one level>
```

## Boundaries

| Direction | With | Verb | Where |
|---|---|---|---|
| in/out | <comp-id> | <verb> | `<file>:<line>` |
<!-- the Where column is this section's source citation -->
````

## `docs/blueprint/manifest.md` — the refresh contract

The machine-readable half; refresh depends on it, so the format is fixed:

````markdown
# Blueprint manifest
<!-- stamp: <date> @ <short-sha> -->

## Nodes

| ID | Name | Path | Page |
|---|---|---|---|
| comp-<slug> | <display name> | `<path>` | README.md § Components |

## Edges

| From | To | Verb | Locator |
|---|---|---|---|
| comp-a | comp-b | calls | `<file>:<line>` |
````

Rules the layout enforces:

- The stamp comment appears in **every** generated file — refresh reads
  the manifest's, humans see each page's.
- **Every prose section carries its sources** — a `Sources:` footer, or a
  table whose locator column serves as one (Components, Boundaries, the
  manifest tables). A section with neither gets rewritten or cut.
- IDs are the identity: refresh matches changed paths against the `Path`
  column, regenerates only the pages those IDs own, and updates renamed
  display names in place.
- Unverified candidate edges stay in `out/blueprint/.work/`, never in the
  manifest — the manifest is the set of defensible claims.
