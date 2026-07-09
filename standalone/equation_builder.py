# -*- coding: utf-8 -*-
"""THE ENUMERATION ALGEBRA — Isaac's equation builder, extracted verbatim
from isaac.py (commit-current, 2026-07-08). Standalone: numpy only.

What it does: given examples (X, y) of something it cannot do, it BUILDS
THE EQUATION — an explicit, human-readable algebraic law — or refuses.
See docs/EQUATION_BUILDER.md for the write-up.

This file is the REAL code (copied, not paraphrased) plus a thin
build_equation() wrapper and a self-demonstration. In the engine the
same class is wrapped by discover(), which adds held-out verdicts,
accounting (articulated+captured+noise=100), rivals with probes,
residual dossiers, and the ledger.
"""
import numpy as np
from collections import defaultdict

_wave_rng = np.random.default_rng(2718)   # the engine's shared null rng


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
    op = {"cosd": "cos", "sind": "sin", "coshd": "cosh"}[kind]
    return f"{op}({k:g}*(x{i}-x{j}))"


def _disc_col(A, term):
    v = A[:, term[0]].copy()
    for a in term[1:]:
        v = v * A[:, a]
    return v


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
        is white (block_L == 1), circular moving-block permutation when it
        is autocorrelated (blocks of the MEASURED length, random phase)."""
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
        return blocks[_wave_rng.permutation(nb)].ravel()[:n]

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
            p_min = 8.0 * span / n        # >= ~8 samples per cycle
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

            def best_fold(vals):
                # coarse map, then a fine scan around the winner — the null
                # replays BOTH stages, so selection stays corrected
                best, bestP = 0.0, None
                for P in Ps:
                    r = fold_score(vals, P)
                    if r > best:
                        best, bestP = r, P
                if bestP is not None:
                    for P in np.linspace(bestP * 0.93, bestP * 1.07, 33):
                        r = fold_score(vals, P)
                        if r > best:
                            best, bestP = r, P
                return best, bestP

            real, realP = best_fold(ys)
            if realP is None:
                continue
            null = np.empty(n_perm)
            for k in range(n_perm):
                null[k] = best_fold(self._null_perm(ys))[0]
            if real > np.percentile(null, pct):
                proposals.append((i, 2.0 * np.pi / realP))
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

    def _refine_term(self, y, ti, sweeps=2):
        improved_any = False
        for _ in range(sweeps):
            improved = False
            t = self.terms[ti]
            for pos, ai in enumerate(t):
                kind, i, j, k = self.specs[ai]
                if k is None:
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




# ── thin wrapper: the discover() core without the Isaac plumbing ──────
def build_equation(X, y, seed_split=0):
    """Fit on half, judge on the held-out half (the rule must WORK, not
    merely fit). Returns dict(verdict, equation, r2_train, r2_held)."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    rng = np.random.default_rng(seed_split)
    idx = rng.permutation(len(y))
    cut = len(y) // 2
    tr, he = idx[:cut], idx[cut:]
    e = _Enumerator().fit(X[tr], y[tr])
    def pred(Xs):
        if not e.terms:
            return np.full(len(Xs), float(np.mean(y[tr])))
        A = np.column_stack([_atom_col(Xs, s) for s in e.specs])
        M = np.column_stack([_disc_col(A, t) for t in e.terms])
        return M @ e.coefs + e.intercept
    def r2(yy, pp):
        ss = float(np.sum((yy - yy.mean()) ** 2))
        return 1 - float(np.sum((yy - pp) ** 2)) / max(ss, 1e-12)
    r2_tr = r2(y[tr], pred(X[tr]))
    r2_he = r2(y[he], pred(X[he]))
    verdict = ("UNDERSTOOD" if r2_he >= 0.9 else
               "PARTIAL" if e.terms and r2_he > 0.2 else "NO RULE")
    return dict(verdict=verdict, equation=e.equation(),
                r2_train=round(r2_tr, 4), r2_held=round(r2_he, 4))


if __name__ == "__main__":
    rng = np.random.default_rng(5)

    print("1) planted law with noise: y = 2*ln|x0| + 0.5*x1*x2")
    X = rng.normal(size=(500, 3))
    y = 2 * np.log(np.abs(X[:, 0]) + 1e-9) + 0.5 * X[:, 1] * X[:, 2]         + 0.05 * rng.normal(size=500)
    r = build_equation(X, y)
    print(f"   {r['verdict']}  held-out R2 {r['r2_held']}")
    print("   " + r["equation"]); print()

    print("2) pure noise: it must REFUSE")
    yn = rng.normal(size=500)
    r = build_equation(X, yn)
    print("   " + r["verdict"] + "  (" + r["equation"] + ")"); print()

    print("3) autocorrelated noise vs time (the sunspot-runaway shape):")
    t = np.linspace(0, 10, 500).reshape(-1, 1)
    ar = np.zeros(500)
    for k in range(1, 500):
        ar[k] = 0.9 * ar[k - 1] + rng.normal()
    r = build_equation(t, ar)
    print(f"   {r['verdict']}  — no false UNDERSTOOD: the block-permutation"
          " null keeps junk from certifying (PARTIAL = range-valid at best)")
