"""lag_battery.py — lag atoms: the temporal vocabulary (2026-07-12).

The causality probe measured the old cause-and-effect failure: on
y(t) = f(x(t-k)) raw discover scored r2 = 0.000 at EVERY lag k >= 1,
while hand-lagged columns healed it completely (r2 = 1.000, lag
NAMED). This battery gates the ENGINE lever: discover() now proposes
lag columns itself — null-gated (selection-corrected block-perm),
bracket + refine (no preset lag menu), honest per-row refusals where
history is missing, and zero behavior change on exchangeable rows.

Every check is a planted truth or a required refusal. Complete
numbers; no padding.
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                # noqa: E402

PASS, FAIL = 0, 0


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


def r2(truth, pred):
    truth, pred = np.asarray(truth, float), np.asarray(pred, float)
    ss = float(np.sum((truth - truth.mean()) ** 2))
    return 1 - float(np.sum((truth - pred) ** 2)) / max(ss, 1e-12)


def main():
    rng = np.random.default_rng(20260712)
    n = 900

    # ── 1+2. planted pure delay: said, and the lag NAMED ─────────
    x = rng.uniform(-2, 2, n)
    k = 3
    y = np.array([2 * x[t - k] ** 2 if t >= k else 0.0
                  for t in range(n)]) + rng.normal(0, 0.05, n)
    m = mod.Isaac()
    res = m.discover(x.reshape(-1, 1), y, name="delay")
    check("planted delay k=3: UNDERSTOOD held-out",
          res["verdict"] == "UNDERSTOOD" and res["r2"] >= 0.9,
          f"{res['verdict']} r2={res['r2']:.4f}")
    check("the lag is NAMED in the equation",
          "x0[t-3]" in res["equation"], res["equation"])

    # ── 3. mixed law: same-row AND lagged parts, both said ───────
    x0 = rng.uniform(-2, 2, n)
    x1 = rng.uniform(-2, 2, n)
    k2 = 5
    ym = 1.5 * x0 + np.array(
        [2 * x1[t - k2] ** 2 if t >= k2 else 0.0 for t in range(n)]) \
        + rng.normal(0, 0.05, n)
    mm = mod.Isaac()
    rm = mm.discover(np.column_stack([x0, x1]), ym, name="mixed")
    check("mixed same-row + lagged: both parts said",
          rm["verdict"] == "UNDERSTOOD" and "x0" in rm["equation"]
          and "x1[t-5]" in rm["equation"],
          f"{rm['verdict']} r2={rm['r2']:.4f}  {rm['equation']}")

    # ── 4. apply on a fresh series: exact refusals + accuracy ────
    xf = rng.uniform(-2, 2, 400)
    yf = np.array([2 * xf[t - k] ** 2 if t >= k else 0.0
                   for t in range(400)])
    p = m.apply_law("delay", xf.reshape(-1, 1))
    fin = np.isfinite(p)
    ok_ref = int((~fin).sum()) == k
    ok_acc = r2(yf[fin], p[fin]) >= 0.9
    check("apply: exactly k history-less rows refuse, rest accurate",
          ok_ref and ok_acc,
          f"refused={int((~fin).sum())}/{len(p)} (k={k}), "
          f"answered r2={r2(yf[fin], p[fin]):.4f} on {int(fin.sum())} rows")

    # ── 5. validate_law: refusals reported, answered rows judged ─
    v = m.validate_law("delay", xf.reshape(-1, 1), yf)
    last = m.findings[-1]
    check("validate_law: HOLDS + refused count in the finding",
          v is not None and v["status"] == "HOLDS"
          and last.get("refused_rows") == k,
          f"{v['status']} r2={v['r2']:.4f} refused_rows="
          f"{last.get('refused_rows')}")

    # ── 6. exchangeable rows: the vocabulary is UNCHANGED ────────
    xi = rng.uniform(-2, 2, 600)
    yi = 3 * xi + rng.normal(0, 0.05, 600)
    props = m._propose_lags(xi.reshape(-1, 1), yi)
    check("iid rows: zero lag proposals (vocabulary unchanged)",
          props == [], f"proposals={props}")

    # ── 7. scrambled-time kill: the null destroys fake time ──────
    sh = rng.permutation(n)
    props2 = m._propose_lags(x[sh].reshape(-1, 1), y[sh])
    check("scrambled-time kill: zero proposals survive",
          props2 == [], f"proposals={props2}")

    # ── 8. autocorrelated decoy: no false LAW on unrelated pairs ─
    # y and x both slow AR(1) series, UNRELATED — the classic false-
    # lag trap. A rare shift-coincidence may still PROPOSE (expansion
    # is free); the claim gated here is end-to-end: admission +
    # held-out validation must never SAY a lag law on independence.
    false_laws, proposals = 0, 0
    for trial in range(10):
        r = np.random.default_rng(100 + trial)
        e1, e2 = r.normal(0, 1, n), r.normal(0, 1, n)
        xa = np.zeros(n)
        ya = np.zeros(n)
        for t in range(1, n):
            xa[t] = 0.9 * xa[t - 1] + e1[t]
            ya[t] = 0.9 * ya[t - 1] + e2[t]
        md = mod.Isaac()
        rd = md.discover(xa.reshape(-1, 1), ya, name=f"decoy{trial}")
        proposals += len(md._last_lag_scan) and len(
            [1 for _, kk, s, g in md._last_lag_scan if s > g])
        if rd["verdict"] in ("UNDERSTOOD", "PARTIAL") \
                and "[t-" in rd["equation"]:
            false_laws += 1
    check("unrelated AR(1) pair x10: zero false lag LAWS said",
          false_laws == 0,
          f"false laws={false_laws}/10, gate-passing proposals="
          f"{proposals}/10 (proposals are free; admission compresses)")

    # ── 9. two delays of ONE channel: both named ─────────────────
    y2 = np.array([(x[t - 2] if t >= 2 else 0.0)
                   - 0.5 * (x[t - 6] ** 2 if t >= 6 else 0.0)
                   for t in range(n)]) + rng.normal(0, 0.03, n)
    m2 = mod.Isaac()
    r2l = m2.discover(x.reshape(-1, 1), y2, name="twolags")
    check("two lags, one column: both said",
          r2l["verdict"] == "UNDERSTOOD" and "x0[t-2]" in r2l["equation"]
          and "x0[t-6]" in r2l["equation"],
          f"{r2l['verdict']} r2={r2l['r2']:.4f}  {r2l['equation']}")

    # ── 10. long lag, iid driver: every integer lag is measured ──
    # (v1's coarse ladder + refine LOST exactly here: an off-by-one
    # lag on an iid driver carries zero signal, so anchors 29 and 41
    # bracket nothing — wrong-kept in the engine banner)
    nL, kL = 2000, 40
    xL = rng.uniform(-2, 2, nL)
    yL = np.array([1.5 * xL[t - kL] if t >= kL else 0.0
                   for t in range(nL)]) + rng.normal(0, 0.05, nL)
    mL = mod.Isaac()
    rL = mL.discover(xL.reshape(-1, 1), yL, name="longlag")
    check("long lag k=40, iid driver: found exactly",
          rL["verdict"] == "UNDERSTOOD" and "x0[t-40]" in rL["equation"],
          f"{rL['verdict']} r2={rL['r2']:.4f}  {rL['equation']}")

    # ── 11. persistence: a lag law survives the ledger round-trip ─
    import json
    import tempfile
    fd, ledger = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for e in m.findings:
            f.write(json.dumps(e, default=str) + "\n")
    fresh = mod.Isaac()
    fresh.load_ledger(ledger)
    os.unlink(ledger)
    p2 = fresh.apply_law("delay", xf.reshape(-1, 1))
    same = (p2 is not None and np.isfinite(p2).sum() == fin.sum()
            and np.allclose(p2[fin], p[fin]))
    check("ledger round-trip: lag law rebuilt identically",
          same, f"answered rows match: {same}")

    # ── 12. law_confidence: honest on history-less rows ──────────
    conf = m.law_confidence("delay", xf.reshape(-1, 1))
    ok_conf = (conf is not None and np.isnan(conf[:k]).all()
               and np.isfinite(conf[k:]).all())
    check("law_confidence: NaN without history, finite with it",
          ok_conf,
          f"first {k} NaN={bool(np.isnan(conf[:k]).all())}, "
          f"rest finite={bool(np.isfinite(conf[k:]).all())}")

    # ── 13. refine() refuses a lag law with the why ───────────────
    rr = m.refine("delay", xf.reshape(-1, 1), yf,
                  ask=lambda Q: np.zeros(len(Q)))
    check("refine on a lag law: refusal with the reason",
          isinstance(rr, dict) and "refused" in rr,
          str(rr.get("refused", ""))[:60])

    # ── 14. the probe's headline, raw road: k=8 heals ─────────────
    k8 = 8
    y8 = np.array([2 * x[t - k8] ** 2 if t >= k8 else 0.0
                   for t in range(n)]) + rng.normal(0, 0.05, n)
    m8 = mod.Isaac()
    r8 = m8.discover(x.reshape(-1, 1), y8, name="delay8")
    check("causality-probe world k=8 through PLAIN discover",
          r8["verdict"] == "UNDERSTOOD" and r8["r2"] >= 0.9
          and "x0[t-8]" in r8["equation"],
          f"{r8['verdict']} r2={r8['r2']:.4f}  {r8['equation']}")

    print()
    print(f"LAG BATTERY: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
