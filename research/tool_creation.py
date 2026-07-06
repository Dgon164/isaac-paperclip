"""
TOOL CREATION — Isaac forges new keys when his existing ones don't fit.

Extends the engine's composite idea (register_composite) up a level: from
reusable basis-atoms to reusable KEYS. A key is born two ways:
  (1) MINT a composition — a chain of existing keys that cracks a hole.
  (2) FORGE a primitive — when no chain works, draw from a stock (abs/sign/sqrt)
      and register the one that cracks it.

CRITICAL (learned the hard way): a "crack" is gated on OUT-OF-RANGE survival,
not in-range fit. Without that gate the system just fits a surrogate with an
existing key and never forges anything — it fools itself. The extrapolation
discipline is what makes autonomous tool-creation possible at all.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac
EPS = 1e-9

def K_identity(X, y): return X, y
def K_log(X, y):
    if (X <= 0).any() or (y <= 0).any(): return None
    return np.log(X), np.log(y)
def K_diff(X, y): return X[1:], np.diff(y)
def K_reciprocal(X, y):
    if (np.abs(y) < EPS).any(): return None
    return X, 1.0 / y
def K_abs(X, y):  return np.abs(X), y
def K_sign(X, y): return np.sign(X), y
def K_sqrt(X, y): return np.sqrt(np.abs(X)), y

BASE = {"identity": K_identity, "log": K_log, "diff": K_diff, "reciprocal": K_reciprocal}
STOCK = {"abs": K_abs, "sign": K_sign, "sqrt": K_sqrt}
FORGED = {}

def apply_chain(X, y, chain, table):
    for name in chain:
        out = table[name](np.asarray(X, float), np.asarray(y, float))
        if out is None: return None
        X, y = out
    return X, y

def cracks(g, tr, te, chain, table):
    """Crack = UNDERSTOOD in-range AND the recovered law holds OUT of range."""
    otr = apply_chain(*g(*tr), chain, table); ote = apply_chain(*g(*te), chain, table)
    if otr is None or ote is None: return None
    Xt, yt = otr; Xq, yq = ote
    if len(yt) < 40 or len(yq) < 20: return None
    iz = Isaac()
    try: r = iz.discover(Xt, yt, name="k")
    except Exception: return None
    if r["verdict"] != "UNDERSTOOD" or r["r2"] < 0.9: return None
    try: pred = iz.apply_law("k", Xq)
    except Exception: return None
    if pred is None or not np.all(np.isfinite(pred)): return None
    ss = np.sum((yq - yq.mean()) ** 2)
    r2o = 1 - np.sum((yq - pred) ** 2) / max(ss, 1e-12)
    return r["equation"] if r2o >= 0.9 else None          # THE GATE: must survive out of range

def solve(g, tr, te):
    for fname, chain in FORGED.items():
        eq = cracks(g, tr, te, chain, BASE)
        if eq: return ("forged-key", fname, eq)
    keys = list(BASE)
    for k in keys:
        eq = cracks(g, tr, te, [k], BASE)
        if eq: return ("base-key", k, eq)
    for a in keys:
        for b in keys:
            eq = cracks(g, tr, te, [a, b], BASE)
            if eq:
                name = f"{a}.{b}"; FORGED[name] = [a, b]
                return ("MINTED", name, eq)
    return None

def forge(g, tr, te):
    for pname, ptool in STOCK.items():
        table = dict(BASE); table[pname] = ptool
        for chain in [[pname]] + [[pname, k] for k in BASE]:
            eq = cracks(g, tr, te, chain, table)
            if eq:
                BASE[pname] = ptool
                return (pname, chain, eq)
    return None

def make_combo(c):
    def g(lo, hi):
        r = np.random.default_rng(int((lo + hi) * 97) + int(c * 13))
        ab = r.uniform(lo, hi, (300, 2)); return ab, np.cumsum(c * ab[:, 0] ** 2 * ab[:, 1] ** 3)
    return g
def make_v(c):
    def g(lo, hi):
        r = np.random.default_rng(int((abs(lo) + hi) * 91) + int(c * 17))
        x = r.uniform(lo, hi, (300, 1)); return x, c * np.abs(x[:, 0]) + 2.0
    return g

PROBLEMS = [
    ("combo_lock  ", make_combo(3), (1, 2), (2, 3)),   # needs a CHAIN -> mint diff.log
    ("v_shape     ", make_v(3),    (-2, 2), (-4, -2)),  # forge abs; test the OTHER branch where surrogate splits
    ("combo_lock_2", make_combo(2), (1, 2), (2, 3)),   # reuse the minted key, 1 move
    ("v_shape_2   ", make_v(5),    (-2, 2), (-4, -2)),  # reuse the forged key, 1 move
]

print("="*82)
print("  TOOL CREATION — forge keys from shaped holes (out-of-range gated)")
print("="*82)
print(f"  start keys: {list(BASE)}\n")
for name, g, tr, te in PROBLEMS:
    res = solve(g, tr, te)
    if res:
        how, key, eq = res
        label = {"forged-key": "solved (1 move) via FORGED/MINTED key",
                 "base-key": "solved via base key", "MINTED": "cracked by chain -> MINTED"}[how]
        print(f"  {name}: {label} '{key}'  ->  {eq[:36]}")
    else:
        fr = forge(g, tr, te)
        if fr:
            print(f"  {name}: no key fit -> FORGED primitive '{fr[0]}'  ->  {fr[2][:32]}")
        else:
            print(f"  {name}: idk — nothing (even the stock) reaches it")

print("\n" + "-"*82)
print(f"  base keys now: {list(BASE)}")
print(f"  minted keys:   {list(FORGED)}")
print("  Repeats solved in one move via the keys it made. The toolkit grew itself.")
print("="*82)
