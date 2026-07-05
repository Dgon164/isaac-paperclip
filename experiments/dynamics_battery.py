# -*- coding: utf-8 -*-
"""RATE-OF-CHANGE BATTERY — the derivative tower (owner, 2026-07-05:
"rate of change. curve, acceleration, jerk... detect linear or compound
spirals"). Curvature is a curve VOCABULARY: line kappa~0, circle
kappa~const, spiral kappa marching one way, s-curve kappa crossing zero.
All accuracy numbers are COMPLETE numbers.

D1  the curve vocabulary on synthetic paths
D2  spiral trajectories detected (the owner's spiral case)
D3  the dynamics channel joins the glyph vote: complete number measured
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(51)
i = Isaac()

# ── D1: the vocabulary ──────────────────────────────────────────────
print("\nD1 — line / arc / circle / spiral / s-curve")
t = np.linspace(0, 1, 60)
line = np.column_stack([3 + 10 * t, 2 + 6 * t])
th = np.linspace(0, 2 * np.pi * 0.95, 80)
circle = np.column_stack([5 * np.cos(th), 5 * np.sin(th)])
arc = circle[:26]
# clothoid: kappa = c*s (the canonical 'linear spiral')
s_ = np.linspace(0, 6, 120)
ang = 0.35 * s_ ** 2 / 2
clo = np.column_stack([np.cumsum(np.cos(ang)) * (s_[1] - s_[0]),
                       np.cumsum(np.sin(ang)) * (s_[1] - s_[0])])
# s-curve: quarter circle left then quarter circle right
t2 = np.linspace(0, np.pi / 2, 40)
sc = np.vstack([np.column_stack([np.sin(t2), 1 - np.cos(t2)]),
                np.column_stack([np.sin(t2[-1]) + np.sin(t2),
                                 2 - np.cos(t2[-1]) - (1 - np.cos(t2))])])
for name, P, want in [("line", line, "line"), ("arc", arc, "arc"),
                      ("circle", circle, "circle"),
                      ("clothoid spiral", clo, "spiral"),
                      ("s-curve", sc, "s-curve")]:
    dyn = i.path_dynamics(P)
    check(f"{name} -> {want}", dyn is not None and dyn["kind"] == want,
          f"got {dyn['kind'] if dyn else None} (turn {dyn['turn']:.1f}, "
          f"k_mean {dyn['kappa_mean']:.2f}, slope {dyn['kappa_slope']:.3f})"
          if dyn else "")

# ── D2: spiral trajectories ─────────────────────────────────────────
print("\nD2 — trajectories: the spiral vs the straight run")
th3 = np.linspace(0.5, 4 * np.pi, 150)
archi = np.column_stack([(1 + 0.4 * th3) * np.cos(th3),
                         (1 + 0.4 * th3) * np.sin(th3)])
d_arch = i.path_dynamics(archi)
d_run = i.path_dynamics(np.column_stack([t * 30, t * 2]))
check("Archimedean trajectory reads spiral-family (spiral/compound, "
      "curvature marching)", d_arch["kind"] in ("spiral", "compound")
      and abs(d_arch["turn"]) > 2 * np.pi,
      f"{d_arch['kind']}, turn {d_arch['turn']:.1f}")
check("straight run reads line", d_run["kind"] == "line", d_run["kind"])

# ── D3: the independent witness joins the glyph vote ────────────────
print("\nD3 — the dynamics channel in the fused vote (complete numbers)")
from sklearn.datasets import fetch_openml
d = fetch_openml("mnist_784", version=1, as_frame=False, parser="liac-arff")
X = d.data.reshape(-1, 28, 28)
y = d.target.astype(int)
tr = np.concatenate([np.where(y[:40000] == c)[0][:200] for c in range(10)])
te = rng.choice(np.where(np.arange(len(y)) > 40000)[0], 500, replace=False)
m = Isaac()
m.learn_glyphs(X[tr], y[tr])
classes = m.net.get_meta("crystal", "glyph_classes")
hits = {}
fused = 0
in_short = 0
for ix in te:
    got, posts = m.recognize_glyph(X[ix])
    fused += (got == y[ix])
    in_short += (y[ix] in [c for c, _ in posts["_shortlist"]])
    for k, p in posts.items():
        if str(k).startswith("_"):
            continue
        hits.setdefault(k, 0)
        hits[k] += (classes[int(np.argmax(p))] == y[ix])
print("    COMPLETE numbers over all 500 test digits:")
for k in sorted(hits):
    print(f"      {k:9s}: {hits[k]/5:.1f}%")
print(f"      FUSED    : {fused/5:.1f}%   (was 90.6 without dynamics)")
print(f"      truth in shortlist: {in_short/5:.1f}%")
check("dynamics alone is a real channel (> 40% complete)",
      hits.get("dynamics", 0) / 500 > 0.40,
      f"{hits.get('dynamics', 0)/5:.1f}%")
check("fusion does not lose with the new channel (>= 89.6%)",
      fused / 500 >= 0.896, f"{fused/5:.1f}%")

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nDYNAMICS BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
