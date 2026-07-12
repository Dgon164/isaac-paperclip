"""The learning battery — Isaac LEARNS through the new system, end
to end. This is the owner's architecture doing its actual job:

  worker1 (leaf, private data)  --discovers a law-->
  scrubber (strips identity)    --clean abstraction-->
  Prime's orchestrator (identity gate + admission) --journal/pack-->
  worker2 (different worker, LiveCache) --pulls ONE record-->
  a fresh Isaac APPLIES the law correctly.

Knowledge crossed the whole system; the private data never did.

E2E-1 worker1 discovers the planted law from private data
E2E-2 the raw (dirty) share is REFUSED at Prime's gate
E2E-3 scrubbed share admitted; law survives byte-exact; PII counts
      stripped; Prime's files contain zero private bytes
E2E-4 worker2 pulls one record cold and applies the law: predictions
      match worker1's within float noise, truth within model error
E2E-5 the quarantine held END TO END (byte-scan of Prime + journal)
Run: python test_learning.py   (from isaac_store/)
"""
import json
import os
import shutil
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.cache import LiveCache
from isaac_store.leaf import LeafIsaac
from isaac_store.orchestrator import Orchestrator
from isaac_store.scrubber import identity_gate, scrub

PASS = FAIL = 0
PII = "billing-alice.w@example-corp.com"


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def files_containing(root, needle):
    hits = []
    nb = needle.encode()
    for dirpath, _d, names in os.walk(root):
        for name in names:
            try:
                with open(os.path.join(dirpath, name), "rb") as f:
                    if nb in f.read():
                        hits.append(os.path.join(dirpath, name))
            except OSError:
                pass
    return hits


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_learning_")
    try:
        print("  loading engine...")
        mod = bridge.load_isaac_module()
        prime_dir = os.path.join(tmp, "prime")
        Orchestrator(prime_dir).compact()  # Prime exists, empty

        print("E2E-1. worker1 learns from private data")
        w1 = LeafIsaac(prime_dir, mode="ephemeral", isaac_module=mod)
        w1.mind.teach(PII, "owns", "dataset_7")  # private context
        rng = np.random.default_rng(3)
        X = rng.uniform(-2, 2, (400, 2))
        y = 3.0 * X[:, 0] * X[:, 1] + X[:, 0] ** 2
        w1.mind.discover(X, y, name="pairs")
        model = w1.mind.net.get_meta("law:pairs", "model")
        Xtest = rng.uniform(-2, 2, (50, 2))
        pred1 = w1.mind.apply_law("pairs", Xtest)
        check("law discovered from private-context data",
              model is not None and pred1 is not None
              and float(np.corrcoef(pred1, 3 * Xtest[:, 0] * Xtest[:, 1]
                                    + Xtest[:, 0] ** 2)[0, 1]) > 0.999)

        # the share: the law node's meta + a sloppy human note with PII
        share = {"meta": {"model": model},
                 "note": f"found while processing {PII} account data"}

        print("E2E-2. the dirty share dies at Prime's gate")
        orch = Orchestrator(prime_dir, admission=identity_gate())
        orch.submit({"op": "put", "key": "node:law:pairs", "value": share,
                     "who": "worker1"})
        a, r = orch.process()
        check("unscrubbed share REFUSED (Identity Law)", a == 0 and r == 1)

        print("E2E-3. scrubbed share admitted")
        result = scrub(share)
        check("scrubber found exactly the email",
              result["ok"] and result["report"] == {"email": 1})
        check("the LAW inside is byte-exact after scrubbing",
              json.dumps(str(result["clean"]["meta"]["model"]))
              == json.dumps(str(model)))
        orch.submit({"op": "put", "key": "node:law:pairs",
                     "value": result["clean"], "who": "scrubber1",
                     "scrub_report": result["report"]})
        a, r = orch.process()
        orch.compact(engine_version="learning-battery")
        check("clean share admitted + packed", a == 1 and r == 0)

        print("E2E-4. worker2 pulls one record cold and USES the law")
        cache = LiveCache(os.path.join(prime_dir, "packs"),
                          os.path.join(prime_dir, "journal.jsonl"))
        rec = cache.get("node:law:pairs")
        w2 = mod.Isaac()  # a different, fresh mind
        w2.net.set_meta("law:pairs", "model", rec["meta"]["model"])
        pred2 = w2.apply_law("pairs", Xtest)
        truth = 3 * Xtest[:, 0] * Xtest[:, 1] + Xtest[:, 0] ** 2
        check("worker2's predictions == worker1's (exact transfer)",
              pred2 is not None and np.allclose(pred1, pred2))
        check("worker2 predicts TRUTH on fresh inputs",
              float(np.corrcoef(pred2, truth)[0, 1]) > 0.999,
              f"corr {np.corrcoef(pred2, truth)[0, 1]:.6f}")
        cache.close()

        print("E2E-5. the quarantine held end to end")
        hits = files_containing(tmp, PII)
        check("zero private bytes anywhere on disk", hits == [],
              "scanned Prime packs + journal + everything")
        note = cache._overlay.get("node:law:pairs", rec)["note"] if False else rec["note"]
        check("even the human note crossed clean", "[email]" in note and PII not in note)
        w1.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
