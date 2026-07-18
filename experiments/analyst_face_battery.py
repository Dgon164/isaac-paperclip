"""analyst_face_battery.py — PROMOTION GATE for THE ANALYST FACE
(A4, the segment's close; owner 2026-07-18: "lets give him a full
data analyst capability").

One command orchestrating the promoted organs: describe + trend +
cycle + anomalies + relations + forecast + the watch, plain language
with receipts. Every section is an engine organ already behind the
wall; the face may only assemble, never judge.

  F1 THE FULL REPORT: a synthetic table (time, trending-seasonal x,
     related y, noise z) — three series analyzed, x's period 12
     found, forecast present, watch baselines established.
  F2 RELATIONS THROUGH THE FACE: x ~ y RELATED; z's pairs refused
     (counted, receipted).
  F3 ANOMALIES: two planted spikes flagged with their times, the
     flagged-never-judged receipt attached.
  F4 NO TIME KEY: a keyless table refuses the series roads WITH the
     receipt and still describes itself.
  F5 THE RENDER: plain-language text carries the load-bearing
     receipts (books balance line, levels-never-judged, the watch).
  F6 THE REAL REPORT: monthly CO2 through the face — 12-month cycle,
     rising forecast, honest accounting.
  F7 THE DOOR ITSELF: askisaac.py --analyst runs end to end.

Run: cd experiments && PYTHONHASHSEED=0 python analyst_face_battery.py
"""
import os
import subprocess
import sys
import tempfile
import time

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from isaac_store.analyst import analyst_source, render_analyst  # noqa: E402

FEEDS = os.path.join(ROOT, "data", "feeds")


def synth_csv(path):
    rng = np.random.default_rng(0)
    n = 240
    t = np.arange(n, dtype=float)
    saw = np.array([3.0, 1.5, 0.5, -0.5, -1.5, -3.0, -2.0, -1.0,
                    0.0, 1.0, 2.0, 0.0])
    x = 0.5 * t + 10.0 + saw[t.astype(int) % 12] \
        + rng.normal(0, 0.3, n)
    x[60] += 12.0
    x[180] -= 12.0                          # two planted anomalies
    y = 0.7 * x + 5.0 + rng.normal(0, 0.4, n)
    z = rng.normal(0, 1.0, n)
    with open(path, "w", encoding="utf-8") as f:
        f.write("t,x,y,z\n")
        for k in range(n):
            f.write(f"{t[k]},{x[k]:.4f},{y[k]:.4f},{z[k]:.4f}\n")


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    td = tempfile.mkdtemp()
    csv = os.path.join(td, "world.csv")
    synth_csv(csv)
    rep = analyst_source(csv)
    tb = rep["tables"][0]
    sx = next(s for s in tb["series"] if s["column"] == "x")

    # F1 — the full report
    ok1 = (len(tb["series"]) == 3
           and tb["time"]["column"] == "t"
           and sx["period"] is not None
           and abs(sx["period"] - 12.0) < 0.5
           and sx.get("forecast") is not None
           and all(s.get("watch", {}).get("verdict") == "BASELINE"
                   for s in tb["series"]))
    check("F1 the full report — 3 series, x's period 12, forecast, "
          "watch baselines", ok1,
          f"time {tb['time']['column']}; x period {sx['period']}; "
          f"accounting {sx['accounting']}")

    # F2 — relations through the face
    pairs = [r["pair"] for r in tb["relations"]]
    ok2 = ("x ~ y" in pairs and tb["refused_pairs"] == 2)
    check("F2 relations — x~y RELATED, z's pairs refused", ok2,
          f"related {pairs}; refused {tb['refused_pairs']}")

    # F3 — anomalies flagged with times
    an = sx.get("anomalies", [])
    times = sorted(a["t"] for a in an)
    ok3 = (len(an) >= 2 and 60.0 in times and 180.0 in times
           and "never judged" in sx.get("anomaly_receipt", ""))
    check("F3 anomalies — both planted spikes flagged, receipt "
          "attached", ok3, f"flagged at {times}")

    # F4 — no time key refuses honestly
    csv2 = os.path.join(td, "keyless.csv")
    rng = np.random.default_rng(3)
    with open(csv2, "w", encoding="utf-8") as f:
        f.write("a,b\n")
        for _ in range(50):
            f.write(f"{rng.normal():.4f},{rng.normal():.4f}\n")
    rep2 = analyst_source(csv2)
    tb2 = rep2["tables"][0]
    ok4 = (tb2["time"]["column"] is None
           and "refused" in tb2.get("receipt", "")
           and len(tb2["describe"]) == 2)
    check("F4 no time key — series roads refused with the receipt, "
          "describe stands", ok4, f"{tb2['time']['why']}")

    # F5 — the render carries the receipts
    txt = render_analyst(rep)
    ok5 = ("= 100" in txt and "never judged" in txt
           and "arriving data will be judged" in txt
           and "RELATED" in txt)
    check("F5 the render — books, levels receipt, watch, relations "
          "all present", ok5, f"{len(txt.splitlines())} lines")

    # F6 — the real report: monthly CO2
    rows = [ln.split() for ln in open(
        os.path.join(FEEDS, "co2_mm_mlo.txt"), encoding="utf-8")
        if ln.strip() and not ln.startswith("#")]
    csv3 = os.path.join(td, "co2.csv")
    with open(csv3, "w", encoding="utf-8") as f:
        f.write("date,co2\n")
        for r in rows:
            if float(r[3]) > 0:
                f.write(f"{r[2]},{r[3]}\n")
    rep3 = analyst_source(csv3)
    s3 = rep3["tables"][0]["series"][0]
    ok6 = (s3["period"] is not None
           and abs(s3["period"] - 1.0) < 0.05
           and s3["forecast"]["hi"] > s3["forecast"]["last_seen"] - 1
           and s3["accounting"]["trend"] > 95.0)
    check("F6 the real report — CO2 through the face: yearly cycle, "
          "rising forecast", ok6,
          f"period {s3['period']} yr; forecast "
          f"{s3['forecast']['lo']}..{s3['forecast']['hi']}; "
          f"accounting {s3['accounting']}")

    # F7 — the door itself
    r = subprocess.run([sys.executable,
                        os.path.join(ROOT, "askisaac.py"),
                        csv, "--analyst"],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONUTF8="1"),
                       timeout=600)
    ok7 = (r.returncode == 0
           and "THE ANALYST'S REPORT" in (r.stdout or ""))
    check("F7 the door — askisaac --analyst runs end to end", ok7,
          f"exit {r.returncode}, {len((r.stdout or '').splitlines())} "
          f"lines")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
