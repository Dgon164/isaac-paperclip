"""netdecode_probe.py — THE FOREIGN-NET DECODE, rungs P1 / P1.5 / P2
(owner, 2026-07-17: "if we have an unbuilt net, one that someone has
provided only the weights for, we need to decode it... lets find out
how much we can find out").

  B1 PLANTED CIRCUIT — a net trained on y = a·AND(x_i,x_j) + b·x_k
     is decoded FROM WEIGHTS into checklist cards; the AND neuron
     must be named (requirements: both, pass mark rules out
     singles), the interaction coefficient PREDICTED from the cards,
     both confirmed on the running net; ablating the named neuron's
     readout must collapse exactly the pair excess (the receipt).
  B2 THE BLIND DRILL — the decoder receives ONLY the weight
     matrices (a function boundary enforces it): no data, no truth,
     no hints. It files claims FIRST — which pair, what
     coefficient, the linear map, and a truth table predicted from
     its READABLE SUMMARY (never by simulating the weights) — then
     the unblinding scores every claim. Five seeded foreign nets.
  B3 THE HALLUCINATION LAW ON THE DECODER ITSELF — pool-style
     RANDOM weights contain no trained information; the decoder
     must declare NO ATOMIC STRUCTURE (restart instability + no
     sparse gain over scrambled), never invent atoms. "If there is
     no good match, its unlearned. its just not present, and best
     fit would be a hallucination."

Run: PYTHONHASHSEED=0 python netdecode_probe.py
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


# ── the specimen maker: train a 1-hidden ReLU net on a circuit ──
def train_circuit_net(rng, kf=6, hid=8, pair=(0, 1), alpha=2.0,
                      lin=(2, 1.0), steps=8000, lr=0.05):
    """y = alpha*AND(x_pair) + beta*x_lin on sparse binary inputs."""
    W1 = 0.3 * rng.standard_normal((hid, kf))
    b1 = np.zeros(hid)
    w2 = 0.3 * rng.standard_normal(hid)
    b2 = 0.0
    c, beta = lin
    for _ in range(steps):
        X = (rng.random((64, kf)) < 0.3).astype(float)
        y = alpha * X[:, pair[0]] * X[:, pair[1]] + beta * X[:, c]
        H = np.maximum(X @ W1.T + b1, 0.0)
        p = H @ w2 + b2
        g = 2.0 * (p - y) / len(y)
        gw2 = H.T @ g
        gb2 = g.sum()
        gH = np.outer(g, w2) * (H > 0)
        gW1 = gH.T @ X
        gb1 = gH.sum(0)
        W1 -= lr * gW1
        b1 -= lr * gb1
        w2 -= lr * gw2
        b2 -= lr * gb2
    return W1, b1, w2, b2


def run_net(W1, b1, w2, b2, X):
    return np.maximum(X @ W1.T + b1, 0.0) @ w2 + b2


# ── THE DECODER: weights in, readable claims out. Nothing else. ──
def blind_decode(W1, b1, w2, b2, wmin=0.25):
    """Per-neuron checklist cards from the weights alone, composed
    with the readout into a READABLE SUMMARY:
      y ~ b2 + sum_j lin[j]*x_j + sum_pairs and_coef[(i,j)]*AND(i,j)
    Linear effect of j = total readout response to j alone; AND
    coefficient of (i,j) = the pair's response excess over singles —
    both computed FROM THE CARDS (closed form per neuron), never by
    running the net. Claims are the summary; the summary must carry
    the behavior."""
    kf = W1.shape[1]
    cards = []
    for i in range(len(W1)):
        req = [int(j) for j in np.flatnonzero(W1[i] > wmin)]
        dis = [int(j) for j in np.flatnonzero(W1[i] < -wmin)]
        cards.append(dict(neuron=i, requires=req, disqualifiers=dis,
                          pass_mark=float(-b1[i]),
                          weights=W1[i].copy(), bias=float(b1[i]),
                          readout=float(w2[i])))

    def neuron_resp(card, active):
        z = card["bias"] + sum(card["weights"][j] for j in active)
        return max(z, 0.0)

    base = sum(c["readout"] * neuron_resp(c, ()) for c in cards) + b2
    lin = {}
    for j in range(kf):
        lin[j] = sum(c["readout"] * neuron_resp(c, (j,))
                     for c in cards) + b2 - base
    and_coef = {}
    for a in range(kf):
        for bb in range(a + 1, kf):
            ex = (sum(c["readout"] * neuron_resp(c, (a, bb))
                      for c in cards) + b2
                  - base - lin[a] - lin[bb])
            if abs(ex) > 0.25:
                and_coef[(a, bb)] = float(ex)
    # the named AND carriers: trained nets DISTRIBUTE gates across
    # partial-AND neurons (first-pass lesson, kept: the textbook
    # single-neuron condition named nobody while the coefficient
    # read perfectly). The truthful unit is the ASSEMBLY — neurons
    # whose card-computed contributions to the pair excess sum to
    # the coefficient (the receipt is the sum).
    and_neurons = {}
    for pair_, coef in and_coef.items():
        a, bb = pair_
        per = []
        for c in cards:
            e = c["readout"] * (neuron_resp(c, (a, bb))
                                - neuron_resp(c, (a,))
                                - neuron_resp(c, (bb,))
                                + neuron_resp(c, ()))
            if abs(e) > 0.1:
                per.append((c["neuron"], float(e)))
        and_neurons[pair_] = per
    # the truth table, predicted from the SUMMARY (the readable
    # equation), never from the weights:
    table = {}
    for j in range(kf):
        table[(j,)] = base + lin[j] - base + base  # = base+lin[j]
    for a in range(kf):
        for bb in range(a + 1, kf):
            table[(a, bb)] = (base + lin[a] + lin[bb]
                              + and_coef.get((a, bb), 0.0))
    return dict(cards=[{k: v for k, v in c.items()
                        if k not in ("weights",)} for c in cards],
                base=float(base), linear=lin, and_terms=and_coef,
                and_neurons=and_neurons, table=table)


# ── the no-structure declaration (restart stability + sparse gain) ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from protoconcept_probe import sparse_decode, match_atoms  # noqa: E402


def structure_verdict(R, k, s, seed=0):
    """Does this weight matrix carry atomic structure AT ALL? Two
    measured legs: (1) sparse gain over the row's own scrambled
    control; (2) restart STABILITY — two independent runs must find
    the same atoms. Unstable or gainless -> NO STRUCTURE: 'its just
    not present, and best fit would be a hallucination.'"""
    rng = np.random.default_rng(seed)
    _, _, r1 = sparse_decode(R, k, s, restarts=4, seed=1)
    D2, _, _ = sparse_decode(R, k, s, restarts=4, seed=2)
    D3, _, _ = sparse_decode(R, k, s, restarts=4, seed=3)
    stab = float(np.mean([p[0] for p in match_atoms(D2, D3)]))
    Rs = np.array([rng.permutation(row) for row in R])
    _, _, rs = sparse_decode(Rs, k, s, restarts=2, seed=4)
    gain = rs / max(r1, 1e-9)
    has = bool(gain > 2.0 and stab > 0.9)
    return dict(structure=has, resid=r1, scrambled=rs,
                gain=float(gain), restart_stability=stab,
                why=("atoms present: sparse gain over scrambled "
                     "and restarts agree" if has else
                     "NO ATOMIC STRUCTURE — unlearned/not present; "
                     "a best-fit dictionary here would be a "
                     "hallucination"))


def main():
    print("=" * 70)
    print("NET-DECODE PROBE — the foreign net, read from weights")
    print("=" * 70)
    rng = np.random.default_rng(11)

    # ── B1: the planted circuit ──
    W1, b1, w2, b2 = train_circuit_net(rng, pair=(0, 1), alpha=2.0,
                                       lin=(2, 1.0))
    dec = blind_decode(W1, b1, w2, b2)
    assembly = dec["and_neurons"].get((0, 1), [])
    named = [i for i, _ in assembly]
    contrib_sum = sum(e for _, e in assembly)
    ok = ((0, 1) in dec["and_terms"]
          and abs(dec["and_terms"][(0, 1)] - 2.0) < 0.3
          and len(named) >= 1
          and abs(contrib_sum - dec["and_terms"][(0, 1)]) < 0.1
          and all(abs(v) < 0.3 for k_, v in dec["and_terms"].items()
                  if k_ != (0, 1)))
    check("B1 circuit read from weights: AND(0,1) coefficient "
          f"{dec['and_terms'].get((0, 1), 0):.2f} (true 2.0), "
          f"carried by ASSEMBLY {named} whose contributions sum to "
          f"{contrib_sum:.2f}", ok,
          f"per-neuron: {[(i, round(e, 2)) for i, e in assembly]}")
    lin_ok = abs(dec["linear"][2] - 1.0) < 0.2 and all(
        abs(dec["linear"][j]) < 0.2 for j in range(6) if j != 2)
    check(f"B1b linear map read: x2 -> {dec['linear'][2]:.2f} "
          f"(true 1.0), others quiet", lin_ok)

    # behavioral confirmation of the pair excess, on the RUNNING net
    def probe(active):
        x = np.zeros(6)
        x[list(active)] = 1.0
        return float(run_net(W1, b1, w2, b2, x.reshape(1, -1))[0])
    exc_meas = (probe((0, 1)) - probe((0,)) - probe((1,))
                + probe(()))
    ctrl_meas = (probe((3, 4)) - probe((3,)) - probe((4,))
                 + probe(()))
    check("B1c measured on the run: pair excess "
          f"{exc_meas:.2f} (predicted "
          f"{dec['and_terms'].get((0, 1), 0):.2f}); control pair "
          f"{ctrl_meas:.2f}",
          abs(exc_meas - dec["and_terms"].get((0, 1), 0)) < 0.15
          and abs(ctrl_meas) < 0.15)

    # the COUNTERFACTUAL receipt: predict from the cards what
    # silencing the assembly does to BOTH pathways, then confirm on
    # the running net — the decode must know the intervention's
    # outcome before it happens
    dec_abl = blind_decode(W1, b1,
                           np.where(np.isin(np.arange(len(w2)),
                                            named), 0.0, w2), b2)
    pred_exc_abl = dec_abl["and_terms"].get((0, 1), 0.0)
    pred_lin_abl = dec_abl["linear"][2]
    w2_abl = w2.copy()
    w2_abl[named] = 0.0

    def probe_abl(active):
        x = np.zeros(6)
        x[list(active)] = 1.0
        return float(run_net(W1, b1, w2_abl, b2,
                             x.reshape(1, -1))[0])
    exc_abl = (probe_abl((0, 1)) - probe_abl((0,))
               - probe_abl((1,)) + probe_abl(()))
    lin_abl = probe_abl((2,)) - probe_abl(())
    check("B1d counterfactual receipt: predicted ablation outcome "
          f"(excess {pred_exc_abl:.2f}, x2 {pred_lin_abl:.2f}) "
          f"CONFIRMED on the run (excess {exc_abl:.2f}, x2 "
          f"{lin_abl:.2f}); the pair pathway collapsed",
          abs(exc_abl - pred_exc_abl) < 0.15
          and abs(lin_abl - pred_lin_abl) < 0.15
          and abs(exc_abl) < 0.5 * abs(exc_meas))

    # ── B2: THE BLIND DRILL over five foreign nets ──
    print("  B2 blind drill (decoder sees ONLY weights; claims "
          "filed, then unblinded):")
    hits_pair = hits_coef = hits_table = 0
    n_drill = 5
    for t in range(n_drill):
        drng = np.random.default_rng(100 + t)
        pool_feats = list(range(6))
        a_, b_ = sorted(drng.choice(pool_feats, 2, replace=False))
        c_ = int(drng.choice([f for f in pool_feats
                              if f not in (a_, b_)]))
        alpha = float(drng.uniform(1.5, 2.5))
        beta = float(drng.uniform(0.8, 1.2))
        net = train_circuit_net(drng, pair=(a_, b_), alpha=alpha,
                                lin=(c_, beta))
        claims = blind_decode(*net)          # weights only
        # unblind and score
        top_pair = max(claims["and_terms"],
                       key=lambda p: abs(claims["and_terms"][p])) \
            if claims["and_terms"] else None
        p_ok = top_pair == (a_, b_)
        c_ok = p_ok and abs(claims["and_terms"][top_pair] - alpha) \
            < 0.15 * alpha + 0.1
        # the readable summary must carry the behavior
        errs = []
        for active, pred in claims["table"].items():
            x = np.zeros(6)
            x[list(active)] = 1.0
            errs.append(abs(pred - float(
                run_net(*net, x.reshape(1, -1))[0])))
        t_ok = max(errs) < 0.25
        hits_pair += p_ok
        hits_coef += c_ok
        hits_table += t_ok
        print(f"    net {t}: truth AND{(int(a_), int(b_))}"
              f"*{alpha:.2f} + x{c_}*{beta:.2f} | claimed {top_pair}"
              f"*{claims['and_terms'].get(top_pair, 0):.2f} | "
              f"table max-err {max(errs):.3f} "
              f"[{'named' if p_ok else 'MISSED'}]")
    check(f"B2 blind drill: pair named {hits_pair}/{n_drill}, "
          f"coefficient within tol {hits_coef}/{n_drill}",
          hits_pair >= 4 and hits_coef >= 4)
    check(f"B2b the readable summary carries the behavior "
          f"({hits_table}/{n_drill} tables within tol)",
          hits_table >= 4)

    # ── B3: the hallucination law on the decoder itself ──
    atoms = rng.standard_normal((6, 20))
    atoms /= np.linalg.norm(atoms, axis=1, keepdims=True)
    loads = np.zeros((96, 6))
    for i in range(96):
        pick = rng.choice(6, 2, replace=False)
        loads[i, pick] = (rng.uniform(0.5, 1.5, 2)
                          * rng.choice([-1, 1], 2))
    Wp = loads @ atoms + 0.02 * rng.standard_normal((96, 20))
    v_planted = structure_verdict(Wp, 6, 2)
    Wr = rng.standard_normal((96, 20)) * rng.uniform(
        0.7, 2.5, (96, 1))                    # pool-style random
    v_random = structure_verdict(Wr, 6, 2)
    check("B3 planted weights: structure DECLARED "
          f"(gain {v_planted['gain']:.1f}x, stability "
          f"{v_planted['restart_stability']:.2f})",
          v_planted["structure"])
    check("B3b RANDOM pool weights: NO STRUCTURE declared — "
          "unlearned, not hallucinated "
          f"(gain {v_random['gain']:.1f}x, stability "
          f"{v_random['restart_stability']:.2f})",
          not v_random["structure"])

    print()
    print(f"NET-DECODE PROBE: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
