# -*- coding: utf-8 -*-
"""RELATIONAL ROTATION BATTERY — lines, rectangles, squares, and rotation
as a RELATION (owner, 2026-07-04): "a slanted 8 is just two circles at 15
degrees, a 7 is a 25 degree 1 with a second line on top, and a 1 is
either a stick line or... a 7 rotated to the left."

R1  rectangles and squares  -> hollow border reads FRAME (square flagged);
                               filled reads RECT; ellipse-vs-rect is FILL
R2  the slanted 8           -> same relational identity as the upright 8
                               (two rings, stacked); tilt reported ~15deg
R3  the 7 and the 1         -> 7 = TWO lines joined ~65deg; 1 = ONE line;
                               the rotated 7 keeps its joint angle
                               (identity) while the tilt moves (pose)
R4  MNIST signature road    -> re-measured with line-splitting (honest)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(47)

def blank(H=48):
    return np.zeros((H, H))

def draw_seg(img, p0, p1, w=1.6):
    (x0, y0), (x1, y1) = p0, p1
    yy, xx = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    px, py = xx.astype(float), yy.astype(float)
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((px - x0) * dx + (py - y0) * dy) / L2, 0, 1)
    d = np.sqrt((px - (x0 + t * dx)) ** 2 + (py - (y0 + t * dy)) ** 2)
    img[d < w] = 1.0
    return img

def draw_ring(H, cx, cy, rx, ry, w=2.0):
    yy, xx = np.mgrid[0:H, 0:H]
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return (np.abs(d - 1.0) * min(rx, ry) < w).astype(float)

def rot_pt(p, c, deg):
    th = np.radians(deg)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    return tuple(R @ (np.array(p) - c) + c)

i = Isaac()

# ── R1: rectangles and squares ──────────────────────────────────────
print("\nR1 — the rectangle family")
box = blank()
for a, b in [((10, 10), (38, 10)), ((38, 10), (38, 30)),
             ((38, 30), (10, 30)), ((10, 30), (10, 10))]:
    draw_seg(box, a, b, 1.8)
r_frame = i.describe_shape(box)
check("hollow rectangle reads FRAME",
      r_frame and any(p["kind"] == "frame" for p in r_frame["parts"]),
      r_frame["english"] if r_frame else "")
sq = blank()
sq[14:34, 14:34] = 1.0
r_sq = i.describe_shape(sq)
check("filled square reads square RECT",
      r_sq and any(p["kind"] == "rect" and p.get("square")
                   for p in r_sq["parts"]),
      r_sq["english"] if r_sq else "")
ring = i.describe_shape(draw_ring(48, 24, 24, 12, 12))
check("ellipse hole still reads RING (fill separates round from square)",
      ring and ring["parts"][0]["kind"] == "ring", ring["english"])

# ── R2: the slanted 8 ───────────────────────────────────────────────
print("\nR2 — a slanted 8 is the upright 8 wearing a tilt")
def eight(tilt_deg):
    im = blank(56)
    c = np.array([28.0, 28.0])
    c1 = rot_pt((28, 18), c, tilt_deg)
    c2 = rot_pt((28, 38), c, tilt_deg)
    im = np.maximum(im, draw_ring(56, c1[0], c1[1], 8, 7, 2.2))
    im = np.maximum(im, draw_ring(56, c2[0], c2[1], 9, 6, 2.2))
    return im
up = i.describe_shape(eight(0))
sl = i.describe_shape(eight(15))
sig = lambda r: (r["n_holes"], tuple(sorted(p["kind"] for p in r["parts"])))
check("relational identity equal (two rings, stacked)",
      sig(up) == sig(sl) and up["n_holes"] == 2,
      f"up={sig(up)} slant={sig(sl)}")
check("the tilt is reported (~15 deg)",
      abs(abs(sl["tilt"]) - 15) <= 6 and abs(up["tilt"]) <= 6,
      f"upright tilt {up['tilt']}, slanted tilt {sl['tilt']} — '{sl['english']}'")

# ── R3: the 7 and the 1 ─────────────────────────────────────────────
print("\nR3 — a 7 is a tilted line with a second line on top")
def seven(rot=0.0):
    im = blank(56)
    c = np.array([28.0, 28.0])
    top0, top1 = rot_pt((16, 12), c, rot), rot_pt((38, 12), c, rot)
    m0 = top1
    m1 = rot_pt((38 - 44 * np.tan(np.radians(25)), 12 + 34), c, rot)
    draw_seg(im, top0, top1, 1.7)
    draw_seg(im, m0, m1, 1.7)
    return im
def one():
    im = blank(56)
    draw_seg(im, (28, 10), (28, 44), 1.7)
    return im
r7 = i.describe_shape(seven())
r1_ = i.describe_shape(one())
lines7 = [p for p in r7["parts"] if p["kind"] == "line"]
joints7 = [e for e in r7["arrangement"] if str(e[2]).startswith("joint")]
check("the 7 is TWO lines", len(lines7) == 2, r7["english"])
j_ang = int(str(joints7[0][2]).split()[1]) if joints7 else None
check("joined at ~65 deg (90-25, the owner's arithmetic)",
      j_ang is not None and abs(j_ang - 65) <= 8, f"joint {j_ang}°")
check("the 1 is ONE line",
      len([p for p in r1_["parts"] if p["kind"] == "line"]) == 1,
      r1_["english"])
r7r = i.describe_shape(seven(-25))
joints7r = [e for e in r7r["arrangement"] if str(e[2]).startswith("joint")]
jr = int(str(joints7r[0][2]).split()[1]) if joints7r else None
check("rotated 7: joint angle SURVIVES (identity)",
      jr is not None and abs(jr - j_ang) <= 8, f"{j_ang}° -> {jr}°")
check("rotated 7: the tilt MOVES (pose)",
      abs(r7r["tilt"] - r7["tilt"]) >= 10,
      f"tilt {r7['tilt']} -> {r7r['tilt']}")

# ── R4: MNIST signature road, re-measured with lines ────────────────
print("\nR4 — the signature road with line-splitting (honest re-measure)")
from sklearn.datasets import fetch_openml
d = fetch_openml("mnist_784", version=1, as_frame=False, parser="liac-arff")
X = d.data.reshape(-1, 28, 28)
y = d.target.astype(int)
m = Isaac()
from collections import defaultdict, Counter
def signature(img):
    r = m.describe_shape(img)
    if r is None:
        return None
    nl = sum(1 for p in r["parts"] if p["kind"] == "line")
    return (r["n_holes"], min(nl, 4))
sig_votes = defaultdict(Counter)
for c in range(10):
    for im in X[y == c][:40]:
        s = signature(im)
        if s:
            sig_votes[s][c] += 1
sig_class = {s: v.most_common(1)[0][0] for s, v in sig_votes.items()}
te = rng.choice(np.where(np.arange(len(y)) > 40000)[0], 300, replace=False)
hit = answered = 0
for ix in te:
    s = signature(X[ix])
    if s in sig_class:
        answered += 1
        hit += (sig_class[s] == y[ix])
acc = hit / max(answered, 1)
print(f"    (holes, n_lines) road: {acc*100:.1f}% on {answered}/300")
check("line-aware signature stays far above chance (>= 30%)",
      acc >= 0.30, f"{acc:.3f}")

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nROTATION BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
