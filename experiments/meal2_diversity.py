"""meal2_diversity.py — MEAL 2: THE DIVERSITY PLATE (owner ruling,
2026-07-18: "larger sets dont do much theoretically because after he
gets the structure down it is just revalidating what he already
knows... its mainly diversity that im interested in").

Five dishes, five DIFFERENT structural forms, all real:

  galileo-1604     Galileo's inclined-plane table (folio 107v, Drake):
                   distance at equal time ticks, in punti. QUADRATIC —
                   the first real t^2 of modern science.
  atmosphere-1976  US Standard Atmosphere: pressure vs altitude,
                   0-20 km. EXPONENTIAL decay (honestly piecewise —
                   the tropopause at ~11 km bends the law; whatever he
                   says about that is a finding, not a failure).
  planet-gravity   11 real bodies (NASA): surface gravity from mass
                   AND radius — a TWO-VARIABLE inverse-square law
                   (g = 66.74*M/R^2 in these units). Tests
                   cross-variable products.
  co2-maunaloa     NOAA GML annual mean CO2, 1959-2025 (fetched:
                   data/feeds/co2_annmean_mlo.txt). An accelerating
                   TREND — his call what form it earns.
  sunspots-1700    SILSO yearly sunspot number, 1700-2025 (fetched:
                   data/feeds/sunspots_yearly.csv). OSCILLATORY with
                   an irregular ~11-year cycle — deliberately feeds
                   the NAMED open leak (lag proposer silent on
                   oscillatory series, 2026-07-16). A refusal or
                   PARTIAL here is an honest frontier receipt.

DRY (default): throwaway mind. LIVE (--live): his account — the
standing feeding order (owner, 2026-07-18: "run full in the alpha
v.1"): dry-prove first, then feed live, journal kind=meal, log the
road-trial line.

usage: python meal2_diversity.py [--live] [home]
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

FEEDS = os.path.join(ROOT, "data", "feeds")


def load_plate():
    """Embedded dishes are documented values; fetched dishes parse
    the plain files (URLs in comments); a missing file SKIPS the dish
    with a said receipt — never a silent absence."""
    plate = []
    # Galileo, folio 107v (Drake 1973): equal time ticks, punti
    t = np.arange(1.0, 9.0)
    d = np.array([33.0, 130.0, 298.0, 526.0, 824.0, 1192.0,
                  1620.0, 2104.0])
    plate.append(("galileo-1604", t.reshape(-1, 1), d))
    # US Standard Atmosphere 1976: altitude km -> pressure kPa
    alt = np.arange(0.0, 21.0)
    p = np.array([101.325, 89.876, 79.501, 70.121, 61.660, 54.048,
                  47.217, 41.105, 35.651, 30.800, 26.499, 22.699,
                  19.399, 16.579, 14.170, 12.111, 10.352, 8.849,
                  7.565, 6.467, 5.529])
    plate.append(("atmosphere-1976", alt.reshape(-1, 1), p))
    # NASA fact sheets: M (1e24 kg), R (1e3 km) -> g (m/s^2);
    # Sun, Mercury..Neptune, Moon, Pluto
    M = [1989000.0, 0.330, 4.87, 5.97, 0.073, 0.642, 1898.0,
         568.0, 86.8, 102.0, 0.0130]
    R = [696.0, 2.4397, 6.0518, 6.371, 1.7374, 3.3895, 69.911,
         58.232, 25.362, 24.622, 1.1883]
    g = [274.0, 3.70, 8.87, 9.81, 1.62, 3.71, 24.79, 10.44,
         8.87, 11.15, 0.62]
    plate.append(("planet-gravity",
                  np.column_stack([M, R]), np.asarray(g)))
    # NOAA GML: https://gml.noaa.gov/webdata/ccgg/trends/co2/
    #   co2_annmean_mlo.txt  (year, mean, unc)
    f = os.path.join(FEEDS, "co2_annmean_mlo.txt")
    if os.path.exists(f):
        rows = [ln.split() for ln in open(f, encoding="utf-8")
                if ln.strip() and not ln.startswith("#")]
        yr = np.array([float(r[0]) for r in rows])
        co2 = np.array([float(r[1]) for r in rows])
        plate.append(("co2-maunaloa", (yr - 1959.0).reshape(-1, 1),
                      co2))
    else:
        print("  SKIPPED co2-maunaloa: data/feeds file absent")
    # SILSO: https://www.sidc.be/SILSO/DATA/SN_y_tot_V2.0.csv
    #   (year; yearly-mean sunspot number; sd; nobs; definitive)
    f = os.path.join(FEEDS, "sunspots_yearly.csv")
    if os.path.exists(f):
        rows = [ln.split(";") for ln in open(f, encoding="utf-8")
                if ln.strip()]
        yr = np.array([float(r[0]) for r in rows])
        sn = np.array([float(r[1]) for r in rows])
        keep = sn >= 0
        plate.append(("sunspots-1700",
                      (yr[keep] - 1700.0).reshape(-1, 1), sn[keep]))
    else:
        print("  SKIPPED sunspots-1700: data/feeds file absent")
    return plate


def feed(mind):
    rng = np.random.default_rng(0)
    report = []
    for name, X, y in load_plate():
        order = rng.permutation(len(y))
        res = mind.discover(X[order], y[order], name=name)
        c = mind.net.get_meta(f"law:{name}", "container")
        acc = res.get("accounting") or {}
        report.append((name, res["verdict"], res["equation"],
                       res["r2"], c))
        print(f"  {name:16s} {res['verdict']:10s} r2={res['r2']:7.4f} "
              f"eq: {res['equation']}")
        print(f"  {'':16s} container: {c}; accounting: "
              f"articulated {acc.get('articulated')}% captured "
              f"{acc.get('captured')}% noise {acc.get('noise')}%")
    crys = mind.crystallize_forms()
    for fm in crys["families"]:
        print(f"  FAMILY {fm['family']}: {fm['members']} across "
              f"{fm['containers']}")
    if not crys["families"]:
        print("  families: none new this meal (five strangers — "
              "that IS the diversity)")
    return report, crys


def receipts(mind):
    p = mind.apply_law("galileo-1604", np.array([[9.0]]))
    if p is not None:
        print(f"  Galileo tick 9 (never in the folio): "
              f"{float(p[0]):.0f} punti (t^2 says ~2673)")
    q = mind.apply_law("planet-gravity",
                       np.array([[0.0148, 1.353]]))   # Eris
    if q is not None:
        print(f"  Eris (M=0.0148, R=1353 km, never fed): "
              f"{float(q[0]):.2f} m/s^2 (measured ~0.82)")


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
        n_said = sum(1 for r in report
                     if r[1] in ("UNDERSTOOD", "PARTIAL"))
        print(f"\n  DRY: {n_said}/{len(report)} spoke "
              f"({', '.join(r[1] for r in report)}); "
              f"{len(crys['families'])} new family  "
              f"({time.perf_counter() - t0:.1f}s)")
        return

    from isaac_store.sparring import IsaacAccount      # noqa: E402
    from isaac_store.roadtrial import log_roadtrial    # noqa: E402
    acct = IsaacAccount(home, mod)
    print(f"LIVE — his account: {home} "
          f"({acct.sessions_so_far()} journal entries so far)")
    report, crys = feed(acct.mind)
    receipts(acct.mind)
    acct._journal(dict(
        kind="meal", stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        dishes=[dict(name=r[0], verdict=r[1], equation=r[2],
                     r2=round(r[3], 5), container=r[4])
                for r in report],
        families=[dict(family=f["family"], members=f["members"],
                       containers=f["containers"])
                  for f in crys["families"]]))
    acct.mind.save(acct.mind_path)
    line = log_roadtrial(home, acct.mind, mod)
    print(f"\n  MEAL JOURNALED + mind saved; road-trial line:")
    print(f"  {line}")


if __name__ == "__main__":
    main()
