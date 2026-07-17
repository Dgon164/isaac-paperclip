"""reproducibility_check.py — the owner's claim, measured (2026-07-17:
"the net isnt so important, its the capability. the net should be
produced roughly the same time every time"). Two fresh minds run the
IDENTICAL experience script — teachings, discoveries, told laws —
and the nets are compared at three depths:

  C1 BYTES: pickle-identical (the strongest possible statement);
  C2 STRUCTURE: same fact keys, same law set, same node count;
  C3 BEHAVIOR: same answers, same law predictions on a fixed grid.

If bytes differ but structure+behavior match, the claim holds at the
level that matters and the byte-level divergence is NAMED. Run:
PYTHONHASHSEED=0 python reproducibility_check.py
"""
import os
import pickle
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                # noqa: E402

PASS, FAIL = 0, 0


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


def experience_script(m):
    """One fixed life, replayed identically: facts, a fiction fact,
    two discoveries, one told law."""
    rng = np.random.default_rng(41)
    m.teach("water", "state", "liquid")
    m.teach("sky", "color", "blue")
    m.teach("broom", "can", "fly", container="hp")
    x = rng.uniform(0.5, 8, 240).reshape(-1, 1)
    m.discover(x, 2.0 * x[:, 0] + rng.normal(0, 0.02, 240),
               name="double")
    x2 = rng.uniform(0.5, 6, 200).reshape(-1, 1)
    m.discover(x2, 3.0 * x2[:, 0] ** 2 + rng.normal(0, 0.05, 200),
               name="square")
    m.tell_law("kepler", "+1.00*x0^1.5 +0.00", d=1)
    return m


def main():
    print("=" * 70)
    print("REPRODUCIBILITY — same experience script, two fresh minds")
    print("=" * 70)
    a = experience_script(mod.Isaac())
    b = experience_script(mod.Isaac())

    pa, pb = pickle.dumps(a), pickle.dumps(b)
    check("C1 bytes: pickle-identical", pa == pb,
          f"{len(pa)} vs {len(pb)} bytes")

    fa = sorted(map(repr, a.fact_index.keys()))
    fb = sorted(map(repr, b.fact_index.keys()))
    la = sorted(str(n) for n in a.net.meta
                if str(n).startswith("law:"))
    lb = sorted(str(n) for n in b.net.meta
                if str(n).startswith("law:"))
    check("C2 structure: same facts, same laws, same node count",
          fa == fb and la == lb
          and len(a.net.meta) == len(b.net.meta),
          f"{len(fa)} facts, {len(la)} laws, "
          f"{len(a.net.meta)}/{len(b.net.meta)} nodes")

    xg = np.linspace(0.6, 7.5, 60).reshape(-1, 1)
    same_pred = all(
        np.allclose(a.apply_law(n, xg), b.apply_law(n, xg),
                    equal_nan=True)
        for n in ("double", "square", "kepler"))
    same_ans = (a.ask("water", "state")["answers"]
                == b.ask("water", "state")["answers"]
                and a.ask("broom", "can", container="hp")["answers"]
                == b.ask("broom", "can", container="hp")["answers"])
    check("C3 behavior: identical answers and law predictions",
          same_pred and same_ans)

    print()
    print(f"REPRODUCIBILITY: {PASS}/{PASS + FAIL} checks passed"
          + ("" if PASS == PASS + FAIL else
             " — divergence NAMED above, not hidden"))
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
