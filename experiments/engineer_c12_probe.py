"""engineer_c12_probe.py — THE ENGINEER LANE, C1-C2 (owner build
queue item 2; docs/engineer/engineer-lane-checklist.md).

RESEARCH, NOT THE ENGINE. The code lane's first two courts:

  C1 READ -> MAP. A small program parses into a map living AS DOORS
     on a mind: stmt:<id> nodes, control-flow doors (next / then /
     else / body), data-flow doors (writes / reads). Court: every
     statement, branch, and variable appears in the map EXACTLY
     once; the map alone regenerates the program's structural
     signature. Null: a scrambled program yields a measurably
     different map.
  C2 THE CONTAINMENT COURT. Input-space accounting, three verdicts:
     CONTAINED (every input in the region provably reaches defined
     handling — proof by exhaustive enumeration over the finite
     region, receipt carries the count), UNCONTAINED (each escaping
     input NAMED with its exception and line), REFUSED (the
     function contains vocabulary the court cannot reason about —
     eval/exec/reflection/global state — so enumeration would not
     constitute proof; parked, never silently passed).

PREDICTIONS (filed before the first run; wrong ones kept)
  M1 completeness: AST statement/branch/variable counts == map
     counts, exactly once each.
  M2 regeneration: the structural signature rebuilt from THE MAP
     ALONE equals the signature read from the source.
  M3 the null: a scrambled program's map differs measurably
     (door-set distance > 0, counted).
  K1 the holey toy: all THREE planted escapes found — x=7
     (ZeroDivisionError), x=13 (IndexError), x=-5 (ValueError) —
     each named with input, exception, and line.
  K2 the instrument receipt: every named escape CONFIRMED by
     execution.
  K3 the solid toy (same shape, guarded): CONTAINED with the
     exhaustive receipt (201/201 inputs reach defined handling).
  K4 the mystery toy (eval inside): REFUSED with the offending
     vocabulary named — parked, never silently passed.
  K5 the null: the court must NOT claim containment on the holey
     toy.

Run: cd experiments && PYTHONHASHSEED=0 python engineer_c12_probe.py
"""
import ast
import os
import sys
import time

import numpy as np  # noqa: F401

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac


# ── C1: read -> map, as doors ─────────────────────────────────────
def code_map(mind, source, tag="prog"):
    """Parse -> stmt nodes + control/data doors on the net. Returns
    the map record (ids, doors, variables) for the courts."""
    tree = ast.parse(source)
    stmts, doors, variables = [], [], set()
    counter = [0]

    def new_id(node):
        counter[0] += 1
        sid = f"{tag}:stmt{counter[0]}"
        stmts.append((sid, type(node).__name__,
                      getattr(node, "lineno", 0)))
        return sid

    def walk_body(body, parent):
        prev = None
        for node in body:
            sid = new_id(node)
            mind.net.add_door(parent, sid, tag="body")
            doors.append((parent, sid, "body"))
            if prev:
                mind.net.add_door(prev, sid, tag="next")
                doors.append((prev, sid, "next"))
            prev = sid
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name):
                    variables.add(sub.id)
                    kind = ("writes" if isinstance(sub.ctx, ast.Store)
                            else "reads")
                    mind.net.add_door(sid, f"{tag}:var:{sub.id}",
                                      tag=kind)
                    doors.append((sid, f"var:{sub.id}", kind))
            if isinstance(node, (ast.If, ast.While, ast.For)):
                walk_body(node.body, sid)
                if node.orelse:
                    walk_body(node.orelse, sid)
            elif isinstance(node, (ast.FunctionDef, ast.Try)):
                walk_body(node.body, sid)
                for h in getattr(node, "handlers", []):
                    walk_body(h.body, sid)
        return prev

    walk_body(tree.body, f"{tag}:root")
    return dict(stmts=stmts, doors=doors,
                variables=sorted(variables), tree=tree)


def ast_counts(tree):
    """Ground truth the map must match exactly once each."""
    n_stmt = sum(1 for n in ast.walk(tree) if isinstance(n, ast.stmt))
    n_vars = len({n.id for n in ast.walk(tree)
                  if isinstance(n, ast.Name)})
    return n_stmt, n_vars


def signature_from_map(m):
    """The structural signature REBUILT FROM THE MAP ALONE: nested
    (type, children) via body doors, in statement order."""
    kids = {}
    for a, b, t in m["doors"]:
        if t == "body":
            kids.setdefault(a, []).append(b)
    types = {sid: ty for sid, ty, _ in m["stmts"]}

    def sig(node):
        return (types.get(node, "root"),
                tuple(sig(c) for c in kids.get(node, [])))
    root = [a for a, _, t in m["doors"] if t == "body"
            and a.endswith(":root")]
    return sig(root[0]) if root else ("root", ())


def signature_from_source(source, tag="prog"):
    """The same signature read straight off the source (via a
    scratch map on a scratch mind) — the regeneration court's
    ground truth."""
    return signature_from_map(code_map(Isaac(), source, tag=tag))


# ── C2: the containment court ─────────────────────────────────────
FORBIDDEN = ("eval", "exec", "getattr", "setattr", "globals",
             "locals", "__import__", "input", "open")


def containment_court(source, fname, region):
    """Three verdicts. Vocabulary scan first: enumeration of code
    the court cannot reason about is not proof."""
    tree = ast.parse(source)
    bad = sorted({n.func.id for n in ast.walk(tree)
                  if isinstance(n, ast.Call)
                  and isinstance(n.func, ast.Name)
                  and n.func.id in FORBIDDEN})
    if bad:
        return dict(verdict="REFUSED",
                    vocabulary=bad,
                    receipt="region beyond current vocabulary "
                            f"({', '.join(bad)}) — parked, never "
                            "silently passed")
    ns = {}
    exec(compile(source, "<toy>", "exec"), ns)      # noqa: S102
    fn = ns[fname]
    escapes = []
    for x in region:
        try:
            fn(x)
        except Exception as e:
            tb = e.__traceback__
            while tb.tb_next is not None:
                tb = tb.tb_next
            escapes.append(dict(input=x,
                                exception=type(e).__name__,
                                line=tb.tb_lineno))
    if escapes:
        return dict(verdict="UNCONTAINED", escapes=escapes,
                    checked=len(region))
    return dict(verdict="CONTAINED", checked=len(region),
                receipt=f"all {len(region)} inputs in the region "
                        "reach defined handling — proof by "
                        "exhaustive enumeration")


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
        try:
            return int("abc")
        except ValueError:
            return -1
    if x == 13:
        return arr[9]
    if x == 7:
        return 0
    y = 100 / (x - 7)
    return y + arr[abs(x) % 10]
'''

MYSTERY = '''
def mystery(x):
    return eval("x * 2")
'''


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    mind = Isaac()
    m = code_map(mind, HOLEY, tag="holey")
    n_stmt, n_vars = ast_counts(m["tree"])

    # M1 — completeness, exactly once each
    ok1 = (len(m["stmts"]) == n_stmt
           and len(m["variables"]) == n_vars
           and len({s for s, _, _ in m["stmts"]}) == len(m["stmts"]))
    check("M1 completeness — statements + variables mapped exactly "
          "once", ok1,
          f"{len(m['stmts'])}/{n_stmt} stmts, "
          f"{len(m['variables'])}/{n_vars} vars")

    # M2 — regeneration from the map alone
    ok2 = signature_from_map(m) == signature_from_source(HOLEY,
                                                         tag="holey")
    check("M2 regeneration — map alone rebuilds the structural "
          "signature", ok2, "signatures equal")

    # M3 — the null: a VALID scrambled program (AST-level shuffle —
    # run-1's line shuffle broke the syntax and passed the cheap
    # way, wrong-kept) must map measurably differently
    tree_s = ast.parse(HOLEY)
    fn_s = tree_s.body[0]
    rng = np.random.default_rng(4)
    order = list(rng.permutation(len(fn_s.body)))
    if order == sorted(order):
        order = order[::-1]
    fn_s.body = [fn_s.body[i] for i in order]
    scrambled = ast.unparse(tree_s)
    ms = code_map(Isaac(), scrambled, tag="scr")
    seq_o = [ty for _, ty, _ in m["stmts"]]
    seq_s = [ty for _, ty, _ in ms["stmts"]]
    dist = sum(a != b for a, b in zip(seq_o, seq_s)) \
        + abs(len(seq_o) - len(seq_s))
    differs = (dist > 0 and signature_from_map(ms)
               != signature_from_source(HOLEY, tag="h2"))
    check("M3 the null — a valid scrambled program maps measurably "
          "differently", differs,
          f"stmt-sequence distance {dist} (program parses)")

    region = list(range(-100, 101))

    # K1 — the holey toy: all three planted escapes found + named
    r = containment_court(HOLEY, "holey", region)
    found = {(e["input"], e["exception"]) for e in r.get("escapes", [])}
    ok4 = (r["verdict"] == "UNCONTAINED"
           and (7, "ZeroDivisionError") in found
           and (13, "IndexError") in found
           and (-5, "ValueError") in found
           and len(found) == 3
           and all(e["line"] > 0 for e in r["escapes"]))
    check("K1 holey — all 3 planted escapes found, named with "
          "input/exception/line", ok4,
          f"{sorted(found)}")

    # K2 — instrument receipt: escapes confirmed by execution
    ns = {}
    exec(compile(HOLEY, "<toy>", "exec"), ns)       # noqa: S102
    confirmed = 0
    for e in r["escapes"]:
        try:
            ns["holey"](e["input"])
        except Exception as ex:
            confirmed += type(ex).__name__ == e["exception"]
    check("K2 the instrument — every named escape reproduces",
          confirmed == 3, f"{confirmed}/3 confirmed")

    # K3 — the solid toy: CONTAINED with the exhaustive receipt
    rs = containment_court(SOLID, "solid", region)
    ok6 = (rs["verdict"] == "CONTAINED" and rs["checked"] == 201
           and "exhaustive" in rs["receipt"])
    check("K3 solid — CONTAINED, 201/201 by enumeration", ok6,
          f"{rs['verdict']} ({rs.get('checked')} checked)")

    # K4 — the mystery toy: REFUSED, vocabulary named
    rm = containment_court(MYSTERY, "mystery", region)
    ok7 = (rm["verdict"] == "REFUSED" and rm["vocabulary"] == ["eval"]
           and "never silently passed" in rm["receipt"])
    check("K4 mystery — REFUSED, eval named, parked", ok7,
          f"{rm['verdict']} ({rm.get('vocabulary')})")

    # K5 — the null: no containment claim on the holey toy
    check("K5 the null — the court never claims containment on "
          "planted holes", r["verdict"] != "CONTAINED",
          f"holey verdict: {r['verdict']}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
