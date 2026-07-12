"""Mind crawlers — Prime federates (owner design, 2026-07-12).

Multiple orchestrators, each owning a KEY RANGE of the mind. When a
section outgrows its capacity, the crawler DIVIDES at its median key
and hands the upper half to a new crawler — the split is a journaled
event in the federation's own log (crawl.jsonl), so the lineage of
every division is wrong-kept and a cold start rebuilds the exact
range table.

Each crawler is a full Orchestrator: its pack index is its PAGE FILE
(key -> storage location), its lazy state does the DRIVE PULLS —
none of them ever needs its section in RAM, let alone the whole
mind. Requests between sections route through the range table;
admission travels with the section (each crawler keeps the gate).

Specialization is emergent: keys are namespaced (node:*, law:*,
skill:*, job:*), so range splits naturally give crawlers coherent
territories.
"""
import bisect
import json
import os

from .orchestrator import Orchestrator


class MindCrawlers:
    def __init__(self, directory, capacity=1000, admission=None):
        self.dir = directory
        self.capacity = capacity
        self.admission = admission
        os.makedirs(directory, exist_ok=True)
        self.log_path = os.path.join(directory, "crawl.jsonl")
        # ranges: sorted list of (lo_key, crawler_name); "" = root
        self.ranges = [("", "c0")]
        self._next_id = 1
        if os.path.exists(self.log_path):
            for line in open(self.log_path, encoding="utf-8"):
                ev = json.loads(line)
                if ev["event"] == "split":
                    bisect.insort(self.ranges, (ev["at"], ev["new"]))
                    self._next_id = max(self._next_id,
                                        int(ev["new"][1:]) + 1)
        self.crawlers = {}
        for _lo, name in self.ranges:
            self.crawlers[name] = Orchestrator(
                os.path.join(directory, name), admission=admission)

    # ---- routing: the federation's page file ------------------------
    def _owner(self, key):
        i = bisect.bisect_right(self.ranges, (str(key), "￿")) - 1
        return self.crawlers[self.ranges[i][1]]

    def submit(self, edit):
        self._owner(edit["key"]).submit(edit)

    def get(self, key):
        return self._owner(key).get(key)

    def keys(self, prefix=""):
        out = []
        for _lo, name in self.ranges:
            out.extend(k for k in self.crawlers[name].state
                       if str(k).startswith(prefix))
        return sorted(out)

    def process(self):
        """Drain every section's queue, then divide any section that
        outgrew its capacity (repeatedly, until all fit)."""
        admitted = rejected = 0
        for c in self.crawlers.values():
            a, r = c.process()
            admitted += a
            rejected += r
        for _ in range(10):  # cascaded splits settle quickly
            grew = False
            for lo, name in list(self.ranges):
                c = self.crawlers[name]
                if len(c.state) > self.capacity:
                    self._split(lo, name)
                    grew = True
            if not grew:
                break
        return admitted, rejected

    def compact(self, engine_version="unknown"):
        for c in self.crawlers.values():
            c.compact(engine_version=engine_version)

    def census(self):
        """The specialization map: who holds what, and how much."""
        out = {}
        for i, (lo, name) in enumerate(self.ranges):
            hi = self.ranges[i + 1][0] if i + 1 < len(self.ranges) else None
            out[name] = dict(lo=lo, hi=hi,
                             records=len(self.crawlers[name].state))
        return out

    # ---- division: the crawler that cannot keep up ------------------
    def _split(self, lo, name):
        old = self.crawlers[name]
        ks = sorted(str(k) for k in old.state)
        at = ks[len(ks) // 2]
        new_name = f"c{self._next_id}"
        self._next_id += 1
        new = Orchestrator(os.path.join(self.dir, new_name),
                           admission=self.admission)
        moved = 0
        for k in ks:
            if k >= at:
                new.submit({"op": "put", "key": k, "value": old.get(k),
                            "who": f"split:{name}"})
                old.submit({"op": "del", "key": k,
                            "who": f"split:{name}"})
                moved += 1
        new.process()
        old.process()
        new.compact(engine_version="split")
        old.compact(engine_version="split")
        self.crawlers[new_name] = new
        bisect.insort(self.ranges, (at, new_name))
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(event="split", parent=name, at=at,
                                    new=new_name, moved=moved)) + "\n")
