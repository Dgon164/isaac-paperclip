"""
TOWER BENCH — Python port of Foundry + Crystallizer v4, to run the ONE
registered-but-untested experiment from the Comparison Tower v2 (section 8):

    "the mixed-detection-rate prescription (registered, untested): a mixture
     should beat any single rate for whole-tower recovery."

Every resolver so far (crystallizer v1-v4) used a SINGLE detection rate = one
focal depth. The theory says hierarchy is written in the dropout and L2 recovery
is non-monotone in detection (peaks ~0.65) -- so a single rate can only surface
one floor well. This runs the same world + the same v4 resolver at a single rate
vs a MIXTURE of rates (same total views) and compares per-layer recovery.

Faithful port of foundry.jsx/foundry_v2.jsx (buildWorld, viewDropout) and
crystallizer_v4.jsx (mineTier+absorption, parseViews explanatory-cover, the tier
loop with the compression invariant). Scoring is extensional best-Jaccard vs
unique extents, exactly as the JS.
"""
import math
import random
import sys


# ---------------- Foundry: world + dropout observation ----------------
def build_world(n_atoms, layer_sizes, span_lo, span_hi, rng):
    layers = [list(range(n_atoms))]
    for L in range(1, len(layer_sizes) + 1):
        groups = []
        for _ in range(layer_sizes[L - 1]):
            span = span_lo + int(rng.random() * (span_hi - span_lo + 1))
            members, seen = [], set()
            while len(members) < span:
                r = rng.random()
                if r < 0.6 or L == 1:
                    ml = L - 1
                elif r < 0.85 and L >= 2:
                    ml = L - 2
                else:
                    ml = int(rng.random() * L)
                mi = int(rng.random() * (n_atoms if ml == 0 else layer_sizes[ml - 1]))
                if (ml, mi) not in seen:
                    seen.add((ml, mi)); members.append((ml, mi))
            groups.append(members)
        layers.append(groups)
    extent = [[None] * (n_atoms if L == 0 else len(layers[L])) for L in range(len(layers))]

    def flat(L, i):
        if L == 0:
            return [i]
        if extent[L][i] is not None:
            return extent[L][i]
        s = set()
        for (ml, mi) in layers[L][i]:
            s.update(flat(ml, mi))
        extent[L][i] = sorted(s)
        return extent[L][i]

    for L in range(1, len(layers)):
        for i in range(len(layers[L])):
            flat(L, i)
    return layers, extent


def sample_view(layers, detect, rng):
    top = len(layers) - 1
    out = []

    def expand(L, i):
        if L == 0:
            out.append(i); return
        for (ml, mi) in layers[L][i]:
            if rng.random() < detect:
                expand(ml, mi)

    draws = 2 if rng.random() < 0.3 else 1
    for _ in range(draws):
        expand(top, int(rng.random() * len(layers[top])))
    return list(set(out))


def make_views(layers, rates, n_views, rng):
    """rates: a list; each view samples one rate uniformly (mixture = >1 rate)."""
    views = []
    while len(views) < n_views:
        det = rates[int(rng.random() * len(rates))]
        v = sample_view(layers, det, rng)
        if v:
            views.append(v)
    return views


# ---------------- Crystallizer v4: mine (absorption) + parse ----------------
def mine_tier(views, rounds, min_sup, max_set, cap, rng):
    index = {}
    for vi, v in enumerate(views):
        for a in v:
            arr = index.setdefault(a, [])
            if len(arr) < 500:
                arr.append(vi)
    support = {}
    nv = len(views)
    for _ in range(rounds):
        v1 = views[int(rng.random() * nv)]
        if len(v1) < 2:
            continue
        a = v1[int(rng.random() * len(v1))]
        pool = index[a]
        v2 = views[pool[int(rng.random() * len(pool))]]
        s2 = set(v2)
        I = [x for x in v1 if x in s2]
        if len(I) < 2 or len(I) > max_set:
            continue
        I.sort(key=lambda x: str(x))
        key = "|".join(map(str, I))
        rec = support.get(key)
        if rec:
            rec[0] += 1
        else:
            support[key] = [1, I]
    cands = [v for v in support.values() if v[0] >= min_sup]
    # ABSORPTION: big-first; absorbed by a kept superset with support >= 0.4x
    cands.sort(key=lambda c: (-len(c[1]), -c[0]))
    kept = []       # each: [n, itemset, items]
    by_item = {}
    for (n, I) in cands:
        absorbed = False
        for ki in by_item.get(I[0], ()):
            Kn, Kset, Kitems = kept[ki]
            if len(Kitems) <= len(I) or Kn < 0.4 * n:
                continue
            if all(x in Kset for x in I):
                absorbed = True; break
        if absorbed:
            continue
        ki = len(kept)
        kept.append([n, set(I), I])
        for x in I:
            by_item.setdefault(x, []).append(ki)
        if len(kept) >= cap:
            break
    return kept


def parse_views(views, groups, recog_frac):
    member_index = {}
    for gi, g in enumerate(groups):
        for m in g["members"]:
            member_index.setdefault(m, []).append(gi)
    out = []
    for v in views:
        present = set(v)
        hits = {}
        for item in v:
            for gi in member_index.get(item, ()):
                hits[gi] = hits.get(gi, 0) + 1
        consumed, tokens = set(), []
        for _ in range(40):
            best, best_cover = -1, 0
            for gi, n0 in hits.items():
                g = groups[gi]; ml = len(g["members"])
                need = max(2, math.ceil(recog_frac * ml))
                if n0 < need:
                    continue
                cover = sum(1 for m in g["members"] if m in present and m not in consumed)
                if cover >= need and cover > best_cover:
                    best, best_cover = gi, cover
            if best < 0:
                break
            tokens.append(groups[best]["id"])
            for m in groups[best]["members"]:
                if m in present:
                    consumed.add(m)
        rest = [x for x in v if x not in consumed]
        out.append(rest + tokens)
    return out


def resolve(views, rounds, max_tiers, recog_frac, rng, log=None):
    vocab = []
    tok = 0
    ext_cache = {}

    def atom_extent(item):
        return [item] if isinstance(item, int) else list(ext_cache[item])

    def mean_size(vs):
        return sum(len(v) for v in vs) / max(1, len(vs))

    prev = mean_size(views)
    for tier in range(1, max_tiers + 1):
        kept = mine_tier(views, rounds, 4, 40, 1500, rng)
        if not kept:
            break
        fresh = []
        for (n, itemset, items) in kept:
            gid = "t%d" % tok; tok += 1
            ext = set()
            for m in items:
                ext.update(atom_extent(m))
            ext_cache[gid] = ext
            fresh.append({"id": gid, "members": items, "extent": ext})
        vocab.extend(fresh)
        views = parse_views(views, fresh, recog_frac)
        size = mean_size(views)
        ratio = size / max(prev, 1e-9)
        if log is not None:
            log.append(f"    tier {tier}: {len(kept)} kept, mean view {prev:.1f}->{size:.1f} "
                       f"({'compressed' if ratio < 1 else 'INFLATED'} x{ratio:.2f})")
        if ratio >= 1.0:
            break
        prev = size
    return vocab


def score(vocab, extent):
    cand = [g["extent"] for g in vocab]
    rows = []
    for L in range(1, len(extent)):
        uniq = {tuple(e): set(e) for e in extent[L]}
        truths = list(uniq.values())
        exact = 0; jsum = 0.0
        for t in truths:
            best = 0.0
            for cs in cand:
                inter = len(t & cs)
                j = inter / (len(t) + len(cs) - inter)
                if j > best:
                    best = j
                if best == 1.0:
                    break
            jsum += best; exact += (best == 1.0)
        rows.append((L, exact, len(truths), jsum / max(1, len(truths))))
    return rows


def run_condition(name, layers, extent, rates, n_views, rounds, max_tiers, recog, seed):
    rng = random.Random(seed)
    log = [f"  [{name}] rates={rates}, views={n_views}, rounds={rounds}"]
    views = make_views(layers, rates, n_views, rng)
    log.append(f"    mean raw view size: {sum(len(v) for v in views)/len(views):.1f}")
    vocab = resolve(views, rounds, max_tiers, recog, rng, log)
    rows = score(vocab, extent)
    for (L, ex, tot, mj) in rows:
        log.append(f"    layer {L}: {ex}/{tot} exact, overlap {mj*100:.1f}%")
    return rows, log


def main():
    ATOMS = 400
    LAYERS = [50, 120, 300]      # 3 floors above atoms (depth 3)
    SPAN = (3, 6)
    N_VIEWS = 25000
    ROUNDS = 120000
    MAX_TIERS = 4
    RECOG = 0.5
    SEED = 1

    wrng = random.Random(SEED * 2654435761 + 13)
    layers, extent = build_world(ATOMS, LAYERS, SPAN[0], SPAN[1], wrng)
    print("=" * 78)
    print(f"  TOWER BENCH — world {ATOMS} atoms, layers {LAYERS}")
    print("  single detection rate vs MIXED rates (the registered-untested lever)")
    print("=" * 78)

    conds = [
        ("single-0.55", [0.55]),
        ("single-0.65", [0.65]),
        ("MIXED-35/55/75", [0.35, 0.55, 0.75]),
    ]
    results = {}
    for name, rates in conds:
        rows, log = run_condition(name, layers, extent, rates, N_VIEWS, ROUNDS,
                                  MAX_TIERS, RECOG, SEED + 7)
        results[name] = rows
        print("\n".join(log))
        print()

    print("=" * 78)
    print("  SUMMARY — exact recovery per layer (higher = better)")
    hdr = "  " + "layer".ljust(8) + "".join(n.rjust(18) for n, _ in conds)
    print(hdr)
    nL = len(next(iter(results.values())))
    for li in range(nL):
        L = results[conds[0][0]][li][0]
        cells = []
        for name, _ in conds:
            ex, tot = results[name][li][1], results[name][li][2]
            cells.append(f"{ex}/{tot}".rjust(18))
        print("  " + f"L{L}".ljust(8) + "".join(cells))
    print("=" * 78)


if __name__ == "__main__":
    main()
