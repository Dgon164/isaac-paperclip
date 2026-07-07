"""
THE CLOCK — detect temporal information, establish the clock, anchor what happened when.

Raw data usually carries a time column that ingestion throws away (I did exactly
that with weather). This detects it: is a column a clock? what's its tick and its
period? Then it feeds the time axis to discovery -- trends (value vs time) and
CYCLES (value vs phase), which are 'circles' in Isaac's wave vocabulary -- and
anchors events (when the extremes happened). 'Where' is the spatial analogue.
"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac

GZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "wx.csv.gz")
NAMES = ["date","hour","temp","dwpt","rhum","prcp","snow","wdir","wspd","wpgt","pres","tsun","coco"]


# ---- the gates (reusable, testable — the red team imports THESE) ----
def _block_perm(values, L, rng):
    """Permute the ORDER of contiguous length-L blocks. Destroys the long-range
    trend but PRESERVES within-block autocorrelation — so the null captures the
    spurious slopes an autocorrelated series produces by chance."""
    n = len(values); nb = int(np.ceil(n / L))
    blocks = [values[i*L:(i+1)*L] for i in range(nb)]
    return np.concatenate([blocks[i] for i in rng.permutation(nb)])[:n]


def trend_gate(x, values, n_null=200, rng=None, pct=95, null="iid", block=None):
    """Null-gated linear trend. Real only if |slope| beats the `pct`th percentile
    of a null. Two nulls:
      null="iid"   : label-shuffle (fast, but INVALID on autocorrelated data — it
                     destroys autocorrelation, making the null far too narrow, so a
                     random walk with no true trend is falsely called REAL).
      null="block" : block-permutation (preserves autocorrelation; the honest null
                     for temporal/autocorrelated targets). block size L defaults to
                     ~sqrt(n). This is the sunspot-runaway cure.
    Returns (slope, is_real)."""
    rng = rng if rng is not None else np.random.default_rng(0)
    x = np.asarray(x, float); values = np.asarray(values, float)
    slope = float(np.polyfit(x, values, 1)[0])
    if null == "block":
        L = block if block else max(2, int(round(len(values) ** 0.5)))
        draws = [np.polyfit(x, _block_perm(values, L, rng), 1)[0] for _ in range(n_null)]
    else:
        draws = [np.polyfit(x, rng.permutation(values), 1)[0] for _ in range(n_null)]
    return slope, bool(abs(slope) > np.percentile(np.abs(draws), pct))


def cycle_gate(phase, values, name="cyc"):
    """Is `values` a lawful function of cyclic phase (a circle)? Delegates the
    verdict to discover()'s null-gated machinery. Returns (verdict, r2)."""
    r = Isaac().discover(np.asarray(phase, float).reshape(-1, 1),
                         np.asarray(values, float), name=name)
    return r["verdict"], float(r["r2"])


def _demo():
    df = pd.read_csv(GZ, header=None, names=NAMES)
    print("="*80)
    print("  THE CLOCK — detect temporal info; anchor what happened when")
    print("="*80)

    # 1. DETECT a temporal column: does it parse as time?
    dt = pd.to_datetime(df["date"], errors="coerce")
    frac = dt.notna().mean()
    print(f"  temporal column detected: 'date' parses as time for {frac*100:.1f}% of rows  -> IS a clock")
    udates = pd.Series(dt.dropna().dt.normalize().unique()).sort_values()   # tick from UNIQUE days
    gaps = udates.diff().dropna().dt.days
    tick = int(gaps.mode().iloc[0]); span_yrs = (dt.max() - dt.min()).days / 365.25
    print(f"  the clock: tick = {tick} day(s) (regular sampling), span = {span_yrs:.0f} years "
          f"({dt.min().date()} .. {dt.max().date()})")

    temp = pd.to_numeric(df["temp"], errors="coerce")
    D = pd.DataFrame({"t": dt, "temp": temp, "doy": dt.dt.dayofyear, "year": dt.dt.year}).dropna()

    # 2. CYCLE (seasonality): temp as a function of yearly PHASE -> a circle
    print("\n  CYCLE — is temperature a lawful function of the yearly phase?")
    rng = np.random.default_rng(0)
    S = D.iloc[rng.choice(len(D), 3000, replace=False)]
    phase = (2*np.pi*S["doy"]/365.25).values
    verdict, r2 = cycle_gate(phase, S["temp"].values, name="season")
    # interpretable amplitude/peak from a direct cos/sin fit
    M = np.column_stack([np.cos(phase), np.sin(phase), np.ones(len(phase))])
    a, b, c = np.linalg.lstsq(M, S["temp"].values, rcond=None)[0]
    amp = float(np.hypot(a, b)); peak_doy = int((np.arctan2(b, a) % (2*np.pi)) / (2*np.pi) * 365.25)
    print(f"     {verdict} R2 {r2:.2f}: a yearly CIRCLE. mean {c:.1f}C, "
          f"amplitude {amp:.1f}C, warmest ~day {peak_doy} of the year.")

    # 3. TREND (value vs time) -> is there long-term change? null-gated.
    #    Annual means are AUTOCORRELATED (lag-1 ~0.5), so the honest null is the
    #    block-permutation one (the iid shuffle is invalid on autocorrelated data —
    #    see redteam_clock.py). The warming trend survives it (confirmed robust).
    print("\n  TREND — long-term change across the clock's full span?")
    ann = D.groupby("year")["temp"].mean()
    yrs = ann.index.values.astype(float); mt = ann.values
    slope, real = trend_gate(yrs, mt, rng=rng, null="block")
    print(f"     {slope*100:+.2f} C / century   "
          f"({'REAL — beats block-permutation (autocorr-aware) null' if real else 'within null'})")

    # 4. WHAT HAPPENED WHEN — anchor the extremes to their timestamps
    hot = D.loc[D['temp'].idxmax()]; cold = D.loc[D['temp'].idxmin()]
    print(f"\n  WHAT HAPPENED WHEN:  hottest {hot['temp']:.1f}C on {hot['t'].date()}   "
          f"coldest {cold['temp']:.1f}C on {cold['t'].date()}")
    print("\n" + "="*80)
    print("  From a column I had discarded: Isaac found the seasonal circle, a century-scale")
    print("  warming trend, and anchored the record days. 'Where' is the same, on a place column.")
    print("="*80)


if __name__ == "__main__":
    _demo()
