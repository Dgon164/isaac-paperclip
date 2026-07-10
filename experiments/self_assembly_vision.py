# -*- coding: utf-8 -*-
"""SELF-ASSEMBLY VISION (owner's usage law, 2026-07-10): "giving it the
language is one thing... telling it how to use them is not. It needs to
learn how to represent ideas using structures that we provide."

The division tested here, by battery:
  HAND-BUILT stays: the vocabulary organs (describe_shape, keypoints,
  dynamics — the measuring instruments) and the TRANSLATION of an image
  into the vocabulary's plain facts. NO signatures, NO per-class logic,
  NO comparison recipes written by us.
  LEARNED: which facts and combinations carry identity — decided by the
  engine's EXISTING null-gated learner (crystallize_features doors +
  compound admission), the same organ that learns any other dataset.

Compared against the hand-taught usage of the same vocabulary
(vision_benchmark 2026-07-10 log): topology-signature channel 57.7%,
bones-variant channel 35.7% — both of those are usages WE wrote.

Registered predictions:
  P1  self-assembled usage of the structure language beats the
      hand-written topology signature (57.7%).
  P2  structure facts + raw pixels through ONE learner beats raw
      pixels through the same learner (independent witness, no hand
      fusion anywhere).
All numbers COMPLETE (accuracy on the whole 1000-glyph test set).
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

rng = np.random.default_rng(8)
from sklearn.datasets import fetch_openml
d = fetch_openml("mnist_784", version=1, as_frame=False, parser="liac-arff")
X = d.data.reshape(-1, 28, 28)
y = d.target.astype(int)
tr_idx = np.concatenate([np.where(y[:40000] == c)[0][:200] for c in range(10)])
te_idx = rng.choice(np.where(np.arange(len(y)) > 40000)[0], 1000, replace=False)

i = Isaac()

def translate(im):
    """Image -> the vocabulary's facts. Translation only: every number
    is something a vocabulary organ already measures; none of it says
    how to compare or what a 7 looks like."""
    f = []
    r = i.describe_shape(im)
    parts = r["parts"] if r else []
    kinds = [p["kind"] for p in parts]
    f.append(r["n_holes"] if r else 0)                    # holes
    f.append(len(parts))                                  # part count
    for k in ("line", "ring", "disc", "rect", "frame"):
        f.append(kinds.count(k))                          # kind counts
    rings = [p for p in parts if p["kind"] in ("ring", "frame")]
    f.append(np.mean([p["squish"] for p in rings]) if rings else 0)
    f.append(np.mean([p["size"] for p in rings]) if rings else 0)
    f.append((min(p["size"] for p in rings) /
              max(p["size"] for p in rings)) if len(rings) >= 2 else 0)
    lines = sorted([p for p in parts if p["kind"] == "line"],
                   key=lambda p: -p.get("length", 0))
    f.append(sum(p.get("length", 0) for p in lines))
    f.append((lines[1]["length"] / lines[0]["length"])
             if len(lines) >= 2 and lines[0].get("length") else 0)
    f.append(lines[0]["rel_angle"] if lines else 0)       # identity angle
    f.append(lines[1]["rel_angle"] if len(lines) >= 2 else 0)
    f.append(abs(lines[0]["rel_angle"] - lines[1]["rel_angle"])
             if len(lines) >= 2 else 0)                   # relation
    edges = r["arrangement"] if r else []
    joints = [e for e in edges if str(e[2]).startswith("joint")]
    f.append(len(joints))
    f.append(float(str(joints[0][2]).split()[1].rstrip("°"))
             if joints else 0)
    for rel in ("above", "below", "touching"):
        f.append(sum(1 for e in edges if e[2] == rel))
    f.append(r["tilt"] if r else 0)                       # pose, a report
    kp = i.keypoints_structural(im, k_min=10)
    f.append(len(kp))
    if len(kp) >= 4:
        P = np.asarray(kp, float)
        D = np.linalg.norm(P[:, None] - P[None, :], axis=-1)
        dv = D[np.triu_indices(len(P), 1)]
        f.append(dv.std() / (dv.mean() + 1e-9))           # shape spread
        f.append(dv.min() / (dv.max() + 1e-9))            # ratio, not px
    else:
        f += [0, 0]
    f.extend(i.dynamics_features(im))                     # the flow, 10
    ys, xs = np.where(im > 0.5 * im.max()) if im.max() > 0 else ([0], [0])
    f.append(len(ys) / im.size)                           # ink fraction
    f.append((max(ys) - min(ys) + 1) / (max(xs) - min(xs) + 1))  # aspect
    return np.array(f, float)

t0 = time.time()
F_tr = np.array([translate(im) for im in X[tr_idx]])
F_te = np.array([translate(im) for im in X[te_idx]])
print(f"translated {len(F_tr)+len(F_te)} images into {F_tr.shape[1]} "
      f"vocabulary facts  [{time.time()-t0:.0f}s]")

def run(A_tr, A_te, name):
    t0 = time.time()
    ii = Isaac()
    ii.crystallize_features(A_tr, y[tr_idx], compounds="auto")
    got = ii.classify_features(A_te)
    acc = (got.astype(int) == y[te_idx]).mean()
    print(f"  {name}: {acc*100:.1f}%  [{time.time()-t0:.0f}s]")
    return acc

print("\nSAME learner, three inputs (complete numbers, 1000 test):")
acc_f = run(F_tr, F_te, "structure facts, usage SELF-ASSEMBLED")
flat_tr = X[tr_idx].reshape(len(tr_idx), -1)
flat_te = X[te_idx].reshape(len(te_idx), -1)
acc_p = run(flat_tr, flat_te, "raw pixels                      ")
acc_b = run(np.column_stack([flat_tr, F_tr]),
            np.column_stack([flat_te, F_te]),
            "pixels + structure facts        ")

print(f"\nhand-taught usage of the SAME vocabulary (recorded, "
      f"vision_benchmark): topology signature 57.7%, bones variants 35.7%")
print(f"P1 self-assembled beats hand-written topology usage: "
      f"{'CONFIRMED' if acc_f > 0.577 else 'REFUTED'} "
      f"({acc_f*100:.1f} vs 57.7)")
print(f"P2 structure facts add to pixels through one learner: "
      f"{'CONFIRMED' if acc_b > acc_p else 'REFUTED'} "
      f"({acc_b*100:.1f} vs {acc_p*100:.1f})")
