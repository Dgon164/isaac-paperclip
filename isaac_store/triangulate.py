"""Triangulation — incomplete information across datasets (owner
design, 2026-07-12): "variable x that is explored in a different
dataset entirely, and it is only through comparing a and b datasets
together that you can resolve it. where they are both halves of the
same whole, but not contained in any single domain."

Two roads, tried in order:

  COMPLETION — A's missing variable is B's COLUMN. Join on the
  shared key, discover A's target over the joint feature space; the
  gain over A-alone must beat the SCRAMBLED-PAIRING NULL (the same
  joint model evaluated under permuted alignment — a real resolution
  dies when the pairing is scrambled, a coincidence survives).

  HALVES — the latent lives in NEITHER dataset: each side's
  articulated residual is a different mixture of the same hidden
  things (A sees x+s, B sees x-s). If the residuals agree across the
  join beyond the scrambled null, the mixtures are unmixed:
  x = (rA+rB)/2, s = (rA-rB)/2 — both halves of the same whole.

Refusals are answers: NO ALIGNMENT (no shared key), NO CLOSURE (the
halves do not close — joint structure within the null). Complete
numbers throughout: alone vs joint vs scrambled.

A KNOWN LIMIT, kept honestly (found by this module's own battery):
two GAUSSIAN latents of EQUAL variance in sum/difference mixtures
are unresolvable IN PRINCIPLE — the rotated pair is distributionally
identical to an independent pair (the classic ICA identifiability
limit). Isaac correctly refuses that case; the halves road needs
some asymmetry (unequal variances or non-Gaussian latents), which
real-world latents almost always have.
"""
import numpy as np

from . import bridge


def _to_xy(table, target=None):
    cols = table["columns"]
    ti = cols.index(target) if target else len(cols) - 1
    rows = np.asarray(table["rows"], float)
    keep = [i for i in range(len(cols)) if i != ti]
    return [cols[i] for i in keep], rows[:, keep], rows[:, ti]


def _shared_key(ta, tb, target_a, target_b):
    a_cols = [c for c in ta["columns"] if c != (target_a or ta["columns"][-1])]
    b_cols = [c for c in tb["columns"] if c != (target_b or tb["columns"][-1])]
    shared = [c for c in a_cols if c in b_cols]
    return shared[0] if len(shared) == 1 else None


def _fit(mod, X, y, name):
    """Discover on a 75/25 split; return (model_mind, holdout_r2,
    residual_fn) — residuals from the ARTICULATED part only."""
    n = len(y)
    order = np.random.default_rng(0).permutation(n)
    tr, ho = order[:int(n * 0.75)], order[int(n * 0.75):]
    mind = mod.Isaac()
    mind.discover(X[tr], y[tr], name=name)
    p = mind.apply_law(name, X[ho])
    if p is None:
        mean = float(y[tr].mean())
        return mind, 0.0, lambda XX, yy: yy - mean
    ss = float(np.sum((y[ho] - y[ho].mean()) ** 2))
    r2 = 1 - float(np.sum((y[ho] - p) ** 2)) / max(ss, 1e-12)

    def resid(XX, yy):
        pr = mind.apply_law(name, XX)
        return yy - (pr if pr is not None else float(y[tr].mean()))
    return mind, max(r2, 0.0), resid


def triangulate(table_a, table_b, target_a=None, target_b=None,
                mod=None, n_null=40, seed=5):
    mod = mod or bridge.load_isaac_module()
    rng = np.random.default_rng(seed)
    key = _shared_key(table_a, table_b, target_a, target_b)
    if key is None:
        return dict(verdict="NO ALIGNMENT",
                    why="no single shared column to join on — "
                        "triangulation needs a correspondence")

    # ---- align on the key (inner join, 1:1 by first occurrence)
    na, Xa, ya = _to_xy(table_a, target_a)
    nb, Xb, yb = _to_xy(table_b, target_b)
    ka, kb = na.index(key), nb.index(key)
    map_b = {}
    for i in range(len(yb)):
        map_b.setdefault(round(float(Xb[i, ka if False else kb]), 6), i)
    pairs = [(i, map_b[round(float(Xa[i, ka]), 6)])
             for i in range(len(ya))
             if round(float(Xa[i, ka]), 6) in map_b]
    coverage = len(pairs) / max(len(ya), 1)
    if coverage < 0.5:
        return dict(verdict="NO ALIGNMENT", key=key,
                    why=f"join coverage only {coverage:.0%}")
    ia = np.array([p[0] for p in pairs])
    ib = np.array([p[1] for p in pairs])
    fa = [j for j in range(len(na)) if j != ka]   # features minus key
    fb = [j for j in range(len(nb)) if j != kb]
    Af, Bf = Xa[ia][:, fa], Xb[ib][:, fb]
    yA, yB = ya[ia], yb[ib]
    names_a = [na[j] for j in fa]
    names_b = [nb[j] for j in fb]

    # ---- each side alone (the honest baseline)
    _, r2_a_alone, resid_a = _fit(mod, Af, yA, "tri_a_alone")
    _, r2_b_alone, resid_b = _fit(mod, Bf, yB, "tri_b_alone")

    # ---- ROAD 1: COMPLETION — the partner's columns join the space
    joint = np.column_stack([Af, Bf])
    mind_j, r2_joint, _ = _fit(mod, joint, yA, "tri_joint")
    gain = r2_joint - r2_a_alone
    null_gains = []
    for _ in range(n_null):
        perm = rng.permutation(len(yA))
        pj = mind_j.apply_law("tri_joint",
                              np.column_stack([Af, Bf[perm]]))
        if pj is None:
            null_gains.append(0.0)
            continue
        ss = float(np.sum((yA - yA.mean()) ** 2))
        null_gains.append((1 - float(np.sum((yA - pj) ** 2))
                           / max(ss, 1e-12)) - r2_a_alone)
    null95 = float(np.percentile(null_gains, 95))
    numbers = dict(key=key, joined_rows=len(pairs),
                   coverage=round(coverage, 3),
                   alone=dict(A=round(r2_a_alone, 4),
                              B=round(r2_b_alone, 4)))
    if gain > 0.1 and gain > null95:
        f = dict(mind_j.findings[-1])
        return dict(verdict="RESOLVED — COMPLETION", **numbers,
                    joint_r2=round(r2_joint, 4), gain=round(gain, 4),
                    scrambled_null95=round(null95, 4),
                    equation=f.get("equation"),
                    columns=names_a + names_b,
                    why=f"B's columns complete A's law: r2 "
                        f"{r2_a_alone:.3f} alone -> {r2_joint:.3f} "
                        f"joint; scrambled pairing gives "
                        f"<= {null95:.3f}")

    # ---- ROAD 2: HALVES — the residuals are mixtures of shared latents
    rA = resid_a(Af, yA)
    rB = resid_b(Bf, yB)
    corr = float(np.corrcoef(rA, rB)[0, 1])
    # CONFIRMATION, not one lucky pass: the agreement must hold in
    # BOTH halves of the join independently, same sign, each beating
    # its own scrambled null — chance does not repeat itself
    half = len(rA) // 2
    halves_ok = True
    for lo, hi in ((0, half), (half, len(rA))):
        ra, rb = rA[lo:hi], rB[lo:hi]
        ch = float(np.corrcoef(ra, rb)[0, 1])
        null_h = [abs(float(np.corrcoef(ra, rb[rng.permutation(len(rb))])
                            [0, 1])) for _ in range(n_null)]
        if abs(ch) <= float(np.percentile(null_h, 95)) or \
                np.sign(ch) != np.sign(corr):
            halves_ok = False
            break
    null_corr = []
    for _ in range(n_null):
        perm = rng.permutation(len(rB))
        null_corr.append(abs(float(np.corrcoef(rA, rB[perm])[0, 1])))
    c95 = float(np.percentile(null_corr, 95))
    if halves_ok and abs(corr) > c95 and abs(corr) > 0.1:
        sign = 1.0 if corr > 0 else -1.0
        x_hat = (rA + sign * rB) / 2.0
        s_hat = (rA - sign * rB) / 2.0
        keys = Xa[ia][:, ka]
        return dict(verdict="RESOLVED — HALVES", **numbers,
                    residual_corr=round(corr, 4),
                    scrambled_null95=round(c95, 4),
                    latents=dict(
                        keys=keys.tolist(),
                        x=x_hat.tolist(), s=s_hat.tolist(),
                        note="x = the shared half (sum road); "
                             "s = the opposed half (difference road); "
                             "signs up to the mixing convention"),
                    why=f"the two leftovers agree across the join "
                        f"(corr {corr:.3f}, scrambled <= {c95:.3f}): "
                        f"two mixtures of the same hidden pair, "
                        f"unmixed")
    return dict(verdict="NO CLOSURE", **numbers,
                residual_corr=round(corr, 4),
                scrambled_null95=round(c95, 4),
                why="the halves do not close: joint structure is "
                    "within what scrambled pairing produces")
