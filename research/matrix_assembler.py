"""
THE MATRIX-CREATOR — build the clean matrix discover() needs, from messy data.

discover() needs a clean spreadsheet-style matrix (fine — that's its job). The
critical capability is CREATING that matrix from raw/ragged/missing/mixed data.
This is a holonic chain of granular functions: load -> coerce -> mark-present ->
handle-absent -> assemble. Missing is never globally dropped; it is an ABSENT
dimension, handled per-question two honest ways:
  complete : keep rows present in ONLY the columns this question uses
             (a missing wind value never kills a temperature row).
  pad      : absent becomes its own dimension — impute + a presence flag 'col?',
             so the absence is recorded, never fabricated away.
"""
import sys, os, re, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac

GZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "wx.csv.gz")  # fetch: see real_data_discovery.py header
NAMES = ["date","hour","temp","dwpt","rhum","prcp","snow","wdir","wspd","wpgt","pres","tsun","coco"]
NUM = ["temp","dwpt","rhum","prcp","snow","wdir","wspd","wpgt","pres","tsun"]
CAP = 2000

# ---- the chain (each a granular, reusable holon) ----
def load_raw(gz):      return pd.read_csv(gz, header=None, names=NAMES)
def coerce(df, cols):  return df[cols].apply(pd.to_numeric, errors="coerce")
def assemble(df, target, predictors, mode="complete", rng=None):
    if mode == "complete":
        sub = df[[target] + predictors].dropna()          # present in JUST these cols
        names = list(predictors)
        Xdf, y = sub[predictors], sub[target].values
    elif mode == "pad":
        sub = df[df[target].notna()]                       # keep every row the target has
        cols, names = [], []
        for p in predictors:
            v = sub[p]
            cols.append(v.fillna(v.mean()).values); names.append(p)          # value (imputed)
            cols.append(v.notna().astype(float).values); names.append(p+"?") # ABSENT as a dimension
        Xdf, y = pd.DataFrame(np.column_stack(cols)), sub[target].values
    n = len(y)
    if n > CAP:                                            # subsample for speed
        idx = (rng or np.random.default_rng(0)).choice(n, CAP, replace=False)
        Xdf, y = Xdf.iloc[idx] if hasattr(Xdf, "iloc") else Xdf[idx], y[idx]; n = CAP
    return np.asarray(Xdf, float), np.asarray(y, float), names, len(sub)

def ask(df, target, predictors, mode="complete"):
    X, y, names, n_avail = assemble(df, target, predictors, mode)
    if len(y) < 50: return f"{target} <- {predictors} [{mode}]: too few rows ({len(y)})"
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-9); ys = (y - y.mean()) / (y.std() + 1e-9)
    r = Isaac().discover(Xs, ys, name=target)
    eq = re.sub(r"x(\d+)", lambda m: names[int(m.group(1))] if int(m.group(1)) < len(names) else m.group(0), r["equation"])
    return (f"{target} <- {predictors} [{mode}]  rows used {len(y)} (of {n_avail:,} present)\n"
            f"      -> {r['verdict']} R2 {r['r2']:.2f}   {target} = {eq[:74]}")

if __name__ == "__main__":
    df = coerce(load_raw(GZ), NUM)
    print("="*84)
    print("  MATRIX-CREATOR — assemble discover-ready matrices from RAW data (no global drop)")
    print("="*84)
    print("  per-column presence (how ragged the raw is):")
    for c in NUM: print(f"     {c:5s}: {int(df[c].notna().sum()):>8,} of {len(df):,} present")

    print("\n  ASK questions; the assembler builds each matrix per-question:\n")
    print("  " + ask(df, "dwpt", ["temp", "rhum"], "complete"))            # dense -> the law
    print("\n  " + ask(df, "prcp", ["temp", "rhum", "pres"], "complete"))  # SPARSE column, now askable
    print("\n  " + ask(df, "dwpt", ["temp", "rhum", "wpgt", "prcp"], "pad"))  # absent-as-dimension
    print("\n" + "="*84)
    print("  Global .dropna() across all columns would have kept ~0 rows (prcp/snow/wpgt/tsun")
    print("  are mostly absent). Per-question assembly keeps what each question actually needs.")
    print("="*84)
