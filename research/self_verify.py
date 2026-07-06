"""
SELF-VERIFICATION — confirm or deny your own derivation, no answer key.

Isaac gets raw data X and the ANSWER y (not the method). It searches the toolkit
for a process that produces y, then GRADES ITSELF:
  held-out reproduction (derive on half, reproduce y on the unseen half?)
  permutation null      (could the toolkit reproduce a SHUFFLED y just as well?)
CONFIRM only if held-out reproduction is high AND crushes the shuffled null;
otherwise DENY -- including real-but-unreachable structure (honest 'I can't').
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac
EPS = 1e-9

def T_identity(X, y):   return X, y
def T_log(X, y):
    if (X <= 0).any() or (y <= 0).any(): return None
    return np.log(X), np.log(y)
def T_diff(X, y):       return X[1:], np.diff(y)
def T_reciprocal(X, y):
    if (np.abs(y) < EPS).any(): return None
    return X, 1.0 / y
TOOLKIT = {"identity": T_identity, "log": T_log, "diff": T_diff, "reciprocal": T_reciprocal}

def best_reproduction(X, y):
    best_name, best_r2 = "none", -9.0
    for name, tool in TOOLKIT.items():
        out = tool(np.asarray(X, float), np.asarray(y, float))
        if out is None: continue
        Xt, yt = out
        try:
            r = Isaac().discover(Xt, yt, name=name)
            r2 = r["r2"] if r["verdict"] in ("UNDERSTOOD", "PARTIAL") else -9.0
        except Exception:
            r2 = -9.0
        if r2 > best_r2: best_name, best_r2 = name, r2
    return best_name, best_r2

def self_verify(X, y, n_null=2):
    name, r_real = best_reproduction(X, y)
    r_null = -9.0
    for s in range(n_null):
        rngN = np.random.default_rng(100 + s)
        yn = np.asarray(y, float).copy(); rngN.shuffle(yn)
        _, rn = best_reproduction(X, yn); r_null = max(r_null, rn)
    confirm = (r_real >= 0.90) and (r_real - r_null >= 0.30)
    return dict(chain=name, r_real=r_real, r_null=r_null, verdict="CONFIRM" if confirm else "DENY")

if __name__ == "__main__":
    rng = np.random.default_rng(0)
    def p_power():      X = rng.uniform(1, 3, (300, 2)); return X, 3*X[:,0]**2*X[:,1]**3, "power law", True
    def p_cumulative(): x = rng.uniform(0.5, 3, 300); return x.reshape(-1,1), np.cumsum(0.5*x), "cumulative rate", True
    def p_noise():      X = rng.uniform(0, 3, (300, 2)); return X, rng.normal(size=300), "pure noise", False
    def p_reach():      X = rng.uniform(0, 3, (300, 1)); return X, (np.sin(9.0*X[:,0])>0).astype(float), "hard square wave", False
    print("="*82); print("  SELF-VERIFICATION — Isaac confirms/denies its OWN derivation (no answer key)"); print("="*82)
    for maker in (p_power, p_cumulative, p_noise, p_reach):
        X, y, label, should = maker(); v = self_verify(X, y)
        ok = "[correct]" if (v["verdict"] == ("CONFIRM" if should else "DENY")) else "[WRONG]"
        print(f"\n  {label:18s} -> {v['verdict']:8s} {ok}   held-out {v['r_real']:+.3f} vs null {v['r_null']:+.3f} (chain {v['chain']})")
