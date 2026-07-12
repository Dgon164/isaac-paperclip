"""Education battery — permanent memory at Prime scale, the missing
proof before learning experiments (owner question, 2026-07-12).

D1 a WHOLE real mind is educated into Prime (every record through
   the queue), compacted, and Prime's cold start opens the pack
   INDEX ONLY — no full load, ever (lazy Prime)
D2 partial recall: one node of the mind fetched alone from the
   cold-started Prime
D3 the mind rebuilt FROM PRIME answers identically (laws + facts)
D4 SESSION TWO: new knowledge learned elsewhere joins the same
   Prime; a third cold start holds BOTH the old and the new —
   permanent memory across sessions, superseding nothing
D5 the compression dividend, measured: compressed pack vs the same
   records uncompressed
D6 cold-start speed at 20k records: index-only open must be far
   under a full read (the Prime-bigger-than-RAM property, timed)
Run: python test_education.py   (from isaac_store/)
"""
import os
import shutil
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.orchestrator import Orchestrator
from isaac_store.pack import PackReader, write_pack

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def educate(orch, records, who):
    for k, v in records.items():
        orch.submit({"op": "put", "key": k, "value": v, "who": who})
    return orch.process()


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_edu_")
    try:
        print("  loading engine...")
        mod = bridge.load_isaac_module()
        rng = np.random.default_rng(83)

        print("D1. a whole mind educated into Prime")
        mind = mod.Isaac()
        mind.teach("whale", "is_a", "mammal")
        X = rng.uniform(-2, 2, (300, 2))
        y = 2.0 * X[:, 0] * X[:, 1] + X[:, 0] ** 2
        mind.discover(X, y, name="pairs")
        records = bridge.extract(mind)
        d = os.path.join(tmp, "prime")
        orch = Orchestrator(d)
        a, r = educate(orch, records, "education_worker")
        orch.compact(engine_version="education")
        check("every record admitted through the queue",
              a == len(records) and r == 0, f"{a} records")
        orch2 = Orchestrator(d)  # cold start
        check("cold start is LAZY: base reader open, overlay empty",
              orch2.state.reader is not None
              and len(orch2.state.over) == 0)

        print("D2. partial recall from the cold Prime")
        one = orch2.get("node:whale")
        check("a single node of the mind, fetched alone",
              one is not None and "doors" in one)

        print("D3. the mind rebuilt FROM PRIME answers identically")
        rebuilt = bridge.rebuild(dict(orch2.state.items()), mod)
        p1 = mind.apply_law("pairs", X[:50])
        p2 = rebuilt.apply_law("pairs", X[:50])
        check("law answers exact", p2 is not None and np.allclose(p1, p2))
        check("facts intact",
              rebuilt.fact_index[("whale", "is_a")] == ["mammal"])

        print("D4. session two: the mind GROWS in the same Prime")
        mind2 = bridge.rebuild(dict(orch2.state.items()), mod)
        y2 = np.sin(3.0 * X[:, 0]) + X[:, 1]
        mind2.discover(X, y2, name="waves")
        new_records = bridge.extract(mind2)
        delta = {k: v for k, v in new_records.items()
                 if k not in records or k.startswith(("sys:", "node:law"))}
        educate(orch2, delta, "education_worker_2")
        orch2.compact(engine_version="education-2")
        orch3 = Orchestrator(d)  # third cold start
        final = bridge.rebuild(dict(orch3.state.items()), mod)
        check("old knowledge still there",
              np.allclose(final.apply_law("pairs", X[:50]), p1)
              and final.fact_index[("whale", "is_a")] == ["mammal"])
        p3 = final.apply_law("waves", X[:50])
        check("new knowledge joined it",
              p3 is not None and
              float(np.corrcoef(p3, y2[:50])[0, 1]) > 0.999)

        print("D5. the compression dividend")
        dz = os.path.join(tmp, "z_on")
        du = os.path.join(tmp, "z_off")
        write_pack(dz, 1, records, meta={"watermark": 0})
        write_pack(du, 1, records, meta={"watermark": 0}, compress=False)
        bz = os.path.getsize(os.path.join(dz, "mind.v1.isaacpack"))
        bu = os.path.getsize(os.path.join(du, "mind.v1.isaacpack"))
        check("compressed pack measurably smaller, still seekable",
              bz < 0.6 * bu, f"{bz/1e3:.0f} KB vs {bu/1e3:.0f} KB "
              f"({bz/bu:.0%})")
        rz = PackReader(os.path.join(dz, "mind.v1.isaacpack"))
        check("single-record fetch from the compressed pack",
              rz.get("node:whale") is not None)
        rz.close()

        print("D6. cold start stays fast as the mind grows (20k records)")
        big = {f"node:n{i}": {"doors": [f"n{i+1}"], "w": float(i)}
               for i in range(20000)}
        db = os.path.join(tmp, "big")
        ob = Orchestrator(db)
        educate(ob, big, "bulk")
        ob.compact()
        t0 = time.perf_counter()
        ob2 = Orchestrator(db)
        t_open = time.perf_counter() - t0
        t0 = time.perf_counter()
        _ = ob2.get("node:n19999")
        t_get = time.perf_counter() - t0
        t0 = time.perf_counter()
        _ = dict(ob2.state.items())
        t_full = time.perf_counter() - t0
        check("index-only cold start far under a full read",
              t_open < t_full / 3,
              f"open {t_open*1000:.0f} ms, one node {t_get*1000:.2f} ms, "
              f"full read {t_full*1000:.0f} ms")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
