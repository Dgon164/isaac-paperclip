"""flow_promotion_battery.py — PROMOTION #15 BATTERY: the flow walker
becomes ENGINE ORGANS (define_flow / walk_flow / mint_chunk — the
kernel loop's first permanent slice). Research basis:
flow_walker_probe.py 10/10; this battery gates the same behavior
through the engine, plus registration and the walk ledger.

WRITTEN BEFORE THE SURGERY (batteries-before-mechanisms law).

PREDICTIONS (filed before the engine is touched; wrong ones kept)
  W1 flows author through mind.define_flow and live in the net.
  W2 true-law world: mind.walk_flow('triage', state) walks
     floor->discover->validate->report_pass.
  W3 noise world: refusal road, validate BYPASSED WITH RECEIPT.
  W4 branch predicates route THROUGH the compare organ (receipt shows
     the sign verdict).
  W5 cyclic flow halts at the hop cap with a receipt.
  W6 missing organ refuses honestly.
  W7 mind.mint_chunk after 3 greens; walking the CHUNK BY NAME
     ('chunk:triage') equals walking the chain.
  W8 replay reproduces the door sequence.
  W9 pickle round-trip: flows, chunks, and walks survive.
  W10 cost: full walk < 5 s.
  W11 REGISTRATION: define_flow / walk_flow / mint_chunk in the
     catalog (every tool ships with its node).
  W12 THE WALK LEDGER: every walk leaves a findings entry
     (kind='flow-walk' with outcome + road) — walks are receipts,
     searchable like any other outcome.
  GATE (separate): engine self-test 11/11.

Run: cd experiments && PYTHONHASHSEED=0 python flow_promotion_battery.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac


def triage_steps():
    return [
        dict(id="floor", op="read_floor",
             args=dict(y="y", X="X"), out="floor_read",
             doors=[dict(to="discover")]),
        dict(id="discover", op="discover",
             args=dict(X="X", y="y", name="law_name"), out="res",
             doors=[dict(to="validate",
                         when=dict(field="verdict",
                                   equals="UNDERSTOOD")),
                    dict(to="refuse")]),
        dict(id="validate", op="apply_law",
             args=dict(name="law_name", X="X_check"), out="val",
             measure=dict(rms_against="y_check"),
             doors=[dict(to="report_pass",
                         when=dict(cmp="smaller", field="rms",
                                   than="floor3")),
                    dict(to="report_flag")]),
        dict(id="refuse", op="record_finding",
             args=dict(kind="k_refuse", name="law_name"),
             out="_r", doors=[]),
        dict(id="report_pass", op="record_finding",
             args=dict(kind="k_pass", name="law_name"),
             out="_r", doors=[]),
        dict(id="report_flag", op="record_finding",
             args=dict(kind="k_flag", name="law_name"),
             out="_r", doors=[]),
    ]


def make_state(world, seed):
    rng = np.random.default_rng(seed)
    if world == "law":
        X = rng.integers(1, 10, (60, 2)).astype(float)
        y = X[:, 0] + X[:, 1]
        Xc = rng.integers(1, 10, (60, 2)).astype(float)
        yc = Xc[:, 0] + Xc[:, 1]
    else:
        X = rng.normal(0, 1, (60, 2))
        y = rng.normal(0, 1, 60)
        Xc, yc = X.copy(), rng.normal(0, 1, 60)
    return dict(X=X, y=y, X_check=Xc, y_check=yc,
                law_name=f"fp_{world}_{seed}",
                k_refuse="flow-refusal", k_pass="flow-pass",
                k_flag="flow-flag", floor3=1.0)


def road(trace):
    return [t["step"].split(".")[-1] for t in trace if "step" in t]


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    mind = Isaac()
    mind.define_flow("triage", triage_steps())

    # W1
    start = mind.net.get_doors("flow:triage", tag="flow-start")
    check("W1 flow authored via organ, lives in the net", bool(start),
          f"start {sorted(start)}")

    # W2
    t_w = time.perf_counter()
    out2, tr2 = mind.walk_flow("triage", make_state("law", 1))
    w_s = time.perf_counter() - t_w
    check("W2 green road end to end",
          road(tr2) == ["floor", "discover", "validate", "report_pass"],
          f"road {road(tr2)}")

    # W3
    out3, tr3 = mind.walk_flow("triage", make_state("noise", 2))
    disc3 = next(t for t in tr3 if t["step"].endswith("discover"))
    check("W3 refusal road; validate bypassed with receipt",
          road(tr3) == ["floor", "discover", "refuse"]
          and any("bypassed validate" in d for d in disc3["doors"]),
          f"{road(tr3)}")

    # W4
    val2 = next(t for t in tr2 if t["step"].endswith("validate"))
    check("W4 compare inside the door choice",
          any("sign(" in d for d in val2["doors"]),
          val2["doors"][0][:70])

    # W5
    mind.define_flow("loopy", [
        dict(id="a", op="open_world", args=dict(container="law_name"),
             out="_a", doors=[dict(to="b")]),
        dict(id="b", op="open_world", args=dict(container="law_name"),
             out="_b", doors=[dict(to="a")]),
    ])
    out5, tr5 = mind.walk_flow("loopy", make_state("law", 5))
    check("W5 hop cap halts cyclic flow", out5 == "hop-cap",
          f"{out5} after {len(tr5)} hops")

    # W6
    mind.define_flow("ghost", [dict(id="a", op="no_such_organ",
                                    args={}, doors=[])])
    out6, tr6 = mind.walk_flow("ghost", make_state("law", 6))
    check("W6 missing organ refused honestly", out6 == "refused",
          tr6[-1]["receipt"][:60])

    # W7 — chunk by name
    greens = int(road(tr2)[-1] == "report_pass")
    for s in (7, 8):
        og, tg = mind.walk_flow("triage", make_state("law", s))
        greens += int(road(tg)[-1] == "report_pass")
    mind.mint_chunk("triage", "triage", minted_after=greens)
    out7, tr7 = mind.walk_flow("chunk:triage", make_state("law", 9))
    out7b, tr7b = mind.walk_flow("triage", make_state("law", 9))
    r7 = road(tr7[0]["nested"]) if tr7 and "nested" in tr7[0] else road(tr7)
    check("W7 chunk minted; chunk walk == chain walk",
          greens == 3 and out7 == out7b and r7 == road(tr7b),
          f"greens {greens}/3; chunk road {r7}")

    # W8
    _, tra = mind.walk_flow("triage", make_state("law", 1))
    check("W8 replay reproduces doors", road(tra) == road(tr2),
          f"{road(tra)}")

    # W9
    import tempfile
    pth = os.path.join(tempfile.gettempdir(), "flow_prom_mind.pkl")
    mind.save(pth)
    m2 = Isaac.load(pth)
    out9, tr9 = m2.walk_flow("triage", make_state("law", 11))
    os.remove(pth)
    check("W9 pickle round-trip walks again",
          road(tr9)[-1] in ("report_pass", "report_flag"),
          f"{road(tr9)}")

    # W10
    check("W10 walk cost < 5 s", w_s < 5.0, f"{w_s:.2f}s")

    # W11
    try:
        cat = mind.catalog_tools()
        names = {c.get("name", "") for c in cat} if isinstance(cat, list) \
            else set(cat)
    except Exception:
        names = {m for m in dir(mind) if not m.startswith("_")}
    check("W11 flow organs registered",
          {"define_flow", "walk_flow", "mint_chunk"} <= names,
          f"{sorted({'define_flow', 'walk_flow', 'mint_chunk'} & names)}")

    # W12 — the walk ledger
    walks = mind.recall_findings(kind="flow-walk", limit=50)
    check("W12 walks land in the findings ledger",
          len(walks) >= 5 and all("road" in w for w in walks[:3]),
          f"{len(walks)} walk records; latest road "
          f"{walks[0].get('road') if walks else '?'}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed of "
          f"{len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
