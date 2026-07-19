"""test_engineer.py — PROMOTION GATE for the engineer lane's
foundation courts (E0 + C1-C2 + the read road; isaac_store/
engineer.py). Every court, every null, condensed from the three
8/8 probes.

Run: cd isaac_store && python test_engineer.py
"""
import ast
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod                    # noqa: E402
from isaac_store import engineer as eng      # noqa: E402

SNAKE_SRC = '''
class Snake:
    def __init__(self, seed=0):
        import numpy as _np
        self.rng = _np.random.default_rng(seed)
        self.lrng = _np.random.default_rng(seed + 7777)
        self.W = self.H = 12
        self.body = [(6, 6), (5, 6), (4, 6), (3, 6), (2, 6),
                     (2, 7), (3, 7), (4, 7)]
        self.dir = (1, 0)
        self.score, self.energy, self.alive = 0, 100, True
        self.lucky = int(self.lrng.integers(0, 100))
        self._place_food()

    def _place_food(self):
        while True:
            f = (int(self.rng.integers(0, self.W)),
                 int(self.rng.integers(0, self.H)))
            if f not in self.body:
                self.food = f
                return

    def step(self, action):
        d = DIRS[action]
        if d == (-self.dir[0], -self.dir[1]):
            d = self.dir
        else:
            self.dir = d
        self.lucky = int(self.lrng.integers(0, 100))
        nx = self.body[0][0] + d[0]
        ny = self.body[0][1] + d[1]
        if not (0 <= nx < self.W and 0 <= ny < self.H) \\
                or (nx, ny) in self.body:
            self.alive = False
            return
        self.body.insert(0, (nx, ny))
        if (nx, ny) == self.food:
            self.score += 10
            self.energy = min(100, self.energy + 40)
            self._place_food()
        else:
            self.body.pop()
        self.energy -= 1
        if self.energy <= 0:
            self.alive = False
'''

HOLEY = '''
def holey(x):
    arr = [0] * 10
    if x == -5:
        return int("abc")
    if x == 13:
        return arr[15]
    y = 100 / (x - 7)
    return y + arr[abs(x) % 10]
'''

SOLID = '''
def solid(x):
    arr = [0] * 10
    if x == -5:
        return -1
    if x == 13:
        return arr[9]
    if x == 7:
        return 0
    y = 100 / (x - 7)
    return y + arr[abs(x) % 10]
'''

MYSTERY = "def mystery(x):\n    return eval('x * 2')\n"


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail=""):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name}"
              + (f" — {detail}" if detail else ""))

    # N1 — the tube court, all roads
    d = eng.tube_court(ID=1.0, wall=0.125)
    c = eng.tube_court(ID=1.0, OD=1.25, wall=0.125)
    r = eng.tube_court(ID=1.0, OD=1.30, wall=0.125)
    g = eng.tube_court(ID=1.0)
    check("N1 tube court — derive/corroborate/refuse-with-residual/"
          "DOF-OPEN",
          abs(d["OD"] - 1.25) < 1e-9 and c["verdict"] == "CONSISTENT"
          and r["verdict"] == "REFUSED"
          and abs(r["residual"] - 0.05) < 1e-9
          and g["verdict"] == "DOF-OPEN" and g["free"] == ["OD", "wall"])

    # N2 — multi-view identity + the wound null
    v = eng.view_court(eng.tube_views_volume(1.0, 1.25, 10.0))
    w = eng.view_court(dict(a=1.5, b=2.7))
    check("N2 multi-view — agreement machine-exact; forced identity "
          "wounds",
          v["verdict"] == "CONSISTENT" and w["verdict"] == "WOUND")

    # N3 — slot signatures + the missing-residue accounting error
    ok = eng.slot_court("divide", dict(a=17, b=5),
                        dict(quotient=3, remainder=2))
    cut = eng.slot_court("cut", dict(length=10.0, at=4.0),
                         dict(piece1=4.0, piece2=5.9, kerf=0.1))
    bad = eng.slot_court("no_residue", dict(a=1), dict(out=1),
                         sigs=dict(no_residue=dict(inputs=("a",),
                                                   outputs=("out",))))
    check("N3 slots — balance holds; a signature without residue "
          "is an accounting error",
          ok["verdict"] == "BALANCED" and cut["verdict"] == "BALANCED"
          and bad["verdict"] == "REFUSED")

    # N4 — TMS: propagate, verify-never-repair, over-constrained
    deps = dict(piston=("bore", "relative", -0.005),
                groove=("piston", "fixed", -0.200))
    vals, flags = eng.tms_propagate(
        dict(bore=4.0, piston=3.98, groove=3.78), deps,
        "bore", 4.010)
    stale = dict(bore=4.010, piston=round(4.010 * 0.995, 12),
                 groove=3.78)
    f2 = eng.tms_verify(stale, deps)
    check("N4 TMS — clean propagation; stale member flagged with "
          "size+direction",
          not flags and len(f2) == 1 and f2[0]["member"] == "groove"
          and f2[0]["direction"] == "low")

    # N5 — code map: completeness + regeneration
    mind = isaac_mod.Isaac()
    m = eng.code_map(mind, HOLEY, tag="h")
    n_stmt = sum(1 for n in ast.walk(m["tree"])
                 if isinstance(n, ast.stmt))
    check("N5 code map — every statement exactly once; map alone "
          "regenerates the signature",
          len(m["stmts"]) == n_stmt
          and eng.map_signature(m)
          == eng.map_signature(eng.code_map(isaac_mod.Isaac(),
                                            HOLEY, tag="h")))

    # N6 — the map null: a valid scramble maps differently
    t = ast.parse(HOLEY)
    t.body[0].body = t.body[0].body[::-1]
    ms = eng.code_map(isaac_mod.Isaac(), ast.unparse(t), tag="s")
    check("N6 map null — a valid scrambled program maps differently",
          eng.map_signature(ms) != eng.map_signature(m))

    # N7 — containment: three verdicts + the null
    region = list(range(-100, 101))
    rh = eng.containment_court(HOLEY, "holey", region)
    rs = eng.containment_court(SOLID, "solid", region)
    rm = eng.containment_court(MYSTERY, "mystery", region)
    found = {(e["input"], e["exception"])
             for e in rh.get("escapes", [])}
    check("N7 containment — 3 escapes named; solid proven 201/201; "
          "mystery REFUSED w/ eval; no false containment",
          rh["verdict"] == "UNCONTAINED" and len(found) == 3
          and (7, "ZeroDivisionError") in found
          and rs["verdict"] == "CONTAINED" and rs["checked"] == 201
          and rm["verdict"] == "REFUSED"
          and rm["vocabulary"] == ["eval"])

    # N8 — the read road: the goal sheet from the text
    sheet = eng.read_goal_sheet(SNAKE_SRC)
    en = sheet["buffers"].get("energy", {})
    check("N8 read road — reward+guard, growth, buffer w/ TRUE "
          "+40/cap-100, lockout, fatal classified, lucky FREE",
          sheet["rewards"].get("score", {}).get("valence") == 10
          and "food" in sheet["rewards"]["score"]["guard"]
          and "length" in sheet["rewards"]
          and en.get("refill") == 40 and en.get("cap") == 100
          and en.get("drain") == -1 and en.get("death_at_zero")
          and len(sheet["forbidden"]) == 1
          and sorted(f["cause"] for f in sheet["fatal"])
          == ["collision", "exhaustion", "wall"]
          and sheet["free"] == ["lucky"])

    # N9 — the mod null, literal: no execution
    mod = eng.read_goal_sheet(SNAKE_SRC.replace("+= 10", "+= -10"))
    check("N9 the mod null — inverted valence read from the text",
          mod["rewards"].get("score", {}).get("valence") == -10)

    # N10 — the instrument court: behavior corroborates the read
    ns = dict(DIRS=dict(U=(0, -1), D=(0, 1), L=(-1, 0), R=(1, 0)))
    exec(compile(SNAKE_SRC, "<snake>", "exec"), ns)   # noqa: S102
    Snake = ns["Snake"]
    rng = np.random.default_rng(0)
    cap_ok, lock_ok, eats = True, True, 0
    for seed in range(12):
        gme = Snake(seed)
        steps = 0
        while gme.alive and steps < 300:
            s_energy, s_score = gme.energy, gme.score
            s_dir = gme.dir
            if seed % 2:                   # half the diet chases food
                a = min("UDLR", key=lambda k: (
                    abs(gme.body[0][0] + ns["DIRS"][k][0]
                        - gme.food[0])
                    + abs(gme.body[0][1] + ns["DIRS"][k][1]
                          - gme.food[1])
                    + float(rng.uniform(0, 0.5))))
            else:
                a = "UDLR"[int(rng.integers(0, 4))]
            want = ns["DIRS"][a]
            gme.step(a)
            if want == (-s_dir[0], -s_dir[1]):
                lock_ok &= (gme.dir == s_dir)
            if gme.alive and gme.score != s_score:
                eats += 1
                cap_ok &= (gme.energy
                           == min(100, s_energy + 40) - 1)
            steps += 1
    check("N10 instrument court — the read's cap law and lockout "
          "reproduce in behavior",
          cap_ok and lock_ok and eats >= 3,
          f"{eats} eats, cap law exact, lockout held")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} "
          f"failed of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
