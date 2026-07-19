"""
Isaac — Unified Engine
======================

Two primitives: differentiation (comparison) and memory recursion (store + repeat).
One operation at every scale. Feed it data. It figures it out.

Pipeline:  SENSE → THINK (store ↔ route ↔ evaluate) → ACT
Active:    crystallize the working set. Real-time. O(k²).
Idle:      consolidate() — full crystallization of dirty set. O(d²).

Core:    Net, observe, consolidate, lookup, check
Logic:   logic_eval, compound decomposition
Reason:  reason_chain, is_a_check, can_check, containment, properties, syllogisms
Compute: decompose_multiply, decompose_add, compute (shrug-decompose-verify-memorize)
Solve:   forward, backward, gap-fill, multi-step
World:   state management, action teaching, execution, planning
Persist: assess consequences, plan/think/execute

No parser. No interpreter. No preprocessing. No weights.
Knowledge is doors. Structure is discovered. Everything enters, nothing leaves.
"""

from collections import defaultdict
import re
import time
import numpy as np


# ═════════════════════════════════════════════════════════════════
# NET — doors, tags, metadata. The only data structure.
# ═════════════════════════════════════════════════════════════════

class Net:
    """The knowledge substrate. Directed graph with tagged edges (doors)."""

    def __init__(self):
        self.doors = defaultdict(set)            # node → {targets}
        self.door_tags = defaultdict(set)         # (src, tgt) → {tags}
        self.meta = defaultdict(dict)             # node → {key: value}
        self.door_counts = defaultdict(int)       # (src, tgt) → observations
        self.preds = defaultdict(set)             # node → {sources} (E3:
        # the reverse index — get_predecessors was a full scan over every
        # door in the net, the measured structural root under the
        # crystallizer knee; 2026-07-04)

    def add_door(self, src, tgt, tag="seq"):
        is_new = tgt not in self.doors[src]
        self.doors[src].add(tgt)
        self.door_tags[(src, tgt)].add(tag)
        # counts are the evidence base: "seen once" and "seen a hundred
        # times" must be different facts (2026-07-03, the foundation fix —
        # without counts no statistical divergence test is possible)
        if not hasattr(self, "door_counts"):      # minds saved pre-counts
            self.door_counts = defaultdict(int)
        self.door_counts[(src, tgt)] += 1
        if not hasattr(self, "preds"):            # minds saved pre-index
            self._rebuild_preds()
        self.preds[tgt].add(src)
        if tgt not in self.doors:
            self.doors[tgt] = set()
        return is_new

    def _rebuild_preds(self):
        """Reconstruct the reverse index from the forward doors (for minds
        saved before the index existed). One scan, then never again."""
        self.preds = defaultdict(set)
        for src, tgts in self.doors.items():
            for tgt in tgts:
                self.preds[tgt].add(src)

    def has_door(self, src, tgt):
        return tgt in self.doors.get(src, set())

    def get_doors(self, node, tag=None):
        all_t = self.doors.get(node, set())
        if tag is None:
            return all_t
        return {t for t in all_t if tag in self.door_tags.get((node, t), set())}

    def get_predecessors(self, node, tag=None):
        if not hasattr(self, "preds"):            # minds saved pre-index
            self._rebuild_preds()
        srcs = self.preds.get(node, set())
        if tag is None:
            return set(srcs)
        return {src for src in srcs
                if tag in self.door_tags.get((src, node), set())}

    def get_door_tags(self, src, tgt):
        return self.door_tags.get((src, tgt), set())

    def get_full_profile(self, node):
        out = {}
        for tgt in self.doors.get(node, set()):
            out[tgt] = self.door_tags.get((node, tgt), set()).copy()
        if not hasattr(self, "preds"):            # minds saved pre-index
            self._rebuild_preds()
        inc = {}
        for src in self.preds.get(node, set()):
            inc[src] = self.door_tags.get((src, node), set()).copy()
        return {"out": out, "in": inc}

    def all_nodes(self):
        nodes = set(self.doors.keys())
        for tgts in self.doors.values():
            nodes.update(tgts)
        return nodes

    def set_meta(self, node, key, value):
        self.meta[node][key] = value

    def get_meta(self, node, key, default=None):
        return self.meta.get(node, {}).get(key, default)


# ═════════════════════════════════════════════════════════════════
# PRIMITIVES — compare and tokenize
# ═════════════════════════════════════════════════════════════════

def _hyper_tail(N, K, n, k):
    """P(X >= k) for X ~ Hypergeometric(N, K, n) — the chance that two
    door-sets of sizes K and n drawn from a universe of N share >= k
    targets. numpy-only (lgamma), exact tail sum. The crystallizer's
    admission tests (A2, 2026-07-04) are built on this."""
    from math import lgamma, exp
    if k <= 0:
        return 1.0
    K, n = int(min(K, N)), int(min(n, N))
    if k > min(K, n):
        return 0.0
    def lC(a, b):
        if b < 0 or b > a:
            return None
        return lgamma(a + 1) - lgamma(b + 1) - lgamma(a - b + 1)
    base = lC(N, n)
    tot = 0.0
    for x in range(k, min(K, n) + 1):
        la, lb = lC(K, x), lC(N - K, n - x)
        if la is None or lb is None:
            continue
        tot += exp(la + lb - base)
    return float(min(1.0, tot))


def compare(set_a, set_b):
    """The single cognitive primitive. Same, different, not significant."""
    shared = set_a & set_b
    only_a = set_a - set_b
    only_b = set_b - set_a
    total = len(shared) + len(only_a) + len(only_b)
    return {
        "shared": shared,
        "only_a": only_a,
        "only_b": only_b,
        "similarity": round(len(shared) / total * 100, 1) if total else 0,
    }


def tokenize(text):
    """Split text into tokens. Punctuation separates. Underscores preserved.
    The ONE allowed pre-net operation (Rule 2 exception):
    defines what a NODE is, not what a DOOR means."""
    return re.findall(r"[a-zA-Z0-9_]+|[^\s]", text.lower())


# ═════════════════════════════════════════════════════════════════
# SCRATCH — working memory. Registers / RAM. The mutable half.
# ═════════════════════════════════════════════════════════════════

class Scratch:
    """His working memory: named registers he writes, reads, and updates in
    real time while processing. The OTHER kind of memory from the door-net:

        door-net   = append-only, permanent, 'what is true in general'
        scratch    = overwritable, transient, 'what is true right now / this run'

    A register holds a number (a tally), a string (a note/association), or a
    list (built by appending — chainable). Every write also logs the value to a
    step-trace, so any computation can be replayed to see where it went wrong.
    """

    def __init__(self):
        self.reg = {}                    # name -> current value
        self.log = defaultdict(list)     # name -> [every value it has held]

    # ── core: write supersedes, read returns now ────────────────
    def write(self, name, value):
        """Overwrite the register. The old value is superseded (not appended,
        unlike a door) — but it is kept in the step-trace."""
        self.reg[name] = value
        self.log[name].append(value)
        return value

    def read(self, name, default=None):
        """What is in this register right NOW."""
        return self.reg.get(name, default)

    def has(self, name):
        return name in self.reg

    # ── number ops: increment / tracking ────────────────────────
    def incr(self, name, by=1):
        """count = count + 1. Creates the register at 0 if new."""
        return self.write(name, self.reg.get(name, 0) + by)

    # ── list ops: append / chain ────────────────────────────────
    def append(self, name, value):
        """Grow a register into a list — chain values onto it."""
        cur = self.reg.get(name)
        if not isinstance(cur, list):
            cur = [] if cur is None else [cur]
        cur = cur + [value]
        self.reg[name] = cur
        self.log[name].append(tuple(cur))
        return cur

    # ── latch: 'has it ever…' (sticky bit) ───────────────────────
    def latch(self, name):
        """Flip to True once and stay — memory that something HAPPENED."""
        return self.write(name, True)

    # ── introspection: the step-trace, for replay / find-the-error
    def history(self, name):
        """Every value this register has held, in order. The audit log."""
        return list(self.log[name])

    def snapshot(self):
        """The whole current working state at this instant."""
        return dict(self.reg)

    def clear(self, name=None):
        if name is None:
            self.reg.clear(); self.log.clear()
        else:
            self.reg.pop(name, None); self.log.pop(name, None)


# ═════════════════════════════════════════════════════════════════
# Isaac — the system
# ═════════════════════════════════════════════════════════════════

CONFIDENCE_THRESHOLD = 1.0

# ── crystal/box helpers (neural transplant: boxes are Isaac concepts) ──
_QLOW, _QHIGH = -7, 8

def _quantize(X, lo=None, hi=None):
    """4-bit signed quantization [-7,8] — the resolution cliff (more = noise)."""
    if lo is None:
        lo, hi = X.min(axis=0), X.max(axis=0)
    rng = np.where((hi - lo) == 0, 1, hi - lo)
    return np.clip(np.round((X - lo) / rng * (_QHIGH - _QLOW) + _QLOW),
                   _QLOW, _QHIGH), lo, hi

def _fisher(H, y, k):
    """Top-k dims by between-class / within-class variance (discriminative)."""
    overall = H.mean(0)
    sb = np.zeros(H.shape[1]); sw = np.zeros(H.shape[1])
    for c in np.unique(y):
        Hc = H[y == c]; mu = Hc.mean(0)
        sb += len(Hc) * (mu - overall) ** 2; sw += ((Hc - mu) ** 2).sum(0)
    sw[sw == 0] = 1e-9
    return np.argsort(-(sb / sw))[:k]


# ═════════════════════════════════════════════════════════════════
# WAVES — the temporal crystallizer.
#
# The static crystallizer compares door PROFILES: it is order-blind by
# construction. This pass watches the whole matrix MOVE — compares each
# instant to the next — and crystallizes three things the profile view
# cannot see:
#   simultaneity  doors that light together        (co-activation groups)
#   movement      one group dims as another lights (handoff edges)
#   circles       waves that return to their start (closed handoff paths)
# Applied recursively: a circle's activity becomes a door one level up.
#
# Null discipline: every claim must beat a JITTER null — small ±2..5-step
# shifts that keep each door's own rhythm and rate but break precise
# co-timing. (A full circular shift is the WRONG null for periodic waves:
# it relands in phase 1-in-period times, so real simultaneity could never
# beat it.) Jitter ONE side of each pair only — jittering both sometimes
# hands them the same shift, which preserves relative timing.
# ═════════════════════════════════════════════════════════════════

_wave_rng = np.random.default_rng(0)


def _wave_jitter(col):
    return np.roll(col, int(_wave_rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])))


def _wave_groups(S, n_perm=40, pct=95):
    """SIMULTANEITY: doors that fire together. Must beat an independence
    floor (column permutation) AND a per-pair jitter null."""
    T, D = S.shape
    Z = (S - S.mean(0)) / (S.std(0) + 1e-12)
    C = (Z.T @ Z) / T
    floor_max = np.empty(n_perm)
    pair_null = np.empty((n_perm, D, D))
    for k in range(n_perm):
        Zp = np.column_stack([_wave_rng.permutation(Z[:, j]) for j in range(D)])
        Cp = (Zp.T @ Zp) / T
        np.fill_diagonal(Cp, 0)
        floor_max[k] = Cp.max()
        Zj = np.column_stack([_wave_jitter(Z[:, j]) for j in range(D)])
        pair_null[k] = (Z.T @ Zj) / T
    floor = np.percentile(floor_max, pct)
    pair_thr = np.percentile(pair_null, pct, axis=0)
    pair_thr = np.maximum(pair_thr, pair_thr.T)
    # 1.4x margin: connected components merge on a SINGLE edge, so a
    # borderline false pair (the ~5% per-pair leak) can bridge two real
    # groups into one. An edge must clearly beat its null, not graze it.
    adj = (C > 1.4 * floor) & (C > 1.4 * pair_thr)
    np.fill_diagonal(adj, False)
    groups, unseen = [], set(range(D))
    while unseen:
        stack = [unseen.pop()]; comp = set(stack)
        while stack:
            j = stack.pop()
            nxt = set(np.flatnonzero(adj[j])) & unseen
            unseen -= nxt; comp |= nxt; stack += list(nxt)
        if len(comp) > 1:
            groups.append(tuple(sorted(int(x) for x in comp)))
    return groups


def _wave_handoff_counts(Goff, Gon):
    """count[a,b] = instants where a switches off and b switches on (±1 step)."""
    m = Goff.shape[1]
    cnt = np.zeros((m, m))
    for a in range(m):
        off = ((Goff[:-1, a] == 1) & (Goff[1:, a] == 0)).astype(float)
        w = off.copy(); w[1:] += off[:-1]; w[:-1] += off[1:]
        for b in range(m):
            if a != b:
                on = (Gon[:-1, b] == 0) & (Gon[1:, b] == 1)
                cnt[a, b] = float((w * on).sum())
    return cnt


def _wave_edges(G, n_perm=40):
    """MOVEMENT: handoffs that beat 1.5× the jitter null's best day."""
    real = _wave_handoff_counts(G, G)
    m = G.shape[1]
    null = np.zeros((n_perm, m, m))
    for k in range(n_perm):
        Gj = np.column_stack([_wave_jitter(G[:, j]) for j in range(m)])
        null[k] = _wave_handoff_counts(G, Gj)
    thr = null.max(axis=0)
    return [(a, b) for a in range(m) for b in range(m)
            if a != b and real[a, b] > max(1.5 * thr[a, b], 2.0)]


def _wave_circles(edges, m):
    """CIRCLES: closed paths in the handoff graph (rotation-canonical)."""
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
    found = set()

    def dfs(start, node, path):
        for nxt in adj[node]:
            if nxt == start and len(path) > 1:
                k = path.index(min(path))
                found.add(tuple(path[k:] + path[:k]))
            elif nxt not in path and len(path) < m:
                dfs(start, nxt, path + [nxt])

    for s in range(m):
        dfs(s, s, [s])
    return sorted(found)


# ═════════════════════════════════════════════════════════════════
# DISCOVERY — the challenge loop. The thing that learns things.
#
# Given examples of something he cannot do, find the rule:
#   compare -> enumerate candidate relations -> admit only what beats its
#   null -> the survivors ARE the equation -> install it as a law node ->
#   the challenge is now computable.
# Term growth is STAGED (candidates grow only around admitted terms — no
# d^k blowup) and admission is NULL-GATED against the max-over-candidates
# correlation on permuted residuals (selection-effect decoys die).
# ═════════════════════════════════════════════════════════════════

def _atom_specs(d):
    """The vocabulary of forms. Linear-in-COEFFICIENTS over a NONLINEAR
    library: unary transcendentals (sin/cos/exp at a scale grid — so a
    single-input challenge is not reduced to polynomials) and pair forms.
    Scales k live INSIDE the nonlinearity, where regression cannot reach —
    the grid proposes them, the refine pass sharpens them. Complex-number
    structure enters as damped-oscillation pairs: exp(-at)*cos(bt) is the
    real face of exp((-a+bi)t)."""
    specs = [("var", i, None, None) for i in range(d)]
    for i in range(d):
        for k in (0.5, 1.0, 2.0, 3.0, 4.5, 6.0, 8.0):
            specs += [("sin", i, None, k), ("cos", i, None, k)]
        for k in (0.25, 0.5, 1.0, -0.25, -0.5, -1.0):   # decay AND growth
            specs.append(("exp", i, None, k))
        for k in (-2.0, -1.0, -0.5, 0.0, 0.5, 1.5):     # ONE DIAL: the
            specs.append(("pow", i, None, k))           # power family with
            # lambda=0 = log (the Box-Cox limit: (x^L-1)/L -> ln x as L->0;
            # x^0 collapses to a constant, so log IS the missing grid point
            # — owner, 2026-07-04: "isn't a log just a power? it's not
            # special." Correct: a family member, reachable by the same
            # grid-proposes/refine-sharpens machinery as every exponent.)
    for i in range(d):
        for j in range(i + 1, d):
            for k in (0.5, 1.0, 2.0):
                specs += [("cosd", i, j, k), ("sind", i, j, k)]
            for k in (0.5, 1.0, 1.5):
                specs.append(("coshd", i, j, k))
            # THE CREASE (mechanisms promotion, 2026-07-15): |xi-xj| —
            # comparison's algebraic face; max/min become sayable:
            # max(a,b) = (a+b+|a-b|)/2. No scale dial (the linear
            # coefficient absorbs it).
            specs.append(("absd", i, j, None))
    return specs


def _atom_col(X, spec):
    kind, i, j, k = spec
    if kind == "var":
        return X[:, i]
    if kind == "sin":
        return np.sin(k * X[:, i])
    if kind == "cos":
        return np.cos(k * X[:, i])
    if kind == "exp":
        return np.exp(np.clip(-k * X[:, i], -30, 30))
    if kind == "pow":
        base = np.maximum(np.abs(X[:, i]), 1e-9)
        if k == 0:                                # the lambda=0 limit: log
            return np.log(base)
        return np.power(base, k)
    if kind == "step":            # the SWITCH: [xi > t], t data-proposed
        return (X[:, i] > k).astype(float)
    if kind == "absd":            # the CREASE: |xi - xj|
        return np.abs(X[:, i] - X[:, j])
    diff = np.clip(X[:, i] - X[:, j], -20, 20)
    if kind == "cosd":
        return np.cos(k * diff)
    if kind == "sind":
        return np.sin(k * diff)
    return np.cosh(np.clip(k * diff, -15, 15))


def _atom_label(spec):
    kind, i, j, k = spec
    if kind == "var":
        return f"x{i}"
    if kind == "sin":
        return f"sin({k:g}*x{i})"
    if kind == "cos":
        return f"cos({k:g}*x{i})"
    if kind == "exp":
        return f"exp({-k:g}*x{i})"
    if kind == "pow":
        return f"log(x{i})" if k == 0 else f"x{i}^{k:g}"
    if kind == "step":
        return f"[x{i}>{k:g}]"
    if kind == "absd":
        return f"|x{i}-x{j}|"
    op = {"cosd": "cos", "sind": "sin", "coshd": "cosh"}[kind]
    return f"{op}({k:g}*(x{i}-x{j}))"


def _disc_col(A, term):
    v = A[:, term[0]].copy()
    for a in term[1:]:
        v = v * A[:, a]
    return v


# ── THE VERDICT REWRITE (S2b, 2026-07-15) ───────────────────────────
# Ported from experiments/verdict_rewrite_probe.py (23/23) and the
# pool instrument in experiments/reservoir_surprise_probe.py (13/13).
# UNDERSTOOD is earned before examiners and a ruler, no longer by r2
# alone (r2 is demoted to a reported number): an EXACT ROAD stamps
# machine-precision fits proven on unseen rows; a residual REPLAY asks
# every candidate form whether it can predict the held-out leftover
# (selection-corrected max-null — the 119/120 lesson); the POOL meter
# (a frozen random net, shallow and fixed — it gates and names, never
# writes into a mind, never feeds an equation) asks the grammar-free
# version of the same question; and exactness claims ride a
# CERTIFICATE read against an EVIDENCED floor (grain / repeats / told
# — the 13-inch foot; no floor evidenced means uncertified, said so).

_EXACT_REL = 1e-9       # machine-exact, relative to the numbers' size
_POOL_MIN_N = 48        # the pool's measured competence floor (R0b)
_POOL_M = 200           # capacity chosen by the probe's own R0 sweep
_POOL_FOLDS = 5
_POOL_RIDGE = 1e-2
_POOL_NULLS = 200
_REPLAY_NULLS = 150


class _PoolMeter:
    """A shallow FIXED pool (owner naming): frozen tanh random features
    + ridge readout, weights seeded BEFORE data. 5-fold cross-fit
    capture: every row judged by a readout that never saw it."""

    GAINS = (0.7, 1.5, 2.5)     # multiscale, fixed — instrument identity

    def __init__(self, X, m=_POOL_M, seed=777, split_seed=0):
        n, d = X.shape
        self.n = n
        self.m_eff = min(m, max(16, 2 * n), 400)
        rng = np.random.default_rng(seed + 1000 * self.m_eff + d)
        gains = np.array([self.GAINS[i % len(self.GAINS)]
                          for i in range(self.m_eff)])
        self.W = rng.normal(0.0, 1.0 / np.sqrt(d), (d, self.m_eff)) * gains
        self.b = rng.uniform(-1.0, 1.0, self.m_eff)
        idx = np.random.default_rng(split_seed).permutation(n)
        folds = [idx[f::_POOL_FOLDS] for f in range(_POOL_FOLDS)]
        self.parts = []
        for ho in folds:
            tr = np.setdiff1d(np.arange(n), ho)
            mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-12
            H_tr = np.tanh(((X[tr] - mu) / sd) @ self.W + self.b)
            H_ho = np.tanh(((X[ho] - mu) / sd) @ self.W + self.b)
            A = H_tr.T @ H_tr + _POOL_RIDGE * len(tr) * np.eye(self.m_eff)
            M = np.linalg.solve(A, H_tr.T)
            self.parts.append((tr, ho, H_ho, M))

    def capture(self, r):
        p = np.empty(self.n)
        for tr, ho, H_ho, M in self.parts:
            c = r[tr].mean()
            p[ho] = H_ho @ (M @ (r[tr] - c)) + c
        ss = np.sum((r - p) ** 2)
        tot = np.sum((r - r.mean()) ** 2)
        return 1.0 - ss / tot if tot > 0 else 0.0


def _pool_scream(X, r, rng_seed=1):
    """Capture vs the selection-corrected permuted-y null. The pool
    POINTS, never answers: one boolean plus receipts."""
    meter = _PoolMeter(np.asarray(X, float))
    cap = meter.capture(r)
    rng = np.random.default_rng(rng_seed)
    null = np.array([meter.capture(rng.permutation(r))
                     for _ in range(_POOL_NULLS)])
    thr = float(np.percentile(null, 99.0))
    return float(cap), thr, cap > thr


def _exact_terms(specs, n_vars):
    """Exact-road candidate TERMS: every single atom, plus raw-var
    pair and triple products (degree<=3 polynomial terms — apply_law
    evaluates any term tuple, so triples are legal even though the
    enumerator's frontier stops at pairs; this is what lets Kepler's
    a^3 be SAID at n=8)."""
    terms = [(i,) for i in range(len(specs))]
    terms += [(i, j) for i in range(n_vars) for j in range(i, n_vars)]
    terms += [(i, j, k) for i in range(n_vars)
              for j in range(i, n_vars) for k in range(j, n_vars)]
    return terms


def _exact_road(specs, A_tr, y_tr, X_ho, y_ho, n_vars, kmax=3, top=16):
    """Requirement 4: exact-checkable data stamps on machine-zero
    residual WITHOUT a floor. A hit must be machine-exact RELATIVE on
    train AND held-out — noise cannot fake held-out exactness, which
    is the selection guard at tiny n (measured 0/20 at n=8, 0/30 with
    the deep road in the probes). Affine-clone candidates are DEDUPED
    before the shortlist (the mechanisms-arc port lesson: clones vote
    as a bloc and starve real terms). Takes explicit specs/atom-matrix
    so callers can run it on a SUBSET (the outlier road's clean
    majority). Returns term list or None."""
    if len(y_ho) < 3 or len(y_tr) < 4:
        return None
    A_ho = np.column_stack([_atom_col(X_ho, s) for s in specs])
    cand = _exact_terms(specs, n_vars)
    cols_tr = np.column_stack([_disc_col(A_tr, t) for t in cand])
    cols_ho = np.column_stack([_disc_col(A_ho, t) for t in cand])
    good = (np.isfinite(cols_tr).all(0) & np.isfinite(cols_ho).all(0)
            & (cols_tr.std(0) > 1e-12))
    scale = max(float(np.max(np.abs(np.concatenate([y_tr, y_ho])))), 1e-12)
    base = y_tr - y_tr.mean()
    bs = base.std() + 1e-12
    Zt = (cols_tr - cols_tr.mean(0)) / (cols_tr.std(0) + 1e-12)
    corr = np.abs(Zt.T @ (base / bs)) / len(y_tr)
    corr[~good] = -1.0
    ranked = np.argsort(-corr)
    order = []
    for j in ranked:
        if corr[j] < 0 or len(order) >= top:
            break
        zj = Zt[:, j]
        if any(abs(float(zj @ Zt[:, k])) / len(y_tr) > 1 - 1e-9
               for k in order):
            continue
        order.append(int(j))
    # STRUCTURAL DIVERSITY GUARANTEE (the enumerator's own shortlist
    # move, reused): monotone families of one variable flood a pure
    # correlation top-N and crowd out the simple true terms — so every
    # pure-variable polynomial term (singles, pairs, triples of raw
    # vars) is guaranteed a seat in the combo pool.
    pure_var = [ji for ji, t in enumerate(cand)
                if all(a < n_vars for a in t) and good[ji]]
    order += [j for j in pure_var if j not in order]
    # crease seats (the diversity rule's fourth sighting): the step-
    # atom flood crowds |xi-xj| out of the correlation top-N, and max
    # is unsayable without it — d(d-1)/2 seats, cheap
    crease = [ji for ji, t in enumerate(cand)
              if len(t) == 1 and specs[t[0]][0] == "absd"
              and good[ji]]
    order += [j for j in crease if j not in order]
    from itertools import combinations
    # BOUNDED COMBO POOLS (efficiency pass, profiled 2026-07-15:
    # 621,021 lstsq calls = 17.7s of a 19.0s discover at d=5 — the
    # seat guarantees made k>=2 combinations explode). k=1 still
    # sweeps EVERY seated candidate; k>=2 runs over a bounded diverse
    # subpool (top-16 deduped + best-12 pure-var + creases, ~<=38 ->
    # ~9k fits); the deep k>=4 pool is pure-var-FIRST (exact
    # conditional rules are polynomial — the deep road's domain) and
    # capped at 24. Held-out machine-exactness stays the guard.
    pvset = set(pure_var)
    # singles are guaranteed BY CONSTRUCTION (only d of them — the
    # cheapest seats there are); products compete on correlation.
    # Fifth sighting of the crowding disease: high-corr pure-var
    # PRODUCTS cut the singles out of a top-12, and the blended
    # world's five-word sentence lost x0 and x1 (battery B3 0/2,
    # wrong-kept in the ledger entry).
    pv_singles = [ji for ji in pure_var if len(cand[ji]) == 1]
    pv_prods = [int(j) for j in ranked
                if int(j) in pvset and len(cand[int(j)]) > 1]
    pool2 = list(dict.fromkeys(order[:16] + pv_singles
                               + pv_prods[:12] + crease))
    pool45 = list(dict.fromkeys(pv_singles + pv_prods[:14] + crease
                                + order[:8]))[:26]
    pools = {1: order, 2: pool2, 3: pool2, 4: pool45, 5: pool45}
    # DEEP ESCALATION (the mechanisms probe's port lesson): exact
    # conditional rules need up to 5 terms (x0+x1-f*x0-f*x1+f*x0*x1);
    # the combinatorics are affordable only on small data, where such
    # rules live. Held-out machine-exactness remains the guard at
    # every k (noise cannot fake it; measured 0/30).
    kmax_eff = 5 if len(y_tr) <= 100 else kmax
    for k in range(1, kmax_eff + 1):
        if len(y_tr) < k + 3:
            break
        for sub in combinations(pools.get(k, pool2), k):
            Ct = np.column_stack([cols_tr[:, list(sub)],
                                  np.ones(len(y_tr))])
            coef, *_ = np.linalg.lstsq(Ct, y_tr, rcond=None)
            if np.max(np.abs(y_tr - Ct @ coef)) / scale > _EXACT_REL:
                continue
            Ch = np.column_stack([cols_ho[:, list(sub)],
                                  np.ones(len(y_ho))])
            if np.max(np.abs(y_ho - Ch @ coef)) / scale > _EXACT_REL:
                continue
            return [cand[j] for j in sub]
    return None


def _replay_scan(enum, A_ho, X_ho_raw, resid, rng):
    """Leg 1: max partial correlation of unadmitted candidates with the
    held-out residual, against the selection-corrected max-null (2nd
    largest of 150 permutations). Candidates: every single atom, raw-
    var pairs, and replay-only CREASE columns |xi-xj| — the mint
    grammar's known blind spot gets a question-asker even before it
    becomes a word (mechanisms arc)."""
    n_vars = X_ho_raw.shape[1]
    cand_cols, labels = [], []
    for i in range(A_ho.shape[1]):
        cand_cols.append(A_ho[:, i])
        labels.append(_atom_label(enum.specs[i]))
    for i in range(n_vars):
        for j in range(i, n_vars):
            cand_cols.append(A_ho[:, i] * A_ho[:, j])
            labels.append(f"x{i}*x{j}")
    for i in range(n_vars):
        for j in range(i + 1, n_vars):
            cand_cols.append(np.abs(X_ho_raw[:, i] - X_ho_raw[:, j]))
            labels.append(f"|x{i}-x{j}|")
    C = np.column_stack(cand_cols)
    good = np.isfinite(C).all(0) & (C.std(0) > 1e-12)
    M = enum._design(A_ho)                      # admitted columns + 1
    beta, *_ = np.linalg.lstsq(M, C[:, good], rcond=None)
    R = C[:, good] - M @ beta                   # residualized candidates
    rstd = R.std(0) + 1e-12
    Z = (R - R.mean(0)) / rstd
    ok = rstd > 1e-10
    if not ok.any() or resid.std() < 1e-15:
        return "quiet", "-", 0.0, 0.0
    Z = Z[:, ok]
    labs = [l for l, g in zip(labels, good) if g]
    labs = [l for l, o in zip(labs, ok) if o]
    rs = (resid - resid.mean()) / (resid.std() + 1e-12)
    obs_all = np.abs(Z.T @ rs) / len(rs)
    b = int(np.argmax(obs_all))
    null = np.empty(_REPLAY_NULLS)
    for p in range(_REPLAY_NULLS):
        rp = rng.permutation(rs)
        null[p] = np.max(np.abs(Z.T @ rp)) / len(rs)
    thr = float(np.sort(null)[::-1][1])         # 2nd largest ~ 99th pct
    obs = float(obs_all[b])
    return ("fired" if obs > thr else "quiet"), labs[b], obs, thr


class _Enumerator:
    def __init__(self, max_degree=3, n_perm=40, pct=95, max_terms=16):
        self.max_degree, self.n_perm, self.pct = max_degree, n_perm, pct
        # max_terms: on AUTOCORRELATED real data (e.g. a smooth time series)
        # the iid permutation null is too easy — shuffling destroys the
        # autocorrelation, so weak junk beats it forever and admission never
        # stops (found the hard way: a 20-CPU-hour runaway on sunspots).
        # CURED 2026-07-04: the admission null is now BLOCK permutation at
        # the residual's measured decorrelation length (see _null_perm).
        # The cap stays as the backstop only; the battery shows admission
        # now stops on its own (experiments/blockperm_battery.py).
        self.max_terms = max_terms
        self.terms, self.coefs, self.intercept = [], np.array([]), 0.0
        self.block_L = 1     # measured decorrelation length of the residual
        # (1 = white; >1 = the admission null permutes BLOCKS of this length)

    # ── A1 (2026-07-04): the block-permutation null ────────────────────
    # On an autocorrelated residual the iid shuffle destroys the
    # autocorrelation itself, not just the claimed alignment — the null gets
    # too easy and junk beats it forever (the sunspot runaway). The cure:
    # measure the residual's decorrelation length L; if L > 1, the null
    # permutes contiguous blocks of length L, preserving the texture the
    # data actually has and destroying ONLY candidate↔residual alignment.

    @staticmethod
    def _decorr_len(rs):
        """Measured decorrelation length of a standardized series.
        Gate: lag-1 autocorrelation tested at 1% (|r1| > 2.58/sqrt(n) under
        the iid null). If significant, L = first lag where the ACF falls
        inside its own significance band (2/sqrt(n)), capped at n//4."""
        n = len(rs)
        if n < 20:
            return 1
        z = rs - rs.mean()
        denom = float(z @ z) + 1e-12
        r1 = float(z[:-1] @ z[1:]) / denom
        if abs(r1) <= 2.58 / np.sqrt(n):
            return 1
        band = 2.0 / np.sqrt(n)
        maxlag = min(n // 4, 200)
        for lag in range(2, maxlag + 1):
            ac = float(z[:-lag] @ z[lag:]) / denom
            if abs(ac) < band:
                return lag
        return maxlag

    def _null_perm(self, rs):
        """One draw from the admission null: iid shuffle when the residual
        is white (block_L == 1); when autocorrelated, circular
        moving-block permutation with an INDEPENDENT circular roll
        inside each block. Block order + one global roll is
        phase-blind to sub-block PERIODICITY (measured 2026-07-12 on
        divisibility streams: a period-2 residual was unfindable —
        every L=18 block carried it in phase, so ~1/P of null draws
        replicated the real alignment and the gate rose to the real
        score; periods dividing L were fully trapped). The per-block
        roll keeps within-block texture (ACF, circularly) — the
        sunspot protection stands — while periodic phase cancels
        across blocks."""
        L = self.block_L
        if L <= 1:
            return _wave_rng.permutation(rs)
        n = len(rs)
        r = np.roll(rs, int(_wave_rng.integers(0, n)))   # random phase
        nb = int(np.ceil(n / L))
        pad = nb * L - n
        if pad:
            r = np.concatenate([r, r[:pad]])
        blocks = r.reshape(nb, L)
        idx = (np.arange(L)[None, :]
               + _wave_rng.integers(0, L, nb)[:, None]) % L
        blocks = np.take_along_axis(blocks, idx, axis=1)
        return blocks[_wave_rng.permutation(nb)].ravel()[:n]

    # ── taught rounding (owner, 2026-07-12) ────────────────────────────
    # "i think we just need to teach it rounding actually. if its
    # 3.0018463 then its probably tested to 3. if its 1.764964 then it
    # may be 1.75 etc." A measured constant's roundings are HYPOTHESES
    # tested outright: candidates at the natural ruler marks ({1, 1/2,
    # 1/4} x powers of ten — 1.75 is a mark), coarsest first; the
    # simplest that does not lose is adopted; if every rounding loses,
    # the measured digits stand. No invented simplicity, no lost
    # precision. Applied wherever constants are measured: proposed
    # periods (fold score as the check) and admitted terms'
    # inside-parameters at fit end (trial refit as the check).

    @staticmethod
    def _round_candidates(x):
        """The rounding ladder near a measured constant, coarsest ruler
        mark first. Sign-preserving; empty for zero/non-finite."""
        ax = abs(float(x))
        if not np.isfinite(ax) or ax <= 0:
            return []
        e = int(np.floor(np.log10(ax)))
        out = []
        for k in range(e, e - 4, -1):
            for s in (1.0, 0.5, 0.25):
                step = s * 10.0 ** k
                c = round(round(x / step) * step, 12)
                if c != 0 and abs(c - x) > 1e-12 and c not in out:
                    out.append(c)
        return out

    # ── E7 (2026-07-04): phase-fold period proposal ────────────────────
    # Owner: "if you suspect a period do the projection thing. you don't
    # need the whole thing, you just need a few samples and to map it."
    # An off-grid frequency over a long window is near-orthogonal to every
    # grid atom (measured: r 0.12 vs gate 0.37) — so PROPOSE periods from
    # the data itself: fold y onto candidate periods of each input and
    # score how much variance the phase map explains. Sparse and irregular
    # sampling is fine — folding needs coverage of the CYCLE, not of time.
    # A period is proposed only past a selection-corrected block-perm null
    # (max-over-all-periods on permuted y). Proposals WIDEN the grid
    # (expansion); every proposed atom still faces the admission null
    # (compression unchanged).

    def _comb_periods(self, t, ys, n_perm=100):
        """REGULAR-GRID period proposal: the DFT comb (2026-07-12,
        divisibility-stream probe). On a regularly sampled axis the periodogram
        measures EVERY representable frequency at once; the geomspace
        fold scan's ~7% coarse steps cannot land on a sharp comb
        (period 3 over 300 units needs ~0.25% placement — measured:
        divisibility periods never lit up, so the stream's label logic was
        unsayable). Score of fundamental j = ENRICHMENT: the comb's
        share of spectral power (j and all harmonics) over the share
        of bins it occupies (flat noise = 1 at every j — the small-j
        degeneracy cancels). Local maxima past a selection-corrected
        SPECTRUM-ENVELOPE surrogate null (max over ALL j, replayed;
        gate = observed max — the interpolated-percentile lesson)
        are proposed. Returns [(period, score), ...] or None when the
        axis is not regular (the fold road handles irregular
        sampling)."""
        order = np.argsort(t, kind="stable")
        ts, vs = t[order], ys[order]
        d = np.diff(ts)
        if len(d) < 8:
            return None
        dt = float(np.median(d))
        if dt <= 0 or float(np.max(np.abs(d - dt))) > 0.01 * dt:
            return None
        n = len(vs)
        nyq = n // 2

        def comb(P):
            tot = float(P[1:].sum()) + 1e-12
            s = np.zeros(nyq + 1)
            for j in range(2, nyq + 1):
                share = float(P[j::j].sum()) / tot
                s[j] = share * nyq / len(P[j::j])
            return s

        F = np.abs(np.fft.rfft(vs - vs.mean())) ** 2
        real = comb(F)
        # THE NULL IS A SPECTRUM-ENVELOPE SURROGATE, not block
        # permutation: blocks preserve a short period INSIDE each
        # block, so for a true short comb the null keeps the very
        # structure under test and the gate inflates (measured:
        # period 4 at n=720 went NO RULE — wrong-kept). Surrogate
        # power = median-smoothed envelope (robust to the comb's own
        # spikes) x Exp(1) per bin — redness preserved, combs
        # destroyed, no FFTs needed in the null at all.
        win = max(5, len(F) // 20)
        pad = np.concatenate([F[1:win + 1][::-1], F, F[-win - 1:-1][::-1]])
        env = np.array([float(np.median(pad[j:j + 2 * win + 1]))
                        for j in range(len(F))])
        env = np.maximum(env, 1e-9 * float(F.mean()))
        null = np.empty(n_perm)
        for k in range(n_perm):
            null[k] = comb(env * _wave_rng.exponential(1.0, len(F))).max()
        gate = float(null.max())
        # among gate-passers, the FUNDAMENTAL of a comb family is the
        # LARGEST j carrying the family's full energy share: every
        # divisor shows the same share with a looser comb (measured:
        # a flat comb TIES the enrichment statistic across divisors
        # and sub-combs, and the true period lost the tie to float
        # noise — the 36-comb proposed as 4/2/6, wrong-kept).
        # Multiples with genuinely lower share are distinct
        # sub-structure and stay candidates.
        tot = float(F[1:].sum()) + 1e-12
        shares = {j: float(F[j::j].sum()) / tot
                  for j in range(2, nyq + 1) if real[j] > gate}
        picks = []
        for j in sorted(shares, key=lambda j: (-round(shares[j], 3), -j)):
            if len(picks) >= 3:
                break
            if any(k % j == 0 and shares[j] <= shares[k] + 1e-3
                   for k, _ in picks):
                continue              # divisor-shadow of a kept comb
            P = n * dt / float(j)
            if any(abs(np.log(P / p0)) < 0.1 for _, p0 in picks):
                continue
            picks.append((j, P))
        return [(P, float(real[j])) for j, P in picks]

    def _propose_periods(self, X, y, n_perm=100, pct=99, bins=8):
        n = len(y)
        if n < 40:
            return []
        ys = (y - np.mean(y)) / (np.std(y) + 1e-12)
        self.block_L = min(self._decorr_len(ys), max(2, n // 20))
        proposals = []
        for i in range(X.shape[1]):
            t = np.asarray(X[:, i], float)
            span = float(t.max() - t.min())
            if span <= 0:
                continue
            # The floor is ALIASING, not samples-per-cycle (2026-07-12,
            # divisibility-stream probe): folding needs coverage of the CYCLE, not
            # of time — on a dense grid a short period bins up fine
            # because many cycles stack. WRONG-KEPT: the old floor
            # p_min = 8*span/n (>=8 samples/cycle) blocked divisibility
            # periods 3 and 5 on an integer grid while 15 passed — the
            # stream's label logic was unsayable. A period must simply
            # exceed ~2x the typical sample spacing.
            diffs = np.diff(np.sort(t))
            pos = diffs[diffs > 0]
            dt = float(np.median(pos)) if len(pos) else span
            p_min = 2.05 * dt
            p_max = span / 2.0            # >= 2 folds, else nothing maps
            if p_min >= p_max:
                continue
            Ps = np.geomspace(p_min, p_max, 64)
            t0 = t - t.min()

            def fold_score(vals, P):
                ph = np.minimum((t0 % P) / P * bins, bins - 1).astype(int)
                cnt = np.bincount(ph, minlength=bins)
                s1 = np.bincount(ph, weights=vals, minlength=bins)
                s2 = np.bincount(ph, weights=vals * vals, minlength=bins)
                ssw = float((s2 - s1 * s1 / np.maximum(cnt, 1)).sum())
                return 1.0 - ssw / (float(vals @ vals) + 1e-12)

            def refine_P(vals, best, bestP):
                # two fine stages pin the period (a 0.3% frequency
                # error de-coheres over hundreds of cycles); the null
                # replays every stage, so selection stays corrected
                for width, pts in ((0.07, 33), (0.007, 33)):
                    if bestP is None:
                        break
                    for P in np.linspace(bestP * (1 - width),
                                         bestP * (1 + width), pts):
                        r = fold_score(vals, P)
                        if r > best:
                            best, bestP = r, P
                return best, bestP

            def coarse(vals):
                return [fold_score(vals, P) for P in Ps]

            def best_fold(vals):
                c = coarse(vals)
                j = int(np.argmax(c))
                return refine_P(vals, c[j], Ps[j])

            # NO ROUNDING AT PROPOSAL TIME (wrong-kept, 2026-07-12):
            # snapping picks with the fold as referee adopted marks
            # the fold cannot resolve (3.6 vs a true 3.5904 — within
            # its bin width), injecting slightly-wrong atoms that
            # admission then smeared into two-atom surrogates. The
            # owner's rounding is POST-HOC by design ("if its
            # 3.0018463 then its probably TESTED to 3"): proposals
            # stay precise; roundings are tested at fit end where the
            # referee is the actual refit (_round_terms).

            # THREE ROADS PROPOSE, NONE REFEREES ANOTHER (untangled
            # 2026-07-12 after measured whack-a-mole: comb picks
            # deduped the fold's precise pick, then fold-refined comb
            # picks walked off exact truths — both wrong-kept).
            # Expansion is free and admission compresses: each road
            # dedups only within itself; every atom still faces the
            # admission null term by term.

            # road 0, integer axes (owner, 2026-07-12): integer
            # periods CHECKED OUTRIGHT by residue classes — exact,
            # cheap, no spectral machinery, no refine walk.
            res_P = []
            if np.allclose(t, np.round(t), atol=1e-9):
                ti = np.round(t).astype(np.int64)
                Pmax = min(max(2, n // 4), 128)   # classes need >=4
                # samples each (n//4); 128 = cost backstop only — the
                # comb road covers longer window-commensurate combs

                def residue_score(vals, P):
                    ph = ti % P
                    cnt = np.bincount(ph, minlength=P)
                    s1 = np.bincount(ph, weights=vals, minlength=P)
                    s2 = np.bincount(ph, weights=vals * vals,
                                     minlength=P)
                    ssw = float((s2 - s1 * s1
                                 / np.maximum(cnt, 1)).sum())
                    return 1.0 - ssw / (float(vals @ vals) + 1e-12)

                Ps_int = range(2, Pmax + 1)
                scores = {P: residue_score(ys, P) for P in Ps_int}
                null0 = np.empty(n_perm)
                for kk in range(n_perm):
                    pv = self._null_perm(ys)
                    null0[kk] = max(residue_score(pv, P)
                                    for P in Ps_int)
                gate0 = float(null0.max())
                passers = {P: s for P, s in scores.items() if s > gate0}
                # the fundamental is the SMALLEST P with its family's
                # score: any multiple of a true period scores >= it
                # (finer classes stay pure) — multiples are shadows
                for P in sorted(passers,
                                key=lambda P: (-round(passers[P], 3), P)):
                    if len(res_P) >= 3:
                        break
                    if any(P % P0 == 0
                           and passers[P] <= passers[P0] + 1e-3
                           for P0 in res_P):
                        continue
                    res_P.append(float(P))

            # road 1, regular axes: the DFT comb. Bin-quantized picks
            # get the whole-number snap-check only — refining them
            # with the fold walked exact truths off (wrong-kept).
            comb_P = []
            for P, _ in (self._comb_periods(t, ys, n_perm) or []):
                if all(abs(np.log(P / p0)) > 0.1 for p0 in comb_P):
                    comb_P.append(P)

            # road 2, any axis: the fold scan; local maxima past the
            # gate (a composed target listens to several periods at
            # once), refined, then snap-checked.
            fold_P = []
            curve = coarse(ys)
            null = np.empty(n_perm)
            for k in range(n_perm):
                null[k] = best_fold(self._null_perm(ys))[0]
            gate = float(np.percentile(null, pct))
            order = np.argsort(-np.asarray(curve))
            for j in order:
                if curve[j] <= gate or len(fold_P) >= 3:
                    break
                left = curve[j - 1] if j else -np.inf
                right = curve[j + 1] if j + 1 < len(Ps) else -np.inf
                if curve[j] < left or curve[j] < right:
                    continue
                r, P = refine_P(ys, curve[j], Ps[j])
                if r > gate and all(abs(np.log(P / p0)) > 0.1
                                    for p0 in fold_P):
                    fold_P.append(P)

            proposals += [(i, 2.0 * np.pi / float(P))
                          for P in res_P + comb_P + fold_P]
        self.proposed_periods = proposals
        return proposals

    def fit(self, X, y):
        self.X = X
        self.specs = _atom_specs(X.shape[1])
        # phase-fold proposals join the grid (dedup against existing ks)
        for (i, k) in self._propose_periods(X, y):
            k = round(float(k), 4)
            if not any(s[0] in ("sin", "cos") and s[1] == i
                       and s[3] is not None and abs(s[3] - k) / k < 0.02
                       for s in self.specs):
                self.specs += [("sin", i, None, k), ("cos", i, None, k)]
        # SWITCH proposals (mechanisms promotion): thresholds live in
        # the data — deciles + the 0.5-mark ladder inside each var's
        # range (a threshold is a constant; the ruler discipline
        # applies). Binary columns skip (already a var atom). Capped at
        # 16 per var by stride (cost guard, disclosed); every proposed
        # step still faces the admission null like any atom.
        for i in range(X.shape[1]):
            u = X[:, i]
            if len(np.unique(u)) <= 2:
                continue
            lo, hi = float(u.min()), float(u.max())
            qs = set(np.round(np.quantile(u, np.linspace(.1, .9, 9)), 6))
            lo_m = np.ceil(lo / 0.5) * 0.5
            qs |= {round(float(t), 6) for t in np.arange(lo_m, hi, 0.5)
                   if lo < t < hi}
            qs = sorted(qs)
            if len(qs) > 16:
                qs = qs[::int(np.ceil(len(qs) / 16))]
            for t in qs:
                self.specs.append(("step", i, None, float(t)))
        self.A = np.column_stack([_atom_col(X, s) for s in self.specs])
        n_atoms = self.A.shape[1]
        n_vars = X.shape[1]
        frontier = [(i,) for i in range(n_atoms)]
        frontier += [(i, j) for i in range(n_vars) for j in range(i, n_vars)]
        seen = set(frontier)
        while len(self.terms) < self.max_terms:
            cand = [t for t in frontier if t not in self.terms]
            M = np.column_stack([_disc_col(self.A, t) for t in cand])
            Ms = (M - M.mean(0)) / (M.std(0) + 1e-12)
            r = y - self._fit_predict(y)
            rs = (r - r.mean()) / (r.std() + 1e-12)
            real = np.abs(Ms.T @ rs) / len(y)
            # re-measured every round; capped so the null keeps >= 20 blocks
            # to permute — uncapped, a slow SIGNAL's own period inflates L
            # until the null preserves the structure under test (measured:
            # sin(1.5t) at L=76 became unfindable; power returns at the cap)
            self.block_L = min(self._decorr_len(rs), max(2, len(rs) // 20))
            null_max = np.empty(self.n_perm)
            for k in range(self.n_perm):
                null_max[k] = np.max(np.abs(Ms.T @ self._null_perm(rs))) / len(y)
            gate = np.percentile(null_max, self.pct)
            if real.max() <= gate:
                break                               # nothing beats its null
            # raw residual correlation is myopic: a degenerate surrogate (a
            # wide cosine mimicking a parabola) can out-correlate the TRUE
            # form on a bounded range. Judge the top candidates by how far
            # they actually go — trial-admit, refit, sharpen the inside-
            # parameter, score by train R2; parsimony breaks ties.
            base = list(self.terms)
            trials = []
            # shortlist needs STRUCTURAL DIVERSITY, not just top correlation:
            # bounded transcendental atoms are better-conditioned than heavy-
            # tailed raw variables, so the true raw-variable factor can sit
            # below the correlation top-10 and never get trialed. Guarantee
            # the best simple candidates (raw vars, low flexibility) a trial.
            ranks = [int(i) for i in np.argsort(-real)]
            simple = [ci for ci in ranks
                      if any(self.specs[a][0] == "var" for a in cand[ci])
                      and sum(1 for a in cand[ci]
                              if self.specs[a][3] is not None) <= 1]
            pure = [ci for ci in ranks
                    if all(self.specs[a][3] is None for a in cand[ci])]
            shortlist = list(dict.fromkeys(ranks[:8] + simple[:4] + pure[:3]))
            for ci in shortlist:
                if real[ci] <= gate:
                    continue
                self.terms = base + [cand[ci]]
                self._refit(y)
                self._refine_term(y, len(self.terms) - 1)
                # explicit parsimony pressure: a scale-parameterized atom is
                # flexible enough to mimic simpler forms on a bounded range
                # (a wide cosine IS a parabola locally) — so it must BUY its
                # flexibility with real R2. Flexibility already paid for is
                # free: only NEWLY introduced scale-atoms are charged.
                used_atoms = {a for t0 in base for a in t0}
                comp = sum(1 for a in self.terms[-1]
                           if self.specs[a][3] is not None
                           and a not in used_atoms)
                r2t = self._train_r2(y)
                pred = self._fit_predict(y)
                trials.append(dict(
                    done=r2t >= 0.995, r2=r2t,
                    sse=float(np.sum((y - pred) ** 2)), comp=comp,
                    tlen=len(self.terms[-1]), terms=list(self.terms)))
                self.terms = base
            if not trials:
                break
            done_set = [tr for tr in trials if tr["done"]]
            if done_set:
                # completers are judged STATISTICALLY: the F-test says
                # whether the best completer's edge over a rival is real
                # (red-team A1: gap 0.00024 in R2 was F~80, decisive) or a
                # noise-ceiling tie (2%-term surrogates: F~4). Significance
                # decides; genuine ties go to the SIMPLER form.
                bestd = min(done_set, key=lambda tr: tr["sse"])
                dof = max(bestd["sse"] / len(y), 1e-30)
                tied = [tr for tr in done_set
                        if (tr["sse"] - bestd["sse"]) / dof < 10.0]
                chosen = min(tied, key=lambda tr: (tr["comp"], tr["tlen"],
                                                   tr["sse"]))
            else:
                chosen = max(trials,
                             key=lambda tr: (tr["r2"] - 0.02 * tr["comp"],
                                             -tr["tlen"]))
            self.terms = chosen["terms"]
            self._refit(y)
            t = self.terms[-1]
            if len(t) < self.max_degree:            # beam: grow around winners
                for a in range(n_atoms):
                    nt = tuple(sorted(t + (a,)))
                    if len(nt) <= self.max_degree and nt not in seen:
                        seen.add(nt); frontier.append(nt)
        self._refine(y)                             # sharpen inside-parameters
        self._simple_rival(y)                       # a single sharpened form
        # must not lose to a blend that absorbs its own error
        self._round_terms(y)                        # taught rounding: a
        # measured inside-parameter's roundings are tested outright;
        # the simplest that does not lose is what the law SAYS
        if self.terms:                              # a term must carry weight
            keep = [t for t, c in zip(self.terms, self.coefs)
                    if abs(c) * _disc_col(self.A, t).std() > 0.02 * y.std()]
            self.terms = keep
            self._refit(y)
        return self

    def _refine(self, y, sweeps=3):
        """Regression finds coefficients; it cannot reach parameters INSIDE a
        nonlinearity (frequency, decay, scale). Hill-climb each admitted
        term's k by trial-refit — the grid proposes, this sharpens."""
        if not self.terms:
            return
        self._refit(y)
        for _ in range(sweeps):
            improved = False
            for ti in range(len(self.terms)):
                improved |= self._refine_term(y, ti)
            if not improved:
                break
        # the last digits are EARNED, not guessed: the coarse climb
        # above cannot correct a 0.2% frequency error, and the beat
        # such an error leaves is exactly the structure the replay
        # leg fires on (rounding battery red, 2026-07-17). Single-term
        # fits only: inside a blend, coordinate sharpening chases the
        # co-fit's noise (measured: it walked 1.7527 AWAY from 1.75) —
        # blends get the simple-rival duel instead (_simple_rival).
        if len(self.terms) == 1:
            for pos in range(len(self.terms[0])):
                self._sharpen_k(y, 0, pos)

    def _refine_term(self, y, ti, sweeps=2):
        improved_any = False
        for _ in range(sweeps):
            improved = False
            t = self.terms[ti]
            for pos, ai in enumerate(t):
                kind, i, j, k = self.specs[ai]
                if k is None or kind == "step":
                    # a threshold is a MARK — re-proposed, never glided
                    # (multiplicative glide slid steps out of range into
                    # constant columns; mechanisms battery, wrong-kept)
                    continue
                base = self._train_r2(y)
                for mult in (0.7, 0.85, 1.15, 1.4):
                    s2 = (kind, i, j, float(k * mult))
                    self.specs.append(s2)
                    self.A = np.column_stack([self.A, _atom_col(self.X, s2)])
                    trial = list(t); trial[pos] = len(self.specs) - 1
                    old = self.terms[ti]
                    self.terms[ti] = tuple(trial)
                    self._refit(y)
                    if self._train_r2(y) > base + 1e-6:
                        improved = improved_any = True
                        t = self.terms[ti]
                        break
                    self.terms[ti] = old
                    self._refit(y)
            if not improved:
                break
        return improved_any

    def _simple_rival(self, y):
        """THE SIMPLE RIVAL AT FIT END (the clean-majority law one
        level up, 2026-07-17): a flexible blend absorbs its own error
        — a pair of close-frequency waves imitates one wave of
        slightly-wrong k by seating junk on its own beat (rounding
        battery red, wrong-kept: the fold's 1.7527 smear seated two
        absorber waves and the replay rightly fired on the leftover).
        Each admitted term carrying an inside-parameter is offered
        ALONE, its k sharpened on the clean single-form ridge; if the
        single form reaches the blend within the noise's own tie
        (dof-scaled, same court as the rounding referee), fewer parts
        win and the blend is superseded. Exact blends are untouched:
        at r2 ~ 1 the tie collapses to machine zero."""
        if len(self.terms) < 2:
            return
        base = self._train_r2(y)
        n = len(y)

        def n_params(terms):
            # one coefficient per term + every tuned inside-k + slope
            return 1 + sum(1 + sum(1 for ai in t
                                   if self.specs[ai][3] is not None)
                           for t in terms)

        p_b = n_params(self.terms)
        save = list(self.terms)
        best = None
        for t in save:
            if not any(self.specs[ai][3] is not None
                       and self.specs[ai][0] != "step" for ai in t):
                continue
            self.terms = [t]
            self._refit(y)
            for pos in range(len(t)):
                self._sharpen_k(y, 0, pos)
            r2s = self._train_r2(y)
            # the F-test shape: the blend keeps its extra parts only
            # if its edge PER EXTRA PARAMETER beats what noise buys
            # (measured 2026-07-17: a 4-term blend's train edge over
            # the true single wave was 6.4e-5 = exactly q*(1-r2)/n —
            # pure parameter count, no signal)
            q = max(p_b - n_params(self.terms), 1)
            tie = 4.0 * q * (1.0 - base) / max(n - p_b, 1)
            if r2s >= base - tie and (best is None or r2s > best[0]):
                best = (r2s, list(self.terms))
            self.terms = list(save)
            self._refit(y)
        if best is not None:
            self.terms = best[1]
            self._refit(y)

    def _sharpen_k(self, y, ti, pos, span=0.03, steps=9, rounds=6):
        """Bounded local search on one inside-parameter: a shrinking
        multiplicative grid around the current k (span quarters each
        round; ~54 refits, all on already-admitted terms). Six rounds
        reach ~2e-5 relative resolution — a frequency error above
        that leaves a beat the replay leg rightly fires on (measured:
        4 rounds stopped 3.8e-4 short of pi and the referee tied at
        3.142). Steps are MARKS and are never glided (excluded, same
        law as _refine)."""
        t = self.terms[ti]
        ai = t[pos]
        kind, i, j, k = self.specs[ai]
        if k is None or kind == "step" or k == 0:
            return
        for _ in range(rounds):
            base = self._train_r2(y)
            best = None
            for c in np.geomspace(1.0 - span, 1.0 + span, steps):
                s2 = (kind, i, j, float(k * c))
                self.specs.append(s2)
                self.A = np.column_stack(
                    [self.A, _atom_col(self.X, s2)])
                trial = list(t)
                trial[pos] = len(self.specs) - 1
                old = self.terms[ti]
                self.terms[ti] = tuple(trial)
                self._refit(y)
                r2 = self._train_r2(y)
                if r2 > base + 1e-12 and (best is None or r2 > best[0]):
                    best = (r2, self.terms[ti])
                self.terms[ti] = old
                self._refit(y)
            if best is not None:
                self.terms[ti] = best[1]
                self._refit(y)
                t = self.terms[ti]
                kind, i, j, k = self.specs[t[pos]]
            span /= 4.0

    def _round_terms(self, y, tol=1e-9):
        """Taught rounding at fit end (owner, 2026-07-12): every
        admitted term's inside-parameter k has its roundings tested
        outright by trial refit, coarsest ruler mark first; the
        simplest that does not lose is what the law SAYS. 1.50008
        says 1.5; a true 3.14159 keeps its digits (every rounding
        loses). NON-LOSING is judged at the noise's own resolution
        (dof-scaled F-style tie), not at machine tie: the hand 1e-9
        asked the mark to beat the ML fit's noise chasing, which no
        true mark on a noisy world can do (rounding battery red,
        2026-07-17, wrong-kept) — on exact worlds the allowance
        collapses back to machine tie, so exactness stamps are
        untouched."""
        if not self.terms:
            return
        self._refit(y)
        n = len(y)
        p = len(self.terms) + 1
        for ti in range(len(self.terms)):
            t = self.terms[ti]
            for pos, ai in enumerate(t):
                kind, i, j, k = self.specs[ai]
                if k is None or kind == "step":
                    # a threshold is a MARK — re-proposed, never glided
                    # (multiplicative glide slid steps out of range into
                    # constant columns; mechanisms battery, wrong-kept)
                    continue
                base = self._train_r2(y)
                # f=8 ~ chi2(1)'s 99.5th pct: the mark differs from
                # the ML k-hat by exactly the noise-chasing the
                # sharpener did; f=4 left true marks refused on ~1 in
                # 20 draws (measured: 1.5's snap cost 3.0e-5 vs the
                # f=4 allowance 2.3e-5). pi's cost is ~100x any
                # allowance — invented simplicity stays refused.
                tie = max(8.0 * (1.0 - base) / max(n - p, 1), tol)
                for c in self._round_candidates(k):
                    s2 = (kind, i, j, float(c))
                    self.specs.append(s2)
                    self.A = np.column_stack(
                        [self.A, _atom_col(self.X, s2)])
                    trial = list(t)
                    trial[pos] = len(self.specs) - 1
                    old = self.terms[ti]
                    self.terms[ti] = tuple(trial)
                    self._refit(y)
                    if self._train_r2(y) >= base - tie and \
                            self._mark_survives_fresh(ti, pos, ai):
                        t = self.terms[ti]     # the simplest mark
                        break                  # that holds, adopted
                    self.terms[ti] = old
                    self._refit(y)

    def _mark_survives_fresh(self, ti, pos, ai_hat):
        """THE FRESH-ROW COURT for the rounding referee (2026-07-17):
        a train tie is not enough — the adopted mark must leave no
        PREDICTABLE structure on rows the sharpener never saw. Train
        r2 cannot arbitrate here (measured: the true mark 1.5 cost
        3.0e-5 while the false mark 3.142-for-pi cost 2.2e-5 — they
        overlap); fresh rows can: noise-chasing does not replicate on
        the held-out half, a real beat does. This is the replay leg's
        own question asked BEFORE adoption, so the referee and the
        judge share one court instead of convicting each other's
        verdicts. Standalone enumerator fits (no holdout attached)
        keep the train tie alone."""
        ho = getattr(self, "holdout", None)
        if ho is None:
            return True
        X_ho, y_ho = ho
        t_mark = self.terms[ti]

        def term_col(tt):
            col = np.ones(len(X_ho))
            for ai in tt:
                col = col * _atom_col(X_ho, self.specs[ai])
            return col

        # the displaced alternative: this term's column at k-hat minus
        # at the mark — exactly the shape a wrong mark leaves behind
        t_hat = list(t_mark)
        t_hat[pos] = ai_hat
        delta = term_col(t_hat) - term_col(t_mark)
        resid = y_ho - self.predict(X_ho)
        sd_d, sd_r = float(np.std(delta)), float(np.std(resid))
        if sd_d < 1e-12 or sd_r < 1e-12:
            return True
        dc = (delta - delta.mean()) / sd_d
        rc = resid - resid.mean()
        obs = abs(float(dc @ rc)) / len(rc)
        rngm = np.random.default_rng(97 + len(rc))
        null = [abs(float(dc @ rngm.permutation(rc))) / len(rc)
                for _ in range(200)]
        return obs <= float(np.quantile(null, 0.99))

    def _train_r2(self, y):
        p = self._fit_predict(y)
        ss = float(np.sum((y - y.mean()) ** 2))
        return 1 - float(np.sum((y - p) ** 2)) / max(ss, 1e-12)

    def rival_check(self, y, f_thr=10.0):
        """IDENTIFIABILITY: the classic look-alikes (parabola vs wide cosine,
        exponential vs cubic, decay vs hyperbola...) agree on the dense
        center of the data and split in tails and past turning points. For
        each admitted single-feature term, swap in each rival FORM, refit,
        refine, F-test. Rivals the data cannot reject stay ALIVE on the law's
        record, each with a PROBE: where to sample to split them."""
        SHAPES = [("linear", [("var",)]),
                  ("quadratic", [("var",), ("var",)]),
                  ("cubic", [("var",), ("var",), ("var",)]),
                  ("cosine", [("cos", 1.0)]),
                  ("sine", [("sin", 1.0)]),
                  ("exp_decay", [("exp", 0.5)]),
                  ("exp_growth", [("exp", -0.5)]),
                  ("log", [("pow", 0.0)]),
                  ("sqrt", [("pow", 0.5)])]
        out = []
        n = len(y)
        base_terms = [tuple(t) for t in self.terms]
        base_sse = float(np.sum((y - self._fit_predict(y)) ** 2))
        base_coefs, base_int = self.coefs.copy(), self.intercept
        for ti, t in enumerate(base_terms):
            feats = {self.specs[a][1] for a in t}
            feats |= {self.specs[a][2] for a in t
                      if self.specs[a][2] is not None}
            if len(feats) != 1:
                continue                      # unary confusions first
            i = int(list(feats)[0])
            kinds = tuple(sorted(self.specs[a][0] for a in t))
            for shape_name, atoms in SHAPES:
                s_kinds = tuple(sorted(a[0] for a in atoms))
                if s_kinds == kinds:
                    continue                  # that IS the current form
                term = []
                for a in atoms:
                    spec = (a[0], i, None, a[1] if len(a) > 1 else None)
                    self.specs.append(spec)
                    self.A = np.column_stack([self.A,
                                              _atom_col(self.X, spec)])
                    term.append(len(self.specs) - 1)
                self.terms = [list(x) for x in base_terms]
                self.terms[ti] = tuple(term)
                self.terms = [tuple(x) for x in self.terms]
                self._refit(y)
                self._refine_term(y, ti)
                sse = float(np.sum((y - self._fit_predict(y)) ** 2))
                better = min(sse, base_sse)
                F = (max(sse, base_sse) - better) / max(better / n, 1e-30)
                if F < f_thr:                 # the data cannot tell them apart
                    lo, hi = self.X[:, i].min(), self.X[:, i].max()
                    span = hi - lo
                    xs = np.linspace(lo - 0.75 * span, hi + 0.75 * span, 300)
                    Xs = np.tile(np.median(self.X, axis=0), (300, 1))
                    Xs[:, i] = xs
                    p_riv = self.predict(Xs)
                    riv = dict(terms=[list(x) for x in self.terms],
                               coefs=self.coefs.copy(),
                               intercept=self.intercept,
                               specs=list(self.specs),
                               equation=self.equation())
                    self.terms = [tuple(x) for x in base_terms]
                    self.coefs, self.intercept = base_coefs, base_int
                    p_cho = self.predict(Xs)
                    gap = np.abs(p_cho - p_riv)
                    x_star = float(xs[int(np.argmax(gap))])
                    out.append(dict(term=ti, feature=i, rival=shape_name,
                                    F=round(float(F), 1), model=riv,
                                    probe=dict(feature=i, x=round(x_star, 2),
                                               gap=round(float(gap.max()), 3),
                                               beyond=bool(x_star < lo or
                                                           x_star > hi)),
                                    rival_equation=riv["equation"]))
                self.terms = [tuple(x) for x in base_terms]
                self._refit(y)
        self.terms = [tuple(x) for x in base_terms]
        self._refit(y)
        return out

    def _design(self, A=None):
        A = self.A if A is None else A
        if not self.terms:
            return np.ones((A.shape[0], 1))
        return np.column_stack([_disc_col(A, t) for t in self.terms]
                               + [np.ones(A.shape[0])])

    def _refit(self, y):
        beta = np.linalg.lstsq(self._design(), y, rcond=None)[0]
        self.coefs, self.intercept = beta[:-1], float(beta[-1])

    def _fit_predict(self, y):
        if not self.terms:
            return np.full_like(y, y.mean())
        return self._design() @ np.concatenate([self.coefs, [self.intercept]])

    def predict(self, X):
        X = np.asarray(X, float)
        if not self.terms:
            return np.full(len(X), self.intercept)
        used = sorted({a for t in self.terms for a in t})
        cols = {a: _atom_col(X, self.specs[a]) for a in used}
        D = np.column_stack(
            [np.prod([cols[a] for a in t], axis=0) for t in self.terms]
            + [np.ones(len(X))])
        return D @ np.concatenate([self.coefs, [self.intercept]])

    def equation(self):
        if not self.terms:
            return "NO RULE (nothing beat the null)"
        parts = [f"{c:+.2f}*{'*'.join(_atom_label(self.specs[a]) for a in t)}"
                 for t, c in zip(self.terms, self.coefs)]
        return " ".join(parts) + f" {self.intercept:+.2f}"


class Isaac:
    def __init__(self):
        self.net = Net()
        self.starts = set()
        self.types = {}
        self.rules = []
        self.lockouts = set()             # ACTIVE lockouts (a comparison set)
        self.lockout_status = {}          # pair -> provisional | confirmed
        self.wrong_lockouts = {}          # retracted lockouts, with the why
        self.observed_sequences = []      # raw record (Rule 5: store raw)
        self.fact_index = defaultdict(list)  # (subject, relation) → [objects]
        self.active_container = "base"    # CONTAINERS (owner, 2026-07-15):
        self.container_tensions = []      # which world facts are IN FORCE in;
                                          # in-world contradictions, kept
        self.scratch = Scratch()          # working memory: his registers / RAM
        self.composites = []              # learned combinations — first-class,
                                          # reused by every future discover()
        self._compiled = None

        # ── pipeline state ──────────────────────────────────────
        self._compiled_up_to = 0          # how many sequences are in the matrix
        self._dirty_nodes = set()         # nodes with new doors since last consolidation
        self._consolidated_up_to = 0     # how many sequences consolidated
        self._type_profiles = {}          # cached type profiles

        # ── wave state ──────────────────────────────────────────
        self.activation_log = []          # one frozenset of active nodes per instant
        self.wave_logging = True          # observe/think record ticks automatically
        self.waves = {}                   # wave_consolidate() results
        self.followed = {}                # circles being tracked (his clock)
        self.phase_log = {}               # circle -> [(log_index, phase)]
        self.world = World(self)          # entity states: temporary statuses live here

        # ── findings ledger: durable, searchable scientific memory ──
        self.findings = []                # structured records of what he knows
        self.ledger_path = None           # set to a .jsonl path to persist

    # ── observation ─────────────────────────────────────────────

    def observe(self, tokens):
        """Stage 1 (SENSE): tokens in, doors built, dirty set updated,
        immediate type-slotting for known categories."""
        if not tokens:
            return
        self.starts.add(tokens[0])
        self.net.set_meta(tokens[0], "start", True)
        for i in range(len(tokens) - 1):
            self.net.add_door(tokens[i], tokens[i + 1], tag="seq")
        self.observed_sequences.append(list(tokens))
        # Mark dirty — new data not yet consolidated
        for t in tokens:
            self._dirty_nodes.add(t)
        # Stage 1: immediately slot new tokens into existing types
        self._sense(tokens)
        # wave sensing: each token is one instant; it lights together with
        # the types it opens — simultaneity the wave pass can see
        if self.wave_logging:
            for t in tokens:
                self.tick({t} | self.net.get_doors(t, tag="type"))

    def _sense(self, tokens):
        """Stage 1 (SENSE): check if new tokens fit existing types.
        Immediate slotting — O(k × T), runs on every observe.
        Full type discovery waits for consolidate()."""
        if not self.types:
            return
        for token in set(tokens):
            # Skip if already typed
            if self.net.get_doors(token, tag="type"):
                continue
            preds = self.net.get_predecessors(token, tag="seq")
            succs = self.net.get_doors(token, tag="seq")
            if not preds and not succs:
                continue
            for tname, tdata in self.types.items():
                tp = tdata.get("preds", set())
                ts = tdata.get("succs", set())
                shared_p = preds & tp if tp else set()
                shared_s = succs & ts if ts else set()
                if len(shared_p) + len(shared_s) >= 2:
                    tdata["members"].add(token)
                    self.net.add_door(token, tname, tag="type")
                    break

    def observe_negative(self, tokens):
        """Same mechanism, different tag. Negation is contrast, not storage."""
        if not tokens:
            return
        for i in range(len(tokens) - 1):
            self.net.add_door(tokens[i], tokens[i + 1], tag="neg")

    def observe_matrix(self, matrix, row_prefix=None):
        """Observe a 2D data matrix. Each row becomes a sequence of tokens.
        No preprocessing. No feature extraction. Just the numbers.

        matrix: 2D numpy array or list of lists
        row_prefix: optional prefix per row (e.g., 'r0', 'r1', ...) for position
        """
        for i, row in enumerate(matrix):
            tokens = [str(int(v)) for v in row]
            if row_prefix:
                tokens.insert(0, f"{row_prefix}{i}")
            self.observe(tokens)

    def observe_frame(self, frame, label=None):
        """Observe a full video/game frame as a matrix.
        Handles 2D (grayscale) or 3D (color) arrays.
        Flattens color channels per pixel. Each row is one observation.

        frame: numpy array (H, W) or (H, W, C)
        label: optional frame label (e.g., 'f0', 'f1', ...) prepended to first row
        """
        if frame.ndim == 3:
            # Color frame: flatten channels per pixel
            h, w, c = frame.shape
            flat = frame.reshape(h, w * c)
        else:
            flat = frame

        for i, row in enumerate(flat):
            tokens = [str(int(v)) for v in row]
            if label and i == 0:
                tokens.insert(0, label)
            self.observe(tokens)

    def observe_tagged(self, tokens, tag):
        """Observe with a custom tag. Properties, relations, anything."""
        if not tokens:
            return
        for i in range(len(tokens) - 1):
            self.net.add_door(tokens[i], tokens[i + 1], tag=tag)

    def open_world(self, container):
        """Open a WORLD (CONTAINERS, owner 2026-07-15: "fiction world
        harry potter has different rules than fiction world hail
        mary"). Routing state: facts taught while a world is open are
        IN FORCE there; asking routes by world. Returns a receipt."""
        prev = getattr(self, "active_container", "base")
        self.active_container = str(container)
        return dict(tool="open_world", value=str(container),
                    receipt=f"world '{prev}' -> '{container}' (facts "
                            f"teach and ask in '{container}' unless "
                            f"told otherwise)")

    def ask(self, subject, relation, container=None, inherit=True):
        """Ask a fact IN A WORLD. Facts in force in the asked container
        answer; a fiction world INHERITS base one-way with a receipt
        (HP water still boils at 100C); base NEVER inherits fiction
        (the anti-poisoning wall, measured: 0 leaks, 0 drift);
        container-less facts belong to base, receipt says so."""
        c = container or getattr(self, "active_container", "base")
        objs = [str(o) for o in self.fact_index.get((subject, relation),
                                                    [])]
        seen = list(dict.fromkeys(objs))

        def tags(o):
            return self.net.get_door_tags(str(subject), o)

        in_c = [o for o in seen if f"in:{c}" in tags(o)]
        if in_c:
            return dict(answers=in_c, container=c,
                        why=f"{len(in_c)} fact(s) in force in '{c}'")
        if c == "base":
            untagged = [o for o in seen
                        if not any(t.startswith("in:")
                                   for t in tags(o))]
            if untagged:
                return dict(answers=untagged, container="base",
                            why="container-less fact(s): landed in "
                                "base (receipt)")
            return dict(answers=[], container="base",
                        why="nothing in force in base")
        if inherit:
            base = self.ask(subject, relation, container="base")
            if base["answers"]:
                return dict(answers=base["answers"], container=c,
                            why=f"inherited from base (no '{c}' fact "
                                f"overrides) — {base['why']}")
        return dict(answers=[], container=c,
                    why=f"nothing in force in '{c}'")

    def teach(self, subject, relation, obj, container=None):
        """Teach a fact. Observes as a sequence AND indexes for
        relation lookup. CONTAINERS: the fact is stamped with the
        world it is true IN (the active container unless told); an
        in-world contradiction is FLAGGED and kept (both readings
        stay — wrongs kept), while cross-world difference never
        flags (different worlds legitimately differ)."""
        c = container or getattr(self, "active_container", "base")
        prior = self.ask(subject, relation, container=c, inherit=False)
        self.observe(tokenize(f"{subject} {relation} {obj}"))
        self.fact_index[(subject, relation)].append(obj)
        self.net.add_door(str(subject), str(obj), tag=f"in:{c}")
        if prior["answers"] and str(obj) not in prior["answers"]:
            if not hasattr(self, "container_tensions"):
                self.container_tensions = []
            self.container_tensions.append(dict(
                container=c, subject=str(subject),
                relation=str(relation), held=list(prior["answers"]),
                new=str(obj)))

    def teach_not(self, subject, prop):
        """A POSITIVE NEGATIVE (owner's law, 2026-07-03): 'penguin does not
        fly' is evidence, not absence. Indexed as a cannot-fact (the
        reasoning layer already honors those) AND written as a first-class
        not_<prop> door, so negative knowledge is present in door profiles
        — where crystallization can both SEE it (penguins and ostriches
        share not_fly) and be VETOED by it (known-different never merges;
        only unknown may)."""
        if prop not in self.fact_index[(subject, "cannot")]:
            self.fact_index[(subject, "cannot")].append(prop)
        self.net.add_door(subject, f"not_{prop}", tag="neg")

    # ── crystallization ─────────────────────────────────────────

    def _crystallize(self, tag="seq", min_shared=2, verbose=False, scope=None):
        """Internal: discover types by comparing door profiles. FCA closure.
        If scope is provided, only pairs involving at least one scope node
        are compared — O(d×n) instead of O(n²)."""
        nodes = sorted([n for n in self.net.all_nodes()
                        if not n.startswith("type:")])
        scope_set = set(scope) if scope else None

        # Phase 1: raw circles via FCA. min_shared stays as the CANDIDATE
        # floor (expansion — propose freely); admission is Phase 3.5's test.
        # PERFORMANCE (2026-07-12, measured on real conversation: 500
        # sentences took 172 s, 30M get_doors / 530M dict.gets — the
        # all-pairs loop refetched door sets per pair and the closure
        # rescanned every node per circle): door profiles are CACHED
        # once, candidate pairs come from the REVERSE INDEX (the E3
        # lesson applied here — only nodes sharing a context can ever
        # reach min_shared), and closures intersect index sets.
        # pairs_scanned keeps the ORIGINAL arithmetic count (the
        # admission's selection charge is unchanged). Same circles,
        # same order, same verdicts — measured 66x faster.
        circles = []
        # LEARNED ONCE, NEVER REPROCESSED (owner, 2026-07-12: "maybe
        # just dont refuse them. learn them, then they will just be
        # in the net and not need to be reprocessed"): the circle
        # memory persists — a member-set already learned (as a sound
        # type OR a wrong one) is skipped before it can cost another
        # merge, reconcile, or verdict. Wrong is kept so it never
        # costs again. The flush resets the memory with everything
        # else.
        seen = getattr(self, "_seen_circles", None)
        if seen is None or scope is None:
            seen = set()
            self._seen_circles = seen
        pos = {n: i for i, n in enumerate(nodes)}
        # THE PERSISTENT MATRIX (owner, 2026-07-12: "anything adjacent
        # or correlated was supposed to be imported... it is purging
        # the matrix each time when it should just be reusing the
        # matrix unless it needs a flush"): door profiles and the
        # reverse index live on the instance and are refreshed
        # ADDITIVELY for dirty nodes only — doors are append-only, so
        # nothing ever needs invalidation. A scoped consolidate
        # touches its neighborhood; full=True is the flush.
        ctx = getattr(self, "_ctx_matrix", None)
        if ctx is None or ctx["tag"] != tag or scope is None:
            ctx = dict(tag=tag, P={}, S={}, pred_index={},
                       succ_index={}, universe=set())
            refresh = nodes
            self._ctx_matrix = ctx
        else:
            refresh = [n for n in (scope or nodes) if n in pos]
        P, S = ctx["P"], ctx["S"]
        pred_index, succ_index = ctx["pred_index"], ctx["succ_index"]
        universe = ctx["universe"]
        for n in refresh:
            P[n] = self.net.get_predecessors(n, tag=tag)
            S[n] = self.net.get_doors(n, tag=tag)
            for c in P[n]:
                pred_index.setdefault(c, set()).add(n)
            for c in S[n]:
                succ_index.setdefault(c, set()).add(n)
            universe |= P[n]
            universe |= S[n]
        for n in nodes:
            if n not in P:
                P[n] = self.net.get_predecessors(n, tag=tag)
                S[n] = self.net.get_doors(n, tag=tag)
                for c in P[n]:
                    pred_index.setdefault(c, set()).add(n)
                for c in S[n]:
                    succ_index.setdefault(c, set()).add(n)
                universe |= P[n]
                universe |= S[n]
        # the selection charge, arithmetically identical to the old loop
        n_total = len(nodes)
        pairs_scanned = 0
        if scope_set is None:
            for i, a in enumerate(nodes):
                if P[a] or S[a]:
                    pairs_scanned += n_total - i - 1
        else:
            suffix = [0] * (n_total + 1)
            for i in range(n_total - 1, -1, -1):
                suffix[i] = suffix[i + 1] + (1 if nodes[i] in scope_set
                                             else 0)
            for i, a in enumerate(nodes):
                if P[a] or S[a]:
                    pairs_scanned += (n_total - i - 1
                                      if a in scope_set else suffix[i + 1])

        def _closure(shared_p, shared_s, seed_pair):
            sets = ([pred_index.get(c, set()) for c in shared_p]
                    + [succ_index.get(c, set()) for c in shared_s])
            if not sets:
                return set(seed_pair)
            sets.sort(key=len)
            out = set(sets[0])
            for s in sets[1:]:
                out &= s
                if not out:
                    break
            return out | set(seed_pair)

        # relevance IS the doors: a node's candidate partners are its
        # context-sharers from the reverse index — scoped passes walk
        # only the dirty neighborhood, in both directions
        seen_pairs = set()
        iter_nodes = nodes if scope_set is None else \
            sorted((x for x in scope_set if x in pos), key=pos.get)
        for a in iter_nodes:
            preds_a, succs_a = P[a], S[a]
            if not preds_a and not succs_a:
                continue
            cand = set()
            for c in preds_a:
                cand |= pred_index.get(c, set())
            for c in succs_a:
                cand |= succ_index.get(c, set())
            ia = pos[a]
            for b in sorted(cand, key=pos.get):
                if b == a:
                    continue
                if scope_set is None and pos[b] <= ia:
                    continue          # unscoped: each pair once
                pk = (a, b) if pos[b] > ia else (b, a)
                if pk in seen_pairs:
                    continue
                seen_pairs.add(pk)
                shared_p = preds_a & P[b]
                shared_s = succs_a & S[b]
                if len(shared_p) + len(shared_s) < min_shared:
                    continue
                members = _closure(shared_p, shared_s, pk)
                key = frozenset(members)
                if key not in seen and len(members) >= 2:
                    seen.add(key)
                    circles.append({"members": members,
                                    "preds": shared_p, "succs": shared_s})

        # Phase 1.5 (the owner's foundation law, 2026-07-03): DIVERGENT
        # doors SELF-ASSEMBLE. The atom's three verdicts finally all write:
        #   SAME      -> membership (always did)
        #   DIVERGENT -> a not_<door> minted from experience
        #   ABSENT    -> nothing (insufficient evidence stays silent)
        # A node that carries the REST of a circle's intent, observed
        # repeatedly WITHOUT the one door its siblings show essentially
        # always, has positively diverged — penguin earns not_fly by being
        # WATCHED, not taught. The null is "this node is like its
        # siblings"; the gate is a smoothed binomial on observation
        # counts, not a constant. Runs BEFORE the merge so a fresh
        # negative can veto a collapse in the same sleep.
        counts = getattr(self.net, "door_counts", {})
        for c in circles:
            intent = {d for d in c["succs"]
                      if not (isinstance(d, str) and d.startswith("not_"))}
            if len(intent) < 2:
                continue
            for d in intent:
                rest = intent - {d}
                obs_sib = sum(max((counts.get((s, r), 0) for r in rest),
                                  default=0) for s in c["members"])
                with_d = sum(counts.get((s, d), 0) for s in c["members"])
                p_hat = (with_d + 1) / (obs_sib + 2)     # Laplace-smoothed
                rest_sets = sorted((succ_index.get(r, set())
                                    for r in rest), key=len)
                cand_m = set(rest_sets[0]) if rest_sets else set()
                for s_ in rest_sets[1:]:
                    cand_m &= s_
                for m in sorted(cand_m - c["members"], key=pos.get):
                    if d in S[m]:
                        continue
                    n_m = min(counts.get((m, r), 0) for r in rest)
                    # repeatable evidence (>= 3 sightings) AND absence must
                    # beat the like-your-siblings null at 1%
                    if n_m >= 3 and (1 - p_hat) ** n_m < 0.01:
                        self.net.add_door(m, f"not_{d}", tag="neg")
                        if d not in self.fact_index[(m, "cannot")]:
                            self.fact_index[(m, "cannot")].append(d)

        # Phase 2: merge overlapping circles (Rule 13; AMENDED 2026-07-03
        # to the owner's two laws). (1) Merge ONLY near-identical member
        # sets (overlap vs the LARGER set): a proper subgroup is a real
        # thing of its own — abc and abd are not the same thing; both may
        # belong to ab via the hierarchy, never by dissolving into it.
        # (2) A POSITIVE NEGATIVE VETOES any merge: penguin not_fly is
        # evidence, not absence — a merge that would erase a distinction
        # some member has positively disclaimed is forbidden. Unknown may
        # collapse; known-different never does.
        def _negs_of(members):
            out = set()
            for m in members:
                out |= set(self.fact_index.get((m, "cannot"), []))
                for t in (tag, "neg"):
                    out |= {d[4:] for d in self.net.get_doors(m, tag=t)
                            if isinstance(d, str) and d.startswith("not_")}
            return out

        def _pos_of(c):
            return {d for d in c["succs"]
                    if not (isinstance(d, str) and d.startswith("not_"))}

        merged = []
        used = set()
        circles.sort(key=lambda c: len(c["members"]), reverse=True)
        # relevance again: a merge partner must share >=80% of the
        # larger member set, so it must share MEMBERS — candidates
        # come from a member->circles index, never a full scan
        import heapq
        cidx = {}
        for j, c in enumerate(circles):
            for m in c["members"]:
                cidx.setdefault(m, []).append(j)
        for i, c in enumerate(circles):
            if i in used:
                continue
            current = {"members": set(c["members"]),
                       "preds": set(c["preds"]), "succs": set(c["succs"])}
            heap, pushed = [], set()

            def _push(ms):
                for m in ms:
                    for j in cidx.get(m, ()):
                        if j > i and j not in used and j not in pushed:
                            pushed.add(j)
                            heapq.heappush(heap, j)

            _push(current["members"])
            while heap:
                j = heapq.heappop(heap)
                if j in used:
                    continue
                other = circles[j]
                larger = max(len(current["members"]), len(other["members"]))
                overlap = len(current["members"] & other["members"])
                if larger == 0 or overlap / larger < 0.8:
                    continue          # subgroup/sibling: keep it its own thing
                if (_pos_of(current) & _negs_of(other["members"])
                        or _pos_of(other) & _negs_of(current["members"])):
                    continue          # positively negative: never collapse
                new_m = other["members"] - current["members"]
                current["members"] |= other["members"]
                current["preds"] &= other["preds"]
                current["succs"] &= other["succs"]
                used.add(j)
                _push(new_m)
            merged.append(current)

        # Phase 3: name and write to net. THE MATRIX IS NOT PURGED
        # (owner, 2026-07-12): existing types persist across scoped
        # consolidates; this pass's circles RECONCILE into them —
        # identical member-sets are already known, near-identical
        # ones ABSORB (the same 0.8-overlap + negative-veto laws the
        # merge uses; supersession, never overwrite), genuinely new
        # ones mint new nodes. full=True is the flush and starts
        # clean, exactly as before.
        if scope is None:
            self.types = {}
        touched = []
        existing_keys = {frozenset(t["members"]) for t in
                         self.types.values()}
        # the member->types reverse index makes reconcile RELEVANT:
        # a circle meets only types it shares members with (measured:
        # scanning all standing types made persistence SLOWER than
        # the purge it replaced — 652 s vs 234 s at 2,000 sentences)
        tindex = getattr(self, "_type_member_index", None)
        if scope is None or tindex is None:
            tindex = {}
            for tn, t in self.types.items():
                for m in t["members"]:
                    tindex.setdefault(m, set()).add(tn)
            self._type_member_index = tindex
        for c in merged:
            key = frozenset(c["members"])
            if key in existing_keys:
                continue                        # already known
            absorbed = False
            cand_types = set()
            for m in c["members"]:
                cand_types |= tindex.get(m, set())
            for tn in sorted(cand_types):
                t = self.types[tn]
                larger = max(len(t["members"]), len(c["members"]))
                overlap = len(t["members"] & c["members"])
                if larger and overlap / larger >= 0.8:
                    if (_pos_of(c) & _negs_of(t["members"])
                            or _pos_of(t) & _negs_of(c["members"])):
                        continue      # positively negative: no merge
                    new_m = c["members"] - t["members"]
                    t["members"] |= c["members"]
                    t["preds"] &= c["preds"]
                    t["succs"] &= c["succs"]
                    for m in new_m:
                        self.net.add_door(m, t["name"], tag="type")
                        tindex.setdefault(m, set()).add(t["name"])
                    existing_keys.add(frozenset(t["members"]))
                    touched.append(t)
                    absorbed = True
                    break
            if absorbed:
                continue
            name = f"type:{'_'.join(sorted(c['members'])[:2])}[{len(c['members'])}]"
            while name in self.types:           # stable ids, no clobber
                name += "'"
            c["name"] = name
            c["parent"] = None
            c["children"] = []
            self.types[name] = c
            existing_keys.add(key)
            touched.append(c)
            for m in c["members"]:
                self.net.add_door(m, name, tag="type")
                tindex.setdefault(m, set()).add(name)

        # Phase 3.5 (owner's law, 2026-07-03): WRONG IS KEPT AND CLASSIFIED.
        # "knowing what is right is intelligence. knowing what is wrong is
        # wisdom." Every type is tested against its chance-null — the same
        # context with door targets shuffled (degrees preserved), scored by
        # the BEST structure chance produces (selection-corrected). Types
        # that fail are NOT deleted and NOT prevented: they are filed in
        # the wrong section with the WHY attached, so error itself becomes
        # learnable material. Downstream behavior is deliberately unchanged
        # (no pruning, no importance-weighting — the old trap).
        # A2 (2026-07-04): the verdict is now a degrees-aware TEST, not a
        # shuffle score. SUPERSEDES the 07-03 global re-clustering shuffle
        # (same battery verdicts — C1 sound, C3 249/249 wrong — at O(types)
        # instead of O(shuffles × n²); the shuffle survives in git and the
        # BUILD_STATE entry, wearing its succession). The claim a type makes:
        # "these m members share this k-door intent beyond chance, given
        # their degrees and this context's universe." p(type) =
        #   pairs_scanned                          (selection charge)
        #   × P(the two chanciest members' door-sets share >= k | degrees)
        #   × ∏ remaining members' chance of covering the whole intent.
        from math import lgamma, exp

        def _lC(a, b):
            if b < 0 or b > a:
                return None
            return lgamma(a + 1) - lgamma(b + 1) - lgamma(a - b + 1)

        N_univ = max(len(universe), 2)

        def _coverage(d, k):
            # P(a random d-subset of the universe contains all k intent doors)
            la, lb = _lC(N_univ - k, d - k), _lC(N_univ, d)
            if la is None or lb is None:
                return 0.0
            return exp(la - lb)

        if scope is None or not hasattr(self, "wrong_types"):
            self.wrong_types = {}
        for c in touched:
            k_int = len(c["preds"]) + len(c["succs"])
            score = (len(c["members"]) - 1) * k_int
            c["score"] = score
            degs = sorted((min(len(P.get(m) if m in P else
                                   self.net.get_predecessors(m, tag=tag))
                               + len(S.get(m) if m in S else
                                     self.net.get_doors(m, tag=tag)),
                               N_univ) for m in c["members"]),
                          reverse=True)
            p = float(max(pairs_scanned, 1))
            if len(degs) >= 2:
                p *= _hyper_tail(N_univ, degs[0], degs[1], k_int)
            for d in degs[2:]:
                p *= _coverage(d, k_int)
            p = min(1.0, p)
            c["p_chance"] = p
            self.net.set_meta(c["name"], "p_chance", p)
            if p >= 0.01:
                why = (f"intent of {k_int} doors shared by "
                       f"{len(c['members'])} members is within chance for "
                       f"their degrees in a {N_univ}-door universe "
                       f"(p≈{p:.3g} ≥ 0.01 after {pairs_scanned} pairs "
                       f"scanned) — co-occurrence alone explains it")
                c["verdict"] = "wrong"
                c["why_wrong"] = why
                self.wrong_types[c["name"]] = c
                self.net.set_meta(c["name"], "verdict", "wrong")
                self.net.set_meta(c["name"], "why_wrong", why)
            else:
                c["verdict"] = "sound"
                self.net.set_meta(c["name"], "verdict", "sound")

        # Phase 4: hierarchy (subset = child). The 0.8 containment stays as
        # the DEFINITION of "belongs under" BETWEEN SOUND TYPES — they
        # already passed the admission test; double-gating broke the
        # owner-settled abc/abd law (battery C2a caught it). Wrong-verdict
        # types are KEPT and classified but demoted from ORGANIZING (law 4,
        # the same demotion route()/senses use): chance structure may
        # exist; it does not get to build the hierarchy. (A hypergeometric
        # OR-branch was tried and failed its battery — chance types share
        # members by construction, so independent-draws significance is
        # the wrong null for "should these organize"; admission battery
        # A2b caught 7 chance links.)
        n_ctx = max(len(nodes), 2)
        type_list = list(self.types.values())
        torder = {tn: i for i, tn in enumerate(self.types)}
        # scoped passes parent only the types this pass touched;
        # standing parent links persist (the flush re-derives all).
        # Parent candidates come from the member index (a parent must
        # hold >=80% of the child's members — it must share members).
        child_iter = type_list if scope is None else \
            [t for t in touched if not t.get("parent")]
        for child in child_iter:
            cand_p = set()
            for m in child["members"]:
                cand_p |= tindex.get(m, set())
            for pname in sorted(cand_p, key=lambda x: torder.get(x, 1 << 30)):
                parent = self.types.get(pname)
                if parent is None or child is parent:
                    continue
                if len(child["members"]) >= len(parent["members"]):
                    continue
                if not (child.get("verdict") == "sound"
                        and parent.get("verdict") == "sound"):
                    continue
                overlap = len(child["members"] & parent["members"])
                if overlap / len(child["members"]) >= 0.8:
                    child["parent"] = parent["name"]
                    parent["children"].append(child["name"])
                    self.net.add_door(child["name"], parent["name"],
                                     tag="subtype_of")
                    break

        # Phase 5: discover rules (co-occurring predecessors) — a
        # predecessor's set IS its successor doors, read through the
        # persistent matrix (no refetching); scoped passes pair only
        # predecessors whose sets changed; standing rules persist
        if scope is None or not hasattr(self, "rules"):
            self.rules = []
        rule_keys = {(r[0], r[1]) for r in self.rules}
        preds = [p for p in nodes if len(S.get(p) or ()) >= 3]
        ppos = {p: i for i, p in enumerate(preds)}
        done_pairs = set()
        p_iter = preds if scope_set is None else \
            [p for p in preds if p in scope_set]
        for a in p_iter:
            for b in preds:
                if b == a:
                    continue
                pk = (a, b) if ppos[a] < ppos[b] else (b, a)
                if pk in done_pairs or pk in rule_keys:
                    continue
                done_pairs.add(pk)
                sa, sb = S[pk[0]], S[pk[1]]
                overlap = len(sa & sb)
                ratio_a = overlap / len(sa) if sa else 0
                ratio_b = overlap / len(sb) if sb else 0
                # A2: the ratio stays as strength; the chance gate decides
                # admission (overlap must beat independence at 1%)
                if ((ratio_a >= 0.8 or ratio_b >= 0.8)
                        and _hyper_tail(n_ctx, len(sa), len(sb),
                                        overlap) < 0.01):
                    self.rules.append((pk[0], pk[1],
                                       round(max(ratio_a, ratio_b), 2)))
                    self.net.add_door(pk[0], pk[1], tag="cooccurs")

        # Phase 6: violations (seq vs neg contrast)
        self._discover_violations()

        # Phase 7: initiator ranking
        for s in self.starts:
            strength = len(self.net.get_doors(s, tag="seq"))
            self.net.set_meta(s, "initiator_strength", strength)

        if verbose:
            print(f"  crystallized: {len(self.types)} types, "
                  f"{len(self.rules)} rules, {len(self.lockouts)} lockouts")
        return self.types

    def _discover_violations(self):
        """Compare seq doors vs neg doors. The difference IS negation.
        A4 (2026-07-04): lockouts are EVIDENCE-WEIGHTED and revisable —
        one negative observation locks PROVISIONALLY (active, honestly
        labeled); repeated negatives (>=2) lock CONFIRMED; a lockout later
        contradicted by positive observation is RETRACTED from the active
        set into wrong_lockouts with the why (the net keeps the door —
        nothing leaves the net; the ACTIVE set is a comparison set, law 4)."""
        seq_pairs = set()
        neg_pairs = set()
        for (src, tgt), tags in self.net.door_tags.items():
            if "seq" in tags:
                seq_pairs.add((src, tgt))
            if "neg" in tags:
                neg_pairs.add((src, tgt))
        counts = getattr(self.net, "door_counts", {})
        if not hasattr(self, "wrong_lockouts"):
            self.wrong_lockouts = {}
        if not hasattr(self, "lockout_status"):
            self.lockout_status = {}
        # retraction: a locked pair now positively observed is overturned
        for pair in list(self.lockouts):
            if pair in seq_pairs:
                self.lockouts.discard(pair)
                self.wrong_lockouts[pair] = (
                    f"retracted: contradicted by positive observation "
                    f"(pair count {counts.get(pair, 0)}) — was "
                    f"{self.lockout_status.get(pair, 'provisional')}")
                self.lockout_status.pop(pair, None)
        for pair in (neg_pairs - seq_pairs):
            src, tgt = pair
            has_lock = "lockout" in self.net.get_door_tags(src, tgt)
            # evidence = observations of the pair minus the single
            # lockout-door bookkeeping add (guarded to at most one)
            ev = max(counts.get(pair, 1) - (1 if has_lock else 0), 1)
            if not has_lock:
                self.net.add_door(src, tgt, tag="lockout")
            self.lockouts.add(pair)
            self.lockout_status[pair] = ("confirmed" if ev >= 2
                                         else "provisional")

    # ── compilation ─────────────────────────────────────────────
    # Doors → matrix. Same information, different representation.
    # W[delta, frame] = door count. y = W @ x. Answer from y.

    def _ensure_compiled(self):
        """Stage 3 (ROUTE): lazy compilation. Only recompile if dirty.
        Called automatically before any inference. Never call compile() manually."""
        if self._compiled_up_to < len(self.observed_sequences):
            self._compile()
        return self._compiled is not None

    def _compile(self, max_context=7):
        """Internal: build the weight matrix from observed sequences."""
        pairs = []
        for seq in self.observed_sequences:
            if len(seq) < 2:
                continue
            frame = tuple(seq[:-1])
            delta = seq[-1]
            pairs.append((frame, delta))
            for width in range(2, min(len(frame) + 1, max_context)):
                partial = frame[-width:]
                if partial != frame:
                    pairs.append((partial, delta))

        if not pairs:
            self._compiled = None
            self._compiled_up_to = len(self.observed_sequences)
            return None

        frames = sorted(set(f for f, d in pairs))
        deltas = sorted(set(d for f, d in pairs))
        fidx = {f: i for i, f in enumerate(frames)}
        didx = {d: i for i, d in enumerate(deltas)}

        W = np.zeros((len(deltas), len(frames)), dtype=np.float32)
        for frame, delta in pairs:
            W[didx[delta], fidx[frame]] += 1.0
        col_sums = W.sum(axis=0, keepdims=True)
        col_sums[col_sums == 0] = 1
        W_norm = W / col_sums

        self._compiled = {
            "W": W, "W_norm": W_norm,
            "frames": frames, "deltas": deltas,
            "fidx": fidx, "didx": didx,
        }
        self._compiled_up_to = len(self.observed_sequences)
        return {
            "frames": len(frames), "deltas": len(deltas),
            "nonzero": int((W != 0).sum()),
            "matrix_shape": W.shape,
        }

    def compile(self, max_context=7):
        """Convenience wrapper. Prefer automatic compilation via lookup/check."""
        return self._compile(max_context)

    def consolidate(self, tag="seq", min_shared=2, verbose=False, full=False):
        """IDLE MODE: Crystallization of dirty regions.
        Run when nothing is waiting. This is sleep.

        By default, scopes to dirty nodes — O(d×n) instead of O(n²).
        Pass full=True to force a complete re-crystallization."""
        scope = None if full or not self._dirty_nodes else list(self._dirty_nodes)
        result = self._crystallize(tag=tag, min_shared=min_shared,
                                   verbose=verbose, scope=scope)
        self._consolidated_up_to = len(self.observed_sequences)
        self._dirty_nodes.clear()
        return result

    def crystallize(self, tag="seq", min_shared=2, verbose=False):
        """Convenience alias. Runs full (unscoped) consolidation."""
        return self.consolidate(tag=tag, min_shared=min_shared,
                                verbose=verbose, full=True)

    # ── waves: temporal crystallization ─────────────────────────

    def tick(self, active):
        """Record one instant of simultaneous activation. Any sensing path
        may call this directly (a retina, a game loop, a sensor frame);
        observe() and the think loop call it automatically.

        If a circle is being followed (see follow()), every tick also advances
        his phase register, registers expectation against observation, and
        opens/clears temporary statuses — whose miss-doors join THIS tick, so
        the ordinary machinery can crystallize them later. (Clock ticks are
        sensory ticks: mixing unrelated observe() streams into a followed
        sensor stream will dead-reckon the clock forward — keep one stream
        per episode, or pause with wave_logging=False.)"""
        if not active:
            return
        active = set(active)
        for circle in list(self.followed):
            active |= self._track(circle, active)
        self.activation_log.append(frozenset(active))

    def follow(self, circle):
        """Attend to a discovered circle: initialize his clock over its phases.
        State lives in scratch; transitions are the circle's own wave_next
        doors; dwell (for dead reckoning) was learned at consolidation."""
        phases = [p for p in self.net.get_predecessors(circle, tag="wave")
                  if str(p).startswith("wave:")]
        if not phases:
            return False
        order, pset = [phases[0]], set(phases)
        while len(order) < len(phases):
            nxt = [d for d in self.net.get_doors(order[-1], tag="wave_next")
                   if d in pset and d not in order]
            if not nxt:
                order += [p for p in phases if p not in order]
                break
            order.append(nxt[0])
        self.followed[circle] = {
            "order": order,
            "members": {p: set(self.net.get_predecessors(p, tag="wave"))
                        for p in order},
            "dwell": {p: float(self.net.get_meta(p, "dwell", 3.0))
                      for p in order}}
        self.scratch.write(f"phase@{circle}", None)
        self.scratch.write(f"dwell@{circle}", 0)
        self.phase_log.setdefault(circle, [])
        return True

    def _track(self, circle, active):
        """One clock step: evidence advances the phase (via recognize_doors —
        partial recognition, so an occluded entity still fires); learned dwell
        dead-reckons when evidence is hidden. Expected-but-dark doors that
        persist open temporary statuses: a status is a world-state fact AND a
        door fed back into the stream."""
        f = self.followed[circle]
        reg, dw = f"phase@{circle}", f"dwell@{circle}"
        fired = self.recognize_doors(active, tag="part", threshold=0.5)
        cur = self.scratch.read(reg)
        order = f["order"]
        if cur is None:                                # first evidence seats the clock
            cands = [p for p in order if p in fired]
            if not cands:
                return set()
            cur = max(cands, key=lambda p: fired[p])
            self.scratch.write(reg, cur)
            self.scratch.write(dw, 0)
        nxt = order[(order.index(cur) + 1) % len(order)]
        advanced = False
        if fired.get(nxt, 0) >= 0.5 and fired.get(cur, 0) < 0.5:
            advanced = True
        elif cur not in fired and (self.scratch.read(dw) or 0) >= f["dwell"][cur]:
            advanced = True
        if advanced:
            # the entity leaves the stage: nothing is expected of it now, so
            # its open statuses close (absence-by-night is not a status)
            for d in f["members"][cur]:
                self.scratch.write(f"miss#{circle}#{d}", 0)
                self.world.clear_state(cur, f"missing {d}")
            self.scratch.write(reg, nxt); self.scratch.write(dw, 0); cur = nxt
        else:
            self.scratch.incr(dw)
        # registration: what the phase EXPECTS vs what is seen
        extras = set()
        for d in f["members"][cur]:
            key = f"miss#{circle}#{d}"
            if d in active:
                self.scratch.write(key, 0)
                self.world.clear_state(cur, f"missing {d}")
            else:
                self.scratch.incr(key)
                if (self.scratch.read(key) or 0) >= 2:   # persistent, not flicker
                    extras.add(f"miss:{d}")
                    self.world.set_state(cur, f"missing {d}")
        self.phase_log[circle].append((len(self.activation_log), cur))
        return extras

    def _teach_fact(self, subject, relation, obj, container=None):
        """Index a discovered relation for the reasoning layer (fact_index +
        a tagged door). Not teach(): the tokenizer would shred structured
        node names like 'wave:a_b[2]'. CONTAINERS (owner, 2026-07-17):
        the fact wears the world it landed in (active container unless
        told) — before this stamp, every discovered fact rode the
        container-less road into base's answers (the measured leak,
        container_crystal_probe D8)."""
        if obj not in self.fact_index[(subject, relation)]:
            self.fact_index[(subject, relation)].append(obj)
        self.net.add_door(str(subject), str(obj), tag=relation)
        c = container or getattr(self, "active_container", "base")
        self.net.add_door(str(subject), str(obj), tag=f"in:{c}")

    # ── whole-mind persistence ──────────────────────────────────

    def __getstate__(self):
        """Runtime-only registries never persist: ext ops are the
        INITIATOR's job on every resurrection (capability belongs to
        code, experience to the net)."""
        d = dict(self.__dict__)
        d.pop("_ext_ops", None)
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)

    def save(self, path):
        """Snapshot the WHOLE mind — net, doors, types, facts, laws,
        compiled matrix, activation log, world state, findings — one file.
        (The ledger persists his science; this persists HIM.)"""
        import pickle
        with open(path, "wb") as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
        return path

    @staticmethod
    def load(path):
        """Resurrect a saved mind, exactly as it was."""
        import pickle
        with open(path, "rb") as f:
            mind = pickle.load(f)
        if not isinstance(mind, Isaac):
            raise ValueError("not an Isaac snapshot")
        return mind

    def fork(self):
        """A living branch: deep-copy this mind for counterfactual work —
        teach the fork something, see what follows, keep it or let it go.
        The original is untouched."""
        import copy
        return copy.deepcopy(self)

    @staticmethod
    def _store():
        """Persistence v2 (infrastructure arc 2026-07-11): the plain-file
        store — immutable indexed packs, per-node records, partial
        loading by seek. Both repos are self-contained: found next to
        this file, else via ISAAC_DC, else the sibling dc checkout."""
        import os
        import sys
        here = os.path.dirname(os.path.abspath(__file__))
        if os.path.isdir(os.path.join(here, "isaac_store")):
            root = here
        else:
            root = os.environ.get("ISAAC_DC") or os.path.join(
                os.path.dirname(here), "dc")
        if root not in sys.path:
            sys.path.insert(0, root)
        from isaac_store import bridge, codec, pack
        codec.register_module(sys.modules[Isaac.__module__], as_name="isaac")
        return bridge, pack

    def save_pack(self, directory, version=None):
        """Snapshot the whole mind as the next immutable pack in
        `directory` — versioned, supersedes (never overwrites), and
        loadable node-by-node. Returns the pack path."""
        bridge, pack = Isaac._store()
        records = bridge.extract(self)
        if version is None:
            version = pack.latest_pack(directory)[0] + 1
        import time
        return pack.write_pack(directory, version, records, meta={
            "version": version, "watermark": 0,
            "engine": "isaac.py", "records": len(records),
            "written": time.strftime("%Y-%m-%d %H:%M:%S")})

    @staticmethod
    def load_pack(directory, version=None):
        """Resurrect a mind from a pack directory (latest version unless
        one is named), exactly as it was."""
        bridge, pack = Isaac._store()
        from isaac_store.pack import PackReader, pack_path
        if version is None:
            version, path = pack.latest_pack(directory)
            if not path:
                raise FileNotFoundError(f"no packs in {directory}")
        else:
            path = pack_path(directory, version)
        r = PackReader(path)
        try:
            import sys
            return bridge.rebuild(r.load_all(), sys.modules[Isaac.__module__])
        finally:
            r.close()

    # ── the instrument floor (data-ops segment, 2026-07-15) ─────
    # "No ruler, no perfect" (owner, 2026-07-14): exactness is
    # INSTRUMENT-RELATIVE. Three roads to a floor, every measurement
    # kept, floor = the LARGEST evidenced noise scale. WRONG-KEPT
    # (07-14 probes): grain-only floors UNDER-EVIDENCE real process
    # noise — the honest PARTIAL that results downstream is correct
    # behavior; the cure is the told/repeats road, never a looser
    # gate. Nearest-neighbor noise estimators were considered and
    # REJECTED for v1: gradient contamination inflates them (a floor
    # estimated too high launders wrong forms back in).

    def _floor_grain(self, y):
        """Road 3 — GRAIN: the quantization step read off the values.
        A LOWER BOUND only: storage resolution, not process noise."""
        y = np.asarray(y, dtype=float)
        y = y[np.isfinite(y)]
        u = np.sort(np.unique(y))
        if len(u) < 3:
            return None, "too few distinct values"
        d = np.diff(u)
        d = d[d > 1e-12 * max(1.0, float(np.abs(u).max()))]
        if len(d) == 0:
            return None, "no positive gaps"
        # WRONG-KEPT x2, both caught by batteries the same day
        # (2026-07-15): (a) floor battery F4 — the reference probe's
        # tolerance scaled with the multiple (0.02 * mult), so pure
        # float-continuous data false-fired a microscopic grain
        # (visible in the probe's own W8 output, masked there by
        # max-of-roads); the tolerance is a fraction OF ONE STEP.
        # (b) audit battery A4 — reading the grain from the single
        # SMALLEST gap let one off-grid value (a typo — exactly what
        # the audit hunts) destroy the whole floor; grain is a
        # CONSENSUS of gaps, never a unanimity, so several candidate
        # grains compete and the violators are simply the
        # inconsistent minority (themselves flag candidates).
        def _grain_frac(g):
            m = np.round(d / g)
            ok = (m > 0) & (np.abs(d / g - m) < 0.02 + 1e-9 * m)
            return float(np.mean(ok)), ok
        # THE TYPO CONCEPT (owner design 2026-07-15: "word and wrod
        # should ... just have a door between them connected through
        # the typo concept"): a mis-entered value is the same thing
        # under a different bit string — a VARIANT to be FILED with a
        # door to the grid, never a new ruler. Two teeth, both from
        # measured breaks (cloud campaign W2b/W2c):
        # (a) COARSEST-consistent wins, not max-consensus — every
        #     divisor of a true grain also scores perfectly, which is
        #     how ONE half-step slip used to rescale the ruler 2x
        #     down while looking maximally consistent; preference
        #     order: coarsest among >=0.95 consensus, else coarsest
        #     among >0.80 (the typo-story band; 4 slips of 150 used
        #     to blind the road outright, and a blinded floor made
        #     the slips themselves unflaggable);
        # (b) the dissenting gaps are EJECTED from the reading and
        #     FILED as mis-entry candidates (they are what the audit
        #     hunts). Beyond 20% dissent this is not a typo story:
        #     refuse and say so.
        cands = sorted({float(c) for c in np.sort(d)[:8]}
                       | {float(np.median(d))})
        passing = []
        for c in cands:
            fr, ok = _grain_frac(c)
            if fr > 0.80 and ok.sum() >= 3:
                passing.append((c, fr, ok))
        if not passing:
            return None, "no consistent grain (float-continuous)"
        strong = [p for p in passing if p[1] >= 0.95]
        best_g, best_frac, best_ok = max(strong or passing,
                                         key=lambda p: p[0])
        m = np.round(d[best_ok] / best_g)
        g = float(np.median(d[best_ok] / m))
        frac, ok2 = _grain_frac(g)           # re-scored at the refined
        if frac >= best_frac:                # grain, never worse
            best_frac, best_ok = frac, ok2
        n_off = int((~best_ok).sum())
        if n_off > 0.2 * len(d):
            return None, (f"off-grid gaps beyond a typo story "
                          f"({n_off}/{len(d)} dissent from every "
                          f"candidate grain) — not a readable grain")
        rec = dict(road="grain", sigma=float(g / np.sqrt(12.0)),
                   step=g, consistency=best_frac,
                   note="lower bound only (storage resolution, "
                        "not process noise)")
        if n_off:
            off = d[~best_ok]
            rec["off_grid_gaps"] = n_off
            rec["worst_offset"] = float(np.max(np.abs(
                off / g - np.round(off / g))) * g)
            rec["note"] += (f"; {n_off} off-grid gap(s) FILED as "
                            f"mis-entry candidates — variants with a "
                            f"door to the grid, never a new ruler")
        return rec, None

    def _floor_repeats(self, y, X):
        """Road 1 — REPEATS: duplicate-input rows; their answer-spread
        IS the noise. Needs >=5 groups and >=10 degrees of freedom.
        CONSENSUS + EJECTION (owner call 2026-07-15, after the bench's
        floor-contamination find: corruption >= ~6% of rows inflated
        the pooled spread until the 4x-floor flag line outgrew the
        corruption itself — the errors being hunted fed the ruler that
        judges them, and the audit reported clean tables while blind).
        The cure is F14's law one road over: deviations are measured
        around each group's MEDIAN (a corrupted member drags a mean,
        not a median); a robust consensus scale is read off ALL
        deviations; values no honest instrument at that scale produces
        (>5x consensus, ~4.6 Gaussian sigmas, chance ~4e-6 per value —
        a clean world ejects NOTHING, battery F16) are ejected FROM
        THE MEASUREMENT and FILED in provenance — never from the
        record: the dissenters are exactly what the audit hunts. The
        final sigma is the ordinary pooled read over the agreeing
        majority (unbiased; arithmetically identical to the old road
        when nothing dissents). MAJORITY DISSENT (>20% of values
        ejected) DISQUALIFIES the road — that is not a typo story,
        and a refusal that says so beats a confident wrong floor.
        Known honest trades, on the record: heavy-tailed instruments
        lose their deepest tail values (~1% on t(3); battery F18
        pins <=3%) so their floor reads nearer the core scale; and a
        consensus of zero spread (heavily quantized repeats) ejects
        nothing by construction — contamination there falls to the
        grain road's own consensus."""
        if X is None:
            return None, "no X given — repeats road not run"
        y = np.asarray(y, dtype=float)
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        seen = {}
        for i in range(len(y)):
            if not np.isfinite(y[i]):
                continue
            seen.setdefault(tuple(np.round(X[i], 10)), []).append(y[i])
        groups = [np.asarray(v, dtype=float)
                  for v in seen.values() if len(v) >= 2]
        dof = sum(len(g) - 1 for g in groups)
        if len(groups) < 5 or dof < 10:
            return None, (f"under-evidenced: {len(groups)} repeat "
                          f"groups, dof {dof} (need >=5 groups, >=10 dof)")
        devs = np.concatenate([g - np.median(g) for g in groups])
        s0 = 1.4826 * float(np.median(np.abs(devs)))
        n_all = sum(len(g) for g in groups)
        kept_groups, ejected, n_ej = [], [], 0
        for g in groups:
            bad = (np.abs(g - np.median(g)) > 5.0 * s0) if s0 > 0 \
                else np.zeros(len(g), dtype=bool)
            if bad.any():
                n_ej += int(bad.sum())
                if len(ejected) < 8:        # capped, counted in full
                    ejected.append(dict(
                        size=int(len(g)), n_ejected=int(bad.sum()),
                        worst=float(np.max(np.abs(g - np.median(g))))))
            k = g[~bad]
            if len(k) >= 2:
                kept_groups.append(k)
        if n_ej > 0.2 * n_all:
            return None, (f"repeat answers disagree beyond a typo story "
                          f"({n_ej}/{n_all} values ejected by consensus)"
                          f" — not an instrument floor; the data itself "
                          f"needs investigating")
        kept_dof = sum(len(g) - 1 for g in kept_groups)
        if len(kept_groups) < 5 or kept_dof < 10:
            return None, (f"under-evidenced after consensus ejection: "
                          f"{len(kept_groups)} groups, dof {kept_dof} "
                          f"(need >=5 groups, >=10 dof)")
        pooled = np.concatenate([g - np.mean(g) for g in kept_groups])
        return dict(road="repeats",
                    sigma=float(np.sqrt(np.sum(pooled ** 2) / kept_dof)),
                    groups=len(kept_groups), dof=int(kept_dof),
                    ejected=int(n_ej),
                    ejected_groups=ejected), None

    def tell_resolution(self, name, sigma, who="told"):
        """Road 2 — TOLD: the instrument's resolution, stated. Usable
        at once (the told-knowledge law); belief stays measured — a
        measured road that contradicts it flags the record (kept,
        never erased)."""
        node = f"floor:{name}"
        rec = dict(sigma=float(sigma), who=str(who), contradicted=False)
        self.net.set_meta(node, "told", rec)
        self.record_finding("floor_told", name, sigma=float(sigma),
                            who=str(who))
        return rec

    def read_floor(self, y, X=None, name=None):
        """The instrument floor: how precise is the tool that produced
        these values? Runs every road, KEEPS every road's measurement,
        answers with the LARGEST evidenced noise scale. No road
        evidenced -> the floor is REFUSED: exactness is unclaimable,
        the report should say best-residual-in-units and ASK for the
        resolution (the logical-gaps posture). With a name, the
        reading lives at floor:<name> — active + superseded chain —
        and lands in the findings ledger: a tool in the chain,
        supersedable like everything else."""
        roads, notes = [], []
        rep, rep_why = self._floor_repeats(y, X)
        if rep:
            roads.append(rep)
        elif X is not None:
            notes.append(f"repeats: {rep_why}")
        told = self.net.get_meta(f"floor:{name}", "told") if name else None
        if told:
            told_road = dict(road="told", sigma=float(told["sigma"]),
                             who=told.get("who", "told"),
                             contradicted=bool(told.get("contradicted")))
            if rep and rep["sigma"] > 1.5 * told["sigma"]:
                told_road["contradicted"] = True
                told["contradicted"] = True          # flag the record,
                self.net.set_meta(f"floor:{name}", "told", told)  # keep it
                notes.append(
                    f"told {told['sigma']:g} CONTRADICTED by measured "
                    f"{rep['sigma']:g} (flagged, kept; the larger wins)")
            roads.append(told_road)
        grain, grain_why = self._floor_grain(y)
        if grain:
            roads.append(grain)
        else:
            notes.append(f"grain: {grain_why}")
        if roads:
            best = max(roads, key=lambda r: r["sigma"])
            why = (f"floor {best['sigma']:g} via {best['road']} "
                   f"(largest of {len(roads)} evidenced road(s))")
            if notes:
                why += "; " + "; ".join(notes)
            result = dict(floor=best["sigma"], road=best["road"],
                          roads=roads, exact_claimable=True, why=why)
        else:
            why = ("no ruler — " + "; ".join(notes) +
                   "; exactness unclaimable: BEST-RESIDUAL posture; "
                   "ASK for the instrument's resolution")
            result = dict(floor=None, road=None, roads=[],
                          exact_claimable=False, why=why)
        if name:
            node = f"floor:{name}"
            old = self.net.get_meta(node, "active")
            if old is not None:
                chain = self.net.get_meta(node, "superseded") or []
                chain.append(dict(record=old, why="re-measured; a newer "
                                  "reading supersedes (kept, never erased)"))
                self.net.set_meta(node, "superseded", chain)
            self.net.set_meta(node, "active", result)
            self.record_finding("floor", name, floor=result["floor"],
                                road=result["road"], roads=result["roads"],
                                why=result["why"])
        return result

    # ── the failure-commonality miner (data-ops §4, 2026-07-15) ──
    # Owner ask (2026-07-14): "assess failures and find
    # commonalities... specifically denied." The commonality of the
    # denied is a DIFFERENTIAL against the allowed — compare()'s
    # only-in-failures, gated by a selection-corrected label-shuffle
    # null. NEVER a frequency: a feature on 100% of failures that is
    # also on 100% of successes says nothing (control B, probe
    # 2026-07-14). Double-duty by design: names the shared factor
    # behind audit flags (news-vs-error) AND mints the CASE CLASS for
    # piecewise supersession (organ failure receipts -> named failure
    # class -> duel scope). v1 mines single feature=value signatures;
    # conjunctions ride the existing confusion-pair/compound move
    # when a case demands them — said here so the limit is on record.

    def mine_commonality(self, records, failed, name=None,
                         n_perm=300, seed=0):
        """From kept receipts (records: list of feature->value dicts;
        failed: parallel bools), name what the failures share that the
        successes lack. Returns named signatures past the null, the
        threshold, and honest refusals; with a name, the reading lives
        at commonality:<name> (active + superseded chain) and lands in
        the findings ledger — a supersedable tool in the chain."""
        n_fail = sum(1 for f in failed if f)
        n_succ = len(failed) - n_fail
        base = dict(named=[], threshold=None, top=None,
                    n_fail=int(n_fail), n_succ=int(n_succ))
        if not records or n_fail == 0 or n_succ == 0:
            base["why"] = ("nothing to mine: need both failures and "
                           f"successes (have {n_fail} fail / "
                           f"{n_succ} pass)")
            return base
        cands = sorted({(k, str(v)) for r in records
                        for k, v in r.items()})
        flags = np.asarray(list(failed), dtype=bool)
        hits = {c: np.fromiter((str(r.get(c[0])) == c[1]
                                for r in records),
                               dtype=bool, count=len(records))
                for c in cands}

        def excess(fl):
            nf = int(fl.sum()); ns = len(fl) - nf
            return {c: float(h[fl].sum()) / nf - float(h[~fl].sum()) / ns
                    for c, h in hits.items()}
        obs = excess(flags)
        rng = np.random.default_rng(seed)
        null = np.zeros(n_perm)
        for p in range(n_perm):
            null[p] = max(excess(rng.permutation(flags)).values())
        thr = float(np.sort(null)[::-1][1])   # ~99th pct, selection-
        named = [(k, v, float(e)) for (k, v), e in    # corrected max
                 sorted(obs.items(), key=lambda kv: -kv[1]) if e > thr]
        result = dict(named=named, threshold=thr,
                      top=float(max(obs.values())),
                      n_fail=int(n_fail), n_succ=int(n_succ),
                      why=("differential signature(s) past the "
                           "label-shuffle null" if named else
                           "nothing named: no feature=value is in the "
                           "failures beyond what shuffled labels give"))
        if name:
            node = f"commonality:{name}"
            old = self.net.get_meta(node, "active")
            if old is not None:
                chain = self.net.get_meta(node, "superseded") or []
                chain.append(dict(record=old, why="re-mined; a newer "
                                  "reading supersedes (kept, never "
                                  "erased)"))
                self.net.set_meta(node, "superseded", chain)
            self.net.set_meta(node, "active", result)
            self.record_finding("commonality", name,
                                named=result["named"],
                                threshold=result["threshold"],
                                n_fail=result["n_fail"],
                                n_succ=result["n_succ"],
                                why=result["why"])
        return result

    # ── cross-check: ECC for data (owner design, 2026-07-15) ─────
    # "you have the inputs and the outputs. 5+5=9. you dont know if
    # 9 was wrong, or if one of the 5s was supposed to be a 4, but
    # you know something here is incorrect. and even if he cant
    # resolve it, he can mark it as false and return to it maybe. if
    # you have a data table with 40,000 inputs and they dont add up
    # at the end, then someone somewhere did something wrong."

    def cross_check(self, values, checks, floor=0.0, name=None):
        """ECC-style error checking over values that must add up.
        values: {cell: number}; checks: dicts with name, cells=[...],
        total=<cell name or plain number>, optional const — meaning
        sum(cells) + const == total. A failing check proves AT LEAST
        ONE member is false WITHOUT saying which: the finding marks
        the TUPLE, never the output alone. Candidate repairs are the
        typo concept's doors — for each cell, the one value that
        would balance the check — and they are PROPOSALS with
        receipts, never silently applied. Localization is the parity
        move (Hamming's): within a connected component of failing
        checks (checks sharing cells), a single-cell repair that
        balances EVERY failing check it touches while breaking NO
        passing one is a survivor; exactly one survivor =
        CORRECTED-CANDIDATE; several or none = FALSE-SOMEWHERE, kept
        OPEN with its candidates so it can be returned to — with a
        name, open marks persist at inconsistency:<name> (active +
        superseded chain), and a later re-run with more checks
        supersedes them (E7: 5+5=9 alone is unresolvable; add a+2=6
        and a=4 is the unique repair of both). Known limits, said:
        v1 checks are sum-shaped; correction capacity is single-error
        per component (multi-error is DETECTED and refused, E4 — and
        a balanced error pair can make the totals look guilty, which
        is why candidates are never auto-applied); tolerance per
        check = max(4*floor*sqrt(n_terms), 1e-9*scale) — the 4x
        rhymes with the audit's flag line, hand-set and said. The
        40,000-input case: one grand total that fails with no
        crossing checks certifies an error EXISTS (someone somewhere
        did something wrong) with candidates counted, not enumerated
        — add a crossing check to localize."""
        vals = dict(values)

        def _cells(ch):
            cs = set(ch["cells"])
            if isinstance(ch["total"], str):
                cs.add(ch["total"])
            return cs

        def _tol(ch):
            scale = max([abs(vals.get(c, 0.0)) for c in _cells(ch)]
                        + [1.0])
            return max(4.0 * floor * np.sqrt(len(ch["cells"]) + 1),
                       1e-9 * scale)

        def _resid(ch, v):
            s = sum(v[c] for c in ch["cells"]) + ch.get("const", 0.0)
            t = ch["total"]
            return s - (v[t] if isinstance(t, str) else float(t))

        failing, passing, unevaluable = [], [], []
        for ch in checks:
            missing = [c for c in _cells(ch) if c not in vals]
            if missing:
                unevaluable.append(dict(check=ch["name"],
                                        missing=missing))
                continue
            (failing if abs(_resid(ch, vals)) > _tol(ch)
             else passing).append(ch)

        comps = []
        for ch in failing:
            cs, merged, rest = _cells(ch), [ch], []
            for comp in comps:
                if cs & comp["cells"]:
                    merged += comp["checks"]
                    cs |= comp["cells"]
                else:
                    rest.append(comp)
            comps = rest + [dict(checks=merged, cells=cs)]

        MAX_ENUM = 96
        results = []
        for comp in comps:
            cand = {}
            for ch in comp["checks"]:
                r = _resid(ch, vals)
                for c in _cells(ch):
                    if isinstance(ch["total"], str) and c == ch["total"]:
                        fix = vals[c] + r
                    else:
                        fix = vals[c] - r
                    cand.setdefault(c, set()).add(round(float(fix), 12))
            n_cand = sum(len(v) for v in cand.values())
            survivors = []
            if n_cand <= MAX_ENUM:
                for c, fixes in sorted(cand.items()):
                    for fx in sorted(fixes):
                        v2 = dict(vals)
                        v2[c] = fx
                        if all(abs(_resid(ch, v2)) <= _tol(ch)
                               for ch in comp["checks"]) and \
                           all(abs(_resid(ch, v2)) <= _tol(ch)
                               for ch in passing if c in _cells(ch)):
                            survivors.append(dict(
                                cell=c, observed=float(vals[c]),
                                repaired=float(fx),
                                why="mis-entry candidate — the one "
                                    "value whose repair balances every"
                                    " failing check it touches (a "
                                    "door to the intended value, the "
                                    "typo concept)"))
            if len(survivors) == 1:
                verdict, why = "CORRECTED-CANDIDATE", (
                    "the failing checks intersect at one cell (the "
                    "parity move): a unique repair balances the books"
                    " — proposed with its receipt, never applied")
            elif n_cand > MAX_ENUM:
                verdict, why = "FALSE-SOMEWHERE", (
                    f"the books do not balance across "
                    f"{len(comp['cells'])} values: someone somewhere "
                    f"did something wrong — an error EXISTS, but "
                    f"{n_cand} candidate repairs cannot be told apart"
                    f" by these checks; add a crossing check to "
                    f"localize")
            else:
                verdict, why = "FALSE-SOMEWHERE", (
                    "at least one of these values is false; no single"
                    " repair explains every failing check (either the"
                    " culprit is unidentifiable with these checks or "
                    "there is more than one error) — marked, kept, "
                    "returnable")
            res = dict(verdict=verdict,
                       checks=[c["name"] for c in comp["checks"]],
                       n_cells=len(comp["cells"]),
                       cells=sorted(comp["cells"])[:24],
                       candidates=survivors[:24], why=why)
            if n_cand > MAX_ENUM:
                res["candidates_not_enumerated"] = n_cand
            results.append(res)

        out = dict(consistent=not results and not unevaluable,
                   n_checks=len(checks), failed=len(failing),
                   passed=len(passing), components=results,
                   unevaluable=unevaluable,
                   why=("all checks balance" if not results else
                        f"{len(results)} inconsistent component(s) — "
                        f"every one marked with its candidates"))
        if name:
            node = f"inconsistency:{name}"
            old = self.net.get_meta(node, "active")
            if old is not None:
                chain = self.net.get_meta(node, "superseded") or []
                chain.append(dict(record=old,
                                  why="re-checked; a newer cross-check"
                                      " supersedes (kept, never "
                                      "erased)"))
                self.net.set_meta(node, "superseded", chain)
            self.net.set_meta(node, "active", results)
            self.record_finding("cross_check", name,
                                failed=len(failing),
                                components=len(results),
                                why=out["why"])
        return out

    # ── vet intake: interpreted, not implemented (owner design,
    # 2026-07-15) — "if its something where we have a known answer,
    # vs the received answer, then he can check... if he determines
    # its wrong, he can still acknowledge the assumed intent and
    # continue but doesnt learn the assumed flaw for integration.
    # bad english is interpreted, but not implemented."

    def vet_intake(self, claims, expectations=None, floor=0.0,
                   name=None):
        """The front door's immune system: check incoming claims
        against what he already expects BEFORE anything is learned.
        Understanding and adoption are SPLIT: a claim that fails his
        own check is INTERPRETED — the assumed intent recorded as
        doors to the likely-meant value (the typo concept) so the
        conversation continues — but integrate=False: the flawed
        form never reaches learning. It is still WRONG-KEPT, not
        deleted: the original verbatim + why + intent persist at
        quarantine:<name> (active + superseded chain). No
        expectation = UNCHECKABLE = the ORDINARY nulls road — never
        a free pass, never a quarantine (checking requires a ruler;
        most of the world arrives unruled). claims: dicts with name
        and kind — kind="sum" (values/cells/total, vetted through
        cross_check) or kind="value" (key/received, vetted against
        expectations[key] when present). v1 scope, said plainly:
        expectations arrive from the caller's road; wiring his OWN
        net (learned grammar, taught rules, known laws) as the
        expectation source is the named next rung — the account
        poisoning entered exactly through this door, and this organ
        is the word-elections cure's PREVENTIVE twin. Tolerance
        rhymes with the audit line: max(4*floor, 1e-9*scale)."""
        expectations = expectations or {}
        results = []
        for cl in claims:
            res = dict(claim=cl.get("name", "?"),
                       original=dict(cl), intent=[])
            if cl.get("kind") == "sum":
                cc = self.cross_check(
                    cl["values"],
                    [dict(name=cl.get("name", "claim"),
                          cells=cl["cells"], total=cl["total"],
                          const=cl.get("const", 0.0))],
                    floor=floor)
                if cc["consistent"]:
                    res.update(verdict="PASSES", integrate=True,
                               why="adds up under his own check")
                else:
                    comp = cc["components"][0]
                    res.update(
                        verdict="FAILS-CHECK", integrate=False,
                        intent=[dict(cell=d["cell"],
                                     observed=d["observed"],
                                     repaired=d["repaired"],
                                     why="assumed intent — the value "
                                         "that would balance the "
                                         "claim (a door, the typo "
                                         "concept)")
                                for d in comp["candidates"]],
                        why="does not add up: acknowledged, intent "
                            "assumed, NOT learned — interpreted, not "
                            "implemented")
            elif cl.get("kind") == "value" and cl.get("key") in \
                    expectations:
                exp = float(expectations[cl["key"]])
                got = float(cl["received"])
                tol = max(4.0 * floor, 1e-9 * max(abs(exp), 1.0))
                if abs(got - exp) <= tol:
                    res.update(verdict="PASSES", integrate=True,
                               why="matches the known answer")
                else:
                    res.update(
                        verdict="FAILS-CHECK", integrate=False,
                        intent=[dict(cell=cl["key"], observed=got,
                                     repaired=exp,
                                     why="assumed intent — his known "
                                         "answer stands in for what "
                                         "was probably meant")],
                        why=f"received {got:g} vs known {exp:g}: "
                            f"wrong by his own check; interpreted, "
                            f"not implemented")
            else:
                res.update(verdict="UNCHECKABLE",
                           integrate="unchecked",
                           why="no expectation to check against — "
                               "the ordinary nulls road (not a pass, "
                               "not a quarantine)")
            results.append(res)
        quarantined = [r for r in results if r["integrate"] is False]
        out = dict(results=results,
                   passed=[r["claim"] for r in results
                           if r["integrate"] is True],
                   quarantined=[r["claim"] for r in quarantined],
                   unchecked=[r["claim"] for r in results
                              if r["integrate"] == "unchecked"],
                   why=(f"{len(quarantined)} claim(s) interpreted, "
                        f"not implemented" if quarantined else
                        "nothing quarantined"))
        if name:
            node = f"quarantine:{name}"
            old = self.net.get_meta(node, "active")
            if old is not None:
                chain = self.net.get_meta(node, "superseded") or []
                chain.append(dict(record=old,
                                  why="re-vetted; a newer intake "
                                      "supersedes (kept, never "
                                      "erased)"))
                self.net.set_meta(node, "superseded", chain)
            self.net.set_meta(node, "active", quarantined)
            self.record_finding("vet_intake", name,
                                passed=len(out["passed"]),
                                quarantined=len(quarantined),
                                unchecked=len(out["unchecked"]),
                                why=out["why"])
        return out

    # ── the tools node (owner design, 2026-07-15) ────────────────
    # "a tools node that he can query. it has the preset files of
    # every thing he has designed or we have built as a function for
    # him to directly access. he can either test them, just go
    # through trial and error and run them all, or he can know what
    # they do and choose the one he is looking for... if nothing in
    # tools is applicable, then he just skips to next."
    # The PRESENCE pillar of the flow-structures design: a capability
    # with no node is invisible to any scan — so every tool is a
    # tool:<name> node doored under 'tools', carrying what it does,
    # how to call it, tags, and use/outcome receipts (the election
    # shape — the same recent-window law as words can climb here).
    # An empty query is an HONEST SKIP, never a stall.

    def register_tool(self, name, does, how="", tags=(), method=None):
        """A capability enters the net: readable description, call
        shape, when-tags, and an empty receipt record. Re-registering
        with a new description supersedes (old kept)."""
        node = f"tool:{name}"
        old = self.net.get_meta(node, "record")
        if old is not None and old.get("does") == str(does):
            return node                      # idempotent re-catalog
        self.net.add_door("tools", node, tag="tool")
        rec = dict(does=str(does), how=str(how),
                   tags=sorted(str(t) for t in tags),
                   method=method, used=0, passed=0, recent=[])
        if old is not None:
            chain = self.net.get_meta(node, "superseded") or []
            chain.append(dict(record=old, why="re-registered with a "
                              "new description (kept, never erased)"))
            self.net.set_meta(node, "superseded", chain)
            rec["used"], rec["passed"] = old["used"], old["passed"]
            rec["recent"] = old.get("recent", [])
        self.net.set_meta(node, "record", rec)
        return node

    def register_ext_op(self, name, fn, does=""):
        """THE INITIATOR'S DOOR (owner law, 2026-07-17: code owns
        exactly two jobs — the base loop and the initiator). An
        EXTERNAL ACT (a conversation partner, file I/O — the world)
        registers as a runtime op the walker can run, so a lived
        pipeline's flow can be NET CONTENT end to end. The registry
        is RUNTIME-ONLY, never pickled: a resurrected mind honestly
        REFUSES ext-op walks until its initiator re-registers (same
        law as tools re-cataloging — capability belongs to code,
        experience to the net). Each ext op also carries a tool node
        (tag ext-op) so the tools catalog can say it exists."""
        if not hasattr(self, "_ext_ops"):
            self._ext_ops = {}
        self._ext_ops[str(name)] = fn
        node = f"tool:{name}"
        self.net.add_door("tools", node, tag="ext-op")
        if not self.net.get_meta(node, "record"):
            self.net.set_meta(node, "record", dict(
                does=str(does) or "external act (initiator-"
                "registered; runtime-only)", how="via flows",
                tags=["ext-op"], method=None, used=0, passed=0,
                recent=[]))
        return node

    def catalog_tools(self):
        """The preset files of everything built: every public engine
        method with a docstring registers itself (first sentence =
        what it does). Idempotent — run any time; new organs join."""
        n = 0
        for attr in sorted(dir(self)):
            if attr.startswith("_"):
                continue
            fn = getattr(self, attr, None)
            doc = (getattr(fn, "__doc__", None) or "").strip()
            if not callable(fn) or not doc:
                continue
            does = " ".join(doc.split())
            does = does.split(". ")[0].rstrip(".") + "."
            self.register_tool(attr, does, how=f"mind.{attr}(...)",
                               tags=("engine",), method=attr)
            n += 1
        return n

    def query_tools(self, want, top=5):
        """Informed choice: rank every tool by word overlap between
        the want and what the tool says it does. Nothing applicable
        -> matches=[] with the skip-to-next why (a bypass answer,
        never a stall)."""
        import re
        toks = set(re.findall(r"[a-z]+", str(want).lower()))
        scored = []
        for tgt in self.net.get_doors("tools", tag="tool"):
            rec = self.net.get_meta(tgt, "record") or {}
            name = tgt.split("tool:", 1)[1]
            text = " ".join([name.replace("_", " "),
                             rec.get("does", ""),
                             " ".join(rec.get("tags", []))]).lower()
            ov = len(toks & set(re.findall(r"[a-z]+", text)))
            if ov:
                scored.append((ov, name, rec.get("does", "")))
        scored.sort(key=lambda s: (-s[0], s[1]))
        if not scored:
            return dict(matches=[], why="nothing in tools is "
                        "applicable — skip to next")
        return dict(matches=[dict(name=nm, does=d, score=int(sc))
                             for sc, nm, d in scored[:top]],
                    why=f"{len(scored)} applicable tool(s)")

    def run_tool(self, name, *args, **kwargs):
        """Trial and error: run a registered tool through its node.
        The use is counted (outcomes land via tool_receipt once
        judged). Unknown or unrunnable tools refuse with a why."""
        node = f"tool:{name}"
        rec = self.net.get_meta(node, "record")
        if rec is None:
            return dict(refused=True,
                        why=f"no tool named '{name}' in the tools "
                            f"node — query_tools() to see what exists")
        method = rec.get("method")
        if not method or not callable(getattr(self, method, None)):
            return dict(refused=True,
                        why=f"'{name}' has no runnable binding on "
                            f"this mind (how: {rec.get('how', '?')})")
        rec["used"] += 1
        self.net.set_meta(node, "record", rec)
        return getattr(self, method)(*args, **kwargs)

    def tool_receipt(self, name, passed):
        """The judged outcome lands on the tool that was used — the
        same receipt shape as word elections; the recent window is
        ready for the same re-election law."""
        node = f"tool:{name}"
        rec = self.net.get_meta(node, "record")
        if rec is None:
            return False
        rec["passed"] += 1 if passed else 0
        rec["recent"] = (rec.get("recent", [])
                         + [1 if passed else 0])[-8:]
        self.net.set_meta(node, "record", rec)
        return True

    # ── structure and order (owner ask, 2026-07-15) ─────────────
    # "he needs to be able to assess structure and order. ab vs ba.
    # if the difference is just position he should be able to
    # identify that." compare() is set-based and order-blind — 'ab'
    # vs 'ba' look identical to it. This organ is comparison-as-
    # registration (theory §13) applied to sequences: align, then
    # read the TRANSFORM (the permutation = pose) and the RESIDUAL
    # (content = identity) — checklist #9 made literal for order.
    # A positional claim is only made when the mapping VERIFIABLY
    # turns a into b (checked before it is said, never asserted).

    def compare_order(self, a, b):
        """Assess structure and order: are these the same parts in a
        different arrangement? Content is compared multiset-honestly
        (an extra copy is CONTENT, not order); when the parts match
        exactly, the arrangement verdict names the transform — swap /
        reversed / rotated / reordered — with the verified mapping
        and the moved positions. When content differs, the shared
        part's order is still assessed, so both differences are said,
        factored apart."""
        from collections import Counter
        a, b = list(a), list(b)
        ca, cb = Counter(a), Counter(b)
        shared = ca & cb
        out = dict(content=dict(
            shared=sorted(shared.elements()),
            only_a=sorted((ca - cb).elements()),
            only_b=sorted((cb - ca).elements())))

        def kept(seq):
            rem, o = dict(shared), []
            for x in seq:
                if rem.get(x, 0) > 0:
                    o.append(x)
                    rem[x] -= 1
            return o

        if out["content"]["only_a"] or out["content"]["only_b"]:
            fa, fb = kept(a), kept(b)
            out["shared_order"] = "kept" if fa == fb else "reordered"
            out["verdict"] = ("content differs" if fa == fb
                              else "content and order differ")
            return out
        if a == b:
            out["verdict"] = "same"
            return out
        # the parts are identical — find and VERIFY the permutation
        # (fixed points claimed first, so moved_positions is minimal)
        n = len(a)
        mapping, used = [-1] * n, [False] * n
        for i in range(n):
            if not used[i] and a[i] == b[i]:
                mapping[i], used[i] = i, True
        for i in range(n):
            if mapping[i] < 0:
                j = next(j for j in range(n)
                         if not used[j] and b[j] == a[i])
                mapping[i], used[j] = j, True
        placed = [None] * n
        for i, j in enumerate(mapping):
            placed[j] = a[i]
        if placed != b:                      # cannot happen with equal
            out["verdict"] = "reordered"     # multisets, but a claim
            out["arrangement"] = dict(       # is never left unchecked
                kind="unverified", mapping=mapping)
            return out
        moved = [i for i in range(n) if a[i] != b[i]]
        if (len(moved) == 2 and a[moved[0]] == b[moved[1]]
                and a[moved[1]] == b[moved[0]]):
            kind = "swap"
        elif n > 1 and b == a[::-1]:
            kind = "reversed"
        else:
            kind = next((f"rotated by {k}" for k in range(1, n)
                         if b == a[k:] + a[:k]), "reordered")
        out["verdict"] = "reordered"
        out["arrangement"] = dict(kind=kind, moved_positions=moved,
                                  mapping=mapping,
                                  why="the parts are identical; only "
                                      "position differs")
        return out

    # ── when order matters (owner theory, 2026-07-15) ────────────
    # "with plus it doesnt matter, but with minus or divide it does...
    # additive does not matter, but subtractive methods are."
    # MEASURED, never told (checklist #3): swap the operands and see.
    # A violation keeps its WITNESS pair as the receipt; order-
    # freeness is only ever "no counterexample in N probes" — honest
    # absence, not proof. The learnable law underneath (kept on the
    # sheet): order matters exactly where the slots carry DIFFERENT
    # ROLES — minuend/subtrahend are roles the way agent/patient are.
    # Composes with compare_order: that organ says WHEN two things
    # differ only in position; this one says WHETHER that difference
    # changes the outcome under the operation at hand.

    _ORDER_OPS = {
        "+": lambda a, b: a + b, "-": lambda a, b: a - b,
        "*": lambda a, b: a * b, "/": lambda a, b: a / b,
        "^": lambda a, b: a ** b,
        "max": lambda a, b: max(a, b), "min": lambda a, b: min(a, b),
    }

    def order_matters(self, op, n_probe=50, seed=0):
        """Does swapping the operands change this operation's answer?
        Measured by probing, never told: order-sensitive verdicts
        carry a verified WITNESS pair; order-free verdicts say only
        'no counterexample in N probes'. The badge lands on the
        op:<symbol> node and in the findings ledger."""
        fn = Isaac._ORDER_OPS.get(op)
        if fn is None:
            return dict(refused=True,
                        why=f"unknown operation '{op}' — known: "
                            f"{sorted(Isaac._ORDER_OPS)}")
        rng = np.random.default_rng(seed)
        witness = None
        for _ in range(int(n_probe)):
            a = float(rng.uniform(0.5, 6.0))
            b = float(rng.uniform(0.5, 6.0))
            try:
                ab, ba = fn(a, b), fn(b, a)
            except ZeroDivisionError:
                continue
            if abs(ab - ba) > 1e-9 * max(1.0, abs(ab), abs(ba)):
                witness = dict(a=a, b=b, ab=float(ab), ba=float(ba))
                break
        if witness:
            result = dict(matters=True, probes=int(n_probe),
                          witness=witness,
                          why=f"'{op}' changes with order: "
                              f"{witness['a']:g} {op} {witness['b']:g} "
                              f"= {witness['ab']:g} but swapped = "
                              f"{witness['ba']:g} (the witness is the "
                              f"receipt)")
        else:
            result = dict(matters=False, probes=int(n_probe),
                          why=f"no counterexample in {int(n_probe)} "
                              f"probes — order-free as far as measured"
                              f" (absence, not proof)")
        self.net.set_meta(f"op:{op}", "order", result)
        self.record_finding("order", op, matters=result["matters"],
                            probes=result["probes"], why=result["why"])
        return result

    # ── the findings ledger ─────────────────────────────────────

    @staticmethod
    def _jsonable(v):
        if isinstance(v, np.ndarray):
            return v.tolist()
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            return float(v)
        if isinstance(v, dict):
            return {str(k): Isaac._jsonable(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [Isaac._jsonable(x) for x in v]
        return v

    def record_finding(self, kind, name, **payload):
        """Every outcome — a law, a family, a NO RULE, an overturn — becomes
        a structured, searchable record. Negative knowledge is knowledge:
        a recorded 'proven nothing' saves the next session from re-proving it."""
        entry = dict(id=len(self.findings) + 1, kind=kind, name=str(name))
        entry.update({k: self._jsonable(v) for k, v in payload.items()})
        self.findings.append(entry)
        node = f"finding:{entry['id']}"
        self.net.add_door("findings", node, tag="finding")
        self.net.set_meta(node, "entry", entry)
        if self.ledger_path:
            import json
            with open(self.ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        return entry["id"]

    def recall_findings(self, kind=None, contains=None, limit=50):
        """Search his own scientific memory."""
        import json
        out = []
        for e in reversed(self.findings):
            if kind and e.get("kind") != kind:
                continue
            if contains and contains.lower() not in \
                    json.dumps(e, default=str).lower():
                continue
            out.append(e)
            if len(out) >= limit:
                break
        return out

    def load_ledger(self, path):
        """Rehydrate a previous session's findings: laws become APPLICABLE
        again (apply_law works on them), records become searchable."""
        import json
        n_laws = 0
        for line in open(path, encoding="utf-8"):
            e = json.loads(line)
            e["id"] = len(self.findings) + 1
            self.findings.append(e)
            if e.get("kind") == "composite":
                if not any(c["name"] == e["name"] for c in self.composites):
                    self.composites.append(dict(
                        op=e["op"], features=[int(f) for f in e["features"]],
                        name=e["name"], provenance=e.get("provenance", "")))
            if e.get("kind") == "rule" and isinstance(e.get("clauses"),
                                                      list):
                node = f"rule:{e['name']}"
                self.net.add_door("rule", node, tag="rule")
                self.net.set_meta(node, "rule", dict(
                    clauses=e["clauses"],
                    status=e.get("status", "told-unverified"),
                    validation=e.get("validation")))
            if e.get("kind") == "law" and e.get("model"):
                m = e["model"]
                node = f"law:{e['name']}"
                self.net.add_door("law", node, tag="law")
                self.net.set_meta(node, "model", dict(
                    terms=[tuple(t) for t in m["terms"]],
                    coefs=np.array(m["coefs"]),
                    intercept=float(m["intercept"]), d=int(m["d"]),
                    r2=float(m.get("r2", 0)),
                    specs=[tuple(s) for s in m["specs"]],
                    rivals=m.get("rivals", []),
                    d_raw=int(m.get("d_raw", m["d"])),
                    composites_used=m.get("composites_used", []),
                    lags_used=[[int(i), int(k)] for i, k in
                               m.get("lags_used", [])]))
                self.net.set_meta(node, "equation", e.get("equation", ""))
                self._teach_fact(node, "explains", e["name"])
                n_laws += 1
        return dict(records=len(self.findings), laws_restored=n_laws)

    # ── lag atoms (2026-07-12): the temporal vocabulary ──────────
    # The causality probe measured the old cause-and-effect failure
    # exactly: on y(t) = f(x(t-k)) raw discover scores r2 = 0.000 at
    # EVERY lag k >= 1 — rows are read as exchangeable, so time is
    # invisible — while the same worlds with lagged columns offered
    # as vocabulary heal completely (r2 = 1.000, the true lag NAMED).
    # So discover PROPOSES lag columns from the data itself, the same
    # expand/compress move as phase-fold periods. The proposer
    # measures EVERY integer lag at once: FFT cross-correlation of y
    # against vocabulary transforms of each column (x, x^2, |x| — the
    # linear projection of any dependence shape), max over transforms
    # per lag, admitted only past a selection-corrected
    # CIRCULAR-SHIFT null (the max over ALL lags AND transforms,
    # replayed on shifted y — alignment destroyed, autocorrelation
    # texture preserved exactly). On exchangeable rows nothing
    # survives and the vocabulary is unchanged. Proposals WIDEN the
    # grid (expansion); every lag column still faces the admission
    # null term by term (compression unchanged).
    # WRONG-KEPT: v1 bracketed a coarse geometric lag ladder and
    # refined +-1 (the no-preset-frequencies move). It LOST: on an
    # iid driver an off-by-one lag carries ZERO signal — there is no
    # gradient between anchors (measured: k=40 planted, anchors 29
    # and 41, refusal). Exact full-lag measurement is cheaper AND
    # complete; bracket-and-refine stands for SMOOTH parameter
    # families, not integer alignment against iid drivers.

    @staticmethod
    def _lag_columns(Xraw, lags):
        """Columns x_i shifted k rows down. The first k rows have no
        history: NaN — a per-row refusal, dropped at discovery and
        reported (never guessed) at apply time."""
        n = len(Xraw)
        cols = []
        for i, k in lags:
            v = np.full(n, np.nan)
            if k < n:            # a series shorter than the lag has no
                v[k:] = Xraw[:n - k, i]   # history at all: all-NaN,
            cols.append(v)                # every row refuses honestly
        return np.column_stack(cols) if cols else np.empty((n, 0))

    def _propose_lags(self, X, y, n_perm=200, max_per_col=3):
        """Null-gated lag proposal. Returns [(col, lag), ...] — empty
        when rows carry no temporal dependence past the null. The
        full scan (every column: best lag, its score, its gate) is
        kept on self._last_lag_scan — refused columns wear their
        numbers too."""
        n = len(y)
        self._last_lag_scan = []
        if n < 60:
            return []
        ys = y - np.mean(y)
        ys = ys / (np.std(ys) + 1e-12)
        max_lag = n // 4
        m_fft = 1 << int(np.ceil(np.log2(2 * n)))
        norm = np.maximum(n - np.arange(1, max_lag + 1), 1)
        # THE NULL IS A CIRCULAR SHIFT, not block permutation: two
        # unrelated slow series show spurious lag alignment whose size
        # is set by their FULL autocorrelation; block permutation
        # breaks that structure at block seams, so its gate sits too
        # low (measured: 3/10 false proposals on unrelated AR(1)
        # pairs — wrong-kept). Shifting y keeps its texture EXACTLY
        # and destroys only alignment; the shift range keeps a true
        # peak outside the scanned window.
        shifts = _wave_rng.integers(max_lag + 1, n - max_lag, n_perm)
        out = []
        for i in range(X.shape[1]):
            xi = np.asarray(X[:, i], float)
            if xi.std() < 1e-12:
                continue
            # transforms carry the dependence SHAPE into a linear
            # statistic: x catches odd parts, x^2 and |x| even parts
            G = []
            for g in (xi, xi ** 2, np.abs(xi)):
                s = g.std()
                if s > 1e-12:
                    G.append(np.conj(np.fft.rfft((g - g.mean()) / s,
                                                 m_fft)))
            if not G:
                continue

            def curve(vals):
                vf = np.fft.rfft(vals, m_fft)
                best = np.zeros(max_lag)
                for gf in G:
                    c = np.fft.irfft(vf * gf, m_fft)
                    # c[k] = sum_t g[t] * vals[t+k]: alignment at lag k
                    np.maximum(best, np.abs(c[1:max_lag + 1]) / norm,
                               out=best)
                return best

            real_curve = curve(ys)
            null = np.empty(n_perm)
            for p in range(n_perm):
                null[p] = curve(np.roll(ys, int(shifts[p]))).max()
            # gate = the null's observed MAX (level ~1/(n_perm+1)):
            # a percentile interpolated from the top of a small sample
            # is noisy exactly where it matters (measured: a 100-draw
            # p99 estimate sat at 0.26 when the true p99 was 0.37 —
            # a false fire). The max needs no interpolation.
            gate = float(null.max())
            k_best = int(np.argmax(real_curve)) + 1
            self._last_lag_scan.append(
                [int(i), k_best, round(float(real_curve.max()), 4),
                 round(gate, 4)])
            order = np.argsort(-real_curve)
            picks = []
            for j in order:
                if real_curve[j] <= gate or len(picks) >= max_per_col:
                    break
                kk = int(j) + 1
                if all(abs(kk - pk) > 1 for pk in picks):
                    picks.append(kk)
            out += [(i, kk) for kk in sorted(picks)]
        return out

    @staticmethod
    def _rename_lags(eq, base, lags):
        """Equation legibility: lag columns print as x<i>[t-<k>]."""
        for j in range(len(lags) - 1, -1, -1):
            i, k = lags[j]
            eq = re.sub(rf"\bx{base + j}\b", f"x{i}[t-{k}]", eq)
        return eq

    # ── basic mechanisms (owner, 2026-07-15): comparison as organs ──
    # "adding these basic tools and any other basic computer mechanism
    # to his toolkit will be extremely helpful." Each returns value +
    # RECEIPT; larger/smaller ROUTE THROUGH compare (the a-b<0 wiring
    # made visible — the execution cycle's smallest trace). Algebraic
    # twins live in the equation grammar (crease/step atoms), so the
    # same mechanism is sayable in equations AND routable in process.

    def compare(self, a, b, tol=0.0):
        """Compare two values: the sign of a-b as -1/0/+1, with a receipt.
        tol widens SAME to a measured tolerance (a floor), never a
        hand-set default."""
        d = float(a) - float(b)
        v = 0 if abs(d) <= tol else (1 if d > 0 else -1)
        return dict(tool="compare", value=v,
                    receipt=f"sign({a:g}-{b:g}) -> {v:+d} (tol {tol:g})",
                    routed_via=[])

    def larger(self, a, b):
        """Larger of two values, routed THROUGH compare (receipt chain).
        Algebraic twin the grammar can say: (a+b+|a-b|)/2."""
        c = self.compare(a, b)
        v = float(a) if c["value"] >= 0 else float(b)
        return dict(tool="larger", value=v,
                    receipt=f"larger({a:g},{b:g}) via compare -> {v:g}",
                    routed_via=[c])

    def smaller(self, a, b):
        """Smaller of two values, routed THROUGH compare (receipt chain).
        Algebraic twin: (a+b-|a-b|)/2."""
        c = self.compare(a, b)
        v = float(b) if c["value"] >= 0 else float(a)
        return dict(tool="smaller", value=v,
                    receipt=f"smaller({a:g},{b:g}) via compare -> {v:g}",
                    routed_via=[c])

    def switch(self, cond, then_v, else_v):
        """The routing primitive: a condition picks the branch and the
        receipt names the door taken (do op, take result door)."""
        v = then_v if cond else else_v
        return dict(tool="switch", value=v,
                    receipt=f"switch({bool(cond)}) -> "
                            f"{'then' if cond else 'else'}",
                    routed_via=[])

    # ── flows: the execution cycle (owner, 2026-07-15) ──────────
    # "do op, take result door, or return to main program. each node
    # can act like a function generator." Flows are NET CONTENT
    # (flow:/step:/chunk: nodes) read by the walker — the kernel
    # loop's first permanent slice. Every juncture leaves receipts
    # for the door taken AND the doors bypassed (the consideration
    # law); every walk lands in the findings ledger.

    def define_flow(self, name, steps):
        """Author a flow as net content: flow:<name> doors to its
        first step; each step:<name>.<id> carries a READABLE spec
        (op = a registered organ, args drawn from state, optional
        declarative measure, doors with declarative predicates — the
        last door without 'when' is the default). Same substrate as
        content, different altitude."""
        fnode = f"flow:{name}"
        first = f"step:{name}.{steps[0]['id']}"
        self.net.add_door(fnode, first, tag="flow-start")
        self.net.set_meta(fnode, "steps", steps)   # ordered, clonable
        for st in steps:
            node = f"step:{name}.{st['id']}"
            self.net.set_meta(node, "spec", st)
            for d in st.get("doors", []):
                self.net.add_door(node, f"step:{name}.{d['to']}",
                                  tag="flow-next")
        return fnode

    def _eval_when(self, when, result, state):
        """Declarative branch predicate, routed THROUGH the compare
        organ when numeric (the comparison booleans ARE the routing
        predicates). Returns (fired, receipt)."""
        if "equals" in when:
            got = result.get(when["field"])
            fired = got == when["equals"]
            return fired, (f"{when['field']}=='{when['equals']}'? "
                           f"got '{got}' -> {fired}")
        if "cmp" in when:
            a = result.get(when["field"])
            b = when["than"]
            b = state.get(b, b) if isinstance(b, str) else b
            c = self.compare(float(a), float(b))
            fired = (c["value"] < 0) if when["cmp"] == "smaller" \
                else (c["value"] > 0)
            return fired, (f"{when['cmp']}({a:.4g},{b:.4g}) via "
                           f"{c['receipt']} -> {fired}")
        return False, f"unknown predicate {when} -> refused"

    def walk_flow(self, name, state, hop_cap=12, _depth=0):
        """THE WALKER: do op -> take result door -> return to main.
        Accepts a flow name, 'flow:<name>', or a minted
        'chunk:<name>'. Every step fires or is BYPASSED WITH A
        RECEIPT; a cyclic flow halts at the hop cap; a step naming a
        missing organ refuses honestly. Returns (outcome, trace) —
        the trace is a replayable record."""
        node = name if str(name).startswith(("flow:", "chunk:")) \
            else f"flow:{name}"
        if node.startswith("chunk:"):
            spec = self.net.get_meta(node, "spec") or {}
            if spec.get("op") == "chunk":
                out, sub = self.walk_flow(spec["flow"], state,
                                          hop_cap, _depth + 1)
                tr = [dict(step=node, op="chunk",
                           receipt=f"chunk expanded -> {out}",
                           nested=sub)]
                if _depth == 0:
                    self.record_finding("flow-walk", node, outcome=out,
                                        hops=len(sub), road=["chunk"])
                return out, tr
            return "refused", [dict(step=node,
                                    receipt="no chunk spec — refused")]
        flow_short = node.split(":", 1)[1]
        trace, outcome, hops = [], None, 0
        nxt = sorted(self.net.get_doors(node, tag="flow-start"))
        step = nxt[0] if nxt else None
        while step is not None and outcome is None:
            if hops >= hop_cap:
                trace.append(dict(step=step,
                                  receipt=f"HOP CAP {hop_cap} reached "
                                          f"— returning to main (no "
                                          f"runaway walks)"))
                outcome = "hop-cap"
                break
            hops += 1
            spec = self.net.get_meta(step, "spec") or {}
            op = spec.get("op")
            if op == "chunk":
                sub_out, sub_tr = self.walk_flow(spec["flow"], state,
                                                 hop_cap, _depth + 1)
                trace.append(dict(step=step, op="chunk",
                                  receipt=f"chunk expanded -> "
                                          f"{sub_out}",
                                  nested=sub_tr))
                outcome = sub_out
                break
            fn = getattr(self, op, None) if op else None
            if fn is None and op:      # the initiator's runtime ops
                fn = getattr(self, "_ext_ops", {}).get(op)
            if fn is None or not callable(fn):
                trace.append(dict(step=step, op=op,
                                  receipt=f"REFUSED: no organ named "
                                          f"'{op}' — walk ends "
                                          f"honestly (ext ops need "
                                          f"their initiator after a "
                                          f"resurrection)"))
                outcome = "refused"
                break
            kwargs = {k: state[v]
                      for k, v in spec.get("args", {}).items()}
            result = fn(**kwargs)
            result = result if isinstance(result, dict) \
                else {"value": result}
            meas = spec.get("measure")
            if meas and meas.get("rms_against") is not None:
                p = np.asarray(result.get("value"), float)
                yv = np.asarray(state[meas["rms_against"]], float)
                okm = np.isfinite(p)
                result["rms"] = float(np.sqrt(
                    np.mean((p[okm] - yv[okm]) ** 2)))
            state[spec.get("out", f"_{spec.get('id', 'r')}")] = result
            rec = dict(step=step, op=op,
                       receipt=f"ran {op}; keys {sorted(result)[:6]}")
            taken, door_receipts = None, []
            for d in spec.get("doors", []):
                if "when" not in d:
                    if taken is None:
                        taken = d["to"]
                        door_receipts.append(f"-> {d['to']} "
                                             f"(default door)")
                    else:
                        door_receipts.append(f"bypassed {d['to']}: an "
                                             f"earlier door already "
                                             f"fired")
                    continue
                fired, why = self._eval_when(d["when"], result, state)
                if fired and taken is None:
                    taken = d["to"]
                    door_receipts.append(f"-> {d['to']}: {why}")
                else:
                    door_receipts.append(f"bypassed {d['to']}: {why}")
            rec["doors"] = door_receipts
            trace.append(rec)
            step = None if taken is None \
                else f"step:{flow_short}.{taken}"
        if outcome is None:
            outcome = state.get("_outcome", "done")
        if _depth == 0:
            self.record_finding(
                "flow-walk", node, outcome=outcome, hops=hops,
                road=[t["step"].split(".")[-1]
                      for t in trace if "step" in t])
        return outcome, trace

    def mint_chunk(self, flow_name, name, minted_after=None):
        """THE FUNCTION GENERATOR v1 (owner: "each node can act like
        a function generator"): a chain that keeps winning becomes
        ONE node — a new step whose op is the recorded chain,
        registered under the chunks hub, walkable by name."""
        node = f"chunk:{name}"
        flow = flow_name if str(flow_name).startswith("flow:") \
            else f"flow:{flow_name}"
        self.net.add_door("chunks", node, tag="chunk")
        self.net.set_meta(node, "spec",
                          dict(id=name, op="chunk", flow=flow,
                               minted_after=minted_after))
        return node

    def _flow_success_steps(self, flow):
        node = flow if str(flow).startswith("flow:") else f"flow:{flow}"
        steps = self.net.get_meta(node, "steps") or []
        return {st["id"] for st in steps if st.get("success")}

    def flow_tally(self, name=None, window=None):
        """Win/loss tallies per flow from the walk ledger. A win = a
        walk ending on a step the flow DECLARED success=True (a flow
        with no declared successes counts outcome=='done'). window=W
        judges only each flow's last W walks (recent-window, the
        word-election shape)."""
        rows = list(reversed(self.recall_findings(kind="flow-walk",
                                                  limit=10_000)))
        per = {}
        for w in rows:
            fl = w.get("name")
            if name and fl not in (name, f"flow:{name}"):
                continue
            per.setdefault(fl, []).append(w)
        tally = {}
        for fl, ws in per.items():
            ws2 = ws[-window:] if window else ws
            succ = self._flow_success_steps(fl)
            wins = 0
            for w in ws2:
                rd = w.get("road") or []
                if succ:
                    wins += int(bool(rd) and rd[-1] in succ)
                else:
                    wins += int(w.get("outcome") == "done")
            tally[fl] = dict(wins=wins, walks=len(ws2))
        return tally

    def elect_flow(self, candidates, task, window=None):
        """Elect the champion flow for a task by MEASURED win rate —
        word elections generalized to PROCESS. Losers stay on the
        books with their tallies; the task node carries the champion
        with an active/superseded chain (never erased — the
        read_floor pattern); the election lands in the ledger."""
        tallies = {}
        for c in candidates:
            t = self.flow_tally(c, window=window)
            tallies[c] = t.get(f"flow:{c}", dict(wins=0, walks=0))

        def rate(d):
            return d["wins"] / max(d["walks"], 1)

        champ = max(candidates,
                    key=lambda c: (rate(tallies[c]),
                                   tallies[c]["wins"]))
        node = f"task:{task}"
        old = self.net.get_meta(node, "champion")
        rec = dict(flow=champ, window=window, tallies=tallies)
        if old is not None:
            chain = old.get("superseded") or []
            if old.get("flow") != champ:
                prev = {k: v for k, v in old.items()
                        if k != "superseded"}
                chain = chain + [prev]
            rec["superseded"] = chain
        self.net.add_door("tasks", node, tag="task")
        self.net.set_meta(node, "champion", rec)
        self.record_finding("flow-election", task, champion=champ,
                            window=window, tallies=tallies)
        return dict(champion=champ, tallies=tallies,
                    receipt=f"champion '{champ}' by win rate; losers "
                            f"kept on the record")

    def branch_flow(self, src, new_name, at_step, door, extra_steps):
        """PIECEWISE FLOW SUPERSESSION, the mechanical half: clone a
        flow, graft ONE door at the named step (before its default
        door) plus the steps that door leads to. The intelligent half
        stays where it belongs — the miner names the condition, the
        election decides, the loser is kept."""
        import copy
        steps = copy.deepcopy(self.net.get_meta(f"flow:{src}", "steps")
                              or [])
        if not steps:
            return None
        placed = False
        for st in steps:
            if st["id"] == at_step:
                doors = st.setdefault("doors", [])
                idx = next((i for i, d in enumerate(doors)
                            if "when" not in d), len(doors))
                doors.insert(idx, copy.deepcopy(door))
                placed = True
        if not placed:
            return None
        pos = next(i for i, st in enumerate(steps)
                   if st["id"] == at_step) + 1
        steps[pos:pos] = copy.deepcopy(extra_steps)
        node = self.define_flow(new_name, steps)
        self.net.set_meta(node, "branched_from",
                          dict(src=f"flow:{src}", at_step=at_step,
                               door=door))
        return node

    def _outlier_source(self, enum, X, y, half):
        """THE OUTLIER'S OWN LAW (owner, 2026-07-15): "if the outlier
        is a plus something else, can it quantify that something else
        ... and identify the model of the source?" Rows the admitted
        law cannot carry are ISOLATED (5*MAD-from-median — robust to
        the bend the outliers themselves cause) and their deviations
        QUANTIFIED in units. Three-way verdict: exact grain multiples
        whose clean majority re-certifies machine-exact -> MIS-ENTRY
        (cells quarantined with receipts; the law superseded by its
        clean refit); a lawful pattern of their own, past a scrambled-
        deviation control -> SECOND SOURCE (news, not error; recorded,
        never silently merged); neither -> deviations kept on the
        record. ONE ROUND ONLY (never flag->model->flag). Mutates enum
        ONLY on a confirmed mis-entry cure. v1 constants (5*MAD, 0.35
        cap, 0.8 grid fraction) are hand-set — the standing
        tests-over-thresholds debt, filed."""
        p_all = np.concatenate([enum.predict(X[:half]),
                                enum.predict(X[half:])])
        d = y - p_all
        med = float(np.median(d))
        mad = float(np.median(np.abs(d - med))) + 1e-12
        flag = np.abs(d - med) > 5.0 * mad
        k = int(flag.sum())
        rec = dict(kind="none", n_flagged=k, rounds=1,
                   mad=round(mad, 6),
                   why=f"{k} rows beyond 5*MAD of the admitted law")
        grain_road, _ = self._floor_grain(y)
        # road A' — THE CLEAN-MAJORITY SEARCH (the rival-form duel
        # fused into the owner's road): a flexible fit ABSORBS point
        # poison (battery O1, wrong-kept: only 2/6 poisoned rows
        # survived as outliers of the 16-term fit), so isolation must
        # run against SIMPLE RIVAL FORMS — a 2-term form cannot bend
        # around single cells. For exact-checkable data (grain
        # evidenced): find a simple pure-variable form that is
        # machine-exact on >=85% of rows with the remainder sitting
        # on the grain — that form BEATS the absorber, and the
        # remainder is quarantined.
        if grain_road:
            n_vars = X.shape[1]
            g = float(grain_road["sigma"]) * np.sqrt(12.0)
            pv = [(i,) for i in range(n_vars)]
            pv += [(i, j) for i in range(n_vars)
                   for j in range(i, n_vars)]
            pv += [(i, j, kk) for i in range(n_vars)
                   for j in range(i, n_vars)
                   for kk in range(j, n_vars)]
            cols_all = {t: np.prod([X[:, a] for a in t], axis=0)
                        for t in pv}
            base = y - y.mean()
            bs = base.std() + 1e-12
            ranked = sorted(pv, key=lambda t: -abs(float(
                np.corrcoef(cols_all[t], base)[0, 1]))
                if cols_all[t].std() > 1e-12 else 0.0)[:12]
            from itertools import combinations
            snap = (list(enum.terms), enum.coefs.copy(), enum.intercept)
            for kk in (1, 2, 3):
                for sub in combinations(ranked, kk):
                    C = np.column_stack([cols_all[t] for t in sub]
                                        + [np.ones(len(y))])
                    beta0, *_ = np.linalg.lstsq(C, y, rcond=None)
                    r = y - C @ beta0
                    rm = float(np.median(r))
                    rmad = float(np.median(np.abs(r - rm))) + 1e-12
                    fl = np.abs(r - rm) > 5.0 * rmad
                    if fl.sum() == 0 or fl.sum() > 0.15 * len(y):
                        continue
                    keep = ~fl
                    beta, *_ = np.linalg.lstsq(C[keep], y[keep],
                                               rcond=None)
                    rk = y - C @ beta
                    scale = float(max(np.max(np.abs(y)), 1e-12))
                    if np.max(np.abs(rk[keep])) / scale > _EXACT_REL:
                        continue
                    mult = rk[fl] / g
                    hit = (np.abs(mult - np.round(mult)) < 0.05) \
                        & (np.abs(np.round(mult)) >= 1)
                    if float(np.mean(hit)) < 0.8:
                        continue
                    # the simple form wins: supersede + quarantine.
                    # terms are var-atom tuples (var atoms are specs
                    # 0..n_vars-1 by construction).
                    enum.terms = [tuple(t) for t in sub]
                    enum.coefs = beta[:-1]
                    enum.intercept = float(beta[-1])
                    kf = int(fl.sum())
                    rec.update(
                        kind="mis-entry", n_flagged=kf,
                        why=(f"a simple {kk}-term form is machine-"
                             f"exact on {int(keep.sum())}/{len(y)} "
                             f"rows; the {kf} leftovers sit exact "
                             f"grain multiples (quantum {g:g}) off it "
                             f"— the flexible fit had ABSORBED them; "
                             f"cells quarantined, never banked"),
                        quarantined=[
                            dict(row=int(i), y=float(y[i]),
                                 predicted=round(float((C @ beta)[i]),
                                                 6),
                                 deviation=round(float(rk[i]), 6))
                            for i in np.where(fl)[0]])
                    return rec, True
            enum.terms, enum.coefs, enum.intercept = snap
        # flag-dependent roads below need enough (and few enough)
        # outliers OF THE ADMITTED FIT — A' above needs neither
        # (the absorber hides its poison; battery O1, wrong-kept)
        if k < 3:
            return rec, False
        if k > 0.35 * len(y):
            rec["why"] += (" — too many to be outliers: the LAW is "
                           "suspect, not the data; pass refused")
            return rec, False
        dev = d[flag]
        rec["deviation_rms"] = round(float(np.sqrt(np.mean(dev ** 2))), 6)
        # road A — MIS-ENTRY vs the admitted fit's own deviations
        if grain_road:
            quantum = None
            for qcand in (float(grain_road["sigma"]) * np.sqrt(12.0),
                          float(grain_road["sigma"])):
                m = dev / qcand
                hit = (np.abs(m - np.round(m)) < 0.05) \
                    & (np.abs(np.round(m)) >= 1)
                if float(np.mean(hit)) >= 0.8:
                    quantum = qcand
                    break
            if quantum is not None:
                snap = (list(enum.terms), enum.coefs.copy(),
                        enum.intercept)
                tr_ok, ho_ok = ~flag[:half], ~flag[half:]
                if tr_ok.sum() >= 8 and ho_ok.sum() >= 4:
                    ex = _exact_road(enum.specs, enum.A[tr_ok],
                                     y[:half][tr_ok], X[half:][ho_ok],
                                     y[half:][ho_ok], X.shape[1])
                    if ex is not None:
                        enum.terms = [tuple(t) for t in ex]
                        D = enum._design(enum.A[tr_ok])
                        beta = np.linalg.lstsq(D, y[:half][tr_ok],
                                               rcond=None)[0]
                        enum.coefs = beta[:-1]
                        enum.intercept = float(beta[-1])
                        p_c = enum.predict(X[half:][ho_ok])
                        rms_c = float(np.sqrt(np.mean(
                            (y[half:][ho_ok] - p_c) ** 2)))
                        scale = float(max(np.max(np.abs(y)), 1e-12))
                        if rms_c / scale < _EXACT_REL:
                            rec["kind"] = "mis-entry"
                            rec["why"] = (
                                f"{k} cells sit an exact grain "
                                f"multiple off the law (quantum "
                                f"{quantum:g}); the clean majority "
                                f"re-certifies machine-exact — cells "
                                f"quarantined, never banked")
                            rec["quarantined"] = [
                                dict(row=int(i), y=float(y[i]),
                                     predicted=round(float(p_all[i]), 6),
                                     deviation=round(float(d[i]), 6))
                                for i in np.where(flag)[0]]
                            return rec, True
                        enum.terms, enum.coefs, enum.intercept = snap
        # road B — SECOND SOURCE: do the deviations have their own law?
        if k >= 24:
            rs = Isaac().discover(X[flag], dev, outlier_pass=False)
            rng = np.random.default_rng(97)
            rs_s = Isaac().discover(X[flag], rng.permutation(dev),
                                    outlier_pass=False)
            if rs["verdict"] == "UNDERSTOOD" \
                    and rs_s["verdict"] != "UNDERSTOOD":
                rec["kind"] = "second-source"
                rec["source_equation"] = rs["equation"]
                rec["source_certificate"] = rs.get("certificate")
                rec["why"] = (f"{k} rows carry a LAWFUL deviation — "
                              f"news, not error: {rs['equation']} "
                              f"(scrambled control minted nothing)")
        return rec, False

    # ── discovery: the challenge loop ───────────────────────────

    def discover(self, X, y, name=None, verbose=False, told_sigma=None,
                 outlier_pass=True, container=None, use_lags=True):
        """THE CHALLENGE LOOP. Given examples of something he cannot yet do
        (inputs X -> outcome y), find the rule. Half the examples are held
        out — the rule must WORK, not merely fit. Four honest verdicts:

          UNDERSTOOD  explicit equation, validated held-out (R2 >= 0.9)
          PARTIAL     a real equation that explains part; the rest is dark
          CAPTURED    no equation yet, but stored examples predict held-out
                      outcomes past the permuted null — caught, not said
          NO RULE     nothing beats chance: proven nothing, at this class

        An UNDERSTOOD/PARTIAL law becomes a node (law:<name>) with its
        equation in meta; apply_law() applies it from then on — the
        challenge has become computable. Facts are indexed for reasoning."""
        X = np.asarray(X, float); y = np.asarray(y, float)
        good = np.isfinite(X).all(1) & np.isfinite(y)     # red-team A8
        if not good.all():
            X, y = X[good], y[good]
        # learned combinations join the basis: every registered composite
        # that fits this data becomes a first-class column, so atoms
        # (sin/cos/exp/pow) can act ON combinations — the vocabulary Isaac
        # earned on past problems is offered to every new one
        d_raw = X.shape[1]
        # lag atoms: rows read as consecutive samples; the proposal is
        # null-gated, so exchangeable rows change nothing. Lag columns
        # are built BEFORE any domain drop can remove interior rows —
        # a lagged value is only true on the original spacing.
        lags = self._propose_lags(X, y) if use_lags else []
        lag_cols = self._lag_columns(X, lags) if lags else None
        comps = self._applicable_composites(d_raw)
        if comps:
            X = self._augment_with(X, comps)
        if lags:
            X = np.column_stack([X, lag_cols])    # [raw | comps | lags]
        if comps or lags:
            ok_rows = np.isfinite(X).all(1)       # composite-domain rows
            if not ok_rows.all():                 # and history-less lag
                X, y = X[ok_rows], y[ok_rows]     # rows drop out honestly
        half = len(y) // 2
        enum = _Enumerator()
        enum.holdout = (X[half:], y[half:])   # the rounding referee's
        # fresh-row court reads these; it never trains on them
        enum.fit(X[:half], y[:half])
        p = enum.predict(X[half:])
        # THE EXACT ROAD (S2b requirement 4): machine precision proven
        # on unseen rows outranks statistics — it may override the
        # admitted form (exactness on fresh rows is the rival-killer),
        # and it is how a law with 8 planets gets said at all.
        exact_stamp = False
        ex_terms = _exact_road(enum.specs, enum.A, y[:half],
                               X[half:], y[half:], X.shape[1])
        if ex_terms is not None:
            enum.terms = [tuple(t) for t in ex_terms]
            enum._refit(y[:half])
            p = enum.predict(X[half:])
            exact_stamp = True
        ss = float(np.sum((y[half:] - y[half:].mean()) ** 2))
        r2 = 1 - float(np.sum((y[half:] - p) ** 2)) / max(ss, 1e-12)
        # right-enough-to-use vs form-true: a surrogate can match the law on
        # the dense CENTER of the observed range yet diverge at its EDGES.
        # Score the outer quarter of the held-out set separately and LABEL
        # the law's scope — both grades are usable, neither is silently the
        # other.
        dist = np.linalg.norm(X[half:] - X[:half].mean(0), axis=1)
        edge = dist >= np.percentile(dist, 75)
        if edge.sum() >= 20:
            ss_e = float(np.sum((y[half:][edge] - y[half:][edge].mean()) ** 2))
            r2_edge = 1 - float(np.sum((y[half:][edge] - p[edge]) ** 2)) \
                / max(ss_e, 1e-12)
        else:
            r2_edge = r2
        scope = "form-true (edges hold)" if r2_edge >= 0.85 else \
            "range-valid (usable inside observed range)"
        cap_r2, cap_null = self._capture(X[:, :d_raw], y, half)
        # a real partial equation is knowledge whatever the headline verdict
        # says — it must never be discarded because capture scored higher
        # (the CAPTURED-erases-law bug, 2026-07-03 audit)
        has_law = bool(enum.terms) and r2 >= 0.2

        # ═══ THE VERDICT REWRITE (S2b, 2026-07-15): UNDERSTOOD is
        # EARNED before examiners and a ruler — r2 is a reported
        # number, no longer the judge. Replay: can any candidate form
        # predict the held-out leftover (selection-corrected)? Pool:
        # can ANYTHING cheap (grammar-free)? Certificate: is the
        # residual machine-exact, within an EVIDENCED floor, above it,
        # or uncertifiable (no floor evidenced — said so, never
        # assumed)? Every examiner fires or leaves a bypass receipt.
        # floors come from the CURED organ (read_floor: consensus-
        # ejected repeats, coarsest-consistent grain, told road with
        # contradiction flagging) — reuse law, never a rival reader
        if told_sigma is not None and name:
            tn = f"floor:{name}"
            if not self.net.get_meta(tn, "told"):
                self.net.set_meta(tn, "told",
                                  dict(sigma=float(told_sigma),
                                       who="caller"))
        fl = self.read_floor(y, X[:, :d_raw], name=name)
        floor_std, floor_why = fl["floor"], fl["why"]
        if told_sigma is not None and not name:
            if floor_std is None or float(told_sigma) > floor_std:
                floor_std = float(told_sigma)
                floor_why = f"told {told_sigma:g} | " + floor_why
        legs = dict(replay=dict(state="bypassed: no law admitted"),
                    pool=dict(state="bypassed: no law admitted"))
        resid_ho = y[half:] - p
        scale_y = float(max(np.max(np.abs(y)), 1e-12))
        rms_ho = float(np.sqrt(np.mean(resid_ho ** 2)))
        if enum.terms and (exact_stamp or rms_ho / scale_y < _EXACT_REL):
            certificate = "machine-exact"
            legs = dict(replay=dict(state="bypassed: machine-exact"),
                        pool=dict(state="bypassed: machine-exact"))
        else:
            if enum.terms:
                A_ho = np.column_stack([_atom_col(X[half:], s)
                                        for s in enum.specs])
                rngv = np.random.default_rng(1234 + len(y))
                st, who, obs, thr = _replay_scan(
                    enum, A_ho, X[half:, :d_raw], resid_ho, rngv)
                legs["replay"] = dict(state=st, who=who,
                                      obs=round(obs, 4),
                                      thr=round(thr, 4))
                resid_tr = y[:half] - enum.predict(X[:half])
                Xp = np.vstack([X[:half, :d_raw], X[half:, :d_raw]])
                rp = np.concatenate([resid_tr, resid_ho])
                if len(rp) >= _POOL_MIN_N:
                    cp, tp, scream = _pool_scream(
                        Xp, rp, rng_seed=4321 + len(y))
                    legs["pool"] = dict(
                        state="scream" if scream else "quiet",
                        cap=round(cp, 4), thr=round(tp, 4))
                else:
                    legs["pool"] = dict(
                        state=f"bypassed: n={len(rp)} < {_POOL_MIN_N}"
                              f" (measured scope)")
            if floor_std is not None:
                certificate = (("within floor"
                                if rms_ho <= 3 * floor_std
                                else "above floor") + f" ({floor_why})")
            else:
                certificate = "uncertified (no floor evidenced)"
        # THE OUTLIER'S OWN LAW (owner, 2026-07-15): when a law stands
        # but is not machine-exact, the rows it cannot carry get
        # isolated, quantified, and ASKED WHAT THEY ARE — mis-entry
        # (quarantine + clean refit supersedes), a second source
        # (news, recorded), or unknown (kept).
        outrec = None
        if outlier_pass and enum.terms and floor_std is not None \
                and certificate != "machine-exact":
            outrec, cured_o = self._outlier_source(enum, X, y, half)
            if cured_o:
                p = enum.predict(X[half:])
                ss = float(np.sum((y[half:] - y[half:].mean()) ** 2))
                r2 = 1 - float(np.sum((y[half:] - p) ** 2)) \
                    / max(ss, 1e-12)
                resid_ho = y[half:] - p
                rms_ho = float(np.sqrt(np.mean(resid_ho ** 2)))
                certificate = (f"machine-exact (clean majority; "
                               f"{outrec['n_flagged']} cells "
                               f"quarantined as mis-entry)")
                legs = dict(
                    replay=dict(state="bypassed: clean-refit "
                                      "machine-exact (outlier road)"),
                    pool=dict(state="bypassed: clean-refit "
                                    "machine-exact (outlier road)"))
        surprise = (legs["replay"].get("state") == "fired"
                    or legs["pool"].get("state") == "scream")
        if enum.terms and r2 >= 0.9 and not surprise \
                and not certificate.startswith("above floor"):
            verdict = "UNDERSTOOD"
        elif cap_r2 > max(cap_null + 0.1, 0.2) and cap_r2 > r2 + 0.1:
            verdict = "CAPTURED"
        elif has_law:
            verdict = "PARTIAL"
        else:
            verdict = "NO RULE"

        # ═══ THE ACCOUNTING (audit 2.8): articulated% + captured% + noise%
        # = 100. Articulated = what the kept equation explains (held-out).
        # Captured = what exemplars additionally predict ON THE RESIDUAL,
        # past a permuted null. Noise = the remainder that beat nothing in
        # this expressive class — proven noise AT THIS CLASS, not absolutely.
        art = max(0.0, min(r2, 1.0)) if has_law else 0.0
        if has_law:
            resid = y - np.concatenate([enum.predict(X[:half]), p])
            if resid[half:].std() > 1e-9 * max(y.std(), 1e-12):
                capres, capres_null = self._capture(X, resid, half)
            else:
                capres, capres_null = 0.0, 0.0
        else:
            resid, capres, capres_null = y - y.mean(), cap_r2, cap_null
        cap_frac = (max(0.0, min(capres, 1.0)) * (1.0 - art)
                    if capres > max(capres_null + 0.1, 0.1) else 0.0)
        accounting = dict(
            articulated=round(100 * art, 1),
            captured=round(100 * cap_frac, 1),
            noise=round(100 * (1.0 - art - cap_frac), 1),
            noise_meaning="proven at THIS expressive class only: neither the "
                          "equation library nor exemplar capture beat the "
                          "permuted null on this remainder")
        # the unexplained share is a FIRST-CLASS object with a dossier:
        # can't say what it is; can characterize how it behaves; track it
        dossier = None
        if (1.0 - art) > 0.05:
            rs = resid[half:]
            cr = np.zeros(X.shape[1])
            if rs.std() > 1e-12:
                Z = (X[half:] - X[half:].mean(0)) / (X[half:].std(0) + 1e-12)
                cr = np.abs((Z * ((rs - rs.mean()) / rs.std())[:, None]
                             ).mean(0))
            top = np.argsort(-cr)[:3]
            dossier = dict(
                unknown=f"x:{name or 'challenge'}",
                share_pct=round(100 * (1.0 - art), 1),
                captured_pct_of_it=round(
                    100 * cap_frac / max(1e-9, 1.0 - art), 1),
                responsive_channels=[[int(j), round(float(cr[j]), 3)]
                                     for j in top],
                rms=round(float(np.sqrt(np.mean(rs ** 2))), 4),
                edge_rms=round(float(np.sqrt(np.mean(rs[edge] ** 2)))
                               if edge.sum() else 0.0, 4))

        # DATA ADEQUACY (owner, 2026-07-03: "able to detect or define the
        # data that is too weak to interpret?"). When little or nothing was
        # interpretable, name the cause WITH evidence and what would fix
        # it — weak data is a diagnosis, not a shrug.
        adequacy = dict(verdict="interpretable", reasons=[])
        if verdict in ("NO RULE", "CAPTURED") or r2 < 0.5:
            reasons = []
            if len(y) < 100:
                reasons.append(
                    f"sample too small: n={len(y)} is below the measured "
                    f"recovery onset (~100 rows) — collect more")
            if dossier and max((c for _, c in
                                dossier["responsive_channels"]),
                               default=0.0) < 2.0 / np.sqrt(max(len(y), 4)):
                reasons.append(
                    "no measured channel responds to the unexplained part "
                    "— the driver may not be among these columns (a "
                    "missing-variable shadow)")
            if cap_r2 > max(cap_null + 0.1, 0.2) and r2 < 0.5:
                reasons.append(
                    "structure IS present (stored examples predict it "
                    f"at {cap_r2:.2f}) but no equation in the library says "
                    "it — an expressive-class limit, not weak data")
            if accounting["noise"] >= 90 and \
                    cap_r2 <= max(cap_null + 0.1, 0.2):
                reasons.append(
                    "nothing beats chance at this class: either noise, or "
                    "the drivers were not measured")
            if reasons or verdict == "NO RULE":
                adequacy = dict(
                    verdict=("too weak to interpret"
                             if verdict == "NO RULE" else
                             "partially interpretable"),
                    reasons=reasons or
                    ["weak fit without a single identified cause"])
        if adequacy["verdict"] == "interpretable" and len(y) < 100:
            # found something anyway — but small samples carry wrong-form
            # risk (battery: provisional below n~400, onset ~100), so the
            # caution attaches even to a success
            adequacy = dict(
                verdict="interpretable (provisional: small sample)",
                reasons=[f"sample too small for a confident form: "
                         f"n={len(y)} — the equation may be a look-alike; "
                         f"collect more or confirm() at the probes"])

        rivals = []
        if has_law and not (outrec is not None
                            and outrec.get("kind") == "mis-entry"):
            # on a mis-entry cure the rival contest is already settled
            # by clean-majority machine-exactness — and rival_check's
            # state restore REFITS on the contaminated train, which
            # would re-poison the cured constants (battery O1,
            # wrong-kept: err 6.7e-2 reappeared through this door)
            rivals = enum.rival_check(y[:half])
        eq_str = self._rename_lags(enum.equation(), d_raw + len(comps),
                                   lags)
        eq_str = self._rename_composites(eq_str, d_raw, comps)
        if rivals and adequacy["verdict"] != "interpretable":
            adequacy["reasons"].append(
                f"observed range too narrow to pin the form: "
                f"{len(rivals)} rival form(s) still tied — extend sampling "
                f"toward the named probe(s)")
        if name and has_law:
            node = f"law:{name}"
            self.net.add_door("law", node, tag="law")
            self.net.set_meta(node, "model", dict(
                terms=list(enum.terms), coefs=enum.coefs,
                intercept=enum.intercept, d=X.shape[1], r2=r2,
                specs=list(enum.specs), rivals=rivals,
                ranges=[[float(X[:, k].min()), float(X[:, k].max())]
                        for k in range(X.shape[1])],
                r2_edge=r2_edge, d_raw=d_raw,
                composites_used=[dict(c) for c in comps],
                lags_used=[[int(i), int(k)] for i, k in lags],
                # the full proposal scan, refused columns included:
                # [col, best_lag, score, null_gate] per raw column
                lag_scan=list(getattr(self, "_last_lag_scan", []))))
            self.net.set_meta(node, "equation", eq_str)
            self.net.set_meta(node, "accounting", accounting)
            self.net.set_meta(node, "certificate", certificate)
            self.net.set_meta(node, "verdict_legs", legs)
            # the earned verdict lives ON the node: crystallize_forms
            # admits only what was EARNED in its own container
            self.net.set_meta(node, "verdict", verdict)
            if outrec is not None:
                self.net.set_meta(node, "outliers", outrec)
            if dossier:
                self.net.set_meta(node, "residual_dossier", dossier)
            # PER-DATASET CONTAINERS (owner, 2026-07-17: "each dataset
            # is defaulted to its own container"): container = SOURCE
            # identity, never a hand-filed subject. Explicit kwarg
            # wins; an open non-base world is respected (the session
            # road); otherwise the dataset's own world, never base.
            c = container
            if c is None:
                active = getattr(self, "active_container", "base")
                c = active if active != "base" else f"data-{name}"
            self.net.add_door(f"world:{c}", node, tag=f"in:{c}")
            self.net.set_meta(node, "container", c)
            # THE FACTS LAYER (owner, 2026-07-18): the structure
            # keeps a sampled breakdown of the datapoints that
            # earned it — deterministic (same data, same memory),
            # capped (a sample, never a hoard), referenceable
            self.net.set_meta(node, "evidence",
                              self._sample_evidence(X[:, :d_raw], y))
            self._teach_fact(node, "explains", name or "challenge",
                             container=c)
        if verbose:
            print(f"    discover[{name}]: {verdict} [{scope}]  R2 {r2:.3f}  "
                  f"edge {r2_edge:.3f}  captured {cap_r2:.3f}  "
                  f"eq: {eq_str}")
            print(f"      accounting: articulated {accounting['articulated']}"
                  f"% + captured {accounting['captured']}% + noise "
                  f"{accounting['noise']}% = 100")
        riv_summary = [dict(rival=r["rival"], F=r["F"], probe=r["probe"])
                       for r in rivals]
        self.record_finding(
            "law" if has_law else "verdict",
            name or "challenge", verdict=verdict, equation=eq_str,
            r2=r2, r2_edge=r2_edge, scope=scope, captured_r2=cap_r2,
            certificate=certificate, floor=floor_why, legs=legs,
            n=len(y), d=X.shape[1], rivals=riv_summary,
            accounting=accounting, dossier=dossier,
            model=(dict(terms=list(enum.terms), coefs=enum.coefs,
                        intercept=enum.intercept, d=X.shape[1], r2=r2,
                        specs=list(enum.specs), d_raw=d_raw,
                        composites_used=[dict(c) for c in comps],
                        lags_used=[[int(i), int(k)] for i, k in lags])
                   if has_law else None))
        capture = None
        if verdict == "CAPTURED" and name:
            capture = self.capture_net(name, X[:, :d_raw], y)
        return dict(verdict=verdict, equation=eq_str,
                    r2=r2, r2_edge=r2_edge, scope=scope, captured_r2=cap_r2,
                    certificate=certificate, floor=floor_why, legs=legs,
                    outliers=outrec,
                    rivals=riv_summary, accounting=accounting,
                    dossier=dossier, adequacy=adequacy, capture=capture)

    # ── THE FACTS LAYER (owner, 2026-07-18: "datapoint breakdowns
    # he can reference and save... sampling for context and
    # reference. give him some kind of memory") ──────────────────

    @staticmethod
    def _sample_evidence(X, y, cap=24):
        """A deterministic sample of the rows that earned a
        structure: per-column extremes + an even spread by outcome
        rank. Same data -> same memory (the artifact claim); capped
        (a sample, never a hoard — re-feeding stays cheap)."""
        X = np.asarray(X, float)
        y = np.asarray(y, float)
        n = len(y)
        idx = set()
        for j in range(X.shape[1]):
            idx.add(int(np.argmin(X[:, j])))
            idx.add(int(np.argmax(X[:, j])))
        idx.add(int(np.argmin(y)))
        idx.add(int(np.argmax(y)))
        order = np.argsort(y, kind="stable")
        for q in np.linspace(0, n - 1, min(12, n)).astype(int):
            idx.add(int(order[q]))
        idx = sorted(idx)[:cap]
        rows = [[float(v) for v in X[i]] + [float(y[i])]
                for i in idx]
        return dict(rows=rows, n_source=int(n),
                    why="extremes + even spread by outcome rank")

    def recall_evidence(self, name):
        """The saved breakdown behind a law or series — what he
        remembers of the data that earned the structure."""
        for node in (f"law:{name}", f"series:{name}"):
            ev = self.net.get_meta(node, "evidence")
            if ev:
                return ev
        return None

    def context_sample(self, name, x, k=3):
        """Sampling FOR CONTEXT: the nearest remembered exemplars to
        a query point — 'what does it look like near here?' — from
        the facts layer, never the discarded raw."""
        ev = self.recall_evidence(name)
        if not ev or not ev.get("rows"):
            return None
        E = np.asarray(ev["rows"], float)
        Xe, ye = E[:, :-1], E[:, -1]
        x = np.asarray(x, float).reshape(-1)
        span = np.where(np.ptp(Xe, 0) > 1e-12, np.ptp(Xe, 0), 1.0)
        d = np.sqrt(((Xe - x) / span) ** 2).sum(1)
        near = np.argsort(d)[:k]
        return [dict(x=[float(v) for v in Xe[i]],
                     y=float(ye[i]), dist=round(float(d[i]), 4))
                for i in near]

    # ── THE DOSSIER (the specifics layer; owner 2026-07-18 evening:
    # "having the law is great, but sometimes you need to reference
    # a specific sample... averages, extremes, ratios, sigfigs, std
    # dev, median and mode... as well as time frames"). THE DESIGN
    # SENTENCE: THE DOSSIER DESCRIBES, THE COURT JUDGES — every
    # number here is a description with its method receipt; trend
    # VERDICTS, nulls, and belief stay the analyst court's. ──────

    @staticmethod
    def _fy_to_ymd(fy):
        """Fractional year -> (y, m, d), the exact inverse of the
        intake road's _fy (noon-of-day convention)."""
        import datetime as _dt
        y = int(np.floor(fy))
        days = _dt.date(y, 12, 31).timetuple().tm_yday
        doy = int(np.clip(np.round((fy - y) * days + 0.5), 1, days))
        d = _dt.date(y, 1, 1) + _dt.timedelta(days=doy - 1)
        return y, d.month, d.day

    def _column_stats(self, col, y, row_at):
        """One column's descriptive card. Every entry carries how it
        was measured; a mode with no recurring value REFUSES."""
        y = np.asarray(y, float)
        n = len(y)
        card = dict(n=n, mean=float(np.mean(y)),
                    median=float(np.median(y)),
                    lo=dict(value=float(y.min()),
                            row=row_at(int(np.argmin(y)))),
                    hi=dict(value=float(y.max()),
                            row=row_at(int(np.argmax(y)))))
        card["std"] = (dict(value=float(np.std(y, ddof=1)),
                            why="sample std (n-1)") if n > 1 else
                       dict(value=None, why="one row — no spread"))
        grain, g_why = self._floor_grain(y)
        if grain:
            step = grain["step"]
            # decimals = smallest k that round-trips the step
            # (0.25 -> 2, 2.5 -> 1, 5.0 -> 0; review find)
            decs = next(k for k in range(13)
                        if abs(round(step, k) - step)
                        <= 1e-9 * max(1.0, abs(step)))
            card["resolution"] = dict(
                step=float(step), consistency=grain["consistency"],
                decimals=int(decs),
                why="the grain court (storage resolution, lower "
                    "bound only)")
            snapped = np.round(y / step) * step
        else:
            card["resolution"] = dict(step=None, why=g_why)
            snapped = y
        vals, counts = np.unique(snapped, return_counts=True)
        top = int(counts.max())
        if top < 2:
            card["mode"] = dict(value=None,
                                why="no recurring value (all "
                                    "distinct at resolution)")
        else:
            tied = [float(v) for v in vals[counts == top]]
            card["mode"] = dict(value=tied[0], count=top,
                                ties=tied[:3] if len(tied) > 1
                                else None,
                                n_tied=len(tied),
                                why="most frequent at the grain's "
                                    "own resolution")
        return card

    @staticmethod
    def _ymd_to_fy(g):
        """(y, m, d) -> fractional year (the intake road's own
        convention, noon of day)."""
        import datetime as _dt
        y, mo, dd = g
        days = _dt.date(y, 12, 31).timetuple().tm_yday
        doy = _dt.date(y, mo, dd).timetuple().tm_yday
        return y + (doy - 0.5) / days

    def _frame_cards(self, ymd, V, vcols, cap=240):
        """Calendar frames: avg/lo/hi/n per bucket per column, plus
        a DESCRIBED slope (least squares over bucket averages —
        described, never judged; the court's verdict lives on the
        analyst road). The bucket time axis is the CALENDAR ITSELF
        (fractional years from ymd), never the caller's time column
        — so per_year is per year by construction (review find: a
        leading id column used to mislabel the slope's unit).
        Frames where aggregation would be identity (data already at
        that grain) are skipped WITH the receipt."""
        fy = np.array([self._ymd_to_fy(g) for g in ymd])
        frames = []
        for level, key, label in (
                ("year", lambda g: (g[0],), "{0:04d}"),
                ("month", lambda g: g[:2], "{0:04d}-{1:02d}"),
                ("day", lambda g: g[:3], "{0:04d}-{1:02d}-{2:02d}")):
            buckets = {}
            for i, g in enumerate(ymd):
                buckets.setdefault(key(g), []).append(i)
            ks = sorted(buckets)
            if len(ks) < 2:
                frames.append(dict(level=level, skipped="span too "
                                   "short (fewer than 2 buckets)"))
                continue
            if len(ks) == len(ymd):
                frames.append(dict(level=level,
                                   skipped="data already at this "
                                           "grain — averaging would "
                                           "change nothing"))
                continue
            total = len(ks)
            kept = ks[-cap:]
            rows = []
            for k in kept:
                idx = buckets[k]
                r = dict(bucket=label.format(*k), n=len(idx),
                         t=float(np.mean(fy[idx])), cols={})
                for j, c in vcols:
                    v = V[idx][:, j]
                    r["cols"][c] = dict(
                        avg=float(np.mean(v)), lo=float(v.min()),
                        hi=float(v.max()),
                        std=(float(np.std(v, ddof=1))
                             if len(v) > 1 else None))
                rows.append(r)
            fr = dict(level=level, buckets=rows, n_buckets=total)
            if total > cap:
                fr["capped"] = (f"kept the last {cap} of {total} "
                                f"buckets — a sample, never a hoard")
            if len(rows) >= 3:
                bt = np.array([r["t"] for r in rows])
                window = ("least squares over bucket averages"
                          if total <= cap else
                          f"least squares over the last {len(rows)}"
                          f" of {total} bucket averages")
                fr["slopes"] = {
                    c: dict(per_year=float(np.polyfit(
                        bt, np.array([r["cols"][c]["avg"]
                                      for r in rows]), 1)[0]),
                            buckets_used=len(rows),
                            buckets_total=total,
                            why=f"described, not judged — {window}")
                    for _j, c in vcols}
            frames.append(fr)
        return frames

    def take_dossier(self, columns, rows, name, time_index=None,
                     ymd=None, target=None, container=None,
                     provenance=None):
        """The specifics layer for a DATASET: descriptive cards per
        column (mean/median/mode/std/resolution, extremes WITH their
        rows), example rows via the facts-layer sampler, calendar
        frames, sign-safe ratio cards, and a taken-history so the
        trend LINE is tracked across re-takes. Net content: lands at
        dossier:<name>, container-stamped, pickled with his life."""
        R = np.asarray(rows, float)
        good = np.isfinite(R).all(1)
        R = R[good]
        if ymd is not None:
            ymd = [g for g, ok in zip(ymd, good) if ok]
        if len(R) < 3:
            return dict(refused=f"{len(R)} usable rows — a dossier "
                                f"needs at least 3")
        cols = list(columns)
        ti = time_index
        vcols = [(j, c) for j, c in enumerate(cols) if j != ti]
        if not vcols:
            return dict(refused="only the time column survived — a "
                                "dossier needs at least one value "
                                "column")
        if target is not None and (target not in cols
                                   or cols.index(target) == ti):
            return dict(refused=f"target '{target}' is the time "
                                f"column or not a column — value "
                                f"columns: {[c for _j, c in vcols]}")
        tgt = target if target in cols else vcols[-1][1]
        tj = cols.index(tgt)

        def row_at(i):
            return {c: float(R[i][j]) for j, c in enumerate(cols)}

        stats = {c: self._column_stats(c, R[:, j], row_at)
                 for j, c in vcols}
        examples = self._sample_evidence(
            np.delete(R, tj, axis=1), R[:, tj])
        examples["columns"] = [c for j, c in enumerate(cols)
                               if j != tj] + [tgt]
        examples["why"] += " (the facts-layer sampler, reused)"

        ratios = []
        pairs = [(a, b) for x, (a, _ca) in enumerate(vcols)
                 for (b, _cb) in vcols[x + 1:]]
        if len(vcols) > 6:
            pairs = [(a, b) for a, b in pairs
                     if tgt in (cols[a], cols[b])]
        for a, b in pairs:
            va, vb = R[:, a], R[:, b]
            pair = f"{cols[a]}/{cols[b]}"
            if np.all(vb > 0) or np.all(vb < 0):
                q = va / vb
                ratios.append(dict(
                    pair=pair, mean=float(np.mean(q)),
                    std=(float(np.std(q, ddof=1)) if len(q) > 1
                         else None),
                    lo=float(q.min()), hi=float(q.max())))
            else:
                ratios.append(dict(pair=pair, refused="denominator "
                              "crosses or touches zero — a ratio "
                              "there is a lie waiting"))
        if len(vcols) > 6:
            ratios.append(dict(note=f"{len(vcols)} value columns — "
                          f"ratio cards limited to pairs holding "
                          f"the target '{tgt}'"))

        if ymd is None and ti is not None:
            import re as _re
            tv = R[:, ti]
            # band alone cannot tell years from odometers (review
            # find): the column's NAME must also look calendar-like
            name_ok = bool(_re.search(
                r"(?i)year|date|time|epoch|^yr$|^t$|^fy$",
                str(cols[ti]).strip()))
            if (len(tv) and tv.min() >= 1000.0 and tv.max() <= 3000.0
                    and np.all(np.diff(tv) >= 0) and name_ok):
                ymd = [self._fy_to_ymd(v) for v in tv]
                cal_why = ("calendar derived from the year-valued "
                           f"time column '{cols[ti]}'")
            else:
                cal_why = None
        else:
            cal_why = "calendar told by the intake road" \
                if ymd is not None else None
        if ymd is not None:
            frames = self._frame_cards(ymd, R, vcols)
        else:
            frames = dict(refused="no calendar time (none told, "
                                  "none derivable — a year-band "
                                  "column also needs a calendar-"
                                  "sounding name) — frames refused; "
                                  "the stats stand")

        node = f"dossier:{name}"
        history = list(self.net.get_meta(node, "history") or [])
        # identity from the last entry, never the capped length
        # (review find: the cap froze the counter at 41)
        entry = dict(take=(history[-1]["take"] + 1) if history
                     else 1, n=int(len(R)),
                     target=tgt,
                     target_mean=stats[tgt]["mean"])
        if isinstance(frames, list):
            for fr in frames:
                for c, s in (fr.get("slopes") or {}).items():
                    if c == tgt:
                        entry[f"slope_per_year_{fr['level']}"] = \
                            s["per_year"]
        history.append(entry)
        if len(history) > 40:
            history = history[-40:]

        dossier = dict(node=node, name=name, n=int(len(R)),
                       columns=cols,
                       time=dict(column=(cols[ti] if ti is not None
                                         else None),
                                 calendar=cal_why),
                       target=tgt, stats=stats, examples=examples,
                       frames=frames, ratios=ratios,
                       history=history,
                       why="THE DOSSIER DESCRIBES, THE COURT JUDGES")
        for k in ("columns", "time", "target", "stats", "examples",
                  "frames", "ratios", "history"):
            self.net.set_meta(node, k, dossier[k])
        if provenance:
            self.net.set_meta(node, "provenance", dict(provenance))
            dossier["provenance"] = dict(provenance)
        elif self.net.get_meta(node, "provenance") is not None:
            # a re-take without provenance must not wear the old
            # stamp on new numbers (review find)
            self.net.set_meta(node, "provenance", None)
        c = container or getattr(self, "active_container", "base")
        self.net.add_door(f"world:{c}", node, tag=f"in:{c}")
        self.net.set_meta(node, "container", c)
        self.record_finding("dossier", name, n=int(len(R)),
                            target=tgt, take=entry["take"])
        return dossier

    def recall_dossier(self, name):
        """The saved specifics behind a dataset — what he can point
        at when the law alone is not the answer."""
        node = f"dossier:{name}"
        stats = self.net.get_meta(node, "stats")
        if not stats:
            return None
        out = dict(node=node, name=name, stats=stats)
        for k in ("columns", "time", "target", "examples", "frames",
                  "ratios", "history", "provenance", "container"):
            v = self.net.get_meta(node, k)
            if v is not None:
                out[k] = v
        return out

    # ── THE HARDER ROAD (the growing grammar, owner 2026-07-18) ──

    def _pool_fit(self, X, y, seed=13, width=32, ridge=1e-3):
        rng = np.random.default_rng(seed)
        Xs = (X - X.mean(0)) / np.where(X.std(0) > 1e-12, X.std(0), 1.0)
        W = rng.normal(0, 1, (X.shape[1], width))
        b = rng.normal(0, 1, width)
        H = np.tanh(Xs @ W + b)
        half = len(y) // 2
        A = H[:half]
        w = np.linalg.solve(A.T @ A + ridge * np.eye(width),
                            A.T @ y[:half])
        p = H[half:] @ w
        ss = float(np.sum((y[half:] - y[half:].mean()) ** 2))
        r2 = 1 - float(np.sum((y[half:] - p) ** 2)) / max(ss, 1e-12)
        return r2, (Xs, W, b, w, half)

    def _pool_scream(self, X, y, n_null=5):
        """Does structure exist AT ALL? The frozen lens (13-inch
        foot: uncalibrated, relationally honest) vs scrambled-y."""
        real, _ = self._pool_fit(X, y)
        rng = np.random.default_rng(7)
        nulls = []
        for _ in range(n_null):
            ys = y.copy()
            rng.shuffle(ys)
            r, _ = self._pool_fit(X, ys)
            nulls.append(r)
        return real, max(nulls), real > max(0.2, max(nulls) + 0.1)

    def _pool_aim(self, X, y):
        """WHERE does it live? Per-column permutation damage names
        the carriers — an informer, never a judge (the Fisher law)."""
        r2, (Xs, W, b, w, half) = self._pool_fit(X, y)
        rng = np.random.default_rng(11)
        drops = []
        for i in range(X.shape[1]):
            Xp = Xs.copy()
            col = Xp[half:, i].copy()
            rng.shuffle(col)
            Xp[half:, i] = col
            H = np.tanh(Xp @ W + b)
            p = H[half:] @ w
            ss = float(np.sum((y[half:] - y[half:].mean()) ** 2))
            r2p = 1 - float(np.sum((y[half:] - p) ** 2)) / max(ss, 1e-12)
            drops.append(r2 - r2p)
        top = max(drops) if drops else 0.0
        named = [i for i, d in enumerate(drops)
                 if d > 0.2 * top and d > 0.02]
        return named, [round(d, 3) for d in drops]

    _HARDER_GRID = [-3.0, -2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5,
                    2.0, 3.0]

    def _compose_candidates(self, X, y, named, top_k=8):
        """Novel coordinates: products of powers over the NAMED
        variables (nesting the combinator menu never did). Ranked by
        LOG-ruler correlation when signs allow — leverage dies under
        the log — as an INFORMER only; the court judges. Proportional
        exponent vectors are deduped sign-fixed (any representative
        closes at court: the enumerator holds powers of the column)."""
        import itertools
        half = len(y) // 2
        logroad = bool(np.all(np.abs(y[:half]) > 1e-12))
        ly = np.log(np.abs(y[:half])) if logroad else None
        seen = {}
        for exps in itertools.product(self._HARDER_GRID + [0.0],
                                      repeat=len(named)):
            if all(e == 0.0 for e in exps) or all(e <= 0 for e in exps):
                continue
            first = next(e for e in exps if e)
            if first < 0:
                exps = tuple(-e for e in exps)   # sign-fixed canonical
            with np.errstate(all="ignore"):
                c = np.ones(len(y))
                for v, e in zip(named, exps):
                    if e:
                        c = c * np.power(np.abs(X[:, v]), e)
            if not np.isfinite(c).all() or c[:half].std() < 1e-12:
                continue
            if logroad and np.all(np.abs(c[:half]) > 1e-12):
                lc = np.log(np.abs(c[:half]))
                r = abs(float(np.corrcoef(lc, ly)[0, 1])) \
                    if lc.std() > 1e-12 else 0.0
            else:
                r = abs(float(np.corrcoef(c[:half], y[:half])[0, 1]))
            if np.isfinite(r) and (exps not in seen
                                   or r > seen[exps][0]):
                seen[exps] = (r, c)
        cands = [(r, e, c) for e, (r, c) in seen.items()]
        cands.sort(key=lambda t: (
            -round(t[0], 6),
            sum(1 for e in t[1] if e != int(e)),
            sum(abs(e) for e in t[1])))
        return cands[:top_k]

    def discover_harder(self, X, y, name=None, container=None,
                        effort=1):
        """THE HARDER ROAD (owner, 2026-07-18: "we need isaac to be
        able to work harder on problems and look for novel solutions,
        not just the ones we programmed") — the genesis loop pointed
        at algebra. Plain discover first (the earned vocabulary is
        already offered there); if the verdict is dark: SCREAM (does
        the residual have structure at all? no scream = no dig, with
        a receipt; small tables skip the aim and dig everywhere —
        the court still judges), AIM (ablation names the carriers),
        EXPERIMENT (composed coordinates over the named variables),
        THE COURT UNCHANGED (every candidate faces ordinary discover
        — the search widens, the court never loosens), MINT + GROW
        (the winner registers as a powerprod composite and is offered
        to every future problem). A qualifying PARTIAL through the
        composed coordinate registers the ENABLER and keeps belief
        honest: the form is said, the residual stays dark, and a
        PARTIAL law never crystallizes (the tooth). Receipts ride on
        the result under 'harder' (consideration law)."""
        X = np.asarray(X, float)
        y = np.asarray(y, float)
        rec = dict(road="", tried=0, bypassed=[])
        res = self.discover(X, y, name=name, container=container)
        if res["verdict"] == "UNDERSTOOD":
            rec["road"] = "plain road (earned vocabulary included)"
            res["harder"] = rec
            return res
        d = X.shape[1]
        if len(y) >= 24:
            real, nullmax, scream = self._pool_scream(X, y)
            rec["scream"] = [round(real, 3), round(nullmax, 3)]
            if not scream:
                rec["bypassed"].append("no scream — nothing to dig "
                                       "for")
                res["harder"] = rec
                return res
            named, drops = self._pool_aim(X, y)
            rec["named"], rec["drops"] = named, drops
            if not named:
                rec["bypassed"].append("scream but no named carrier")
                res["harder"] = rec
                return res
        else:
            named = list(range(d))
            rec["named"] = named
            rec["road"] = ("small table — dug everywhere with a "
                           "receipt; the court decides")
        named = named[:3]
        best, best_partial = None, None
        for r, exps, c in self._compose_candidates(
                X, y, named, top_k=8 * max(1, int(effort))):
            rec["tried"] += 1
            trial = self.discover(np.column_stack([X, c]), y)
            if trial["verdict"] == "UNDERSTOOD":
                best = exps
                break
            if (trial["verdict"] == "PARTIAL"
                    and f"x{d}" in trial.get("equation", "")
                    and trial["r2"] > max(res["r2"] + 0.1, 0.99)
                    and (best_partial is None
                         or trial["r2"] > best_partial[1])):
                best_partial = (exps, trial["r2"])
        if best is None and best_partial is None:
            rec["bypassed"].append("no composition survived the "
                                   "court")
            res["harder"] = rec
            return res
        exps = best if best is not None else best_partial[0]
        cname = self.register_composite(
            "powerprod", list(named), exps=list(exps),
            provenance=("harder road: courted UNDERSTOOD"
                        if best is not None else
                        "harder road: form-said enabler "
                        "(uncertified — belief stays the court's)"))
        final = self.discover(X, y, name=name, container=container)
        rec["mint"] = cname
        rec["road"] = ("novel coordinate courted UNDERSTOOD; the "
                       "vocabulary grew" if best is not None else
                       "form said through the composed coordinate; "
                       "belief stays PARTIAL (residual above floor, "
                       "kept dark, kept honest)")
        final["harder"] = rec
        return final

    # ── THE TREND ROAD (the analyst segment, owner 2026-07-18) ──

    def analyze_series(self, t, y, name=None, container=None,
                       max_period=None):
        """THE TREND ROAD (the analyst segment, owner 2026-07-18: a
        trend line "is just one job that a data analyst would do").
        A time series decomposed with receipts, nothing assumed:
        TREND by the ordinary discover vocabulary (changepoints come
        free — the switch atoms fire on time like any column; a
        refusal means flat, said so); PERIOD by autocorrelation past
        a shuffle null, sharpened by parabolic refine (bracket+refine
        law — never a preset frequency menu); the SEASONAL PROFILE
        is FOLDED AND LEARNED (per-phase offsets — a shape, never a
        forced sinusoid), admitted only past its own shuffle null;
        ACCOUNTING is complete: trend% + seasonal% + residual% = 100.
        The residual stays honestly dark (an amplitude-varying cycle
        says its period and keeps its amplitude variation as named
        leftover). The series lands in its own container (the
        per-dataset default); apply_series() forecasts from it."""
        t = np.asarray(t, float)
        y = np.asarray(y, float)
        o = np.argsort(t)
        t, y = t[o], y[o]
        n = len(y)
        rec = dict(bypassed=[])
        c = container
        if c is None:
            active = getattr(self, "active_container", "base")
            c = active if active != "base" else \
                (f"data-{name}" if name else "base")
        step = float(np.median(np.diff(t))) or 1.0
        # 1) PERIOD FIRST, on the DIFFERENCED series — differencing
        # kills trend and keeps cycles, so the trend fit can never
        # eat the cycle before it is measured (run-1 lesson)
        period, prof, nbins, r2_seas = None, None, 0, 0.0
        bins_all = None
        dy = np.diff(y)
        # spike-proof detection (the face's lesson): heavy outliers
        # hijack the differenced autocorrelation — clip at 5 robust
        # sigmas FOR DETECTION ONLY (informer, never judge; the
        # profile and accounting still see the real data)
        med_d = float(np.median(dy))
        mad_d = float(np.median(np.abs(dy - med_d))) * 1.4826
        if mad_d > 1e-12:
            lo_c, hi_c = med_d - 5 * mad_d, med_d + 5 * mad_d
            n_clip = int(np.sum((dy < lo_c) | (dy > hi_c)))
            if n_clip:
                dy = np.clip(dy, lo_c, hi_c)
                rec["detection_clip"] = n_clip
        maxlag = int(min(n // 3, max_period or n // 3))
        if maxlag >= 3 and dy.std() > 1e-12:
            def _ac(sig, lag):
                a, b = sig[:-lag], sig[lag:]
                if a.std() < 1e-12 or b.std() < 1e-12:
                    return 0.0
                return float(np.corrcoef(a, b)[0, 1])
            acs = [_ac(dy, L) for L in range(2, maxlag + 1)]
            rng = np.random.default_rng(17)
            nullmax = 0.0
            for _ in range(20):
                ds = dy.copy()
                rng.shuffle(ds)
                nullmax = max(nullmax, max(abs(_ac(ds, L))
                                           for L in range(2, maxlag + 1)))
            # THE FUNDAMENTAL RULE (run-2 lesson): a cycle's autocorr
            # is equally tall at every multiple of its period, and
            # argmax wanders to harmonics. Candidates = local peaks
            # past the null; among those within 90% of the tallest,
            # the SMALLEST lag is the fundamental.
            cands = [i for i in range(len(acs))
                     if acs[i] > nullmax
                     and (i == 0 or acs[i] >= acs[i - 1])
                     and (i == len(acs) - 1 or acs[i] >= acs[i + 1])]
            if cands:
                # v2 (the face's lesson): among harmonics, finite-
                # sample luck can make a MULTIPLE the tallest peak —
                # the fundamental is the smallest past-null peak that
                # DIVIDES the tallest (integer ratio) at >=60% of its
                # height; unrelated small peaks cannot steal the seat
                top = max(cands, key=lambda i: acs[i])
                best = top
                for i in sorted(cands):
                    ratio = (top + 2) / (i + 2)
                    if (acs[i] >= 0.6 * acs[top]
                            and abs(ratio - round(ratio)) <= 0.15):
                        best = i
                        break
                # parabolic refine around the integer peak
                if 0 < best < len(acs) - 1:
                    y0, y1, y2 = acs[best - 1], acs[best], acs[best + 1]
                    den = (y0 - 2 * y1 + y2)
                    off = 0.5 * (y0 - y2) / den if abs(den) > 1e-12 \
                        else 0.0
                    off = float(np.clip(off, -0.5, 0.5))
                else:
                    off = 0.0
                period = (best + 2 + off) * step
                rec["period_ac"] = round(acs[best], 3)
                rec["period_null"] = round(nullmax, 3)
            else:
                best = int(np.argmax(acs))
                rec["bypassed"].append(
                    f"period: best autocorr {acs[best]:.2f} <= null "
                    f"{nullmax:.2f} — no cycle said")
        # 2) THE PROFILE — folded on a moving-average detrend (the
        # scaffold never ships: the trend LAW is fit afterward),
        # admitted only past its own shuffle null
        if period is not None:
            w = int(max(2, round(period / step)))
            ma = np.convolve(y, np.ones(w) / w, mode="same")
            half_w = w // 2
            core = slice(half_w, n - half_w)
            d0 = (y - ma)[core]
            tc = t[core]
            nbins = int(max(4, min(24, round(period / step))))
            phase = ((tc - t[0]) % period) / period
            bins = np.minimum((phase * nbins).astype(int), nbins - 1)
            prof = np.array([d0[bins == k].mean()
                             if np.any(bins == k) else 0.0
                             for k in range(nbins)])
            prof = prof - prof.mean()
            sfit = prof[bins]
            r2_seas = 1 - float(np.sum((d0 - sfit) ** 2)) \
                / max(float(np.sum((d0 - d0.mean()) ** 2)), 1e-12)
            rng = np.random.default_rng(19)
            null_seas = 0.0
            for _ in range(20):
                ds = d0.copy()
                rng.shuffle(ds)
                pn = np.array([ds[bins == k].mean()
                               if np.any(bins == k) else 0.0
                               for k in range(nbins)])
                rn = 1 - float(np.sum((ds - pn[bins]) ** 2)) \
                    / max(float(np.sum((ds - ds.mean()) ** 2)), 1e-12)
                null_seas = max(null_seas, rn)
            rec["seasonal_null"] = round(null_seas, 3)
            if r2_seas <= null_seas:
                rec["bypassed"].append(
                    f"profile: explains {r2_seas:.2f} <= null "
                    f"{null_seas:.2f} — period said, shape refused")
                prof, r2_seas, nbins = None, 0.0, 0
            else:
                phase_all = ((t - t[0]) % period) / period
                bins_all = np.minimum((phase_all * nbins).astype(int),
                                      nbins - 1)
        # 3) THE TREND LAW on the seasonally-adjusted series (lags of
        # a time index are affine clones of it — never proposed here)
        y_adj = y - (prof[bins_all] if prof is not None else 0.0)
        trend_name = f"{name}-trend" if name else None
        # the time axis is CENTERED for the trend fit (the relative-
        # space law: an epoch offset is one factor applied last —
        # raw calendar dates at large offsets cost extrapolation
        # precision, the face's second lesson)
        tc0 = (t - t[0]).reshape(-1, 1)
        tr = self.discover(tc0, y_adj, name=trend_name,
                           container=c, use_lags=False)
        trend_pred = None
        if trend_name and tr["verdict"] in ("UNDERSTOOD", "PARTIAL"):
            trend_pred = self.apply_law(trend_name, tc0)
        if trend_pred is None:
            trend_pred = np.full(n, float(y_adj.mean()))
            rec["bypassed"].append(
                f"trend: {tr['verdict']} — flat (mean) stands, said")
        # 4) COMPLETE ACCOUNTING — trend + seasonal + residual = 100
        var_y = max(float(np.var(y)), 1e-12)
        after_t = float(np.var(y - trend_pred))
        after_ts = float(np.var(y - trend_pred
                                - (prof[bins_all] if prof is not None
                                   else 0.0)))
        p_trend = 100.0 * (1 - after_t / var_y)
        p_seas = 100.0 * (after_t - after_ts) / var_y
        p_resid = 100.0 - p_trend - p_seas
        accounting = dict(trend=round(p_trend, 1),
                          seasonal=round(p_seas, 1),
                          residual=round(p_resid, 1))
        out = dict(trend_verdict=tr["verdict"],
                   trend_equation=tr.get("equation"),
                   period=(round(period, 4) if period else None),
                   profile=(None if prof is None else
                            [round(v, 4) for v in prof]),
                   nbins=(nbins if prof is not None else 0),
                   accounting=accounting, receipts=rec,
                   container=c)
        if name:
            node = f"series:{name}"
            self.net.add_door("series", node, tag="series")
            self.net.add_door(f"world:{c}", node, tag=f"in:{c}")
            self.net.set_meta(node, "series", dict(
                trend_law=trend_name, period=out["period"],
                profile=out["profile"], nbins=out["nbins"],
                t0=float(t[0]), accounting=accounting,
                container=c, receipts=rec))
            # the facts layer: remembered points + the largest
            # leftovers (the residual's own witnesses)
            ev = self._sample_evidence(t.reshape(-1, 1), y)
            resid = y - trend_pred
            worst = np.argsort(-np.abs(resid))[:3]
            ev["leftovers"] = [dict(t=float(t[i]), y=float(y[i]),
                                    resid=round(float(resid[i]), 4))
                               for i in worst]
            self.net.set_meta(node, "evidence", ev)
            self.record_finding("series", name, period=out["period"],
                                accounting=accounting,
                                trend=tr.get("equation"))
        return out

    def apply_series(self, name, t_new):
        """Forecast from an analyzed series: trend law + the learned
        seasonal profile at each time's phase. Honest scope: the
        trend law's own range labels apply; no series = None."""
        s = self.net.get_meta(f"series:{name}", "series")
        if not s:
            return None
        t_new = np.asarray(t_new, float)
        if s["trend_law"] and self.net.get_meta(
                f"law:{s['trend_law']}", "model"):
            base = self.apply_law(s["trend_law"],
                                  (t_new - s["t0"]).reshape(-1, 1))
        else:
            base = np.zeros(len(t_new))
        if base is None:
            return None
        if s["period"] and s["profile"]:
            phase = ((t_new - s["t0"]) % s["period"]) / s["period"]
            bins = np.minimum((phase * s["nbins"]).astype(int),
                              s["nbins"] - 1)
            base = base + np.asarray(s["profile"])[bins]
        return base

    def relate_series(self, ta, ya, tb, yb, name=None,
                      containers=None, max_shift=5):
        """CROSS-CONTAINER CORRELATION (A2 of the analyst segment;
        the triangulation thread built — owner 2026-07-12: two
        datasets as "halves of the same whole", owner 2026-07-18:
        "finding correlations between different things"). Two series
        aligned on their shared key (the overlap window; B
        interpolated onto A's points), then judged on DIFFERENCES —
        levels co-move trivially when both trend (the spurious-
        correlation trap), so level correlation is REPORTED with
        that receipt but never judged; the differenced correlation
        is scanned across lead/lag shifts and faces THE ALIGNMENT
        NULL: circular shifts of B preserve each side's internal
        structure and destroy only the true pairing — a real
        relation dies when alignment does, a spurious one survives
        it. Verdict RELATED (sign, strength, who leads) or NO
        RELATION SAID. A RELATED pair mints a relation:<name> node
        doored to both worlds (the meaningful-doors design: the
        relationship as a first-class thing)."""
        ta = np.asarray(ta, float)
        ya = np.asarray(ya, float)
        tb = np.asarray(tb, float)
        yb = np.asarray(yb, float)
        rec = dict(bypassed=[])
        lo, hi = max(ta.min(), tb.min()), min(ta.max(), tb.max())
        keep = (ta >= lo) & (ta <= hi)
        if keep.sum() < 12:
            rec["bypassed"].append(
                f"overlap {int(keep.sum())} points < 12 — refused")
            return dict(verdict="NO RELATION SAID", receipts=rec)
        t = ta[keep]
        a = ya[keep]
        b = np.interp(t, tb, yb)
        levels = float(np.corrcoef(a, b)[0, 1])
        da, db = np.diff(a), np.diff(b)
        n = len(da)
        if da.std() < 1e-12 or db.std() < 1e-12:
            rec["bypassed"].append("a flat side — nothing to relate")
            return dict(verdict="NO RELATION SAID", receipts=rec)

        def _c(x, z):
            if x.std() < 1e-12 or z.std() < 1e-12:
                return 0.0
            return float(np.corrcoef(x, z)[0, 1])

        best_s, best_r = 0, _c(da, db)
        for s in range(1, max_shift + 1):
            r1 = _c(da[s:], db[:-s])       # b leads a by s
            r2 = _c(da[:-s], db[s:])       # a leads b by s
            if abs(r1) > abs(best_r):
                best_s, best_r = s, r1
            if abs(r2) > abs(best_r):
                best_s, best_r = -s, r2
        rng = np.random.default_rng(23)
        offsets = rng.choice(np.arange(max_shift + 3,
                                       n - max_shift - 3),
                             size=min(40, max(8, n // 4)),
                             replace=False)
        nullmax = 0.0
        for k in offsets:
            dbr = np.roll(db, int(k))
            m = max(abs(_c(da, dbr)),
                    max(abs(_c(da[s:], dbr[:-s]))
                        for s in range(1, max_shift + 1)))
            nullmax = max(nullmax, m)
        rec["levels_corr"] = round(levels, 3)
        rec["levels_receipt"] = ("levels co-move trivially under "
                                 "shared trends — reported, never "
                                 "judged")
        rec["null"] = round(nullmax, 3)
        related = abs(best_r) > nullmax
        leader = ("b" if best_s > 0 else "a") if best_s else "none"
        out = dict(verdict=("RELATED" if related
                            else "NO RELATION SAID"),
                   corr=round(best_r, 3), shift=abs(best_s),
                   leader=leader, n=n, levels=round(levels, 3),
                   receipts=rec)
        if related and name:
            node = f"relation:{name}"
            self.net.add_door("relations", node, tag="relation")
            for c in (containers or []):
                self.net.add_door(f"world:{c}", node, tag=f"in:{c}")
            self.net.set_meta(node, "relation", dict(
                corr=out["corr"], shift=out["shift"],
                leader=leader, n=n, null=rec["null"],
                levels=rec["levels_corr"],
                containers=list(containers or [])))
            self.record_finding("relation", name, corr=out["corr"],
                                shift=out["shift"], leader=leader,
                                n=n, null=rec["null"])
        return out

    def _watch_judge(self, node, kind, err_norm, n):
        """The watch's shared court: the FIRST batch establishes the
        baseline (a receipt, never a judgment); after that, a batch
        drifts when its normalized error exceeds max(2.5x the median
        of confirmed history, 0.005) — v1 hand-set constants, filed
        as such (the known-limits discipline). The watch learns its
        own normal from its own measurements (the 13-inch foot: the
        instrument earns its consistency)."""
        hist = self.net.get_meta(node, kind) or []
        if not hist:
            verdict = "BASELINE"
        else:
            med = float(np.median([h["err"] for h in hist
                                   if h["verdict"] != "DRIFT"] or [0]))
            verdict = "DRIFT" if err_norm > max(2.5 * med, 0.005) \
                else "CONFIRMED"
        hist.append(dict(err=round(float(err_norm), 6), n=int(n),
                         verdict=verdict,
                         stamp=time.strftime("%Y-%m-%d %H:%M:%S")))
        self.net.set_meta(node, kind, hist)
        return verdict, hist

    def watch(self, name, X_new, y_new):
        """THE WATCH (A3 of the analyst segment; owner 2026-07-18:
        "trends and tracking of long term things"). New data arrives
        at a law's world and the law DEFENDS ITS SEAT: predictions
        vs actuals, error normalized by the batch's own scale,
        judged against the watch's accumulated normal. CONFIRMED
        batches are witnesses (belief grows the ordinary way); DRIFT
        is flagged with receipts and the incumbent immediately faces
        the SUPERSESSION DUEL on the new data — winner active, loser
        kept wearing its numbers. Every check appends to the node's
        watch history: long-term tracking as first-class knowledge."""
        node = f"law:{name}"
        if self.net.get_meta(node, "model") is None:
            return None
        X_new = np.asarray(X_new, float)
        y_new = np.asarray(y_new, float)
        p = self.apply_law(name, X_new)
        if p is None:
            return dict(verdict="UNCHECKABLE",
                        why="law does not apply to these columns")
        err = float(np.sqrt(np.mean((y_new - p) ** 2)))
        scale = max(float(np.sqrt(np.mean(y_new ** 2))), 1e-12)
        verdict, hist = self._watch_judge(node, "watch",
                                          err / scale, len(y_new))
        out = dict(verdict=verdict, err=round(err, 6),
                   err_norm=round(err / scale, 6), n=len(y_new),
                   checks=len(hist))
        if verdict == "DRIFT":
            # THE REPLAY COURT (the facts layer's win): the drift
            # duel runs on remembered evidence + the new batch — the
            # incumbent's world is REPRESENTED in the court that may
            # unseat it, no fresh-data dependence for history
            ev = self.net.get_meta(node, "evidence")
            if ev and ev.get("rows"):
                E = np.asarray(ev["rows"], float)
                Xd = np.vstack([E[:, :-1], X_new])
                yd = np.concatenate([E[:, -1], y_new])
            else:
                Xd, yd = X_new, y_new
            duel = self.supersession_duel(name, Xd, yd)
            out["duel"] = (duel.get("verdict") if duel else None)
            out["duel_court"] = (f"{len(yd) - len(y_new)} remembered "
                                 f"+ {len(y_new)} new rows")
        self.record_finding("watch", name, verdict=verdict,
                            err_norm=out["err_norm"], n=len(y_new),
                            duel=out.get("duel"))
        return out

    def watch_series(self, name, t_new, y_new):
        """The watch for an analyzed series: the standing forecast
        (trend law + learned profile) meets the arriving months;
        same court, same receipts, same history on the node."""
        node = f"series:{name}"
        if self.net.get_meta(node, "series") is None:
            return None
        t_new = np.asarray(t_new, float)
        y_new = np.asarray(y_new, float)
        p = self.apply_series(name, t_new)
        if p is None:
            return dict(verdict="UNCHECKABLE",
                        why="series does not apply")
        err = float(np.sqrt(np.mean((y_new - p) ** 2)))
        scale = max(float(np.sqrt(np.mean(y_new ** 2))), 1e-12)
        verdict, hist = self._watch_judge(node, "watch",
                                          err / scale, len(y_new))
        out = dict(verdict=verdict, err=round(err, 6),
                   err_norm=round(err / scale, 6), n=len(y_new),
                   checks=len(hist))
        self.record_finding("watch_series", name, verdict=verdict,
                            err_norm=out["err_norm"], n=len(y_new))
        return out

    def apply_law(self, name, X):
        """Apply a discovered law: the challenge, now computable.
        (Distinct from solve(), the token-problem solver.) A law with
        lag columns reads rows as consecutive samples; its first
        max-lag rows have no history and return NaN — per-row
        refusals, never guesses."""
        m = self.net.get_meta(f"law:{name}", "model")
        d_raw = (m or {}).get("d_raw", (m or {}).get("d"))
        if m is None or np.asarray(X).shape[1] != d_raw:
            return None
        X = self._augment_with(np.asarray(X, float),
                               m.get("composites_used", []))
        lu = m.get("lags_used", [])
        if lu:
            X = np.column_stack([X, self._lag_columns(X[:, :d_raw], lu)])
        used = sorted({a for t in m["terms"] for a in t})
        cols = {a: _atom_col(X, m["specs"][a]) for a in used}
        D = np.column_stack(
            [np.prod([cols[a] for a in t], axis=0) for t in m["terms"]]
            + [np.ones(len(X))])
        return D @ np.concatenate([m["coefs"], [m["intercept"]]])

    # Extrapolation survival of form-true claims, MEASURED (2026-07-03,
    # experiments/confidence_curve.py — 100-world externally graded audit;
    # re-measure whenever the enumerator changes). Keys are hull-exceedance
    # distances in units of the observed span; values are observed hold
    # rates. This is a calibrated prior, not an opinion.
    DECAY_MEASURED = {0.0: 0.765, 0.1: 0.588, 0.3: 0.451,
                      0.6: 0.431, 1.0: 0.353}
    # (measured 2026-07-03 on 51 externally-graded laws; validated on 52
    # FRESH laws: ECE 0.070, Brier 0.249 vs flat-baseline 0.288.
    # RE-MEASURED 2026-07-04 after the block-permutation null joined the
    # enumerator: curve unchanged within noise except the far point
    # (1.0: 0.373 → 0.353); validation on 60 fresh worlds ECE 0.079,
    # Brier 0.255 vs flat 0.284 — the profile stands.)

    def law_confidence(self, name, X, decay=None):
        """GRADED BELIEF instead of a binary scope stamp (owner's design,
        2026-07-03: 'maybe just a boundary confidence? what about
        extrapolated confidence?'). Per query point:
          - inside the observed hull -> the law's boundary confidence
            (held-out edge R2, clamped to [0,1])
          - beyond the hull -> boundary confidence x the MEASURED survival
            curve of claims like this one, interpolated at the point's
            hull-exceedance distance (in units of the observed span).
        Returns an array of per-point confidences. Honest by construction:
        the decay is what actually happened to extrapolating laws in the
        externally-graded audit, not an assertion."""
        m = self.net.get_meta(f"law:{name}", "model")
        if m is None or "ranges" not in m:
            return None
        X = self._augment_with(np.asarray(X, float),
                               m.get("composites_used", []))
        lu = m.get("lags_used", [])
        ranges = m["ranges"]
        if lu:
            # only lag columns the law's admitted terms actually USE
            # bind confidence: a proposed-but-unused lag must not
            # demand history. Used-and-missing history -> NaN conf
            # (an honest per-row refusal).
            d_raw = int(m.get("d_raw", X.shape[1]))
            X = np.column_stack([X, self._lag_columns(X[:, :d_raw], lu)])
            used = {m["specs"][a][1] for t in m["terms"] for a in t}
            used |= {m["specs"][a][2] for t in m["terms"] for a in t
                     if m["specs"][a][2] is not None}
            n_base = X.shape[1] - len(lu)
            keep = [c for c in range(X.shape[1])
                    if c < n_base or c in used]
            X = X[:, keep]
            ranges = [m["ranges"][c] for c in keep]
        lo = np.array([r[0] for r in ranges])
        hi = np.array([r[1] for r in ranges])
        span = np.maximum(hi - lo, 1e-12)
        exceed = np.maximum(np.maximum(lo - X, X - hi), 0.0) / span
        delta = exceed.max(axis=1)                    # hull distance / span
        curve = decay if decay is not None else {
            k: v for k, v in self.DECAY_MEASURED.items() if v is not None}
        boundary = float(np.clip(m.get("r2_edge", m.get("r2", 0.0)), 0, 1))
        if not curve:
            return np.where(delta <= 0, boundary, np.nan)
        ks = np.array(sorted(curve))
        vs = np.array([curve[k] for k in ks])
        surv = np.interp(delta, ks, vs, left=vs[0], right=vs[-1])
        conf = np.where(delta <= 0, boundary, boundary * surv)
        return conf

    def _fit_terms(self, specs, terms, X, y):
        """Least-squares refit of a term set; returns (coefs, intercept,
        predictions_fn ingredients). Shared by pruning and refinement."""
        used = sorted({a for t in terms for a in t})
        cols = {a: _atom_col(X, specs[a]) for a in used}
        D = np.column_stack([np.prod([cols[a] for a in t], axis=0)
                             for t in terms] + [np.ones(len(X))])
        beta, *_ = np.linalg.lstsq(D, y, rcond=None)
        pred = D @ beta
        sse = float(np.sum((y - pred) ** 2))
        return list(beta[:-1]), float(beta[-1]), sse

    def _prune_terms(self, m, X, y, f_thr=10.0):
        """OCCAM'S RAZOR as an operation (owner's law, 2026-07-03: 'simpler
        with the same accuracy or better is better'). Greedily drop any
        term whose removal survives an F-test tie on held-out data — a
        genuine tie goes to the simpler form. Returns (terms, coefs,
        intercept, n_dropped)."""
        half = len(y) // 2
        terms = list(m["terms"])
        specs = list(m["specs"])
        coefs, intercept, _ = self._fit_terms(specs, terms, X[:half],
                                              y[:half])

        def held_sse(ts):
            c, b, _ = self._fit_terms(specs, ts, X[:half], y[:half])
            used = sorted({a for t in ts for a in t})
            cols = {a: _atom_col(X[half:], specs[a]) for a in used}
            D = np.column_stack([np.prod([cols[a] for a in t], axis=0)
                                 for t in ts] + [np.ones(len(y) - half)])
            p = D @ np.concatenate([c, [b]])
            return float(np.sum((y[half:] - p) ** 2)), c, b

        sse_full, coefs, intercept = held_sse(terms)
        dropped = 0
        changed = True
        while changed and len(terms) > 1:
            changed = False
            for k in range(len(terms)):
                trial = terms[:k] + terms[k + 1:]
                sse_t, c_t, b_t = held_sse(trial)
                F = (max(sse_t - sse_full, 0.0)) \
                    / max(sse_full / max(len(y) - half, 1), 1e-30)
                if F < f_thr:                     # tie -> simpler wins
                    terms, coefs, intercept = trial, c_t, b_t
                    sse_full = sse_t
                    dropped += 1
                    changed = True
                    break
        return terms, coefs, intercept, dropped

    def refine(self, name, X, y, ask=None, budget=60, rounds=3,
               verbose=False):
        """THE CORRECTION LOOP (owner's design, 2026-07-03: 'it has an
        indicator it can use as a correction signal... recalculate and
        experiment with different information to refine'). The confidence
        curve stops being a dashboard and becomes a steering signal:

          1. find the law's WEAKEST region (lowest extrapolated confidence)
          2. EXPERIMENT exactly there (ask(X)->y — the oracle/instrument),
             spending a budget
          3. re-derive on everything now known
          4. PREFER what is better — or equally good and simpler (Occam
             as a preference, not a gate; same F-test that judges rivals)
          5. the displaced law is SUPERSEDED with the why; a candidate
             that is not preferred is RETAINED as an alternative —
             nothing is rejected into nothing

        Ends with an Occam prune either way. Returns a report dict."""
        node = f"law:{name}"
        m = self.net.get_meta(node, "model")
        if m is None:
            return None
        if m.get("lags_used"):
            # a lag law lives on a SERIES: refine's probe road asks an
            # oracle at points, and a lagged value is not a free axis
            # you can set. Refusal is the answer — extend the series
            # and re-discover instead.
            return dict(rounds=[], accepted=0, spent=0,
                        refused="lag law: probing points cannot set a "
                                "lagged value; extend the series and "
                                "re-discover")
        X = np.asarray(X, float); y = np.asarray(y, float)
        comps_m = m.get("composites_used", [])
        d_raw_m = int(m.get("d_raw", X.shape[1]))
        pool_X, pool_y = X.copy(), y.copy()      # pool stays RAW; the
        spent = 0                                 # instrument speaks raw
        report = dict(rounds=[], accepted=0, spent=0)

        def complexity(mm):
            return (len(mm["terms"]),
                    sum(len(t) for t in mm["terms"]))

        def held_sse_of(mm, Xh, yh):
            used = sorted({a for t in mm["terms"] for a in t})
            cols = {a: _atom_col(Xh, mm["specs"][a]) for a in used}
            D = np.column_stack([np.prod([cols[a] for a in t], axis=0)
                                 for t in mm["terms"]]
                                + [np.ones(len(Xh))])
            p = D @ np.concatenate([mm["coefs"], [mm["intercept"]]])
            return float(np.sum((yh - p) ** 2))

        for rd in range(rounds):
            if ask is None or spent >= budget:
                break
            m = self.net.get_meta(node, "model")
            lo = np.array([r[0] for r in m["ranges"]])[:d_raw_m]
            hi = np.array([r[1] for r in m["ranges"]])[:d_raw_m]
            span = np.maximum(hi - lo, 1e-12)
            # 1. weakest region: candidate probes fan out past the hull;
            #    the confidence signal picks where belief is thinnest
            cand = np.vstack([
                lo + _wave_rng.uniform(-1.0, 1.4, (300, len(lo))) * span])
            conf = self.law_confidence(name, cand)
            b = max(min(budget - spent, budget // rounds), 8)
            weakest = cand[np.argsort(conf)[:b]]
            # 2. experiment there (an instrument can fail — a probe outside
            # a law's physical support returns nothing; keep only finite
            # answers, red-team A8 discipline)
            y_new = np.asarray(ask(weakest), float)
            spent += b
            fin = np.isfinite(y_new) & np.isfinite(weakest).all(1)
            weakest, y_new = weakest[fin], y_new[fin]
            if not len(y_new):
                report["rounds"].append("all probes returned non-finite")
                continue
            pool_X = np.vstack([pool_X, weakest])
            pool_y = np.concatenate([pool_y, y_new])
            sh = _wave_rng.permutation(len(pool_y))
            pool_X, pool_y = pool_X[sh], pool_y[sh]
            # 3. re-derive on everything known (fits see the augmented
            # basis: learned combinations are columns here too)
            poolA = self._augment_with(pool_X, comps_m)
            enum = _Enumerator()
            half = len(pool_y) // 2
            enum.fit(poolA[:half], pool_y[:half])
            cand_m = dict(terms=list(enum.terms), coefs=enum.coefs,
                          intercept=enum.intercept, specs=list(enum.specs))
            if not cand_m["terms"]:
                report["rounds"].append("no candidate")
                continue
            # 4. the Occam gate: judged on the held half of the pool
            sse_old = held_sse_of(m, poolA[half:], pool_y[half:])
            sse_new = held_sse_of(cand_m, poolA[half:], pool_y[half:])
            n_h = len(pool_y) - half
            F = (sse_old - sse_new) / max(min(sse_old, sse_new) / n_h, 1e-30)
            better = F > 10.0 and sse_new < sse_old
            tie_simpler = abs(F) <= 10.0 and \
                complexity(cand_m) < complexity(m)
            # OCCAM IS A PREFERENCE, NOT A GATE (owner, 2026-07-03: "its
            # not only. its just preferred."). Accuracy decides; at ties
            # the simpler form is PREFERRED for use — and the
            # non-preferred candidate is RETAINED as an alternative, not
            # discarded. Nothing is rejected into nothing.
            if better or tie_simpler:
                old_eq = self.net.get_meta(node, "equation")
                why = (f"refined with {b} experiments in the weakest "
                       f"region (round {rd+1}): "
                       + (f"held-out SSE {sse_new:.4g} vs {sse_old:.4g} "
                          f"(F {F:.1f})" if better else
                          f"tie (F {F:.1f}) and simpler "
                          f"({complexity(cand_m)[0]} vs "
                          f"{complexity(m)[0]} terms)"))
                m.setdefault("superseded", []).append(dict(
                    equation=old_eq,
                    model=dict(terms=m["terms"], coefs=m["coefs"],
                               intercept=m["intercept"], specs=m["specs"]),
                    why=why))
                m.update(terms=cand_m["terms"], coefs=cand_m["coefs"],
                         intercept=cand_m["intercept"],
                         specs=cand_m["specs"],
                         ranges=[[float(poolA[:, k].min()),
                                  float(poolA[:, k].max())]
                                 for k in range(poolA.shape[1])])
                self.net.set_meta(node, "equation", self._rename_composites(
                    enum.equation(), d_raw_m, comps_m))
                self.net.set_meta(node, "model", m)
                report["accepted"] += 1
                report["rounds"].append(why)
                if verbose:
                    print(f"    refine[{name}] r{rd+1}: ACCEPTED — {why}")
            else:
                e = _Enumerator()
                e.terms, e.coefs, e.intercept, e.specs = \
                    (cand_m["terms"], cand_m["coefs"],
                     cand_m["intercept"], cand_m["specs"])
                m.setdefault("alternatives", []).append(dict(
                    equation=e.equation(), model=cand_m,
                    why=(f"round {rd+1}: not preferred — "
                         f"F {F:.1f} vs incumbent"
                         + ("" if abs(F) > 10.0 else
                            f", tied but not simpler "
                            f"({complexity(cand_m)[0]} vs "
                            f"{complexity(m)[0]} terms)"))))
                self.net.set_meta(node, "model", m)
                report["rounds"].append(
                    f"incumbent preferred (F {F:.1f}); candidate retained "
                    f"as alternative")

        # 5. Occam prune the final law on everything known
        m = self.net.get_meta(node, "model")
        poolA = self._augment_with(pool_X, comps_m)
        terms, coefs, intercept, dropped = self._prune_terms(
            m, poolA, pool_y)
        if dropped:
            old_eq = self.net.get_meta(node, "equation")
            m.setdefault("superseded", []).append(dict(
                equation=old_eq, model=dict(
                    terms=m["terms"], coefs=m["coefs"],
                    intercept=m["intercept"], specs=m["specs"]),
                why=f"Occam prune: {dropped} term(s) removed at F-tie — "
                    f"simpler with the same accuracy"))
            m.update(terms=terms, coefs=coefs, intercept=intercept)
            self.net.set_meta(node, "model", m)
            e = _Enumerator()
            e.terms, e.coefs, e.intercept, e.specs = \
                terms, coefs, intercept, m["specs"]
            self.net.set_meta(node, "equation", self._rename_composites(
                e.equation(), d_raw_m, comps_m))
        report["spent"] = spent
        report["pruned"] = dropped
        report["equation"] = self.net.get_meta(node, "equation")
        return report

    def validate_law(self, name, X, y):
        """Re-validate a (possibly inherited) law on NEW evidence before
        trusting it. load_ledger() restores laws as APPLICABLE; this is the
        check that keeps 'applicable' from silently meaning 'still true'.
        Returns HOLDS (R2 >= 0.9) / DEGRADED (>= 0.2) / FAILS, recorded in
        the ledger either way. (2026-07-03: apply_law was applied blind.)"""
        p = self.apply_law(name, X)
        if p is None:
            return None
        y = np.asarray(y, float)
        p = np.asarray(p, float)
        fin = np.isfinite(p)
        refused = int((~fin).sum())    # lag laws: rows without history
        if refused:                    # refuse — validate the answered
            y, p = y[fin], p[fin]      # rows, REPORT the refused count
            if not len(y):
                return None
        ss = float(np.sum((y - y.mean()) ** 2))
        r2 = 1 - float(np.sum((y - p) ** 2)) / max(ss, 1e-12)
        status = ("HOLDS" if r2 >= 0.9 else
                  "DEGRADED" if r2 >= 0.2 else "FAILS")
        if refused:
            self.record_finding("validation", name, r2=round(r2, 4),
                                status=status, n=len(y),
                                refused_rows=refused)
        else:
            self.record_finding("validation", name, r2=round(r2, 4),
                                status=status, n=len(y))
        return dict(status=status, r2=r2)

    # ── task responses: told the GOAL, he finds the method ───────
    # (owner, 2026-07-12: "you tell him the goals and he needs to
    # figure out what to do... all he needs to do is respond with
    # <token A> or <token B>. next token prediction style.") Hand-built is
    # ONLY translation (tokens <-> his substrate) and epistemics.
    # LEARNED: the default relation (responses ECHO the prompt —
    # found by his compare primitive, never assumed), the response
    # classes (the observed distinct tokens, nothing pre-named), and
    # WHEN each class fires (his own discover, nulls and all). No
    # task word exists in this file; the same organ must solve ANY
    # echo-with-exceptions stream or refuse it — the battery proves
    # both on foreign worlds. WRONG-KEPT (owner correction, same
    # day): the assistant first probed this by hand-building
    # one-vs-rest targets and composing them — programming the
    # lesson. The decomposition below is Isaac's own differentiation
    # (classes = the distinct tokens he observed), inside a
    # task-blind organ.

    def learn_responses(self, prompts, responses, name="task"):
        """Learn prompt->response from examples alone; the goal is
        told, the method is his. Prompts must translate to the number
        line (numerals); responses are opaque tokens. Returns the
        task record: the echo rate he measured, the classes he
        differentiated, and each class's discover verdict."""
        prompts = [str(p) for p in prompts]
        resp = [str(r) for r in responses]
        try:
            xs = np.array([float(p) for p in prompts]).reshape(-1, 1)
        except ValueError:
            rec = dict(task=name, refused="prompts do not translate "
                                          "to the number line")
            self.record_finding("task", name, **rec)
            return rec
        echo = np.array([r == p for r, p in zip(resp, prompts)])
        classes = sorted({r for r, e in zip(resp, echo) if not e})
        record = dict(task=name, echo_rate=round(float(echo.mean()), 3),
                      classes=[], laws={})
        if len(classes) > max(8, int(np.sqrt(len(resp)))):
            record["refused"] = (f"{len(classes)} distinct non-echo "
                                 f"tokens in {len(resp)} examples: no "
                                 "small class structure to learn")
            self.record_finding("task", name, **record)
            return record
        targets = [("__echo__", echo.astype(float))]
        targets += [(c, np.array([1.0 if r == c else 0.0 for r in resp]))
                    for c in classes]
        ns = np.round(xs[:, 0]).astype(np.int64)
        int_axis = bool(np.allclose(xs[:, 0], ns, atol=1e-9))
        for c, y in targets:
            law = f"{name}:{c}"
            res = self.discover(xs, y, name=law)
            kept = self.net.get_meta(f"law:{law}", "model") is not None
            cls = dict(token=c, verdict=res["verdict"],
                       r2=round(res["r2"], 3))
            # the recognition bridge (all methods, one concept): a
            # class firing EXACTLY on the multiples of a whole P is
            # SAID that way — the discovered comb and a told
            # "multiple of P" are the same concept
            if int_axis and c != "__echo__":
                fires = y > 0.5
                for P in range(2, min(len(ns) // 4, 128) + 1):
                    if bool(((ns % P == 0) == fires).all()):
                        cls["reads_as"] = f"every {P}th"
                        break
            record["classes"].append(cls)
            if kept:
                record["laws"][c] = law
        node = f"task:{name}"
        self.net.add_door("task", node, tag="task")
        self.net.set_meta(node, "record", record)
        self.record_finding("task", name, **record)
        return record

    def respond(self, prompt, name="task"):
        """Answer a prompt with the learned task's token — the echo
        class answers with the prompt itself. Rank decides (argmax
        over his class laws, no hand thresholds); no admitted law
        firing = ABSTAIN with the why: a shrug with a diagnosis beats
        a guess."""
        rec = self.net.get_meta(f"task:{name}", "record")
        if rec is None or rec.get("refused"):
            return dict(token=None,
                        why=rec.get("refused", "no learned task")
                        if rec else "no learned task")
        x = np.array([[float(prompt)]])
        scores = {}
        for c, law in rec["laws"].items():
            p = self.apply_law(law, x)
            if p is not None and np.isfinite(p[0]):
                scores[c] = float(p[0])
        if not scores:
            return dict(token=None,
                        why="no class law says anything here")
        best = max(scores, key=scores.get)
        token = str(prompt) if best == "__echo__" else best
        return dict(token=token, class_=best,
                    scores={k: round(v, 3) for k, v in scores.items()})

    # ── told RULES: generation, not duplication ──────────────────
    # (owner, 2026-07-12, the correction: "he didnt learn it. you fed
    # him a pattern and he had to mimic it. thats not generation,
    # thats duplication... what i want is to say if its a 3 say
    # <token>, if its a 5 say <other>, if its both say <both-token>,
    # and if its neither increment the number. i want him to be able
    # to understand that kind of thing.") A rule is TOLD — conditions
    # over the number line -> utterances — and the behavior is
    # GENERATED from the understanding, zero examples seen.
    # Precedence is his own general logic: the MOST SPECIFIC
    # satisfied clause wins (a bare clause with no conditions is the
    # base case); an unresolvable tie is a REFUSAL, never a guess.
    # Told rules follow the told-knowledge law: usable at once,
    # belief only from data (validate_rule against an observed
    # stream), and the example road (learn_responses) is the duel
    # partner, not the goal.

    _RULE_CONDS = {"multiple_of"}          # the condition vocabulary

    def tell_rule(self, name, clauses):
        """Accept a told rule: [{'when': {'multiple_of': [3]},
        'say': 'tok'}, ..., {'when': {}, 'say': '__number__'}].
        '__number__' says the prompt itself. Unknown condition words
        are refused loudly, never guessed at."""
        for c in clauses:
            when = c.get("when", None)
            if not isinstance(when, dict) or "say" not in c:
                raise ValueError(f"clause needs 'when' dict + 'say': {c}")
            bad = set(when) - self._RULE_CONDS
            if bad:
                raise ValueError(
                    f"unknown condition word(s) {sorted(bad)} — "
                    f"vocabulary is {sorted(self._RULE_CONDS)}")
            for k in when.get("multiple_of", []):
                if int(k) != k or k < 2:
                    raise ValueError(f"multiple_of wants whole "
                                     f"numbers >= 2, got {k}")
        node = f"rule:{name}"
        self.net.add_door("rule", node, tag="rule")
        self.net.set_meta(node, "rule", dict(
            clauses=[dict(when=dict(c["when"]), say=str(c["say"]))
                     for c in clauses],
            status="told-unverified", validation=None))
        self.record_finding(
            "rule", name, status="told-unverified",
            clauses=[dict(when=dict(c["when"]), say=str(c["say"]))
                     for c in clauses])
        return self.net.get_meta(node, "rule")

    def respond_by_rule(self, name, prompt):
        """One prompt through the told rule. The most specific
        satisfied clause speaks; a specificity tie with different
        utterances is a refusal with the why."""
        rule = self.net.get_meta(f"rule:{name}", "rule")
        if rule is None:
            return dict(token=None, why="no such rule")
        n = float(prompt)
        if int(n) != n:
            return dict(token=None,
                        why=f"rule conditions live on whole numbers; "
                            f"got {prompt}")
        n = int(n)
        best_spec, best = -1, []
        for c in rule["clauses"]:
            ks = c["when"].get("multiple_of", [])
            if all(n % int(k) == 0 for k in ks):
                spec = sum(len(v) for v in c["when"].values())
                if spec > best_spec:
                    best_spec, best = spec, [c]
                elif spec == best_spec:
                    best.append(c)
        if not best:
            return dict(token=None, why="no clause covers this case")
        says = {c["say"] for c in best}
        if len(says) > 1:
            return dict(token=None,
                        why=f"ambiguous: {len(best)} equally specific "
                            f"clauses disagree ({sorted(says)}) — "
                            f"the rule needs a more specific clause")
        say = best[0]["say"]
        return dict(token=str(n) if say == "__number__" else say,
                    clause=best[0])

    def generate_by_rule(self, name, upto, start=1):
        """The counting loop the owner described: increment the
        number, speak each one through the rule."""
        return [self.respond_by_rule(name, i)["token"]
                for i in range(start, start + upto)]

    def validate_rule(self, name, prompts, responses):
        """Belief comes only from data (the told-knowledge law): run
        the rule against an observed stream, record the COMPLETE
        match number, promote to validated or mark contradicted with
        the first disagreements kept."""
        rule = self.net.get_meta(f"rule:{name}", "rule")
        if rule is None:
            return None
        diffs = []
        right = 0
        for p, r in zip(prompts, responses):
            out = self.respond_by_rule(name, p)
            if out["token"] == str(r):
                right += 1
            elif len(diffs) < 5:
                diffs.append(dict(prompt=str(p), rule_said=out["token"],
                                  observed=str(r)))
        total = len(list(prompts))
        result = dict(match=right, of=total,
                      status=("validated" if right == total else
                              "contradicted"), disagreements=diffs)
        rule["status"] = result["status"]
        rule["validation"] = dict(match=right, of=total)
        self.net.set_meta(f"rule:{name}", "rule", rule)
        self.record_finding("rule_validation", name, **result)
        return result

    # ── told knowledge: the supersession test candidate ─────────
    # (owner, 2026-07-12: "if you just give it the equations directly,
    #  can it use them... check if the submitted thing applies or
    #  matches any and it can be listed as a supersession test
    #  candidate")

    @staticmethod
    def _parse_equation(eq, d=None):
        """Equation string (Isaac's own canonical grammar, the format
        _atom_label prints) -> a model dict apply_law can run. Raises
        ValueError naming the exact unparseable factor — told knowledge
        outside the vocabulary is refused loudly, never guessed at."""
        import re
        specs, spec_ix, terms, coefs = [], {}, [], []
        intercept = 0.0
        ATOMS = [
            (re.compile(r"^x(\d+)$"), lambda m: ("var", int(m[1]), None, None)),
            (re.compile(r"^x(\d+)\^(-?[\d.]+)$"),
             lambda m: ("pow", int(m[1]), None, float(m[2]))),
            (re.compile(r"^log\(x(\d+)\)$"),
             lambda m: ("pow", int(m[1]), None, 0.0)),
            (re.compile(r"^(sin|cos)\(([\d.]+)\*x(\d+)\)$"),
             lambda m: (m[1], int(m[3]), None, float(m[2]))),
            (re.compile(r"^exp\((-?[\d.]+)\*x(\d+)\)$"),
             lambda m: ("exp", int(m[2]), None, -float(m[1]))),
            (re.compile(r"^(sin|cos|cosh)\(([\d.]+)\*\(x(\d+)-x(\d+)\)\)$"),
             lambda m: ({"sin": "sind", "cos": "cosd", "cosh": "coshd"}[m[1]],
                        int(m[3]), int(m[4]), float(m[2]))),
        ]

        def split_factors(body):
            out, depth, cur = [], 0, ""
            for ch in body:
                depth += (ch == "(") - (ch == ")")
                if ch == "*" and depth == 0:
                    out.append(cur); cur = ""
                else:
                    cur += ch
            out.append(cur)
            return out

        s = eq.replace(" ", "")
        term_strs, cur, depth = [], "", 0
        for ch in s:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch in "+-" and depth == 0 and cur and cur[-1] not in "^*eE(":
                term_strs.append(cur)
                cur = ch
            else:
                cur += ch
        if cur:
            term_strs.append(cur)
        for tm in term_strs:
            tm = tm.strip()
            if not tm:
                continue
            sign = -1.0 if tm.startswith("-") else 1.0
            body = tm.lstrip("+-")
            factors = split_factors(body)
            try:
                coef = sign * float(factors[0]); factors = factors[1:]
            except ValueError:
                coef = sign
            if not factors:
                intercept += coef
                continue
            t = []
            for f in factors:
                for rx, mk in ATOMS:
                    m = rx.match(f)
                    if m:
                        spec = mk(m)
                        if spec not in spec_ix:
                            spec_ix[spec] = len(specs); specs.append(spec)
                        t.append(spec_ix[spec])
                        break
                else:
                    raise ValueError(f"cannot parse factor {f!r} — told "
                                     f"knowledge must use the canonical "
                                     f"vocabulary (x0, x0^k, log(x0), "
                                     f"sin/cos(k*x0), exp(k*x0), "
                                     f"sin/cos/cosh(k*(xi-xj)))")
            terms.append(tuple(sorted(t)))
            coefs.append(coef)
        d_raw = d if d is not None else 1 + max(
            [s[1] for s in specs] + [s[2] for s in specs if s[2] is not None],
            default=-1)
        return dict(terms=terms, coefs=np.array(coefs, float),
                    intercept=float(intercept), specs=specs,
                    d_raw=d_raw, composites_used=[])

    @staticmethod
    def _form_signature(m):
        """Coefficient-free canonical form, for the match check."""
        sig = []
        for t in m["terms"]:
            labels = sorted(
                _atom_label((k, i, j, None if kk is None else round(kk, 3)))
                for (k, i, j, kk) in (m["specs"][a] for a in t))
            sig.append(tuple(labels))
        return tuple(sorted(sig))

    def tell_law(self, name, equation, d=None, who="told"):
        """Direct knowledge, welcomed as a CANDIDATE. Match-checked
        against every existing law first (a same-form submission is a
        confirming WITNESS on that law, never a duplicate node). New
        forms enter TOLD-UNVERIFIED: usable at once via apply_law, but
        carrying NO belief — law_confidence stays None until data
        earns it (belief is measured, never told)."""
        model = self._parse_equation(equation, d)
        sig = self._form_signature(model)
        for node, meta in list(self.net.meta.items()):
            if not str(node).startswith("law:"):
                continue
            other = meta.get("model")
            if other and self._form_signature(other) == sig:
                if self._coefs_match(model, other):
                    # same form AND same constants: a confirming witness
                    st = meta.setdefault("status", {})
                    st.setdefault("witnesses", []).append(
                        dict(who=who, equation=equation))
                    self.record_finding("told_match", name,
                                        matches=str(node)[4:], provenance=who)
                    return dict(status="MATCHES", law=str(node)[4:])
                # same form, DIFFERENT constants: a VARIANT in a family
                # (Earth vs Jupiter gravity — never smushed; hierarchy
                # law: variants are real things under a parent form)
                import zlib
                fam = f"lawform:{zlib.crc32(repr(sig).encode()):08x}"
                sibling = str(node)[4:]
                self._install_law(name, model, equation, who)
                for member in (f"law:{name}", node):
                    self.net.add_door(fam, member, tag="variant")
                    self.net.meta[member].setdefault(
                        "status", {})["family"] = fam
                self.record_finding("law_variant", name, family=fam,
                                    sibling=sibling, provenance=who)
                return dict(status="VARIANT", family=fam, sibling=sibling)
        self._install_law(name, model, equation, who)
        return dict(status="TOLD-UNVERIFIED", name=name)

    def _install_law(self, name, model, equation, who):
        node = f"law:{name}"
        self.net.set_meta(node, "model", model)
        self.net.set_meta(node, "status",
                          dict(state="TOLD-UNVERIFIED", provenance=who,
                               equation=equation))
        # CONTAINERS (owner, 2026-07-17): a told law lands in the
        # world it was told IN — base when told plainly, its source's
        # world when a container is open (a decoded foreign net tells
        # its laws inside its own container; THE CITIZEN's door).
        c = getattr(self, "active_container", "base")
        self.net.add_door(f"world:{c}", node, tag=f"in:{c}")
        self.net.set_meta(node, "container", c)
        self.record_finding("told_law", name, equation=equation,
                            provenance=who)

    @staticmethod
    def _coefs_match(a, b, tol=0.05):
        """Same-form models: do the CONSTANTS agree (relative, 5%)?
        Earth's g and Jupiter's g share a form and differ here."""
        la = {tuple(sorted(_atom_label(a["specs"][i]) for i in t)): c
              for t, c in zip(a["terms"], a["coefs"])}
        lb = {tuple(sorted(_atom_label(b["specs"][i]) for i in t)): c
              for t, c in zip(b["terms"], b["coefs"])}
        for k in la:
            ca, cb = la[k], lb.get(k, 0.0)
            if abs(ca - cb) > tol * max(abs(ca), abs(cb), 1e-9):
                return False
        ia, ib = a.get("intercept", 0.0), b.get("intercept", 0.0)
        return abs(ia - ib) <= tol * max(abs(ia), abs(ib), 1.0)

    def which_law(self, X, y, names=None, min_fit=0.5, margin=0.1):
        """Overlapping-confusion resolver: WHICH known law does this
        data obey? Every candidate is applied and scored; the answer
        is rank + abstention (checklist #10): a clear winner names
        itself, near-ties are declared AMBIGUOUS with the shortlist,
        and if nothing fits the verdict is NONE — a new-variant
        candidate, not a forced guess."""
        X = np.asarray(X, float)
        y = np.asarray(y, float)
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        cands = names if names is not None else [
            str(n)[4:] for n in self.net.meta if str(n).startswith("law:")]
        scores = []
        for nm in cands:
            p = self.apply_law(nm, X)
            if p is None:
                continue
            r2 = 1 - float(np.sum((y - p) ** 2)) / max(ss_tot, 1e-12)
            scores.append((nm, round(r2, 4)))
        scores.sort(key=lambda t: -t[1])
        if not scores or scores[0][1] < min_fit:
            verdict, name = "NONE — new variant candidate", None
        elif len(scores) > 1 and scores[0][1] - scores[1][1] < margin:
            verdict, name = "AMBIGUOUS", None
        else:
            verdict, name = "MATCH", scores[0][0]
        self.record_finding("which_law", name or "?", verdict=verdict,
                            ranking=scores[:5], n=len(y))
        return dict(verdict=verdict, law=name, ranking=scores[:5])

    def crystallize_forms(self, min_members=2):
        """CROSS-DOMAIN CRYSTALLIZATION (owner, 2026-07-17: "each
        dataset is defaulted to its own container, and it can
        crystalize the container structures into cross domain
        structures"). Laws are grouped by coefficient-free form; a
        form spanning distinct containers mints the lawform: parent
        (tell_law's variant machinery one level up — same crc32
        naming, so told and crystallized families UNIFY on one node),
        each variant keeping its own constants (never smushed; the
        parent holds form, never numbers). THE TOOTH: only laws that
        EARNED UNDERSTOOD in their own container may crystallize —
        kinship between confusions is not knowledge (the receipt:
        scrambled pseudo-worlds mint PARTIAL mixtures and are
        excluded, which is exactly how the scrambled-assignment null
        dies). Same form + SAME constants across containers = a
        WITNESS record (one law multiply confirmed — the universality
        road; promoting any parent into BASE stays the full court's
        job, never this organ's). Every exclusion carries a receipt
        (consideration law: bypassed, with the why).
        MEASURED-JITTER KINSHIP (the first real meal's finding,
        2026-07-18): real data earns jittered inner constants — the
        three orbital systems minted exponents 1.5 / 1.49938 / 1.5007,
        one form wearing measurement noise — and machine-identical
        signatures called kin strangers. Forms now group by atom
        STRUCTURE, inner constants judged the same at the SAME 5%
        relative tolerance the family machinery already applies to
        outer constants (_coefs_match: one tolerance, one concept of
        'same number'); the family id snaps each inner constant to
        the coarsest quarter-step ruler mark inside the tolerance
        (1.49938 -> 1.5), so told and crystallized families still
        unify on clean forms. NAMED NEXT RUNG: one FORM COURT
        deciding same-form everywhere (tell_law's match check still
        uses exact signatures)."""
        import zlib
        SENT = -999

        def _struct(m):
            terms = []
            for t in m["terms"]:
                atoms = []
                for a in t:
                    kind, i, j, k = m["specs"][a]
                    atoms.append((str(kind),
                                  SENT if i is None else int(i),
                                  SENT if j is None else int(j),
                                  None if k is None else float(k)))
                atoms.sort(key=lambda s: s[:3])
                terms.append(tuple(atoms))
            terms.sort(key=lambda t: tuple(a[:3] for a in t))
            key = tuple(tuple(a[:3] for a in t) for t in terms)
            ks = [a[3] for t in terms for a in t]
            return key, ks

        def _kclose(ka, kb):
            for a, b in zip(ka, kb):
                if a is None and b is None:
                    continue
                if a is None or b is None:
                    return False
                if abs(a - b) > 0.05 * max(abs(a), abs(b), 1e-9):
                    return False
            return True

        def _canon_k(vals):
            vals = [v for v in vals if v is not None]
            if not vals:
                return None
            m0 = sum(vals) / len(vals)
            q = round(m0 * 4) / 4.0        # quarter-step ruler marks
            if abs(q - m0) <= 0.05 * max(abs(m0), 1e-9):
                return q
            return round(m0, 3)

        groups, excluded = {}, []
        for node in list(self.net.meta):
            n = str(node)
            if not n.startswith("law:"):
                continue
            m = self.net.get_meta(n, "model")
            c = self.net.get_meta(n, "container")
            if not m or not c:
                continue
            v = self.net.get_meta(n, "verdict")
            if v != "UNDERSTOOD":
                excluded.append(dict(node=n, container=c, verdict=v,
                                     why="not earned UNDERSTOOD in its "
                                         "own container"))
                continue
            key, ks = _struct(m)
            groups.setdefault(key, []).append((n, c, ks))
        out = dict(families=[], witnesses=[], excluded=excluded)
        clusters = []
        for key, membs in groups.items():
            for item in membs:
                placed = False
                for ckey, cl in clusters:
                    if ckey == key and any(_kclose(item[2], o[2])
                                           for o in cl):
                        cl.append(item)
                        placed = True
                        break
                if not placed:
                    clusters.append((key, [item]))
        for key, membs in clusters:
            members = [(n, c) for n, c, _ in membs]
            containers = sorted({c for _, c in members})
            if len(members) < min_members or len(containers) < 2:
                continue
            # the family signature: canonical (mark-snapped) inner
            # constants per aligned position — same label grammar and
            # crc32 as tell_law, so clean told forms land on the node
            canon = [_canon_k([ks[p] for _, _, ks in membs])
                     for p in range(len(membs[0][2]))]
            sig_terms, pos = [], 0
            for t in key:
                labs = []
                for (kind, i, j) in t:
                    kk = canon[pos]
                    pos += 1
                    labs.append(_atom_label(
                        (kind, None if i == SENT else i,
                         None if j == SENT else j,
                         None if kk is None else round(kk, 3))))
                sig_terms.append(tuple(sorted(labs)))
            sig = tuple(sorted(sig_terms))
            models = [self.net.get_meta(n, "model") for n, _ in members]
            if all(self._coefs_match(models[0], m2) for m2 in models[1:]):
                w = dict(members=sorted(n for n, _ in members),
                         containers=containers,
                         why="same form AND same constants across "
                             "containers — one law seen twice, never "
                             "a family")
                out["witnesses"].append(w)
                self.record_finding("crossdomain_witness",
                                    ",".join(w["members"]),
                                    containers=containers)
                continue
            fam = f"lawform:{zlib.crc32(repr(sig).encode()):08x}"
            for n, _ in members:
                self.net.add_door(fam, n, tag="variant")
                self.net.meta[n].setdefault("status", {})["family"] = fam
            self.record_finding("crossdomain_form", fam,
                                members=sorted(n for n, _ in members),
                                containers=containers)
            out["families"].append(dict(family=fam,
                                        members=sorted(n for n, _
                                                       in members),
                                        containers=containers))
        return out

    def supersession_duel(self, name, X, y, margin=0.02):
        """The owner's test: when data arrives, the told/incumbent law
        faces a FRESH discovery on the same data, judged on a held-out
        quarter. Winner is active; the loser is KEPT wearing its
        numbers (challenger -> rivals list; superseded incumbent ->
        'superseded' history with why). A confirmed told law finally
        EARNS belief: ranges + edge-r2 from this data."""
        node = f"law:{name}"
        m = self.net.get_meta(node, "model")
        if m is None:
            return None
        X = np.asarray(X, float); y = np.asarray(y, float)
        n = len(y); cut = int(n * 0.75)
        rng = np.random.default_rng(0)
        order = rng.permutation(n)
        tr, ho = order[:cut], order[cut:]

        def r2_on(rows, pred):
            yy = y[rows]
            ss = float(np.sum((yy - yy.mean()) ** 2))
            return 1 - float(np.sum((yy - pred) ** 2)) / max(ss, 1e-12)

        inc = self.apply_law(name, X[ho])
        r2_inc = r2_on(ho, inc) if inc is not None else -np.inf
        scratch = Isaac()
        scratch.discover(X[tr], y[tr], name="challenger")
        ch = scratch.net.get_meta("law:challenger", "model")
        p = scratch.apply_law("challenger", X[ho]) if ch else None
        r2_ch = r2_on(ho, p) if p is not None else -np.inf
        status = self.net.meta[node].setdefault("status", {})
        if r2_ch > r2_inc + margin:
            status.setdefault("superseded", []).append(dict(
                model=m, state=status.get("state"),
                why=f"lost the supersession duel: held-out r2 "
                    f"{r2_inc:.4f} vs challenger {r2_ch:.4f}"))
            self.net.set_meta(node, "model", ch)
            status["state"] = "DISCOVERED-SUPERSEDED-TOLD"
            verdict = "SUPERSEDED"
            winner_r2 = r2_ch
        else:
            m.setdefault("rivals", [])
            if ch:
                m["rivals"].append(dict(model=ch, note=(
                    f"challenger lost the duel: {r2_ch:.4f} vs {r2_inc:.4f}")))
            m["ranges"] = [(float(X[:, c].min()), float(X[:, c].max()))
                           for c in range(X.shape[1])]
            m["r2_edge"] = float(max(r2_inc, 0.0))
            status["state"] = "TOLD-CONFIRMED"
            verdict = "CONFIRMED"
            winner_r2 = r2_inc
        self.record_finding("supersession_duel", name, verdict=verdict,
                            r2_incumbent=round(float(r2_inc), 4),
                            r2_challenger=round(float(r2_ch), 4),
                            n_holdout=len(ho))
        return dict(verdict=verdict, r2_incumbent=r2_inc,
                    r2_challenger=r2_ch, r2=winner_r2)

    def confirm(self, name, X, y):
        """Resolve a tied law with NEW evidence — ideally sampled at the
        probe the tie names. F-tests every live rival against the chosen
        form on the new data: decisively beaten rivals retire; a rival that
        decisively wins OVERTURNS the law, which is rewritten. 'Check both
        and keep whichever fits, until confirmed.'"""
        node = f"law:{name}"
        m = self.net.get_meta(node, "model")
        if m is None:
            return None
        X = self._augment_with(np.asarray(X, float),
                               m.get("composites_used", []))
        y = np.asarray(y, float)

        def sse_of(model):
            used = sorted({a for t in model["terms"] for a in t})
            cols = {a: _atom_col(X, model["specs"][a]) for a in used}
            D = np.column_stack([np.prod([cols[a] for a in t], axis=0)
                                 for t in model["terms"]]
                                + [np.ones(len(X))])
            p = D @ np.concatenate([model["coefs"], [model["intercept"]]])
            return float(np.sum((y - p) ** 2))

        chosen = dict(terms=m["terms"], coefs=m["coefs"],
                      intercept=m["intercept"], specs=m["specs"])
        s0, n = sse_of(chosen), len(y)
        kept, winner = [], None
        for r in m.get("rivals", []):
            s1 = sse_of(r["model"])
            better = min(s0, s1)
            F = (max(s0, s1) - better) / max(better / n, 1e-30)
            if F < 10.0:
                kept.append(r)                       # still genuinely tied
            elif s1 < s0 and (winner is None or s1 < winner[0]):
                winner = (s1, r)
        if winner is not None:
            r = winner[1]
            # SUPERSESSION, not overwrite (owner's law, 2026-07-03): "if
            # there is a and b, and b works better, use b" — and A is KEPT,
            # wearing its defeat. The overturned form stays on the record
            # with the WHY: what was believed, what beat it, by how much.
            # Knowing what was wrong — and why — is the wisdom half.
            old_eq = self.net.get_meta(node, "equation")
            m.setdefault("superseded", []).append(dict(
                equation=old_eq,
                model=dict(terms=m["terms"], coefs=m["coefs"],
                           intercept=m["intercept"], specs=m["specs"]),
                why=(f"overturned by rival '{r['rival']}' on new evidence "
                     f"(n={n}): rival SSE {winner[0]:.4g} vs {s0:.4g}")))
            m.update(terms=r["model"]["terms"], coefs=r["model"]["coefs"],
                     intercept=r["model"]["intercept"],
                     specs=r["model"]["specs"], rivals=[])
            self.net.set_meta(node, "equation", r["model"]["equation"])
            self.net.set_meta(node, "model", m)
            self.record_finding("confirmation", name,
                                status=f"OVERTURNED -> {r['rival']}",
                                equation=r["model"]["equation"],
                                superseded=old_eq)
            return dict(status=f"OVERTURNED -> {r['rival']}", rivals_left=[])
        m["rivals"] = kept
        self.net.set_meta(node, "model", m)
        # absolute-fit guard (2026-07-03): beating your rivals is not the
        # same as fitting the data — a law with no live rivals must still
        # actually hold on the new evidence to be CONFIRMED
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2_abs = 1 - s0 / max(ss_tot, 1e-12)
        if r2_abs < 0.2:
            status = f"REFUTED (fit collapsed on new data: R2 {r2_abs:.2f})"
        else:
            status = "CONFIRMED" if not kept else f"STILL TIED ({len(kept)})"
        self.record_finding("confirmation", name, status=status,
                            r2_new=round(r2_abs, 4),
                            rivals_left=[r["rival"] for r in kept])
        return dict(status=status, r2_new=r2_abs,
                    rivals_left=[r["rival"] for r in kept])

    def _capture(self, X, y, half):
        """Nearest-exemplar prediction (presence, not average): do stored
        examples predict held-out outcomes past a permuted-outcome null?
        If yes, the relationship is CAUGHT even while unarticulated —
        tracked until discovery can articulate it. No net, no training."""
        mu, sd = X[:half].mean(0), X[:half].std(0) + 1e-12
        A, B = (X[:half] - mu) / sd, (X[half:] - mu) / sd
        d2 = ((B[:, None, :] - A[None, :, :]) ** 2).sum(-1)
        nn = np.argsort(d2, 1)[:, :5]
        yh = y[half:]
        ss = float(np.sum((yh - yh.mean()) ** 2))

        def r2_of(vals, nn_idx):
            pred = vals[nn_idx].mean(1)
            return 1 - float(np.sum((yh - pred) ** 2)) / max(ss, 1e-12)

        # per-feature 1-D neighbors too: a rule living in ONE feature must
        # not be drowned by 30 irrelevant distance dimensions (red-team A4)
        nns = [nn]
        for j in range(A.shape[1]):
            d1 = np.abs(B[:, j:j + 1] - A[None, :, j])
            nns.append(np.argsort(d1, 1)[:, :5])
        real, best_nn = max(((r2_of(y[:half], m), m) for m in nns),
                            key=lambda t: t[0])
        # the null must attack EXACTLY the claimed structure: the real score
        # won a max-over-candidate-neighbor-sets contest, so each permutation
        # replays the same contest (permuting only under the winner is
        # anti-conservative — found in the 2026-07-03 audit)
        null = max(max(r2_of(yp, m) for m in nns)
                   for yp in (_wave_rng.permutation(y[:half])
                              for _ in range(20)))
        return real, null

    # ── spatial perception: relations from motion (the bridge) ─────────
    # Migrated from spatial/ (2026-07-03) after harness validation
    # (spatial/test_isaac_bridge.py 4/4, test_null_battery.py clean).
    # Coordinates are scratch, relations are storage: what enters the net
    # is locked/bounded edges, parts, hinges, anchors, and a scale-free
    # ratio signature. Every verdict is null-gated (variance-ratio vs the
    # pair's own noise floor; increment-shuffle surrogate for bounded) —
    # no hand-tuned thresholds. Assumes temporally continuous frames.

    @staticmethod
    def _extreme_visits(ds, nf):
        """min(visits to own min, to own max), hysteresis-counted."""
        lo, hi = float(ds.min()), float(ds.max())
        rng_ = hi - lo
        if rng_ <= 0:
            return 0
        band = max(0.02 * rng_, 3 * nf)
        if band >= 0.2 * rng_:
            return 0
        away = 0.25 * rng_
        counts = []
        for target in (lo, hi):
            v, armed = 0, True
            for d in ds:
                if armed and abs(d - target) < band:
                    v += 1
                    armed = False
                elif not armed and abs(d - target) > away:
                    armed = True
            counts.append(v)
        return min(counts)

    def _lift_depth(self, F, machine_eps=1e-9):
        """2D→3D (owner's caveat build, 2026-07-04): Tomasi–Kanade
        factorization with metric upgrade, NULL-GATED. Rotation is the
        condition under which depth becomes recoverable — if one rigid
        3D body explains the 2D tracks, reconstruct per-frame 3D
        trajectories; a genuinely FLAT scene must refuse the third
        coordinate (its z-variance is noise-sized). Returns
        (frames3, report). frames3 is None when depth is refused."""
        T, n, d = F.shape
        rep = dict(lifted=False)
        if d != 2 or n < 4 or T < 8:
            rep["why"] = "needs 2D tracks, >=4 points, >=8 frames"
            return None, rep
        # noise floor from temporal jitter of the tracks themselves
        nf = float(np.sqrt(max(np.diff(F, axis=0).var(), 0.0) / 2.0))
        C = F - F.mean(axis=1, keepdims=True)       # remove per-frame drift
        W = np.concatenate([C[:, :, 0], C[:, :, 1]], axis=0)   # (2T, n)
        U, s, Vt = np.linalg.svd(W, full_matrices=False)
        # planar null: does the 3rd component carry more than noise?
        resid2 = float(np.sqrt((s[2:] ** 2).sum() / W.size))
        resid3 = float(np.sqrt((s[3:] ** 2).sum() / W.size)) if len(s) > 3 else 0.0
        gate = max(nf * (1 + 4 / np.sqrt(T)), machine_eps)
        rep["resid_planar"], rep["resid_3d"], rep["gate"] = resid2, resid3, gate
        if resid2 <= gate:
            rep["why"] = "planar: two components already explain the tracks"
            return None, rep
        if resid3 > gate * 3:
            rep["why"] = "not one rigid body: rank-3 leaves structure"
            return None, rep
        # the rank-gap null: rank-3 reconstruction is rigid BY CONSTRUCTION,
        # so small residual alone cannot certify a rigid body — random walks
        # decay smoothly across components and would be FABRICATED into a
        # rigid shape (battery L3 caught exactly this). A real rigid body
        # has a cliff after component 3; no cliff, no lift.
        rep["rank_gap"] = float(s[2] / (s[3] + 1e-12)) if len(s) > 3 else np.inf
        if len(s) > 3 and s[2] < 5.0 * s[3]:
            rep["why"] = (f"no rank-3 cliff (s3/s4 = {rep['rank_gap']:.1f}) "
                          f"— structure is not one rigid body")
            return None, rep
        M = U[:, :3] * s[:3]                        # (2T, 3) camera rows
        S = Vt[:3]                                  # (3, n) affine shape
        # metric upgrade: find G (3x3 sym, = QQ^T) with M rows orthonormal
        A_rows, b_rows = [], []
        def _quad(u, v):
            return [u[0]*v[0], u[1]*v[1], u[2]*v[2],
                    u[0]*v[1] + u[1]*v[0],
                    u[0]*v[2] + u[2]*v[0],
                    u[1]*v[2] + u[2]*v[1]]
        for f in range(T):
            i_f, j_f = M[f], M[T + f]
            A_rows += [_quad(i_f, i_f), _quad(j_f, j_f), _quad(i_f, j_f)]
            b_rows += [1.0, 1.0, 0.0]
        sol, *_ = np.linalg.lstsq(np.array(A_rows), np.array(b_rows),
                                  rcond=None)
        G = np.array([[sol[0], sol[3], sol[4]],
                      [sol[3], sol[1], sol[5]],
                      [sol[4], sol[5], sol[2]]])
        w, V = np.linalg.eigh(G)
        if (w <= 0).any():                           # not metrically upgradable
            rep["why"] = "metric upgrade failed (degenerate motion)"
            return None, rep
        Q = V @ np.diag(np.sqrt(w))
        S3 = np.linalg.inv(Q) @ S                    # metric shape (3, n)
        Mq = M @ Q
        frames3 = np.empty((T, n, 3))
        for f in range(T):
            i_f = Mq[f] / (np.linalg.norm(Mq[f]) + 1e-12)
            j_raw = Mq[T + f]
            j_f = j_raw - (j_raw @ i_f) * i_f
            j_f /= (np.linalg.norm(j_f) + 1e-12)
            k_f = np.cross(i_f, j_f)
            R = np.stack([i_f, j_f, k_f])
            frames3[f] = (R @ S3).T
        rep["lifted"] = True
        rep["z_extent"] = float(S3[2].std())
        return frames3, rep

    def observe_spatial(self, frames, label="scene", machine_eps=1e-9,
                        lift="auto"):
        """THE BRIDGE: watch trajectories, store only what refuses to vary.
        Teaches facts (locked_to / bounded_with / contains / hinge_at /
        anchored_at) via teach() — indexed AND observed, so doors form —
        and a scale-free signature on a scene node. If nothing survives
        the nulls, NOTHING is taught (perception that can refuse).
        lift='auto' (2026-07-04): 2D tracks are first offered the 3D lift
        (_lift_depth, null-gated) — a rotating rigid body's true locked
        distances live in 3D; a flat scene refuses and stays 2D.
        Returns the relation bundle."""
        F = np.asarray(frames, float)               # (T, n_points, dims)
        if lift == "auto" and F.ndim == 3 and F.shape[2] == 2:
            # THE TRIGGER (same discipline as compound doors): attempt the
            # lift ONLY when flat perception hits its ceiling — a 2D scene
            # with NOTHING locked. A real planar mechanism has locked bars
            # and never triggers (the four-bar broke when the lift ran
            # unconditionally — suite caught it); a rotating 3D body has
            # no locked 2D pairs, which is precisely the shortfall depth
            # exists to explain.
            Tt = F.shape[0]
            any_locked = False
            for i_ in range(F.shape[1]):
                if any_locked:
                    break
                for j_ in range(i_ + 1, F.shape[1]):
                    ds_ = np.linalg.norm(F[:, i_] - F[:, j_], axis=1)
                    nf_ = float(np.sqrt(max(np.diff(ds_).var(), 0.0) / 2.0))
                    gate_ = max(nf_ * (1 + 4 / np.sqrt(Tt)),
                                machine_eps * max(float(ds_.mean()), 1e-12))
                    if float(ds_.std()) <= gate_:
                        any_locked = True
                        break
            if not any_locked:
                F3, lift_rep = self._lift_depth(F, machine_eps)
                if F3 is not None:
                    F = F3
        T, n, _ = F.shape
        rng = np.random.default_rng(1234)
        verdicts, scale = {}, 0.0
        series = {}
        for i in range(n):
            for j in range(i + 1, n):
                ds = np.linalg.norm(F[:, i] - F[:, j], axis=1)
                series[(i, j)] = ds
                scale = max(scale, float(ds.mean()))
        for pair, ds in series.items():
            std = float(ds.std())
            diffs = np.diff(ds)
            nf = float(np.sqrt(max(float(diffs.var()), 0.0) / 2.0))
            gate = max(nf * (1 + 4 / np.sqrt(T)), machine_eps * scale)
            if std <= gate:
                kind = "locked"
            else:
                real_v = self._extreme_visits(ds, nf)
                d0 = diffs.copy()
                surr = []
                for _ in range(20):
                    rng.shuffle(d0)
                    walk = np.concatenate([[ds[0]], ds[0] + np.cumsum(d0)])
                    surr.append(self._extreme_visits(walk, nf))
                rng_ = float(ds.max() - ds.min())
                kind = ("bounded" if real_v >= 2 and real_v > max(surr)
                        and rng_ > 10 * max(nf, machine_eps * scale)
                        else "free")
            verdicts[pair] = dict(kind=kind, mean=float(ds.mean()), std=std,
                                  noise=nf)
        locked = {p: v["mean"] for p, v in verdicts.items()
                  if v["kind"] == "locked"}
        bounded = sorted(p for p, v in verdicts.items()
                         if v["kind"] == "bounded")
        # parts = maximal pairwise-locked cliques, grown from EDGES
        cliques = []
        for (a, b) in locked:
            c = {a, b}
            for cand in range(n):
                if cand not in c and all(
                        (min(cand, m), max(cand, m)) in locked for m in c):
                    c.add(cand)
            if not any(c <= q for q in cliques):
                cliques = [q for q in cliques if not q <= c] + [c]
        hinges = sorted({min(a & b) for ai, a in enumerate(cliques)
                         for b in cliques[ai + 1:] if len(a & b) == 1})
        # anchors: coordinate variation explained by noise alone
        anchors = []
        for i in range(n):
            still = True
            for d in range(F.shape[2]):
                cs = F[:, i, d]
                nf = float(np.sqrt(max(float(np.diff(cs).var()), 0.0) / 2.0))
                if float(cs.std()) > max(nf * (1 + 4 / np.sqrt(T)),
                                         machine_eps * max(scale, 1e-12)):
                    still = False
                    break
            if still:
                anchors.append(i)
        lens = sorted(locked.values())
        sig = [round(x / lens[-1], 3) for x in lens] if lens else []
        # ---- emit: relations cross, coordinates never do
        for (i, j) in sorted(locked):
            self.teach(f"{label}.p{i}", "locked_to", f"{label}.p{j}")
        for (i, j) in bounded:
            self.teach(f"{label}.p{i}", "bounded_with", f"{label}.p{j}")
        for k, part in enumerate(sorted(map(sorted, cliques))):
            for i in part:
                self.teach(f"{label}.part{k}", "contains", f"{label}.p{i}")
        for h in hinges:
            self.teach(label, "hinge_at", f"{label}.p{h}")
        for a in anchors:
            self.teach(label, "anchored_at", f"{label}.p{a}")
        if sig:
            self.net.add_door("scene", f"scene:{label}", tag="scene")
            self.net.set_meta(f"scene:{label}", "spatial_signature", sig)
            self.net.set_meta(f"scene:{label}", "structure", dict(
                n_parts=len(cliques),
                part_sizes=sorted(len(p) for p in cliques),
                n_hinges=len(hinges)))
        return dict(locked=sorted(locked), bounded=bounded,
                    parts=[sorted(c) for c in cliques], hinges=hinges,
                    anchors=anchors, signature=sig)

    def compare_scenes(self, label_a, label_b, tol=0.02):
        """Are two perceived scenes the same STRUCTURE? Judged entirely from
        stored relations: the scale-free signature (sorted locked-length
        ratios) plus part-size multiset and hinge count. Pose, scale and
        position cannot matter — they were never stored."""
        sa = self.net.get_meta(f"scene:{label_a}", "spatial_signature")
        sb = self.net.get_meta(f"scene:{label_b}", "spatial_signature")
        ta = self.net.get_meta(f"scene:{label_a}", "structure")
        tb = self.net.get_meta(f"scene:{label_b}", "structure")
        if None in (sa, sb, ta, tb):
            return dict(verdict="UNKNOWN", reason="scene(s) not perceived")
        if len(sa) != len(sb):
            return dict(verdict="DIFFERENT", reason="different bar counts")
        gap = max(abs(x - y) for x, y in zip(sa, sb))
        same = (gap < tol and ta["part_sizes"] == tb["part_sizes"]
                and ta["n_hinges"] == tb["n_hinges"])
        return dict(verdict="SAME" if same else "DIFFERENT",
                    signature_gap=round(gap, 4))

    # ── the SPATIAL PATTERN NET: 2D→2D abstraction (owner, 2026-07-04:
    # "it needs to work on 2d to 2d abstraction too... it can learn the
    # spatial pattern net because it's always really struggled with that")
    # Instances of a class are VIEWS of a canonical form; registration
    # factors the view-transform out; the canonical part-set that recurs
    # past a null crystallizes into the net as pattern:<label> with part
    # doors. Depth (the 3D lift) is the special case where the residual
    # across views earns a new coordinate; here the residual IS instance
    # variation, and what survives it is the pattern.

    @staticmethod
    def _norm_points(P):
        """Center + unit-RMS scale (the self-calibrating scale rule)."""
        P = np.asarray(P, float)
        P = P - P.mean(0)
        return P / (np.sqrt((P ** 2).sum(1).mean()) + 1e-12)

    @staticmethod
    def _register_points(canon, P, n_rot=8, iters=5):
        """ICP-lite similarity registration of P onto canon (both
        normalized): try n_rot starting rotations, iterate nearest-
        neighbour correspondence + Procrustes. Returns (aligned P,
        matches, mean residual)."""
        best = (None, None, np.inf)
        for r in range(n_rot):
            th = 2 * np.pi * r / n_rot
            R0 = np.array([[np.cos(th), -np.sin(th)],
                           [np.sin(th), np.cos(th)]])
            Q = P @ R0.T
            for _ in range(iters):
                d2 = ((Q[:, None, :] - canon[None, :, :]) ** 2).sum(-1)
                m = d2.argmin(1)                     # each pt -> canon part
                A, B = canon[m], Q
                U, s, Vt = np.linalg.svd(B.T @ A)
                if np.linalg.det(U @ Vt) < 0:
                    U[:, -1] *= -1
                R = U @ Vt
                # both sides are unit-RMS normalized; free scale here
                # invites ICP scale-collapse (shrink toward the centroid
                # to fake a low residual) — clamp it near 1
                sc = np.clip(s.sum() / max((B ** 2).sum(), 1e-12),
                             0.8, 1.25)
                Q = (B @ R) * sc
            res = float(np.sqrt(((Q - canon[m]) ** 2).sum(-1).mean()))
            if res < best[2]:
                best = (Q, m, res)
        return best

    @staticmethod
    def _keypoints_from_image(img, k=16, thresh=0.5):
        """Ink pixels → k keypoints by farthest-point sampling (a
        tracker-free front end for glyph-like images)."""
        img = np.asarray(img, float)
        ys, xs = np.where(img > thresh * img.max())
        if len(ys) == 0:
            return np.zeros((0, 2))
        pts = np.column_stack([xs, -ys]).astype(float)   # y up
        if len(pts) <= k:
            return pts
        chosen = [int(np.argmax(((pts - pts.mean(0)) ** 2).sum(1)))]
        d = ((pts - pts[chosen[0]]) ** 2).sum(1)
        for _ in range(k - 1):
            nxt = int(np.argmax(d))
            chosen.append(nxt)
            d = np.minimum(d, ((pts - pts[nxt]) ** 2).sum(1))
        return pts[chosen]

    def learn_pattern(self, views, label, n_null=20, n_rot=8):
        """Learn a SPATIAL PATTERN NET from 2D instances (no
        correspondence given): register every view onto a growing
        canonical form; a canonical part is admitted only if its
        cross-view position spread beats the spread of the same
        registration run on NULL views (same point counts, positions
        scrambled uniformly) — chance alignment refuses. The pattern is
        NET STRUCTURE: pattern:<label> node, part:<label>.k nodes with
        position meta, plus the training residual (the pattern's own
        abstention bar for recognition)."""
        views = [self._norm_points(v) for v in views if len(v) >= 4]
        if len(views) < 3:
            return None
        canon = views[0].copy()
        hits = [[canon[i]] for i in range(len(canon))]
        resids = []
        for P in views[1:]:
            Q, m, res = self._register_points(canon, P, n_rot=n_rot)
            resids.append(res)
            for qi, ci in enumerate(m):
                hits[ci].append(Q[qi])
            canon = np.array([np.mean(h, axis=0) for h in hits])
        spread = np.array([np.mean(np.linalg.norm(
            np.array(h) - np.mean(h, axis=0), axis=1)) for h in hits])
        # the null: the same registration story on scrambled views — both
        # the part-spread gate AND the residual bar recognition abstains
        # at come from what CHANCE registration achieves.
        rng = np.random.default_rng(17)
        null_spread, null_res = [], []
        for _ in range(n_null):
            fake = [self._norm_points(
                rng.uniform(-1.5, 1.5, size=(len(v), 2))) for v in views]
            nc = fake[0].copy()
            nh = [[nc[i]] for i in range(len(nc))]
            for P in fake[1:]:
                Q, m, r_ = self._register_points(nc, P, n_rot=4, iters=3)
                null_res.append(r_)
                for qi, ci in enumerate(m):
                    nh[ci].append(Q[qi])
                nc = np.array([np.mean(h, axis=0) for h in nh])
            null_spread.append(np.median([np.mean(np.linalg.norm(
                np.array(h) - np.mean(h, axis=0), axis=1)) for h in nh]))
        gate = float(np.percentile(null_spread, 5))   # tighter than chance
        keep = spread < gate
        if not keep.any():
            return None                               # perception refuses
        canon = canon[keep]
        # THE BONE'S NORMAL (owner, 2026-07-05): each part's measured
        # cross-view spread IS its acceptance radius — scale-relative
        # (views are unit-normalized), kept instead of discarded. A match
        # is judged part by part: within the normal, just beyond, or far.
        spreads = np.maximum(spread[keep], 1e-3)
        pname = f"pattern:{label}"
        for ki in range(len(canon)):
            part = f"part:{label}.{ki}"
            self.net.add_door(pname, part, tag="part")
            self.net.set_meta(part, "pos", canon[ki].tolist())
            self.net.set_meta(part, "normal", float(spreads[ki]))
        self.net.set_meta(pname, "canon", canon)
        self.net.set_meta(pname, "spreads", spreads)
        self.net.set_meta(pname, "train_resid",
                          float(np.percentile(resids, 95)) if resids else 0.1)
        self.net.set_meta(pname, "null_resid",
                          float(np.percentile(null_res, 5)) if null_res
                          else 0.3)
        self.net.set_meta(pname, "n_rot", n_rot)
        self.net.set_meta(pname, "n_views", len(views))
        return pname

    def learn_pattern_variants(self, views, label, n_rot=8, max_variants=6):
        """REFINING STRUCTURES (owner, 2026-07-05): "jens numbers are
        different than franks... but they are all numbers." One canonical
        per class SMUSHES genuinely different styles into a form nobody
        writes (the abc/abd law applies: a style is a real thing of its
        own, under the parent by hierarchy, never dissolved into it).
        Views cluster by registration residual (leader clustering with a
        bar measured from the data's own pairwise residuals); each style
        with >=3 views becomes its own null-gated pattern
        pattern:<label>.v<k>, doored variant_of -> the parent concept."""
        views = [self._norm_points(v) for v in views if len(v) >= 4]
        if len(views) < 3:
            return []
        # the bar: what does 'same style' look like in THIS data?
        probe = []
        for a in range(min(10, len(views))):
            for b in range(a + 1, min(10, len(views))):
                probe.append(self._register_points(views[a], views[b],
                                                   n_rot=n_rot, iters=3)[2])
        bar = float(np.median(probe)) * 1.15
        clusters = [[views[0]]]
        canons = [views[0]]
        for v in views[1:]:
            res = [self._register_points(c, v, n_rot=n_rot, iters=3)[2]
                   for c in canons]
            k = int(np.argmin(res))
            if res[k] < bar or len(canons) >= max_variants:
                clusters[k].append(v)
            else:
                clusters.append([v])
                canons.append(v)
        names = []
        for k, cl in enumerate(clusters):
            if len(cl) < 3:
                continue
            pn = self.learn_pattern(cl, f"{label}.v{k}", n_rot=n_rot)
            if pn:
                names.append(pn)
                self.net.add_door(pn, f"concept:{label}", tag="variant_of")
        return names

    def _pattern_normal_fit(self, pname, P, n_rot=None):
        """Score a registered match part by part in units of each bone's
        NORMAL: z = distance / that part's measured spread. Unmatched
        canonical parts count as far (z=3). Lower is better."""
        canon = self.net.get_meta(pname, "canon")
        if canon is None or len(P) < 3:
            return np.inf
        canon = np.asarray(canon)
        spreads = self.net.get_meta(pname, "spreads")
        if spreads is None:
            spreads = np.full(len(canon),
                              self.net.get_meta(pname, "train_resid", 0.1))
        nr = n_rot if n_rot is not None else \
            self.net.get_meta(pname, "n_rot", 8)
        Q, m, _ = self._register_points(canon, P, n_rot=nr)
        zs = np.full(len(canon), 3.0)
        for qi, ci in enumerate(m):
            z = np.linalg.norm(Q[qi] - canon[ci]) / (spreads[ci] + 1e-6)
            zs[ci] = min(zs[ci], min(z, 3.0))
        return float(zs.mean())

    def recognize_pattern(self, points, patterns=None, n_rot=None):
        """Register the instance against each learned pattern; best mean
        residual wins — WITH ABSTENTION: a match that cannot beat what
        CHANCE registration achieves (the pattern's measured null_resid
        bar) is a shrug, not a guess. n_rot defaults to what the pattern
        was learned with — rotation freedom is part of the CLASS (a 6 is
        an upside-down 9; digits are learned with n_rot=1)."""
        P = self._norm_points(points)
        if patterns is None:
            patterns = [n for n in self.net.all_nodes()
                        if isinstance(n, str) and n.startswith("pattern:")]
        best, best_res = None, np.inf
        scores = {}
        for pname in patterns:
            canon = self.net.get_meta(pname, "canon")
            if canon is None or len(P) < 3:
                continue
            nr = n_rot if n_rot is not None else \
                self.net.get_meta(pname, "n_rot", 8)
            _, _, res = self._register_points(np.asarray(canon), P, n_rot=nr)
            scores[pname] = res
            if res < best_res:
                best, best_res = pname, res
        if best is not None and \
                best_res >= self.net.get_meta(best, "null_resid", 0.3):
            return None, scores                       # honest shrug
        return best, scores

    # ── the WIREFRAME (owner's design, 2026-07-04): "create a wireframe
    # concept of the thing that isaac can then run numbers over... bones
    # and structures... rigid structures with a wireframe point based
    # mesh... and for 2d the same thing across a single plane."
    # Pixels → skeleton → BONES (segments between junctions/endpoints);
    # partial 3D views STITCH via shared points; an earned reflection
    # symmetry fills the unseen side (inferred, marked, revisable).

    @staticmethod
    def _skeletonize(img, thresh=0.5):
        """Zhang–Suen thinning: ink → one-pixel-wide skeleton (the bones'
        raw material). numpy only."""
        B = (np.asarray(img, float) > thresh * np.max(img)).astype(np.uint8)
        changed = True
        while changed:
            changed = False
            for step in (0, 1):
                P = np.pad(B, 1)
                p2 = P[:-2, 1:-1]; p3 = P[:-2, 2:]; p4 = P[1:-1, 2:]
                p5 = P[2:, 2:]; p6 = P[2:, 1:-1]; p7 = P[2:, :-2]
                p8 = P[1:-1, :-2]; p9 = P[:-2, :-2]
                nb = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
                seq = np.stack([p2, p3, p4, p5, p6, p7, p8, p9, p2])
                A = ((seq[:-1] == 0) & (seq[1:] == 1)).sum(0)
                if step == 0:
                    cond = ((B == 1) & (nb >= 2) & (nb <= 6) & (A == 1)
                            & (p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0))
                else:
                    cond = ((B == 1) & (nb >= 2) & (nb <= 6) & (A == 1)
                            & (p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0))
                if cond.any():
                    B[cond] = 0
                    changed = True
        return B

    @staticmethod
    def _skel_crossings(S):
        """Crossing number per pixel: 0->1 transitions in the 8-ring.
        Endpoints have 1, line interiors 2, junctions >= 3 — robust on
        diagonal staircases where raw neighbour counts lie."""
        P = np.pad(S, 1)
        p2 = P[:-2, 1:-1]; p3 = P[:-2, 2:]; p4 = P[1:-1, 2:]
        p5 = P[2:, 2:]; p6 = P[2:, 1:-1]; p7 = P[2:, :-2]
        p8 = P[1:-1, :-2]; p9 = P[:-2, :-2]
        seq = np.stack([p2, p3, p4, p5, p6, p7, p8, p9, p2])
        return ((seq[:-1] == 0) & (seq[1:] == 1)).sum(0)

    @staticmethod
    def _skeleton_keynodes(skel, k_min=6, prune=3):
        """Structural keypoints from a skeleton: ENDPOINTS (1 neighbour)
        and JUNCTIONS (>=3) — the bone ends. Thick strokes sprout
        spurious short branches (battery W1 caught it): SPURS shorter
        than `prune` are removed first, and junction pixel clusters
        merge to their centroid. Loops (a '0') have neither endpoints
        nor junctions, so pad to k_min with farthest-point samples
        along the skeleton."""
        S = skel.copy().astype(np.uint8)

        def degrees(S_):
            P = np.pad(S_, 1)
            return sum(P[1 + dy:P.shape[0] - 1 + dy,
                         1 + dx:P.shape[1] - 1 + dx]
                       for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                       if (dy, dx) != (0, 0))

        for _ in range(prune):                       # shave spur tips
            nb = degrees(S)
            tips = (S == 1) & (nb == 1)
            if not tips.any():
                break
            S[tips] = 0
        ys, xs = np.where(S > 0)
        if len(ys) == 0:
            ys, xs = np.where(skel > 0)              # tiny glyph: un-pruned
            S = skel
            if len(ys) == 0:
                return np.zeros((0, 2))
        nb = degrees(S)
        deg = nb[ys, xs]
        cross = Isaac._skel_crossings(S)[ys, xs]
        key = (cross == 1) | (cross >= 3)            # crossing number, not
        pts = np.column_stack([xs, -ys]).astype(float)   # raw neighbours
        kpts = pts[key]
        # merge junction clusters (thick joints -> several junction px)
        merged = []
        for p in kpts:
            for q in merged:
                if np.linalg.norm(p - q["c"] / q["n"]) < 2.0:
                    q["c"] += p
                    q["n"] += 1
                    break
            else:
                merged.append({"c": p.copy(), "n": 1})
        chosen_pts = [q["c"] / q["n"] for q in merged]
        if len(chosen_pts) < k_min and len(pts) > len(chosen_pts):
            d = np.full(len(pts), np.inf)
            if not chosen_pts:
                chosen_pts = [pts[int(np.argmax(
                    ((pts - pts.mean(0)) ** 2).sum(1)))]]
            for c in chosen_pts:
                d = np.minimum(d, ((pts - c) ** 2).sum(1))
            while len(chosen_pts) < min(k_min, len(pts)):
                nxt = int(np.argmax(d))
                chosen_pts.append(pts[nxt])
                d = np.minimum(d, ((pts - pts[nxt]) ** 2).sum(1))
        return np.array(chosen_pts)

    def keypoints_structural(self, img, k_min=6):
        """The wireframe front end for glyph-like images: skeleton bones'
        endpoints and junctions instead of raw ink samples."""
        return self._skeleton_keynodes(self._skeletonize(img), k_min)

    def complete_symmetry(self, points, n_axes=36, tol=0.08, n_null=20):
        """The owner's trick: 'assumed reflection axis of symmetry to
        fill out unknowns.' Search candidate reflection axes (2D) or
        planes (3D, PCA-guided); an axis is EARNED only if the fraction
        of observed points whose mirror lands on another observed point
        beats the same search on scrambled points (selection-corrected
        null). The unmatched points' mirrors are returned as INFERRED
        geometry — hypotheses wearing their provenance, never silently
        mixed with observations."""
        P = np.asarray(points, float)
        n, d = P.shape
        if n < 4:
            return dict(axis=None, inferred=np.zeros((0, d)))
        mu = P.mean(0)
        scale = np.sqrt(((P - mu) ** 2).sum(1).mean()) + 1e-12

        def plane_candidates(Q):
            # a mirror pair DEFINES its plane: normal = the pair's
            # difference direction, offset = the midpoint's projection.
            # (v1 forced the plane through the observed centroid — a
            # PARTIAL scan's centroid is off the true plane; battery W2.)
            cands = []
            m = len(Q)
            pair_ix = [(a, b) for a in range(m) for b in range(a + 1, m)]
            if len(pair_ix) > 200:
                sel = np.random.default_rng(7).choice(len(pair_ix), 200,
                                                      replace=False)
                pair_ix = [pair_ix[int(t)] for t in sel]
            for a, b in pair_ix:
                v = Q[a] - Q[b]
                nv = np.linalg.norm(v)
                if nv > 1e-9:
                    nrm = v / nv
                    cands.append((nrm, float(((Q[a] + Q[b]) / 2) @ nrm)))
            return cands

        def best_plane(Q):
            best_f, best_nc, best_M = 0.0, None, None
            for nrm, c in plane_candidates(Q):
                Zd = Q @ nrm - c
                M = Q - 2 * np.outer(Zd, nrm)          # mirrored points
                d2 = ((M[:, None, :] - Q[None, :, :]) ** 2).sum(-1)
                f = float((np.sqrt(d2.min(1)) / scale < tol).mean())
                if f > best_f:
                    best_f, best_nc, best_M = f, (nrm, c), M
            return best_f, best_nc, best_M

        real_f, nc, M = best_plane(P)
        rng = np.random.default_rng(23)
        null_f = [best_plane(mu + (rng.uniform(-1, 1, P.shape)) * scale)[0]
                  for _ in range(n_null)]
        if nc is None or real_f <= np.percentile(null_f, 95):
            return dict(axis=None, inferred=np.zeros((0, d)),
                        why=f"symmetry {real_f:.2f} within chance "
                            f"(null 95th {np.percentile(null_f, 95):.2f})")
        d2 = ((M[:, None, :] - P[None, :, :]) ** 2).sum(-1)
        unmatched = np.sqrt(d2.min(1)) / scale >= tol
        return dict(axis=nc[0], offset=nc[1], coverage=real_f,
                    inferred=M[unmatched])

    @staticmethod
    def stitch_views(views):
        """'Build a lidar scan of the faces and stitch them into an
        idea': views = list of (ids, points) partial rigid scans — point
        identities as labels, coordinates local to each view. Views merge
        through >=3 shared points (Procrustes, both reflection signs
        tried — factorization depth carries a sign ambiguity). Returns
        (ids, points) of the stitched model, or None when views never
        overlap enough (stitching that can refuse)."""
        views = [(list(ids), np.asarray(P, float)) for ids, P in views]
        ids0, P0 = views[0]
        model = {i: p for i, p in zip(ids0, P0)}
        pending = list(views[1:])
        progress = True
        while pending and progress:
            progress = False
            for vi, (ids, P) in enumerate(pending):
                shared = [i for i in ids if i in model]
                if len(shared) < 3:
                    continue
                A = np.array([model[i] for i in shared])
                B = np.array([P[ids.index(i)] for i in shared])
                best = None
                for sign in (1.0, -1.0):
                    Bs = B.copy()
                    Bs[:, -1] *= sign
                    muA, muB = A.mean(0), Bs.mean(0)
                    A0, B0 = A - muA, Bs - muB
                    U, s, Vt = np.linalg.svd(B0.T @ A0)
                    if np.linalg.det(U @ Vt) < 0:
                        U[:, -1] *= -1
                    R = U @ Vt
                    sc = s.sum() / max((B0 ** 2).sum(), 1e-12)
                    res = float(((B0 @ R) * sc - A0).std())
                    if best is None or res < best[0]:
                        Pf = P.copy()
                        Pf[:, -1] *= sign
                        best = (res, (Pf - muB) @ R * sc + muA)
                for i, p in zip(ids, best[1]):
                    if i not in model:
                        model[i] = p
                pending.pop(vi)
                progress = True
                break
        if pending:
            return None
        ids = sorted(model)
        return ids, np.array([model[i] for i in ids])

    # ── FULL AND HOLLOW: the shape vocabulary (owner, 2026-07-04:
    # "what if it had full and hollow bones? circle vs disc vs sphere vs
    # ball... we can teach it the basic shapes and it could see the 8 is
    # two circles maybe one a bit squished"). Topology is identity,
    # geometry is framing: a HOLE is what makes a ring a ring; a shell
    # is all-surface at one radius; a ball fills its radii. Decomposed
    # glyphs become WHOLES with arranged shape-parts (the C1 machinery),
    # sayable in gated English.

    @staticmethod
    def _ink_components(mask, conn=4):
        """Connected components of a boolean mask (iterative flood).
        conn=4 for REGIONS (holes must stay separated from outside by
        8-connected ink); conn=8 for SKELETONS — a thinned stroke is an
        8-connected path, and 4-conn splits it at every diagonal step
        (battery R3: the 7's strokes shattered and the top bar's
        fragments fell under the size floor)."""
        mask = mask.copy()
        nbrs = (((1, 0), (-1, 0), (0, 1), (0, -1)) if conn == 4 else
                tuple((dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                      if (dy, dx) != (0, 0)))
        comps = []
        H, W = mask.shape
        for y0 in range(H):
            for x0 in range(W):
                if not mask[y0, x0]:
                    continue
                stack, comp = [(y0, x0)], []
                mask[y0, x0] = False
                while stack:
                    y, x = stack.pop()
                    comp.append((y, x))
                    for dy, dx in nbrs:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx]:
                            mask[ny, nx] = False
                            stack.append((ny, nx))
                comps.append(np.array(comp))
        return comps

    @classmethod
    def _holes(cls, ink):
        """Background components NOT touching the border = holes."""
        bg = ~ink
        H, W = ink.shape
        border = np.zeros_like(bg)
        seen = bg.copy()
        stack = [(y, x) for y in range(H) for x in (0, W - 1) if bg[y, x]]
        stack += [(y, x) for x in range(W) for y in (0, H - 1) if bg[y, x]]
        for y, x in stack:
            seen[y, x] = False
        while stack:
            y, x = stack.pop()
            border[y, x] = True
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and seen[ny, nx]:
                    seen[ny, nx] = False
                    stack.append((ny, nx))
        return cls._ink_components(bg & ~border)

    @staticmethod
    def _region_geometry(pts):
        """Center, axes, angle, squish, and FILL of a pixel region in its
        own principal frame. Fill separates ellipse from rectangle: a
        rectangle fills its rotated bounding box (~1.0), an ellipse fills
        pi/4 (~0.785) of it. Full-vs-hollow is topology; round-vs-square
        is fill."""
        c = pts.mean(0)
        _, sv, Vt = np.linalg.svd(pts - c, full_matrices=False)
        sd = sv / np.sqrt(len(pts))
        angle = float(np.degrees(np.arctan2(Vt[0, 1], Vt[0, 0]))) % 180.0
        R = (pts - c) @ Vt.T
        ext = R.max(0) - R.min(0) + 1.0
        fill = float(len(pts) / max(ext[0] * ext[1], 1.0))
        squish = float(sd[1] / (sd[0] + 1e-9))
        return c, sd, angle, squish, fill

    @staticmethod
    def _split_polyline(path, tol=1.8):
        """Douglas–Peucker: split an ordered pixel path at its corners —
        a 7 is a tilted line PLUS a top line, never one smeared bar."""
        segs = []

        def rec(i, j):
            if j - i < 3:
                segs.append((i, j))
                return
            a, b = path[i], path[j]
            ab = b - a
            L = np.linalg.norm(ab) + 1e-12
            u = ab / L; diff = path[i:j + 1] - a       # 2-D cross (numpy 2 removed it):
            d = np.abs(u[0] * diff[:, 1] - u[1] * diff[:, 0])
            k = int(np.argmax(d))
            if d[k] > tol and 2 <= k <= j - i - 2:
                rec(i, i + k)
                rec(i + k, j)
            else:
                segs.append((i, j))
        rec(0, len(path) - 1)
        return segs

    def describe_shape(self, img, thresh=0.5, teach_label=None,
                       min_hole=3):
        """Decompose a glyph into TAUGHT shape primitives — full and
        hollow, round and square (owner, 2026-07-04): holes mint RINGS
        (elliptical) or FRAMES (rectangular hollow); hole-less blobs mint
        DISCS or RECTS (square flagged); skeleton paths split at corners
        into LINES with JOINT angles between connected lines. RELATIONAL
        ROTATION: the glyph's principal frame gives a global TILT (pose);
        every part also carries rel_angle (identity) — a slanted 8 is the
        upright 8 wearing a tilt; a 7 is a tilted line with a second line
        joined at its head. With teach_label the decomposition ASSEMBLES
        into the net."""
        img = np.asarray(img, float)
        ink = img > thresh * img.max() if img.max() > 0 else img > 0.5
        if not ink.any():
            return None
        iy0, ix0 = np.where(ink)
        ink_pts = np.column_stack([ix0, -iy0]).astype(float)
        _, _, frame_angle, _, _ = self._region_geometry(ink_pts)
        tilt = min((frame_angle % 90), 90 - (frame_angle % 90)) * \
            (1 if (frame_angle % 90) <= 45 else -1)
        parts = []
        for h in self._holes(ink):
            if len(h) < min_hole:
                continue
            pts = np.column_stack([h[:, 1], -h[:, 0]]).astype(float)
            c, sd, angle, squish, fill = self._region_geometry(pts)
            kind = "frame" if fill > 0.92 else "ring"
            parts.append(dict(kind=kind, center=c.tolist(),
                              size=float(sd[0] * 4), squish=round(squish, 2),
                              angle=round(angle, 1),
                              square=bool(kind == "frame" and squish > 0.8)))
        # lines from the skeleton (rings' own ink excluded)
        skel = self._skeletonize(img, thresh)
        if parts:
            hole_pts = np.vstack([np.column_stack([h[:, 1], -h[:, 0]])
                                  for h in self._holes(ink)
                                  if len(h) >= min_hole])
            ys, xs = np.where(skel > 0)
            sk = np.column_stack([xs, -ys]).astype(float)
            if len(sk):
                d2 = ((sk[:, None, :] - hole_pts[None, :, :]) ** 2).sum(-1)
                ring_r = max(np.sqrt(len(hole_pts) / np.pi), 2.0)
                far = np.sqrt(d2.min(1)) > ring_r * 1.2
                keep = np.zeros_like(skel)
                for (x, y), f in zip(sk, far):
                    if f:
                        keep[int(-y), int(x)] = 1
                skel = keep
        # strokes: PEEL DIAMETER PATHS. Junction-pixel chopping was tried
        # twice and failed twice (raw-neighbour junctions shattered
        # diagonals; crossing-number junctions still misfire where the
        # thinning leaves 2px bits, chopping straight strokes and
        # dropping the 7's top bar under the min-size floor — battery
        # R3). No junction detection at all: take the LONGEST path
        # through the component, split it at corners, remove it, repeat
        # on what remains. Straight strokes, corners, and T/Y branches
        # all fall out of the same loop.
        S = (skel > 0).astype(np.uint8)
        # SOLID-VS-STROKE GATE (measured 2026-07-10): a skeleton reading
        # is only valid for ink that IS a stroke. Ink-to-skeleton
        # thickness ratio, measured populations: strokes top out at 14.9
        # (MNIST; printed fonts 3.1) and solid blobs start at 25.1 —
        # gate 20, mid-gap. A filled rectangle is a region, not a thick
        # line. Holed components (rings/frames) are exempt: the hole
        # reader already owns them.
        comps0 = self._ink_components(ink.copy())
        lbl0 = np.full(ink.shape, -1)
        for ci, comp in enumerate(comps0):
            lbl0[comp[:, 0], comp[:, 1]] = ci
        holed = set()
        for h in self._holes(ink):
            if len(h) < min_hole:
                continue
            for hy, hx in h:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        py, px = int(hy) + dy, int(hx) + dx
                        if 0 <= py < ink.shape[0] \
                                and 0 <= px < ink.shape[1] \
                                and lbl0[py, px] >= 0:
                            holed.add(int(lbl0[py, px]))
        for ci, comp in enumerate(comps0):
            if ci in holed or len(comp) < 6:
                continue
            n_sk = int(S[comp[:, 0], comp[:, 1]].sum())
            if len(comp) / max(n_sk, 1) >= 20:
                pts = np.column_stack([comp[:, 1], -comp[:, 0]]).astype(float)
                c, sd, angle, squish, fill = self._region_geometry(pts)
                if squish > 0.55:
                    kind = "rect" if fill > 0.92 else "disc"
                else:
                    kind = "line"
                parts.append(dict(kind=kind, center=c.tolist(),
                                  size=float(sd[0] * 4),
                                  squish=round(squish, 2),
                                  angle=round(angle, 1),
                                  square=bool(kind == "rect"
                                              and squish > 0.8)))
                S[comp[:, 0], comp[:, 1]] = 0
        from collections import deque

        def _bfs_far(start, cset):
            par, dist = {start: None}, {start: 0}
            q = deque([start])
            far = start
            while q:
                p = q.popleft()
                if dist[p] > dist[far]:
                    far = p
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if (dy, dx) == (0, 0):
                            continue
                        n_ = (p[0] + dy, p[1] + dx)
                        if n_ in cset and n_ not in dist:
                            dist[n_] = dist[p] + 1
                            par[n_] = p
                            q.append(n_)
            return far, par

        for comp in self._ink_components(S == 1, conn=8):
            cset = {(int(y), int(x)) for y, x in comp}
            while len(cset) >= 4:
                a0, _ = _bfs_far(next(iter(cset)), cset)
                b0, par = _bfs_far(a0, cset)
                chain = []
                p = b0
                while p is not None:
                    chain.append(p)
                    p = par[p]
                if len(chain) < 4:
                    break
                path = np.array([(x, -y) for y, x in chain], float)
                for i0, j0 in self._split_polyline(path):
                    seg = path[i0:j0 + 1]
                    if len(seg) < 4:
                        continue
                    c, sd, angle, squish, fill = self._region_geometry(seg)
                    parts.append(dict(kind="line", center=c.tolist(),
                                      length=float(np.linalg.norm(
                                          seg[-1] - seg[0])),
                                      angle=round(angle, 1),
                                      rel_angle=round((angle - frame_angle)
                                                      % 180, 1),
                                      ends=[seg[0].tolist(),
                                            seg[-1].tolist()]))
                # peel: remove the path (and its immediate halo) and
                # continue with the remaining branches
                for p in chain:
                    cset.discard(p)
                cset = {p for p in cset
                        if any((p[0] + dy, p[1] + dx) in cset
                               for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                               if (dy, dx) != (0, 0))}
        if not parts:                                   # hole-less blob
            for comp in self._ink_components(ink.copy()):
                if len(comp) < 6:
                    continue
                pts = np.column_stack([comp[:, 1], -comp[:, 0]]).astype(float)
                c, sd, angle, squish, fill = self._region_geometry(pts)
                if squish > 0.55:
                    kind = "rect" if fill > 0.92 else "disc"
                else:
                    kind = "line"
                parts.append(dict(kind=kind, center=c.tolist(),
                                  size=float(sd[0] * 4),
                                  squish=round(squish, 2),
                                  angle=round(angle, 1),
                                  square=bool(kind == "rect"
                                              and squish > 0.8)))
        # arrangement between parts: TOUCHING = carved from the same
        # connected ink component (no radius arithmetic — connectivity is
        # a fact of the ink, not an estimate; the first cut used
        # center-distance thresholds and missed the 8's own join)
        comps = self._ink_components(ink.copy())
        labels = np.full(ink.shape, -1)
        for ci, comp in enumerate(comps):
            labels[comp[:, 0], comp[:, 1]] = ci
        iy, ix_ = np.where(ink)
        ink_px = np.column_stack([ix_, -iy]).astype(float)

        def comp_of(center):
            c = np.asarray(center)
            j = int(np.argmin(((ink_px - c) ** 2).sum(1)))
            return labels[int(-ink_px[j, 1]), int(ink_px[j, 0])]

        part_comp = [comp_of(p["center"]) for p in parts]
        edges = []
        for a in range(len(parts)):
            for b in range(a + 1, len(parts)):
                if part_comp[a] != part_comp[b]:
                    continue
                pa, pb = parts[a], parts[b]
                # RELATIONAL ROTATION: two joined lines relate by their
                # JOINT ANGLE (identity survives any global tilt)
                if (pa["kind"] == "line" and pb["kind"] == "line"
                        and "ends" in pa and "ends" in pb):
                    ea = np.array(pa["ends"])
                    eb = np.array(pb["ends"])
                    gap = np.sqrt(((ea[:, None, :] - eb[None, :, :]) ** 2)
                                  .sum(-1)).min()
                    if gap < 4.0:
                        d_ang = abs(pa["angle"] - pb["angle"]) % 180
                        d_ang = min(d_ang, 180 - d_ang)
                        edges.append((a, b, f"joint {int(round(d_ang))}"))
                        continue
                ca = np.array(pa["center"])
                cb = np.array(pb["center"])
                dy, dx = cb[1] - ca[1], cb[0] - ca[0]
                rel = ("above" if dy > abs(dx) else
                       "below" if -dy > abs(dx) else "beside")
                edges.append((a, b, rel))
        # gated English
        kinds = [p["kind"] for p in parts]
        segs = []
        for k in sorted(set(kinds)):
            n_k = kinds.count(k)
            word = k
            if k in ("frame", "rect") and all(
                    p.get("square") for p in parts if p["kind"] == k):
                word = "square " + k
            segs.append(f"{['zero','one','two','three','four','five'][n_k] if n_k < 6 else n_k} {word}{'s' if n_k != 1 else ''}")
        english = ", ".join(segs)
        rings = [p for p in parts if p["kind"] in ("ring", "frame")]
        if len(rings) == 2 and edges:
            sq = sorted(r["squish"] for r in rings)
            english += f", stacked" if any(e[2] in ("above", "below")
                                           for e in edges) else ", touching"
            if sq[0] < 0.8 <= sq[1]:
                english += f", one squished ({sq[0]:.2f})"
        joints = [e for e in edges if str(e[2]).startswith("joint")]
        if joints:
            english += ", " + ", ".join(
                f"joined at {e[2].split()[1]}°" for e in joints[:2])
        if abs(tilt) >= 8:
            english += f", tilted {tilt:+.0f}°"
        result = dict(parts=parts, arrangement=edges, english=english,
                      n_holes=len(rings), tilt=round(float(tilt), 1),
                      frame_angle=round(float(frame_angle), 1))
        if teach_label:
            names = []
            for pi, p in enumerate(parts):
                pn = f"{teach_label}.{p['kind']}{pi}"
                self.register_part(pn, {p["kind"]: ()})
                self.net.set_meta(pn, "shape_params", p)
                names.append(pn)
            up = [(names[a], rel, names[b]) for a, b, rel in edges]
            self.assemble(teach_label, names, up)
            self.net.set_meta(f"whole:{teach_label}", "english", english)
        return result

    @staticmethod
    def classify_solid(points):
        """3D full-vs-hollow: sphere (shell) vs ball (solid). A shell's
        radii concentrate at one value (cv → 0); a uniform solid ball's
        radii spread (cv ≈ 0.26, exact for uniform density). The middle
        band refuses — an honest 'neither'."""
        P = np.asarray(points, float)
        r = np.linalg.norm(P - P.mean(0), axis=1)
        cv = float(r.std() / (r.mean() + 1e-12))
        if cv < 0.10:
            return dict(kind="shell", cv=cv)          # hollow: sphere
        if cv > 0.18:
            return dict(kind="solid", cv=cv)          # full: ball
        return dict(kind="uncertain", cv=cv)

    # ── RATE OF CHANGE (owner, 2026-07-05: "curve, acceleration, jerk,
    # etc. being able to detect linear or compound spirals"). The
    # derivative tower along any traced path: tangent angle θ(s) →
    # curvature κ(s)=dθ/ds → curvature rate dκ/ds. The tower IS a curve
    # vocabulary: line κ≈0; arc/circle κ≈const; spiral κ changing
    # steadily; s-curve κ crossing zero; compound = a κ-profile in
    # segments. Independent of densities/topology/bones — those see
    # where ink IS; this sees how it FLOWS.

    @staticmethod
    def path_dynamics(path, smooth=2):
        """Arc-length resample a path, then the derivative tower.
        Returns kind + measured parameters, or None for stubs."""
        P = np.asarray(path, float)
        if len(P) < 8:
            return None
        d = np.linalg.norm(np.diff(P, axis=0), axis=1)
        s = np.concatenate([[0], np.cumsum(d)])
        L = float(s[-1])
        if L <= 1e-9:
            return None
        n = int(max(16, min(64, len(P))))
        ss = np.linspace(0, L, n)
        Q = np.column_stack([np.interp(ss, s, P[:, 0]),
                             np.interp(ss, s, P[:, 1])])
        for _ in range(smooth):
            Q[1:-1] = 0.5 * Q[1:-1] + 0.25 * (Q[2:] + Q[:-2])
        T = np.diff(Q, axis=0)
        th = np.unwrap(np.arctan2(T[:, 1], T[:, 0]))
        ds = L / (n - 1)
        kappa = np.diff(th) / ds
        turn = float(th[-1] - th[0])
        km, ks = float(kappa.mean()), float(kappa.std())
        x = np.arange(len(kappa), dtype=float)
        slope = float(np.polyfit(x, kappa, 1)[0]) / ds
        signs = np.sign(kappa[np.abs(kappa) > 0.25 * (ks + 1e-12)])
        flips = int((np.diff(signs[signs != 0]) != 0).sum())
        # relative gates (scale-free): how much does κ vary vs its level?
        flat = ks < 0.15 * abs(km) + 1e-9
        if abs(km) * L < 0.35 and ks * L < 0.6:
            kind = "line"
        elif flat and abs(turn) >= 1.6 * np.pi:
            kind = "circle"
        elif flat:
            kind = "arc"
        elif flips == 0 and abs(slope) * L * L > 2.0 * ks:
            kind = "spiral"          # curvature marches one way
        elif flips == 1:
            kind = "s-curve"
        else:
            kind = "compound"
        return dict(kind=kind, length=L, turn=turn, kappa_mean=km,
                    kappa_std=ks, kappa_slope=slope, sign_flips=flips,
                    profile=kappa)

    def _skeleton_paths(self, img, thresh=0.5):
        """Ordered stroke paths from a glyph (skeleton → peel diameter
        paths), for the dynamics tower."""
        from collections import deque
        S = (self._skeletonize(img, thresh) > 0).astype(np.uint8)
        paths = []
        for comp in self._ink_components(S == 1, conn=8):
            cset = {(int(y), int(x)) for y, x in comp}
            while len(cset) >= 8:
                def far(start):
                    par, dist = {start: None}, {start: 0}
                    q = deque([start])
                    fa = start
                    while q:
                        p = q.popleft()
                        if dist[p] > dist[fa]:
                            fa = p
                        for dy in (-1, 0, 1):
                            for dx in (-1, 0, 1):
                                if (dy, dx) == (0, 0):
                                    continue
                                w = (p[0] + dy, p[1] + dx)
                                if w in cset and w not in dist:
                                    dist[w] = dist[p] + 1
                                    par[w] = p
                                    q.append(w)
                    return fa, par
                a0, _ = far(next(iter(cset)))
                b0, par = far(a0)
                chain = []
                p = b0
                while p is not None:
                    chain.append(p)
                    p = par[p]
                if len(chain) < 8:
                    break
                paths.append(np.array([(x, -y) for y, x in chain], float))
                for p in chain:
                    cset.discard(p)
                cset = {p for p in cset
                        if any((p[0] + dy, p[1] + dx) in cset
                               for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                               if (dy, dx) != (0, 0))}
        return paths

    def dynamics_features(self, img):
        """The glyph's flow signature: length-weighted tangent histogram
        + curvature statistics over all strokes. 10 numbers; the
        'dynamics' evidence channel."""
        paths = self._skeleton_paths(img)
        f = np.zeros(10)
        if not paths:
            return f
        wsum = 0.0
        for P in paths:
            dyn = self.path_dynamics(P)
            if dyn is None:
                continue
            L = dyn["length"]
            wsum += L
            T = np.diff(P, axis=0)
            th = np.arctan2(T[:, 1], T[:, 0]) % np.pi
            seg = np.linalg.norm(T, axis=1)
            hb = np.zeros(4)
            for t_, w_ in zip(th, seg):
                hb[int(t_ / (np.pi / 4)) % 4] += w_
            f[0:4] += hb
            f[4] += abs(dyn["kappa_mean"]) * L
            f[5] += dyn["kappa_std"] * L
            f[6] += abs(dyn["turn"])
            f[7] += dyn["sign_flips"]
            f[8] += abs(dyn["kappa_slope"]) * L
        f[9] = len(paths)
        if wsum > 0:
            f[0:4] /= wsum
            f[4:6] /= wsum
            f[8] /= wsum
        return f

    # ── ALL METHODS, ONE CONCEPT (owner, 2026-07-05): "it should be
    # using all methods... the doors are just pointer connections. a door
    # between bones and a door between textures or patterns and a door
    # between topology and a door between sensor values, they all point
    # to the same nodes. we don't care what or where or how the
    # information is sorted, we only care that the information is
    # represented." Every extracted structure writes evidence for the
    # SAME concept nodes; recognition sums what every channel says.

    def _norm_glyph(self, img, size=28, box=20):
        """MNIST-style normalization for ANY glyph image: crop to ink,
        longest side -> `box` px (numpy bilinear), centered by mass in a
        `size` x `size` field. Both observed glyphs and rendered symbol
        forms pass through here, so overlays compare like with like."""
        a = np.asarray(img, float)
        mx = a.max()
        if mx <= 0:
            return np.zeros((size, size))
        a = a / mx
        ys, xs = np.where(a > 0.1)
        if len(ys) == 0:
            return np.zeros((size, size))
        a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        h, w = a.shape
        s = box / max(h, w)
        nh, nw = max(1, int(round(h * s))), max(1, int(round(w * s)))
        yy = np.linspace(0, h - 1, nh)
        xx = np.linspace(0, w - 1, nw)
        y0 = np.floor(yy).astype(int)
        x0 = np.floor(xx).astype(int)
        y1 = np.minimum(y0 + 1, h - 1)
        x1 = np.minimum(x0 + 1, w - 1)
        fy = (yy - y0)[:, None]
        fx = (xx - x0)[None, :]
        r = (a[np.ix_(y0, x0)] * (1 - fy) * (1 - fx)
             + a[np.ix_(y1, x0)] * fy * (1 - fx)
             + a[np.ix_(y0, x1)] * (1 - fy) * fx
             + a[np.ix_(y1, x1)] * fy * fx)
        out = np.zeros((size, size))
        Y, X = np.mgrid[:nh, :nw]
        m = r.sum()
        cy, cx = (Y * r).sum() / m, (X * r).sum() / m
        ty, tx = int(round(size / 2 - cy)), int(round(size / 2 - cx))
        ys0, xs0 = max(0, ty), max(0, tx)
        ys1, xs1 = min(size, ty + nh), min(size, tx + nw)
        out[ys0:ys1, xs0:xs1] = r[ys0 - ty:ys1 - ty, xs0 - tx:xs1 - tx]
        return out

    @staticmethod
    def _soft_glyph(a):
        """3x3 box blur: soft ink so overlays reward NEAR misses."""
        p = np.pad(a, 1)
        out = np.zeros_like(a)
        for dy in range(3):
            for dx in range(3):
                out += p[dy:dy + a.shape[0], dx:dx + a.shape[1]]
        return out / 9.0

    def attach_symbol_forms(self, forms):
        """THE PRINT-AND-OVERLAY CHANNEL (owner, 2026-07-10: "just print
        and overlay the nearest font number... trivial for a computer").
        Rendered forms of each class's SYMBOL become templates on the
        SAME concept node — no new classifier, a new door. The string
        becomes a first-class net object (symbol:<c> -names-> concept:<c>
        — inbound polysemy: the name now reaches the concept), and
        recognition gains a `render` channel: overlay the nearest
        rendered form; the leftover after subtraction is a SIGNED DELTA
        (overlay_delta) — expectation, subtraction, perceived difference.
        `forms`: dict class -> list of rendered images (any size; the
        engine normalizes). Rendering itself is I/O and stays outside
        the engine, like any other observation."""
        for c, imgs in forms.items():
            T = []
            for im in imgs:
                t = self._soft_glyph(self._norm_glyph(im))
                n = np.linalg.norm(t)
                if n > 0:
                    T.append(t / n)
            if not T:
                continue
            node = f"concept:{c}"
            self.net.set_meta(node, "symbol_forms", np.array(T))
            self.net.add_door(f"symbol:{c}", node, tag="names")
            self.net.set_meta(f"symbol:{c}", "string", str(c))

    def overlay_delta(self, img, label=None):
        """Expect -> subtract -> perceive the delta (the effect-entity
        move, in vision). Overlays the nearest symbol form of `label`
        (or the best-fitting class) at the best shift and returns the
        SIGNED difference — extra ink (the glyph has it, the symbol
        doesn't: style, flourish) and missing ink (the symbol expects
        it, the glyph lacks it: breaks, damage) — plus the delta image
        itself. Signed deltas law: the two directions are different
        facts."""
        classes = self.net.get_meta("crystal", "glyph_classes")
        obs = self._soft_glyph(self._norm_glyph(img))
        n = np.linalg.norm(obs)
        if n == 0 or classes is None:
            return None
        obsn = obs / n
        cands = [label] if label is not None else list(classes)
        best = None
        for c in cands:
            T = self.net.get_meta(f"concept:{c}", "symbol_forms")
            if T is None or not len(T):
                continue
            for t in T:
                for dy in (-2, -1, 0, 1, 2):
                    for dx in (-2, -1, 0, 1, 2):
                        s = float((np.roll(np.roll(obsn, dy, 0), dx, 1)
                                   * t).sum())
                        if best is None or s > best[0]:
                            best = (s, c, t, dy, dx)
        if best is None:
            return None
        sim, c, t, dy, dx = best
        o = np.roll(np.roll(obs, dy, 0), dx, 1)
        tn = t * (o.sum() / max(t.sum(), 1e-9))       # match ink mass
        delta = o - tn
        ink = max(o.sum(), 1e-9)
        return dict(label=c, similarity=round(sim, 3), delta=delta,
                    extra_ink=round(float(np.clip(delta, 0, None).sum())
                                    / ink, 3),
                    missing_ink=round(float(np.clip(-delta, 0, None).sum())
                                      / ink, 3),
                    shift=(int(dy), int(dx)))

    def learn_glyphs(self, images, labels, max_exemplars=60,
                     symbol_forms=None):
        """One concept node per class; EVERY channel attaches evidence to
        it: pixel densities (crystallize_features doors), topology+line
        signatures (describe_shape), bones pattern nets, and raw
        exemplars. No channel is a separate classifier — they are doors
        on the same node."""
        images = np.asarray(images, float)
        labels = np.asarray(labels)
        self.net.set_meta("crystal", "glyph_pair_weights", {})
        self.net.set_meta("crystal", "glyph_pair_diff", {})
        self.net.set_meta("crystal", "readout_W", None)
        flat = images.reshape(len(images), -1)
        self.crystallize_features(flat, labels, compounds="off")
        classes = np.unique(labels)
        # the RATE-OF-CHANGE channel: flow signatures, density-doored
        dynF = np.array([self.dynamics_features(im) for im in images])
        qs_d = np.linspace(0, 100, 9)[1:-1]
        dyn_edges = np.stack([np.percentile(dynF[:, j], qs_d)
                              for j in range(dynF.shape[1])])
        self.net.set_meta("crystal", "dyn_edges", dyn_edges)
        for c in classes:
            node = f"concept:{c}"
            imgs = images[labels == c]
            topo = {}
            views = []
            for im in imgs:
                r = self.describe_shape(im)
                if r is not None:
                    nl = sum(1 for p in r["parts"] if p["kind"] == "line")
                    sig = (r["n_holes"], min(nl, 4))
                    topo[sig] = topo.get(sig, 0) + 1
                kp = self.keypoints_structural(im, k_min=10)
                if len(kp) >= 4:
                    views.append(kp)
            self.net.set_meta(node, "topo_counts", topo)
            self.net.set_meta(node, "topo_total", int(sum(topo.values())))
            self.net.set_meta(node, "pred_counts", topo)  # for the nevers
            if len(views) >= 3:
                # variants, not a smushed mean: Jens's 3 and Frank's 3 are
                # both 3s (owner, 2026-07-05); each style its own pattern
                vnames = self.learn_pattern_variants(views, f"glyph{c}",
                                                     n_rot=1)
                for vn in vnames:
                    self.net.add_door(node, vn, tag="evidence")
                self.net.set_meta(node, "variants", vnames)
            ex = flat[labels == c][:max_exemplars]
            ex = ex / (np.linalg.norm(ex, axis=1, keepdims=True) + 1e-9)
            self.net.set_meta(node, "exemplars", ex)
            dF = dynF[labels == c]
            ldd = np.empty((dynF.shape[1], 8))
            for j in range(dynF.shape[1]):
                cnt = np.bincount(np.searchsorted(dyn_edges[j], dF[:, j]),
                                  minlength=8).astype(float)
                ldd[j] = np.log((cnt + 1.0) / (cnt.sum() + 8))
            self.net.set_meta(node, "dyn_doors", ldd)
        self.net.set_meta("crystal", "glyph_classes", list(classes))
        # NEGATIVE STRUCTURE (owner, 2026-07-05): "it says it is this and
        # or this, but never this." A predicate a class NEVER shows across
        # all its training — while common elsewhere — is a certified
        # positive negative (the penguin law for patterns), written as a
        # not_ door past a binomial null at 1%. Candidates exhibiting a
        # certified never are VETOED at recognition.
        marg, totals = {}, {}
        per_class = {int(c): {} for c in classes}
        for c in classes:
            topo = self.net.get_meta(f"concept:{c}", "topo_counts") or {}
            for (h, l), n_ in topo.items():
                for pred in (("holes", int(h)), ("lines", int(l))):
                    marg[pred] = marg.get(pred, 0) + n_
                    totals[pred[0]] = totals.get(pred[0], 0) + n_
                    per_class[int(c)][pred] = \
                        per_class[int(c)].get(pred, 0) + n_
        for c in classes:
            n_c = self.net.get_meta(f"concept:{c}", "topo_total") or 0
            nevers = []
            for pred, cnt in marg.items():
                p = cnt / max(totals[pred[0]], 1)
                if per_class[int(c)].get(pred, 0) == 0 and n_c > 0 \
                        and (1 - p) ** n_c < 0.01:
                    nevers.append(pred)
                    self.net.add_door(f"concept:{c}",
                                      f"not_{pred[0]}={pred[1]}", tag="neg")
            self.net.set_meta(f"concept:{c}", "never", nevers)
        # print-and-overlay: attach BEFORE calibration so the render
        # channel's reliability is MEASURED like every other channel's
        if symbol_forms:
            self.attach_symbol_forms(symbol_forms)
        # measured reliability weights (calibration, not opinion): each
        # channel's vote is weighted by what it DEMONSTRATES on held-out
        # glyphs — equal weighting let a sharp-but-weak channel veto
        # strong ones (fusion battery caught the 4-point drop)
        rng = np.random.default_rng(3)
        # calibrate ONLY on glyphs outside the exemplar store — a stored
        # glyph self-matches at similarity 1.0 and would gift the
        # exemplar channel a perfect (fake) reliability score
        beyond = []
        for c in classes:
            idx_c = np.where(labels == c)[0]
            beyond.extend(idx_c[max_exemplars:])
        pool = np.array(beyond) if len(beyond) >= 50 else np.arange(len(images))
        cal = rng.choice(pool, min(300, len(pool)), replace=False)
        hits = {}
        for ix in cal:
            _, posts = self.recognize_glyph(images[ix])
            for k, p in posts.items():
                if str(k).startswith("_"):
                    continue
                hits.setdefault(k, [0, 0])
                hits[k][1] += 1
                if classes[int(np.argmax(p))] == labels[ix]:
                    hits[k][0] += 1
        chance = 1.0 / len(classes)
        weights = {k: max(h / t - chance, 0.0) for k, (h, t) in hits.items()}
        s = sum(weights.values()) or 1.0
        weights = {k: v / s for k, v in weights.items()}
        self.net.set_meta("crystal", "glyph_weights", weights)
        # PAIR JUDGES (the decision autopsy, 2026-07-05: 60% of fusion
        # errors had the truth in SECOND place — a channel knew and was
        # outvoted). Global weights say who is reliable in general;
        # 4-vs-9 has its own best witness. Per class pair, measure each
        # channel's binary accuracy on the calibration glyphs; close
        # calls get re-decided by the pair's own weights (rivals +
        # differentia, at decision time).
        # DIFFERENTIA per pair (owner's fix chain, 2026-07-05): a 4 and a
        # 9 share most of their ink — shared ink is NOISE in that duel.
        # From the density doors themselves, find the channels where the
        # two classes' observed distributions differ; the duel gains a
        # 'differentia' voter that judges on those channels ONLY.
        calib = self.net.get_meta("crystal", "calib")
        pair_diff = {}
        cl = list(classes)
        for ai in range(len(cl)):
            for bi in range(ai + 1, len(cl)):
                a, b = cl[ai], cl[bi]
                pa = np.exp(self.net.get_meta(f"concept:{a}", "doors"))
                pb = np.exp(self.net.get_meta(f"concept:{b}", "doors"))
                tv = 0.5 * np.abs(pa - pb).sum(1)
                pair_diff[(int(a), int(b))] = \
                    np.argsort(-tv)[:40].astype(int)
        self.net.set_meta("crystal", "glyph_pair_diff", pair_diff)
        cal_posts = {}
        Hcal = self.apply_lens(calib["lens"],
                               images[cal].reshape(len(cal), -1))
        e_ = calib["edges"]
        IXcal = np.column_stack([np.searchsorted(e_[j], Hcal[:, j])
                                 for j in range(Hcal.shape[1])])
        for ci, ix in enumerate(cal):
            _, posts = self.recognize_glyph(images[ix])
            cal_posts[int(ix)] = (labels[ix], posts, IXcal[ci])
        pair_w = {}
        for ai in range(len(cl)):
            for bi in range(ai + 1, len(cl)):
                a, b = cl[ai], cl[bi]
                lda = self.net.get_meta(f"concept:{a}", "doors")
                ldb = self.net.get_meta(f"concept:{b}", "doors")
                top = pair_diff[(int(a), int(b))]
                per = {}
                n_ab = 0
                m_ds = []
                for ix, (truth, posts, bins_) in cal_posts.items():
                    if truth not in (a, b):
                        continue
                    n_ab += 1
                    votes = {}
                    for k, p in posts.items():
                        if str(k).startswith("_"):
                            continue
                        votes[k] = a if p[ai] >= p[bi] else b
                    m_d = float(lda[top, bins_[top]].sum()
                                - ldb[top, bins_[top]].sum())
                    m_ds.append(m_d)
                    votes["differentia"] = a if m_d >= 0 else b
                    for k, pick in votes.items():
                        per.setdefault(k, [0, 0])
                        per[k][1] += 1
                        if pick == truth:
                            per[k][0] += 1
                if n_ab < 12:
                    continue
                w = {k: max(h / t - 0.5, 0.0) for k, (h, t) in per.items()}
                s2 = sum(w.values())
                if s2 > 0:
                    pw_ = {k: v / s2 for k, v in w.items()}
                    pw_["_sd_d"] = float(np.std(m_ds) + 1e-9)
                    pair_w[(int(a), int(b))] = pw_
        self.net.set_meta("crystal", "glyph_pair_weights", pair_w)
        return [f"concept:{c}" for c in classes]

    def train_readout(self, images, labels, steps=2000, lr=0.5):
        """THE TRAINED COMPARATOR (owner, 2026-07-05): one softmax layer
        over the node structure outputs — 'how information from multiple
        sources is compared to total activation.' Linear, so the
        extraction back into ratios/doors is EXACT (see
        extract_readout). Trained only on glyphs outside the exemplar
        store (no self-match bias)."""
        images = np.asarray(images, float)
        labels = np.asarray(labels)
        self.net.set_meta("crystal", "readout_W", None)   # no stale layer
        classes = list(self.net.get_meta("crystal", "glyph_classes"))
        CH = ["bones", "density", "dynamics", "exemplar", "topology"]
        if any(self.net.get_meta(f"concept:{c}", "symbol_forms")
               is not None for c in classes):
            CH.append("render")
        self.net.set_meta("crystal", "readout_channels", CH)
        pool = []
        for c in classes:
            idx_c = np.where(labels == c)[0]
            pool.extend(idx_c[60:])
        pool = np.array(pool if len(pool) >= 100 else range(len(images)))
        A, Y1 = [], []
        for ix in pool:
            _, posts = self.recognize_glyph(images[ix])
            v = [posts.get(k) if posts.get(k) is not None
                 else np.full(len(classes), 1.0 / len(classes)) for k in CH]
            A.append(np.concatenate(v))
            Y1.append((labels[ix] == np.array(classes)).astype(float))
        A, Y1 = np.array(A), np.array(Y1)
        r = np.random.default_rng(7)
        W = r.normal(0, 0.01, (A.shape[1], len(classes)))
        b = np.zeros(len(classes))
        vW = np.zeros_like(W)
        for _ in range(steps):
            Z = A @ W + b
            Z -= Z.max(1, keepdims=True)
            P = np.exp(Z)
            P /= P.sum(1, keepdims=True)
            G = (P - Y1) / len(A)
            vW = 0.9 * vW - lr * (A.T @ G + 1e-4 * W)
            W += vW
            b -= lr * G.sum(0)
        self.net.set_meta("crystal", "readout_W", W)
        self.net.set_meta("crystal", "readout_b", b)
        return W

    def extract_readout(self, top_k=4):
        """THE NET-EXTRACTOR TURNED ON OUR OWN NET (owner: 'analyze that
        net using the net extractor method... still human readable...
        essentially an equation'). The layer is linear, so extraction is
        LOSSLESS: each class's decision IS the equation
        score_c = Σ w·evidence + b. Writes signed evidence doors into the
        net (evid:<channel>[<class>] → concept, weight on meta — signed
        deltas law: excitation and INHIBITION are different facts) and
        returns the equations + ratio profiles in gated English."""
        W = self.net.get_meta("crystal", "readout_W")
        b = self.net.get_meta("crystal", "readout_b")
        CH = self.net.get_meta("crystal", "readout_channels")
        classes = list(self.net.get_meta("crystal", "glyph_classes"))
        if W is None:
            return None
        nC = len(classes)
        report = []
        for ci, c in enumerate(classes):
            w = W[:, ci]
            terms = []
            for kk, k in enumerate(CH):
                for j in range(nC):
                    terms.append((float(w[kk * nC + j]), k, classes[j]))
            terms.sort(key=lambda t: -abs(t[0]))
            eq = " ".join(f"{t[0]:+.2f}·{t[1]}[{t[2]}]"
                          for t in terms[:top_k])
            inhib = [t for t in terms if t[0] < -0.5][:2]
            line = f"decide {c}: {eq} {b[ci]:+.2f}"
            if inhib:
                line += ("  | inhibited by " +
                         ", ".join(f"{t[1]}[{t[2]}]" for t in inhib))
            report.append(line)
            for t in terms[:top_k]:
                en = f"evid:{t[1]}[{t[2]}]"
                self.net.add_door(en, f"concept:{c}", tag="readout")
                self.net.set_meta(f"{en}->{c}", "weight", t[0])
        return report

    def recognize_glyph(self, img, verbose=False):
        """ALL channels vote on the SAME concepts: each channel's class
        scores become a posterior (softmax of standardized scores); the
        concept with the highest SUMMED log-posterior wins — or, when a
        trained readout exists (train_readout), the READABLE LINEAR
        LAYER over the same channel outputs decides. Returns
        (label, {channel: posterior vector}) so the vote is readable."""
        img = np.asarray(img, float)
        classes = self.net.get_meta("crystal", "glyph_classes")
        calib = self.net.get_meta("crystal", "calib")
        flat = img.reshape(1, -1)
        chan = {}
        # 1. pixel-density doors
        H = self.apply_lens(calib["lens"], flat)
        e = calib["edges"]
        ix_bins = np.array([int(np.searchsorted(e[j], H[0, j]))
                            for j in range(H.shape[1])])
        jj = np.arange(H.shape[1])
        dens = []
        for c in classes:
            ld = self.net.get_meta(f"concept:{c}", "doors")
            dens.append(float(ld[jj, ix_bins].sum()))
        chan["density"] = np.array(dens)
        # 2. topology / line signature
        r = self.describe_shape(img)
        sig_seen = None
        if r is not None:
            nl = sum(1 for p in r["parts"] if p["kind"] == "line")
            sig = (r["n_holes"], min(nl, 4))
            sig_seen = sig
            tp = []
            for c in classes:
                cnts = self.net.get_meta(f"concept:{c}", "topo_counts") or {}
                tot = self.net.get_meta(f"concept:{c}", "topo_total") or 0
                tp.append(np.log((cnts.get(sig, 0) + 1.0) / (tot + 20.0)))
            chan["topology"] = np.array(tp)
        # 3. bones pattern registration
        kp = self.keypoints_structural(img, k_min=10)
        if len(kp) >= 4:
            P = self._norm_points(kp)
            res = []
            for c in classes:
                vnames = self.net.get_meta(f"concept:{c}", "variants") or []
                best = np.nan
                for vn in vnames:     # nearest STYLE, judged bone by bone
                    z_ = self._pattern_normal_fit(vn, P, n_rot=1)
                    if np.isfinite(z_):
                        best = z_ if np.isnan(best) else min(best, z_)
                res.append(best)
            res = np.array(res)
            if not np.isnan(res).all():
                res = np.where(np.isnan(res), np.nanmax(res), res)
                chan["bones"] = -res
        # 3b. rate of change: the flow signature
        de = self.net.get_meta("crystal", "dyn_edges")
        if de is not None:
            fd = self.dynamics_features(img)
            ixd = np.array([int(np.searchsorted(de[j], fd[j]))
                            for j in range(len(fd))])
            jd = np.arange(len(fd))
            dsc = []
            for c in classes:
                ldd = self.net.get_meta(f"concept:{c}", "dyn_doors")
                dsc.append(float(ldd[jd, ixd].sum())
                           if ldd is not None else 0.0)
            chan["dynamics"] = np.array(dsc)
        # 4. exemplars (presence, not average)
        f = flat[0] / (np.linalg.norm(flat[0]) + 1e-9)
        ex_s = []
        for c in classes:
            ex = self.net.get_meta(f"concept:{c}", "exemplars")
            ex_s.append(float((ex @ f).max()) if ex is not None and
                        len(ex) else -np.inf)
        chan["exemplar"] = np.array(ex_s)
        # 5. print-and-overlay: the SYMBOL channel (owner, 2026-07-10).
        # The engine overlays each class's rendered symbol forms at the
        # best small shift; the nearest print IS the vote. Cosine on
        # soft ink, max over forms and shifts.
        obs_r = self._soft_glyph(self._norm_glyph(img))
        n_r = np.linalg.norm(obs_r)
        if n_r > 0:
            obs_r = obs_r / n_r
            Sh = np.array([np.roll(np.roll(obs_r, dy, 0), dx, 1).ravel()
                           for dy in (-2, -1, 0, 1, 2)
                           for dx in (-2, -1, 0, 1, 2)])
            rsc, have = [], False
            for c in classes:
                T = self.net.get_meta(f"concept:{c}", "symbol_forms")
                if T is None or not len(T):
                    rsc.append(np.nan)
                    continue
                have = True
                rsc.append(float((T.reshape(len(T), -1) @ Sh.T).max()))
            if have:
                rsc = np.array(rsc)
                rsc = np.where(np.isnan(rsc), np.nanmin(rsc), rsc)
                chan["render"] = rsc
        # the vote: standardized scores -> per-channel posterior ->
        # RELIABILITY-WEIGHTED sum (weights measured at learn time)
        wts = self.net.get_meta("crystal", "glyph_weights") or {}
        total = np.zeros(len(classes))
        posts = {}
        for k, s in chan.items():
            z = (s - s.mean()) / (s.std() + 1e-9)
            p = np.exp(z - z.max())
            p = p / p.sum()
            posts[k] = p
            total += wts.get(k, 1.0) * np.log(p + 1e-12)
        # the trained READABLE layer, when present, is the comparator
        # (train_readout/extract_readout — the layer IS an equation)
        W_r = self.net.get_meta("crystal", "readout_W")
        readout_used = False
        if W_r is not None:
            CHo = self.net.get_meta("crystal", "readout_channels")
            v = np.concatenate([posts.get(k, np.full(len(classes),
                                                     1.0 / len(classes)))
                                for k in CHo])
            total = v @ W_r + self.net.get_meta("crystal", "readout_b")
            readout_used = True
        # THE OVERLAP STRUCTURE (owner, 2026-07-05: "for things it
        # genuinely can't resolve it can rank... then the bones can
        # select because it knows what the answer is compared to the
        # others"). The fused vote names a ranked SHORTLIST; the measured
        # pair judges duel it round-robin (each duel decided by the
        # channels that demonstrably separate that pair); the tournament
        # winner answers. A split tournament is DECLARED, ranking kept.
        # NEGATIVE STRUCTURE: "it is this or this, but NEVER that" — a
        # candidate exhibiting a certified never-predicate is vetoed
        # (hard demotion; ranking kept, nothing deleted)
        vetoed = []
        if sig_seen is not None:
            preds = {("holes", int(sig_seen[0])),
                     ("lines", int(sig_seen[1]))}
            for ci_, c in enumerate(classes):
                nev = {tuple(x) for x in
                       (self.net.get_meta(f"concept:{c}", "never") or [])}
                hit = preds & nev
                if hit:
                    vetoed.append((c, sorted(hit)))
            if len(vetoed) < len(classes):            # never veto everyone
                for c, _ in vetoed:
                    total[list(classes).index(c)] -= 50.0
        posts["_never"] = vetoed
        order = np.argsort(-total)
        pair_w = self.net.get_meta("crystal", "glyph_pair_weights") or {}
        pair_diff = self.net.get_meta("crystal", "glyph_pair_diff") or {}
        S = [int(order[t]) for t in range(min(3, len(order)))]

        def duel(ia, ib):
            # the PROVEN log-margin duel (binary votes lost the
            # confidence magnitudes and dropped 5 points — battery),
            # plus the DIFFERENTIA margin as a fifth term, judging only
            # on the channels where these two classes differ,
            # scale-normalized by its own calibration spread
            a, b = classes[ia], classes[ib]
            key = (int(min(a, b)), int(max(a, b)))
            pw = pair_w.get(key)
            if not pw:
                return ia if total[ia] >= total[ib] else ib
            lo_i, hi_i = (ia, ib) if a <= b else (ib, ia)
            m = 0.0
            for k, p in posts.items():
                if str(k).startswith("_") or k not in pw:
                    continue
                m += pw[k] * (np.log(p[lo_i] + 1e-12)
                              - np.log(p[hi_i] + 1e-12))
            if "differentia" in pw and key in pair_diff:
                lda = self.net.get_meta(f"concept:{classes[lo_i]}", "doors")
                ldb = self.net.get_meta(f"concept:{classes[hi_i]}", "doors")
                top = pair_diff[key]
                m_d = float(lda[top, ix_bins[top]].sum()
                            - ldb[top, ix_bins[top]].sum())
                m += pw["differentia"] * (m_d / pw.get("_sd_d", 1.0))
            return lo_i if m >= 0 else hi_i

        wins = {ii: 0 for ii in S}
        if readout_used:
            for rank, ii in enumerate(S):     # the layer already compared
                wins[ii] = len(S) - 1 - rank
        else:
            for ai in range(len(S)):
                for bi in range(ai + 1, len(S)):
                    wins[duel(S[ai], S[bi])] += 1
        top_wins = max(wins.values())
        finalists = [ii for ii in S if wins[ii] == top_wins]
        best = finalists[0] if len(finalists) == 1 else \
            int(S[int(np.argmin([S.index(f) for f in finalists]))])
        contested = len(finalists) > 1
        ranked = sorted(S, key=lambda ii: (-wins[ii],
                                           list(order).index(ii)))
        posts["_shortlist"] = [(classes[ii], int(wins[ii]))
                               for ii in ranked]
        posts["_contested"] = contested
        if verbose:
            for k, p in posts.items():
                if str(k).startswith("_"):
                    continue
                print(f"    {k:9s} votes {classes[int(np.argmax(p))]} "
                      f"(p={p.max():.2f})")
            print(f"    shortlist {[(c, w) for c, w in posts['_shortlist']]}"
                  f"{'  CONTESTED' if contested else ''}")
        return classes[best], posts

    # ── IDENTITY BY INTERACTION (owner, 2026-07-05: "you have to
    # understand how a thing interacts with other things... which may be
    # the part that we are missing... what are the translation factors of
    # an effect? lack of rain means no fireworks... not a direct result,
    # but a preemptive signal"). A thing's identity includes its SIGNED
    # effect profile on everything else; an observed link may be a CHAIN
    # mediated through translation factors, whose final hop can be
    # anticipatory (a response to risk) rather than physical.

    def interaction_map(self, X, names=None, n_perm=40, pct=99):
        """The signed interaction graph: for every pair, dependence past
        a selection-corrected permutation null, with SIGN (signed deltas
        — suppresses and promotes are different facts). Teaches
        affects(+/-) facts; refuses on noise."""
        X = np.asarray(X, float)
        n, d = X.shape
        names = names or [f"x{j}" for j in range(d)]
        rng = np.random.default_rng(29)
        C = np.corrcoef(X.T)
        null_max = []
        for _ in range(n_perm):
            j = rng.integers(0, d)
            k = rng.integers(0, d - 1)
            k += (k >= j)
            null_max.append(abs(np.corrcoef(
                X[:, j], rng.permutation(X[:, k]))[0, 1]))
        gate = float(np.percentile(null_max, pct))
        edges = []
        for a in range(d):
            for b_ in range(a + 1, d):
                r = float(C[a, b_])
                if abs(r) > gate:
                    sign = "+" if r > 0 else "-"
                    edges.append((names[a], names[b_], sign, round(r, 3)))
                    self.teach(names[a], f"affects{sign}", names[b_])
        self.net.set_meta("interactions", "gate", gate)
        return dict(edges=edges, gate=gate)

    def explain_link(self, x, y, X, names, n_bins=12, n_perm=30):
        """THE TRANSLATION FACTORS: is the x→y link direct, or does it
        translate through mediators? For each candidate z: stratify on z
        and re-test x↔y inside the strata. If the link DIES under
        conditioning, z is a translation factor and the chain is said;
        a near-threshold discrete terminal hop is named a PREEMPTIVE
        SIGNAL, not a consequence."""
        X = np.asarray(X, float)
        ix, iy = names.index(x), names.index(y)
        rng = np.random.default_rng(31)

        def strata(z):
            edges_ = np.percentile(X[:, z],
                                   np.linspace(0, 100, n_bins + 1))
            out = []
            for k in range(n_bins):
                m = (X[:, z] >= edges_[k]) & (X[:, z] <= edges_[k + 1])
                if m.sum() >= 12:
                    out.append(np.where(m)[0])
            return out

        def cond_r(a, bvals, groups):
            rs, ws = [], []
            for g in groups:
                sa, sb = X[g, a], bvals[g]
                if sa.std() < 1e-9 or sb.std() < 1e-9:
                    continue
                rs.append(np.corrcoef(sa, sb)[0, 1])
                ws.append(len(g))
            return float(np.average(rs, weights=ws)) if rs else 0.0

        raw = float(np.corrcoef(X[:, ix], X[:, iy])[0, 1])
        null = [abs(np.corrcoef(X[:, ix],
                                rng.permutation(X[:, iy]))[0, 1])
                for _ in range(n_perm)]
        gate = float(np.percentile(null, 95))
        mediators = []
        for iz, z in enumerate(names):
            if iz in (ix, iy):
                continue
            groups = strata(iz)
            rc = cond_r(ix, X[:, iy], groups)
            # the null that matches the CLAIM: permute y WITHIN strata —
            # what conditional correlation does chance produce once z is
            # held? (the raw-shuffle gate was wrongly strict and called
            # the fireworks chain 'direct' — battery caught it)
            null_c = []
            for _ in range(n_perm):
                yp = X[:, iy].copy()
                for g in groups:
                    yp[g] = yp[rng.permutation(g)]
                null_c.append(abs(cond_r(ix, yp, groups)))
            gate_c = float(np.percentile(null_c, 95))
            if abs(raw) > gate and abs(rc) <= gate_c:
                mediators.append((z, round(rc, 3)))
        # chain order: mediators sorted by closeness to the cause
        mediators.sort(key=lambda t: -abs(np.corrcoef(
            X[:, ix], X[:, names.index(t[0])])[0, 1]))
        direct = not mediators
        preemptive = None
        if mediators:
            # the PROXIMAL mediator (nearest the response) is what the
            # terminal hop responds to
            z = max(mediators, key=lambda t: abs(np.corrcoef(
                X[:, names.index(t[0])], X[:, iy])[0, 1]))[0]
            iz = names.index(z)
            zx, yy = X[:, iz], X[:, iy]
            if len(np.unique(yy)) <= 3:               # a discrete response
                lo = yy[zx < np.median(zx)].mean()
                hi = yy[zx >= np.median(zx)].mean()
                if abs(hi - lo) > 0.5 * (yy.std() + 1e-9):
                    preemptive = z
        if direct:
            english = (f"{x}→{y} (r={raw:+.2f}) survives conditioning on "
                       f"every candidate: DIRECT as far as these "
                       f"variables can tell.")
        else:
            chain = " → ".join([x] + [m[0] for m in mediators] + [y])
            english = (f"{x}→{y} (r={raw:+.2f}) is NOT direct: it dies "
                       f"under conditioning — it translates through "
                       f"{', '.join(m[0] for m in mediators)} "
                       f"(the chain: {chain}).")
            if preemptive:
                english += (f" The final hop is a near-threshold response "
                            f"to {preemptive}: a PREEMPTIVE SIGNAL, not a "
                            f"physical consequence.")
        return dict(raw_r=raw, direct=direct, mediators=mediators,
                    preemptive=preemptive, english=english)

    # ── THE INFORMATION LEDGER (owner, 2026-07-05: "something that
    # tells us how much information is missing still and how much we can
    # extract, and where we can go to extract it"). The mathematics:
    # total information is never upper-boundable (absence of structure
    # is unprovable), but WITNESSES prove floors — any method achieving
    # X% proves X% is extractable — and the 1-NN error bounds the
    # irreducible noise from below (Cover–Hart: Bayes error >= NN_err/2).
    # So the ledger reads  SAID <= CAUGHT <= REACHABLE <= CEILING, every
    # gap names the organ that closes it, and error-conditioned contrast
    # names WHERE the missing information lives.

    def information_ledger(self, X_tr, y_tr, X_te, y_te, pred_articulated,
                           hidden=48, steps=800, top_where=6):
        """pred_articulated = the engine's own SAID predictions on X_te.
        Computes: caught (1-NN witness), reachable (quarantined capture
        net witness — never the deliverable, exists to MEASURE), ceiling
        (Cover–Hart estimate), the gaps, and the WHERE (channels ranked
        by contrast between events the witness solves and the doors
        miss). All numbers are COMPLETE numbers."""
        X_tr = np.asarray(X_tr, float)
        X_te = np.asarray(X_te, float)
        y_tr = np.asarray(y_tr)
        y_te = np.asarray(y_te)
        mu, sd = X_tr.mean(0), X_tr.std(0) + 1e-9
        A = (X_tr - mu) / sd
        B = (X_te - mu) / sd
        said = float((np.asarray(pred_articulated) == y_te).mean())
        # CAUGHT: the exemplar witness (presence, not average)
        d2 = (B ** 2).sum(1)[:, None] - 2 * B @ A.T + (A ** 2).sum(1)[None, :]
        nn = np.argmin(d2, axis=1)
        pred_nn = y_tr[nn]
        caught = float((pred_nn == y_te).mean())
        # CEILING: Cover–Hart — Bayes error >= (1-NN error)/2, so no
        # method can exceed 1 - nn_err/2 (asymptotic estimate, labelled)
        ceiling = float(1.0 - (1.0 - caught) / 2.0)
        # REACHABLE: a quarantined softmax capture net (the stopgap that
        # exists to measure; THE NO-NETS LAW HOLDS — this is a witness,
        # never a deliverable)
        classes = np.unique(y_tr)
        Y = (y_tr[:, None] == classes[None, :]).astype(float)
        rng = np.random.default_rng(7)
        W1 = rng.normal(0, 0.1, (X_tr.shape[1], hidden))
        b1 = np.zeros(hidden)
        W2 = rng.normal(0, 0.1, (hidden, len(classes)))
        b2 = np.zeros(len(classes))
        vW1 = np.zeros_like(W1); vW2 = np.zeros_like(W2)
        lr, mom = 0.05, 0.9
        for _ in range(steps):
            Hh = np.tanh(A @ W1 + b1)
            Z = Hh @ W2 + b2
            Z -= Z.max(1, keepdims=True)
            P = np.exp(Z); P /= P.sum(1, keepdims=True)
            G = (P - Y) / len(A)
            gW2 = Hh.T @ G; gb2 = G.sum(0)
            GH = (G @ W2.T) * (1 - Hh ** 2)
            gW1 = A.T @ GH; gb1 = GH.sum(0)
            vW2 = mom * vW2 - lr * gW2; W2 += vW2; b2 -= lr * gb2
            vW1 = mom * vW1 - lr * gW1; W1 += vW1; b1 -= lr * gb1
        pred_net = classes[np.argmax(np.tanh(B @ W1 + b1) @ W2 + b2, 1)]
        reachable = float((pred_net == y_te).mean())
        # WHERE: the events a witness solves and the doors miss HOLD the
        # missing information; contrast them per channel (nulls via
        # label scrambles of the two groups)
        witness_pred = pred_net if reachable >= caught else pred_nn
        missed = (np.asarray(pred_articulated) != y_te) & \
                 (witness_pred == y_te)
        got = (np.asarray(pred_articulated) == y_te)
        where = []
        if missed.sum() >= 10 and got.sum() >= 10:
            for j in range(X_te.shape[1]):
                a_, b_ = B[missed, j], B[got, j]
                lo, hi = np.percentile(B[:, j], [1, 99])
                if hi <= lo:
                    continue
                e = np.linspace(lo, hi, 13)[1:-1]
                ha = np.bincount(np.searchsorted(e, a_), minlength=12)
                hb = np.bincount(np.searchsorted(e, b_), minlength=12)
                tv = 0.5 * np.abs(ha / max(ha.sum(), 1)
                                  - hb / max(hb.sum(), 1)).sum()
                where.append((float(tv), j))
            where.sort(reverse=True)
        best_wit = max(caught, reachable)
        gap_say = max(0.0, best_wit - said)     # PROVEN present, unsaid
        headroom = max(0.0, ceiling - max(said, best_wit))  # unproven room
        if gap_say > 0.005:
            english = (f"said {said*100:.1f}% of the whole task; witnesses "
                       f"PROVE {best_wit*100:.1f}% is extractable (exemplar "
                       f"{caught*100:.1f}%, quarantined net "
                       f"{reachable*100:.1f}%) — {gap_say*100:.1f} points are "
                       f"PRESENT but not yet said, concentrated in channels "
                       f"{[j for _, j in where[:top_where]]}. Ceiling "
                       f"estimate {ceiling*100:.1f}% (Cover–Hart); a further "
                       f"{headroom*100:.1f} points may exist, unproven.")
        else:
            english = (f"said {said*100:.1f}% of the whole task — MORE than "
                       f"any current witness proves (exemplar "
                       f"{caught*100:.1f}%, quarantined net "
                       f"{reachable*100:.1f}%): the witnesses are exhausted; "
                       f"nothing further is PROVABLY extractable today. "
                       f"Ceiling estimate {ceiling*100:.1f}% leaves "
                       f"{headroom*100:.1f} points of UNPROVEN headroom — "
                       f"finding them requires a stronger witness (richer "
                       f"percepts, more data), and the witnessed misses "
                       f"point at channels "
                       f"{[j for _, j in where[:top_where]]}.")
        return dict(said=said, caught=caught, reachable=reachable,
                    ceiling=ceiling, gap_unsaid=gap_say, headroom=headroom,
                    where=where[:top_where],
                    n_missed_witnessed=int(missed.sum()), english=english)

    # ── the capture net: a stopgap that exists to be destroyed ─────────
    # Audit 2.8, built 2026-07-03 at the owner's prompt. THE NO-NETS LAW
    # HOLDS: the net is never the deliverable — it is quarantined inside
    # the residual dossier as the tracked unknown x:<name>, it counts ONLY
    # if it beats its own permuted-output null, and its purpose is to be
    # ATTACKED by graduate() (distillation) until caught becomes said.

    @staticmethod
    def _net_fit(X, y, hidden=16, steps=400, lr=0.05, seed=7):
        """Tiny numpy MLP (1 tanh layer), full-batch momentum GD."""
        r = np.random.default_rng(seed)
        mu, sd = X.mean(0), X.std(0) + 1e-9
        ym, ys = y.mean(), y.std() + 1e-9
        Xs, yn = (X - mu) / sd, (y - ym) / ys
        d = X.shape[1]
        W1 = r.normal(0, 1 / np.sqrt(d), (d, hidden))
        b1 = np.zeros(hidden)
        W2 = r.normal(0, 1 / np.sqrt(hidden), hidden)
        b2 = 0.0
        vW1 = np.zeros_like(W1); vb1 = np.zeros_like(b1)
        vW2 = np.zeros_like(W2); vb2 = 0.0
        n = len(yn)
        for _ in range(steps):
            H = np.tanh(Xs @ W1 + b1)
            p = H @ W2 + b2
            g = 2 * (p - yn) / n
            gW2 = H.T @ g; gb2 = g.sum()
            gH = np.outer(g, W2) * (1 - H ** 2)
            gW1 = Xs.T @ gH; gb1 = gH.sum(0)
            vW1 = 0.9 * vW1 - lr * gW1; W1 += vW1
            vb1 = 0.9 * vb1 - lr * gb1; b1 += vb1
            vW2 = 0.9 * vW2 - lr * gW2; W2 += vW2
            vb2 = 0.9 * vb2 - lr * gb2; b2 += vb2
        return dict(W1=W1.tolist(), b1=b1.tolist(), W2=W2.tolist(),
                    b2=float(b2), mu=mu.tolist(), sd=sd.tolist(),
                    ym=float(ym), ys=float(ys))

    @staticmethod
    def _net_predict(net, X):
        X = np.asarray(X, float)
        Xs = (X - np.array(net["mu"])) / np.array(net["sd"])
        H = np.tanh(Xs @ np.array(net["W1"]) + np.array(net["b1"]))
        return (H @ np.array(net["W2"]) + net["b2"]) * net["ys"] + net["ym"]

    def capture_net(self, name, X, y, n_perm=8):
        """Train the stopgap on (X, y) with train/held halves. COUNTS ONLY
        if held-out R2 beats the max over permuted-output re-trainings
        (the null replays the whole training contest). On success the net
        is stored on the unknown's dossier node x:<name>; on failure
        NOTHING is stored — a big-enough net memorizing noise is exactly
        the lie the null exists to kill (audit 2.8)."""
        X = np.asarray(X, float); y = np.asarray(y, float)
        half = len(y) // 2

        def held_r2(yy):
            net = self._net_fit(X[:half], yy[:half])
            p = self._net_predict(net, X[half:])
            ss = float(np.sum((y[half:] - y[half:].mean()) ** 2))
            return 1 - float(np.sum((yy[half:] - p) ** 2)) / max(
                float(np.sum((yy[half:] - yy[half:].mean()) ** 2)), 1e-12), net

        real, net = held_r2(y)
        null = max(held_r2(_wave_rng.permutation(y))[0]
                   for _ in range(n_perm))
        if real <= max(null + 0.1, 0.2):
            return dict(status="FAILED NULL", r2=real, null=null)
        node = f"x:{name}"
        self.net.add_door("unknown", node, tag="unknown")
        self.net.set_meta(node, "capture_net", net)
        resid = y[half:] - self._net_predict(net, X[half:])
        self.net.set_meta(node, "capture_resid_sd", float(resid.std()))
        self.net.set_meta(node, "capture_r2", round(real, 4))
        self.net.set_meta(node, "ranges",
                          [[float(X[:, k].min()), float(X[:, k].max())]
                           for k in range(X.shape[1])])
        self.record_finding("capture", name, r2=round(real, 4),
                            null=round(null, 4))
        return dict(status="CAPTURED (net)", r2=real, null=null, node=node)

    def graduate(self, name, X=None, y=None, n_queries=3000, verbose=False):
        """THE DISTILLATION ATTACK (audit 2.8's closing loop): query the
        captured net as a free oracle across the unknown's observed
        ranges, run discover() on its answers, and accept the resulting
        equation ONLY if it also explains the net's held behavior — then
        the law supersedes the capture and x:<name> is retired (kept,
        marked graduated — supersession, never deletion). If no equation
        survives, the capture stands, honestly still unarticulated."""
        node = f"x:{name}"
        net = self.net.get_meta(node, "capture_net")
        ranges = self.net.get_meta(node, "ranges")
        if net is None or ranges is None:
            return None
        lo = np.array([r[0] for r in ranges])
        hi = np.array([r[1] for r in ranges])
        Xq = _wave_rng.uniform(0, 1, (n_queries, len(lo))) * (hi - lo) + lo
        yq = self._net_predict(net, Xq)
        # the net's held-out residual IS its uncertainty: answer queries
        # with that noise attached, so the net's own wiggle-artifacts die
        # at F-ties instead of graduating as tiny fake terms
        resid_sd = self.net.get_meta(node, "capture_resid_sd", 0.0)
        if resid_sd:
            yq = yq + _wave_rng.normal(0, resid_sd, len(yq))
        res = self.discover(Xq, yq, name=f"{name}_distilled")
        ok = res["verdict"] == "UNDERSTOOD" and res["r2"] >= 0.95
        if ok:
            # the razor runs at graduation too: a distilled law should be
            # the SIMPLE form, not a term-cloud imitating the net — and
            # when the ORIGINAL data is available, prune against REALITY:
            # terms that only serve the net's private warp F-tie on real
            # data and die; terms that serve the truth survive
            dnode = f"law:{name}_distilled"
            dm = self.net.get_meta(dnode, "model")
            if X is not None and y is not None:
                Xp, yp_ = np.asarray(X, float), np.asarray(y, float)
            else:
                Xp, yp_ = Xq, yq
            terms, coefs, intercept, dropped = self._prune_terms(dm, Xp, yp_)
            if dropped:
                dm.update(terms=terms, coefs=coefs, intercept=intercept)
                self.net.set_meta(dnode, "model", dm)
                e2 = _Enumerator()
                e2.terms, e2.coefs, e2.intercept, e2.specs = \
                    terms, coefs, intercept, dm["specs"]
                self.net.set_meta(dnode, "equation", e2.equation())
                res = dict(res, equation=e2.equation())
            self.net.set_meta(node, "status",
                              f"graduated -> law:{name}_distilled")
            self.record_finding("graduation", name,
                                equation=res["equation"], r2=res["r2"])
            if verbose:
                print(f"    graduate[{name}]: CAUGHT became SAID — "
                      f"{res['equation'][:60]}")
            return dict(status="GRADUATED", equation=res["equation"],
                        r2=res["r2"])
        self.net.set_meta(node, "status", "still captured (distillation "
                                          "found no equation)")
        return dict(status="STILL CAPTURED", r2=res["r2"],
                    verdict=res["verdict"])

    # ── interrogation: make the CAPTURED explicit (owner, 2026-07-04:
    # "there is structure and meaning, there is something being found but
    # we don't know what... enumerate that and make it explicit. define
    # the heuristic connections... even if they aren't specifically
    # correct, they can at least point in the direction — 'this is a
    # pattern' as a deliverable.")

    def interrogate(self, name, n=2500, grid=24):
        """Enumerate what a captured net is responding to, as explicit,
        gated heuristic claims stored on x:<name> and returned in English:
          drivers      — share of the response each input carries
                         (permutation importance on net queries)
          interactions — joint vs additive, per driver pair (ANOVA share
                         on a 2-D query grid)
          composites   — does the dependence flow ONLY THROUGH xi*xj,
                         xi+xj or xi−xj? (level-set invariance, judged
                         against random-direction level sets — the claim
                         must beat its matched null)
          shape        — along the main axis: monotone / peaked /
                         periodic, with a frequency estimate
        None of this claims the LAW — it points at it."""
        node = f"x:{name}"
        net = self.net.get_meta(node, "capture_net")
        ranges = self.net.get_meta(node, "ranges")
        if net is None or ranges is None:
            return None
        lo = np.array([r[0] for r in ranges])
        hi = np.array([r[1] for r in ranges])
        d = len(lo)
        X = _wave_rng.uniform(0, 1, (n, d)) * (hi - lo) + lo
        f0 = self._net_predict(net, X)
        var0 = max(float(f0.var()), 1e-12)

        # drivers: permutation importance
        drivers = []
        for j in range(d):
            Xp = X.copy()
            Xp[:, j] = _wave_rng.permutation(Xp[:, j])
            damage = float(np.mean((self._net_predict(net, Xp) - f0) ** 2))
            drivers.append(damage)
        tot = sum(drivers) + 1e-12
        drivers = [round(v / tot, 3) for v in drivers]
        main = [j for j in np.argsort(drivers)[::-1]
                if drivers[j] >= 0.05]

        # interactions on the top driver pairs (2-D ANOVA share)
        mid = (lo + hi) / 2
        interactions = {}
        for a_i in range(len(main)):
            for b_i in range(a_i + 1, len(main)):
                i, j = main[a_i], main[b_i]
                gi = np.linspace(lo[i], hi[i], grid)
                gj = np.linspace(lo[j], hi[j], grid)
                Q = np.tile(mid, (grid * grid, 1))
                Q[:, i] = np.repeat(gi, grid)
                Q[:, j] = np.tile(gj, grid)
                F = self._net_predict(net, Q).reshape(grid, grid)
                row = F.mean(1, keepdims=True)
                col = F.mean(0, keepdims=True)
                resid = F - row - col + F.mean()
                share = float(resid.var() / max(F.var(), 1e-12))
                interactions[(int(i), int(j))] = round(share, 3)

        # composites: level-set invariance vs random-direction null
        composites = []
        for (i, j), share in interactions.items():
            if share < 0.1:
                continue
            # each candidate composite = (z-function, level-set solver:
            # given z0 and a sweep of xi values, the xj that keeps z=z0)
            cands = {
                "product": (lambda a, b: a * b,
                            lambda z0, ai: np.where(np.abs(ai) > 1e-6,
                                                    z0 / ai, np.nan)),
                "sum": (lambda a, b: a + b, lambda z0, ai: z0 - ai),
                "difference": (lambda a, b: a - b, lambda z0, ai: ai - z0),
                "ratio": (lambda a, b: np.where(np.abs(b) > 1e-9, a / b,
                                                np.nan),
                          lambda z0, ai: np.where(np.abs(z0) > 1e-9,
                                                  ai / z0, np.nan))}

            def invariance(zfun, solve_b):
                keep = []
                for _ in range(40):
                    base = _wave_rng.uniform(0, 1, d) * (hi - lo) + lo
                    z0 = zfun(base[i], base[j])
                    ai = np.linspace(lo[i], hi[i], 24)
                    with np.errstate(divide="ignore", invalid="ignore"):
                        bj = solve_b(z0, ai)
                    okm = np.isfinite(bj) & (bj >= lo[j]) & (bj <= hi[j])
                    if okm.sum() < 8:
                        continue
                    Q = np.tile(base, (int(okm.sum()), 1))
                    Q[:, i] = ai[okm]
                    Q[:, j] = bj[okm]
                    keep.append(float(self._net_predict(net, Q).var()))
                if not keep:
                    return 0.0
                return 1.0 - float(np.mean(keep)) / var0

            scores = {k: invariance(z, s) for k, (z, s) in cands.items()}
            # matched null: the SAME level-set walk along random oblique
            # directions w0*xi + w1*xj — the claim must beat directions
            # nobody proposed
            nulls = []
            for _ in range(6):
                w = _wave_rng.normal(0, 1, 2)
                if abs(w[1]) < 0.1:
                    w[1] = 0.1 * np.sign(w[1] or 1)
                nulls.append(invariance(
                    lambda a, b, w=w: w[0] * a + w[1] * b,
                    lambda z0, ai, w=w: (z0 - w[0] * ai) / w[1]))
            best = max(scores, key=scores.get)
            if scores[best] > 0.8 and scores[best] > max(nulls):
                # shape along the composite axis
                z = cands[best][0](X[:, i], X[:, j])
                order = np.argsort(z)
                zs, fs = z[order], f0[order]
                bins = np.array_split(np.arange(len(zs)), 60)
                prof = np.array([fs[b].mean() for b in bins])
                zc = np.array([zs[b].mean() for b in bins])
                dsign = np.sign(np.diff(prof))
                turns = int(np.sum(np.diff(dsign[dsign != 0]) != 0))
                s_ = np.sign(prof - prof.mean())
                crossings = int(np.sum(s_[:-1] * s_[1:] < 0))
                span = float(zc[-1] - zc[0]) or 1.0
                freq = round(np.pi * crossings / span, 2)
                shape = ("periodic" if turns >= 3 else
                         "single-peaked" if turns in (1, 2) else "monotone")
                composites.append(dict(
                    features=[int(i), int(j)], through=best,
                    invariance=round(scores[best], 3),
                    null_best=round(max(nulls), 3),
                    shape=shape, turns=turns,
                    freq_estimate=(freq if shape == "periodic" else None)))

        # COLLECTIVE probe (owner, 2026-07-04: "a strong significant
        # collective signal, but a weak individual signal" — and SIGNED:
        # "5-7 is -2, but 5--7 is 12. darkening vs brightening"). Shift
        # all drivers TOGETHER (coherently) vs one at a time vs the
        # matched null: same-size shifts with SCRAMBLED signs (breaks
        # coherence, keeps perturbation). Responses reported signed, both
        # directions — darkening and brightening are different facts.
        collective = None
        if len(main) >= 3:
            feats = sorted(int(j) for j in main)
            pad = 0.25 * (hi - lo)
            Xc = _wave_rng.uniform(0, 1, (600, d)) * (hi - lo - 2 * pad)                 + lo + pad
            fc = self._net_predict(net, Xc)

            def resp(signs, scale=1.0):
                Xs = Xc.copy()
                for k_, j in enumerate(feats):
                    Xs[:, j] = Xs[:, j] + signs[k_] * scale * pad[j]
                return float(np.mean(self._net_predict(net, Xs) - fc))

            ones = np.ones(len(feats))
            up, down = resp(ones), resp(-ones)
            indiv = []
            for k_, j in enumerate(feats):
                e = np.zeros(len(feats)); e[k_] = 1.0
                indiv.append(max(abs(resp(e)), abs(resp(-e))))
            max_indiv = max(indiv)
            scrambled = []
            for _ in range(12):
                sgn = _wave_rng.choice([-1.0, 1.0], len(feats))
                scrambled.append(max(abs(resp(sgn)), abs(resp(-sgn))))
            strength = max(abs(up), abs(down))
            if strength > max(scrambled) and strength > 2 * max_indiv:
                collective = dict(
                    features=feats, up=round(up, 3), down=round(down, 3),
                    ratio=round(strength / max(max_indiv, 1e-9), 1),
                    null=round(max(scrambled), 3))
                self.register_composite(
                    "mean", feats,
                    provenance=f"collective probe of x:{name}")

        # English: the deliverable, even when the law is out of reach
        names_ = [f"x{k}" for k in range(d)]
        lines = []
        if main:
            lines.append("the pattern lives in "
                         + ", ".join(f"{names_[j]} ({drivers[j]*100:.0f}%)"
                                     for j in main)
                         + (" — the rest of the columns are bystanders"
                            if len(main) < d else ""))
        for (i, j), share in sorted(interactions.items(),
                                    key=lambda kv: -kv[1]):
            if share >= 0.1:
                lines.append(f"{names_[i]} and {names_[j]} act JOINTLY "
                             f"(interaction carries {share*100:.0f}% of "
                             f"their effect) — not a sum of separate "
                             f"influences")
        for c in composites:
            i, j = c["features"]
            lines.append(
                f"the dependence flows through the {c['through']} "
                f"{names_[i]}{ {'product': '*', 'sum': '+', 'difference': '-', 'ratio': '/'}[c['through']] }{names_[j]} "
                f"ONLY (invariance {c['invariance']:.2f}, beats its null "
                f"{c['null_best']:.2f}); along that axis the response is "
                f"{c['shape']}"
                + (f", roughly {c['freq_estimate']} rad/unit"
                   if c["freq_estimate"] else ""))
        if collective:
            k_ = len(collective["features"])
            dirword = ("rises" if collective["up"] > 0 else "falls")
            lines.append(
                f"the {k_} drivers move TOGETHER: a coherent shift up moves "
                f"the response {collective['up']:+.2f} and a coherent shift "
                f"down moves it {collective['down']:+.2f} (signed — "
                f"brightening and darkening are different facts); the "
                f"collective is {collective['ratio']}x any single feature "
                f"and beats sign-scrambled shifts ({collective['null']:.2f})"
                f" — the response {dirword} with the group's common mode")
        if not lines:
            lines.append("no gated heuristic survived — the capture is "
                         "real but structureless to these probes")
        for c in composites:
            self.register_composite(
                c["through"], c["features"],
                provenance=f"interrogation of x:{name}")
        heur = dict(drivers=drivers, collective=collective, interactions={
            f"{i},{j}": v for (i, j), v in interactions.items()},
            composites=composites, english=lines)
        self.net.set_meta(node, "heuristics", heur)
        self.record_finding("heuristics", name, english=lines)
        return heur

    # ── combinations are THINGS (owner, 2026-07-04: "x0,x1 in this
    # relationship... shouldn't be two separate things. it should have a
    # node... enumerate and then use that... it's combinatorial. it should
    # be able to memorize and reuse those combinations. a topological venn
    # diagram... a dimensionless structure.") A certified combination is
    # minted as a node comb:<name>, distinct from its parts and from every
    # other combination (ab ≠ a,b ≠ abc ≠ abd), persisted through the
    # ledger, and OFFERED TO EVERY FUTURE discover() as a first-class
    # feature — the atom library grows with experience.

    _COMP_OPS = {"product": (lambda a, b: a * b, "*"),
                 "sum": (lambda a, b: a + b, "+"),
                 "difference": (lambda a, b: a - b, "-"),
                 "ratio": (lambda a, b: np.where(np.abs(b) > 1e-9,
                                                 a / np.where(b == 0, 1, b),
                                                 np.nan), "/")}

    def register_composite(self, op, features, provenance="", exps=None):
        """Mint a combination as a first-class node. Idempotent.
        POWERPROD (the growing grammar, owner 2026-07-18): products
        of powers over variables — the combinators nested, which the
        hand menu never did; minted by the harder road, offered to
        every future problem like any earned word."""
        features = [int(f) for f in features]
        if op == "mean":                          # collective coordinate
            cname = "mean(" + ",".join(f"x{f}" for f in features) + ")"
        elif op == "log":                         # arity-1 transform:
            cname = f"log(x{features[0]})"        # domain-guarded (x > 0)
        elif op == "powerprod":
            parts = [f"x{f}" if e == 1 else f"x{f}^{e:g}"
                     for f, e in zip(features, exps) if e]
            cname = "(" + "*".join(parts) + ")"
        else:
            sym = self._COMP_OPS[op][1]
            cname = "(" + sym.join(f"x{f}" for f in features) + ")"
        if any(c["name"] == cname for c in self.composites):
            return cname
        comp = dict(op=op, features=features, name=cname,
                    provenance=provenance)
        if op == "powerprod":
            comp["exps"] = [float(e) for e in exps]
        self.composites.append(comp)
        node = f"comb:{cname}"
        self.net.add_door("combination", node, tag="comb")
        for f in features:
            self.net.add_door(node, f"feat:x{f}", tag="comb")
        self.net.set_meta(node, "composite", comp)
        self.record_finding("composite", cname, op=op, features=features,
                            provenance=provenance)
        return cname

    def _augment_with(self, X, comps):
        """Append the given combinations as columns. Order = comps order."""
        X = np.asarray(X, float)
        cols = []
        for c in comps:
            if c["op"] == "mean":                 # a COLLECTIVE coordinate
                cols.append(X[:, c["features"]].mean(1))
            elif c["op"] == "log":                # domain-guarded transform
                v = X[:, c["features"][0]]
                with np.errstate(divide="ignore", invalid="ignore"):
                    cols.append(np.where(v > 1e-12, np.log(
                        np.where(v > 1e-12, v, 1.0)), np.nan))
            elif c["op"] == "powerprod":          # the grown word:
                with np.errstate(all="ignore"):   # |x_i|^e_i products,
                    v = np.ones(len(X))           # domain rows drop
                    for f, e in zip(c["features"], c["exps"]):
                        if e:
                            v = v * np.power(np.abs(X[:, f]), e)
                    cols.append(np.where(np.isfinite(v), v, np.nan))
            else:
                i, j = c["features"][0], c["features"][1]
                with np.errstate(divide="ignore", invalid="ignore"):
                    cols.append(
                        self._COMP_OPS[c["op"]][0](X[:, i], X[:, j]))
        return np.column_stack([X] + cols) if cols else X

    def _applicable_composites(self, d):
        return [c for c in self.composites
                if max(c["features"]) < d
                and (len(c["features"]) == 2
                     or c["op"] in ("mean", "log", "powerprod"))]

    @staticmethod
    def _rename_composites(eq, d_raw, comps):
        """Equation legibility: augmented columns print by their names."""
        for k in range(len(comps) - 1, -1, -1):
            eq = re.sub(rf"\bx{d_raw + k}\b", comps[k]["name"], eq)
        return eq

    def graduate_composite(self, name, X, y, verbose=False):
        """The closing move: if interrogation found the dependence flows
        through a composite, RE-DISCOVER IN THAT COORDINATE — a pattern
        that was out of class in raw coordinates may be plainly sayable
        in the right ones. Returns the law (with the composite named) or
        an honest miss."""
        node = f"x:{name}"
        heur = self.net.get_meta(node, "heuristics")
        if not heur or not heur["composites"]:
            return None
        X = np.asarray(X, float); y = np.asarray(y, float)
        best = max(heur["composites"], key=lambda c: c["invariance"])
        i, j = best["features"]
        op = {"product": (lambda a, b: a * b, "*"),
              "sum": (lambda a, b: a + b, "+"),
              "difference": (lambda a, b: a - b, "-"),
              "ratio": (lambda a, b: a / np.where(np.abs(b) > 1e-9, b,
                                                  np.nan), "/")}[
            best["through"]]
        z = op[0](X[:, i], X[:, j]).reshape(-1, 1)
        res = self.discover(z, y, name=f"{name}_via_composite")
        if res["verdict"] == "UNDERSTOOD":
            eq = res["equation"].replace("x0", f"(x{i}{op[1]}x{j})")
            self.net.set_meta(f"law:{name}_via_composite", "equation", eq)
            self.net.set_meta(node, "status",
                              f"graduated via composite -> {eq[:60]}")
            self.record_finding("graduation", name, equation=eq,
                                r2=res["r2"], via=best["through"])
            if verbose:
                print(f"    graduate_composite[{name}]: {eq[:70]}")
            return dict(status="GRADUATED (via composite)", equation=eq,
                        r2=res["r2"])
        return dict(status="STILL CAPTURED", verdict=res["verdict"],
                    r2=res["r2"])

    def wave_consolidate(self, min_count=5, n_perm=40, verbose=False):
        """IDLE MODE, temporal: crystallize the activation STREAM.

        Where consolidate() compares door profiles (order-blind),
        this compares each instant of the whole matrix to the next:
          groups   — doors that light together (simultaneity, a real thing)
          edges    — one group dims as another lights (the wave moving)
          circles  — waves that return to their start
          level 2  — the same three over circle-activity: patterns of patterns
        Discoveries enter the net as first-class nodes (tag 'wave', order in
        tag 'wave_next') so they can compose upward like anything else.
        Every admission beats a jitter null. Shuffle the log in time and
        the groups survive but every edge and circle dies — that is exactly
        the slice of structure the static crystallizer cannot see."""
        log = self.activation_log
        empty = {"groups": [], "edges": [], "circles": [], "level2": {}}
        if len(log) < 30:
            return empty
        counts = defaultdict(int)
        for fs in log:
            for n in fs:
                counts[n] += 1
        doors = sorted(str(n) for n, c in counts.items() if c >= min_count)
        if len(doors) < 2:
            return empty
        idx = {n: j for j, n in enumerate(doors)}
        S = np.zeros((len(log), len(doors)))
        for t, fs in enumerate(log):
            for n in fs:
                j = idx.get(str(n))
                if j is not None:
                    S[t, j] = 1.0
        groups_ix = _wave_groups(S, n_perm)
        if not groups_ix:
            return empty
        G = np.column_stack([(S[:, list(g)].mean(1) >= 0.5).astype(float)
                             for g in groups_ix])

        # conditional rescue: a door exiled from its group by heavy
        # interference re-joins when membership is re-tested WHERE a candidate
        # blocker is absent — and the blocker is a 'blocks' fact, discovered
        # in the same move. (Occlusion weakens correlation; conditioning on
        # the blocker's absence restores it. Decompose to find comparability.)
        grouped_ix = {j for g in groups_ix for j in g}
        pending_blocks = []
        for j in range(len(doors)):
            if j in grouped_ix or doors[j].startswith("miss:"):
                continue
            x = S[:, j]
            if x.std() < 1e-9:
                continue
            best = None
            for gi in range(len(groups_ix)):
                uncond = float(np.corrcoef(x, G[:, gi])[0, 1])
                for bi in range(len(groups_ix)):
                    if bi == gi:
                        continue
                    off = G[:, bi] == 0
                    if off.sum() < 150:
                        continue
                    xs, gs = x[off], G[off, gi]
                    if xs.std() < 1e-9 or gs.std() < 1e-9:
                        continue
                    c = float(np.corrcoef(xs, gs)[0, 1])
                    null = [abs(float(np.corrcoef(
                        _wave_rng.permutation(xs), gs)[0, 1]))
                        for _ in range(30)]
                    if c > max(2 * np.percentile(null, 95), 0.35) \
                            and c - uncond > 0.1:
                        if best is None or c > best[0]:
                            best = (c, gi, bi)
            if best is not None:
                _, gi, bi = best
                groups_ix[gi] = tuple(sorted(groups_ix[gi] + (j,)))
                pending_blocks.append((bi, doors[j]))
        if pending_blocks:                       # membership changed: re-derive
            G = np.column_stack([(S[:, list(g)].mean(1) >= 0.5).astype(float)
                                 for g in groups_ix])

        groups = [tuple(doors[j] for j in g) for g in groups_ix]
        edges_ix = _wave_edges(G, n_perm)
        circles_ix = _wave_circles(edges_ix, len(groups))

        # discoveries become nodes — same naming shape as type crystals.
        # 'wave' doors: member -> group (identity); 'part' doors: group ->
        # member (so recognize_doors can fire the group from partial members
        # — permanence through the existing organ). Dwell meta = his clock.
        gname = []
        for gi, g in enumerate(groups):
            name = f"wave:{'_'.join(g[:2])}[{len(g)}]"
            gname.append(name)
            col = G[:, gi]
            runs, r = [], 0
            for v in col:
                r = r + 1 if v else (runs.append(r) or 0 if r else 0)
            if r:
                runs.append(r)
            self.net.set_meta(name, "dwell", float(np.mean(runs)) if runs else 3.0)
            for m in g:
                self.net.add_door(m, name, tag="wave")
                self.net.add_door(name, m, tag="part")
                self._teach_fact(m, "part_of", name)
        edges = [(gname[a], gname[b]) for a, b in edges_ix]
        for a, b in edges:
            self.net.add_door(a, b, tag="wave_next")
            # C1 (2026-07-04): a handoff IS an uptake edge, learned — the
            # provider hands ACTIVATION to the consumer. Same structure as
            # taught assemblies, so wholes carry arrangement either way.
            unode = f"uptake:{a}.activation->{b}"
            self.net.add_door(a, unode, tag="provides")
            self.net.add_door(unode, b, tag="feeds")
            self.net.add_door(unode, "activation", tag="carries")
        circles = []
        for c in circles_ix:
            cname = "circle:" + ">".join(groups[i][0] for i in c)
            circles.append(cname)
            for i in c:
                self.net.add_door(gname[i], cname, tag="wave")
                self.net.add_door(cname, gname[i], tag="part")
                self._teach_fact(gname[i], "phase_of", cname)
            seq = [gname[i] for i in c]
            for x, y_ in zip(seq, seq[1:] + seq[:1]):
                unode = f"uptake:{x}.activation->{y_}"
                if self.net.has_door(x, unode):
                    self.net.add_door(cname, unode, tag="arranges")
        for bi, dname in pending_blocks:         # rescue's discovered blockers
            self._teach_fact(gname[bi], "blocks", dname)

        # one level up: each circle's activity is a door; same machinery
        level2 = {}
        if len(circles_ix) >= 2:
            A = np.column_stack([G[:, list(c)].max(1) for c in circles_ix])
            K = np.ones(3) / 3.0                     # smooth handoff flicker
            A = np.column_stack([(np.convolve(A[:, j], K, mode="same") >= 0.5)
                                 .astype(float) for j in range(A.shape[1])])
            keys = [tuple(int(v) for v in r) for r in A]
            uniq = sorted(set(keys))
            if len(uniq) >= 2:
                S2 = np.zeros((len(keys), len(uniq)))
                for t, k in enumerate(keys):
                    S2[t, uniq.index(k)] = 1.0
                e2 = _wave_edges(S2, n_perm)
                level2 = {"states": uniq, "edges": e2,
                          "circles": _wave_circles(e2, len(uniq))}

        # statuses are doors: explain each one WITHIN its entity's own
        # timeframe (the ticks where the tracker had that phase) using the
        # SAME co-activation machinery — explanations EMERGE, then enter the
        # reasoning layer as 'blocks' facts.
        explanations = []
        for sd in [d for d in doors if d.startswith("miss:")]:
            target = sd[5:]
            for gname_t in self.net.get_doors(target, tag="wave"):
                ent_members = set(self.net.get_predecessors(gname_t, tag="wave"))
                for circle, plog in self.phase_log.items():
                    rows = [ti for ti, ph in plog if ph == gname_t and ti < len(log)]
                    if len(rows) < 60:
                        continue
                    cols = [d for d in doors
                            if d not in ent_members
                            and (not d.startswith("miss:") or d == sd)]
                    sub = S[np.array(rows)][:, [idx[d] for d in cols]]
                    for eg in _wave_groups(sub, n_perm):
                        names_e = [cols[j] for j in eg]
                        if sd in names_e:
                            co = [n for n in names_e if n != sd]
                            for c in co:
                                self._teach_fact(c, "blocks", target)
                            for W in set(self.net.get_doors(co[0], tag="wave")) if co else set():
                                if set(self.net.get_predecessors(W, tag="wave")) <= set(co) | {sd}:
                                    self._teach_fact(W, "blocks", target)
                            explanations.append((sd, sorted(co)))

        self.waves = {"groups": groups, "edges": edges, "circles": circles,
                      "circle_orders": [[gname[i] for i in c] for c in circles_ix],
                      "level2": level2, "explanations": explanations}
        if groups:
            self.record_finding(
                "waves", "consolidation", n_groups=len(groups),
                circles=circles, explanations=explanations,
                level2_circles=len(level2.get("circles", [])))
        if verbose:
            print(f"    waves: {len(groups)} groups, {len(edges)} handoffs, "
                  f"{len(circles)} circles, "
                  f"{len(level2.get('circles', []))} level-2 circles, "
                  f"{len(explanations)} explained statuses")
        return self.waves

    def _encode(self, context):
        """Encode context tokens into the input vector.
        Full frame gets highest weight. Partial trailing frames get lower.
        Phase 6: when direct frames miss, try type-member substitution."""
        if not self._compiled:
            return None
        c = self._compiled
        x = np.zeros(len(c["frames"]), dtype=np.float32)

        # Direct frame matching
        frame = tuple(context)
        if frame in c["fidx"]:
            x[c["fidx"][frame]] = 16.0
        for width in range(2, min(len(context) + 1, 8)):
            partial = tuple(context[-width:])
            if partial in c["fidx"] and partial != frame:
                x[c["fidx"][partial]] = float(width)

        # Phase 6: type-level attention
        # If no direct frames matched, try substituting tokens with
        # their type members. Activate ALL matches — let the matmul
        # resolve which type member is most relevant. Weight lower
        # than direct (8.0 vs 16.0) so direct always wins.
        if x.sum() == 0 and self.types:
            for i, token in enumerate(context):
                type_doors = self.net.get_doors(token, tag="type")
                for tname in type_doors:
                    tdata = self.types.get(tname)
                    if not tdata:
                        continue
                    for member in sorted(tdata["members"]):
                        if member == token:
                            continue
                        # Try full frame with this substitution
                        trial = list(context)
                        trial[i] = member
                        trial_frame = tuple(trial)
                        if trial_frame in c["fidx"]:
                            x[c["fidx"][trial_frame]] += 8.0
                        # Try partial frames with substitution
                        for w in range(2, min(len(trial) + 1, 8)):
                            partial = tuple(trial[-w:])
                            if partial in c["fidx"] and partial != trial_frame:
                                x[c["fidx"][partial]] += float(w) * 0.5

        return x if x.sum() > 0 else None

    # ── inference (matrix) ──────────────────────────────────────
    # The THINK loop: recall → process → evaluate → repeat until stable.
    # Memory sends forward. Evaluation sends back. Loop until settled.

    def _route(self, context, mode="lookup", target=None):
        """Stage 3 (ROUTE): single matmul pass. Returns (answer, confidence)."""
        x = self._encode(context)
        if x is None:
            if mode == "check":
                return False, 0.0
            return None, 0.0
        y = self._compiled["W_norm"] @ x
        if mode == "check":
            if target not in self._compiled["didx"]:
                return False, 0.0
            score = float(y[self._compiled["didx"][target]])
            return score >= CONFIDENCE_THRESHOLD, score
        else:
            idx = y.argsort()[-1]
            answer = self._compiled["deltas"][idx]
            conf = float(y[idx])
            if conf < CONFIDENCE_THRESHOLD:
                return None, conf
            return answer, conf

    def _recall(self, context):
        """Stage 2 (STORE/RECALL): What do I know about these tokens?
        Pull types, related tokens, known facts, door profiles.
        This is memory sending information forward to processing."""
        knowledge = {}
        for token in context:
            types = list(self.net.get_doors(token, tag="type"))
            successors = self.net.get_doors(token, tag="seq")
            predecessors = self.net.get_predecessors(token, tag="seq")
            # Tokens with rich profiles are well-known.
            # Tokens with empty profiles are novel/unknown.
            type_members = set()
            for t in types:
                for n in self.net.all_nodes():
                    if t in self.net.get_doors(n, tag="type"):
                        type_members.add(n)
                type_members.discard(token)
            knowledge[token] = {
                "types": types,
                "successors": successors,
                "predecessors": predecessors,
                "type_members": type_members,
                "known": len(successors) > 0 or len(predecessors) > 0,
            }
        return knowledge

    def _evaluate(self, answer, conf, context, knowledge, mode):
        """Stage 4 (EVALUATE): Is this answer good? What should we do next?
        Returns a verdict dict — stable, or what to try next.
        This is evaluation sending feedback back to memory/processing.

        Critical distinction:
          - conf > 0 but < threshold: system has SOME info, just weak → don't substitute
          - conf == 0 and no frames match: genuine unknown → try substitution
          - answer found but wrong target: definite no, not unknown"""
        verdict = {"stable": False, "answer": answer, "conf": conf}

        # Confident answer → stable
        if conf >= CONFIDENCE_THRESHOLD:
            verdict["stable"] = True
            return verdict

        # Check: did the encoding produce ANY activation?
        # If yes, the system has info — just not for this target.
        # That's a real 'no', not an 'I don't know'.
        has_some_info = False
        if self._compiled:
            x = self._encode(context)
            if x is not None:
                y = self._compiled["W_norm"] @ x
                if y.max() >= CONFIDENCE_THRESHOLD:
                    has_some_info = True

        # Which tokens are unknown?
        unknown_tokens = [t for t in context
                          if not knowledge.get(t, {}).get("known", False)]
        known_tokens = [t for t in context
                        if knowledge.get(t, {}).get("known", False)]

        verdict["unknown_tokens"] = unknown_tokens
        verdict["known_tokens"] = known_tokens

        # If we have unknown tokens, suggest dropping them
        if unknown_tokens and len(known_tokens) >= 2:
            verdict["try_known_only"] = known_tokens

        # Only try type substitution when the system has NO info at all.
        # If it has info but the target doesn't match, that's a real 'no'.
        elif not unknown_tokens and not has_some_info:
            verdict["try_type_substitution"] = True

        return verdict

    def _think(self, context, mode="lookup", target=None, max_cycles=5):
        """Stages 2/3/4 loop. Recall → Process → Evaluate → repeat.

        Memory sends knowledge forward to processing.
        Processing sends results forward to evaluation.
        Evaluation sends feedback back to memory/processing.
        Loop until the answer stabilizes or we've exhausted what we know.

        Exit conditions (governor):
          1. Confidence >= threshold → stable
          2. Evaluation says stable (exhausted all strategies)
          3. Max cycles reached
        """
        self._ensure_compiled()
        if not self._compiled:
            return (None, 0.0) if mode == "lookup" else (False, 0.0)

        # wave sensing: thinking about a context IS simultaneous activation
        if self.wave_logging and context:
            self.tick(set(context))

        # ── Stage 2: RECALL — what do I know about this? ────────
        knowledge = self._recall(context)

        best_answer = None
        best_conf = 0.0
        tried = set()  # track what we've already attempted

        for cycle in range(max_cycles):
            # ── Stage 3: PROCESS — compute against what I know ──
            context_key = tuple(context)
            if context_key not in tried:
                tried.add(context_key)
                answer, conf = self._route(context, mode, target)

                if conf > best_conf:
                    best_answer, best_conf = answer, conf

                # ── Stage 4: EVALUATE — is this good enough? ────
                verdict = self._evaluate(answer, conf, context, knowledge, mode)

                if verdict["stable"]:
                    return answer, conf

            # ── Evaluation feedback → back to memory/processing ─
            # The verdict tells us what to try next

            # Strategy A: drop unknown tokens, keep what we know
            known_only = verdict.get("try_known_only")
            if known_only and tuple(known_only) not in tried:
                context = known_only
                # Recall again with the simplified context
                knowledge = self._recall(context)
                continue

            # Strategy B: type substitution — replace unknown tokens
            # with type members from related known tokens
            if verdict.get("try_type_substitution"):
                found = False
                for i, token in enumerate(context):
                    members = knowledge.get(token, {}).get("type_members", set())
                    for member in sorted(members):
                        trial = list(context)
                        trial[i] = member
                        trial_key = tuple(trial)
                        if trial_key not in tried:
                            tried.add(trial_key)
                            answer, conf = self._route(trial, mode, target)
                            if conf > best_conf:
                                best_answer, best_conf = answer, conf
                            if conf >= CONFIDENCE_THRESHOLD:
                                return answer, conf
                            found = True
                if found:
                    continue

            # Strategy C: try each known token paired with the tail
            # (verb-level: "smash" + "result")
            if len(context) > 2:
                tail = context[-1]
                for token in context[:-1]:
                    pair_key = (token, tail)
                    if pair_key not in tried:
                        tried.add(pair_key)
                        answer, conf = self._route(list(pair_key), mode, target)
                        if conf > best_conf:
                            best_answer, best_conf = answer, conf
                        if conf >= CONFIDENCE_THRESHOLD:
                            return answer, conf

            # Nothing more to try — return best we found
            break

        return best_answer, best_conf

    def lookup(self, context, top_k=5):
        """Argmax over the output vector. 'What comes next?'
        Routes through the think loop — recall, process, evaluate."""
        return self._think(context, mode="lookup")

    def check(self, context, target):
        """Read a SPECIFIC cell in y. 'Is THIS claim true?'
        Routes through the think loop — recall, process, evaluate."""
        return self._think(context, mode="check", target=target)

    # ── walking (net) ───────────────────────────────────────────

    def predict_next(self, context, tag="seq"):
        """Convergence voting from context words. For language, not math."""
        if not context:
            return None
        votes = defaultdict(int)
        voters = defaultdict(list)
        for word in context:
            for tgt in self.net.get_doors(word, tag=tag):
                if (word, tgt) not in self.lockouts:
                    votes[tgt] += 1
                    voters[tgt].append(word)
        if not votes:
            return None
        max_votes = max(votes.values())
        candidates = [c for c, v in votes.items() if v == max_votes]

        def recency(c):
            positions = [context.index(w) for w in voters[c] if w in context]
            return max(positions) if positions else -1
        winner = max(candidates, key=recency)
        return {"prediction": winner, "votes": votes[winner],
                "total_voters": len(context),
                "all_candidates": dict(votes)}

    def walk_chain(self, start, tag="seq", max_steps=20):
        """Walk forward from start, following doors."""
        chain = [start]
        current = start
        visited = {start}
        for _ in range(max_steps):
            nexts = self.net.get_doors(current, tag=tag) - visited
            nexts = {n for n in nexts if (current, n) not in self.lockouts}
            if not nexts:
                break
            best = max(nexts, key=lambda n: (
                self.net.get_meta(n, "initiator_strength") or 0, n))
            chain.append(best)
            visited.add(best)
            current = best
        return chain

    def transduce(self, start, stream, into="state", halt=None,
                  max_steps=None, verbose=False):
        """Universal state walk over an input stream — the missing primitive.

        Thread a state through a sequence of input symbols. At each step the
        NEXT state is chosen by HIS matrix: lookup([state, symbol]) -> state'.
        The transition function delta(state, symbol)=state' lives entirely in
        learned doors (a real frame->delta), so no task logic sits in Python.

        This is the finite-state-transducer / Turing-head shape: the loop here
        is the universal tape-reader (general, the same for every machine); the
        PROGRAM is whatever transitions were taught. Counting, parity, motion,
        and the game loop all reuse this — they differ only in their doors.

        The state is held in a working-memory register (`into`), so it lives in
        HIM across steps — read from scratch and written back each step. The
        harness loop holds nothing but the next symbol.

        Returns (final_state, trace). final_state is None on an honest shrug
        (no transition learned for some [state, symbol]); trace is the register's
        full step-history (scratch.history(into)).
        """
        self.scratch.clear(into)                       # fresh episode
        self.scratch.write(into, start)                # state lives in HIM
        steps = 0
        for symbol in stream:
            state = self.scratch.read(into)            # he reads his own state
            nxt, conf = self.lookup([state, symbol])   # his matmul decides
            if nxt is None or conf < CONFIDENCE_THRESHOLD:
                if verbose:
                    print(f"    shrug at step {steps}: no door for "
                          f"[{state}, {symbol}]")
                return None, self.scratch.history(into)  # honest: rule unlearned
            self.scratch.write(into, nxt)              # he writes it back into himself
            steps += 1
            if verbose:
                print(f"    {symbol:>4} -> {nxt}  (conf {conf:.1f})")
            if halt is not None and nxt == halt:
                break
            if max_steps is not None and steps >= max_steps:
                break
        return self.scratch.read(into), self.scratch.history(into)

    def _apply_op(self, op, target):
        """The tiny ALU: execute one named op against a working register.
        Fixed instruction set (like a CPU's decoder); the PROGRAM — which op to
        run when — is in his net, not here."""
        if op == "incr":
            self.scratch.incr(target)
        elif op == "hold":
            pass
        elif op == "reset":
            self.scratch.write(target, 0)
        elif op == "mark":
            self.scratch.latch(target + "_seen")
        else:
            return False                               # unknown op -> shrug
        return True

    def react(self, stream, target="acc", verbose=False):
        """Run an input stream against his ACTION doors, updating working memory
        in real time. For each symbol his matrix says what to DO
        (lookup([symbol]) -> an op token); the ALU applies it to `target`.

        The program (which op fires for which symbol) is HIS — learned doors.
        The register is HIS. Only 'apply a named op' is engine plumbing. This is
        counting-without-a-state-ladder: 'on'->incr, 'off'->hold lets him count
        to ANY N with two doors, because the magnitude lives in RAM, not in the
        graph as N separate nodes.
        """
        self.scratch.clear(target)                     # fresh episode
        self.scratch.write(target, 0)
        for symbol in stream:
            op, conf = self.lookup([symbol])           # his matmul: what to do
            if op is None or conf < CONFIDENCE_THRESHOLD:
                if verbose:
                    print(f"    {symbol:>4}: (no instruction — skip)")
                continue
            self._apply_op(op, target)
            if verbose:
                print(f"    {symbol:>4} -> {op:<6} {target}={self.scratch.read(target)}")
        return self.scratch.read(target), self.scratch.history(target)

    def generate(self, concept, tag="seq"):
        """Generate a sequence containing the concept.
        Trace backward to find an initiator, then forward to completion."""
        backward = []
        current = concept
        visited = {concept}
        for _ in range(10):
            preds = self.net.get_predecessors(current, tag=tag)
            preds = {p for p in preds if p not in visited
                     and (p, current) not in self.lockouts}
            if not preds:
                break
            starts = {p for p in preds if self.net.get_meta(p, "start")}
            if starts:
                best = max(starts, key=lambda p: (
                    self.net.get_meta(p, "initiator_strength") or 0))
                backward.append(best)
                break
            best = max(preds, key=lambda p: len(self.net.get_doors(p, tag=tag)))
            backward.append(best)
            visited.add(best)
            current = best
        backward.reverse()
        chain = backward + [concept]
        current = concept
        for _ in range(10):
            nexts = self.net.get_doors(current, tag=tag) - visited
            nexts = {n for n in nexts if (current, n) not in self.lockouts}
            if not nexts:
                break
            best = sorted(nexts)[0]
            chain.append(best)
            visited.add(best)
            current = best
            if best in (".", "!", "?", "="):
                break
        return chain

    def check_connection(self, src, tgt):
        """Is src→tgt valid? Walk the full net to check. Returns (valid, manifest)."""
        manifest = {"direct_seq": False, "direct_neg": False,
                    "lockout": False, "types_checked": [],
                    "type_support": 0, "type_contradict": 0}
        tags = self.net.get_door_tags(src, tgt)
        if "seq" in tags:
            manifest["direct_seq"] = True
        if "neg" in tags:
            manifest["direct_neg"] = True
        if (src, tgt) in self.lockouts:
            manifest["lockout"] = True
            return False, manifest
        src_types = self.net.get_doors(src, tag="type")
        for t in src_types:
            members = {n for n in self.net.all_nodes()
                       if t in self.net.get_doors(n, tag="type")}
            members.discard(src)
            support = any(self.net.has_door(m, tgt) for m in members)
            manifest["types_checked"].append({"type": t, "support": support})
            if support:
                manifest["type_support"] += 1
            else:
                manifest["type_contradict"] += 1
        valid = manifest["direct_seq"] or manifest["type_support"] > 0
        if manifest["lockout"]:
            valid = False
        return valid, manifest

    def compare_nodes(self, a, b, tag=None):
        """Structural comparison of two nodes."""
        return {
            "outgoing": compare(set(self.net.get_doors(a, tag=tag)),
                                set(self.net.get_doors(b, tag=tag))),
            "incoming": compare(self.net.get_predecessors(a, tag=tag),
                                self.net.get_predecessors(b, tag=tag)),
        }

    def infer(self, src, tgt, tag="seq"):
        """Can src connect to tgt? Walk types to find out."""
        src_types = self.net.get_doors(src, tag="type")
        for t in src_types:
            members = {n for n in self.net.all_nodes()
                       if t in self.net.get_doors(n, tag="type")}
            for m in members:
                if m != src and self.net.has_door(m, tgt):
                    self.net.add_door(src, tgt, tag=tag)
                    return {"inferred": True, "via": m, "type": t}
        return {"inferred": False}

    # ── crystal: transplant a net/features into box-concepts IN THE NET ──

    def fit_lens(self, name, X, y=None, lift=0, select=None, seed=0,
                 rotate=True):
        """Register an ALIGNER as net infrastructure: optional random lift
        (spread the data so classes pull apart) + basis-first alignment +
        discriminative dim-select. Lives in the net as a 'lens:<name>' node.

        The default alignment is now the NULL-GATED BASIS (the learned aligner
        this slot was reserved for): standardize, then rotate only along
        correlations that beat the sampling null (~3/sqrt(n)) — the basis
        itself must beat chance, otherwise near-identity eigenvectors are
        noise-driven arbitrary rotations. rotate=False restores plain
        strip-DC."""
        g = np.random.default_rng(seed); R = b = None; H = np.asarray(X, float)
        if lift:
            R = g.standard_normal((H.shape[1], lift)) / np.sqrt(H.shape[1])
            b = g.standard_normal(lift) * 0.1
            H = np.maximum(H @ R + b, 0.0)
        mu = sd = rot = None
        dc = H.mean(0)
        if rotate and len(H) >= 30:
            mu, sd = H.mean(0), H.std(0) + 1e-12
            Z = (H - mu) / sd
            C = np.nan_to_num(np.corrcoef(Z, rowvar=False))
            gate = np.abs(C) >= 3.0 / np.sqrt(len(Z))
            np.fill_diagonal(gate, True)
            w, V = np.linalg.eigh(np.where(gate, C, 0.0))
            rot = V[:, np.argsort(-w, kind="stable")]
            Hc = Z @ rot
        else:
            Hc = H - dc
        dims = (_fisher(Hc, y, select)
                if (select and y is not None and select < Hc.shape[1]) else None)
        node = f"lens:{name}"
        self.net.add_door("lens", node, tag="lens")
        self.net.set_meta(node, "transform",
                          dict(R=R, b=b, dc=dc, mu=mu, sd=sd, rot=rot, dims=dims))
        return name

    def apply_lens(self, name, X):
        """Run an input through a registered lens. None = identity."""
        if name is None:
            return np.asarray(X, float)
        t = self.net.get_meta(f"lens:{name}", "transform") or {}
        H = np.asarray(X, float)
        if t.get("R") is not None:
            H = np.maximum(H @ t["R"] + t["b"], 0.0)
        if t.get("rot") is not None:
            H = ((H - t["mu"]) / t["sd"]) @ t["rot"]
        elif t.get("dc") is not None:
            H = H - t["dc"]
        if t.get("dims") is not None:
            H = H[:, t["dims"]]
        return H

    @staticmethod
    def _compound_bins(H, nb=8, cedges=None):
        """Quantile-bin lensed features for compound-door evaluation."""
        if cedges is None:
            qs = np.linspace(0, 100, nb + 1)[1:-1]
            cedges = np.stack([np.percentile(H[:, j], qs)
                               for j in range(H.shape[1])])
        B = np.column_stack([np.searchsorted(cedges[j], H[:, j])
                             for j in range(H.shape[1])]).astype(int)
        return B, cedges

    @staticmethod
    def _compound_indicators(B, spec):
        if not spec:
            return np.empty((len(B), 0))
        return np.column_stack([((B[:, f1] == b1) & (B[:, f2] == b2))
                                .astype(float) for f1, b1, f2, b2 in spec])

    def _mine_compound_doors(self, H, y, bins, nb=6, n_perm=20,
                             top_feats=6, max_pairs=3, keep_per_pair=30):
        """C2 (2026-07-04), migrated from the covtype harness: COMPOUND
        DOORS behind the CEILING TRIGGER (audit 2.11, now wired). When flat
        doors leave held-out confusions, mine conjunction doors ('feature i
        in bin a AND feature j in bin b') per confused class pair; a
        compound is admitted only when its joint separation beats its best
        PART by a margin surviving a label-permutation null (selection-
        corrected max-gain, 95th pct). Kept only if held-out accuracy
        actually improves. Returns (spec, cedges, report)."""
        n, d = H.shape
        classes = np.unique(y)
        report = dict(trigger="silent", admitted=0, kept=False)
        if n < 200 or d < 2 or len(classes) < 2:
            report["why"] = "too little data/dims/classes to mine"
            return [], None, report
        rng = np.random.default_rng(11)
        idx = rng.permutation(n)
        cut = int(0.75 * n)
        tr, he = idx[:cut], idx[cut:]
        qs = np.linspace(0, 100, bins + 1)[1:-1]

        def flat_fit(Ht, yt):
            e = np.stack([np.percentile(Ht[:, j], qs)
                          for j in range(Ht.shape[1])])
            mods = []
            for c in classes:
                obs = Ht[yt == c]
                ld = np.empty((Ht.shape[1], bins))
                for j in range(Ht.shape[1]):
                    cnt = np.bincount(np.searchsorted(e[j], obs[:, j]),
                                      minlength=bins).astype(float)
                    ld[j] = np.log((cnt + 1.0) / (cnt.sum() + bins))
                mods.append(ld)
            return e, mods

        def flat_predict(e, mods, Hs):
            sc = np.zeros((len(Hs), len(classes)))
            for j in range(Hs.shape[1]):
                ix = np.searchsorted(e[j], Hs[:, j])
                for k, ld in enumerate(mods):
                    sc[:, k] += ld[j][ix]
            return classes[np.argmax(sc, axis=1)]

        e0, m0 = flat_fit(H[tr], y[tr])
        pred = flat_predict(e0, m0, H[he])
        acc_flat = float((pred == y[he]).mean())
        conf = defaultdict(int)
        for a, b in zip(y[he], pred):
            if a != b:
                conf[(min(a, b), max(a, b))] += 1
        top = sorted(conf, key=conf.get, reverse=True)[:max_pairs]
        if not top or conf[top[0]] < 10:
            report["why"] = f"no confusable pair (held acc {acc_flat:.3f})"
            return [], None, report
        report["trigger"] = "fired"
        report["pairs"] = [tuple(int(v) for v in p) for p in top]

        B, cedges = self._compound_bins(H, nb)
        spec = []
        for a, b in top:
            sa = B[tr][y[tr] == a][:10000]
            sb = B[tr][y[tr] == b][:10000]
            marg = np.zeros((d, nb))
            for j in range(d):
                pa = np.bincount(sa[:, j], minlength=nb) / max(len(sa), 1)
                pb = np.bincount(sb[:, j], minlength=nb) / max(len(sb), 1)
                marg[j] = np.abs(pa - pb)
            frank = np.argsort(-marg.max(axis=1))[:top_feats]

            # NOTE: the covtype harness skipped bins with marginal
            # separation < 0.02 as a work-saver — a hard gate that BLOCKED
            # pure-XOR structure, where marginals are exactly zero and the
            # signal lives ONLY in the conjunction (battery X1 caught it).
            # Pruning is not statistics; the permutation null is the gate.
            def gains(A, B_):
                out = []
                for fi in range(len(frank)):
                    for fj in range(fi + 1, len(frank)):
                        f1, f2 = int(frank[fi]), int(frank[fj])
                        for b1 in range(nb):
                            m1a = A[:, f1] == b1
                            m1b = B_[:, f1] == b1
                            for b2 in range(nb):
                                ja = float((m1a & (A[:, f2] == b2)).mean())
                                jb = float((m1b & (B_[:, f2] == b2)).mean())
                                g = abs(ja - jb) - max(marg[f1, b1],
                                                       marg[f2, b2])
                                if g > 0:
                                    out.append((g, f1, b1, f2, b2))
                return out

            real = gains(sa, sb)
            if not real:
                continue
            pool = np.vstack([sa, sb])
            na = len(sa)
            null_max = np.empty(n_perm)
            for k in range(n_perm):
                p = rng.permutation(len(pool))
                nl = gains(pool[p[:na]], pool[p[na:]])
                null_max[k] = max((g for g, *_ in nl), default=0.0)
            thr = np.percentile(null_max, 95)
            surv = sorted([r for r in real if r[0] > thr], reverse=True)
            spec += [(f1, b1, f2, b2)
                     for _, f1, b1, f2, b2 in surv[:keep_per_pair]]
        seen = set()
        spec = [c for c in spec if not (c in seen or seen.add(c))][:60]
        report["admitted"] = len(spec)
        if not spec:
            report["why"] = "no compound survived its null"
            return [], None, report
        # the keep decision: held-out accuracy must actually improve
        Haug = np.column_stack([H, self._compound_indicators(B, spec)])
        e1, m1 = flat_fit(Haug[tr], y[tr])
        acc_aug = float((flat_predict(e1, m1, Haug[he]) == y[he]).mean())
        report["held_flat"], report["held_aug"] = acc_flat, acc_aug
        if acc_aug <= acc_flat:
            report["why"] = "compounds admitted but did not improve held-out"
            return [], None, report
        report["kept"] = True
        return spec, cedges, report

    def crystallize_features(self, X, y, lens=None, margin=1.5, bins=12,
                             compounds="auto"):
        """Transplant: one concept per class as a NODE in the net, tagged
        'crystal'. The concept's doors are now OBSERVED DISTRIBUTIONS
        (quantile-binned per-dim log-densities) — observe + matmul, not a
        fitted box. Boxes were a ceiling: they cap on diagonal data and flip
        verdicts under re-encoding (rebuild A head-to-head). The legacy box
        meta is still written so recognize_matrix and old scripts keep
        running; classification no longer uses it.
        compounds='auto' (C2, 2026-07-04): when flat doors leave held-out
        confusions, conjunction doors are mined per confused pair
        (null-gated, kept only if held-out improves) and joined to the
        feature set; classify_features augments identically."""
        H = self.apply_lens(lens, np.asarray(X, float))
        comp_spec, comp_edges, comp_report = [], None, None
        if compounds == "auto":
            comp_spec, comp_edges, comp_report = \
                self._mine_compound_doors(H, np.asarray(y), bins)
            if comp_spec:
                B, _ = self._compound_bins(H, cedges=comp_edges)
                H = np.column_stack([H,
                                     self._compound_indicators(B, comp_spec)])
        d = H.shape[1]
        qs = np.linspace(0, 100, bins + 1)[1:-1]
        edges = np.stack([np.percentile(H[:, j], qs) for j in range(d)])
        Hq, qlo, qhi = _quantize(H)
        for c in np.unique(y):
            obs = H[y == c]
            ld = np.empty((d, bins))
            for j in range(d):
                cnt = np.bincount(np.searchsorted(edges[j], obs[:, j]),
                                  minlength=bins).astype(float)
                ld[j] = np.log((cnt + 1.0) / (cnt.sum() + bins))
            node = f"concept:{c}"
            self.net.add_door("crystal", node, tag="crystal")
            self.net.set_meta(node, "doors", ld)          # observed densities
            self.net.set_meta(node, "label", c)
            obs_q = Hq[y == c]                            # legacy box, kept
            self.net.set_meta(node, "box", dict(
                lo=np.percentile(obs_q, 1, axis=0) - margin,
                hi=np.percentile(obs_q, 95, axis=0) + margin,
                med=np.median(obs_q, axis=0)))
        self.net.set_meta("crystal", "calib",
                          dict(qlo=qlo, qhi=qhi, lens=lens, edges=edges,
                               compounds=comp_spec, cedges=comp_edges,
                               compound_report=comp_report))
        return sorted(self.net.get_doors("crystal", tag="crystal"))

    def classify_features(self, X):
        """Classify by summed log-likelihood over each concept's observed
        density doors — graded membership, one matmul-shaped decision.
        Lens + doors both live in the net."""
        calib = self.net.get_meta("crystal", "calib")
        H = self.apply_lens(calib["lens"], np.atleast_2d(np.asarray(X, float)))
        if calib.get("compounds"):
            B, _ = self._compound_bins(H, cedges=calib["cedges"])
            H = np.column_stack([H, self._compound_indicators(
                B, calib["compounds"])])
        edges = calib["edges"]
        concepts = [(self.net.get_meta(n, "label"), self.net.get_meta(n, "doors"))
                    for n in sorted(self.net.get_doors("crystal", tag="crystal"))]
        n, d = H.shape
        scores = np.zeros((n, len(concepts)))
        for j in range(d):
            idx = np.searchsorted(edges[j], H[:, j])
            for k, (_, ld) in enumerate(concepts):
                scores[:, k] += ld[j][idx]
        labels = np.array([lab for lab, _ in concepts], dtype=object)
        return labels[np.argmax(scores, axis=1)]

    # ── recognition by PARTIAL DOOR OVERLAP (recursive) ──

    def recognize_doors(self, active, tag="part", threshold=0.5, max_loops=12):
        """Recognize concepts by how many of their defining doors are present —
        partial, not all-or-nothing. A concept is a node with out-doors (tagged
        `tag`) to its parts; its score is the fraction of those doors present in
        `active`, weighted by each part's confidence (his compare 'similarity',
        carried). A concept that clears `threshold` joins `active` with its score,
        which lets HIGHER concepts (whose doors point to it) fire in turn. Loop
        until nothing new fires — on a finite net that always halts. So '10 of a
        concept's 12 doors present' -> 0.83 -> it fires, and its 0.83 flows up.

        active: an iterable of present nodes, or {node: confidence}.
        Returns {concept: score} for every concept that fired, all levels."""
        active = dict(active) if isinstance(active, dict) else {n: 1.0 for n in active}
        fired = {}
        for _ in range(max_loops):
            changed = False
            for node in self.net.all_nodes():
                doors = self.net.get_doors(node, tag)
                if not doors:
                    continue
                score = sum(active.get(d, 0.0) for d in doors) / len(doors)
                if score >= threshold and score > active.get(node, 0.0):
                    active[node] = fired[node] = score
                    changed = True
            if not changed:                       # stabilized: finite net is exhausted
                break
        return fired

    # ── recognition by the PADDED CONCEPT-MATRIX (box-friendly + padding) ──

    def recognize_matrix(self, X, rule="count", mask=None):
        """The working matrix: every box-concept is a ROW (its [lo,hi,med] across
        F dims, padded to F); a per-concept 0/1 MASK marks its committed slots
        (its real list vs padding). Score by PARTIAL OVERLAP over committed dims —
        ported from range_classifier/v3 fastscore, fed by crystallize_features.
          rule='count'   : # committed dims in range (membership), median-dist tiebreak
                           — all-ones mask reproduces classify_features (the box reader)
          rule='deepest' : fires if ALL committed satisfied; deepest fired wins;
                           else most-satisfied partial ('10 of 12'). Length-aware.
        Returns predicted labels (B,)."""
        calib = self.net.get_meta("crystal", "calib")
        H = self.apply_lens(calib["lens"], np.atleast_2d(np.asarray(X, float)))
        Xq, _, _ = _quantize(H, calib["qlo"], calib["qhi"])
        nodes = sorted(self.net.get_doors("crystal", tag="crystal"))
        LO = np.array([self.net.get_meta(n, "box")["lo"] for n in nodes])
        HI = np.array([self.net.get_meta(n, "box")["hi"] for n in nodes])
        MED = np.array([self.net.get_meta(n, "box")["med"] for n in nodes])
        labels = np.array([self.net.get_meta(n, "label") for n in nodes])
        N, F = LO.shape
        if mask is None:
            mask = np.ones((N, F))
        Xq = np.asarray(Xq, float); B = Xq.shape[0]
        BIG = 16.0 * F + 1.0
        if rule == "count":
            cnt = np.empty((B, N)); dist = np.empty((B, N))
            for c in range(N):
                inr = (Xq >= LO[c]) & (Xq <= HI[c]); w = inr * mask[c]
                cnt[:, c] = w.sum(1); dist[:, c] = (np.abs(Xq - MED[c]) * w).sum(1)
            key = cnt * BIG - dist
        elif rule == "deepest":                          # bundle-match + significant-digit
            depth = mask.sum(1); W1 = BIG; W2 = (F + 1.0) * W1
            fires = np.empty((B, N)); satisf = np.empty((B, N)); dist = np.empty((B, N))
            for c in range(N):
                inr = (Xq >= LO[c]) & (Xq <= HI[c]); comm = mask[c].astype(bool)
                m = int(comm.sum())
                s = inr[:, comm].sum(1) if m else np.zeros(B)
                satisf[:, c] = s; fires[:, c] = (s == m) if m else 1.0
                dist[:, c] = (np.abs(Xq - MED[c]) * (inr * mask[c])).sum(1)
            fb = fires.astype(bool)
            key = fb * W2 + np.where(fb, depth[None], satisf) * W1 - dist
        elif rule == "avgdiff":                          # arity-normalized (length-fair)
            depth = mask.sum(1); BIGA = 1e9; BIGB = 1e3
            avgdiff = np.empty((B, N)); avgmed = np.empty((B, N))
            for c in range(N):
                comm = mask[c].astype(bool); m = max(int(comm.sum()), 1)
                gap = np.maximum.reduce([LO[c] - Xq, Xq - HI[c], np.zeros_like(Xq)])
                avgdiff[:, c] = gap[:, comm].sum(1) / m
                avgmed[:, c] = (np.abs(Xq - MED[c])[:, comm]).sum(1) / m
            key = -avgdiff * BIGA + depth[None] * BIGB - avgmed
        else:
            raise ValueError(f"unknown rule {rule!r}")
        return labels[key.argmax(1)]

    # ── sense routing: internal node routers (conditional / binding) ──

    def crystallize_senses(self, node, min_shared=2, n_shuffles=20):
        """SENSES ARE THINGS (2026-07-04). Split a node's occurrences into
        sense-sections and mint each as a FIRST-CLASS NODE with directed
        doors — not a meta side-channel. Each occurrence carries its context;
        occurrences sharing >= min_shared context tokens link into candidate
        senses (the crystallizer turned inward). Then the owner's laws:
        - NULL-GATED ADMISSION: each candidate is scored against a chance
          null that destroys exactly the claimed structure — the same
          occurrences with their context tokens reshuffled (context sizes and
          token frequencies preserved), scored by the BEST sense chance
          produces (selection-corrected). Failures are KEPT and classified
          wrong with the why (`isaac.wrong_senses`), never deleted.
        - DOORS, NOT BLOBS: sense node `sense:<node>#<gen>.<k>` gets
          node→sense (tag "sense"), pred→sense and sense→succ (tag
          "sense_seq" — direction is real doors now), sense→context tokens
          (tag "sense_ctx"). Every net-walker can see sense structure.
        - SUPERSESSION on re-run: the previous generation is demoted
          (verdict "superseded", kept in the net), never overwritten."""
        occ = []  # (context_set, pred, succ) per occurrence
        for seq in self.observed_sequences:
            for k, t in enumerate(seq):
                if t == node:
                    occ.append((set(seq) - {node},
                                seq[k - 1] if k > 0 else None,
                                seq[k + 1] if k + 1 < len(seq) else None))
        n = len(occ)

        def _cluster(contexts):
            parent = list(range(len(contexts)))
            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]; x = parent[x]
                return x
            for a in range(len(contexts)):
                for b in range(a + 1, len(contexts)):
                    if len(contexts[a] & contexts[b]) >= min_shared:
                        parent[find(a)] = find(b)
            comps = defaultdict(list)
            for i in range(len(contexts)):
                comps[find(i)].append(i)
            return list(comps.values())

        def _score(members, contexts):
            # coherence = (extra occurrences) x (context core ALL of them share)
            if len(members) < 2:
                return 0
            core = set(contexts[members[0]])
            for m in members[1:]:
                core &= contexts[m]
            return (len(members) - 1) * len(core)

        contexts = [c for c, _, _ in occ]
        clusters = _cluster(contexts)

        # the chance null: same context sizes, same token pool, membership
        # destroyed — what does the BEST shuffled sense score?
        pool = [t for c in contexts for t in sorted(c)]  # sorted: the null
        # must not depend on set iteration order (hash randomization)
        chance_best = 0
        if pool and n >= 2:
            srng = np.random.default_rng(len(pool) * 31 + n)
            for _ in range(n_shuffles):
                sh = list(srng.permutation(pool))
                shuffled, pos = [], 0
                for c in contexts:
                    shuffled.append(set(sh[pos:pos + len(c)]))
                    pos += len(c)
                for members in _cluster(shuffled):
                    chance_best = max(chance_best,
                                      _score(members, shuffled))

        # supersession: the previous generation is demoted, never erased
        gen = (self.net.get_meta(node, "sense_gen") or 0) + 1
        for old in self.net.get_doors(node, tag="sense"):
            if self.net.get_meta(old, "verdict") != "superseded":
                self.net.set_meta(old, "verdict", "superseded")
                self.net.set_meta(old, "superseded_by_gen", gen)
        self.net.set_meta(node, "sense_gen", gen)

        if not hasattr(self, "wrong_senses"):
            self.wrong_senses = {}
        senses = []
        for k, members in enumerate(clusters):
            s = {"in": set(), "out": set(), "context": set()}
            for i in members:
                ctx, p, su = occ[i]
                if p: s["in"].add(p)
                if su: s["out"].add(su)
                s["context"] |= ctx
            score = _score(members, contexts)
            name = f"sense:{node}#{gen}.{k}"
            s["name"], s["n_occurrences"], s["score"] = name, len(members), score
            if score <= chance_best:
                s["verdict"] = "wrong"
                s["why_wrong"] = (f"context coherence {score} within chance "
                                  f"(best shuffled sense scores {chance_best})"
                                  f" — token co-occurrence alone explains it")
                self.wrong_senses[name] = s
                self.net.set_meta(name, "why_wrong", s["why_wrong"])
            else:
                s["verdict"] = "sound"
            # the doors — direction is net structure, not an annotation
            self.net.add_door(node, name, tag="sense")
            for p in s["in"]:
                self.net.add_door(p, name, tag="sense_seq")
            for su in s["out"]:
                self.net.add_door(name, su, tag="sense_seq")
            for c in s["context"]:
                self.net.add_door(name, c, tag="sense_ctx")
            self.net.set_meta(name, "verdict", s["verdict"])
            self.net.set_meta(name, "of_node", node)
            self.net.set_meta(name, "n_occurrences", len(members))
            self.net.set_meta(name, "score", score)
            senses.append(s)
        # legacy mirror (pre-2026-07-04 readers); the doors are authoritative
        self.net.set_meta(node, "senses", senses)
        return senses

    def route(self, node, incoming):
        """Route through the node by which sense the incoming context matches
        — READ FROM THE DOORS. Only SOUND senses compete (wrong and
        superseded are demoted from the comparison set, never deleted —
        law 4). incoming = a token or a set of context tokens. Returns the
        winning sense's out-doors; falls back to the flat door-set when no
        sound sense matches."""
        inc = {incoming} if isinstance(incoming, str) else set(incoming)
        best, best_ov = None, 0
        for sense in self.net.get_doors(node, tag="sense"):
            if self.net.get_meta(sense, "verdict") != "sound":
                continue
            in_doors = self.net.get_predecessors(sense, tag="sense_seq")
            ctx = self.net.get_doors(sense, tag="sense_ctx")
            ov = len(inc & (in_doors | ctx))
            if ov > best_ov:
                best_ov, best = ov, sense
        if best is None:
            return set(self.net.get_doors(node, tag="seq"))
        return set(self.net.get_doors(best, tag="sense_seq"))

    # ── composition: wholes with ARRANGEMENT (uptake edges) ─────────
    # C1 (2026-07-04), migrated from rebuild B (7/7): a whole is parts +
    # uptake edges (provider --affordance--> consumer), not a member bag.
    # Emergence = interlocking affordances; configuration IS the edge set.
    # Everything is net structure: offer:<part>.<aff> nodes carry offers,
    # uptake:<src>.<aff>-><dst> nodes carry arrangement, whole:<name>
    # arranges them. Wave circles write the SAME structure (learned
    # arrangement); assemblies are taught (proposal principle).

    def register_part(self, name, offers):
        """Teach a part: offers = {affordance: iterable of requirements}.
        A requirement-free offer is what the part can do ALONE."""
        for aff, req in offers.items():
            onode = f"offer:{name}.{aff}"
            self.net.add_door(name, onode, tag="offers")
            self.net.add_door(onode, aff, tag="affords")
            for r in req:
                self.net.add_door(onode, r, tag="requires")
        return name

    def part_operable(self, name):
        """What the part can do alone: requirement-free offers."""
        out = set()
        for onode in self.net.get_doors(name, tag="offers"):
            if not self.net.get_doors(onode, tag="requires"):
                out |= self.net.get_doors(onode, tag="affords")
        return out

    def assemble(self, name, parts, edges):
        """A whole = parts + uptake edges [(provider, affordance,
        consumer), ...]. Identity is (parts, edges) — same whole from any
        assembly order; a rewired whole is a DIFFERENT whole."""
        wname = f"whole:{name}"
        for p in parts:
            self.net.add_door(p, wname, tag="part_of")
            self.net.add_door(wname, p, tag="part")
        for (src, aff, dst) in edges:
            unode = f"uptake:{src}.{aff}->{dst}"
            self.net.add_door(src, unode, tag="provides")
            self.net.add_door(unode, dst, tag="feeds")
            self.net.add_door(unode, aff, tag="carries")
            self.net.add_door(wname, unode, tag="arranges")
        self.net.set_meta(wname, "identity",
                          (tuple(sorted(parts)),
                           tuple(sorted(tuple(e) for e in edges))))
        return wname

    def dismantle(self, whole):
        """Decomposition recovers the parts (the arrangement stays on the
        whole — nothing leaves the net)."""
        return set(self.net.get_doors(whole, tag="part"))

    def operable(self, whole):
        """Fixed-point propagation over the doors: (part, affordance)
        becomes live when every requirement arrives via an uptake edge
        from a part whose provided affordance is itself live."""
        parts = self.dismantle(whole)
        edges = set()
        for unode in self.net.get_doors(whole, tag="arranges"):
            for s in self.net.get_predecessors(unode, tag="provides"):
                for a in self.net.get_doors(unode, tag="carries"):
                    for d in self.net.get_doors(unode, tag="feeds"):
                        edges.add((s, a, d))
        live = set()
        changed = True
        while changed:
            changed = False
            for p in parts:
                for onode in self.net.get_doors(p, tag="offers"):
                    reqs = self.net.get_doors(onode, tag="requires")
                    for f in self.net.get_doors(onode, tag="affords"):
                        if (p, f) in live:
                            continue
                        if all(any((s, need, p) in edges and (s, need) in live
                                   for s in parts) for need in reqs):
                            live.add((p, f))
                            changed = True
        return {f for _, f in live}

    def emergent(self, whole):
        """Operable at the whole, operable in NO part alone — the thing
        membership bags could never represent."""
        alone = set()
        for p in self.dismantle(whole):
            alone |= self.part_operable(p)
        return self.operable(whole) - alone

    def whole_as_part(self, whole):
        """First-class upward composition: the whole re-enters as a part
        offering everything it can do (emergent included), requirement-
        free — circles of circles, engines into cars."""
        self.register_part(whole, {f: () for f in self.operable(whole)})
        return whole

    # ── logic ───────────────────────────────────────────────────

    def logic_eval(self, expression, verbose=False):
        """Evaluate a logic expression via chained matmul lookups.
        Decompose-when-shrug: compound → single-gate lookups."""
        tokens = expression.lower().split()
        result, trace = self._logic_reduce(tokens, verbose)
        return result, trace

    def _logic_reduce(self, tokens, verbose=False):
        trace = []
        while len(tokens) >= 2 and tokens[0] == "(" and tokens[-1] == ")":
            tokens = tokens[1:-1]
        if len(tokens) == 1:
            return tokens[0], trace
        if tokens[0] == "not":
            inner, inner_trace = self._logic_reduce(tokens[1:], verbose)
            trace.extend(inner_trace)
            context = ["not", inner, "="]
            answer, conf = self.lookup(context)
            trace.append({"op": f"not {inner}", "answer": answer, "conf": conf})
            if verbose:
                print(f"    not {inner} → {answer} (conf={conf:.1f})")
            return answer, trace
        main_op_idx = self._find_main_op(tokens)
        if main_op_idx is not None:
            left_tokens = tokens[:main_op_idx]
            op = tokens[main_op_idx]
            right_tokens = tokens[main_op_idx + 1:]
            left_val, lt = self._logic_reduce(left_tokens, verbose)
            trace.extend(lt)
            right_val, rt = self._logic_reduce(right_tokens, verbose)
            trace.extend(rt)
            context = [left_val, op, right_val, "="]
            answer, conf = self.lookup(context)
            trace.append({"op": f"{left_val} {op} {right_val}",
                          "answer": answer, "conf": conf})
            if verbose:
                print(f"    {left_val} {op} {right_val} → {answer} (conf={conf:.1f})")
            return answer, trace
        return " ".join(tokens), trace

    def _find_main_op(self, tokens):
        ops_by_precedence = [{"implies"}, {"or", "nor"}, {"xor"},
                             {"and", "nand"}, {"equals"}]
        depth = 0
        for prec_level in ops_by_precedence:
            for i, t in enumerate(tokens):
                if t == "(":
                    depth += 1
                elif t == ")":
                    depth -= 1
                elif depth == 0 and t in prec_level and i > 0:
                    return i
        return None

    # ── reasoning ───────────────────────────────────────────────

    def reason_chain(self, subject, relation, verbose=False):
        """Follow a relation chain via matmul hops. Each hop is one matmul."""
        chain = [subject]
        current = subject
        visited = {subject}
        for step in range(20):
            answer, conf = self.lookup([current, relation])
            if answer is None or conf < CONFIDENCE_THRESHOLD or answer in visited:
                break
            chain.append(answer)
            visited.add(answer)
            current = answer
            if verbose:
                print(f"    hop {step}: {chain[-2]} {relation} → {answer}"
                      f" (conf={conf:.1f})")
        return chain

    def is_a_check(self, subject, target, verbose=False):
        """Is subject a target? Walk the is_a chain."""
        chain = self.reason_chain(subject, "is_a", verbose=verbose)
        return target in chain, chain

    def can_check(self, subject, ability, verbose=False):
        """Can subject do ability? Negative first, then direct, then inherited.
        Each check is one matmul reading a specific cell."""
        # Step 1: negative blocks everything
        neg_match, neg_conf = self.check([subject, "cannot"], ability)
        if neg_match:
            if verbose:
                print(f"    {subject} cannot {ability} → BLOCKED (conf={neg_conf:.1f})")
            return False, [subject]
        # Step 2: direct capability
        direct_match, direct_conf = self.check([subject, "can"], ability)
        if direct_match:
            if verbose:
                print(f"    {subject} can {ability} → YES (direct, conf={direct_conf:.1f})")
            return True, [subject]
        # Step 3: walk is_a chain, check each ancestor
        chain = self.reason_chain(subject, "is_a")
        for ancestor in chain[1:]:
            aneg, aneg_conf = self.check([ancestor, "cannot"], ability)
            if aneg:
                if verbose:
                    print(f"    {ancestor} cannot {ability} → BLOCKED")
                return False, chain[:chain.index(ancestor) + 1]
            amatch, aconf = self.check([ancestor, "can"], ability)
            if amatch:
                if verbose:
                    print(f"    {subject} can {ability} → YES"
                          f" (inherited from {ancestor}, conf={aconf:.1f})")
                return True, chain[:chain.index(ancestor) + 1]
        # Step 4: fact index fallback (for multi-valued relations)
        direct_facts = self.fact_index.get((subject, "can"), [])
        if ability in direct_facts:
            if verbose:
                print(f"    {subject} can {ability} → YES (fact index)")
            return True, [subject]
        for ancestor in chain[1:]:
            ancestor_facts = self.fact_index.get((ancestor, "can"), [])
            if ability in ancestor_facts:
                if verbose:
                    print(f"    {subject} can {ability} → YES"
                          f" (inherited from {ancestor} via fact index)")
                return True, chain[:chain.index(ancestor) + 1]
        if verbose:
            print(f"    {subject} can {ability} → UNKNOWN")
        return None, chain

    def containment_check(self, item, container, verbose=False):
        """Is item in container? Walk the 'in' chain."""
        chain = self.reason_chain(item, "in", verbose=verbose)
        return container in chain, chain

    def property_check(self, subject, verbose=False):
        """What properties does subject have? Direct + inherited."""
        properties = []
        direct = self.fact_index.get((subject, "has"), [])
        for p in direct:
            properties.append((p, "direct"))
        chain = self.reason_chain(subject, "is_a")
        for ancestor in chain[1:]:
            inherited = self.fact_index.get((ancestor, "has"), [])
            for p in inherited:
                if not any(pp == p for pp, _ in properties):
                    properties.append((p, f"from {ancestor}"))
        if verbose:
            for prop, source in properties:
                print(f"    {subject} has {prop} ({source})")
        return properties

    def syllogism(self, premises, conclusion, verbose=False):
        """Evaluate a syllogism by asserting premises and checking conclusion."""
        if verbose:
            for p in premises:
                print(f"    premise: {p[0]} {p[1]} {p[2]}")
            print(f"    ∴ {conclusion[0]} {conclusion[1]} {conclusion[2]}?")
        subj, rel, obj = conclusion
        if rel == "is_a":
            found, chain = self.is_a_check(subj, obj, verbose=verbose)
            return found, chain
        elif rel == "can":
            found, chain = self.can_check(subj, obj, verbose=verbose)
            return found, chain
        elif rel == "in":
            found, chain = self.containment_check(subj, obj, verbose=verbose)
            return found, chain
        return None, []

    # ── computation ─────────────────────────────────────────────

    def compute(self, a, op, b, memorize=True, verbose=True):
        """The full loop: try → shrug → decompose → verify → memorize."""
        context = [str(a), op, str(b), "="]
        answer, conf = self.lookup(context)
        if answer is not None and conf >= CONFIDENCE_THRESHOLD:
            if verbose:
                print(f"  {a} {op} {b} = {answer}  [direct recall, conf={conf:.1f}]")
            return answer, "recall"

        if verbose:
            print(f"  {a} {op} {b} = ?  [shrug, conf={conf:.2f}] → decomposing...")

        if op == "*":
            result = _decompose_multiply(a, b, self, verbose)
        elif op == "+":
            result = _decompose_add(a, b, self, verbose)
        elif op == "-":
            result = _decompose_add(a, -b, self, verbose)  # placeholder
            if result is None:
                result = a - b
        else:
            result = None

        if result is None:
            if verbose:
                print(f"  FAILED TO DECOMPOSE")
            return None, "failed"

        # Cross-check (commutative verify for multiplication)
        if op == "*":
            rev, rev_conf = self.lookup([str(b), op, str(a), "="])
            if rev is not None and rev_conf >= CONFIDENCE_THRESHOLD:
                if int(rev) == result and verbose:
                    print(f"  cross-check: {b}*{a} = {rev} ✓")
            else:
                rev_result = _decompose_multiply(b, a, self, False)
                if rev_result == result and verbose:
                    print(f"  cross-check: {b}*{a} decomposed = {rev_result} ✓")

        # Memorize
        if memorize and result is not None:
            self.observe(tokenize(f"{a} {op} {b} = {result}"))
            if verbose:
                print(f"  memorized: {a} {op} {b} = {result}")

        return result, "decomposed"

    # ── problem solving ─────────────────────────────────────────

    def solve(self, problem, verbose=True):
        """Solve a problem with unknowns. Forward, backward, gap-fill."""
        tokens = tokenize(problem)
        unknowns = [i for i, t in enumerate(tokens) if t == "?"]

        if not unknowns:
            # Forward: just lookup
            answer, conf = self.lookup(tokens)
            if verbose:
                print(f"  {problem} → {answer} (conf={conf:.1f})")
            return answer

        if len(unknowns) == 1:
            pos = unknowns[0]
            if pos == len(tokens) - 1:
                # Forward: ? is the answer
                context = tokens[:-1]
                answer, conf = self.lookup(context)
                if verbose:
                    print(f"  {problem} → {answer} (conf={conf:.1f})")
                return answer
            else:
                # Backward: try candidates, validate
                target = tokens[-1] if "=" in tokens else None
                eq_pos = tokens.index("=") if "=" in tokens else None
                if eq_pos and eq_pos + 1 < len(tokens):
                    target = tokens[eq_pos + 1]
                candidates = self._get_candidates(tokens, pos)
                for c in candidates:
                    trial = list(tokens)
                    trial[pos] = c
                    context = trial[:-1] if trial[-1] != "=" else trial
                    if target:
                        match, conf = self.check(
                            trial[:eq_pos + 1] if eq_pos else trial[:-1],
                            target)
                        if match:
                            if verbose:
                                print(f"  {problem} → {c} (conf={conf:.1f})")
                            return c
        # Multi-unknown gap-fill
        if len(unknowns) >= 2 and "=" in tokens:
            eq_pos = tokens.index("=")
            target = tokens[eq_pos + 1] if eq_pos + 1 < len(tokens) else None
            if target:
                solutions = []
                candidates = self._get_candidates(tokens, unknowns[0])
                for c1 in candidates:
                    for c2 in candidates:
                        trial = list(tokens)
                        trial[unknowns[0]] = c1
                        trial[unknowns[1]] = c2
                        match, conf = self.check(trial[:eq_pos + 1], target)
                        if match:
                            solutions.append((c1, c2))
                if verbose:
                    print(f"  {problem} → {len(solutions)} solutions")
                    for s in solutions[:5]:
                        print(f"    {s}")
                return solutions
        return None

    def _get_candidates(self, tokens, pos):
        """Generate candidate values for an unknown position."""
        candidates = set()
        for t in tokens:
            if t != "?":
                candidates.update(self.net.get_doors(t, tag="seq"))
                candidates.update(self.net.get_predecessors(t, tag="seq"))
        candidates.discard("?")
        candidates.discard("=")
        for op in ["+", "-", "*", "/", "and", "or", "not"]:
            candidates.discard(op)
        return sorted(candidates)

    def solve_steps(self, steps, verbose=True):
        """Multi-step problem solving with scratch references ($0, $1, ...)."""
        results = []
        for i, step in enumerate(steps):
            # Replace scratch references
            resolved = step
            for j, prev in enumerate(results):
                resolved = resolved.replace(f"${j}", str(prev))
            result = self.solve(resolved, verbose=verbose)
            results.append(result)
            if verbose:
                print(f"  step {i}: {step} → {result}")
        return results

    # ── persistence ─────────────────────────────────────────────

    def assess(self, action_text):
        """Ask the matrix what it learned about this action's consequences.
        The think loop handles fallback automatically — if the full context
        shrugs, it tries progressively simpler contexts."""
        tokens = tokenize(action_text)
        context = tokens + ["result"]
        assessment = {"action": action_text, "checks": {}}

        pos, pos_c = self.check(context, "net_positive")
        neg, neg_c = self.check(context, "net_negative")
        zero, zero_c = self.check(context, "net_zero")

        assessment["checks"]["net_positive"] = (pos, pos_c)
        assessment["checks"]["net_negative"] = (neg, neg_c)
        assessment["checks"]["net_zero"] = (zero, zero_c)

        if neg and neg_c > pos_c and neg_c > zero_c:
            assessment["recommendation"] = "caution"
        elif pos and pos_c > neg_c:
            assessment["recommendation"] = "proceed"
        elif zero and zero_c > neg_c:
            assessment["recommendation"] = "proceed"
        else:
            assessment["recommendation"] = "unknown"

        return assessment

    def plan_think_execute(self, action_text, verbose=True):
        """The universal output loop. Plan, assess persistence, execute or block."""
        if verbose:
            print(f"\n  ┌─ PLAN: {action_text}")
        a = self.assess(action_text)
        if verbose:
            print(f"  ├─ THINK:")
            for name, (val, conf) in a["checks"].items():
                if val:
                    print(f"  │  ✓ {name} (conf={conf:.1f})")
            print(f"  │  → {a['recommendation'].upper()}")
        if a["recommendation"] == "caution":
            if verbose:
                print(f"  └─ ⚠ CAUTION — net negative outcome learned")
            return False, a
        else:
            if verbose:
                print(f"  └─ ✓ PROCEED")
            return True, a

    # ── status ──────────────────────────────────────────────────

    def status(self):
        nodes = self.net.all_nodes()
        tags = set()
        for t in self.net.door_tags.values():
            tags.update(t)
        doors = sum(len(t) for t in self.net.doors.values())
        compiled = bool(self._compiled)
        matrix_shape = self._compiled["W"].shape if compiled else None
        dirty_seqs = len(self.observed_sequences) - self._compiled_up_to
        dirty_consolidation = len(self.observed_sequences) - self._consolidated_up_to
        return {
            "nodes": len(nodes), "doors": doors,
            "tags": sorted(tags), "types": len(self.types),
            "rules": len(self.rules), "lockouts": len(self.lockouts),
            "starts": len(self.starts),
            "observations": len(self.observed_sequences),
            "facts_indexed": sum(len(v) for v in self.fact_index.values()),
            "compiled": compiled, "matrix_shape": matrix_shape,
            "dirty_sequences": dirty_seqs,
            "dirty_nodes": len(self._dirty_nodes),
            "needs_consolidation": dirty_consolidation > 0,
        }


# ═════════════════════════════════════════════════════════════════
# COMPUTATION HELPERS — decompose when shrug
# ═════════════════════════════════════════════════════════════════

def digits_of(n):
    """Extract digits of a number. Tokenization-level (Rule 2 exception)."""
    n = abs(int(n))
    if n == 0:
        return [0]
    ds = []
    while n > 0:
        ds.append(n % 10)
        n //= 10
    ds.reverse()
    return ds


def _decompose_multiply(a, b, isaac, verbose=True):
    """Decompose a * b into digit-pair lookups from memorized tables."""
    da = digits_of(a)
    db = digits_of(b)
    total = 0
    for i, digit_a in enumerate(da):
        place_a = len(da) - 1 - i
        for j, digit_b in enumerate(db):
            place_b = len(db) - 1 - j
            place_value = 10 ** (place_a + place_b)
            product_str, conf = isaac.lookup(
                [str(digit_a), "*", str(digit_b), "="])
            if product_str is None or conf < CONFIDENCE_THRESHOLD:
                return None
            product = int(product_str)
            contribution = product * place_value
            total += contribution
            if verbose:
                print(f"    {digit_a}×{digit_b}={product:>4d}"
                      f" × {place_value:>6d} = {contribution:>8d}")
    if verbose:
        print(f"    {'─' * 40}")
        print(f"    TOTAL = {total}")
    return total


def _decompose_add(a, b, isaac, verbose=True):
    """Decompose a + b into digit-pair additions with carry."""
    da = digits_of(a)
    db = digits_of(b)
    max_len = max(len(da), len(db))
    da = [0] * (max_len - len(da)) + da
    db = [0] * (max_len - len(db)) + db
    result_digits = []
    carry = 0
    for i in range(max_len - 1, -1, -1):
        digit_sum = da[i] + db[i] + carry
        sum_str, conf = isaac.lookup([str(da[i]), "+", str(db[i]), "="])
        if sum_str is not None and conf >= CONFIDENCE_THRESHOLD:
            partial = int(sum_str)
            if carry > 0:
                carry_str, cc = isaac.lookup([str(partial), "+", str(carry), "="])
                if carry_str is not None and cc >= CONFIDENCE_THRESHOLD:
                    digit_sum = int(carry_str)
                else:
                    digit_sum = da[i] + db[i] + carry
            else:
                digit_sum = partial
        carry = digit_sum // 10
        result_digits.append(digit_sum % 10)
    if carry > 0:
        result_digits.append(carry)
    result_digits.reverse()
    result = int("".join(str(d) for d in result_digits))
    if verbose:
        print(f"    {a} + {b} = {result}")
    return result


# ═════════════════════════════════════════════════════════════════
# WORLD — state management and planning
# ═════════════════════════════════════════════════════════════════

class World:
    """Manages mutable world state. Actions have preconditions and effects.
    Uses Isaac for persistence assessment."""

    def __init__(self, isaac=None):
        self.state = defaultdict(set)   # entity → {facts}
        self.actions = {}               # (source_pattern, action, target_pattern) → {...}
        self.isaac = isaac

    def set_state(self, entity, fact):
        self.state[entity].add(fact)

    def clear_state(self, entity, fact):
        self.state[entity].discard(fact)

    def has_state(self, entity, fact):
        return fact in self.state.get(entity, set())

    def show_state(self):
        for entity in sorted(self.state):
            facts = sorted(self.state[entity])
            if facts:
                print(f"  {entity}: {', '.join(facts)}")

    def teach_action(self, source, action, target,
                     preconditions=None, effects=None):
        self.actions[(source, action, target)] = {
            "preconditions": preconditions or [],
            "effects": effects or [],
        }

    def execute(self, source, action, target, verbose=True):
        """Execute an action. Check preconditions. Apply effects."""
        key = (source, action, target)
        wildcard = ("*", action, "*")
        specific_src = (source, action, "*")
        specific_tgt = ("*", action, target)

        spec = None
        for k in [key, specific_src, specific_tgt, wildcard]:
            if k in self.actions:
                spec = self.actions[k]
                break
        if spec is None:
            if verbose:
                print(f"  Unknown action: {source} {action} {target}")
            return False, ["unknown action"]

        # Check preconditions
        failed = []
        for cond in spec["preconditions"]:
            resolved = cond.replace("SOURCE", source).replace("TARGET", target)
            parts = resolved.split()
            if len(parts) >= 3 and parts[1] == "near":
                # Proximity check
                loc_src = self._get_location(parts[0])
                loc_tgt = self._get_location(parts[2])
                if loc_src != loc_tgt:
                    failed.append(resolved)
            elif len(parts) >= 3 and parts[1] == "is":
                if not self.has_state(parts[0], " ".join(parts[1:])):
                    failed.append(resolved)
            elif len(parts) >= 2 and parts[1] == "has":
                if not self.has_state(parts[0], " ".join(parts[1:])):
                    failed.append(resolved)

        if failed:
            if verbose:
                print(f"  Preconditions failed: {failed}")
            return False, failed

        # Apply effects
        for effect in spec["effects"]:
            resolved = effect.replace("SOURCE", source).replace("TARGET", target)
            parts = resolved.split()
            if len(parts) >= 3 and parts[1] == "is":
                self.set_state(parts[0], " ".join(parts[1:]))
            elif len(parts) >= 2 and parts[0].startswith("not_"):
                entity = parts[0].replace("not_", "")
                # Remove the matching positive state
                # This is a simplification — should match more carefully
                pass
            elif len(parts) >= 2 and parts[1] == "has":
                self.set_state(parts[0], " ".join(parts[1:]))
            if verbose:
                print(f"  effect: {resolved}")
        return True, []

    def _get_location(self, entity):
        for fact in self.state.get(entity, set()):
            if fact.startswith("in_") or fact.startswith("at_"):
                return fact
        return None


# ═════════════════════════════════════════════════════════════════
# TEST SUITE
# ═════════════════════════════════════════════════════════════════

def _div(title):
    print(f"\n{'═' * 65}")
    print(f"  {title}")
    print(f"{'═' * 65}")


def test_language():
    """Language: observe, crystallize, generate, type inference."""
    _div("LANGUAGE")
    isaac = Isaac()
    sentences = [
        "the cat sat .", "the dog ran .", "the cat ran .",
        "the big cat sat .", "the small dog ran .",
        "a cat is soft .", "a dog is loyal .",
        "the bird flew .", "a fish swam .",
        "the big dog barked .", "the small cat purred .",
        "she ran fast .", "he walked slowly .",
        "a red ball bounced .", "the blue car stopped .",
    ]
    bad = ["cat the sat .", "dog the ran .", "the sat cat .", "the ran dog ."]
    for s in sentences:
        isaac.observe(tokenize(s))
    for s in bad:
        isaac.observe_negative(tokenize(s))
    isaac.crystallize(verbose=True)

    print(f"\n  Generation:")
    for concept in ["cat", "dog", "ball"]:
        chain = isaac.generate(concept)
        print(f"    '{concept}' → {' '.join(chain)}")

    # Type inference
    result = isaac.infer("dog", "sat")
    print(f"\n  dog→sat inferred: {result['inferred']} via {result.get('via')}")

    # Polysemy: senses as first-class nodes (null-gated, doors not blobs)
    poly = Isaac()
    for s in [["river", "water", "flows", "past", "the", "bank", "shore"],
              ["muddy", "river", "bank", "erodes", "water", "slowly"],
              ["the", "river", "bank", "flooded", "water", "rose"],
              ["fish", "swim", "near", "the", "river", "bank", "water"],
              ["boat", "moored", "river", "bank", "water", "calm"],
              ["money", "deposit", "at", "the", "bank", "teller"],
              ["bank", "loan", "money", "interest", "teller", "counter"],
              ["the", "bank", "vault", "holds", "money", "teller"],
              ["savings", "money", "bank", "account", "teller", "opened"],
              ["cash", "money", "withdrawn", "bank", "teller", "queue"]]:
        poly.observe(s)
    senses = poly.crystallize_senses("bank")
    sound = [s for s in senses if s["verdict"] == "sound"]
    r = poly.route("bank", {"river", "water"})
    m = poly.route("bank", {"money", "teller"})
    ok_senses = (len(sound) == 2
                 and r <= {"shore", "erodes", "flooded", "water"}
                 and m <= {"teller", "loan", "vault", "account"})
    print(f"\n  Polysemy: {len(sound)} sound senses of 'bank'; "
          f"river→{sorted(r)} money→{sorted(m)} "
          f"({'ok' if ok_senses else 'WRONG'})")
    return ok_senses


def test_math():
    """Math: memorize tables, recall via matrix, shrug boundary."""
    _div("MATH — matrix recall")
    isaac = Isaac()
    for a in range(20):
        for b in range(20):
            isaac.observe(tokenize(f"{a} + {b} = {a + b}"))
            isaac.observe(tokenize(f"{a} * {b} = {a * b}"))
    # No manual compile() — lookup auto-compiles (Stage 3: ROUTE)

    tests = [
        (["7", "*", "8", "="], "56"),
        (["3", "+", "5", "="], "8"),
        (["12", "*", "12", "="], "144"),
        (["19", "+", "19", "="], "38"),
        (["0", "*", "15", "="], "0"),
        (["1", "*", "7", "="], "7"),
    ]
    correct = 0
    for context, expected in tests:
        answer, conf = isaac.lookup(context)
        ok = answer == expected
        correct += ok
        print(f"  {'✓' if ok else '✗'}  {' '.join(context)} → {answer}"
              f"  (expected {expected}, conf={conf:.1f})")
    print(f"\n  {correct}/{len(tests)}")
    return correct == len(tests)


def test_logic():
    """Logic: truth tables via matmul, compound decomposition."""
    _div("LOGIC")
    isaac = Isaac()
    for a in ["true", "false"]:
        for b in ["true", "false"]:
            av, bv = a == "true", b == "true"
            isaac.observe(tokenize(f"{a} and {b} = {'true' if av and bv else 'false'}"))
            isaac.observe(tokenize(f"{a} or {b} = {'true' if av or bv else 'false'}"))
            isaac.observe(tokenize(f"{a} xor {b} = {'true' if av ^ bv else 'false'}"))
            isaac.observe(tokenize(f"{a} implies {b} = {'true' if (not av) or bv else 'false'}"))
        isaac.observe(tokenize(f"not {a} = {'false' if a == 'true' else 'true'}"))
    # Auto-compiles on first query

    tests = [
        ("true and true", "true"), ("true and false", "false"),
        ("false or true", "true"), ("false or false", "false"),
        ("not true", "false"), ("not false", "true"),
        ("true xor false", "true"),
    ]
    correct = 0
    for expr, expected in tests:
        result, _ = isaac.logic_eval(expr)
        ok = result == expected
        correct += ok
        print(f"  {'✓' if ok else '✗'}  {expr:30s} → {result}")
    print(f"\n  {correct}/{len(tests)}")

    # Compound
    compound = [
        ("true and false or true", "true"),
        ("not true or false", "false"),
        ("not false and true", "true"),
    ]
    cc = 0
    for expr, expected in compound:
        result, _ = isaac.logic_eval(expr)
        ok = result == expected
        cc += ok
        print(f"  {'✓' if ok else '✗'}  {expr:30s} → {result}")
    print(f"  compound: {cc}/{len(compound)}")
    return correct == len(tests) and cc == len(compound)


def test_reasoning():
    """Reasoning: is_a chains, capability inheritance, containment."""
    _div("REASONING")
    isaac = Isaac()
    # Taxonomy
    for subj, obj in [("cat", "mammal"), ("dog", "mammal"),
                      ("mammal", "animal"), ("animal", "living_thing"),
                      ("robin", "bird"), ("penguin", "bird"),
                      ("bird", "animal"), ("salmon", "fish"),
                      ("fish", "animal"), ("oak", "tree"),
                      ("tree", "plant"), ("plant", "living_thing")]:
        isaac.teach(subj, "is_a", obj)
    # Capabilities
    for subj, obj in [("bird", "fly"), ("bird", "sing"),
                      ("fish", "swim"), ("cat", "purr"), ("cat", "climb"),
                      ("dog", "bark"), ("penguin", "swim"),
                      ("living_thing", "grow"), ("animal", "move")]:
        isaac.teach(subj, "can", obj)
    # Negatives
    for subj, obj in [("penguin", "fly"), ("fish", "walk")]:
        isaac.observe(tokenize(f"{subj} cannot {obj}"))
        isaac.fact_index[(subj, "cannot")].append(obj)
    # Containment
    for inner, outer in [("ball", "box"), ("box", "closet"),
                         ("closet", "room"), ("room", "house")]:
        isaac.teach(inner, "in", outer)
    # Auto-compiles on first query

    # Is-a
    correct = 0
    for subj, tgt, expected in [("cat", "animal", True),
                                 ("cat", "living_thing", True),
                                 ("robin", "animal", True),
                                 ("cat", "plant", False)]:
        found, chain = isaac.is_a_check(subj, tgt)
        ok = found == expected
        correct += ok
        print(f"  {'✓' if ok else '✗'}  {subj} is_a {tgt}? {found}"
              f"  chain: {' → '.join(chain)}")

    # Can
    for subj, ability, expected in [("robin", "fly", True),
                                     ("robin", "sing", True),
                                     ("cat", "climb", True),
                                     ("cat", "grow", True),
                                     ("penguin", "fly", False),
                                     ("penguin", "swim", True)]:
        result, chain = isaac.can_check(subj, ability, verbose=True)
        if result is None:
            result = False
        ok = result == expected
        correct += ok
        print(f"  {'✓' if ok else '✗'}  can {subj} {ability}? {result}")

    # Containment
    found, chain = isaac.containment_check("ball", "house")
    ok = found == True
    correct += ok
    print(f"  {'✓' if ok else '✗'}  ball in house? {found}  chain: {' → '.join(chain)}")

    print(f"\n  {correct}/11")
    return correct == 11


def test_decompose():
    """Decompose: shrug → digit-pair lookups → assemble → verify."""
    _div("DECOMPOSE WHEN SHRUG")
    isaac = Isaac()
    for a in range(100):
        for b in range(100):
            isaac.observe(tokenize(f"{a} * {b} = {a * b}"))
            isaac.observe(tokenize(f"{a} + {b} = {a + b}"))
    for a in range(100):
        isaac.observe(tokenize(f"{a} * 100 = {a * 100}"))
        isaac.observe(tokenize(f"{a} * 1000 = {a * 1000}"))
    # Auto-compiles on first compute() call

    tests = [(137, "*", 48, 6576), (256, "*", 31, 7936), (999, "*", 999, 998001)]
    correct = 0
    for a, op, b, expected in tests:
        result, method = isaac.compute(a, op, b, memorize=False)
        ok = (result == expected)
        correct += ok
        print(f"  {'✓' if ok else '✗'}  {a} {op} {b} = {result}"
              f"  (expected {expected}) [{method}]")
    print(f"\n  {correct}/{len(tests)}")
    return correct == len(tests)


def test_persistence():
    """Persistence: learn from consequences, assess novel actions."""
    _div("PERSISTENCE — learn from consequences")
    isaac = Isaac()

    scenarios = [
        ("me build birdhouse", 3, 6),
        ("me assemble watch", 6, 8),
        ("me smash watch", 8, 3),
        ("me knock tower", 7, 5),
        ("me burn painting", 6, 2),
        ("me snap stick", 1, 1),
        ("me crack rock", 1, 1),
        ("me oil watch", 7, 8),
        ("me repair roof", 5, 5),
    ]
    for action, before, after in scenarios:
        delta = after - before
        if delta > 0:
            isaac.observe(tokenize(f"{action} result net_positive"))
        elif delta < 0:
            isaac.observe(tokenize(f"{action} result net_negative"))
        else:
            isaac.observe(tokenize(f"{action} result net_zero"))
        # Verb-level observation for generalization
        verb = tokenize(action)[1]  # "me VERB object" → VERB at index 1
        if delta > 0:
            isaac.observe(tokenize(f"{verb} result net_positive"))
        elif delta < 0:
            isaac.observe(tokenize(f"{verb} result net_negative"))
        else:
            isaac.observe(tokenize(f"{verb} result net_zero"))

    # Auto-compiles on first assess() call

    # Known actions
    correct = 0
    for action, expected in [("me build birdhouse", "proceed"),
                              ("me smash watch", "caution"),
                              ("me snap stick", "proceed"),
                              ("me oil watch", "proceed")]:
        a = isaac.assess(action)
        ok = a["recommendation"] == expected
        correct += ok
        print(f"  {'✓' if ok else '✗'}  {action:25s} → {a['recommendation']}")

    # Novel actions (verb-level generalization)
    for action, expected in [("me smash computer", "caution"),
                              ("me build castle", "proceed"),
                              ("me snap pencil", "proceed")]:
        a = isaac.assess(action)
        ok = a["recommendation"] == expected
        correct += ok
        print(f"  {'✓' if ok else '✗'}  {action:25s} → {a['recommendation']}"
              f"  [think loop fallback]")

    print(f"\n  {correct}/7")
    return correct == 7


def test_waves():
    _div("WAVES — simultaneity, movement, circles")
    isaac = Isaac()
    rng = np.random.default_rng(5)
    # two independent routines wave through his doors, noise flickers around:
    # day cycle (dwell 3):   sun+light -> work+tools -> moon+dark -> ...
    # tide cycle (dwell 5):  tide_in+wet <-> tide_out+dry
    P1 = [("sun", "light"), ("work", "tools"), ("moon", "dark")]
    P2 = [("tide_in", "wet"), ("tide_out", "dry")]
    noise = ["gull", "cloud", "truck", "radio"]
    for _ in range(8):                       # fresh phases: independent waves
        o1, o2 = int(rng.integers(0, 9)), int(rng.integers(0, 10))
        for s in range(75):
            active = set(P1[((s + o1) // 3) % 3]) | set(P2[((s + o2) // 5) % 2])
            active = {a for a in active if rng.random() < 0.9}   # sensor flicker
            active |= {n for n in noise if rng.random() < 0.3}
            isaac.tick(active)
    waves = isaac.wave_consolidate()

    correct = 0
    got = {frozenset(g) for g in waves["groups"]}
    want = {frozenset(p) for p in P1 + P2}
    ok = got == want
    correct += ok
    print(f"  {'✓' if ok else '✗'}  simultaneity: the 5 planted pairs, "
          f"no noise doors ({len(waves['groups'])} groups)")

    ok = sorted(len(c) for c in waves["circle_orders"]) == [2, 3]
    correct += ok
    print(f"  {'✓' if ok else '✗'}  circles: day-cycle (3) and tide-cycle (2) "
          f"→ {waves['circles']}")

    ok = all(isaac.net.get_predecessors(c, tag="wave") for c in waves["circles"])
    correct += ok
    print(f"  {'✓' if ok else '✗'}  circles entered the net as nodes "
          f"(composable upward)")

    # shuffled time: co-occurrence survives, ALL movement must die
    shuffled = Isaac()
    order = rng.permutation(len(isaac.activation_log))
    shuffled.activation_log = [isaac.activation_log[i] for i in order]
    w2 = shuffled.wave_consolidate()
    ok = ({frozenset(g) for g in w2["groups"]} == want
          and not w2["edges"] and not w2["circles"])
    correct += ok
    print(f"  {'✓' if ok else '✗'}  shuffled-time control: groups survive, "
          f"movement dies ({len(w2['edges'])} edges, {len(w2['circles'])} circles)")

    print(f"\n  {correct}/4")
    return correct == 4


def test_tracking():
    _div("TRACKING — his clock, temporary statuses, emergent explanation")
    isaac = Isaac()
    rng = np.random.default_rng(9)
    SUNd = ["disk", "light", "warm", "sky"]
    NIGHTd = ["moon", "stars"]
    CLOUDd = ["cloud_a", "cloud_b"]
    NOISEd = ["gull", "truck"]

    def build(T):
        day = np.zeros(T, dtype=int); cl = np.zeros(T, dtype=int)
        t, ph = 0, 1
        while t < T:
            for _ in range(int(rng.integers(8, 15))):
                if t < T:
                    day[t] = ph; t += 1
            ph = 1 - ph
        t = int(rng.integers(0, 5))
        while t < T:
            for _ in range(int(rng.integers(6, 14))):
                if t < T:
                    cl[t] = 1; t += 1
            t += int(rng.integers(8, 16))
        ticks = []
        for t in range(T):
            a = set()
            base = (SUNd if day[t] else NIGHTd)
            for dname in base:
                if dname == "disk" and day[t] and cl[t]:
                    if rng.random() < 0.05:
                        a.add(dname)
                elif rng.random() < 0.9:
                    a.add(dname)
            for dname in CLOUDd:
                if (cl[t] and rng.random() < 0.9) or rng.random() < 0.05:
                    a.add(dname)
            a |= {dname for dname in NOISEd if rng.random() < 0.3}
            ticks.append(a)
        return ticks, day, cl

    # phase A: plain sensing -> consolidation discovers identity + rhythm
    ticksA, _, _ = build(1400)
    for a in ticksA:
        isaac.tick(a)
    waves = isaac.wave_consolidate()
    sun_g = next((g for g in waves["groups"] if "light" in g), None)
    sun_name = f"wave:{'_'.join(sun_g[:2])}[{len(sun_g)}]" if sun_g else None
    circle = next((c for c in waves["circles"]
                   if sun_name in isaac.net.get_predecessors(c, tag="wave")), None)
    ok = circle is not None and isaac.follow(circle)
    correct = int(ok)
    print(f"  {'✓' if ok else '✗'}  day/night circle discovered and followed "
          f"({circle})")
    if not ok:
        print(f"\n  {correct}/5")
        return False

    # phase B: tracked sensing — clock, statuses, world state
    ticksB, dayB, clB = build(900)
    state_hits = phase_hits = 0
    for t, a in enumerate(ticksB):
        isaac.tick(a)
        _, ph = isaac.phase_log[circle][-1] if isaac.phase_log[circle] else (0, None)
        phase_hits += ((ph == sun_name) == bool(dayB[t]))
        want = bool(dayB[t] and clB[t])
        state_hits += (isaac.world.has_state(sun_name, "missing disk") == want)
    ok = phase_hits / len(ticksB) >= 0.9
    correct += ok
    print(f"  {'✓' if ok else '✗'}  clock in scratch: phase correct "
          f"{phase_hits/len(ticksB)*100:.1f}% (incl. occlusion)")
    ok = state_hits / len(ticksB) >= 0.85
    correct += ok
    print(f"  {'✓' if ok else '✗'}  temporary status via world state: "
          f"'sun missing disk' tracks (day AND cloud) "
          f"{state_hits/len(ticksB)*100:.1f}%/tick")

    # consolidate again: statuses are doors -> explanation emerges -> fact
    isaac.wave_consolidate()
    blockers = set()
    for (s, r), objs in isaac.fact_index.items():
        if r == "blocks" and "disk" in objs:
            blockers.add(s)
    ok = any("cloud" in str(b) for b in blockers) and \
        not any(n in str(b) for b in blockers for n in NOISEd)
    correct += ok
    print(f"  {'✓' if ok else '✗'}  explanation emerged and was taught as a "
          f"fact: blocks(disk) <- {sorted(str(b) for b in blockers)}")

    # permanence through the existing organ
    fired = isaac.recognize_doors({"light", "warm", "sky"}, tag="part")
    ok = fired.get(sun_name, 0) >= 0.5
    correct += ok
    print(f"  {'✓' if ok else '✗'}  recognize_doors: sun fires from partial "
          f"doors, disk hidden (score {fired.get(sun_name, 0):.2f})")

    print(f"\n  {correct}/5")
    return correct == 5


def test_discovery():
    _div("DISCOVERY — the challenge loop: the thing that learns things")
    isaac = Isaac()
    rng = np.random.default_rng(12)
    n = 1600

    # (a) a hidden law -> UNDERSTOOD, and the law is REUSABLE
    X = rng.normal(0, 1, (n, 5))
    y = X[:, 0] * X[:, 1] + X[:, 2] ** 2 - X[:, 3] + rng.normal(0, 0.02, n)
    res = isaac.discover(X, y, name="challenge_a")
    ok = res["verdict"] == "UNDERSTOOD"
    correct = int(ok)
    print(f"  {'✓' if ok else '✗'}  hidden law found: {res['verdict']} "
          f"(held-out R2 {res['r2']:.3f})")
    print(f"       equation: {res['equation']}")

    Xn = rng.normal(0, 1, (400, 5))
    yn = Xn[:, 0] * Xn[:, 1] + Xn[:, 2] ** 2 - Xn[:, 3]
    p = isaac.apply_law("challenge_a", Xn)
    r2n = 1 - np.sum((yn - p) ** 2) / np.sum((yn - yn.mean()) ** 2)
    ok = r2n >= 0.99
    correct += ok
    print(f"  {'✓' if ok else '✗'}  the law is now COMPUTABLE: apply_law() on "
          f"new instances R2 {r2n:.3f}")

    # (b) a transcendental law (the physics shape)
    Xb = np.column_stack([rng.lognormal(0, .4, n), rng.lognormal(0, .4, n),
                          rng.normal(0, 1, n), rng.normal(0, 1, n)])
    yb = Xb[:, 0] * Xb[:, 1] * np.cos(Xb[:, 2] - Xb[:, 3])
    yb = yb + rng.normal(0, 0.01 * yb.std(), n)
    resb = isaac.discover(Xb, yb, name="challenge_b")
    ok = resb["verdict"] == "UNDERSTOOD"
    correct += ok
    print(f"  {'✓' if ok else '✗'}  transcendental law: {resb['verdict']} "
          f"(R2 {resb['r2']:.3f})  {resb['equation']}")

    # (c) pure noise -> he must SAY there is nothing, and the accounting
    # must put essentially everything in the noise column
    resc = isaac.discover(X, rng.normal(0, 1, n))
    acc_c = resc["accounting"]
    ok = (resc["verdict"] == "NO RULE" and acc_c["noise"] >= 90.0
          and abs(acc_c["articulated"] + acc_c["captured"]
                  + acc_c["noise"] - 100.0) < 0.2)
    correct += ok
    print(f"  {'✓' if ok else '✗'}  pure noise: {resc['verdict']} "
          f"(no invented equation; accounting {acc_c['articulated']}/"
          f"{acc_c['captured']}/{acc_c['noise']} = law/caught/noise)")

    # (d) a rule his equation class cannot say (yet): caught, not said
    Xd = np.column_stack([rng.normal(0, 1, (n, 2)), rng.normal(0, 1, (n, 1))])
    yd = np.sin(3.0 * Xd[:, 0] * Xd[:, 1])
    resd = isaac.discover(Xd, yd)
    ok = resd["verdict"] in ("CAPTURED", "PARTIAL") and resd["r2"] < 0.9
    correct += ok
    print(f"  {'✓' if ok else '✗'}  hard rule sin(3*x0*x1): {resd['verdict']} "
          f"(equation R2 {resd['r2']:.3f}, captured {resd['captured_r2']:.3f})"
          f" — partially said / caught, honestly not UNDERSTOOD")

    # (e) single input, mixed forms — 'it only does linear' is dead here
    Xe = rng.uniform(-3, 3, (n, 1))
    ye = 0.5 * Xe[:, 0] ** 2 + 1.5 * np.sin(2 * Xe[:, 0]) \
        + rng.normal(0, 0.02, n)
    rese = isaac.discover(Xe, ye, name="challenge_e")
    ok = rese["verdict"] == "UNDERSTOOD"
    correct += ok
    print(f"  {'✓' if ok else '✗'}  one input, transcendental+poly: "
          f"{rese['verdict']} (R2 {rese['r2']:.3f})")
    print(f"       equation: {rese['equation']}")

    # (f) damped oscillation — the real face of exp((-a+bi)t): complex
    # structure arrives as an exp*cos PAIR, and the decay 0.4 is NOT on the
    # atom grid — the refine pass must find it
    t = rng.uniform(0, 5, n).reshape(-1, 1)
    yf = np.exp(-0.4 * t[:, 0]) * np.cos(3.0 * t[:, 0]) \
        + rng.normal(0, 0.01, n)
    resf = isaac.discover(t, yf, name="challenge_f")
    ok = resf["verdict"] == "UNDERSTOOD"
    correct += ok
    print(f"  {'✓' if ok else '✗'}  damped oscillation (complex pair, "
          f"off-grid decay): {resf['verdict']} (R2 {resf['r2']:.3f})")
    print(f"       equation: {resf['equation']}")

    # (g) THE ACCOUNTING (audit 2.8): plant a law + a KNOWN noise fraction;
    # articulated% + captured% + noise% must equal 100 and match the truth.
    # y = x0*x1 (var ~1) + noise sd 0.6 (var 0.36) -> true law share ~73.5%
    Xg = rng.normal(0, 1, (n, 4))
    yg = Xg[:, 0] * Xg[:, 1] + rng.normal(0, 0.6, n)
    resg = isaac.discover(Xg, yg, name="challenge_g")
    acc = resg["accounting"]
    true_share = 100.0 / 1.36
    ok = (abs(acc["articulated"] + acc["captured"] + acc["noise"] - 100.0)
          < 0.2 and abs(acc["articulated"] - true_share) < 10.0
          and resg["dossier"] is not None)
    correct += ok
    print(f"  {'✓' if ok else '✗'}  accounting vs planted truth: articulated "
          f"{acc['articulated']}% (true ~{true_share:.1f}%) + captured "
          f"{acc['captured']}% + noise {acc['noise']}% = 100; residual "
          f"dossier attached ({resg['dossier']['unknown']}, "
          f"{resg['dossier']['share_pct']}% share)")

    # (h) graded belief: confidence must be high inside the data, decay
    # with extrapolation distance, and never be a binary stamp
    Xin = rng.normal(0, 1, (200, 4))
    Xnear = Xg.max(0) * 1.1 + rng.uniform(0, 0.1, (200, 4))
    Xfar = Xg.max(0) * 2.0 + rng.uniform(0, 0.1, (200, 4))
    ci = isaac.law_confidence("challenge_g", Xin).mean()
    cn = isaac.law_confidence("challenge_g", Xnear).mean()
    cf = isaac.law_confidence("challenge_g", Xfar).mean()
    ok = ci > 0.85 and ci > cn > cf and cf < 0.5
    correct += ok
    print(f"  {'✓' if ok else '✗'}  extrapolated confidence: inside "
          f"{ci:.2f} > near-beyond {cn:.2f} > far-beyond {cf:.2f} "
          f"(measured decay, not a stamp)")

    print(f"\n  {correct}/9")
    return correct == 9


def test_rivalry():
    _div("RIVALRY — the classic look-alikes, held open until confirmed")
    isaac = Isaac()
    rng = np.random.default_rng(15)
    n = 1200

    # a pendulum observed only near its center: cos(0.5x) on |x|<1.2 —
    # parabola territory. The tie must be DECLARED, with a probe.
    X = rng.uniform(-1.2, 1.2, (n, 2))
    y = 5.0 * np.cos(0.5 * X[:, 0]) + rng.normal(0, 0.02, n)
    res = isaac.discover(X, y, name="pendulum")
    ties = res["rivals"]
    ok = len(ties) > 0
    correct = int(ok)
    print(f"  {'✓' if ok else '✗'}  narrow-range cosine: tie declared with "
          f"{[t['rival'] for t in ties]} (F {[t['F'] for t in ties]})")

    probes_out = [t for t in ties if t["probe"]["beyond"]]
    ok = len(probes_out) > 0
    correct += ok
    p0 = (probes_out or ties or [dict(probe=dict(x=0))])[0]["probe"]
    print(f"  {'✓' if ok else '✗'}  probe points OUTSIDE the observed range: "
          f"sample x0 near {p0.get('x')} (observed was ±1.2)")

    # the discriminating data arrives — the tie must resolve to the cosine
    X2 = rng.uniform(-4.5, 4.5, (600, 2))
    y2 = 5.0 * np.cos(0.5 * X2[:, 0]) + rng.normal(0, 0.02, 600)
    c = isaac.confirm("pendulum", X2, y2)
    eq = isaac.net.get_meta("law:pendulum", "equation")
    ok = c is not None and not c["rivals_left"] and "cos" in eq
    correct += ok
    print(f"  {'✓' if ok else '✗'}  confirm(): {c['status'] if c else None} "
          f"-> {eq[:60]}")

    # control: a TRUE parabola, same narrow range — must resolve the other way
    yb = 5.0 - 0.6 * X[:, 0] ** 2 + rng.normal(0, 0.02, n)
    isaac.discover(X, yb, name="bowl")
    y2b = 5.0 - 0.6 * X2[:, 0] ** 2 + rng.normal(0, 0.02, 600)
    cb = isaac.confirm("bowl", X2, y2b)
    eqb = isaac.net.get_meta("law:bowl", "equation")
    ok = cb is not None and not cb["rivals_left"] and "x0*x0" in eqb \
        and "cos" not in eqb.split("x0*x0")[0]
    correct += ok
    print(f"  {'✓' if ok else '✗'}  control (true parabola): "
          f"{cb['status'] if cb else None} -> {eqb[:60]}")

    print(f"\n  {correct}/4")
    return correct == 4


def test_spatial():
    _div("SPATIAL — the bridge: relations from motion, coordinates stay out")
    isaac = Isaac()
    rng = np.random.default_rng(23)

    def fourbar_frames(scale=1.0, rot=0.0, tx=0.0, ty=0.0, T=480,
                       noise=0.003):
        """Closed-form four-bar (crank 2, coupler 7, rocker 6, ground 8)
        under 2 crank cycles, arbitrary pose, gaussian measurement noise."""
        crank, coupler, rocker, ground = (x * scale for x in (2., 7., 6., 8.))
        c, s = np.cos(rot), np.sin(rot)
        p0 = np.array([tx, ty])
        p3 = p0 + ground * np.array([c, s])
        out = []
        for k in range(T):
            th = 4 * np.pi * k / T + rot
            p1 = p0 + crank * np.array([np.cos(th), np.sin(th)])
            d = np.linalg.norm(p3 - p1)
            a = (coupler ** 2 - rocker ** 2 + d ** 2) / (2 * d)
            h = np.sqrt(max(coupler ** 2 - a ** 2, 0.0))
            u = (p3 - p1) / d
            p2 = p1 + a * u + h * np.array([-u[1], u[0]])
            out.append(np.stack([p0, p1, p2, p3])
                       + rng.normal(0, noise * scale, (4, 2)))
        return np.array(out)

    # (a) perceive a four-bar; the facts must be queryable
    rel = isaac.observe_spatial(fourbar_frames(), label="fbA")
    q_locked = isaac.fact_index[("fbA.p0", "locked_to")]
    q_anchor = isaac.fact_index[("fbA", "anchored_at")]
    ok = (len(rel["parts"]) == 4 and len(rel["hinges"]) == 4
          and "fbA.p1" in q_locked and "fbA.p3" in q_locked
          and set(q_anchor) == {"fbA.p0", "fbA.p3"})
    correct = int(ok)
    print(f"  {'✓' if ok else '✗'}  four-bar perceived: 4 bars (incl. the "
          f"undeclared ground), 4 hinges; facts answer: p0 locked_to "
          f"{q_locked}, anchored {q_anchor}")

    # (b) recognition across pose and scale — relations are invariant
    isaac.observe_spatial(fourbar_frames(scale=2.4, rot=0.9, tx=6, ty=-2),
                          label="fbB")
    v = isaac.compare_scenes("fbA", "fbB")
    ok = v["verdict"] == "SAME"
    correct += ok
    print(f"  {'✓' if ok else '✗'}  same mechanism, 2.4x bigger, rotated, "
          f"moved: {v['verdict']} (signature gap {v.get('signature_gap')})")

    # (c) discrimination: a rigid plate swinging on a pin is NOT a four-bar
    sq = np.array([[0., 0.], [0., 3.], [2., 3.], [2., 0.]])
    plate = []
    for k in range(360):
        th = 1.2 * np.sin(2 * np.pi * k / 180)
        c, s = np.cos(th), np.sin(th)
        R = np.array([[c, -s], [s, c]])
        plate.append(sq @ R.T + rng.normal(0, 0.003, (4, 2)))
    isaac.observe_spatial(np.array(plate), label="plate")
    v = isaac.compare_scenes("fbA", "plate")
    ok = v["verdict"] == "DIFFERENT"
    correct += ok
    print(f"  {'✓' if ok else '✗'}  rigid plate on a pin vs four-bar: "
          f"{v['verdict']}")

    # (d) the null gate at the bridge: walkers must teach NOTHING
    walk = np.cumsum(rng.normal(0, 0.08, (500, 5, 2)), axis=0) \
        + rng.normal(0, 0.003, (500, 5, 2))
    before = sum(len(v_) for v_ in isaac.fact_index.values())
    reln = isaac.observe_spatial(walk, label="nothing")
    after = sum(len(v_) for v_ in isaac.fact_index.values())
    ok = before == after and not reln["locked"] and not reln["parts"]
    correct += ok
    print(f"  {'✓' if ok else '✗'}  random walkers: 0 relations survive the "
          f"nulls, 0 facts taught (index {before} -> {after})")

    print(f"\n  {correct}/4")
    return correct == 4


# ═════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Isaac — Unified Engine")
    print("One operation. All the way up.\n")

    results = {}
    results["language"] = test_language()
    results["math"] = test_math()
    results["logic"] = test_logic()
    results["reasoning"] = test_reasoning()
    results["decompose"] = test_decompose()
    results["persistence"] = test_persistence()
    results["waves"] = test_waves()
    results["tracking"] = test_tracking()
    results["discovery"] = test_discovery()
    results["rivalry"] = test_rivalry()
    results["spatial"] = test_spatial()

    _div("SUMMARY")
    for name, passed in results.items():
        print(f"  {'✓' if passed else '✗'}  {name}")
    total = sum(1 for v in results.values() if v)
    print(f"\n  {total}/{len(results)} capability areas passed")

    # Final status
    isaac = Isaac()
    for expr in ["the cat sat .", "3 + 5 = 8", "true and false = false",
                 "cat is_a mammal"]:
        isaac.observe(tokenize(expr))
    isaac.consolidate()
    st = isaac.status()
    print(f"\n  Quick status: {st['nodes']} nodes, {st['doors']} doors, "
          f"compiled={st['compiled']}, dirty_seqs={st['dirty_sequences']}")
    print(f"\n  One file. One class. One operation.")
