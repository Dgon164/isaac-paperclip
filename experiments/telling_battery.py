"""telling_battery.py — PROMOTION GATE for THE TELLING ROAD
(owner, 2026-07-18 evening: "if he could just interpret 'ohm's law
is v=ir' and he would create a node for ohms law containing v=ir
and will use it but validate with more information later").

The organ under test (isaac_store/telling.py) is TRANSLATION + VET
ONLY — knowledge lands through the promoted doors (tell_law + the
curriculum's application fact-bundle). Pins:

  T1  THE OWNER'S SENTENCE: "ohm's law is v=ir" parses to the
      canonical grammar and echoes back in the teller's letters.
  T2  POWERS + PI: a^1.5 and pi*r^2 read exactly.
  T3  DIVISION: m/v reads as a negative power.
  T4  TERMS: 3x^2-2x+7 keeps its signs and its intercept.
  T5  THE REFUSALS, LOUD: gibberish, self-reference, functions/
      parentheses, ambiguous /ab, multi-letter output, constants.
  T6  THE LANDING: a fresh telling is TOLD-UNVERIFIED, wears
      who=owner, binds output/slots/uses-form as facts, and is
      USABLE AT ONCE via apply_law.
  T7  THE SHAPES LAW: rect-area told first, ohm told second —
      tell_law answers MATCHES (one form, two labels), and
      recall_law still renders "v = +1*i*r" BY NAME. The name
      survives the shared shape.
  T8  THE NAME VET: retelling a held name with a DIFFERENT form
      refuses — supersession is the duel's job.
  T9  VARIANTS: same form, different constant -> a family, never
      a smush (earth g vs jupiter g).
  T10 PERSISTENCE: the told law + its name survive save/load.
  T11 CONTAINERS: a telling lands in the world it was told in.
  T12 VALIDATE LATER (the owner's whole ask, end to end): the told
      ohm HOLDS on clean v=ir rows via validate_law, and FAILS on
      rows from a different world — belief measured, never told.

Run: cd experiments && PYTHONHASHSEED=0 python telling_battery.py
"""
import os
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
import isaac as isaac_mod                          # noqa: E402
from isaac_store.telling import (parse_told_law,   # noqa: E402
                                 tell_english, recall_law)

Isaac = isaac_mod.Isaac


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(bool(ok))
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    # T1 the owner's sentence
    g = parse_told_law("ohm's law is v=ir")
    ok = (g.get("name") == "ohms-law" and g.get("output") == "v"
          and g.get("slots") == ["i", "r"]
          and g.get("positional") == "+1*x0*x1"
          and g.get("said") == "v = +1*i*r")
    check("T1 \"ohm's law is v=ir\"", ok, f"{g.get('said')} "
          f"(name {g.get('name')}, slots {g.get('slots')})")

    # T2 powers + pi
    k = parse_told_law("kepler's law is t=a^1.5")
    c = parse_told_law("circle area is a=pi*r^2")
    ok = (k.get("positional") == "+1*x0^1.5"
          and c.get("positional", "").startswith("+3.14159")
          and c.get("positional", "").endswith("*x0*x0"))
    check("T2 powers + pi", ok,
          f"kepler {k.get('positional')}, circle "
          f"{c.get('positional')}")

    # T3 division
    d = parse_told_law("density is d=m/v")
    check("T3 division -> negative power",
          d.get("positional") == "+1*x0*x1^-1",
          f"{d.get('said')}")

    # T4 terms + intercept
    ln = parse_told_law("some line is y=3x^2-2x+7")
    check("T4 terms keep signs + intercept",
          ln.get("positional") == "+3*x0*x0 -2*x0 +7",
          f"{ln.get('positional')}")

    # T5 the refusals, loud
    bad = [
        ("just words with no equation", "not a telling"),
        ("weird is v=vr", "both sides"),
        ("fn is v=sin(i)", "vocabulary"),
        ("amb is v=k/ir", "ambiguous"),
        ("wide is vol=m", "single quantity letter"),
        ("const is y=3", "constant, not a law"),
    ]
    oks, why = [], []
    for txt, frag in bad:
        r = parse_told_law(txt)
        oks.append("refused" in r and frag in r["refused"])
        why.append(r.get("refused", "NOT REFUSED")[:22])
    check("T5 six refusals, each naming its why", all(oks),
          "; ".join(why[:3]) + " ...")

    # T6 the landing
    m = Isaac()
    r6 = tell_english(m, "ohm's law is v=ir", who="owner")
    st = m.net.get_meta("law:ohms-law", "status")
    pred = m.apply_law("ohms-law", np.array([[2.0, 3.0]]))
    ok = (r6["tell"]["status"] == "TOLD-UNVERIFIED"
          and st["state"] == "TOLD-UNVERIFIED"
          and st["provenance"] == "owner"
          and m.ask("ohms-law", "output")["answers"] == ["v"]
          and m.ask("ohms-law", "slots")["answers"] == ["i,r"]
          and pred is not None and abs(float(pred[0]) - 6.0) < 1e-9)
    check("T6 lands TOLD-UNVERIFIED, who=owner, facts bound, "
          "usable at once", ok,
          f"state {st['state']}, v(2,3)={float(pred[0]):.1f}")

    # T7 the shapes law: the name survives the shared form
    m7 = Isaac()
    tell_english(m7, "rectangle area is a=wh", who="owner")
    r7 = tell_english(m7, "ohm's law is v=ir", who="owner")
    back = recall_law(m7, "ohm's law")
    ok = (r7["tell"]["status"] == "MATCHES"
          and r7["form"] == "rectangle-area"
          and back is not None and back["said"] == "v = +1*i*r"
          and back["state"] == "TOLD-UNVERIFIED"
          and back["witnesses"] == 1)
    check("T7 ohm MATCHES rect-area's shape, name recallable",
          ok, f"form {r7.get('form')}, recalled '{back['said'] if back else None}'")

    # T8 the name vet
    r8 = tell_english(m7, "ohm's law is v=i*r^2", who="owner")
    check("T8 held name + different form -> the duel's job, "
          "refused", "refused" in r8 and "duel" in r8["refused"],
          r8.get("refused", "NOT REFUSED")[:52])

    # T9 variants make a family
    m9 = Isaac()
    tell_english(m9, "earth gravity is f=9.8*m", who="owner")
    r9 = tell_english(m9, "jupiter gravity is f=24.8*m",
                      who="owner")
    check("T9 same form, different constant -> VARIANT family",
          r9["tell"]["status"] == "VARIANT",
          f"{r9['tell'].get('status')} family "
          f"{r9['tell'].get('family', '?')[:20]}")

    # T10 persistence
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "m.isaac")
        m7.save(p)
        b10 = recall_law(Isaac.load(p), "ohms-law")
        ok = b10 is not None and b10["said"] == "v = +1*i*r" \
            and b10["witnesses"] == 1
    check("T10 the told name survives save/load", ok,
          f"recalled '{b10['said'] if b10 else None}'")

    # T11 containers
    m11 = Isaac()
    tell_english(m11, "boyle's law is p=1413.86/v", who="owner",
                 container="told-gases")
    ok = (m11.net.get_meta("law:boyles-law", "container")
          == "told-gases")
    check("T11 a telling lands in its world", ok,
          f"container {m11.net.get_meta('law:boyles-law', 'container')}")

    # T12 validate later — the whole ask, end to end
    m12 = Isaac()
    tell_english(m12, "ohm's law is v=ir", who="owner")
    rng = np.random.default_rng(5)
    I = rng.uniform(0.1, 5, 60)
    R = rng.uniform(1, 100, 60)
    holds = m12.validate_law("ohms-law",
                             np.column_stack([I, R]), I * R)
    fails = m12.validate_law("ohms-law",
                             np.column_stack([I, R]),
                             I + R ** 2)
    ok = holds["status"] == "HOLDS" and fails["status"] == "FAILS"
    check("T12 told law validates on real rows, fails on a lie",
          ok, f"clean {holds['status']} (r2 {holds['r2']:.4f}), "
              f"wrong-world {fails['status']}")

    # T13 cross-container names + the retelling road (session-1
    # dry-prove finds): a name taught in a WORLD is still seen by
    # the vet and recall from base; a retelling of a held name
    # lands as a witness on HIS OWN node, never on a same-form
    # stranger the scan meets first
    m13 = Isaac()
    tell_english(m13, "galileo fall is d=33.08*t*t", who="owner")
    tell_english(m13, "circle area is a=pi*r^2", who="geometry",
                 container="cad")
    r13a = tell_english(m13, "circle area is a=pi*r^2",
                        who="owner")            # retell from base
    b13 = recall_law(m13, "circle area")
    r13b = tell_english(m13, "circle area is a=r^3", who="owner")
    ok = (r13a["tell"]["status"] == "MATCHES"
          and r13a["tell"].get("retold")
          and r13a["form"] == "circle-area"
          and b13 is not None and b13["witnesses"] == 1
          and b13["container"] == "cad"
          and "refused" in r13b and "duel" in r13b["refused"])
    check("T13 world-taught name seen from base; retell = witness "
          "on HIS node; new form refused", ok,
          f"retold form {r13a.get('form')}, witnesses "
          f"{b13['witnesses'] if b13 else '?'}, container "
          f"{b13['container'] if b13 else '?'}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} "
          f"failed of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
