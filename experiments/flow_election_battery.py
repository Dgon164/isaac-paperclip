"""flow_election_battery.py — PROMOTION #16 BATTERY: flow ELECTIONS
and SUPERSESSION become engine organs (flow_tally / elect_flow /
branch_flow). Research basis: flow_adaptation_probe.py 11/11 (the
mechanics ran shim-side over the ledger); this battery gates them as
organs, with the word-election shape: champions re-electable, losers
kept with their records, supersession chains never erased.

WRITTEN BEFORE THE SURGERY (batteries-before-mechanisms law).

PREDICTIONS (filed before the engine is touched; wrong ones kept)
  H1 SUCCESS DECLARATION: steps may declare success=True; flow_tally
     counts wins by declared success steps over the walk ledger.
  H2 elect_flow picks the champion by win rate, writes an election
     receipt to the ledger, and the task node carries the champion
     with the full tallies (losers ON the record).
  H3 RE-ELECTION: after a window of reversed fortunes (the champion
     losing, the old flow winning), a WINDOWED election flips the
     champion — and the supersession chain keeps the prior champion
     with its record (active/superseded, the read_floor pattern).
  H4 branch_flow: ONE CALL clones a flow and grafts the named-case
     door + steps — reproducing the adaptation probe's branched flow
     (same roads, same duel outcome) without hand-authoring.
  H5 WINDOWING: the election over window=W uses only the last W
     walks per flow (old losses age out; measured, not assumed).
  H6 REGISTRATION: flow_tally / elect_flow / branch_flow in the
     catalog.
  GATE (separate): engine self-test 11/11.

Run: cd experiments && PYTHONHASHSEED=0 python flow_election_battery.py
"""
import os
import sys
import time

import numpy as np  # noqa: F401

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402
from flow_adaptation_probe import (  # noqa: E402
    make_world, road, triage2_steps)

Isaac = isaac_mod.Isaac


def with_success(steps):
    for st in steps:
        if st["id"] == "report_pass":
            st["success"] = True
    return steps


def run_worlds(mind, flow, worlds, tag, x_small_full=False):
    outs = []
    for i, (kind, seed) in enumerate(worlds):
        st = make_world(kind, seed)
        if x_small_full:
            st["X_small"], st["y_small"] = st["X"], st["y"]
        st["law_name"] = f"{tag}_{i}"
        st["law2"] = f"{tag}_{i}b"
        out, tr = mind.walk_flow(flow, st)
        outs.append(road(tr))
    return outs


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    mind = Isaac()
    mind.define_flow("triage2", with_success(triage2_steps(deepen=False)))

    # H4 first: branch in ONE CALL, then use both flows throughout
    mind.branch_flow(
        "triage2", "triage2b", at_step="discover",
        door=dict(to="deepen", when=dict(field="verdict",
                                         equals="PARTIAL")),
        extra_steps=[
            dict(id="deepen", op="discover",
                 args=dict(X="X_small", y="y_small", name="law2"),
                 out="res2",
                 doors=[dict(to="validate2",
                             when=dict(field="verdict",
                                       equals="UNDERSTOOD")),
                        dict(to="refuse")]),
            dict(id="validate2", op="apply_law",
                 args=dict(name="law2", X="X_check"), out="val2",
                 measure=dict(rms_against="y_check"),
                 doors=[dict(to="report_pass",
                             when=dict(cmp="smaller", field="rms",
                                       than="thr")),
                        dict(to="report_flag")])])
    worlds = [("plain", 100 + i) for i in range(3)] \
        + [("blended", 201), ("blended", 202)]
    r_orig = run_worlds(mind, "triage2", worlds, "o")
    r_br = run_worlds(mind, "triage2b", worlds, "b")
    br_wins = sum(r[-1] == "report_pass" for r in r_br)
    orig_wins = sum(r[-1] == "report_pass" for r in r_orig)
    check("H4 branch_flow reproduces the adaptation duel in one call",
          br_wins == 5 and orig_wins == 3
          and any("deepen" in r for r in r_br),
          f"orig {orig_wins}/5, branched {br_wins}/5; deepen roads "
          f"{sum('deepen' in r for r in r_br)}")

    # H1 tallies with declared success
    t_all = mind.flow_tally()
    t2 = t_all.get("flow:triage2", {})
    t2b = t_all.get("flow:triage2b", {})
    check("H1 tallies from the ledger via declared success steps",
          t2.get("wins") == 3 and t2.get("walks") == 5
          and t2b.get("wins") == 5 and t2b.get("walks") == 5,
          f"triage2 {t2}; triage2b {t2b}")

    # H2 election
    el = mind.elect_flow(["triage2", "triage2b"], task="triage-task")
    rec = mind.recall_findings(kind="flow-election", limit=5)
    champ_meta = mind.net.get_meta("task:triage-task", "champion")
    check("H2 champion elected with receipts; losers on the record",
          el["champion"] == "triage2b" and len(rec) >= 1
          and champ_meta and champ_meta.get("flow") == "triage2b"
          and "triage2" in el["tallies"],
          f"champion {el['champion']}; tallies {el['tallies']}")

    # H3 re-election on reversed fortunes (windowed). Build the
    # history so window and full-history genuinely disagree: triage2b
    # earns 8 more wins (lifetime rate high), THEN loses 4 in a row
    # (deepen defanged: X_small = full n=240, past the deep road).
    run_worlds(mind, "triage2b",
               [("plain", 500 + i) for i in range(8)], "mid")
    bad = [("blended", 301 + i) for i in range(4)]
    run_worlds(mind, "triage2b", bad, "bad", x_small_full=True)
    el2 = mind.elect_flow(["triage2", "triage2b"], task="triage-task",
                          window=4)
    champ2 = mind.net.get_meta("task:triage-task", "champion")
    chain = champ2.get("superseded") or []
    check("H3 windowed re-election flips the champion; chain kept",
          el2["champion"] == "triage2" and champ2["flow"] == "triage2"
          and any(c.get("flow") == "triage2b" for c in chain),
          f"champion {el2['champion']}; chain "
          f"{[c.get('flow') for c in chain]}")

    # H5 window mechanics: full-history election still favors triage2b
    el3 = mind.elect_flow(["triage2", "triage2b"], task="triage-task")
    check("H5 window vs full history measured (old losses age out "
          "only in the window)", el3["champion"] == "triage2b",
          f"full-history champion {el3['champion']} (windowed was "
          f"{el2['champion']})")

    # H6 registration
    try:
        cat = mind.catalog_tools()
        names = {c.get("name", "") for c in cat} if isinstance(cat, list) \
            else set(cat)
    except Exception:
        names = {m for m in dir(mind) if not m.startswith("_")}
    check("H6 election organs registered",
          {"flow_tally", "elect_flow", "branch_flow"} <= names,
          f"{sorted({'flow_tally', 'elect_flow', 'branch_flow'} & names)}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed of "
          f"{len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
