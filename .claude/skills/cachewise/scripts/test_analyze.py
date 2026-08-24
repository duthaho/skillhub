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


class TestPricing(unittest.TestCase):
    def test_known_model_rate(self):
        rate = analyze.rate_for("claude-opus-4-8")
        self.assertEqual(rate["input"], 5.0)
        self.assertEqual(rate["output"], 25.0)
        self.assertFalse(rate["fallback"])

    def test_opus_variants(self):
        for m in ("claude-opus-5", "claude-opus-4-7", "claude-opus-4-5"):
            self.assertEqual(analyze.rate_for(m)["input"], 5.0)

    def test_haiku_and_fable(self):
        self.assertEqual(analyze.rate_for("claude-haiku-4-5-20251001")["input"], 1.0)
        self.assertEqual(analyze.rate_for("claude-fable-5")["input"], 10.0)

    def test_unknown_model_falls_back_flagged(self):
        rate = analyze.rate_for("<synthetic>")
        self.assertTrue(rate["fallback"])
        self.assertEqual(rate["input"], 3.0)

    def test_turn_cost_5m_write_and_read(self):
        t = {"model": "claude-opus-4-8", "input": 1000, "output": 100,
             "read": 2000, "creation": 4000, "creation_5m": 4000,
             "creation_1h": 0, "has_split": True}
        c = analyze.turn_cost(t)
        self.assertAlmostEqual(c["input"], 1000 * 5.0 / 1e6)
        self.assertAlmostEqual(c["read"], 2000 * 0.1 * 5.0 / 1e6)
        self.assertAlmostEqual(c["write"], 4000 * 1.25 * 5.0 / 1e6)
        self.assertAlmostEqual(c["output"], 100 * 25.0 / 1e6)

    def test_turn_cost_1h_write(self):
        t = {"model": "claude-opus-4-8", "input": 0, "output": 0,
             "read": 0, "creation": 1000, "creation_5m": 0,
             "creation_1h": 1000, "has_split": True}
        c = analyze.turn_cost(t)
        self.assertAlmostEqual(c["write"], 1000 * 2.0 * 5.0 / 1e6)

    def test_no_split_treated_as_5m(self):
        t = {"model": "claude-opus-4-8", "input": 0, "output": 0,
             "read": 0, "creation": 1000, "creation_5m": 0,
             "creation_1h": 0, "has_split": False}
        c = analyze.turn_cost(t)
        self.assertAlmostEqual(c["write"], 1000 * 1.25 * 5.0 / 1e6)

    def test_avoidable_usd_is_write_minus_hit(self):
        av = analyze.avoidable_usd(1000, "claude-opus-4-8", "5m")
        self.assertAlmostEqual(av, 1000 * (1.25 - 0.1) * 5.0 / 1e6)


def turn(ts, **kw):
    d = {"session": "s1", "project": "/p", "ts": ts, "model": "claude-opus-4-8",
         "effort": "high", "sidechain": False, "input": 2, "output": 50,
         "read": 0, "creation": 0, "creation_5m": 0, "creation_1h": 0,
         "has_split": True}
    d.update(kw)
    if kw.get("creation") and not kw.get("creation_5m") and not kw.get("creation_1h"):
        d["creation_5m"] = d["creation"]
    return d


class TestWithinSession(unittest.TestCase):
    B = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)

    def seq(self, *turns):
        return analyze.attribute_session(list(turns))

    def test_idle_gap_rebuild(self):
        ev = self.seq(
            turn(self.B, read=20000, creation=20000),
            turn(self.B.replace(minute=15), read=0, creation=20000),
        )
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["cause"], "idle_gap")

    def test_idle_gap_with_switch_tagged(self):
        ev = self.seq(
            turn(self.B, read=20000, creation=20000),
            turn(self.B.replace(minute=15), read=0, creation=20000,
                 model="claude-opus-4-7"),
        )
        self.assertEqual(ev[0]["cause"], "idle_gap")
        self.assertIn("switch", ev[0]["tags"])

    def test_model_switch_within_ttl(self):
        ev = self.seq(
            turn(self.B, read=20000, creation=20000),
            turn(self.B.replace(minute=1), read=0, creation=20000,
                 model="claude-opus-4-7"),
        )
        self.assertEqual(ev[0]["cause"], "model_switch")

    def test_effort_switch_within_ttl(self):
        ev = self.seq(
            turn(self.B, read=20000, creation=20000),
            turn(self.B.replace(minute=1), read=0, creation=20000, effort="xhigh"),
        )
        self.assertEqual(ev[0]["cause"], "model_switch")

    def test_write_churn(self):
        ev = self.seq(
            turn(self.B, read=20000, creation=20000),
            turn(self.B.replace(minute=1), read=0, creation=20000),
        )
        self.assertEqual(ev[0]["cause"], "write_churn")

    def test_small_incremental_write_not_a_miss(self):
        ev = self.seq(
            turn(self.B, read=20000, creation=20000),
            turn(self.B.replace(minute=1), read=20000, creation=500),
        )
        self.assertEqual(ev, [])

    def test_below_cache_floor_ignored(self):
        ev = self.seq(
            turn(self.B, read=1000, creation=1000),
            turn(self.B.replace(minute=15), read=0, creation=1000),
        )
        self.assertEqual(ev, [])

    def test_missing_timestamp_unattributed(self):
        ev = self.seq(
            turn(self.B, read=20000, creation=20000),
            turn(None, read=0, creation=20000),
        )
        self.assertEqual(ev[0]["cause"], "unattributed")

    def test_unknown_model_not_counted_as_switch(self):
        ev = self.seq(
            turn(self.B, read=20000, creation=20000, model="<synthetic>"),
            turn(self.B.replace(minute=1), read=0, creation=20000,
                 model="claude-opus-4-8"),
        )
        self.assertEqual(ev[0]["cause"], "write_churn")


class TestContextTax(unittest.TestCase):
    B = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)

    def test_sprawl_session_flagged_lean_not(self):
        lean = {("/p", "lean"): [
            turn(self.B.replace(minute=m), session="lean", read=10000)
            for m in range(0, 10)
        ]}
        # many other lean sessions to set the baseline median ~10k
        sessions = dict(lean)
        for s in range(5):
            sessions[("/p", "b%d" % s)] = [
                turn(self.B.replace(minute=m), session="b%d" % s, read=10000)
                for m in range(0, 5)
            ]
        # one bloated session carrying ~300k/turn over many turns
        sessions[("/p", "sprawl")] = [
            turn(self.B.replace(hour=12 + (m // 6), minute=(m * 7) % 60),
                 session="sprawl", read=300000)
            for m in range(0, 30)
        ]
        tax = analyze.context_tax(sessions)
        top = {t["session"]: t for t in tax["top_sessions"]}
        self.assertIn("sprawl", top)
        self.assertGreater(top["sprawl"]["excess_usd"], 0)
        self.assertNotIn("lean", top)

    def test_single_session_no_false_positive(self):
        sessions = {("/p", "solo"): [
            turn(self.B.replace(minute=m), session="solo", read=200000)
            for m in range(0, 10)
        ]}
        tax = analyze.context_tax(sessions)
        self.assertEqual(tax["total_excess_usd"], 0)


if __name__ == "__main__":
    unittest.main()
