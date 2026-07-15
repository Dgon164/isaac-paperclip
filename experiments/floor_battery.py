"""floor_battery.py — THE INSTRUMENT FLOOR ORGAN (data-ops segment §2).
Battery written FIRST, per discipline; the organ is built to pass it.

The law under test (owner, 2026-07-14): "no ruler, no perfect" —
exactness is INSTRUMENT-RELATIVE. Three roads to a floor, every
measurement kept, floor = the LARGEST evidenced noise scale:
  REPEATS  — duplicate-input rows; their answer-spread IS the noise
             (measured; needs >=5 groups and >=10 degrees of freedom)
  TOLD     — tell_resolution(name, sigma): usable at once, belief
             measured — FLAGGED (kept, never erased) when a measured
             road contradicts it
  GRAIN    — the quantization step read off the values; a LOWER BOUND
             only (grain-only floors under-evidence real process
             noise — probe lesson 2026-07-14, wrong-kept)
No road evidenced -> floor refused; the honest posture is
BEST-RESIDUAL-in-units + ASK for the instrument's resolution.
Everything stored is a supersedable record in the net (owner law
2026-07-15: every build = a tool in the chain).

Checks F1-F12. Run: PYTHONHASHSEED=0 python floor_battery.py
"""
import json
import os
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

rng = np.random.default_rng(42)
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" +
          (f"   {detail}" if detail else ""))


def q(y, g):
    return np.round(y / g) * g


def main():
    print("=" * 70)
    print("FLOOR BATTERY — the instrument floor organ")
    print("=" * 70)

    # ── F1: grain road reads a planted 0.001 quantization exactly ──
    m = mod.Isaac()
    y = q(rng.uniform(0, 10, 500), 0.001)
    r = m.read_floor(y)
    g = next((rd for rd in r["roads"] if rd["road"] == "grain"), None)
    ok = (g is not None and abs(g["step"] - 0.001) / 0.001 < 0.02
          and r["floor"] is not None)
    check("F1 grain 0.001 read exactly", ok,
          f"step {g['step']:.6g}" if g else "no grain road")

    # ── F2: grain road reads 1/16 exactly ──
    y = q(3.0 * rng.uniform(0, 30, 400), 1 / 16)
    r = m.read_floor(y)
    g = next((rd for rd in r["roads"] if rd["road"] == "grain"), None)
    ok = g is not None and abs(g["step"] - 1 / 16) / (1 / 16) < 0.02
    check("F2 grain 1/16 read exactly", ok,
          f"step {g['step']:.6g}" if g else "no grain road")

    # ── F3: truncated-CSV data — grain honestly coarser (storage res) ──
    y = q(rng.normal(50, 3, 400) + rng.normal(0, 0.0004, 400), 0.01)
    r = m.read_floor(y)
    g = next((rd for rd in r["roads"] if rd["road"] == "grain"), None)
    ok = g is not None and abs(g["step"] - 0.01) / 0.01 < 0.02
    check("F3 truncated CSV -> grain = storage resolution 0.01", ok,
          f"step {g['step']:.6g}" if g else "no grain road")

    # ── F4: float-continuous, no repeats, nothing told -> REFUSED ──
    y = rng.normal(0, 1, 400)
    r = m.read_floor(y)
    ok = (r["floor"] is None and r["exact_claimable"] is False
          and "ask" in r["why"].lower())
    check("F4 no road evidenced -> floor refused + ASK", ok, r["why"][:60])

    # ── F5: repeats road measures a planted sigma 0.12 ──
    xg = np.repeat(np.linspace(0.5, 6, 40), 8)
    rng.shuffle(xg)
    y = 1.5 * xg ** 2 + rng.normal(0, 0.12, len(xg))
    r = m.read_floor(y, X=xg.reshape(-1, 1))
    rep = next((rd for rd in r["roads"] if rd["road"] == "repeats"), None)
    ok = rep is not None and abs(rep["sigma"] - 0.12) / 0.12 < 0.15
    check("F5 repeats floor vs planted 0.12 (within 15%)", ok,
          f"measured {rep['sigma']:.4g}" if rep else "no repeats road")

    # ── F6: too few repeat groups -> repeats road NOT evidenced ──
    xg = np.repeat(np.array([1.0, 2.0, 3.0]), 2)          # 3 groups, dof 3
    y = xg + rng.normal(0, 0.1, len(xg))
    r = m.read_floor(y, X=xg.reshape(-1, 1))
    rep = next((rd for rd in r["roads"] if rd["road"] == "repeats"), None)
    check("F6 under-evidenced repeats (3 groups, dof 3) refused",
          rep is None)

    # ── F7: told road — usable at once, carries its provenance ──
    m.tell_resolution("volts", 0.05)
    y = rng.normal(0, 1, 300)                              # continuous
    r = m.read_floor(y, name="volts")
    ok = (r["floor"] == 0.05 and r["road"] == "told"
          and r["exact_claimable"] is True)
    check("F7 told resolution usable at once", ok,
          f"floor {r['floor']} via {r['road']}")

    # ── F8: told contradicted by measured — flagged, kept, max wins ──
    m.tell_resolution("amps", 0.01)
    xg = np.repeat(np.linspace(0.5, 6, 40), 8)
    rng.shuffle(xg)
    y = 2.0 * xg + rng.normal(0, 0.12, len(xg))
    r = m.read_floor(y, X=xg.reshape(-1, 1), name="amps")
    told = next((rd for rd in r["roads"] if rd["road"] == "told"), None)
    ok = (r["road"] == "repeats" and r["floor"] > 0.09
          and told is not None and told.get("contradicted") is True
          and "contradict" in r["why"].lower())
    check("F8 told 0.01 vs measured ~0.12: flagged, kept, max wins", ok,
          f"floor {r['floor']:.4g} via {r['road']}; told flagged: "
          f"{told.get('contradicted') if told else '-'}")

    # ── F9: grain-only provenance says LOWER BOUND ──
    m2 = mod.Isaac()
    y = q(rng.uniform(0, 10, 400), 0.001)
    r = m2.read_floor(y)
    g = next((rd for rd in r["roads"] if rd["road"] == "grain"), None)
    check("F9 grain-only floor carries 'lower bound' provenance",
          g is not None and "lower bound" in g.get("note", "").lower())

    # ── F10: provenance round-trips through packs ──
    m3 = mod.Isaac()
    m3.tell_resolution("pressure", 0.02)
    xg = np.repeat(np.linspace(1, 5, 30), 6)
    y = xg + rng.normal(0, 0.3, len(xg))
    r_before = m3.read_floor(y, X=xg.reshape(-1, 1), name="pressure")
    with tempfile.TemporaryDirectory() as td:
        m3.save_pack(td)
        m4 = mod.Isaac.load_pack(td)
    a = json.dumps(m3.net.get_meta("floor:pressure", "active"),
                   sort_keys=True, default=str)
    b = json.dumps(m4.net.get_meta("floor:pressure", "active"),
                   sort_keys=True, default=str)
    ta = json.dumps(m3.net.get_meta("floor:pressure", "told"),
                    sort_keys=True, default=str)
    tb = json.dumps(m4.net.get_meta("floor:pressure", "told"),
                    sort_keys=True, default=str)
    check("F10 floor + provenance survive the pack road",
          a == b and ta == tb and a != "null")

    # ── F11: re-measuring SUPERSEDES — old reading kept with why ──
    m5 = mod.Isaac()
    y1 = q(rng.uniform(0, 10, 400), 0.001)
    m5.read_floor(y1, name="length")
    y2 = q(rng.uniform(0, 10, 400), 0.01)                  # coarser tool
    r2 = m5.read_floor(y2, name="length")
    chain = m5.net.get_meta("floor:length", "superseded") or []
    ok = (len(chain) == 1
          and abs(chain[0]["record"]["floor"] - 0.001 / np.sqrt(12))
          / (0.001 / np.sqrt(12)) < 0.05
          and "why" in chain[0]
          and abs(r2["floor"] - 0.01 / np.sqrt(12))
          / (0.01 / np.sqrt(12)) < 0.05)
    check("F11 re-measure supersedes; old reading kept with why", ok,
          f"chain {len(chain)}; active floor {r2['floor']:.5g}")

    # ── F12: max-of-roads — grain 0.001 present, repeats 0.12 wins ──
    xg = np.repeat(np.linspace(0.5, 6, 40), 8)
    rng.shuffle(xg)
    y = q(1.5 * xg ** 2 + rng.normal(0, 0.12, len(xg)), 0.001)
    r = m5.read_floor(y, X=xg.reshape(-1, 1))
    names = sorted(rd["road"] for rd in r["roads"])
    ok = (r["road"] == "repeats" and "grain" in names
          and abs(r["floor"] - 0.12) / 0.12 < 0.15)
    check("F12 both roads kept; floor = max (repeats beats grain)", ok,
          f"roads {names}; floor {r['floor']:.4g}")

    # ── F13: the finding lands in the ledger organ ──
    hits = m5.recall_findings(kind="floor")
    check("F13 floor readings recorded as findings",
          len(hits) >= 2 and hits[0].get("name") == "length")

    # ── F14: one off-grid typo cannot blind the ruler ──
    # (audit battery A4 lesson, 2026-07-15: grain is a CONSENSUS of
    # gaps, never a unanimity — the violating value is itself a flag
    # candidate, not a reason to refuse the floor)
    y = q(rng.uniform(0, 15, 150), 0.01)
    y[7] += 0.004                              # the typo the audit hunts
    r = m5.read_floor(y)
    g = next((rd for rd in r["roads"] if rd["road"] == "grain"), None)
    ok = g is not None and abs(g["step"] - 0.01) / 0.01 < 0.02
    check("F14 grain by consensus survives one off-grid value", ok,
          f"step {g['step']:.6g}, consistency {g['consistency']:.3f}"
          if g else "no grain road")

    n_ok = sum(CHECKS)
    print("=" * 70)
    print(f"FLOOR BATTERY: {n_ok}/{len(CHECKS)}")
    print("=" * 70)
    sys.exit(0 if n_ok == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
