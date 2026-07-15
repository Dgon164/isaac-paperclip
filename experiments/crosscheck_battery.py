"""crosscheck_battery.py — ECC FOR DATA (owner design 2026-07-15).
Battery written FIRST, per discipline; the organ is built to pass it.

The owner's design, verbatim: "you have the inputs and the outputs.
5+5=9. you dont know if 9 was wrong, or if one of the 5s was supposed
to be a 4, but you know something here is incorrect. and even if he
cant resolve it, he can mark it as false and return to it maybe. if
you have a data table with 40,000 inputs and they dont add up at the
end, then someone somewhere did something wrong."

The laws under test:
  - a failing check marks the TUPLE false, never the output alone;
  - candidate repairs are enumerated as mis-entry doors (the typo
    concept), NEVER silently applied;
  - overlapping checks localize like parity bits (the Hamming move):
    a UNIQUE single-cell repair that balances every failing check it
    touches and breaks none that pass = CORRECTED-CANDIDATE;
  - no unique repair = FALSE-SOMEWHERE, kept open, RETURNABLE — new
    checks later can resolve it (supersession);
  - 40,000 values that don't add up = certainty an error EXISTS even
    when nothing can say where (batch parity below per-item
    detectability);
  - floors gate tolerance: noise-level imbalance is not a finding.

Checks E1-E8. Run: PYTHONHASHSEED=0 python crosscheck_battery.py
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

rng = np.random.default_rng(11)
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" +
          (f"   {detail}" if detail else ""))


def main():
    print("=" * 70)
    print("CROSS-CHECK BATTERY — ECC for data")
    print("=" * 70)

    # ── E1: the owner's receipt — 5+5=9 marks the TUPLE, blames no one ──
    m = mod.Isaac()
    r = m.cross_check(dict(a=5, b=5, c=9),
                      [dict(name="sum", cells=["a", "b"], total="c")])
    comp = r["components"][0]
    cand_cells = {cd["cell"] for cd in comp["candidates"]}
    ok = (r["consistent"] is False
          and comp["verdict"] == "FALSE-SOMEWHERE"
          and cand_cells == {"a", "b", "c"}
          and all(cd["repaired"] in (4.0, 10.0)
                  for cd in comp["candidates"]))
    check("E1 5+5=9: tuple marked false; 3 repair doors (a->4, b->4, "
          "c->10); nothing blamed", ok,
          f"verdict {comp['verdict']}, candidates "
          f"{sorted((cd['cell'], cd['repaired']) for cd in comp['candidates'])}")

    # ── E2: THE CONTROL — clean books, zero findings ──
    r = m.cross_check(dict(a=5, b=5, c=10),
                      [dict(name="sum", cells=["a", "b"], total="c")])
    check("E2 clean control: consistent, no components",
          r["consistent"] is True and not r["components"])

    # ── E3: the ECC move — row+column totals localize ONE bad cell ──
    n = 6
    grid = rng.integers(1, 50, (n, n)).astype(float)
    vals, checks = {}, []
    for i in range(n):
        for j in range(n):
            vals[f"m{i}{j}"] = grid[i, j]
    for i in range(n):
        vals[f"r{i}"] = float(grid[i].sum())
        checks.append(dict(name=f"row{i}",
                           cells=[f"m{i}{j}" for j in range(n)],
                           total=f"r{i}"))
    for j in range(n):
        vals[f"c{j}"] = float(grid[:, j].sum())
        checks.append(dict(name=f"col{j}",
                           cells=[f"m{i}{j}" for i in range(n)],
                           total=f"c{j}"))
    r = m.cross_check(vals, checks)                    # clean first
    check("E3a clean grid control: consistent",
          r["consistent"] is True and not r["components"])
    vals2 = dict(vals)
    vals2["m23"] += 7.0                                # ONE bad cell
    r = m.cross_check(vals2, checks)
    comp = r["components"][0] if r["components"] else None
    ok = (comp is not None and len(r["components"]) == 1
          and comp["verdict"] == "CORRECTED-CANDIDATE"
          and len(comp["candidates"]) == 1
          and comp["candidates"][0]["cell"] == "m23"
          and abs(comp["candidates"][0]["repaired"]
                  - (vals["m23"])) < 1e-9)
    check("E3b one bad cell: failing row x failing col intersect -> "
          "unique repair at m23, exact value", ok,
          f"candidates {[(cd['cell'], cd['repaired']) for cd in comp['candidates']] if comp else '-'}")

    # ── E4: two errors in one row — beyond single-error correction:
    #        honest FALSE-SOMEWHERE, kept open, never a forced guess ──
    vals3 = dict(vals)
    vals3["m23"] += 7.0
    vals3["m24"] -= 3.0
    r = m.cross_check(vals3, checks)
    ok = (r["consistent"] is False
          and all(c["verdict"] == "FALSE-SOMEWHERE"
                  for c in r["components"])
          and all(len(c["candidates"]) != 1 for c in r["components"]))
    check("E4 two errors, one row: no unique repair -> FALSE-SOMEWHERE "
          "(detects, refuses to guess)", ok,
          f"{[(c['verdict'], len(c['candidates'])) for c in r['components']]}")

    # ── E5: the 40,000-row books — error EXISTS, location unknowable ──
    big = rng.integers(1, 100, 40000).astype(float)
    vals4 = {f"x{i}": v for i, v in enumerate(big)}
    vals4["G"] = float(big.sum())
    vals4["x31337"] += 250.0                           # someone, somewhere
    r = m.cross_check(vals4,
                      [dict(name="grand",
                            cells=[f"x{i}" for i in range(40000)],
                            total="G")])
    comp = r["components"][0]
    ok = (comp["verdict"] == "FALSE-SOMEWHERE"
          and comp.get("candidates_not_enumerated", 0) > 30000
          and "someone somewhere" in comp["why"])
    check("E5 40,000 inputs don't add up: error certified to exist, "
          "candidates counted not enumerated", ok,
          f"n_cells {comp['n_cells']}, unenumerated "
          f"{comp.get('candidates_not_enumerated')}")

    # ── E6: floors gate the imbalance — noise is not a finding ──
    xs = rng.normal(10, 2, 5)
    noisy = {f"v{i}": float(xs[i] + rng.normal(0, 0.05))
             for i in range(5)}
    noisy["T"] = float(xs.sum())
    ck = [dict(name="t", cells=[f"v{i}" for i in range(5)], total="T")]
    r = m.cross_check(noisy, ck, floor=0.05)
    ok1 = r["consistent"] is True
    noisy2 = dict(noisy)
    noisy2["v2"] += 1.0
    r = m.cross_check(noisy2, ck, floor=0.05)
    check("E6 floor-aware: noise-level imbalance passes; a real 1.0 "
          "slip fails", ok1 and r["consistent"] is False,
          f"clean {ok1}, slipped {not r['consistent']}")

    # ── E7: RETURN TO IT — the owner's own example, resolved by a
    #        second witness (5+5=9 + a+2=6 -> a was the 4) ──
    m2 = mod.Isaac()
    r1 = m2.cross_check(dict(a=5, b=5, c=9),
                        [dict(name="sum", cells=["a", "b"], total="c")],
                        name="books")
    open1 = m2.net.get_meta("inconsistency:books", "active")
    r2 = m2.cross_check(dict(a=5, b=5, c=9),
                        [dict(name="sum", cells=["a", "b"], total="c"),
                         dict(name="witness", cells=["a"], const=2,
                              total=6)],
                        name="books")
    comp = r2["components"][0]
    chain = m2.net.get_meta("inconsistency:books", "superseded") or []
    ok = (r1["components"][0]["verdict"] == "FALSE-SOMEWHERE"
          and open1 and len(open1) == 1
          and comp["verdict"] == "CORRECTED-CANDIDATE"
          and comp["candidates"][0]["cell"] == "a"
          and comp["candidates"][0]["repaired"] == 4.0
          and len(chain) == 1)
    check("E7 marked false, RETURNED TO: second check arrives -> "
          "a=4 localized; old open record superseded, kept", ok,
          f"then: {comp['verdict']} "
          f"{[(cd['cell'], cd['repaired']) for cd in comp['candidates']]}"
          f", chain {len(chain)}")

    # ── E8: a repair may not break the books elsewhere ──
    # b appears in a PASSING check too; repairing b would break it,
    # so the survivor set must exclude b
    r = m.cross_check(dict(a=5, b=5, c=9, d=7),
                      [dict(name="bad", cells=["a", "b"], total="c"),
                       dict(name="good", cells=["b"], const=2,
                            total="d")])
    comp = r["components"][0]
    cand_cells = {cd["cell"] for cd in comp["candidates"]}
    check("E8 passing checks veto repairs: b protected by its good "
          "check; candidates = {a, c} only",
          cand_cells == {"a", "c"},
          f"candidates {sorted(cand_cells)}")

    n_ok = sum(CHECKS)
    print("=" * 70)
    print(f"CROSS-CHECK BATTERY: {n_ok}/{len(CHECKS)}")
    print("=" * 70)
    sys.exit(0 if n_ok == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
