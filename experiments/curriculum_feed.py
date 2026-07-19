"""curriculum_feed.py — THE FULL CURRICULUM FEED (owner, 2026-07-18:
"lets just do it all, and we can assess when it is done").

The checklist curriculum fed AS CONTENT through his promoted doors —
laws TOLD in his grammar (tell_law, provenance cited), facts TAUGHT
(teach/teach_not, containers per domain), every law BULK-COURTED
(forward / derive-each-unknown / corrupt-refuses-with-residual /
DOF), constructions SAMPLED per section from HIS content only.

THE FIRST DISCOVERY THE FEED FORCED: physics reuses a handful of
SHAPES. Ohm's law, density, Hooke's law, and spring force are ALL
y = x0*x1 — one form, many labels. tell_law correctly answers
MATCHES on the second telling: the equation node is ONE, and each
application binds its own quantities to the shared slots as FACTS
(the shapes-and-labels ontology arriving by itself). The curriculum
therefore lands as: FORMS (few law nodes) + APPLICATIONS (many
fact-bundles naming output/slots/citation onto their form).

DRY (default): throwaway mind, full courts, complete numbers.
LIVE (--live): his account — the biggest meal of his life; journal
kind=meal; road-trial line (selection at scale gets real load).

usage: python curriculum_feed.py [--live] [home]
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

# ── THE CURRICULUM DATA ───────────────────────────────────────────
# laws: (application, container, equation, output, slots, citation)
LAWS = [
    # CAD / mechanical
    ("tube-od", "cad", "+1.00*x0 +2.00*x1", "OD", "ID,wall",
     "machinist handbook"),
    ("circle-area", "cad", "+3.14159*x0*x0", "area", "radius",
     "geometry"),
    ("circle-circumference", "cad", "+6.28319*x0", "circumference",
     "radius", "geometry"),
    ("rect-area", "cad", "+1.00*x0*x1", "area", "width,height",
     "geometry"),
    ("triangle-area", "cad", "+0.50*x0*x1", "area", "base,height",
     "geometry"),
    ("cylinder-volume", "cad", "+3.14159*x0*x0*x1", "volume",
     "radius,height", "geometry"),
    ("sphere-volume", "cad", "+4.18879*x0^3", "volume", "radius",
     "geometry"),
    ("cone-volume", "cad", "+1.04720*x0*x0*x1", "volume",
     "radius,height", "geometry"),
    ("pythagoras-c2", "cad", "+1.00*x0^2 +1.00*x1^2", "c-squared",
     "a,b", "geometry"),
    ("gear-center-distance", "cad", "+0.50*x0*x1 +0.50*x0*x2",
     "center-distance", "module,z1,z2", "machinery handbook"),
    ("gear-ratio", "cad", "+1.00*x0*x1^-1", "ratio", "z2,z1",
     "machinery handbook"),
    ("spring-force", "cad", "+1.00*x0*x1", "force", "k,deflection",
     "hooke"),
    ("torque", "cad", "+1.00*x0*x1", "torque", "force,radius",
     "mechanics"),
    ("pressure", "cad", "+1.00*x0*x1^-1", "pressure", "force,area",
     "mechanics"),
    ("stress", "cad", "+1.00*x0*x1^-1", "stress", "force,area",
     "mechanics of materials"),
    ("hooke-stress", "cad", "+1.00*x0*x1", "stress", "E,strain",
     "mechanics of materials"),
    ("density-mass", "cad", "+1.00*x0*x1", "mass", "density,volume",
     "physics"),
    ("thermal-expansion", "cad", "+1.00*x0*x1*x2", "delta-L",
     "alpha,L,delta-T", "physics"),
    ("kinetic-energy", "cad", "+0.50*x0*x1^2", "KE", "mass,velocity",
     "physics"),
    ("potential-energy", "cad", "+9.81*x0*x1", "PE", "mass,height",
     "physics; g=9.81 cited"),
    ("newton-2", "cad", "+1.00*x0*x1", "force", "mass,acceleration",
     "physics"),
    ("momentum", "cad", "+1.00*x0*x1", "momentum", "mass,velocity",
     "physics"),
    ("work", "cad", "+1.00*x0*x1", "work", "force,distance",
     "physics"),
    ("leadscrew-advance", "cad", "+1.00*x0*x1", "advance",
     "lead,turns", "machinery handbook"),
    ("pulley-speed", "cad", "+1.00*x0*x1*x2^-1", "n2", "d1,n1,d2",
     "machinery handbook"),
    ("spring-rate-coil", "cad", "+0.125*x0*x1^4*x2^-3*x3^-1", "k",
     "G,wire-d,coil-D,n-coils", "machinery handbook (Gd^4/8D^3n)"),
    # electrical
    ("ohms-law", "elec", "+1.00*x0*x1", "voltage",
     "current,resistance", "ohm"),
    ("power-vi", "elec", "+1.00*x0*x1", "power", "voltage,current",
     "physics"),
    ("power-i2r", "elec", "+1.00*x0^2*x1", "power",
     "current,resistance", "physics"),
    ("power-v2r", "elec", "+1.00*x0^2*x1^-1", "power",
     "voltage,resistance", "physics"),
    ("series-resistance", "elec", "+1.00*x0 +1.00*x1", "R-total",
     "R1,R2", "circuit theory"),
    ("parallel-conductance", "elec", "+1.00*x0 +1.00*x1", "G-total",
     "G1,G2", "circuit theory (the conductance VIEW of parallel)"),
    ("series-voltage", "elec", "+1.00*x0 +1.00*x1", "V-total",
     "V1,V2", "kirchhoff"),
    ("rc-time-constant", "elec", "+1.00*x0*x1", "tau", "R,C",
     "circuit theory"),
    ("rl-time-constant", "elec", "+1.00*x0*x1^-1", "tau", "L,R",
     "circuit theory"),
    ("capacitive-reactance", "elec", "+0.15915*x0^-1*x1^-1", "Xc",
     "frequency,C", "1/(2*pi*f*C)"),
    ("inductive-reactance", "elec", "+6.28319*x0*x1", "Xl",
     "frequency,L", "2*pi*f*L"),
    ("resonant-frequency", "elec", "+0.15915*x0^-0.5*x1^-0.5", "f",
     "L,C", "1/(2*pi*sqrt(LC))"),
    ("led-resistor", "elec", "+1.00*x0*x2^-1 -1.00*x1*x2^-1", "R",
     "V-supply,V-forward,I", "(Vs-Vf)/I"),
    ("charge", "elec", "+1.00*x0*x1", "charge", "C,V", "Q=CV"),
    ("cap-energy", "elec", "+0.50*x0*x1^2", "energy", "C,V",
     "physics"),
    ("inductor-energy", "elec", "+0.50*x0*x1^2", "energy", "L,I",
     "physics"),
    ("transformer", "elec", "+1.00*x0*x1*x2^-1", "V-secondary",
     "V-primary,N-s,N-p", "turns ratio"),
    ("rms-sine", "elec", "+0.70711*x0", "V-rms", "V-peak",
     "1/sqrt(2)"),
    ("wire-resistance", "elec", "+1.00*x0*x1*x2^-1", "R",
     "resistivity,length,area", "physics"),
    ("cutoff-frequency", "elec", "+0.15915*x0^-1*x1^-1", "fc",
     "R,C", "1/(2*pi*RC)"),
    # python (the few genuinely lawful bits)
    ("gauss-sum", "code", "+0.50*x0^2 -0.50*x0", "sum-0-to-n-1",
     "n", "arithmetic series"),
    ("slice-length", "code", "+1.00*x0 -1.00*x1", "length",
     "stop,start", "step=1 slice"),
]

# facts: (container, subject, relation, object)
FACTS = []


def _facts():
    F = []

    def add(c, s, r, o):
        F.append((c, s, r, o))

    # python: types & mutability
    for t in ("int", "float", "str", "bool", "tuple", "frozenset",
              "bytes"):
        add("code", t, "mutability", "immutable")
    for t in ("list", "dict", "set", "bytearray"):
        add("code", t, "mutability", "mutable")
    for t, o in (("list-index", "O(1)"), ("dict-lookup", "O(1)"),
                 ("set-membership", "O(1)"), ("list-search", "O(n)"),
                 ("binary-search", "O(log n)"), ("list-append", "O(1)"),
                 ("list-insert-front", "O(n)"), ("sort", "O(n log n)")):
        add("code", t, "complexity", o)
    for s in ("empty-list", "empty-dict", "empty-str", "zero",
              "none"):
        add("code", s, "truthiness", "falsy")
    for a, b in (("**", "1"), ("unary-minus", "2"), ("*", "3"),
                 ("/", "3"), ("+", "4"), ("-", "4"),
                 ("comparison", "5"), ("not", "6"), ("and", "7"),
                 ("or", "8")):
        add("code", a, "precedence-tier", b)
    for s in ("local", "enclosing", "global", "builtin"):
        add("code", f"scope-{s}", "lookup-order",
            str(("local", "enclosing", "global",
                 "builtin").index(s) + 1))
    for shape, part in (("validation-shape", "check-then-use"),
                        ("retry-shape", "loop+backoff+limit"),
                        ("error-shape", "try-log-reraise"),
                        ("accumulator", "init-loop-fold"),
                        ("sentinel", "special-value-terminates")):
        add("code", shape, "has-part", part)
    for st, ops in (("stack", "push-pop-LIFO"),
                    ("queue", "enqueue-dequeue-FIFO"),
                    ("heap", "push-pop-min"),
                    ("tree", "parent-children"),
                    ("graph", "nodes-edges")):
        add("code", st, "discipline", ops)
    # CAD: fits, GD&T vocabulary, drawing conventions
    for fit, mean in (("clearance-fit", "gap-positive"),
                      ("transition-fit", "gap-near-zero"),
                      ("interference-fit", "gap-negative")):
        add("cad", fit, "means", mean)
    add("cad", "H7-g6", "fit-class", "clearance-fit")
    add("cad", "H7-k6", "fit-class", "transition-fit")
    add("cad", "H7-p6", "fit-class", "interference-fit")
    for g in ("flatness", "straightness", "circularity",
              "cylindricity"):
        add("cad", g, "gdt-family", "form")
    for g in ("perpendicularity", "parallelism", "angularity"):
        add("cad", g, "gdt-family", "orientation")
    for g in ("position", "concentricity", "symmetry"):
        add("cad", g, "gdt-family", "location")
    for g in ("circular-runout", "total-runout"):
        add("cad", g, "gdt-family", "runout")
    for g in ("profile-line", "profile-surface"):
        add("cad", g, "gdt-family", "profile")
    for m, kinds in (("coincident", "removes-3-dof"),
                     ("concentric", "removes-4-dof"),
                     ("distance", "removes-1-dof"),
                     ("gear", "couples-rotation"),
                     ("cam-follower", "couples-profile")):
        add("cad", m, "mate-property", kinds)
    for f, s in (("extrude", "profile+direction+depth"),
                 ("revolve", "profile+axis+angle"),
                 ("sweep", "profile+path"),
                 ("loft", "profiles+guides"),
                 ("shell", "solid+wall+open-faces"),
                 ("fillet", "edge+radius"),
                 ("chamfer", "edge+distance"),
                 ("pattern-linear", "feature+direction+count"),
                 ("pattern-circular", "feature+axis+count")):
        add("cad", f, "slots", s)
    for e, d in (("bolt", "clamps-by-preload"),
                 ("bearing", "constrains-radially"),
                 ("key", "transmits-torque-shaft-to-hub"),
                 ("oring", "seals-by-squeeze"),
                 ("circlip", "constrains-axially")):
        add("cad", e, "function", d)
    # drafting
    for lt, m in (("visible-line", "solid-thick"),
                  ("hidden-line", "dashed"),
                  ("center-line", "chain-thin"),
                  ("section-line", "hatching"),
                  ("phantom-line", "chain-two-dash"),
                  ("dimension-line", "thin+arrowheads")):
        add("draft", lt, "drawn-as", m)
    add("draft", "first-angle", "projection-rule",
        "object-between-observer-and-plane")
    add("draft", "third-angle", "projection-rule",
        "plane-between-observer-and-object")
    add("draft", "third-angle", "used-in", "US")
    add("draft", "first-angle", "used-in", "EU")
    for d, c in (("R", "resistor"), ("C", "capacitor"),
                 ("L", "inductor"), ("D", "diode"),
                 ("Q", "transistor"), ("U", "integrated-circuit"),
                 ("K", "relay"), ("J", "connector"), ("F", "fuse"),
                 ("T", "transformer"), ("Y", "crystal"),
                 ("SW", "switch")):
        add("draft", f"designator-{d}", "names", c)
    for v, m in (("section-full", "cut-straight-through"),
                 ("section-half", "quarter-removed"),
                 ("section-offset", "cut-follows-features"),
                 ("detail-view", "enlarged-region"),
                 ("auxiliary-view", "true-shape-of-inclined-face")):
        add("draft", v, "means", m)
    # electrical facts
    for e in ("10", "12", "15", "18", "22", "27", "33", "39", "47",
              "56", "68", "82"):
        add("elec", f"E12-{e}", "is-standard-value", "yes")
    for band, digit in (("black", "0"), ("brown", "1"), ("red", "2"),
                        ("orange", "3"), ("yellow", "4"),
                        ("green", "5"), ("blue", "6"),
                        ("violet", "7"), ("grey", "8"),
                        ("white", "9")):
        add("elec", f"band-{band}", "digit", digit)
    for g, tt in (("AND", "1-only-if-all-1"), ("OR", "1-if-any-1"),
                  ("NOT", "inverts"), ("NAND", "AND-inverted"),
                  ("NOR", "OR-inverted"), ("XOR", "1-if-different")):
        add("elec", f"gate-{g}", "truth-rule", tt)
    add("elec", "diode-silicon", "forward-drop", "0.7V")
    add("elec", "led-red", "forward-drop", "2.0V")
    add("elec", "bjt-active", "requires", "base-emitter-0.7V")
    add("elec", "opamp-ideal", "rule", "no-input-current")
    add("elec", "opamp-ideal", "rule2", "inputs-equal-with-feedback")
    add("elec", "resistor-sizing", "safety-rule",
        "round-up-to-reduce-current")
    return F


FACTS = _facts()

# negatives: (container, subject, prop) — certified nevers
NEGATIVES = [
    ("code", "mutable-default-argument", "safe"),
    ("code", "mutation-during-iteration", "safe"),
    ("code", "float-equality-comparison", "reliable"),
    ("code", "late-binding-closure-in-loop", "intuitive"),
    ("code", "bare-except", "good-practice"),
    ("cad", "over-constrained-sketch", "buildable"),
    ("cad", "interference-without-intent", "assemblable"),
    ("elec", "electrolytic-reverse-polarity", "safe"),
    ("elec", "led-without-current-limit", "safe"),
    ("elec", "unfused-mains", "safe"),
]

CONTAINERS = dict(cad="cad-mechanical", code="python-code",
                  elec="electrical", draft="drafting")


def solve_backward(mind, name, known, want):
    """GENERIC solver v2: y = A*u^p + B where A and B fold from the
    known slots — covers every linear, product, and power form in
    the curriculum, reading the model FROM HIS NET."""
    m = mind.net.get_meta(f"law:{name}", "model")
    if m is None:
        return None
    terms = []
    for t, c in zip(m["terms"], m["coefs"]):
        fac = []
        for a in t:
            kind, i, j, k = m["specs"][a]
            if kind == "var":
                fac.append((f"x{i}", 1.0))
            elif kind == "pow":
                fac.append((f"x{i}", float(k)))
            else:
                return dict(verdict="REFUSED",
                            receipt="outside the solver's scope")
        terms.append((float(c), fac))
    b0 = float(m.get("intercept", 0.0))
    if want == "y":
        y = b0
        for c, fac in terms:
            v = c
            for var, p in fac:
                v *= known[var] ** p
            y += v
        return dict(verdict="DERIVED", y=float(y))
    A, B, pw = 0.0, b0, None
    for c, fac in terms:
        coef, has = c, None
        for var, p in fac:
            if var == want:
                has = p
            else:
                coef *= known[var] ** p
        if has is None:
            B += coef
        else:
            if pw is not None and has != pw:
                return dict(verdict="REFUSED",
                            receipt="mixed powers of the unknown")
            pw = has
            A += coef
    if pw is None or A == 0:
        return dict(verdict="REFUSED", receipt="unknown not present")
    base = (known["y"] - B) / A
    if base < 0 and (pw % 1 or pw < 0):
        return dict(verdict="REFUSED", receipt="no real solution")
    return dict(verdict="DERIVED",
                **{want: float(base ** (1.0 / pw))})


def court_law(mind, name, nvars, rng):
    """The bulk B-court: forward, derive each unknown round-trip,
    corrupt refuses, DOF names itself."""
    vals = {f"x{i}": float(rng.uniform(1.2, 3.7)) for i in range(nvars)}
    fwd = solve_backward(mind, name, vals, "y")
    if fwd.get("verdict") != "DERIVED":
        return dict(court="partial", why=fwd.get("receipt"))
    y = fwd["y"]
    derived = 0
    for i in range(nvars):
        k = {v: vals[v] for v in vals if v != f"x{i}"}
        k["y"] = y
        got = solve_backward(mind, name, k, f"x{i}")
        if got.get("verdict") == "DERIVED" \
                and abs(got[f"x{i}"] - vals[f"x{i}"]) < 1e-6 \
                * max(1, abs(vals[f"x{i}"])):
            derived += 1
    bad = dict(vals)
    bad["y"] = y * 1.07 + 0.11
    chk = solve_backward(mind, name, bad, None)
    refused = False
    if chk is None or chk.get("verdict") != "DERIVED":
        p2 = solve_backward(mind, name, dict(bad), "y")
        refused = abs(p2["y"] - bad["y"]) > 1e-9
    dof = "DOF" if nvars > 1 else "n/a"
    return dict(court="full", derived=derived, of=nvars,
                corrupt_refused=bool(refused), dof=dof)


def feed(mind):
    rng = np.random.default_rng(3)
    stats = dict(forms=0, matches=0, apps=0, facts=0, negatives=0,
                 courts_full=0, courts_partial=0, derived=0,
                 derivable=0, corrupt_ok=0)
    arity = {}
    for app, dom, eq, out, slots, cite in LAWS:
        mind.open_world(CONTAINERS[dom])
        r = mind.tell_law(app, eq, d=len(slots.split(",")),
                          who=cite)
        if r.get("status") == "MATCHES":
            stats["matches"] += 1
            form = r["law"]
        else:
            stats["forms"] += 1
            form = app
        arity[form] = len(slots.split(","))
        mind.teach(app, "uses-form", form)
        mind.teach(app, "output", out)
        mind.teach(app, "slots", slots)
        stats["apps"] += 1
    for form, nv in arity.items():
        c = court_law(mind, form, nv, rng)
        if c["court"] == "full":
            stats["courts_full"] += 1
            stats["derived"] += c["derived"]
            stats["derivable"] += c["of"]
            stats["corrupt_ok"] += c["corrupt_refused"]
        else:
            stats["courts_partial"] += 1
    for dom, s, rel, o in FACTS:
        mind.open_world(CONTAINERS[dom])
        mind.teach(s, rel, o)
        stats["facts"] += 1
    for dom, s, prop in NEGATIVES:
        mind.open_world(CONTAINERS[dom])
        mind.teach_not(s, prop)
        stats["negatives"] += 1
    mind.open_world("base")
    return stats


def form_of(mind, app):
    """Resolve an application to its FORM through his own facts —
    the shapes-and-labels ontology in use: ohms-law binds to the
    shared product form; the label is his fact, the shape is one
    node."""
    for c in CONTAINERS.values():
        got = mind.ask(app, "uses-form", container=c)["answers"]
        if got:
            return got[0]
    return app


def constructions(mind):
    """C-samples: built from HIS content, generic glue only."""
    out = []

    def solve(app, known, want):
        return solve_backward(mind, form_of(mind, app), known, want)
    # 1) LED resistor sized from his law + his E12 facts + his rule
    need = solve("led-resistor",
                          dict(x0=9.0, x1=2.0, x2=0.02), "y")["y"]
    e12 = []
    for d in ("10", "12", "15", "18", "22", "27", "33", "39", "47",
              "56", "68", "82"):
        if mind.ask(f"E12-{d}", "is-standard-value",
                    container="electrical")["answers"]:
            e12 += [int(d) * m for m in (1, 10, 100)]
    rule = mind.ask("resistor-sizing", "safety-rule",
                    container="electrical")["answers"]
    pick = min([v for v in e12 if v >= need]) if rule else None
    out.append(("LED resistor", need, pick,
                abs(need - 350.0) < 1e-6 and pick == 390))
    # 2) power multi-view: three of HIS laws, one answer
    V, I = 6.0, 1.5
    R = solve("ohms-law",
                       dict(y=V, x0=I), "x1")["x1"]
    p1 = solve("power-vi", dict(x0=V, x1=I), "y")["y"]
    p2 = solve("power-i2r", dict(x0=I, x1=R), "y")["y"]
    p3 = solve("power-v2r", dict(x0=V, x1=R), "y")["y"]
    agree = max(p1, p2, p3) - min(p1, p2, p3) < 1e-9
    out.append(("power 3 views", round(p1, 3), round(p3, 3), agree))
    # 3) divider by chained laws: Rtot -> I -> V2
    r1, r2, vs = 1000.0, 2000.0, 9.0
    rt = solve("series-resistance",
                        dict(x0=r1, x1=r2), "y")["y"]
    i = solve("ohms-law", dict(y=vs, x1=rt), "x0")["x0"]
    v2 = solve("ohms-law", dict(x0=i, x1=r2), "y")["y"]
    out.append(("divider chain", round(v2, 4), 6.0,
                abs(v2 - 6.0) < 1e-9))
    # 4) a mating pair from his fit facts + tube law
    kind = mind.ask("H7-g6", "fit-class",
                    container="cad-mechanical")["answers"]
    gap_kind = mind.ask(kind[0], "means",
                        container="cad-mechanical")["answers"] \
        if kind else []
    pin_ok = gap_kind == ["gap-positive"]
    od = solve("tube-od",
                        dict(x0=10.02, x1=1.5), "y")["y"]
    out.append(("H7/g6 pair + sleeve OD", gap_kind, round(od, 3),
                pin_ok and abs(od - 13.02) < 1e-9))
    # 5) the bug detector: HIS negative knowledge + generic AST scan
    import ast as _ast
    SNIP = "def f(x, acc=[]):\n    acc.append(x)\n    return acc\n"
    tree = _ast.parse(SNIP)
    has_mut_default = any(
        isinstance(d, (_ast.List, _ast.Dict, _ast.Set))
        for n in _ast.walk(tree)
        if isinstance(n, _ast.FunctionDef)
        for d in n.args.defaults)
    flagged = bool(has_mut_default and mind.net.get_door_tags(
        "mutable-default-argument", "not_safe"))
    out.append(("mutable-default flagged from HIS negative",
                has_mut_default, flagged, flagged))
    return out


def main():
    live = "--live" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    home = args[0] if args else os.path.join(
        os.path.expanduser("~"), "Documents", "isaac_home")
    t0 = time.perf_counter()

    if not live:
        print("DRY RUN — throwaway mind, his account untouched")
        mind = mod.Isaac()
        stats = feed(mind)
        cons = constructions(mind)
    else:
        from isaac_store.sparring import IsaacAccount  # noqa: E402
        from isaac_store.roadtrial import log_roadtrial  # noqa
        acct = IsaacAccount(home, mod)
        print(f"LIVE — his account: {home} "
              f"({acct.sessions_so_far()} journal entries so far)")
        mind = acct.mind
        stats = feed(mind)
        cons = constructions(mind)

    print(f"  applications told: {stats['apps']} "
          f"({stats['forms']} new forms + {stats['matches']} "
          f"landing on shared forms — the shapes discovery)")
    print(f"  facts taught: {stats['facts']}; negatives certified: "
          f"{stats['negatives']}")
    print(f"  B-courts: {stats['courts_full']} full / "
          f"{stats['courts_partial']} partial; unknowns derived "
          f"{stats['derived']}/{stats['derivable']}; corrupt "
          f"refused {stats['corrupt_ok']}/{stats['courts_full']}")
    print("  C-constructions:")
    okc = 0
    for name, a, b, ok in cons:
        okc += ok
        print(f"    [{'ok ' if ok else 'FAIL'}] {name}: {a} -> {b}")
    print(f"  constructions {okc}/{len(cons)}  "
          f"({time.perf_counter() - t0:.1f}s)")

    if live:
        acct._journal(dict(
            kind="meal", stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            dishes=[dict(name="curriculum-feed", stats=stats,
                         constructions=[[c[0], bool(c[3])]
                                        for c in cons])]))
        acct.mind.save(acct.mind_path)
        line = log_roadtrial(home, acct.mind, mod)
        print(f"\n  MEAL JOURNALED + mind saved; road-trial line:")
        print(f"  {line}")


if __name__ == "__main__":
    main()
