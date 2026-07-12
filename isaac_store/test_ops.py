"""Ops battery — system/operational management, content-free by law.

O1 the ledger REFUSES content at write time (long strings, objects)
O2 orchestrator operations self-report: process + compact events with
   counts, sizes, timings
O3 THE LEAK-CHANNEL PROOF: drive Prime over HTTP with identity-bearing
   requests (PII in keys, values, queries) -> ops.jsonl + server log
   carry paths/statuses/timings ONLY; byte-scan finds zero PII
O4 the alpha launcher: boots from empty (seeds the scrubber skill),
   serves, persists, and resumes across a restart
Run: python test_ops.py   (from isaac_store/)
"""
import json
import os
import shutil
import sys
import tempfile
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store.ops import OpsLedger
from isaac_store.orchestrator import Orchestrator

PASS = FAIL = 0
PII = "carol.d@example-bank.com"


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def get(base, path, body=None):
    req = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode() if body is not None else None,
        method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_ops_")
    try:
        print("O1. the ledger refuses content")
        led = OpsLedger(os.path.join(tmp, "solo_ops.jsonl"))
        led.event("test", n=3, ms=1.25, path="/api/record")
        try:
            led.event("bad", note="x" * 200)
            check("long string refused", False)
        except ValueError as e:
            check("long string refused", "content-free" in str(e))
        try:
            led.event("bad", value={"a": 1})
            check("structured value refused", False)
        except ValueError as e:
            check("structured value refused", "content-free" in str(e))

        print("O2. operations self-report")
        d = os.path.join(tmp, "prime")
        orch = Orchestrator(d)
        for i in range(5):
            orch.submit({"op": "put", "key": f"node:n{i}", "value": {"i": i},
                         "who": "w1"})
        orch.process()
        orch.compact(engine_version="ops-battery")
        kinds = [e["kind"] for e in orch.ops.read()]
        proc = [e for e in orch.ops.read() if e["kind"] == "process"][0]
        comp = [e for e in orch.ops.read() if e["kind"] == "compact"][0]
        check("process event: counts + ms",
              proc["admitted"] == 5 and proc["rejected"] == 0 and proc["ms"] >= 0)
        check("compact event: version/records/bytes/ms",
              comp["version"] == 1 and comp["records"] == 5 and comp["bytes"] > 0)

        print("O3. the leak-channel proof")
        from isaac_store.scrubber import identity_gate
        from isaac_store.server import PrimeServer
        sd = os.path.join(tmp, "prime_http")
        server = PrimeServer(sd, admission=identity_gate())
        base = server.start()
        get(base, f"/api/record?key=node:{PII}")             # PII in a query
        get(base, "/api/submit", {"op": "put", "key": "node:x",
                                  "value": f"call {PII} re: account",
                                  "who": "rogue"})           # PII in a value
        get(base, "/api/watermark")
        server.stop()
        ops_path = os.path.join(sd, "ops.jsonl")
        blob = open(ops_path, "rb").read()
        check("ops events exist for every request",
              sum(1 for e in OpsLedger(ops_path).read() if e["kind"] == "http") == 3)
        check("zero PII bytes in the ops ledger", PII.encode() not in blob)
        check("no query strings in ops paths",
              b"?" not in blob and b"key=" not in blob)
        jblob = open(os.path.join(sd, "journal.jsonl"), "rb").read()
        check("journal also clean (Identity Law redaction)",
              PII.encode() not in jblob)

        print("O4. the alpha launcher")
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import alpha
        ad = os.path.join(tmp, "alpha_data")
        s1 = alpha.launch(ad, port=0)
        b1 = s1.start()
        code, w = get(b1, "/api/watermark")
        check("boots from empty and serves", code == 200 and w["ok"])
        code, r = get(b1, "/api/record?key=skill:scrubber")
        check("first boot educated Prime with the scrubber skill",
              r["ok"] is True)
        s1.orch.compact(engine_version="test-shutdown")
        v1 = s1.orch.pack_version
        s1.stop()
        s2 = alpha.launch(ad, port=0)   # restart on the same data
        check("state survives restart (recovery invariant)",
              s2.orch.pack_version == v1
              and s2.orch.get("skill:scrubber") is not None)
        check("restart did NOT re-seed (education not repeated)",
              sum(1 for _s, e in s2.orch.journal.read_since(0)
                  if e.get("edit", {}).get("key") == "skill:scrubber") == 1)
        s2.stop()
        try:
            alpha.launch(ad, host="0.0.0.0", port=0)
            check("non-localhost bind without token REFUSED", False)
        except SystemExit as e:
            check("non-localhost bind without token REFUSED",
                  "token" in str(e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
