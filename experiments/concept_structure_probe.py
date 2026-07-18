"""concept_structure_probe.py — THE CONCEPT TOWER, rung 1 (owner,
2026-07-18: "he needs to be able to build conceptual structures. so
periodicity, or other relations that are not specifically about the
data, but about the structure of the data... furry would be coating
of many fur, and fur would be hair, and hair would be... line of
caratin").

RESEARCH, NOT THE ENGINE. The claim probed: some concepts carry no
content — their meaning IS ARRANGEMENT, with slots for what is
arranged. So ONE detector, fed atoms of any kind (numbers, words,
grid rows), should find THE SAME concept in all of them; things
then DOOR onto one concept node (identity = relations, kinship of
arrangement); and a TOLD concept tower (striped; furry) should be
RECOGNIZED in never-seen data from its structural definition alone
— zero examples, generation-not-duplication applied to concepts.

PREDICTIONS (filed before the first run; wrong ones kept)
  S1 REPEAT IN NUMBERS: a repeating numeric motif [5,2,7,1] is
     found (period 4, the motif SAID) past the shuffle null.
  S2 THE SAME DETECTOR, WORDS: "a b c d" repeating -> period 4 —
     not one line of detector code changed.
  S3 THE SAME DETECTOR, SPACE: striped grid rows -> alternation
     (period 2, two distinct atoms).
  S4 SCRAMBLED ALL THREE: nothing said (0 false structures).
  S5 ONE CONCEPT NODE: all three things door onto concept:repeat;
     each instance keeps its OWN period and motif (variants never
     smushed); scrambled things are absent.
  S6 KINSHIP RECEIPT: the cross-substrate grouping is recorded —
     "three substrates, one arrangement" as a finding.
  S7 THE TOLD TOWER, STRIPED: striped := alternate(two coats) —
     a fresh striped grid is RECOGNIZED, a speckled grid REFUSED.
  S8 THE TOLD TOWER, FURRY: furry := covering of MANY STRANDS on a
     surface; strand := line of cells (his 'line of keratin').
     A furry grid is RECOGNIZED; a bald grid REFUSED; and the
     killer control: the SAME number of cells SCATTERED (right
     material, wrong arrangement) is REFUSED — because the
     arrangement IS the concept.

Run: cd experiments && PYTHONHASHSEED=0 python concept_structure_probe.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac


# ── ONE detector for ANY atoms (the substrate-free claim) ──────────
def detect_repeat(seq, seed=5):
    """Best period by same-again match fraction, fundamental by the
    divisor rule, admitted past a shuffle null. Atoms are ANY
    hashables — numbers, words, whole grid rows."""
    seq = list(seq)
    n = len(seq)
    top = max(2, n // 3)

    def match(s, L):
        return sum(1 for i in range(n - L) if s[i] == s[i + L]) \
            / (n - L)

    ms = {L: match(seq, L) for L in range(1, top)}
    best_L = max(ms, key=lambda L: ms[L])
    for L in sorted(ms):
        if ms[L] >= 0.9 * ms[best_L] and best_L % L == 0:
            best_L = L
            break
    best_m = ms[best_L]
    rng = np.random.default_rng(seed)
    s2 = list(seq)
    null = 0.0
    for _ in range(20):
        rng.shuffle(s2)
        null = max(null, max(match(s2, L) for L in range(1, top)))
    if best_m <= null:
        return None
    return dict(period=int(best_L), match=round(best_m, 3),
                null=round(null, 3),
                motif=[str(a) for a in seq[:best_L]])


def reify(mind, thing, det):
    """An admitted arrangement becomes NET CONTENT: the thing doors
    onto ONE concept node; the instance keeps its own parameters."""
    node = "concept:repeat"
    mind.net.add_door("concepts", node, tag="concept")
    mind.net.add_door(str(thing), node, tag="has_structure")
    inst = f"structure:{thing}:repeat"
    mind.net.add_door(node, inst, tag="instance")
    mind.net.set_meta(inst, "instance", dict(det))
    mind.record_finding("structure", str(thing), concept="repeat",
                        period=det["period"], motif=det["motif"])


# ── the told towers: structural definitions, grounded ──────────────
def is_striped(grid_rows):
    """striped := alternate(two coats) — repeat with period 2 over
    two distinct atoms, detected, never pattern-matched by hand."""
    det = detect_repeat(grid_rows)
    return bool(det and det["period"] == 2
                and len(set(det["motif"])) == 2), det


def strands_on_surface(grid):
    """strand := a LINE of cells (the owner's 'line of keratin'):
    a vertical run of >=2 filled cells ATTACHED to the surface row.
    Returns the strand count (many-ness is judged by the caller)."""
    H, W = grid.shape
    count = 0
    for c in range(W):
        run = 0
        r = H - 2                       # the row above the surface
        while r >= 0 and grid[r, c]:
            run += 1
            r -= 1
        if run >= 2:
            count += 1
    return count


def is_furry(grid, many=8):
    """furry := covering of MANY strands on a surface — the tower:
    furry -> (many, attached, strand); strand -> line-of(cells)."""
    return strands_on_surface(grid) >= many


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    rng = np.random.default_rng(0)
    mind = Isaac()

    # the three substrates, one arrangement
    numbers = [5, 2, 7, 1] * 30
    words = ["a", "b", "c", "d"] * 30
    stripes = ["red", "blue"] * 15

    d1 = detect_repeat(numbers)
    ok1 = (d1 and d1["period"] == 4
           and d1["motif"] == ["5", "2", "7", "1"])
    check("S1 repeat in numbers — period 4, the motif said", bool(ok1),
          f"{d1}")

    d2 = detect_repeat(words)
    ok2 = d2 and d2["period"] == 4
    check("S2 the same detector, words — period 4, no code changed",
          bool(ok2), f"{d2}")

    d3 = detect_repeat(stripes)
    ok3 = (d3 and d3["period"] == 2 and len(set(d3["motif"])) == 2)
    check("S3 the same detector, space — stripes alternate", bool(ok3),
          f"{d3}")

    # S4 — scrambled controls say nothing
    false_hits = 0
    for seq in (numbers, words, stripes):
        s = list(seq)
        rng.shuffle(s)
        if detect_repeat(s) is not None:
            false_hits += 1
    check("S4 scrambled all three — nothing said", false_hits == 0,
          f"{false_hits}/3 false structures")

    # S5 — one concept node, three doors, variants kept
    for thing, det in (("thing:pulse", d1), ("thing:chant", d2),
                       ("thing:floor", d3)):
        reify(mind, thing, det)
    prof = mind.net.get_full_profile("concept:repeat")
    holders = {s for s in prof["in"]
               if "has_structure" in prof["in"][s]}
    inst_p = mind.net.get_meta("structure:thing:floor:repeat",
                               "instance")
    ok5 = (holders == {"thing:pulse", "thing:chant", "thing:floor"}
           and inst_p["period"] == 2
           and mind.net.get_meta("structure:thing:pulse:repeat",
                                 "instance")["period"] == 4)
    check("S5 one concept node — three substrates door on, variants "
          "kept", ok5, f"holders {sorted(holders)}")

    # S6 — the kinship receipt
    findings = [f for f in mind.findings
                if f.get("kind") == "structure"]
    mind.record_finding("structure_kinship", "repeat",
                        holders=sorted(holders),
                        why="three substrates, one arrangement")
    ok6 = len(findings) == 3
    check("S6 kinship recorded — three substrates, one arrangement",
          ok6, f"{len(findings)} structure findings + kinship record")

    # S7 — the told tower: striped, recognized fresh
    fresh = ["green", "gold"] * 20
    speck = list(rng.choice(["green", "gold"], 40))
    hit, _ = is_striped(fresh)
    miss, _ = is_striped(speck)
    check("S7 told tower STRIPED — fresh stripes recognized, "
          "speckle refused", hit and not miss,
          f"stripes {hit}, speckle {miss}")

    # S8 — the told tower: FURRY (the owner's exact example)
    H, W = 12, 40
    furry = np.zeros((H, W), bool)
    cols = rng.choice(W, 14, replace=False)
    for c in cols:                       # strands: lines attached
        furry[H - 1 - rng.integers(2, 6):H - 1, c] = True
    bald = np.zeros((H, W), bool)
    scattered = np.zeros((H, W), bool)
    ncells = int(furry.sum())
    flat = rng.choice(H * W, ncells, replace=False)
    scattered[np.unravel_index(flat, (H, W))] = True
    ok8 = (is_furry(furry) and not is_furry(bald)
           and not is_furry(scattered))
    mind.record_finding(
        "concept_tower", "furry",
        definition="covering of MANY strands on a surface",
        chain=["furry -> many + attached + strand",
               "strand -> line of cells"],
        receipts=dict(furry=strands_on_surface(furry),
                      bald=strands_on_surface(bald),
                      scattered=strands_on_surface(scattered)))
    check("S8 told tower FURRY — recognized; bald refused; SAME "
          "cells scattered refused (arrangement IS the concept)",
          ok8,
          f"strands: furry {strands_on_surface(furry)}, bald "
          f"{strands_on_surface(bald)}, scattered "
          f"{strands_on_surface(scattered)} (need >=8)")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
