"""
RED TEAM — THE MATRIX-CREATOR.  Try to make assemble() (matrix_assembler.py) FABRICATE.

The load-bearing claim: "missing is an ABSENT dimension, never fabricated away."
  complete : keep rows present in JUST the used columns (never a global drop).
  pad      : impute the value AND add a presence flag 'col?' so absence is recorded.

Attacks:
  - does complete return exactly the present rows, with no NaN leaking through?
  - does pad's flag column exactly mark where the value was real?
  - does mean-imputation ever MANUFACTURE a law that isn't in the real data?
  - when the SIGNAL is the absence (MNAR), does pad surface it as the flag (honest)
    or launder it into the imputed value (fabrication)?
  - complete under INFORMATIVE missingness: the honest limit — a biased subset.
"""
import sys, os, re, numpy as np, pandas as pd
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE); sys.path.insert(0, os.path.join(_HERE, ".."))
from isaac import Isaac
import matrix_assembler as ma

TITLE = "RED TEAM — THE MATRIX-CREATOR (no-fabrication gates)"


def _discover(df, target, predictors, mode):
    X, y, names, n_avail = ma.assemble(df, target, predictors, mode)
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-9)
    ys = (y - y.mean()) / (y.std() + 1e-9)
    r = Isaac().discover(Xs, ys, name=target)
    eq = re.sub(r"x(\d+)", lambda m: names[int(m.group(1))] if int(m.group(1)) < len(names)
                else m.group(0), r["equation"])
    return r, eq, X, y, names


def run():
    results = []
    rng = np.random.default_rng(0)
    N = 1000

    # ---- build a controlled ragged frame ----
    y_all = rng.normal(0, 1, N)
    p_full = rng.normal(0, 1, N)
    present = rng.random(N) < 0.5                       # MCAR mask, ~50%
    p_mcar = np.where(present, p_full, np.nan)

    df = pd.DataFrame({"y": y_all, "p": p_mcar})

    # 1. COMPLETE — exact present rows, no NaN fabricated in.
    X, y, names, n_avail = ma.assemble(df, "y", ["p"], "complete")
    want = int(np.isfinite(p_mcar).sum())
    ok = (len(y) == want) and np.all(np.isfinite(X))
    results.append(("complete: exact rows, no NaN", f"rows=={want}, finite",
                    f"rows={len(y)} finite={bool(np.all(np.isfinite(X)))}",
                    "PASS" if ok else "FAIL"))

    # 2. PAD — flag column marks presence EXACTLY; no NaN.
    Xp, yp, namesp, _ = ma.assemble(df, "y", ["p"], "pad")
    flag = Xp[:, namesp.index("p?")]
    flag_ok = np.array_equal(flag, present.astype(float)) and np.all(np.isfinite(Xp))
    results.append(("pad: flag == presence, no NaN", "flag exact & finite",
                    f"flag_match={np.array_equal(flag, present.astype(float))} "
                    f"finite={bool(np.all(np.isfinite(Xp)))}",
                    "PASS" if flag_ok else "FAIL"))

    # 3. PAD on pure noise — imputation must NOT manufacture a law.
    df3 = pd.DataFrame({"y": rng.normal(0, 1, N),
                        "p": np.where(rng.random(N) < 0.3, rng.normal(0, 1, N), np.nan)})
    r3, eq3, *_ = _discover(df3, "y", ["p"], "pad")
    results.append(("pad noise -> no law", "not UNDERSTOOD", f"{r3['verdict']} R2 {r3['r2']:.2f}",
                    "PASS" if r3["verdict"] != "UNDERSTOOD" else "FAIL"))

    # 4. MNAR — the SIGNAL is the absence itself. Honest = surface it as the flag,
    #    fabrication = launder it into the imputed value.
    pres4 = rng.random(N) < 0.5
    y4 = 5.0 * pres4 + rng.normal(0, 0.5, N)            # y depends on WHETHER p exists
    p4 = np.where(pres4, rng.normal(0, 1, N), np.nan)   # p's VALUE is uninformative noise
    df4 = pd.DataFrame({"y": y4, "p": p4})
    r4, eq4, X4, _, names4 = _discover(df4, "y", ["p"], "pad")
    vcol = X4[:, names4.index("p")]; fcol = X4[:, names4.index("p?")]
    c_val = abs(np.corrcoef(vcol, y4)[0, 1]); c_flag = abs(np.corrcoef(fcol, y4)[0, 1])
    surfaced = ("p?" in eq4) and r4["verdict"] != "NO RULE" and c_flag > 3 * c_val
    results.append(("MNAR: absence surfaces as flag", "flag carries, value doesn't",
                    f"{r4['verdict']} |c_flag|={c_flag:.2f} |c_val|={c_val:.2f} flag_in_eq={'p?' in eq4}",
                    "PASS" if surfaced else "FAIL"))

    # 5. PAD impute artifact — real law y=2p on present rows, half missing (MCAR). Does the
    #    mean-imputed cluster corrupt the recovered slope, or does the flag absorb it?
    pres5 = rng.random(N) < 0.5
    p5_full = rng.normal(0, 1, N)
    y5 = 2.0 * p5_full + rng.normal(0, 0.3, N)
    p5 = np.where(pres5, p5_full, np.nan)
    df5 = pd.DataFrame({"y": y5, "p": p5})
    # ground-truth slope on present rows only:
    b_true = np.polyfit(p5_full[pres5], y5[pres5], 1)[0]
    r5, eq5, X5, yy5, names5 = _discover(df5, "y", ["p"], "pad")
    #   recover a slope of y on the (unstandardized) imputed value column, controlling flag:
    M = np.column_stack([X5[:, names5.index("p")], X5[:, names5.index("p?")], np.ones(len(yy5))])
    b_pad = np.linalg.lstsq(M, yy5, rcond=None)[0][0]
    slope_ok = abs(b_pad - b_true) < 0.25 * abs(b_true)
    results.append(("pad impute: slope not corrupted", f"slope~={b_true:.2f}",
                    f"{r5['verdict']} pad-slope={b_pad:.2f} (true {b_true:.2f})",
                    "PASS" if slope_ok else "FAIL"))

    # 6. COMPLETE under COLLIDER selection (Berkson) — the honest LIMIT, sharp form. y and p
    #    are INDEPENDENT (full corr ~0), but p is missing based on a collider of the two, so
    #    the complete subset INVENTS a correlation that isn't in the population. Complete-case
    #    analysis assumes missingness independent of the relationship; when it isn't, the
    #    assembled matrix carries a fabricated association. This is a limit of complete, not a
    #    bug in assemble — surfaced so a downstream 'law' on it is known to be suspect.
    a = rng.normal(0, 1, N); b = rng.normal(0, 1, N)   # independent
    y6, p6_full = a, b                                  # true corr(p,y) = corr(b,a) ~ 0
    keep = (a + b) > 0.3                                # select on the collider a+b
    p6 = np.where(keep, p6_full, np.nan)
    df6 = pd.DataFrame({"y": y6, "p": p6})
    c_full = np.corrcoef(p6_full, y6)[0, 1]
    Xc, yc, _, _ = ma.assemble(df6, "y", ["p"], "complete")
    c_sub = np.corrcoef(Xc[:, 0], yc)[0, 1]
    fabricated = abs(c_full) < 0.1 and abs(c_sub) > 0.3
    results.append(("complete: collider selection bias", "independent -> subset INVENTS corr",
                    f"full r={c_full:+.2f} complete-subset r={c_sub:+.2f} fabricated={fabricated}",
                    "LIMIT" if fabricated else "FAIL"))

    return results


def report(results, title):
    print("=" * 100)
    print(f"  {title}")
    print("=" * 100)
    for name, expect, got, status in results:
        tag = {"PASS": "[PASS] ", "FAIL": "[FAIL] ", "LIMIT": "[LIMIT]"}[status]
        print(f"  {tag} {name:34s} expect: {expect:34s} got: {got}")
    p = sum(s == "PASS" for *_, s in results)
    f = sum(s == "FAIL" for *_, s in results)
    l = sum(s == "LIMIT" for *_, s in results)
    print("-" * 100)
    print(f"  {p} held, {f} failed, {l} known-limit  (of {len(results)})")
    print("=" * 100)
    return p, f, l


if __name__ == "__main__":
    report(run(), TITLE)
