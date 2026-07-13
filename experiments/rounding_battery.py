"""rounding_battery.py — taught rounding (owner, 2026-07-12: "i think
we just need to teach it rounding actually. if its 3.0018463 then its
probably tested to 3. if its 1.764964 then it may be 1.75 etc.")

A measured constant's roundings are hypotheses tested OUTRIGHT,
coarsest ruler mark ({1, 1/2, 1/4} x powers of ten) first; the
simplest that does not lose is what the law says. Two failure modes
are gated: INVENTED SIMPLICITY (rounding a constant that is truly
irrational — pi must keep its digits) and LOST SIMPLICITY (printing
1.5688 garbage when the truth is 1.5).
"""
import os
import re
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


def said_ks(eq):
    """Every inside-parameter the equation says."""
    return [float(m) for m in re.findall(r"(?:sin|cos|exp)\((-?[\d.]+)\*",
                                         eq)]


def world(k, n=400, noise=0.05, seed=5):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 40, n)
    y = 2.0 * np.sin(k * x) + rng.normal(0, noise, n)
    return x.reshape(-1, 1), y


def main():
    # ── 1. the ladder itself: his two examples ────────────────────
    e = mod._Enumerator()
    c1 = e._round_candidates(3.0018463)
    c2 = e._round_candidates(1.764964)
    check("3.0018463's first hypothesis is 3",
          c1 and c1[0] == 3.0, f"ladder: {c1[:4]}")
    check("1.764964's ladder reaches 1.75 before finer marks",
          1.75 in c2 and c2.index(1.75) <= 2, f"ladder: {c2[:4]}")

    # ── 2. LOST SIMPLICITY cured: k=1.5 said exactly ──────────────
    X, y = world(1.5)
    m = mod.Isaac()
    r = m.discover(X, y, name="k15")
    ks = said_ks(r["equation"])
    check("planted sin(1.5x): the law SAYS 1.5 exactly",
          r["verdict"] == "UNDERSTOOD" and 1.5 in ks,
          f"{r['verdict']} r2={r['r2']:.4f} ks={ks}")

    # ── 3. the quarter mark: k=1.75 said exactly ──────────────────
    X, y = world(1.75, seed=6)
    m2 = mod.Isaac()
    r2_ = m2.discover(X, y, name="k175")
    ks2 = said_ks(r2_["equation"])
    check("planted sin(1.75x): the law SAYS 1.75 (a ruler mark)",
          r2_["verdict"] == "UNDERSTOOD" and 1.75 in ks2,
          f"{r2_['verdict']} r2={r2_['r2']:.4f} ks={ks2}")

    # ── 4. INVENTED SIMPLICITY refused: pi keeps its digits ───────
    X, y = world(np.pi, n=600, seed=7)
    m3 = mod.Isaac()
    r3 = m3.discover(X, y, name="kpi")
    ks3 = said_ks(r3["equation"])
    near_pi = [k for k in ks3 if abs(k - np.pi) / np.pi < 0.002]
    coarse = [k for k in ks3 if k in (3.0, 3.1, 3.25, 3.5)]
    check("planted sin(pi*x): NOT rounded to a coarse mark",
          r3["verdict"] == "UNDERSTOOD" and near_pi and not coarse,
          f"{r3['verdict']} r2={r3['r2']:.4f} ks={ks3}")

    # ── 5. decay constants too: exp(-0.4x) said 0.4 ───────────────
    rng = np.random.default_rng(8)
    x = np.linspace(0, 8, 500)
    y5 = 3.0 * np.exp(-0.4 * x) + rng.normal(0, 0.02, 500)
    m4 = mod.Isaac()
    r4 = m4.discover(x.reshape(-1, 1), y5, name="decay")
    ks4 = said_ks(r4["equation"])
    check("planted exp(-0.4x): the law SAYS 0.4",
          r4["verdict"] == "UNDERSTOOD" and any(abs(k) == 0.4
                                                for k in ks4),
          f"{r4['verdict']} r2={r4['r2']:.4f} ks={ks4}")

    # ── 6. rounding never fakes a law: noise stays NO RULE ────────
    rng = np.random.default_rng(9)
    m5 = mod.Isaac()
    r5 = m5.discover(rng.uniform(-2, 2, (400, 1)),
                     rng.normal(0, 1, 400), name="noise")
    check("pure noise: still NO RULE (rounding adds no claims)",
          r5["verdict"] == "NO RULE", r5["verdict"])

    print()
    print(f"ROUNDING BATTERY: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
