"""outlier_source_battery.py — PROMOTION #13 BATTERY: THE OUTLIER'S
OWN LAW (owner, 2026-07-15 night: "is it able to isolate and quantify
the outlier componants? like if the outlier is a plus something else,
can it quantify that something else to create a correlation pattern
and identify the model of the source?").

WRITTEN BEFORE THE SURGERY (batteries-before-mechanisms law).

THE ROAD UNDER TEST (discover()'s new pass): when a law stands but
the certificate is not machine-exact, deviations d = y - law(x) are
examined; rows beyond 5*MAD-from-median are ISOLATED (robust to the
bend the poison itself causes) and QUANTIFIED in units. Then the
three-way verdict:
  MIS-ENTRY — the y-grain exists and >=80% of flagged deviations are
    exact grain multiples AND the clean majority re-certifies
    (exact road / within-floor on clean rows only): the law is
    SUPERSEDED by its clean refit, the cells quarantined WITH their
    deviations (receipts; interpreted, never banked).
  SECOND SOURCE (NEWS) — enough flagged rows (>=24) and a throwaway
    discover() on (X_flagged, d) mints a law past its own examiners,
    while the SCRAMBLED-deviation control mints nothing: the source
    model is recorded on the law node (news, not error).
  NEITHER — deviations kept in the dossier; verdict unchanged.
ONE ROUND ONLY (no flag->model->flag loops — the sheet's attack list).

PREDICTIONS (filed before the engine is touched; wrong ones kept)
  O1 F3-CLASS CURE x5 (y=x0+x1 exact integers n=60, 10% cells +-1):
     UNDERSTOOD with the TRUE constants (fresh-truth median err
     <1e-6), poisoned cells quarantined as mis-entry; wrong-confident
     0/5. (The port-gate's last leak class, closed by the owner's
     road rather than by refusing.)
  O2 SECOND SOURCE: y = 2*x0 + N(0,0.02), n=240, and 20% of rows
     additionally receive +0.5*x1 (a real second process on an
     observed channel): the pass isolates those rows, discover() ON
     THE DEVIATIONS mints ~+0.50*x1, recorded as source model (NEWS);
     the primary law's constant recovers ~2.00.
  O3 SCRAMBLED CONTROL: same world as O2 with deviations shuffled
     across flagged rows -> NO source law minted (the mint must die
     on the scrambled-pairing move).
  O4 CLEAN WORLDS UNHARMED x5 (F1-shape n=400 d=5): verdicts and
     certificates unchanged by the pass (a 5*MAD tail on Gaussian
     noise flags ~0.7% of rows; with no grain road and <24 flags the
     pass leaves only a receipt); availability 5/5.
  O5 the pass runs ONE round (receipt says so) and never flags more
     than 35% of rows (a 'law' that calls a third of the data outlier
     is the wrong law, not bad data — refuse the pass).

Run: cd experiments && PYTHONHASHSEED=0 python outlier_source_battery.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    # O1 — the F3-class cure
    print("O1. poisoned integer sums x5: isolate, quarantine, clean-refit")
    cured = wrongc = 0
    for s in range(5):
        rng = np.random.default_rng(30_000 + s)
        X = rng.integers(1, 10, (60, 2)).astype(float)
        y = X[:, 0] + X[:, 1]
        bad = rng.choice(60, 6, replace=False)
        y = y.copy(); y[bad] += rng.choice([-1.0, 1.0], 6)
        mind = Isaac()
        res = mind.discover(X, y, name=f"o1_{s}")
        Z = np.random.default_rng(77_000 + s).integers(
            1, 10, (300, 2)).astype(float)
        p = mind.apply_law(f"o1_{s}", Z)
        err = float(np.median(np.abs(p - (Z[:, 0] + Z[:, 1])))) \
            if p is not None else np.inf
        oq = res.get("outliers") or {}
        okw = (res["verdict"] == "UNDERSTOOD" and err < 1e-6
               and oq.get("kind") == "mis-entry")
        cured += okw
        wrongc += (res["verdict"] == "UNDERSTOOD" and err > 1e-6)
        if s == 0:
            print(f"       seed 0: {res['verdict']} err {err:.2e} "
                  f"outliers: {oq.get('kind')} n={oq.get('n_flagged')} "
                  f"({str(oq.get('why'))[:60]})")
    check("O1 cured with true constants + quarantine >=4/5",
          cured >= 4 and wrongc == 0,
          f"cured {cured}/5, wrong-confident {wrongc}/5")

    # O2 — a real second source
    print("O2. second source: y = 2*x0 (+noise), 20% of rows += 0.5*x1")
    rng = np.random.default_rng(41_000)
    X = np.column_stack([rng.uniform(-2, 2, 240), rng.uniform(1, 5, 240)])
    y = 2.0 * X[:, 0] + rng.normal(0, 0.02, 240)
    hit_rows = rng.choice(240, 48, replace=False)
    y[hit_rows] += 0.5 * X[hit_rows, 1]
    res = Isaac().discover(X, y, name="o2", told_sigma=0.02)
    oq = res.get("outliers") or {}
    src = oq.get("source_equation", "")
    print(f"       verdict {res['verdict']}; outliers kind={oq.get('kind')} "
          f"n={oq.get('n_flagged')}; source eq: {src}")
    got_src = oq.get("kind") == "second-source" and "x1" in str(src)
    check("O2 source model minted from the deviations (NEWS)", got_src,
          f"kind {oq.get('kind')}; eq {src}")

    # O3 — scrambled control (build manually: flag the same rows, shuffle d)
    print("O3. scrambled control: shuffled deviations must mint nothing")
    y3 = 2.0 * X[:, 0] + rng.normal(0, 0.02, 240)
    dev = np.zeros(240)
    dev[hit_rows] = 0.5 * X[hit_rows, 1]
    y3 += np.random.default_rng(5).permutation(dev)   # structure broken
    res3 = Isaac().discover(X, y3, name="o3", told_sigma=0.02)
    oq3 = res3.get("outliers") or {}
    check("O3 no source law on scrambled deviations",
          oq3.get("kind") != "second-source",
          f"kind {oq3.get('kind')} (n_flagged {oq3.get('n_flagged')})")

    # O4 — clean worlds unharmed
    print("O4. clean true-law worlds x5 (n=400, d=5): pass must not meddle")
    und = meddled = 0
    for s in range(5):
        rng = np.random.default_rng(900 + s)
        X4 = rng.normal(0, 1, (400, 5))
        y4 = X4[:, 0] * X4[:, 1] + X4[:, 2] ** 2 - X4[:, 3] \
            + rng.normal(0, 0.02, 400)
        res4 = Isaac().discover(X4, y4, name=f"o4_{s}")
        und += res4["verdict"] == "UNDERSTOOD"
        oq4 = res4.get("outliers") or {}
        meddled += oq4.get("kind") in ("mis-entry", "second-source")
    check("O4 availability 5/5, no false cures", und == 5 and meddled == 0,
          f"UNDERSTOOD {und}/5; false cures {meddled}/5")

    # O5 — receipts: one round, bounded flags
    oq = res.get("outliers") or {}
    check("O5 receipts: one round, flags bounded",
          oq.get("rounds") == 1 and (oq.get("n_flagged") or 0) <= 84,
          f"rounds {oq.get('rounds')}, flagged {oq.get('n_flagged')}/240")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed of "
          f"{len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
