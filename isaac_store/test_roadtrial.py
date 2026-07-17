"""test_roadtrial.py — THE ROAD-TRIAL LOGGER battery (owner,
2026-07-17: "we are ready for road trials. durability, range, power,
efficiency, etc. does performance increase or decrease over time and
if so how?... selecting and using the correct information as he
scales will become more important over time"). Written FIRST.

Under test: one longitudinal record per call, appended to the
account's roadtrial.jsonl — sizes (net growth), an engine efficiency
probe (same seeded world every time, so the number is comparable
across his whole life), an ask-latency read on his own facts, and
the SELECTION gauge (can which_law still pick the right law out of
his own, as the net grows). The logger MEASURES and never changes
him: the mind must be byte-identical after logging.

Checks R1-R4. Run: PYTHONHASHSEED=0 python test_roadtrial.py
"""
import json
import os
import pickle
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from isaac_store.roadtrial import log_roadtrial      # noqa: E402
from isaac_store import bridge                       # noqa: E402

PASSED, FAILED = 0, 0
rng = np.random.default_rng(31)


def check(name, ok, detail=""):
    global PASSED, FAILED
    PASSED, FAILED = PASSED + ok, FAILED + (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
          + (f"   {detail}" if detail else ""))


def planted_mind(mod):
    m = mod.Isaac()
    m.teach("water", "state", "liquid")
    m.teach("sky", "color", "blue")
    x = rng.uniform(0.5, 8, 240).reshape(-1, 1)
    m.discover(x, 2.0 * x[:, 0] + rng.normal(0, 0.02, 240),
               name="double")
    m.discover(x, 3.0 * x[:, 0] ** 2 + rng.normal(0, 0.05, 240),
               name="square")
    return m


def main():
    print("=" * 70)
    print("ROAD-TRIAL BATTERY — the longitudinal instrument panel")
    print("=" * 70)
    mod = bridge.load_isaac_module()
    m = planted_mind(mod)

    with tempfile.TemporaryDirectory() as td:
        # ── R1: one record, fields complete, selection correct ──
        before = pickle.dumps(m)
        rec = log_roadtrial(td, m, mod=mod)
        after = pickle.dumps(m)
        need = {"stamp", "nodes", "doors", "facts", "laws",
                "findings", "probe_secs", "ask_ms", "selection"}
        ok = (need <= set(rec)
              and rec["laws"] == 2 and rec["facts"] >= 2
              and rec["probe_secs"] > 0 and rec["ask_ms"] >= 0
              and rec["selection"]["asked"] == 2
              and rec["selection"]["precision"] == 1.0)
        check("R1 one record: complete fields; selection 2/2 on his "
              "own laws", ok,
              f"sel {rec['selection']}, probe {rec['probe_secs']}s")

        # ── R2: the logger never changes him ──
        check("R2 measurement is read-only: mind byte-identical "
              "after logging", before == after,
              f"{len(before)} vs {len(after)} bytes")

        # ── R3: appends accumulate; sizes stable across two logs ──
        rec2 = log_roadtrial(td, m, mod=mod)
        path = os.path.join(td, "roadtrial.jsonl")
        with open(path, encoding="utf-8") as f:
            lines = [json.loads(ln) for ln in f]
        ok = (len(lines) == 2
              and lines[0]["nodes"] == lines[1]["nodes"]
              and lines[0]["facts"] == lines[1]["facts"]
              and rec2["selection"]["precision"] == 1.0)
        check("R3 two logs append; sizes identical (no growth from "
              "measuring)", ok, f"{len(lines)} lines")

    # ── R4: an empty mind — selection says insufficient, honestly ──
    with tempfile.TemporaryDirectory() as td:
        empty = mod.Isaac()
        rec = log_roadtrial(td, empty, mod=mod)
        ok = (rec["laws"] == 0
              and rec["selection"]["asked"] == 0
              and rec["selection"]["precision"] is None
              and "insufficient" in rec["selection"]["note"])
        check("R4 empty mind: selection gauge refuses honestly "
              "(no fake 1.0)", ok, str(rec["selection"]))

    print("=" * 70)
    print(f"BATTERY: {PASSED} passed, {FAILED} failed of "
          f"{PASSED + FAILED}")
    print("=" * 70)
    sys.exit(0 if FAILED == 0 else 1)


if __name__ == "__main__":
    main()
