"""Gravity-family battery — overlapping confusion (owner, 2026-07-12:
"earth gravity acceleration and jupiter or pluto? can the system
distinguish these?").

Same FORM (d = 1/2 g t^2), different CONSTANTS per planet. The traps:
smushing them into one law (forbidden: variants are real things), or
answering mixed data with a forced guess.

G1 Jupiter told after Earth -> a VARIANT in a form family, NOT a
   witness; both laws live, doored under one lawform parent
G2 Earth re-told with matching constant -> witness (that IS the same)
G3 which_law: fresh Earth data names earth; Jupiter data names
   jupiter (clear margins, ranking shown)
G4 Pluto data with NO Pluto law known -> NONE, new-variant candidate
   (abstention, not a guess); after telling Pluto it joins the
   family (3 variants) and is named correctly
G5 MIXED Earth+Jupiter data -> AMBIGUOUS/NONE, never a single-planet
   answer; split by context -> both resolve cleanly
G6 the old containment machinery still stands: relational circles
   (waves) and senses-as-nodes run in the same engine (suite areas)
Run: python gravity_family_battery.py   (from experiments/)
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from isaac_store import bridge  # noqa: E402

PASS = FAIL = 0
G = {"earth": 9.81, "jupiter": 24.79, "pluto": 0.62}


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def fall_data(rng, g, n=300, noise=0.01):
    t = rng.uniform(0.1, 10, (n, 1))
    d = 0.5 * g * t[:, 0] ** 2
    return t, d * (1 + rng.normal(0, noise, n))


def main():
    print("  loading engine...")
    mod = bridge.load_isaac_module()
    rng = np.random.default_rng(21)
    i = mod.Isaac()

    print("G1. same form, different constant -> VARIANT, not witness")
    i.tell_law("fall_earth", f"+{0.5 * G['earth']:.4f}*x0^2", d=1)
    r = i.tell_law("fall_jupiter", f"+{0.5 * G['jupiter']:.4f}*x0^2", d=1)
    check("Jupiter enters as VARIANT with Earth as sibling",
          r["status"] == "VARIANT" and r["sibling"] == "fall_earth")
    fam = r["family"]
    members = i.net.doors.get(fam, set())
    check("both laws doored under one lawform parent",
          members == {"law:fall_earth", "law:fall_jupiter"}, fam)
    check("both laws independently applicable",
          i.apply_law("fall_earth", np.array([[2.0]]))[0] !=
          i.apply_law("fall_jupiter", np.array([[2.0]]))[0])

    print("G2. matching constant -> witness (that IS the same law)")
    r2 = i.tell_law("earth_again", "+4.9080*x0^2", d=1)  # within 5% of 4.905
    check("re-telling Earth's constant files as witness",
          r2["status"] == "MATCHES" and r2["law"] == "fall_earth")

    print("G3. which planet is this data from?")
    te, de = fall_data(rng, G["earth"])
    tj, dj = fall_data(rng, G["jupiter"])
    we = i.which_law(te, de)
    wj = i.which_law(tj, dj)
    check("Earth data names earth", we["verdict"] == "MATCH"
          and we["law"] == "fall_earth", f"ranking {we['ranking']}")
    check("Jupiter data names jupiter", wj["verdict"] == "MATCH"
          and wj["law"] == "fall_jupiter", f"ranking {wj['ranking']}")

    print("G4. unknown planet -> abstain, then learn it")
    tp, dp = fall_data(rng, G["pluto"])
    wp = i.which_law(tp, dp)
    check("Pluto data with no Pluto law -> NONE (new-variant candidate)",
          wp["verdict"].startswith("NONE"), f"ranking {wp['ranking']}")
    rp = i.tell_law("fall_pluto", f"+{0.5 * G['pluto']:.4f}*x0^2", d=1)
    check("Pluto joins the same family as a third variant",
          rp["status"] == "VARIANT" and rp["family"] == fam
          and len(i.net.doors[fam]) == 3)
    wp2 = i.which_law(tp, dp)
    check("now Pluto data names pluto", wp2["verdict"] == "MATCH"
          and wp2["law"] == "fall_pluto")

    print("G5. mixed-planet data -> confusion DETECTED, never guessed")
    tm = np.vstack([te, tj])
    dm = np.concatenate([de, dj])
    wm = i.which_law(tm, dm)
    check("mixed data refuses a single-planet answer",
          wm["verdict"] != "MATCH", f"{wm['verdict']} {wm['ranking'][:2]}")
    split_e = i.which_law(tm[:300], dm[:300])
    split_j = i.which_law(tm[300:], dm[300:])
    check("split by context -> both resolve cleanly",
          split_e["law"] == "fall_earth" and split_j["law"] == "fall_jupiter")

    print("G6. the old containment machinery still stands")
    import isaac as eng
    circles = hasattr(i, "wave_consolidate") and hasattr(eng, "_wave_circles")
    check("relational circles (waves) present in the same engine", circles)
    check("laws + families live beside them, one net",
          fam in i.net.doors and "findings" in i.net.doors)

    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
