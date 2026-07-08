# -*- coding: utf-8 -*-
"""THE FOUNDRY STUDY — blind recovery of a DAG-holarchy world
(owner's generator, 2026-07-07). The metastructure challenge made
concrete: 500 atoms, 4 hidden layers (60/146/292/791 groups), mixed-order
membership, 55%-per-edge detection, 30% contaminated views.

BLIND PROTOCOL: the solver sees ONLY the views (sets of atom ids).
The truth is used exclusively for scoring, after.

The solver is THE TOWER CLIMB: co-occurrence past an analytic
independence null (Bonferroni-corrected) -> greedy cliques = certified
groups -> groups become TOKENS in the views -> the same machinery runs
again one level up. Levels climb until nothing new certifies.

Scoring per manifest: best-Jaccard of recovered extents against UNIQUE
truth extents per layer. COMPLETE numbers.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from foundry_port import forge

t0 = time.time()
print("forging the world (seed 1, faithful port, truth_dag verified)...")
world, views = forge()
print(f"  {len(views):,} usable views, mean size "
      f"{np.mean([len(v) for v in views]):.1f}  [{time.time()-t0:.0f}s]")

N_ATOMS = 500

# ═══ THE BLIND SOLVER ═══════════════════════════════════════════════
def climb(views, n_atoms, max_levels=5, alpha=0.01, min_lift=1.5,
          merge_j=None, floor=None):
    # merge_j/floor: v3/v4 experiments (shingle merge, block coherence).
    # Defaults = v2, the measured best recall config (L1 100%@J0.5,
    # 50%@0.8, 26.7% exact). v3 (merge .55 + cv coherence): precision
    # 17.4% but recall collapsed. v4 (merge .7 + floor .45): no winner.
    # The whipsaw is recorded; the principled fix is per-group
    # activation-model verification, queued.
    """Views of atom-ids only. Returns recovered groups per level, each
    group = (member token ids, atom extent)."""
    tokens = list(range(n_atoms))          # token id -> atom extent
    extents = [frozenset([a]) for a in range(n_atoms)]
    view_tok = [set(v) for v in views]
    levels = []
    all_ext = []
    consumed = set()
    for level in range(1, max_levels + 1):
        nT = len(tokens)
        M = np.zeros((len(view_tok), nT), dtype=np.float32)
        for vi, v in enumerate(view_tok):
            for t in v:
                M[vi, t] = 1.0
        n = M.sum(0)
        Nv = len(view_tok)
        C = M.T @ M
        # analytic independence null: co-occurrence ~ Poisson(E),
        # Bonferroni over live pairs (the A2 spirit: a TEST, degrees-aware)
        E = np.outer(n, n) / Nv
        with np.errstate(divide="ignore", invalid="ignore"):
            z = (C - E) / np.sqrt(E + 1e-9)
        live = (n > 20)
        n_pairs = max(int(live.sum()) ** 2 / 2, 1)
        from math import erfc, sqrt
        z_gate = 0.0
        # invert Bonferroni via search (cheap)
        lo, hi = 3.0, 12.0
        for _ in range(40):
            mid = (lo + hi) / 2
            p = 0.5 * erfc(mid / sqrt(2)) * n_pairs
            if p > alpha:
                lo = mid
            else:
                hi = mid
        z_gate = hi
        lift = C / (E + 1e-9)
        adj = (z > z_gate) & (lift > min_lift) & live[:, None] & live[None, :]
        np.fill_diagonal(adj, False)
        # RESIDUAL DISCIPLINE: edges already explained by certified
        # groups are consumed - the residual is the next level's data
        for m1, m2 in consumed:
            if m1 < nT and m2 < nT:
                adj[m1, m2] = adj[m2, m1] = False
        # greedy cliques, strongest edges first, with COHERENCE: a true
        # group's sibling edges share one visibility process - a new
        # member must hold comparable lift to EVERY current member
        order = np.argwhere(np.triu(adj))
        strengths = z[order[:, 0], order[:, 1]]
        order = order[np.argsort(-strengths)]
        used_pairs = set()
        found = []
        for a, b in order[:4000]:
            if (a, b) in used_pairs:
                continue
            clique = {int(a), int(b)}
            base_lift = lift[a, b]
            cands = sorted(np.where(adj[a] & adj[b])[0],
                           key=lambda c: -min(z[c, a], z[c, b]))
            for c in cands:
                if len(clique) >= 6:
                    break
                if not all(adj[c, m] for m in clique):
                    continue
                mlift = min(lift[c, m] for m in clique)
                if mlift < 0.5 * base_lift:
                    continue                    # different tier: not kin
                clique.add(int(c))
            if len(clique) < 3:
                continue
            key = frozenset(clique)
            if any(key <= f or f <= key for f in found):
                continue
            found.append(key)
            for m1 in clique:
                for m2 in clique:
                    if m1 < m2:
                        used_pairs.add((m1, m2))
        if not found:
            break
        # SHINGLE AGGLOMERATION: near-copies of one group are ONE group
        # (tight overlap only, no chain-fusion, never mangle the union)
        merged = []
        if merge_j is None:
            merged = list(found)
        for g in (found if merge_j is not None else []):
            hit = None
            for mg in merged:
                u = g | mg
                if len(g & mg) / len(u) >= merge_j and len(u) <= 8:
                    hit = mg
                    break
            if hit is not None:
                merged.remove(hit)
                merged.append(hit | g)
            else:
                merged.append(g)
        # BLOCK COHERENCE: a true group's member pairs ride ONE
        # activation process - their implied activation counts must
        # agree; incoherent claims are refused
        coherent = []
        if floor is None:
            coherent = list(merged)
        for g in (merged if floor is not None else []):
            gl = sorted(g)
            counts = [C[a_, b_] for i_, a_ in enumerate(gl)
                      for b_ in gl[i_ + 1:]]
            counts = np.array(counts, float)
            # overlap inflates SOME pairs (co-membership elsewhere) - a
            # true group needs a common FLOOR, not uniformity
            if np.median(counts) > 0 and                     counts.min() / np.median(counts) >= floor:
                coherent.append(g)
        found = coherent
        if not found:
            break
        # SUPERSESSION dedup: an extent already held (J>=0.9) by any
        # prior certification is not a new thing
        new_ext = []
        for g in found:
            ext = frozenset().union(*[extents[m] for m in g])
            dup = any(len(ext & e) / len(ext | e) >= 0.9
                      for e in all_ext)
            if not dup:
                new_ext.append((g, ext))
                all_ext.append(ext)
            for m1 in g:
                for m2 in g:
                    if m1 < m2:
                        consumed.add((m1, m2))
        if not new_ext:
            print(f"  level {level}: nothing NOVEL certifies - the tower "
                  f"rests  [{time.time()-t0:.0f}s]")
            break
        levels.append(new_ext)
        base = len(tokens)
        for gi, (g, ext) in enumerate(new_ext):
            tokens.append(base + gi)
            extents.append(ext)
        # group token active in a view when >=2 member tokens present
        for vi, v in enumerate(view_tok):
            add = set()
            for gi, (g, ext) in enumerate(new_ext):
                need = max(2, int(np.ceil(0.45 * len(g))))
                if len(v & g) >= need:
                    add.add(base + gi)
            view_tok[vi] = v | add
        print(f"  level {level}: {len(found)} groups certified "
              f"(z-gate {z_gate:.1f})  [{time.time()-t0:.0f}s]")
    return levels

print("\nBLIND CLIMB (the solver sees only views):")
levels = climb(views, N_ATOMS)

# ═══ SCORING (the answer key, used only now) ════════════════════════
print("\nSCORING against unique truth extents per layer:")
truth = {}
for L in range(1, len(world["extent"])):
    uniq = {}
    for ext in world["extent"][L]:
        uniq[tuple(ext)] = uniq.get(tuple(ext), 0) + 1
    truth[L] = [frozenset(e) for e in uniq]

def jac(a, b):
    return len(a & b) / len(a | b)

all_recovered = [ext for lvl in levels for (_, ext) in lvl]
print(f"  recovered groups total: {len(all_recovered)}")
for L in sorted(truth):
    tg = truth[L]
    best = [max((jac(t, r) for r in all_recovered), default=0.0)
            for t in tg]
    best = np.array(best)
    print(f"  truth layer {L} ({len(tg)} unique groups): "
          f"EXACT {np.mean(best >= 0.999)*100:5.1f}%  "
          f"J>=0.8 {np.mean(best >= 0.8)*100:5.1f}%  "
          f"J>=0.5 {np.mean(best >= 0.5)*100:5.1f}%  "
          f"mean best-J {best.mean():.3f}")
# precision: of what was recovered, how much matches SOME truth extent
truth_all = [t for L in truth for t in truth[L]]
prec = [max((jac(r, t) for t in truth_all), default=0.0)
        for r in all_recovered]
prec = np.array(prec)
print(f"  precision: {np.mean(prec >= 0.8)*100:.1f}% of recovered groups "
      f"match a true group at J>=0.8 (mean {prec.mean():.3f})")
print(f"\ntotal time {time.time()-t0:.0f}s")
