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
vocabulary scan (enumerating unreasoned code is not proof). The
goal-sheet reader's COURTS are additionally keyed to one game's
identifier vocabulary (score/food/body/energy/DIRS/W/H) — a
DECLARED ceiling (on programs wearing other names the sheet goes
quiet, it never guesses); the FREE court is vocabulary-clean (dead
data flow minus what the sheet's own courts claimed). Reader v2 =
semantics from structure, the scaling campaign's first build."""
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

def _loc(n):
    return dict(l0=n.lineno, c0=n.col_offset,
                l1=n.end_lineno, c1=n.end_col_offset)


def read_goal_sheet(class_src):
    """The G-rung's read road, v2 (the scaling campaign's rung 1,
    2026-07-19): semantics from WRITE-SHAPE, never from names — the
    v1 identifier vocabulary (score/food/energy/alive/DIRS) is
    ABLATED; the same program wearing alien names must read the
    same sheet. The shapes: REWARD = guarded constant accumulator;
    BUFFER = unguarded constant drain and/or min-capped refill;
    FATAL = a False-latch (an attr only ever assigned literal False
    in step) with each guard branch classified by the standing
    generic shapes (membership-in-a-collection -> collision;
    bounds against never-written config attrs -> wall; <=0 on a
    buffer -> exhaustion); LENGTH-REWARD = a collection with
    unconditional insert and guarded pop (net growth = the pop's
    else condition); LOCKOUT = an input-derived local overwritten
    from persistent state under a guard; FREE = dead data flow
    minus what the sheet's own courts claimed."""
    tree = ast.parse(class_src)
    step = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef)
                and n.name == "step")
    step_args = {a.arg for a in step.args.args} - {"self"}
    writes, calls, tests = [], [], []
    input_locals = set()

    def _names(node):
        return {n.id for n in ast.walk(node)
                if isinstance(n, ast.Name)}

    def walk(body, guards):
        for node in body:
            if isinstance(node, ast.Assign) and \
                    isinstance(node.targets[0], ast.Name):
                if _names(node.value) & (step_args | input_locals):
                    if not isinstance(node.value, ast.Attribute):
                        input_locals.add(node.targets[0].id)
                if node.targets[0].id in input_locals \
                        and isinstance(node.value, ast.Attribute):
                    writes.append(dict(kind="input_discard",
                                       guards=list(guards)))
            if isinstance(node, (ast.Assign, ast.AugAssign)):
                tgt = node.targets[0] if isinstance(node, ast.Assign) \
                    else node.target
                if isinstance(tgt, ast.Attribute):
                    writes.append(dict(
                        kind=type(node).__name__, attr=tgt.attr,
                        value=node.value, node=node,
                        op=(type(node.op).__name__
                            if isinstance(node, ast.AugAssign)
                            else None),
                        guards=list(guards)))
            if isinstance(node, ast.Expr) and \
                    isinstance(node.value, ast.Call) and \
                    isinstance(node.value.func, ast.Attribute):
                calls.append(dict(method=node.value.func.attr,
                                  on=ast.unparse(node.value.func.value),
                                  obj=node.value.func.value,
                                  guards=list(guards)))
            if isinstance(node, ast.If):
                tests.append(node.test)
                walk(node.body, guards + [(node.test, "then")])
                walk(node.orelse, guards + [(node.test, "else")])
    walk(step.body, [])

    def _const(v):
        try:
            return ast.literal_eval(v)
        except Exception:
            return None

    by_attr = {}
    for w in writes:
        if w.get("attr"):
            by_attr.setdefault(w["attr"], []).append(w)
    written = set(by_attr)
    # collections: attrs that receive mutating calls in step
    MUTATORS = {"insert", "pop", "append", "remove", "extend",
                "add", "discard", "appendleft", "popleft"}
    collections = {c["on"].replace("self.", "") for c in calls
                   if c["method"] in MUTATORS
                   and isinstance(c["obj"], ast.Attribute)}
    # config attrs: read in step, never written in step
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
    config = read_names - written - collections

    sheet = dict(rewards={}, buffers={}, forbidden=[], fatal=[],
                 free=[], reward_source=None)
    claimed = set()

    # BUFFERS: unguarded constant drain and/or min-capped refill
    for attr, ws in by_attr.items():
        en = {}
        for w in ws:
            val = _const(w["value"]) if w["kind"] == "AugAssign" \
                else None
            if w["kind"] == "AugAssign" and val is not None \
                    and not w["guards"]:
                en["drain"] = -val if w["op"] == "Sub" else val
                en["drain_op"] = w["op"]
                en["drain_loc"] = _loc(w["value"])
            if w["kind"] == "Assign" \
                    and isinstance(w["value"], ast.Call) \
                    and getattr(w["value"].func, "id", "") == "min" \
                    and len(w["value"].args) == 2:
                cap = _const(w["value"].args[0])
                plus = w["value"].args[1]
                if cap is not None and isinstance(plus, ast.BinOp) \
                        and isinstance(plus.op, ast.Add) \
                        and attr in {n.attr for n in ast.walk(plus)
                                     if isinstance(n, ast.Attribute)}:
                    en["cap"] = cap
                    en["refill"] = _const(plus.right)
                    en["cap_loc"] = _loc(w["value"].args[0])
                    en["refill_loc"] = _loc(plus.right)
        if en:
            sheet["buffers"][attr] = en
            claimed.add(attr)

    # REWARDS: guarded constant accumulators (buffers excluded)
    for attr, ws in by_attr.items():
        if attr in sheet["buffers"]:
            continue
        for w in ws:
            if w["kind"] != "AugAssign" or not w["guards"]:
                continue
            val = _const(w["value"])
            if val is None:
                continue
            delta = -val if w["op"] == "Sub" else val
            guard = ast.unparse(w["guards"][-1][0])
            sheet["rewards"][attr] = dict(valence=delta,
                                          guard=guard,
                                          op=w["op"],
                                          loc=_loc(w["value"]))
            claimed.add(attr)
            if sheet["reward_source"] is None:
                sheet["reward_source"] = (f"read from the reward's "
                                          f"guard: {guard}")

    # LENGTH-REWARD: unconditional insert + guarded pop on one
    # collection — net growth exactly on the pop's else condition
    for coll in sorted(collections):
        ins = [c for c in calls if c["method"] in ("insert",
               "append", "appendleft")
               and c["on"].replace("self.", "") == coll]
        pop = [c for c in calls if c["method"] in ("pop", "popleft")
               and c["on"].replace("self.", "") == coll]
        if ins and pop and not ins[0]["guards"] and pop[0]["guards"]:
            g, side = pop[0]["guards"][-1]
            cond = ast.unparse(g)
            grows = (cond if side == "else"
                     else f"not ({cond})")
            key = "length" if len(collections) == 1 \
                else f"length:{coll}"
            sheet["rewards"][key] = dict(
                valence=1,
                guard=f"grows exactly when {grows} (insert "
                      f"always, pop otherwise)")

    # FATAL: a False-latch — an attr only ever assigned literal
    # False in step, each guarded write classified by shape
    for attr, ws in by_attr.items():
        if not ws or not all(
                w["kind"] == "Assign"
                and isinstance(w["value"], ast.Constant)
                and w["value"].value is False for w in ws):
            continue
        claimed.add(attr)
        for w in ws:
            if not w["guards"]:
                continue
            test = w["guards"][-1][0]
            inner = test.operand if isinstance(test, ast.UnaryOp) \
                and isinstance(test.op, ast.Not) else test
            ops = (inner.values if isinstance(inner, ast.BoolOp)
                   else [test])
            for op in ops:
                s = ast.unparse(op)
                op_reads = {n.attr for n in ast.walk(op)
                            if isinstance(n, ast.Attribute)}
                is_member = any(isinstance(c, (ast.In, ast.NotIn))
                                for n in ast.walk(op)
                                if isinstance(n, ast.Compare)
                                for c in n.ops)
                if is_member and op_reads & collections:
                    sheet["fatal"].append(dict(cause="collision",
                                               read=s))
                elif op_reads & config:
                    sheet["fatal"].append(dict(cause="wall",
                                               read=s))
                elif op_reads & set(sheet["buffers"]):
                    sheet["fatal"].append(dict(cause="exhaustion",
                                               read=s))
                    for b in op_reads & set(sheet["buffers"]):
                        sheet["buffers"][b]["death_at_zero"] = True

    # LOCKOUT: input-derived local overwritten from state
    for w in writes:
        if w.get("kind") == "input_discard" and w["guards"]:
            sheet["forbidden"].append(dict(
                action="reverse",
                read=ast.unparse(w["guards"][-1][0]),
                receipt="the commanded input is overwritten from "
                        "persistent state — the transition does "
                        "not exist"))

    sheet["free"] = sorted(written - read_names - claimed)
    return sheet


# ── THE RETUNE COURT (the scaling campaign's rung 3, owner
# 2026-07-19: learning, discovery, and APPLICATION — read the
# sheet, edit the text at the reading's own location, echo by
# re-reading, verify by RUNNING both versions). v1 scope, said:
# retunes of CONSTANT readings only (reward valence, buffer
# drain/refill/cap); structural changes (guards, growth, fatal)
# are named v2. The program is DATA; nothing here learns. ─────────

def _splice(src, loc, new_text):
    lines = src.split("\n")
    if loc["l0"] != loc["l1"]:
        return None
    i = loc["l0"] - 1
    line = lines[i]
    lines[i] = line[:loc["c0"]] + new_text + line[loc["c1"]:]
    return "\n".join(lines)


def retune(class_src, changes):
    """changes: list of dict(court='rewards'|'buffers', attr=...,
    field='valence'|'drain'|'refill'|'cap', to=<number>). Edits are
    spliced at the sheet's own read locations (deepest-first so
    offsets hold), then the ECHO COURT re-reads the edited text and
    every requested field must read back exactly `to` — a mis-edit
    is visible at the door, never downstream."""
    sheet = read_goal_sheet(class_src)
    plan = []
    for ch in changes:
        court, attr = ch.get("court"), ch.get("attr")
        field, to = ch.get("field"), ch.get("to")
        entry = (sheet.get(court) or {}).get(attr)
        if entry is None:
            return dict(refused=f"no {court} entry '{attr}' read "
                                f"from this program")
        if court == "rewards" and field == "valence":
            loc, op = entry.get("loc"), entry.get("op")
        elif court == "buffers" and field == "drain":
            loc, op = entry.get("drain_loc"), entry.get("drain_op")
        elif court == "buffers" and field in ("refill", "cap"):
            loc, op = entry.get(f"{field}_loc"), "Add"
        else:
            return dict(refused=f"field '{field}' is outside the "
                                f"v1 retune scope (constant "
                                f"readings only: valence/drain/"
                                f"refill/cap)")
        if loc is None:
            return dict(refused=f"'{attr}.{field}' was read "
                                f"without a spliceable location")
        literal = -to if op == "Sub" else to
        if literal != int(literal) and field in ("cap",):
            pass
        text = (f"{int(literal)}" if float(literal).is_integer()
                else f"{literal}")
        plan.append((loc, text, ch))
    plan.sort(key=lambda p: (p[0]["l0"], p[0]["c0"]), reverse=True)
    edited = class_src
    for loc, text, _ch in plan:
        edited = _splice(edited, loc, text)
        if edited is None:
            return dict(refused="multi-line value — outside the "
                                "v1 splice")
    echo = read_goal_sheet(edited)
    receipts = []
    for _loc, _text, ch in plan:
        entry = (echo.get(ch["court"]) or {}).get(ch["attr"], {})
        got = entry.get(ch["field"])
        if got != ch["to"]:
            return dict(refused=f"echo failed: "
                                f"{ch['attr']}.{ch['field']} "
                                f"reads {got}, wanted {ch['to']}")
        receipts.append(f"{ch['attr']}.{ch['field']}: "
                        f"{ch['to']} (echoed from the edited text)")
    return dict(edited=edited, echo=receipts, sheet=echo)


def behavior_delta(src_a, src_b, ns_extra, actions, cls=None):
    """THE INSTRUMENT: run BOTH versions on the same drive and
    report each numeric attribute's per-step deltas. The drive
    (globals + action sequence) is the caller's DATA — the organ
    knows no program's vocabulary."""
    def run(src):
        ns = dict(ns_extra)
        exec(compile(src, "<retune>", "exec"), ns)  # noqa: S102
        klass = ns[cls] if cls else next(
            v for v in ns.values()
            if isinstance(v, type) and hasattr(v, "step"))
        g = klass()
        traj = []
        for a in actions:
            g.step(a)
            traj.append({k: v for k, v in vars(g).items()
                         if isinstance(v, (int, float, bool))
                         and not k.startswith("_")})
        return traj
    ta, tb = run(src_a), run(src_b)
    deltas = {}
    keys = set().union(*[set(t) for t in ta + tb])
    for k in sorted(keys):
        da = [t.get(k) for t in ta]
        db = [t.get(k) for t in tb]
        if da != db:
            first = next(i for i in range(min(len(da), len(db)))
                         if da[i] != db[i])
            steps_b = [round(float(db[i]) - float(db[i - 1]), 9)
                       for i in range(1, len(db))
                       if isinstance(db[i], (int, float))
                       and isinstance(db[i - 1], (int, float))]
            deltas[k] = dict(first_divergence=first,
                             a_at=da[first], b_at=db[first],
                             b_step_deltas=sorted(set(steps_b)),
                             b_max=max(v for v in db
                                       if isinstance(v,
                                                     (int, float))))
    return deltas
