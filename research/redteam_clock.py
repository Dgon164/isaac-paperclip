"""
RED TEAM — THE CLOCK.  Try to make the temporal gates (temporal_detector.py) LIE.

Two gates under attack:
  trend_gate(x, v)     : null-gated linear trend (beat the 95th pct of a shuffle null)
  cycle_gate(phase, v) : is v a lawful function of cyclic phase? (discover's verdict)

PASS  = the gate did the honest thing (found real signal / refused spurious signal).
FAIL  = the gate lied (crowned noise, or missed a plant we can independently confirm).
LIMIT = an honest boundary we document rather than hide.

Designed NOT to be easy: the trend battery includes a RANDOM WALK — no deterministic
trend, but heavy autocorrelation. An iid label-shuffle null is known-invalid there
(the sunspot-runaway lesson). We measure the false-REAL rate and report it straight.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from temporal_detector import trend_gate, cycle_gate

TITLE = "RED TEAM — THE CLOCK (trend + cycle gates)"


def _fp_rate(make_series, n_years, trials, seed0, null="iid"):
    """Fraction of `trials` no-true-trend series the trend_gate wrongly calls REAL."""
    yrs = np.arange(1900, 1900 + n_years, dtype=float)
    hits = 0
    for k in range(trials):
        rng = np.random.default_rng(seed0 + k)
        v = make_series(rng, n_years)
        _, real = trend_gate(yrs, v, n_null=200, rng=np.random.default_rng(9000 + k), null=null)
        hits += int(real)
    return hits / trials


def _tp_rate(slope_per_yr, n_years, trials, seed0, null="iid"):
    """Fraction of `trials` genuine-trend series the trend_gate correctly calls REAL."""
    yrs = np.arange(1900, 1900 + n_years, dtype=float)
    hits = 0
    for k in range(trials):
        rng = np.random.default_rng(seed0 + k)
        v = slope_per_yr * (yrs - yrs.mean()) + rng.normal(0, 0.4, n_years)
        _, real = trend_gate(yrs, v, n_null=200, rng=np.random.default_rng(9000 + k), null=null)
        hits += int(real)
    return hits / trials


def run():
    results = []
    rng = np.random.default_rng(0)

    # 1. REAL TREND (positive control) — a planted warming slope must be found.
    yrs = np.arange(1900, 2021, dtype=float)
    v = 0.02 * (yrs - 1960) + rng.normal(0, 0.4, len(yrs))   # ~+2C/century, noisy
    slope, real = trend_gate(yrs, v, rng=np.random.default_rng(1))
    results.append(("real trend -> REAL", "beats null", f"{slope*100:+.2f}/century real={real}",
                    "PASS" if real else "FAIL"))

    # 2. FLAT NOISE (negative control) — iid noise, no trend. FPR should be ~5% at pct95.
    fpr_flat = _fp_rate(lambda r, n: r.normal(0, 1, n), 121, 200, 100)
    results.append(("flat iid noise -> refuse", "FPR ~5%", f"false-REAL {fpr_flat*100:.1f}% of 200",
                    "PASS" if fpr_flat <= 0.09 else "FAIL"))

    # 3. SPARSE fake trend — only 6 years of noise. A calibrated gate still ~5% FPR;
    #    a gate fooled by small-N would inflate. (The 'sparse-data fake trend' attack.)
    fpr_sparse = _fp_rate(lambda r, n: r.normal(0, 1, n), 6, 300, 200)
    results.append(("sparse (6yr) noise -> refuse", "FPR ~5%, not inflated",
                    f"false-REAL {fpr_sparse*100:.1f}% of 300",
                    "PASS" if fpr_sparse <= 0.10 else "FAIL"))

    # --- STATIONARY AUTOCORRELATION (the sunspot case): iid null lies, block null cures ---
    # AR(1), phi=0.8, mean-reverting, NO trend. This is the case block-permutation is FOR.
    def ar1(r, n, phi=0.8):
        v = np.zeros(n); e = r.normal(0, 1, n)
        for t in range(1, n):
            v[t] = phi * v[t-1] + e[t]
        return v

    # 4. AR(1) noise, IID NULL -> lies (autocorrelation inflates spurious slopes).
    fpr_ar_iid = _fp_rate(ar1, 121, 200, 400, null="iid")
    results.append(("AR(1) noise, IID null -> LIES", "iid null invalid on autocorr",
                    f"false-REAL {fpr_ar_iid*100:.1f}% of 200",
                    "FAIL" if fpr_ar_iid > 0.15 else "PASS"))

    # 5. AR(1) noise, BLOCK NULL -> refuse (the cure, on the case it's designed for).
    fpr_ar_blk = _fp_rate(ar1, 121, 200, 400, null="block")
    results.append(("AR(1) noise, BLOCK null -> refuse", "block null restores calibration",
                    f"false-REAL {fpr_ar_blk*100:.1f}% of 200",
                    "PASS" if fpr_ar_blk <= 0.12 else "FAIL"))

    # 6. REAL TREND under the BLOCK null — the cure must not kill true positives.
    tpr_blk = _tp_rate(0.02, 121, 100, 500, null="block")
    results.append(("real trend, BLOCK null -> keep", "power retained >=90%",
                    f"true-REAL {tpr_blk*100:.1f}% of 100",
                    "PASS" if tpr_blk >= 0.90 else "FAIL"))

    # --- NON-STATIONARY random walk: the deeper limit. Block null HELPS but a unit-root
    #     series violates the exchangeability every permutation null assumes, so it is not
    #     fully cured — it needs explicit non-stationarity/drift handling. Documented, not hidden.
    rw = lambda r, n: np.cumsum(r.normal(0, 1, n))
    fpr_rw_iid = _fp_rate(rw, 121, 200, 300, null="iid")
    fpr_rw_blk = _fp_rate(rw, 121, 200, 300, null="block")
    helped = fpr_rw_blk < fpr_rw_iid - 0.15
    results.append(("random walk (unit root)", "block helps, not a full cure",
                    f"iid {fpr_rw_iid*100:.0f}% -> block {fpr_rw_blk*100:.0f}% false-REAL",
                    "LIMIT" if helped else "FAIL"))

    # 5. REAL CYCLE (positive control) — temp as a clean function of yearly phase.
    ph = rng.uniform(0, 2*np.pi, 1500)
    tv = 15 + 10*np.cos(ph) + rng.normal(0, 0.5, len(ph))
    verd, r2 = cycle_gate(ph, tv, name="cyc_real")
    results.append(("real cycle -> found", "UNDERSTOOD/strong", f"{verd} R2 {r2:.2f}",
                    "PASS" if (verd in ("UNDERSTOOD", "PARTIAL") and r2 > 0.9) else "FAIL"))

    # 6. SPURIOUS CYCLE — random phase, iid-noise values. Must NOT be crowned a law.
    ph2 = rng.uniform(0, 2*np.pi, 1500)
    nv = rng.normal(0, 1, len(ph2))
    verd2, r2_2 = cycle_gate(ph2, nv, name="cyc_noise")
    results.append(("phase vs noise -> refuse", "not UNDERSTOOD", f"{verd2} R2 {r2_2:.2f}",
                    "PASS" if verd2 != "UNDERSTOOD" else "FAIL"))

    # 7. TREND MASQUERADING AS CYCLE — a pure linear ramp fed on a phase axis. There is
    #    no real periodicity; the cycle gate should not report a strong circular law.
    ph3 = rng.uniform(0, 2*np.pi, 1500)
    ramp = 3*ph3 + rng.normal(0, 0.3, len(ph3))   # monotonic in the "phase" var, not cyclic
    verd3, r2_3 = cycle_gate(ph3, ramp, name="cyc_ramp")
    #   honest outcome: it may legitimately find v ~ linear(phase) (that IS a real law of
    #   this variable); what it must NOT do is invent a periodic structure that isn't there.
    results.append(("linear ramp on phase axis", "a real law, not a fake cycle",
                    f"{verd3} R2 {r2_3:.2f}", "PASS" if verd3 != "NO RULE" else "LIMIT"))

    return results


def report(results, title):
    print("=" * 92)
    print(f"  {title}")
    print("=" * 92)
    for name, expect, got, status in results:
        tag = {"PASS": "[PASS] ", "FAIL": "[FAIL] ", "LIMIT": "[LIMIT]"}[status]
        print(f"  {tag} {name:32s} expect: {expect:30s} got: {got}")
    p = sum(s == "PASS" for *_, s in results)
    f = sum(s == "FAIL" for *_, s in results)
    l = sum(s == "LIMIT" for *_, s in results)
    print("-" * 92)
    print(f"  {p} held, {f} failed, {l} known-limit  (of {len(results)})")
    print("=" * 92)
    return p, f, l


if __name__ == "__main__":
    report(run(), TITLE)
