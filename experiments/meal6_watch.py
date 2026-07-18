"""meal6_watch.py — MEAL 6: THE WATCH GOES LIVE.

His solar-system law (fed the 8 planets) now meets ARRIVING DATA it
never saw: the dwarf planets and trans-Neptunian objects — bodies
humanity discovered long after Kepler's table. Batch 1 (Eris,
Makemake, Haumea) establishes the baseline; batch 2 (Quaoar, Orcus,
Gonggong, Sedna) is JUDGED: the law defends its seat against the
Kuiper belt. Standing watches are then established on his CO2 and
sunspot series — from now on, every new NOAA/SILSO release gets
judged on arrival.

DRY runs a throwaway rehearsal; LIVE is his account (standing
order): journal kind=meal, mind saved, road-trial line.

usage: python meal6_watch.py [--live] [home]
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

FEEDS = os.path.join(ROOT, "data", "feeds")

# JPL/MPC values: semi-major axis (AU), period (years)
BATCH1 = (["Eris", "Makemake", "Haumea"],
          [67.86, 45.43, 43.12], [558.0, 306.2, 283.2])
BATCH2 = (["Quaoar", "Orcus", "Gonggong", "Sedna"],
          [43.69, 39.42, 67.5, 506.0], [288.8, 247.5, 554.4, 11400.0])


def feed(mind):
    dishes = []
    for label, (names, a, T) in (("kuiper-batch-1", BATCH1),
                                 ("kuiper-batch-2", BATCH2)):
        r = mind.watch("solar-system",
                       np.asarray(a, float).reshape(-1, 1),
                       np.asarray(T, float))
        print(f"  solar-system vs {label} ({', '.join(names)}):")
        print(f"    {r['verdict']}  err_norm {r['err_norm']}  "
              f"(check #{r['checks']})")
        dishes.append(dict(name=f"solar-system~{label}",
                           verdict=r["verdict"],
                           err_norm=r["err_norm"], n=r["n"]))
    # standing watches on his series: the latest real months/years
    rows = [ln.split() for ln in open(
        os.path.join(FEEDS, "co2_mm_mlo.txt"), encoding="utf-8")
        if ln.strip() and not ln.startswith("#")]
    dec = np.array([float(r[2]) for r in rows])
    co2 = np.array([float(r[3]) for r in rows])
    keep = co2 > 0
    tm = (dec[keep] - dec[keep][0]) * 12.0
    r = mind.watch_series("co2-series", tm[-12:], co2[keep][-12:])
    if r:
        print(f"  co2-series watch (last 12 months): {r['verdict']} "
              f"err_norm {r['err_norm']}")
        dishes.append(dict(name="co2-series-watch",
                           verdict=r["verdict"],
                           err_norm=r["err_norm"]))
    rows = [ln.split(";") for ln in open(
        os.path.join(FEEDS, "sunspots_yearly.csv"), encoding="utf-8")
        if ln.strip()]
    yr = np.array([float(r[0]) for r in rows])
    sn = np.array([float(r[1]) for r in rows])
    keep = sn >= 0
    r = mind.watch_series("sunspots-series", yr[keep][-10:],
                          sn[keep][-10:])
    if r:
        print(f"  sunspots-series watch (last 10 years): "
              f"{r['verdict']} err_norm {r['err_norm']}")
        dishes.append(dict(name="sunspots-series-watch",
                           verdict=r["verdict"],
                           err_norm=r["err_norm"]))
    return dishes


def main():
    live = "--live" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    home = args[0] if args else os.path.join(
        os.path.expanduser("~"), "Documents", "isaac_home")

    if not live:
        print("DRY RUN — rehearsal on a throwaway mind (its own "
              "solar law + series first)")
        m = mod.Isaac()
        rng = np.random.default_rng(0)
        a8 = np.array([0.387, 0.723, 1.000, 1.524, 5.203, 9.537,
                       19.191, 30.069])
        T8 = np.array([0.2408, 0.6152, 1.0000, 1.8808, 11.862,
                       29.457, 84.011, 164.79])
        o = rng.permutation(8)
        m.discover(a8[o].reshape(-1, 1), T8[o], name="solar-system")
        rows = [ln.split() for ln in open(
            os.path.join(FEEDS, "co2_mm_mlo.txt"), encoding="utf-8")
            if ln.strip() and not ln.startswith("#")]
        dec = np.array([float(r[2]) for r in rows])
        co2 = np.array([float(r[3]) for r in rows])
        keep = co2 > 0
        tm = (dec[keep] - dec[keep][0]) * 12.0
        m.analyze_series(tm, co2[keep], name="co2-series")
        rows = [ln.split(";") for ln in open(
            os.path.join(FEEDS, "sunspots_yearly.csv"),
            encoding="utf-8") if ln.strip()]
        yr = np.array([float(r[0]) for r in rows])
        sn = np.array([float(r[1]) for r in rows])
        keep = sn >= 0
        m.analyze_series(yr[keep], sn[keep], name="sunspots-series",
                         max_period=40)
        feed(m)
        return

    from isaac_store.sparring import IsaacAccount      # noqa: E402
    from isaac_store.roadtrial import log_roadtrial    # noqa: E402
    acct = IsaacAccount(home, mod)
    print(f"LIVE — his account: {home} "
          f"({acct.sessions_so_far()} journal entries so far)")
    dishes = feed(acct.mind)
    acct._journal(dict(kind="meal",
                       stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                       dishes=dishes))
    acct.mind.save(acct.mind_path)
    line = log_roadtrial(home, acct.mind, mod)
    print(f"\n  MEAL JOURNALED + mind saved; road-trial line:")
    print(f"  {line}")


if __name__ == "__main__":
    main()
