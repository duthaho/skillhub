#!/usr/bin/env python3
"""Cachewise — prompt-cache economics forensics over Claude Code transcripts.

Reads ~/.claude/projects/**/*.jsonl, attributes cache-miss creation tokens to
causes, prices them in USD-equivalent, and emits one JSON document. Stdlib
only; deterministic; malformed input skipped and counted, never fatal.
"""
import argparse
import glob
import json
import os
from collections import defaultdict
from datetime import datetime, timezone


# API list prices per million tokens, verified against
# platform.claude.com/docs/en/about-claude/pricing on this date. USD.
PRICING_ASOF = "2026-08-24"
# (model-id substring, base-input $/MTok, output $/MTok) — checked in order,
# most specific first. Cache prices derive from base input via the standard
# multipliers (5m write 1.25x, 1h write 2x, read 0.1x).
_PRICE_TABLE = [
    ("opus-4-1", 15.0, 75.0),
    ("opus-4.1", 15.0, 75.0),
    ("opus-5", 5.0, 25.0),
    ("opus-4", 5.0, 25.0),
    ("sonnet-5", 2.0, 10.0),
    ("sonnet-4", 3.0, 15.0),
    ("haiku-4", 1.0, 5.0),
    ("haiku-3", 0.80, 4.0),
    ("fable-5", 10.0, 50.0),
    ("mythos-5", 10.0, 50.0),
]
_FALLBACK = (3.0, 15.0)  # Sonnet 4.x — used for unknown/synthetic model ids
WRITE_5M_MULT = 1.25
WRITE_1H_MULT = 2.0
READ_MULT = 0.1


def _matches(key, m):
    # substring match, but the char after the key must not be a digit — so
    # "opus-4-1" (Opus 4.1) doesn't swallow a future "opus-4-10".
    start = 0
    while True:
        i = m.find(key, start)
        if i < 0:
            return False
        after = i + len(key)
        if after >= len(m) or not m[after].isdigit():
            return True
        start = i + 1


def rate_for(model):
    m = (model or "").lower()
    for key, inp, out in _PRICE_TABLE:
        if _matches(key, m):
            return {"input": inp, "output": out, "fallback": False}
    return {"input": _FALLBACK[0], "output": _FALLBACK[1], "fallback": True}


def turn_cost(t):
    r = rate_for(t.get("model"))
    inp_rate = r["input"] / 1e6
    if t.get("has_split", True):
        write = (t.get("creation_5m", 0) * WRITE_5M_MULT
                 + t.get("creation_1h", 0) * WRITE_1H_MULT) * inp_rate
    else:
        write = t.get("creation", 0) * WRITE_5M_MULT * inp_rate
    return {
        "input": t.get("input", 0) * inp_rate,
        "read": t.get("read", 0) * READ_MULT * inp_rate,
        "write": write,
        "output": t.get("output", 0) * r["output"] / 1e6,
        "fallback": r["fallback"],
    }


def avoidable_usd(tokens, model, ttl="5m"):
    """USD that a cache hit would have saved vs re-writing these tokens."""
    inp_rate = rate_for(model)["input"] / 1e6
    write_mult = WRITE_1H_MULT if ttl == "1h" else WRITE_5M_MULT
    return tokens * (write_mult - READ_MULT) * inp_rate


def parse_ts(v):
    if not isinstance(v, str):
        return None
    s = v.strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0  # tolerate garbage numeric fields, never crash (spec A1)


def parse_entry(d):
    if not isinstance(d, dict) or d.get("type") != "assistant":
        return None
    msg = d.get("message")
    if not isinstance(msg, dict):
        return None
    u = msg.get("usage")
    if not isinstance(u, dict):
        return None
    cc = u.get("cache_creation")
    cc = cc if isinstance(cc, dict) else {}
    creation = _int(u.get("cache_creation_input_tokens"))
    c5m = cc.get("ephemeral_5m_input_tokens")
    c1h = cc.get("ephemeral_1h_input_tokens")
    has_split = c5m is not None or c1h is not None
    c5m = _int(c5m)
    c1h = _int(c1h)
    return {
        "session": d.get("sessionId") or "unknown",
        "project": d.get("cwd") or "unknown",
        "ts": parse_ts(d.get("timestamp")),
        "model": msg.get("model") or "unknown",
        "effort": d.get("effort"),
        "sidechain": bool(d.get("isSidechain")),
        "input": _int(u.get("input_tokens")),
        "output": _int(u.get("output_tokens")),
        "read": _int(u.get("cache_read_input_tokens")),
        "creation": creation,
        "creation_5m": c5m,
        "creation_1h": c1h,
        "has_split": has_split,
    }


def load_turns(claude_dir, days=30, now=None):
    now = now or datetime.now(timezone.utc)
    cutoff = now.timestamp() - days * 86400
    pattern = os.path.join(os.path.expanduser(claude_dir), "projects", "**", "*.jsonl")
    stats = {"files": 0, "malformed_lines": 0, "missing_timestamp": 0, "turns": 0}
    turns = []
    for path in sorted(glob.glob(pattern, recursive=True)):
        stats["files"] += 1
        try:
            fh = open(path, "r", encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except (ValueError, TypeError):
                    stats["malformed_lines"] += 1
                    continue
                t = parse_entry(d)
                if t is None:
                    continue
                if t["ts"] is None:
                    stats["missing_timestamp"] += 1
                elif t["ts"].timestamp() < cutoff:
                    continue
                turns.append(t)
    stats["turns"] = len(turns)
    return turns, stats


def by_session(turns):
    groups = defaultdict(list)
    for t in turns:
        session = t["session"] + ("::sidechain" if t["sidechain"] else "")
        groups[(t["project"], session)].append(t)
    for key, seq in groups.items():
        seq.sort(key=lambda t: (t["ts"] is None, t["ts"] or datetime.min.replace(tzinfo=timezone.utc)))
    return groups


# A rebuild only counts as a miss when the re-created chunk is comparable to
# the cache that was alive — this gate is what keeps normal incremental writes
# (small deltas of new content) from being mislabeled as waste.
REBUILD_RATIO = 0.5
CACHE_FLOOR = 5000
TTL_5M = 300
TTL_1H = 3600


def _switched(t, prev):
    model_sw = (t["model"] != prev["model"]
                and "unknown" not in (t["model"], prev["model"])
                and "<synthetic>" not in (t["model"], prev["model"]))
    effort_sw = bool(t["effort"]) and bool(prev["effort"]) and t["effort"] != prev["effort"]
    return model_sw or effort_sw


def attribute_session(seq):
    """Classify within-session cache rebuilds. Returns one event per miss."""
    events = []
    established = 0
    for i, t in enumerate(seq):
        if i > 0:
            prev = seq[i - 1]
            c = t["creation"]
            if c > 0 and established >= CACHE_FLOOR and c >= REBUILD_RATIO * established:
                ttl = "1h" if (t["creation_1h"] > 0 or prev["creation_1h"] > 0) else "5m"
                window = TTL_1H if ttl == "1h" else TTL_5M
                gap = None
                if t["ts"] is not None and prev["ts"] is not None:
                    gap = (t["ts"] - prev["ts"]).total_seconds()
                switched = _switched(t, prev)
                tags = []
                if gap is None:
                    cause = "unattributed"
                elif gap > window:
                    cause = "idle_gap"
                    if switched:
                        tags.append("switch")
                elif switched:
                    cause = "model_switch"
                else:
                    cause = "write_churn"
                events.append({
                    "cause": cause, "tokens": c, "ttl": ttl, "gap": gap,
                    "tags": tags, "usd": avoidable_usd(c, t["model"], ttl),
                    "session": t["session"], "project": t["project"],
                    "model": t["model"],
                })
        # cache alive after this turn ≈ prefix read + increment written; a
        # cold-start turn (read=0, creation>0) still establishes a cache.
        established = max(established, t["read"] + t["creation"])
    return events


SPRAWL_TOP_N = 5


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return 0
    mid = n // 2
    return xs[mid] if n % 2 else (xs[mid - 1] + xs[mid]) / 2


def context_tax(sessions):
    """Read-cost of carrying more prefix than a typical same-model session.

    Not a cache *miss* — it's the standing tax of oversized sessions. Baseline
    is the per-model median per-turn read, so long-but-necessary context isn't
    penalized against a different model's norm. Conservative: a session is only
    charged for reads above its own model's median, and a lone session (no
    baseline) shows zero.
    """
    reads_by_model = defaultdict(list)
    sessions_by_model = defaultdict(set)
    for (project, session), seq in sessions.items():
        for t in seq:
            if t["read"] > 0:
                reads_by_model[t["model"]].append(t["read"])
                sessions_by_model[t["model"]].add((project, session))
    # a baseline needs more than one session; a lone session has no norm to
    # be judged against, so it's never charged context tax.
    median = {m: _median(v) for m, v in reads_by_model.items()
              if len(sessions_by_model[m]) >= 2}

    rows = []
    total = 0.0
    for (project, session), seq in sessions.items():
        excess_usd = 0.0
        excess_tokens = 0
        reads = [t["read"] for t in seq if t["read"] > 0]
        for t in seq:
            if t["model"] not in median:
                continue
            base = median[t["model"]]
            over = t["read"] - base
            if over > 0:
                excess_tokens += over
                excess_usd += over * READ_MULT * rate_for(t["model"])["input"] / 1e6
        if excess_usd <= 0:
            continue
        tss = [t["ts"] for t in seq if t["ts"] is not None]
        span_h = ((max(tss) - min(tss)).total_seconds() / 3600) if len(tss) > 1 else 0.0
        total += excess_usd
        rows.append({
            "project": project, "session": session, "turns": len(seq),
            "span_hours": round(span_h, 1),
            "mean_read": int(sum(reads) / len(reads)) if reads else 0,
            "excess_tokens": excess_tokens, "excess_usd": excess_usd,
        })
    rows.sort(key=lambda r: r["excess_usd"], reverse=True)
    return {
        "total_excess_usd": total,
        "top_sessions": rows[:SPRAWL_TOP_N],
    }


DEAD_SESSION_WINDOW_H = 2.0


def _session_span(seq):
    timed = [t for t in seq if t["ts"] is not None]
    if not timed:
        return None
    return {
        "start": timed[0]["ts"], "end": timed[-1]["ts"],
        "last_read": timed[-1]["read"],
        "first_creation": timed[0]["creation"], "model": timed[0]["model"],
    }


def attribute_cross_session(sessions):
    """Cold re-boot of a same-project session shortly after another ended —
    work that likely could have continued in the warm session. Strict and
    labeled low-confidence: same project, prior session fully ended before this
    one started, within the window, and this boot re-creates a chunk comparable
    to the prior session's live cache. Sidechains (sub-agents) are excluded."""
    by_project = defaultdict(list)
    for (project, session), seq in sessions.items():
        if session.endswith("::sidechain"):
            continue
        span = _session_span(seq)
        if span:
            span["session"] = session
            span["project"] = project
            by_project[project].append(span)

    events = []
    window = DEAD_SESSION_WINDOW_H * 3600
    for project, spans in by_project.items():
        spans.sort(key=lambda s: s["start"])
        for i, s in enumerate(spans):
            if s["first_creation"] <= 0:
                continue
            for p in spans[:i]:
                if p["end"] >= s["start"]:
                    continue
                if (s["start"] - p["end"]).total_seconds() > window:
                    continue
                if p["last_read"] < CACHE_FLOOR:
                    continue
                if s["first_creation"] >= REBUILD_RATIO * p["last_read"]:
                    events.append({
                        "cause": "dead_session", "tokens": s["first_creation"],
                        "usd": avoidable_usd(s["first_creation"], s["model"], "5m"),
                        "low_confidence": True, "project": project,
                        "session": s["session"], "model": s["model"],
                    })
                    break
    return events


def roll_up(events):
    causes = {}
    for e in events:
        c = causes.setdefault(e["cause"], {"events": 0, "tokens": 0, "usd": 0.0})
        c["events"] += 1
        c["tokens"] += e["tokens"]
        c["usd"] += e["usd"]
    return causes


def totals(turns):
    read = sum(t["read"] for t in turns)
    creation = sum(t["creation"] for t in turns)
    inp = sum(t["input"] for t in turns)
    out = sum(t["output"] for t in turns)
    denom = read + creation + inp
    return {
        "input": inp,
        "output": out,
        "cache_read": read,
        "cache_creation": creation,
        "creation_5m": sum(t["creation_5m"] for t in turns),
        "creation_1h": sum(t["creation_1h"] for t in turns),
        "hit_rate": (read / denom) if denom else 0.0,
    }


_FIX = {
    "idle_gap": "Idle gaps past the cache TTL are your biggest rebuild cost. "
                "Return to the session within the window, or batch questions so "
                "the agent isn't left waiting past the ~5-min TTL — the cache you "
                "already paid for expires and gets rewritten at 1.25x.",
    "model_switch": "Pin one model/effort per session. Switching mid-session "
                    "invalidates the cached prefix and rewrites the whole thing.",
    "write_churn": "Mid-session rebuilds with no idle gap point at prefix churn: "
                   "MCP tool-list changes, an edited CLAUDE.md/system prompt, or "
                   "dynamic content (timestamps) near the top. Keep the prefix "
                   "byte-stable across turns.",
    "dead_session": "You restarted a cold session for the same project soon after "
                    "another ended, re-paying the initial build. Resume the prior "
                    "session (--resume / resume-from-summary) instead of starting "
                    "fresh. (low-confidence heuristic)",
    "unattributed": "Rebuilds whose cause couldn't be determined from the "
                    "transcript (usually missing timestamps).",
    "context_tax": "These sessions carry far more prefix per turn than your norm. "
                   "One task per session — /clear or a handoff brief between tasks "
                   "— shrinks the context re-read (and re-billed) every turn.",
}


def _offenders(events, key, n=5):
    agg = defaultdict(lambda: {"usd": 0.0, "tokens": 0})
    for e in events:
        a = agg[e[key]]
        a["usd"] += e["usd"]
        a["tokens"] += e["tokens"]
    rows = [{key: k, **v} for k, v in agg.items()]
    rows.sort(key=lambda r: r["usd"], reverse=True)
    return rows[:n]


def build_report(turns, sessions, stats, days):
    miss_events = []
    for seq in sessions.values():
        miss_events.extend(attribute_session(seq))
    dead_events = attribute_cross_session(sessions)
    causes = roll_up(miss_events)
    tax = context_tax(sessions)

    tot = totals(turns)
    spent = {"input": 0.0, "read": 0.0, "write": 0.0, "output": 0.0}
    fallback_models = set()
    for t in turns:
        c = turn_cost(t)
        for k in spent:
            spent[k] += c[k]
        if c["fallback"]:
            fallback_models.add(t["model"])
    spent["total"] = sum(spent.values())

    miss_usd = sum(c["usd"] for c in causes.values())
    dead_usd = sum(e["usd"] for e in dead_events)

    presc = []
    for cause, agg in causes.items():
        presc.append({"cause": cause, "usd": agg["usd"], "tokens": agg["tokens"],
                      "fix": _FIX.get(cause, "")})
    if tax["total_excess_usd"] > 0:
        presc.append({"cause": "context_tax", "usd": tax["total_excess_usd"],
                      "tokens": sum(r["excess_tokens"] for r in tax["top_sessions"]),
                      "fix": _FIX["context_tax"]})
    if dead_usd > 0:
        presc.append({"cause": "dead_session", "usd": dead_usd,
                      "tokens": sum(e["tokens"] for e in dead_events),
                      "fix": _FIX["dead_session"], "low_confidence": True})
    presc.sort(key=lambda p: p["usd"], reverse=True)

    return {
        "meta": {"days": days, "pricing_asof": PRICING_ASOF},
        "stats": stats,
        "totals": {**tot, "usd": spent},
        "miss_attribution": {
            "causes": causes, "total_usd": miss_usd,
            "invariant_tokens": sum(c["tokens"] for c in causes.values()),
        },
        "dead_session": {"events": len(dead_events), "usd": dead_usd,
                         "low_confidence": True,
                         "sessions": dead_events[:SPRAWL_TOP_N]},
        "context_tax": tax,
        "top_offenders": {
            "sessions": _offenders(miss_events, "session"),
            "projects": _offenders(miss_events, "project"),
        },
        "prescriptions": presc,
        "flags": {
            "pricing_fallback_models": sorted(fallback_models),
            "missing_timestamp_turns": stats.get("missing_timestamp", 0),
            "malformed_lines": stats.get("malformed_lines", 0),
        },
    }


def run(claude_dir, days=30, now=None):
    turns, stats = load_turns(claude_dir, days=days, now=now)
    sessions = by_session(turns)
    return build_report(turns, sessions, stats, days)


def main(argv=None):
    p = argparse.ArgumentParser(description="Cachewise cache-economics analyzer")
    p.add_argument("--claude-dir", default="~/.claude")
    p.add_argument("--days", type=int, default=30)
    args = p.parse_args(argv)
    print(json.dumps(run(args.claude_dir, days=args.days), indent=2))


if __name__ == "__main__":
    main()
