"""test_audit.py — THE AUDIT FACE battery (data-ops segment §1).
Written FIRST, per discipline; the face is built to pass it.

The product under test: drop data on Isaac, get flags WITH RECEIPTS,
honest refusals, and questions where information is missing. Flags are
CLASSIFIED (error-candidate / news-candidate / duplicate /
unvalidatable), every flag traceable to law + residual + floor + row.
The differential decides news-vs-error (the commonality miner), never
a threshold. Floors gate exactness: no ruler, no flags — the ASK is
the answer (never "just estimate").

Checks A1-A8 (+A0 render). Run: PYTHONHASHSEED=0 python test_audit.py
"""
import io
import json
import os
import sys
import tempfile
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from isaac_store.audit import audit_source, render_audit   # noqa: E402

rng = np.random.default_rng(7)
PASSED, FAILED = 0, 0


def check(name, ok, detail=""):
    global PASSED, FAILED
    PASSED, FAILED = PASSED + ok, FAILED + (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
          + (f"   {detail}" if detail else ""))


def csv_text(cols, rows):
    return "\n".join([",".join(cols)] +
                     [",".join(f"{v:.10g}" for v in r) for r in rows])


def write(td, name, text):
    p = os.path.join(td, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def q(y, g):
    return np.round(y / g) * g


def main():
    print("=" * 70)
    print("AUDIT BATTERY — the audit face")
    print("=" * 70)

    # ── A1: planted errors flagged, complete precision/recall ──
    x = np.repeat(np.linspace(0.5, 6, 40), 8)
    rng.shuffle(x)
    y = 2.0 * x + rng.normal(0, 0.05, len(x))
    bad = [3, 47, 111, 200, 260, 301]
    y2 = y.copy()
    for i in bad:
        y2[i] += 5.0
    with tempfile.TemporaryDirectory() as td:
        p = write(td, "a1.csv", csv_text(["x", "y"],
                                         np.column_stack([x, y2])))
        rep = audit_source(p)
    t = rep["tables"][0]
    flagged = {f["row"] for f in t["flags"]
               if f["kind"].endswith("CANDIDATE")}
    ok = (flagged == set(bad)
          and t["floors"][t["target"]]["road"] == "repeats"
          and all("residual" in f["receipt"] and "floor" in f["receipt"]
                  and "law" in f["receipt"] for f in t["flags"]))
    check("A1 planted errors: 6/6 flagged, 0 extra, receipts complete",
          ok, f"flagged {sorted(flagged)} (floor via "
              f"{t['floors'][t['target']]['road']})")

    # ── A2: THE CONTROL — clean table, false-flag rate 0 ──
    with tempfile.TemporaryDirectory() as td:
        p = write(td, "a2.csv", csv_text(["x", "y"],
                                         np.column_stack([x, y])))
        rep = audit_source(p)
    t = rep["tables"][0]
    nf = sum(1 for f in t["flags"] if f["kind"].endswith("CANDIDATE"))
    check("A2 clean-table control: 0 false flags of "
          f"{t['counts']['rows']} rows", nf == 0, f"flags {nf}")

    # ── A3: news vs error — recurrence names the shared factor ──
    # The regime lives in a NARROW BAND of a continuous feature:
    # invisible to the atom pool (a law cannot absorb it), visible to
    # the miner's bins — deviations there RECUR, so they are NEWS.
    n = 240
    x0 = rng.uniform(0, 10, n)
    x1 = rng.uniform(0, 10, n)
    y = 2.0 * x0 + rng.normal(0, 0.1, n)
    band = (x1 >= 3.2) & (x1 < 3.8)   # safely inside one quartile bin
    y[band] += 8.0                             # the recurring regime
    lone = int(np.argmax(x1))                  # far from the band
    y[lone] += 50.0                            # the one-off error
    with tempfile.TemporaryDirectory() as td:
        p = write(td, "a3.csv", csv_text(
            ["x0", "x1", "y"], np.column_stack([x0, x1, y])))
        rep = audit_source(p, resolutions={"y": 0.1})
    t = rep["tables"][0]
    news = [f for f in t["flags"] if f["kind"] == "NEWS-CANDIDATE"]
    errs = [f for f in t["flags"] if f["kind"] == "ERROR-CANDIDATE"]
    regime = set(np.where(band)[0].tolist())
    news_rows = {f["row"] for f in news}
    named_feats = {f_ for f_, v, _ in t.get("news_factors", [])}
    ok = ("x1" in named_feats
          and len(news_rows & regime) >= 0.8 * len(regime)
          and any(f["row"] == lone for f in errs)
          and t["floors"][t["target"]]["road"] == "told")
    check("A3 recurring deviation = NEWS (factor on x1 named); "
          "one-off = ERROR", ok,
          f"named {sorted((f_, v) for f_, v, _ in t.get('news_factors', []))}; "
          f"news {len(news)}, errors {len(errs)}")

    # ── A4: duplicates — exact + near (within floor), both rows cited ──
    xs = rng.uniform(0, 5, 150)
    ys = q(3.0 * xs + rng.normal(0, 0.003, 150), 0.01)
    rows = np.column_stack([xs, ys]).tolist()
    rows.append([xs[10], ys[10]])                     # exact copy of 10
    rows.append([xs[20], ys[20] + 0.004])             # near copy of 20
    with tempfile.TemporaryDirectory() as td:
        p = write(td, "a4.csv", csv_text(["x", "y"], np.array(rows)))
        rep = audit_source(p)
    t = rep["tables"][0]
    dups = [f for f in t["flags"] if f["kind"] == "DUPLICATE"]
    cited = {tuple(sorted(f["receipt"]["rows"])) for f in dups}
    ok = ((10, 150) in cited and (20, 151) in cited
          and all("note" in f["receipt"] for f in dups))
    check("A4 duplicates: exact (10,150) + near (20,151) cited", ok,
          f"cited {sorted(cited)}")

    # ── A5: floor behavior — the honest misses ──
    # (a) grain-only with process noise ABOVE grain -> flags REFUSED
    xs = rng.uniform(0, 5, 200)
    ys = q(2.0 * xs + rng.normal(0, 0.5, 200), 0.01)
    with tempfile.TemporaryDirectory() as td:
        p = write(td, "a5a.csv", csv_text(["x", "y"],
                                          np.column_stack([xs, ys])))
        rep = audit_source(p)
    t = rep["tables"][0]
    ok = (t["flags_status"].startswith("refused")
          and "ask" in t["flags_status"].lower()
          and not t["flags"])
    check("A5a grain-only under process noise: flags REFUSED + ASK",
          ok, t["flags_status"][:70])
    # (b) nothing evidenced at all -> refused, ASK in the report
    ys = 2.0 * xs + rng.normal(0, 0.3, 200)
    with tempfile.TemporaryDirectory() as td:
        p = write(td, "a5b.csv", csv_text(["x", "y"],
                                          np.column_stack([xs, ys])))
        rep = audit_source(p)
    t = rep["tables"][0]
    ok = (t["floors"][t["target"]]["floor"] is None
          and t["flags_status"].startswith("refused")
          and t["target"] in rep["asks"])
    check("A5b floor unevidenced: refused; the ASK appears", ok,
          f"asks: {rep['asks']}")
    # (c) same world, resolution TOLD -> flags unlock
    with tempfile.TemporaryDirectory() as td:
        p = write(td, "a5c.csv", csv_text(["x", "y"],
                                          np.column_stack([xs, ys])))
        rep = audit_source(p, resolutions={"y": 0.3})
    t = rep["tables"][0]
    check("A5c resolution told -> flags active",
          t["flags_status"] == "active",
          f"floor {t['floors'][t['target']]['floor']}")

    # ── A6: join discovery across tables ──
    keys = np.arange(1.0, 81.0)
    z = rng.uniform(-3, 3, 80)
    xa = rng.uniform(0, 5, 80)
    ya = xa + z + rng.normal(0, 0.02, 80)
    w = 0.5 * z + rng.normal(0, 0.1, 80)      # B's own target column
    ta = csv_text(["key", "x", "y"], np.column_stack([keys, xa, ya]))
    tb = csv_text(["key", "z", "w"], np.column_stack([keys, z, w]))
    with tempfile.TemporaryDirectory() as td:
        write(td, "a.csv", ta)
        write(td, "b.csv", tb)
        rep = audit_source(td)
    j = rep["joins"][0]
    ok = j["verdict"].startswith("RESOLVED") and j.get("key") == "key"
    check("A6 join found past the scrambled-pairing null", ok,
          f"{j['verdict']} on '{j.get('key')}'")
    tb2 = csv_text(["key", "z", "w"],
                   np.column_stack([keys + 500.0, z, w]))  # disjoint keys
    with tempfile.TemporaryDirectory() as td:
        write(td, "a.csv", ta)
        write(td, "b.csv", tb2)
        rep = audit_source(td)
    j = rep["joins"][0]
    check("A6b disjoint keys -> NO ALIGNMENT (reported, not hidden)",
          j["verdict"] == "NO ALIGNMENT", j.get("why", "")[:50])

    # ── A7: refusal rendering — noise table still accounts every row ──
    xs = rng.normal(0, 1, 200)
    ys = rng.normal(0, 1, 200)
    with tempfile.TemporaryDirectory() as td:
        p = write(td, "a7.csv", csv_text(["x", "y"],
                                         np.column_stack([xs, ys])))
        rep = audit_source(p)
    t = rep["tables"][0]
    c = t["counts"]
    accounted = (c["unvalidatable"] + c["error"] + c["news"]
                 + c["duplicate"] + c["unflagged"])
    ok = (t["law"]["verdict"] in ("NO RULE", "CAPTURED", "PARTIAL")
          and c["unvalidatable"] == c["rows"]
          and accounted == c["rows"])
    check("A7 noise: refusal card + every row accounted", ok,
          f"verdict {t['law']['verdict']}, "
          f"unvalidatable {c['unvalidatable']}/{c['rows']}")
    text = render_audit(rep)
    check("A0 render: text from report fields only, verdict present",
          t["law"]["verdict"] in text and "COMPLETE NUMBERS" in text)

    # ── A8: door laws — garbage, unsupported, zip-bomb entry ──
    y8 = 2.0 * x + rng.normal(0, 0.05, len(x))
    with tempfile.TemporaryDirectory() as td:
        write(td, "fine.csv", csv_text(["x", "y"],
                                       np.column_stack([x, y8])))
        with open(os.path.join(td, "junk.xyz"), "wb") as f:
            f.write(b"\x00\x01garbage")
        rep = audit_source(td)
    ok = (any("unsupported" in s["why"] for s in rep["intake"]["skipped"])
          and len(rep["tables"]) == 1)
    check("A8a unsupported file skipped WITH ITS WHY; table still audited",
          ok, "; ".join(s["why"] for s in rep["intake"]["skipped"])[:50])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ok.csv", csv_text(["x", "y"],
                                       np.column_stack([x, y8])))
        zf.writestr("bomb.bin", b"\x00" * (51 * 1024 * 1024))
    with tempfile.TemporaryDirectory() as td:
        zp = os.path.join(td, "input.zip")
        with open(zp, "wb") as f:
            f.write(buf.getvalue())
        rep = audit_source(zp)
    ok = (any("cap" in s["why"] for s in rep["intake"]["skipped"])
          and len(rep["tables"]) == 1)
    check("A8b zip-bomb entry refused at the cap; the rest audited", ok,
          "; ".join(s["why"] for s in rep["intake"]["skipped"])[:50])

    # ── the machine-readable records road ──
    kinds = {r["record"] for r in rep["records"]}
    check("A0b audit records present (law/floor lines, ledger-shaped)",
          "law" in kinds and "floor" in kinds, f"kinds {sorted(kinds)}")

    print("=" * 70)
    print(f"BATTERY: {PASSED} passed, {FAILED} failed of {PASSED + FAILED}")
    print("=" * 70)
    sys.exit(0 if FAILED == 0 else 1)


if __name__ == "__main__":
    main()
