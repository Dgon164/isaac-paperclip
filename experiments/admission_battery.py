# -*- coding: utf-8 -*-
"""ADMISSION BATTERY — A2 + A4: tests replace thresholds in the crystallizer
(2026-07-04). What the crystallizer battery pins (C1-C6) stays pinned; THIS
battery pins the new machinery itself.

A2a  degrees-aware verdict  -> clean categories carry p < 0.01; chance types
                               carry p >= 0.01 with the why naming degrees
A2b  hierarchy sound-gating -> wrong-verdict types do not mint hierarchy
A2c  rules chance gate      -> co-occurrence rules need significance
A4a  provisional lockout    -> one negative observation locks, labeled honest
A4b  confirmed lockout      -> repeated negatives upgrade to confirmed
A4c  retraction             -> positive evidence retracts a lockout into
                               wrong_lockouts with the why; net keeps the door
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

rng = np.random.default_rng(9)

# ── A2a: the verdict is a test with a p-value ───────────────────────
print("\nA2a — degrees-aware admission verdicts")
i = Isaac()
for animal in ("cat", "dog", "bird", "fish"):
    for _ in range(2):
        i.observe(["the", animal, "ran"])
        i.observe(["a", animal, "slept"])
i.crystallize()
sound = [t for t in i.types.values() if t.get("verdict") == "sound"]
check("clean categories admitted with p < 0.01",
      any(t.get("p_chance", 1) < 0.01 and {"cat", "dog"} <= t["members"]
          for t in sound),
      f"{len(sound)} sound types")

j = Isaac()
pool = [f"p{k}" for k in range(30)]
for k in range(40):
    for p in rng.choice(30, 4, replace=False):
        j.observe([f"e{k}", pool[p]])
j.consolidate()
wrongs = list(j.wrong_types.values())
check("chance co-occurrence filed wrong with degrees in the why",
      len(wrongs) > 0 and all("degrees" in w.get("why_wrong", "")
                              for w in wrongs),
      f"{len(wrongs)} wrong, {sum(1 for t in j.types.values() if t.get('verdict')=='sound')} sound")

# ── A2b: wrong types do not organize ────────────────────────────────
print("\nA2b — hierarchy needs soundness (or significance)")
chance_links = sum(1 for t in j.types.values()
                   if t.get("verdict") == "wrong" and t.get("parent"))
check("no wrong-verdict type minted a parent link", chance_links == 0,
      f"{chance_links} chance hierarchy links")

# ── A2c: rules face the chance gate ─────────────────────────────────
print("\nA2c — rules gate")
check("chance context mints few/no co-occurrence rules",
      len(j.rules) <= 2, f"{len(j.rules)} rules from noise")

# ── A4: evidence-weighted, revisable lockouts ───────────────────────
print("\nA4 — lockouts: provisional / confirmed / retracted")
k = Isaac()
k.observe(["the", "cat", "sat"])
k.observe_negative(["cat", "the"])           # one negative observation
k.crystallize()
p1 = k.lockout_status.get(("cat", "the"))
check("one negative -> ACTIVE provisional lockout",
      ("cat", "the") in k.lockouts and p1 == "provisional", f"status={p1}")

k.observe_negative(["dog", "the"])
k.observe_negative(["dog", "the"])           # repeated negative
k.crystallize()
p2 = k.lockout_status.get(("dog", "the"))
check("repeated negatives -> confirmed", p2 == "confirmed", f"status={p2}")

k.observe(["cat", "the", "end"])             # positive evidence arrives
k.crystallize()
check("contradicted lockout RETRACTED from the active set",
      ("cat", "the") not in k.lockouts)
check("retraction recorded with the why (wrong_lockouts)",
      "contradicted" in k.wrong_lockouts.get(("cat", "the"), ""),
      k.wrong_lockouts.get(("cat", "the"), "")[:50])
check("the net keeps the door (nothing leaves the net)",
      "lockout" in k.net.get_door_tags("cat", "the"))
check("uncontradicted lockout still active",
      ("dog", "the") in k.lockouts)

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nADMISSION BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
