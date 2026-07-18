"""container_crystal_battery.py — PROMOTION GATE for per-dataset
containers + cross-domain crystallization (owner, 2026-07-17: "each
dataset is defaulted to its own container, and it can crystalize the
container structures into cross domain structures").

Engine road ONLY (no shims — the research shims of
container_crystal_probe.py moved into discover/_teach_fact/
_install_law/crystallize_forms). The battery pins:

  B1 DEFAULT STAMPING: a bare discover(name=) lands in the dataset's
     OWN container (data-<name>), never base; the earned verdict
     lives on the node.
  B2 ROUTING RESPECTED: an open non-base world captures the law (the
     session road); an explicit container= kwarg beats both.
  B3 THE KINDRED PAIR: two star systems' Kepler laws crystallize into
     exactly ONE lawform family; the falling-bodies stranger joins
     nothing.
  B4 NEVER SMUSHED: each variant keeps its own constants machine-
     close; the parent holds form, never numbers.
  B5 SELECTION BY CONTAINER: which_law names the right law per world
     and REFUSES the interleaved superposition (the mixed-planet
     precedent; >=2 laws = the selection gauge's precondition).
  B6 THE NULL: scrambled row->container assignment yields mixture
     laws that never earn UNDERSTOOD -> excluded with receipts -> no
     family mints (the tooth: kinship between confusions is not
     knowledge).
  B7 THE WOUND CLOSED: the explains-fact of a bare discover is
     invisible under base and answers in its own world; base Q&A
     byte-identical across the whole battery (0 drift).
  B8 TOLD AND CRYSTALLIZED FAMILIES UNIFY: a told same-form law joins
     the SAME lawform node the crystallizer minted (crc32 naming
     shared with tell_law — all methods, one concept).
  B9 MEASURED-JITTER KINSHIP (the first real meal's finding,
     2026-07-18): REAL data — the Sun's planets, Jupiter's moons,
     Saturn's moons (NASA/JPL values) — earns jittered exponents
     (1.5 / 1.49938 / 1.5007), one form wearing measurement noise.
     Machine-identical grouping called these kin strangers (0
     families, wrong-kept); structure grouping with inner constants
     judged at the family machinery's own 5% tolerance mints ONE
     family, THREE variants, constants never smushed.

Run: cd experiments && PYTHONHASHSEED=0 python container_crystal_battery.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac


def worlds(seed=0):
    rng = np.random.default_rng(seed)
    a1 = np.sort(rng.uniform(0.5, 9.0, 240))
    a2 = np.sort(rng.uniform(0.5, 9.0, 240))
    t = np.sort(rng.uniform(0.5, 9.0, 240))
    return (
        ("orbits-sol", a1.reshape(-1, 1), 1.0 * a1 ** 1.5),
        ("orbits-trappist", a2.reshape(-1, 1), 4.9 * a2 ** 1.5),
        ("falling-bodies", t.reshape(-1, 1), 3.0 * t ** 2),
    )


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    mind = Isaac()
    for (s, r, o) in [("water", "boils-at", "100C"),
                      ("stars", "do", "shine"),
                      ("gravity", "pulls", "down")]:
        mind.teach(s, r, o)
    BASE_QA = [("water", "boils-at"), ("stars", "do"),
               ("gravity", "pulls"),
               ("law:orbits-sol", "explains"),
               ("law:orbits-trappist", "explains"),
               ("law:falling-bodies", "explains")]
    before = {q: mind.ask(*q, container="base")["answers"]
              for q in BASE_QA}

    W = worlds()
    for source, X, y in W:
        res = mind.discover(X, y, name=source)
        print(f"    fed {source}: {res['verdict']}  eq: {res['equation']}")

    # B1 — default stamping: the dataset's own container, never base
    ok1, det1 = True, []
    for source, _, _ in W:
        node = f"law:{source}"
        c = f"data-{source}"
        good = (f"in:{c}" in mind.net.get_door_tags(f"world:{c}", node)
                and mind.net.get_meta(node, "container") == c
                and mind.net.get_meta(node, "verdict") == "UNDERSTOOD"
                and not mind.net.get_door_tags("world:base", node))
        ok1 &= good
        det1.append(f"{source}->{mind.net.get_meta(node, 'container')}"
                    f"{'' if good else '(BAD)'}")
    check("B1 default stamping — own container, never base, verdict "
          "on the node", ok1, "; ".join(det1))

    # B2 — routing respected: open world captures; explicit kwarg wins
    m2 = Isaac()
    rng = np.random.default_rng(3)
    xw = np.sort(rng.uniform(0.5, 9.0, 200)).reshape(-1, 1)
    m2.open_world("net-gpt2")
    m2.discover(xw, 2.0 * xw[:, 0], name="carrier")
    m2.discover(xw, 3.0 * xw[:, 0], name="forced", container="side-room")
    m2.open_world("base")
    ok2 = (m2.net.get_meta("law:carrier", "container") == "net-gpt2"
           and m2.net.get_meta("law:forced", "container") == "side-room")
    check("B2 routing respected — open world captures, explicit "
          "container wins", ok2,
          f"carrier->{m2.net.get_meta('law:carrier', 'container')}, "
          f"forced->{m2.net.get_meta('law:forced', 'container')}")

    # B3 — the kindred pair crystallizes; the stranger joins nothing
    crys = mind.crystallize_forms()
    fams = crys["families"]
    kin = fams[0] if fams else dict(family="", members=[], containers=[])
    fam_node = kin.get("family", "")
    ok3 = (len(fams) == 1
           and kin["members"] == ["law:orbits-sol", "law:orbits-trappist"]
           and kin["containers"] == ["data-orbits-sol",
                                     "data-orbits-trappist"]
           and "variant" in mind.net.get_door_tags(fam_node,
                                                   "law:orbits-sol")
           and "variant" in mind.net.get_door_tags(fam_node,
                                                   "law:orbits-trappist")
           and (mind.net.get_meta("law:falling-bodies", "status")
                or {}).get("family") is None)
    check("B3 kindred pair -> one family; stranger excluded", ok3,
          f"{len(fams)} family(ies); members {kin['members']}")

    # B4 — never smushed
    a_fresh = np.linspace(1.0, 8.0, 50).reshape(-1, 1)
    e_sol = float(np.max(np.abs(
        mind.apply_law("orbits-sol", a_fresh) - 1.0 * a_fresh[:, 0] ** 1.5)
        / (1.0 * a_fresh[:, 0] ** 1.5)))
    e_tra = float(np.max(np.abs(
        mind.apply_law("orbits-trappist", a_fresh)
        - 4.9 * a_fresh[:, 0] ** 1.5) / (4.9 * a_fresh[:, 0] ** 1.5)))
    ok4 = (e_sol < 0.01 and e_tra < 0.01
           and mind.net.get_meta(fam_node, "model") is None)
    check("B4 never smushed — variants keep constants; parent holds "
          "form, not numbers", ok4,
          f"rel err {e_sol:.1e}/{e_tra:.1e}; parent model "
          f"{mind.net.get_meta(fam_node, 'model')}")

    # B5 — selection by container; refusal on superposition
    ax = np.sort(np.random.default_rng(7)
                 .uniform(1.0, 8.0, 60)).reshape(-1, 1)
    w_sol = mind.which_law(ax, 1.0 * ax[:, 0] ** 1.5)
    w_tra = mind.which_law(ax, 4.9 * ax[:, 0] ** 1.5)
    y_mix = np.where(np.arange(len(ax)) % 2 == 0,
                     1.0 * ax[:, 0] ** 1.5, 4.9 * ax[:, 0] ** 1.5)
    w_mix = mind.which_law(ax, y_mix)
    ok5 = (w_sol["verdict"] == "MATCH" and w_sol["law"] == "orbits-sol"
           and w_tra["verdict"] == "MATCH"
           and w_tra["law"] == "orbits-trappist"
           and w_mix["verdict"] != "MATCH")
    check("B5 selection by container — right law per world, refusal "
          "on the mix", ok5,
          f"sol->{w_sol['law']} tra->{w_tra['law']} "
          f"mix->{w_mix['verdict']}")

    # B6 — the null: scrambled assignment mints no family
    fresh = Isaac()
    _, X1, y1 = W[0]
    _, X2, y2 = W[1]
    Xp = np.concatenate([X1, X2]); yp = np.concatenate([y1, y2])
    perm = np.random.default_rng(1).permutation(len(yp))
    Xp, yp = Xp[perm], yp[perm]
    nh = len(yp) // 2
    r1 = fresh.discover(Xp[:nh], yp[:nh], name="pseudo1")
    r2 = fresh.discover(Xp[nh:], yp[nh:], name="pseudo2")
    crys_n = fresh.crystallize_forms()
    ok6 = (len(crys_n["families"]) == 0
           and len(crys_n["excluded"]) >= 2)
    check("B6 the null — scrambled worlds excluded by verdict, no "
          "family mints", ok6,
          f"verdicts {r1['verdict']}/{r2['verdict']}; families "
          f"{len(crys_n['families'])}, excluded "
          f"{len(crys_n['excluded'])}")

    # B7 — the wound closed: explains scoped to its world; base 0 drift
    after = {q: mind.ask(*q, container="base")["answers"]
             for q in BASE_QA}
    drift = sum(before[q] != after[q] for q in BASE_QA)
    in_world = mind.ask("law:orbits-sol", "explains",
                        container="data-orbits-sol")["answers"]
    ok7 = (drift == 0 and after[("law:orbits-sol", "explains")] == []
           and in_world == ["orbits-sol"])
    check("B7 the wound closed — explains lives in its world, base "
          "0 drift", ok7,
          f"drift {drift}/{len(BASE_QA)}; base sees "
          f"{after[('law:orbits-sol', 'explains')]}, world sees "
          f"{in_world}")

    # B8 — told and crystallized families unify on one node
    told = mind.tell_law("orbits-kepler62", "+2.50*x0^1.5", d=1)
    ok8 = (told["status"] == "VARIANT" and told["family"] == fam_node
           and "variant" in mind.net.get_door_tags(
               fam_node, "law:orbits-kepler62"))
    check("B8 told law joins the crystallized family — one node, all "
          "methods", ok8,
          f"told status {told['status']}, family {told.get('family')} "
          f"vs crystallized {fam_node}")

    # B9 — measured-jitter kinship on REAL sky data (NASA/JPL values)
    real = Isaac()
    REAL = dict(
        solar=([0.387, 0.723, 1.000, 1.524, 5.203, 9.537, 19.191,
                30.069],
               [0.2408, 0.6152, 1.0000, 1.8808, 11.862, 29.457,
                84.011, 164.79]),
        jupiter=([128.0, 181.4, 221.9, 421.8, 671.1, 1070.4, 1882.7,
                  11165.0, 11461.0, 11717.0, 11741.0],
                 [0.2948, 0.4982, 0.6745, 1.7691, 3.5512, 7.1546,
                  16.689, 240.92, 250.56, 259.20, 259.64]),
        saturn=([139.4, 141.7, 151.5, 185.5, 238.0, 294.7, 377.4,
                 527.1, 1221.9, 1481.0, 3560.8, 12947.8],
                [0.6127, 0.6285, 0.6950, 0.9424, 1.3702, 1.8878,
                 2.7369, 4.5175, 15.945, 21.277, 79.331, 550.56]))
    rr = np.random.default_rng(0)
    verds = []
    for nm, (xs, ys) in REAL.items():
        Xr = np.asarray(xs, float).reshape(-1, 1)
        yr = np.asarray(ys, float)
        ordr = rr.permutation(len(yr))
        verds.append(real.discover(Xr[ordr], yr[ordr],
                                   name=f"orbits-{nm}")["verdict"])
    crys_r = real.crystallize_forms()
    fam_r = crys_r["families"][0] if crys_r["families"] else \
        dict(members=[], containers=[])
    ok9 = (verds == ["UNDERSTOOD"] * 3
           and len(crys_r["families"]) == 1
           and len(fam_r["members"]) == 3
           and len(fam_r["containers"]) == 3)
    check("B9 measured-jitter kinship — real sky, one family, three "
          "variants", ok9,
          f"verdicts {verds}; families {len(crys_r['families'])}, "
          f"members {len(fam_r['members'])} across "
          f"{len(fam_r['containers'])} containers")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
