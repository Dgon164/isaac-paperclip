"""
TOWER — the RIGHT success metric (owner's, 2026-07-10): not per-layer exact match
in one snapshot, but "how much of the WORLD is known, and is any IDEA known
PERFECTLY" — its whole decomposition present, all the way down to atoms. An idea
with a hole anywhere in its tree is a FAILED state. Cost to get there is irrelevant.

Runs the FULL recursive resolver (all tiers) and reports:
  - total structures discovered across all layers (coverage)
  - the COMPLETENESS PYRAMID: for how many true groups is the ENTIRE recursive
    decomposition present (a "perfectly known idea") vs only partial (failed).
"""
import random
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tower_bench as tb

ATOMS = 400
LAYERS = [50, 120, 300]
SPAN = (3, 6)
N_VIEWS = 25000
ROUNDS = 120000
MAX_TIERS = 5
RECOG = 0.5
SEED = 1
RATES = [0.35, 0.55, 0.75]   # cost-agnostic: use the best lever we have (mixed)


def jacc(a, b):
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter) if (a or b) else 0.0


def main():
    wrng = random.Random(SEED * 2654435761 + 13)
    layers, extent = tb.build_world(ATOMS, LAYERS, SPAN[0], SPAN[1], wrng)

    rng = random.Random(SEED + 7)
    views = tb.make_views(layers, RATES, N_VIEWS, rng)
    vocab = tb.resolve(views, ROUNDS, MAX_TIERS, RECOG, rng)
    recovered = [g["extent"] for g in vocab]
    rec_exact = set(frozenset(e) for e in recovered)
    print("=" * 76)
    print(f"  WORLD COVERAGE + COMPLETENESS  (full resolver, rates {RATES})")
    print(f"  world: {ATOMS} atoms + {sum(len(layers[L]) for L in range(1,len(layers)))} "
          f"structures ({LAYERS}); recovered vocab: {len(vocab)} nodes")
    print("=" * 76)

    # present[(L,i)] : is this true group's extent recovered? exact and near(J>=0.9)
    def present(atom_set, thr):
        aset = set(atom_set)
        if frozenset(aset) in rec_exact:
            return True
        if thr < 1.0:
            for r in recovered:
                if len(r) and jacc(aset, r) >= thr:
                    return True
        return False

    for thr, label in ((1.0, "PERFECT (exact extent)"), (0.9, "near (J>=0.9)")):
        pres = {}
        for L in range(1, len(layers)):
            for i in range(len(layers[L])):
                pres[(L, i)] = present(extent[L][i], thr)
        # completeness bottom-up: complete iff present AND every member complete
        comp = {}

        def complete(L, i):
            if (L, i) in comp:
                return comp[(L, i)]
            if L == 0:
                return True
            ok = pres[(L, i)] and all(complete(ml, mi) for (ml, mi) in layers[L][i])
            comp[(L, i)] = ok
            return ok

        print(f"\n  --- {label} ---")
        print(f"    {'layer':7}{'present':>12}{'COMPLETE idea':>16}"
              f"{'(full decomposition, no holes)':>32}")
        tot_p = tot_c = tot_n = 0
        for L in range(1, len(layers)):
            nL = len(layers[L])
            p = sum(pres[(L, i)] for i in range(nL))
            c = sum(complete(L, i) for i in range(nL))
            tot_p += p; tot_c += c; tot_n += nL
            print(f"    L{L:<6}{p}/{nL:<10}{c}/{nL:<10}"
                  f"{'  '+ ('OK' if c>0.8*nL else 'FAILED at this layer'):>32}")
        print(f"    {'TOTAL':7}{tot_p}/{tot_n:<10}{tot_c}/{tot_n:<10}"
              f"{'  world known-perfectly: '+f'{100*tot_c/tot_n:.0f}%':>32}")

    print("\n" + "=" * 76)
    print("  READ: coverage is a pyramid — the base is fully known, the top is not,")
    print("  so COMPLETE ideas exist only near the floor. Deep ideas are failed states")
    print("  because a node in their tree was never observed whole enough to close.")
    print("  'Don't care what it takes' => the fix must INFER never-fully-seen nodes")
    print("  (assemble partials into a posited whole); observing more of the same at")
    print("  any budget can't complete them (a deep extent ~never appears whole).")
    print("=" * 76)


if __name__ == "__main__":
    main()
