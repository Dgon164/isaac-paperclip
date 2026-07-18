"""netdecode_higgs.py — P3 FIRST BITE: decode a real-physics net
from its weights (owner: "lets find out how much we can find out").

The specimen: a 28->32->1 ReLU net trained here on HIGGS (torch,
GPU) — a modest single-hidden-layer net, NOT the 0.885 deep monster
(that stays the segment's prize). The inputs are NAMED physics
quantities, so meaning grounds at the boundary and propagates.

PREDICTIONS FILED BEFORE THE DECODE RUNS (printed first; judged
CONFIRMED/FALSIFIED after — findings either way, the probe does not
fail on a falsified physics prediction):
  HP1 the decode will rank the 7 ENGINEERED mass features (m_jj..
      m_wwbb) above the 21 low-level detector features in carried
      weight share — the physics claim that engineered invariants
      are what shallow nets lean on.
  HP2 the 7 phi angles carry ~nothing (rotational symmetry): all
      land in the bottom half of the ranking.

MACHINERY GATES (these do fail the probe):
  H1 the specimen is worth decoding (test AUC >= 0.78);
  H2 the decode's ranking is BEHAVIORALLY REAL: ablating its top-3
     named features costs >= 2x the AUC drop of its bottom-3 —
     the receipt that the reading reflects the computation.

Run: PYTHONHASHSEED=0 python netdecode_higgs.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["l_pT", "l_eta", "l_phi", "MET", "MET_phi",
         "j1_pT", "j1_eta", "j1_phi", "j1_btag",
         "j2_pT", "j2_eta", "j2_phi", "j2_btag",
         "j3_pT", "j3_eta", "j3_phi", "j3_btag",
         "j4_pT", "j4_eta", "j4_phi", "j4_btag",
         "m_jj", "m_jjj", "m_lv", "m_jlv", "m_bb", "m_wbb",
         "m_wwbb"]
ENGINEERED = set(range(21, 28))
PHI = {j for j, n in enumerate(NAMES) if n.endswith("phi")}

PASS, FAIL = 0, 0


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


def auc_of(scores, truth):
    order = np.argsort(scores)
    ranks = np.empty(len(scores))
    ranks[order] = np.arange(len(scores))
    n1 = int((truth == 1).sum())
    n0 = len(truth) - n1
    return float((ranks[truth == 1].sum()
                  - n1 * (n1 - 1) / 2) / (n1 * n0))


def main():
    import torch
    print("=" * 70)
    print("NET-DECODE, REAL PHYSICS — first bite of the HIGGS net")
    print("=" * 70)
    print("  FILED FIRST: HP1 engineered masses outrank low-level; "
          "HP2 phi angles land bottom-half.")

    rng = np.random.default_rng(4)
    D = np.load(os.path.join(os.path.dirname(HERE), "data",
                             "HIGGS.npy"), mmap_mode="r")
    sel = np.sort(rng.choice(len(D), 1_000_000, replace=False))
    Xy = np.asarray(D[sel], dtype=np.float32)
    y = Xy[:, 0]
    X = Xy[:, 1:]
    mu, sd = X[:800_000].mean(0), X[:800_000].std(0) + 1e-9
    X = (X - mu) / sd
    torch.manual_seed(0)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    net = torch.nn.Sequential(
        torch.nn.Linear(28, 32), torch.nn.ReLU(),
        torch.nn.Linear(32, 1)).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    lossf = torch.nn.BCEWithLogitsLoss()
    Xtr = torch.tensor(X[:800_000], device=dev)
    ytr = torch.tensor(y[:800_000], device=dev)
    for step in range(4000):
        idx = torch.randint(0, len(Xtr), (4096,), device=dev)
        opt.zero_grad()
        out = net(Xtr[idx]).squeeze(1)
        loss = lossf(out, ytr[idx])
        loss.backward()
        opt.step()
    with torch.no_grad():
        sc = net(torch.tensor(X[800_000:], device=dev)) \
            .squeeze(1).cpu().numpy()
    auc = auc_of(sc, y[800_000:])
    check(f"H1 specimen worth decoding: test AUC {auc:.4f} on 200k "
          f"fresh rows", auc >= 0.78,
          "(the 0.885 deep monster remains the prize)")

    # ── THE DECODE: weights only ──
    W1 = net[0].weight.detach().cpu().numpy()
    w2 = net[2].weight.detach().cpu().numpy().ravel()
    carried = (np.abs(W1) * np.abs(w2)[:, None]).sum(0)
    order = np.argsort(-carried)
    share = carried / carried.sum()
    print("  the decode's ranking (readout-weighted carried "
          "weight, from W ALONE):")
    for r, j in enumerate(order[:10]):
        print(f"    {r + 1:2d}. {NAMES[j]:8s} {share[j]:.3f}"
              f"{'  [engineered]' if j in ENGINEERED else ''}")
    eng_share = share[list(ENGINEERED)].mean()
    low_share = share[[j for j in range(28)
                       if j not in ENGINEERED]].mean()
    hp1 = eng_share > low_share
    print(f"  HP1 {'CONFIRMED' if hp1 else 'FALSIFIED'}: mean share "
          f"engineered {eng_share:.4f} vs low-level {low_share:.4f}"
          f" ({eng_share / max(low_share, 1e-9):.1f}x)")
    ranks = {j: int(np.where(order == j)[0][0]) for j in range(28)}
    phi_bottom = sum(1 for j in PHI if ranks[j] >= 14)
    hp2 = phi_bottom >= 6
    print(f"  HP2 {'CONFIRMED' if hp2 else 'FALSIFIED'}: {phi_bottom}"
          f"/7 phi angles in the bottom half "
          f"(ranks {sorted(ranks[j] + 1 for j in PHI)})")

    # ── H2: the ranking must be behaviorally real (ablation) ──
    def auc_ablated(cols):
        Wa = W1.copy()
        Wa[:, cols] = 0.0
        H = np.maximum(X[800_000:] @ Wa.T
                       + net[0].bias.detach().cpu().numpy(), 0.0)
        s = H @ w2 + float(net[2].bias.detach().cpu().numpy()[0])
        return auc_of(s, y[800_000:])
    top3, bot3 = list(order[:3]), list(order[-3:])
    d_top = auc - auc_ablated(top3)
    d_bot = auc - auc_ablated(bot3)
    check(f"H2 the reading is behaviorally REAL: ablating decode's "
          f"top-3 ({', '.join(NAMES[j] for j in top3)}) costs "
          f"{d_top:.4f} AUC vs bottom-3 "
          f"({', '.join(NAMES[j] for j in bot3)}) {d_bot:.4f}",
          d_top >= 2 * max(d_bot, 1e-4),
          f"ratio {d_top / max(d_bot, 1e-4):.0f}x")

    # informational: does a real first layer carry sparse atomic
    # structure? (reported, not gated — a finding either way)
    from protoconcept_probe import sparse_decode
    _, _, r1 = sparse_decode(W1, 8, 3, restarts=3, seed=1)
    Ws = np.array([np.random.default_rng(9).permutation(row)
                   for row in W1])
    _, _, rs = sparse_decode(Ws, 8, 3, restarts=2, seed=2)
    print(f"  [finding] first-layer sparse structure: resid {r1:.3f}"
          f" vs scrambled {rs:.3f} (gain {rs / max(r1, 1e-9):.2f}x)"
          f" — a REAL net's layer, reported as measured")

    print()
    print(f"HIGGS FIRST BITE: {PASS}/{PASS + FAIL} machinery gates "
          f"passed; HP1 {'CONFIRMED' if hp1 else 'FALSIFIED'}, "
          f"HP2 {'CONFIRMED' if hp2 else 'FALSIFIED'}")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    main()
