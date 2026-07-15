"""The Audit Face — data ops deliverable 1 (owner positioning,
2026-07-14: "data refinement and updating, data entry, organization,
trend graphing and system modelling"). The product is TRUST: flags
WITH RECEIPTS, honest refusals, and questions where information is
missing — never a silent pass, never an estimated floor.

audit_source(source) -> the audit report dict:
  - INGEST & ACCOUNT: every item listed, every skip with its why
  - FLOORS per column (repeats > told > grain); unevidenced -> ASK
  - LAW PASS per table (a refusal card has the same standing as a law)
  - ROW AUDIT, flags CLASSIFIED with receipts:
      ERROR-CANDIDATE  — violates the law beyond the floor, does not recur
      NEWS-CANDIDATE   — the deviation RECURS; the commonality miner
                         names the shared factor (the differential
                         decides, never a threshold)
      DUPLICATE        — exact, or near (within 3x floor) isolated pairs
  - JOIN DISCOVERY across tables (triangulate; NO ALIGNMENT is said)
  - COMPLETE NUMBERS + machine-readable records (ledger-shaped)

Scripted control flow is ACCEPTED for this face (the askisaac
precedent) — a fixed workflow, not learning; it migrates to the
interpreter when the kernel exists. The audit runs a FRESH mind per
call; it never writes into a living account.

Honest v1 scopes, said plainly:
  - law-pass claims are numeric-columns only (categoricals are dropped
    and accounted by intake — the covtype lesson)
  - OUT-OF-DOMAIN flags activate when laws are ledger-inherited /
    cross-table; a same-table law has seen every row, so the class
    cannot fire here yet
  - near-duplicates are flagged only for ISOLATED pairs: many repeats
    of one input row are a measurement design (the floor's evidence),
    not double-entry
  - flags measure deviation from the MEDIAN-centered residual, and the
    floor-coverage gate uses the robust (MAD) spread — otherwise the
    planted errors being hunted would drag the baseline and disqualify
    the hunt (contamination lesson, built in from day one)
"""
import numpy as np

from . import bridge
from .intake import ingest
from .report import _rename
from .triangulate import triangulate

MAX_JOIN_PAIRS = 10


def _table_xy(item, target=None):
    cols = item["columns"]
    ti = cols.index(target) if target in cols else len(cols) - 1
    rows = np.asarray(item["rows"], float)
    keep = [i for i in range(len(cols)) if i != ti]
    return ([cols[i] for i in keep], rows[:, keep], rows[:, ti],
            cols[ti])


def _bin_records(names, X):
    """Rows -> feature=value records for the commonality miner:
    low-cardinality columns keep their values; continuous columns get
    quartile labels."""
    n, d = X.shape
    recs = [dict() for _ in range(n)]
    for j in range(d):
        col = X[:, j]
        u = np.unique(col)
        if len(u) <= 8:
            for i in range(n):
                recs[i][names[j]] = f"{col[i]:g}"
        else:
            qs = np.quantile(col, [0.25, 0.5, 0.75])
            lab = np.digitize(col, qs)
            for i in range(n):
                recs[i][names[j]] = f"Q{lab[i] + 1}"
    return recs


def _audit_table(mind, item, target, resolutions, asks, records):
    tbl = item["name"]
    names, X, y, target_name = _table_xy(item, target)
    for col, sig in (resolutions or {}).items():
        if col == target_name or col in names:
            mind.tell_resolution(f"{tbl}:{col}", float(sig))

    # ── floors, every column, every road kept ──
    floors = {}
    r = mind.read_floor(y, X=X, name=f"{tbl}:{target_name}")
    floors[target_name] = r
    if r["floor"] is None:
        asks.append(target_name)
    for j, nm in enumerate(names):
        fr = mind.read_floor(X[:, j], name=f"{tbl}:{nm}")
        floors[nm] = fr
        records.append(dict(record="floor", table=tbl, column=nm,
                            floor=fr["floor"], road=fr["road"]))
    records.append(dict(record="floor", table=tbl, column=target_name,
                        floor=r["floor"], road=r["road"]))

    # ── the law pass (a refusal is a card, not a blank) ──
    law_name = f"audit:{tbl}"
    mind.discover(X, y, name=law_name)
    f = dict(mind.findings[-1])
    model = mind.net.get_meta(f"law:{law_name}", "model")
    law = dict(verdict=f.get("verdict", "?"))
    if f.get("equation"):
        law["equation"] = f"{target_name} = " \
                          f"{_rename(f['equation'], names)}"
    if isinstance(f.get("r2"), float):
        law["r2"] = round(f["r2"], 4)
    for k in ("articulated", "captured", "noise"):
        if k in f:
            law.setdefault("accounting", {})[k] = f[k]
    if f.get("adequacy"):
        law["adequacy"] = f["adequacy"]
    records.append(dict(record="law", table=tbl,
                        verdict=law["verdict"],
                        equation=law.get("equation")))

    flags, news_factors = [], []
    n = len(y)
    counts = dict(rows=n, error=0, news=0, duplicate=0,
                  unvalidatable=0, unflagged=0)
    floor_t = floors[target_name]["floor"]

    if model is None:
        counts["unvalidatable"] = n
        flags_status = "refused (no applicable law — rows counted " \
                       "unvalidatable, never silently passed)"
    else:
        pred0 = mind.apply_law(law_name, X)
        mask = np.isfinite(pred0)
        # CONSENSUS RECALIBRATION (wrong-kept, audit battery A3,
        # 2026-07-15): the planted deviations DRAGGED the fitted law
        # (slope 2.0 -> 1.89, intercept 0 -> 1.5), tilting every clean
        # row's residual until the audit disqualified itself. The
        # law's FORM stands as discovered; the row-judging baseline is
        # an affine recalibration refit on the CONSENSUS rows,
        # dissenters trimmed iteratively (the Gate 6 trim; the
        # poisoning cure's logic applied to laws). Affine-only is the
        # honest v1 scope; the verdict rewrite is the deeper cure.
        a_c, b_c = 0.0, 1.0
        inl = mask.copy()
        pred = pred0.copy()
        for _ in range(4):
            A = np.column_stack([pred0[inl], np.ones(int(inl.sum()))])
            (b_c, a_c), *_ = np.linalg.lstsq(A, y[inl], rcond=None)
            pred = np.where(mask, b_c * pred0 + a_c, np.nan)
            rr = y - pred
            med0 = float(np.median(rr[mask]))
            mad0 = float(1.4826 * np.median(np.abs(rr[mask] - med0)))
            cut = 3.5 * max(mad0, float(floor_t or 0.0), 1e-12)
            nxt = mask & (np.abs(rr - med0) <= cut)
            if nxt.sum() < max(8, 0.5 * mask.sum()) or \
                    (nxt == inl).all():
                break
            inl = nxt
        resid = np.where(mask, y - pred, np.nan)
        rv = resid[mask]
        med = float(np.median(rv))
        mad = float(1.4826 * np.median(np.abs(rv - med)))
        counts["unvalidatable"] = int((~mask).sum())
        if floor_t is None:
            flags_status = ("refused (target floor UNEVIDENCED — ASK "
                            "for the instrument's resolution; no ruler,"
                            " no flags)")
        elif mad > 3 * floor_t:
            # The honest fork, both named (bench W3 lesson, 2026-07-15:
            # after the floor's consensus cure, a trial refused HERE
            # because gross outliers had dragged the discovered FORM —
            # the old message blamed the user's ruler for what was the
            # law's failure; a refusal must not misdiagnose its cause):
            flags_status = (f"refused (evidenced floor {floor_t:g} does"
                            f" not cover the residual spread {mad:g}: "
                            f"EITHER the floor under-evidences — ASK "
                            f"for the true resolution, never loosen "
                            f"the gate — OR the discovered law does "
                            f"not hold at that precision and the "
                            f"residual carries structure the law "
                            f"missed; the verdict rewrite is the "
                            f"deeper cure)")
        else:
            flags_status = "active"
            cand = np.zeros(n, bool)
            cand[mask] = np.abs(rv - med) > 4 * floor_t
            cand_rows = np.where(cand)[0]
            if len(cand_rows) >= 3:
                recs = _bin_records(names, X)
                mres = mind.mine_commonality(
                    recs, cand.tolist(), name=f"audit:{tbl}:flags")
                news_factors = mres["named"]
            named = {(k, v) for k, v, _ in news_factors}
            recs_all = _bin_records(names, X) if named else None
            for i in cand_rows:
                is_news = named and any(
                    (k, recs_all[i].get(k)) in named
                    for k in recs_all[i])
                kind = "NEWS-CANDIDATE" if is_news else "ERROR-CANDIDATE"
                counts["news" if is_news else "error"] += 1
                fl = dict(kind=kind, row=int(i),
                          why=("deviation recurs — shared factor named"
                               if is_news else
                               "violates the law beyond the floor; "
                               "does not recur"),
                          receipt=dict(law=law_name,
                                       residual=float(resid[i]),
                                       floor=float(floor_t),
                                       value=float(y[i]),
                                       predicted=float(pred[i])))
                flags.append(fl)
            # duplicates: exact always; near only for isolated pairs
            groups = {}
            for i in range(n):
                groups.setdefault(tuple(np.round(X[i], 10)),
                                  []).append(i)
            for g in groups.values():
                if len(g) < 2:
                    continue
                for a in range(len(g)):
                    for b in range(a + 1, len(g)):
                        i, j = g[a], g[b]
                        if y[i] == y[j]:
                            note = "exact"
                        elif (len(g) == 2 and floor_t is not None
                              and abs(y[i] - y[j]) <= 3 * floor_t):
                            note = "near (within 3x floor)"
                        else:
                            continue
                        counts["duplicate"] += 1
                        flags.append(dict(
                            kind="DUPLICATE", row=int(j),
                            why=f"{note} duplicate of row {i}",
                            receipt=dict(rows=[int(i), int(j)],
                                         note=note,
                                         floor=floor_t)))
    recal = None
    if model is not None and (abs(b_c - 1.0) > 1e-3
                              or abs(a_c) > 1e-3):
        recal = dict(scale=round(float(b_c), 6),
                     offset=round(float(a_c), 6),
                     why="consensus recalibration: the row-judging "
                         "baseline is refit on the rows most of the "
                         "data agrees on, so planted deviations "
                         "cannot drag the judge")
    counts["unflagged"] = max(0, n - counts["error"] - counts["news"]
                              - counts["duplicate"]
                              - counts["unvalidatable"])
    for fl in flags:
        records.append(dict(record="flag", table=tbl, **{
            k: v for k, v in fl.items() if k != "receipt"},
            receipt=fl["receipt"]))
    return dict(name=tbl, target=target_name, columns=names,
                dropped_columns=item.get("dropped_columns", []),
                floors=floors, law=law, flags_status=flags_status,
                flags=flags, news_factors=news_factors, counts=counts,
                recalibration=recal)


def audit_source(source, target=None, resolutions=None, mod=None):
    """The whole audit: source -> ingest -> floors -> laws -> row
    flags -> joins -> complete numbers. Returns the report dict;
    render with render_audit(); rep["records"] is the audit.jsonl
    content (one ledger-shaped line per law/floor/flag/join)."""
    mod = mod or bridge.load_isaac_module()
    got = ingest(source)
    tables = [i for i in got["items"] if i["kind"] == "table"]
    texts = [i for i in got["items"] if i["kind"] == "text"]
    mind = mod.Isaac()
    asks, records = [], []
    reps = [_audit_table(mind, t, target, resolutions, asks, records)
            for t in tables]

    joins = []
    pairs = [(a, b) for a in range(len(tables))
             for b in range(a + 1, len(tables))]
    for a, b in pairs[:MAX_JOIN_PAIRS]:
        try:
            tri = triangulate(tables[a], tables[b], mod=mod)
        except Exception as e:                # a join scan must never
            tri = dict(verdict="SCAN FAILED",  # kill the whole audit
                       why=f"triangulation raised "
                           f"{type(e).__name__} — reported, not hidden")
        j = dict(tables=(tables[a]["name"], tables[b]["name"]),
                 verdict=tri["verdict"], why=tri.get("why", ""))
        if "key" in tri:
            j["key"] = tri["key"]
        if "equation" in tri:
            j["equation"] = tri["equation"]
        joins.append(j)
        records.append(dict(record="join", **j))
    if len(pairs) > MAX_JOIN_PAIRS:
        joins.append(dict(tables=("...",),
                          verdict="NOT SCANNED",
                          why=f"join scan capped at {MAX_JOIN_PAIRS} "
                              f"pairs of {len(pairs)} — capped and "
                              f"accounted, never silent"))

    summary = dict(
        tables=len(tables), texts=len(texts),
        skipped=len(got["skipped"]),
        rows=sum(r["counts"]["rows"] for r in reps),
        error=sum(r["counts"]["error"] for r in reps),
        news=sum(r["counts"]["news"] for r in reps),
        duplicate=sum(r["counts"]["duplicate"] for r in reps),
        unvalidatable=sum(r["counts"]["unvalidatable"] for r in reps),
        laws=sum(1 for r in reps
                 if r["law"]["verdict"] in ("UNDERSTOOD", "PARTIAL")),
        refusals=sum(1 for r in reps
                     if r["flags_status"].startswith("refused")),
        asks=sorted(set(asks)))
    return dict(intake=dict(
                    items=[dict(name=i["name"], kind=i["kind"],
                                provenance=i["provenance"])
                           for i in got["items"]],
                    skipped=got["skipped"]),
                tables=reps, texts=[t["name"] for t in texts],
                joins=joins, asks=sorted(set(asks)),
                summary=summary, records=records)


def render_audit(rep):
    """Text rendered ONLY from report fields (the faithfulness law)."""
    L = ["ISAAC — the audit", "=" * 60]
    for s in rep["intake"]["skipped"]:
        L.append(f"[skipped] {s['source']} — {s['why']}")
    for t in rep["tables"]:
        L += ["", f"TABLE {t['name']}   target: {t['target']}   "
                  f"rows: {t['counts']['rows']}",
              f"  VERDICT: {t['law']['verdict']}"]
        if t["law"].get("equation"):
            L.append(f"    {t['law']['equation']}")
        for col, fr in t["floors"].items():
            if fr["floor"] is None:
                L.append(f"  floor[{col}]: UNEVIDENCED — ASK for the "
                         f"instrument's resolution")
            else:
                L.append(f"  floor[{col}]: {fr['floor']:g} via "
                         f"{fr['road']}")
        L.append(f"  flags: {t['flags_status']}")
        for fl in t["flags"][:10]:
            r = fl["receipt"]
            if fl["kind"] == "DUPLICATE":
                L.append(f"    row {fl['row']}: DUPLICATE — {fl['why']}")
            else:
                L.append(f"    row {fl['row']}: {fl['kind']} — value "
                         f"{r['value']:g} vs predicted "
                         f"{r['predicted']:g} (residual "
                         f"{r['residual']:g}, floor {r['floor']:g})")
        if len(t["flags"]) > 10:
            L.append(f"    ... and {len(t['flags']) - 10} more")
        if t["news_factors"]:
            L.append("  NEWS factors named: " + ", ".join(
                f"{k}={v} (excess {e:.2f})"
                for k, v, e in t["news_factors"]))
        c = t["counts"]
        L.append(f"  counts: {c['error']} error / {c['news']} news / "
                 f"{c['duplicate']} duplicate / "
                 f"{c['unvalidatable']} unvalidatable / "
                 f"{c['unflagged']} unflagged")
    for j in rep["joins"]:
        L.append(f"JOIN {j['tables']}: {j['verdict']}"
                 + (f" on '{j['key']}'" if "key" in j else "")
                 + (f" — {j['why']}" if j.get("why") else ""))
    if rep["asks"]:
        L += ["", "ASK: the instrument's resolution for: "
                  + ", ".join(rep["asks"])
                  + "  (rerun with --resolution col=sigma)"]
    s = rep["summary"]
    L += ["", "COMPLETE NUMBERS",
          f"  {s['tables']} tables, {s['rows']} rows audited; "
          f"{s['error']} error / {s['news']} news / "
          f"{s['duplicate']} duplicate flags; "
          f"{s['unvalidatable']} unvalidatable; "
          f"{s['laws']} laws; {s['refusals']} flag refusals; "
          f"asks: {', '.join(s['asks']) or 'none'}"]
    return "\n".join(L)
