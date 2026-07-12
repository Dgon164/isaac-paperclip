"""Mind-crawlers battery — division under load, nothing lost.

G1 one crawler until capacity; overflow -> it DIVIDES (ranges
   partition, every key still routable)
G2 sustained growth -> repeated divisions; the census maps the
   sections; ZERO records lost (complete count + spot values)
G3 specialization is emergent: namespaced keys land in coherent
   territories (law:* held by at most 2 crawlers)
G4 cold start: the split log rebuilds the exact federation; every
   record identical (the recovery invariant, federated)
G5 every crawler is lazy after compaction (page file + drive pulls:
   base readers open, overlays empty)
G6 the division lineage is wrong-kept (parent, boundary, counts in
   crawl.jsonl)
G7 admission travels with the section (a gated edit dies in ITS
   crawler's journal)
Run: python test_crawlers.py   (from isaac_store/)
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store.crawlers import MindCrawlers

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_crawl_")
    try:
        d = os.path.join(tmp, "prime")
        mc = MindCrawlers(d, capacity=300)

        print("G1. overflow divides")
        for i in range(200):
            mc.submit({"op": "put", "key": f"node:a{i:04d}",
                       "value": {"i": i}, "who": "w"})
        mc.process()
        check("under capacity: one crawler", len(mc.ranges) == 1)
        for i in range(200):
            mc.submit({"op": "put", "key": f"node:b{i:04d}",
                       "value": {"i": i}, "who": "w"})
        mc.process()
        check("overflow: the section divided", len(mc.ranges) == 2,
              str([r[1] for r in mc.ranges]))
        check("every key still routable",
              mc.get("node:a0007") == {"i": 7}
              and mc.get("node:b0199") == {"i": 199})

        print("G2. sustained growth, zero loss")
        for i in range(600):
            mc.submit({"op": "put", "key": f"law:l{i:04d}",
                       "value": {"eq": f"x^{i}"}, "who": "w"})
        for i in range(400):
            mc.submit({"op": "put", "key": f"skill:s{i:04d}",
                       "value": {"v": i}, "who": "w"})
        mc.process()
        census = mc.census()
        total = sum(c["records"] for c in census.values())
        check("repeated divisions under load", len(mc.ranges) >= 4,
              f"{len(mc.ranges)} sections")
        check("ZERO records lost (complete count)", total == 1400,
              f"{total}/1400")
        check("spot values exact across sections",
              mc.get("law:l0555") == {"eq": "x^555"}
              and mc.get("skill:s0399") == {"v": 399}
              and mc.get("node:a0000") == {"i": 0})

        print("G3. specialization is emergent")
        order = [name for _lo, name in mc.ranges]
        law_pos = [i for i, name in enumerate(order)
                   if any(str(k).startswith("law:")
                          for k in mc.crawlers[name].state)]
        check("law:* is a CONTIGUOUS territory (adjacent sections)",
              law_pos == list(range(law_pos[0], law_pos[-1] + 1)),
              f"sections {[order[i] for i in law_pos]}")

        print("G4. cold start rebuilds the federation")
        mc.compact()
        mc2 = MindCrawlers(d, capacity=300)
        check("range table rebuilt from the split log",
              mc2.ranges == mc.ranges)
        same = all(mc2.get(k) == mc.get(k)
                   for k in ["node:a0007", "node:b0199", "law:l0555",
                             "skill:s0399", "law:l0000"])
        total2 = sum(c["records"] for c in mc2.census().values())
        check("every record identical after cold start",
              same and total2 == 1400)

        print("G5. page file + drive pulls in every section")
        lazy = all(c.state.reader is not None and len(c.state.over) == 0
                   for c in mc2.crawlers.values())
        check("all crawlers lazy after compaction", lazy,
              f"{len(mc2.crawlers)} crawlers")

        print("G6. the division lineage is wrong-kept")
        evs = [json.loads(ln) for ln in open(os.path.join(d, "crawl.jsonl"),
                                             encoding="utf-8")]
        check("every split logged with parent/boundary/counts",
              len(evs) == len(mc.ranges) - 1
              and all(e["event"] == "split" and "at" in e
                      and e["moved"] > 0 for e in evs))

        print("G7. admission travels with the section")
        def gate(edit, state):
            if edit.get("why") == "bad":
                return False, "gated in this section"
            return True, "ok"
        d2 = os.path.join(tmp, "gated")
        mg = MindCrawlers(d2, capacity=10, admission=gate)
        for i in range(15):
            mg.submit({"op": "put", "key": f"k{i:02d}", "value": i,
                       "who": "w"})
        mg.process()  # forces a split; gate must survive it
        mg.submit({"op": "put", "key": "k14", "value": 99, "who": "w",
                   "why": "bad"})
        a, r = mg.process()
        owner = mg._owner("k14")
        wrongs = [e for _s, e in owner.journal.read_since(0)
                  if e["verdict"] == "rejected"]
        check("gated edit died in ITS OWN crawler's journal",
              r == 1 and len(wrongs) >= 1 and mg.get("k14") != 99)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
