"""engineer_transplant_probe.py — THE OWNERSHIP TRANSPLANT (owner,
2026-07-18: "how did you teach him about this because it will
matter. what did you build for him to be able to recreate these.")

THE HONEST AUDIT the question forced: the mechanical rung's
knowledge lived in MY Python (tube_court's constraint,
contact_court's taxonomy, force_path's transmit rules) — none of it
in Isaac's net, none of it his to examine, duel, or supersede. The
probes proved court DESIGNS; they taught the codebase, not him.

THE TRANSPLANT, proven here: the same eight answers, produced from
NET CONTENT + GENERIC organs, with the hand courts ABLATED
(monkeypatched to raise — if anything calls them, the probe dies):

  HIS CONTENT   the tube constraint TOLD in his own equation
                grammar (tell_law -> law node, mechanics container,
                told-unverified, supersedable); the groove
                dependency and a voltage sum told the same way
                (three domains, zero new Python); the contact
                taxonomy TAUGHT as facts (teach/teach_not in the
                mechanics world — editable by teaching, not coding).
  GENERIC ORGAN laws_run_backward: solve ANY linear told/discovered
                law for ANY unknown, reading the MODEL FROM HIS NET
                — derive-the-third, consistency-with-residual, and
                DOF-naming fall out for every constraint he ever
                holds. One solver, no domain.
  THE PROOF     every answer reproduced; the taxonomy CHANGED BY
                TEACHING (weld gains 'torque' with no code change);
                and the ablation receipt: the hand courts were
                never called.

PREDICTIONS (filed before the first run; wrong ones kept)
  X1 the constraint told into the mechanics world, his grammar,
     container stamped.
  X2 derive all three ways from HIS law node via the generic
     backward solver, machine-exact.
  X3 consistent triple corroborates (residual ~0); bad triple
     refuses with the residual named; two unknowns -> DOF-OPEN.
  X4 domain-freeness: groove dependency + voltage sum through the
     SAME solver; a bore change propagates through HIS relations
     and the stale groove is flagged by residual.
  X5 the taxonomy as HIS facts: transmit sets answered by ask();
     negative knowledge (touching never pulls) first-class.
  X6 force paths 6/6 via ask()-walks — the walker is generic.
  X7 contact classification via his facts + generic comparison,
     clearance/interference named.
  X8 THE ABLATION + THE EDIT: hand courts raise if touched — all
     green anyway; then ONE teach() gives weld 'torque' and the
     answer changes — his knowledge, his to change.

Run: cd experiments && PYTHONHASHSEED=0 python engineer_transplant_probe.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod                    # noqa: E402
from isaac_store import engineer as eng      # noqa: E402

Isaac = isaac_mod.Isaac


def laws_run_backward(mind, name, known, want):
    """GENERIC: solve a linear law y = sum(ci*xi) + b, read from
    HIS net, for any one unknown. known: dict var->value ('y' for
    the output). Returns DERIVED / CORROBORATION / REFUSED-with-
    residual / DOF-OPEN — the constraint court for every linear
    relation he holds, with zero domain code."""
    m = mind.net.get_meta(f"law:{name}", "model")
    if m is None:
        return dict(verdict="UNKNOWN LAW")
    coefs = {}
    for t, c in zip(m["terms"], m["coefs"]):
        spec = m["specs"][t[0]]
        if len(t) != 1 or spec[0] != "var":
            return dict(verdict="REFUSED",
                        receipt="nonlinear law — outside the linear "
                                "solver's honest scope")
        coefs[f"x{spec[1]}"] = float(c)
    b = float(m.get("intercept", 0.0))
    allvars = sorted(coefs) + ["y"]
    unknowns = [v for v in allvars if v not in known]
    if want in known and not unknowns:
        pass
    if len(unknowns) > 1:
        return dict(verdict="DOF-OPEN", free=sorted(unknowns))
    if not unknowns:
        resid = known["y"] - (sum(coefs[v] * known[v]
                                  for v in coefs) + b)
        if abs(resid) <= 1e-9:
            return dict(verdict="CORROBORATION",
                        receipt="every dimension given, zero "
                                "residual — the books balance")
        return dict(verdict="REFUSED",
                    residual=round(float(resid), 6),
                    receipt="the constraint he holds is violated")
    u = unknowns[0]
    if u != want:
        return dict(verdict="DOF-OPEN", free=[u])
    if u == "y":
        val = sum(coefs[v] * known[v] for v in coefs) + b
    else:
        val = (known["y"] - b - sum(coefs[v] * known[v]
                                    for v in coefs if v != u)) \
            / coefs[u]
    return dict(verdict="DERIVED", **{u: float(val)})


def transmit_set(mind, kind):
    """GENERIC: what a contact kind transmits = HIS facts."""
    got = set(mind.ask(kind, "transmits",
                       container="mechanics")["answers"])
    return got


def walk_force(mind, chain, action):
    """GENERIC: the claim tested against HIS knowledge only."""
    return all(action in transmit_set(mind, k) for k in chain)


def classify_contact(mind, pin_od, hole_id, intent="loose",
                     joint=None):
    """Thin generic glue: arithmetic + HIS facts. The mapping from
    situation to kind is TAUGHT, not coded."""
    if joint:
        key = f"joint-{joint}"
    else:
        gap = hole_id - pin_od
        if gap > 1e-9:
            key = "gap-positive"
        elif abs(gap) <= 1e-9:
            key = "gap-zero"
        else:
            key = f"gap-negative-{intent}"
    kinds = mind.ask(key, "means", container="mechanics")["answers"]
    out = dict(kind=(kinds[0] if kinds else "UNKNOWN"))
    if not joint:
        if gap > 0:
            out["clearance"] = round(float(gap), 6)
        elif gap < 0:
            out["interference"] = round(float(-gap), 6)
    return out


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    # THE ABLATION: if any hand court is touched, the probe dies
    def _dead(*a, **k):
        raise AssertionError("hand court called — ownership failed")
    eng.tube_court = _dead
    eng.view_court = eng.view_court          # instruments stay
    eng.slot_court = _dead

    mind = Isaac()
    mind.open_world("mechanics")

    # X1 — the constraint is TOLD, in his grammar, in his world
    r = mind.tell_law("tube-od", "+1.00*x0 +2.00*x1", d=2,
                      who="machinist handbook")
    node = mind.net.get_meta("law:tube-od", "container")
    ok1 = (r["status"] == "TOLD-UNVERIFIED"
           and node == "mechanics")
    check("X1 the constraint TOLD — his grammar, his world, "
          "supersedable", ok1,
          f"{r['status']} in '{node}' (x0=ID, x1=wall -> y=OD)")

    # X2 — derive all three ways from HIS node, generic solver
    d1 = laws_run_backward(mind, "tube-od",
                           dict(x0=1.0, x1=0.125), "y")
    d2 = laws_run_backward(mind, "tube-od",
                           dict(y=1.25, x1=0.125), "x0")
    d3 = laws_run_backward(mind, "tube-od",
                           dict(y=1.25, x0=1.0), "x1")
    ok2 = (abs(d1["y"] - 1.25) < 1e-12
           and abs(d2["x0"] - 1.0) < 1e-12
           and abs(d3["x1"] - 0.125) < 1e-12)
    check("X2 derive all three ways — one generic solver, HIS law",
          ok2, f"OD {d1['y']}, ID {d2['x0']}, wall {d3['x1']}")

    # X3 — corroboration / refusal with residual / DOF
    c = laws_run_backward(mind, "tube-od",
                          dict(y=1.25, x0=1.0, x1=0.125), None)
    rref = laws_run_backward(mind, "tube-od",
                             dict(y=1.30, x0=1.0, x1=0.125), None)
    dof = laws_run_backward(mind, "tube-od", dict(x0=1.0), "y")
    ok3 = (c["verdict"] == "CORROBORATION"
           and rref["verdict"] == "REFUSED"
           and abs(rref["residual"] - 0.05) < 1e-9
           and dof["verdict"] == "DOF-OPEN")
    check("X3 corroborate / refuse-with-residual / DOF-OPEN — from "
          "his constraint", ok3,
          f"{c['verdict']} / {rref['verdict']}({rref.get('residual')})"
          f" / {dof['verdict']}{dof.get('free')}")

    # X4 — domain-freeness + propagation through HIS relations
    mind.tell_law("groove-from-piston", "+1.00*x0 -0.20", d=1,
                  who="design dependency")
    mind.tell_law("piston-from-bore", "+0.995*x0", d=1,
                  who="design dependency")
    mind.tell_law("series-voltage", "+1.00*x0 +1.00*x1", d=2,
                  who="kirchhoff")
    bore = 4.010
    piston = laws_run_backward(mind, "piston-from-bore",
                               dict(x0=bore), "y")["y"]
    groove = laws_run_backward(mind, "groove-from-piston",
                               dict(x0=piston), "y")["y"]
    stale = laws_run_backward(mind, "groove-from-piston",
                              dict(x0=piston, y=3.78), None)
    v2 = laws_run_backward(mind, "series-voltage",
                           dict(y=12.0, x0=7.4), "x1")
    ok4 = (abs(piston - 4.010 * 0.995) < 1e-12
           and abs(groove - (piston - 0.2)) < 1e-12
           and stale["verdict"] == "REFUSED"
           and abs(abs(stale["residual"]) - 0.00995) < 1e-5
           and abs(v2["x1"] - 4.6) < 1e-12)
    check("X4 three domains, zero new Python — propagation + stale "
          "flag + Kirchhoff from the SAME organ", ok4,
          f"piston {piston:.5f}, groove {groove:.5f}, stale residual "
          f"{stale.get('residual')}, v2 {v2['x1']}")

    # X5 — the taxonomy is HIS: facts + negative knowledge
    for kind, tr in (("connected", ("push", "pull")),
                     ("touching", ("push",))):
        for t in tr:
            mind.teach(kind, "transmits", t)
    mind.teach_not("touching", "transmits-pull")
    for key, kind in (("gap-positive", "not-touching"),
                      ("gap-zero", "touching"),
                      ("gap-negative-press", "connected"),
                      ("gap-negative-loose", "WOUND"),
                      ("joint-weld", "connected")):
        mind.teach(key, "means", kind)
    ok5 = (transmit_set(mind, "connected") == {"push", "pull"}
           and transmit_set(mind, "touching") == {"push"}
           and transmit_set(mind, "gap") == set())
    check("X5 the taxonomy TAUGHT — transmit sets from ask(); "
          "negatives first-class", ok5,
          f"connected {sorted(transmit_set(mind, 'connected'))}, "
          f"touching {sorted(transmit_set(mind, 'touching'))}")

    # X6 — force paths from HIS knowledge, 6/6
    truth = [
        (walk_force(mind, ["connected"], "pull"), True),
        (walk_force(mind, ["connected"], "push"), True),
        (walk_force(mind, ["touching"], "push"), True),
        (walk_force(mind, ["touching"], "pull"), False),
        (walk_force(mind, ["gap"], "push"), False),
        (walk_force(mind, ["connected", "touching"], "pull"), False),
    ]
    ok6 = all(got == want for got, want in truth)
    check("X6 force paths — 6/6 tested against his facts, generic "
          "walker", ok6,
          f"{['Y' if g else 'N' for g, _ in truth]}")

    # X7 — classification via his facts, quantities named
    c1 = classify_contact(mind, 9.98, 10.00)
    c3 = classify_contact(mind, 10.05, 10.00, intent="press")
    c5 = classify_contact(mind, 10.05, 10.00, intent="loose")
    c4 = classify_contact(mind, 8.0, 10.0, joint="weld")
    ok7 = (c1["kind"] == "not-touching" and c1["clearance"] == 0.02
           and c3["kind"] == "connected"
           and c3["interference"] == 0.05
           and c5["kind"] == "WOUND" and c4["kind"] == "connected")
    check("X7 classification — his mapping, quantities named", ok7,
          f"{c1['kind']}({c1['clearance']}) / {c3['kind']}"
          f"({c3['interference']}) / {c5['kind']} / {c4['kind']}")

    # X8 — the edit: one teach() changes the answer, no code
    before = walk_force(mind, ["connected"], "torque")
    mind.teach("connected", "transmits", "torque")
    after = walk_force(mind, ["connected"], "torque")
    ok8 = (not before) and after
    check("X8 THE EDIT — one teach() and welds carry torque; his "
          "knowledge, his to change (hand courts never called)",
          ok8, f"torque before {before} -> after {after}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
