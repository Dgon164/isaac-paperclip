"""PrimeServer battery — the between-programs doorway.

S1 watermark (the cheap recheck, over the wire)
S2 submit -> admitted -> record readable back
S3 rejected edit is HTTP 200 ok:false WITH its why (refusals are
   answers), and wrong-kept in the journal
S4 journal delta (?since=) — a remote worker's recheck
S5 a full remote-worker loop: pull, someone else writes, delta sees it
S6 malformed requests get clean 400 JSON, never a stack trace
S7 bearer token: 401 without, 200 with
S8 server binds localhost only by default
Run: python test_server.py   (from isaac_store/)
"""
import json
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store.codec import dec
from isaac_store.server import PrimeServer

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def call(base, path, body=None, token=None):
    req = urllib.request.Request(base + path,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 method="POST" if body is not None else "GET")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_server_battery_")
    server = tok_server = None
    try:
        def gate(edit, state):
            if edit.get("why") == "bad":
                return False, "planted rejection: evidence below null"
            return True, "gate ok"

        server = PrimeServer(os.path.join(tmp, "prime"), admission=gate)
        base = server.start()

        print("S1. watermark")
        code, w = call(base, "/api/watermark")
        check("watermark reachable", code == 200 and w["ok"] and w["last_seq"] == 0)

        print("S2. submit -> admitted -> read back")
        code, r = call(base, "/api/submit",
                       {"op": "put", "key": "node:law_of_pairs",
                        "value": {"eq": "3*x0*x1", "r2": 0.98}, "who": "worker_1"})
        check("edit admitted over the wire",
              code == 200 and r["ok"] and r["verdict"] == "admitted" and r["seq"] == 1)
        code, r = call(base, "/api/record?key=node:law_of_pairs")
        check("record readable back (codec wire format)",
              code == 200 and r["ok"] and dec(r["value"])["r2"] == 0.98)
        code, r = call(base, "/api/record?key=node:absent")
        check("missing record is an ANSWER (200 ok:false)",
              code == 200 and not r["ok"] and "no such record" in r["why"])

        print("S3. refusals are answers")
        code, r = call(base, "/api/submit",
                       {"op": "put", "key": "node:junk", "value": 1,
                        "who": "worker_2", "why": "bad"})
        check("rejection: HTTP 200, ok:false, why stated",
              code == 200 and not r["ok"] and r["verdict"] == "rejected"
              and "null" in r["why"])
        code, r = call(base, "/api/record?key=node:junk")
        check("rejected edit never entered state", not r["ok"])
        code, j = call(base, "/api/journal?since=0")
        rejected = [e for e in j["events"] if dec(e["e"])["verdict"] == "rejected"]
        check("rejection wrong-kept in the journal", len(rejected) == 1)

        print("S4. journal delta")
        code, j = call(base, "/api/journal?since=1")
        check("?since= returns only the tail",
              j["ok"] and [e["seq"] for e in j["events"]] == [2])

        print("S5. remote worker loop")
        _, before = call(base, "/api/watermark")
        call(base, "/api/submit", {"op": "put", "key": "node:law_of_pairs",
                                   "value": {"eq": "3*x0*x1", "r2": 0.99},
                                   "who": "worker_3"})
        _, after = call(base, "/api/watermark")
        check("worker's cheap recheck sees the change",
              after["last_seq"] == before["last_seq"] + 1)
        _, j = call(base, f"/api/journal?since={before['last_seq']}")
        touched = {dec(e["e"])["edit"]["key"] for e in j["events"]}
        check("delta names exactly the touched key",
              touched == {"node:law_of_pairs"})
        _, r = call(base, "/api/record?key=node:law_of_pairs")
        check("refetched record is current", dec(r["value"])["r2"] == 0.99)

        print("S6. malformed requests")
        code, r = call(base, "/api/submit", {"nonsense": True})
        check("edit without op/key -> 400 with clean why",
              code == 400 and "op and key" in r["why"])
        code, r = call(base, "/api/journal?since=NaNsense")
        check("bad since -> 400", code == 400)
        code, r = call(base, "/api/wrong_path")
        check("unknown path -> 400", code == 400)

        print("S7. bearer token")
        tok_server = PrimeServer(os.path.join(tmp, "prime_tok"), token="s3cret")
        tok_base = tok_server.start()
        code, r = call(tok_base, "/api/watermark")
        check("no token -> 401", code == 401)
        code, r = call(tok_base, "/api/watermark", token="s3cret")
        check("right token -> 200", code == 200 and r["ok"])

        print("S8. bind address")
        check("localhost only by default",
              server.host == "127.0.0.1" and tok_server.host == "127.0.0.1")
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
