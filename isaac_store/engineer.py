"""engineer.py — THE ENGINEER LANE's foundation courts (owner
D1-D5 + the read road; probe-proven in engineer_e0_probe,
engineer_c12_probe, engineer_gread_probe — all 8/8).

The lane's grammar, promoted: every later rung is these courts
wearing domain costume. Verdict vocabulary: CONSISTENT / WOUND /
DOF-OPEN (structures), BALANCED / RESIDUAL / REFUSED (slots),
CONTAINED / UNCONTAINED / REFUSED (code). Standing rules: nulls
must refuse; instruments never mind; a verifier NEVER repairs what
it checks.

v1 vocabulary limits, named: constraint courts are arithmetic
(linear recipes); the goal-sheet reader's classification shapes are
bounds-tests / membership / <=0 / dead-data-flow; containment's
proof is exhaustive enumeration over finite regions after a
vocabulary scan (enumerating unreasoned code is not proof)."""
import ast

import numpy as np

TOL = 1e-9

# ── E0.1 / M1: the kind as parametric recipe (the tube court) ─────


def tube_court(ID=None, OD=None, wall=None):
    """OD = ID + 2*wall. Two given -> third derived; three ->
    consistency court (corroboration or refusal with the residual
    named); one -> named degrees of freedom, never a guess."""
    given = {k: v for k, v in dict(ID=ID, OD=OD, wall=wall).items()
             if v is not None}
    if len(given) == 3:
        resid = OD - ID - 2 * wall
        if abs(resid) <= TOL:
            return dict(verdict="CONSISTENT",
                        receipt="corroboration: three dimensions, "
                                "one recipe, zero residual")
        return dict(verdict="REFUSED",
                    residual=round(float(resid), 6),
                    direction=("OD large or ID/wall small"
                               if resid > 0 else
                               "OD small or ID/wall large"))
    if len(given) == 2:
        if ID is None:
            ID = OD - 2 * wall
        elif OD is None:
            OD = ID + 2 * wall
        else:
            wall = (OD - ID) / 2.0
        return dict(verdict="DERIVED", ID=ID, OD=OD, wall=wall)
    return dict(verdict="DOF-OPEN",
                free=sorted(set(("ID", "OD", "wall")) - set(given)))


# ── E0.2: multi-view identity ─────────────────────────────────────

def view_court(views, tol=1e-9):
    """Where views of one identity overlap in consequences they
    must agree machine-exact; disagreement is a WOUND, routed."""
    vals = list(views.values())
    spread = max(vals) - min(vals)
    if spread <= tol * max(abs(v) for v in vals):
        return dict(verdict="CONSISTENT", spread=float(spread))
    return dict(verdict="WOUND", spread=float(spread),
                views={k: round(float(v), 6)
                       for k, v in views.items()},
                receipt="views of one identity disagree — routed "
                        "to conflict machinery")


def tube_views_volume(ID, OD, L):
    """Three decompositions of one tube answering 'how much
    material?' — the view court's reference instance."""
    wall = (OD - ID) / 2.0
    return dict(hollow=np.pi / 4 * (OD ** 2 - ID ** 2) * L,
                schedule=np.pi * (ID + wall) * wall * L,
                faces=(np.pi * (OD / 2) ** 2
                       - np.pi * (ID / 2) ** 2) * L)


# ── E0.3: slot signatures ─────────────────────────────────────────

SLOT_SIGS = dict(
    divide=dict(inputs=("a", "b"),
                outputs=("quotient", "remainder"),
                balance=lambda i, o: abs(o["quotient"] * i["b"]
                                         + o["remainder"] - i["a"])),
    cut=dict(inputs=("length", "at"),
             outputs=("piece1", "piece2", "kerf"),
             balance=lambda i, o: abs(o["piece1"] + o["piece2"]
                                      + o["kerf"] - i["length"])))


def slot_court(op, ins, outs, sigs=None):
    """Presence + type + balance; an operation whose signature
    declares no residue slot is an accounting error (division is
    two-in two-out); an unaccounted slot is a named violation."""
    sig = (sigs or SLOT_SIGS).get(op)
    if sig is None or len(sig.get("outputs", ())) < 2 \
            and "balance" not in sig:
        return dict(verdict="REFUSED",
                    receipt="accounting error: operation declares "
                            "no residue slot")
    missing_in = [k for k in sig["inputs"] if k not in ins]
    missing_out = [k for k in sig["outputs"] if k not in outs]
    if missing_in or missing_out:
        return dict(verdict="REFUSED", missing_in=missing_in,
                    missing_out=missing_out,
                    receipt="unaccounted slot(s) named")
    bal = sig["balance"](ins, outs)
    if bal > TOL:
        return dict(verdict="RESIDUAL", imbalance=float(bal))
    return dict(verdict="BALANCED")


# ── E0.4: TMS dependency propagation ──────────────────────────────

def tms_propagate(values, deps, changed, new_value, tol=1e-9):
    """deps: child -> (parent, 'fixed'|'relative', k). Change one
    value -> propagate through the typed chain -> re-verify all."""
    vals = dict(values)
    vals[changed] = new_value
    for _ in deps:
        for child, (parent, kind, k) in deps.items():
            want = (vals[parent] + k if kind == "fixed"
                    else vals[parent] * (1 + k))
            if child != changed:
                vals[child] = round(want, 12)
    return vals, tms_verify(vals, deps, tol)


def tms_verify(values, deps, tol=1e-9):
    """RE-VERIFY, NEVER REPAIR (the E0 lesson: a verifier that
    fixes what it checks can never flag anything): every diverging
    member named with size and direction."""
    flags = []
    for child, (parent, kind, k) in deps.items():
        want = (values[parent] + k if kind == "fixed"
                else values[parent] * (1 + k))
        dv = values[child] - want
        if abs(dv) > tol:
            flags.append(dict(member=child,
                              size=round(float(abs(dv)), 6),
                              direction="high" if dv > 0 else "low"))
    return flags


# ── C1: read -> map, as doors ─────────────────────────────────────

def code_map(mind, source, tag="prog"):
    """A program parsed into the net: stmt nodes, control doors
    (body/next), data doors (writes/reads). The map holds the whole
    program: every statement and variable exactly once, and the map
    alone regenerates the structural signature."""
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
                    kind = ("writes"
                            if isinstance(sub.ctx, ast.Store)
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


def map_signature(m):
    """The structural signature rebuilt FROM THE MAP ALONE."""
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


# ── C2: the containment court ─────────────────────────────────────

CONTAINMENT_FORBIDDEN = ("eval", "exec", "getattr", "setattr",
                         "globals", "locals", "__import__",
                         "input", "open")


def containment_court(source, fname, region):
    """Three verdicts. Vocabulary scan FIRST: enumerating code the
    court cannot reason about is not proof. Then proof by
    exhaustive enumeration over the finite region: CONTAINED with
    the count, or UNCONTAINED with every escape named (input,
    exception, line)."""
    tree = ast.parse(source)
    bad = sorted({n.func.id for n in ast.walk(tree)
                  if isinstance(n, ast.Call)
                  and isinstance(n.func, ast.Name)
                  and n.func.id in CONTAINMENT_FORBIDDEN})
    if bad:
        return dict(verdict="REFUSED", vocabulary=bad,
                    receipt="region beyond current vocabulary "
                            f"({', '.join(bad)}) — parked, never "
                            "silently passed")
    ns = {}
    exec(compile(source, "<contained>", "exec"), ns)   # noqa: S102
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
                receipt=f"all {len(region)} inputs reach defined "
                        "handling — proof by exhaustive enumeration")


# ── THE READ ROAD: goal sheets from program text ──────────────────

def read_goal_sheet(class_src):
    """The G-rung's read road: rewards (valence FROM the text, the
    do from the reward's guard), buffers (drain/refill/cap read),
    the lockout from shape (input overwritten from state = the
    transition does not exist), fatal guards split on OR and
    classified by shape (bounds/membership/<=0), FREE by dead data
    flow. v1 shapes vocabulary, named in the module docstring."""
    tree = ast.parse(class_src)
    step = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef)
                and n.name == "step")
    writes, calls, tests = [], [], []
    input_locals = set()

    def walk(body, guards):
        for node in body:
            if isinstance(node, ast.Assign) and \
                    isinstance(node.targets[0], ast.Name):
                if "DIRS[" in ast.unparse(node.value):
                    input_locals.add(node.targets[0].id)
                if node.targets[0].id in input_locals \
                        and isinstance(node.value, ast.Attribute):
                    writes.append(dict(kind="input_discard",
                                       guards=list(guards)))
            if isinstance(node, (ast.Assign, ast.AugAssign)):
                tgt = node.targets[0] if isinstance(node, ast.Assign) \
                    else node.target
                if isinstance(tgt, ast.Attribute):
                    writes.append(dict(kind=type(node).__name__,
                                       attr=tgt.attr,
                                       value=node.value,
                                       node=node,
                                       guards=list(guards)))
            if isinstance(node, ast.Expr) and \
                    isinstance(node.value, ast.Call) and \
                    isinstance(node.value.func, ast.Attribute):
                calls.append(dict(method=node.value.func.attr,
                                  on=ast.unparse(node.value.func.value),
                                  guards=list(guards)))
            if isinstance(node, ast.If):
                tests.append(node.test)
                walk(node.body, guards + [(node.test, "then")])
                walk(node.orelse, guards + [(node.test, "else")])
    walk(step.body, [])

    sheet = dict(rewards={}, buffers={}, forbidden=[], fatal=[],
                 free=[], reward_source=None)
    for w in writes:
        if w.get("attr") == "score" and w["kind"] == "AugAssign":
            try:
                val = ast.literal_eval(w["value"])
            except Exception:
                continue
            guard = (ast.unparse(w["guards"][-1][0])
                     if w["guards"] else None)
            sheet["rewards"]["score"] = dict(valence=val,
                                             guard=guard)
            if guard and "food" in guard:
                sheet["reward_source"] = ("next cell == food (read "
                                          "from the reward's guard)")
    ins = [c for c in calls if c["method"] == "insert"
           and "body" in c["on"]]
    pop = [c for c in calls if c["method"] == "pop"
           and "body" in c["on"]]
    if ins and pop and any(
            g[1] == "else" and "food" in ast.unparse(g[0])
            for g in pop[0]["guards"]) and not any(
            "food" in ast.unparse(g[0]) for g in ins[0]["guards"]):
        sheet["rewards"]["length"] = dict(
            valence=1,
            guard="grows exactly on food (insert always, pop "
                  "unless food)")
    en = dict()
    for w in writes:
        if w.get("attr") != "energy":
            continue
        if w["kind"] == "AugAssign" and not w["guards"]:
            en["drain"] = -ast.literal_eval(w["value"])
        if w["kind"] == "Assign" and isinstance(w["value"], ast.Call) \
                and getattr(w["value"].func, "id", "") == "min":
            en["cap"] = ast.literal_eval(w["value"].args[0])
            plus = w["value"].args[1]
            if isinstance(plus, ast.BinOp) and \
                    isinstance(plus.op, ast.Add):
                en["refill"] = ast.literal_eval(plus.right)
    for w in writes:
        if w.get("attr") == "alive" and w["kind"] == "Assign" \
                and isinstance(w["value"], ast.Constant) \
                and w["value"].value is False and w["guards"]:
            test = w["guards"][-1][0]
            ops = (test.values if isinstance(test, ast.BoolOp)
                   and isinstance(test.op, ast.Or) else [test])
            for op in ops:
                s = ast.unparse(op)
                if "in self.body" in s:
                    sheet["fatal"].append(dict(cause="collision",
                                               read=s))
                elif "self.W" in s or "self.H" in s:
                    sheet["fatal"].append(dict(cause="wall",
                                               read=s))
                elif "<= 0" in s:
                    sheet["fatal"].append(dict(cause="exhaustion",
                                               read=s))
                    en["death_at_zero"] = True
    if en:
        sheet["buffers"]["energy"] = en
    for w in writes:
        if w.get("kind") == "input_discard" and w["guards"]:
            sheet["forbidden"].append(dict(
                action="reverse",
                read=ast.unparse(w["guards"][-1][0]),
                receipt="the commanded direction is overwritten "
                        "from persistent state — the transition "
                        "does not exist"))
    written = {w["attr"] for w in writes if w.get("attr")}
    read_names = set()
    for t in tests:
        read_names |= {n.attr for n in ast.walk(t)
                       if isinstance(n, ast.Attribute)}
    for w in writes:
        v = w.get("value")
        if w.get("attr") and isinstance(v, ast.AST):
            read_names |= {n.attr for n in ast.walk(v)
                           if isinstance(n, ast.Attribute)
                           and n.attr != w["attr"]}
    for c in calls:
        read_names.add(c["on"].replace("self.", ""))
    sheet["free"] = sorted(written - read_names
                           - {"alive", "score", "dir", "food",
                              "energy"})
    return sheet
