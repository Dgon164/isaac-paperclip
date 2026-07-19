"""retune_battery.py — PROMOTION GATE for THE RETUNE COURT (the
scaling campaign's rung 3; owner, 2026-07-19: learning, discovery,
and APPLICATION closed into one circuit on code).

The circuit under test: an ENGLISH change order -> the sheet is
read -> the text is edited AT THE READING'S OWN LOCATION -> the
ECHO court re-reads the edited text -> the INSTRUMENT runs both
versions on the same drive and the behavior moves by exactly the
ordered amount. The program is DATA; the organs know no names.

  R1  "set score valence to 20" — echo + the eaten reward IS 20.
  R2  "make energy cap 150" — the buffer saturates at 150 in the
      run, not 100.
  R3  "set energy drain to -2" — the per-step fall reads -2 in
      behavior; the game dies sooner (consequence observed).
  R4  THE ALIEN RETUNE: the renamed program takes the same change
      order by ITS names — zero vocabulary in the organs.
  R5  REFUSALS: an attr the sheet never read; a field outside the
      v1 scope — both loud, by name.
  R6  MINIMAL SURGERY: the edit touches exactly one line, and on
      that line exactly the constant.
  R7  THE MOD NULL, DRIVEN: valence retuned NEGATIVE — the same
      eats now punish (behavior shows -5 where +10 lived).
  R8  THE ENGLISH DOOR: parse_change round-trips into the court;
      gibberish refused with the shape named.

Run: cd experiments && PYTHONHASHSEED=0 python retune_battery.py
"""
import difflib
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
from isaac_store.engineer import (retune,             # noqa: E402
                                  behavior_delta)
from isaac_store.telling import parse_change          # noqa: E402
from isaac_store.test_engineer import SNAKE_SRC       # noqa: E402

NS = dict(DIRS=dict(U=(0, -1), D=(0, 1), L=(-1, 0), R=(1, 0)))


def drive(n=300, seed=0):
    """A fixed action sequence (greedy-ish chase recorded once on
    the ORIGINAL program) — the same drive feeds both versions."""
    ns = dict(NS)
    exec(compile(SNAKE_SRC, "<snake>", "exec"), ns)  # noqa: S102
    g = ns["Snake"](seed)
    rng = np.random.default_rng(seed)
    actions = []
    while g.alive and len(actions) < n:
        a = min("UDLR", key=lambda k: (
            abs(g.body[0][0] + ns["DIRS"][k][0] - g.food[0])
            + abs(g.body[0][1] + ns["DIRS"][k][1] - g.food[1])
            + float(rng.uniform(0, 0.5))))
        actions.append(a)
        g.step(a)
    return actions


ACTIONS = drive()


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(bool(ok))
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    # R1 valence 10 -> 20
    r1 = retune(SNAKE_SRC, [dict(court="rewards", attr="score",
                                 field="valence", to=20)])
    d1 = behavior_delta(SNAKE_SRC, r1["edited"], NS, ACTIONS,
                        cls="Snake")
    ok = ("score" in d1 and 20.0 in d1["score"]["b_step_deltas"]
          and 10.0 not in d1["score"]["b_step_deltas"]
          and r1["echo"])
    check("R1 valence 10->20 — echoed AND eaten at 20", ok,
          f"score deltas {d1.get('score', {}).get('b_step_deltas')}")

    # R2 cap 100 -> 150
    r2 = retune(SNAKE_SRC, [dict(court="buffers", attr="energy",
                                 field="cap", to=150)])
    d2 = behavior_delta(SNAKE_SRC, r2["edited"], NS, ACTIONS,
                        cls="Snake")
    ok = "energy" in d2 and d2["energy"]["b_max"] == 149
    check("R2 cap 100->150 — the buffer saturates at the new cap "
          "(149 after the step drain)", ok,
          f"energy b_max {d2.get('energy', {}).get('b_max')}")

    # R3 drain -1 -> -2
    r3 = retune(SNAKE_SRC, [dict(court="buffers", attr="energy",
                                 field="drain", to=-2)])
    d3 = behavior_delta(SNAKE_SRC, r3["edited"], NS, ACTIONS,
                        cls="Snake")
    dl3 = d3.get("energy", {}).get("b_step_deltas", [])
    ok = ("energy" in d3 and -2.0 in dl3 and -1.0 not in dl3)
    check("R3 drain -1->-2 — falls at 2/step, the old -1 gone "
          "(refill deltas stay cap-clipped, honestly variable)",
          ok, f"energy deltas {dl3}")

    # R4 the alien retune — its OWN names, zero shared vocabulary
    alien = SNAKE_SRC
    for a, b in [("score", "points"), ("food", "apple"),
                 ("body", "tail"), ("energy", "stamina"),
                 ("alive", "active"), ("dir", "heading"),
                 ("DIRS", "MOVES"), ("lucky", "charm"),
                 ("action", "cmd"), ("Snake", "Rover"),
                 ("W", "XMAX"), ("H", "YMAX")]:
        alien = alien.replace(a, b)
    r4 = retune(alien, [dict(court="rewards", attr="points",
                             field="valence", to=25)])
    d4 = behavior_delta(alien, r4["edited"],
                        dict(MOVES=NS["DIRS"]), ACTIONS,
                        cls="Rover")
    ok = ("points" in d4
          and 25.0 in d4["points"]["b_step_deltas"])
    check("R4 alien retune — the renamed program, its own names",
          ok, f"points deltas "
              f"{d4.get('points', {}).get('b_step_deltas')}")

    # R5 refusals, loud
    r5a = retune(SNAKE_SRC, [dict(court="rewards", attr="mana",
                                  field="valence", to=5)])
    r5b = retune(SNAKE_SRC, [dict(court="rewards", attr="score",
                                  field="guard", to=1)])
    ok = ("refused" in r5a and "mana" in r5a["refused"]
          and "refused" in r5b and "v1" in r5b["refused"])
    check("R5 refusals — unread attr and out-of-scope field, "
          "by name", ok, f"{r5a.get('refused', '')[:30]}; "
                         f"{r5b.get('refused', '')[:34]}")

    # R6 minimal surgery
    diff = [ln for ln in difflib.unified_diff(
        SNAKE_SRC.split("\n"), r1["edited"].split("\n"), n=0)
        if ln.startswith(("+", "-"))
        and not ln.startswith(("+++", "---"))]
    ok = (len(diff) == 2
          and diff[0][1:].replace("10", "20") == diff[1][1:])
    check("R6 minimal surgery — one line, one constant", ok,
          f"{len(diff)} changed lines: "
          f"{[d.strip() for d in diff][:2]}")

    # R7 the mod null, driven: reward turned punishment
    r7 = retune(SNAKE_SRC, [dict(court="rewards", attr="score",
                                 field="valence", to=-5)])
    d7 = behavior_delta(SNAKE_SRC, r7["edited"], NS, ACTIONS,
                        cls="Snake")
    ok = ("score" in d7 and -5.0 in d7["score"]["b_step_deltas"]
          and d7["score"]["b_max"] <= 0)
    check("R7 mod null driven — the same eats now punish", ok,
          f"score b_max {d7.get('score', {}).get('b_max')}")

    # R8 the english door
    ch = parse_change("set score valence to 20")
    bad = parse_change("please improve the snake")
    r8 = retune(SNAKE_SRC, [ch])
    ok = (r8.get("echo") and "refused" in bad
          and "shape" in bad["refused"] or "change order"
          in bad.get("refused", ""))
    check("R8 english door — order round-trips; gibberish refused",
          bool(ok), f"echo {r8.get('echo', ['-'])[0][:34]}; "
                    f"bad: {bad.get('refused', '')[:30]}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} "
          f"failed of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
