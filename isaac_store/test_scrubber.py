"""Scrubber battery — the Identity Law, enforced and measured.

P1 every pattern class stripped, complete count (planted -> found)
P2 the abstraction survives: equations/stats byte-identical
P3 the scrub REPORT never contains content (counts only)
P4 refusal when identity is load-bearing (in keys/node names)
P5 a clean share passes through byte-identical
P6 deny_list: customer-named identities stripped wherever they hide
P7 identity_gate at Prime's admission: dirty edit refused wrong-kept,
   clean edit admitted, inner gate still consulted
Run: python test_scrubber.py   (from isaac_store/)
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store.orchestrator import Orchestrator
from isaac_store.scrubber import identity_gate, scrub

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


PLANTS = {
    "email": "reach me at alice.w+work@example-corp.com ok",
    "ssn": "ssn on file 123-45-6789 end",
    "phone": "call (555) 123-4567 anytime",
    "card": "card 4111 1111 1111 1111 charged",
    "ip": "login from 192.168.10.44 seen",
    "address": "ships to 742 Evergreen Terrace Ave today",
    "honorific_name": "reviewed by Dr. Alice Wong today",
}


def main():
    print("P1. every pattern class stripped")
    payload = {"notes": list(PLANTS.values()),
               "nested": {"deep": (PLANTS["email"], {PLANTS["ssn"]})}}
    r = scrub(payload)
    blob = json.dumps(r["clean"], default=list)
    for cat, planted in PLANTS.items():
        check(f"{cat} stripped + counted",
              r["report"].get(cat, 0) >= 1 and planted not in blob)

    print("P2. the abstraction survives")
    share = {"equation": "+1.00*sin(3*(x1*x0))", "r2": 0.98,
             "scope": [-2.0, 2.0], "n_obs": 300,
             "note": f"discovered on data from {PLANTS['email']}"}
    r = scrub(share)
    check("equation byte-identical", r["clean"]["equation"] == share["equation"])
    check("measurements untouched",
          r["clean"]["r2"] == 0.98 and r["clean"]["scope"] == [-2.0, 2.0]
          and r["clean"]["n_obs"] == 300)
    check("identity gone from the note", "[email]" in r["clean"]["note"])

    print("P3. the report never leaks content")
    rep = json.dumps(r["report"])
    check("report = categories and counts only",
          "example-corp" not in rep and "alice" not in rep.lower()
          and r["report"] == {"email": 1})

    print("P4. refusal when identity is load-bearing")
    r = scrub({"per_customer": {PLANTS["email"]: {"total": 91.5}}})
    check("identity-as-key REFUSED with why",
          not r["ok"] and "structure depends on WHO" in r["why"])
    check("refusal still reports categories", r["report"].get("email", 0) == 1)

    print("P5. clean shares pass untouched")
    clean_share = {"equation": "3*x0*x1+x0**2", "r2": 0.997,
                   "residual": "below noise floor", "n_obs": 300}
    r = scrub(clean_share)
    check("byte-identical, empty report",
          r["ok"] and r["clean"] == clean_share and r["report"] == {})

    print("P6. deny_list")
    r = scrub({"note": "as discussed with Alice Wong of Example Corp",
               "tag": "ExampleCorp-internal"},
              deny_list=["Alice Wong", "Example Corp", "ExampleCorp"])
    blob = json.dumps(r["clean"])
    check("named identities stripped wherever they hide",
          "Alice Wong" not in blob and "ExampleCorp" not in blob
          and r["report"]["deny_list"] == 3)

    print("P7. identity_gate at Prime's admission")
    tmp = tempfile.mkdtemp(prefix="isaac_scrub_gate_")
    try:
        def inner(edit, state):
            if edit.get("why") == "bad":
                return False, "inner gate: evidence below null"
            return True, "inner gate ok"

        orch = Orchestrator(os.path.join(tmp, "prime"),
                            admission=identity_gate(inner))
        orch.submit({"op": "put", "key": "node:law", "who": "scrubber_1",
                     "value": {"equation": "3*x0*x1", "r2": 0.98}})
        orch.submit({"op": "put", "key": "node:dirty", "who": "rogue",
                     "value": {"note": f"belongs to {PLANTS['ssn']}"}})
        orch.submit({"op": "put", "key": "node:weak", "who": "w",
                     "value": 1, "why": "bad"})
        a, rej = orch.process()
        check("clean admitted, dirty + weak refused", a == 1 and rej == 2)
        check("dirty edit never entered state", "node:dirty" not in orch.state)
        whys = [e["why"] for _s, e in orch.journal.read_since(0)
                if e["verdict"] == "rejected"]
        check("Identity Law rejection wrong-kept, categories not content",
              any("Identity Law" in w and "ssn" in w for w in whys)
              and not any("123-45" in w for w in whys))
        check("inner gate still consulted",
              any("below null" in w for w in whys))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
