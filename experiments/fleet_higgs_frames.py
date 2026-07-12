"""fleet_higgs_frames.py — the frame duel (2026-07-12).

The first fleet run refused m_jj/m_jjj honestly: an invariant mass is
the SQUARE ROOT of a sum of product terms, and sqrt-of-composite is
outside the enumerator's sentence shape. The duel: for every derived
mass, TWO rival jobs — discover y, and discover y² — both judged in
ORIGINAL mass space on 2000 held-out rows (never trained on). The
measured number picks the frame; nothing is hand-told about which
masses "should" square.

Run:  python fleet_higgs_frames.py [--workers 4] [--rows 5000]
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

MASSES = [
    ("m_jj", 22, [6, 7, 8, 10, 11, 12]),
    ("m_jjj", 23, [6, 7, 8, 10, 11, 12, 14, 15, 16]),
    ("m_lv", 24, [1, 2, 3, 4, 5]),
    ("m_jlv", 25, [1, 2, 3, 4, 5, 6, 7, 8]),
    ("m_bb", 26, list(range(6, 22))),
    ("m_wbb", 27, list(range(1, 22))),
    ("m_wwbb", 28, list(range(1, 22))),
]
FRAMES = ["y", "y2"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--rows", type=int, default=5000)
    a = p.parse_args()

    day = time.strftime("%Y-%m-%d")
    run_dir = os.path.join(ROOT, "experiments", "runs", day)
    os.makedirs(run_dir, exist_ok=True)
    server = PrimeServer(os.path.join(run_dir, "fleet_frames_prime"))
    jobs = []
    for name, tgt, cols in MASSES:
        for frame in FRAMES:
            jobs.append((name, tgt, cols, frame))
    for k, (name, tgt, cols, frame) in enumerate(jobs):
        server.orch.submit({"op": "put", "key": f"job:{k}", "who": "fleet",
                            "value": {"kind": "discover_file", "path": HIGGS,
                                      "rows": a.rows, "target_col": tgt,
                                      "input_cols": cols, "frame": frame,
                                      "name": f"{name}_{frame}",
                                      "status": "open"}})
    server.orch.process()
    base = server.start()
    print(f"  FRAME DUEL: {a.workers} workers x {len(jobs)} jobs "
          f"({len(MASSES)} masses x 2 frames), {a.rows} rows each")
    env = dict(os.environ, PYTHONUTF8="1")
    t0 = time.perf_counter()
    procs = [subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "worker.py"), "--prime", base,
         "--who", f"w{i}", "--jobs", str(len(jobs)), "--drain"],
        cwd=ROOT, env=env) for i in range(a.workers)]
    for pr in procs:
        pr.wait(timeout=3600)
    wall = time.perf_counter() - t0
    server.orch.compact(engine_version="fleet_frames")

    lines = [f"FRAME DUEL — {day}, {len(MASSES)} masses x 2 frames, "
             f"{a.rows} rows/job + 2000 held-out, real HIGGS", ""]
    busy = 0.0
    for m_i, (name, tgt, cols) in enumerate(MASSES):
        row = {}
        for f_i, frame in enumerate(FRAMES):
            k = m_i * 2 + f_i
            res = server.orch.get(f"node:law:{k}") or {}
            busy += res.get("seconds", 0.0)
            row[frame] = res
        ry = row["y"].get("r2_orig")
        r2 = row["y2"].get("r2_orig")
        vy = row["y"].get("finding", {}).get("verdict", "?")
        v2 = row["y2"].get("finding", {}).get("verdict", "?")
        best = "y2" if (r2 or -9) > (ry or -9) else "y"
        gain = (r2 or 0) - (ry or 0)
        lines.append(f"  {name:7s} y : {str(vy):8s} held-out r2={ry}")
        lines.append(f"          y2: {str(v2):8s} held-out r2={r2}   "
                     f"WINNER: {best} ({gain:+.3f})")
        eq = str(row[best].get("finding", {}).get("equation", ""))
        if best == "y2" and eq:
            lines.append(f"          => {name} = sqrt( {eq[:90]} )")
        lines.append("")
    lines.append(f"  wall {wall:.1f}s | worker-busy {busy:.1f}s | "
                 f"utilization {busy / wall:.2f}x ({a.workers} workers)")
    report = "\n".join(lines)
    print(report)
    with open(os.path.join(run_dir, "fleet_frames_report.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(report + "\n")
    server.stop()


if __name__ == "__main__":
    main()
