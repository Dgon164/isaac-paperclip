"""
RAW REAL-WORLD DATA -> unsupervised uncovering.

No labels, no designated target. Isaac asks, of each column: 'is this a LAWFUL
function of the others, or an independent degree of freedom?' -- held-out + null
gated, so a coincidence can't pass.

Demonstrated on raw hourly weather (Frankfurt station, meteostat, since 1926):
  UNCOVERED lawful: dew point <-> temperature <-> humidity  (all three directions,
    R2=1.00) -- the real thermodynamic trio.
  REFUSED (NO RULE): wind, pressure -- genuinely freer, not fabricated.
Known physics = the right first result: proves it finds REAL structure on REAL
data, correctly and honestly, before trusting it where the answer is unknown.

DATA (not committed; ~7MB): fetch any station's raw hourly file, e.g.
  Invoke-WebRequest https://bulk.meteostat.net/v2/hourly/10637.csv.gz -OutFile research/data/wx.csv.gz
Then run with the repo venv. Works on any raw numeric CSV -- point USE at its columns.
"""
import sys, os, re, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from isaac import Isaac

GZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "wx.csv.gz")
NAMES = ["date","hour","temp","dwpt","rhum","prcp","snow","wdir","wspd","wpgt","pres","tsun","coco"]
USE = ["temp", "dwpt", "rhum", "wspd", "pres"]

if not os.path.exists(GZ):
    sys.exit(f"data not found at {GZ}\n  fetch it (see this file's header) then re-run.")

df = pd.read_csv(GZ, header=None, names=NAMES)[USE].apply(pd.to_numeric, errors="coerce").dropna()
print(f"  raw complete rows: {len(df):,}   columns: {USE}")
rng = np.random.default_rng(0)
D = df.iloc[rng.choice(len(df), size=min(2000, len(df)), replace=False)].reset_index(drop=True)
Z = (D - D.mean()) / D.std()
X = Z.values

def humanize(eq, others):
    return re.sub(r"x(\d+)", lambda m: others[int(m.group(1))] if int(m.group(1)) < len(others) else m.group(0), eq)

results = []
for j, col in enumerate(USE):
    others = [USE[k] for k in range(len(USE)) if k != j]
    Xo = X[:, [k for k in range(len(USE)) if k != j]]; y = X[:, j]
    r = Isaac().discover(Xo, y, name=col)
    yn = y.copy(); rng.shuffle(yn)
    rn = Isaac().discover(Xo, yn, name=col + "_null")
    null_r2 = rn["r2"] if rn["verdict"] in ("UNDERSTOOD", "PARTIAL") else -9.0
    real_r2 = r["r2"] if r["verdict"] in ("UNDERSTOOD", "PARTIAL") else -9.0
    results.append((col, others, r, real_r2, null_r2, real_r2 >= 0.85 and real_r2 - null_r2 >= 0.3))

results.sort(key=lambda t: t[3], reverse=True)
print("\n  UNCOVERED — lawful (a measurement determined by the others):")
for col, others, r, real_r2, null_r2, lawful in results:
    if lawful:
        print(f"   {col}: LAWFUL (held-out R2 {real_r2:.2f} vs null {null_r2:+.2f})  {col} = {humanize(r['equation'], others)[:80]}")
print("\n  INDEPENDENT — freer degrees of freedom:")
for col, others, r, real_r2, null_r2, lawful in results:
    if not lawful:
        print(f"   {col:5s}  R2 {real_r2:+.2f} ({r['verdict']}) — not a clean function of the others")
