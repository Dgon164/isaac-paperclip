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
                                  compose_print_main,
                                  compose_transform,
                                  compose_chain_main, mint,
                                  minted_shapes, minted_names,
                                  record_attempt, ledger_set,
                                  ledger_get, ledger_report,
                                  TOOLSET)

WSL = ["wsl.exe", "-d", "Ubuntu", "-u", "root", "--", "bash", "-lc"]
WORKDIR = "/root/bookbot"   # overridable: --workdir=/root/x
ALLOW = re.compile(
    r"^(mkdir |curl (-s?L )?[\"']?https://storage\.googleapis\.com"
    r"|uv |git |echo |printf |python3? |ls|head |cat |wc |touch "
    r"|cd |rm |mv |cp |xxd |sort|uniq|grep |find )")
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def wsl(cmd, timeout=120):
    # ONE invocation, command shipped base64 — wsl.exe re-splits
    # quoted argv (cut -d ' ' arrived mangled) and temp-script
    # relays go stale under flaky session starts; base64 has no
    # quotes and nothing shared to race
    import base64
    b64 = base64.b64encode(cmd.encode()).decode()
    out = subprocess.run(
        WSL + [f"echo {b64} | base64 -d | bash"],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout)
    return out.stdout + out.stderr


def fetch(path):
    out = subprocess.run(
        WSL + [f"/root/go/bin/lessonfetch {path}"],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=60)
    return json.loads(out.stdout)


def _run_cmd(command):
    import base64
    b64 = base64.b64encode(
        f"cd {WORKDIR} && {command}".encode()).decode()
    out = subprocess.run(
        WSL + [f"echo {b64} | base64 -d | bash"],
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
        if os.environ.get("BOOTDEV_DEBUG"):
            print(f"    [court] wd={WORKDIR} "
                  f"cmd={step['Command'][:40]!r} exit={code} "
                  f"out={out[:60]!r}")
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


def read_file(name):
    out = subprocess.run(WSL + [f"cat {WORKDIR}/{name}"],
                         capture_output=True, text=True,
                         encoding="utf-8", errors="replace",
                         timeout=60)
    return out.stdout


def write_file(name, src):
    d = os.path.dirname(name)
    if d:
        wsl(f"mkdir -p {WORKDIR}/{d}")
    p = subprocess.run(WSL + [f"cat > {WORKDIR}/{name}"],
                       input=src, capture_output=True, text=True,
                       encoding="utf-8")
    return p.returncode == 0


def write_artifact(defs, main_body):
    src = ("\n\n".join(defs) + "\n\n" + main_body) if defs \
        else main_body
    return write_file("main.py", src)


def told_commands(readme):
    """Whole ```sh blocks, one script each — a cd inside a block
    holds for the block (the lesson's own sequence). A block is
    admitted only if EVERY line is on the allowlist."""
    blocks = []
    for block in re.findall(r"```(?:sh|bash)\n(.*?)```", readme,
                            re.S):
        lines = [ln.strip() for ln in block.strip().split("\n")
                 if ln.strip() and not ln.strip().startswith("#")]
        if lines and all(ALLOW.match(ln) for ln in lines):
            blocks.append(" && ".join(lines))
    return blocks


def main():
    global WORKDIR
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cap = 20
    for a in sys.argv[1:]:
        if a.startswith("--max"):
            cap = int(a.split("=")[-1]) if "=" in a else cap
        if a.startswith("--workdir="):
            WORKDIR = a.split("=", 1)[1]
            # Git Bash (MSYS) rewrites unix-looking args into
            # Windows paths (--workdir=/root/x arrived as
            # C:/Program Files/Git/root/x — an hour of ghost
            # hunting, 2026-07-19); strip the mangle
            m = re.search(r"[A-Za-z]:.*?(/root/.*)$", WORKDIR)
            if m:
                WORKDIR = m.group(1)
    course = args[0] if args else \
        "094fd7d4-ec78-4202-96ca-c5f79fc332d2"

    from isaac_store.sparring import IsaacAccount
    home = os.path.join(os.path.expanduser("~"), "Documents",
                        "isaac_home")
    shutil.copy2(os.path.join(home, "mind.isaac"),
                 os.path.join(home, "mind.isaac.bak"))
    acct = IsaacAccount(home, mod)
    mind = acct.mind

    if "--report" in sys.argv[1:]:
        print("THE STUDY LEDGER — tracked and checked:")
        print(ledger_report(mind))
        return

    if "--diagnose" in sys.argv[1:]:
        # THE DIAGNOSIS FLIGHT (owner 2026-07-19: "its evaluating
        # backward... there are only so many variables to adjust,
        # and you can check each state directly"). Standing darks
        # only: court the structure; walk the requirements model
        # backward; court each variable at its own instrument;
        # adjust ONE suspect by the lesson's own told road; the
        # court re-rules. All-known-variables-green residue = the
        # fire-triangle clause = an ASK, never a repair.
        from isaac_store.diagnosis import (diagnose, adjust_roads,
                                           run_road, say_diagnosis,
                                           ask_from_darks,
                                           ask_report, PROSE_PATH)
        c = fetch(f"/v1/courses/{course}")
        print(f"DIAGNOSIS FLIGHT: {c['Title']} — evaluating "
              f"backward on the standing darks\n")
        transcript = []
        for ch in c["Chapters"]:
            for les in (ch.get("Lessons") or []):
                uuid, title = les["UUID"], les["Title"]
                led = ledger_get(mind, uuid)
                if not led or led["status"] not in ("DARK",
                                                    "RETRY"):
                    continue
                L = fetch(uuid)["Lesson"]
                readme = (L.get("LessonDataCLI") or {}).get(
                    "Readme", "") or ""
                d = diagnose(_run_cmd, L)
                print(f"  {title}:")
                print("    " + say_diagnosis(d)
                      .replace("\n", "\n    "))
                if d["green"]:
                    ok = submit(uuid)
                    ledger_set(mind, uuid, title, "PASSED",
                               road="AS-IS (diagnosis: the bench "
                                    "already agrees)")
                    transcript.append((title, "PASS", "as-is"))
                    continue
                # bounded injection rounds: one suspect at a time,
                # told roads only, progress or stop
                for _round in range(4):
                    if d["green"] or not d["suspects"]:
                        break
                    sus = d["suspects"][0]
                    roads = adjust_roads(readme, sus,
                                         lesson_title=title)
                    if not roads:
                        print(f"    (no told road moves "
                              f"{sus['var']['kind']}:"
                              f"{sus['var']['name'][:24]})")
                        break
                    before = [x["var"]["name"]
                              for x in d["suspects"]]
                    moved = False
                    for road in roads:
                        run_road(_run_cmd, road,
                                 write_file=write_file,
                                 admit=lambda ln: bool(
                                     ALLOW.match(ln)))
                        d = diagnose(_run_cmd, L)
                        record_attempt(
                            mind, title,
                            f"DIAGNOSIS: adjust "
                            f"{sus['var']['kind']}:"
                            f"{sus['var']['name'][:24]} "
                            f"({road['why'][:32]})",
                            dict(green=d["green"],
                                 why=(d.get("failing")
                                      or "all steps green")))
                        now = [x["var"]["name"]
                               for x in d["suspects"]]
                        if d["green"] or now != before:
                            moved = True
                            print(f"    adjusted {sus['var']['kind']}"
                                  f":{sus['var']['name'][:24]} — "
                                  f"{'GREEN' if d['green'] else 'progress'}")
                            break
                    if not moved:
                        break
                if d["green"]:
                    ok = submit(uuid)
                    road_s = ("DIAGNOSIS: backward walk + told "
                              "adjustment")
                    ledger_set(mind, uuid, title, "PASSED",
                               road=road_s)
                    transcript.append((title, "PASS", road_s
                                       + ("" if ok else
                                          " (submit unconfirmed)")))
                    print(f"  [PASS] {title} — cured by "
                          f"adjustment")
                else:
                    why = ("MODEL MISSING A VARIABLE (fire "
                           "triangle)" if d.get("named_unknown")
                           else "suspects remain: " + ",".join(
                               x["var"]["name"][:16]
                               for x in d["suspects"]))
                    ledger_set(mind, uuid, title, "DARK",
                               bug=(d.get("failing") or "")[:60])
                    transcript.append((title, "DARK", why))
                    print(f"  [DARK] {title} — {why[:52]}")
                    # THE RESIDUE ASK: a dark whose roads carry a
                    # prose reference to another lesson's artifact
                    # ("path/to/file/from-before"), or a suspect
                    # no told road moves — each is a NAMED hole,
                    # filed as his ask (future tense, zero
                    # belief), never guessed at
                    for sus in d["suspects"]:
                        rds = adjust_roads(readme, sus,
                                           lesson_title=title)
                        toks = sorted({m for r in rds
                                       for ln in r.get("lines", [])
                                       for m in
                                       PROSE_PATH.findall(ln)})
                        if toks:
                            hole = (f"the told road references "
                                    f"{toks} — artifact(s) from a "
                                    f"previous lesson I do not "
                                    f"hold (cross-lesson memory)")
                        elif not rds:
                            hole = (f"no told road moves "
                                    f"{sus['var']['kind']}:"
                                    f"{sus['var']['name'][:32]} — "
                                    f"the transfer is not in the "
                                    f"lesson's text or not in my "
                                    f"menu")
                        else:
                            continue
                        a = ask_report(
                            mind, f"lesson:{title[:32]}", hole,
                            evidence=dict(
                                lesson=title,
                                failing=d.get("failing"),
                                suspect=sus["var"]["name"]))
                        print(f"    ASK filed: {hole[:64]}")
                time.sleep(2)
        ask = ask_from_darks(mind, "gitcourse")
        if ask["asked"]:
            print(f"\n  THE ASK (self-generated): "
                  f"{ask['ask']['hole']}")
        else:
            print(f"\n  no ask fired: {ask['why'][:64]}")
        acct._journal(dict(
            kind="diagnosis",
            stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            course=c["Title"],
            transcript=[f"{s}: {t} ({w[:60]})"
                        for t, s, w in transcript],
            ask=(ask.get("ask") if ask.get("asked")
                 else ask.get("why"))))
        mind.save(acct.mind_path)
        p = sum(1 for _t, s, _w in transcript if s == "PASS")
        print(f"\nDIAGNOSIS DONE: {p} cured, "
              f"{len(transcript) - p} still dark of "
              f"{len(transcript)}; journal + mind saved.")
        return

    # THE BENCH PERSISTS (owner: "he seems to start from the
    # beginning every time") — his repo is study state; only the
    # missing pieces are initialized, never a wipe
    wsl(f"mkdir -p {WORKDIR}")
    if "bookbot" in WORKDIR:
        wsl(f"mkdir -p {WORKDIR}/books")
        wsl(f"cd {WORKDIR} && [ -f books/frankenstein.txt ] || "
            f"curl -sL https://storage.googleapis.com/qvault-"
            f"webapp-dynamic-assets/course_assets/frankenstein.txt"
            f" -o books/frankenstein.txt", timeout=180)
        wsl(f"[ -f {WORKDIR}/main.py ] || echo "
            f"'print(\"placeholder\")' > {WORKDIR}/main.py")

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
            # THE LEDGER FIRST — never start from the beginning
            led = ledger_get(mind, uuid)
            if led and led["status"] == "PASSED":
                # THE TRAJECTORY LAW (the thrash of 2026-07-19
                # taught it): a cumulative course's specs CONFLICT
                # across time — one main.py cannot satisfy them
                # all at once. A submitted pass is a HISTORICAL
                # FACT, never re-courted against a bench that has
                # rightly moved on.
                transcript.append((title, "PASS",
                                   f"ledger: passed via "
                                   f"{led['road'][:36]}"))
                print(f"  [done] {title} — ledger (historical "
                      f"fact, not re-courted)")
                continue
            elif led and led["status"] == "DARK" \
                    and set(led["toolset"]) >= set(TOOLSET):
                # one cheap reality-check before trusting memory —
                # the bench may have evolved past the dark (the
                # replay-court spirit)
                L = fetch(uuid)["Lesson"]
                v = spec_court(L)
                if v.get("green"):
                    ok = submit(uuid)
                    ledger_set(mind, uuid, title, "PASSED",
                               road="AS-IS (bench evolved past "
                                    "the standing bug)")
                    transcript.append((title, "PASS",
                                       "AS-IS — bench evolved"))
                    print(f"  [PASS] {title} — bench evolved past "
                          f"the standing bug")
                    continue
                transcript.append((title, "DARK",
                                   f"ledger: dark, toolset "
                                   f"unchanged — standing bug: "
                                   f"{led['bug'][:40]}"))
                print(f"  [dark] {title} — ledger: toolset "
                      f"unchanged, not re-courting "
                      f"(check said: {v.get('why', '?')[:48]})")
                continue
            L = fetch(uuid)["Lesson"] if not (
                led and led["status"] == "PASSED") else L
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
            snap = read_file("main.py")

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
            # road 1 — the readme's own told commands (block-wise,
            # every line allowlisted; a cd holds within its block)
            if road is None:
                ran = [b[:40] for b in told_commands(readme)
                       if wsl(f"cd {WORKDIR} && {b}",
                              timeout=180) is not None]
                if ran:
                    if spec_court(L)["green"]:
                        road = f"TOLD-CMDS ({len(ran)})"
                    else:
                        # THE BENCH FOLLOWS THE STUDENT: a lesson
                        # that moves into a new repo dir moves the
                        # bench — with the receipt
                        sub = wsl(f"cd {WORKDIR} && ls -d */ "
                                  f"2>/dev/null | head -3").split()
                        for sd in sub:
                            cand = f"{WORKDIR}/{sd.rstrip('/')}"
                            if ".git" in wsl(f"ls -a {cand}"):
                                old = WORKDIR
                                WORKDIR = cand
                                if spec_court(L)["green"]:
                                    road = (f"TOLD-CMDS ({len(ran)})"
                                            f" — bench moved into "
                                            f"{sd.rstrip('/')}")
                                    break
                                WORKDIR = old
            # road 1.4 — TOLD-FILE (the git course's prose shape:
            # "Create a file ... called `X` and add the following"
            # + the next fenced block as the contents — the lesson
            # tells both the name and the text)
            if road is None:
                mfile = re.search(r"(?:called|named) `([\w./-]+)`",
                                  readme)
                if mfile and "." in mfile.group(1):
                    pos = readme.find(mfile.group(0))
                    fence = re.search(r"```[a-z]*\n(.*?)```",
                                      readme[pos:], re.S)
                    if fence:
                        write_file(mfile.group(1),
                                   fence.group(1).strip() + "\n")
                        for b in told_commands(readme):
                            wsl(f"cd {WORKDIR} && {b}",
                                timeout=180)
                        if spec_court(L)["green"]:
                            road = (f"TOLD-FILE("
                                    f"{mfile.group(1)}) + "
                                    f"told-cmds")
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
                targets = (new_funcs[:1] if new_funcs
                           else minted_names(mind))
                for target in targets:
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
                # road 2.4 — MODULE-SPLIT: the readme tells the
                # import structure ("from stats import ..."); the
                # named module receives his minted shape, main
                # imports it back — every move readme-told
                imp = re.search(r"from (\w+) import (\w+)", readme)
                if road is None and imp:
                    modname = imp.group(1)
                    import ast as _ast
                    try:
                        tree = _ast.parse(snap)
                        fns = [n for n in tree.body if isinstance(
                            n, _ast.FunctionDef)
                            and n.name not in ("main",)
                            and "open(" not in _ast.unparse(n)]
                        rest = [n for n in tree.body
                                if n not in fns]
                        if fns:
                            moved = "\n\n".join(
                                _ast.unparse(n) for n in fns)
                            names = ", ".join(n.name for n in fns)
                            write_file(f"{modname}.py",
                                       moved + "\n")
                            newmain = (f"from {modname} import "
                                       f"{names}\n\n"
                                       + "\n\n".join(
                                           _ast.unparse(n)
                                           for n in rest) + "\n")
                            write_file("main.py", newmain)
                            v = spec_court(L)
                            rec = (f"MODULE-SPLIT({modname}.py <- "
                                   f"{names}) + IMPORT-FROM-HINT")
                            record_attempt(mind, title, rec, v)
                            if v["green"]:
                                road = "COMPOSE: " + rec
                                snap = read_file("main.py")
                            else:
                                bugs.append(v.get("why", ""))
                                write_artifact([], snap)
                    except SyntaxError:
                        pass
                # road 2.5 — transform chain: METHOD-FROM-HINT +
                # BUILTIN-LEN + CALL-BIND + TEMPLATE-FILL (all
                # told by the readme or born-declared)
                if road is None and got.get("hints") \
                        and known_paths:
                    wants_n = bool(re.search(
                        r"number of|count", got["assignment"],
                        re.I))
                    fname = None
                    mnoun = re.search(
                        r"number of (\w+)", got["assignment"],
                        re.I)
                    if mnoun:
                        fname = f"count_{mnoun.group(1)}"
                    fname = (got["funcs"] or [fname or
                             "transform"])[0]
                    if fname == "main":
                        fname = "transform"
                    tfs = compose_transform(
                        fname, got["arg"] or "text",
                        got["hints"], wants_n)
                    tmpl = (got.get("templates") or [None])[0]
                    prior = minted_names(mind)
                    for tf in tfs:
                        steps = []
                        if prior:
                            steps.append((prior[0],
                                          known_paths[0]))
                        steps.append((fname, None))
                        mn = compose_chain_main(steps, tmpl,
                                                got["literals"])
                        write_artifact(
                            minted_shapes(mind) + [tf["code"]], mn)
                        v = spec_court(L)
                        rec = (tf["receipt"]
                               + " + CALL-BIND chain"
                               + (" + TEMPLATE-FILL" if tmpl
                                  else ""))
                        record_attempt(mind, title, rec, v)
                        if v["green"]:
                            road = "COMPOSE: " + rec[:60]
                            mint(mind, fname, tf["code"],
                                 tf["receipt"], container,
                                 f"boot.dev spec green ({title})")
                            snap = read_file("main.py")
                            break
                        bugs.append(v.get("why", ""))
                        write_artifact([], snap)
                if road is None and bugs:
                    print(f"         (bug-detection: {len(bugs)} "
                          f"candidates courted+rolled back; last: "
                          f"{bugs[-1][:44]})")
            if road:
                ok = submit(uuid)
                ledger_set(mind, uuid, title, "PASSED", road=road)
                transcript.append((title, "PASS",
                                   road + ("" if ok else
                                           " (run green; submit "
                                           "unconfirmed)")))
                print(f"  [PASS] {title} — {road}"
                      + ("" if ok else "  [submit?]"))
            else:
                ledger_set(mind, uuid, title, "DARK",
                           bug=v.get("why", ""))
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
