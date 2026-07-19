"""diagnosis_battery.py — PROMOTION GATE for THE DIAGNOSIS COURT
+ THE ASK ROAD (owner 2026-07-19: "its evaluating backward...
there are only so many variables to adjust... and you can check
each state directly" + THE FIRE-TRIANGLE CLAUSE: all known
variables green and it still fails = the model is missing a
variable = a NAMED UNKNOWN -> ask, never repair).

  DX1 the requirements model derives from the spec's OWN checks
      (commit-log / file / config-key variables with expected
      states — nothing hand-coded per lesson).
  DX2 EVALUATING BACKWARD: on a planted single-variable fault the
      backward walk names exactly the differing variable; the
      agreeing variables carry their receipts.
  DX3 THE INJECTION DIAGNOSTIC: adjusting ONLY the named suspect
      by the lesson's own told road un-darks the court.
  DX4 THE FIRE-TRIANGLE CLAUSE: a fault OUTSIDE the variable menu
      (an env anchor no file/log/config carries) -> all known
      variables agree, court still red, named_unknown=True — and
      the organ makes NO repair (the bench is untouched).
  DX5 NO SCREAM = NO ASK: a green structure yields no suspects
      and no ask; an all-pass ledger refuses the mine honestly.
  DX6 THE ASK IS A CITIZEN: planted darks sharing one condition
      mine past the shuffled-label null; the ask lands as
      ask:<name>, FUTURE tense, OPEN, evidence attached; re-ask
      SUPERSEDES, never erases.
  DX7 CALL-BIND AT THE SHELL: a told road's `<slot>` fills from
      the previous command's single-token output and runs green
      (the /tmp plumbing dataflow).
  DX8 THE SCOPE IS A VARIABLE (found live on the real Git
      Config dark): a key held in GLOBAL scope while the court
      reads --local is a named suspect with the scope desync
      SAID; the road writes the court's own scope -> green.
  DX9 COMPOSE-COMMIT: no told fence commits — the transfer that
      grows the log (his tense tracker's candidate->past) is
      instantiated with the court's OWN expected fragment as the
      message dimension -> green.
  DX10 THE CAPTURE ROAD: a `*-command-here` placeholder takes
      the neighbor fence's command, whose `<hash>` slot is
      resolved by ASKING THE REPO (operational access), and the
      redirect satisfies the file's court -> green.

Run: cd experiments && PYTHONHASHSEED=0 python diagnosis_battery.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
import isaac as isaac_mod                            # noqa: E402
from isaac_store.diagnosis import (                  # noqa: E402
    requirements_from_spec, diagnose, court_spec, adjust_roads,
    run_road, ask_report, ask_from_darks, featurize_darks,
    say_diagnosis)
from isaac_store.composer import ledger_set          # noqa: E402

Isaac = isaac_mod.Isaac


def spec(steps):
    """A lesson dict in THEIR shape."""
    return {"LessonDataCLI": {"CLIData": {"Steps": [
        {"CLICommand": s} for s in steps]}}}


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(bool(ok))
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    bench = tempfile.mkdtemp(prefix="dxbench_")
    env = dict(os.environ, GIT_AUTHOR_NAME="dx",
               GIT_AUTHOR_EMAIL="dx@x", GIT_COMMITTER_NAME="dx",
               GIT_COMMITTER_EMAIL="dx@x",
               MSYS_NO_PATHCONV="1",   # the 2026-07-19 ghost
               # a sandbox global config — DX8 plants a global
               # key without ever touching the user's real one
               GIT_CONFIG_GLOBAL=os.path.join(
                   bench, "gitconfig_global"))

    def run(cmd):
        # bash, never cmd.exe — the organ's contract is a POSIX
        # instrument (the flight passes its wsl runner)
        p = subprocess.run(["bash", "-c", cmd], cwd=bench,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env=env, timeout=60)
        return p.stdout + p.stderr, p.returncode

    run("git init -q -b master . && git config user.name dx && "
        "git config user.email dx@x")
    run("echo hello > contents.md && git add . && "
        "git commit -q -m 'A: add contents.md'")

    # ── DX1: the requirements model from the spec's own checks ──
    L = spec([
        dict(Command="git --no-pager log --oneline",
             Tests=[dict(StdoutContainsAll=["A:", "B:"])]),
        dict(Command="cat quotes.md",
             Tests=[dict(ExitCode=0,
                         StdoutContainsAll=["ship it"])]),
        dict(Command="git config webflyx.ceo",
             Tests=[dict(StdoutContainsAll=["ThePrimeagen"])]),
    ])
    reqs = requirements_from_spec(L)
    kinds = sorted(r["kind"] for r in reqs)
    check("DX1 requirements from the spec's own checks",
          kinds == ["commit-log", "commit-log", "config-key",
                    "file"]
          and any(r["kind"] == "file" and r["name"] == "quotes.md"
                  for r in reqs)
          and any(r["kind"] == "commit-log" and r["name"] == "B:"
                  for r in reqs),
          f"{len(reqs)} variables: {kinds}")

    # ── DX2: backward walk names exactly the differing variable ─
    run("echo 'ship it' > quotes.md && "
        "git config webflyx.ceo ThePrimeagen")
    d = diagnose(run, L)
    sus = [c["var"]["name"] for c in d["suspects"]]
    check("DX2 the backward walk names the one differing variable",
          not d["green"] and sus == ["B:"]
          and len(d["variables"]) == 4
          and sum(c["agree"] for c in d["variables"]) == 3,
          f"suspects={sus}; "
          f"{sum(c['agree'] for c in d['variables'])}/4 agree")

    # ── DX3: the injection diagnostic — one told adjustment ─────
    readme = ("Now make your second commit:\n\n```sh\n"
              "git add .\ngit commit -m \"B: add quotes\"\n```\n")
    roads = adjust_roads(readme, d["suspects"][0])
    if roads:
        run_road(run, roads[0])
    d3 = diagnose(run, L)
    check("DX3 adjust the named suspect by its told road -> green",
          bool(roads) and d3["green"],
          f"road: {roads[0]['why'] if roads else 'NONE'}; "
          f"re-court green={d3['green']}")

    # ── DX4: the fire-triangle clause — fault OUTSIDE the menu ──
    L4 = spec([
        dict(Command="git --no-pager log --oneline",
             Tests=[dict(StdoutContainsAll=["A:"])]),
        dict(Command="test -n \"$WEBFLYX_TOKEN\"",
             Tests=[dict(ExitCode=0)]),
    ])
    before = run("git --no-pager log --oneline && ls && "
                 "git config --list")[0]
    d4 = diagnose(run, L4)
    after = run("git --no-pager log --oneline && ls && "
                "git config --list")[0]
    check("DX4 all known variables agree + still red = NAMED "
          "UNKNOWN, no repair",
          not d4["green"] and d4["named_unknown"]
          and not d4["suspects"] and before == after,
          f"named_unknown={d4['named_unknown']}; bench "
          f"untouched={before == after}")

    # ── DX5: no scream = no ask ─────────────────────────────────
    L5 = spec([dict(Command="git --no-pager log --oneline",
                    Tests=[dict(StdoutContainsAll=["A:"])])])
    d5 = diagnose(run, L5)
    m5 = Isaac()
    for i in range(4):
        ledger_set(m5, f"u{i}", f"lesson {i}", "PASSED",
                   road="AS-IS")
    r5 = ask_from_darks(m5, "quiet")
    check("DX5 no scream = no ask (green court; all-pass ledger "
          "refuses the mine)",
          d5["green"] and not d5["suspects"]
          and not r5["asked"] and "nothing to mine"
          in r5["why"],
          f"court green={d5['green']}; mine: {r5['why'][:44]}")

    # ── DX6: the ask is a citizen (mined, future, superseded) ───
    # enough of both sides that a perfect separator can beat the
    # selection-corrected null (the 119/120 lesson applies to the
    # battery's own plant: 3-of-8 hands the shuffle a 1-in-56
    # chance at a perfect match — 6-of-18 does not)
    m6 = Isaac()
    for i in range(12):
        ledger_set(m6, f"p{i}", f"pass {i}", "PASSED",
                   road="TOLD-CMDS (2)")
    for i, bug in enumerate([
            "exit 1!=0 on `cat /tmp/catfileout.txt`",
            "exit 1!=0 on `cat /tmp/blobfile.txt`",
            "exit 1!=0 on `xxd /tmp/objdump.txt`",
            "exit 1!=0 on `cat /tmp/treefile.txt`",
            "exit 1!=0 on `cat /tmp/tagfile.txt`",
            "exit 1!=0 on `xxd /tmp/packfile.txt`"]):
        ledger_set(m6, f"d{i}", f"dark {i}", "DARK", bug=bug)
    r6 = ask_from_darks(m6, "tmp-plumbing")
    node = m6.net.get_meta("ask:tmp-plumbing", "active")
    ask_report(m6, "tmp-plumbing", "re-diagnosed hole",
               dict(note="second reading"))
    chain = m6.net.get_meta("ask:tmp-plumbing", "superseded")
    check("DX6 mined ask lands FUTURE+OPEN with evidence; re-ask "
          "supersedes",
          r6["asked"]
          and ("path_zone", "/tmp") in [(k, v) for k, v, _ in
                                        r6["mined"]["named"]]
          and node and node["tense"] == "future"
          and node["status"] == "OPEN"
          and chain and len(chain) == 1
          and chain[0]["record"]["hole"].startswith("the failures"),
          f"named={r6['mined']['named'][:1]}; tense="
          f"{node['tense'] if node else '?'}; chain={len(chain or [])}")

    # ── DX7: CALL-BIND at the shell — <slot> from prior output ──
    road7 = dict(lines=["git hash-object contents.md",
                        "git cat-file -p <hash>"],
                 why="told dataflow", slots=["hash"])
    tr = run_road(run, road7)
    check("DX7 `<slot>` filled from the previous command's output",
          len(tr) == 2 and tr[1][2] == 0 and "hello" in tr[1][1]
          and "<hash>" not in tr[1][0],
          f"ran `{tr[1][0][:40]}` -> {tr[1][1][:24]!r}")

    # ── DX8: THE SCOPE IS A VARIABLE (the live Git Config find) ─
    run("git config --global dx.ceo Prime")     # sandbox global
    L8 = spec([
        dict(Command="git config --local --list",
             Tests=[dict(ExitCode=0,
                         StdoutContainsAll=["dx.ceo=Prime"])]),
    ])
    d8 = diagnose(run, L8)
    sus8 = d8["suspects"][0] if d8["suspects"] else None
    desync_said = bool(sus8 and "scope desync" in sus8["current"])
    readme8 = "Set the CEO:\n\n```sh\ngit config get dx.ceo\n```\n"
    roads8 = adjust_roads(readme8, sus8) if sus8 else []
    if roads8:
        run_road(run, roads8[0])
    d8b = diagnose(run, L8)
    check("DX8 global-vs-local key = suspect w/ scope desync "
          "SAID; local set -> green",
          sus8 is not None and desync_said and roads8
          and d8b["green"],
          f"desync said={desync_said}; road="
          f"{roads8[0]['kind'] if roads8 else 'NONE'}; "
          f"green={d8b['green']}")

    # ── DX9: COMPOSE-COMMIT — the transfer, court-dimensioned ───
    run("echo z > zfile.txt")
    L9 = spec([dict(Command="git --no-pager log --oneline",
                    Tests=[dict(StdoutContainsAll=["Z:"])])])
    d9 = diagnose(run, L9)
    readme9 = ("Make a commit whose message starts with Z:\n\n"
               "```md\nnot a command fence\n```\n")
    roads9 = (adjust_roads(readme9, d9["suspects"][0],
                           lesson_title="dx nine")
              if d9["suspects"] else [])
    compose = [r for r in roads9 if r["kind"] == "COMPOSE-COMMIT"]
    if compose:
        run_road(run, compose[0])
    d9b = diagnose(run, L9)
    check("DX9 no told fence — COMPOSE-COMMIT carries the "
          "court's own 'Z:' -> green",
          d9["suspects"] and compose and d9b["green"],
          f"road={compose[0]['lines'][1][:40] if compose else 'NONE'};"
          f" green={d9b['green']}")

    # ── DX10: CAPTURE — command-here + instrument-resolved hash ─
    L10 = spec([dict(Command="cat dxcap.txt",
                     Tests=[dict(ExitCode=0,
                                 StdoutContainsAll=["tree"])])])
    readme10 = ("Print the commit object:\n\n```bash\n"
                "git cat-file -p <hash>\n```\n\nNow capture it:"
                "\n\n```bash\ncatfile-command-here > dxcap.txt"
                "\n```\n")
    d10 = diagnose(run, L10)
    roads10 = (adjust_roads(readme10, d10["suspects"][0])
               if d10["suspects"] else [])
    cap = [r for r in roads10 if r["kind"] == "CAPTURE"]
    tr10 = run_road(run, cap[0]) if cap else []
    d10b = diagnose(run, L10)
    filled = any("[fill" in x[0] for x in tr10)
    resolved = any("[resolve <hash>]" in x[0] for x in tr10)
    check("DX10 command-here filled from the neighbor fence; "
          "<hash> asked of the repo -> green",
          cap and filled and resolved and d10b["green"],
          f"filled={filled}; resolved={resolved}; "
          f"green={d10b['green']}")

    shutil.rmtree(bench, ignore_errors=True)
    npass = sum(checks)
    print(f"\nDIAGNOSIS BATTERY: {npass}/{len(checks)} in "
          f"{time.perf_counter() - t0:.1f}s")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
