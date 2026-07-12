"""worker.py — a Worker: a separate OS process that pulls jobs from
Prime over the doorway, computes with the engine on its own core, and
routes results back through the orchestrator's queue.

This is the multicore model (owner design): Prime's write path stays
a single writer (edits are milliseconds); the COMPUTE — discovery,
perception, batch — fans out across worker processes. Workers claim
jobs optimistically ("expect": the open record); queue order
arbitrates races, so a job runs exactly once with no locks anywhere.

  python worker.py --prime http://127.0.0.1:8675 --who w1 --jobs 8 --drain

Job records: job:<k> = {"kind": "discover", "seed", "rows", "a", "b",
"status": open|claimed|done}. Results: node:law:<k> = {"model": ...}.
"""
import argparse
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from isaac_store import bridge          # noqa: E402
from isaac_store.codec import dec, enc  # noqa: E402


def call(base, path, body=None, encoded=False):
    data = None
    if body is not None:
        data = json.dumps({"_encoded": enc(body)} if encoded else body).encode()
    req = urllib.request.Request(base + path, data=data,
                                 method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def run_job(mod, job):
    import numpy as np
    rng = np.random.default_rng(job["seed"])
    X = rng.uniform(-2, 2, (job["rows"], 2))
    y = job["a"] * X[:, 0] * X[:, 1] + job["b"] * X[:, 0] ** 2
    mind = mod.Isaac()
    mind.discover(X, y, name="job")
    return mind.net.get_meta("law:job", "model")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prime", required=True)
    p.add_argument("--who", required=True)
    p.add_argument("--jobs", type=int, required=True)
    p.add_argument("--drain", action="store_true")
    a = p.parse_args()
    mod = None
    done_by_me = 0
    while True:
        claimed = None
        for k in range(a.jobs):
            r = call(a.prime, f"/api/record?key=job:{k}")
            if not r.get("ok"):
                continue
            rec = dec(r["value"])
            if rec.get("status") != "open":
                continue
            claim = dict(rec, status="claimed", claimed_by=a.who)
            verdict = call(a.prime, "/api/submit",
                           {"op": "put", "key": f"job:{k}", "value": claim,
                            "who": a.who, "expect": rec})
            if verdict["ok"]:  # we won the race; a loss is normal, move on
                claimed = (k, claim)
                break
        if claimed is None:
            if a.drain:
                print(f"  [{a.who}] drained after {done_by_me} job(s)")
                return
            continue
        k, claim = claimed
        if mod is None:
            mod = bridge.load_isaac_module()  # engine loads once per worker
        model = run_job(mod, claim)
        call(a.prime, "/api/submit",
             {"op": "put", "key": f"node:law:{k}", "value": {"model": model},
              "who": a.who}, encoded=True)
        call(a.prime, "/api/submit",
             {"op": "put", "key": f"job:{k}",
              "value": dict(claim, status="done"), "who": a.who,
              "expect": claim})
        done_by_me += 1
        print(f"  [{a.who}] job:{k} done")


if __name__ == "__main__":
    main()
