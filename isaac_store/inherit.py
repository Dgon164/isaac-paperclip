"""The First Teacher — a predecessor mind's net extracted into
TELLABLE material and fed to a fresh mind through the standard doors
(owner, 2026-07-17: "the alpha version needs to start from the start.
we can use the information it has already learned to see if it can
learn from developed sources and improve actual one shot through
direct telling or not, and give him a chance to process everything
one last time before he gets to work").

The rulings this module implements:
  - EXPERIENCE IS TOLD, BELIEF IS NOT: facts arrive via teach() with
    their world stamps preserved (fiction stays fiction — the wall);
    laws arrive via tell_law() and land TOLD-UNVERIFIED — usable at
    once (the one-shot road), carrying no belief until the
    successor's OWN data earns it. Wrong prologue entries fail
    revalidation naturally; nothing is trusted on provenance.
  - REFUSALS ARE LOUD AND COUNTED: a law outside the telling
    vocabulary (unparseable factor, learned lag/composite columns a
    fresh mind does not have) is refused WITH its why, never
    silently dropped. Complete numbers: extracted = told + witness
    + refused, per layer.
  - THE NET IS A BUILD ARTIFACT: what transfers is experience-as-
    telling; the capability (organs) is the engine's, not the
    net's. Organ-internal bookkeeping (law:/flow:/step:/quarantine:/
    inconsistency: subjects) is NOT experience and is not re-told —
    the fresh mind's organs write their own.
  - A HOME IS NEVER OVERWRITTEN: inherit_account() refuses an
    occupied destination. The prologue home is read, never touched.
"""
import json
import os
import shutil
import time

from . import bridge

_INTERNAL = ("law:", "flow:", "step:", "quarantine:",
             "inconsistency:", "lawform:", "tool:", "speech:")


def _world_of(mind, subject, obj):
    tags = mind.net.get_door_tags(str(subject), str(obj))
    for t in tags:
        if str(t).startswith("in:"):
            return str(t)[3:]
    return "base"


def extract_teachings(mind):
    """The prologue net -> tellable material: FACTS with their
    worlds, LAWS with their equations (Isaac's own canonical
    grammar — the same door a textbook would use). Returns the
    material plus complete counts of what was seen and skipped."""
    facts, skipped_internal = [], 0
    for key, objs in mind.fact_index.items():
        try:
            subject, relation = key
        except (TypeError, ValueError):
            skipped_internal += 1
            continue
        s, r = str(subject), str(relation)
        if s.startswith(_INTERNAL) or r.startswith(_INTERNAL):
            skipped_internal += 1
            continue
        for o in dict.fromkeys(str(x) for x in objs):
            facts.append(dict(subject=s, relation=r, obj=o,
                              world=_world_of(mind, s, o)))
    laws = []
    for node in list(mind.net.meta):
        n = str(node)
        if not n.startswith("law:") or n.startswith("lawform:"):
            continue
        model = mind.net.get_meta(n, "model")
        if not model:
            continue
        eq = mind.net.get_meta(n, "equation")
        if not eq:
            st = mind.net.get_meta(n, "status") or {}
            eq = st.get("equation")
        if not eq:
            continue
        laws.append(dict(
            name=n[4:], equation=str(eq),
            d=int(model.get("d_raw") or model.get("d") or 1),
            lags=bool(model.get("lags_used")),
            composites=bool(model.get("composites_used"))))
    return dict(facts=facts, laws=laws,
                counts=dict(facts=len(facts), laws=len(laws),
                            internal_skipped=skipped_internal))


def ingest_teachings(mind, teachings, source="prologue"):
    """Feed extracted material to a fresh mind through the standard
    doors. Facts: teach() with worlds preserved (in-world
    contradictions flag and keep, as always). Laws: tell_law() —
    TOLD-UNVERIFIED, MATCHES (a confirming witness), or VARIANT;
    out-of-vocabulary refused loudly with the why. The whole act is
    one provenance-stamped finding on the successor's record."""
    counts = dict(facts_extracted=len(teachings["facts"]),
                  facts_told=0, facts_refused=0,
                  laws_extracted=len(teachings["laws"]),
                  laws_told=0, laws_witness=0)
    facts_refused, laws_refused = [], []
    for f in teachings["facts"]:
        try:
            mind.teach(f["subject"], f["relation"], f["obj"],
                       container=f.get("world") or "base")
            counts["facts_told"] += 1
        except Exception as e:                  # malformed material
            counts["facts_refused"] += 1        # is counted, never
            facts_refused.append(dict(          # silently dropped
                fact=f, why=f"{type(e).__name__}: {e}"))
    for l in teachings["laws"]:
        if l.get("lags") or l.get("composites"):
            laws_refused.append(dict(
                name=l["name"],
                why="carries learned lag/composite columns a fresh "
                    "mind does not have — beyond the v1 telling "
                    "vocabulary; he can rediscover it from data"))
            continue
        try:
            got = mind.tell_law(l["name"], l["equation"], d=l["d"],
                                who=source)
            if got.get("status") == "TOLD-UNVERIFIED":
                counts["laws_told"] += 1
            else:                    # MATCHES / VARIANT: a witness
                counts["laws_witness"] += 1
        except ValueError as e:
            laws_refused.append(dict(name=l["name"], why=str(e)))
    mind.record_finding("inheritance", "launch", source=source,
                        **counts,
                        laws_refused=[r["name"] for r in laws_refused])
    return dict(counts=counts, facts_refused=facts_refused,
                laws_refused=laws_refused)


def inherit_account(old_home, new_home, mod=None, source=None):
    """THE LAUNCH (owner naming, 2026-07-17): a fresh account whose first experience is being
    taught by its predecessor. Reads the prologue home (never
    touches it), refuses an occupied destination (a home is never
    overwritten), carries the speech corpus as a file (the practice
    loop relearns from it on the standard road), and journals the
    launch as the permanent record's first entry."""
    mod = mod or bridge.load_isaac_module()
    new_mind_path = os.path.join(new_home, "mind.isaac")
    if os.path.exists(new_mind_path):
        raise RuntimeError(
            f"{new_home} already holds a mind — a home is never "
            f"overwritten; choose a fresh path")
    # the predecessor's LIVE state: packs are the account's storage
    # road since 2026-07-15 (the pickle is kept frozen, superseded)
    # — launching from the stale pickle would teach from a two-day-
    # old ghost (caught at the real launch's preflight, 2026-07-17)
    from .pack import latest_pack
    packs_dir = os.path.join(old_home, "packs")
    ver, ppath = latest_pack(packs_dir)
    old_mind_path = os.path.join(old_home, "mind.isaac")
    if ppath is not None:
        old = mod.Isaac.load_pack(packs_dir)
        source_road = f"packs v{ver} (the live road)"
    elif os.path.exists(old_mind_path):
        old = mod.Isaac.load(old_mind_path)
        source_road = "pickle (mind.isaac — no packs present)"
    else:
        raise RuntimeError(f"no predecessor mind in {old_home} "
                           f"(neither packs nor mind.isaac)")
    teachings = extract_teachings(old)
    fresh = mod.Isaac()
    rep = ingest_teachings(fresh, teachings,
                           source=source or old_home)
    rep["source_road"] = source_road
    # the registration rule at day one (owner, 2026-07-17: "we need
    # tools (controller nodes) and everything for information and
    # logic and decisions to flow through it"): the CURRENT engine
    # catalog seeds the tools node — fresher than inheriting the
    # prologue's (new organs join between lives); use/outcome
    # receipts start empty, measured on the road, never inherited
    rep["tools_cataloged"] = fresh.catalog_tools()
    os.makedirs(os.path.join(new_home, "transcripts"), exist_ok=True)
    old_corpus = os.path.join(old_home, "sparring_corpus.txt")
    if os.path.exists(old_corpus):
        shutil.copy2(old_corpus,
                     os.path.join(new_home, "sparring_corpus.txt"))
        rep["corpus_carried"] = True
    fresh.save(new_mind_path)
    entry = dict(kind="launch",
                 stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                 source=old_home, source_road=source_road,
                 counts=rep["counts"],
                 laws_refused=[r["name"] for r in rep["laws_refused"]],
                 note="day one: first experience = the predecessor's "
                      "net as direct telling; belief not inherited")
    with open(os.path.join(new_home, "practice_journal.jsonl"), "a",
              encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return rep
