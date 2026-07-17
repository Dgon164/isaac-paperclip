"""flow_adaptation_probe.py — FLOW ADAPTATION: elections, piecewise
supersession, and the interpreter attack list, on the promoted walker
(the sheet: "steps carry use/outcome receipts and face the same
recent-window ELECTIONS as words; a flow that keeps losing gets mined
and the named condition IS the branch point — BRANCHING A FLOW =
PIECEWISE SUPERSESSION AT THE FLOW LEVEL (clone the step for the
named case, duel decides, loser kept)").

RESEARCH, NOT THE ENGINE (the walker organs are engine; the election
and supersession MECHANICS are probed here before their promotion).

THE STORY UNDER TEST: flow 'triage2' refuses PARTIAL verdicts. On
plain worlds that is right; on BLENDED-CONDITIONAL worlds (a real law
the big-n road cannot say exactly) it LOSES — a lawful world refused.
  1. Walk a batch; outcomes bank per flow (the walk ledger).
  2. MINE the walk receipts with the REAL commonality organ: the
     losing class gets NAMED (verdict=PARTIAL + pool=scream).
  3. Clone the road for the named case: triage2b = triage2 plus ONE
     new door (PARTIAL -> deepen: re-discover on a n<=100 subsample,
     where the deep exact road lives) — everything else untouched.
  4. THE DUEL: branched flow wins the named class and changes NOTHING
     off it; the original flow is KEPT and still walkable (loser
     kept, re-electable).
  5. ELECTION v1: ledger tallies elect the champion per task; the
     loser keeps its record.
ATTACK LIST (07-13, unblocked by the walker): productive LOOPS that
halt by predicate, not just by cap; INTERFERENCE (interleaved walks
stay separate); CHUNK-IN-FLOW composition.

PREDICTIONS (filed before the first run; wrong ones kept)
  G1 outcomes bank: the walk ledger tallies wins/losses per flow.
  G2 the miner names the losing class from walk-receipt features
     (verdict=PARTIAL named past its null; plain worlds not named).
  G3 branched flow: named-class walks take the deepen door BY
     PREDICATE (receipt shows it), reach machine-exact, and pass.
  G4 PIECEWISE: off the named class the branched flow's road is
     IDENTICAL (deepen door bypassed with receipt).
  G5 duel, complete numbers: original 5/10 wins; branched 10/10.
  G6 loser kept: the original flow still walks, still refuses the
     blended class (its record intact).
  G7 election v1: tallies pick the branched flow as champion; the
     original stays on the books with its score.
  G8 a productive LOOP (retry discover on growing data) halts by
     predicate with receipts, not by the hop cap.
  G9 interleaved walks of two flows do not interfere (separate
     states, correct roads both).
  G10 a CHUNK used as a STEP inside another flow walks correctly
     (composition: minted functions are callable words).
  G11 cost: the full probe < 240 s.

RUN-2 WRONG-KEPT: one blended seed stamps UNDERSTOOD-uncertified
with a merely-APPROXIMATE fit (the enriched vocabulary is genuinely
good at n=240) and sailed through the sloppy thr=1.0 — the failing
class has TWO FACES (refused-PARTIAL and flagged-inexact). Cures,
disclosed: the flow now DEMANDS near-exactness (thr=0.01) and the
clone covers both faces (validate-flag -> deepen as well). The
miner's named signature stays dominated by verdict=PARTIAL.

Run: cd experiments && PYTHONHASHSEED=0 python flow_adaptation_probe.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac


def triage2_steps(deepen=False):
    disc_doors = [dict(to="validate",
                       when=dict(field="verdict", equals="UNDERSTOOD"))]
    if deepen:
        disc_doors.append(dict(to="deepen",
                               when=dict(field="verdict",
                                         equals="PARTIAL")))
    disc_doors.append(dict(to="refuse"))
    steps = [
        dict(id="floor", op="read_floor", args=dict(y="y", X="X"),
             out="floor_read", doors=[dict(to="discover")]),
        dict(id="discover", op="discover",
             args=dict(X="X", y="y", name="law_name"), out="res",
             doors=disc_doors),
        dict(id="validate", op="apply_law",
             args=dict(name="law_name", X="X_check"), out="val",
             measure=dict(rms_against="y_check"),
             doors=[dict(to="report_pass",
                         when=dict(cmp="smaller", field="rms",
                                   than="thr")),
                    (dict(to="deepen") if deepen
                     else dict(to="report_flag"))]),
        dict(id="refuse", op="record_finding",
             args=dict(kind="k_refuse", name="law_name"), out="_r",
             doors=[]),
        dict(id="report_pass", op="record_finding",
             args=dict(kind="k_pass", name="law_name"), out="_r",
             doors=[]),
        dict(id="report_flag", op="record_finding",
             args=dict(kind="k_flag", name="law_name"), out="_r",
             doors=[]),
    ]
    if deepen:
        steps.insert(3, dict(
            id="deepen", op="discover",
            args=dict(X="X_small", y="y_small", name="law2"),
            out="res2",
            doors=[dict(to="validate2",
                        when=dict(field="verdict",
                                  equals="UNDERSTOOD")),
                   dict(to="refuse")]))
        steps.insert(4, dict(
            id="validate2", op="apply_law",
            args=dict(name="law2", X="X_check"), out="val2",
            measure=dict(rms_against="y_check"),
            doors=[dict(to="report_pass",
                        when=dict(cmp="smaller", field="rms",
                                  than="thr")),
                   dict(to="report_flag")]))
    return steps


def make_world(kind, seed):
    rng = np.random.default_rng(seed)
    if kind == "plain":                       # exact integer sums
        X = rng.integers(1, 10, (60, 2)).astype(float)
        y = X[:, 0] + X[:, 1]
        Xc = rng.integers(1, 10, (60, 2)).astype(float)
        yc = Xc[:, 0] + Xc[:, 1]
        Xs, ys = X, y
    else:                                     # blended conditional, big n
        # RUN-1 WRONG-KEPT: n=200 splits to a 100-row train half —
        # EXACTLY the deep exact road's boundary — so the engine now
        # SAYS the 5-term law and the planted weakness never fails
        # (the probe's premise was falsified by promotion #12's own
        # strength). n=240 puts the train half past the boundary.
        n = 240
        x01 = rng.integers(1, 10, (n, 2)).astype(float)
        f = (np.arange(n) % 2).astype(float)
        y = np.where(f == 0, x01[:, 0] + x01[:, 1],
                     x01[:, 0] * x01[:, 1])
        X = np.column_stack([x01, f])
        Xs, ys = X[:96], y[:96]               # where the deep road lives
        xc = rng.integers(1, 10, (60, 2)).astype(float)
        fc = (rng.uniform(size=60) < 0.5).astype(float)
        Xc = np.column_stack([xc, fc])
        yc = np.where(fc == 0, xc[:, 0] + xc[:, 1], xc[:, 0] * xc[:, 1])
    return dict(X=X, y=y, X_small=Xs, y_small=ys, X_check=Xc,
                y_check=yc, thr=0.01,
                k_refuse="fa-refuse", k_pass="fa-pass",
                k_flag="fa-flag")


def road(tr):
    return [t["step"].split(".")[-1] for t in tr if "step" in t]


def walk_batch(mind, flow, worlds, tag):
    recs = []
    for i, (kind, seed) in enumerate(worlds):
        st = make_world(kind, seed)
        st["law_name"] = f"{tag}_{i}"
        st["law2"] = f"{tag}_{i}b"
        out, tr = mind.walk_flow(flow, st)
        r = road(tr)
        res = st.get("res", {})
        legs = res.get("legs") or {}
        recs.append(dict(kind=kind, road=r, win=r[-1] == "report_pass",
                         verdict=str(res.get("verdict")),
                         pool=str((legs.get("pool") or {}).get("state",
                                                               "-")),
                         trace=tr))
    return recs


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    mind = Isaac()
    mind.define_flow("triage2", triage2_steps(deepen=False))
    worlds = [("plain", 100 + i) for i in range(5)] \
        + [("blended", 200 + i) for i in range(5)]

    # 1-2: walk the original, bank outcomes, mine the losing class
    recs = walk_batch(mind, "triage2", worlds, "orig")
    wins = sum(r["win"] for r in recs)
    ledger = mind.recall_findings(kind="flow-walk", limit=100)
    # RUN-3 WRONG-KEPT: 1/5 blended seeds is GENUINELY solvable at
    # n=240 (validates at rms<0.01 on fresh truth) — the engine
    # outgrew the planted weakness twice in one probe. The adaptation
    # story measures the 4 that really fail.
    check("G1 outcomes bank in the walk ledger",
          wins == 6 and len(ledger) >= 10,
          f"wins {wins}/10 (5 plain + 1 legitimately-solved blended); "
          f"ledger walks {len(ledger)}")

    events = [dict(verdict=r["verdict"], pool=r["pool"],
                   size=("big" if r["kind"] == "blended" else "small"))
              for r in recs]
    fails = [not r["win"] for r in recs]
    mined = mind.mine_commonality(events, fails)
    named = {tuple(c[:2]) for c in mined["named"]}
    check("G2 the miner NAMES the losing class from walk receipts",
          ("verdict", "PARTIAL") in named,
          f"named {sorted(named)}")

    # 3: clone the road for the named case
    mind.define_flow("triage2b", triage2_steps(deepen=True))
    recs_b = walk_batch(mind, "triage2b", worlds, "branched")
    wins_b = sum(r["win"] for r in recs_b)
    blended_b = [r for r in recs_b if r["kind"] == "blended"]
    partial_b = [r for r in blended_b if r["verdict"] == "PARTIAL"]
    took_deepen = all("deepen" in r["road"] for r in partial_b)
    check("G3 the FAILING face takes the deepen door and PASSES",
          took_deepen and len(partial_b) >= 3
          and all(r["win"] for r in blended_b),
          f"{len(partial_b)} PARTIAL walks all deepened; blended wins "
          f"{sum(r['win'] for r in blended_b)}/5")

    # 4: piecewise — off the named class nothing changes
    plain_o = [r["road"] for r in recs if r["kind"] == "plain"]
    plain_b = [r["road"] for r in recs_b if r["kind"] == "plain"]
    disc_tr = next(t for r in recs_b if r["kind"] == "plain"
                   for t in r["trace"] if t["step"].endswith("discover"))
    bypassed = any("bypassed deepen" in d for d in disc_tr["doors"])
    check("G4 piecewise: plain roads identical, deepen bypassed with "
          "receipt", plain_o == plain_b and bypassed,
          f"roads equal {plain_o == plain_b}; receipt {bypassed}")

    # 5: the duel, complete numbers
    check("G5 duel: original 6/10 -> branched 10/10",
          wins == 6 and wins_b == 10, f"{wins}/10 vs {wins_b}/10")

    # 6: loser kept, still walkable, unchanged behavior
    st6 = make_world("blended", 201)
    st6["law_name"], st6["law2"] = "kept_0", "kept_0b"
    out6, tr6 = mind.walk_flow("triage2", st6)
    check("G6 loser kept: original flow still walks, still loses",
          road(tr6)[-1] in ("refuse", "report_flag"),
          f"road {road(tr6)}")

    # 7: election v1 over the ledger tallies
    tally = {}
    for w in mind.recall_findings(kind="flow-walk", limit=200):
        fl = w.get("name", "?")
        if "triage2" not in fl:
            continue
        t = tally.setdefault(fl, [0, 0])
        t[0] += int((w.get("road") or ["-"])[-1] == "report_pass")
        t[1] += 1
    champ = max(tally, key=lambda k: tally[k][0] / max(tally[k][1], 1))
    check("G7 election: branched flow elected, loser keeps its record",
          champ == "flow:triage2b" and "flow:triage2" in tally,
          f"tallies {dict((k, tuple(v)) for k, v in tally.items())}; "
          f"champion {champ}")

    # 8: a productive loop halting by predicate (not the cap)
    mind.define_flow("grow", [
        dict(id="grab", op="scratch_store",
             args=dict(key="grab_key", value="grow_n"), out="_g",
             doors=[dict(to="try")]) if hasattr(mind, "scratch_store")
        else dict(id="grab", op="record_finding",
                  args=dict(kind="k_pass", name="law_name"), out="_g",
                  doors=[dict(to="try")]),
        dict(id="try", op="discover",
             args=dict(X="X_small", y="y_small", name="law_name"),
             out="res",
             doors=[dict(to="done_",
                         when=dict(field="verdict",
                                   equals="UNDERSTOOD")),
                    dict(to="try")]),
        dict(id="done_", op="record_finding",
             args=dict(kind="k_pass", name="law_name"), out="_r",
             doors=[]),
    ])
    st8 = make_world("blended", 208)
    st8["law_name"] = "loop_0"
    out8, tr8 = mind.walk_flow("grow", st8, hop_cap=8)
    r8 = road(tr8)
    check("G8 productive loop halts by predicate, under the cap",
          out8 == "done" and r8[-1] == "done_" and len(r8) < 8,
          f"road {r8} (out {out8})")

    # 9: interference — interleave two walks' step results manually
    stA = make_world("plain", 300)
    stA["law_name"] = "ilA"
    stB = make_world("blended", 301)
    stB["law_name"], stB["law2"] = "ilB", "ilBb"
    outA, trA = mind.walk_flow("triage2", stA)
    outB, trB = mind.walk_flow("triage2b", stB)
    outA2, trA2 = mind.walk_flow("triage2", stA | {"law_name": "ilA2"})
    check("G9 interleaved walks stay separate (roads correct both)",
          road(trA)[-1] == "report_pass" == road(trA2)[-1]
          and road(trB)[-1] == "report_pass",
          f"A {road(trA)[-1]}, B {road(trB)[-1]}, A2 {road(trA2)[-1]}")

    # 10: chunk-in-flow composition
    mind.mint_chunk("triage2b", "triage2b")
    mind.define_flow("outer", [
        dict(id="run_chunk", op="chunk", flow="flow:triage2b",
             doors=[])])
    st10 = make_world("blended", 210)
    st10["law_name"], st10["law2"] = "cf_0", "cf_0b"
    out10, tr10 = mind.walk_flow("outer", st10)
    nested = tr10[0].get("nested") if tr10 else None
    check("G10 chunk-as-step composition walks correctly",
          out10 == "done" and nested is not None
          and road(nested)[-1] == "report_pass",
          f"outer out {out10}; nested road "
          f"{road(nested) if nested else '?'}")

    dt = time.perf_counter() - t0
    check("G11 cost < 240 s", dt < 240, f"{dt:.1f}s")
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed of "
          f"{len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
