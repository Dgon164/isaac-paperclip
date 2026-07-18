"""facts_layer_battery.py — PROMOTION GATE for THE FACTS LAYER
(owner, 2026-07-18: "we have the main structural information, and
then datapoint breakdowns he can reference and save... sampling for
context and reference. give him some kind of memory").

Two layers: STRUCTURE (laws/series — what he understands) and FACTS
(sampled datapoints kept with the structure they earned — what he
remembers). Evidence is deterministic, capped, referenceable; the
watch's drift duel becomes a REPLAY COURT (remembered rows + the
new batch — the incumbent's world represented).

  E1 EVIDENCE AT MINTING: a discovered law carries its sampled
     breakdown — extremes present, spread present, capped, source
     count kept.
  E2 SAME DATA, SAME MEMORY: two minds fed identically remember
     byte-identically (the artifact claim extended to memory).
  E3 REFERENCE: context_sample near a query returns the true
     nearest remembered exemplars.
  E4 SERIES MEMORY: an analyzed series remembers sampled points AND
     its largest leftovers (the residual's own witnesses).
  E5 PERSISTENCE: memory survives save/load; recall works after
     resurrection.
  E6 THE REPLAY COURT: on drift, the duel runs on remembered + new
     rows (court receipt says so) and the incumbent is honestly
     superseded, loser kept.
  E7 SIZE DISCIPLINE: evidence is capped (<= 24 rows however large
     the source) and the whole mind stays small — complete numbers.

Run: cd experiments && PYTHONHASHSEED=0 python facts_layer_battery.py
"""
import os
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    rng = np.random.default_rng(0)
    n = 400
    x = rng.uniform(0, 10, n)
    y = 3.0 * x + 2.0 + rng.normal(0, 0.05, n)
    X = x.reshape(-1, 1)

    # E1 — evidence at minting
    m1 = Isaac()
    m1.discover(X, y, name="line")
    ev = m1.recall_evidence("line")
    rows = np.asarray(ev["rows"], float)
    ok1 = (ev is not None and 4 <= len(rows) <= 24
           and ev["n_source"] == n
           and abs(rows[:, 0].min() - x.min()) < 1e-9
           and abs(rows[:, 0].max() - x.max()) < 1e-9)
    check("E1 evidence at minting — extremes + spread, capped, "
          "source counted", ok1,
          f"{len(rows)} rows of {ev['n_source']} ({ev['why']})")

    # E2 — same data, same memory
    m2 = Isaac()
    m2.discover(X, y, name="line")
    ok2 = m2.recall_evidence("line") == ev
    check("E2 same data, same memory — deterministic to the byte",
          ok2, "identical evidence dicts")

    # E3 — reference: nearest remembered exemplars
    ctx = m1.context_sample("line", [5.0], k=3)
    true_near = rows[np.argsort(np.abs(rows[:, 0] - 5.0))[:3], 0]
    ok3 = (ctx is not None and len(ctx) == 3
           and abs(ctx[0]["x"][0] - true_near[0]) < 1e-9
           and abs(ctx[0]["y"] - (3.0 * ctx[0]["x"][0] + 2.0)) < 0.2)
    check("E3 reference — context_sample returns the true nearest "
          "remembered", ok3,
          f"query 5.0 -> x {[round(c['x'][0], 2) for c in ctx]}")

    # E4 — series memory with its leftovers
    tt = np.arange(200, dtype=float)
    ys = 0.5 * tt + 10.0 + rng.normal(0, 0.3, 200)
    ys[70] += 9.0                          # a leftover worth naming
    m4 = Isaac()
    m4.analyze_series(tt, ys, name="tracked")
    ev4 = m4.recall_evidence("tracked")
    ok4 = (ev4 is not None and len(ev4["rows"]) >= 4
           and len(ev4.get("leftovers", [])) == 3
           and any(lo["t"] == 70.0 for lo in ev4["leftovers"]))
    check("E4 series memory — sampled points + the largest leftovers "
          "named", ok4,
          f"{len(ev4['rows'])} points; leftovers at "
          f"{[lo['t'] for lo in ev4['leftovers']]}")

    # E5 — persistence through save/load
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "m.isaac")
        m1.save(p)
        m5 = Isaac.load(p)
        ok5 = (m5.recall_evidence("line") == ev
               and m5.context_sample("line", [2.0]) is not None)
        check("E5 persistence — memory survives resurrection", ok5,
              "recall + context after load")

    # E6 — the replay court on drift
    m6 = Isaac()
    xb = rng.uniform(0, 10, 60)
    m6.discover(xb.reshape(-1, 1), 3.0 * xb + 2.0
                + rng.normal(0, 0.05, 60), name="drifty")
    xw = rng.uniform(0, 10, 60)
    m6.watch("drifty", xw.reshape(-1, 1),
             3.0 * xw + 2.0 + rng.normal(0, 0.05, 60))
    xd = rng.uniform(0, 10, 60)
    r6 = m6.watch("drifty", xd.reshape(-1, 1),
                  3.9 * xd + 2.0 + rng.normal(0, 0.05, 60))
    ok6 = (r6["verdict"] == "DRIFT"
           and "remembered" in r6.get("duel_court", "")
           and r6.get("duel") is not None)
    check("E6 the replay court — drift duels on remembered + new, "
          "receipt says so", ok6,
          f"{r6['verdict']}; court: {r6.get('duel_court')}; duel "
          f"{r6.get('duel')}")

    # E7 — size discipline, complete numbers
    big = rng.uniform(0, 100, 20000)
    m7 = Isaac()
    m7.discover(big.reshape(-1, 1),
                2.0 * big + rng.normal(0, 0.1, 20000), name="big")
    ev7 = m7.recall_evidence("big")
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "m.isaac")
        m7.save(p)
        kb = os.path.getsize(p) / 1000.0
    ok7 = len(ev7["rows"]) <= 24 and ev7["n_source"] == 20000 and kb < 500
    check("E7 size discipline — 20,000 rows remembered as <=24, "
          "mind stays small", ok7,
          f"{len(ev7['rows'])} rows kept of 20000; mind {kb:.0f} KB")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
