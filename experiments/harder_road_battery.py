"""harder_road_battery.py — PROMOTION GATE for THE GROWING GRAMMAR
rung 2 (owner, 2026-07-18: "ideally we have a system that can grow
and expand and experiment... look for novel solutions, not just the
ones we programmed").

Engine road ONLY (the probe's shims moved into isaac.py:
register_composite gained powerprod, _augment_with builds the grown
word's column, discover_harder is the escalation organ). Pins:

  HB1 THE WALL: plain discover stays dark on clean g=66.74*M/R^2
      (the vocabulary ceiling that started this — never silently
      cured by accident).
  HB2 THE NOVEL SOLUTION: discover_harder courts a composed
      coordinate to UNDERSTOOD; the final law wears the composite's
      NAME (legible via the registry) and the constant is exact.
  HB3 THE AIM: receipts name exactly {M, R}; the decoy is never
      named.
  HB4 THE GROWTH: a fresh same-form world (Coulomb-shaped) is
      solved by the PLAIN road — the earned word is offered
      automatically — and the two laws crystallize across their
      containers.
  HB5 THE HONEST PARTIAL: the 11 real bodies say the form
      (+66.74*c) with belief kept PARTIAL (residual above floor —
      rotation/oblateness ARE dark to the point-mass form); the law
      still APPLIES to raw columns (Eris predicted, never fed); a
      PARTIAL law never crystallizes (the tooth, excluded receipt).
  HB6 THE NULL: scrambled y refuses to dig (receipt), registers
      nothing, mints nothing.
  HB7 PERSISTENCE: the grown word survives save/load and still
      carries a fresh world through the plain road.

Run: cd experiments && PYTHONHASHSEED=0 python harder_road_battery.py
"""
import os
import sys
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
    M = rng.uniform(0.05, 2000, 200)
    R = rng.uniform(1.5, 70, 200)
    X = np.column_stack([M, R, rng.normal(0, 1, 200)])
    y = 66.74 * M / R ** 2

    # HB1 — the wall stands on the plain road
    m1 = Isaac()
    plain = m1.discover(X, y, name="gravity-plain")
    check("HB1 the wall — plain road dark on the clean world",
          plain["verdict"] != "UNDERSTOOD",
          f"plain: {plain['verdict']} (r2 {plain['r2']:.3f})")

    # HB2 — the novel solution, legible through the registry
    mind = Isaac()
    res = mind.discover_harder(X, y, name="gravity-hard")
    rec = res.get("harder", {})
    n_pp = sum(1 for c in mind.composites if c["op"] == "powerprod")
    ok2 = (res["verdict"] == "UNDERSTOOD" and rec.get("mint")
           and rec["mint"] in res.get("equation", "")
           and n_pp == 1)
    check("HB2 the novel solution — courted UNDERSTOOD, law wears "
          "the grown word's name", ok2,
          f"mint {rec.get('mint')}; eq {res.get('equation', '')[:44]}; "
          f"tried {rec.get('tried')}")

    # HB3 — the aim names exactly {M, R}
    check("HB3 the aim — receipts name exactly {x0,x1}, decoy out",
          rec.get("named") == [0, 1],
          f"named {rec.get('named')}, drops {rec.get('drops')}")

    # HB4 — the growth: plain road + crystallized kinship
    q = rng.uniform(0.1, 100, 160)
    r_ = rng.uniform(0.5, 20, 160)
    Xc = np.column_stack([q, r_, rng.normal(0, 1, 160)])
    res4 = mind.discover(Xc, 8.99 * q / r_ ** 2, name="coulomb-shaped")
    fams = mind.crystallize_forms()
    ok4 = (res4["verdict"] == "UNDERSTOOD"
           and rec["mint"] in res4.get("equation", "")
           and len(fams["families"]) >= 1)
    check("HB4 the growth — fresh world solved PLAIN via the earned "
          "word; kinship crystallizes", ok4,
          f"eq {res4.get('equation', '')[:40]}; families "
          f"{len(fams['families'])}")

    # HB5 — the honest PARTIAL on the 11 real bodies
    Mr = np.array([1989000.0, 0.330, 4.87, 5.97, 0.073, 0.642,
                   1898.0, 568.0, 86.8, 102.0, 0.0130])
    Rr = np.array([696.0, 2.4397, 6.0518, 6.371, 1.7374, 3.3895,
                   69.911, 58.232, 25.362, 24.622, 1.1883])
    gr = np.array([274.0, 3.70, 8.87, 9.81, 1.62, 3.71, 24.79,
                   10.44, 8.87, 11.15, 0.62])
    o = np.random.default_rng(4).permutation(11)
    m5 = Isaac()
    res5 = m5.discover_harder(np.column_stack([Mr, Rr])[o], gr[o],
                              name="planet-gravity")
    rec5 = res5.get("harder", {})
    eris = m5.apply_law("planet-gravity",
                        np.array([[0.0166, 1.163]]))
    crys5 = m5.crystallize_forms()
    excl = any(e["node"] == "law:planet-gravity"
               for e in crys5["excluded"])
    ok5 = (res5["verdict"] == "PARTIAL" and res5["r2"] > 0.99
           and rec5.get("mint")
           and eris is not None
           and abs(float(eris[0]) - 0.82) < 0.05
           and excl)
    check("HB5 honest PARTIAL — form said, belief withheld, law "
          "applies (Eris), never crystallizes", ok5,
          f"{res5['verdict']} r2 {res5['r2']:.4f}; Eris "
          f"{float(eris[0]) if eris is not None else None:.3f} "
          f"(true ~0.82); excluded receipt: {excl}")

    # HB6 — the null refuses to dig
    ys = y.copy()
    np.random.default_rng(3).shuffle(ys)
    m6 = Isaac()
    res6 = m6.discover_harder(X, ys, name="gravity-scrambled")
    rec6 = res6.get("harder", {})
    ok6 = (res6["verdict"] != "UNDERSTOOD"
           and not rec6.get("mint")
           and any("no scream" in b for b in rec6.get("bypassed", []))
           and not any(c["op"] == "powerprod" for c in m6.composites))
    check("HB6 the null — scrambled y: no dig, no mint, receipt "
          "kept", ok6,
          f"verdict {res6['verdict']}; bypassed {rec6.get('bypassed')}")

    # HB7 — persistence: the grown word survives save/load
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "m.isaac")
        mind.save(p)
        m7 = Isaac.load(p)
        q2 = rng.uniform(0.2, 50, 150)
        r2_ = rng.uniform(1.0, 15, 150)
        X7 = np.column_stack([q2, r2_, rng.normal(0, 1, 150)])
        res7 = m7.discover(X7, 123.4 * q2 / r2_ ** 2,
                           name="post-reload-world")
        ok7 = (any(c["op"] == "powerprod" for c in m7.composites)
               and res7["verdict"] == "UNDERSTOOD"
               and rec["mint"] in res7.get("equation", ""))
        check("HB7 persistence — the grown word survives save/load "
              "and still carries", ok7,
              f"eq {res7.get('equation', '')[:44]}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
