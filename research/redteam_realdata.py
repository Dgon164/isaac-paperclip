"""
RED TEAM — REAL DATA.  Run the clock's honesty gates on real datasets whose answers
are already known from published science, and check the gate tells the truth.

Unlike the synthetic batteries (which isolate a mechanism), this grades the gates on
real-world mess against ground truth we didn't make up:

  MAUNA LOA CO2 (NOAA GML, 1958-)   the textbook trend+cycle+fluctuation signal.
    known: a strong REAL rising trend (~1.5-2.5 ppm/yr); a clean ANNUAL cycle
    (~6 ppm peak-to-trough, peak in spring); a STICKY residual (memory in the leftover).
  SUNSPOTS (SILSO monthly, 1749-)   the dataset that caused the runaway.
    known: a real ~11-year cycle; NO real linear trend. The honesty trap — the naive
    (iid) null is fooled by the cycle's autocorrelation and calls a trend REAL; the
    honest (block) null must REFUSE it.

Data (gitignored): fetch once with
  co2:      https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv
  sunspots: https://www.sidc.be/SILSO/DATA/SN_m_tot_V2.0.csv
"""
import sys, os, numpy as np, pandas as pd
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE); sys.path.insert(0, os.path.join(_HERE, ".."))
from temporal_detector import trend_gate, cycle_gate

TITLE = "RED TEAM — REAL DATA (clock gates vs known science)"
DATA = os.path.join(_HERE, "data")


def _load_co2():
    df = pd.read_csv(os.path.join(DATA, "co2_mlo.csv"), comment="#", header=None,
                     names=["year", "month", "decimal", "average", "deseason",
                            "ndays", "sdev", "unc"])
    for c in ("year", "month", "average"):
        df[c] = pd.to_numeric(df[c], errors="coerce")   # drops the stray header row
    df = df.dropna(subset=["average"])
    df = df[df["average"] > 0].reset_index(drop=True)
    return df


def _load_sunspots():
    df = pd.read_csv(os.path.join(DATA, "sunspots_monthly.csv"), sep=";", header=None,
                     names=["year", "month", "decimal", "sn", "sd", "nobs", "flag"])
    df = df[df["sn"] >= 0].reset_index(drop=True)
    return df


def run():
    results = []

    # ============================ MAUNA LOA CO2 ============================
    co2 = _load_co2()
    ann = co2.groupby("year")["average"].mean()
    yrs = ann.index.values.astype(float); vv = ann.values

    # 1. TREND — known REAL and rising. Must beat the honest (block) null and be ~1.5-2.5 ppm/yr.
    slope, real = trend_gate(yrs, vv, rng=np.random.default_rng(0), null="block")
    ok = real and 1.0 < slope < 3.0
    results.append(("CO2 trend -> REAL rising", "REAL, ~1.5-2.5 ppm/yr",
                    f"{slope:+.2f} ppm/yr real={real}", "PASS" if ok else "FAIL"))

    # 2. CYCLE — known ANNUAL (~6 ppm peak-to-trough, spring peak). Detrend with a 12-mo
    #    centered moving average (self-contained), then test value vs month-phase.
    trend_ma = co2["average"].rolling(12, center=True).mean()
    seas = (co2["average"] - trend_ma)
    m = seas.notna()
    phase = (2 * np.pi * (co2["month"].values - 0.5) / 12.0)[m.values]
    sv = seas[m].values
    verd, r2 = cycle_gate(phase, sv, name="co2cyc")
    a = np.column_stack([np.cos(phase), np.sin(phase), np.ones(len(phase))])
    ca, cb, _ = np.linalg.lstsq(a, sv, rcond=None)[0]
    amp = float(np.hypot(ca, cb)); peak_m = (np.arctan2(cb, ca) % (2*np.pi)) / (2*np.pi) * 12
    cyc_ok = verd in ("UNDERSTOOD", "PARTIAL") and 2.0 < amp < 4.5 and 3 <= peak_m <= 6
    results.append(("CO2 cycle -> annual found", "~3 ppm amp, spring peak",
                    f"{verd} amp={amp:.1f}ppm peak~month {peak_m:.1f}", "PASS" if cyc_ok else "FAIL"))

    # 3. FLUCTUATION MEMORY — the layer that was missed. Remove trend AND the monthly
    #    climatology; the leftover should be STICKY (positive lag-1 autocorrelation).
    clim = seas.groupby(co2["month"]).transform("mean")
    resid = (seas - clim)[m].values
    ac1 = float(np.corrcoef(resid[:-1], resid[1:])[0, 1])
    results.append(("CO2 fluctuation is sticky", "residual has memory (ac1>0.2)",
                    f"lag-1 autocorr = {ac1:+.2f}", "PASS" if ac1 > 0.2 else "FAIL"))

    # ============================ SUNSPOTS ============================
    sn = _load_sunspots()
    sann = sn.groupby("year")["sn"].mean()
    syr = sann.index.values.astype(float); sv2 = sann.values

    # 4. THE TRAP — a linear trend. Known: NONE. The iid null is fooled by the 11-yr cycle's
    #    autocorrelation; the honest block null must refuse. PASS = block refuses.
    _, real_iid = trend_gate(syr, sv2, n_null=2000, rng=np.random.default_rng(1), null="iid")
    slope_s, real_blk = trend_gate(syr, sv2, n_null=2000, rng=np.random.default_rng(1), null="block")
    trap_ok = (not real_blk)
    results.append(("sunspots trend -> REFUSE", "no real linear trend",
                    f"iid says real={real_iid}  ->  block says real={real_blk}",
                    "PASS" if trap_ok else "FAIL"))

    # 5. THE CYCLE — known ~11 yr. Characterize the dominant period (spectral peak) and
    #    confirm it lands in 9-13 yr. (Period-FINDING is a characterization step; the
    #    engine gate above is the honesty test.)
    x = sv2 - sv2.mean()
    freqs = np.fft.rfftfreq(len(x), d=1.0)          # cycles per YEAR (annual sampling)
    power = np.abs(np.fft.rfft(x)) ** 2
    power[0] = 0.0
    peak = freqs[np.argmax(power)]
    period = (1.0 / peak) if peak > 0 else np.inf
    results.append(("sunspots cycle ~11 yr", "dominant period 9-13 yr",
                    f"dominant period = {period:.1f} yr", "PASS" if 9 <= period <= 13 else "FAIL"))

    return results


def report(results, title):
    print("=" * 100)
    print(f"  {title}")
    print("=" * 100)
    for name, expect, got, status in results:
        tag = {"PASS": "[PASS] ", "FAIL": "[FAIL] ", "LIMIT": "[LIMIT]"}[status]
        print(f"  {tag} {name:30s} expect: {expect:28s} got: {got}")
    p = sum(s == "PASS" for *_, s in results)
    f = sum(s == "FAIL" for *_, s in results)
    l = sum(s == "LIMIT" for *_, s in results)
    print("-" * 100)
    print(f"  {p} held, {f} failed, {l} known-limit  (of {len(results)})")
    print("=" * 100)
    return p, f, l


if __name__ == "__main__":
    report(run(), TITLE)
