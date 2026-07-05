# -*- coding: utf-8 -*-
"""SINGLE-LAYER STUDY (owner, 2026-07-05): "how information from multiple
sources is compared to total activation and output decisions... what is
the highest trained percentage with just a single neural net, and can one
be trained on the node structure outputs directly?"

Same data as the fusion battery (200/class train, 500 test, seed 8).
ALL numbers complete numbers. The trained combiners are MEASUREMENTS
(witnesses/quarantine tier) — the printable-weights softmax over named
channel scores is the boundary case: a linear read-out, inspectable.

S1  softmax layer on raw pixels        (no hidden layer)
S2  one-hidden-layer net on raw pixels (the other reading of 'single')
S3  softmax layer on THE NODE STRUCTURE OUTPUTS (5 channels x 10 classes
    = 50 named inputs) vs the hand-calibrated fusion
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
tr = np.concatenate([np.where(y[:40000] == c)[0][:200] for c in range(10)])
te = rng.choice(np.where(np.arange(len(y)) > 40000)[0], 500, replace=False)


def softmax_train(A, Y1, hidden=0, steps=1200, lr=0.1, seed=7):
    """numpy softmax (hidden=0) or 1-hidden-tanh net. Returns predict fn."""
    r = np.random.default_rng(seed)
    n_out = Y1.shape[1]
    if hidden == 0:
        W = r.normal(0, 0.01, (A.shape[1], n_out)); b = np.zeros(n_out)
        vW = np.zeros_like(W)
        for _ in range(steps):
            Z = A @ W + b
            Z -= Z.max(1, keepdims=True)
            P = np.exp(Z); P /= P.sum(1, keepdims=True)
            G = (P - Y1) / len(A)
            vW = 0.9 * vW - lr * (A.T @ G + 1e-4 * W)
            W += vW; b -= lr * G.sum(0)
        return lambda B: np.argmax(B @ W + b, 1), W
    W1 = r.normal(0, 0.05, (A.shape[1], hidden)); b1 = np.zeros(hidden)
    W2 = r.normal(0, 0.05, (hidden, n_out)); b2 = np.zeros(n_out)
    v1 = np.zeros_like(W1); v2 = np.zeros_like(W2)
    for _ in range(steps):
        H = np.tanh(A @ W1 + b1)
        Z = H @ W2 + b2
        Z -= Z.max(1, keepdims=True)
        P = np.exp(Z); P /= P.sum(1, keepdims=True)
        G = (P - Y1) / len(A)
        gW2 = H.T @ G + 1e-4 * W2
        GH = (G @ W2.T) * (1 - H ** 2)
        gW1 = A.T @ GH + 1e-4 * W1
        v2 = 0.9 * v2 - lr * gW2; W2 += v2; b2 -= lr * G.sum(0)
        v1 = 0.9 * v1 - lr * gW1; W1 += v1; b1 -= lr * GH.sum(0)
    return lambda B: np.argmax(np.tanh(B @ W1 + b1) @ W2 + b2, 1), None


Ytr = y[tr]
Y1 = (Ytr[:, None] == np.arange(10)[None, :]).astype(float)
Ptr = X[tr].reshape(len(tr), -1) / 255.0
Pte = X[te].reshape(len(te), -1) / 255.0

print("S1 — softmax layer on raw pixels (784 -> 10, nothing hidden)")
t0 = time.time()
pred, _ = softmax_train(Ptr, Y1, hidden=0, steps=1500, lr=0.5)
acc1 = (pred(Pte) == y[te]).mean()
print(f"    complete: {acc1*100:.1f}%   [{time.time()-t0:.0f}s]")

print("S2 — one hidden layer (784 -> 128 -> 10) on raw pixels")
t0 = time.time()
pred, _ = softmax_train(Ptr, Y1, hidden=128, steps=1500, lr=0.3)
acc2 = (pred(Pte) == y[te]).mean()
print(f"    complete: {acc2*100:.1f}%   [{time.time()-t0:.0f}s]")

print("S3 — softmax layer on the NODE STRUCTURE OUTPUTS")
i = Isaac()
i.learn_glyphs(X[tr], y[tr])
classes = list(i.net.get_meta("crystal", "glyph_classes"))
CH = ["bones", "density", "dynamics", "exemplar", "topology"]

def channel_vec(img):
    _, posts = i.recognize_glyph(img)
    v = []
    for k in CH:
        p = posts.get(k)
        v.append(p if p is not None else np.full(10, 0.1))
    return np.concatenate(v)

# combiner train set: glyphs OUTSIDE the exemplar store (no self-match bias)
comb_idx = np.concatenate([np.where(y[:40000] == c)[0][60:200]
                           for c in range(10)])
t0 = time.time()
Atr = np.array([channel_vec(X[ix]) for ix in comb_idx])
Ate = np.array([channel_vec(X[ix]) for ix in te])
Yc = (y[comb_idx][:, None] == np.arange(10)[None, :]).astype(float)
pred, W = softmax_train(Atr, Yc, hidden=0, steps=2000, lr=0.5)
acc3 = (pred(Ate) == y[te]).mean()
# the hand-calibrated fusion on the same test set, for the comparison
fused = sum(i.recognize_glyph(X[ix])[0] == y[ix] for ix in te) / len(te)
print(f"    complete: {acc3*100:.1f}%   (hand-calibrated fusion on the "
      f"same test: {fused*100:.1f}%)   [{time.time()-t0:.0f}s]")
print("    the trained layer's weights are READABLE — total |weight| "
      "per channel:")
for kk, k in enumerate(CH):
    print(f"      {k:9s} {np.abs(W[kk*10:(kk+1)*10]).sum():6.1f}")

print("\nsummary (complete numbers, 500-digit test):")
print(f"  softmax on pixels        {acc1*100:5.1f}%")
print(f"  1-hidden-layer on pixels {acc2*100:5.1f}%")
print(f"  softmax on node outputs  {acc3*100:5.1f}%")
print(f"  hand-calibrated fusion   {fused*100:5.1f}%")
