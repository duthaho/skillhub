import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

import analyze


def entry(ts, session="s1", project="/proj", model="claude-opus-4-8",
          effort="high", read=0, creation=0, c5m=None, c1h=0, inp=1,
          out=10, sidechain=False, kind="assistant"):
    if c5m is None:
        c5m = creation - c1h
    e = {
        "type": kind,
        "isSidechain": sidechain,
        "sessionId": session,
        "cwd": project,
        "timestamp": ts,
        "effort": effort,
        "message": {
            "model": model,
            "usage": {
                "input_tokens": inp,
                "cache_read_input_tokens": read,
                "cache_creation_input_tokens": creation,
                "output_tokens": out,
                "cache_creation": {
                    "ephemeral_5m_input_tokens": c5m,
                    "ephemeral_1h_input_tokens": c1h,
                },
            },
        },
    }
    return e


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def write_jsonl(dirpath, name, entries):
    os.makedirs(os.path.join(dirpath, "projects", "p"), exist_ok=True)
    path = os.path.join(dirpath, "projects", "p", name)
    with open(path, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    return path


class TmpClaude:
    def __enter__(self):
        self.d = tempfile.mkdtemp()
        return self

    def __exit__(self, *a):
        import shutil
        shutil.rmtree(self.d, ignore_errors=True)


class TestParsing(unittest.TestCase):
    def test_totals_and_hit_rate(self):
        base = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)
        entries = [
            entry(iso(base), read=0, creation=1000, inp=5),
            entry(iso(base + timedelta(minutes=1)), read=1000, creation=0, inp=3),
        ]
        with TmpClaude() as t:
            write_jsonl(t.d, "a.jsonl", entries)
            turns, stats = analyze.load_turns(t.d, days=3650, now=base + timedelta(minutes=2))
        self.assertEqual(len(turns), 2)
        tot = analyze.totals(turns)
        self.assertEqual(tot["cache_read"], 1000)
        self.assertEqual(tot["cache_creation"], 1000)
        self.assertAlmostEqual(tot["hit_rate"], 1000 / (1000 + 1000 + 8))

    def test_malformed_and_missing_fields_skipped(self):
        base = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)
        good = entry(iso(base), read=5, creation=0)
        with TmpClaude() as t:
            path = write_jsonl(t.d, "a.jsonl", [good])
            with open(path, "a") as f:
                f.write("{not json}\n")
                f.write(json.dumps({"type": "assistant", "message": {}}) + "\n")
                f.write(json.dumps({"type": "user", "message": {"usage": {}}}) + "\n")
            turns, stats = analyze.load_turns(t.d, days=3650, now=base + timedelta(minutes=1))
        self.assertEqual(len(turns), 1)
        self.assertEqual(stats["malformed_lines"], 1)

    def test_missing_timestamp_excluded_from_gap_but_counted(self):
        base = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)
        e = entry(iso(base), read=5, creation=0)
        bad = entry(None, read=0, creation=200)
        with TmpClaude() as t:
            write_jsonl(t.d, "a.jsonl", [e, bad])
            turns, stats = analyze.load_turns(t.d, days=3650, now=base + timedelta(minutes=1))
        self.assertEqual(len(turns), 2)
        self.assertEqual(stats["missing_timestamp"], 1)
        timed = [x for x in turns if x["ts"] is not None]
        self.assertEqual(len(timed), 1)

    def test_out_of_order_sorted_within_session(self):
        base = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)
        later = entry(iso(base + timedelta(minutes=5)), read=10, creation=0)
        earlier = entry(iso(base), read=0, creation=100)
        with TmpClaude() as t:
            write_jsonl(t.d, "a.jsonl", [later, earlier])
            turns, stats = analyze.load_turns(t.d, days=3650, now=base + timedelta(minutes=6))
        sessions = analyze.by_session(turns)
        seq = sessions[("/proj", "s1")]
        self.assertLess(seq[0]["ts"], seq[1]["ts"])

    def test_sidechain_partitioned(self):
        base = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)
        main = entry(iso(base), session="s1", read=0, creation=100)
        side = entry(iso(base), session="s1", sidechain=True, read=0, creation=100)
        with TmpClaude() as t:
            write_jsonl(t.d, "a.jsonl", [main, side])
            turns, stats = analyze.load_turns(t.d, days=3650, now=base + timedelta(minutes=1))
        sessions = analyze.by_session(turns)
        keys = set(sessions.keys())
        self.assertIn(("/proj", "s1"), keys)
        self.assertIn(("/proj", "s1::sidechain"), keys)

    def test_days_window_filters_old(self):
        now = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)
        old = entry(iso(now - timedelta(days=40)), read=0, creation=100)
        recent = entry(iso(now - timedelta(days=1)), read=5, creation=0)
        with TmpClaude() as t:
            write_jsonl(t.d, "a.jsonl", [old, recent])
            turns, stats = analyze.load_turns(t.d, days=30, now=now)
        self.assertEqual(len(turns), 1)


if __name__ == "__main__":
    unittest.main()
