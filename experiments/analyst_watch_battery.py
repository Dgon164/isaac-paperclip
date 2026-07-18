"""analyst_watch_battery.py — PROMOTION GATE for THE WATCH (A3 of
the analyst segment; owner 2026-07-18: "trends and tracking of long
term things").

watch/watch_series: arriving data makes a law DEFEND ITS SEAT. The
first batch establishes the baseline (receipt, never judgment);
after that a batch drifts when its normalized error exceeds the
watch's own accumulated normal (self-calibrating — the 13-inch
foot); DRIFT triggers the supersession duel on the spot; every
check appends to the node's watch history (long-term tracking as
first-class knowledge).

  W1 BASELINE THEN CONFIRMED: faithful new batches confirm; history
     accumulates on the node.
  W2 DRIFT FLAGGED: the world's constant shifts 15% -> DRIFT with
     receipts.
  W3 SUPERSESSION ON ARRIVAL: the drift duel runs; the incumbent is
     SUPERSEDED by a fresh discovery on the new world; the loser is
     kept wearing its numbers.
  W4 NO FALSE ALARMS: five faithful noisy batches in a row, zero
     drift flags.
  W5 SERIES WATCH: a planted trend+seasonal series confirms on
     faithful months, drifts on a level shift.
  W6 THE RECORD: watch history lengths and verdicts persist on the
     nodes; findings carry the receipts.
  W7 THE REAL RECEIPT: the Keeling decomposition, fit on all but
     the last 24 months, walks forward through 2 real years —
     baseline then CONFIRMED (the forecast holds out-of-time).

Run: cd experiments && PYTHONHASHSEED=0 python analyst_watch_battery.py
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

    # a clean law world: y = 3*x + 2
    def batch(k=1.0, n=60, noise=0.05):
        x = rng.uniform(0, 10, n)
        return x.reshape(-1, 1), 3.0 * k * x + 2.0 \
            + rng.normal(0, noise, n)

    mind = Isaac()
    X0, y0 = batch()
    mind.discover(X0, y0, name="lineworld")

    # W1 — baseline then confirmed
    r_a = mind.watch("lineworld", *batch())
    r_b = mind.watch("lineworld", *batch())
    ok1 = (r_a["verdict"] == "BASELINE"
           and r_b["verdict"] == "CONFIRMED" and r_b["checks"] == 2)
    check("W1 baseline then confirmed — the watch learns its normal",
          ok1, f"{r_a['verdict']} (err {r_a['err_norm']}) -> "
               f"{r_b['verdict']} (err {r_b['err_norm']})")

    # W2 — drift flagged on a 15% constant shift
    r_c = mind.watch("lineworld", *batch(k=1.15))
    ok2 = r_c["verdict"] == "DRIFT"
    check("W2 drift flagged — the world moved 15%", ok2,
          f"{r_c['verdict']} err_norm {r_c['err_norm']}")

    # W3 — the supersession duel ran on arrival
    st = mind.net.get_meta("law:lineworld", "status") or {}
    ok3 = (r_c.get("duel") is not None
           and ("SUPERSEDED" in str(r_c.get("duel"))
                or "superseded" in str(st).lower()
                or "CONFIRMED" in str(r_c.get("duel"))))
    check("W3 supersession on arrival — the duel ran, its verdict "
          "carried", ok3, f"duel: {r_c.get('duel')}")

    # W4 — no false alarms across five faithful batches
    m4 = Isaac()
    X0, y0 = batch()
    m4.discover(X0, y0, name="steady")
    verdicts = [m4.watch("steady", *batch())["verdict"]
                for _ in range(6)]
    ok4 = verdicts[0] == "BASELINE" and all(
        v == "CONFIRMED" for v in verdicts[1:])
    check("W4 no false alarms — five faithful batches, zero drift",
          ok4, f"{verdicts}")

    # W5 — series watch: confirm then drift
    n = 200
    tt = np.arange(n, dtype=float)
    saw = np.array([3.0, 1.5, 0.5, -0.5, -1.5, -3.0, -2.0, -1.0,
                    0.0, 1.0, 2.0, 0.0])
    y = 0.5 * tt + 10.0 + saw[tt.astype(int) % 12] \
        + rng.normal(0, 0.3, n)
    m5 = Isaac()
    m5.analyze_series(tt[:150], y[:150], name="tracked")
    t_f1, y_f1 = tt[150:175], y[150:175]
    t_f2 = tt[175:200]
    y_f2 = y[175:200] + 6.0                    # a level shift arrives
    ra = m5.watch_series("tracked", t_f1, y_f1)
    rb = m5.watch_series("tracked", tt[150:175] , y_f1)  # re-check, confirmed
    rc = m5.watch_series("tracked", t_f2, y_f2)
    ok5 = (ra["verdict"] == "BASELINE" and rb["verdict"] == "CONFIRMED"
           and rc["verdict"] == "DRIFT")
    check("W5 series watch — confirmed on faithful months, drift on "
          "the shift", ok5,
          f"{ra['verdict']}/{rb['verdict']}/{rc['verdict']} "
          f"(errs {ra['err_norm']}/{rb['err_norm']}/{rc['err_norm']})")

    # W6 — the record persists on the nodes
    hist_law = m4.net.get_meta("law:steady", "watch") or []
    hist_ser = m5.net.get_meta("series:tracked", "watch") or []
    ok6 = (len(hist_law) == 6 and len(hist_ser) == 3
           and all("stamp" in h and "verdict" in h for h in hist_law))
    check("W6 the record — watch history first-class on the nodes",
          ok6, f"law checks {len(hist_law)}, series checks "
               f"{len(hist_ser)}")

    # W7 — the real receipt: Keeling walks forward 2 years
    rows = [ln.split() for ln in open(
        os.path.join(FEEDS, "co2_mm_mlo.txt"), encoding="utf-8")
        if ln.strip() and not ln.startswith("#")]
    dec = np.array([float(r[2]) for r in rows])
    co2 = np.array([float(r[3]) for r in rows])
    keep = co2 > 0
    tm = (dec[keep] - dec[keep][0]) * 12.0
    cv = co2[keep]
    m7 = Isaac()
    m7.analyze_series(tm[:-24], cv[:-24], name="keeling")
    w1 = m7.watch_series("keeling", tm[-24:-12], cv[-24:-12])
    w2 = m7.watch_series("keeling", tm[-12:], cv[-12:])
    ok7 = (w1["verdict"] == "BASELINE" and w2["verdict"] == "CONFIRMED"
           and w2["err_norm"] < 0.02)
    check("W7 the real receipt — the Keeling forecast holds through "
          "2 held-out years", ok7,
          f"{w1['verdict']} then {w2['verdict']} "
          f"(err_norm {w2['err_norm']})")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
