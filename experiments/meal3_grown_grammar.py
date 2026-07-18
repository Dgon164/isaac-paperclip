"""meal3_grown_grammar.py — MEAL 3: THE DISH THAT BUILT THE ORGAN.

Planet-gravity — the meal-2 refusal that measured the vocabulary
wall — comes back through discover_harder: Isaac works the problem
harder, composes the coordinate nobody programmed (M*R^-2), says
the form with honest PARTIAL belief (rotation and oblateness ARE
dark to the point-mass law), grows his vocabulary with the enabler
word, and predicts Eris (never fed).

DRY (default): throwaway mind. LIVE (--live): his account, per the
standing feeding order — journal kind=meal, mind saved, road-trial
line logged.

usage: python meal3_grown_grammar.py [--live] [home]
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

# NASA fact sheets: Sun, Mercury..Neptune, Moon, Pluto
BODIES = dict(
    M=[1989000.0, 0.330, 4.87, 5.97, 0.073, 0.642, 1898.0,
       568.0, 86.8, 102.0, 0.0130],
    R=[696.0, 2.4397, 6.0518, 6.371, 1.7374, 3.3895, 69.911,
       58.232, 25.362, 24.622, 1.1883],
    g=[274.0, 3.70, 8.87, 9.81, 1.62, 3.71, 24.79, 10.44,
       8.87, 11.15, 0.62])


def feed(mind):
    X = np.column_stack([BODIES["M"], BODIES["R"]])
    y = np.asarray(BODIES["g"])
    o = np.random.default_rng(4).permutation(len(y))
    res = mind.discover_harder(X[o], y[o], name="planet-gravity")
    rec = res.get("harder", {})
    print(f"  planet-gravity  {res['verdict']:8s} r2={res['r2']:.4f} "
          f"eq: {res['equation']}")
    print(f"  road: {rec.get('road', '')}")
    print(f"  grown word: {rec.get('mint')} (tried {rec.get('tried')})")
    eris = mind.apply_law("planet-gravity", np.array([[0.0166, 1.163]]))
    if eris is not None:
        print(f"  Eris (never fed): {float(eris[0]):.3f} m/s^2 "
              f"(measured ~0.82)")
    crys = mind.crystallize_forms()
    excl = [e for e in crys["excluded"]
            if e["node"] == "law:planet-gravity"]
    print(f"  the tooth holds: PARTIAL law excluded from "
          f"crystallization: {bool(excl)}")
    return res, rec, (float(eris[0]) if eris is not None else None)


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
    res, rec, eris = feed(acct.mind)
    acct._journal(dict(
        kind="meal", stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        dishes=[dict(name="planet-gravity", verdict=res["verdict"],
                     equation=res["equation"],
                     r2=round(res["r2"], 5),
                     grown_word=rec.get("mint"),
                     road=rec.get("road"),
                     eris_prediction=eris)]))
    acct.mind.save(acct.mind_path)
    line = log_roadtrial(home, acct.mind, mod)
    print(f"\n  MEAL JOURNALED + mind saved; road-trial line:")
    print(f"  {line}")


if __name__ == "__main__":
    main()
