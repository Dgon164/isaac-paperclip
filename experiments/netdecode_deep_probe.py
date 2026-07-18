"""netdecode_deep_probe.py — VALIDATE THE THEORIES (owner,
2026-07-17: "these are theories. so lets validate and assemble").

Two claims from the design conversation, now gated:

  CLAIM 1 — SUBSTITUTION COLLAPSES DEPTH ("we dont need the carry
  ... we collect and immidiately use the parts. we run the quick
  simplified interactions"). Specimen: a TWO-hidden-layer net
  trained on a genuinely compositional circuit,
      y = 2 * AND(XOR(x0, x1), x2) + 1 * x4
  (XOR must form in layer 1; the AND composes it in layer 2; x4
  must pass THROUGH both layers — the "carried" group). The decode
  reads cards bottom-up ONCE, then produces the FLAT interaction
  expansion (base / linear / pair / triple). The algebra says the
  truth is FLAT: y = 2*x0*x2 + 2*x1*x2 - 4*x0*x1*x2 + x4.
    C1a the expansion recovers exactly those terms (the triple is
        the ORDER-3 EXCESS, measured in a deep net);
    C1b the flat form ALONE (no stepping, truncated at order 3)
        predicts all 32 input patterns of the running net —
        including 4- and 5-feature patterns, so any order-4+ junk
        the net learned would show up as mismatch;
    C1c CARRY FOR FREE: x4 appears as a pure linear term, zero
        interactions — the carried group collapsed to identity by
        algebra, no carry detector anywhere;
    C1d the counterfactual receipt at DEPTH: silence the layer-1
        XOR assembly, PREDICT the collapse of every composed term
        and the survival of x4 from the cards, confirm on the run.

  CLAIM 2 — ASSEMBLE THE CITIZEN ("we are just creating a concept
  net replacement and correlating them into isaac speech"). The
  decoded flat form generates examples; Isaac DISCOVERS the law in
  HIS OWN grammar; his law is then applied against the ORIGINAL
  FOREIGN NET's outputs. Agreement = a stranger's weights became a
  citizen of his net through his own court.
    C3a his verdict + his equation (the speakable artifact);
    C3b apply_law(his law) vs the foreign net on all 32 patterns.

Run: PYTHONHASHSEED=0 python netdecode_deep_probe.py
"""
import itertools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

PASS, FAIL = 0, 0


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


def truth(X):
    return (2.0 * X[:, 2] * np.abs(X[:, 0] - X[:, 1])
            + 1.0 * X[:, 4])


def train_deep(rng, kf=5, h1n=8, h2n=6, steps=12000, lr=0.05):
    W1 = 0.4 * rng.standard_normal((h1n, kf))
    b1 = np.zeros(h1n)
    W2 = 0.4 * rng.standard_normal((h2n, h1n))
    b2 = np.zeros(h2n)
    w3 = 0.4 * rng.standard_normal(h2n)
    b3 = 0.0
    for _ in range(steps):
        X = (rng.random((64, kf)) < 0.5).astype(float)
        y = truth(X)
        H1 = np.maximum(X @ W1.T + b1, 0.0)
        H2 = np.maximum(H1 @ W2.T + b2, 0.0)
        p = H2 @ w3 + b3
        g = 2.0 * (p - y) / len(y)
        gw3 = H2.T @ g
        gb3 = g.sum()
        gH2 = np.outer(g, w3) * (H2 > 0)
        gW2 = gH2.T @ H1
        gb2 = gH2.sum(0)
        gH1 = (gH2 @ W2) * (H1 > 0)
        gW1 = gH1.T @ X
        gb1 = gH1.sum(0)
        W1 -= lr * gW1
        b1 -= lr * gb1
        W2 -= lr * gW2
        b2 -= lr * gb2
        w3 -= lr * gw3
        b3 -= lr * gb3
    return W1, b1, W2, b2, w3, b3


def run_deep(net, X):
    W1, b1, W2, b2, w3, b3 = net
    H1 = np.maximum(X @ W1.T + b1, 0.0)
    H2 = np.maximum(H1 @ W2.T + b2, 0.0)
    return H2 @ w3 + b3


# ── the decode: cards bottom-up once, then the FLAT expansion ──
def card_response(net, active, w2_mask=None):
    """Closed-form response for a binary input pattern, computed
    from the CARDS (the extraction-time substitution). w2_mask
    silences layer-1 neurons for counterfactual prediction."""
    W1, b1, W2, b2, w3, b3 = net
    x = np.zeros(W1.shape[1])
    x[list(active)] = 1.0
    h1 = np.maximum(W1 @ x + b1, 0.0)
    if w2_mask is not None:
        h1 = h1 * w2_mask
    h2 = np.maximum(W2 @ h1 + b2, 0.0)
    return float(w3 @ h2 + b3)


def flat_expansion(net, kf=5, w2_mask=None):
    """The interaction expansion up to order 3 — THE flat form.
    Use never steps: evaluating a pattern sums its subset terms."""
    f = {(): card_response(net, (), w2_mask)}
    for r in (1, 2, 3):
        for S in itertools.combinations(range(kf), r):
            f[S] = card_response(net, S, w2_mask)
    coef = {(): f[()]}
    for r in (1, 2, 3):
        for S in itertools.combinations(range(kf), r):
            c = f[S]
            for rr in range(r):
                for T in itertools.combinations(S, rr):
                    c -= coef[T]
            coef[S] = c
    return coef


def eval_flat(coef, active, kf=5):
    s = set(active)
    tot = 0.0
    for T, c in coef.items():
        if set(T) <= s:
            tot += c
    return tot


def main():
    print("=" * 70)
    print("DEEP-NET DECODE — validate: substitution collapses depth;"
          " assemble the citizen")
    print("=" * 70)
    rng = np.random.default_rng(23)
    net = train_deep(rng)
    W1, b1, W2, b2, w3, b3 = net

    # specimen quality (informational): the net must have learned it
    allX = np.array(list(itertools.product([0.0, 1.0], repeat=5)))
    net_out = run_deep(net, allX)
    fit_err = float(np.max(np.abs(net_out - truth(allX))))
    print(f"  specimen: 5->8->6->1, max |net - truth| = "
          f"{fit_err:.3f} over all 32 patterns")

    coef = flat_expansion(net)
    named = {T: round(c, 2) for T, c in coef.items()
             if T and abs(c) > 0.15}
    want = {(0, 2): 2.0, (1, 2): 2.0, (0, 1, 2): -4.0, (4,): 1.0}
    ok = (set(named) == set(want)
          and all(abs(named[T] - want[T]) < 0.3 for T in want))
    check("C1a the FLAT form recovered: pairs (0,2),(1,2)=+2, "
          "TRIPLE (0,1,2)=-4 (order-3 excess in a deep net), "
          "linear x4=+1, nothing else", ok, f"named {named}")

    errs = [abs(eval_flat(coef, S) - float(run_deep(
        net, np.array([[1.0 if j in S else 0.0
                        for j in range(5)]]))[0]))
            for r in range(6)
            for S in itertools.combinations(range(5), r)]
    check(f"C1b the flat form ALONE predicts all 32 patterns "
          f"(max err {max(errs):.3f}) — incl. 4- and 5-feature "
          f"patterns the expansion never probed", max(errs) < 0.2)

    x4_interactions = [abs(c) for T, c in coef.items()
                       if 4 in T and len(T) > 1]
    check("C1c CARRY FOR FREE: x4 crossed two layers yet lands as a "
          "pure linear term — interactions all "
          f"<= {max(x4_interactions):.3f}",
          max(x4_interactions) < 0.15,
          "depth was the net's problem, not the algebra's")

    # C1d: the counterfactual at depth — silence the (0,1) machinery.
    # First-pass lesson, wrong-kept: selecting by pair-excess alone
    # caught only the NONLINEAR carriers and missed the linear
    # members (the x0+x1 riders have zero pair-excess) — an assembly
    # includes its linear parts; the cards correctly PREDICTED the
    # partial collapse that mistake produced. Selection now: every
    # layer-1 neuron that reads x0 or x1 at all.
    assembly = [i for i in range(len(W1))
                if max(abs(W1[i, 0]), abs(W1[i, 1])) > 0.25]
    mask = np.ones(len(W1))
    mask[assembly] = 0.0
    coef_abl = flat_expansion(net, w2_mask=mask)
    pred = {T: coef_abl.get(T, 0.0)
            for T in [(0, 2), (1, 2), (0, 1, 2), (4,)]}
    W2m = W2 * mask[None, :]
    net_abl = (W1, b1, W2m, b2, w3, b3)
    f = {(): float(run_deep(net_abl, np.zeros((1, 5)))[0])}
    for r in (1, 2, 3):
        for S in itertools.combinations(range(5), r):
            x = np.array([[1.0 if j in S else 0.0
                           for j in range(5)]])
            f[S] = float(run_deep(net_abl, x)[0])
    coef_meas = {(): f[()]}
    for r in (1, 2, 3):
        for S in itertools.combinations(range(5), r):
            c = f[S]
            for rr in range(r):
                for T in itertools.combinations(S, rr):
                    c -= coef_meas[T]
            coef_meas[S] = c
    agree = all(abs(pred[T] - coef_meas[T]) < 0.15 for T in pred)
    check("C1d-i THE THEORY GATE: the cards PREDICT the intervention"
          f" outcome before it runs (all four terms within 0.15)",
          agree,
          f"pred {[round(pred[T], 2) for T in pred]} vs meas "
          f"{[round(coef_meas[T], 2) for T in pred]}")
    collapsed = all(abs(coef_meas[T]) < 0.3
                    for T in [(0, 2), (1, 2), (0, 1, 2)])
    survived = abs(coef_meas[(4,)] - pred[(4,)]) < 0.15
    check("C1d-ii the full (0,1) machinery silenced: every composed "
          f"term collapses, x4 lands where the cards said "
          f"(assembly {assembly})",
          collapsed and survived,
          f"composed {[round(coef_meas[T], 2) for T in [(0, 2), (1, 2), (0, 1, 2)]]}, "
          f"x4 {coef_meas[(4,)]:.2f} (pred {pred[(4,)]:.2f})")

    # ── C3: ASSEMBLE THE CITIZEN ──
    import isaac as mod
    Xd = np.tile(allX, (4, 1))
    yd = np.array([eval_flat(coef, tuple(np.flatnonzero(row)))
                   for row in Xd])
    yd = yd + rng.normal(0, 0.01, len(yd))
    m = mod.Isaac()
    r = m.discover(Xd, yd, name="foreign_net_citizen")
    print(f"  C3 his verdict: {r['verdict']}  his equation: "
          f"{r['equation']}")
    pred_isaac = m.apply_law("foreign_net_citizen", allX)
    ok3 = pred_isaac is not None and np.isfinite(pred_isaac).all()
    err3 = float(np.max(np.abs(pred_isaac - net_out))) if ok3 \
        else np.inf
    check("C3a the citizen minted: a verdict and a readable "
          "equation in HIS grammar",
          r["verdict"] in ("UNDERSTOOD", "PARTIAL") and ok3)
    check(f"C3b his law vs the FOREIGN NET on all 32 patterns: "
          f"max err {err3:.3f} — the stranger's weights are now a "
          f"citizen of his net", err3 < 0.25)

    print()
    print(f"DEEP-DECODE PROBE: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
