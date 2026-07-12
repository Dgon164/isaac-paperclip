"""The Honest Report — how people use Isaac (owner MVP, 2026-07-04:
"drop a CSV, get an honest report").

One function: challenge(csv) -> a report a person can read:
- the VERDICT first (UNDERSTOOD / PARTIAL / CAPTURED / NO RULE — a
  refusal is a first-class answer, with its diagnosis)
- the equation IN THE USER'S COLUMN NAMES, complete numbers (r2,
  held-out edge, rows), graded confidence on their own data
- the accounting (articulated + captured + noise) when present
- live rivals the data could not reject, with the probe that would
  settle each
- what to do next (the experiment suggestion)
- the provenance appendix: rows, columns, data hash, engine, date —
  every report traceable to exactly what produced it.

No dressing, no padding: the moat is calibrated honesty.
"""
import csv as _csv
import hashlib
import io
import re
import time

import numpy as np

from . import bridge


def load_csv(text_or_path, target=None):
    """CSV -> (names, X, y, target_name). Header auto-detected;
    target by column name, else the LAST column."""
    if "\n" not in str(text_or_path) and len(str(text_or_path)) < 500:
        with open(text_or_path, "r", encoding="utf-8-sig") as f:
            text = f.read()
    else:
        text = text_or_path
    rows = [r for r in _csv.reader(io.StringIO(text)) if r]
    def _num(v):
        try:
            float(v); return True
        except ValueError:
            return False
    header = None
    if rows and not all(_num(v) for v in rows[0]):
        header, rows = [h.strip() for h in rows[0]], rows[1:]
    data = np.array([[float(v) for v in r] for r in rows], dtype=float)
    names = header or [f"col{i}" for i in range(data.shape[1])]
    ti = names.index(target) if target else len(names) - 1
    mask = np.ones(data.shape[1], bool); mask[ti] = False
    return ([n for i, n in enumerate(names) if i != ti],
            data[:, mask], data[:, ti], names[ti])


def _rename(text, names):
    """x0..xN -> the user's column names (descending, so x12 != x1+2)."""
    for i in sorted(range(len(names)), reverse=True):
        text = re.sub(rf"\bx{i}\b", names[i], str(text))
    return text


def challenge(csv_text_or_path, target=None, name="challenge", mod=None):
    """The whole journey: CSV -> discover -> the honest report dict."""
    mod = mod or bridge.load_isaac_module()
    names, X, y, target_name = load_csv(csv_text_or_path, target)
    raw = (csv_text_or_path if "\n" in str(csv_text_or_path)
           else open(csv_text_or_path, "rb").read().decode("utf-8", "replace"))
    mind = mod.Isaac()
    mind.discover(X, y, name=name)
    f = dict(mind.findings[-1])
    m = mind.net.get_meta(f"law:{name}", "model")

    verdict = f.get("verdict", f.get("kind", "?"))
    rep = dict(verdict=verdict, target=target_name, finding=f,
               rows=int(len(y)), columns=names)
    eq = f.get("equation")
    if eq:
        rep["equation"] = f"{target_name} = {_rename(eq, names)}"
    if m is not None:
        # the structure itself, as plain data — speech realizes from
        # THIS, never from parsing strings
        rep["terms"] = [
            dict(coef=float(c),
                 atoms=[dict(zip(("kind", "i", "j", "k"), m["specs"][a]))
                        for a in t])
            for t, c in zip(m["terms"], m["coefs"])]
        rep["intercept"] = float(m.get("intercept", 0.0))
    if isinstance(f.get("r2"), float):
        rep["fit"] = dict(r2=round(f["r2"], 4),
                          r2_edge=f.get("r2_edge"))
    conf = mind.law_confidence(name, X) if m is not None else None
    if conf is not None:
        rep["confidence"] = dict(
            mean=round(float(np.mean(conf)), 3),
            note="calibrated on 100 externally-graded worlds; "
                 "inside-data belief, not optimism")
    acct = {k: f[k] for k in ("articulated", "captured", "noise")
            if k in f}
    if acct:
        rep["accounting"] = acct
    rivals = (m or {}).get("rivals", [])
    if rivals:
        rep["rivals"] = [dict(note=r.get("note", ""),
                              probe=r.get("probe", "")) for r in rivals[:3]]
    if verdict == "UNDERSTOOD":
        nxt = ("Confirm out of range: sample beyond the observed span "
               "and run validate_law — extrapolation is where look-alikes split.")
    elif rivals:
        nxt = "Sample where the top rival and the law disagree most."
    elif verdict in ("PARTIAL", "CAPTURED"):
        nxt = ("The residual holds unarticulated structure: more rows, "
               "or add the variable the residual dossier points at.")
    else:
        nxt = (f.get("adequacy") or
               "No relation passed the nulls: more data, another "
               "variable, or there is genuinely nothing here.")
    rep["next_experiment"] = str(nxt)
    rep["provenance"] = dict(
        rows=int(len(y)), cols=len(names) + 1,
        data_sha=hashlib.sha256(raw.encode()).hexdigest()[:16],
        engine="isaac.py", date=time.strftime("%Y-%m-%d %H:%M"))
    return rep


def render_text(rep):
    L = [f"ISAAC — the honest report ({rep['provenance']['date']})",
         "=" * 60,
         f"VERDICT: {rep['verdict']}   target: {rep['target']}   "
         f"rows: {rep['rows']}"]
    if "equation" in rep:
        L += ["", f"  {rep['equation']}"]
    if "fit" in rep:
        edge = rep["fit"].get("r2_edge")
        L.append(f"  fit r2={rep['fit']['r2']}"
                 + (f"  held-out edge r2={edge}" if edge else ""))
    if "confidence" in rep:
        L.append(f"  confidence (this data): {rep['confidence']['mean']}"
                 f"  [{rep['confidence']['note']}]")
    if "accounting" in rep:
        a = rep["accounting"]
        L.append("  accounting: " + " + ".join(f"{k} {v}"
                                               for k, v in a.items()))
    if rep.get("rivals"):
        L.append("")
        L.append("  RIVALS the data could not reject:")
        for r in rep["rivals"]:
            L.append(f"    - {r['note']}" +
                     (f" | probe: {r['probe']}" if r["probe"] else ""))
    L += ["", f"NEXT: {rep['next_experiment']}",
          "", f"provenance: {rep['provenance']}"]
    return "\n".join(L)
