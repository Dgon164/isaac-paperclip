# -*- coding: utf-8 -*-
"""CONCEPTUAL CONCEPTS BATTERY (owner, 2026-07-05: "we have
decompositional aspects, but we don't have conceptual concepts").

The thesis: a conceptual concept is an equivalence of ROLE, not content.
Three worlds with ZERO shared vocabulary — weather, a power grid, a
body — each containing the same organization: driver -> translation
factor -> risk -> discrete preemptive response, plus a bystander. Each
variable's ROLE PROFILE (from interaction_map + explain_link) becomes
observation tokens; the EXISTING crystallizer must then mint concepts
that span the worlds: 'the preemptive responder' containing ban, trip,
and fever — things that share nothing but their role.

C1  role profiles extracted per world (no hand labels)
C2  the crystallizer mints CROSS-WORLD role concepts
C3  the concept is nameable and queryable (teach once, ask anywhere)
C4  bystanders join no role concept
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(77)
n = 2500

def world(names, seed):
    r = np.random.default_rng(seed)
    drive = r.gamma(2.0, 1.0, n)
    med = 3.0 - 0.8 * drive + r.normal(0, 0.3, n)
    risk = 1.2 * med + r.normal(0, 0.3, n)
    resp = (risk + r.normal(0, 0.3, n) > 2.6).astype(float)
    by = r.normal(0, 1, n)
    return np.column_stack([drive, med, risk, resp, by]), names

WORLDS = [
    world(["rain", "dryness", "fire_risk", "fireworks_ban", "birdsong"], 1),
    world(["load", "heat", "failure_risk", "breaker_trip", "paint"], 2),
    world(["stress", "cortisol", "illness_risk", "fever_response", "shoe"], 3),
]

# ── C1: role profiles, no hand labels ───────────────────────────────
print("\nC1 — role profiles from the interaction organs")
i = Isaac()
role_tokens = {}
for X, names in WORLDS:
    m = i.interaction_map(X, names)
    deg = {v: 0 for v in names}
    for a, b, s, _ in m["edges"]:
        deg[a] += 1
        deg[b] += 1
    for v in names:
        toks = [f"deg{min(deg[v], 3)}"]
        iv = names.index(v)
        if len(np.unique(X[:, iv])) <= 3:
            toks.append("discrete_response")
        # mediator-ness: does v translate any pair's link?
        is_med = False
        is_pre = False
        for a in names:
            for b in names:
                if a == b or v in (a, b):
                    continue
                if abs(np.corrcoef(X[:, names.index(a)],
                                   X[:, names.index(b)])[0, 1]) < 0.3:
                    continue
                r_ = i.explain_link(a, b, X, names)
                if any(z == v for z, _ in r_["mediators"]):
                    is_med = True
                if r_["preemptive"] == v:
                    is_pre = True
            if is_med and is_pre:
                break
        if is_med:
            toks.append("translator")
        if is_pre:
            toks.append("risk_carrier")
        skew = float(((X[:, iv] - X[:, iv].mean()) ** 3).mean()
                     / (X[:, iv].std() ** 3 + 1e-9))
        if abs(skew) > 0.9:
            toks.append("skewed_source")
        role_tokens[v] = toks
for v in ("rain", "fire_risk", "fireworks_ban", "breaker_trip", "birdsong"):
    print(f"    {v:14s}: {role_tokens[v]}")
check("responses read discrete across all worlds",
      all("discrete_response" in role_tokens[v]
          for v in ("fireworks_ban", "breaker_trip", "fever_response")))
check("risk variables read as risk carriers",
      sum("risk_carrier" in role_tokens[v]
          for v in ("fire_risk", "failure_risk", "illness_risk")) >= 2)

# ── C2: the crystallizer mints the cross-world concepts ─────────────
print("\nC2 — the EXISTING crystallizer, one level up")
for v, toks in role_tokens.items():
    for t in toks:
        i.observe([v, t])
        i.observe([v, t])          # repeatable evidence
i.crystallize()
sound = [t for t in i.types.values() if t.get("verdict") == "sound"]
resp_type = [t for t in sound
             if {"fireworks_ban", "breaker_trip",
                 "fever_response"} <= t["members"]]
check("ONE concept holds ban+trip+fever (zero shared vocabulary)",
      len(resp_type) >= 1,
      resp_type[0]["name"] if resp_type else f"{len(sound)} sound types")
cross = sum(1 for t in sound
            if len({w for w in ("rain dryness fire_risk fireworks_ban",
                                "load heat failure_risk breaker_trip",
                                "stress cortisol illness_risk fever_response")
                    if any(m in w for m in t["members"])}) >= 2)
check("multiple concepts span worlds", cross >= 2, f"{cross} cross-world")

# ── C3: name it once, ask anywhere ──────────────────────────────────
print("\nC3 — the concept is nameable")
if resp_type:
    tname = resp_type[0]["name"]
    i.teach(tname, "is_a", "preemptive_responder")
    members = sorted(resp_type[0]["members"])
    print(f"    {tname} named preemptive_responder; members: {members}")
    check("queryable via the net",
          "preemptive_responder" in i.fact_index.get((tname, "is_a"), []))
else:
    check("queryable via the net", False, "no concept to name")

# ── C4: bystanders stay out ─────────────────────────────────────────
print("\nC4 — bystanders join no role concept")
lonely = all(not any({"birdsong", "paint", "shoe"} & t["members"]
                     and len(t["members"] - {"birdsong", "paint", "shoe"}) > 0
                     for t in sound if len(t["members"]) >= 3)
             for _ in [0])
check("bystanders not absorbed into role concepts", lonely)

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nCONCEPTS BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
