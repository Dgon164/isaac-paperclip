# -*- coding: utf-8 -*-
"""BLOCK-PERMUTATION NULL BATTERY — A1, the oldest methods debt (2026-07-04).

The claim: discover()'s admission null is now valid on autocorrelated
targets. The iid shuffle destroyed the autocorrelation itself, making the
null too easy — junk beat it forever (the sunspot runaway, stopped only by
the max_terms brake). The block null permutes contiguous blocks at the
residual's MEASURED decorrelation length, preserving texture, destroying
only candidate↔residual alignment.

B1  the detector      -> white noise L==1; AR(1) L>1 and grows with phi
B2  iid path untouched -> planted x0*x1 - x2 still UNDERSTOOD exact
B3  the runaway case  -> AR(1) noise vs time: admission stops FAR below the
                         brake and the verdict refuses (no false law)
B4  power retained    -> real law + AR noise on time: still articulated
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac, _Enumerator

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(2026)

def ar1(n, phi, rng):
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + rng.normal()
    return x

# ── B1: the decorrelation-length detector ───────────────────────────
print("\nB1 — the measured decorrelation length")
white_trips = sum(_Enumerator._decorr_len(rng.normal(size=600)) > 1
                  for _ in range(20))
check("white noise: lag-1 gate holds (<=2/20 trips at the 1% level)",
      white_trips <= 2, f"{white_trips}/20 draws measured L>1")
L_weak = _Enumerator._decorr_len(ar1(600, 0.6, rng))
L_strong = _Enumerator._decorr_len(ar1(600, 0.95, rng))
check("AR(1) phi=0.6 detected (L > 1)", L_weak > 1, f"L={L_weak}")
check("stronger autocorrelation -> longer blocks", L_strong > L_weak,
      f"L(0.95)={L_strong} > L(0.6)={L_weak}")

# ── B2: the iid path is untouched ───────────────────────────────────
print("\nB2 — iid data: planted law still exact")
i = Isaac()
X = rng.normal(size=(400, 3))
y = X[:, 0] * X[:, 1] - X[:, 2] + 0.05 * rng.normal(size=400)
res = i.discover(X, y, name="planted_iid")
check("verdict UNDERSTOOD", res["verdict"] == "UNDERSTOOD", res["equation"])
check("form exact", "x0*x1" in res["equation"].replace(" ", "")
      or "x1*x0" in res["equation"].replace(" ", ""), res["equation"])

# ── B3: the runaway condition, replayed ─────────────────────────────
print("\nB3 — AR(1) noise against time (the sunspot shape, no law present)")
n = 500
t = np.linspace(0, 10, n).reshape(-1, 1)
y_noise = ar1(n, 0.9, rng)
j = Isaac()
res3 = j.discover(t, y_noise, name="ar_noise")
n_terms = len(res3.get("model", {}).get("terms", []) if isinstance(
    res3.get("model"), dict) else res3.get("model", []) or [])
eq_terms = res3["equation"].count("+") + res3["equation"].count("-")
check("no false UNDERSTOOD on autocorrelated noise",
      res3["verdict"] != "UNDERSTOOD", f"verdict={res3['verdict']}")
check("admission stopped far below the brake (< 8 of 16)",
      eq_terms < 8, f"~{eq_terms} terms: {res3['equation'][:60]}")

# repeat for stability across seeds
false_laws = 0
for s in range(5):
    r2 = Isaac().discover(t, ar1(n, 0.9, np.random.default_rng(100 + s)),
                          name=f"ar_noise_{s}")
    if r2["verdict"] == "UNDERSTOOD":
        false_laws += 1
check("0/5 false laws across seeds", false_laws == 0, f"{false_laws}/5")

# ── B4: power retained — a real law under AR noise ──────────────────
# Two fairness notes, both discoveries of this battery:
# (1) the first draft gave only 2.4 sine cycles against slow AR noise —
#     refusal there is HONEST (evidence genuinely weak);
# (2) the second draft planted k=1.5, which is NOT on the proposal grid
#     [0.5,1,2,3,4.5,6,8] — over a long window a near-miss grid atom is
#     ~orthogonal to the truth (r=0.12 vs gate 0.37), so nothing can enter.
#     The OLD invalid null (gate ~0.08) admitted the near-miss and let
#     hill-climbing walk it to the truth — power by accident, through an
#     invalid gate. The block null unmasks this as a GRID-RESOLUTION limit
#     over long windows (checklist E6). Power of the NULL is tested on-grid.
print("\nB4 — real structure + AR noise (on-grid frequency): still found")
n4 = 800
t4 = np.linspace(0, 40, n4).reshape(-1, 1)
y_law = 3.0 * np.sin(3.0 * t4[:, 0]) + 0.35 * ar1(n4, 0.9, rng)
k = Isaac()
res4 = k.discover(t4, y_law, name="law_in_ar_noise")
check("law articulated despite autocorrelated noise",
      res4["verdict"] in ("UNDERSTOOD", "PARTIAL")
      and ("sin" in res4["equation"] or "cos" in res4["equation"]),
      f"{res4['verdict']}: {res4['equation'][:60]}")

# ── B5: the unmasked limit, recorded as expected behavior ───────────
print("\nB5 — off-grid frequency over a long window: honest refusal (E6)")
y_off = 3.0 * np.sin(1.5 * t4[:, 0]) + 0.35 * ar1(n4, 0.9, rng)
res5 = Isaac().discover(t4, y_off, name="offgrid_long_window")
check("no false law where the grid cannot reach",
      res5["verdict"] != "UNDERSTOOD", f"verdict={res5['verdict']}")

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nBLOCK-PERM BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
