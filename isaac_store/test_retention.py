"""Restore-point cache battery (owner, 2026-07-12: 3 supersession
layers by default, or a full log; restore is an append, never a
rewrite).

N1 default keeps exactly 3 snapshots — older ones pruned
N2 the journal is trimmed to the kept span (and the RECOVERY
   INVARIANT still holds on the trimmed journal)
N3 full-log mode prunes NOTHING (all packs, journal from seq 1)
N4 restore: rewind to a kept snapshot; the rewind is a journaled
   event; cold-start after a restore replays to the restored state
N5 the storage numbers: supersession mode vs full log, measured
N6 retention prunes are ops-ledger events (content-free)
Run: python test_retention.py   (from isaac_store/)
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store.ops import OpsLedger
from isaac_store.orchestrator import Orchestrator

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def grow(orch, gen, n=40):
    for i in range(n):
        orch.submit({"op": "put", "key": f"node:g{gen}_{i}",
                     "value": {"gen": gen, "i": i, "blob": "x" * 200},
                     "who": "w"})
    orch.process()
    orch.compact()


def packs_on_disk(d):
    p = os.path.join(d, "packs")
    return sorted(int(n[len("mind.v"):-len(".isaacpack")])
                  for n in os.listdir(p) if n.endswith(".isaacpack"))


def dir_bytes(d):
    total = 0
    for dp, _dn, fn in os.walk(d):
        for f in fn:
            total += os.path.getsize(os.path.join(dp, f))
    return total


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_retention_")
    try:
        print("N1. default: exactly 3 supersession layers")
        d3 = os.path.join(tmp, "keep3")
        o = Orchestrator(d3)  # default retention_keep=3
        for g in range(6):
            grow(o, g)
        check("6 compactions -> packs v4,v5,v6 only",
              packs_on_disk(d3) == [4, 5, 6])

        print("N2. journal trimmed, recovery invariant intact")
        first_seq = o.journal.read_since(0)[0][0]
        check("events before the oldest kept snapshot are gone",
              first_seq > 1, f"journal now starts at seq {first_seq}")
        o.submit({"op": "put", "key": "node:tail", "value": 1, "who": "w"})
        o.process()  # a post-compact tail event
        o2 = Orchestrator(d3)
        check("cold start == live state on the TRIMMED journal",
              dict(o2.state.items()) == dict(o.state.items()),
              f"{len(o2.state)} records")

        print("N3. full-log mode prunes nothing")
        dF = os.path.join(tmp, "full")
        f = Orchestrator(dF, retention_keep=None)
        for g in range(6):
            grow(f, g)
        check("all 6 packs kept", packs_on_disk(dF) == [1, 2, 3, 4, 5, 6])
        check("journal intact from seq 1",
              f.journal.read_since(0)[0][0] == 1)

        print("N4. restore is an append, never a rewrite")
        before_restore_seq = o.journal.last_seq()
        n_restored = o.restore(5)  # rewind to snapshot v5
        check("state rewound to the v5 restore point",
              "node:g5_0" not in o.state and "node:g4_0" in o.state,
              f"{n_restored} records")
        ev = o.journal.read_since(before_restore_seq)
        check("the rewind itself is a journaled event",
              len(ev) == 1 and ev[0][1]["edit"]["op"] == "restore")
        o3 = Orchestrator(d3)
        check("cold start replays THROUGH the restore correctly",
              dict(o3.state.items()) == dict(o.state.items()))

        print("N5. the storage numbers")
        b3, bF = dir_bytes(d3), dir_bytes(dF)
        check("supersession mode is measurably smaller", b3 < bF,
              f"keep-3: {b3/1e3:.0f} KB vs full log: {bF/1e3:.0f} KB")

        print("N6. prunes are ops events")
        events = [e for e in OpsLedger(os.path.join(d3, "ops.jsonl")).read()
                  if e["kind"] == "retention"]
        check("retention events with counts only",
              len(events) >= 3 and events[-1]["kept"] == 3
              and all("pruned_packs" in e and "trimmed_events" in e
                      for e in events))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
