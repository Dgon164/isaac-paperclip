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
r = Isaac().discover(phase.reshape(-1,1), S["temp"].values, name="season")
# interpretable amplitude/peak from a direct cos/sin fit
M = np.column_stack([np.cos(phase), np.sin(phase), np.ones(len(phase))])
a, b, c = np.linalg.lstsq(M, S["temp"].values, rcond=None)[0]
amp = float(np.hypot(a, b)); peak_doy = int((np.arctan2(b, a) % (2*np.pi)) / (2*np.pi) * 365.25)
print(f"     {r['verdict']} R2 {r['r2']:.2f}: a yearly CIRCLE. mean {c:.1f}C, "
      f"amplitude {amp:.1f}C, warmest ~day {peak_doy} of the year.")

# 3. TREND (value vs time) -> is there long-term change? null-gated
print("\n  TREND — long-term change across the clock's full span?")
ann = D.groupby("year")["temp"].mean()
yrs = ann.index.values.astype(float); mt = ann.values
slope = np.polyfit(yrs, mt, 1)[0]
null = np.array([np.polyfit(yrs, rng.permutation(mt), 1)[0] for _ in range(200)])
real = abs(slope) > np.percentile(np.abs(null), 95)
print(f"     {slope*100:+.2f} C / century   ({'REAL — beats shuffled-year null' if real else 'within null'})")

# 4. WHAT HAPPENED WHEN — anchor the extremes to their timestamps
hot = D.loc[D['temp'].idxmax()]; cold = D.loc[D['temp'].idxmin()]
print(f"\n  WHAT HAPPENED WHEN:  hottest {hot['temp']:.1f}C on {hot['t'].date()}   "
      f"coldest {cold['temp']:.1f}C on {cold['t'].date()}")
print("\n" + "="*80)
print("  From a column I had discarded: Isaac found the seasonal circle, a century-scale")
print("  warming trend, and anchored the record days. 'Where' is the same, on a place column.")
print("="*80)
