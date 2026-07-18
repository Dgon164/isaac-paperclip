"""meal7_memory.py — MEAL 7: HIS LAWS GET THEIR MEMORY.

The same dishes he has already eaten, re-fed through the promoted
facts layer: identical data -> identical laws (the artifact claim,
proven at promotion #17) — but now every law KEEPS its sampled
breakdown, and his series remember their points and largest
leftovers. Then the reference receipts: recall_evidence shows the
planets behind Kepler; context_sample answers "what does Boyle's
world look like near V=30?" from remembered rows.

usage: python meal7_memory.py [--live] [home]
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402
import meal1_first_laws as m1                          # noqa: E402
import meal2_diversity as m2                           # noqa: E402


def feed(mind):
    dishes = []
    rng = np.random.default_rng(0)
    for key in ("solar_system", "jupiter_moons", "saturn_moons",
                "boyle_1662"):
        name, xs, ys = m1.PLATE[key]
        X = np.asarray(xs, float).reshape(-1, 1)
        y = np.asarray(ys, float)
        o = rng.permutation(len(y))
        r = mind.discover(X[o], y[o], name=name)
        ev = mind.recall_evidence(name)
        print(f"  {name:16s} {r['verdict']:10s} remembered "
              f"{len(ev['rows'])}/{ev['n_source']} rows")
        dishes.append(dict(name=name, verdict=r["verdict"],
                           remembered=len(ev["rows"])))
    for name, X, y in m2.load_plate():
        if name in ("planet-gravity", "sunspots-1700",
                    "co2-maunaloa"):
            continue
        o = rng.permutation(len(y))
        r = mind.discover(X[o], y[o], name=name)
        ev = mind.recall_evidence(name)
        print(f"  {name:16s} {r['verdict']:10s} remembered "
              f"{len(ev['rows'])}/{ev['n_source']} rows")
        dishes.append(dict(name=name, verdict=r["verdict"],
                           remembered=len(ev["rows"])))
    # the reference receipts
    ev = mind.recall_evidence("solar-system")
    xs = sorted(row[0] for row in ev["rows"])
    print(f"  Kepler's remembered planets: a = {xs}")
    ctx = mind.context_sample("boyle-1662", [30.0], k=2)
    print(f"  'near V=30, what did Boyle see?' -> "
          f"{[(c['x'][0], c['y']) for c in ctx]}")
    return dishes, dict(kepler_rows=xs,
                        boyle_near_30=[(c["x"][0], c["y"])
                                       for c in ctx])


def main():
    live = "--live" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    home = args[0] if args else os.path.join(
        os.path.expanduser("~"), "Documents", "isaac_home")

    if not live:
        print("DRY RUN — throwaway mind, his account untouched")
        feed(mod.Isaac())
        return

    from isaac_store.sparring import IsaacAccount      # noqa: E402
    from isaac_store.roadtrial import log_roadtrial    # noqa: E402
    acct = IsaacAccount(home, mod)
    print(f"LIVE — his account: {home} "
          f"({acct.sessions_so_far()} journal entries so far)")
    dishes, refs = feed(acct.mind)
    acct._journal(dict(kind="meal",
                       stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                       dishes=dishes, references=refs))
    acct.mind.save(acct.mind_path)
    line = log_roadtrial(home, acct.mind, mod)
    print(f"\n  MEAL JOURNALED + mind saved; road-trial line:")
    print(f"  {line}")


if __name__ == "__main__":
    main()
