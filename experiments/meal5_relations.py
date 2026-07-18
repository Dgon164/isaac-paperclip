"""meal5_relations.py — MEAL 5: THE FIRST CROSS-DOMAIN FINDING.

Two containers he already holds — the carbon record and the
temperature record — asked the analyst's question: do these move
together? The levels road is reported and refused judgment (shared
trends co-move trivially); the differenced road faces the alignment
null. The expected finding (his to earn, not ours to tell): the
carbon cycle's year-to-year breathing is coupled to global
temperature, same-year, positive — ENSO's fingerprint, found by
his own court.

DRY (default): throwaway mind. LIVE (--live): his account —
relation minted into his net, doored to both worlds, journaled,
road-trial logged.

usage: python meal5_relations.py [--live] [home]
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

FEEDS = os.path.join(ROOT, "data", "feeds")


def load_pair():
    rows = [ln.split() for ln in open(
        os.path.join(FEEDS, "co2_annmean_mlo.txt"), encoding="utf-8")
        if ln.strip() and not ln.startswith("#")]
    yr_c = np.array([float(r[0]) for r in rows])
    co2 = np.array([float(r[1]) for r in rows])
    yr_g, temp = [], []
    for ln in open(os.path.join(FEEDS, "gistemp_glb.csv"),
                   encoding="utf-8"):
        p = ln.strip().split(",")
        if p and p[0].isdigit() and p[13] not in ("***", ""):
            yr_g.append(float(p[0]))
            temp.append(float(p[13]))
    return yr_c, co2, np.array(yr_g), np.array(temp)


def feed(mind):
    yr_c, co2, yr_g, temp = load_pair()
    r = mind.relate_series(yr_c[1:], np.diff(co2), yr_g, temp,
                           name="co2growth-temp",
                           containers=["data-co2-maunaloa",
                                       "data-gistemp"])
    print(f"  co2-growth ~ temperature: {r['verdict']}")
    print(f"    differenced corr {r.get('corr')} (alignment null "
          f"{r['receipts'].get('null')}), shift {r.get('shift')}, "
          f"leader {r.get('leader')}, n {r.get('n')} years")
    print(f"    levels {r.get('levels')} — "
          f"{r['receipts'].get('levels_receipt')}")
    return r


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
    r = feed(acct.mind)
    acct._journal(dict(
        kind="meal", stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        dishes=[dict(name="co2growth-temp", verdict=r["verdict"],
                     corr=r.get("corr"), shift=r.get("shift"),
                     leader=r.get("leader"), n=r.get("n"),
                     null=r["receipts"].get("null"),
                     levels=r.get("levels"))]))
    acct.mind.save(acct.mind_path)
    line = log_roadtrial(home, acct.mind, mod)
    print(f"\n  MEAL JOURNALED + mind saved; road-trial line:")
    print(f"  {line}")


if __name__ == "__main__":
    main()
