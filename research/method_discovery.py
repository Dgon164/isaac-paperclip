"""
METHOD DISCOVERY — raw data + toolkit, find the key that derives the answer.

Isaac is given raw data and a TOOLKIT of transforms, and must find WHICH tool
turns the data into a form where the law is recoverable -- it is NOT told which.
Success = it finds the key by testing each against recovery, preferring the
simplest that works. Three planted problems, each needs a different key:
  simple poly -> IDENTITY | power law -> LOG | cumulative -> DIFF
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac
rng = np.random.default_rng(0)
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

def isaac_solve(X, y):
    scored = {}
    for name, tool in TOOLKIT.items():
        out = tool(np.asarray(X, float), np.asarray(y, float))
        if out is None:
            scored[name] = dict(verdict="n/a", r2=-9.0, eq="(out of domain)"); continue
        Xt, yt = out
        try:
            r = Isaac().discover(Xt, yt, name=name)
            scored[name] = dict(verdict=r["verdict"], r2=r["r2"], eq=r["equation"])
        except Exception as e:
            scored[name] = dict(verdict="err", r2=-9.0, eq=str(e)[:40])
    ok = [(n, s) for n, s in scored.items() if s["verdict"] == "UNDERSTOOD" and s["r2"] >= 0.95]
    ok.sort(key=lambda t: (-t[1]["r2"], t[0] != "identity"))
    winner = ok[0][0] if ok else max(scored, key=lambda n: scored[n]["r2"])
    return winner, scored

def prob_simple():
    X = rng.uniform(-2, 2, (300, 2)); return X, X[:, 0] ** 2 - X[:, 1], "x0^2 - x1", "identity"
def prob_power():
    X = rng.uniform(1, 3, (300, 2)); return X, 3 * X[:, 0] ** 2 * X[:, 1] ** 3, "3*x0^2*x1^3", "log"
def prob_cumulative():
    x = rng.uniform(0.5, 3, 300); return x.reshape(-1, 1), np.cumsum(0.5 * x), "increment=0.5*x", "diff"

if __name__ == "__main__":
    print("="*80)
    print("  METHOD DISCOVERY — raw data + toolkit, find the key that derives the answer")
    print("="*80)
    for maker in (prob_simple, prob_power, prob_cumulative):
        X, y, truth, intended = maker()
        winner, scored = isaac_solve(X, y)
        print(f"\n  PROBLEM (truth: {truth})   intended key: {intended}")
        for n, s in scored.items():
            star = "  <-- FOUND" if n == winner else ""
            print(f"     {n:11s}: {s['verdict']:10s} R2 {s['r2']:+.3f}   {s['eq'][:48]}{star}")
        print(f"     => Isaac chose '{winner}' " + ("[MATCH]" if winner == intended else "[picked " + winner + "]"))
