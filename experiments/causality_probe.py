"""causality_probe.py — is the old failure fixed? (owner, 2026-07-12:
"it was very bad with cause and effect. it sucked at long term
things. it would perform well for about 5 sec then just die and
loop.")

Nothing is asserted here — this probe MEASURES the failure:

P1 the delay curve: y(t) = f(x(t-k)); raw discover on aligned rows
   for k = 0..8 — where does the causal link die?
P2 the lag-vocabulary candidate: the same worlds with lagged columns
   offered as features — does the curve heal, and does discover NAME
   the right lag?
P3 rollout drift + the die-and-loop signature: learn x(t+1)=f(x(t)),
   iterate forward; measure the horizon where error passes 10% of
   signal, and let the structural patterner say whether the rollout
   fell into a cycle the truth does not have.
P4 chain composition: laws A->B and B->C learned separately,
   composed A->C; error per hop.
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from isaac_store import bridge                    # noqa: E402
from isaac_store.structural import analyze        # noqa: E402


def r2(truth, pred):
    """Lag laws refuse rows without history (NaN, 2026-07-12): score
    the answered rows — refusals are answers, not crashes."""
    truth, pred = np.asarray(truth, float), np.asarray(pred, float)
    fin = np.isfinite(pred)
    truth, pred = truth[fin], pred[fin]
    if not len(truth):
        return float("-inf")
    ss = float(np.sum((truth - truth.mean()) ** 2))
    return 1 - float(np.sum((truth - pred) ** 2)) / max(ss, 1e-12)


def fit_apply(mod, X, y, Xtest, name):
    mind = mod.Isaac()
    mind.discover(X, y, name=name)
    p = mind.apply_law(name, Xtest)
    eq = mind.findings[-1].get("equation")
    return p, eq


def main():
    print("  loading engine...")
    mod = bridge.load_isaac_module()
    rng = np.random.default_rng(97)
    n = 900
    lines = ["CAUSALITY PROBE — 2026-07-12", ""]

    print("P1/P2. the delay curve: raw road (engine's own lag atoms)"
          " vs hand-lagged columns")
    lines.append("P1/P2  delayed cause y(t) = 2*x(t-k)^2 + noise")
    lines.append("       (2026-07-12: the engine now PROPOSES lag atoms"
                 " itself — P1 measures the raw road healed):")
    lines.append("       k | raw r2 | raw named | hand-lagged r2 | "
                 "raw equation")
    x = rng.uniform(-2, 2, n)
    LAGS = 8
    for k in (0, 1, 2, 4, 8):
        y = np.array([2 * x[t - k] ** 2 if t >= k else 0.0
                      for t in range(n)]) + rng.normal(0, 0.05, n)
        # raw: ONE aligned column — before lag atoms this scored
        # r2 = 0.000 for every k >= 1 (temporal blindness, measured)
        Xr = x[LAGS:].reshape(-1, 1)
        yr = y[LAGS:]
        cut = int(len(yr) * 0.75)
        p_raw, eq_r = fit_apply(mod, Xr[:cut], yr[:cut], Xr[cut:],
                                f"raw{k}")
        raw = r2(yr[cut:], p_raw) if p_raw is not None else 0.0
        named_r = (f"x0[t-{k}]" in str(eq_r)) if k else \
            ("x0" in str(eq_r) and "[t-" not in str(eq_r))
        # hand-lagged columns: the pre-fix road, kept as comparison
        # (equations may say the same law through equivalent columns,
        # e.g. x2[t-2] == x(t-4) — names not graded here)
        Xl = np.column_stack([x[LAGS - j:n - j] for j in range(LAGS + 1)])
        p_lag, _ = fit_apply(mod, Xl[:cut], yr[:cut], Xl[cut:], f"lag{k}")
        lag = r2(yr[cut:], p_lag) if p_lag is not None else 0.0
        lines.append(f"       {k} |  {max(raw,0):.3f} |    "
                     f"{'YES' if named_r else 'no '}    |      "
                     f"{max(lag,0):.3f}     | {str(eq_r)[:38]}")

    print("P3. rollout drift + die-and-loop")
    # the Henon map: bounded, sustained, EXACTLY polynomial (fully in
    # vocabulary), and truly aperiodic — chaos bounds ANY forecaster
    # (Lyapunov), so the diagnostic here is not the horizon alone but
    # the SIGNATURE: does the rollout collapse into a loop the truth
    # does not have?
    def step(s):
        a, b = s
        return np.array([1.0 - 1.4 * a * a + b, 0.3 * a])
    traj = [np.array([0.1, 0.1])]
    for _ in range(n):
        traj.append(step(traj[-1]))
    traj = np.array(traj)
    S, S1 = traj[:-1], traj[1:]
    cut = int(len(S) * 0.75)
    minds = []
    for dim in (0, 1):
        m = mod.Isaac()
        m.discover(S[:cut], S1[:cut, dim], name="f")
        minds.append(m)
    preds = [minds[d].apply_law("f", S[cut:]) for d in (0, 1)]
    onestep = [r2(S1[cut:, d], p) if p is not None else float("-inf")
               for d, p in enumerate(preds)]
    lines.append("")
    lines.append(f"P3     one-step law quality: r2 = "
                 f"{onestep[0]:.4f}, {onestep[1]:.4f}")
    s = traj[cut].copy()
    scale = traj[:, 0].std()
    horizon = None
    roll = []
    for h in range(1, 200):
        pred = np.array([minds[d].apply_law("f", s.reshape(1, -1))[0]
                         for d in (0, 1)])
        roll.append(pred.copy())
        true = traj[cut + h]
        if horizon is None and abs(pred[0] - true[0]) > 0.1 * scale:
            horizon = h
        s = pred
    roll = np.array(roll)
    sym = ["".join(f"{'p' if v>0 else 'n'}" for v in r) for r in
           np.round(roll, 2)]
    st = analyze([f"{a:.2f}" for a in roll[:, 0]])
    truth_st = analyze([f"{a:.2f}" for a in traj[cut + 1:cut + 200, 0]])
    lines.append(f"       drift horizon (error > 10% of signal): "
                 f"{horizon if horizon else '>199'} steps")
    lines.append(f"       rollout structure: {st['pattern']}"
                 f"{' — period ' + str(st['levels'][0]['constraints'].get('global_period')) if st.get('levels') and 'global_period' in st['levels'][0]['constraints'] else ''}"
                 f" | truth structure: {truth_st['pattern']}")

    print("P4. chain composition")
    a4 = rng.uniform(-2, 2, n)
    b4 = 1.5 * a4 - 0.4 * a4 ** 2 + rng.normal(0, 0.03, n)
    c4 = np.sin(1.0 * b4) + 0.5 * b4 + rng.normal(0, 0.03, n)
    cut = int(n * 0.75)
    mAB = mod.Isaac(); mAB.discover(a4[:cut].reshape(-1, 1), b4[:cut], name="ab")
    mBC = mod.Isaac(); mBC.discover(b4[:cut].reshape(-1, 1), c4[:cut], name="bc")
    b_hat = mAB.apply_law("ab", a4[cut:].reshape(-1, 1))
    c_direct = mBC.apply_law("bc", b4[cut:].reshape(-1, 1))
    c_chain = mBC.apply_law("bc", b_hat.reshape(-1, 1))
    lines.append("")
    lines.append(f"P4     hop1 (A->B): r2={r2(b4[cut:], b_hat):.4f} | "
                 f"hop2 alone (B->C): r2={r2(c4[cut:], c_direct):.4f} | "
                 f"composed (A->B->C): r2={r2(c4[cut:], c_chain):.4f}")

    report = "\n".join(lines)
    print()
    print(report)
    out_dir = os.path.join(ROOT, "experiments", "runs", "2026-07-12")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "causality_probe.txt"), "w",
              encoding="utf-8") as f:
        f.write(report + "\n")


if __name__ == "__main__":
    main()
