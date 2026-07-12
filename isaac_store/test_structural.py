"""Multicycle structural patterning battery.

S1 CHAIN: a strict pipeline -> chain type, the links in the chart
S2 CYCLE: a rotation -> cycle type with the measured period
S3 HIERARCHY: nested open/close -> balanced pair found
S4 BRANCH: a checkpoint that forks -> the flow chart says so
S5 NOISE REFUSES: shuffled junk -> NO STRUCTURE, 10 seeds, 0 false
S6 MULTICYCLE: two motifs alternating -> level 1 finds the chains,
   level 2 finds the CYCLE of collapsed motifs (the tower)
S7 TEXT ROAD: templated prose with varying slots -> the constant
   structure emerges as a chart, slots as slots
Run: python test_structural.py   (from isaac_store/)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store.structural import analyze

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def main():
    rng = np.random.default_rng(61)

    print("S1. chain")
    seq = []
    for _ in range(12):
        seq += ["intake", "wash", "dry", "pack"]
    r = analyze(seq)
    lv = r["levels"][0]
    check("pipeline admitted as structure",
          "always_follows" in lv["constraints"])
    check("the links are in the chart",
          "intake -> wash" in lv["chart"] and "dry -> pack" in lv["chart"])

    print("S2. cycle")
    r2 = analyze(["red", "green", "blue"] * 15)
    check("rotation -> CYCLE with the period",
          r2["levels"][0]["pattern"] == "CYCLE"
          and r2["levels"][0]["constraints"]["global_period"] == 3)

    print("S3. hierarchy")
    seq3 = []
    for _ in range(6):
        seq3 += ["open", "open", "leaf", "close", "open", "leaf",
                 "close", "close"]
    r3 = analyze(seq3)
    check("nesting -> HIERARCHY with the pair",
          r3["levels"][0]["pattern"] == "HIERARCHY"
          and ("close", "open") in
          [tuple(sorted(p)) for p in
           r3["levels"][0]["constraints"]["balanced_pairs"]])

    print("S4. branch — the flow chart")
    seq4 = []
    for i in range(20):  # random outcomes: a true fork, not a cycle
        seq4 += ["job", "check",
                 ("fail" if rng.random() < 0.3 else "pass"), "done"]
    r4 = analyze(seq4)
    lv4 = r4["levels"][0]
    check("the fork is admitted",
          "forks" in lv4["constraints"]
          and sorted(lv4["constraints"]["forks"].get("check", [])) ==
          ["fail", "pass"])
    check("the chart draws it",
          any("check -> {fail | pass}" in c for c in lv4["chart"]))

    print("S5. noise refuses (10 seeds)")
    false_hits = 0
    for s in range(10):
        junk = list(np.random.default_rng(s).choice(
            list("abcdefghijklmnop"), size=120))
        if analyze(junk)["pattern"] != "NO STRUCTURE":
            false_hits += 1
    check("0/10 false structures on shuffled junk", false_hits == 0,
          f"{false_hits}/10")

    print("S6. the multicycle tower")
    # fixed irregular fillers: every filler follows both motifs and
    # precedes both, so nothing is accidentally deterministic — and
    # no global period exists
    after_z = ["m", "n", "w", "k", "m", "n", "w", "k", "m", "n", "w", "k"]
    after_r = ["n", "m", "k", "w", "k", "w", "m", "n", "w", "k", "n", "m"]
    seq6 = []
    for i in range(12):
        seq6 += ["x", "y", "z", after_z[i], "p", "q", "r", after_r[i]]
    r6 = analyze(seq6)
    check("level 1 finds the motif chains",
          "always_follows" in r6["levels"][0]["constraints"])
    lv2 = r6["levels"][1] if len(r6["levels"]) > 1 else {"constraints": {}}
    per2 = lv2["constraints"].get("periodic", {})
    check("level 2: the COLLAPSED motifs beat on a regular rhythm",
          len(r6["levels"]) >= 2
          and per2.get("<x·y·z>") == 4 and per2.get("<p·q·r>") == 4,
          f"tower: {r6['tower']}")

    print("S7. the text road")
    text = " ".join(f"open the file {n} . read the file {n} . "
                    f"close the file {n} ."
                    for n in ["alpha", "beta", "gamma", "delta",
                              "epsilon", "zeta"])
    r7 = analyze(text)
    lv7 = r7["levels"][0]
    links = lv7["constraints"].get("always_follows", {})
    check("templated prose admits its skeleton",
          links.get("open") == "the" and links.get("read") == "the"
          and links.get("close") == "the")
    check("the varying names became the slot atom",
          any("<slot>" in c for c in lv7["chart"]))
    check("structure found, not memorized names",
          "alpha" not in str(lv7["chart"]))
    print()
    print("  the flow chart from S4:", " ; ".join(lv4["chart"]))
    print("  the text chart from S7:", " ; ".join(lv7["chart"][:6]))
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
