# -*- coding: utf-8 -*-
"""COMPOUND BATTERY — C2: compound doors + the ceiling trigger, IN THE
ENGINE (2026-07-04). Audit 2.11's missing wiring: when flat doors leave
held-out confusions, conjunction doors are mined per confused pair
(label-permutation null, selection-corrected), kept only if held-out
accuracy improves; classify_features augments identically.

X1  XOR rescue      -> flat doors ~chance; compounds lift far above
X2  trigger honest  -> report says fired + kept, with both held numbers
X3  refusal         -> random labels: no compound survives / not kept
X4  trigger silent  -> linearly separable: no mining, flat behavior kept
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(5)

# ── X1/X2: XOR — the case flat boxes/doors cannot bind ─────────────
print("\nX1 — XOR rescue")
n = 4000
X = rng.normal(size=(n, 4))
y = ((X[:, 0] > 0) ^ (X[:, 1] > 0)).astype(int)
split = 3000
i = Isaac()
i.crystallize_features(X[:split], y[:split], compounds="off")
acc_flat = float((i.classify_features(X[split:]) == y[split:]).mean())
j = Isaac()
j.crystallize_features(X[:split], y[:split], compounds="auto")
acc_comp = float((j.classify_features(X[split:]) == y[split:]).mean())
rep = j.net.get_meta("crystal", "calib").get("compound_report") or {}
check("flat doors near chance on XOR", acc_flat < 0.62, f"{acc_flat:.3f}")
check("compound doors rescue XOR", acc_comp > 0.80,
      f"{acc_comp:.3f} (flat {acc_flat:.3f})")

print("\nX2 — the trigger reports honestly")
check("trigger fired and compounds kept",
      rep.get("trigger") == "fired" and rep.get("kept") is True,
      f"admitted={rep.get('admitted')} held {rep.get('held_flat')}"
      f"->{rep.get('held_aug')} why={rep.get('why', '')}")

# ── X3: refusal on random labels ────────────────────────────────────
print("\nX3 — random labels: compounds must not be kept")
kept = 0
for s in range(3):
    r = np.random.default_rng(70 + s)
    Xr = r.normal(size=(1200, 4))
    yr = r.integers(0, 2, 1200)
    k = Isaac()
    k.crystallize_features(Xr, yr, compounds="auto")
    repr_ = k.net.get_meta("crystal", "calib").get("compound_report") or {}
    kept += bool(repr_.get("kept"))
check("0/3 random-label runs kept compounds", kept == 0, f"{kept}/3")

# ── X4: linearly separable — the trigger stays silent ───────────────
print("\nX4 — separable data: no ceiling, no mining")
Xs = rng.normal(size=(1500, 3))
ys = (Xs[:, 0] > 0).astype(int)
m = Isaac()
m.crystallize_features(Xs, ys, compounds="auto")
reps = m.net.get_meta("crystal", "calib").get("compound_report") or {}
acc_sep = float((m.classify_features(Xs) == ys).mean())
check("trigger silent on separable data", reps.get("trigger") == "silent",
      reps.get("why", ""))
check("flat behavior intact", acc_sep > 0.95, f"{acc_sep:.3f}")

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nCOMPOUND BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
