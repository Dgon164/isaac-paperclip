"""
BEST-GUESS — a usable pattern whose CAUSE is unresolved.

Separates two things most systems conflate: 'predicts reliably' vs 'knows why'.
A finding gets two coordinates:
  usable?  -- does it beat the null and hold (discover).
  direct?  -- does the link SURVIVE conditioning on the other variables, or does
              it vanish (the 'fireworks law': a link that dies under stratum-
              matched conditioning is a chain/confound, not a direct cause)?

  usable + survives conditioning  -> DIRECT-consistent (toward LAW)
  usable + dies under conditioning -> BEST-GUESS: use it, but cause is a proxy;
              resolution-path names what to investigate.

Confound demo: A and B are both driven by C. So A predicts B (usable) -- but the
link is entirely through C. Isaac should NOT call it a law.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac

rng = np.random.default_rng(0)
n = 1500
C = rng.uniform(-2, 2, n)                    # hidden-in-spirit driver (measured here)
A = 2.0 * C + 0.3 * rng.normal(size=n)       # A is driven by C
B = 3.0 * C + 0.3 * rng.normal(size=n)       # B is driven by C  -> A,B correlated, A doesn't cause B
E = rng.uniform(-2, 2, n)                     # independent driver
D = 2.0 * E + 0.3 * rng.normal(size=n)       # D genuinely driven by E
X = np.column_stack([A, B, C, D, E]); names = ["A", "B", "C", "D", "E"]

def corr(a, b): return abs(np.corrcoef(a, b)[0, 1])
def resid(a, z):                              # regress a on z, return the residual (condition on z)
    M = np.column_stack([z, np.ones(len(a))]); c, *_ = np.linalg.lstsq(M, a, rcond=None)
    return a - M @ c

def examine(tgt, pred):
    ti, pi = names.index(tgt), names.index(pred)
    y = (X[:, ti] - X[:, ti].mean()) / X[:, ti].std()
    x = (X[:, [pi]] - X[:, [pi]].mean(0)) / X[:, [pi]].std(0)
    r = Isaac().discover(x, y, name=f"{tgt}_from_{pred}")
    usable = r["verdict"] in ("UNDERSTOOD", "PARTIAL") and r["r2"] >= 0.6
    r_marg = corr(X[:, pi], X[:, ti])
    killers = []
    for zi in range(X.shape[1]):
        if zi in (ti, pi): continue
        rc = corr(resid(X[:, pi], X[:, [zi]]), resid(X[:, ti], X[:, [zi]]))
        if r_marg > 0.5 and rc < 0.3 * r_marg:      # the link vanishes when conditioned on this var
            killers.append((names[zi], rc))
    return r, usable, r_marg, killers

print("="*80)
print("  BEST-GUESS — usable pattern vs resolved cause (confound test)")
print("="*80)
for tgt, pred in [("B", "A"), ("D", "E")]:
    r, usable, r_marg, killers = examine(tgt, pred)
    print(f"\n  {tgt} <- {pred}:  pattern {r['verdict']}  R2 {r['r2']:.2f}  (|corr| {r_marg:.2f})")
    if usable and killers:
        z, rc = killers[0]
        print(f"     VERDICT: BEST-GUESS  (usable, cause UNRESOLVED)")
        print(f"       reliable enough to observe and use, BUT the {tgt}<-{pred} link VANISHES")
        print(f"       when conditioned on {z}  (|corr| {r_marg:.2f} -> {rc:.2f}) — {pred} is a proxy,")
        print(f"       the pattern flows through {z}.")
        print(f"       resolution-path: investigate {z} (measure / condition / intervene) to resolve why.")
    elif usable:
        print(f"     VERDICT: DIRECT-consistent  (survives conditioning on all measured variables)")
        print(f"       no measured confound found. (Observation still can't PROVE cause —")
        print(f"       resolution-path: intervene on {pred} to confirm.)")
    else:
        print(f"     VERDICT: no usable pattern.")
print("\n" + "="*80)
print("  Both B<-A and D<-E predict at R2~0.9. Only D<-E survives conditioning. Isaac keeps")
print("  the usable pattern for B<-A but refuses to call it a cause — and says what to check.")
print("="*80)
