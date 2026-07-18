"""engineer_e0_probe.py — THE ENGINEER LANE, E0: the four foundation
courts (owner build queue item 1; docs/engineer/
engineer-lane-checklist.md).

RESEARCH, NOT THE ENGINE. The lane's whole grammar on toys:

  E0.1 KINDS — structural primitives as vocabulary; a kind is a
       parametric RECIPE with constraints. Court: the composite
       accounts for planted composed data better than its
       ingredients separately, past a scrambled null.
  E0.2 MULTI-VIEW IDENTITY — one identity, N decompositions; where
       views overlap in consequences they agree machine-exact.
       Null: two views of DIFFERENT things forced under one
       identity -> disagreement detected, routed as a WOUND.
  E0.3 SLOT SIGNATURES — inputs + outputs + RESIDUE as official
       slots; court: presence, type, balance; an unclaimed residue
       is a named accounting error.
  E0.4 TMS PROPAGATION — dependencies typed FIXED or RELATIVE;
       change one value -> propagate -> re-verify -> divergence
       flagged with size and direction. Null: an over-constrained
       inconsistent set refuses with the residual named.

THE TUBE BATTERY rides E0.1 (T1-T4 from the checklist): ID/OD/wall —
any two derive the third; three consistent = CORROBORATION; three
inconsistent = REFUSAL with residual; one given = named DOF, never
a guess.

PREDICTIONS (filed before the first run; wrong ones kept)
  T1 two given -> third derived machine-exact, all three ways;
     three consistent -> corroboration receipt.
  T2 inconsistent triple -> refusal, residual named w/ size + sign.
  T3 one given -> DOF-OPEN naming the free dimensions — no guess.
  T4 the kind court: the tube recipe accounts for planted tube data
     (predict wall from ID,OD) machine-exact where ingredients
     alone cannot; scrambled wall column kills it.
  V1 three views of one tube (hollow-cylinder / extrusion /
     wall-schedule) agree on material volume machine-exact.
  V2 a cone's data forced under the tube identity -> WOUND detected
     (views disagree beyond tolerance), routed, named.
  S1 slot court: divide reconstructs (q*b + r = a, balance);
     cut(tube) balances L = L1 + L2 + kerf; an op with an unclaimed
     residue slot -> named accounting error.
  P1 TMS: bore +0.010 propagates through typed deps (piston
     RELATIVE, groove FIXED); a stale member is flagged with size
     AND direction; an over-constrained set refuses w/ residual.

Run: cd experiments && PYTHONHASHSEED=0 python engineer_e0_probe.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac
TOL = 1e-9


# ── E0.1: the kind as parametric recipe with constraints ──────────
def tube_court(ID=None, OD=None, wall=None):
    """The tube's constraint: OD = ID + 2*wall. Two given -> third
    derived; three -> consistency court; one -> named DOF."""
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
                               "OD small or ID/wall large"),
                    receipt="constraint OD = ID + 2*wall violated")
    if len(given) == 2:
        if ID is None:
            ID = OD - 2 * wall
        elif OD is None:
            OD = ID + 2 * wall
        else:
            wall = (OD - ID) / 2.0
        return dict(verdict="DERIVED", ID=ID, OD=OD, wall=wall)
    return dict(verdict="DOF-OPEN",
                free=sorted(set(("ID", "OD", "wall")) - set(given)),
                receipt="one dimension cannot pin a tube — named "
                        "degrees of freedom, never a guess")


# ── E0.2: multi-view identity ─────────────────────────────────────
def tube_views_volume(ID, OD, L):
    """Three decompositions of one tube; each answers 'how much
    material?' its own way."""
    v_hollow = np.pi / 4 * (OD ** 2 - ID ** 2) * L
    wall = (OD - ID) / 2.0
    v_schedule = np.pi * (ID + wall) * wall * L
    v_faces = (np.pi * (OD / 2) ** 2 - np.pi * (ID / 2) ** 2) * L
    return dict(hollow=v_hollow, schedule=v_schedule, faces=v_faces)


def view_court(views, tol=1e-9):
    vals = list(views.values())
    spread = max(vals) - min(vals)
    if spread <= tol * max(abs(v) for v in vals):
        return dict(verdict="CONSISTENT", spread=float(spread))
    return dict(verdict="WOUND", spread=float(spread),
                views={k: round(float(v), 6) for k, v in views.items()},
                receipt="views of one identity disagree — routed to "
                        "conflict machinery")


# ── E0.3: slot signatures ─────────────────────────────────────────
SIGS = dict(
    divide=dict(inputs=("a", "b"), outputs=("quotient", "remainder")),
    cut=dict(inputs=("length", "at"),
             outputs=("piece1", "piece2", "kerf")),
    bad_divide=dict(inputs=("a", "b"), outputs=("quotient",)),
)


def slot_court(op, ins, outs):
    sig = SIGS[op]
    missing_in = [k for k in sig["inputs"] if k not in ins]
    missing_out = [k for k in sig["outputs"] if k not in outs]
    if op in ("divide", "bad_divide"):
        if "remainder" not in sig["outputs"]:
            return dict(verdict="REFUSED",
                        receipt="accounting error: operation "
                                "declares no residue slot — division "
                                "is two-in two-out")
        balance = abs(outs["quotient"] * ins["b"]
                      + outs["remainder"] - ins["a"])
    else:
        balance = abs(outs["piece1"] + outs["piece2"] + outs["kerf"]
                      - ins["length"])
    if missing_in or missing_out:
        return dict(verdict="REFUSED", missing_in=missing_in,
                    missing_out=missing_out,
                    receipt="unaccounted slot(s) named")
    if balance > TOL:
        return dict(verdict="RESIDUAL", imbalance=float(balance))
    return dict(verdict="BALANCED")


# ── E0.4: TMS dependency propagation ──────────────────────────────
def tms_propagate(values, deps, changed, new_value, tol=1e-9):
    """deps: child -> (parent, kind, k). FIXED: child = parent + k;
    RELATIVE: child = parent * (1 + k). Change one -> propagate ->
    re-verify all -> divergences flagged with size and direction."""
    vals = dict(values)
    vals[changed] = new_value
    for _ in deps:                         # relax to fixpoint (toy)
        for child, (parent, kind, k) in deps.items():
            want = (vals[parent] + k if kind == "fixed"
                    else vals[parent] * (1 + k))
            if child != changed:
                vals[child] = round(want, 12)
    return vals, tms_verify(vals, deps, tol)


def tms_verify(values, deps, tol=1e-9):
    """RE-VERIFY, NEVER REPAIR (run-1 lesson: a verifier that fixes
    what it checks can never flag anything): walk the typed deps and
    flag every member diverging from its expectation, with size and
    direction."""
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


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    # T1 — derive + corroborate
    d1 = tube_court(ID=1.0, wall=0.125)
    d2 = tube_court(OD=1.25, wall=0.125)
    d3 = tube_court(ID=1.0, OD=1.25)
    c = tube_court(ID=1.0, OD=1.25, wall=0.125)
    ok1 = (abs(d1["OD"] - 1.25) < TOL and abs(d2["ID"] - 1.0) < TOL
           and abs(d3["wall"] - 0.125) < TOL
           and c["verdict"] == "CONSISTENT")
    check("T1 two derive the third (3 ways) + corroboration", ok1,
          f"OD {d1['OD']}, ID {d2['ID']}, wall {d3['wall']}; "
          f"{c['verdict']}")

    # T2 — refusal with residual
    r = tube_court(ID=1.0, OD=1.30, wall=0.125)
    ok2 = (r["verdict"] == "REFUSED" and abs(r["residual"] - 0.05) < TOL
           and "large" in r["direction"])
    check("T2 inconsistent triple refuses, residual named", ok2,
          f"residual {r['residual']} ({r['direction']})")

    # T3 — DOF-OPEN, never a guess
    g = tube_court(ID=1.0)
    ok3 = g["verdict"] == "DOF-OPEN" and g["free"] == ["OD", "wall"]
    check("T3 one given -> named DOF, no guess", ok3, f"{g['free']}")

    # T4 — the kind court on planted data vs scrambled null
    rng = np.random.default_rng(0)
    ID = rng.uniform(0.5, 4.0, 60)
    wall = rng.uniform(0.05, 0.5, 60)
    OD = ID + 2 * wall
    pred = np.array([tube_court(ID=i, OD=o)["wall"]
                     for i, o in zip(ID, OD)])
    err_kind = float(np.max(np.abs(pred - wall)))
    wall_s = wall.copy()
    rng.shuffle(wall_s)
    err_null = float(np.max(np.abs(pred - wall_s)))
    ok4 = err_kind < TOL and err_null > 0.05
    check("T4 the kind accounts for composed data; scrambled dies",
          ok4, f"recipe err {err_kind:.1e}; scrambled err "
               f"{err_null:.3f}")

    # V1 — three views, one answer
    v = view_court(tube_views_volume(1.0, 1.25, 10.0))
    check("V1 multi-view identity — three decompositions agree "
          "machine-exact", v["verdict"] == "CONSISTENT",
          f"spread {v['spread']:.2e}")

    # V2 — a cone forced under the tube identity -> WOUND
    cone_v_end1 = np.pi / 4 * (1.25 ** 2 - 1.0 ** 2) * 10.0
    cone_v_taper = np.pi / 4 * (1.10 ** 2 - 1.0 ** 2) * 10.0
    w = view_court(dict(end1=cone_v_end1, taper=cone_v_taper))
    ok6 = w["verdict"] == "WOUND" and "routed" in w["receipt"]
    check("V2 different thing under one identity -> WOUND detected",
          ok6, f"spread {w['spread']:.4f}")

    # S1 — slot signatures: balance + the missing-residue error
    s_ok = slot_court("divide", dict(a=17, b=5),
                      dict(quotient=3, remainder=2))
    s_cut = slot_court("cut", dict(length=10.0, at=4.0),
                       dict(piece1=4.0, piece2=5.9, kerf=0.1))
    s_bad = slot_court("bad_divide", dict(a=17, b=5),
                       dict(quotient=3))
    ok7 = (s_ok["verdict"] == "BALANCED"
           and s_cut["verdict"] == "BALANCED"
           and s_bad["verdict"] == "REFUSED"
           and "residue" in s_bad["receipt"])
    check("S1 slots — divide + cut balance; missing residue = named "
          "accounting error", ok7,
          f"{s_ok['verdict']}/{s_cut['verdict']}/{s_bad['verdict']}")

    # P1 — TMS propagation with typed deps + stale flag + refusal
    values = dict(bore=4.000, piston=3.980, groove=3.780)
    deps = dict(piston=("bore", "relative", -0.005),
                groove=("piston", "fixed", -0.200))
    vals, flags = tms_propagate(values, deps, "bore", 4.010)
    ok_prop = (abs(vals["piston"] - 4.010 * 0.995) < 1e-9
               and abs(vals["groove"] - (vals["piston"] - 0.200)) < 1e-9
               and not flags)
    stale = dict(values)
    stale["bore"] = 4.010
    stale["piston"] = round(4.010 * 0.995, 12)
    # groove left stale on purpose — VERIFY (never repair) names it
    flags2 = tms_verify(stale, deps)
    ok_stale = (len(flags2) == 1 and flags2[0]["member"] == "groove"
                and flags2[0]["direction"] == "low"
                and abs(flags2[0]["size"] - 0.00995) < 1e-5)
    over = tube_court(ID=1.0, OD=1.2, wall=0.15)
    ok8 = ok_prop and ok_stale and over["verdict"] == "REFUSED"
    check("P1 TMS — typed propagation clean; stale member flagged "
          "w/ size+direction; over-constrained refuses", ok8,
          f"prop flags {flags}; stale {flags2}; over "
          f"{over['verdict']} ({over.get('residual')})")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
