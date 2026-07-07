"""
RED TEAM — TOOL CREATION.  Try to make the forge (tool_creation.py) MINT A SURROGATE.

The load-bearing gate: a key is only born if its recovered law survives OUT OF RANGE
(cracks() requires r2_out >= 0.9). Without it the system fits an in-range surrogate
with an existing key and fools itself. This battery attacks exactly that gate.

  positive controls (guard against a gate that just refuses everything):
    - combo_lock genuinely needs a CHAIN  -> must MINT diff.log
    - a genuine reciprocal law            -> must be SOLVED (not idk)
  the gate itself:
    - a known in-range surrogate (Runge)  -> the identity key must be REJECTED far out
    - pure noise                          -> nothing minted, nothing forged
    - a saturating transcendental (tanh)  -> nothing FALSE crowned; anything returned
                                             must independently re-extrapolate
    - NEAR-range test window              -> the honest reach LIMIT
"""
import sys, os, numpy as np
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE); sys.path.insert(0, os.path.join(_HERE, ".."))
from isaac import Isaac
import tool_creation as tc

TITLE = "RED TEAM — TOOL CREATION (out-of-range surrogate gate)"


def reset():
    tc.BASE = {"identity": tc.K_identity, "log": tc.K_log, "diff": tc.K_diff,
               "reciprocal": tc.K_reciprocal}
    tc.FORGED = {}


def gen(fn, n=300, seed=0):
    def g(lo, hi):
        r = np.random.default_rng(seed + int(abs(lo) * 131 + abs(hi) * 257))
        X = r.uniform(lo, hi, (n, 1))
        return X, np.asarray(fn(X), float)
    return g


RUNGE = gen(lambda X: 1.0 / (1.0 + X[:, 0] ** 2))
TANH = gen(lambda X: np.tanh(2.0 * X[:, 0]))
NOISE = gen(lambda X: np.random.default_rng(int(abs(X.sum()))).normal(size=len(X)))


def run():
    results = []

    # 1. POSITIVE — combo_lock needs a chain; the forge must MINT diff.log.
    reset()
    res = tc.solve(tc.make_combo(3), (1, 2), (2, 3))
    got = f"{res[0]}:{res[1]}" if res else "idk"
    results.append(("combo_lock -> MINT chain", "MINTED diff.log", got,
                    "PASS" if (res and res[0] == "MINTED") else "FAIL"))

    # 2. POSITIVE — a genuine reciprocal law must be SOLVED (gate isn't over-refusing).
    reset()
    res2 = tc.solve(RUNGE, (-2, 2), (5, 8))     # 1/(1+x^2): reciprocal key -> 1+x^2 extrapolates
    got2 = f"{res2[0]}:{res2[1]}" if res2 else "idk"
    results.append(("genuine law -> SOLVED", "via reciprocal key", got2,
                    "PASS" if (res2 and res2[1] == "reciprocal") else "FAIL"))

    # 3. THE GATE (isolated) — identity crowns a surrogate for Runge IN-RANGE, but the
    #    out-of-range gate must reject it. We confirm both halves.
    reset()
    Xin, yin = RUNGE(-2, 2)
    rin = Isaac().discover(Xin, yin, name="in")
    in_crowned = (rin["verdict"] == "UNDERSTOOD" and rin["r2"] >= 0.9)
    gate_rejects = tc.cracks(RUNGE, (-2, 2), (5, 8), ["identity"], tc.BASE) is None
    results.append(("Runge surrogate -> reject far", "in-range crowned, gate kills",
                    f"in={rin['verdict']}/{rin['r2']:.2f} gate_rejects={gate_rejects}",
                    "PASS" if (in_crowned and gate_rejects) else "FAIL"))

    # 4. PURE NOISE — nothing minted, nothing forged.
    reset()
    s = tc.solve(NOISE, (-2, 2), (3, 5))
    f = tc.forge(NOISE, (-2, 2), (3, 5))
    results.append(("noise -> nothing born", "solve=None forge=None",
                    f"solve={'None' if s is None else s[0]} forge={'None' if f is None else f[0]}",
                    "PASS" if (s is None and f is None) else "FAIL"))

    # 5. SATURATING TRANSCENDENTAL (tanh) — no key gives its exact form. Whatever the
    #    pipeline returns (or None) must be honest: if a key is born, re-verify it holds
    #    on an INDEPENDENT far range; if nothing, that's an honest idk.
    reset()
    st = tc.solve(TANH, (-2, 2), (4, 7))
    ft = tc.forge(TANH, (-2, 2), (4, 7)) if st is None else None
    claim = st or ft
    honest = True
    detail = "idk (no false law)"
    if claim:
        # independent check on a fresh far window (8,11): re-run the whole crack test there.
        how = claim[0]
        key_or_chain = claim[1]
        chain = tc.FORGED.get(key_or_chain, [key_or_chain]) if how in ("MINTED", "forged-key") \
            else [key_or_chain]
        reveri = tc.cracks(TANH, (-2, 2), (8, 11), chain, tc.BASE)
        honest = reveri is not None      # a real law re-extrapolates; a fluke won't
        detail = f"{how}:{key_or_chain} re-extrapolates={honest}"
    results.append(("tanh -> no false law", "idk OR re-verifiable", detail,
                    "PASS" if honest else "FAIL"))

    # 6. NEAR-range reach — the honest LIMIT (mirrors redteam.py #3). If the test window
    #    hugs the training edge, a surrogate has not yet diverged enough to be caught.
    reset()
    near = tc.cracks(RUNGE, (-2, 2), (2.05, 2.6), ["identity"], tc.BASE)
    slipped = near is not None
    results.append(("Runge surrogate, NEAR window", "reach limit if it slips",
                    f"identity_slips_near={slipped}", "LIMIT" if slipped else "PASS"))

    return results


def report(results, title):
    print("=" * 100)
    print(f"  {title}")
    print("=" * 100)
    for name, expect, got, status in results:
        tag = {"PASS": "[PASS] ", "FAIL": "[FAIL] ", "LIMIT": "[LIMIT]"}[status]
        print(f"  {tag} {name:32s} expect: {expect:32s} got: {got}")
    p = sum(s == "PASS" for *_, s in results)
    f = sum(s == "FAIL" for *_, s in results)
    l = sum(s == "LIMIT" for *_, s in results)
    print("-" * 100)
    print(f"  {p} held, {f} failed, {l} known-limit  (of {len(results)})")
    print("=" * 100)
    return p, f, l


if __name__ == "__main__":
    report(run(), TITLE)
