# -*- coding: utf-8 -*-
"""UPTAKE BATTERY — C1: wholes with arrangement, IN THE ENGINE (2026-07-04).

Mirrors rebuild B's (a)-(g) — previously provable only in the harness — as
net structure: offer:/uptake:/whole: nodes, fixed-point operability read
from doors. Plus the learned side: wave handoffs mint the same uptake
structure, so circles carry arrangement without being taught.

U-a  emergent function operable at the whole
U-b  inoperable in every individual part
U-c  dismantled aggregate (same parts, no edges) lacks it
U-d  same parts, different arrangement -> different whole, no function
U-e  identity deterministic across assembly order
U-f  decomposition recovers the parts
U-g  wholes are first-class: engine + wheels -> car affords locomotion
U-h  LEARNED arrangement: wave circle mints uptake edges from handoffs
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

results = []
def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

# ── the taught engine world ─────────────────────────────────────────
i = Isaac()
i.register_part("tank", {"fuel": ()})
i.register_part("spark", {"ignition": ()})
i.register_part("piston", {"torque": ("fuel", "ignition")})
parts = ["tank", "spark", "piston"]

engine = i.assemble("engine", parts,
                    [("tank", "fuel", "piston"),
                     ("spark", "ignition", "piston")])
miswired = i.assemble("miswired", parts,
                      [("tank", "fuel", "spark"),
                       ("spark", "ignition", "tank")])
pile = i.assemble("pile", parts, [])

print("\nU-a..d — emergence lives in the arrangement")
check("(a) whole affords torque", "torque" in i.operable(engine),
      str(sorted(i.operable(engine))))
check("(b) torque inoperable in every part alone",
      all("torque" not in i.part_operable(p) for p in parts))
check("(c) dismantled pile lacks torque", "torque" not in i.operable(pile))
check("(d) rewired whole differs and loses torque",
      i.net.get_meta(engine, "identity") != i.net.get_meta(miswired, "identity")
      and "torque" not in i.operable(miswired))
check("emergent() names exactly the new capability",
      i.emergent(engine) == {"torque"}, str(i.emergent(engine)))

print("\nU-e..f — determinism and decomposition")
j = Isaac()
for p, off in [("piston", {"torque": ("fuel", "ignition")}),
               ("tank", {"fuel": ()}), ("spark", {"ignition": ()})]:
    j.register_part(p, off)
eng2 = j.assemble("engine", ["piston", "spark", "tank"],
                  [("spark", "ignition", "piston"),
                   ("tank", "fuel", "piston")])
check("(e) same identity from a different assembly order",
      j.net.get_meta(eng2, "identity") == i.net.get_meta(engine, "identity"))
check("(f) decomposition recovers the parts",
      i.dismantle(engine) == set(parts))

print("\nU-g — first-class upward composition")
i.whole_as_part(engine)
i.register_part("wheels", {"traction": ()})
i.register_part("frame", {"locomotion": ("torque", "traction")})
car = i.assemble("car", [engine, "wheels", "frame"],
                 [(engine, "torque", "frame"),
                  ("wheels", "traction", "frame")])
check("(g) engine composes upward -> car affords locomotion",
      "locomotion" in i.operable(car), str(sorted(i.operable(car))))

print("\nU-h — LEARNED arrangement: wave handoffs mint uptake edges")
k = Isaac()
k.wave_logging = False
groups = [("a1", "a2"), ("b1", "b2"), ("c1", "c2")]
for t in range(1200):
    k.tick(set(groups[(t // 4) % 3]))
k.wave_consolidate(verbose=False)
uptakes = [n for n in k.net.all_nodes()
           if isinstance(n, str) and n.startswith("uptake:")]
circles = [n for n in k.net.all_nodes()
           if isinstance(n, str) and n.startswith("circle:")]
check("handoffs minted uptake nodes", len(uptakes) >= 3, f"{len(uptakes)} uptake nodes")
arranged = circles and any(k.net.get_doors(c, tag="arranges") for c in circles)
check("the circle ARRANGES its uptake edges (learned whole)",
      bool(arranged), f"{len(circles)} circles")

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nUPTAKE BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
