"""bootdev_flight.py — THE FIRST FLIGHT (the code genesis, rung 2;
owner 2026-07-19: "lets keep it going").

Walks a boot.dev course IN ORDER, maintaining the repo state, and
at each lesson tries the HONEST roads in sequence:

  road 0  AS-IS      the current repo already satisfies the spec
  road 1  TOLD-CMDS  the readme's own ```sh blocks, run under a
                     declared allowlist (the lesson tells the
                     student to run them — told knowledge)
  road 2  COMPOSE    eat the lesson's idioms (cited meal), compose
                     the named function from the pool (idioms +
                     minted codeshapes), assemble main.py, court
  road 3  DARK       no road reached it — the frontier receipt

The court is THEIR grader (bootdev run); submit fires only after
a green run (the owner's standing autopilot blessing for this
course). Every pass mints; every dark names its why. His account
eats the idiom meals and keeps the codeshapes — the flight IS a
study session, journaled kind=study.

usage: python bootdev_flight.py [--max N] [course-uuid]
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
import isaac as mod                                    # noqa: E402
from isaac_store.composer import (eat_lesson,          # noqa: E402
                                  compose_function, compose_main,
                                  compose_print_main, mint,
                                  minted_shapes, minted_names,
                                  record_attempt)

WSL = ["wsl.exe", "-d", "Ubuntu", "-u", "root", "--", "bash", "-lc"]
WORKDIR = "/root/bookbot"
ALLOW = re.compile(
    r"^(mkdir |curl (-s?L )?[\"']?https://storage\.googleapis\.com"
    r"|uv |git |echo |python3? |ls|head |cat |wc |touch )")
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def wsl(cmd, timeout=120):
    out = subprocess.run(WSL + [cmd], capture_output=True,
                         text=True, encoding="utf-8",
                         errors="replace", timeout=timeout)
    return out.stdout + out.stderr


def fetch(path):
    out = subprocess.run(
        WSL + [f"/root/go/bin/lessonfetch {path}"],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=60)
    return json.loads(out.stdout)


def _run_cmd(command):
    out = subprocess.run(
        WSL + [f"cd {WORKDIR} && {command}"],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=180)
    return out.stdout, out.returncode


def spec_court(lesson):
    """Isaac's court = THEIR grader's own published spec, run
    faithfully and parsed deterministically (no TUI scraping). Each
    CLI step's command runs in the workdir; each test (exit code /
    stdout-contains-all / -none / lines>) is checked. Green only if
    every step passes; the failing check is named."""
    steps = ((lesson.get("LessonDataCLI") or {}).get("CLIData")
             or {}).get("Steps") or []
    cli = [s["CLICommand"] for s in steps if s.get("CLICommand")]
    if not cli:
        return dict(green=False, why="no CLI test steps",
                    gradeable=False)
    for step in cli:
        out, code = _run_cmd(step["Command"])
        for t in step.get("Tests", []):
            if t.get("ExitCode") is not None and \
                    code != t["ExitCode"]:
                return dict(green=False, gradeable=True,
                            why=f"exit {code}!={t['ExitCode']} on "
                                f"`{step['Command'][:40]}`")
            for need in (t.get("StdoutContainsAll") or []):
                if need not in out:
                    return dict(green=False, gradeable=True,
                                why=f"stdout missing '{need[:30]}'")
            for no in (t.get("StdoutContainsNone") or []):
                if no in out:
                    return dict(green=False, gradeable=True,
                                why=f"stdout has forbidden "
                                    f"'{no[:30]}'")
            if t.get("StdoutLinesGt") is not None and \
                    len(out.splitlines()) <= t["StdoutLinesGt"]:
                return dict(green=False, gradeable=True,
                            why=f"too few lines")
    return dict(green=True, gradeable=True, why="all steps green")


def submit(uuid):
    raw = wsl(f"cd {WORKDIR} && /root/go/bin/bootdev submit {uuid}",
              timeout=180)
    clean = ANSI.sub("", raw)
    return "✓" in raw or "assed" in clean


def write_artifact(defs, main_body):
    src = ("\n\n".join(defs) + "\n\n" + main_body) if defs \
        else main_body
    p = subprocess.run(WSL + [f"cat > {WORKDIR}/main.py"],
                       input=src, capture_output=True, text=True)
    return p.returncode == 0


def told_commands(readme):
    cmds = []
    for block in re.findall(r"```(?:sh|bash)\n(.*?)```", readme,
                            re.S):
        for ln in block.strip().split("\n"):
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                cmds.append(ln)
    return cmds


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cap = 20
    for a in sys.argv[1:]:
        if a.startswith("--max"):
            cap = int(a.split("=")[-1]) if "=" in a else cap
    course = args[0] if args else \
        "094fd7d4-ec78-4202-96ca-c5f79fc332d2"

    from isaac_store.sparring import IsaacAccount
    home = os.path.join(os.path.expanduser("~"), "Documents",
                        "isaac_home")
    shutil.copy2(os.path.join(home, "mind.isaac"),
                 os.path.join(home, "mind.isaac.bak"))
    acct = IsaacAccount(home, mod)
    mind = acct.mind

    # a clean bench: fresh workdir with the book the lessons need
    wsl(f"rm -rf {WORKDIR} && mkdir -p {WORKDIR}/books")
    wsl(f"cd {WORKDIR} && [ -f books/frankenstein.txt ] || curl "
        f"-sL https://storage.googleapis.com/qvault-webapp-dynamic"
        f"-assets/course_assets/frankenstein.txt -o "
        f"books/frankenstein.txt", timeout=180)
    wsl(f"echo 'print(\"placeholder\")' > {WORKDIR}/main.py")

    c = fetch(f"/v1/courses/{course}")
    print(f"FLIGHT: {c['Title']} — {c['NumLessons']} lessons\n")
    container = f"bootdev-{c.get('Slug', c['UUID'][:8])[:20]}"
    transcript = []
    known_paths = []
    n_done = 0

    for ch in c["Chapters"]:
        for les in (ch.get("Lessons") or []):
            if n_done >= cap:
                break
            n_done += 1
            uuid, title = les["UUID"], les["Title"]
            L = fetch(uuid)["Lesson"]
            if L["Type"] == "type_choice":
                transcript.append((title, "SKIP",
                                   "browser choice — the owner's "
                                   "click, never automated"))
                print(f"  [skip] {title} — owner's click")
                continue
            readme = (L.get("LessonDataCLI") or {}).get("Readme",
                                                        "") or ""
            got = eat_lesson(mind, title, L.get("CanonicalURL",
                                                ""), container,
                             readme)
            for pth in re.findall(r"books/\S+\.txt", readme):
                if pth not in known_paths:
                    known_paths.append(pth)
            road = None
            snap = wsl(f"cat {WORKDIR}/main.py 2>/dev/null")

            # road 0 — as-is (repo already satisfies the spec)
            v = spec_court(L)
            if not v.get("gradeable"):
                transcript.append((title, "SKIP",
                                   "no CLI test — reading/setup "
                                   "lesson, nothing to grade"))
                print(f"  [read] {title} — no gradeable test")
                continue
            if v["green"]:
                road = "AS-IS"
            # road 1 — the readme's own told commands (allowlisted)
            if road is None:
                ran = [cm[:40] for cm in told_commands(readme)
                       if ALLOW.match(cm)
                       and wsl(f"cd {WORKDIR} && {cm}",
                               timeout=180) is not None]
                if ran and spec_court(L)["green"]:
                    road = f"TOLD-CMDS ({len(ran)})"
            # road 2 — compose from the idiom pool + minted shapes
            if road is None and readme:
                defs = minted_shapes(mind)
                pool = got["idioms"]
                new_funcs = [f for f in got["funcs"]
                             if f != "main"
                             and f"def {f}(" not in "".join(defs)]
                cand_fns = compose_function(
                    new_funcs[0], got["arg"] or "filepath",
                    pool, minted=None)[:5] if new_funcs else [None]
                mains = []
                target = new_funcs[0] if new_funcs else (
                    minted_names(mind)[-1:] or [None])[0]
                if target:
                    for pth in (known_paths[:2] or [None]):
                        if pth:
                            mains.append(compose_main(target, pth))
                if got["literals"]:
                    mains.append(compose_print_main(
                        got["literals"][:3]))
                for idiom in pool:
                    if "print(" in idiom and "def " not in idiom:
                        mains.append(idiom + "\n")
                tried, bugs = 0, []
                for cf in (cand_fns or [None]):
                    for mn in (mains or [None]):
                        if mn is None:
                            continue
                        tried += 1
                        if tried > 12:
                            break
                        all_defs = defs + ([cf["code"]] if cf
                                           else [])
                        write_artifact(all_defs, mn)
                        v = spec_court(L)
                        rec = (cf["receipt"] if cf else
                               "main from idioms")
                        # each candidate is a hypothesis: court it,
                        # keep green / roll back red WITH the bug
                        record_attempt(mind, title, rec, v)
                        if v["green"]:
                            road = "COMPOSE: " + rec[:44]
                            if cf:
                                mint(mind, new_funcs[0], cf["code"],
                                     cf["receipt"], container,
                                     f"boot.dev spec green ({title})")
                            break
                        # ROLLBACK: a red candidate never survives —
                        # restore last-green before the next try
                        bugs.append(v.get("why", ""))
                        write_artifact([], snap)
                    if road:
                        break
                if road is None and bugs:
                    print(f"         (bug-detection: {len(bugs)} "
                          f"candidates courted+rolled back; last: "
                          f"{bugs[-1][:44]})")
            if road:
                ok = submit(uuid)
                transcript.append((title, "PASS",
                                   road + ("" if ok else
                                           " (run green; submit "
                                           "unconfirmed)")))
                print(f"  [PASS] {title} — {road}"
                      + ("" if ok else "  [submit?]"))
            else:
                transcript.append((title, "DARK", v.get("why", "")))
                print(f"  [DARK] {title} — {v.get('why','')[:52]}")
            time.sleep(5)
        if n_done >= cap:
            break

    passes = sum(1 for _t, s, _w in transcript if s == "PASS")
    darks = sum(1 for _t, s, _w in transcript if s == "DARK")
    skips = sum(1 for _t, s, _w in transcript if s == "SKIP")
    acct._journal(dict(kind="study",
                       stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                       course=c["Title"],
                       transcript=[f"{s}: {t} ({w[:60]})"
                                   for t, s, w in transcript]))
    mind.save(acct.mind_path)
    print(f"\nFLIGHT DONE: {passes} passed, {darks} dark, "
          f"{skips} owner-clicks of {len(transcript)}; "
          f"codeshapes now {len(minted_shapes(mind))}; "
          f"journal + mind saved.")


if __name__ == "__main__":
    main()
