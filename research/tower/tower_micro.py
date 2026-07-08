"""
TOWER MICROSCOPE — atoms -> L1, concretely. What does tier 1 actually CREATE,
vs the L1 groups we expect? "50/50 exact" is RECALL only; it hides how many
junk candidates ride along, and what they are. This dissects tier-1 output.
"""
import random
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tower_bench as tb

ATOMS = 400
LAYERS = [50, 120, 300]
SPAN = (3, 6)
N_VIEWS = 15000
ROUNDS = 90000
SEED = 1


def classify(cand, l1_sets, l1_by_size, all_true_by_layer):
    """cand: frozenset of atoms. Return (category, detail)."""
    if cand in l1_sets:
        return "exact_L1"
    # exact match to a higher-layer extent?
    for L, s in all_true_by_layer.items():
        if L >= 2 and cand in s:
            return f"exact_L{L}"
    # relationship to the best-overlapping L1 group
    best_j, best_g = 0.0, None
    overlapped = 0
    for g in l1_by_size:
        inter = len(cand & g)
        if inter:
            overlapped += 1
            j = inter / (len(cand) + len(g) - inter)
            if j > best_j:
                best_j, best_g = j, g
    if best_g is None:
        return "disjoint_junk"
    if cand < best_g:
        return "fragment (subset of one L1)"
    if cand > best_g:
        return "superset of one L1"
    if overlapped >= 2:
        return "cross (spans >=2 L1 groups)"
    return "partial (overlaps one L1, neither sub/super)"


def main():
    wrng = random.Random(SEED * 2654435761 + 13)
    layers, extent = tb.build_world(ATOMS, LAYERS, SPAN[0], SPAN[1], wrng)

    true_by_layer = {L: set(frozenset(e) for e in extent[L])
                     for L in range(1, len(extent))}
    l1_sets = true_by_layer[1]
    l1_list = [set(g) for g in l1_sets]

    print("=" * 74)
    print(f"  TOWER MICROSCOPE — atoms -> L1  (world {ATOMS} atoms, layers {LAYERS})")
    print("=" * 74)
    print(f"  true L1 groups: {len(l1_sets)} unique extents "
          f"(sizes {min(len(g) for g in l1_sets)}-{max(len(g) for g in l1_sets)})")

    rng = random.Random(SEED + 7)
    views = tb.make_views(layers, [0.55], N_VIEWS, rng)
    print(f"  {N_VIEWS} views @ detect 0.55, mean size "
          f"{sum(len(v) for v in views)/len(views):.1f} atoms\n")

    kept = tb.mine_tier(views, ROUNDS, 4, 40, 100000, rng)  # cap high: keep them all
    cands = [frozenset(items) for (n, s, items) in kept]
    supports = [n for (n, s, items) in kept]
    print(f"  tier-1 candidates after absorption: {len(cands)}")

    # recall: how many true L1 groups have an exact candidate?
    cand_set = set(cands)
    l1_recall = sum(1 for g in l1_sets if g in cand_set)
    print(f"  L1 recall: {l1_recall}/{len(l1_sets)} true groups appear exactly\n")

    # categorize every candidate
    cats = {}
    examples = {}
    for c in cands:
        cat = classify(c, l1_sets, l1_list, true_by_layer)
        cats[cat] = cats.get(cat, 0) + 1
        if cat not in examples and cat != "exact_L1":
            examples[cat] = c
    print("  WHAT THE 1000s OF CANDIDATES ACTUALLY ARE:")
    for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
        pct = 100 * n / len(cands)
        print(f"    {cat:34s} {n:6d}  ({pct:4.1f}%)")
    prec = 100 * cats.get("exact_L1", 0) / len(cands)
    print(f"\n  PRECISION: {cats.get('exact_L1',0)}/{len(cands)} candidates are true L1 "
          f"= {prec:.1f}%   (recall was {100*l1_recall/len(l1_sets):.0f}%)")

    # support: do true L1 groups outrank the junk by support?
    true_sup = [n for (n, s, items) in kept if frozenset(items) in l1_sets]
    junk_sup = [n for (n, s, items) in kept if frozenset(items) not in l1_sets]
    import statistics as st
    print(f"\n  support (co-occurrence count) — can a threshold separate them?")
    print(f"    true L1 candidates : median {st.median(true_sup):.0f}, "
          f"range {min(true_sup)}-{max(true_sup)}")
    print(f"    junk candidates    : median {st.median(junk_sup):.0f}, "
          f"range {min(junk_sup)}-{max(junk_sup)}")

    # a couple of concrete examples of the dominant junk category
    print(f"\n  concrete examples:")
    for cat in ("cross (spans >=2 L1 groups)", "superset of one L1",
                "fragment (subset of one L1)", "exact_L2"):
        if cat in examples:
            c = examples[cat]
            # which L1 groups does it touch?
            touched = [i for i, g in enumerate(l1_list) if c & g]
            print(f"    [{cat}] size {len(c)} touches L1 groups {touched[:6]}"
                  f"{'...' if len(touched) > 6 else ''}")

    # what does re-tokenization then hand to L2?
    groups = [{"id": "t%d" % i, "members": list(items), "extent": frozenset(items)}
              for i, (n, s, items) in enumerate(kept)]
    parsed = tb.parse_views(views, groups, 0.5)
    tok_total = tok_true = 0
    id_is_true = {("t%d" % i): (frozenset(items) in l1_sets)
                  for i, (n, s, items) in enumerate(kept)}
    for v in parsed:
        for x in v:
            if isinstance(x, str):
                tok_total += 1
                tok_true += id_is_true.get(x, False)
    print(f"\n  RE-TOKENIZATION handed to L2: of {tok_total} tokens placed in views, "
          f"{100*tok_true/max(1,tok_total):.1f}% are true-L1 tokens "
          f"(the rest is what L2 must mine through).")
    print("=" * 74)


if __name__ == "__main__":
    main()
