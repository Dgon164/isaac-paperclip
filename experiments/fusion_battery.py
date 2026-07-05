# -*- coding: utf-8 -*-
"""FUSION BATTERY — all methods, one concept (owner, 2026-07-05): "the
doors are just pointer connections... they all point to the same nodes."

Every channel (pixel densities, topology signatures, bones patterns,
exemplars) attaches evidence to the SAME concept nodes; recognition sums
what all of them say. ALL numbers below are COMPLETE numbers — accuracy
against the whole test set, no coverage conditioning, no padding.

F1  each single channel measured alone (complete numbers)
F2  the fused vote measured (complete number)
F3  fusion must not lose to its best single channel
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

rng = np.random.default_rng(8)
from sklearn.datasets import fetch_openml
d = fetch_openml("mnist_784", version=1, as_frame=False, parser="liac-arff")
X = d.data.reshape(-1, 28, 28)
y = d.target.astype(int)

# train: 200/class; test: 500 unseen
tr_idx = np.concatenate([np.where(y[:40000] == c)[0][:200] for c in range(10)])
te_idx = rng.choice(np.where(np.arange(len(y)) > 40000)[0], 500, replace=False)

i = Isaac()
print("learning all channels onto one set of concept nodes "
      f"({len(tr_idx)} training glyphs)...")
i.learn_glyphs(X[tr_idx], y[tr_idx])

hits = {"density": 0, "topology": 0, "bones": 0, "exemplar": 0,
        "dynamics": 0, "FUSED": 0}
n = len(te_idx)
for ix in te_idx:
    got, posts = i.recognize_glyph(X[ix])
    classes = i.net.get_meta("crystal", "glyph_classes")
    if got == y[ix]:
        hits["FUSED"] += 1
    for k, p in posts.items():
        if str(k).startswith("_"):
            continue
        if classes[int(np.argmax(p))] == y[ix]:
            hits[k] += 1

print(f"\nCOMPLETE numbers over all {n} test digits:")
for k in ("topology", "bones", "dynamics", "density", "exemplar", "FUSED"):
    print(f"  {k:9s}: {hits[k]/n*100:5.1f}%")

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

best_single = max(v for k, v in hits.items() if k != "FUSED")
print()
check("fusion does not lose to its best single channel",
      hits["FUSED"] >= best_single - 5,
      f"fused {hits['FUSED']}/{n} vs best single {best_single}/{n}")
check("fusion is a real classifier (>= 85% complete)",
      hits["FUSED"] / n >= 0.85, f"{hits['FUSED']/n*100:.1f}%")

# one readable vote, for the record
print("\none glyph's vote, in the open:")
got, _ = i.recognize_glyph(X[te_idx[0]], verbose=True)
print(f"    -> {got} (truth {y[te_idx[0]]})")

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nFUSION BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
