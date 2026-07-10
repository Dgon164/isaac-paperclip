"""
TOWER — the candidates ARE the FCA lattice (a multi-parent trie), not a flat pile.
Compute the actual subset partial order on tier-1 candidates and read the structure:
  1. is it a multi-parent DAG? (parents per node)
  2. do the true L1/L2/L3 groups sit as nodes at increasing depth?
  3. WHERE does the trie truncate — the deep parents that never formed because
     their extents were never observed whole (the channel truncating the lattice top).
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


def main():
    wrng = random.Random(SEED * 2654435761 + 13)
    layers, extent = tb.build_world(ATOMS, LAYERS, SPAN[0], SPAN[1], wrng)
    truth = {L: [set(e) for e in {tuple(x) for x in extent[L]}]
             for L in range(1, len(extent))}

    rng = random.Random(SEED + 7)
    views = tb.make_views(layers, [0.55], N_VIEWS, rng)
    kept = tb.mine_tier(views, ROUNDS, 4, 40, 100000, rng)
    C = [set(items) for (n, s, items) in kept]
    n = len(C)
    print("=" * 76)
    print(f"  FCA LATTICE / MULTI-PARENT TRIE on {n} tier-1 candidates")
    print(f"  true: L1={len(truth[1])}  L2={len(truth[2])}  L3={len(truth[3])}")
    print("=" * 76)

    # --- subset partial order: children[i] = all proper subsets of C[i] among cands
    children = [[] for _ in range(n)]
    parents = [[] for _ in range(n)]
    for i in range(n):
        ci = C[i]; li = len(ci)
        for j in range(n):
            if i != j and len(C[j]) < li and C[j] < ci:
                children[i].append(j); parents[j].append(i)

    # immediate parents: a parent p is immediate if no other parent q is subset of p
    imm_parent_ct = []
    for j in range(n):
        ps = parents[j]
        imm = 0
        for p in ps:
            if not any(q != p and C[q] < C[p] for q in ps):
                imm += 1
        imm_parent_ct.append(imm)

    # depth = longest proper-subset chain below (atoms = depth 0)
    depth = [1] * n
    for i in sorted(range(n), key=lambda k: len(C[k])):
        depth[i] = 1 + max((depth[j] for j in children[i]), default=0)

    multi = sum(1 for x in imm_parent_ct if x > 1)
    roots = sum(1 for j in range(n) if not parents[j])
    print(f"\n  STRUCTURE:")
    print(f"    nodes with >1 immediate parent: {multi}/{n} ({100*multi/n:.0f}%) "
          f"-> {'multi-parent DAG' if multi else 'tree'}")
    print(f"    mean immediate parents/node: {st.mean(imm_parent_ct):.2f}")
    print(f"    depth range: {min(depth)}..{max(depth)}  "
          f"(a chain from a small set up to the biggest)")

    # --- locate the true groups in the order: best candidate, its depth, coverage
    print(f"\n  WHERE THE TRUE GROUPS LAND (best candidate per true group):")
    print(f"    {'layer':6}{'covered J>=0.5':>16}{'exact':>8}{'mean depth of match':>22}")
    for L in (1, 2, 3):
        depths, covered, exact = [], 0, 0
        for t in truth[L]:
            best_j, best_i = 0.0, -1
            for i in range(n):
                j = jacc(C[i], t)
                if j > best_j:
                    best_j, best_i = j, i
            if best_j >= 0.5:
                covered += 1; depths.append(depth[best_i])
            if best_i >= 0 and C[best_i] == t:
                exact += 1
        md = f"{st.mean(depths):.1f}" if depths else "  -"
        print(f"    L{L:<5}{covered}/{len(truth[L]):<14}{exact:>8}{md:>22}")

    # --- truncation: how deep does the lattice reach vs how deep it should
    print(f"\n  TRUNCATION — the lattice top that never formed:")
    for L in (1, 2, 3):
        # a true group is 'present' if some candidate is >=0.5 of it
        present = sum(1 for t in truth[L] if any(jacc(C[i], t) >= 0.5 for i in range(n)))
        print(f"    L{L}: {present}/{len(truth[L])} present as a lattice node "
              f"({100*present/len(truth[L]):.0f}%)  -> "
              f"{'INTACT' if present > 0.8*len(truth[L]) else 'TRUNCATED'}")
    print("=" * 76)
    print("  READ: L1 forms the base; each higher layer forms LESS, because a whole's")
    print("  extent is never observed complete enough to CLOSE into a lattice node.")
    print("  The top of the trie is missing -> deep parents must be INFERRED from")
    print("  shared children, not observed. That is the real recovery operation.")
    print("=" * 76)


if __name__ == "__main__":
    main()
