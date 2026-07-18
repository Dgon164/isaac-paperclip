"""meal4_analyst.py — MEAL 4: THE ANALYST'S FIRST ASSIGNMENTS.

Two real series through the new trend road, both with history:

  sunspots-series   326 years of SILSO sunspot numbers — meal 2's
                    honest refusal, now answered: the ~11-year cycle
                    said past the null, amplitude variation kept
                    dark (it IS dark to a fixed profile).
  co2-series        NOAA monthly CO2 — meal 2 saw only annual means
                    (a PARTIAL trend); the analyst now says the
                    whole decomposition: trend + the 12-month
                    Keeling sawtooth + the honest leftover, and
                    FORECASTS forward.

DRY (default): throwaway mind. LIVE (--live): his account, standing
order — journal kind=meal, mind saved, road-trial line.

usage: python meal4_analyst.py [--live] [home]
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

FEEDS = os.path.join(ROOT, "data", "feeds")


def load_series():
    out = []
    f = os.path.join(FEEDS, "sunspots_yearly.csv")
    rows = [ln.split(";") for ln in open(f, encoding="utf-8")
            if ln.strip()]
    yr = np.array([float(r[0]) for r in rows])
    sn = np.array([float(r[1]) for r in rows])
    keep = sn >= 0
    out.append(("sunspots-series", yr[keep], sn[keep], dict(max_period=40)))
    f = os.path.join(FEEDS, "co2_mm_mlo.txt")
    rows = [ln.split() for ln in open(f, encoding="utf-8")
            if ln.strip() and not ln.startswith("#")]
    dec = np.array([float(r[2]) for r in rows])
    co2 = np.array([float(r[3]) for r in rows])
    keep = co2 > 0
    out.append(("co2-series", (dec[keep] - dec[keep][0]) * 12.0,
                co2[keep], dict()))
    return out


def feed(mind):
    dishes = []
    for name, t, y, kw in load_series():
        r = mind.analyze_series(t, y, name=name, **kw)
        print(f"  {name:16s} trend[{r['trend_verdict']}]: "
              f"{(r['trend_equation'] or '')[:40]}")
        print(f"  {'':16s} period: {r['period']}  accounting: "
              f"{r['accounting']}")
        if r["profile"]:
            pr = np.array(r["profile"])
            print(f"  {'':16s} profile swing {pr.max() - pr.min():.2f} "
                  f"({r['nbins']} bins)")
        for b in r["receipts"]["bypassed"]:
            print(f"  {'':16s} receipt: {b}")
        dishes.append(dict(name=name, period=r["period"],
                           trend=r["trend_equation"],
                           trend_verdict=r["trend_verdict"],
                           accounting=r["accounting"],
                           container=r["container"]))
    # the forecast receipt: CO2 12 months ahead of the data's end
    t_end = load_series()[1][1][-1]
    future = t_end + np.arange(1.0, 13.0)
    fc = mind.apply_series("co2-series", future)
    if fc is not None:
        print(f"  CO2 forecast, next 12 months: "
              f"{fc.min():.1f}..{fc.max():.1f} ppm "
              f"(data ends {load_series()[1][2][-1]:.1f})")
        dishes[-1]["forecast_12mo"] = [round(float(v), 2) for v in fc]
    return dishes


def main():
    live = "--live" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    home = args[0] if args else os.path.join(
        os.path.expanduser("~"), "Documents", "isaac_home")

    if not live:
        print("DRY RUN — throwaway mind, his account untouched")
        feed(mod.Isaac())
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
