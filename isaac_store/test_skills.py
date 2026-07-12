"""Skills battery — roles are loadouts, not species (owner, 2026-07-12).

K1 the scrubber skill is published INTO Prime as a plain record and
   a worker becomes a scrubber by PULLING it (no baked-in vocabulary)
K2 educating Prime re-equips workers: a new pattern published to the
   skill record reaches a worker at its recheck; a pinned job keeps
   its old loadout to the job boundary
K3 skills ride the same doorway as everything else: pulled over
   PrimeServer HTTP and used directly
Run: python test_skills.py   (from isaac_store/)
"""
import json
import os
import shutil
import sys
import tempfile
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store.cache import LiveCache
from isaac_store.codec import dec
from isaac_store.orchestrator import Orchestrator
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
    tmp = tempfile.mkdtemp(prefix="isaac_skills_")
    server = None
    t = [0.0]
    try:
        prime_dir = os.path.join(tmp, "prime")
        orch = Orchestrator(prime_dir)

        print("K1. a worker becomes a scrubber by pulling the skill")
        check("skill published into Prime via the normal queue",
              publish_skill(orch, "scrubber", seed_skill()))
        orch.compact()
        cache = LiveCache(os.path.join(prime_dir, "packs"),
                          os.path.join(prime_dir, "journal.jsonl"),
                          clock=lambda: t[0])
        skill = pull_skill(cache, "scrubber")
        check("skill is a plain record (learned things + structures)",
              skill["kind"] == "scrubber_vocabulary" and len(skill["patterns"]) == 7)
        r = scrub({"note": "ssn 123-45-6789, from bob@corp.io"}, vocabulary=skill)
        check("scrubbing runs on the PULLED vocabulary",
              r["ok"] and r["report"] == {"email": 1, "ssn": 1}
              and "123-45" not in json.dumps(r["clean"]))

        print("K2. educating Prime re-equips workers")
        grown = dict(skill)
        grown["version"] = 2
        grown["patterns"] = skill["patterns"] + [["employee_id", r"EMP-\d{6}"]]
        publish_skill(orch, "scrubber", grown, who="education")
        with cache.job():
            t[0] += 3 * 3600
            mid_job = pull_skill(cache, "scrubber")
            check("pinned job keeps its old loadout", mid_job["version"] == 1)
        fresh = pull_skill(cache, "scrubber")  # job over; overdue recheck ran
        check("worker re-equipped at the job boundary", fresh["version"] == 2)
        r = scrub({"note": "badge EMP-104233 flagged"}, vocabulary=fresh)
        check("the LEARNED pattern strips",
              r["report"] == {"employee_id": 1} and "EMP-104233" not in r["clean"]["note"])

        print("K3. skills ride the same doorway (HTTP)")
        server = PrimeServer(os.path.join(tmp, "prime2"))
        base = server.start()
        publish_skill(server.orch, "scrubber", grown)
        with urllib.request.urlopen(base + "/api/record?key=skill:scrubber",
                                    timeout=10) as resp:
            wire = json.loads(resp.read())
        remote_skill = dec(wire["value"])
        r = scrub({"note": "EMP-999999 called from 10.0.0.7"},
                  vocabulary=remote_skill)
        check("skill pulled over HTTP and used directly",
              wire["ok"] and r["report"] == {"employee_id": 1, "ip": 1})
        cache.close()
    finally:
        if server:
            server.stop()
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
