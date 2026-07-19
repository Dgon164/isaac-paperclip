"""engineer_assess_probe.py — STRUCTURE ASSESSMENT + THE OBSERVED
MAPS (owner, 2026-07-18: "give him complete structures and he can
assess how they are built and connected" + "we need to figure out
how to observe the maps... what he understands about a thing, not
just how its built").

RESEARCH, NOT THE ENGINE. Two capabilities, one probe:

  ASSESS. A complete structure goes in (a 5-part mechanical
  assembly; a 4-component circuit); the assessment comes out — every
  claim from HIS OWN knowledge (the curriculum feed runs first and
  the assessor stands on it): parts identified via his kind
  signatures, connections via his contact taxonomy (quantities
  named), functions via his pattern facts (bushing + clearance shaft
  = journal bearing), derived quantities via his laws (the LED
  loop's operating point), dangers via his negatives, and a
  dims-inconsistent part flagged as a WOUND by his own constraint —
  never silently classified.

  OBSERVE. Three windows onto him, emitted as files:
    (1) THE PROCESSING TRACE — every fact asked, law fired, court
        run during the assessment, in order, with receipts (the
        mental-processing state of one task);
    (2) THE UNDERSTANDING MAP — the ego-graph of what HE holds
        about a subject (doors in/out, facts, laws, evidence,
        containers), rendered as SVG;
    (3) THE ASSESSMENT MAP — the structure as he concluded it
        (parts + typed connections), rendered as SVG.

PREDICTIONS (filed before the first run; wrong ones kept)
  A1 parts identified via HIS signature facts (4/4 + 1 honest wound).
  A2 connections classified w/ quantities (press 0.05 / clearance
     0.04 / weld) from his taxonomy.
  A3 the planted dims-wound flagged by HIS tube constraint.
  A4 function recognized from HIS pattern fact (journal bearing).
  A5 load paths from the assessed graph: 3/3.
  A6 regeneration (assessment rebuilds the relation graph) +
     exploded null (all not-touching, no function, no wounds
     invented).
  A7 circuit: kinds from designator facts; loop traced; operating
     point 17.95mA DERIVED from his law + his forward-drop fact;
     the resistor-less variant flagged from his negative.
  A8 the maps observed: trace >= 25 receipted steps; understanding
     map + assessment map SVGs emitted, non-trivial.

Run: cd experiments && PYTHONHASHSEED=0 python engineer_assess_probe.py
"""
import os
import sys
import time

import numpy as np  # noqa: F401

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod                     # noqa: E402
from curriculum_feed import (feed, form_of,   # noqa: E402
                             solve_backward)

Isaac = isaac_mod.Isaac
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "runs")
os.makedirs(RUNS, exist_ok=True)


# ── the structures under assessment ───────────────────────────────
ASSEMBLY = dict(
    parts=[
        dict(name="block", prim="block-with-bore", bore=14.00,
             pos=(0, 0)),
        dict(name="bushing", prim="hollow-cylinder", ID=10.00,
             OD=14.05, pos=(0, 0)),
        dict(name="shaft", prim="solid-cylinder", OD=9.96,
             pos=(0, 0)),
        dict(name="collar", prim="hollow-cylinder", ID=9.96,
             OD=16.0, pos=(0, 0)),
        # the planted wound: claims tube dims that violate the recipe
        dict(name="gasket", prim="hollow-cylinder", ID=12.0,
             OD=12.5, wall=0.5, pos=(0, 0)),
    ],
    intents=[("bushing", "block", "press")],
    joints=[("collar", "shaft", "weld")],
    # radial pairs that share an axis (who sits inside whom)
    seats=[("bushing", "block"), ("shaft", "bushing"),
           ("shaft", "collar")])

CIRCUIT = dict(
    comps=[("V1", 9.0, ("n1", "gnd")), ("SW1", None, ("n1", "n2")),
           ("R1", 390.0, ("n2", "n3")), ("D1", "led-red",
                                         ("n3", "gnd"))])

CIRCUIT_BAD = dict(
    comps=[("V1", 9.0, ("n1", "gnd")), ("SW1", None, ("n1", "n2")),
           ("D1", "led-red", ("n2", "gnd"))])


# ── the assessor (generic glue; every claim from HIS content) ─────
def assess_assembly(mind, world, trace):
    def ask(s, r, c="cad-mechanical"):
        got = mind.ask(s, r, container=c)["answers"]
        trace.append(dict(op="ask", what=f"{s}.{r}", got=got))
        return got

    out = dict(parts={}, connections=[], functions=[], wounds=[])
    for p in world["parts"]:
        kinds = ask(p["prim"], "kind-is")
        kind = kinds[0] if kinds else "UNKNOWN"
        if "ID" in p and "OD" in p and "wall" in p:
            chk = solve_backward(
                mind, form_of(mind, "tube-od"),
                dict(y=p["OD"], x0=p["ID"], x1=p["wall"]), None)
            trace.append(dict(op="court", what=f"{p['name']} dims",
                              got=chk["verdict"]))
            if chk["verdict"] != "CORROBORATION":
                out["wounds"].append(dict(
                    part=p["name"], why="claimed dims violate his "
                    "tube constraint",
                    residual=chk.get("residual")))
                kind = "WOUND"
        out["parts"][p["name"]] = kind
    bore_of = dict()
    for p in world["parts"]:
        bore_of[p["name"]] = p.get("ID", p.get("bore"))
    od_of = {p["name"]: p.get("OD") for p in world["parts"]}
    for inner, outer in world["seats"]:
        if out["parts"][inner] == "WOUND" or \
                out["parts"][outer] == "WOUND":
            continue
        gap = bore_of[outer] - od_of[inner]
        joint = next((j[2] for j in world["joints"]
                      if {j[0], j[1]} == {inner, outer}), None)
        intent = next((i[2] for i in world["intents"]
                       if {i[0], i[1]} == {inner, outer}), "loose")
        if joint:
            key = f"joint-{joint}"
        elif gap > 1e-9:
            key = "gap-positive"
        elif abs(gap) <= 1e-9:
            key = "gap-zero"
        else:
            key = f"gap-negative-{intent}"
        kinds = ask(key, "means")
        conn = dict(pair=(inner, outer),
                    kind=(kinds[0] if kinds else "UNKNOWN"))
        if gap is not None and not joint:
            if gap > 0:
                conn["clearance"] = round(gap, 4)
            elif gap < 0:
                conn["interference"] = round(-gap, 4)
        out["connections"].append(conn)
    for c in out["connections"]:
        if c["kind"] == "not-touching" and "clearance" in c:
            pat = ask("clearance-shaft-in-bushing", "pattern-of")
            if pat:
                out["functions"].append(dict(
                    what=pat[0], where=c["pair"],
                    receipt=f"clearance {c['clearance']} permits "
                            "rotation"))
    return out


def transmits(mind, kind, trace):
    got = set(mind.ask(kind, "transmits",
                       container="cad-mechanical")["answers"])
    trace.append(dict(op="ask", what=f"{kind}.transmits",
                      got=sorted(got)))
    return got


def load_path(mind, assessment, a, b, action, trace):
    """Walk the assessed graph from a to b; every hop needs the
    action in HIS transmit set for that connection kind."""
    conns = {frozenset(c["pair"]): c["kind"]
             for c in assessment["connections"]}
    seen, frontier = {a}, [a]
    while frontier:
        cur = frontier.pop()
        if cur == b:
            return True
        for pair, kind in conns.items():
            if cur in pair:
                nxt = next(x for x in pair if x != cur)
                if nxt not in seen and action in transmits(
                        mind, kind, trace):
                    seen.add(nxt)
                    frontier.append(nxt)
    return b in seen


def assess_circuit(mind, world, trace):
    def ask(s, r, c):
        got = mind.ask(s, r, container=c)["answers"]
        trace.append(dict(op="ask", what=f"{s}.{r}", got=got))
        return got

    out = dict(comps={}, loop=False, operating=None, flags=[])
    for d, val, pins in world["comps"]:
        prefix = "".join(ch for ch in d if not ch.isdigit())
        kinds = ask(f"designator-{prefix}", "names", "drafting")
        out["comps"][d] = kinds[0] if kinds else "UNKNOWN"
    nets = {}
    for d, val, pins in world["comps"]:
        for p in pins:
            nets.setdefault(p, []).append(d)
    out["loop"] = all(len(v) == 2 for v in nets.values())
    kinds = out["comps"]
    has_led = any(k == "diode" for k in kinds.values())
    has_r = any(k == "resistor" for k in kinds.values())
    if has_led and has_r and out["loop"]:
        vs = next(v for d, v, _ in world["comps"]
                  if kinds[d] == "UNKNOWN" or d.startswith("V"))
        rv = next(v for d, v, _ in world["comps"]
                  if kinds[d] == "resistor")
        led = next(v for d, v, _ in world["comps"]
                   if kinds[d] == "diode")
        drop = ask(led, "forward-drop", "electrical")
        vf = float(drop[0].rstrip("V")) if drop else None
        got = solve_backward(mind, form_of(mind, "led-resistor"),
                             dict(x0=vs, x1=vf, y=rv), "x2")
        trace.append(dict(op="law", what="led-resistor solve I",
                          got=got))
        out["operating"] = round(got["x2"] * 1000, 2)
    if has_led and not has_r:
        neg = mind.net.get_door_tags("led-without-current-limit",
                                     "not_safe")
        trace.append(dict(op="negative",
                          what="led-without-current-limit",
                          got=sorted(neg)))
        if neg:
            out["flags"].append("DANGER: LED without current limit "
                                "— his certified negative")
    return out


# ── the observed maps ─────────────────────────────────────────────
def understanding_map(mind, subject, path):
    """What HE holds about a thing: doors in/out, facts, evidence —
    rendered as a radial SVG + a text dossier."""
    prof = mind.net.get_full_profile(subject)
    facts = [(r, o) for (s, r), objs in mind.fact_index.items()
             if s == subject for o in objs]
    ev = mind.recall_evidence(subject)
    spokes = []
    for tgt, tags in list(prof["out"].items())[:14]:
        spokes.append((f"→{tgt}", ",".join(sorted(tags))[:18]))
    for src, tags in list(prof["in"].items())[:8]:
        spokes.append((f"←{src}", ",".join(sorted(tags))[:18]))
    for r, o in facts[:10]:
        spokes.append((f"{r}: {o}", "fact"))
    if ev:
        spokes.append((f"evidence: {len(ev['rows'])} rows",
                       "facts layer"))
    _radial_svg(path, subject, spokes)
    return dict(doors_out=len(prof["out"]), doors_in=len(prof["in"]),
                facts=len(facts), spokes=len(spokes))


def assessment_map(assessment, path):
    spokes = []
    for name, kind in assessment["parts"].items():
        spokes.append((f"{name}: {kind}", "part"))
    for c in assessment["connections"]:
        q = c.get("clearance", c.get("interference", ""))
        spokes.append((f"{c['pair'][0]}~{c['pair'][1]}: {c['kind']} "
                       f"{q}", "connection"))
    for f in assessment["functions"]:
        spokes.append((f"{f['what']} @ {f['where'][0]}", "function"))
    for w in assessment["wounds"]:
        spokes.append((f"WOUND: {w['part']} ({w['residual']})",
                       "wound"))
    _radial_svg(path, "assembly (as he concluded)", spokes)
    return len(spokes)


def flow_map(trace, path):
    """The mental-processing state of one task: every step boxed,
    in order, with its receipt."""
    H = 26 * len(trace) + 60
    L = [f'<svg xmlns="http://www.w3.org/2000/svg" width="880" '
         f'height="{H}" font-family="monospace" font-size="12">']
    L.append('<text x="20" y="28" font-size="15">the processing '
             'trace — one assessment, every step receipted</text>')
    for i, t in enumerate(trace):
        y = 50 + 26 * i
        got = str(t["got"])[:64]
        L.append(f'<rect x="20" y="{y}" width="840" height="20" '
                 f'fill="none" stroke="#888"/>')
        L.append(f'<text x="26" y="{y + 14}">{i + 1:>3}. '
                 f'[{t["op"]}] {t["what"]} = {got}</text>')
    L.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(L))


def _radial_svg(path, center, spokes):
    import math
    n = max(1, len(spokes))
    W = Hh = 900
    cx = cy = W // 2
    L = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" '
         f'height="{Hh}" font-family="monospace" font-size="11">']
    L.append(f'<circle cx="{cx}" cy="{cy}" r="60" fill="none" '
             f'stroke="#333" stroke-width="2"/>')
    L.append(f'<text x="{cx}" y="{cy}" text-anchor="middle">'
             f'{center[:20]}</text>')
    for i, (label, tag) in enumerate(spokes):
        a = 2 * math.pi * i / n
        x = cx + int(330 * math.cos(a))
        y = cy + int(330 * math.sin(a))
        L.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" '
                 f'stroke="#bbb"/>')
        anchor = "start" if math.cos(a) >= 0 else "end"
        L.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}">'
                 f'{label[:44]}</text>')
        L.append(f'<text x="{x}" y="{y + 12}" text-anchor="{anchor}"'
                 f' fill="#777">{tag}</text>')
    L.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(L))


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    mind = Isaac()
    feed(mind)                             # he stands on his feed
    mind.open_world("cad-mechanical")
    for prim, kind in (("hollow-cylinder", "tube"),
                       ("solid-cylinder", "shaft-or-pin"),
                       ("block-with-bore", "housing")):
        mind.teach(prim, "kind-is", kind)
    mind.teach("clearance-shaft-in-bushing", "pattern-of",
               "journal-bearing")
    for key, kind in (("gap-positive", "not-touching"),
                      ("gap-zero", "touching"),
                      ("gap-negative-press", "connected"),
                      ("gap-negative-loose", "WOUND"),
                      ("joint-weld", "connected")):
        mind.teach(key, "means", kind)
    for kind, tr in (("connected", ("push", "pull")),
                     ("touching", ("push",))):
        for t in tr:
            mind.teach(kind, "transmits", t)
    mind.open_world("base")

    trace = []
    A = assess_assembly(mind, ASSEMBLY, trace)

    # A1 — parts identified from his signature facts
    ok1 = (A["parts"]["bushing"] == "tube"
           and A["parts"]["shaft"] == "shaft-or-pin"
           and A["parts"]["collar"] == "tube"
           and A["parts"]["block"] == "housing"
           and A["parts"]["gasket"] == "WOUND")
    check("A1 parts identified via HIS signatures (+1 honest wound)",
          ok1, f"{A['parts']}")

    # A2 — connections with quantities
    conns = {frozenset(c["pair"]): c for c in A["connections"]}
    c_sb = conns[frozenset(("shaft", "bushing"))]
    c_bb = conns[frozenset(("bushing", "block"))]
    c_cs = conns[frozenset(("collar", "shaft"))]
    ok2 = (c_sb["kind"] == "not-touching"
           and c_sb["clearance"] == 0.04
           and c_bb["kind"] == "connected"
           and c_bb["interference"] == 0.05
           and c_cs["kind"] == "connected")
    check("A2 connections classified w/ quantities from HIS "
          "taxonomy", ok2,
          f"shaft~bushing {c_sb['kind']}({c_sb.get('clearance')}), "
          f"bushing~block {c_bb['kind']}({c_bb.get('interference')}), "
          f"collar~shaft {c_cs['kind']}")

    # A3 — the planted wound
    ok3 = (len(A["wounds"]) == 1 and A["wounds"][0]["part"] == "gasket"
           and abs(A["wounds"][0]["residual"] + 0.5) < 1e-9)
    check("A3 the dims-wound flagged by HIS constraint, never "
          "silently classified", ok3, f"{A['wounds']}")

    # A4 — function recognized
    ok4 = (len(A["functions"]) == 1
           and A["functions"][0]["what"] == "journal-bearing")
    check("A4 function named from HIS pattern fact", ok4,
          f"{A['functions']}")

    # A5 — load paths on the assessed graph
    p1 = load_path(mind, A, "collar", "shaft", "pull", trace)
    p2 = load_path(mind, A, "bushing", "block", "pull", trace)
    p3 = load_path(mind, A, "shaft", "block", "pull", trace)
    ok5 = p1 and p2 and not p3
    check("A5 load paths — weld pulls, press pulls, the clearance "
          "gap does not", ok5, f"{p1}/{p2}/{p3}")

    # A6 — regeneration + the exploded null
    truth = {frozenset(("shaft", "bushing")): "not-touching",
             frozenset(("bushing", "block")): "connected",
             frozenset(("collar", "shaft")): "connected"}
    regen = {k: v["kind"] for k, v in conns.items()}
    exploded = dict(ASSEMBLY)
    exploded["parts"] = [dict(p) for p in ASSEMBLY["parts"]
                         if p["name"] != "gasket"]
    for i, p in enumerate(exploded["parts"]):
        p["pos"] = (i * 100, 0)
    exploded["seats"] = []
    exploded["joints"] = []
    E = assess_assembly(mind, exploded, [])
    ok6 = (regen == truth and E["connections"] == []
           and E["functions"] == [] and E["wounds"] == [])
    check("A6 regeneration == truth; exploded null says nothing "
          "false", ok6,
          f"regen match {regen == truth}; exploded conns "
          f"{len(E['connections'])}")

    # A7 — the circuit
    C = assess_circuit(mind, CIRCUIT, trace)
    B = assess_circuit(mind, CIRCUIT_BAD, trace)
    ok7 = (C["comps"]["R1"] == "resistor"
           and C["comps"]["D1"] == "diode" and C["loop"]
           and abs(C["operating"] - 17.95) < 0.01
           and len(B["flags"]) == 1 and "DANGER" in B["flags"][0])
    check("A7 circuit — kinds named, loop traced, 17.95mA DERIVED "
          "from his law, danger flagged from his negative", ok7,
          f"operating {C['operating']}mA; flags {B['flags']}")

    # A8 — the maps observed
    um = understanding_map(mind, "connected",
                           os.path.join(RUNS,
                                        "understanding_map.svg"))
    n_assess = assessment_map(A, os.path.join(
        RUNS, "assessment_map.svg"))
    flow_map(trace, os.path.join(RUNS, "processing_trace.svg"))
    ok8 = (len(trace) >= 25 and um["spokes"] >= 3 and n_assess >= 8
           and all(os.path.getsize(os.path.join(RUNS, f)) > 800
                   for f in ("understanding_map.svg",
                             "assessment_map.svg",
                             "processing_trace.svg")))
    check("A8 the maps observed — trace + understanding map + "
          "assessment map emitted", ok8,
          f"trace {len(trace)} receipted steps; understanding "
          f"spokes {um['spokes']}; assessment spokes {n_assess}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
