import sys
import time

import numpy as np

sys.path.insert(0, r"c:\Users\jtwee\Documents\isaac-paperclip")
from isaac_store import bridge

mod = bridge.load_isaac_module()
rng = np.random.default_rng(5)
n = 5000

# synthetic jets with the TRUE m_jj physics, columns like HIGGS order
pt1 = np.exp(rng.normal(0, 0.5, n)) * 0.8 + 0.2
pt2 = np.exp(rng.normal(0, 0.5, n)) * 0.8 + 0.2
eta1, eta2 = rng.uniform(-2.5, 2.5, n), rng.uniform(-2.5, 2.5, n)
phi1, phi2 = rng.uniform(-np.pi, np.pi, n), rng.uniform(-np.pi, np.pi, n)
m2 = 2 * pt1 * pt2 * (np.cosh(eta1 - eta2) - np.cos(phi1 - phi2))
X = np.column_stack([pt1, eta1, phi1, pt2, eta2, phi2])

for frame, target in (("y2", m2), ("y", np.sqrt(m2))):
    mind = mod.Isaac()
    t0 = time.perf_counter()
    mind.discover(X, target, name=f"mjj_{frame}")
    f = mind.findings[-1]
    print(f"SYNTH frame={frame}: {time.perf_counter()-t0:.0f}s "
          f"verdict={f.get('verdict')} r2={f.get('r2'):.4f}")
    print("   eq:", str(f.get("equation"))[:110])

# and what does the real HIGGS data actually look like?
arr = np.load(r"c:\Users\jtwee\Documents\isaac_project\data\HIGGS.npy",
              mmap_mode="r")
cols = {"j1pt": 6, "j1eta": 7, "j1phi": 8, "j2pt": 10, "j2eta": 11,
        "j2phi": 12, "m_jj": 22}
print("\nHIGGS column stats (first 100k rows):")
for name, c in cols.items():
    v = np.asarray(arr[:100000, c], dtype=np.float64)
    print(f"  {name:6s} mean={v.mean():7.3f} std={v.std():6.3f} "
          f"min={v.min():7.3f} max={v.max():8.3f}")
# does the physics identity hold on the stored columns as-is?
v = {k: np.asarray(arr[:100000, c], dtype=np.float64) for k, c in cols.items()}
m2_raw = 2 * v["j1pt"] * v["j2pt"] * (np.cosh(v["j1eta"] - v["j2eta"])
                                      - np.cos(v["j1phi"] - v["j2phi"]))
pred = np.sqrt(np.clip(m2_raw, 0, None))
r = np.corrcoef(pred, v["m_jj"])[0, 1]
ratio = v["m_jj"] / np.maximum(pred, 1e-9)
print(f"\nidentity check on stored columns: corr(sqrt(2·pt·pt·(coshΔη−cosΔφ)), m_jj) = {r:.4f}")
print(f"scale ratio m_jj/pred: median={np.median(ratio):.4f} "
      f"IQR=({np.percentile(ratio,25):.4f},{np.percentile(ratio,75):.4f})")
