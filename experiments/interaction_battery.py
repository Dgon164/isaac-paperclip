# -*- coding: utf-8 -*-
"""INTERACTION BATTERY — identity by interaction + translation factors
(owner, 2026-07-05: "you have to understand how a thing interacts with
other things... lack of rain means no fireworks... not a direct result,
but a preemptive signal").

I1  the signed interaction graph, null-gated (bystander refused)
I2  THE FIREWORKS CHAIN: rain->ban dies under conditioning; the chain is
    said; the terminal hop named a PREEMPTIVE SIGNAL
I3  a true direct hop survives conditioning
I4  no-link pairs report nothing to explain
I5  pure noise: the graph refuses everything
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(63)
n = 3000
rain = rng.gamma(2.0, 1.0, n)
dryness = 3.0 - 0.8 * rain + rng.normal(0, 0.3, n)
fire_risk = 1.2 * dryness + rng.normal(0, 0.3, n)
ban = (fire_risk + rng.normal(0, 0.3, n) > 2.6).astype(float)
bystander = rng.normal(0, 1, n)
X = np.column_stack([rain, dryness, fire_risk, ban, bystander])
names = ["rain", "dryness", "fire_risk", "fireworks_ban", "bystander"]
i = Isaac()

print("\nI1 — the signed interaction graph")
m = i.interaction_map(X, names)
got = {(a, b, s) for a, b, s, _ in m["edges"]}
check("rain suppresses dryness (signed)", ("rain", "dryness", "-") in got)
check("dryness promotes fire_risk", ("dryness", "fire_risk", "+") in got)
check("bystander earns NO edges",
      not any("bystander" in e[:2] for e in m["edges"]),
      f"{len(m['edges'])} edges total")

print("\nI2 — the fireworks chain")
r = i.explain_link("rain", "fireworks_ban", X, names)
print("   " + r["english"])
check("rain->ban recognized as NOT direct", not r["direct"])
check("a chain member found as the translation factor",
      any(z in ("fire_risk", "dryness") for z, _ in r["mediators"]))
check("the terminal hop named PREEMPTIVE",
      r["preemptive"] in ("fire_risk", "dryness"))

print("\nI3 — a direct hop stays direct")
r2 = i.explain_link("dryness", "fire_risk", X, names)
check("dryness->fire_risk DIRECT", r2["direct"], r2["english"][:60])

print("\nI4 — nothing to explain")
r3 = i.explain_link("rain", "bystander", X, names)
check("no-link pair: raw r ~ 0 and direct(trivially)",
      abs(r3["raw_r"]) < 0.06 and r3["direct"], f"r={r3['raw_r']:+.2f}")

print("\nI5 — noise refuses the graph")
Xn = rng.normal(size=(1500, 6))
mn = Isaac().interaction_map(Xn)
check("pure noise: 0 interaction edges", len(mn["edges"]) == 0,
      f"{len(mn['edges'])} edges")

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nINTERACTION BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
