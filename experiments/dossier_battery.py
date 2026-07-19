"""dossier_battery.py — PROMOTION GATE for THE SPECIFICS LAYER
(owner, 2026-07-18 evening: "having the law is great, but sometimes
you need to reference a specific sample... averages, extremes,
ratios, sigfigs, std dev, median and mode... as well as time
frames. avg per day, avg per month, avg per year, track trend
lines. plot data points, error bars").

THE DESIGN SENTENCE UNDER TEST: THE DOSSIER DESCRIBES, THE COURT
JUDGES. Pins:

  D1  STATS EXACTNESS: mean/median/std(n-1) match hand arithmetic
      exactly; extremes carry their FULL ROWS (specific samples).
  D2  MODE HONESTY: all-distinct REFUSES ("no recurring value");
      a tie lists the tied values, never picks one silently.
  D3  RESOLUTION: a 0.25-grid column reads grain 0.25 with its
      decimals; float-continuous reads none WITH the why.
  D4  THE CALENDAR ROAD: date columns are PARSED, never dropped —
      ISO round-trips exactly through fy; a 13 in the first slot
      flips the whole column day-first (evidence, not guess).
  D5  FRAMES: yearly/monthly averages exact by hand (leap year
      included); a frame at the data's own grain is SKIPPED with
      the identity receipt, never echoed back as insight.
  D6  THE DESCRIBED SLOPE: matches hand least squares and wears
      "described, not judged".
  D7  RATIOS SIGN-SAFE: constant-sign denominator exact; a
      zero-crossing denominator is REFUSED with the why.
  D8  PERSISTENCE + DETERMINISM: the dossier survives save/load
      via recall_dossier; a second take APPENDS history (the line
      is tracked); same table twice -> identical description.
  D9  THE PLOT FACE: the SVG holds every point, the error bars,
      the trend, the frame steps, the anomaly rings — and the same
      inputs write the same bytes.
  D10 THE FACE END-TO-END: askisaac's analyst road renders the
      dossier for a dated CSV AND for an untimed table (stats
      stand, frames refuse with the receipt).
  D11 THE SMALL-TABLE REFUSAL: fewer than 3 usable rows refuses.
  D12 YEAR-VALUED TIME: decimal-year columns (the house unit)
      derive their calendar; a bare 1..8 time column does NOT.

Run: cd experiments && PYTHONHASHSEED=0 python dossier_battery.py
"""
import io
import os
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
import isaac as isaac_mod                       # noqa: E402
from isaac_store import intake                  # noqa: E402
from isaac_store.plot import plot_series        # noqa: E402
from isaac_store.analyst import (analyst_source,  # noqa: E402
                                 render_analyst)

Isaac = isaac_mod.Isaac


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(bool(ok))
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    # ── D1 stats exactness on a hand table ──
    cols = ["t", "a", "b"]
    rows = [[1.0, 2.0, 10.0], [2.0, 4.0, 20.0], [3.0, 4.0, 30.0],
            [4.0, 6.0, 40.0], [5.0, 9.0, 50.0]]
    m = Isaac()
    dz = m.take_dossier(cols, rows, "hand", time_index=0)
    a = dz["stats"]["a"]
    ok = (a["n"] == 5 and abs(a["mean"] - 5.0) < 1e-12
          and abs(a["median"] - 4.0) < 1e-12
          and abs(a["std"]["value"] - np.std(
              [2, 4, 4, 6, 9], ddof=1)) < 1e-12
          and a["lo"]["value"] == 2.0 and a["hi"]["value"] == 9.0
          and a["hi"]["row"] == dict(t=5.0, a=9.0, b=50.0))
    check("D1 stats exactness + extreme rows kept", ok,
          f"mean {a['mean']}, median {a['median']}, "
          f"std {a['std']['value']:.4f}, hi row t={a['hi']['row']['t']}")

    # ── D2 mode honesty ──
    mode_a = a["mode"]          # 4.0 twice
    b = dz["stats"]["b"]        # all distinct
    m2 = Isaac()
    dz2 = m2.take_dossier(["x", "y"], [[1, 1], [1, 2], [2, 2],
                                       [2, 3], [3, 9]], "ties")
    tie = dz2["stats"]["x"]["mode"]
    ok = (mode_a["value"] == 4.0 and mode_a["count"] == 2
          and b["mode"]["value"] is None
          and "no recurring" in b["mode"]["why"]
          and tie["n_tied"] == 2 and tie["ties"] is not None)
    check("D2 mode honesty — refusal on all-distinct, ties listed",
          ok, f"a mode {mode_a['value']} x{mode_a['count']}; "
              f"b {b['mode']['why'][:24]}; ties {tie['ties']}")

    # ── D3 resolution via the grain court ──
    rng = np.random.default_rng(7)
    grid = np.round(rng.uniform(0, 10, 60) / 0.25) * 0.25
    cont = rng.normal(0, 1, 60)
    m3 = Isaac()
    dz3 = m3.take_dossier(["g", "c"],
                          np.column_stack([grid, cont]).tolist(),
                          "grain")
    rg, rc = dz3["stats"]["g"]["resolution"], \
        dz3["stats"]["c"]["resolution"]
    ok = (rg["step"] is not None and abs(rg["step"] - 0.25) < 1e-9
          and rg["decimals"] == 2 and rc["step"] is None
          and rc["why"])
    check("D3 resolution — 0.25 grid read, continuous refused", ok,
          f"grid step {rg['step']} (decimals {rg['decimals']}); "
          f"continuous: {rc['why'][:34]}")

    # ── D4 the calendar road at intake ──
    iso = "date,v\n" + "\n".join(
        f"2024-0{mm}-{dd:02d},{mm * 10 + dd}"
        for mm in (1, 2, 3) for dd in (5, 15, 25))
    got = intake.ingest(iso)
    it = got["items"][0]
    ok_iso = (it.get("calendar") is not None
              and it["calendar"]["column"] == "date"
              and "ISO" in it["calendar"]["format"]
              and "date" not in it["dropped_columns"]
              and all(Isaac._fy_to_ymd(r[0]) == tuple(g)
                      for r, g in zip(it["rows"], it["ymd"])))
    dm = "d,v\n01/02/2024,1\n13/02/2024,2\n25/02/2024,3\n"
    it2 = intake.ingest(dm)["items"][0]
    ok_dm = (it2.get("ymd") and tuple(it2["ymd"][0]) == (2024, 2, 1)
             and "D/M" in it2["calendar"]["format"])
    check("D4 calendar road — ISO round-trips, 13 flips day-first",
          ok_iso and ok_dm,
          f"iso fmt '{it['calendar']['format']}', "
          f"dm first {it2['ymd'][0]}")

    # ── D5/D6 frames + the described slope (leap year inside) ──
    import datetime as dt
    d0 = dt.date(2023, 11, 25)
    days = [(d0 + dt.timedelta(days=k)) for k in range(102)]
    # crosses 2024-02-29; value = day index (hand-averagable)
    csv = "date,v\n" + "\n".join(
        f"{d.isoformat()},{float(k)}" for k, d in enumerate(days))
    it5 = intake.ingest(csv)["items"][0]
    m5 = Isaac()
    dz5 = m5.take_dossier(it5["columns"], it5["rows"], "frames",
                          time_index=0, ymd=it5["ymd"])
    fr = {f["level"]: f for f in dz5["frames"]}
    feb = [bk for bk in fr["month"]["buckets"]
           if bk["bucket"] == "2024-02"][0]
    k_feb = [k for k, d in enumerate(days)
             if (d.year, d.month) == (2024, 2)]
    ok5 = (feb["n"] == 29
           and abs(feb["cols"]["v"]["avg"] - np.mean(k_feb)) < 1e-9
           and fr["day"].get("skipped")
           and "grain" in fr["day"]["skipped"]
           and fr["year"]["n_buckets"] == 2)
    check("D5 frames — Feb-2024 has its 29 days, hand-exact avg; "
          "daily identity skipped", ok5,
          f"feb n {feb['n']} avg {feb['cols']['v']['avg']:.3f} "
          f"(hand {np.mean(k_feb):.3f})")
    mo = fr["month"]
    bt = np.array([bk["t"] for bk in mo["buckets"]])
    bv = np.array([bk["cols"]["v"]["avg"] for bk in mo["buckets"]])
    hand = float(np.polyfit(bt, bv, 1)[0])
    sl = mo["slopes"]["v"]
    ok6 = (abs(sl["per_year"] - hand) < 1e-9
           and "described, not judged" in sl["why"])
    check("D6 described slope — hand least squares, labeled", ok6,
          f"slope {sl['per_year']:.2f}/yr (hand {hand:.2f})")

    # ── D7 ratios sign-safe ──
    m7 = Isaac()
    dz7 = m7.take_dossier(
        ["p", "q", "z"],
        [[2.0, 4.0, -1.0], [4.0, 8.0, 0.5], [6.0, 12.0, 2.0]],
        "ratios")
    r = {x["pair"]: x for x in dz7["ratios"] if x.get("pair")}
    ok = (abs(r["p/q"]["mean"] - 0.5) < 1e-12
          and "refused" in r["p/z"] and "refused" in r["q/z"])
    check("D7 ratios — p/q exact 0.5, zero-crossing z refused", ok,
          f"p/q {r['p/q']['mean']}, p/z: {r['p/z']['refused'][:28]}")

    # ── D8 persistence + history + determinism ──
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "m.isaac")
        m8 = Isaac()
        m8.take_dossier(cols, rows, "hand", time_index=0)
        m8.take_dossier(cols, rows, "hand", time_index=0)
        m8.save(p)
        back = Isaac.load(p).recall_dossier("hand")
        ma, mb = Isaac(), Isaac()
        da = ma.take_dossier(cols, rows, "hand", time_index=0)
        db = mb.take_dossier(cols, rows, "hand", time_index=0)
        same = all(repr(da[k]) == repr(db[k])
                   for k in ("stats", "examples", "frames",
                             "ratios"))
        ok = (back is not None and len(back["history"]) == 2
              and back["history"][1]["take"] == 2
              and back["stats"]["a"]["mean"] == 5.0 and same)
    check("D8 persistence — survives save/load, history tracks the "
          "line, deterministic", ok,
          f"takes {[h['take'] for h in back['history']]}, "
          f"deterministic {same}")

    # ── D9 the plot face ──
    with tempfile.TemporaryDirectory() as td:
        t = list(range(10))
        y = [float(v) for v in t]
        pth = os.path.join(td, "p.svg")
        plot_series(pth, t, y, err=0.5, err_why="test",
                    trend=[v + 0.1 for v in y],
                    steps=[(2, 2.0), (7, 7.0)], anomalies=[3])
        svg = open(pth, encoding="utf-8").read()
        plot_series(os.path.join(td, "p2.svg"), t, y, err=0.5,
                    err_why="test", trend=[v + 0.1 for v in y],
                    steps=[(2, 2.0), (7, 7.0)], anomalies=[3])
        svg2 = open(os.path.join(td, "p2.svg"),
                    encoding="utf-8").read()
        ok = (svg.count('class="pt"') == 10
              and svg.count('class="errbar"') == 10
              and svg.count('class="trend"') == 1
              and svg.count('class="steps"') == 1
              and svg.count('class="anomaly"') == 1
              and svg == svg2)
    check("D9 plot face — 10 points, 10 bars, trend, steps, ring, "
          "deterministic bytes", ok,
          f"{svg.count(chr(34) + 'pt' + chr(34))} pt marks? "
          f"pts {svg.count('class=' + chr(34) + 'pt' + chr(34))}")

    # ── D10 the face end-to-end (dated + untimed) ──
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "keel.csv")
        with open(fp, "w", encoding="utf-8") as f:
            f.write(csv)  # the D5 dated table
        rep = analyst_source(fp, plots=os.path.join(td, "plots"))
        tb = rep["tables"][0]
        txt = render_analyst(rep)
        ok10a = (tb.get("dossier") and not tb["dossier"].get(
            "refused") and "the dossier" in txt
            and tb.get("plots") and os.path.exists(tb["plots"][0]))
        fp2 = os.path.join(td, "flat.csv")
        with open(fp2, "w", encoding="utf-8") as f:
            f.write("x,y\n" + "\n".join(
                f"{v},{w}" for v, w in zip(
                    np.r_[3, 1, 2, 5, 4], np.r_[9, 2, 6, 1, 4])))
        rep2 = analyst_source(fp2)
        dz10 = rep2["tables"][0]["dossier"]
        ok10b = (isinstance(dz10["frames"], dict)
                 and "refused" in dz10["frames"]
                 and dz10["stats"]["y"]["mean"] == 4.4)
        check("D10 the face — dated table renders dossier + plot; "
              "untimed keeps stats, refuses frames",
              ok10a and ok10b,
              f"plot {os.path.basename(tb['plots'][0]) if tb.get('plots') else 'NONE'}; "
              f"untimed frames: {str(dz10['frames'])[:36]}")

    # ── D11 the small-table refusal ──
    dz11 = Isaac().take_dossier(["a", "b"], [[1, 2], [3, 4]], "tiny")
    check("D11 small-table refusal", "refused" in dz11,
          dz11.get("refused", "NO REFUSAL"))

    # ── D12 year-valued time derives calendar; bare 1..8 does not ──
    fy = [2000 + (i + 0.5) / 12.0 for i in range(48)]
    m12 = Isaac()
    dz12 = m12.take_dossier(
        ["t", "v"], [[t_, float(i)] for i, t_ in enumerate(fy)],
        "decimalyears", time_index=0)
    fr12 = {f["level"]: f for f in dz12["frames"]}
    yr = fr12["year"]
    ok12a = (yr.get("buckets") and yr["n_buckets"] == 4
             and abs(yr["buckets"][0]["cols"]["v"]["avg"] - 5.5)
             < 1e-9)
    dz12b = Isaac().take_dossier(
        ["t", "v"], [[float(i + 1), float(i * i)] for i in range(8)],
        "galileo-like", time_index=0)
    ok12b = (isinstance(dz12b["frames"], dict)
             and "refused" in dz12b["frames"])
    check("D12 year-valued time — decimal years aggregate yearly; "
          "bare 1..8 refuses frames", ok12a and ok12b,
          f"yr buckets {yr.get('n_buckets')}, first avg "
          f"{yr['buckets'][0]['cols']['v']['avg']:.2f} (hand 5.50)")

    # ── D13 the newest-first file (review pin): reordered + said ──
    rev_csv = "date,v\n" + "\n".join(
        f"{d.isoformat()},{float(k)}"
        for k, d in sorted(enumerate(days), key=lambda kd: -kd[0]))
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "rev.csv")
        open(fp, "w", encoding="utf-8").write(rev_csv)
        tb = analyst_source(fp)["tables"][0]
        fc = tb["series"][0].get("forecast") if tb["series"] else None
        ok = ("reordered into time order" in tb["time"]["why"]
              and fc is not None and fc["last_seen"] == 101.0
              and fc["lo"] > 95.0)
    check("D13 newest-first file — rows reordered WITH receipt, "
          "forecast walks forward", ok,
          f"why '...{tb['time']['why'][-46:]}', forecast lo "
          f"{fc['lo'] if fc else 'NONE'}")

    # ── D14 the id-column trap (review pin): told calendar wins ──
    id_csv = "id,date,v\n" + "\n".join(
        f"{k + 1},{d.isoformat()},{float(k)}"
        for k, d in enumerate(days))
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "idd.csv")
        open(fp, "w", encoding="utf-8").write(id_csv)
        tb = analyst_source(fp)["tables"][0]
        dzf = {f["level"]: f for f in tb["dossier"]["frames"]}
        sl = dzf["month"]["slopes"]["v"]["per_year"]
        ok = (tb["time"]["column"] == "date"
              and "told by intake" in tb["time"]["why"]
              and abs(sl - 365.0) < 30.0)
    check("D14 id-column trap — declared calendar beats the scan; "
          "per_year is per YEAR", ok,
          f"time '{tb['time']['column']}', month slope {sl:.1f}/yr "
          f"(true ~365.25)")

    # ── D15 the sentinel date (review pin): garbage cannot vote ──
    sent = ("d,v\n" + "\n".join(
        f"{mm}/5/2024,{mm}" for mm in range(1, 11))
        + "\n99/99/2024,99\n")
    it15 = intake.ingest(sent)["items"][0]
    ok = (it15.get("ymd") and tuple(it15["ymd"][0]) == (2024, 1, 5)
          and "M/D" in it15["calendar"]["format"]
          and len(it15["rows"]) == 10)
    check("D15 sentinel 99/99 — dropped, never voting day-first",
          ok, f"first {it15['ymd'][0]}, fmt "
              f"'{it15['calendar']['format']}', rows "
              f"{len(it15['rows'])}")

    # ── D16 refusals + identity (review pins) ──
    m16 = Isaac()
    r_t = m16.take_dossier(["t", "a"], rows_ta := [[1.0, 2.0],
                           [2.0, 3.0], [3.0, 4.0]], "x",
                           time_index=0, target="t")
    r_only = Isaac().take_dossier(["t"], [[1.0], [2.0], [3.0]],
                                  "y", time_index=0)
    m16b = Isaac()
    for _k in range(43):
        m16b.take_dossier(["a", "b"], rows, "many")
    h = m16b.recall_dossier("many")["history"]
    m16c = Isaac()
    m16c.take_dossier(["a", "b"], [[1, 2], [3, 4], [5, 6]], "pv",
                      provenance=dict(sha="abc"))
    m16c.take_dossier(["a", "b"], [[1, 2], [3, 4], [5, 6]], "pv")
    ok = ("refused" in r_t and "refused" in r_only
          and h[-1]["take"] == 43 and len(h) == 40
          and m16c.recall_dossier("pv").get("provenance") is None)
    check("D16 loud refusals (target=time, time-only) + takes stay "
          "monotonic past the cap + stale provenance cleared", ok,
          f"takes tail {h[-1]['take']}, hist {len(h)}")

    # ── D17 untimed render + hostile column names (review pins) ──
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "hostile.csv")
        open(fp, "w", encoding="utf-8").write(
            "date,a/b:c\n" + "\n".join(
                f"{d.isoformat()},{float(k)}"
                for k, d in enumerate(days[:20])))
        rep = analyst_source(fp, plots=os.path.join(td, "p"))
        tb = rep["tables"][0]
        okp = (tb.get("plots")
               and os.path.exists(tb["plots"][0])
               and ":" not in os.path.basename(tb["plots"][0]))
        fp2 = os.path.join(td, "flat2.csv")
        open(fp2, "w", encoding="utf-8").write(
            "x,y\n3,9\n1,2\n2,6\n5,1\n4,4")
        txt2 = render_analyst(analyst_source(fp2))
        ok = okp and "the dossier" in txt2
    check("D17 hostile header plotted safely + untimed report "
          "RENDERS its dossier", ok,
          f"plot {os.path.basename(tb['plots'][0]) if tb.get('plots') else 'NONE'}")

    # ── D18 no phantom trend (review pin) + escaped title ──
    with tempfile.TemporaryDirectory() as td:
        rng18 = np.random.default_rng(3)
        fp = os.path.join(td, "noise.csv")
        open(fp, "w", encoding="utf-8").write(
            "date,n\n" + "\n".join(
                f"{d.isoformat()},{rng18.normal():.6f}"
                for d in days[:40]))
        tb = analyst_source(fp, plots=os.path.join(td, "p")
                            )["tables"][0]
        verdict = tb["series"][0]["trend_verdict"]
        svg18 = (open(tb["plots"][0], encoding="utf-8").read()
                 if tb.get("plots") else "")
        no_phantom = (verdict in ("UNDERSTOOD", "PARTIAL")
                      or 'class="trend"' not in svg18)
        pth = os.path.join(td, "esc.svg")
        plot_series(pth, [1, 2, 3], [1, 2, 3], title="a & b < c")
        esc_ok = "a &amp; b &lt; c" in open(pth,
                                            encoding="utf-8").read()
    check("D18 no phantom trend when the court refused + XML-safe "
          "titles", no_phantom and esc_ok,
          f"verdict {verdict}, trend drawn "
          f"{'yes' if 'class=' + chr(34) + 'trend' + chr(34) in svg18 else 'no'}")

    dt_ = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} "
          f"failed of {len(checks)}  ({dt_:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
