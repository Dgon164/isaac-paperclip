"""
MEANINGFUL ABSENCE — detect 'something that should be there but isn't'.

The Mendeleev move. Isaac learns the structure, then asks of every place the
structure COVERS: is something present here? Where the structure strongly
predicts presence but the data is empty -- an INTERIOR hole surrounded by
structure-conforming neighbors -- that absence is a FINDING, and its shape is
predicted. Places OUTSIDE the structure's support are NOT flagged (unknown is
not the same as should-be-there-but-isn't).

A meaningful absence then splits two ways:
  MISSING   -> predict it (Mendeleev: an undiscovered element).
  FORBIDDEN -> a null-law: it's actively suppressed (the dog that didn't bark).
This demo does the detection + MISSING prediction; the FORBIDDEN branch is where
the certified-NEVER machinery attaches.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac

rng = np.random.default_rng(0)
# a regular structure y = 2x+1, sampled at these positions -- with INTERIOR GAPS at 6 and 9,
# and nothing beyond 12 (that's the edge of what we've observed, not a gap).
present = [1, 2, 3, 4, 5, 7, 8, 10, 11, 12]
xs, ys = [], []
for x in present:
    xs += [x] * 25
    ys += list(2.0 * x + 1.0 + 0.2 * rng.normal(size=25))
X = np.array(xs, float).reshape(-1, 1); y = np.array(ys, float)

iz = Isaac()
r = iz.discover(X, y, name="struct")
lo, hi = min(present), max(present)
print("="*78)
print("  MEANINGFUL ABSENCE — what the structure says should be there, but isn't")
print("="*78)
print(f"  learned structure: {r['verdict']} R2 {r['r2']:.2f}  y = {r['equation'][:40]}")
print(f"  observed support: positions {lo}..{hi}\n")

present_set = set(present)
print("  scanning every position the structure covers:")
for c in range(lo, hi + 1):
    covered = True                                   # inside observed support
    interior = (c - 1 in present_set) or (c + 1 in present_set)   # has structure-conforming neighbors
    here = c in present_set
    if here:
        continue
    if covered and interior:
        pred = iz.apply_law("struct", np.array([[float(c)]]))
        pv = float(pred[0]) if pred is not None else float("nan")
        print(f"   x={c:2d}: MEANINGFUL ABSENCE — structure predicts something here (y~{pv:.1f}) but it's EMPTY.")
        print(f"          verdict: MISSING (should exist; predicted shape y~{pv:.1f}). Or FORBIDDEN — check for a suppressor.")

print("\n  contrast — a position OUTSIDE the observed support:")
c = 20
inside = lo <= c <= hi
print(f"   x={c}: {'gap' if inside else 'NOT flagged'} — outside support ({lo}..{hi}); this is UNKNOWN,")
print(f"          not 'should-be-there-but-isn't'. Absence at the edge carries no expectation.")
print("\n" + "="*78)
print("  It flags only the INTERIOR holes (6, 9) — absences the structure had a right to")
print("  expect filled — and predicts their shape. The edge (beyond 12) it leaves as unknown.")
print("="*78)
