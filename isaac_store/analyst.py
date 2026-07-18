"""analyst.py — THE ANALYST FACE (A4, the segment's close; owner
2026-07-18: "seeing a trend line for a market statistic is fine, but
thats just one job that a data analyst would do. lets give him a
full data analyst capability").

One door in, the full report out — every section an ENGINE organ the
wall already guards, plain language on top, receipts underneath:

  DESCRIBE   shape, ranges, the detected time key (receipted)
  TREND      analyze_series per column: trend law (changepoints
             free), period past the null, learned profile, complete
             accounting (trend+seasonal+residual=100)
  ANOMALIES  residuals beyond 4x their own rms — FLAGGED with their
             times, never judged (the audit face owns deep cleaning)
  RELATIONS  relate_series per pair: levels reported-never-judged,
             differenced correlation vs the alignment null, lead/lag
  FORECAST   apply_series, 12 steps beyond the data's end
  THE WATCH  baselines established — arriving data will be JUDGED

No time key = the series roads refuse with a receipt (the law road
and the audit face still stand for such tables).
"""
import numpy as np

from . import bridge
from .intake import ingest


def _detect_time(cols, R, time_col=None):
    if time_col and time_col in cols:
        return cols.index(time_col), "told"
    for i, c in enumerate(cols):
        v = R[:, i]
        if np.all(np.isfinite(v)) and len(v) > 2 \
                and np.all(np.diff(v) > 0):
            return i, f"auto: '{c}' strictly increases"
    return None, "no strictly-increasing column found"


def _analyze_table(mind, item, time_col):
    cols = item["columns"]
    R = np.asarray(item["rows"], float)
    good = np.isfinite(R).all(1)
    R = R[good]
    ti, time_why = _detect_time(cols, R, time_col)
    table = dict(name=item.get("name", "table"), n=int(len(R)),
                 columns=list(cols), time=dict(column=(
                     cols[ti] if ti is not None else None),
                     why=time_why),
                 series=[], relations=[], refused_pairs=0)
    table["describe"] = [
        dict(column=c, lo=round(float(R[:, i].min()), 6),
             hi=round(float(R[:, i].max()), 6))
        for i, c in enumerate(cols)]
    if ti is None:
        table["receipt"] = ("series roads refused: " + time_why
                            + " — the law road (askisaac plain) and "
                              "the audit face still apply")
        return table
    t = R[:, ti]
    step = float(np.median(np.diff(t))) or 1.0
    vals = [(i, c) for i, c in enumerate(cols) if i != ti]
    for i, c in vals:
        y = R[:, i]
        r = mind.analyze_series(t, y, name=c)
        s = dict(column=c, trend_verdict=r["trend_verdict"],
                 trend=r.get("trend_equation"),
                 period=r.get("period"),
                 profile_swing=(round(float(np.ptp(r["profile"])), 4)
                                if r.get("profile") else None),
                 accounting=r["accounting"],
                 receipts=r["receipts"]["bypassed"])
        pred = mind.apply_series(c, t)
        if pred is not None:
            resid = y - pred
            rms = float(np.sqrt(np.mean(resid ** 2))) or 1e-12
            flags = [dict(t=round(float(t[k]), 4),
                          value=round(float(y[k]), 4),
                          dev=round(float(resid[k] / rms), 1))
                     for k in np.argsort(-np.abs(resid))[:5]
                     if abs(resid[k]) > 4 * rms]
            s["anomalies"] = flags
            s["anomaly_receipt"] = ("flagged beyond 4x residual rms "
                                    "— named, never judged")
            fut = t[-1] + step * np.arange(1.0, 13.0)
            fc = mind.apply_series(c, fut)
            if fc is not None:
                s["forecast"] = dict(
                    horizon=12, lo=round(float(fc.min()), 4),
                    hi=round(float(fc.max()), 4),
                    last_seen=round(float(y[-1]), 4))
            w = mind.watch_series(c, t[-max(12, len(t) // 10):],
                                  y[-max(12, len(t) // 10):])
            if w:
                s["watch"] = dict(verdict=w["verdict"],
                                  err_norm=w["err_norm"])
        table["series"].append(s)
    for a in range(len(vals)):
        for b in range(a + 1, len(vals)):
            ia, ca = vals[a]
            ib, cb = vals[b]
            r = mind.relate_series(t, R[:, ia], t, R[:, ib],
                                   name=f"{ca}~{cb}",
                                   containers=[f"data-{ca}",
                                               f"data-{cb}"])
            if r["verdict"] == "RELATED":
                table["relations"].append(dict(
                    pair=f"{ca} ~ {cb}", corr=r["corr"],
                    shift=r["shift"], leader=r["leader"],
                    null=r["receipts"]["null"],
                    levels=r.get("levels"),
                    levels_receipt=r["receipts"]["levels_receipt"]))
            else:
                table["refused_pairs"] += 1
    return table


def analyst_source(source, time_col=None, mod=None):
    """The one command: ingest -> the full analyst report."""
    mod = mod or bridge.load_isaac_module()
    got = ingest(source)
    rep = dict(tables=[], skipped=got.get("skipped", []))
    for item in got["items"]:
        if item.get("kind") != "table":
            continue
        mind = mod.Isaac()
        rep["tables"].append(_analyze_table(mind, item, time_col))
    if not rep["tables"]:
        rep["receipt"] = "no tables found — nothing to analyze, said"
    return rep


def render_analyst(rep):
    L = []
    for tb in rep["tables"]:
        L.append(f"THE ANALYST'S REPORT — {tb['name']}")
        tcol = tb["time"]["column"]
        L.append(f"  {tb['n']} rows; time key: "
                 f"{tcol or 'NONE'} ({tb['time']['why']})")
        for d in tb["describe"]:
            L.append(f"    {d['column']}: {d['lo']} .. {d['hi']}")
        if tcol is None:
            L.append(f"  {tb['receipt']}")
            continue
        for s in tb["series"]:
            L.append(f"  ── {s['column']} ──")
            L.append(f"    trend [{s['trend_verdict']}]: {s['trend']}")
            if s["period"] is not None:
                L.append(f"    cycle: period {s['period']}"
                         + (f", profile swing {s['profile_swing']}"
                            if s["profile_swing"] else
                            " (shape refused past the null)"))
            acc = s["accounting"]
            L.append(f"    the books: trend {acc['trend']}% + "
                     f"seasonal {acc['seasonal']}% + residual "
                     f"{acc['residual']}% = 100")
            for rcpt in s.get("receipts", []):
                L.append(f"    receipt: {rcpt}")
            if s.get("anomalies"):
                worst = s["anomalies"][0]
                L.append(f"    anomalies: {len(s['anomalies'])} "
                         f"flagged (worst {worst['dev']}x at "
                         f"t={worst['t']}) — {s['anomaly_receipt']}")
            if s.get("forecast"):
                f = s["forecast"]
                L.append(f"    forecast next {f['horizon']}: "
                         f"{f['lo']} .. {f['hi']} (last seen "
                         f"{f['last_seen']})")
            if s.get("watch"):
                L.append(f"    watch: {s['watch']['verdict']} "
                         f"(err_norm {s['watch']['err_norm']}) — "
                         f"arriving data will be judged")
        L.append("  ── relations ──")
        for r in tb["relations"]:
            lead = ("same-step" if r["leader"] == "none"
                    else f"{r['leader']} leads by {r['shift']}")
            L.append(f"    {r['pair']}: RELATED corr {r['corr']} vs "
                     f"null {r['null']} ({lead}); levels "
                     f"{r['levels']} — {r['levels_receipt']}")
        if not tb["relations"]:
            L.append("    none said")
        if tb["refused_pairs"]:
            L.append(f"    refused pairs: {tb['refused_pairs']} "
                     f"(the null was not beaten — receipts kept)")
    if rep.get("receipt"):
        L.append(rep["receipt"])
    return "\n".join(L)
