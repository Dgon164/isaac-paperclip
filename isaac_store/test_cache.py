"""LiveCache battery.

H1 cache correctness — fetch once, serve from cache after
H2 recheck is a DELTA — only touched keys invalidated
H3 the 30-minute timer — no recheck before, recheck after (fake clock)
H4 pinned job — an overdue recheck WAITS until the job ends
H5 new pack adoption at recheck
H6 stale proposal caught at the admission gate (wrong-kept with why)
Run: python test_cache.py   (from isaac_store/)
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store.cache import LiveCache
from isaac_store.orchestrator import Orchestrator

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_cache_battery_")
    t = [0.0]  # fake clock, seconds
    try:
        d = os.path.join(tmp, "prime")
        orch = Orchestrator(d)
        for i in range(50):
            orch.submit({"op": "put", "key": f"node:n{i}", "value": {"i": i}, "who": "seed"})
        orch.process()
        orch.compact(engine_version="test")

        cache = LiveCache(os.path.join(d, "packs"),
                          os.path.join(d, "journal.jsonl"),
                          clock=lambda: t[0])

        print("H1. cache correctness")
        v1 = cache.get("node:n7")
        f_after_first = cache.fetches
        v2 = cache.get("node:n7")
        check("value correct", v1 == {"i": 7} and v2 == v1)
        check("second read served from cache (no new pack fetch)",
              cache.fetches == f_after_first)
        check("missing key -> None", cache.get("node:nope") is None)

        print("H2. recheck is a delta")
        cache.get("node:n8")
        orch.submit({"op": "put", "key": "node:n7", "value": {"i": 7, "rev": 2}, "who": "w2"})
        orch.process()
        check("stale until recheck (cached view stable)",
              cache.get("node:n7") == {"i": 7})
        cache.recheck()
        f_before = cache.fetches
        check("touched key updated after recheck",
              cache.get("node:n7") == {"i": 7, "rev": 2})
        check("untouched key NOT refetched",
              cache.get("node:n8") == {"i": 8} and cache.fetches == f_before)

        print("H3. the 30-minute timer")
        r0 = cache.rechecks
        orch.submit({"op": "put", "key": "node:n9", "value": {"i": 9, "rev": 2}, "who": "w2"})
        orch.process()
        t[0] += 29 * 60
        cache.get("node:n9")
        check("29 min: no recheck, still the pinned-era value",
              cache.rechecks == r0 and cache.get("node:n9") == {"i": 9})
        t[0] += 2 * 60
        got = cache.get("node:n9")
        check("31 min: recheck fired, fresh value",
              cache.rechecks == r0 + 1 and got == {"i": 9, "rev": 2})

        print("H4. pinned job")
        orch.submit({"op": "put", "key": "node:n10", "value": {"i": 10, "rev": 2}, "who": "w2"})
        orch.process()
        r1 = cache.rechecks
        with cache.job():
            t[0] += 3 * 3600  # recheck three hours overdue MID-JOB
            inside = cache.get("node:n10")
            inside_rechecks = cache.rechecks
        check("mid-job: overdue recheck deferred, view consistent",
              inside == {"i": 10} and inside_rechecks == r1)
        check("job end: the deferred recheck ran",
              cache.rechecks == r1 + 1 and cache.get("node:n10") == {"i": 10, "rev": 2})

        print("H5. new pack adoption")
        orch.submit({"op": "put", "key": "node:new_era", "value": {"born": "v2"}, "who": "w2"})
        orch.process()
        orch.compact(engine_version="test")
        t[0] += 31 * 60
        check("recheck adopts the new pack",
              cache.get("node:new_era") == {"born": "v2"} and cache.pack_version == 2)

        print("H6. staleness cannot corrupt — admission is the arbiter")

        def gate(edit, state):
            exp = edit.get("expect", ...)
            if exp is not ... and state.get(edit["key"]) != exp:
                return False, "based on superseded evidence (expect != current)"
            return True, "current"

        orch2 = Orchestrator(os.path.join(tmp, "prime2"), admission=gate)
        orch2.submit({"op": "put", "key": "node:x", "value": 1, "who": "seed"})
        orch2.process()
        stale_view = orch2.get("node:x")          # worker reads: 1
        orch2.submit({"op": "put", "key": "node:x", "value": 2, "who": "other",
                      "expect": 1})
        orch2.process()                            # someone else updates first
        orch2.submit({"op": "put", "key": "node:x", "value": 99, "who": "stale_worker",
                      "expect": stale_view})       # proposal from the stale read
        a, r = orch2.process()
        wrongs = [e for _s, e in orch2.journal.read_since(0) if e["verdict"] == "rejected"]
        check("stale proposal rejected at the gate",
              r == 1 and orch2.get("node:x") == 2)
        check("rejection wrong-kept with its why",
              len(wrongs) == 1 and "superseded" in wrongs[0]["why"])

        cache.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
