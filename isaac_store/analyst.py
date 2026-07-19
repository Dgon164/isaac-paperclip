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
  DOSSIER    the specifics layer (owner 2026-07-18): per-column
             mean/median/mode/std/resolution with extremes AND
             their rows, example rows, calendar frames (avg per
             day/month/year), sign-safe ratios, slope history —
             THE DOSSIER DESCRIBES, THE COURT JUDGES
  PLOTS      --plot writes an SVG per column: points, error bars,
             the court's trend dashed, yearly averages stepped,
             anomalies ringed

No time key = the series roads refuse with a receipt (the law road
and the audit face still stand for such tables).
"""
import os
import re

import numpy as np

from . import bridge
from .intake import ingest
from .plot import plot_series


def _detect_time(cols, R, time_col=None):
    if time_col and time_col in cols:
        return cols.index(time_col), "told"
    for i, c in enumerate(cols):
        v = R[:, i]
        if np.all(np.isfinite(v)) and len(v) > 2 \
                and np.all(np.diff(v) > 0):
            return i, f"auto: '{c}' strictly increases"
    return None, "no strictly-increasing column found"


def _analyze_table(mind, item, time_col, plots=None):
    cols = item["columns"]
    R = np.asarray(item["rows"], float)
    good = np.isfinite(R).all(1)
    R = R[good]
    ymd = ([g for g, ok in zip(item["ymd"], good) if ok]
           if item.get("ymd") else None)
    ti, time_why = _detect_time(cols, R, time_col)
    if item.get("calendar") is not None and time_col is None:
        # a declared calendar IS the time key — told beats the scan
        # (review find: a leading id column used to win the scan
        # and mislabel every downstream unit)
        ci = item["calendar"]["index_in_keep"]
        if ti != ci:
            ti = ci
        time_why = (f"calendar column '{item['calendar']['column']}' "
                    f"({item['calendar']['format']}) — told by "
                    f"intake")
    if ti is not None:
        o = np.argsort(R[:, ti], kind="stable")
        if not np.array_equal(o, np.arange(len(R))):
            # the file's order is not time's order — reorder and
            # SAY SO (review find: newest-first CSVs walked the
            # forecast into the pre-data past)
            R = R[o]
            if ymd is not None:
                ymd = [ymd[k] for k in o]
            time_why += (" — rows reordered into time order (the "
                         "file was not time-sorted)")
        if len(np.unique(R[:, ti])) < len(R):
            time_why += (" — duplicate timestamps present (step "
                         "read from median spacing)")
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
        _take_dossier_and_plots(mind, item, table, R, cols, ti, ymd,
                                plots)
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
    _take_dossier_and_plots(mind, item, table, R, cols, ti, ymd,
                            plots)
    return table


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", str(s))


def _dossier_name(item):
    """Collision-proof: the FULL item name (relpath + npz key)
    sanitized, extension stripped — 'a/data.csv' and 'b/data.csv'
    stay two dossiers (review find)."""
    n = str(item.get("name", "table"))
    n = re.sub(r"\.(csv|tsv|json|jsonl|npy|npz|xlsx|txt)$", "", n,
               flags=re.I)
    return _safe(n) or "table"


def _take_dossier_and_plots(mind, item, table, R, cols, ti, ymd,
                            plots):
    """The specifics layer + the plot face, one road for both the
    timed and the untimed table (stats stand even when frames
    refuse)."""
    dz = mind.take_dossier(cols, R.tolist(), _dossier_name(item),
                           time_index=ti, ymd=ymd,
                           provenance=item.get("provenance"))
    table["dossier"] = dz
    if plots is None:
        return
    if dz.get("refused") or ti is None:
        table["plots_receipt"] = ("plots refused: "
                                  + (dz.get("refused")
                                     or "no time key — points need "
                                        "an axis"))
        return
    os.makedirs(plots, exist_ok=True)
    t = R[:, ti]
    written = []
    for j, c in enumerate(cols):
        if j == ti:
            continue
        y = R[:, j]
        # the trend is drawn ONLY where the court said one — when
        # the verdict was a refusal, apply_series answers zeros and
        # a phantom trend would be a lie (review find)
        s_entry = next((s for s in table.get("series", [])
                        if s["column"] == c), None)
        trusted = (s_entry is not None
                   and s_entry.get("trend_verdict")
                   in ("UNDERSTOOD", "PARTIAL"))
        pred = mind.apply_series(c, t) if trusted else None
        err = err_why = None
        anom = None
        if pred is not None:
            resid = y - pred
            rms = float(np.sqrt(np.mean(resid ** 2))) or 1e-12
            err, err_why = rms, "± residual rms (the court's own)"
            anom = [int(k) for k in np.where(
                np.abs(resid) > 4 * rms)[0]]
        else:
            step = dz["stats"][c]["resolution"].get("step")
            if step:
                err, err_why = step / 2.0, "± half the grain"
        steps = None
        if isinstance(dz["frames"], list):
            for fr in dz["frames"]:
                if fr.get("buckets") and fr["level"] in ("year",
                                                         "month"):
                    steps = [(b["t"], b["cols"][c]["avg"])
                             for b in fr["buckets"]]
                    break
        path = os.path.join(
            plots, f"{_dossier_name(item)}_{_safe(c)}_{j}.svg")
        plot_series(path, t, y, title=f"{c} — points, the court's "
                    f"trend, frame averages",
                    xlabel=(cols[ti] if ti is not None else "t"),
                    ylabel=c, err=err, err_why=err_why,
                    trend=(pred if pred is not None else None),
                    steps=steps, anomalies=anom)
        written.append(path)
    if written:
        table["plots"] = written


def analyst_source(source, time_col=None, mod=None, mind=None,
                   plots=None):
    """The one command: ingest -> the full analyst report. Pass
    mind= to run on a LIVE account (the meal road — dossiers and
    series persist there); default stays a fresh consult mind per
    table. plots= names a directory for the SVG faces."""
    mod = mod or bridge.load_isaac_module()
    got = ingest(source)
    rep = dict(tables=[], skipped=got.get("skipped", []))
    for item in got["items"]:
        if item.get("kind") != "table":
            continue
        m = mind or mod.Isaac()
        rep["tables"].append(_analyze_table(m, item, time_col,
                                            plots=plots))
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
            _render_dossier(L, tb.get("dossier"))
            if tb.get("plots_receipt"):
                L.append(f"  {tb['plots_receipt']}")
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
        _render_dossier(L, tb.get("dossier"))
        if tb.get("plots_receipt"):
            L.append(f"  {tb['plots_receipt']}")
        for pth in tb.get("plots", []):
            L.append(f"  plot written: {pth}")
    if rep.get("receipt"):
        L.append(rep["receipt"])
    return "\n".join(L)


def _render_dossier(L, dz):
    if not dz:
        return
    if dz.get("refused"):
        L.append(f"  ── the dossier ── refused: {dz['refused']}")
        return
    L.append(f"  ── the dossier (node {dz['node']}) ──")
    for c, s in dz["stats"].items():
        res = s["resolution"]
        r_txt = (f"resolution {res['step']:.6g}"
                 if res.get("step") else "resolution: none read")
        mode = s["mode"]
        m_txt = (f"mode {mode['value']:.6g} (x{mode['count']}"
                 + (f", {mode['n_tied']} tied" if mode.get("ties")
                    else "") + ")"
                 if mode.get("value") is not None
                 else "mode: none (no recurring value)")
        std = s["std"]["value"]
        L.append(f"    {c}: n {s['n']}, mean {s['mean']:.6g}, "
                 f"median {s['median']:.6g}, "
                 f"std {std:.6g}" if std is not None else
                 f"    {c}: n {s['n']}, mean {s['mean']:.6g}, "
                 f"median {s['median']:.6g}, std: none (one row)")
        L.append(f"      {m_txt}; {r_txt}; "
                 f"lo {s['lo']['value']:.6g} / "
                 f"hi {s['hi']['value']:.6g} (rows kept)")
    ex = dz["examples"]
    L.append(f"    examples: {len(ex['rows'])} rows remembered of "
             f"{ex['n_source']} ({ex['why']})")
    if isinstance(dz["frames"], list):
        for fr in dz["frames"]:
            if fr.get("skipped"):
                L.append(f"    frames/{fr['level']}: skipped — "
                         f"{fr['skipped']}")
                continue
            b0, b1 = fr["buckets"][0], fr["buckets"][-1]
            tgt = dz["target"]
            L.append(f"    frames/{fr['level']}: {fr['n_buckets']} "
                     f"buckets; {tgt} avg {b0['cols'][tgt]['avg']:.6g}"
                     f" ({b0['bucket']}) -> "
                     f"{b1['cols'][tgt]['avg']:.6g} ({b1['bucket']})"
                     + (f"; slope {fr['slopes'][tgt]['per_year']:.6g}"
                        f"/yr (described, not judged)"
                        if fr.get("slopes") else ""))
    else:
        L.append(f"    frames: {dz['frames']['refused']}")
    for r in dz["ratios"]:
        if r.get("refused"):
            L.append(f"    ratio {r['pair']}: refused — "
                     f"{r['refused']}")
        elif r.get("pair"):
            L.append(f"    ratio {r['pair']}: mean {r['mean']:.6g} "
                     f"({r['lo']:.6g} .. {r['hi']:.6g})")
    if len(dz["history"]) > 1:
        h0, h1 = dz["history"][0], dz["history"][-1]
        L.append(f"    the line, tracked: take {h0['take']} mean "
                 f"{h0['target_mean']:.6g} -> take {h1['take']} "
                 f"mean {h1['target_mean']:.6g}")
