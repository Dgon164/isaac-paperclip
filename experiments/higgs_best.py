# -*- coding: utf-8 -*-
"""HIGGS — CURRENT BEST STANDING RESULTS, one reproducible file
(2026-07-09). All numbers COMPLETE numbers; every claim within the laws
(no net is ever the deliverable; the one lawful trained object is a
single softmax layer whose weights are printable — extracted below).

  A. classification, flat doors        (the additive baseline)
  B. classification, WEIGHTED SIGNALS  (the best lawful number):
     one softmax layer over every per-feature per-class density signal
     (28 features x 2 classes = 56 named inputs), extracted to readable
     per-sensor weights
  C. the formula road: the transverse-mass law said blind (from
     higgs_map.py, recorded here)
  D. the resonance enumerated: expect background, subtract, the delta
     is the particle (null-gated)

Record corrections that stand: the old 'detector equation AUC 0.848'
was a torch MLP in an equation costume - OVERTURNED 2026-07-05. The
deep-net benchmark (~AUC 0.885, Baldi 2014) is NOT matched by any
lawful road here.

SUPERSEDED 2026-07-09 as best classification number by higgs_pairs.py:
B+ (1D signals + 220 pair doors admitted by interaction excess, same
printable softmax) = 71.18% / AUC 0.7886. The road-B number below
(68.07% / AUC 0.7479) stands as the 1D-only record. Saturation curve
measured: 60 pairs 70.02%, 150 70.73%, 220 71.18% (peak), 300 70.28%,
378 66.43% (readout drowns). This file still reproduces A-D unchanged.
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

rng = np.random.default_rng(4)
D = np.load(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "HIGGS.npy"), mmap_mode="r")
sel = np.sort(rng.choice(len(D), 500_000, replace=False))
Xy = np.asarray(D[sel], dtype=np.float64)
y = Xy[:, 0].astype(int)
X = Xy[:, 1:]
tr, te = slice(0, 400_000), slice(400_000, 500_000)
print(f"HIGGS: {len(D):,} rows; sampled 500k (400k train / 100k test)\n")

def auc_of(scores, truth):
    order = np.argsort(scores)
    ranks = np.empty(len(scores))
    ranks[order] = np.arange(len(scores))
    n1 = int((truth == 1).sum()); n0 = len(truth) - n1
    return (ranks[truth == 1].sum() - n1 * (n1 - 1) / 2) / (n1 * n0)

# ── A. flat doors ───────────────────────────────────────────────────
t0 = time.time()
i = Isaac()
i.crystallize_features(X[tr], y[tr], bins=32, compounds="off")
calib = i.net.get_meta("crystal", "calib")
classes = np.unique(y[tr])
lds = [i.net.get_meta(f"concept:{c}", "doors") for c in classes]

def door_scores(Xs, chunk=100_000):
    out = np.zeros((len(Xs), len(classes)))
    e = calib["edges"]
    for s0 in range(0, len(Xs), chunk):
        H = i.apply_lens(calib["lens"], Xs[s0:s0 + chunk])
        for j in range(H.shape[1]):
            ix = np.searchsorted(e[j], H[:, j])
            for k in range(len(classes)):
                out[s0:s0 + len(H), k] += lds[k][j][ix]
    return out

S = door_scores(X[te])
acc_a = (classes[np.argmax(S, 1)] == y[te]).mean()
auc_a = auc_of(S[:, 1] - S[:, 0], y[te])
print(f"A. flat doors:        {acc_a*100:.2f}%  AUC {auc_a:.4f}  "
      f"[{time.time()-t0:.0f}s]")

# ── B. weighted signals (the best lawful number) ────────────────────
t0 = time.time()
d = X.shape[1]; C = len(classes)

def signals(Xs, chunk=100_000):
    out = np.empty((len(Xs), d * C), dtype=np.float32)
    e = calib["edges"]
    for s0 in range(0, len(Xs), chunk):
        H = i.apply_lens(calib["lens"], Xs[s0:s0 + chunk])
        for j in range(d):
            ix = np.searchsorted(e[j], H[:, j])
            for k in range(C):
                out[s0:s0 + len(H), j * C + k] = lds[k][j][ix]
    return out

cut = 340_000                       # readout trains on a held slice
A = signals(X[cut:400_000])
mu, sd = A.mean(0), A.std(0) + 1e-9
A = (A - mu) / sd
Y1 = (y[cut:400_000][:, None] == classes[None, :]).astype(float)
r = np.random.default_rng(7)
W = r.normal(0, 0.01, (d * C, C)); b = np.zeros(C)
vW = np.zeros_like(W)
for _ in range(1200):
    Z = A @ W + b; Z -= Z.max(1, keepdims=True)
    P = np.exp(Z); P /= P.sum(1, keepdims=True)
    G = (P - Y1) / len(A)
    vW = 0.9 * vW - 0.3 * (A.T @ G + 1e-4 * W)
    W += vW; b -= 0.3 * G.sum(0)
St = (signals(X[te]) - mu) / sd
Z = St @ W + b
acc_b = (classes[np.argmax(Z, 1)] == y[te]).mean()
auc_b = auc_of(Z[:, 1] - Z[:, 0], y[te])
per_feat = np.abs(W).reshape(d, C, C).sum((1, 2))
top = np.argsort(-per_feat)[:6]
print(f"B. WEIGHTED SIGNALS:  {acc_b*100:.2f}%  AUC {auc_b:.4f}  "
      f"[{time.time()-t0:.0f}s]")
print("   extracted (the layer IS readable) — top-weighted sensors:")
for j in top:
    print(f"     {NAMES[j]:8s} weight {per_feat[j]:.1f}")

# ── C. the formula road (recorded; script: higgs_map.py) ────────────
print("\nC. the formula road (higgs_map.py, 2026-07-04): m_lv discovered"
      "\n   blind among 21 low-level channels as"
      "\n   +0.29*lep_pT*MET - 0.29*lep_pT*MET*cos(1.7*(lep_phi-MET_phi))"
      "\n   = pT*MET*(1 - cos(dphi)) — THE TRANSVERSE MASS, R2 0.856;"
      "\n   m_jj/m_jjj failed honestly (heavy tails, jet pairing).")

# ── D. the resonance, enumerated ────────────────────────────────────
t0 = time.time()
v = X[:, 25]                                        # m_bb channel
lo, hi = np.percentile(v, [0.2, 99.0])
bins = np.linspace(lo, hi, 80)
hb, _ = np.histogram(v[y == 0], bins=bins, density=True)
hs, _ = np.histogram(v[y == 1], bins=bins, density=True)
resid = hs - hb
centers = (bins[:-1] + bins[1:]) / 2
null_max = []
for _ in range(20):
    yp = rng.permutation(y)
    h0, _ = np.histogram(v[yp == 0], bins=bins, density=True)
    h1, _ = np.histogram(v[yp == 1], bins=bins, density=True)
    null_max.append(np.abs(h1 - h0).max())
gate = np.percentile(null_max, 95)
pos = resid > gate
w = np.where(pos, np.clip(resid, 0, None), 0.0)
peak = float((centers * w).sum() / w.sum())
width = float(np.sqrt(((centers - peak) ** 2 * w).sum() / w.sum()))
frac = float(w.sum() * (bins[1] - bins[0]))
print(f"\nD. the resonance (m_bb, null gate {gate:.4f}): peak at "
      f"{peak:.3f} (dataset units),\n   width {width:.3f}, holding "
      f"{frac*100:.1f}% of signal events  [{time.time()-t0:.0f}s]"
      f"\n   (units caveat: columns are normalized — GeV unrecoverable)")

print("\nnot matched: deep-net benchmark ~AUC 0.885 (Baldi 2014).")
