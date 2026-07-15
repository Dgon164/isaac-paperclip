"""vet_intake_battery.py — INTERPRETED, NOT IMPLEMENTED (owner
design 2026-07-15). Battery written FIRST, per discipline.

The owner's design, verbatim: "if its something where we have a known
answer, vs the received answer, then he can check. so he can check
incoming grammar and math and stuff based off of what he expects and
assess whether its right or not. if he determines its wrong, he can
still acknowledge the assumed intent and continue but doesnt learn
the assumed flaw for integration. bad english is interpreted, but
not implemented."

The laws under test:
  - incoming claims are CHECKED against his expectations where any
    exist (known answers; sums via cross_check);
  - a claim that fails its check is INTERPRETED (assumed intent
    recorded as doors to the likely meant value — the typo concept)
    and the conversation can CONTINUE — but integrate=False: the
    flawed form NEVER reaches learning;
  - no expectation = UNCHECKABLE, which is the ORDINARY nulls road —
    neither a free pass nor a quarantine;
  - quarantine is WRONG-KEPT, not deletion: the original form
    verbatim + why + intent, persisted and supersedable;
  - end to end: teach only what the gate passes — the net holds the
    good fact, lacks the bad one, and the bad one is still READABLE
    from quarantine (interpreted, available; not implemented).

Checks Q1-Q6. Run: PYTHONHASHSEED=0 python vet_intake_battery.py
"""
import os
import sys

import numpy as np                                     # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" +
          (f"   {detail}" if detail else ""))


def main():
    print("=" * 70)
    print("VET-INTAKE BATTERY — interpreted, not implemented")
    print("=" * 70)
    m = mod.Isaac()

    # ── Q1: a wrong sum arrives as a lesson — interpreted, refused ──
    r = m.vet_intake([dict(name="lesson1", kind="sum",
                           values=dict(a=5, b=5, c=9),
                           cells=["a", "b"], total="c")])
    c1 = r["results"][0]
    ok = (c1["verdict"] == "FAILS-CHECK" and c1["integrate"] is False
          and len(c1["intent"]) == 3
          and c1["original"]["values"] == dict(a=5, b=5, c=9))
    check("Q1 5+5=9 arrives: FAILS-CHECK, integrate=False, 3 intent "
          "doors, original kept verbatim", ok,
          f"{c1['verdict']}, intent "
          f"{sorted((d['cell'], d['repaired']) for d in c1['intent'])}")

    # ── Q2: a right sum passes and may be learned ──
    r = m.vet_intake([dict(name="lesson2", kind="sum",
                           values=dict(a=5, b=5, c=10),
                           cells=["a", "b"], total="c")])
    c2 = r["results"][0]
    check("Q2 5+5=10 arrives: PASSES, integrate=True",
          c2["verdict"] == "PASSES" and c2["integrate"] is True)

    # ── Q3: known answer vs received answer ──
    r = m.vet_intake([dict(name="ans", kind="value", key="dozen",
                           received=13.0)],
                     expectations=dict(dozen=12.0))
    c3 = r["results"][0]
    ok = (c3["verdict"] == "FAILS-CHECK" and c3["integrate"] is False
          and c3["intent"][0]["repaired"] == 12.0
          and "intent" in c3["intent"][0]["why"].lower())
    check("Q3 expected 12, received 13: wrong by his own check; "
          "assumed intent = 12; not learned", ok,
          f"intent {c3['intent'][0]['observed']} -> "
          f"{c3['intent'][0]['repaired']}")

    # ── Q4: no expectation = UNCHECKABLE — the ordinary nulls road,
    #        never a free pass, never a quarantine ──
    r = m.vet_intake([dict(name="new", kind="value", key="sprocket",
                           received=7.0)])
    c4 = r["results"][0]
    check("Q4 no expectation: UNCHECKABLE, integrate='unchecked' "
          "(ordinary nulls road)",
          c4["verdict"] == "UNCHECKABLE"
          and c4["integrate"] == "unchecked")

    # ── Q5: quarantine persists, re-vetting supersedes ──
    m2 = mod.Isaac()
    m2.vet_intake([dict(name="bad", kind="sum",
                        values=dict(a=5, b=5, c=9),
                        cells=["a", "b"], total="c")], name="tutor")
    q1 = m2.net.get_meta("quarantine:tutor", "active")
    m2.vet_intake([dict(name="bad2", kind="value", key="dozen",
                        received=13.0)],
                  expectations=dict(dozen=12.0), name="tutor")
    chain = m2.net.get_meta("quarantine:tutor", "superseded") or []
    q2 = m2.net.get_meta("quarantine:tutor", "active")
    ok = (q1 and len(q1) == 1 and q1[0]["claim"] == "bad"
          and len(chain) == 1 and q2 and q2[0]["claim"] == "bad2")
    check("Q5 quarantine persists at quarantine:<name>; re-vet "
          "supersedes, old kept", ok,
          f"first {q1[0]['claim'] if q1 else '-'}, chain {len(chain)}")

    # ── Q6: END TO END — bad english interpreted, not implemented ──
    m3 = mod.Isaac()
    claims = [dict(name="good", kind="sum",
                   values=dict(a=2, b=3, c=5), cells=["a", "b"],
                   total="c", fact=("two_plus_three", "equals", "five")),
              dict(name="bad", kind="sum",
                   values=dict(a=5, b=5, c=9), cells=["a", "b"],
                   total="c", fact=("five_plus_five", "equals", "nine"))]
    r = m3.vet_intake(claims, name="lessons")
    for res in r["results"]:
        if res["integrate"] is True and res["original"].get("fact"):
            m3.teach(*res["original"]["fact"])
    learned_good = m3.fact_index.get(("two_plus_three", "equals"), [])
    learned_bad = m3.fact_index.get(("five_plus_five", "equals"), [])
    quar = m3.net.get_meta("quarantine:lessons", "active") or []
    ok = ("five" in learned_good and learned_bad == []
          and len(quar) == 1 and quar[0]["claim"] == "bad"
          and quar[0]["intent"])
    check("Q6 end to end: good fact taught; bad fact ABSENT from the "
          "net but readable in quarantine WITH its intent", ok,
          f"good {learned_good}, bad {learned_bad}, "
          f"quarantined {len(quar)} w/ {len(quar[0]['intent']) if quar else 0} doors")

    n_ok = sum(CHECKS)
    print("=" * 70)
    print(f"VET-INTAKE BATTERY: {n_ok}/{len(CHECKS)}")
    print("=" * 70)
    sys.exit(0 if n_ok == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
