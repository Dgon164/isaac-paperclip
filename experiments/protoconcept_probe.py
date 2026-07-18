"""protoconcept_probe.py — THE PROTOCONCEPT DECODE, first light
(owner design 2026-07-17: "take each neuron, decode what its major
componants are like its activators and inhibitors, find the atomic
structures in the superposition sets, and then calculate what the
interactions are actually doing with information").

Planted truth first, per the standard:
  A1 THE INSTRUMENT — weights CONSTRUCTED as known sparse mixtures
     of planted atoms: the decoder must recover the atoms and every
     neuron's signed loadings; the SCRAMBLED control (each row's
     entries permuted) must show no atomic structure. The
     null-checked quantity is sparse-representability itself.
  A2 THE STOPWORD DIRECTION — a component added to EVERY neuron
     must be flagged identity-free (the excess/base-rate law's third
     domain: words, worlds, now weight space), while the true atoms
     still recover.
  A3 A TRAINED NET — the canonical superposition world: 6 sparse
     features forced into 3 neurons (autoencoder, tied weights,
     ReLU), trained by SGD from scratch. Read the WEIGHTS into
     per-neuron activator/inhibitor cards + a feature-interference
     map; then CONFIRM BEHAVIORALLY: the top interfering pairs
     predicted from weight geometry must be the top spurious
     responses measured on the running net. Weights propose,
     behavior confirms.

The solver here is an INSTRUMENT (hand-built translation, like the
pools): it points; every claim proves itself against planted truth
and the scrambled null. sklearn appears nowhere.
Run: PYTHONHASHSEED=0 python protoconcept_probe.py
"""
import os
import sys

import numpy as np

PASS, FAIL = 0, 0


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


# ── the decoder instrument: alternating sparse coding, numpy only ──
def _omp_row(row, D, s):
    """Orthogonal matching pursuit for one row: greedy by residual
    correlation, exact least squares on the growing support."""
    resid, sup = row.copy(), []
    for _ in range(s):
        corr = np.abs(D @ resid)
        corr[sup] = -1.0
        sup.append(int(np.argmax(corr)))
        A = D[sup].T
        coef, *_ = np.linalg.lstsq(A, row, rcond=None)
        resid = row - A @ coef
    c = np.zeros(len(D))
    c[sup] = coef
    return c


def sparse_decode(Wrows, k, s, iters=60, restarts=8, seed=0):
    """Rows -> (atoms D [k x n], codes C [rows x k]), each row <= s
    atoms. Multi-restart alternation (OMP coding + per-atom least
    squares), best residual kept — single-start OMP locked into a
    worse minimum than greedy projection on the planted world
    (0.614 vs 0.906; first-light lesson, kept). Operating floor,
    measured and said: the decoder wants >= ~2 dozen users per atom;
    a starved layer is under-evidenced, not decodable-by-magic."""
    R = np.asarray(Wrows, float)
    _, _, Vt = np.linalg.svd(R, full_matrices=False)
    B = Vt[:k]                                # the row subspace
    rng = np.random.default_rng(seed)
    best = None
    for t in range(restarts):
        if t == 0:
            D = B.copy()
        else:                                 # random rotation of
            Q, _ = np.linalg.qr(               # the same subspace
                rng.standard_normal((k, k)))
            D = Q @ B
        C = np.zeros((len(R), k))
        for _ in range(iters):
            C = np.array([_omp_row(r, D, s) for r in R])
            for j in range(k):
                users = np.abs(C[:, j]) > 1e-9
                if not users.any():
                    continue
                resid = R[users] - C[users] @ D \
                    + np.outer(C[users, j], D[j])
                d = C[users, j] @ resid
                n = np.linalg.norm(d)
                if n > 1e-12:
                    D[j] = d / n
        resid = float(np.mean(
            np.linalg.norm(R - C @ D, axis=1)
            / np.maximum(np.linalg.norm(R, axis=1), 1e-12)))
        if best is None or resid < best[2]:
            best = (D, C, resid)
    return best


def match_atoms(D, truth):
    """Greedy |cos| matching decoded atoms -> planted atoms."""
    sims = np.abs(D @ truth.T)
    used_d, used_t, pairs = set(), set(), []
    for _ in range(min(D.shape[0], truth.shape[0])):
        best = None
        for i in range(D.shape[0]):
            if i in used_d:
                continue
            for j in range(truth.shape[0]):
                if j in used_t:
                    continue
                if best is None or sims[i, j] > best[0]:
                    best = (sims[i, j], i, j)
        used_d.add(best[1])
        used_t.add(best[2])
        pairs.append(best)
    return pairs


def main():
    rng = np.random.default_rng(7)
    print("=" * 70)
    print("PROTOCONCEPT PROBE — unmix first, then read")
    print("=" * 70)

    # ── A1: the instrument on constructed weights ──
    # m=96 neurons: ~32 users/atom, inside the decoder's measured
    # operating range (24 neurons = 8/atom starved it — said, kept)
    n, k, s, m = 20, 6, 2, 96
    atoms = rng.standard_normal((k, n))
    atoms /= np.linalg.norm(atoms, axis=1, keepdims=True)
    loads = np.zeros((m, k))
    for i in range(m):
        pick = rng.choice(k, s, replace=False)
        loads[i, pick] = (rng.uniform(0.5, 1.5, s)
                          * rng.choice([-1, 1], s))
    W = loads @ atoms + 0.02 * rng.standard_normal((m, n))

    D, C, resid = sparse_decode(W, k, s)
    pairs = match_atoms(D, atoms)
    cos_min = min(p[0] for p in pairs)
    # neuron cards: does the decoded support+sign match the plant?
    right = 0
    perm = {p[1]: p[2] for p in pairs}          # decoded j -> true
    signflip = {p[1]: np.sign(D[p[1]] @ atoms[p[2]]) for p in pairs}
    for i in range(m):
        sup_d = set(np.flatnonzero(np.abs(C[i]) > 0.15))
        sup_t = set(np.flatnonzero(np.abs(loads[i]) > 0))
        if {perm[j] for j in sup_d} == sup_t and all(
                np.sign(C[i, j] * signflip[j])
                == np.sign(loads[i, perm[j]]) for j in sup_d):
            right += 1
    check(f"A1 atoms recovered from constructed weights "
          f"(min |cos| {cos_min:.3f})", cos_min >= 0.95,
          f"resid {resid:.3f}")
    check(f"A1b neuron cards: {right}/{m} supports+signs exact "
          f"(>=95% bar; misses counted, never hidden)",
          right >= 0.95 * m)

    Ws = np.array([rng.permutation(row) for row in W])
    _, _, resid_s = sparse_decode(Ws, k, s)
    check("A1c SCRAMBLED control: sparse structure GONE "
          f"(resid {resid:.3f} -> {resid_s:.3f})",
          resid_s > 4 * max(resid, 1e-3),
          "atomic structure is not free — it must be in the rows")

    # ── A2: the stopword direction = THE COMMON MODE ──
    # What every neuron carries is the mean row; the base-rate law
    # (words: 'the'; worlds: base; now weight space): subtract what
    # everyone shares BEFORE asking what distinguishes. A sign-flip
    # permutation null decides whether a common mode exists at all.
    # (First try hunted the stopword as a dictionary atom — the
    # alternation smeared it across atoms; wrong-kept.)
    def common_mode(R, n_null=200):
        gbar = R.mean(0)
        obs = float(np.linalg.norm(gbar))
        crng = np.random.default_rng(17)
        null = [float(np.linalg.norm(
            (R * crng.choice([-1.0, 1.0], (len(R), 1))).mean(0)))
            for _ in range(n_null)]
        return gbar, obs, float(np.quantile(null, 0.99))

    g = rng.standard_normal(n)
    g /= np.linalg.norm(g)
    W2 = W + 0.7 * g                            # EVERY neuron carries g
    _, obs0, thr0 = common_mode(W)              # control: no g planted
    gbar, obs2, thr2 = common_mode(W2)
    aligned = abs(gbar / max(np.linalg.norm(gbar), 1e-12) @ g)
    check("A2 common mode: QUIET where none planted, FLAGGED where "
          "every neuron carries it, direction named",
          obs0 <= thr0 and obs2 > thr2 and aligned > 0.95,
          f"control {obs0:.3f}<=thr {thr0:.3f}; planted {obs2:.3f}>"
          f"thr {thr2:.3f}; |cos to g| {aligned:.3f}")
    D2, C2, _ = sparse_decode(W2 - gbar, k, s)  # base rate removed
    pairs2 = match_atoms(D2, atoms)
    cos2 = min(p[0] for p in pairs2)
    check(f"A2b true atoms recover once the base rate is removed "
          f"(min |cos| {cos2:.3f})", cos2 >= 0.95)

    # ── A3: a TRAINED net — 6 features forced into 3 neurons ──
    kf, dh = 6, 3
    Wt = 0.1 * rng.standard_normal((dh, kf))
    b = np.zeros(kf)
    lr = 0.03
    for step in range(6000):
        X = ((rng.random((64, kf)) < 0.15)
             * rng.random((64, kf)))            # sparse features
        H = X @ Wt.T                            # (64, dh)
        A = H @ Wt + b                          # tied weights
        Xh = np.maximum(A, 0.0)
        G = 2.0 * (Xh - X) * (A > 0) / len(X)
        gW = H.T @ G + (G @ Wt.T).T @ X         # both paths (tied)
        b -= lr * G.sum(0)
        Wt -= lr * gW
    # per-neuron activator/inhibitor cards, read from the weights
    print("  A3 neuron cards (weights only):")
    superposed = 0
    for i in range(dh):
        acts = [int(j) for j in np.flatnonzero(Wt[i] > 0.35)]
        inhs = [int(j) for j in np.flatnonzero(Wt[i] < -0.35)]
        superposed += (len(acts) + len(inhs)) >= 2
        print(f"    neuron {i}: activators {acts}, "
              f"inhibitors {inhs}")
    check("A3 superposition is REAL in the trained net (neurons "
          "carry >=2 features)", superposed >= 2,
          f"{superposed}/{dh} neurons superposed")
    # SIGNED interference map from WEIGHTS: cos between feature
    # embeddings. First-light lesson (wrong-kept): |cos| predicted
    # nothing, because antipodal features (cos < 0) read out as
    # ZERO spurious response — the ReLU kills them. The sign IS the
    # information story: +cos = confusable pair (spurious
    # co-activation), -cos = MUTUAL INHIBITION — the net's packing
    # trick, tolerated because sparse features rarely co-occur.
    E = Wt.T                                    # feature j -> column
    en = E / np.maximum(np.linalg.norm(E, axis=1, keepdims=True),
                        1e-12)
    I = en @ en.T
    np.fill_diagonal(I, 0.0)
    base = np.maximum(b, 0.0)                   # nothing-active read
    spur = np.zeros((kf, kf))                   # co-activation
    supp = np.zeros((kf, kf))                   # suppression
    for a in range(kf):
        x = np.zeros(kf)
        x[a] = 1.0
        xh = np.maximum((x @ Wt.T) @ Wt + b, 0.0)
        for c in range(kf):
            if c != a:
                spur[a, c] = xh[c]
                supp[a, c] = base[c] - xh[c]
    pairs_all = [(a, c) for a in range(kf) for c in range(a + 1, kf)]
    pred_pos = sorted(pairs_all, key=lambda p: -I[p])[:2]
    pred_neg = sorted(pairs_all, key=lambda p: I[p])[:2]
    meas_pos = sorted(pairs_all,
                      key=lambda p: -max(spur[p], spur[p[::-1]]))[:2]
    meas_neg = sorted(pairs_all,
                      key=lambda p: -max(supp[p], supp[p[::-1]]))[:2]
    hits = (len(set(pred_pos) & set(meas_pos))
            + len(set(pred_neg) & set(meas_neg)))
    check("A3b SIGNED interference confirmed on the running net: "
          f"+cos pairs co-activate, -cos pairs suppress ({hits}/4)",
          hits >= 3,
          f"+pred {pred_pos} vs +meas {meas_pos}; "
          f"-pred {pred_neg} vs -meas {meas_neg}")
    recon = []
    for a in range(kf):
        x = np.zeros(kf)
        x[a] = 0.8
        xh = np.maximum((x @ Wt.T) @ Wt + b, 0.0)
        recon.append(abs(xh[a] - 0.8) / 0.8)
    print(f"    reconstruction rel-err per feature: "
          f"{[round(r, 2) for r in recon]}")

    print()
    print(f"PROTOCONCEPT PROBE: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
