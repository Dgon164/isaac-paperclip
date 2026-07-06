"""
Parallel workers with composition search — concurrent background attack.

Disposable fork-workers run CONCURRENTLY (multiprocessing.Pool). Each is deeper
than the orchestrator's single-key pass: it tries COMPOSITIONS (chains of keys),
so a background worker can crack a combination-lock the foreground never could.
Workers are stateless (pull an idk name, search, return a result); the main
process is the single consumer that commits. Race-free by construction.

Planted so you can see the point:
  combo_lock  -> needs a CHAIN (diff then log); single keys fail; a worker cracks it.
  square_wave -> needs a NEW key, not a chain; stays honestly open (that's tool-creation).
"""
import sys, os, time, numpy as np
from multiprocessing import Pool, cpu_count
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac
EPS = 1e-9

def T_identity(X, y): return X, y
def T_log(X, y):
    if (X <= 0).any() or (y <= 0).any(): return None
    return np.log(X), np.log(y)
def T_diff(X, y): return X[1:], np.diff(y)
def T_reciprocal(X, y):
    if (np.abs(y) < EPS).any(): return None
    return X, 1.0 / y
TOOLKIT = {"identity": T_identity, "log": T_log, "diff": T_diff, "reciprocal": T_reciprocal}

SEEDS = {"power_law": 1, "cumulative": 2, "simple_poly": 3, "square_wave": 4, "combo_lock": 6}
def gen(name):
    rng = np.random.default_rng(SEEDS[name])
    if name == "power_law":   X = rng.uniform(1, 3, (300, 2)); return X, 3*X[:,0]**2*X[:,1]**3
    if name == "cumulative":  x = rng.uniform(0.5, 3, 300);   return x.reshape(-1,1), np.cumsum(0.5*x)
    if name == "simple_poly": X = rng.uniform(-2, 2, (300, 2)); return X, X[:,0]**2 - X[:,1]
    if name == "square_wave": X = rng.uniform(0, 3, (300, 1)); return X, (np.sin(9.0*X[:,0])>0).astype(float)
    if name == "combo_lock":                                   # cumulative of a power-law step
        ab = rng.uniform(1, 3, (300, 2)); steps = 3*ab[:,0]**2*ab[:,1]**3
        return ab, np.cumsum(steps)

def chain_apply(X, y, chain):
    for t in chain:
        out = TOOLKIT[t](np.asarray(X, float), np.asarray(y, float))
        if out is None: return None
        X, y = out
    return X, y

def deep_search(X, y):
    keys = list(TOOLKIT)
    chains = [(k,) for k in keys] + [(a, b) for a in keys for b in keys]
    best = None
    for chain in chains:
        out = chain_apply(X, y, chain)
        if out is None: continue
        Xt, yt = out
        if len(yt) < 40: continue
        try: r = Isaac().discover(Xt, yt, name="w")
        except Exception: continue
        und = (r["verdict"] == "UNDERSTOOD" and r["r2"] >= 0.9)
        score = (und, r["r2"] if r["verdict"] in ("UNDERSTOOD", "PARTIAL") else -9.0, -len(chain))
        if best is None or score > best[0]:
            best = (score, chain, r["equation"], r["r2"])
    return best

def worker_solve(name):                    # runs in a separate process
    t0 = time.perf_counter()
    X, y = gen(name)
    best = deep_search(X, y)
    dt = time.perf_counter() - t0
    if best is None: return dict(id=name, verdict="NO-STRUCTURE", chain=(), eq="", r2=-9, secs=dt)
    (und, r2, _), chain, eq, r2v = best
    verdict = "CONFIRMED" if und else ("PARTIAL" if r2v >= 0.5 else "NO-STRUCTURE")
    return dict(id=name, verdict=verdict, chain=chain, eq=eq, r2=r2v, secs=dt)

if __name__ == "__main__":
    queue = ["power_law", "cumulative", "simple_poly", "combo_lock", "square_wave"]
    nproc = min(len(queue), max(2, cpu_count() - 1))
    print("="*80)
    print(f"  PARALLEL WORKERS — {len(queue)} idks across {nproc} concurrent processes, composition search")
    print("="*80)
    t0 = time.perf_counter()
    with Pool(processes=nproc) as pool:
        results = pool.map(worker_solve, queue)      # concurrent background attack
    wall = time.perf_counter() - t0
    cpu_secs = sum(r["secs"] for r in results)
    for r in results:
        chain = "->".join(r["chain"]) if r["chain"] else "-"
        tag = {"CONFIRMED": "CONFIRMED", "PARTIAL": "idk (carry forward)", "NO-STRUCTURE": "nothing there"}[r["verdict"]]
        print(f"  {r['id']:12s}: {tag:20s} via [{chain:16s}]  r2 {r['r2']:+.2f}  {r['eq'][:34]}")
    print("-"*80)
    print(f"  wall {wall:.1f}s  vs  summed worker time {cpu_secs:.1f}s  -> ~{cpu_secs/max(wall,1e-9):.1f}x concurrency")
    print("  NOTE: combo_lock was cracked by a CHAIN (diff->log) the single-key foreground can't open.")
    print("        square_wave stays open — it needs a NEW key, not a chain. That's tool-creation (thread 2).")
