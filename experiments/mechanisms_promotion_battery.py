"""mechanisms_promotion_battery.py — PROMOTION #12 BATTERY: the
comparison words enter the ENGINE vocabulary (crease |xi-xj| atoms,
switch [xi>t] atoms with data-proposed thresholds, deep exact road on
small data) and the mechanism tools (compare/larger/smaller/switch)
register as engine organs. Research basis: basic_mechanisms_probe.py
(12/12) — this battery gates the ENGINE port of that result.

WRITTEN BEFORE THE SURGERY (batteries-before-mechanisms law).

PREDICTIONS (filed before the engine is touched; wrong ones kept)
  B1 MAX WORLD x3 seeds (y=max(x0,x1) exact, n=252): UNDERSTOOD with
     certificate machine-exact — the crease atom makes max a word and
     the exact road spells it ((a+b+|a-b|)/2, coefficients 0.5).
     This is the F5 leak-class cure: vocabulary, not guards.
  B2 STEP WORLD (y = 2*x0 + 1.5*[1<x1<2] + 0.05 noise, 0.01 grain,
     sigma TOLD, n=400): UNDERSTOOD with two step terms at thresholds
     1 and 2 and certificate within-floor. (The wordless port left
     this PARTIAL.)
  B3 BLENDED WORLD (flag ? x0*x1 : x0+x1, exact) at n=48 and n=96:
     UNDERSTOOD machine-exact via the DEEP exact road (k<=5 escalation
     on small data; the 5-term form: x0 + x1 - f*x0 - f*x1 + f*x0*x1).
  B4 NOISE x10 (n=200, d=3 incl. binary flag) with the enriched
     vocabulary: false UNDERSTOOD 0/10 — the selection-corrected
     admission null and held-out examiners must absorb the bigger
     pool, measured not assumed.
  B5 TRUE-LAW x5 (gauntlet-(a) shape, n=400, d=5): UNDERSTOOD 5/5
     preserved with the ~80 extra step atoms in the vocabulary;
     per-call cost reported (complete numbers, no silent caps).
  B6 TOOLS: catalog_tools() lists compare/larger/smaller/switch;
     larger(3,-1) routes THROUGH compare with a receipt chain and
     returns 3 (the owner's a-b<0 wiring, now an organ).
  B7 KEPLER n=8 regression: still UNDERSTOOD machine-exact (the
     vocabulary growth must not disturb requirement 4).

Run: cd experiments && PYTHONHASHSEED=0 python mechanisms_promotion_battery.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac


def q(y, g):
    return np.round(y / g) * g


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    # B1 — the max world x3 (the F5 cure)
    print("B1. max world x3: y = max(x0,x1) exact, n=252")
    hit = 0
    eq0 = ""
    for s in range(3):
        rng = np.random.default_rng(50_000 + s)
        X = rng.uniform(-2, 2, (252, 2))
        y = np.maximum(X[:, 0], X[:, 1])
        res = Isaac().discover(X, y, name=f"b1_{s}")
        okw = (res["verdict"] == "UNDERSTOOD"
               and res["certificate"] == "machine-exact")
        hit += okw
        if s == 0:
            eq0 = res["equation"]
            print(f"       seed 0: {res['verdict']} / {res['certificate']}"
                  f"  eq: {res['equation']}")
    check("B1 max UNDERSTOOD machine-exact 3/3", hit == 3,
          f"{hit}/3; eq {eq0}")

    # B2 — the step world
    print("B2. step world: 2*x0 + 1.5*[1<x1<2], noise 0.05 told, n=400")
    rng = np.random.default_rng(600)
    X = np.column_stack([rng.uniform(0, 3, 400), rng.uniform(0, 3, 400)])
    y = q(2.0 * X[:, 0] + 1.5 * ((X[:, 1] > 1) & (X[:, 1] < 2))
          + rng.normal(0, 0.05, 400), 0.01)
    res = Isaac().discover(X, y, name="b2", told_sigma=0.05)
    eq = res["equation"]
    has_steps = "[x1>1]" in eq and "[x1>2]" in eq
    print(f"       {res['verdict']} / {res['certificate']}  eq: {eq}")
    check("B2 UNDERSTOOD with steps at 1 and 2, within floor",
          res["verdict"] == "UNDERSTOOD" and has_steps
          and res["certificate"].startswith("within floor"),
          f"{res['verdict']} / {eq}")

    # B3 — the blended world at two sizes (deep exact road)
    print("B3. blended world (flag ? x0*x1 : x0+x1) at n=48 and n=96")
    hit = 0
    for n in (48, 96):
        rng = np.random.default_rng(300 + n)
        x01 = rng.integers(1, 10, (n, 2)).astype(float)
        flag = (np.arange(n) % 2).astype(float)
        y = np.where(flag == 0, x01[:, 0] + x01[:, 1],
                     x01[:, 0] * x01[:, 1])
        X = np.column_stack([x01, flag])
        res = Isaac().discover(X, y, name=f"b3_{n}")
        okw = (res["verdict"] == "UNDERSTOOD"
               and res["certificate"] == "machine-exact")
        hit += okw
        print(f"       n={n}: {res['verdict']} / {res['certificate']}"
              f"  eq: {res['equation'][:70]}")
    check("B3 blended machine-exact at both sizes", hit == 2, f"{hit}/2")

    # B4 — noise with the enriched vocabulary
    print("B4. noise x10 (n=200, d=3 incl. binary) — the new words must "
          "not buy false laws")
    fn = 0
    for s in range(10):
        rng = np.random.default_rng(700 + s)
        X = np.column_stack([rng.normal(0, 1, (200, 2)),
                             (rng.uniform(size=200) < 0.5).astype(float)])
        yy = rng.normal(0, 1, 200)
        res = Isaac().discover(X, yy)
        fn += res["verdict"] == "UNDERSTOOD"
    check("B4 false UNDERSTOOD 0/10 on noise", fn == 0, f"{fn}/10")

    # B5 — availability + cost on true laws with the bigger vocabulary
    print("B5. true law x5 (n=400, d=5): availability + per-call cost")
    und, times = 0, []
    for s in range(5):
        rng = np.random.default_rng(900 + s)
        X = rng.normal(0, 1, (400, 5))
        y = X[:, 0] * X[:, 1] + X[:, 2] ** 2 - X[:, 3] \
            + rng.normal(0, 0.02, 400)
        tc = time.perf_counter()
        res = Isaac().discover(X, y, name=f"b5_{s}")
        times.append(time.perf_counter() - tc)
        und += res["verdict"] == "UNDERSTOOD"
    check("B5 availability 5/5 with enriched vocabulary", und == 5,
          f"{und}/5; per-call {np.mean(times):.2f}s "
          f"(max {max(times):.2f}s)")

    # B6 — the tools are organs now
    print("B6. mechanism tools registered and routing")
    mind = Isaac()
    try:
        cat = mind.catalog_tools()
        names = {c.get("name", "") for c in cat} if isinstance(cat, list) \
            else set(cat)
    except Exception:
        names = {m for m in dir(mind) if not m.startswith("_")}
    have = {"compare", "larger", "smaller", "switch"} <= names
    lg = mind.larger(3.0, -1.0)
    routed = (lg["value"] == 3.0 and lg["routed_via"]
              and lg["routed_via"][0]["tool"] == "compare")
    check("B6 tools in the catalog", have,
          f"present: {sorted({'compare','larger','smaller','switch'} & names)}")
    check("B6 larger routes through compare (receipt)", routed,
          lg.get("receipt", "?"))

    # B7 — Kepler regression
    a = np.random.default_rng(11).permutation(
        np.array([0.387, 0.723, 1.0, 1.524, 5.203, 9.537, 19.19, 30.07]))
    res = Isaac().discover(a.reshape(-1, 1), a ** 3, name="kepler")
    check("B7 Kepler n=8 still machine-exact",
          res["verdict"] == "UNDERSTOOD"
          and res["certificate"] == "machine-exact",
          f"{res['verdict']} / {res['certificate']}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed of "
          f"{len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
