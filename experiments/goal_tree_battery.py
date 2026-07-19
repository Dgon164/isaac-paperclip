"""goal_tree_battery.py — PROMOTION GATE for THE GOAL TREE (the
scaling campaign's rung 2; owner, 2026-07-19: "he needs to
understand end goal decomposition and stuff").

The engine owns the CHAINING MECHANICS only — every tree step is a
law/fact from HIS net (told in English through the telling road in
this very battery). Pins:

  G1  FORWARD: v from {i,r} through a told ohm — computed exact.
  G2  INVERSION: i from {v,r} — solve_law promoted INTO the
      engine (the audit noted the solver lived exam-side only).
  G3  THE CHAIN: a=b*c and b=d*e; a from {c,d,e} — two laws
      chained, computed exact.
  G4  CHAIN + INVERSION: r from {p,i} via p=v*i then v=i*r —
      two inversions deep, exact.
  G5  THE DARK LEAF, NAMED: a quantity no law reaches says so —
      the refusal tells the owner exactly what to teach next.
  G6  THE CYCLE, REFUSED: i from {p} alone (p=v*i, v=i*r) loops
      i->v->i — refused with the path receipt, no infinite walk.
  G7  THE DUEL CASE: two laws produce f — alternatives COUNTED,
      never hidden.
  G8  MULTI-TERM REFUSAL: a 3-term line cannot be inverted in v1
      — refused BY NAME; forward apply still stands.
  G9  FRACTIONAL POWER: kepler a from {t} — the 1/1.5 root exact.
  G10 EVEN-POWER RECEIPT: the positive root SAYS it was taken.
  G11 STRUCTURE-ONLY ASK: names without values -> tree stands,
      value honestly None.
  G12 THE LEDGER: every decomposition records its finding.

Run: cd experiments && PYTHONHASHSEED=0 python goal_tree_battery.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
import isaac as isaac_mod                          # noqa: E402
from isaac_store.telling import tell_english       # noqa: E402

Isaac = isaac_mod.Isaac


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(bool(ok))
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    m = Isaac()
    tell_english(m, "ohms law is v=ir", who="owner")
    tell_english(m, "power law is p=vi", who="owner")

    # G1 forward
    g1 = m.decompose("v", known=dict(i=2.0, r=3.0))
    check("G1 forward — v from {i,r}",
          g1["value"] == 6.0 and not g1["dark"],
          f"v = {g1['value']}")

    # G2 inversion (the solver, engine-side at last)
    g2 = m.decompose("i", known=dict(v=6.0, r=3.0))
    check("G2 inversion — i from {v,r}", g2["value"] == 2.0,
          f"i = {g2['value']}")

    # G3 the chain (fresh mind, clean letters)
    m3 = Isaac()
    tell_english(m3, "first law is a=bc", who="owner")
    tell_english(m3, "second law is b=de", who="owner")
    g3 = m3.decompose("a", known=dict(c=2.0, d=3.0, e=4.0))
    check("G3 chain — a from {c,d,e} through two laws",
          g3["value"] == 24.0 and not g3["dark"],
          f"a = {g3['value']} (hand 24.0)")

    # G4 chain + two inversions: r from {p,i} (p=v*i -> v; v=i*r -> r)
    g4 = m.decompose("r", known=dict(p=12.0, i=2.0))
    check("G4 chain + inversion — r from {p,i}",
          g4["value"] is not None and abs(g4["value"] - 3.0) < 1e-9,
          f"r = {g4['value']} (hand p/i^2 = 3.0)")

    # G5 the dark leaf, named
    g5 = m.decompose("z", known=dict(v=1.0))
    check("G5 dark leaf — unknown quantity says what is missing",
          g5["dark"] == ["z"] and g5["tree"]["status"] == "dark"
          and "teach or discover" in g5["tree"]["why"],
          f"dark {g5['dark']}")

    # G6 the cycle, refused with the path receipt
    g6 = m.decompose("i", known=dict(p=12.0))
    check("G6 cycle — i from {p} alone refuses the loop, no hang",
          g6["value"] is None
          and any("cycle refused" in r for r in g6["receipts"]),
          (next((r for r in g6["receipts"] if "cycle" in r),
                "NO RECEIPT"))[:56])

    # G7 the duel case: two roads to f — alternatives counted
    m7 = Isaac()
    tell_english(m7, "hookes law is f=kx", who="owner")
    tell_english(m7, "newtons second is f=ma", who="owner")
    g7 = m7.decompose("f", known=dict(k=2.0, x=3.0, m=4.0, a=5.0))
    check("G7 duel — two complete roads, alternatives counted",
          g7["value"] in (6.0, 20.0)
          and g7["tree"].get("alternatives") == 1,
          f"f = {g7['value']}, alternatives "
          f"{g7['tree'].get('alternatives')}")

    # G8 multi-term inversion refused BY NAME; forward stands
    m8 = Isaac()
    tell_english(m8, "some line is y=3x^2-2x+7", who="owner")
    s8 = m8.solve_law("some-line", {"y": 8.0}, 0)
    f8 = m8.apply_law("some-line", np.array([[1.0]]))
    check("G8 multi-term — inversion refused by name, forward "
          "stands (apply_law's road)",
          "refused" in s8 and "multi-term" in s8["refused"]
          and f8 is not None and abs(float(f8[0]) - 8.0) < 1e-9,
          f"{s8.get('refused', '')[:40]}; forward y(1)="
          f"{float(f8[0]) if f8 is not None else None}")

    # G9 fractional power inversion (kepler)
    m9 = Isaac()
    tell_english(m9, "keplers third law is t=a^1.5", who="owner")
    g9 = m9.solve_law("keplers-third-law", {"y": 8.0}, 0)
    check("G9 fractional power — a from t=8 is 4.0 exact",
          abs(g9.get("value", 0) - 4.0) < 1e-9,
          f"a = {g9.get('value')}")

    # G10 even power takes the positive root AND says so
    m10 = Isaac()
    tell_english(m10, "square law is y=x^2", who="owner")
    g10 = m10.solve_law("square-law", {"y": 9.0}, 0)
    check("G10 even power — positive root taken, receipt says so",
          g10.get("value") == 3.0 and "positive root" in
          g10.get("receipt", ""), f"x = {g10.get('value')} "
          f"({g10.get('receipt', '')[:34]})")

    # G11 structure-only ask
    g11 = m.decompose("v", known={"i", "r"})
    check("G11 structure-only — tree stands, value honestly None",
          g11["value"] is None and g11["tree"]["status"] == "via"
          and not g11["dark"], f"tree via {g11['tree'].get('app')}")

    # G12 the ledger
    n_dec = sum(1 for f in m.findings
                if f.get("kind") == "decomposition")
    check("G12 ledger — decompositions recorded",
          n_dec >= 4, f"{n_dec} decomposition findings on m")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} "
          f"failed of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
