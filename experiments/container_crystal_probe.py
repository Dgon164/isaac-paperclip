"""container_crystal_probe.py — PER-DATASET CONTAINERS + CROSS-DOMAIN
CRYSTALLIZATION (owner, 2026-07-17, the feeding design: "what if we
had it so that each dataset is defaulted to its own container, and it
can crystalize the container structures into cross domain
structures").

RESEARCH, NOT THE ENGINE. Two shims over promoted organs prove the
design before any promotion:

  INTAKE STAMPING (DatasetIntake.feed): every dataset discovers under
  its OWN container (in:data-<source>), stamped automatically from
  source identity — provenance is measured, never designed. Base is
  never the default landing zone again. Promotion would move this
  inside discover()/tell_law/the session road.

  CROSS-DOMAIN CRYSTALLIZATION (crystallize_across): laws grouped by
  the engine's own coefficient-free form signature; a form spanning
  >=2 DISTINCT containers with genuinely different constants mints
  the lawform: parent (tell_law's VARIANT machinery pointed one level
  up — same crc32 naming, so told families and crystallized families
  UNIFY on the same node); same form + same constants across
  containers is recorded as a WITNESS (one law seen twice — the
  universality road, parked: promotion of a parent into BASE goes
  through the full court or not at all, and that court is not run
  here).

THE WORLD OF THE PROBE (Newton's actual move, replayed): Kepler's
third law discovered independently in two star systems — sol
(y = 1.0*a^1.5) and trappist (y = 4.9*a^1.5, heavier star) — plus one
stranger (falling bodies, y = 3.0*t^2). The kinship between the two
orbit datasets is REAL and the stranger's exclusion is the control.

THE MEASURED WOUND (the promotion case): discover()'s _teach_fact
indexes 'law:<n> explains <n>' with NO container tag, and ask()'s
base road answers container-less facts — so today every dataset
feeding leaks a fact into base. The shim stamps it; D8 measures the
raw road leaking on a fresh mind.

PREDICTIONS (filed before the first run; wrong ones kept)
  D1 STAMPED INTAKE: three datasets in, each law node carries exactly
     its own source's container stamp; none carries in:base.
  D2 THE KINDRED PAIR: crystallization mints exactly ONE lawform
     parent, spanning exactly {data-orbits-sol, data-orbits-trappist},
     variant doors on both member laws.
  D3 THE STRANGER EXCLUDED: falling-bodies joins no family.
  D4 NEVER SMUSHED: each variant keeps its own constants (each law
     predicts its OWN world's fresh rows; the parent node carries no
     model — no averaged constants exist anywhere).
  D5 SELECTION BY CONTAINER (the gauge's food — this is the >=2-laws
     milestone, research-side): which_law names sol on fresh sol
     rows, trappist on fresh trappist rows, and REFUSES on mixed rows
     (the mixed-planet precedent).
  D6 THE NULL: scrambled row->container assignment (pool sol+trappist,
     random split into two pseudo-datasets) mints NO distinct-constant
     family — the scrambled worlds are one world twice, and the
     machinery must say so (witness or refusal, either honest outcome
     passes; a variant family is the lie that must die).
  D7 BASE UNTOUCHED: base Q&A byte-identical across the entire
     feeding + crystallization; the laws' explains-facts are invisible
     under base and visible under their own containers.
  D8 THE WOUND, CLOSED (flipped at promotion — run 1 measured the
     raw road LEAKING, which was the promotion case; the engine now
     stamps at intake): a bare discover on a fresh mind lands its
     explains-fact in the dataset's own world, invisible under BASE;
     the minted parent carries no in:base stamp (base entry = the
     full court, required).

WRONG-KEPT (run 1, 6/8 — both cures are the probe's real findings):
  D6 FAILED AS WRITTEN: scrambled pseudo-worlds minted PARTIAL
  mixture-laws (different weighted-average constants) and the
  crystallizer let them family up. THE TOOTH, from admission
  discipline: ONLY LAWS THAT EARNED UNDERSTOOD IN THEIR OWN CONTAINER
  MAY CRYSTALLIZE — cross-domain kinship between two confusions is
  not knowledge. (Promotion reads the law's own certificate; the shim
  carries the verdict.) The null now kills the family exactly as the
  owner specified.
  D5 FAILED AS WRITTEN: the first mixed set gave sol the small-a rows
  and trappist the large-a rows — a RANGE-SEPARABLE mix, which the
  heavy end's law legitimately fits (kept: such a mix is honestly
  piecewise-answerable; the refusal test needs SUPERPOSITION).
  Interleaved mix now used.

PROMOTED same day: the shims moved into the engine (discover's
container= + per-dataset default, container-aware _teach_fact,
_install_law stamping, crystallize_forms with the tooth); the
permanent gate is container_crystal_battery.py. D8 flipped from
wound-measured to wound-closed at that moment — run 1's leak record
stands above as the why of the promotion.

Run: cd experiments && PYTHONHASHSEED=0 python container_crystal_probe.py
"""
import os
import sys
import time
import zlib

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import isaac as isaac_mod  # noqa: E402

Isaac = isaac_mod.Isaac


class DatasetIntake:
    """The candidate default: intake stamps the SOURCE's own container.
    Container = source identity (the dataset, the partner model, the
    decoded net) — never per-session, never a hand-filed subject."""

    def __init__(self, mind):
        self.m = mind
        self.stamps = {}                  # law node -> container
        self.verdicts = {}                # law node -> earned verdict

    def feed(self, source, X, y):
        c = f"data-{source}"
        prev = getattr(self.m, "active_container", "base")
        self.m.open_world(c)
        try:
            res = self.m.discover(X, y, name=source)
        finally:
            self.m.open_world(prev)
        node = f"law:{source}"
        if self.m.net.get_meta(node, "model") is not None:
            self.m.net.add_door(f"world:{c}", node, tag=f"in:{c}")
            self.m.net.set_meta(node, "container", c)
            # the wound's bandage: _teach_fact indexed the explains
            # fact with no container tag — stamp it into the source's
            # world so base's container-less road never answers it
            self.m.net.add_door(node, source, tag=f"in:{c}")
            self.stamps[node] = c
            self.verdicts[node] = res["verdict"]
        return res, c


def crystallize_across(mind, stamps, verdicts=None):
    """Cross-domain crystallization: group laws by the engine's own
    coefficient-free form signature; a form spanning >=2 distinct
    containers mints the lawform parent IF the constants genuinely
    differ (variants — container-dependent constants under one shared
    form); same constants across containers = a WITNESS record (one
    law, multiply confirmed — the universality road, parked). Family
    naming reuses tell_law's crc32 exactly, so told and crystallized
    families land on the SAME node.
    THE TOOTH (run-1 cure): only laws that EARNED UNDERSTOOD in their
    own container may crystallize — a PARTIAL law is a container's
    confusion, and kinship between confusions is not knowledge. This
    is what makes the scrambled-assignment null die: pseudo-worlds
    hold mixtures, mixtures never earn UNDERSTOOD, no family mints."""
    groups = {}
    excluded = []
    for node, c in stamps.items():
        m = mind.net.get_meta(node, "model")
        if not m:
            continue
        v = (verdicts or {}).get(node, "UNDERSTOOD")
        if v != "UNDERSTOOD":
            excluded.append(dict(node=node, container=c, verdict=v,
                                 why="not earned in its own container"))
            continue
        sig = Isaac._form_signature(m)
        groups.setdefault(sig, []).append((node, c))
    out = dict(families=[], witnesses=[], excluded=excluded)
    for sig, members in groups.items():
        containers = sorted({c for _, c in members})
        if len(members) < 2 or len(containers) < 2:
            continue
        models = [mind.net.get_meta(n, "model") for n, _ in members]
        if all(Isaac._coefs_match(models[0], m2) for m2 in models[1:]):
            out["witnesses"].append(dict(
                members=[n for n, _ in members], containers=containers,
                why="same form AND same constants across containers — "
                    "one law seen twice, never a family"))
            continue
        fam = f"lawform:{zlib.crc32(repr(sig).encode()):08x}"
        for node, _ in members:
            mind.net.add_door(fam, node, tag="variant")
            mind.net.meta[node].setdefault("status", {})["family"] = fam
        mind.record_finding("crossdomain_form", fam,
                            members=[n for n, _ in members],
                            containers=containers)
        out["families"].append(dict(family=fam,
                                    members=[n for n, _ in members],
                                    containers=containers))
    return out


def make_worlds(seed=0):
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

    # base, before any feeding — the answers that must not move
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

    # ── the feeding: three datasets, each into its own container ──
    intake = DatasetIntake(mind)
    worlds = make_worlds()
    results = {}
    for source, X, y in worlds:
        res, c = intake.feed(source, X, y)
        results[source] = res
        print(f"    fed {source} -> container '{c}': {res['verdict']}  "
              f"eq: {res['equation']}")

    # D1 — stamped intake, and never into base
    ok1, det1 = True, []
    for source, _, _ in worlds:
        node = f"law:{source}"
        c = f"data-{source}"
        tags = mind.net.get_door_tags(f"world:{c}", node)
        meta_c = mind.net.get_meta(node, "container")
        base_tags = mind.net.get_door_tags("world:base", node)
        good = (f"in:{c}" in tags and meta_c == c and not base_tags)
        ok1 &= good
        det1.append(f"{source}:{meta_c}{'' if good else '(BAD)'}")
    check("D1 stamped intake — each law wears its own container, "
          "none wear base", ok1, "; ".join(det1))

    # ── crystallization across containers ──
    crys = crystallize_across(mind, intake.stamps, intake.verdicts)
    fams = crys["families"]

    # D2 — the kindred pair
    kin = fams[0] if fams else dict(members=[], containers=[])
    ok2 = (len(fams) == 1
           and sorted(kin["members"]) == ["law:orbits-sol",
                                          "law:orbits-trappist"]
           and kin["containers"] == ["data-orbits-sol",
                                     "data-orbits-trappist"]
           and "variant" in mind.net.get_door_tags(kin.get("family", ""),
                                                   "law:orbits-sol")
           and "variant" in mind.net.get_door_tags(kin.get("family", ""),
                                                   "law:orbits-trappist"))
    check("D2 kindred pair crystallized — one family, exactly the two "
          "orbit worlds", ok2,
          f"{len(fams)} family(ies); members {kin['members']} across "
          f"{kin['containers']}")

    # D3 — the stranger excluded
    fb_fam = (mind.net.get_meta("law:falling-bodies", "status") or {}).get("family")
    ok3 = fb_fam is None and all(
        "law:falling-bodies" not in f["members"] for f in fams)
    check("D3 the stranger excluded — falling-bodies joins no family",
          ok3, f"family on falling-bodies: {fb_fam}")

    # D4 — never smushed: each variant keeps its own constants
    a_fresh = np.linspace(1.0, 8.0, 50).reshape(-1, 1)
    p_sol = mind.apply_law("orbits-sol", a_fresh)
    p_tra = mind.apply_law("orbits-trappist", a_fresh)
    tru_sol = 1.0 * a_fresh[:, 0] ** 1.5
    tru_tra = 4.9 * a_fresh[:, 0] ** 1.5
    err_sol = float(np.max(np.abs(p_sol - tru_sol) / tru_sol))
    err_tra = float(np.max(np.abs(p_tra - tru_tra) / tru_tra))
    fam_node = kin.get("family", "")
    parent_model = mind.net.get_meta(fam_node, "model") if fam_node else None
    ok4 = err_sol < 0.01 and err_tra < 0.01 and parent_model is None
    check("D4 never smushed — each variant keeps its constants; the "
          "parent holds form, not numbers", ok4,
          f"rel err sol {err_sol:.2e}, trappist {err_tra:.2e}; parent "
          f"model: {parent_model}")

    # D5 — selection by container (>=2 laws: the gauge's precondition)
    rng = np.random.default_rng(7)
    ax = np.sort(rng.uniform(1.0, 8.0, 60)).reshape(-1, 1)
    w_sol = mind.which_law(ax, 1.0 * ax[:, 0] ** 1.5)
    w_tra = mind.which_law(ax, 4.9 * ax[:, 0] ** 1.5)
    # superposition, not a range split (run-1 lesson): interleave the
    # two worlds across the whole range so no single law owns the mass
    y_mix = np.where(np.arange(len(ax)) % 2 == 0,
                     1.0 * ax[:, 0] ** 1.5, 4.9 * ax[:, 0] ** 1.5)
    w_mix = mind.which_law(ax, y_mix)
    ok5 = (w_sol["verdict"] == "MATCH" and w_sol["law"] == "orbits-sol"
           and w_tra["verdict"] == "MATCH"
           and w_tra["law"] == "orbits-trappist"
           and w_mix["verdict"] != "MATCH")
    check("D5 selection by container — right law per world, refusal on "
          "the mix", ok5,
          f"sol->{w_sol['law']} tra->{w_tra['law']} "
          f"mixed->{w_mix['verdict']}")

    # D6 — the null: scrambled assignment must mint no variant family
    fresh = Isaac()
    intake_n = DatasetIntake(fresh)
    _, X1, y1 = worlds[0]
    _, X2, y2 = worlds[1]
    Xp = np.concatenate([X1, X2]); yp = np.concatenate([y1, y2])
    perm = np.random.default_rng(1).permutation(len(yp))
    Xp, yp = Xp[perm], yp[perm]
    n_half = len(yp) // 2
    r_p1, _ = intake_n.feed("pseudo1", Xp[:n_half], yp[:n_half])
    r_p2, _ = intake_n.feed("pseudo2", Xp[n_half:], yp[n_half:])
    crys_n = crystallize_across(fresh, intake_n.stamps,
                                intake_n.verdicts)
    ok6 = len(crys_n["families"]) == 0
    check("D6 the null — scrambled worlds mint no cross-domain family",
          ok6,
          f"pseudo verdicts {r_p1['verdict']}/{r_p2['verdict']} "
          f"(eqs {r_p1['equation']} / {r_p2['equation']}); families "
          f"{len(crys_n['families'])}, witnesses "
          f"{len(crys_n['witnesses'])}, excluded-by-verdict "
          f"{len(crys_n['excluded'])}")

    # D7 — base untouched, explains-facts scoped to their worlds
    after = {q: mind.ask(*q, container="base")["answers"]
             for q in BASE_QA}
    drift = sum(before[q] != after[q] for q in BASE_QA)
    in_world = mind.ask("law:orbits-sol", "explains",
                        container="data-orbits-sol")["answers"]
    ok7 = (drift == 0 and after[("law:orbits-sol", "explains")] == []
           and in_world == ["orbits-sol"])
    check("D7 base untouched — 0 drift; explains-facts live in their "
          "own worlds, invisible under base", ok7,
          f"drift {drift}/{len(BASE_QA)}; base sees "
          f"{after[('law:orbits-sol', 'explains')]}, world sees "
          f"{in_world}")

    # D8 — the wound closed (engine stamps at intake) + base needs court
    raw = Isaac()
    raw.discover(worlds[0][1], worlds[0][2], name="orbits-sol")
    leak = raw.ask("law:orbits-sol", "explains", container="base")
    owned = raw.ask("law:orbits-sol", "explains",
                    container="data-orbits-sol")
    fam_base = mind.net.get_door_tags("world:base", fam_node) \
        if fam_node else set()
    ok8 = (not leak["answers"] and owned["answers"] == ["orbits-sol"]
           and not fam_base)
    check("D8 the wound, closed — bare intake lands in its own world, "
          "never base; parent holds no base stamp", ok8,
          f"base sees {leak['answers']}, world sees {owned['answers']}; "
          f"parent base tags: {sorted(fam_base)}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed of "
          f"{len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
