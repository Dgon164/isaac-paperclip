"""
TOWER — reference / redundancy lens on tier-1 candidates (owner's reframe).
Question is NOT "857 > 50 = junk". It is: relate each candidate to the others
and to ALL layers. Is a candidate (a) a higher-order idea (its parts bind
beyond chance), or (b) redundant (a shadow of a bigger idea / a near-duplicate)?
Score against L1+L2+L3, not a flat L1 count.
"""
import random
import sys, os
import statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tower_bench as tb

ATOMS = 400
LAYERS = [50, 120, 300]
SPAN = (3, 6)
N_VIEWS = 15000
ROUNDS = 90000
SEED = 1


def jacc(a, b):
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter) if (a or b) else 0.0


def best_j(cand, truth_sets):
    best = 0.0
    for t in truth_sets:
        j = jacc(cand, t)
        if j > best:
            best = j
            if best == 1.0:
                break
    return best


def main():
    wrng = random.Random(SEED * 2654435761 + 13)
    layers, extent = tb.build_world(ATOMS, LAYERS, SPAN[0], SPAN[1], wrng)
    truth = {L: [set(e) for e in {tuple(x) for x in extent[L]}]
             for L in range(1, len(extent))}

    rng = random.Random(SEED + 7)
    views = tb.make_views(layers, [0.55], N_VIEWS, rng)
    kept = tb.mine_tier(views, ROUNDS, 4, 40, 100000, rng)
    cands = [frozenset(items) for (n, s, items) in kept]
    print("=" * 74)
    print(f"  REFERENCE/REDUNDANCY LENS on {len(cands)} tier-1 candidates")
    print(f"  true groups: L1={len(truth[1])}  L2={len(truth[2])}  L3={len(truth[3])}")
    print("=" * 74)

    # 1. which LAYER does each candidate most resemble? (home layer)
    home = {1: 0, 2: 0, 3: 0, "none": 0}
    jbylayer = {1: [], 2: [], 3: []}
    for c in cands:
        js = {L: best_j(c, truth[L]) for L in (1, 2, 3)}
        for L in (1, 2, 3):
            jbylayer[L].append(js[L])
        L = max(js, key=js.get)
        if js[L] < 0.34:
            home["none"] += 1
        else:
            home[L] += 1
    print("\n  each candidate's HOME layer (best-Jaccard argmax, >=0.34):")
    for k in (1, 2, 3, "none"):
        lab = f"L{k}" if k != "none" else "no home (real noise)"
        print(f"    {lab:22s} {home[k]:5d}  ({100*home[k]/len(cands):4.1f}%)")

    # 2. partial COVERAGE per layer: true groups with a candidate at J>=0.5
    print("\n  partial coverage — true groups with a candidate at J>=0.5:")
    for L in (1, 2, 3):
        covered = sum(1 for t in truth[L] if any(jacc(c, t) >= 0.5 for c in cands))
        exact = sum(1 for t in truth[L] if any(c == t for c in cands))
        print(f"    L{L}: {covered}/{len(truth[L])} covered (J>=0.5),  "
              f"{exact}/{len(truth[L])} exact")

    # 3. REDUNDANCY: dedup near-duplicates (J>=0.7) -> distinct ideas
    order = sorted(cands, key=lambda c: -len(c))
    reps = []
    for c in order:
        if not any(jacc(c, r) >= 0.7 for r in reps):
            reps.append(c)
    print(f"\n  redundancy: {len(cands)} candidates -> {len(reps)} distinct ideas "
          f"after near-duplicate merge (J>=0.7)")

    # 4. MADE-OF: how many distinct ideas are composed of >=2 other ideas?
    reps_sorted = sorted(reps, key=lambda c: len(c))
    made_of = 0
    primitive = 0
    for c in reps:
        parts = [r for r in reps_sorted if r < c and len(r) >= 2]
        # does a disjoint-ish combination of parts cover most of c?
        covered_atoms = set()
        used = 0
        for p in parts:
            if len(p - covered_atoms) >= 2:      # p adds new atoms
                covered_atoms |= p
                used += 1
            if len(covered_atoms & c) >= 0.8 * len(c):
                break
        if used >= 2 and len(covered_atoms & c) >= 0.8 * len(c):
            made_of += 1
        else:
            primitive += 1
    print(f"  made-of check: of {len(reps)} distinct ideas, {made_of} are composed "
          f"of >=2 smaller ideas (candidate higher-order), {primitive} are primitive")

    print("\n" + "=" * 74)
    print("  READ: if most 'junk' has an L2/L3 home and covers higher layers,")
    print("  it is spread higher structure, not noise -> the fix is RELATE+DEDUP")
    print("  (reference + redundancy), not a boundary cut / precision score.")
    print("=" * 74)


if __name__ == "__main__":
    main()
