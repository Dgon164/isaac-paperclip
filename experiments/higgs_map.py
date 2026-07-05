# -*- coding: utf-8 -*-
"""HIGGS: THE CONTRAST AND THE MAP (owner, 2026-07-04: "it's got the
answer sheet. it can look at a vs b and find out what is different...
maybe we can see if it can create a physical map of the sensors").

Part 1  CONTRAST (labels used): per-channel signed signal-vs-background
        gaps, each past a label-permutation null, said in gated English.
Part 2  SENSOR MAP (labels NEVER used — blind): channel kinds (angles by
        flatness+bounded range, counters by discreteness), the dependence
        graph past a permutation null.
Part 3  THE WIRING (blind): discover() with each derived channel as the
        target of the low-level channels — which sensors is each computed
        from, and can the formula be SAID? m_jj^2 = 2 pT1 pT2
        (cosh(d_eta) - cos(d_phi)) is exactly in the atom class.

External grading (we hold the answer key; the mind never sees it):
true blocks = lepton{1,2,3} MET{4,5} jet1{6..9} jet2{10..13} jet3{14..17}
jet4{18..21}; derived 22..28 = m_jj, m_jjj, m_lv, m_jlv, m_bb, m_wbb,
m_wwbb.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

NAMES = {1: "lep_pT", 2: "lep_eta", 3: "lep_phi", 4: "MET", 5: "MET_phi",
         6: "j1_pT", 7: "j1_eta", 8: "j1_phi", 9: "j1_btag",
         10: "j2_pT", 11: "j2_eta", 12: "j2_phi", 13: "j2_btag",
         14: "j3_pT", 15: "j3_eta", 16: "j3_phi", 17: "j3_btag",
         18: "j4_pT", 19: "j4_eta", 20: "j4_phi", 21: "j4_btag",
         22: "m_jj", 23: "m_jjj", 24: "m_lv", 25: "m_jlv",
         26: "m_bb", 27: "m_wbb", 28: "m_wwbb"}

rng = np.random.default_rng(4)
D = np.load(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "HIGGS.npy"), mmap_mode="r")
sel = rng.choice(len(D), 400_000, replace=False)
sel.sort()
Xy = np.asarray(D[sel], dtype=np.float64)
y = Xy[:, 0].astype(int)
X = Xy[:, 1:]
print(f"HIGGS loaded: {X.shape[0]:,} rows sampled of {len(D):,}")

# ═══ Part 1: the contrast — what IS different between A and B ═══════
print("\n" + "=" * 70)
print("PART 1 — signal vs background, channel by channel (null-gated)")
print("=" * 70)
t0 = time.time()
nb = 40
gaps = np.zeros(28)
signs = np.zeros(28)
for j in range(28):
    lo, hi = np.percentile(X[:, j], [0.5, 99.5])
    e = np.linspace(lo, hi, nb + 1)[1:-1]
    ha = np.bincount(np.searchsorted(e, X[y == 1, j]), minlength=nb)
    hb = np.bincount(np.searchsorted(e, X[y == 0, j]), minlength=nb)
    ha = ha / ha.sum()
    hb = hb / hb.sum()
    gaps[j] = 0.5 * np.abs(ha - hb).sum()          # total variation
    signs[j] = X[y == 1, j].mean() - X[y == 0, j].mean()
# selection-corrected null: permuted labels, max gap over all channels
null_max = []
sub = rng.choice(len(y), 100_000, replace=False)
for _ in range(20):
    yp = rng.permutation(y[sub])
    m = 0.0
    for j in range(28):
        lo, hi = np.percentile(X[sub, j], [0.5, 99.5])
        e = np.linspace(lo, hi, nb + 1)[1:-1]
        ha = np.bincount(np.searchsorted(e, X[sub][yp == 1, j]),
                         minlength=nb)
        hb = np.bincount(np.searchsorted(e, X[sub][yp == 0, j]),
                         minlength=nb)
        m = max(m, 0.5 * np.abs(ha / ha.sum() - hb / hb.sum()).sum())
    null_max.append(m)
gate = np.percentile(null_max, 95)
order = np.argsort(-gaps)
print(f"gate (max-over-28-channels, permuted labels, 95th): {gate:.4f}")
n_sig = 0
for j in order:
    if gaps[j] <= gate:
        continue
    n_sig += 1
    if n_sig <= 12:
        d_ = "signal HIGHER" if signs[j] > 0 else "signal LOWER"
        print(f"  {NAMES[j+1]:8s} differs: TV {gaps[j]:.3f}  ({d_} "
              f"on average)")
same = [NAMES[j + 1] for j in range(28) if gaps[j] <= gate]
print(f"  ... {n_sig} channels differ beyond chance; "
      f"indistinguishable: {same if same else 'none'}   [{time.time()-t0:.0f}s]")

# ═══ Part 2: the blind sensor map — kinds and wiring ════════════════
print("\n" + "=" * 70)
print("PART 2 — the sensor map, labels never used")
print("=" * 70)
t0 = time.time()
U = X[rng.choice(len(X), 30_000, replace=False)]
kinds = {}
for j in range(28):
    col = U[:, j]
    nu = len(np.unique(np.round(col, 4)))
    if nu <= 5:
        kinds[j] = f"counter ({nu} levels)"
        continue
    h, _ = np.histogram(col, bins=24)
    h = h / h.sum()
    flat = h[h > 0].min() / h.max() if h.max() > 0 else 0
    bounded = (col.min() > -2.0) and (col.max() < 2.0) and \
              abs(col.min() + col.max()) < 0.2
    if bounded and flat > 0.5:
        kinds[j] = "angle (bounded, flat)"
    elif col.min() >= 0:
        kinds[j] = "magnitude (one-sided)"
    else:
        kinds[j] = "signed measure"
for j in range(28):
    print(f"  ch{j+1:2d} [{NAMES[j+1]:8s}] -> {kinds[j]}")

# dependence graph: binned MI past a permutation null
def mi(a, b, nb2=12):
    ea = np.percentile(a, np.linspace(0, 100, nb2 + 1)[1:-1])
    eb = np.percentile(b, np.linspace(0, 100, nb2 + 1)[1:-1])
    ia = np.searchsorted(ea, a)
    ib = np.searchsorted(eb, b)
    J = np.bincount(ia * nb2 + ib, minlength=nb2 * nb2).reshape(nb2, nb2)
    J = J / J.sum()
    pa = J.sum(1, keepdims=True)
    pb = J.sum(0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = J * np.log(J / (pa @ pb))
    return float(np.nansum(t))

null_mi = []
for _ in range(60):
    a = U[:, rng.integers(0, 28)]
    null_mi.append(mi(a, rng.permutation(U[:, rng.integers(0, 28)])))
mi_gate = np.percentile(null_mi, 99.9)
edges = []
for a in range(28):
    for b in range(a + 1, 28):
        m_ = mi(U[:, a], U[:, b])
        if m_ > mi_gate * 2:                       # strong wiring only
            edges.append((m_, a, b))
edges.sort(reverse=True)
print(f"\n  wiring (MI > 2x the 99.9th-pct null {mi_gate:.4f}); top 15:")
for m_, a, b in edges[:15]:
    print(f"    {NAMES[a+1]:8s} -- {NAMES[b+1]:8s}  MI {m_:.3f}")
print(f"  [{time.time()-t0:.0f}s]")

# ═══ Part 3: which sensors is each derived channel COMPUTED from ════
print("\n" + "=" * 70)
print("PART 3 — the wiring of the derived channels (blind discover())")
print("=" * 70)
low = X[:12_000, :21]
wiring = {}
for tgt in range(21, 28):
    t0 = time.time()
    name = f"higgs_ch{tgt+1}"
    i = Isaac()
    target = X[:12_000, tgt]
    if tgt == 21:                                   # m_jj: try the square
        target = target ** 2
        name += "_sq"
    res = i.discover(low, target, name=name)
    eq = res["equation"]
    used = sorted({int(t[1:]) for t in
                   __import__("re").findall(r"x\d+", eq)})
    wiring[tgt] = used
    print(f"  {NAMES[tgt+1]:7s}: {res['verdict']:10s} R2 "
          f"{res.get('r2', 0):.3f}  uses chans "
          f"{[NAMES[u+1] for u in used][:6]}  [{time.time()-t0:.0f}s]")
    print(f"           eq: {eq[:100]}")

print("\nEXTERNAL GRADE (the mind never saw this): m_jj should wire to "
      "jets; m_lv to lepton+MET; m_bb to b-tagged jets.")
