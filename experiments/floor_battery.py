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

Checks F1-F18. Run: PYTHONHASHSEED=0 python floor_battery.py

F15-F18 (2026-07-15, owner call "add outlier ejection" after the
bench's floor-contamination find): the repeats road gets the consensus
treatment the grain road already had (F14) — dissenting values are
ejected FROM THE MEASUREMENT by consensus, FILED in provenance (never
erased: the dissenters are exactly what the audit hunts), and a
majority dissent DISQUALIFIES the road instead of reading a confident
wrong floor. The vulnerability these gates pin: corruption >= ~6% of
rows inflated the pooled floor until the 4x-floor flag line outgrew
the corruption itself — the audit reported clean tables while blind
(probe_floor_contamination.py, recall 1.00 -> 0.00 between 5%% and
7.5%%).
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

    # ── F15: 10% planted corruption cannot drag the repeats floor ──
    # (the bench's find: pooled spread fed by the errors being hunted;
    # consensus ejection must keep the ruler at the true noise scale)
    m6 = mod.Isaac()
    xg = np.repeat(np.linspace(0.5, 6, 40), 8)
    rng.shuffle(xg)
    y = 2.0 * xg + rng.normal(0, 0.05, len(xg))
    bad = rng.choice(len(y), 32, replace=False)            # 10% of rows
    for i in bad:
        y[i] += float(rng.choice([-1.0, 1.0])) * 3.0
    r = m6.read_floor(y, X=xg.reshape(-1, 1))
    rep = next((rd for rd in r["roads"] if rd["road"] == "repeats"), None)
    ok = bool(rep is not None and 0.035 < rep["sigma"] < 0.075
              and rep.get("ejected", 0) >= 25
              and rep.get("ejected_groups"))
    check("F15 repeats floor survives 10% corruption (dissenters "
          "ejected + FILED)", ok,
          f"sigma {rep['sigma']:.4g}, ejected {rep.get('ejected')}"
          if rep else "no repeats road")

    # ── F16: the false-ejection control — clean data ejects NOTHING ──
    # (without this gate F15 means nothing: a floor that ejects honest
    # values would launder its own blindness the other way)
    m7 = mod.Isaac()
    y = 2.0 * xg + rng.normal(0, 0.05, len(xg))
    r = m7.read_floor(y, X=xg.reshape(-1, 1))
    rep = next((rd for rd in r["roads"] if rd["road"] == "repeats"), None)
    ok = (rep is not None and rep.get("ejected") == 0
          and abs(rep["sigma"] - 0.05) / 0.05 < 0.15)
    check("F16 clean world: zero ejections, sigma within 15% of planted",
          ok, f"sigma {rep['sigma']:.4g}, ejected {rep.get('ejected')}"
          if rep else "no repeats road")

    # ── F17: majority dissent DISQUALIFIES the road — never a
    # confident wrong floor (the self-disqualify move the audit's
    # recalibration already has, one level down) ──
    m8 = mod.Isaac()
    y = 2.0 * xg + rng.normal(0, 0.05, len(xg))
    bad = rng.choice(len(y), 128, replace=False)           # 40% of rows
    for i in bad:
        y[i] += float(rng.choice([-1.0, 1.0])) * 3.0
    r = m8.read_floor(y, X=xg.reshape(-1, 1))
    rep = next((rd for rd in r["roads"] if rd["road"] == "repeats"), None)
    ok = (rep is None and r["floor"] is None
          and "disagree" in r["why"].lower())
    check("F17 40% corruption: the road refuses (says the disagreement), "
          "never a wrong floor", ok, r["why"][:64])

    # ── F18: honest heavy tails are NOT mass-ejected ──
    # (t(3) noise, zero corruption: the ejection line must not shave a
    # heavy-tailed instrument into a false Gaussian; a small tail-trim
    # is the accepted, MEASURED trade — said here, on the record)
    m9 = mod.Isaac()
    y = 2.0 * xg + 0.05 * rng.standard_t(3, len(xg))
    r = m9.read_floor(y, X=xg.reshape(-1, 1))
    rep = next((rd for rd in r["roads"] if rd["road"] == "repeats"), None)
    ok = (rep is not None and rep.get("ejected", 99) <= 0.03 * len(y)
          and 0.05 < rep["sigma"] < 0.15)
    check("F18 heavy-tail t(3) clean: evidenced, <=3% tail-trim, "
          "sigma in [0.05, 0.15]", ok,
          f"sigma {rep['sigma']:.4g}, ejected {rep.get('ejected')}"
          if rep else "no repeats road")

    # ── F19-F22 (owner design 2026-07-15: "word and wrod should ...
    # just have a door between them connected through the typo
    # concept"): a mis-entered NUMBER is the same thing under a
    # different bit string — a VARIANT filed with a door to the grid,
    # NEVER a new ruler. The two cloud-campaign breaks these gates
    # pin: 4 slips of 150 blinded the grain road outright (W2b), and
    # ONE half-step slip rescaled the ruler 2x down while looking
    # maximally consistent (W2c). ──

    # F19: a few off-grid slips cannot blind the ruler
    m10 = mod.Isaac()
    y = q(rng.uniform(0, 15, 150), 0.01)
    for i, off in ((7, 0.004), (31, 0.004), (77, 0.004), (120, 0.004),
                   (55, 0.004), (90, 0.004), (101, 0.004), (140, 0.004)):
        y[i] += off                       # 8 slips of 150 (5.3%)
    r = m10.read_floor(y)
    g = next((rd for rd in r["roads"] if rd["road"] == "grain"), None)
    ok = bool(g is not None and abs(g["step"] - 0.01) / 0.01 < 0.02
              and g.get("off_grid_gaps", 0) >= 1
              and "mis-entry" in g.get("note", ""))
    check("F19 grain HELD through 8 slips of 150; dissent FILED as "
          "mis-entry", ok,
          f"step {g['step']:.6g}, off-grid gaps {g.get('off_grid_gaps')}"
          if g else "no grain road (blinded)")

    # F20: ONE half-step slip must not rescale the ruler (dense grid:
    # every honest gap is 0.01, so the slip's 0.005 gaps make the
    # half-step candidate look PERFECTLY consistent — the trap)
    m11 = mod.Isaac()
    y = np.round(5.0 + 0.01 * np.arange(300), 10)
    y[70] += 0.005                         # exactly half a step off
    r = m11.read_floor(y)
    g = next((rd for rd in r["roads"] if rd["road"] == "grain"), None)
    ok = bool(g is not None and abs(g["step"] - 0.01) / 0.01 < 0.02
              and g.get("off_grid_gaps", 0) >= 1)
    check("F20 half-step slip: ruler stays 0.01 (was: quietly "
          "rescaled to 0.005), slip filed", ok,
          f"step {g['step']:.6g}, off-grid gaps {g.get('off_grid_gaps')}"
          if g else "no grain road")

    # F21: the guard — a TRUE fine grain must still be read fine
    # (coarsest-consistent must not over-coarsen honest 0.005 data)
    m12 = mod.Isaac()
    y = q(rng.uniform(0, 15, 400), 0.005)
    r = m12.read_floor(y)
    g = next((rd for rd in r["roads"] if rd["road"] == "grain"), None)
    ok = bool(g is not None and abs(g["step"] - 0.005) / 0.005 < 0.02)
    check("F21 true 0.005 grain still read exactly (no over-coarsening)",
          ok, f"step {g['step']:.6g}" if g else "no grain road")

    # F22: majority off-grid is NOT a typo story — refuse
    m13 = mod.Isaac()
    y = q(rng.uniform(0, 15, 150), 0.01)
    idx = rng.choice(len(y), 60, replace=False)            # 40% smeared
    y[idx] += rng.uniform(0.001, 0.009, len(idx))
    r = m13.read_floor(y)
    g = next((rd for rd in r["roads"] if rd["road"] == "grain"), None)
    check("F22 40% off-grid: grain refused (beyond a typo story)",
          g is None)

    n_ok = sum(CHECKS)
    print("=" * 70)
    print(f"FLOOR BATTERY: {n_ok}/{len(CHECKS)}")
    print("=" * 70)
    sys.exit(0 if n_ok == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
