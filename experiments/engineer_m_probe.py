"""engineer_m_probe.py — THE MECHANICAL RUNG (owner, 2026-07-18:
"i want to see if he can eventually do things like make a 3d model
or structural details of a tube... and if he can learn about
connected vs touching vs not touching interactions... can we get
him to learn interactions and information from code, and physics
or anything. we need to see what and how he understands things.")

RESEARCH, NOT THE ENGINE. Understanding proven by CONSTRUCTION:

  THE INSTANCE  the tube recipe INSTANTIATES: a full structural
                spec (area, volume, mass at a cited density) and a
                REAL 3D MODEL — a watertight .obj mesh emitted from
                the recipe. The mesh is a FOURTH VIEW of the tube
                and faces the view court at instrument-relative
                tolerance: its volume must equal the POLYGONAL
                prism's analytic volume machine-exact (the mesh's
                own ruler) and the circular recipe within the
                named discretization error.
  THE FAMILY    a DIFFERENT tube built from the same recipe passes
                the same courts — learn one tube, own the family.
  THE CONTACT TAXONOMY (the owner's ask, made courts):
                clearance > 0  -> NOT TOUCHING, clearance NAMED
                contact, no joint -> TOUCHING (transmits push,
                                     never pull)
                interference + press INTENT -> CONNECTED (the
                    machinist's truth: interference IS a fastening)
                the SAME geometry + loose intent -> WOUND ("two
                    solids, one space") — geometry plus intent,
                    two verdicts
                declared weld -> CONNECTED
  FORCE PATHS   claims TESTED by propagation over the contact
                graph, not asserted: pull follows connections only,
                push crosses touching too, nothing crosses a gap.
  PHYSICS FROM CODE  the read road on simulation source: F = -k*x
                and restitution READ from the text; then the
                INSTRUMENT confirms — k from the measured period,
                e from the measured bounce ratio.

PREDICTIONS (filed before the first run; wrong ones kept)
  P1 the spec sheet: area/volume/mass complete numbers from the
     recipe + a cited density.
  P2 the 3D model: watertight mesh emitted; mesh volume ==
     polygonal analytic machine-exact; circular recipe within the
     named discretization (<1% at 64 segments).
  P3 the family: a second instance from the same recipe, same
     courts green.
  P4 contact taxonomy: all five classifications correct with
     clearance/interference NAMED.
  P5 intent court: same interference geometry — press intent
     CONNECTED, loose intent WOUND.
  P6 force paths: 6/6 propagation answers correct (pull/push
     across connected/touching/gap).
  P7 physics read: k=3.5, e=0.8 from the text alone.
  P8 the instrument: k from period within 1%, e from bounce within
     2% — read proposes, measurement confirms.

Run: cd experiments && PYTHONHASHSEED=0 python engineer_m_probe.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from isaac_store import engineer as eng  # noqa: E402

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "runs")
os.makedirs(RUNS, exist_ok=True)

STEEL = 7.85e3  # kg/m^3 — machinery handbook value, told w/ citation


# ── the instance: recipe -> spec + mesh ───────────────────────────
def tube_spec(ID, OD, L):
    wall = eng.tube_court(ID=ID, OD=OD)["wall"]
    area = np.pi / 4 * (OD ** 2 - ID ** 2)
    vol = area * L
    return dict(ID=ID, OD=OD, wall=wall, L=L,
                section_area=area, volume=vol,
                mass=vol * STEEL,
                density_receipt="steel 7850 kg/m^3 (handbook, told)")


def tube_mesh_clean(ID, OD, L, n=64):
    """Watertight annular prism, orientation-consistent."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    Ri, Ro = ID / 2, OD / 2
    V = []
    for z, r in ((0, Ro), (0, Ri), (L, Ro), (L, Ri)):
        for t in th:
            V.append((r * np.cos(t), r * np.sin(t), z))
    V = np.array(V)
    OB, IB, OT, IT = 0, n, 2 * n, 3 * n
    F = []
    for i in range(n):
        j = (i + 1) % n
        # outer wall (normal out)
        F += [(OB + i, OB + j, OT + j), (OB + i, OT + j, OT + i)]
        # inner wall (normal toward axis = out of the solid)
        F += [(IB + i, IT + j, IB + j), (IB + i, IT + i, IT + j)]
        # top annulus (normal +z)
        F += [(OT + i, OT + j, IT + j), (OT + i, IT + j, IT + i)]
        # bottom annulus (normal -z)
        F += [(OB + i, IB + j, OB + j), (OB + i, IB + i, IB + j)]
    return V, F


def mesh_volume(V, F):
    """The instrument: signed-tetrahedron integration."""
    vol = 0.0
    for a, b, c in F:
        vol += np.dot(V[a], np.cross(V[b], V[c])) / 6.0
    return abs(vol)


def write_obj(path, V, F):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# tube instantiated from the recipe\n")
        for v in V:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for a, b, c in F:
            f.write(f"f {a + 1} {b + 1} {c + 1}\n")


# ── the contact taxonomy ──────────────────────────────────────────
def contact_court(pin_od, hole_id, intent="loose", joint=None):
    """Geometry + intent -> the interaction kind, quantities NAMED."""
    if joint == "weld":
        return dict(kind="CONNECTED", how="weld (declared joint)",
                    transmits=("push", "pull"))
    gap = hole_id - pin_od
    if gap > eng.TOL:
        return dict(kind="NOT TOUCHING",
                    clearance=round(float(gap), 6),
                    transmits=())
    if abs(gap) <= eng.TOL:
        return dict(kind="TOUCHING", how="surface contact, no joint",
                    transmits=("push",))
    if intent == "press":
        return dict(kind="CONNECTED",
                    how="interference fit (fastening by intent)",
                    interference=round(float(-gap), 6),
                    transmits=("push", "pull"))
    return dict(kind="WOUND",
                receipt="two solids, one space — interference "
                        f"{round(float(-gap), 6)} with no press "
                        "intent",
                transmits=())


def force_path(chain, action):
    """Claims tested by propagation: does the far end move?"""
    for link in chain:
        if action not in link["transmits"]:
            return False
    return True


# ── physics from code ─────────────────────────────────────────────
SPRING_SRC = '''
class SpringBall:
    def __init__(self):
        self.k = 3.5
        self.m = 2.0
        self.e = 0.8
        self.x = 1.0
        self.v = 0.0

    def step(self, dt):
        F = -self.k * self.x
        self.v += (F / self.m) * dt
        self.x += self.v * dt

class Bouncer:
    def __init__(self):
        self.e = 0.8
        self.y = 1.0
        self.v = 0.0

    def step(self, dt):
        self.v -= 9.8 * dt
        self.y += self.v * dt
        if self.y <= 0.0:
            self.y = 0.0
            self.v = -self.e * self.v
'''

import ast  # noqa: E402


def read_physics(src):
    """The read road on simulation source: constants and the force
    law taken from the text."""
    tree = ast.parse(src)
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) \
                and isinstance(node.targets[0], ast.Attribute):
            a = node.targets[0].attr
            if a in ("k", "m", "e") and a not in out:
                try:
                    out[a] = ast.literal_eval(node.value)
                except Exception:
                    pass
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) \
                and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id == "F":
            out["force_law"] = ast.unparse(node.value)
    return out


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    # P1 — the spec sheet from the recipe
    spec = tube_spec(ID=0.050, OD=0.060, L=2.0)
    ok1 = (abs(spec["wall"] - 0.005) < 1e-12
           and abs(spec["volume"] - np.pi / 4
                   * (0.06 ** 2 - 0.05 ** 2) * 2.0) < 1e-12
           and abs(spec["mass"] - spec["volume"] * STEEL) < 1e-9)
    check("P1 the spec sheet — structural details, complete numbers",
          ok1, f"wall {spec['wall'] * 1000:.1f}mm, volume "
               f"{spec['volume'] * 1e6:.1f}cm3, mass "
               f"{spec['mass']:.2f}kg (density cited)")

    # P2 — THE 3D MODEL: emitted, watertight, court-passing
    n = 64
    V, F = tube_mesh_clean(0.050, 0.060, 2.0, n)
    obj = os.path.join(RUNS, "tube.obj")
    write_obj(obj, V, F)
    v_mesh = mesh_volume(V, F)
    poly = (n / 2) * np.sin(2 * np.pi / n)
    v_poly = poly * ((0.03) ** 2 - (0.025) ** 2) * 2.0
    v_circ = spec["volume"]
    ok2 = (abs(v_mesh - v_poly) < 1e-12 * max(1, v_poly)
           and abs(v_mesh - v_circ) / v_circ < 0.01
           and len(F) == 8 * n and os.path.getsize(obj) > 10000)
    check("P2 the 3D model — watertight mesh, volume exact at the "
          "mesh's own ruler, recipe within named discretization",
          ok2, f"{len(V)} verts / {len(F)} faces -> {obj}; mesh "
               f"{v_mesh * 1e6:.3f} vs poly {v_poly * 1e6:.3f} vs "
               f"circle {v_circ * 1e6:.3f} cm3 "
               f"({(1 - v_mesh / v_circ) * 100:.2f}% discretization)")

    # P3 — the family: a different instance, same recipe
    V2, F2 = tube_mesh_clean(0.102, 0.114, 6.0, n)
    v2 = mesh_volume(V2, F2)
    v2_circ = np.pi / 4 * (0.114 ** 2 - 0.102 ** 2) * 6.0
    ok3 = abs(v2 - v2_circ) / v2_circ < 0.01
    check("P3 the family — learn one tube, own the family", ok3,
          f"4in-sch40-ish instance: {v2 * 1e6:.0f} vs "
          f"{v2_circ * 1e6:.0f} cm3")

    # P4 — the contact taxonomy, quantities named
    c1 = contact_court(9.98, 10.00)
    c2 = contact_court(10.00, 10.00)
    c3 = contact_court(10.05, 10.00, intent="press")
    c4 = contact_court(8.0, 10.0, joint="weld")
    ok4 = (c1["kind"] == "NOT TOUCHING" and c1["clearance"] == 0.02
           and c2["kind"] == "TOUCHING"
           and c3["kind"] == "CONNECTED"
           and c3["interference"] == 0.05
           and c4["kind"] == "CONNECTED" and "weld" in c4["how"])
    check("P4 contact taxonomy — clearance named, touching, press "
          "fit, weld", ok4,
          f"{c1['kind']}({c1['clearance']}) / {c2['kind']} / "
          f"{c3['kind']}({c3['interference']}) / {c4['kind']}")

    # P5 — the intent court: same geometry, two verdicts
    c5 = contact_court(10.05, 10.00, intent="loose")
    ok5 = c5["kind"] == "WOUND" and "one space" in c5["receipt"]
    check("P5 intent court — the same interference is a fastening "
          "or a wound by INTENT", ok5, f"{c5['receipt'][:56]}")

    # P6 — force paths: tested, not asserted
    pressed = contact_court(10.05, 10.00, intent="press")
    resting = contact_court(10.00, 10.00)
    gap = contact_court(9.98, 10.00)
    truth = [
        (force_path([pressed], "pull"), True,
         "pull through a press fit"),
        (force_path([pressed], "push"), True,
         "push through a press fit"),
        (force_path([resting], "push"), True,
         "push through resting contact"),
        (force_path([resting], "pull"), False,
         "pull through resting contact"),
        (force_path([gap], "push"), False, "push across a gap"),
        (force_path([pressed, resting], "pull"), False,
         "pull through press THEN resting — the chain's weakest "
         "link rules"),
    ]
    ok6 = all(got == want for got, want, _ in truth)
    check("P6 force paths — 6/6 propagation answers correct", ok6,
          "; ".join(f"{name}:{'Y' if got else 'N'}"
                    for got, _, name in truth[:3]) + " ...")

    # P7 — physics read from the text
    phys = read_physics(SPRING_SRC)
    ok7 = (phys.get("k") == 3.5 and phys.get("e") == 0.8
           and "-self.k * self.x" in phys.get("force_law", ""))
    check("P7 physics READ — k, e, and the force law from the text",
          ok7, f"{phys}")

    # P8 — the instrument confirms the read
    ns = {}
    exec(compile(SPRING_SRC, "<sim>", "exec"), ns)   # noqa: S102
    sb = ns["SpringBall"]()
    dt = 1e-4
    xs = []
    for _ in range(int(12.0 / dt)):
        sb.step(dt)
        xs.append(sb.x)
    xs = np.asarray(xs)
    crossings = np.where((xs[:-1] > 0) & (xs[1:] <= 0))[0]
    T = float(np.mean(np.diff(crossings))) * dt
    k_meas = 2.0 * (2 * np.pi / T) ** 2
    bc = ns["Bouncer"]()
    peaks, prev_v, cur_max = [], bc.v, 0.0
    for _ in range(int(6.0 / dt)):
        bc.step(dt)
        cur_max = max(cur_max, bc.y)
        if prev_v < 0 and bc.v > 0:          # bounce happened
            peaks.append(cur_max)
            cur_max = 0.0
        prev_v = bc.v
    e_meas = float(np.sqrt(np.mean(
        [peaks[i + 1] / peaks[i] for i in range(2, 5)])))
    ok8 = (abs(k_meas - 3.5) / 3.5 < 0.01
           and abs(e_meas - 0.8) / 0.8 < 0.02)
    check("P8 the instrument — measured k and e confirm the read",
          ok8, f"k {k_meas:.4f} (read 3.5), e {e_meas:.4f} "
               f"(read 0.8)")

    dt2 = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt2:.1f}s)")


if __name__ == "__main__":
    main()
