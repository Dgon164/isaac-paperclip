"""Honest-report battery — the user journey, proven.

H1 a real law in a CSV with named columns -> UNDERSTOOD, the equation
   speaks the USER'S column names, complete numbers present
H2 calibrated confidence rides along
H3 pure noise -> a REFUSAL report (NO RULE) with a next step —
   never a fake equation
H4 provenance appendix: rows/cols/hash/date (hash stable across runs)
H5 target selection by name works; the renderer produces a readable
   text report leading with the verdict
Run: python test_report.py   (from isaac_store/)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.report import challenge, render_text

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def make_csv(rng, law=True, n=400):
    a = rng.uniform(-2, 2, n)
    b = rng.uniform(-2, 2, n)
    y = 3.0 * a * b + a ** 2 if law else rng.normal(0, 1, n)
    lines = ["alpha,beta,energy"]
    lines += [f"{a[i]:.6f},{b[i]:.6f},{y[i]:.6f}" for i in range(n)]
    return "\n".join(lines)


def main():
    print("  loading engine...")
    mod = bridge.load_isaac_module()
    rng = np.random.default_rng(41)

    print("H1. a real law, in the user's own words")
    csv_law = make_csv(rng, law=True)
    rep = challenge(csv_law, mod=mod)
    check("verdict UNDERSTOOD", rep["verdict"] == "UNDERSTOOD")
    check("equation speaks the column names",
          "alpha" in rep.get("equation", "") and
          "beta" in rep.get("equation", "") and
          rep["equation"].startswith("energy ="),
          rep.get("equation", "")[:70])
    check("complete numbers: r2 + rows",
          rep["fit"]["r2"] > 0.99 and rep["rows"] == 400)

    print("H2. calibrated confidence rides along")
    check("confidence present with its calibration note",
          rep.get("confidence", {}).get("mean", 0) > 0.7
          and "calibrated" in rep["confidence"]["note"])

    print("H3. noise gets a refusal report, never a fake equation")
    rep_n = challenge(make_csv(rng, law=False), mod=mod)
    check("NO RULE verdict on noise", rep_n["verdict"] == "NO RULE")
    check("a next step is offered even in refusal",
          len(rep_n["next_experiment"]) > 10)

    print("H4. provenance appendix")
    rep2 = challenge(csv_law, mod=mod)
    check("rows/cols/hash/date present",
          rep["provenance"]["rows"] == 400
          and rep["provenance"]["cols"] == 3
          and len(rep["provenance"]["data_sha"]) == 16)
    check("hash stable for identical data",
          rep2["provenance"]["data_sha"] == rep["provenance"]["data_sha"])

    print("H5. target by name + the readable render")
    rep3 = challenge(csv_law, target="energy", mod=mod)
    check("explicit target matches default (last column)",
          rep3["verdict"] == "UNDERSTOOD" and rep3["target"] == "energy")
    txt = render_text(rep)
    check("report leads with the verdict",
          txt.splitlines()[2].startswith("VERDICT: UNDERSTOOD"))
    check("render carries equation, confidence, next, provenance",
          all(s in txt for s in ("energy =", "confidence", "NEXT:",
                                 "provenance")))
    print()
    print(txt)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
