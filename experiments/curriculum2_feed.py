"""curriculum2_feed.py — MEAL 9: THE SCALE MEAL (the campaign's
rung 4; owner 2026-07-19 "lets go" + the standing order from the
engineer-day handoff: "push laws 37 -> 100+ ... measure precision/
probe-time at each step" + THE DIVERSITY RULING: form diversity
over volume).

Coding + systems + electrical + mechanics + thermal + materials +
waves, told through the promoted doors (tell_law + the app
fact-bundle), IN TRANCHES — after every tranche the road-trial
organ measures SELECTION PRECISION and probe time: the selection
curve is the deliverable, not just the count. Every law carries
its citation; per-material variants are real handbook knowledge
(steel E=200 GPa, copper k=401 W/mK); shared shapes are the
SHAPES DISCOVERY working (KE = capacitor energy = spring energy =
one 0.5*x*y^2 form wearing three labels — witnesses, never
duplicate nodes).

DRY (default): throwaway mind, full receipts, the curve printed.
LIVE (--live): his account — journal kind=meal, road-trial lines
per tranche.

usage: python curriculum2_feed.py [--live] [home]
"""
import os
import shutil
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
import isaac as mod                                    # noqa: E402

# (app, container, equation, output, slots, citation)
TRANCHES = dict(
    algorithms=[
        ("linear-scan", "+1.00*x0", "time", "n",
         "O(n) sequential scan"),
        ("all-pairs", "+1.00*x0*x0", "time", "n",
         "O(n^2) nested loops"),
        ("merge-sort", "+1.00*x0*log(x0)", "time", "n",
         "O(n log n), von Neumann 1945"),
        ("binary-search", "+1.00*log(x0)", "time", "n",
         "O(log n) bisection"),
        ("naive-matmul", "+1.00*x0*x0*x0", "time", "n",
         "O(n^3) triple loop"),
        ("array-bytes", "+8.00*x0", "bytes", "n",
         "8-byte elements"),
        ("hash-slots", "+16.00*x0", "bytes", "n",
         "16-byte buckets"),
        ("comparison-bound", "+1.44*x0*log(x0)", "comparisons",
         "n", "information-theoretic sorting bound"),
        ("subset-blowup", "+1.00*exp(0.693*x0)", "count", "n",
         "2^n subsets (exp form)"),
    ],
    systems=[
        ("littles-law", "+1.00*x0*x1", "queue", "rate,wait",
         "Little 1961"),
        ("transmission-time", "+1.00*x0*x1^-1", "time",
         "size,bandwidth", "store-and-forward"),
        ("amdahl-limit", "+1.00*x0^-1", "speedup",
         "serialfraction", "Amdahl 1967 asymptote"),
        ("cpu-dynamic-power", "+1.00*x0*x1*x1", "power",
         "frequency,voltage", "P ~ f V^2 CMOS"),
        ("rc-time-constant", "+1.00*x0*x1", "tau",
         "resistance,capacitance", "RC first-order"),
        ("capacitor-charge-curve", "+1.00 -1.00*exp(-1.00*x0)",
         "fraction", "timeconstants", "1 - e^-t/tau"),
    ],
    electrical2=[
        ("capacitor-energy", "+0.50*x0*x1*x1", "energy",
         "capacitance,voltage", "E = CV^2/2"),
        ("inductor-energy", "+0.50*x0*x1*x1", "energy",
         "inductance,current", "E = LI^2/2"),
        ("charge-from-current", "+1.00*x0*x1", "charge",
         "current,time", "Q = It"),
        ("electrical-energy", "+1.00*x0*x1", "energy",
         "power,time", "E = Pt"),
        ("wire-resistance", "+1.00*x0*x1*x2^-1", "resistance",
         "resistivity,length,area", "R = rho L / A"),
        ("rms-power", "+0.50*x0*x1", "power", "vpeak,ipeak",
         "P = Vp Ip / 2 (sine)"),
    ],
    mechanics2=[
        ("kinetic-energy", "+0.50*x0*x1*x1", "energy",
         "mass,velocity", "KE = mv^2/2"),
        ("spring-energy", "+0.50*x0*x1*x1", "energy",
         "stiffness,extension", "E = kx^2/2"),
        ("momentum", "+1.00*x0*x1", "momentum", "mass,velocity",
         "p = mv"),
        ("gravity-pe", "+9.81*x0*x1", "energy", "mass,height",
         "g = 9.81 SI"),
        ("centripetal-force", "+1.00*x0*x1*x1*x2^-1", "force",
         "mass,velocity,radius", "F = mv^2/r"),
        ("cantilever-tip", "+0.333*x0*x1*x1*x1*x2^-1*x3^-1",
         "deflection", "force,length,modulus,inertia",
         "FL^3/3EI point load"),
        ("dynamic-pressure", "+0.50*x0*x1*x1", "pressure",
         "density,velocity", "q = rho v^2 / 2"),
        ("drag-force", "+0.50*x0*x1*x2*x3*x3", "force",
         "density,dragcoeff,area,velocity",
         "F = 1/2 rho Cd A v^2"),
    ],
    thermal=[
        ("sensible-heat", "+1.00*x0*x1*x2", "heat",
         "mass,specificheat,deltat", "Q = m c dT"),
        ("conduction-copper", "+401.0*x0*x1*x2^-1", "heatrate",
         "area,deltat,thickness", "k = 401 W/mK copper"),
        ("conduction-aluminum", "+237.0*x0*x1*x2^-1", "heatrate",
         "area,deltat,thickness", "k = 237 W/mK aluminum"),
        ("conduction-steel", "+50.0*x0*x1*x2^-1", "heatrate",
         "area,deltat,thickness", "k = 50 W/mK steel"),
        ("conduction-glass", "+1.05*x0*x1*x2^-1", "heatrate",
         "area,deltat,thickness", "k = 1.05 W/mK glass"),
        ("conduction-concrete", "+1.40*x0*x1*x2^-1", "heatrate",
         "area,deltat,thickness", "k = 1.4 W/mK concrete"),
        ("conduction-pine", "+0.12*x0*x1*x2^-1", "heatrate",
         "area,deltat,thickness", "k = 0.12 W/mK pine"),
        ("stefan-boltzmann", "+0.0000000567*x0^4", "radiance",
         "temperature", "sigma = 5.67e-8"),
        ("ideal-gas-pressure", "+8.314*x0*x1*x2^-1", "pressure",
         "moles,temperature,volume", "R = 8.314 J/molK"),
    ],
    materials=[
        ("hooke-steel", "+200000*x0", "stress", "strain",
         "E = 200 GPa (MPa units)"),
        ("hooke-aluminum", "+69000*x0", "stress", "strain",
         "E = 69 GPa"),
        ("hooke-copper", "+117000*x0", "stress", "strain",
         "E = 117 GPa"),
        ("hooke-titanium", "+110000*x0", "stress", "strain",
         "E = 110 GPa"),
        ("hooke-concrete", "+30000*x0", "stress", "strain",
         "E = 30 GPa"),
        ("hooke-nylon", "+3000*x0", "stress", "strain",
         "E = 3 GPa"),
        ("hooke-oak", "+11000*x0", "stress", "strain",
         "E = 11 GPa along grain"),
        ("hooke-glass", "+70000*x0", "stress", "strain",
         "E = 70 GPa"),
    ],
    waves=[
        ("wave-speed", "+1.00*x0*x1", "speed",
         "frequency,wavelength", "v = f lambda"),
        ("lens-power", "+1.00*x0^-1", "power", "focallength",
         "P = 1/f diopters"),
        ("half-life-decay", "+1.00*exp(-0.693*x0)", "fraction",
         "halflives", "N/N0 = 2^-t"),
        ("unit-oscillator", "+1.00*sin(6.283*x0)", "displacement",
         "phase", "sin, one turn per unit"),
        ("stress-basic", "+1.00*x0*x1^-1", "stress", "force,area",
         "sigma = F/A"),
        ("flow-rate", "+1.00*x0*x1", "flow", "area,velocity",
         "Q = A v"),
    ],
)


def court(mind, name, eq, nslots, rng):
    """Forward-exact + corrupt-refuses: the light bulk court."""
    X = rng.uniform(0.5, 3.0, (24, max(nslots, 1)))
    y = mind.apply_law(name, X)
    if y is None:
        return "REFUSED-APPLY"
    ok = mind.validate_law(name, X, y)["status"] == "HOLDS"
    bad = mind.validate_law(name, X, y + rng.normal(
        0, 3.0 * (np.abs(y).mean() + 1.0), len(y)))["status"]
    return "OK" if ok and bad in ("FAILS", "DEGRADED") else \
        f"COURT-ODD({ok},{bad})"


def feed(mind, roadtrial=None, home=None):
    rng = np.random.default_rng(42)
    curve = []
    stats = dict(forms=0, matches=0, variants=0, apps=0, odd=0)
    for tranche, laws in TRANCHES.items():
        cont = f"told-{tranche}"
        mind.open_world(cont)
        for app, eq, out, slots, cite in laws:
            nslots = len(slots.split(","))
            r = mind.tell_law(app, eq, d=nslots, who=cite)
            st = r.get("status")
            if st == "MATCHES":
                stats["matches"] += 1
                form = r["law"]
            elif st == "VARIANT":
                stats["variants"] += 1
                form = app
            else:
                stats["forms"] += 1
                form = app
            mind.teach(app, "uses-form", form)
            mind.teach(app, "output", out)
            mind.teach(app, "slots", slots)
            stats["apps"] += 1
            verdict = court(mind, form, eq, nslots, rng)
            if verdict != "OK":
                stats["odd"] += 1
        n_laws = sum(1 for n in mind.net.meta
                     if str(n).startswith("law:"))
        point = dict(tranche=tranche, laws=n_laws)
        if roadtrial:
            line = roadtrial(home, mind, mod)
            point.update(precision=line["selection"]["precision"],
                         probe_secs=line["probe_secs"],
                         nodes=line["nodes"], facts=line["facts"])
        else:
            t0 = time.perf_counter()
            mind.decompose("energy", known=dict(mass=2.0,
                                                velocity=3.0))
            point["probe_secs"] = round(
                time.perf_counter() - t0, 4)
        curve.append(point)
        print(f"  tranche {tranche}: laws {n_laws}"
              + (f", precision {point.get('precision')}"
                 if "precision" in point else "")
              + f", probe {point.get('probe_secs')}s")
    return curve, stats


def main():
    args = [a for a in sys.argv[1:] if a != "--live"]
    live = "--live" in sys.argv[1:]
    home = args[0] if args else os.path.join(
        os.path.expanduser("~"), "Documents", "isaac_home")
    if live:
        from isaac_store.sparring import IsaacAccount
        from isaac_store.roadtrial import log_roadtrial
        shutil.copy2(os.path.join(home, "mind.isaac"),
                     os.path.join(home, "mind.isaac.bak"))
        print("[mind.isaac.bak written]")
        acct = IsaacAccount(home, mod)
        n0 = sum(1 for n in acct.mind.net.meta
                 if str(n).startswith("law:"))
        print(f"LIVE — his account: {home} (laws before: {n0})")
        curve, stats = feed(acct.mind, roadtrial=log_roadtrial,
                            home=home)
        acct._journal(dict(kind="meal",
                           stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                           meal="curriculum2 — the scale meal",
                           tranches=list(TRANCHES),
                           stats=stats, curve=curve))
        acct.mind.save(acct.mind_path)
        print(f"\n  MEAL JOURNALED + mind saved.")
    else:
        with tempfile.TemporaryDirectory() as td:
            scratch = os.path.join(td, "scratch_home")
            shutil.copytree(home, scratch)
            from isaac_store.sparring import IsaacAccount
            from isaac_store.roadtrial import log_roadtrial
            acct = IsaacAccount(scratch, mod)
            n0 = sum(1 for n in acct.mind.net.meta
                     if str(n).startswith("law:"))
            print(f"DRY (scratch copy of his account; laws "
                  f"before: {n0})")
            curve, stats = feed(acct.mind, roadtrial=log_roadtrial,
                                home=scratch)
    print(f"\n  STATS: {stats}")
    print(f"  THE SELECTION CURVE:")
    for p in curve:
        print(f"    {p}")


if __name__ == "__main__":
    main()
