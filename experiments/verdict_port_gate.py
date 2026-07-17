"""verdict_port_gate.py — S2b PROMOTION GATE: the 100-world verdict
duel (old judge vs ported judge), run through the REAL engine.

USAGE:
  python verdict_port_gate.py baseline   # BEFORE the port: freeze the
                                          # old judge's numbers
  python verdict_port_gate.py ported     # AFTER the port: compare and
                                          # judge the gate

THE DUEL (plan S2b: "100-world verdict duel (wrong-form UNDERSTOOD
rate, old vs new)"): five families x 20 worlds, every world with a
KNOWN truth so wrong-confidence is measured against reality, not
against r2:
  F1 TRUE LAWS (availability must survive): y = x0*x1 + x2^2 - x3
     + N(0, 0.02), n=400, d=5 — the gauntlet-(a) shape.
  F2 ADDITIVE HOLE: y = x0 + x1 exact on integers 1..9, n=60 — the
     campaign's founding exhibit (engine admits the x0*x1 impostor at
     small n and stamps it).
  F3 NEAR-MISS POISON: F2 + 10% +-1 cell corruption.
  F4 BLENDED CONDITIONAL: flag ? x0*x1 : x0+x1, n=48 (the 0.9972
     exhibit).
  F5 MAX RELATION: y = max(x0, x1) exact, continuous, n=252 — the
     pool-branch eval's BROKEN (9-term chaser at r2=0.99945).
  KEPLER EXTRA: n=8, y = a^3 exact (requirement 4: must survive the
     ported judge; the old judge is expected NO RULE).

WRONG-CONFIDENT = verdict UNDERSTOOD while apply_law on FRESH rows
misses the known truth by more than the family tolerance. TOLERANCE
CORRECTION after baseline run 1 (disclosed): exact-law families
(F2-F5) now demand MACHINE agreement (1e-6) — their worlds are exact,
so any true-form fit lands ~1e-12 and anything above 1e-6 is a wrong
form shipped confidently (run 1's loose 0.1/0.5 tolerances let the
max-world 9-term chaser and bent-constant fits pass as 'close
enough'; on an exact world, close-enough IS the disease). F1 keeps
5*sigma = 0.1 (noisy world, coefficient error is honest).
AVAILABILITY = UNDERSTOOD rate on F1.

GATE CHECKS (ported mode only; predictions filed):
  G1 wrong-confident TOTAL: 0 (baseline expected to show the disease
     across F2-F5 at a substantial rate).
  G2 F1 availability >= baseline - 1 (the cure must not starve him).
  G3 Kepler: ported = UNDERSTOOD with certificate machine-exact.
  G4 examiner false-fire on F1 <= 2/20 (legs receipts, ported only).
Each world runs on a FRESH throwaway mind; deterministic seeds;
results JSON under experiments/runs/ for the writeup.

Run: cd experiments && PYTHONHASHSEED=0 python verdict_port_gate.py <mode>
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
os.makedirs(RUNS, exist_ok=True)


def fam_worlds(fam, s):
    rng = np.random.default_rng(10_000 * (fam + 1) + s)
    if fam == 0:   # F1 true law
        X = rng.normal(0, 1, (400, 5))
        y = X[:, 0] * X[:, 1] + X[:, 2] ** 2 - X[:, 3] \
            + rng.normal(0, 0.02, 400)
        truth = lambda Z: Z[:, 0] * Z[:, 1] + Z[:, 2] ** 2 - Z[:, 3]
        fresh = lambda r: r.normal(0, 1, (500, 5))
        return X, y, truth, fresh, 0.1
    if fam == 1:   # F2 additive hole
        X = rng.integers(1, 10, (60, 2)).astype(float)
        y = X[:, 0] + X[:, 1]
        truth = lambda Z: Z[:, 0] + Z[:, 1]
        fresh = lambda r: r.integers(1, 10, (500, 2)).astype(float)
        return X, y, truth, fresh, 1e-6
    if fam == 2:   # F3 near-miss poison
        X = rng.integers(1, 10, (60, 2)).astype(float)
        y = X[:, 0] + X[:, 1]
        bad = rng.choice(60, 6, replace=False)
        y = y.copy(); y[bad] += rng.choice([-1.0, 1.0], 6)
        truth = lambda Z: Z[:, 0] + Z[:, 1]
        fresh = lambda r: r.integers(1, 10, (500, 2)).astype(float)
        return X, y, truth, fresh, 1e-6
    if fam == 3:   # F4 blended conditional
        x01 = rng.integers(1, 10, (48, 2)).astype(float)
        flag = (np.arange(48) % 2).astype(float)
        y = np.where(flag == 0, x01[:, 0] + x01[:, 1],
                     x01[:, 0] * x01[:, 1])
        X = np.column_stack([x01, flag])
        truth = lambda Z: np.where(Z[:, 2] == 0, Z[:, 0] + Z[:, 1],
                                   Z[:, 0] * Z[:, 1])

        def fresh(r):
            a = r.integers(1, 10, (500, 2)).astype(float)
            f = (r.uniform(size=500) < 0.5).astype(float)
            return np.column_stack([a, f])
        return X, y, truth, fresh, 1e-6
    # F5 max relation
    X = rng.uniform(-2, 2, (252, 2))
    y = np.maximum(X[:, 0], X[:, 1])
    truth = lambda Z: np.maximum(Z[:, 0], Z[:, 1])
    fresh = lambda r: r.uniform(-2, 2, (500, 2))
    return X, y, truth, fresh, 1e-6


FAM_NAMES = ["F1 true-law", "F2 additive-hole", "F3 near-miss",
             "F4 blended", "F5 max-relation"]


def run_world(fam, s):
    X, y, truth, fresh, tol = fam_worlds(fam, s)
    mind = Isaac()
    nm = f"gate{fam}_{s}"
    res = mind.discover(X, y, name=nm)
    rec = dict(family=FAM_NAMES[fam], seed=s, verdict=res["verdict"],
               r2=round(float(res["r2"]), 4),
               certificate=res.get("certificate"),
               legs=res.get("legs"))
    wrong = False
    if res["verdict"] == "UNDERSTOOD":
        Zr = np.random.default_rng(99_000 + 100 * fam + s)
        Z = fresh(Zr)
        p = mind.apply_law(nm, Z)
        if p is None:
            wrong = True
        else:
            ok = np.isfinite(p)
            err = float(np.median(np.abs(p[ok] - truth(Z)[ok]))) \
                if ok.any() else np.inf
            wrong = err > tol
            rec["truth_median_err"] = round(err, 4)
    rec["wrong_confident"] = bool(wrong)
    return rec


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    assert mode in ("baseline", "ported")
    t0 = time.perf_counter()
    rows = []
    for fam in range(5):
        tf = time.perf_counter()
        for s in range(20):
            rows.append(run_world(fam, s))
        wc = sum(r["wrong_confident"] for r in rows
                 if r["family"] == FAM_NAMES[fam])
        und = sum(r["verdict"] == "UNDERSTOOD" for r in rows
                  if r["family"] == FAM_NAMES[fam])
        print(f"{FAM_NAMES[fam]:18s} UNDERSTOOD {und:2d}/20  "
              f"wrong-confident {wc:2d}/20  "
              f"({time.perf_counter() - tf:.0f}s)", flush=True)

    # Kepler n=8 extra
    a = np.random.default_rng(11).permutation(
        np.array([0.387, 0.723, 1.0, 1.524, 5.203, 9.537, 19.19, 30.07]))
    mind = Isaac()
    resk = mind.discover(a.reshape(-1, 1), a ** 3, name="kepler")
    kep = dict(verdict=resk["verdict"], r2=round(float(resk["r2"]), 4),
               certificate=resk.get("certificate"))
    print(f"KEPLER n=8         verdict {kep['verdict']} "
          f"(certificate {kep['certificate']})")

    out = dict(mode=mode, rows=rows, kepler=kep,
               total_wrong=sum(r["wrong_confident"] for r in rows),
               f1_avail=sum(r["verdict"] == "UNDERSTOOD" for r in rows
                            if r["family"] == FAM_NAMES[0]),
               secs=round(time.perf_counter() - t0, 1))
    path = os.path.join(RUNS, f"verdict_gate_{mode}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nTOTAL wrong-confident {out['total_wrong']}/100   "
          f"F1 availability {out['f1_avail']}/20   ({out['secs']}s)")
    print(f"saved {path}")

    if mode == "ported":
        with open(os.path.join(RUNS, "verdict_gate_baseline.json")) as f:
            base = json.load(f)
        print("\n==== THE DUEL (old judge vs ported judge) ====")
        for fam in FAM_NAMES:
            bw = sum(r["wrong_confident"] for r in base["rows"]
                     if r["family"] == fam)
            nw = sum(r["wrong_confident"] for r in rows
                     if r["family"] == fam)
            print(f"  {fam:18s} wrong-confident {bw:2d}/20 -> {nw:2d}/20")
        checks = []

        def check(name, ok, detail):
            checks.append(ok)
            print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

        check("G1 wrong-confident 0/100 (baseline "
              f"{base['total_wrong']}/100)", out["total_wrong"] == 0,
              f"{out['total_wrong']}/100")
        check("G2 F1 availability preserved",
              out["f1_avail"] >= base["f1_avail"] - 1,
              f"{out['f1_avail']}/20 vs baseline {base['f1_avail']}/20")
        check("G3 Kepler machine-exact UNDERSTOOD",
              kep["verdict"] == "UNDERSTOOD"
              and kep["certificate"] == "machine-exact",
              f"{kep['verdict']} / {kep['certificate']}")
        f1_fired = sum(1 for r in rows if r["family"] == FAM_NAMES[0]
                       and r.get("legs")
                       and (r["legs"].get("replay", {}).get("state")
                            == "fired"
                            or r["legs"].get("pool", {}).get("state")
                            == "scream"))
        check("G4 examiner false-fire on F1 <= 2/20", f1_fired <= 2,
              f"{f1_fired}/20")
        n = sum(checks)
        print(f"\n  GATE: {n} passed, {len(checks) - n} failed of "
              f"{len(checks)}")


if __name__ == "__main__":
    main()
