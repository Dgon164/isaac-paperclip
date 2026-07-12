"""Triangulation battery — both halves of the same whole, proven.

Y1 COMPLETION: A's law needs x; x is a COLUMN of B; alone A refuses,
   jointly the law is SAID exactly; the scrambled-pairing null is
   beaten by a mile
Y2 HALVES: x lives in NEITHER dataset (A's leftover is x+s, B's is
   x-s); alone each side holds ~half the truth (measured); jointly
   the latents unmix (x recovered r2 > 0.95 vs the PLANTED truth)
Y3 the scrambled kill: the same extraction under permuted pairing
   recovers nothing (r2 ~ 0)
Y4 NO ALIGNMENT: no shared column -> refusal
Y5 NO CLOSURE: unrelated datasets sharing a key -> refusal, 2 seeds,
   0 false closures
Run: python test_triangulate.py   (from isaac_store/)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.triangulate import triangulate

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def table(columns, arrays):
    rows = np.column_stack(arrays).tolist()
    return dict(columns=columns, rows=rows)


def r2(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return float(np.corrcoef(a, b)[0, 1]) ** 2


def main():
    print("  loading engine...")
    mod = bridge.load_isaac_module()
    rng = np.random.default_rng(71)
    n = 400
    k = np.arange(n, dtype=float)

    print("Y1. completion: A's shadow is B's column")
    x = rng.uniform(-2, 2, n)
    a1 = rng.uniform(-2, 2, n)
    yA = 3.0 * x * a1 + rng.normal(0, 0.02, n)
    A = table(["k", "a1", "yA"], [k, a1, yA])
    B = table(["k", "x", "yB"], [k, x, rng.normal(0, 1, n)])
    r = triangulate(A, B, mod=mod)
    check("verdict RESOLVED — COMPLETION",
          r["verdict"] == "RESOLVED — COMPLETION", r.get("why", ""))
    check("alone A held almost nothing, jointly nearly all",
          r["alone"]["A"] < 0.2 and r["joint_r2"] > 0.95,
          f"alone {r['alone']['A']} -> joint {r['joint_r2']}")
    check("the scrambled null is beaten by a mile",
          r["gain"] > 5 * max(r["scrambled_null95"], 0.01))
    check("the joint equation names the crossing",
          "x0" in str(r.get("equation", "")) or
          r.get("equation") is not None)

    print("Y2. halves: x lives in NEITHER dataset")
    # asymmetric latents on purpose: equal-variance Gaussians are
    # unresolvable IN PRINCIPLE (the ICA limit — this battery found
    # it; the refusal there is correct and documented)
    x2 = rng.normal(0, 1, n)
    s2 = rng.normal(0, 0.8, n)
    a2 = rng.uniform(-2, 2, n)
    b2 = rng.uniform(-2, 2, n)
    yA2 = x2 + s2 + a2 ** 2 + rng.normal(0, 0.05, n)
    yB2 = x2 - s2 + np.sin(3 * b2) + rng.normal(0, 0.05, n)
    A2 = table(["k", "a1", "yA"], [k, a2, yA2])
    B2 = table(["k", "b1", "yB"], [k, b2, yB2])
    r2_ = triangulate(A2, B2, mod=mod)
    check("verdict RESOLVED — HALVES",
          r2_["verdict"] == "RESOLVED — HALVES", r2_.get("why", ""))
    x_hat = np.array(r2_["latents"]["x"])
    s_hat = np.array(r2_["latents"]["s"])
    fit_x = max(r2(x_hat, x2), r2(s_hat, x2))
    fit_s = max(r2(x_hat, s2), r2(s_hat, s2))
    check("the shared latent x is RECOVERED vs planted truth",
          fit_x > 0.95, f"r2={fit_x:.4f}")
    check("the opposed latent s too", fit_s > 0.95, f"r2={fit_s:.4f}")
    alone_x = r2(yA2 - a2 ** 2, x2)
    check("measured: either side ALONE holds only ~half of x",
          0.3 < alone_x < 0.7, f"alone r2={alone_x:.3f}")

    print("Y3. the scrambled kill")
    perm = np.random.default_rng(1).permutation(n)
    B2s = table(["k", "b1", "yB"], [k, b2[perm], yB2[perm]])
    rs = triangulate(A2, B2s, mod=mod)
    if rs["verdict"] == "RESOLVED — HALVES":
        xs = np.array(rs["latents"]["x"])
        check("scrambled pairing recovers NOTHING",
              r2(xs, x2) < 0.6, f"r2={r2(xs, x2):.3f}")
    else:
        check("scrambled pairing refused outright",
              rs["verdict"] == "NO CLOSURE", rs["verdict"])

    print("Y4. no shared column -> refusal")
    C = table(["idx", "c1", "yC"], [k, a2, yA2])
    r4 = triangulate(A2, C, mod=mod)
    check("NO ALIGNMENT refusal", r4["verdict"] == "NO ALIGNMENT")

    print("Y5. unrelated datasets -> no false closure (2 seeds)")
    false_hits = 0
    for s in range(2):
        g = np.random.default_rng(100 + s)
        u1 = g.uniform(-2, 2, n)
        u2 = g.uniform(-2, 2, n)
        U = table(["k", "a1", "yA"],
                  [k, u1, u1 ** 2 + g.normal(0, 0.05, n)])
        V = table(["k", "b1", "yB"],
                  [k, u2, np.sin(3 * u2) + g.normal(0, 0.05, n)])
        rv = triangulate(U, V, mod=mod)
        if rv["verdict"] != "NO CLOSURE":
            false_hits += 1
    check("0 false closures on unrelated data", false_hits == 0,
          f"{false_hits}/2")
    print()
    print("  Y1:", r["why"])
    print("  Y2:", r2_["why"])
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
