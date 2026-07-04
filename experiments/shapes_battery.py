# -*- coding: utf-8 -*-
"""SHAPES BATTERY — full and hollow (owner, 2026-07-04): "circle vs disc
vs sphere vs ball... teach it the basic shapes and it could see the 8 is
two circles maybe one a bit squished."

H1  hollow vs full (2D)   -> a drawn ring reads 'ring'; a filled blob 'disc'
H2  THE 8                 -> two rings, stacked; squish reported; the 0 is
                             one ring; decomposition ASSEMBLES into the net
H3  shell vs ball (3D)    -> point shell reads hollow; solid fill reads full;
                             the middle band refuses
H4  topology road (MNIST) -> hole-count + part signature separates the
                             topology classes (0/8 vs 1/2/3/5/7) far above
                             chance, measured honestly
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(43)

def draw_ring(H=32, cx=16, cy=16, rx=9, ry=9, w=2.0):
    yy, xx = np.mgrid[0:H, 0:H]
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return (np.abs(d - 1.0) * min(rx, ry) < w).astype(float)

def draw_disc(H=32, cx=16, cy=16, r=8):
    yy, xx = np.mgrid[0:H, 0:H]
    return (((xx - cx) ** 2 + (yy - cy) ** 2) < r * r).astype(float)

# ── H1: hollow vs full in 2D ────────────────────────────────────────
print("\nH1 — circle vs disc")
i = Isaac()
ring = i.describe_shape(draw_ring())
disc = i.describe_shape(draw_disc())
check("a drawn circle is a RING (hollow)",
      ring and ring["n_holes"] == 1
      and ring["parts"][0]["kind"] == "ring", ring["english"] if ring else "")
check("a filled circle is a DISC (full)",
      disc and disc["n_holes"] == 0
      and any(p["kind"] == "disc" for p in disc["parts"]),
      disc["english"] if disc else "")

# ── H2: the owner's 8 ───────────────────────────────────────────────
print("\nH2 — the 8 is two circles, one a bit squished")
eight = np.maximum(draw_ring(40, 20, 11, 8, 7, 2.2),
                   draw_ring(40, 20, 29, 9, 6, 2.2))   # lower one squished
r8 = i.describe_shape(eight, teach_label="glyph8")
check("two rings seen", r8 and r8["n_holes"] == 2, r8["english"] if r8 else "")
check("stacked arrangement seen",
      r8 and any(rel in ("above", "below") for _, _, rel in r8["arrangement"]),
      str(r8["arrangement"]) if r8 else "")
sq = sorted(p["squish"] for p in r8["parts"] if p["kind"] == "ring") if r8 else []
check("the squish is measured (one rounder, one squashed)",
      len(sq) == 2 and sq[0] < sq[1] - 0.1, f"squish {sq}")
zero = i.describe_shape(draw_ring(40, 20, 20, 9, 12, 2.5))
check("the 0 is ONE ring", zero and zero["n_holes"] == 1,
      zero["english"] if zero else "")
check("decomposition assembled into the net (a whole with shape parts)",
      "whole:glyph8" in i.net.all_nodes()
      and len(i.dismantle("whole:glyph8")) == 2,
      i.net.get_meta("whole:glyph8", "english"))

# ── H3: sphere vs ball ──────────────────────────────────────────────
print("\nH3 — shell vs solid in 3D")
u = rng.normal(size=(400, 3))
shell = u / np.linalg.norm(u, axis=1, keepdims=True) * 5.0
shell += rng.normal(0, 0.05, shell.shape)
ball = rng.normal(size=(400, 3))
ball = ball / np.linalg.norm(ball, axis=1, keepdims=True) * \
    5.0 * rng.uniform(0, 1, (400, 1)) ** (1 / 3)
ks = Isaac.classify_solid(shell)
kb = Isaac.classify_solid(ball)
check("point shell reads HOLLOW (sphere)", ks["kind"] == "shell",
      f"cv={ks['cv']:.3f}")
check("filled points read FULL (ball)", kb["kind"] == "solid",
      f"cv={kb['cv']:.3f}")

# ── H4: the topology road on MNIST ──────────────────────────────────
print("\nH4 — topology as identity on real digits")
from sklearn.datasets import fetch_openml
d = fetch_openml("mnist_784", version=1, as_frame=False, parser="liac-arff")
X = d.data.reshape(-1, 28, 28)
y = d.target.astype(int)
m = Isaac()

def signature(img):
    r = m.describe_shape(img)
    if r is None:
        return None
    kinds = sorted(p["kind"] for p in r["parts"])
    return (r["n_holes"], tuple(kinds))

# learn: majority class per signature from 40/class
from collections import defaultdict, Counter
sig_votes = defaultdict(Counter)
for c in range(10):
    for im in X[y == c][:40]:
        s = signature(im)
        if s:
            sig_votes[s][c] += 1
sig_class = {s: v.most_common(1)[0][0] for s, v in sig_votes.items()}
te = rng.choice(np.where(np.arange(len(y)) > 40000)[0], 300, replace=False)
hit = answered = 0
hole_hit = hole_tot = 0
TRUE_HOLES = {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 0, 8: 2, 9: 1}
for ix in te:
    s = signature(X[ix])
    if s is None:
        continue
    hole_tot += 1
    hole_hit += (s[0] == TRUE_HOLES[y[ix]])
    if s in sig_class:
        answered += 1
        hit += (sig_class[s] == y[ix])
acc = hit / max(answered, 1)
print(f"    hole-count agreement with canonical digit topology: "
      f"{hole_hit/max(hole_tot,1)*100:.1f}%  |  signature road: "
      f"{acc*100:.1f}% on {answered}/300")
check("hole counting is reliable on real handwriting (>= 75%)",
      hole_hit / max(hole_tot, 1) >= 0.75,
      f"{hole_hit}/{hole_tot}")
check("signature road far above chance (>= 30% where answered)",
      acc >= 0.30, f"{acc:.3f}")

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nSHAPES BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
