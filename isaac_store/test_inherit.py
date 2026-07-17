"""test_inherit.py — THE FIRST TEACHER battery (owner, 2026-07-17:
"the alpha version needs to start from the start. we can use the
information it has already learned to see if it can learn from
developed sources and improve actual one shot through direct telling
or not"). Written FIRST, per discipline; the mechanism is built to
pass it.

Under test: a predecessor mind's net extracted into TELLABLE material
and fed to a FRESH mind through the standard doors — teach() with
world stamps preserved, tell_law() landing told-unverified (usable at
once, NO inherited belief — belief is earned by the successor's own
data), refusals loud with their why, complete numbers, provenance on
the record. The net is a build artifact; what is inherited is
EXPERIENCE AS TELLING, never belief.

Checks I1-I9. Run: PYTHONHASHSEED=0 python test_inherit.py
"""
import json
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from isaac_store.inherit import (extract_teachings, ingest_teachings,
                                 inherit_account)          # noqa: E402
from isaac_store import bridge                             # noqa: E402

PASSED, FAILED = 0, 0
rng = np.random.default_rng(21)


def check(name, ok, detail=""):
    global PASSED, FAILED
    PASSED, FAILED = PASSED + ok, FAILED + (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
          + (f"   {detail}" if detail else ""))


def build_predecessor(mod):
    """A small planted life: base facts, one fiction-world fact, one
    honestly discovered law, one WRONG told law, one law outside the
    telling vocabulary (planted bogus equation)."""
    old = mod.Isaac()
    old.teach("water", "state", "liquid")
    old.teach("sky", "color", "blue")
    old.teach("broom", "can", "fly", container="hp")
    x = rng.uniform(0, 10, 240).reshape(-1, 1)
    y = 2.0 * x[:, 0] + rng.normal(0, 0.02, 240)
    old.discover(x, y, name="double")
    old.tell_law("wrongy", "+9.99*x0 +0.00", d=1)
    old.net.add_door("law", "law:alien", tag="law")
    old.net.set_meta("law:alien", "model", dict(d=1, terms=[],
                                                coefs=[]))
    old.net.set_meta("law:alien", "equation", "+1.00*zorp(x0) +0.00")
    return old


def main():
    print("=" * 70)
    print("INHERIT BATTERY — the predecessor as the first teacher")
    print("=" * 70)
    mod = bridge.load_isaac_module()
    old = build_predecessor(mod)

    # ── I1: extraction — facts with worlds, laws with equations ──
    t = extract_teachings(old)
    fset = {(f["subject"], f["relation"], f["obj"], f["world"])
            for f in t["facts"]}
    lnames = {l["name"] for l in t["laws"]}
    ok = ({("water", "state", "liquid", "base"),
           ("sky", "color", "blue", "base"),
           ("broom", "can", "fly", "hp")} <= fset
          and {"double", "wrongy", "alien"} <= lnames
          and all(l.get("equation") for l in t["laws"]))
    check("I1 extraction: facts carry their worlds; laws carry "
          "their equations", ok,
          f"{len(t['facts'])} facts, {sorted(lnames)}")

    # ── I2: ingestion — facts answerable, the fiction wall holds ──
    new = mod.Isaac()
    rep = ingest_teachings(new, t, source="prologue")
    a1 = new.ask("water", "state")
    a2 = new.ask("broom", "can", container="hp")
    a3 = new.ask("broom", "can", container="base", inherit=False)
    ok = ("liquid" in a1["answers"] and "fly" in a2["answers"]
          and not a3["answers"])
    check("I2 facts land; fiction stays in its world; base never "
          "inherits it", ok,
          f"base broom answers: {a3['answers']}")

    # ── I3: ONE SHOT — a told law is usable immediately ──
    xg = np.linspace(0, 10, 50).reshape(-1, 1)
    pred = new.apply_law("double", xg)
    ok = pred is not None and np.nanmax(
        np.abs(pred - 2.0 * xg[:, 0])) < 0.1
    check("I3 one-shot: the inherited law applies immediately on the "
          "fresh mind", ok,
          f"max err {np.nanmax(np.abs(pred - 2.0 * xg[:, 0])):.4f}"
          if pred is not None else "apply_law returned None")

    # ── I7 (before any validation): no belief inherited ──
    st = new.net.get_meta("law:wrongy", "status") or {}
    ok = st.get("state") == "TOLD-UNVERIFIED" \
        and st.get("provenance") == "prologue"
    check("I7 no belief inherited: told laws land TOLD-UNVERIFIED "
          "with the source named", ok, str(st)[:70])

    # ── I4: revalidation — belief is EARNED, wrongness caught ──
    xv = rng.uniform(0, 10, 120).reshape(-1, 1)
    yv = 2.0 * xv[:, 0] + rng.normal(0, 0.02, 120)
    v_good = new.validate_law("double", xv, yv)
    v_bad = new.validate_law("wrongy", xv, yv)
    ok = (v_good and v_good.get("status") == "HOLDS"
          and v_bad and v_bad.get("status") == "FAILS")
    check("I4 revalidation: true inherited law HOLDS on his own "
          "data; wrong one FAILS", ok,
          f"double={v_good}, wrongy={v_bad}"[:90])

    # ── I5: the vocabulary edge — refused loudly, counted ──
    refused = {r["name"]: r["why"] for r in rep["laws_refused"]}
    ok = ("alien" in refused and refused["alien"]
          and rep["counts"]["laws_extracted"]
          == rep["counts"]["laws_told"]
          + rep["counts"]["laws_witness"]
          + len(rep["laws_refused"]))
    check("I5 out-of-vocabulary law refused WITH its why; law "
          "accounting sums", ok, str(refused)[:80])

    # ── I5b: fact accounting sums too ──
    c = rep["counts"]
    ok = c["facts_extracted"] == c["facts_told"] + c["facts_refused"]
    check("I5b fact accounting sums (complete numbers)", ok,
          f"{c['facts_extracted']} = {c['facts_told']} told + "
          f"{c['facts_refused']} refused")

    # ── I6: provenance + persistence ──
    inh = [f for f in new.findings if f["kind"] == "inheritance"]
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "m.isaac")
        new.save(p)
        back = mod.Isaac.load(p)
        a = back.ask("water", "state")
        pred2 = back.apply_law("double", xg)
    ok = (len(inh) == 1 and inh[0].get("source") == "prologue"
          and "liquid" in a["answers"] and pred2 is not None)
    check("I6 provenance recorded (source=prologue); everything "
          "survives save/load", ok)

    # ── I8: reproducibility — same teachings, two fresh minds ──
    m1, m2 = mod.Isaac(), mod.Isaac()
    ingest_teachings(m1, t, source="prologue")
    ingest_teachings(m2, t, source="prologue")
    same_facts = (sorted(map(str, m1.fact_index.keys()))
                  == sorted(map(str, m2.fact_index.keys())))
    p1 = m1.apply_law("double", xg)
    p2 = m2.apply_law("double", xg)
    ok = same_facts and p1 is not None and p2 is not None \
        and np.allclose(p1, p2, equal_nan=True)
    check("I8 reproducibility: two fresh minds, one telling, same "
          "net behavior", ok)

    # ── I9: the account wrapper — birth on plain files ──
    with tempfile.TemporaryDirectory() as td:
        old_home = os.path.join(td, "old_home")
        new_home = os.path.join(td, "new_home")
        os.makedirs(old_home)
        old.save(os.path.join(old_home, "mind.isaac"))
        with open(os.path.join(old_home, "sparring_corpus.txt"),
                  "w", encoding="utf-8") as f:
            f.write("hello there\nhow are you\n")
        rep9 = inherit_account(old_home, new_home, mod=mod)
        acct_mind = mod.Isaac.load(os.path.join(new_home,
                                                "mind.isaac"))
        a = acct_mind.ask("sky", "color")
        corpus_ok = os.path.exists(os.path.join(
            new_home, "sparring_corpus.txt"))
        jpath = os.path.join(new_home, "practice_journal.jsonl")
        with open(jpath, encoding="utf-8") as f:
            first = json.loads(f.readline())
        # SAFETY: a second birth into an occupied home must refuse
        try:
            inherit_account(old_home, new_home, mod=mod)
            refused_second = False
        except RuntimeError:
            refused_second = True
        ok = ("blue" in a["answers"] and corpus_ok
              and first.get("kind") == "birth"
              and refused_second
              and rep9["counts"]["facts_told"] >= 3)
        check("I9 birth wrapper: fresh home built, corpus carried, "
              "birth journaled, occupied home REFUSED", ok,
              f"journal[0]={first.get('kind')}, "
              f"second-birth refused={refused_second}")

    print("=" * 70)
    print(f"BATTERY: {PASSED} passed, {FAILED} failed of "
          f"{PASSED + FAILED}")
    print("=" * 70)
    sys.exit(0 if FAILED == 0 else 1)


if __name__ == "__main__":
    main()
