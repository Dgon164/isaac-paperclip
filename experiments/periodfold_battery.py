# -*- coding: utf-8 -*-
"""PHASE-FOLD PERIOD PROPOSAL BATTERY — E7 cured the owner's way (2026-07-04).

Owner: "if you suspect a period do the projection thing. you don't need the
whole thing, you just need a few samples and to map it."

Folding y onto candidate periods of an input maps scattered samples onto one
cycle; coherence (variance explained by phase bins) proposes the period past
a selection-corrected block-perm null. Proposal widens the grid (EXPANSION);
admission still faces its own null (COMPRESSION unchanged).

P1  E7 case cured    -> off-grid sin(1.5t) over 40u + AR noise: articulated
P2  few samples      -> 150 SCATTERED timestamps, same law: articulated
P3  noise refusal    -> AR(0.9) alone: no false law, 0/5 seeds
P4  white refusal    -> white noise proposes nothing
P5  iid untouched    -> planted x0*x1 - x2 still exact
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac, _Enumerator

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(41)

def ar1(n, phi, rng):
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + rng.normal()
    return x

# ── P1: the E7 case, cured ──────────────────────────────────────────
print("\nP1 — off-grid frequency over a long window (yesterday's honest NO RULE)")
n = 800
t = np.linspace(0, 40, n).reshape(-1, 1)
y = 3.0 * np.sin(1.5 * t[:, 0]) + 0.35 * ar1(n, 0.9, rng)
res = Isaac().discover(t, y, name="offgrid_cured")
eq = res["equation"].replace(" ", "")
found_k = None
import re
m = re.search(r"(?:sin|cos)\((\d+\.?\d*)\*x0\)", eq)
if m:
    found_k = float(m.group(1))
check("articulated (was NO RULE before folding)",
      res["verdict"] in ("UNDERSTOOD", "PARTIAL"), f"{res['verdict']}: {eq[:50]}")
check("frequency recovered near 1.5",
      found_k is not None and abs(found_k - 1.5) < 0.05, f"k={found_k}")

# ── P2: a few scattered samples suffice ─────────────────────────────
print("\nP2 — 150 scattered timestamps ('you just need a few samples and to map it')")
n2 = 150
t2 = np.sort(rng.uniform(0, 40, n2)).reshape(-1, 1)
y2 = 3.0 * np.sin(1.5 * t2[:, 0]) + 0.3 * rng.normal(size=n2)
res2 = Isaac().discover(t2, y2, name="sparse_fold")
check("law found from scattered samples",
      res2["verdict"] in ("UNDERSTOOD", "PARTIAL")
      and ("sin" in res2["equation"] or "cos" in res2["equation"]),
      f"{res2['verdict']}: {res2['equation'][:50]}")

# ── P3: AR noise alone still refused ────────────────────────────────
print("\nP3 — AR(0.9) noise alone: folding must not create false laws")
false_laws = 0
for s in range(5):
    r3 = Isaac().discover(t, ar1(n, 0.9, np.random.default_rng(300 + s)),
                          name=f"ar_{s}")
    if r3["verdict"] == "UNDERSTOOD":
        false_laws += 1
check("0/5 false laws on autocorrelated noise", false_laws == 0, f"{false_laws}/5")

# ── P4: white noise proposes nothing ────────────────────────────────
print("\nP4 — proposal gate refuses white noise")
trips = 0
for s in range(10):
    e = _Enumerator()
    w = np.random.default_rng(500 + s).normal(size=400)
    trips += len(e._propose_periods(t[:400], w))
check("white noise: ~0 proposals across 10 draws (<=1 at the 1% gate)",
      trips <= 1, f"{trips} proposals")

# ── P5: iid multi-feature law untouched ─────────────────────────────
print("\nP5 — planted iid law still exact")
X = rng.normal(size=(400, 3))
y5 = X[:, 0] * X[:, 1] - X[:, 2] + 0.05 * rng.normal(size=400)
res5 = Isaac().discover(X, y5, name="planted_iid")
check("UNDERSTOOD, form exact",
      res5["verdict"] == "UNDERSTOOD"
      and ("x0*x1" in res5["equation"].replace(" ", "")
           or "x1*x0" in res5["equation"].replace(" ", "")),
      res5["equation"])

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nPERIOD-FOLD BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
