import numpy as np

arr = np.load(r"c:\Users\jtwee\Documents\isaac_project\data\HIGGS.npy",
              mmap_mode="r")
n = 100000
g = lambda c: np.asarray(arr[:n, c], dtype=np.float64)
mjj = g(22)

PAIRS = {"jets(1,2)": (6, 7, 8, 10, 11, 12), "jets(1,3)": (6, 7, 8, 14, 15, 16),
         "jets(2,3)": (10, 11, 12, 14, 15, 16)}
print("best corr(sqrt(2 pt pt (cosh(a*deta) - cos(b*dphi))), m_jj) over scale scan:")
for name, (p1, e1, f1, p2, e2, f2) in PAIRS.items():
    pt1, pt2 = g(p1), g(p2)
    deta, dphi = g(e1) - g(e2), g(f1) - g(f2)
    best = (0, 0, 0)
    for a in np.arange(0.6, 2.4, 0.1):
        for b in np.arange(1.0, 2.4, 0.1):
            m2 = 2 * pt1 * pt2 * (np.cosh(np.clip(a * deta, -15, 15))
                                  - np.cos(b * dphi))
            r = np.corrcoef(np.sqrt(np.clip(m2, 0, None)), mjj)[0, 1]
            if r > best[0]:
                best = (r, a, b)
    print(f"  {name}: corr={best[0]:.4f} at a={best[1]:.1f} b={best[2]:.1f}")
