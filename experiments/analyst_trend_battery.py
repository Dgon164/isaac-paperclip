"""analyst_trend_battery.py — PROMOTION GATE for THE TREND ROAD (A1
of the analyst segment; owner, 2026-07-18: "seeing a trend line for
a market statistic is fine, but thats just one job that a data
analyst would do. lets give him a full data analyst capability").

analyze_series decomposes a time series with receipts: trend by the
ordinary discover vocabulary (changepoints free via switch atoms),
period by autocorrelation past a shuffle null (bracket+refined),
the seasonal profile FOLDED AND LEARNED (a shape, never a forced
sinusoid) past its own null, accounting complete
(trend+seasonal+residual=100), the series in its own container,
apply_series forecasting forward.

  T1 PLANTED DECOMPOSITION: trend 0.5t+10 + 12-period sawtooth +
     noise -> trend said, period ~12, profile recovered, accounting
     sums to 100.
  T2 CHANGEPOINT FREE: a level step at t=50 lands in the trend law
     via the switch atom ([x0>...] in the equation).
  T3 THE NULL: shuffled y -> no period said, no profile, receipts
     kept.
  T4 HONEST AMPLITUDE DARKNESS: an amplitude-modulated cycle says
     its PERIOD and keeps amplitude variation in the residual (the
     sunspot shape, synthetic).
  T5 REAL SUNSPOTS (SILSO 1700-2025): the meal-2 refusal cured at
     the analyst level — period said in 10..12 years past the null.
  T6 REAL MONTHLY CO2 (NOAA): trend + period ~12 months + the
     Keeling sawtooth profile (spring peak, autumn trough) — the
     famous decomposition, his receipts.
  T7 FORECAST: apply_series predicts T1's held-out future within
     tolerance.
  T8 CONTAINERS: the series and its trend law land in the series'
     own world; base untouched.

Run: cd experiments && PYTHONHASHSEED=0 python analyst_trend_battery.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac
FEEDS = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "feeds")


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    rng = np.random.default_rng(0)

    # T1 — planted trend + seasonality
    n = 240
    tt = np.arange(n, dtype=float)
    saw = np.array([3.0, 1.5, 0.5, -0.5, -1.5, -3.0, -2.0, -1.0,
                    0.0, 1.0, 2.0, 0.0])
    y1 = 0.5 * tt + 10.0 + saw[(tt.astype(int)) % 12] \
        + rng.normal(0, 0.3, n)
    m1 = Isaac()
    r1 = m1.analyze_series(tt[:200], y1[:200], name="planted")
    acc = r1["accounting"]
    prof_ok = (r1["profile"] is not None and r1["nbins"] == 12
               and max(abs(np.array(r1["profile"])
                           - saw)) < 0.5)
    ok1 = (r1["period"] is not None
           and abs(r1["period"] - 12.0) < 0.5
           and prof_ok
           and abs(acc["trend"] + acc["seasonal"]
                   + acc["residual"] - 100.0) < 0.2
           and acc["residual"] < 5.0)
    check("T1 planted decomposition — trend + period 12 + profile "
          "recovered, books balance", ok1,
          f"period {r1['period']}; accounting {acc}")

    # T2 — changepoint free via the switch atom (the step sits at a
    # ruler mark — thresholds are data-proposed on marks, never
    # refined: the promoted rounding law)
    y2 = 2.0 * tt + np.where(tt > 100, 30.0, 0.0) \
        + rng.normal(0, 0.2, n)
    m2 = Isaac()
    r2 = m2.analyze_series(tt, y2, name="stepworld")
    eq2 = r2["trend_equation"] or ""
    thr = None
    if "[x0>" in eq2:
        thr = float(eq2.split("[x0>")[1].split("]")[0])
    # the switch names the changepoint; a threshold one row off is
    # graded PARTIAL honestly (proposals live on marks+deciles, never
    # refined — exact jump-point proposal is a NAMED DEBT, queued)
    ok2 = (r2["trend_verdict"] in ("UNDERSTOOD", "PARTIAL")
           and thr is not None and abs(thr - 100.0) <= 2.0)
    check("T2 changepoint free — the switch atom names the step in "
          "the trend law", ok2,
          f"{r2['trend_verdict']}: {eq2[:44]} (threshold {thr})")

    # T3 — the null: shuffled y says nothing
    ys = y1.copy()
    rng.shuffle(ys)
    m3 = Isaac()
    r3 = m3.analyze_series(tt, ys, name="shuffled")
    ok3 = (r3["period"] is None and r3["profile"] is None
           and len(r3["receipts"]["bypassed"]) >= 1)
    check("T3 the null — shuffled series: no period, no profile, "
          "receipts kept", ok3,
          f"bypassed: {r3['receipts']['bypassed'][:2]}")

    # T4 — amplitude-varying cycle: period said, amplitude dark.
    # Run-1 wrong-kept: deterministic AM was FULLY ARTICULATED as
    # sidebands (three exact sinusoids) — the machine outdid the
    # prediction. The genuinely dark world needs per-cycle RANDOM
    # amplitudes, which no sinusoid sum can say.
    amps = rng.uniform(0.2, 1.8, 30)
    y4 = amps[(tt / 11.0).astype(int) % 30] \
        * np.sin(2 * np.pi * tt / 11.0) + rng.normal(0, 0.1, n)
    m4 = Isaac()
    r4 = m4.analyze_series(tt, y4, name="ampvary")
    ok4 = (r4["period"] is not None
           and abs(r4["period"] - 11.0) < 1.0
           and r4["accounting"]["residual"] > 10.0)
    check("T4 honest amplitude darkness — period said, variation "
          "stays residual", ok4,
          f"period {r4['period']}; accounting {r4['accounting']}")

    # T5 — real sunspots: the meal-2 refusal answered
    f = os.path.join(FEEDS, "sunspots_yearly.csv")
    rows = [ln.split(";") for ln in open(f, encoding="utf-8")
            if ln.strip()]
    yr = np.array([float(r[0]) for r in rows])
    sn = np.array([float(r[1]) for r in rows])
    keep = sn >= 0
    m5 = Isaac()
    r5 = m5.analyze_series(yr[keep], sn[keep], name="sunspots",
                           max_period=40)
    ok5 = r5["period"] is not None and 10.0 <= r5["period"] <= 12.0
    check("T5 real sunspots — the ~11-year cycle SAID past the null",
          ok5,
          f"period {r5['period']} yr (ac {r5['receipts'].get('period_ac')} "
          f"vs null {r5['receipts'].get('period_null')}); "
          f"accounting {r5['accounting']}")

    # T6 — real monthly CO2: the Keeling decomposition
    f = os.path.join(FEEDS, "co2_mm_mlo.txt")
    rows = [ln.split() for ln in open(f, encoding="utf-8")
            if ln.strip() and not ln.startswith("#")]
    dec = np.array([float(r[2]) for r in rows])
    co2 = np.array([float(r[3]) for r in rows])
    keep = co2 > 0
    tm = (dec[keep] - dec[keep][0]) * 12.0     # months since start
    m6 = Isaac()
    r6 = m6.analyze_series(tm, co2[keep], name="co2-monthly")
    pr = np.array(r6["profile"]) if r6["profile"] else None
    swing = float(pr.max() - pr.min()) if pr is not None else -1.0
    ok6 = (r6["period"] is not None
           and abs(r6["period"] - 12.0) < 0.5
           and pr is not None
           and r6["accounting"]["trend"] > 95.0
           and swing > 4.0)
    check("T6 real monthly CO2 — trend + 12-month period + the "
          "Keeling sawtooth", ok6,
          f"period {r6['period']} mo; profile swing {swing:.1f} ppm; "
          f"accounting {r6['accounting']}; receipts "
          f"{r6['receipts']['bypassed'][:1]}")

    # T7 — forecast: the held-out future
    fc = m1.apply_series("planted", tt[200:])
    err = float(np.max(np.abs(fc - (0.5 * tt[200:] + 10.0
                                    + saw[(tt[200:].astype(int)) % 12]))))
    ok7 = fc is not None and err < 1.0
    check("T7 forecast — held-out future within tolerance", ok7,
          f"max err {err:.2f} over 40 future steps")

    # T8 — containers: the series lands in its own world
    ok8 = (r1["container"] == "data-planted"
           and "in:data-planted" in m1.net.get_door_tags(
               "world:data-planted", "series:planted")
           and m1.net.get_meta("law:planted-trend",
                               "container") == "data-planted")
    check("T8 containers — series + trend law in their own world",
          ok8, f"container {r1['container']}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
