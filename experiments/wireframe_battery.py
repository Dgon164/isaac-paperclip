# -*- coding: utf-8 -*-
"""WIREFRAME BATTERY — the owner's 2D-transformer design (2026-07-04):
"a wireframe concept of the thing that isaac can then run numbers over...
bones and structures... lidar scan of the faces stitched into an idea...
assumed reflection axis of symmetry to fill out unknowns."

W1  bones beat ink       -> digit recognition on skeleton keynodes vs
                            farthest-point ink samples (same pattern net)
W2  symmetry earns fill  -> half-seen symmetric shape: axis found, hidden
                            points inferred close to truth
W3  asymmetric refuses   -> no axis minted on an asymmetric cloud
W4  stitching            -> two partial scans of one rigid body, sharing
                            4 anchor points, merge into one model whose
                            distances match ground truth
W5  stitching refuses    -> views with <3 shared points return None
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(31)

# ── W1: bones vs ink on MNIST ───────────────────────────────────────
print("\nW1 — structural keypoints (bones) vs ink sampling, same pattern net")
from sklearn.datasets import fetch_openml
d = fetch_openml("mnist_784", version=1, as_frame=False, parser="liac-arff")
X = d.data.reshape(-1, 28, 28)
y = d.target.astype(int)

def run_road(extract, tag):
    m = Isaac()
    for c in range(10):
        views = [extract(m, im) for im in X[y == c][:30]]
        m.learn_pattern(views, f"{tag}{c}", n_rot=1)
    te = rng.choice(np.where(np.arange(len(y)) > 40000)[0], 200, replace=False)
    hit = answered = 0
    for ix in te:
        kp = extract(m, X[ix])
        if len(kp) < 4:
            continue
        th = rng.uniform(-0.15, 0.15)
        R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
        kp = (kp @ R.T) * rng.uniform(0.5, 2.0) + rng.uniform(-20, 20, 2)
        got, _ = m.recognize_pattern(kp)
        if got is not None:
            answered += 1
            hit += (got == f"pattern:{tag}{y[ix]}")
    return (hit / max(answered, 1)), answered

acc_bones, ans_bones = run_road(
    lambda m, im: m.keypoints_structural(im, k_min=10), "bone")
acc_ink, ans_ink = run_road(
    lambda m, im: m._keypoints_from_image(im, k=16), "ink")
print(f"    bones: {acc_bones*100:.1f}% on {ans_bones}/200 answered   "
      f"ink: {acc_ink*100:.1f}% on {ans_ink}/200 answered")
check("bones beat ink where answered", acc_bones > acc_ink,
      f"{acc_bones:.3f} vs {acc_ink:.3f}")
check("bones win on TOTAL correct answers per 200",
      acc_bones * ans_bones > acc_ink * ans_ink,
      f"{acc_bones*ans_bones:.0f} vs {acc_ink*ans_ink:.0f} "
      f"(coverage {ans_bones} vs {ans_ink} — the open dial)")

# ── W2: symmetry completion on a half-seen shape ────────────────────
print("\nW2 — the assumed axis fills the unseen side")
i = Isaac()
# a symmetric 3D 'face' mirrored across x=0. The scan saw the whole right
# side and a SLIVER of the left (3 points) — symmetry is unfalsifiable
# from one side alone (the first battery draft demanded exactly that and
# the organ CORRECTLY refused; the test was wrong, not the refusal).
right = np.array([[0.2, 0, 0], [0.8, 0.1, 0.3], [0.5, 0.7, 0.1],
                  [0.9, 0.5, 0.6], [0.3, 0.9, 0.4], [0.6, 0.3, 0.8],
                  [0.0, 0.5, 0.5], [0.0, 0.2, 0.9]])
full = np.vstack([right, right[:6] * [-1, 1, 1]])   # unique mirrors only
seen = np.vstack([right, right[:3] * [-1, 1, 1]])   # right + a sliver
res = i.complete_symmetry(seen)
ok_axis = res["axis"] is not None and abs(abs(res["axis"][0]) - 1) < 0.1
check("reflection axis earned (x-normal)", ok_axis,
      f"axis={None if res['axis'] is None else np.round(res['axis'],2)}")
if ok_axis and len(res["inferred"]):
    hidden = full[full[:, 0] < -1e-9]
    d2 = ((res["inferred"][:, None, :] - hidden[None, :, :]) ** 2).sum(-1)
    err = float(np.sqrt(d2.min(1)).mean())
    check("inferred points land on the hidden truth", err < 0.05,
          f"mean err {err:.4f} over {len(res['inferred'])} inferred")
else:
    check("inferred points land on the hidden truth", False, "nothing inferred")

# ── W3: asymmetric cloud refuses ────────────────────────────────────
print("\nW3 — no symmetry invented")
refused = 0
for s in range(10):
    cloud = np.random.default_rng(50 + s).uniform(-1, 1, (12, 3))
    r3 = Isaac().complete_symmetry(cloud)
    refused += (r3["axis"] is None)
check("asymmetric clouds refuse an axis (>= 8/10)", refused >= 8,
      f"{refused}/10 refused")

# ── W4: stitch two partial scans into one idea ──────────────────────
print("\nW4 — faces stitched into an idea")
body = rng.normal(size=(12, 3))
ids = list(range(12))
# view A sees points 0..7, view B sees 4..11, each in its own pose
def posed(P, rng):
    q = rng.normal(size=(3, 3))
    Q, _ = np.linalg.qr(q)
    Q *= np.sign(np.linalg.det(Q))
    return P @ Q.T + rng.uniform(-5, 5, 3)
vA = (ids[:8], posed(body[:8], rng))
vB = (ids[4:], posed(body[4:], rng))
st = Isaac.stitch_views([vA, vB])
check("two overlapping views merge", st is not None and len(st[0]) == 12,
      f"{0 if st is None else len(st[0])} points in the model")
if st:
    sid, sp = st
    # all pairwise distances must match the true body (rigid stitch)
    dt = np.linalg.norm(body[:, None] - body[None, :], axis=-1)
    dm = np.linalg.norm(sp[:, None] - sp[None, :], axis=-1)
    err = float(np.abs(dt - dm).max())
    check("stitched distances match ground truth", err < 1e-6,
          f"max err {err:.2e}")

# ── W5: stitching refuses thin overlap ──────────────────────────────
print("\nW5 — stitching that can refuse")
vC = (ids[:6], posed(body[:6], rng))
vD = (ids[8:], posed(body[8:], rng))   # shares 0 points with vC
check("non-overlapping views return None",
      Isaac.stitch_views([vC, vD]) is None)

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nWIREFRAME BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
