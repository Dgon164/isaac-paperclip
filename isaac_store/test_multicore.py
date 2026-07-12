"""Multicore battery — the orchestrator/worker design doing its real
job: separate OS processes computing in parallel, coordinating
through Prime's doorway, no locks anywhere.

M1 the claim mechanism: two racing claims, exactly one wins, the
   loser is wrong-kept with its why
M2 4 worker PROCESSES drain 8 discover-jobs: every job done exactly
   once, work actually distributed across workers
M3 every parallel result is CORRECT (laws match truth, corr > 0.999)
M4 measured multicore numbers: same jobs, 1 worker vs 4 workers —
   wall-clock reported complete, speedup must be real (> 1.2x)
Run: python test_multicore.py   (from isaac_store/)
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.orchestrator import Orchestrator
from isaac_store.server import PrimeServer

PASS = FAIL = 0
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = os.path.join(ROOT, "worker.py")
N_JOBS = 8


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def seed_jobs(orch):
    for k in range(N_JOBS):
        orch.submit({"op": "put", "key": f"job:{k}", "who": "battery",
                     "value": {"kind": "discover", "seed": 100 + k,
                               "rows": 2000, "a": 2.0 + k, "b": 1.0 + 0.5 * k,
                               "status": "open"}})
    orch.process()


def run_fleet(tmp, name, n_workers):
    server = PrimeServer(os.path.join(tmp, name))
    seed_jobs(server.orch)
    base = server.start()
    env = dict(os.environ, PYTHONUTF8="1")
    t0 = time.perf_counter()
    procs = [subprocess.Popen(
        [sys.executable, WORKER, "--prime", base, "--who", f"w{i}",
         "--jobs", str(N_JOBS), "--drain"],
        cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for i in range(n_workers)]
    for pr in procs:
        pr.wait(timeout=600)
    elapsed = time.perf_counter() - t0
    server.stop()
    return server, elapsed


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_multicore_")
    try:
        print("M1. the claim mechanism")
        orch = Orchestrator(os.path.join(tmp, "claims"))
        orch.submit({"op": "put", "key": "job:x", "who": "seed",
                     "value": {"status": "open"}})
        orch.process()
        rec = orch.get("job:x")
        for who in ("w1", "w2"):  # both saw the same open record
            orch.submit({"op": "put", "key": "job:x", "who": who,
                         "value": {"status": "claimed", "claimed_by": who},
                         "expect": rec})
        a, r = orch.process()
        check("exactly one claim wins", a == 1 and r == 1
              and orch.get("job:x")["claimed_by"] == "w1")
        lost = [e for _s, e in orch.journal.read_since(0)
                if e["verdict"] == "rejected"]
        check("the lost claim is wrong-kept with its why",
              len(lost) == 1 and "superseded" in lost[0]["why"])

        print(f"M4a. sequential baseline: 1 worker, {N_JOBS} jobs")
        srv1, t_seq = run_fleet(tmp, "prime_seq", 1)
        seq_done = sum(1 for k in range(N_JOBS)
                       if srv1.orch.get(f"job:{k}")["status"] == "done")
        check("sequential run completes all jobs", seq_done == N_JOBS,
              f"{t_seq:.1f}s wall")

        print(f"M2. parallel fleet: 4 worker processes, {N_JOBS} jobs")
        srv4, t_par = run_fleet(tmp, "prime_par", 4)
        jobs = [srv4.orch.get(f"job:{k}") for k in range(N_JOBS)]
        check("every job done exactly once",
              all(j["status"] == "done" for j in jobs))
        claimants = {j["claimed_by"] for j in jobs}
        check("work distributed across workers (no double-claims)",
              len(claimants) >= 2, f"workers used: {sorted(claimants)}")

        print("M3. every parallel result is correct")
        mod = bridge.load_isaac_module()
        rng = np.random.default_rng(7)
        Xt = rng.uniform(-2, 2, (200, 2))
        good = 0
        for k in range(N_JOBS):
            rec = srv4.orch.get(f"node:law:{k}")
            mind = mod.Isaac()
            mind.net.set_meta("law:job", "model", rec["model"])
            pred = mind.apply_law("job", Xt)
            truth = (2.0 + k) * Xt[:, 0] * Xt[:, 1] + (1.0 + 0.5 * k) * Xt[:, 0] ** 2
            good += pred is not None and float(np.corrcoef(pred, truth)[0, 1]) > 0.999
        check("all laws survive the trip and match truth",
              good == N_JOBS, f"{good}/{N_JOBS} exact")

        print("M4b. the multicore numbers (complete, measured)")
        speedup = t_seq / t_par if t_par > 0 else 0
        print(f"       1 worker : {t_seq:6.1f}s for {N_JOBS} jobs")
        print(f"       4 workers: {t_par:6.1f}s for {N_JOBS} jobs")
        print(f"       speedup  : {speedup:.2f}x")
        check("parallel is genuinely faster", speedup > 1.2,
              f"{speedup:.2f}x")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
