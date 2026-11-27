---
name: harden
description: >-
  Production-readiness audit for implemented code — five named failure modes,
  each finding paired with the pattern that prevents it. Audits code in context
  (a file, directory, or diff) for: silent error swallowing, missing
  observability at trust boundaries, infrastructure coupling in domain logic, no
  resilience at external calls (timeout/retry/circuit-breaker), and missing input
  validation at entry points. Every recommendation names the failure it prevents,
  not just the pattern to apply. Findings are BLOCK (ship-stopper) or ADVISE
  (before first traffic). Persists gap history in out/harden/tracker.md so repeat
  runs open with what changed and flag recurring issues. Use when code works but
  needs to be production-grade — e.g. "/harden", "/harden src/orders/", "/harden
  the new auth module", "make this feature enterprise-grade", "is my code
  production-ready". For structural refactoring use refactor; for shipping
  verification use done.
---

# harden — production-ready, not just working

`/harden` — audit code in context (current diff or last-commit files)
`/harden <path>` — audit a specific file or directory

Answer one question: **which production failure modes is this code structurally
exposed to — and what prevents each one?**

Every finding follows a fixed form: the structural signal that triggered it →
the named failure mode it exposes → the pattern that prevents it → why that
pattern prevents *this* failure specifically → a concrete remediation task.
"The textbook recommends it" appears nowhere.

## Step 0 — Establish the target and check memory

**Determine what to audit:**
- `/harden` (no arg): run `git diff HEAD`; if empty, use `git diff HEAD~1 HEAD`
  to get the last commit's files.
- `/harden <path>`: audit that file or directory.
- Code mentioned in conversation: audit that code directly.

**Check memory:** read `out/harden/tracker.md` if it exists. Open with
**"Since last harden"** — which failure modes were previously found, which were
fixed, which recur. A finding marked `open` in two consecutive runs gets ⚠️
**recurring** in this run's output.

## Step 1 — The five checks

Run each check against the target. A check fires only when the structural signal
is present in the code — **absence is not a finding, and a clean result is
reported as such.** Never invent a finding to appear thorough.

---

### Check 1 — Silent error swallowing [BLOCK]

**Signal:** catch blocks that (a) swallow without any log, (b) return a zero-value
or null that erases the error context, or (c) catch a broad type (`Exception`,
`Error`, `any`) where a narrower type is possible.

**Failure mode:** the system fails silently; the operator has no signal; recovery
is impossible because the failure is invisible.

**Pattern:** typed error hierarchy + explicit propagation. Each error is either
handled (logged with context + defined recovery) or re-thrown as a typed error
with the original cause wrapped.

**Why:** typed errors make failure modes explicit in the type system; wrapping
preserves the stack; structured context makes the log searchable.

**Remediation task:** for each silent catch — (a) log with structured context and
decide on recovery, or (b) wrap and re-throw as a domain-specific error type.

---

### Check 2 — Missing observability [ADVISE]

**Signal:** operations that cross a trust boundary (HTTP call, DB query, queue
publish, auth decision) with no structured log event, or only a bare string log
(`console.log("here")`, `logger.info("done")`).

**Failure mode:** the system misbehaves in production and the operator cannot
reconstruct what happened — no timestamps, no correlation IDs, no outcome fields.

**Pattern:** structured log at every trust-boundary crossing: operation name,
correlation/trace ID, outcome (success/error), duration where latency matters.

**Why:** structured fields are queryable in any log aggregator; correlation IDs
link events across services; outcome + duration give SLOs something to measure.

**Remediation task:** for each flagged call site, emit a structured log event:
`{ op, traceId, outcome, durationMs, errorType? }`.

---

### Check 3 — Infrastructure coupling [BLOCK]

**Signal:** domain logic (business rules, use-case code) with direct calls to
infrastructure — raw SQL/ORM queries, HTTP client instantiation, filesystem reads,
cache client calls — inside functions named after domain operations, not
infrastructure operations.

**Failure mode:** domain logic cannot be unit-tested without a real
database/network; infrastructure changes force domain rewrites; no seam exists
for swapping implementations.

**Pattern:** port/repository interface — domain code depends on an interface;
infrastructure implements it. The domain function receives the dependency, not
the concrete driver.

**Why:** the interface is the seam; tests inject a fake; infrastructure is
swappable; the domain stays pure.

**Remediation task:** extract the infrastructure call behind an interface; inject
it; the domain function receives the interface, not the driver.

---

### Check 4 — No resilience at external boundaries [BLOCK]

**Signal:** calls to external systems (HTTP, gRPC, message broker, third-party API)
with no timeout, no retry with backoff, no circuit-breaker, and no fallback — a
raw call with only a happy-path response handler.

**Failure mode:** a slow or unavailable dependency cascades — the caller blocks
indefinitely, thread pool exhausts, failure propagates system-wide.

**Pattern:** timeout + retry with exponential backoff + circuit breaker at each
external call site.

**Why:** timeout bounds the worst case; retry handles transient failures; circuit
breaker stops cascade when the dependency is down; fallback keeps the caller
operational.

**Remediation task:** for each flagged call, add: explicit timeout, retry (2–3
attempts, exponential backoff), and either a circuit breaker or a defined fallback
behavior.

---

### Check 5 — Missing input validation at entry points [BLOCK]

**Signal:** public-facing entry points (HTTP handlers, queue consumers, CLI
argument parsers, public API methods) that pass inputs directly to internal logic
without schema validation, type coercion, or guard clauses.

**Failure mode:** malformed input causes unexpected failures deep in the call
stack — hard to debug, potentially exploitable, and the error message reveals
internals.

**Pattern:** validate at the boundary, trust inside. All inputs
validated/coerced at the entry point; internal functions receive trusted types.

**Why:** the entry point is the last place you control the input; validating there
gives one authoritative place for input contracts; downstream code can be simple
because it assumes valid inputs.

**Remediation task:** add schema validation or guard clauses at each flagged entry
point; return a structured error response for invalid inputs before reaching domain
logic.

---

## Step 2 — Emit findings

For each check that fired, emit one block:

```
### [BLOCK|ADVISE] <Check name>
**Location:** `<path>` line <n>
**Signal:** <quote or describe the structural pattern found>
**Failure mode:** <one sentence>
**Pattern:** <name>
**Why here:** <one sentence specific to this code, not generic>
**Task:** <concrete action, naming files/functions where known>
```

If no checks fired: state that explicitly — "No production-readiness gaps found
in the target. If you expected findings, verify the target points at
implementation code (not config, tests, or generated files)."

Close with a **severity summary**: `N BLOCK, N ADVISE`. BLOCK means don't merge
without resolution. ADVISE means schedule before first real traffic.

## Step 3 — Write the tracker

```bash
mkdir -p out/harden
```

Append a run to `out/harden/tracker.md` (create with heading if absent):

```
## <date> — <target>

| Check | Severity | Location | Status |
|---|---|---|---|
| Silent error swallowing | BLOCK | src/orders/handler.ts:42 | open |
| Missing observability | ADVISE | src/orders/handler.ts:60 | open |
```

On a re-run, carry forward open findings and flip `open → fixed (<commit>)` for
resolved ones. A finding appearing `open` in two consecutive runs gets ⚠️
**recurring** in the output and in the tracker.
