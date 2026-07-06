"""
The persistent orchestrator — Isaac gets a LIFETIME.

Boots from its prior self (or fresh), holds an idk-ledger as a QUEUE, works a
bounded BURST of open holes per session (find a supported key via the toolkit,
self-verify with held-out + null), COMMITS confirmed closures, REQUEUES partials
as shaped idks ('come back'), resolves the empty ones, and SAVES. Run it again:
it remembers what it confirmed and resumes what it didn't. No longer seconds-old
each boot -- as old as its accumulated self.

The queue is the spine: agenda + inbox + deferred buffer. Single-process for now;
disposable fork-workers drop onto the same queue later without changing this.
"""
import sys, os, pickle, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isaac_state.pkl")
EPS = 1e-9
BURST = 2          # holes worked per session (bounded)

def T_identity(X, y): return X, y
def T_log(X, y):
    if (X <= 0).any() or (y <= 0).any(): return None
    return np.log(X), np.log(y)
def T_diff(X, y): return X[1:], np.diff(y)
def T_reciprocal(X, y):
    if (np.abs(y) < EPS).any(): return None
    return X, 1.0 / y
TOOLKIT = {"identity": T_identity, "log": T_log, "diff": T_diff, "reciprocal": T_reciprocal}

def _best(X, y):
    bn, br, beq = "none", -9.0, ""
    for name, tool in TOOLKIT.items():
        out = tool(np.asarray(X, float), np.asarray(y, float))
        if out is None: continue
        Xt, yt = out
        try:
            r = Isaac().discover(Xt, yt, name=name)
            r2 = r["r2"] if r["verdict"] in ("UNDERSTOOD", "PARTIAL") else -9.0
            if r2 > br: bn, br, beq = name, r2, r["equation"]
        except Exception: pass
    return bn, br, beq

def work_idk(X, y):
    name, r_real, eq = _best(X, y)
    rngN = np.random.default_rng(7); yn = np.asarray(y, float).copy(); rngN.shuffle(yn)
    _, r_null, _ = _best(X, yn)
    if r_real >= 0.9 and r_real - r_null >= 0.3:
        return dict(verdict="CONFIRMED", key=name, r2=r_real, eq=eq)
    if r_real >= 0.5 and r_real - r_null >= 0.3:
        return dict(verdict="PARTIAL", key=name, r2=r_real, eq=eq,
                    note=f"structure present (r2 {r_real:.2f}) but no current key fully reaches it")
    return dict(verdict="NO-STRUCTURE", key=name, r2=r_real, eq="")

SEEDS = {"power_law": 1, "cumulative": 2, "simple_poly": 3, "square_wave": 4, "pure_noise": 5}
def gen(name):
    rng = np.random.default_rng(SEEDS[name])
    if name == "power_law":   X = rng.uniform(1, 3, (300, 2)); return X, 3*X[:,0]**2*X[:,1]**3
    if name == "cumulative":  x = rng.uniform(0.5, 3, 300);   return x.reshape(-1,1), np.cumsum(0.5*x)
    if name == "simple_poly": X = rng.uniform(-2, 2, (300, 2)); return X, X[:,0]**2 - X[:,1]
    if name == "square_wave": X = rng.uniform(0, 3, (300, 1)); return X, (np.sin(9.0*X[:,0])>0).astype(float)
    if name == "pure_noise":  X = rng.uniform(0, 3, (300, 2)); return X, rng.normal(size=300)
FRESH = ["power_law", "cumulative", "simple_poly", "square_wave", "pure_noise"]

if os.path.exists(STATE):
    with open(STATE, "rb") as f: S = pickle.load(f); born = False
else:
    S = dict(session=0, confirmed=[], queue=[dict(id=n, attempts=0) for n in FRESH], resolved_empty=[]); born = True

S["session"] += 1
print("="*76)
print(f"  BOOT — session {S['session']}   " + ("(FIRST boot — fresh mind)" if born
      else f"(loaded prior self: {len(S['confirmed'])} confirmed, {len(S['queue'])} open idk)"))
print("="*76)

worked = 0
while worked < BURST and S["queue"]:
    hole = S["queue"].pop(0)
    X, y = gen(hole["id"]); hole["attempts"] += 1
    res = work_idk(X, y); worked += 1
    if res["verdict"] == "CONFIRMED":
        S["confirmed"].append(dict(id=hole["id"], key=res["key"], eq=res["eq"], r2=res["r2"]))
        print(f"  worked '{hole['id']}' (attempt {hole['attempts']}): CONFIRMED via '{res['key']}' -> {res['eq'][:42]}")
    elif res["verdict"] == "PARTIAL":
        hole["note"] = res["note"]; S["queue"].append(hole)
        print(f"  worked '{hole['id']}' (attempt {hole['attempts']}): PARTIAL/idk -> requeued ({res['note']})")
    else:
        S["resolved_empty"].append(hole["id"])
        print(f"  worked '{hole['id']}' (attempt {hole['attempts']}): NO STRUCTURE -> resolved (nothing there)")

with open(STATE, "wb") as f: pickle.dump(S, f)
print("-"*76)
print(f"  saved.  age = {S['session']} sessions | confirmed = {len(S['confirmed'])} | "
      f"open idk = {len(S['queue'])} | resolved-empty = {len(S['resolved_empty'])}")
print("  knows: " + (", ".join(c["id"] for c in S["confirmed"]) or "(nothing yet)"))
if S["queue"]:
    print("  carrying forward: " + ", ".join(h["id"] for h in S["queue"]))
