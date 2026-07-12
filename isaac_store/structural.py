"""Multicycle structural patterning (owner design, 2026-07-12):
"find the atoms of different things, then go through the cycle to
select the constraints that he can set and output the pattern type
that satisfies those constraints" — basically a flow-logic chart.

The cycle, per level:
  ATOMS -> measure constraint families, EACH behind a shuffle null:
    - always-follows   (deterministic links: A -> B every time)
    - forks            (after A: B or C, each seen, nothing else)
    - periodicity      (an atom returns on a regular beat)
    - balanced pairs   (open/close nesting, depth >= 2)
    - never-follows    (frequent pair that never touches — negatives
                        are first-class)
  -> the PATTERN TYPE that satisfies the admitted set:
     HIERARCHY / CYCLE / BRANCH / CHAIN / REPEAT / NO STRUCTURE
     (a refusal is the honest answer for shuffled noise)
  -> MULTICYCLE: admitted chains COLLAPSE into single higher atoms
     and the cycle runs again — patterns of patterns, the tower.

Everything measured, nothing hand-told: a constraint family is only
spoken of when the real sequence beats its own shuffles.
"""
import re

import numpy as np


def atoms_of(x, slot_min_count=5):
    """Text -> word/punct atoms (rare tokens become the SLOT atom —
    variation is a measured fact, not noise to trip on); list -> as-is."""
    if isinstance(x, str):
        toks = re.findall(r"[A-Za-z_]+|\d+(?:\.\d+)?|[^\sA-Za-z\d]", x.lower())
        from collections import Counter
        c = Counter(toks)
        return [t if c[t] >= slot_min_count else "<slot>" for t in toks]
    return list(x)


def _successors(seq):
    succ = {}
    for a, b in zip(seq, seq[1:]):
        succ.setdefault(a, []).append(b)
    return succ


def _det_links(seq, min_count=3):
    return {a: nx[0] for a, nx in _successors(seq).items()
            if len(nx) >= min_count and len(set(nx)) == 1}


def _fork_candidates(seq, min_count=6):
    out = {}
    for a, nx in _successors(seq).items():
        kinds = sorted(set(nx))
        if 2 <= len(kinds) <= 3 and len(nx) >= min_count and \
                all(nx.count(k) >= 2 for k in kinds):
            out[a] = kinds
    return out


def _periodic(seq, min_occ=5):
    """Exact recurrence only (gap std == 0): min_occ equally spaced
    hits are chance-proof — no null needed, chance cannot fake it."""
    out = {}
    pos = {}
    for i, a in enumerate(seq):
        pos.setdefault(a, []).append(i)
    for a, ps in pos.items():
        if len(ps) < min_occ:
            continue
        gaps = np.diff(ps)
        if len(set(gaps.tolist())) == 1:
            out[a] = int(gaps[0])
    return out


def _try_balance(seq, opener, closer, min_deep_episodes=3):
    """Real nesting NESTS, repeatedly: episode after episode reaches
    depth >= 2 and closes back to zero. Chance walks that stay
    balanced are shallow bounces — three separate deep episodes is
    what luck cannot fake."""
    depth, ep_peak, deep_eps = 0, 0, 0
    for t in seq:
        prev = depth
        depth += (t == opener) - (t == closer)
        ep_peak = max(ep_peak, depth)
        if depth < 0:
            return False
        if depth == 0 and prev > 0:
            if ep_peak >= 2:
                deep_eps += 1
            ep_peak = 0
    return depth == 0 and deep_eps >= min_deep_episodes


def _balanced(seq, min_pairs=10):
    """min_pairs is high on purpose: the ballot problem makes short
    balanced walks cheap for chance; long ones are structure."""
    from collections import Counter
    c = Counter(seq)
    out = []
    keys = sorted(c)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if c[a] != c[b] or c[a] < min_pairs:
                continue
            if _try_balance(seq, a, b):
                out.append((a, b))
            elif _try_balance(seq, b, a):
                out.append((b, a))
    return out


def _never_follows(seq, min_count=6, min_expected=3.0):
    """Certified nevers: only when chance says the pair SHOULD have
    touched (expected adjacencies >= min_expected) and it never did."""
    from collections import Counter
    c = Counter(seq)
    adj = set(zip(seq, seq[1:]))
    n = max(len(seq) - 1, 1)
    return [(a, b) for a in c for b in c
            if a != b and c[a] >= min_count and c[b] >= min_count
            and c[a] * c[b] / n >= min_expected
            and (a, b) not in adj]


def _null_beats(stat_fn, seq, actual, rng, n_perm=50, pct=95):
    """Admission: the real sequence must beat its own shuffles."""
    if actual == 0:
        return False
    null = []
    s = list(seq)
    for _ in range(n_perm):
        rng.shuffle(s)
        null.append(stat_fn(s))
    return actual > np.percentile(null, pct)


def _cycle_period(seq):
    n = len(seq)
    for p in range(2, n // 3 + 1):
        if all(seq[i] == seq[i % p] for i in range(n - (n % p))):
            if len(set(seq[:p])) > 1:
                return p
    return None


def analyze_level(seq, n_perm=50, seed=3):
    rng = np.random.default_rng(seed)
    rng_shuffle = np.random.default_rng(seed + 1)

    def shuffler(s):
        idx = rng_shuffle.permutation(len(s))
        return [s[i] for i in idx]

    def beats(fn, actual):
        if actual == 0:
            return False
        null = [fn(shuffler(seq)) for _ in range(n_perm)]
        return actual > np.percentile(null, 95)

    cons = {}
    links = _det_links(seq)
    if beats(lambda s: len(_det_links(s)), len(links)):
        cons["always_follows"] = links
    # forks: FAMILY gate first (does this sequence have more fork
    # candidates than its own shuffles produce? — kills the one lucky
    # fork in noise), then a PER-FORK null on each survivor
    forks = {}
    cands = _fork_candidates(seq)
    if cands and beats(lambda s: len(_fork_candidates(s)), len(cands)):
        shuffles = [shuffler(seq) for _ in range(30)]
        for a, kinds in cands.items():
            null_distinct = []
            for s in shuffles:
                nx = [y for x, y in zip(s, s[1:]) if x == a]
                null_distinct.append(len(set(nx)))
            surprise = np.mean([nd <= len(kinds) for nd in null_distinct])
            if surprise < 0.05:
                forks[a] = kinds
    if forks:
        cons["forks"] = forks
    per = _periodic(seq)          # exact recurrence is chance-proof
    if per:
        cons["periodic"] = per
    bal = _balanced(seq)          # long balanced walks only
    if bal:
        cons["balanced_pairs"] = bal
    nev = _never_follows(seq)     # certified only when chance says
    if nev:                       # they SHOULD have touched
        cons["never_follows"] = nev[:8]

    p = _cycle_period(seq)
    if p:
        cons["global_period"] = p

    # the pattern type that satisfies the admitted constraints
    if "balanced_pairs" in cons:
        ptype = "HIERARCHY"
    elif "global_period" in cons:
        ptype = "CYCLE"
    elif "forks" in cons:
        ptype = "BRANCH"
    elif "always_follows" in cons and len(cons["always_follows"]) >= 2:
        ptype = "CHAIN"
    elif "periodic" in cons:
        ptype = "REPEAT"
    else:
        ptype = "NO STRUCTURE"

    chart = []
    for a, b in cons.get("always_follows", {}).items():
        chart.append(f"{a} -> {b}")
    for a, kinds in cons.get("forks", {}).items():
        chart.append(f"{a} -> {{{' | '.join(kinds)}}}")
    for a, b in cons.get("balanced_pairs", []):
        chart.append(f"{a} ... {b} (nested)")
    if "global_period" in cons:
        chart.append(f"repeats every {cons['global_period']} atoms")
    return dict(pattern=ptype, constraints=cons, chart=chart,
                n_atoms=len(set(seq)), length=len(seq))


def _collapse(seq, links):
    """Deterministic chains become single higher atoms: the admitted
    pattern is the next cycle's atom."""
    chain_starts = {a for a in links
                    if a not in set(links.values())}
    out, i = [], 0
    while i < len(seq):
        a = seq[i]
        if a in chain_starts:
            unit, j = [a], i
            while j + 1 < len(seq) and seq[j] in links and \
                    seq[j + 1] == links[seq[j]]:
                unit.append(seq[j + 1])
                j += 1
            if len(unit) > 1:
                out.append("<" + "·".join(unit) + ">")
                i = j + 1
                continue
        out.append(a)
        i += 1
    return out


def analyze(x, max_cycles=3, n_perm=50, seed=3):
    """The multicycle: atoms -> constraints -> pattern -> collapse ->
    again. Returns the tower of levels + the top pattern."""
    seq = atoms_of(x)
    if len(seq) < 8:
        return dict(pattern="TOO SHORT",
                    why="fewer than 8 atoms — nothing to test",
                    levels=[])
    levels = []
    for _ in range(max_cycles):
        lv = analyze_level(seq, n_perm=n_perm, seed=seed)
        levels.append(lv)
        links = lv["constraints"].get("always_follows")
        if not links:
            break
        seq2 = _collapse(seq, links)
        if seq2 == seq or len(seq2) < 8:
            break
        seq = seq2
    return dict(pattern=levels[-1]["pattern"], levels=levels,
                tower=[lv["pattern"] for lv in levels])
