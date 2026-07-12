"""fleet_higgs.py — the worker fleet on REAL data (2026-07-12).

Ten discovery jobs over the real HIGGS array (11M rows, sampled),
drained by N worker PROCESSES coordinating through Prime's doorway:
each derived-mass column posed from ITS OWN particles' raw components
(the challenge as a physicist would pose it), plus three control jobs
where the honest answer is a refusal (a lepton is not a function of
the jets). Whatever the verdicts are, they are reported plainly —
refusals are answers.

Run:  python fleet_higgs.py [--workers 4] [--rows 5000]
Artifacts: runs/<date>/fleet_higgs_prime/ (packs+journal+ops) and
fleet_higgs_report.txt.
"""
import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from isaac_store.server import PrimeServer  # noqa: E402

HIGGS = os.path.join(ROOT, "data", "HIGGS.npy")
if not os.path.exists(HIGGS):
    HIGGS = r"c:\Users\jtwee\Documents\isaac_project\data\HIGGS.npy"

# columns: 0 label | 1-21 raw kinematics | 22-28 derived masses
JOBS = [
    ("m_jj    <- jet1,jet2 raw",        22, [6, 7, 8, 10, 11, 12], "physics"),
    ("m_jjj   <- jets1-3 raw",          23, [6, 7, 8, 10, 11, 12, 14, 15, 16], "physics"),
    ("m_lv    <- lepton+MET raw",       24, [1, 2, 3, 4, 5], "physics"),
    ("m_jlv   <- jet1+lepton+MET raw",  25, [1, 2, 3, 4, 5, 6, 7, 8], "physics"),
    ("m_bb    <- jets+btags raw",       26, list(range(6, 22)), "physics"),
    ("m_wbb   <- all 21 raw",           27, list(range(1, 22)), "physics"),
    ("m_wwbb  <- all 21 raw",           28, list(range(1, 22)), "physics"),
    ("CONTROL jet1_pt <- lepton+MET",    6, [1, 2, 3, 4, 5], "control"),
    ("CONTROL lep_pt  <- jets",          1, [6, 7, 8, 10, 11, 12, 14, 15, 16,
                                             18, 19, 20], "control"),
    ("CONTROL jet1_btag <- jet1 kin",    9, [6, 7, 8], "control"),
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--rows", type=int, default=5000)
    a = p.parse_args()

    day = time.strftime("%Y-%m-%d")
    run_dir = os.path.join(ROOT, "experiments", "runs", day)
    os.makedirs(run_dir, exist_ok=True)
    server = PrimeServer(os.path.join(run_dir, "fleet_higgs_prime"))
    for k, (name, tgt, cols, note) in enumerate(JOBS):
        server.orch.submit({"op": "put", "key": f"job:{k}", "who": "fleet",
                            "value": {"kind": "discover_file", "path": HIGGS,
                                      "rows": a.rows, "target_col": tgt,
                                      "input_cols": cols, "name": f"higgs_{tgt}",
                                      "note": note, "status": "open"}})
    server.orch.process()
    base = server.start()

    print(f"  FLEET: {a.workers} workers x {len(JOBS)} jobs, "
          f"{a.rows} rows each, real HIGGS")
    env = dict(os.environ, PYTHONUTF8="1")
    t0 = time.perf_counter()
    procs = [subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "worker.py"), "--prime", base,
         "--who", f"w{i}", "--jobs", str(len(JOBS)), "--drain"],
        cwd=ROOT, env=env) for i in range(a.workers)]
    for pr in procs:
        pr.wait(timeout=3600)
    wall = time.perf_counter() - t0
    server.orch.compact(engine_version="fleet_higgs")

    lines = [f"FLEET HIGGS — {day}, {a.workers} workers, {len(JOBS)} jobs, "
             f"{a.rows} rows/job (of 11,000,000)", ""]
    busy = 0.0
    for k, (name, tgt, cols, note) in enumerate(JOBS):
        job = server.orch.get(f"job:{k}")
        res = server.orch.get(f"node:law:{k}") or {}
        f = res.get("finding", {})
        secs = res.get("seconds", 0.0)
        busy += secs
        verdict = f.get("verdict", f.get("kind", "?"))
        r2 = f.get("r2", f.get("R2"))
        r2s = f"r2={r2:.3f}" if isinstance(r2, float) else ""
        eq = str(f.get("equation", ""))[:64]
        lines.append(f"  {name:34s} [{job['claimed_by']:>3s}] {secs:6.1f}s  "
                     f"{str(verdict):12s} {r2s:10s} {eq}")
    lines += ["",
              f"  wall {wall:.1f}s | worker-busy {busy:.1f}s | "
              f"utilization {busy / wall:.2f}x of 1 core "
              f"({a.workers} workers)"]
    report = "\n".join(lines)
    print(report)
    with open(os.path.join(run_dir, "fleet_higgs_report.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(report + "\n")
    server.stop()


if __name__ == "__main__":
    main()
