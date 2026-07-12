"""Remote-worker battery — the whole client side over the doorway.

M1 RemoteCache.get over HTTP == Prime's state (codec wire, numpy)
M2 the delta recheck: only touched keys drop; untouched stay cached
M3 the 30-minute clock + job pinning, remote form (fake clock)
M4 auth: no token -> clean refusal; right token -> works
M5 a LEAF over the doorway: pulls and grafts from remote Prime,
   learns privately, and Prime's journal shows ZERO writes from it
M6 skills equip through the remote cache (same pull as any record)
M7 the recreation check works remotely (via /api/keys): user-told
   Kepler upgrades against Prime's public record across the wire
Run: python test_remote.py   (from isaac_store/)
"""
import os
import shutil
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.leaf import LeafIsaac
from isaac_store.remote import RemoteCache
from isaac_store.scrubber import scrub, seed_skill
from isaac_store.server import PrimeServer
from isaac_store.skills import publish_skill, pull_skill

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_remote_")
    server = tok_server = None
    t = [0.0]
    try:
        print("  loading engine + booting Prime...")
        mod = bridge.load_isaac_module()
        server = PrimeServer(os.path.join(tmp, "prime"))
        orch = server.orch
        kepler = mod.Isaac._parse_equation("+1.00*x0^1.5", 1)
        orch.submit({"op": "put", "key": "node:law:kepler_public",
                     "value": {"meta": {"model": kepler}, "public": True},
                     "who": "education"})
        orch.submit({"op": "put", "key": "node:mammal",
                     "value": {"doors": ["lungs"], "counts": {"lungs": 7},
                               "meta": {"n_obs": 40}}, "who": "education"})
        orch.process()
        publish_skill(orch, "scrubber", seed_skill())
        base = server.start()

        print("M1. remote reads are Prime's truth")
        rc = RemoteCache(base, clock=lambda: t[0])
        rec = rc.get("node:law:kepler_public")
        check("record over the wire, model intact",
              rec["public"] and rec["meta"]["model"]["d_raw"] == 1)
        check("a miss is None, not an error", rc.get("node:absent") is None)

        print("M2. the delta recheck")
        rc.get("node:mammal")
        orch.submit({"op": "put", "key": "node:mammal",
                     "value": {"doors": ["lungs", "fur"]}, "who": "edu"})
        orch.process()
        check("stale until recheck", rc.get("node:mammal")["doors"] == ["lungs"])
        f0 = rc.fetches
        rc.recheck()
        check("touched key refetched fresh",
              rc.get("node:mammal")["doors"] == ["lungs", "fur"])
        check("untouched key stayed cached",
              rc.get("node:law:kepler_public") is rec and
              rc.fetches == f0 + 1)

        print("M3. the 30-minute clock + pinning, remote")
        orch.submit({"op": "put", "key": "node:mammal",
                     "value": {"doors": ["lungs", "fur", "milk"]},
                     "who": "edu"})
        orch.process()
        r0 = rc.rechecks
        t[0] += 29 * 60
        rc.get("node:mammal")
        check("29 min: no recheck", rc.rechecks == r0)
        with rc.job():
            t[0] += 3 * 3600
            inside = rc.get("node:mammal")["doors"]
            check("pinned mid-job view holds", inside == ["lungs", "fur"])
        check("job end: deferred recheck ran, truth arrives",
              rc.rechecks == r0 + 1
              and rc.get("node:mammal")["doors"] == ["lungs", "fur", "milk"])

        print("M4. auth over the wire")
        tok_server = PrimeServer(os.path.join(tmp, "prime_tok"),
                                 token="s3cret")
        tok_base = tok_server.start()
        try:
            RemoteCache(tok_base)
            check("no token -> clean refusal", False)
        except RuntimeError as e:
            check("no token -> clean refusal", "401" in str(e))
        rc_tok = RemoteCache(tok_base, token="s3cret")
        check("right token -> works", rc_tok.watermark == 0)

        print("M5. a leaf across the wire")
        seq_before = orch.journal.last_seq()
        leaf = LeafIsaac(prime_url=base, mode="ephemeral", isaac_module=mod,
                         clock=lambda: t[0])
        tier = leaf.pull("mammal")
        check("pulled and grafted from REMOTE Prime",
              tier == "prime" and "lungs" in leaf.mind.net.doors["mammal"])
        leaf.mind.teach("whale", "is_a", "mammal")
        check("leaf learned privately; Prime journal shows ZERO writes",
              orch.journal.last_seq() == seq_before)

        print("M6. skills equip remotely")
        skill = pull_skill(leaf.prime, "scrubber")
        r = scrub({"note": "ssn 123-45-6789"}, vocabulary=skill)
        check("remote-pulled skill scrubs",
              r["ok"] and r["report"] == {"ssn": 1})

        print("M7. recreation check across the wire")
        leaf.leaf_tell("kepler_u", "+1.00*x0^1.5", d=1)  # user provenance
        banned, _, _ = leaf.exportable("law:kepler_u")
        rcheck = leaf.recreation_check("kepler_u")
        ok_now, _, tiers = leaf.exportable("law:kepler_u")
        check("banned until recreated", not banned)
        check("recreated from the remote public record",
              rcheck["recreated"]
              and rcheck["source"] == "node:law:kepler_public")
        check("export unlocked, provenance public",
              ok_now and tiers == {"public"})
        leaf.close()
    finally:
        if server:
            server.stop()
        if tok_server:
            tok_server.stop()
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
