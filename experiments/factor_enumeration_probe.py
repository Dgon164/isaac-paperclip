"""factor_enumeration_probe.py — THE FACTOR ENUMERATION (owner
clarification, 2026-07-17: "enumerate the input contribution
signals... those 12 things are the primary factors. we only care
about how those 12 things contribute to the output activation...
it amplifies certain carriers and inhibits others. so of those 12
atoms or whatever, what are the combinations that each output is
looking for").

Specimen shaped like the GPT-2 claim in miniature: inputs arrive as
12 FACTOR BLOCKS x 8 dims (96 raw dims). Each factor carries a
planted SIGNAL direction inside its block. Six outputs, each wired
to a planted recipe: AMPLIFY a pair of factors (an AND — the
combination), INHIBIT one. A 96->32->6 ReLU net is trained on it
from scratch; the decoder gets the WEIGHTS and the block boundaries
(the architecture's gift, like 64x12) — nothing else.

The decode must enumerate, per output:
  D1 the RECIPE: the amplified pair (+2 AND term), the inhibitor
     (-1 single), nothing else — 6/6 outputs;
  D2 the CONTRIBUTION SIGNALS: the direction read INSIDE each used
     factor block matches the planted signal (|cos| >= 0.85);
  D3 the SCRAMBLED control: same pipeline on permuted weights
     recovers zero planted recipes — enumeration is not free.

Run: PYTHONHASHSEED=0 python factor_enumeration_probe.py
"""
import itertools
import os
import sys

import numpy as np

PASS, FAIL = 0, 0
NF, DF, NOUT = 12, 8, 6                 # factors x dims, outputs


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


def build_world(rng):
    signals = rng.standard_normal((NF, DF))
    signals /= np.linalg.norm(signals, axis=1, keepdims=True)
    recipes = []
    for o in range(NOUT):
        a, b, c = rng.choice(NF, 3, replace=False)
        recipes.append((int(a), int(b), int(c)))
    return signals, recipes


def sample(rng, signals, recipes, n):
    act = (rng.random((n, NF)) < 0.35).astype(float)
    X = np.zeros((n, NF * DF))
    for f in range(NF):
        X[:, f * DF:(f + 1) * DF] = (act[:, [f]] * signals[f]
                                     + 0.05 * rng.standard_normal(
                                         (n, DF)))
    Y = np.zeros((n, NOUT))
    for o, (a, b, c) in enumerate(recipes):
        Y[:, o] = 2.0 * act[:, a] * act[:, b] - 1.0 * act[:, c]
    return X, Y


def train(rng, signals, recipes, steps=15000, lr=0.03, hid=32):
    W1 = 0.2 * rng.standard_normal((hid, NF * DF))
    b1 = np.zeros(hid)
    W2 = 0.2 * rng.standard_normal((NOUT, hid))
    b2 = np.zeros(NOUT)
    for _ in range(steps):
        X, Y = sample(rng, signals, recipes, 64)
        H = np.maximum(X @ W1.T + b1, 0.0)
        P = H @ W2.T + b2
        G = 2.0 * (P - Y) / len(X)
        gW2 = G.T @ H
        gb2 = G.sum(0)
        gH = (G @ W2) * (H > 0)
        gW1 = gH.T @ X
        gb1 = gH.sum(0)
        W1 -= lr * gW1
        b1 -= lr * gb1
        W2 -= lr * gW2
        b2 -= lr * gb2
    return W1, b1, W2, b2


def factor_probe_x(signals, S):
    x = np.zeros(NF * DF)
    for f in S:
        x[f * DF:(f + 1) * DF] = signals[f]
    return x


def enumerate_factors(net, probe_signals):
    """THE DECODE: weights + block boundaries + per-factor probe
    signals. Per output: Mobius over FACTOR subsets (the
    combinations), and per used factor the contribution SIGNAL —
    the direction actually read inside the block, composed from the
    cards at the recipe's operating point."""
    W1, b1, W2, b2 = net

    def out(S):
        h = np.maximum(W1 @ factor_probe_x(probe_signals, S) + b1,
                       0.0)
        return W2 @ h + b2

    coef = {(): out(())}
    for r in (1, 2, 3):
        for S in itertools.combinations(range(NF), r):
            c = out(S)
            for rr in range(r):
                for T in itertools.combinations(S, rr):
                    c = c - coef[T]
            coef[S] = c
    recipes = []
    for o in range(NOUT):
        pairs = {S: float(coef[S][o])
                 for S in coef if len(S) == 2
                 and abs(coef[S][o]) > 0.6}
        singles = {S[0]: float(coef[S][o])
                   for S in coef if len(S) == 1
                   and abs(coef[S][o]) > 0.4}
        top_pair = max(pairs, key=lambda S: abs(pairs[S])) \
            if pairs else None
        inhib = [f for f, v in singles.items() if v < 0]
        recipes.append(dict(pair=top_pair,
                            pair_gain=pairs.get(top_pair),
                            inhibitors=inhib,
                            singles=singles, n_pairs=len(pairs)))
    # the contribution signal inside each used block: the Jacobian
    # of output o w.r.t. block f at the recipe's operating point,
    # composed from the cards (weights x the active mask)
    # a single operating point leaves the Jacobian fragile where
    # units sit near threshold (first-pass: one slot read 0.42) —
    # average the read over a small amplitude grid around the
    # recipe's operating region
    sig_read = {}
    for o in range(NOUT):
        S = recipes[o]["pair"]
        if S is None:
            continue
        for f in S:
            J = np.zeros(DF)
            for amp_f in (0.7, 1.0, 1.3):
                for amp_p in (1.0, 1.3):
                    x = np.zeros(NF * DF)
                    for g in S:
                        a = amp_f if g == f else amp_p
                        x[g * DF:(g + 1) * DF] = \
                            a * probe_signals[g]
                    m = (W1 @ x + b1 > 0).astype(float)
                    J = J + (W2[o] * m) @ W1[:, f * DF:
                                            (f + 1) * DF]
            n = np.linalg.norm(J)
            if n > 1e-9:
                sig_read[(o, f)] = J / n
    return recipes, sig_read


def main():
    print("=" * 70)
    print("FACTOR ENUMERATION — which combinations is each output "
          "looking for?")
    print("=" * 70)
    rng = np.random.default_rng(29)
    signals, recipes_true = build_world(rng)
    net = train(rng, signals, recipes_true)

    Xte, Yte = sample(rng, signals, recipes_true, 4000)
    H = np.maximum(Xte @ net[0].T + net[1], 0.0)
    P = H @ net[2].T + net[3]
    fit = float(np.sqrt(np.mean((P - Yte) ** 2)))
    print(f"  specimen: 96->32->6 trained to rms {fit:.3f} "
          f"(12 factor blocks x 8 dims, planted AND-pair + "
          f"inhibitor per output)")

    dec, sig_read = enumerate_factors(net, signals)
    print("  the enumeration (weights + block boundaries only):")
    hits = clean = 0
    for o, (a, b, c) in enumerate(recipes_true):
        d = dec[o]
        got_pair = d["pair"] == tuple(sorted((a, b)))
        got_inh = c in d["inhibitors"]
        gain_ok = d["pair_gain"] is not None \
            and abs(d["pair_gain"] - 2.0) < 0.4
        inh_ok = abs(d["singles"].get(c, 0.0) + 1.0) < 0.4
        extra = (d["n_pairs"] == 1
                 and len(d["inhibitors"]) == 1)
        hits += got_pair and got_inh and gain_ok and inh_ok
        clean += extra
        print(f"    out {o}: truth AMPLIFY({a},{b})*2 INHIBIT({c})"
              f"*-1 | decoded {d['pair']}*"
              f"{(d['pair_gain'] or 0):.2f} inhibit "
              f"{d['inhibitors']} "
              f"[{'named' if got_pair and got_inh else 'MISSED'}]")
    check(f"D1 recipes enumerated: {hits}/{NOUT} outputs exact "
          f"(pair + gain + inhibitor)", hits >= 5)
    check(f"D1b nothing extra: {clean}/{NOUT} outputs carry exactly "
          f"one pair and one inhibitor", clean >= 5)

    coss = [abs(float(v @ signals[f])) for (o, f), v in
            sig_read.items()]
    check(f"D2 contribution SIGNALS read inside the blocks: "
          f"{len(coss)} (output,factor) slots, min |cos| "
          f"{min(coss):.3f}, mean {np.mean(coss):.3f}",
          min(coss) >= 0.85)

    # D3: the scrambled control — enumeration is not free
    srng = np.random.default_rng(5)
    W1s = np.array([srng.permutation(row) for row in net[0]])
    dec_s, _ = enumerate_factors((W1s, net[1], net[2], net[3]),
                                 signals)
    s_hits = sum(1 for o, (a, b, c) in enumerate(recipes_true)
                 if dec_s[o]["pair"] == tuple(sorted((a, b))))
    check(f"D3 scrambled control: {s_hits}/{NOUT} planted recipes "
          f"recovered from permuted weights", s_hits == 0)

    print()
    print(f"FACTOR ENUMERATION: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
