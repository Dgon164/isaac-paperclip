"""meal1_first_laws.py — THE FIRST MEAL (data as food; owner go).

The first real datasets of Isaac's life, all REAL MEASUREMENTS,
chosen so his first cross-domain crystallization is Newton's actual
move replayed on the actual sky:

  solar-system    8 planets: semi-major axis (AU), period (years).
                  NASA planetary fact sheet values.
  jupiter-moons   6 moons (Amalthea..Himalia): a (10^3 km), T (days).
  saturn-moons    7 moons (Mimas..Iapetus): a (10^3 km), T (days).
  boyle-1662      Robert Boyle's original 1662 table: volume
                  (graduations) vs pressure (inches Hg) — real
                  17th-century hands, real noise. A SECOND form.

Every dish lands in its own container (promotion #17: per-dataset
default — no shims, the engine stamps). Then crystallize_forms():
the three orbital systems share T = k*a^1.5 with three different k
(the central body's mass wearing three sizes) -> ONE lawform family,
three variants, constants never smushed. Boyle joins nothing.

Predictions printed as receipts: Pluto (never fed) from the solar
law; Boyle's own held rows from his law.

DRY (default): a fresh throwaway mind — proves the plate, touches
nothing. LIVE (--live): HIS account (Documents/isaac_home) — feeds
the same plate through the same doors, journals kind=meal, saves the
mind, logs the road-trial line (the gauge's first >=2-laws record).
The live road runs ONLY on the owner's go (standing law: nothing
touches isaac_home without the owner).

usage: python meal1_first_laws.py [--live] [home]
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

# ── the plate: real measurements, sources in-line ──────────────────
PLATE = dict(
    # NASA planetary fact sheet: a in AU, T in years
    solar_system=(
        "solar-system",
        [0.387, 0.723, 1.000, 1.524, 5.203, 9.537, 19.191, 30.069],
        [0.2408, 0.6152, 1.0000, 1.8808, 11.862, 29.457, 84.011,
         164.79]),
    # Jupiter's moons: a in 10^3 km, T in days (JPL satellite tables)
    # Metis, Thebe, Amalthea, Io, Europa, Ganymede, Callisto, Leda,
    # Himalia, Lysithea, Elara + run-1 lesson: 6 rows = 3 training
    # rows after holdout -> NO RULE (an honest refusal); more real
    # moons is more knowledge, so the table grew to 11
    jupiter_moons=(
        "jupiter-moons",
        [128.0, 181.4, 221.9, 421.8, 671.1, 1070.4, 1882.7,
         11165.0, 11461.0, 11717.0, 11741.0],
        [0.2948, 0.4982, 0.6745, 1.7691, 3.5512, 7.1546, 16.689,
         240.92, 250.56, 259.20, 259.64]),
    # Saturn's moons: a in 10^3 km, T in days (JPL satellite tables)
    # Prometheus, Pandora, Janus, Mimas, Enceladus, Tethys, Dione,
    # Rhea, Titan, Hyperion, Iapetus, Phoebe (same run-1 lesson)
    saturn_moons=(
        "saturn-moons",
        [139.4, 141.7, 151.5, 185.5, 238.0, 294.7, 377.4, 527.1,
         1221.9, 1481.0, 3560.8, 12947.8],
        [0.6127, 0.6285, 0.6950, 0.9424, 1.3702, 1.8878, 2.7369,
         4.5175, 15.945, 21.277, 79.331, 550.56]),
    # Boyle 1662, "New Experiments Physico-Mechanicall" 2nd ed. table:
    # air volume (tube graduations) vs pressure (inches of mercury)
    boyle_1662=(
        "boyle-1662",
        [48.0, 44.0, 40.0, 36.0, 32.0, 28.0, 24.0, 20.0, 16.0, 12.0],
        [29.125, 31.9375, 35.3125, 39.3125, 44.1875, 50.3125,
         58.8125, 70.6875, 87.875, 117.5625]),
)


def feed(mind):
    """The same doors whichever mind is eating: discover per dish
    (engine stamps the dish's own container), then crystallize."""
    rng = np.random.default_rng(0)
    report = []
    for key in ("solar_system", "jupiter_moons", "saturn_moons",
                "boyle_1662"):
        name, xs, ys = PLATE[key]
        X = np.asarray(xs, float).reshape(-1, 1)
        y = np.asarray(ys, float)
        order = rng.permutation(len(y))     # mix magnitudes across
        X, y = X[order], y[order]           # train and holdout halves
        res = mind.discover(X, y, name=name)
        c = mind.net.get_meta(f"law:{name}", "container")
        report.append((name, res["verdict"], res["equation"],
                       res["r2"], c))
        print(f"  {name:14s} {res['verdict']:10s} r2={res['r2']:.5f} "
              f"eq: {res['equation']}  -> {c}")
    crys = mind.crystallize_forms()
    for f in crys["families"]:
        print(f"  FAMILY {f['family']}: {len(f['members'])} variants "
              f"across {f['containers']}")
    for w in crys["witnesses"]:
        print(f"  witness: {w['members']} ({w['why'][:50]})")
    for e in crys["excluded"]:
        print(f"  excluded: {e['node']} ({e['verdict']}) — {e['why']}")
    return report, crys


def receipts(mind):
    """Predictions on worlds never fed — the law reaching past its
    table is the receipt that he ate knowledge, not rows."""
    out = []
    p = mind.apply_law("solar-system", np.array([[39.482]]))
    if p is not None:
        out.append(("Pluto (a=39.482 AU, never fed)",
                    float(p[0]), 248.09))
        print(f"  Pluto from the solar law: {float(p[0]):.2f} yr "
              f"(true 248.09 — err "
              f"{abs(float(p[0]) - 248.09) / 248.09:.2%})")
    q = mind.apply_law("jupiter-moons", np.array([[129.0]]))
    if q is not None:
        out.append(("Adrastea (a=129e3 km, never fed)",
                    float(q[0]), 0.2983))
        print(f"  Adrastea from the jupiter law: {float(q[0]):.4f} d "
              f"(true 0.2983)")
    s = mind.apply_law("saturn-moons", np.array([[133.58]]))
    if s is not None:
        out.append(("Pan (a=133.58e3 km, never fed)",
                    float(s[0]), 0.575))
        print(f"  Pan from the saturn law: {float(s[0]):.4f} d "
              f"(true 0.575)")
    return out


def selection_demo(mind):
    """The gauge's food: with >=2 laws held, naming the right law per
    world and refusing a superposition is what selection precision
    measures from here on."""
    hits = 0
    for key in ("solar_system", "jupiter_moons", "saturn_moons",
                "boyle_1662"):
        name, xs, ys = PLATE[key]
        w = mind.which_law(np.asarray(xs, float).reshape(-1, 1),
                           np.asarray(ys, float))
        ok = w["verdict"] == "MATCH" and w["law"] == name
        hits += ok
        print(f"  which_law({name}): {w['verdict']} -> {w['law']}"
              f"{'' if ok else '  (MISS)'}")
    _, xs, _ = PLATE["jupiter_moons"]
    _, xs2, ys2 = PLATE["saturn_moons"]
    n = min(len(xs), len(xs2))
    mixX = np.asarray(xs[:n], float).reshape(-1, 1)
    mixy = np.where(np.arange(n) % 2 == 0,
                    2.042e-4 * mixX[:, 0] ** 1.5,
                    3.733e-4 * mixX[:, 0] ** 1.5)
    wm = mind.which_law(mixX, mixy)
    refused = wm["verdict"] != "MATCH"
    print(f"  which_law(interleaved jupiter/saturn): {wm['verdict']}"
          f"{'' if refused else '  (SHOULD REFUSE)'}")
    return hits, refused


def main():
    live = "--live" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    home = args[0] if args else os.path.join(
        os.path.expanduser("~"), "Documents", "isaac_home")
    t0 = time.perf_counter()

    if not live:
        print("DRY RUN — throwaway mind, his account untouched")
        mind = mod.Isaac()
        report, crys = feed(mind)
        receipts(mind)
        hits, refused = selection_demo(mind)
        n_laws = sum(1 for r in report if r[1] in
                     ("UNDERSTOOD", "PARTIAL"))
        print(f"\n  DRY: {n_laws}/4 laws, "
              f"{len(crys['families'])} family, selection "
              f"{hits}/4 named + {'refusal ok' if refused else 'NO refusal'}"
              f"  ({time.perf_counter() - t0:.1f}s)")
        return

    from isaac_store.sparring import IsaacAccount      # noqa: E402
    from isaac_store.roadtrial import log_roadtrial    # noqa: E402
    acct = IsaacAccount(home, mod)
    print(f"LIVE — his account: {home} "
          f"({acct.sessions_so_far()} journal entries so far)")
    report, crys = feed(acct.mind)
    receipts(acct.mind)
    hits, refused = selection_demo(acct.mind)
    acct._journal(dict(
        kind="meal", stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        dishes=[dict(name=r[0], verdict=r[1], equation=r[2],
                     r2=round(r[3], 5), container=r[4])
                for r in report],
        families=[dict(family=f["family"], members=f["members"],
                       containers=f["containers"])
                  for f in crys["families"]],
        selection=dict(named=hits, of=4, refusal=bool(refused))))
    acct.mind.save(acct.mind_path)
    line = log_roadtrial(home, acct.mind, mod)
    print(f"\n  MEAL JOURNALED + mind saved; road-trial line logged:")
    print(f"  {line}")


if __name__ == "__main__":
    main()
