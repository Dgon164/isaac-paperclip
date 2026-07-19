"""engineer_gread_probe.py — THE G-RUNG, THE READ ROAD (owner
correction, 2026-07-18: "the idea was to read the code directly and
learn information" — not logs).

RESEARCH, NOT THE ENGINE. The goal sheet recovered STATICALLY, from
the program text alone, by walking the AST with a guard stack:

  REWARD    the `score += 10` line found under its guard; valence
            READ from the code constant, source READ from the guard
            (`(nx, ny) == self.food`).
  GROWTH    body.insert on every survive path, body.pop on the
            not-food branch — growth exactly on food, structural.
  BUFFER    energy: unconditional -1, `min(100, energy + 40)` on
            the food branch (the TRUE +40 and its cap, which the
            behavioral road could only see as +39-at-best), and the
            `energy <= 0 -> alive = False` exhaustion guard.
  FORBIDDEN the lockout READ from structure: an If whose body
            overwrites the input-derived direction from persistent
            state — the commanded transition does not exist.
  FATAL     every `alive = False` site's dominating guard, split on
            OR, each operand CLASSIFIED by shape: bounds test ->
            wall; membership in body -> collision; attr <= 0 ->
            exhaustion.
  FREE      lucky: written every step, READ BY NOTHING that flows
            into any guard or any other variable — dead data flow,
            statically FREE.

THE MOD NULL, LITERAL: parse the modded source (`score += -10`) —
the sheet reads the inverted valence FROM THE TEXT, zero execution.

THE INSTRUMENT COURT: the behavioral road (engineer_grung_probe)
then corroborates every read claim by running the mechanism — read
proposes, execution confirms, divergence would be a wound. The read
even PREDICTS the instrument's cap artifact: observed refill deltas
must equal min(100, e+40) - e - 1 exactly.

PREDICTIONS (filed before the first run; wrong ones kept)
  R1 reward read: +10 from the text, guarded by the food equality.
  R2 growth read: insert-always + pop-unless-food, structural.
  R3 buffer read: -1 unconditional, +40 capped at 100, exhaustion
     guard found.
  R4 lockout read: reverse discards input — forbidden, from shape.
  R5 fatal guards read + classified: wall, collision, exhaustion.
  R6 lucky statically FREE by dead data flow.
  R7 THE MOD NULL: -10 read from the modded text, no execution.
  R8 THE INSTRUMENT COURT: behavioral recovery agrees on every
     claim; the read's cap law reproduces every observed refill
     delta exactly.

Run: cd experiments && PYTHONHASHSEED=0 python engineer_gread_probe.py
"""
import ast
import inspect
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import engineer_grung_probe as game  # noqa: E402

SRC = inspect.getsource(game.Snake)
SRC_NORMAL = SRC.replace("(-10 if self.invert else 10)", "10")
SRC_MOD = SRC.replace("(-10 if self.invert else 10)", "-10")


def _attr(node):
    return node.attr if isinstance(node, ast.Attribute) else None


def read_goal_sheet(class_src):
    """The static read: one walk of step() with a guard stack."""
    tree = ast.parse(class_src)
    step = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "step")
    writes, calls, tests = [], [], []
    input_locals = set()

    def walk(body, guards):
        for node in body:
            if isinstance(node, ast.Assign) and \
                    isinstance(node.targets[0], ast.Name):
                src = ast.unparse(node.value)
                if "DIRS[" in src:
                    input_locals.add(node.targets[0].id)
                if node.targets[0].id in input_locals \
                        and isinstance(node.value, ast.Attribute):
                    writes.append(dict(kind="input_discard",
                                       guards=list(guards),
                                       text=ast.unparse(node)))
            if isinstance(node, (ast.Assign, ast.AugAssign)):
                tgt = node.targets[0] if isinstance(node, ast.Assign) \
                    else node.target
                a = _attr(tgt)
                if a:
                    writes.append(dict(kind=type(node).__name__,
                                       attr=a, value=node.value,
                                       guards=list(guards),
                                       text=ast.unparse(node)))
            if isinstance(node, ast.Expr) and \
                    isinstance(node.value, ast.Call):
                fn = node.value.func
                if isinstance(fn, ast.Attribute):
                    calls.append(dict(method=fn.attr,
                                      on=ast.unparse(fn.value),
                                      guards=list(guards)))
            if isinstance(node, ast.If):
                tests.append(node.test)
                walk(node.body, guards + [(node.test, "then")])
                walk(node.orelse, guards + [(node.test, "else")])
    walk(step.body, [])

    sheet = dict(rewards={}, buffers={}, forbidden=[], fatal=[],
                 free=[], reward_source=None)
    # rewards: numeric AugAssign constants, valence FROM THE TEXT
    for w in writes:
        if w.get("attr") == "score" and w["kind"] == "AugAssign":
            try:
                val = ast.literal_eval(w["value"])
            except Exception:
                continue
            guard = ast.unparse(w["guards"][-1][0]) if w["guards"] \
                else None
            sheet["rewards"]["score"] = dict(valence=val,
                                             guard=guard)
            if guard and "self.food" in guard:
                sheet["reward_source"] = "next cell == food (read " \
                                         "from the reward's guard)"
    # growth: insert always on the survive path, pop unless food
    ins = [c for c in calls if c["method"] == "insert"
           and "body" in c["on"]]
    pop = [c for c in calls if c["method"] == "pop"
           and "body" in c["on"]]
    if ins and pop:
        pop_else_food = any(
            g[1] == "else" and "self.food" in ast.unparse(g[0])
            for g in pop[0]["guards"])
        ins_unguarded_by_food = not any(
            "self.food" in ast.unparse(g[0]) for g in ins[0]["guards"])
        if pop_else_food and ins_unguarded_by_food:
            sheet["rewards"]["length"] = dict(
                valence=1, guard="grows exactly on food "
                                 "(insert always, pop unless food)")
    # buffer: energy writes
    en = dict()
    for w in writes:
        if w.get("attr") != "energy":
            continue
        if w["kind"] == "AugAssign" and not w["guards"]:
            en["drain"] = -ast.literal_eval(w["value"])
        if w["kind"] == "Assign" and isinstance(w["value"], ast.Call) \
                and getattr(w["value"].func, "id", "") == "min":
            cap = ast.literal_eval(w["value"].args[0])
            plus = w["value"].args[1]
            if isinstance(plus, ast.BinOp) and \
                    isinstance(plus.op, ast.Add):
                en["refill"] = ast.literal_eval(plus.right)
                en["cap"] = cap
    # fatal: alive=False sites, guards split on OR, classified
    for w in writes:
        if w.get("attr") == "alive" and w["kind"] == "Assign" \
                and isinstance(w["value"], ast.Constant) \
                and w["value"].value is False and w["guards"]:
            test = w["guards"][-1][0]
            ops = test.values if isinstance(test, ast.BoolOp) \
                and isinstance(test.op, ast.Or) else [test]
            for op in ops:
                s = ast.unparse(op)
                if "in self.body" in s:
                    sheet["fatal"].append(dict(cause="collision",
                                               read=s))
                elif "self.W" in s or "self.H" in s:
                    sheet["fatal"].append(dict(cause="wall", read=s))
                elif "<= 0" in s:
                    sheet["fatal"].append(dict(cause="exhaustion",
                                               read=s))
                    en["death_at_zero"] = True
    if en:
        sheet["buffers"]["energy"] = en
    # forbidden: input discarded from state under a condition
    for w in writes:
        if w.get("kind") == "input_discard" and w["guards"]:
            sheet["forbidden"].append(dict(
                action="reverse",
                read=ast.unparse(w["guards"][-1][0]),
                receipt="the commanded direction is overwritten "
                        "from persistent state — the transition "
                        "does not exist"))
    # free: attrs written but read by nothing downstream
    written = {w["attr"] for w in writes if w.get("attr")}
    read_names = set()
    for t in tests:
        read_names |= {n.attr for n in ast.walk(t)
                       if isinstance(n, ast.Attribute)}
    for w in writes:
        if w.get("attr") and not isinstance(w.get("value"), type(None)):
            v = w["value"]
            if isinstance(v, ast.AST):
                read_names |= {n.attr for n in ast.walk(v)
                               if isinstance(n, ast.Attribute)
                               and n.attr != w["attr"]}
    for c in calls:
        read_names.add(c["on"].replace("self.", ""))
    sheet["free"] = sorted(written - read_names
                           - {"alive", "score", "dir", "food",
                              "energy"})
    return sheet


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    sheet = read_goal_sheet(SRC_NORMAL)

    # R1 — reward read from the text
    sc = sheet["rewards"].get("score", {})
    ok1 = (sc.get("valence") == 10
           and "self.food" in (sc.get("guard") or "")
           and "food" in (sheet["reward_source"] or ""))
    check("R1 reward READ — +10 from the text, food-guarded", ok1,
          f"{sc}")

    # R2 — growth read structurally
    ok2 = "length" in sheet["rewards"]
    check("R2 growth READ — insert always, pop unless food", ok2,
          f"{sheet['rewards'].get('length')}")

    # R3 — buffer read: the TRUE +40 and its cap
    en = sheet["buffers"].get("energy", {})
    ok3 = (en.get("drain") == -1 and en.get("refill") == 40
           and en.get("cap") == 100 and en.get("death_at_zero"))
    check("R3 buffer READ — -1 drain, +40 refill, cap 100, "
          "exhaustion guard", ok3, f"{en}")

    # R4 — the lockout read from shape
    fb = sheet["forbidden"]
    ok4 = (len(fb) == 1 and fb[0]["action"] == "reverse"
           and "does not exist" in fb[0]["receipt"])
    check("R4 lockout READ — input discarded from state, forbidden",
          ok4, f"{fb[0]['read'] if fb else None}")

    # R5 — fatal guards read + classified
    causes = sorted(f["cause"] for f in sheet["fatal"])
    ok5 = causes == ["collision", "exhaustion", "wall"]
    check("R5 fatal READ — wall, collision, exhaustion from the "
          "guards", ok5, f"{causes}")

    # R6 — lucky statically FREE
    ok6 = sheet["free"] == ["lucky"]
    check("R6 FREE by dead data flow — lucky written, read by "
          "nothing", ok6, f"free {sheet['free']}")

    # R7 — THE MOD NULL, literal: no execution
    sheet_m = read_goal_sheet(SRC_MOD)
    ok7 = sheet_m["rewards"].get("score", {}).get("valence") == -10
    check("R7 THE MOD NULL — -10 read from the modded text, zero "
          "execution", ok7,
          f"valence {sheet_m['rewards'].get('score', {}).get('valence')}")

    # R8 — the instrument corroborates the read
    logs = [game.play(s, game.random_policy(1000 + s))
            for s in range(30)]
    logs += [game.play(200 + s, game.ring_policy()) for s in range(8)]
    logs += [game.play(600 + s, game.starver_policy(700 + s))
             for s in range(6)]
    beh = game.recover(logs)
    agree_score = beh["rewards"].get("score", {}).get("valence") == 10.0
    agree_fatal = {"next_cell_wall", "next_cell_body",
                   "energy_exhausted"} == {f["predicate"]
                                           for f in beh["fatal"]}
    agree_free = beh["free"] == ["lucky"]
    # the read's cap law must reproduce every observed refill delta
    cap_ok = True
    for ep in logs:
        for s, a, s2 in ep:
            if s2["score"] != s["score"]:
                want = min(100, s["energy"] + 40) - s["energy"] - 1
                cap_ok &= (s2["energy"] - s["energy"]) == want
    ok8 = agree_score and agree_fatal and agree_free and cap_ok
    check("R8 THE INSTRUMENT COURT — behavior corroborates every "
          "read claim; cap law exact", ok8,
          f"score {agree_score}, fatal {agree_fatal}, free "
          f"{agree_free}, cap-law {cap_ok}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
