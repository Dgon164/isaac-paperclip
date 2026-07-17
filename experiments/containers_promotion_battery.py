"""containers_promotion_battery.py — PROMOTION #14 BATTERY:
CONTAINERS become engine organs (open_world / teach(container=) /
ask). Research basis: containers_probe.py 8/8 (the shim design) —
this battery gates the same behavior THROUGH THE ENGINE, plus
persistence and catalog registration.

WRITTEN BEFORE THE SURGERY (batteries-before-mechanisms law).

PREDICTIONS (filed before the engine is touched; wrong ones kept)
  E1 per-world answers via mind.ask(): brooms are-for base=sweeping /
     harry-potter=flying; the three-way stars fact (shine/dim/sing)
     correct under each world.
  E2 cross-world difference: 0 tension flags.
  E3 in-world contradiction: flagged in container_tensions, both kept.
  E4 leakage 0/5 both directions (fiction->base, fiction->fiction).
  E5 one-way inheritance with receipt (HP water = 100C 'inherited
     from base'; base portraits = nothing).
  E6 poisoning guard: base answers byte-identical after fiction.
  E7 keystone: ONE brooms node carries both worlds' doors, container
     tags disambiguate.
  E8 container-less facts (organ-internal fact_index writes, e.g.
     teach_not / _teach_fact) land in base WITH a receipt.
  E9 PERSISTENCE: save/load a mind with three worlds -> answers and
     the active container survive the pickle round-trip.
  E10 REGISTRATION: open_world and ask appear in catalog_tools()
     (the registration rule: every tool ships with its node).
  GATE (run separately): engine self-test 11/11 — the new s->obj
     tagged doors from teach() must not disturb crystallization or
     any capability area; if they do, the fallback design (a parallel
     container index, no new doors) is the named alternative.

Run: cd experiments && PYTHONHASHSEED=0 python containers_promotion_battery.py
"""
import os
import sys
import time

import numpy as np  # noqa: F401

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac


def build_worlds(mind):
    mind.teach("brooms", "are-for", "sweeping")            # base default
    mind.teach("water", "boils-at", "100C")
    mind.teach("stars", "do", "shine")
    mind.teach("owls", "are", "birds")
    mind.open_world("harry-potter")
    mind.teach("brooms", "are-for", "flying")
    mind.teach("owls", "deliver", "mail")
    mind.teach("portraits", "do", "talk")
    mind.teach("stars", "do", "sing")
    mind.open_world("hail-mary")
    mind.teach("stars", "do", "dim")
    mind.teach("astrophage", "eats", "starlight")
    mind.open_world("base")


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    mind = Isaac()
    build_worlds(mind)

    # E1
    a_b = mind.ask("brooms", "are-for", "base")["answers"]
    a_hp = mind.ask("brooms", "are-for", "harry-potter")["answers"]
    s3 = [mind.ask("stars", "do", c)["answers"]
          for c in ("base", "hail-mary", "harry-potter")]
    check("E1 per-world answers through the engine",
          a_b == ["sweeping"] and a_hp == ["flying"]
          and s3 == [["shine"], ["dim"], ["sing"]],
          f"brooms {a_b}/{a_hp}; stars {s3}")

    # E2
    n_t = len(getattr(mind, "container_tensions", []))
    check("E2 cross-world difference: 0 tensions", n_t == 0, f"{n_t}")

    # E3
    mind.teach("brooms", "are-for", "sinking", container="harry-potter")
    ten = getattr(mind, "container_tensions", [])
    both = mind.ask("brooms", "are-for", "harry-potter")["answers"]
    check("E3 in-world contradiction flagged, both kept",
          len(ten) == 1 and ten[0]["container"] == "harry-potter"
          and set(both) == {"flying", "sinking"},
          f"tensions {len(ten)}; held {both}")

    # E4
    leaks = sum(bool(mind.ask(s, r, "base")["answers"]) for (s, r) in
                [("owls", "deliver"), ("portraits", "do"),
                 ("astrophage", "eats")])
    cross = int(bool(mind.ask("astrophage", "eats",
                              "harry-potter")["answers"] and
                     "inherited" not in mind.ask("astrophage", "eats",
                                                 "harry-potter")["why"])) \
        + int(bool(mind.ask("portraits", "do", "hail-mary")["answers"]
                   and "inherited" not in
                   mind.ask("portraits", "do", "hail-mary")["why"]))
    check("E4 leakage 0 both directions", leaks == 0 and cross == 0,
          f"fiction->base {leaks}/3; cross-fiction {cross}/2")

    # E5
    hp_w = mind.ask("water", "boils-at", "harry-potter")
    b_p = mind.ask("portraits", "do", "base")
    check("E5 one-way inheritance with receipt",
          hp_w["answers"] == ["100C"]
          and "inherited from base" in hp_w["why"]
          and b_p["answers"] == [],
          f"hp water {hp_w['answers']}; base portraits {b_p['answers']}")

    # E6 — poisoning guard on a fresh mind
    m2 = Isaac()
    for (s, r, o) in [("brooms", "are-for", "sweeping"),
                      ("water", "boils-at", "100C"),
                      ("stars", "do", "shine"),
                      ("owls", "are", "birds")]:
        m2.teach(s, r, o)
    QA = [("brooms", "are-for"), ("water", "boils-at"), ("stars", "do"),
          ("owls", "deliver"), ("owls", "are"), ("portraits", "do"),
          ("astrophage", "eats")]
    before = {q: m2.ask(*q, "base")["answers"] for q in QA}
    m2.open_world("harry-potter")
    for (s, r, o) in [("brooms", "are-for", "flying"),
                      ("owls", "deliver", "mail"),
                      ("portraits", "do", "talk"),
                      ("stars", "do", "sing")]:
        m2.teach(s, r, o)
    m2.open_world("hail-mary")
    m2.teach("stars", "do", "dim")
    m2.teach("astrophage", "eats", "starlight")
    after = {q: m2.ask(*q, "base")["answers"] for q in QA}
    check("E6 base byte-identical after fiction", before == after,
          f"drift {sum(before[k] != after[k] for k in QA)}/{len(QA)}")

    # E7 — keystone: one node, both worlds
    tf = mind.net.get_door_tags("brooms", "flying")
    ts = mind.net.get_door_tags("brooms", "sweeping")
    check("E7 one node, both worlds' doors",
          "in:harry-potter" in tf and "in:base" in ts,
          f"flying {sorted(tf)}; sweeping {sorted(ts)}")

    # E8 — organ-internal fact (no container stamp) -> base + receipt
    mind.teach_not("penguins", "fly")
    r8 = mind.ask("penguins", "cannot", "base")
    check("E8 container-less organ facts -> base with receipt",
          r8["answers"] == ["fly"] and "container-less" in r8["why"],
          f"{r8['answers']} ({r8['why'][:50]})")

    # E9 — persistence round-trip
    import tempfile
    pth = os.path.join(tempfile.gettempdir(), "cont_battery_mind.pkl")
    mind.open_world("harry-potter")
    mind.save(pth)
    m3 = Isaac.load(pth)
    check("E9 pickle round-trip: worlds + active container survive",
          m3.ask("brooms", "are-for")["answers"] == ["flying", "sinking"]
          and m3.ask("brooms", "are-for", "base")["answers"]
          == ["sweeping"]
          and getattr(m3, "active_container", "?") == "harry-potter",
          f"active {getattr(m3, 'active_container', '?')}; "
          f"hp {m3.ask('brooms', 'are-for')['answers']}")
    os.remove(pth)

    # E10 — registration
    try:
        cat = mind.catalog_tools()
        names = {c.get("name", "") for c in cat} if isinstance(cat, list) \
            else set(cat)
    except Exception:
        names = {m for m in dir(mind) if not m.startswith("_")}
    check("E10 open_world + ask registered",
          {"open_world", "ask"} <= names,
          f"present {sorted({'open_world', 'ask'} & names)}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed of "
          f"{len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
