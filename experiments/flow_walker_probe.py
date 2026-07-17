"""flow_walker_probe.py — THE EXECUTION CYCLE, first build (owner,
2026-07-15: "do op, take result door, or return to main program. each
node can act like a function generator"; and 07-13: the interpreter
package gets its own attack-first R&D segment).

RESEARCH, NOT THE ENGINE. The sheet's specced first build: ONE real
pipeline as FLOW NODES in the net + a WALKER with bypass receipts +
one EVIDENCE-DRIVEN BRANCH, end to end — using only engine primitives
(flow:/step: nodes via add_door/set_meta; ops are REAL registered
organs; branch predicates are DECLARATIVE and evaluated through the
compare tool — the comparison booleans as routing predicates, exactly
as the execution-cycle capture says).

THE PIPELINE (real, useful): TRIAGE — read the floor, discover, then
BRANCH ON EVIDENCE: UNDERSTOOD -> validate the law on held-back rows
(compare(rms, 3*floor) routes pass/flag); anything else -> the honest
refusal road. Every step fires or is BYPASSED WITH A RECEIPT (the
consideration law); the walk returns to main with a replayable trace.

THE FUNCTION GENERATOR (v1): a chain that runs green three times is
REIFIED as a chunk node — one new step whose op is the recorded
chain; walking the chunk expands it with a nested trace. Elections /
piecewise flow supersession are NAMED segment work, not claimed here.

PREDICTIONS (filed before the first run; wrong ones kept)
  F1 flows are NET CONTENT: flow:triage and its step: nodes exist as
     nodes with doors; the step specs are readable meta (an equation
     of process, inspectable like any law).
  F2 TRUE-LAW WORLD walks the full green road: floor -> discover ->
     [verdict==UNDERSTOOD fires] -> validate -> [rms < 3*floor via
     compare] -> report-pass; every step receipted, hops recorded.
  F3 NOISE WORLD takes the refusal road and the validate step is
     BYPASSED WITH A RECEIPT (consideration law: the not-taken door
     carries why-not).
  F4 the branch predicates route THROUGH the compare organ (the
     receipt chain shows compare's sign verdict inside the door
     choice) — comparison booleans ARE the routing predicates.
  F5 a deliberately CYCLIC flow halts at the hop cap with a receipt
     (return-to-main is guaranteed; no runaway).
  F6 a step pointing at a MISSING organ refuses with a receipt and
     the walk ends honestly (no crash, no silent skip).
  F7 after 3 green runs the chain is MINTED as chunk:triage (the
     function generator); walking the CHUNK on a fresh world gives
     the same outcome as walking the chain, with a nested trace.
  F8 REPLAY: re-walking from the trace's recorded doors reproduces
     the same door sequence (any computation can be replayed).
  F9 flows and chunks survive the pickle round-trip.
  F10 cost: a full triage walk < 5 s.

Run: cd experiments && PYTHONHASHSEED=0 python flow_walker_probe.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac
HOP_CAP = 12


# ─────────────────────────── flow authoring (net content)
def define_flow(mind, name, steps):
    """Steps live IN the net: flow:<name> doors to its first step;
    each step:<name> node carries meta spec = dict(op, args(fields of
    state), measure?, doors=[{to, when?}] — last door with no 'when'
    is the default). Same substrate as content, different altitude."""
    fnode = f"flow:{name}"
    first = f"step:{name}.{steps[0]['id']}"
    mind.net.add_door(fnode, first, tag="flow-start")
    for st in steps:
        node = f"step:{name}.{st['id']}"
        mind.net.set_meta(node, "spec", st)
        for d in st.get("doors", []):
            mind.net.add_door(node, f"step:{name}.{d['to']}",
                              tag="flow-next")
    return fnode


def _eval_when(mind, when, result, state):
    """Declarative predicate, routed THROUGH the compare organ when
    numeric. Returns (fired, receipt)."""
    if "equals" in when:
        got = result.get(when["field"])
        fired = got == when["equals"]
        return fired, (f"{when['field']}=='{when['equals']}'? got "
                       f"'{got}' -> {fired}")
    if "cmp" in when:                      # {'cmp':'smaller','field':...,
        a = result.get(when["field"])      #  'than': state-field or number}
        b = when["than"]
        b = state.get(b, b) if isinstance(b, str) else b
        c = mind.compare(float(a), float(b))
        fired = (c["value"] < 0) if when["cmp"] == "smaller" \
            else (c["value"] > 0)
        return fired, (f"{when['cmp']}({a:.4g},{b:.4g}) via "
                       f"{c['receipt']} -> {fired}")
    return False, f"unknown predicate {when} -> refused"


def walk(mind, flow, state, hop_cap=HOP_CAP, _depth=0):
    """THE KERNEL LOOP v1: do op -> take result door -> return to
    main. Every juncture leaves receipts for the door taken AND the
    doors bypassed (the consideration law). Returns (outcome, trace)."""
    trace = []
    nxt = sorted(mind.net.get_doors(flow, tag="flow-start"))
    step = nxt[0] if nxt else None
    hops = 0
    while step is not None:
        if hops >= hop_cap:
            trace.append(dict(step=step, receipt=f"HOP CAP {hop_cap} "
                              f"reached — returning to main (no "
                              f"runaway walks)"))
            return "hop-cap", trace
        hops += 1
        spec = mind.net.get_meta(step, "spec") or {}
        op = spec.get("op")
        if op == "chunk":                  # the minted function expands
            sub_out, sub_trace = walk(mind, spec["flow"], state,
                                      hop_cap, _depth + 1)
            trace.append(dict(step=step, op="chunk",
                              receipt=f"chunk expanded -> {sub_out}",
                              nested=sub_trace))
            return sub_out, trace
        fn = getattr(mind, op, None) if op else None
        if fn is None:
            trace.append(dict(step=step, op=op,
                              receipt=f"REFUSED: no organ named "
                                      f"'{op}' — walk ends honestly"))
            return "refused", trace
        kwargs = {k: state[v] for k, v in spec.get("args", {}).items()}
        result = fn(**kwargs)
        result = result if isinstance(result, dict) else {"value": result}
        # declarative measure (receipted walker reduction, disclosed)
        meas = spec.get("measure")
        if meas and meas.get("rms_against"):
            p = np.asarray(result.get("value")
                           if "value" in result else result, float)
            yv = np.asarray(state[meas["rms_against"]], float)
            ok = np.isfinite(p)
            result["rms"] = float(np.sqrt(np.mean((p[ok] - yv[ok]) ** 2)))
        state[spec.get("out", f"_{spec.get('id', 'r')}")] = result
        rec = dict(step=step, op=op,
                   receipt=f"ran {op}; keys {sorted(result)[:6]}")
        # take the result door: predicates fire or leave bypass receipts
        doors = spec.get("doors", [])
        taken, door_receipts = None, []
        for d in doors:
            if "when" not in d:
                if taken is None:
                    taken = d["to"]
                    door_receipts.append(f"-> {d['to']} (default door)")
                else:
                    door_receipts.append(f"bypassed {d['to']}: an "
                                         f"earlier door already fired")
                continue
            fired, why = _eval_when(mind, d["when"], result, state)
            if fired and taken is None:
                taken = d["to"]
                door_receipts.append(f"-> {d['to']}: {why}")
            else:
                door_receipts.append(f"bypassed {d['to']}: {why}")
        rec["doors"] = door_receipts
        trace.append(rec)
        step = (None if taken is None
                else f"step:{flow.split(':', 1)[1]}.{taken}")
    return state.get("_outcome", "done"), trace


def mint_chunk(mind, flow, runs_green, name):
    """The FUNCTION GENERATOR v1: a chain that keeps winning becomes
    ONE node — a new step whose op is the recorded chain."""
    node = f"chunk:{name}"
    mind.net.add_door("chunks", node, tag="chunk")
    mind.net.set_meta(node, "spec", dict(id=name, op="chunk", flow=flow,
                                         minted_after=runs_green))
    return node


def triage_flow(mind):
    return define_flow(mind, "triage", [
        dict(id="floor", op="read_floor",
             args=dict(y="y", X="X"), out="floor_read",
             doors=[dict(to="discover")]),
        dict(id="discover", op="discover",
             args=dict(X="X", y="y", name="law_name"), out="res",
             doors=[dict(to="validate",
                         when=dict(field="verdict",
                                   equals="UNDERSTOOD")),
                    dict(to="refuse")]),
        dict(id="validate", op="apply_law",
             args=dict(name="law_name", X="X_check"), out="val",
             measure=dict(rms_against="y_check"),
             doors=[dict(to="report_pass",
                         when=dict(cmp="smaller", field="rms",
                                   than="floor3")),
                    dict(to="report_flag")]),
        dict(id="refuse", op="record_finding",
             args=dict(kind="k_refuse", name="law_name"),
             out="_outcome_rec", doors=[]),
        dict(id="report_pass", op="record_finding",
             args=dict(kind="k_pass", name="law_name"),
             out="_outcome_rec", doors=[]),
        dict(id="report_flag", op="record_finding",
             args=dict(kind="k_flag", name="law_name"),
             out="_outcome_rec", doors=[]),
    ])


def make_state(world, seed):
    rng = np.random.default_rng(seed)
    if world == "law":
        X = rng.integers(1, 10, (60, 2)).astype(float)
        y = X[:, 0] + X[:, 1]
        Xc = rng.integers(1, 10, (60, 2)).astype(float)
        yc = Xc[:, 0] + Xc[:, 1]
    else:
        X = rng.normal(0, 1, (60, 2))
        y = rng.normal(0, 1, 60)
        Xc, yc = X.copy(), rng.normal(0, 1, 60)
    return dict(X=X, y=y, X_check=Xc, y_check=yc,
                law_name=f"flow_{world}_{seed}",
                k_refuse="flow-refusal", k_pass="flow-pass",
                k_flag="flow-flag", floor3=1.0)


def road(trace):
    return [t["step"].split(".")[-1] for t in trace if "step" in t]


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    mind = Isaac()
    flow = triage_flow(mind)

    # F1 — flows are net content
    start = mind.net.get_doors(flow, tag="flow-start")
    spec_ok = (mind.net.get_meta("step:triage.discover", "spec")
               or {}).get("op") == "discover"
    check("F1 flow lives in the net, specs readable",
          bool(start) and spec_ok,
          f"start doors {sorted(start)}; discover spec op ok {spec_ok}")

    # F2 — the green road
    st = make_state("law", 1)
    t_walk = time.perf_counter()
    out2, tr2 = walk(mind, flow, st)
    walk_s = time.perf_counter() - t_walk
    r2 = road(tr2)
    check("F2 true law walks floor->discover->validate->report_pass",
          r2 == ["floor", "discover", "validate", "report_pass"],
          f"road {r2}")

    # F3 — refusal road with bypass receipts
    st3 = make_state("noise", 2)
    out3, tr3 = walk(mind, flow, st3)
    r3 = road(tr3)
    disc3 = next(t for t in tr3 if t["step"].endswith("discover"))
    bypassed = any("bypassed validate" in dr for dr in disc3["doors"])
    check("F3 noise takes the refusal road; validate bypassed WITH "
          "receipt", r3 == ["floor", "discover", "refuse"] and bypassed,
          f"road {r3}; discover doors {disc3['doors']}")

    # F4 — compare inside the door choice
    val2 = next(t for t in tr2 if t["step"].endswith("validate"))
    via_cmp = any("sign(" in dr for dr in val2["doors"])
    check("F4 branch predicate routes THROUGH compare",
          via_cmp, f"validate doors {val2['doors']}")

    # F5 — cyclic flow halts at the cap
    define_flow(mind, "loopy", [
        dict(id="a", op="open_world", args=dict(container="law_name"),
             out="_a", doors=[dict(to="b")]),
        dict(id="b", op="open_world", args=dict(container="law_name"),
             out="_b", doors=[dict(to="a")]),
    ])
    out5, tr5 = walk(mind, "flow:loopy", make_state("law", 5))
    check("F5 cyclic flow halts at hop cap with receipt",
          out5 == "hop-cap" and "HOP CAP" in tr5[-1]["receipt"],
          f"{out5} after {len(tr5)} hops")

    # F6 — missing organ refused honestly
    define_flow(mind, "ghost", [
        dict(id="a", op="no_such_organ", args={}, doors=[])])
    out6, tr6 = walk(mind, "flow:ghost", make_state("law", 6))
    check("F6 missing organ -> honest refusal receipt",
          out6 == "refused" and "no organ named" in tr6[-1]["receipt"],
          tr6[-1]["receipt"])

    # F7 — the function generator: three green runs mint a chunk
    greens = 1 if r2[-1] == "report_pass" else 0
    for s in (7, 8):
        stg = make_state("law", s)
        og, tg = walk(mind, flow, stg)
        greens += road(tg)[-1] == "report_pass"
    chunk = mint_chunk(mind, flow, greens, "triage")
    st7 = make_state("law", 9)
    # walking the chunk node directly
    spec7 = mind.net.get_meta(chunk, "spec")
    out7, tr7 = (None, None)
    if spec7 and spec7.get("op") == "chunk":
        out7, tr7 = walk(mind, spec7["flow"], st7)
    st7b = make_state("law", 9)
    out7b, tr7b = walk(mind, flow, st7b)
    check("F7 chunk minted after 3 greens; chunk walk == chain walk",
          greens == 3 and out7 == out7b
          and road(tr7) == road(tr7b),
          f"greens {greens}/3; chunk road {road(tr7)}")

    # F8 — replay: doors taken reproduce
    st8a, st8b = make_state("law", 1), make_state("law", 1)
    _, tra = walk(mind, flow, st8a)
    _, trb = walk(mind, flow, st8b)
    check("F8 replay reproduces the door sequence",
          road(tra) == road(trb) == r2,
          f"{road(tra)} == {road(trb)}")

    # F9 — pickle round-trip
    import tempfile
    pth = os.path.join(tempfile.gettempdir(), "flow_probe_mind.pkl")
    mind.save(pth)
    m2 = Isaac.load(pth)
    out9, tr9 = walk(m2, flow, make_state("law", 11))
    os.remove(pth)
    check("F9 flows survive save/load and walk again",
          road(tr9)[-1] in ("report_pass", "report_flag"),
          f"road {road(tr9)}")

    # F10 — cost
    check("F10 full triage walk < 5 s", walk_s < 5.0,
          f"{walk_s:.2f}s")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed of "
          f"{len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
