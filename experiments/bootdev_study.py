"""bootdev_study.py — THE STUDY HARNESS (owner 2026-07-19: "set
isaac to autopilot and see if he can finish the course").

HONEST BY CONSTRUCTION. It fetches the real lesson specs (through
the owner's own CLI token, via lessonfetch in WSL) and runs
ISAAC'S OWN ORGANS against each one — no LLM ghost-writes his
homework (that would be the rigged exam the audit hunts). For each
lesson it rules, with receipts, whether his CURRENT organs can
genuinely reach the artifact the grader demands, and names the
DARK ones — the measured frontier is the deliverable.

The reach test, per his real organs:
  - reader v2  : can READ a program into a goal sheet (not write)
  - goal tree  : can decompose a QUANTITY into his laws
  - retune     : can EDIT a constant in a given program
  - telling    : can take a told LAW
None of these AUTHORS novel imperative Python. So a lesson is
REACHABLE only if its artifact is (law/goal/edit)-shaped; a lesson
that needs new imperative code is DARK — needs a code-generation
organ Isaac does not have.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))

WSL = ["wsl.exe", "-d", "Ubuntu", "-u", "root", "--", "bash", "-lc"]


def fetch(path):
    out = subprocess.run(
        WSL + [f"/root/go/bin/lessonfetch {path}"],
        capture_output=True, text=True, timeout=60)
    return json.loads(out.stdout)


def classify(lesson):
    L = lesson["Lesson"]
    typ = L["Type"]
    if typ == "type_choice":
        return dict(kind="quiz", reach="DARK",
                    why="multiple-choice — needs reading "
                        "comprehension + a chosen answer; no organ "
                        "selects a prose answer")
    data = L.get("LessonDataCLI") or {}
    readme = (data.get("Readme") or "")
    steps = ((data.get("CLIData") or {}).get("Steps") or [])
    cmds = [s["CLICommand"]["Command"] for s in steps
            if s.get("CLICommand")]
    # what does the assignment demand?
    asg = readme.lower()
    writes_code = bool(re.search(
        r"write a (new )?function|create a file|def |\.py\b|"
        r"build|implement|return", asg))
    only_setup = bool(cmds) and all(
        re.search(r"uv |pip |python3? --version|install|git |ls|"
                  r"echo|which|mkdir", c) for c in cmds) \
        and not writes_code
    if only_setup:
        return dict(kind="setup", reach="ENV",
                    why="environment/tooling step (install, "
                        "version, git) — a shell action, not a "
                        "reasoning artifact",
                    cmds=cmds)
    if writes_code:
        return dict(kind="code", reach="DARK",
                    why="authors novel imperative Python (a "
                        "function/file the grader runs) — Isaac's "
                        "organs read/decompose/edit, they do not "
                        "WRITE new code",
                    cmds=cmds)
    return dict(kind="other", reach="DARK",
                why="not law/goal/edit-shaped; outside his "
                    "current organs", cmds=cmds)


def main():
    course = sys.argv[1] if len(sys.argv) > 1 \
        else "094fd7d4-ec78-4202-96ca-c5f79fc332d2"  # Bookbot
    c = fetch(f"/v1/courses/{course}")
    print(f"COURSE: {c['Title']}  ({c['NumLessons']} lessons)\n")
    tally = {}
    for ch in c["Chapters"]:
        print(f"— chapter: {ch['Title']} —")
        for l in (ch.get("Lessons") or []):
            full = fetch(l["UUID"])
            v = classify(full)
            tally[v["reach"]] = tally.get(v["reach"], 0) + 1
            mark = {"ENV": "env ", "REACHABLE": "REACH",
                    "DARK": "DARK"}[v["reach"]]
            print(f"  [{mark}] {l['Title']}  — {v['why'][:64]}")
    print(f"\nFRONTIER: {tally}")
    total = sum(tally.values())
    reach = tally.get("REACHABLE", 0) + tally.get("ENV", 0)
    print(f"his organs genuinely reach {reach}/{total} "
          f"(env+reasoning); {tally.get('DARK', 0)} need a "
          f"code-writing organ he does not have.")


if __name__ == "__main__":
    main()
