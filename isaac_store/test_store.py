"""The Phase 1 battery. Settle by battery, not argument.

A. codec — nasty-structure round trip, loud failure on lambdas
B. journal — total order, watermark reads, truncated-tail tolerance
C. pack — index-only open, partial fetch, immutability, supersession
D. orchestrator — queue order, wrong-kept rejection, RECOVERY
   INVARIANT: latest pack + journal tail == live state (two roads,
   one state — the accounting law as a storage test)
E. real Isaac — teach + observe + discover a planted law, store ->
   rebuild -> identical answers AND identical re-extracted state
F. pickle migration — old save() file -> store -> same state
Run:  python test_store.py   (from isaac_store/'s parent)
"""
import json
import os
import shutil
import sys
import tempfile
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import codec, bridge
from isaac_store.codec import enc, dec, CodecError
from isaac_store.journal import Journal
from isaac_store.orchestrator import Orchestrator
from isaac_store.pack import PackReader, latest_pack, write_pack

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def canon(x):
    return json.dumps(enc(x), sort_keys=True)


def diff_records(a, b, label):
    """Per-record canonical compare (the record is the storage unit).
    Returns True if identical; prints the first few diffs otherwise."""
    same = set(a) == set(b)
    if not same:
        print(f"      {label}: record-name sets differ: "
              f"only-left={sorted(set(a) - set(b))[:5]} only-right={sorted(set(b) - set(a))[:5]}")
    diffs = [k for k in a if k in b and canon(a[k]) != canon(b[k])]
    for k in diffs[:3]:
        ca, cb = canon(a[k]), canon(b[k])
        pos = next((i for i, (x, y) in enumerate(zip(ca, cb)) if x != y), min(len(ca), len(cb)))
        print(f"      {label}: {k!r} differs at char {pos}:")
        print(f"        left : ...{ca[max(0, pos - 60):pos + 80]}...")
        print(f"        right: ...{cb[max(0, pos - 60):pos + 80]}...")
    return same and not diffs


def test_codec():
    print("A. codec")
    nasty = {
        ("tuple", "key"): {1, 2, frozenset({"a", ("b", 3)})},
        "arr": np.arange(6, dtype=np.float32).reshape(2, 3),
        "npv": np.float64(3.25),
        "dd": defaultdict(set, {("x", "y"): {"tag1", "tag2"}}),
        "nested": [({"k": b"bytes"},), None, True, 2.5],
    }
    rt = dec(json.loads(json.dumps(enc(nasty))))
    check("nasty round-trip equal", canon(rt) == canon(nasty))
    check("tuple key survives", ("tuple", "key") in rt)
    check("ndarray exact", np.array_equal(rt["arr"], nasty["arr"]) and rt["arr"].dtype == np.float32)
    check("defaultdict factory survives", isinstance(rt["dd"], defaultdict) and rt["dd"].default_factory is set)
    try:
        enc({"bad": lambda: 1})
        check("lambda refused loudly", False)
    except CodecError as e:
        check("lambda refused loudly", "$.['bad']" in str(e) or "bad" in str(e))


def test_journal(tmp):
    print("B. journal")
    path = os.path.join(tmp, "j.jsonl")
    j = Journal(path)
    seqs = [j.append({"n": i, "k": (i, "tup")}) for i in range(1, 51)]
    check("total order 1..50", seqs == list(range(1, 51)))
    tail = j.read_since(45)
    check("watermark read", [s for s, _ in tail] == [46, 47, 48, 49, 50]
          and tail[0][1]["k"] == (46, "tup"))
    with open(path, "a", encoding="utf-8") as f:
        f.write('{"seq": 51, "e": {"trunca')  # simulated crash mid-write
    j2 = Journal(path)
    check("truncated tail tolerated", j2.last_seq() == 50)
    check("append after crash continues order", j2.append({"n": 51}) == 51)


def test_pack(tmp):
    print("C. pack")
    d = os.path.join(tmp, "packs")
    records = {f"node:n{i}": {"doors": [f"n{i+1}"], "w": np.float64(i) / 7} for i in range(200)}
    write_pack(d, 1, records, meta={"watermark": 0})
    r = PackReader(os.path.join(d, "mind.v1.isaacpack"))
    check("index-only open sees all names", len(r.names()) == 200)
    one = r.get("node:n17")
    check("partial fetch (one record, no full load)",
          one["doors"] == ["n18"] and abs(one["w"] - 17 / 7) < 1e-12)
    check("full load equals source", canon(r.load_all()) == canon(records))
    try:
        write_pack(d, 1, records, meta={})
        check("immutability enforced", False)
    except FileExistsError:
        check("immutability enforced", True)
    records2 = dict(records, **{"node:new": {"doors": []}})
    write_pack(d, 2, records2, meta={"watermark": 9})
    v, p = latest_pack(d)
    check("supersession: v2 latest, v1 intact",
          v == 2 and os.path.exists(os.path.join(d, "mind.v1.isaacpack")))
    r.close()


def test_orchestrator(tmp):
    print("D. orchestrator")
    d = os.path.join(tmp, "orch")

    def gate(edit, state):
        if edit.get("why") == "bad":
            return False, "planted rejection: evidence below null"
        return True, "test gate"

    o = Orchestrator(d, admission=gate)
    for i in range(30):
        o.submit({"op": "put", "key": f"node:k{i}", "value": {"i": i}, "who": "w1"})
    o.submit({"op": "put", "key": "node:evil", "value": 1, "who": "w2", "why": "bad"})
    o.submit({"op": "inc", "key": "count:a", "value": 5, "who": "w3"})
    o.submit({"op": "inc", "key": "count:a", "value": 2, "who": "w4"})
    a, rej = o.process()
    check("admitted/rejected counts", a == 32 and rej == 1)
    check("rejected edit kept OUT of state", "node:evil" not in o.state)
    wrongs = [e for _s, e in o.journal.read_since(0) if e["verdict"] == "rejected"]
    check("rejection wrong-kept with why", len(wrongs) == 1
          and "null" in wrongs[0]["why"])
    check("commutative inc merged", o.state["count:a"] == 7)
    o.compact(engine_version="test")
    for i in range(5):  # post-compact edits live only in the journal tail
        o.submit({"op": "put", "key": f"node:tail{i}", "value": i, "who": "w1"})
    o.process()
    o2 = Orchestrator(d, admission=gate)  # cold start: pack + tail replay
    check("RECOVERY INVARIANT: pack + tail == live state",
          canon(dict(o2.state.items())) == canon(dict(o.state.items())),
          f"{len(o2.state)} records")


def build_mind(mod):
    i = mod.Isaac()
    i.teach("whale", "is_a", "mammal")
    i.teach("mammal", "has", "lungs")
    i.observe(mod.tokenize("the cat sat on the mat"))
    i.observe(mod.tokenize("the dog sat on the rug"))
    rng = np.random.default_rng(7)
    X = rng.uniform(-2, 2, size=(300, 2))
    y = 3.0 * X[:, 0] * X[:, 1] + X[:, 0] ** 2  # planted law
    i.discover(X, y, name="planted")
    return i, X


def probe(i, mod, X):
    """Behavior fingerprint: reasoning answer + law application."""
    out = {"lookup": repr(i.lookup(mod.tokenize("whale"))),
           "law": None}
    try:
        out["law"] = np.asarray(i.apply_law("planted", X[:20])).round(9).tolist()
    except Exception as e:
        out["law"] = f"apply_law raised: {e}"
    return out


def test_isaac_roundtrip(tmp, mod):
    print("E. real Isaac round-trip")
    i, X = build_mind(mod)
    before = probe(i, mod, X)
    records = bridge.extract(i)
    d = os.path.join(tmp, "mind_packs")
    write_pack(d, 1, records, meta={"watermark": 0})
    r = PackReader(os.path.join(d, "mind.v1.isaacpack"))
    i2 = bridge.rebuild(r.load_all(), mod)
    # state check FIRST — probing observes, and observation is logged
    re_extracted = bridge.extract(i2)
    check("re-extracted state identical (complete keep)",
          diff_records(records, re_extracted, "E"),
          f"{len(records)} records")
    after = probe(i2, mod, X)
    check("identical answers after round-trip", before == after,
          "lookup + apply_law on 20 rows")
    check("law survived (not an error)", "raised" not in str(after["law"]))
    node_names = [n for n in r.names() if n.startswith("node:")]
    if node_names:
        r2 = PackReader(os.path.join(d, "mind.v1.isaacpack"))
        rec = r2.get(node_names[0])
        check("partial load of one Isaac node", isinstance(rec, dict),
              f"{len(node_names)} node records, fetched {node_names[0]!r}")
        r2.close()
    else:
        check("partial load of one Isaac node", False, "no node records found")
    r.close()
    return i


def test_pickle_migration(tmp, mod, i):
    print("F. pickle migration")
    pkl = os.path.join(tmp, "old.isaac")
    i.save(pkl)
    old = mod.Isaac.load(pkl)
    check("old pickle still loads", isinstance(old, mod.Isaac))
    migrated = bridge.extract(old)
    direct = bridge.extract(i)
    check("migrated state == direct state", diff_records(direct, migrated, "F"))


def test_engine_native(tmp, mod, i):
    print("G. engine-native save_pack/load_pack")
    d = os.path.join(tmp, "native_packs")
    before = bridge.extract(i)
    p1 = i.save_pack(d)
    check("save_pack publishes v1", p1.endswith("mind.v1.isaacpack"))
    p2 = i.save_pack(d)
    check("save_pack again supersedes (v2, v1 intact)",
          p2.endswith("mind.v2.isaacpack") and os.path.exists(p1))
    i3 = mod.Isaac.load_pack(d)
    check("load_pack rebuilds identical state",
          diff_records(before, bridge.extract(i3), "G"))
    i4 = mod.Isaac.load_pack(d, version=1)
    check("named-version load works",
          diff_records(before, bridge.extract(i4), "G.v1"))


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_store_battery_")
    try:
        test_codec()
        test_journal(tmp)
        test_pack(tmp)
        test_orchestrator(tmp)
        print("  loading engine (isaac-paperclip/isaac.py)...")
        mod = bridge.load_isaac_module()
        i = test_isaac_roundtrip(tmp, mod)
        test_pickle_migration(tmp, mod, i)
        test_engine_native(tmp, mod, i)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
