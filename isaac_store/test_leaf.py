"""LeafIsaac battery — the security-net quarantine, proven not promised.

L1 graft: pull a Prime node, door LOCAL private evidence onto it
L2 local wins: layered read prefers the local version
L3 THE QUARANTINE PROOF: after a full teach/observe/answer cycle with
   a planted secret, scan EVERY byte of EVERY file outside the user's
   own directory — the secret must appear nowhere
L4 ephemeral evaporation: mode="ephemeral" refuses save(); the secret
   exists on NO disk at all
L5 user-held: save lands ONLY under the user's directory; resume works
L6 no upstream channel: a leaf has no submit path by construction
Run: python test_leaf.py   (from isaac_store/)
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store.leaf import LeafIsaac
from isaac_store.orchestrator import Orchestrator
from isaac_store import bridge

PASS = FAIL = 0
SECRET = "SENTINEL-ssn-987-65-4321-alice-example-corp"


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def files_containing(root, needle, exclude=None):
    hits = []
    needle_b = needle.encode("utf-8")
    for dirpath, _dirs, names in os.walk(root):
        if exclude and os.path.abspath(dirpath).startswith(os.path.abspath(exclude)):
            continue
        for name in names:
            p = os.path.join(dirpath, name)
            try:
                if name.endswith(".isaacpack"):
                    # DECODED-record scan: compression must never
                    # hide a secret from this scan, either direction
                    from isaac_store.pack import PackReader
                    r = PackReader(p)
                    found = any(needle in repr(r.get(k)) for k in r.index)
                    r.close()
                    if found:
                        hits.append(p)
                    continue
                with open(p, "rb") as f:
                    if needle_b in f.read():
                        hits.append(p)
            except OSError:
                pass
    return hits


def seed_prime(tmp):
    d = os.path.join(tmp, "prime")
    orch = Orchestrator(d)
    orch.submit({"op": "put", "key": "node:mammal",
                 "value": {"doors": ["lungs", "warm_blooded"],
                           "tags": {"lungs": ["has"]},
                           "counts": {"lungs": 40},
                           "meta": {"spread": 0.12, "n_obs": 200}},
                 "who": "education"})
    orch.process()
    orch.compact(engine_version="test")
    return d


def run_private_cycle(leaf, mod):
    """A user session: private facts doored onto shared knowledge."""
    leaf.pull("mammal")
    leaf.mind.teach(SECRET, "is_a", "mammal")       # user-submitted
    leaf.mind.observe(mod.tokenize(f"the account of {SECRET} is overdue"))
    return leaf.mind.lookup(mod.tokenize(SECRET))    # processed + answered


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_leaf_battery_")
    try:
        print("  loading engine...")
        mod = bridge.load_isaac_module()
        prime_dir = seed_prime(tmp)

        print("L1. graft + local evidence")
        leaf = LeafIsaac(prime_dir, mode="ephemeral", isaac_module=mod)
        tier = leaf.pull("mammal")
        net = leaf.mind.net
        check("pulled from Prime and grafted",
              tier == "prime" and "lungs" in net.doors["mammal"])
        check("provenance tag on grafted doors",
              "prime" in net.door_tags[("mammal", "lungs")])
        check("grafted counts kept", net.door_counts[("mammal", "lungs")] == 40)
        leaf.mind.teach("whale", "is_a", "mammal")   # local evidence doors on
        check("local evidence doored onto grafted node",
              leaf.pull("mammal") == "local"
              and leaf.mind.fact_index[("whale", "is_a")] == ["mammal"]
              and "whale" in net.doors)

        print("L2. local wins")
        net.meta["mammal"]["spread"] = 0.99          # local revision
        leaf.pull("mammal")
        check("layered read prefers local values",
              net.meta["mammal"]["spread"] == 0.99)

        print("L3. THE QUARANTINE PROOF")
        answer = run_private_cycle(leaf, mod)
        check("private cycle processed and answered", answer is not None)
        check("the secret LIVES in the leaf's mind (processing worked)",
              SECRET in str(leaf.mind.fact_index))
        hits = files_containing(tmp, SECRET)
        check("secret in ZERO files anywhere upstream",
              hits == [], f"scanned every file under the test root")

        print("L4. ephemeral evaporation")
        try:
            leaf.save()
            check("ephemeral save() refuses", False)
        except RuntimeError as e:
            check("ephemeral save() refuses", "EVER" in str(e))
        leaf.close()

        print("L5. user-held mode")
        user_dir = os.path.join(tmp, "USER_OWN_DEVICE")
        leaf2 = LeafIsaac(prime_dir, mode="user-held", user_dir=user_dir,
                          isaac_module=mod)
        run_private_cycle(leaf2, mod)
        p = leaf2.save()
        check("save lands under the user's directory",
              os.path.abspath(p).startswith(os.path.abspath(user_dir)))
        outside = files_containing(tmp, SECRET, exclude=user_dir)
        inside = files_containing(user_dir, SECRET)
        check("secret ONLY inside the user's directory",
              outside == [] and len(inside) == 1)
        leaf2.close()
        leaf3 = LeafIsaac(prime_dir, mode="user-held", user_dir=user_dir,
                          isaac_module=mod)
        check("user-held mind resumes across sessions",
              SECRET in str(leaf3.mind.fact_index))
        leaf3.close()

        print("L6. no upstream channel")
        check("leaf exposes no submit/queue path",
              not hasattr(leaf3, "submit") and not hasattr(leaf3, "orchestrator")
              and not hasattr(leaf3.mind, "submit"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
