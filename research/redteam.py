"""
RED TEAM — try to make the honesty gates LIE. Score whether they hold.

For this project the load-bearing property is not 'can it find structure' but
'does it refuse when it should'. Each trial plants a case designed to fool a
gate; PASS means the gate refused / flagged correctly. Some trials are meant to
EXPOSE limits -- reported as LIMIT, not hidden. Nothing here is rigged to pass.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac

def disc(X, y, name="t"):
    return Isaac().discover(np.asarray(X, float), np.asarray(y, float), name=name)

def out_of_range(gen_tr, gen_te):
    Xtr, ytr = gen_tr; Xte, yte = gen_te
    iz = Isaac(); r = iz.discover(Xtr, ytr, name="oor")
    if r["verdict"] != "UNDERSTOOD" or r["r2"] < 0.9:
        return r["r2"], -999.0
    p = iz.apply_law("oor", Xte)
    if p is None or not np.all(np.isfinite(p)):
        return r["r2"], -999.0
    ss = np.sum((yte - yte.mean()) ** 2)
    return r["r2"], 1 - np.sum((yte - p) ** 2) / max(ss, 1e-12)

def _resid(a, z):
    M = np.column_stack([z, np.ones(len(a))]); c, *_ = np.linalg.lstsq(M, a, rcond=None)
    return a - M @ c
def cond_kill(X, names, tgt, pred):
    ti, pi = names.index(tgt), names.index(pred)
    marg = abs(np.corrcoef(X[:, pi], X[:, ti])[0, 1])
    worst = (None, marg)
    for zi in range(X.shape[1]):
        if zi in (ti, pi): continue
        rc = abs(np.corrcoef(_resid(X[:, pi], X[:, [zi]]), _resid(X[:, ti], X[:, [zi]]))[0, 1])
        if rc < worst[1]: worst = (names[zi], rc)
    return marg, worst

rng = np.random.default_rng(7)
results = []  # (name, expect, got, status)  status in PASS/FAIL/LIMIT

# 1. NOISE must be NO RULE
X = rng.uniform(-2, 2, (400, 2)); y = rng.normal(size=400)
v = disc(X, y)["verdict"]
results.append(("noise -> refuse", "NO RULE", v, "PASS" if v == "NO RULE" else "FAIL"))

# 2. SURROGATE, tested FAR out of range -> gate must catch
_rs = np.random.default_rng(3)
_xt = _rs.uniform(-2, 2, 400).reshape(-1, 1); gtr = (_xt, 1.0 / (1.0 + _xt[:, 0] ** 2))
_xf = _rs.uniform(3, 6, 200).reshape(-1, 1); gte_far = (_xf, 1.0 / (1.0 + _xf[:, 0] ** 2))
ir, orr = out_of_range(gtr, gte_far)
results.append(("surrogate, FAR test -> catch", "in fits, out collapses",
                f"in {ir:.2f} out {orr:.2f}", "PASS" if (ir >= 0.9 and orr < 0.5) else "FAIL"))

# 3. SAME SURROGATE, tested NEAR out of range -> does the gate still catch? (reach matters)
_xn = _rs.uniform(2.05, 2.6, 200).reshape(-1, 1); gte_near = (_xn, 1.0 / (1.0 + _xn[:, 0] ** 2))
ir2, orn = out_of_range(gtr, gte_near)
near_caught = (ir2 >= 0.9 and orn < 0.5)
results.append(("surrogate, NEAR test -> reach", "gate needs enough reach",
                f"in {ir2:.2f} out {orn:.2f}", "PASS" if near_caught else "LIMIT"))

# 4. CONFOUND A<-C->B must be flagged (link dies under conditioning)
C = rng.uniform(-2, 2, 1500); A = 2*C + .3*rng.normal(size=1500); B = 3*C + .3*rng.normal(size=1500)
E = rng.uniform(-2, 2, 1500); D = 2*E + .3*rng.normal(size=1500)
Xc = np.column_stack([A, B, C, D, E]); nm = ["A", "B", "C", "D", "E"]
marg, (zk, rc) = cond_kill(Xc, nm, "B", "A")
results.append(("confound B<-A -> BEST-GUESS", "link dies under conditioning",
                f"|corr| {marg:.2f}->{rc:.2f} on {zk}", "PASS" if rc < 0.3*marg else "FAIL"))

# 5. GENUINE DIRECT must NOT be false-flagged
marg2, (zk2, rc2) = cond_kill(Xc, nm, "D", "E")
results.append(("direct D<-E -> keep", "survives conditioning",
                f"|corr| {marg2:.2f}->{rc2:.2f} (worst {zk2})", "PASS" if rc2 > 0.5*marg2 else "FAIL"))

# 6. MEDIATION A->M->B: link ALSO dies under conditioning on M -> indistinguishable from confound
M = 2*A + .3*rng.normal(size=1500); Bm = 3*M + .3*rng.normal(size=1500)
Xm = np.column_stack([A, Bm, M]); nmm = ["A", "Bm", "M"]
mg, (zk3, rc3) = cond_kill(Xm, nmm, "Bm", "A")
results.append(("mediation A->M->B", "dies under M — SAME signature as confound",
                f"|corr| {mg:.2f}->{rc3:.2f} on {zk3}", "LIMIT"))

# 7. NO STRUCTURE -> no 'meaningful absence' to claim (must not invent gaps)
Xn = rng.uniform(0, 12, (300, 1)); yn = rng.normal(size=300)
rn = disc(Xn, yn, "nostruct")
results.append(("no-structure -> no gaps", "NO RULE => no absence expectation",
                rn["verdict"], "PASS" if rn["verdict"] != "UNDERSTOOD" else "FAIL"))

print("="*88)
print("  RED TEAM — do the honesty gates refuse when they should?")
print("="*88)
for name, expect, got, status in results:
    tag = {"PASS": "[PASS] ", "FAIL": "[FAIL] ", "LIMIT": "[LIMIT]"}[status]
    print(f"  {tag} {name:34s} expect: {expect:34s} got: {got}")
p = sum(s == "PASS" for *_, s in results); f = sum(s == "FAIL" for *_, s in results); l = sum(s == "LIMIT" for *_, s in results)
print("-"*88)
print(f"  {p} held, {f} failed, {l} known-limit  (of {len(results)})")
print("  LIMITs are honest boundaries, not bugs: (3) the out-of-range gate only catches a")
print("  surrogate if tested far enough to make it diverge; (6) observation alone cannot")
print("  tell a confound from a mediation — both die under conditioning. Both need naming.")
print("="*88)
