# -*- coding: utf-8 -*-
"""HIGGS pair-door battery (2026-07-09). Tests the comparison-tower law
'depth is question shape' on the REAL dataset: the weighted-signals
layer (higgs_best.py road B) reads each sensor's density alone and is
structurally blind to interactions. Here we add 2D COMPOUND DOORS --
joint density signals over feature pairs (16x16 bins), pairs admitted
by interaction EXCESS over what the two marginals already explain --
into the same printable softmax. Everything stays extractable.

Registered prediction: beats B (68.07% / AUC 0.7479); does not reach
the deep-net 0.885 (3-jet+ interactions remain unspoken).
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

NAMES = ["lep_pT", "lep_eta", "lep_phi", "MET", "MET_phi",
         "j1_pT", "j1_eta", "j1_phi", "j1_btag",
         "j2_pT", "j2_eta", "j2_phi", "j2_btag",
         "j3_pT", "j3_eta", "j3_phi", "j3_btag",
         "j4_pT", "j4_eta", "j4_phi", "j4_btag",
         "m_jj", "m_jjj", "m_lv", "m_jlv", "m_bb", "m_wbb", "m_wwbb"]

rng = np.random.default_rng(4)                      # same draw as higgs_best
D = np.load(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "HIGGS.npy"), mmap_mode="r")
sel = np.sort(rng.choice(len(D), 500_000, replace=False))
Xy = np.asarray(D[sel], dtype=np.float64)
y = Xy[:, 0].astype(int)
X = Xy[:, 1:]
tr, te = slice(0, 400_000), slice(400_000, 500_000)
d = X.shape[1]
classes = np.unique(y[tr])
C = len(classes)
print(f"HIGGS: sampled 500k (400k train / 100k test), same seed as higgs_best\n")

def auc_of(scores, truth):
    order = np.argsort(scores)
    ranks = np.empty(len(scores))
    ranks[order] = np.arange(len(scores))
    n1 = int((truth == 1).sum()); n0 = len(truth) - n1
    return (ranks[truth == 1].sum() - n1 * (n1 - 1) / 2) / (n1 * n0)

# ── 1D doors (identical road to higgs_best B) ───────────────────────
t0 = time.time()
i = Isaac()
i.crystallize_features(X[tr], y[tr], bins=32, compounds="off")
calib = i.net.get_meta("crystal", "calib")
lds = [i.net.get_meta(f"concept:{c}", "doors") for c in classes]
print(f"1D doors crystallized  [{time.time()-t0:.0f}s]")

def signals_1d(Xs, chunk=100_000):
    out = np.empty((len(Xs), d * C), dtype=np.float32)
    e = calib["edges"]
    for s0 in range(0, len(Xs), chunk):
        H = i.apply_lens(calib["lens"], Xs[s0:s0 + chunk])
        for j in range(d):
            ix = np.searchsorted(e[j], H[:, j])
            for k in range(C):
                out[s0:s0 + len(H), j * C + k] = lds[k][j][ix]
    return out

# ── 2D pair doors: 16-bin quantile indices in lens space ────────────
t0 = time.time()
B2 = 16
def lens_of(Xs, chunk=100_000):
    out = np.empty((len(Xs), d))
    for s0 in range(0, len(Xs), chunk):
        out[s0:s0 + chunk] = i.apply_lens(calib["lens"], Xs[s0:s0 + chunk])
    return out

Htr = lens_of(X[tr])
edges2 = [np.quantile(Htr[:, j], np.linspace(0, 1, B2 + 1))[1:-1]
          for j in range(d)]
def ix16(H):
    out = np.empty(H.shape, dtype=np.int16)
    for j in range(d):
        out[:, j] = np.searchsorted(edges2[j], H[:, j])
    return out
IXtr = ix16(Htr); del Htr

# per-class joint counts for every pair; admit by interaction EXCESS
pairs = [(a, b) for a in range(d) for b in range(a + 1, d)]
m1 = np.zeros((C, d, B2))
for k, c in enumerate(classes):
    for j in range(d):
        m1[k, j] = np.bincount(IXtr[y[tr] == c][:, j], minlength=B2)
m1 /= m1.sum(axis=2, keepdims=True)

counts = {}
excess = np.empty(len(pairs))
for pi, (a, b) in enumerate(pairs):
    joint = IXtr[:, a].astype(np.int32) * B2 + IXtr[:, b]
    cs = np.stack([np.bincount(joint[y[tr] == c], minlength=B2 * B2)
                   for c in classes]).astype(np.float64)
    counts[(a, b)] = cs
    P = cs / cs.sum(axis=1, keepdims=True)
    D2 = np.abs(P[1] - P[0]).sum()
    ind = np.abs(np.outer(m1[1, a], m1[1, b]) -
                 np.outer(m1[0, a], m1[0, b])).ravel().sum()
    excess[pi] = D2 - ind
K = int(os.environ.get("PAIR_K", "220"))
top_pairs = [pairs[pi] for pi in np.argsort(-excess)[:K]]
print(f"2D doors: {len(pairs)} pairs scored; {K} admitted by interaction "
      f"excess  [{time.time()-t0:.0f}s]")
print("   top-5 admitted pairs (excess beyond marginals):")
for pi in np.argsort(-excess)[:5]:
    a, b = pairs[pi]
    print(f"     {NAMES[a]} x {NAMES[b]}   excess {excess[pi]:.3f}")

lds2 = {}
for (a, b) in top_pairs:
    cs = counts[(a, b)]
    lds2[(a, b)] = np.log((cs + 1.0) / (cs.sum(axis=1, keepdims=True)
                                        + B2 * B2)).astype(np.float32)

def signals_2d(Xs, chunk=100_000):
    out = np.empty((len(Xs), K * C), dtype=np.float32)
    for s0 in range(0, len(Xs), chunk):
        IX = ix16(lens_of(Xs[s0:s0 + chunk]))
        for p, (a, b) in enumerate(top_pairs):
            joint = IX[:, a].astype(np.int32) * B2 + IX[:, b]
            for k in range(C):
                out[s0:s0 + len(IX), p * C + k] = lds2[(a, b)][k][joint]
    return out

# ── the same printable softmax, over 1D + 2D signals ────────────────
def train_and_test(mk_signals, label):
    t0 = time.time()
    cut = 340_000
    A = mk_signals(X[cut:400_000])
    mu, sd = A.mean(0), A.std(0) + 1e-9
    A = (A - mu) / sd
    Y1 = (y[cut:400_000][:, None] == classes[None, :]).astype(float)
    r = np.random.default_rng(7)
    W = r.normal(0, 0.01, (A.shape[1], C)); b = np.zeros(C)
    vW = np.zeros_like(W)
    for _ in range(1200):
        Z = A @ W + b; Z -= Z.max(1, keepdims=True)
        P = np.exp(Z); P /= P.sum(1, keepdims=True)
        G = (P - Y1) / len(A)
        vW = 0.9 * vW - 0.3 * (A.T @ G + 1e-4 * W)
        W += vW; b -= 0.3 * G.sum(0)
    St = (mk_signals(X[te]) - mu) / sd
    Z = St @ W + b
    acc = (classes[np.argmax(Z, 1)] == y[te]).mean()
    auc = auc_of(Z[:, 1] - Z[:, 0], y[te])
    print(f"{label}: {acc*100:.2f}%  AUC {auc:.4f}  [{time.time()-t0:.0f}s]")
    return acc, auc, W

acc_b, auc_b, _ = train_and_test(signals_1d, "B  1D signals (record) ")
both = lambda Xs: np.concatenate([signals_1d(Xs), signals_2d(Xs)], axis=1)
acc_p, auc_p, W = train_and_test(both, "B+ 1D + 2D pair doors  ")

pw = np.abs(W[d * C:]).reshape(K, C, C).sum((1, 2))
print("\n   top-weighted PAIR doors in the trained layer (extracted):")
for p in np.argsort(-pw)[:6]:
    a, b = top_pairs[p]
    print(f"     {NAMES[a]} x {NAMES[b]}   weight {pw[p]:.1f}")
print(f"\ndelta over record: {100*(acc_p-acc_b):+.2f} pts, "
      f"AUC {auc_p-auc_b:+.4f}")
print("deep-net benchmark ~AUC 0.885 (Baldi 2014): "
      f"{'matched' if auc_p >= 0.885 else 'NOT matched'}")
