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
    creation = int(u.get("cache_creation_input_tokens") or 0)
    c5m = cc.get("ephemeral_5m_input_tokens")
    c1h = cc.get("ephemeral_1h_input_tokens")
    has_split = c5m is not None or c1h is not None
    c5m = int(c5m or 0)
    c1h = int(c1h or 0)
    return {
        "session": d.get("sessionId") or "unknown",
        "project": d.get("cwd") or "unknown",
        "ts": parse_ts(d.get("timestamp")),
        "model": msg.get("model") or "unknown",
        "effort": d.get("effort"),
        "sidechain": bool(d.get("isSidechain")),
        "input": int(u.get("input_tokens") or 0),
        "output": int(u.get("output_tokens") or 0),
        "read": int(u.get("cache_read_input_tokens") or 0),
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


def main(argv=None):
    p = argparse.ArgumentParser(description="Cachewise cache-economics analyzer")
    p.add_argument("--claude-dir", default="~/.claude")
    p.add_argument("--days", type=int, default=30)
    args = p.parse_args(argv)
    turns, stats = load_turns(args.claude_dir, days=args.days)
    out = {"stats": stats, "totals": totals(turns)}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
