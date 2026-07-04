# -*- coding: utf-8 -*-
"""PATTERN/3D BATTERY — the owner's two-regime build (2026-07-04):
"2D→3D scan modeling... but it needs to work on 2d to 2d abstraction too.
it can learn the spatial pattern net."

One mechanism, two regimes: when views are FRAMES of one moving thing,
the residual across views earns a depth coordinate (Tomasi–Kanade,
null-gated); when views are INSTANCES of a class, what survives
registration is the canonical pattern, crystallized into the net.

L1  3D lift recovers depth   -> rotating rigid body: 3D distances constant,
                                same body recognized across motions
L2  flat refuses depth       -> planar scene: lift declines (null)
L3  noise refuses everything
P1  glyph abstraction        -> 3 synthetic patterns learned; fresh
                                transformed instances recognized
P2  abstention               -> junk points get a shrug, not a guess
P3  digits under transform   -> MNIST keypoints, rotated+scaled+shifted:
                                registration >> unregistered baseline
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(21)

def rot3(rng):
    q = rng.normal(size=(3, 3))
    Q, _ = np.linalg.qr(q)
    return Q * np.sign(np.linalg.det(Q))

def project_motion(S3, T, rng, noise=0.002):
    """Orthographic 2D tracks of rigid 3D shape S3 (n,3) under smooth rotation."""
    n = len(S3)
    F = np.empty((T, n, 2))
    axis = rng.normal(size=3); axis /= np.linalg.norm(axis)
    base = rot3(rng)
    for t in range(T):
        ang = 0.05 * t
        c, s = np.cos(ang), np.sin(ang)
        ux, uy, uz = axis
        K = np.array([[0, -uz, uy], [uz, 0, -ux], [-uy, ux, 0]])
        R = np.eye(3) + s * K + (1 - c) * (K @ K)
        P3 = (base @ R @ S3.T).T
        F[t] = P3[:, :2] + rng.normal(0, noise, size=(n, 2))
    return F

# ── L1: depth recovered, body recognized across motions ────────────
print("\nL1 — the 3D lift on a rotating rigid body")
S3 = rng.normal(size=(10, 3))
i = Isaac()
F = project_motion(S3, 80, rng)
F3, rep = i._lift_depth(F)
check("lift admits depth", F3 is not None and rep["lifted"],
      rep.get("why", f"z_extent={rep.get('z_extent', 0):.3f}"))
if F3 is not None:
    d_true = np.linalg.norm(S3[0] - S3[1])
    ds = np.linalg.norm(F3[:, 0] - F3[:, 1], axis=1)
    check("recovered 3D distances constant through rotation",
          ds.std() / ds.mean() < 0.02,
          f"cv={ds.std()/ds.mean():.4f} (2D distances varied "
          f"{np.linalg.norm(F[:,0]-F[:,1],axis=1).std()/np.linalg.norm(F[:,0]-F[:,1],axis=1).mean():.2f})")
    # same body, different motion -> SAME; different body -> DIFFERENT
    i.observe_spatial(F, label="bodyA_run1")
    i.observe_spatial(project_motion(S3, 80, rng), label="bodyA_run2")
    i.observe_spatial(project_motion(rng.normal(size=(10, 3)), 80, rng),
                      label="bodyB")
    same = i.compare_scenes("bodyA_run1", "bodyA_run2")
    diff = i.compare_scenes("bodyA_run1", "bodyB")
    check("same body across motions -> SAME", same.get("verdict") == "SAME",
          f"gap={same.get('signature_gap')}")
    check("different body -> DIFFERENT", diff.get("verdict") == "DIFFERENT",
          f"gap={diff.get('signature_gap')}")

# ── L2: a flat scene refuses depth ──────────────────────────────────
print("\nL2 — planar refuses the third coordinate")
S2 = np.column_stack([rng.normal(size=(8, 2)), np.zeros(8)])
Fflat = np.empty((60, 8, 2))
for t in range(60):
    th = 0.05 * t
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    Fflat[t] = S2[:, :2] @ R.T + rng.normal(0, 0.002, size=(8, 2))
F3f, repf = Isaac()._lift_depth(Fflat)
check("planar: depth refused", F3f is None and "planar" in repf.get("why", ""),
      repf.get("why", ""))

# ── L3: noise refuses ───────────────────────────────────────────────
print("\nL3 — random walks refuse")
Fn = np.cumsum(rng.normal(0, 0.1, size=(60, 6, 2)), axis=0)
F3n, repn = Isaac()._lift_depth(Fn)
j = Isaac()
j.observe_spatial(Fn, label="noise")
n_facts = sum(len(v) for k, v in j.fact_index.items())
check("noise: lift refused AND no relations taught",
      F3n is None and n_facts == 0, f"{n_facts} facts, why={repn.get('why','')[:40]}")

# ── P1: the spatial pattern net on synthetic glyphs ─────────────────
print("\nP1 — 2D→2D abstraction: glyphs")
TEMPLATES = {
    "tri":  np.array([[0, 0], [1, 0], [0.5, 0.9], [0.5, 0.3], [0.25, 0.45],
                      [0.75, 0.45]]),
    "bar":  np.array([[0, 0], [0, 0.5], [0, 1], [0, 1.5], [0.2, 0.75],
                      [-0.2, 0.75]]),
    "ring": np.array([[np.cos(a), np.sin(a)] for a in
                      np.linspace(0, 2 * np.pi, 7)[:-1]]),
}
def instance(T_, rng, jit=0.04):
    th = rng.uniform(0, 2 * np.pi)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    s = rng.uniform(0.5, 2.0)
    return (T_ @ R.T) * s + rng.uniform(-5, 5, 2) + \
        rng.normal(0, jit, T_.shape)

k = Isaac()
for name, T_ in TEMPLATES.items():
    pn = k.learn_pattern([instance(T_, rng) for _ in range(20)], name)
    assert pn, f"pattern {name} refused"
hits = 0
trials = 60
for _ in range(trials):
    name = list(TEMPLATES)[rng.integers(0, 3)]
    got, _ = k.recognize_pattern(instance(TEMPLATES[name], rng))
    hits += (got == f"pattern:{name}")
check("fresh transformed glyphs recognized >= 90%", hits / trials >= 0.9,
      f"{hits}/{trials}")

# ── P2: abstention on junk ──────────────────────────────────────────
print("\nP2 — junk points get a shrug")
shrugs = sum(k.recognize_pattern(rng.uniform(-1, 1, (12, 2)))[0] is None
             for _ in range(20))
check("junk mostly refused (>= 15/20 shrugs)", shrugs >= 15, f"{shrugs}/20")

# ── P3: MNIST digits under transform ────────────────────────────────
print("\nP3 — digits: keypoint pattern nets vs unregistered baseline")
try:
    from sklearn.datasets import fetch_openml
    d = fetch_openml("mnist_784", version=1, as_frame=False,
                     parser="liac-arff")
    X = d.data.reshape(-1, 28, 28)
    y = d.target.astype(int)
    m = Isaac()
    for c in range(10):
        imgs = X[y == c][:30]
        views = [m._keypoints_from_image(im, k=16) for im in imgs]
        # n_rot=1: rotation freedom is NOT part of the digit class
        # (a 6 is an upside-down 9); ICP still absorbs small tilts
        m.learn_pattern(views, f"digit{c}", n_rot=1)
    te_idx = rng.choice(np.where(np.arange(len(y)) > 40000)[0], 200,
                        replace=False)
    hit_reg = hit_raw = answered = 0
    canons = {c: np.asarray(m.net.get_meta(f"pattern:digit{c}", "canon"))
              for c in range(10)
              if m.net.get_meta(f"pattern:digit{c}", "canon") is not None}
    for ix in te_idx:
        kp = m._keypoints_from_image(X[ix], k=16)
        if len(kp) < 4:
            continue
        th = rng.uniform(-0.15, 0.15)                # small tilt only
        R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
        kp = (kp @ R.T) * rng.uniform(0.5, 2.0) + rng.uniform(-20, 20, 2)
        got, scores = m.recognize_pattern(kp)
        if got is not None:
            answered += 1
            hit_reg += (got == f"pattern:digit{y[ix]}")
        # unregistered baseline: nearest canonical by raw normalized overlap
        P = m._norm_points(kp)
        raw_best, raw_res = None, np.inf
        for c, canon in canons.items():
            d2 = ((P[:, None, :] - canon[None, :, :]) ** 2).sum(-1)
            r = float(np.sqrt(d2.min(1).mean()))
            if r < raw_res:
                raw_best, raw_res = c, r
        hit_raw += (raw_best == y[ix])
    acc_reg = hit_reg / max(answered, 1)
    acc_raw = hit_raw / len(te_idx)
    print(f"    registered pattern nets: {acc_reg*100:.1f}% on the "
          f"{answered}/{len(te_idx)} it answered; "
          f"unregistered baseline {acc_raw*100:.1f}%")
    check("registration beats the unregistered baseline by >= 15 pts",
          acc_reg - acc_raw >= 0.15, f"{acc_reg:.3f} vs {acc_raw:.3f}")
except Exception as e:
    check("digits test ran", False, str(e)[:80])

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nPATTERN/3D BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
