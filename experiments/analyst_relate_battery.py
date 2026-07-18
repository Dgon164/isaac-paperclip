"""analyst_relate_battery.py — PROMOTION GATE for CROSS-CONTAINER
CORRELATION (A2 of the analyst segment; the triangulation thread
built; owner 2026-07-18: "finding correlations between different
things").

relate_series aligns two series on their shared key, REPORTS level
correlation with the spurious-trend receipt (never judged), judges
the DIFFERENCED correlation across lead/lag shifts against the
ALIGNMENT NULL (circular shifts preserve internal structure,
destroy only the pairing), and mints a relation: node doored to
both worlds when the verdict is RELATED.

  R1 PLANTED DRIVER: a shared wiggle in two trending series, B
     carrying it 2 steps later -> RELATED, lag 2, b... a leads b by
     2 (the driver enters A first), sign +.
  R2 THE SPURIOUS TRAP REFUSED: two independent random walks —
     levels correlate strongly (reported), differences say NO
     RELATION.
  R3 THE NULL: R1's pair with B's years shuffled -> NO RELATION.
  R4 SIGN: an anti-aligned driver -> RELATED, negative.
  R5 THE REAL PAIR: annual CO2 growth vs GISTEMP anomaly — the
     known ENSO-flavored coupling: temperature and the carbon
     cycle's year-to-year breathing -> RELATED past the null, sign
     +, receipts complete.
  R6 THE RELATION NODE: doored into both worlds, meta receipts kept.

Run: cd experiments && PYTHONHASHSEED=0 python analyst_relate_battery.py
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
    n = 120
    tt = np.arange(n, dtype=float)
    z = np.cumsum(rng.normal(0, 1, n + 2))          # a wandering driver
    z = z - np.linspace(z[0], z[-1], n + 2)          # detrended wiggle

    # R1 — planted shared driver, B late by 2
    ya = 0.8 * tt + 5.0 * z[2:] + rng.normal(0, 0.4, n)
    yb = -0.3 * tt + 4.0 * z[:-2] + rng.normal(0, 0.4, n)
    m = Isaac()
    r1 = m.relate_series(tt, ya, tt, yb, name="planted-pair",
                         containers=["data-wa", "data-wb"])
    ok1 = (r1["verdict"] == "RELATED" and r1["corr"] > 0.5
           and r1["shift"] == 2)
    check("R1 planted driver — RELATED, lag 2 recovered, sign +",
          ok1, f"{r1['verdict']} corr {r1['corr']} shift "
               f"{r1['shift']} leader {r1['leader']} "
               f"(null {r1['receipts']['null']})")

    # R2 — the spurious trap: independent random walks
    wa = np.cumsum(rng.normal(0.5, 1, n))
    wb = np.cumsum(rng.normal(0.5, 1, n))
    r2 = m.relate_series(tt, wa, tt, wb)
    ok2 = (abs(r2.get("levels", 0)) > 0.7
           and r2["verdict"] == "NO RELATION SAID")
    check("R2 spurious trap — levels co-move (reported), verdict "
          "refuses", ok2,
          f"levels {r2.get('levels')} but {r2['verdict']} "
          f"(diff corr {r2.get('corr')} vs null "
          f"{r2['receipts'].get('null')})")

    # R3 — scrambled alignment kills the planted relation
    ys = yb.copy()
    rng.shuffle(ys)
    r3 = m.relate_series(tt, ya, tt, ys)
    ok3 = r3["verdict"] == "NO RELATION SAID"
    check("R3 the null — shuffled alignment says nothing", ok3,
          f"{r3['verdict']} (corr {r3.get('corr')} vs null "
          f"{r3['receipts'].get('null')})")

    # R4 — anti-aligned driver: RELATED, negative
    yc = 0.2 * tt - 4.5 * z[2:] + rng.normal(0, 0.4, n)
    r4 = m.relate_series(tt, ya, tt, yc)
    ok4 = r4["verdict"] == "RELATED" and r4["corr"] < -0.5
    check("R4 sign — anti-aligned driver RELATED, negative", ok4,
          f"{r4['verdict']} corr {r4['corr']}")

    # R5 — the real pair: annual CO2 growth vs GISTEMP anomaly
    rows = [ln.split() for ln in open(
        os.path.join(FEEDS, "co2_annmean_mlo.txt"), encoding="utf-8")
        if ln.strip() and not ln.startswith("#")]
    yr_c = np.array([float(r[0]) for r in rows])
    co2 = np.array([float(r[1]) for r in rows])
    dgrow = np.diff(co2)                     # the carbon breathing
    yr_g, temp = [], []
    for ln in open(os.path.join(FEEDS, "gistemp_glb.csv"),
                   encoding="utf-8"):
        p = ln.strip().split(",")
        if p and p[0].isdigit():
            v = p[13]                        # J-D annual mean
            if v not in ("***", ""):
                yr_g.append(float(p[0]))
                temp.append(float(v))
    yr_g = np.array(yr_g)
    temp = np.array(temp)
    m5 = Isaac()
    r5 = m5.relate_series(yr_c[1:], dgrow, yr_g, temp,
                          name="co2growth-temp",
                          containers=["data-co2-annual",
                                      "data-gistemp"])
    ok5 = r5["verdict"] == "RELATED" and r5["corr"] > 0.3
    check("R5 the real pair — CO2 growth ~ temperature RELATED, "
          "sign +", ok5,
          f"{r5['verdict']} corr {r5.get('corr')} shift "
          f"{r5.get('shift')} leader {r5.get('leader')} n {r5.get('n')} "
          f"(null {r5['receipts'].get('null')})")

    # R6 — the relation node wears both worlds
    tags_a = m5.net.get_door_tags("world:data-co2-annual",
                                  "relation:co2growth-temp")
    tags_b = m5.net.get_door_tags("world:data-gistemp",
                                  "relation:co2growth-temp")
    meta = m5.net.get_meta("relation:co2growth-temp", "relation")
    ok6 = (bool(tags_a) and bool(tags_b) and meta is not None
           and meta.get("null") is not None)
    check("R6 the relation node — doored to both worlds, receipts "
          "kept", ok6,
          f"tags {sorted(tags_a)}/{sorted(tags_b)}; meta keys "
          f"{sorted(meta) if meta else None}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
