"""diagnosis.py — THE DIAGNOSIS COURT + THE ASK ROAD (owner,
2026-07-19, correcting the internal-modelling umbrella):

  "really its being able to model the cause and effect of failure
  modes. there is an expected state, what is different between the
  expected state and the current state that is preventing this
  from working. its evaluating backward. this is the state we are
  in, this is the output. we dont know what will cause that state
  exactly. but we know the initial state. there are only so many
  variables to adjust, and figuring out which ones will work and
  what the state needs to be for everything for that structure to
  work... if you are diagnosing an engine, you are under the
  understanding of the fire triangle, but with an engine you need
  air, spark, fuel, and compression. and you can check each state
  directly."

FORWARD RUNS THE MODEL, DIAGNOSIS RUNS IT BACKWARD.

The REQUIREMENTS MODEL is derived from the court's OWN published
checks (the spec is data; nothing here hand-codes what a lesson
needs). Each failing check is walked backward to the finite menu
of state variables it reads — a commit in the log, a file at a
path, a config key IN THE COURT'S OWN SCOPE, the stage's tension
— and EACH VARIABLE IS COURTED DIRECTLY at its own instrument
(operational access, per variable). Variables whose current
state differs from the expected state are the SUSPECTS.

THE CAUSE-AND-EFFECT MODEL: each variable kind carries its
TRANSFER — the act that moves it (a commit grows the log; a set
writes the key; a told fence writes or captures the file). An
adjustment instantiates the transfer with dimensions read from
the lesson's own text and from the instruments (a `<hash>` slot
is filled by asking the repo, not by guessing — operational
access again). The court then re-rules: the injection
diagnostic — a one-variable wall is confirmed when one
adjustment un-darks it.

THE FIRE-TRIANGLE CLAUSE: when EVERY known variable checks green
and the structure still fails, the requirements model itself is
missing a variable (you hold three, the engine has four — the
config SCOPE was found exactly this way). That residue is not a
defeat — it is a NAMED UNKNOWN, and it opens THE ASK ROAD: the
failure pile is mined against the successes (mine_commonality —
no scream, no ask) and the hole becomes an ask:<name> node,
FUTURE tense, zero belief, wearing its not-yet honestly. A
VERIFIER NEVER REPAIRS WHAT IT CHECKS: this organ names, checks,
and adjusts by told transfers only; it never invents the missing
law.
"""
import re
import time

_SLOT = re.compile(r"<([\w-]+)>")
_HERE = re.compile(r"^[\w-]*command-here\b")
# prose placeholders that reference an artifact from OUTSIDE this
# lesson ("path/to/file/from-before") — no instrument here can
# resolve them; they name a missing capability: memory of what a
# PREVIOUS lesson discovered
PROSE_PATH = re.compile(r"\bpath/to/[\w./-]+|\bfrom-before\b")

# operational access per slot: a slot's value is COURTED at the
# instrument, never guessed. hash = the past tense's own name.
RESOLVERS = {
    "hash": "git rev-parse HEAD",
}


# ---------------------------------------------------------------
# the requirements model — derived from the spec's own checks
# ---------------------------------------------------------------

def _path_tokens(cmd):
    """File-looking tokens read off the command itself (split,
    never regex-over-string — `./quotes/dune.md` stays itself)."""
    toks = []
    for t in cmd.replace("|", " ").replace(">", " ").split():
        t = t.strip("'\";{}")
        if not t or t.startswith(("-", "$", "`")):
            continue
        if "/" in t or re.search(r"\.\w{1,4}$", t):
            if t not in ("git", "bash", "sh", "python3", "python",
                         "false", "true", "..", "."):
                toks.append(t[2:] if t.startswith("./") else t)
    return toks


def _classify(command):
    """The variable KIND a command's checks read — from the
    command's own text (the generic move; never a per-lesson
    list)."""
    c = command.strip()
    head = c.split()[0] if c else ""
    if c.startswith("git log") or re.search(r"git .*log", c):
        return "commit-log"
    if c.startswith("git status"):
        return "tense"
    if c.startswith("git config"):
        return "config-key"
    if head in ("cat", "xxd", "head", "tail", "wc", "ls", "find",
                "grep", "sort", "uniq"):
        return "file"
    return "command"


def _config_bits(cmd):
    """The court's own scope + key, read off its command. The
    SCOPE IS A VARIABLE (found live 2026-07-19: a key set global
    while the court reads --local = the fourth variable)."""
    scope = ("--local" if "--local" in cmd else
             "--global" if "--global" in cmd else "merged")
    m = re.search(r"config (?:get )([\w.]+)", cmd)
    key = m.group(1) if m else None
    return scope, key


def requirements_from_spec(lesson):
    """EVALUATING BACKWARD, step 1: from THEIR court's published
    steps, the finite menu of state variables with their EXPECTED
    states."""
    steps = ((lesson.get("LessonDataCLI") or {}).get("CLIData")
             or {}).get("Steps") or []
    reqs, seen = [], set()
    for s in steps:
        step = s.get("CLICommand")
        if not step:
            continue
        cmd = step.get("Command", "")
        kind = _classify(cmd)
        for t in step.get("Tests", []):
            wants = list(t.get("StdoutContainsAll") or [])
            exitc = t.get("ExitCode")
            if kind == "file":
                for p in _path_tokens(cmd):
                    key = ("file", p)
                    if key in seen:
                        continue
                    seen.add(key)
                    reqs.append(dict(
                        kind="file", name=p, expected="exists",
                        wants=wants, check=f"ls {p}",
                        step_cmd=cmd))
            elif kind == "commit-log":
                for w in wants:
                    key = ("commit-log", w)
                    if key in seen:
                        continue
                    seen.add(key)
                    reqs.append(dict(
                        kind="commit-log", name=w,
                        expected=f"log contains '{w}'", wants=[w],
                        check="git --no-pager log --oneline"))
            elif kind == "config-key":
                scope, cfgkey = _config_bits(cmd)
                key = ("config-key", scope, cfgkey,
                       tuple(wants), exitc)
                if key in seen:
                    continue
                seen.add(key)
                reqs.append(dict(
                    kind="config-key",
                    name=(cfgkey or ",".join(w.split("=")[0]
                                             for w in wants)
                          or "list"),
                    cfgkey=cfgkey, scope=scope,
                    expected=(f"{scope} config has "
                              + (cfgkey or str(wants))),
                    wants=wants, exit=exitc,
                    check=cmd))          # the court's OWN scope
            elif kind == "tense":
                key = ("tense", tuple(wants))
                if key in seen:
                    continue
                seen.add(key)
                reqs.append(dict(
                    kind="tense", name="status",
                    expected=f"tension report says {wants}",
                    wants=wants, check="git status"))
            else:
                key = ("command", cmd)
                if key in seen:
                    continue
                seen.add(key)
                reqs.append(dict(
                    kind="command", name=cmd[:48],
                    expected=(f"exit {exitc}" if exitc is not None
                              else "runs")
                    + (f" + prints {wants}" if wants else ""),
                    wants=wants, check=cmd, opaque=True))
    return reqs


def check_variable(run, var):
    """"and you can check each state directly." — one variable,
    one instrument, one receipt. For a config variable the check
    IS the court's own command (same scope — the instrument, not
    a paraphrase of it); a miss is then probed against the merged
    scope so a scope desync is SAID, not mysterious."""
    out, code = run(var["check"])
    current = out.strip()[:120] or f"(empty, exit {code})"
    if var["kind"] == "file":
        agree = code == 0
        current = "exists" if agree else "ABSENT"
    elif var["kind"] == "config-key":
        agree = (code == (var.get("exit") if var.get("exit")
                          is not None else 0)
                 and all(w in out for w in (var.get("wants")
                                            or [])))
        if not agree:
            probe, _ = run("git config --list")
            missing = ([w for w in (var.get("wants") or [])
                        if w not in out]
                       or ([var["cfgkey"]] if var.get("cfgkey")
                           else []))
            held = [m for m in missing
                    if m and m.split("=")[0] in probe]
            if held:
                current += (" | MERGED SCOPE HOLDS "
                            f"{held} — scope desync")
    elif var["kind"] in ("commit-log", "tense"):
        agree = all(w in out for w in (var.get("wants") or []))
    else:
        agree = code == 0 and all(
            w in out for w in (var.get("wants") or []))
    return dict(var=var, agree=bool(agree), current=current,
                receipt=f"courted `{var['check'][:48]}` "
                        f"-> exit {code}")


def court_spec(run, lesson):
    """THEIR grader's own spec, run faithfully. Green only if
    every check passes; the failing check is named."""
    steps = ((lesson.get("LessonDataCLI") or {}).get("CLIData")
             or {}).get("Steps") or []
    cli = [s["CLICommand"] for s in steps if s.get("CLICommand")]
    if not cli:
        return dict(green=False, why="no CLI test steps",
                    gradeable=False)
    for step in cli:
        out, code = run(step["Command"])
        for t in step.get("Tests", []):
            if t.get("ExitCode") is not None \
                    and code != t["ExitCode"]:
                return dict(green=False, gradeable=True,
                            why=f"exit {code}!={t['ExitCode']} on"
                                f" `{step['Command'][:40]}`",
                            step=step["Command"])
            for need in (t.get("StdoutContainsAll") or []):
                if need not in out:
                    return dict(green=False, gradeable=True,
                                why=f"stdout missing "
                                    f"'{need[:30]}'",
                                step=step["Command"])
            for no in (t.get("StdoutContainsNone") or []):
                if no in out:
                    return dict(green=False, gradeable=True,
                                why=f"stdout has forbidden "
                                    f"'{no[:30]}'",
                                step=step["Command"])
            if t.get("StdoutLinesGt") is not None and \
                    len(out.splitlines()) <= t["StdoutLinesGt"]:
                return dict(green=False, gradeable=True,
                            why="too few lines",
                            step=step["Command"])
    return dict(green=True, gradeable=True, why="all steps green")


def diagnose(run, lesson):
    """THE BACKWARD WALK. Court the structure; if red, derive the
    requirements model and court EVERY variable at its own
    instrument. The differing ones are the SUSPECTS. A file that
    EXISTS while its own step still fails becomes a derived
    file-content suspect (the variable is the content, not the
    presence). All known variables green + still red = THE
    FIRE-TRIANGLE RESIDUE: the model is missing a variable — a
    NAMED UNKNOWN, never a repair."""
    verdict = court_spec(run, lesson)
    if verdict.get("green") or not verdict.get("gradeable"):
        return dict(green=verdict.get("green", False),
                    gradeable=verdict.get("gradeable", True),
                    failing=None, variables=[], suspects=[],
                    named_unknown=False)
    reqs = requirements_from_spec(lesson)
    checks = [check_variable(run, v) for v in reqs
              if not v.get("opaque")]
    # causal order: contents before the acts that record them —
    # a commit stores files, so file suspects adjust first
    suspects = sorted(
        (c for c in checks if not c["agree"]),
        key=lambda c: {"file": 0, "file-content": 0, "tense": 1,
                       "config-key": 2}.get(c["var"]["kind"], 3))
    # derived suspects: the file is there, its step still fails —
    # the CONTENT is the variable ("what the state needs to be")
    fstep = verdict.get("step", "")
    for c in checks:
        v = c["var"]
        if (v["kind"] == "file" and c["agree"]
                and v["name"] in fstep):
            dv = dict(kind="file-content", name=v["name"],
                      expected=(f"content satisfies "
                                f"`{fstep[:36]}` "
                                f"({v.get('wants') or 'exit 0'})"),
                      wants=v.get("wants") or [],
                      check=f"cat {v['name']}")
            suspects.append(dict(var=dv, agree=False,
                                 current="exists, content does "
                                         "not satisfy the step",
                                 receipt="derived: file agrees, "
                                         "its step fails"))
    return dict(green=False, gradeable=True,
                failing=verdict["why"], step=fstep,
                variables=checks, suspects=suspects,
                named_unknown=not suspects)


# ---------------------------------------------------------------
# the cause-and-effect model — what MOVES each variable kind
# ---------------------------------------------------------------

def _fences(readme):
    return re.findall(r"```([a-z]*)\n(.*?)```", readme, re.S)


def _bash_fences(readme):
    return [b.strip() for t, b in _fences(readme)
            if t in ("sh", "bash", "")]


def adjust_roads(readme, suspect, lesson_title=""):
    """"there are only so many variables to adjust" — the menu of
    moves for ONE suspect. Every road is an instantiation of the
    variable's TRANSFER (the cause that effects it), dimensioned
    from the lesson's own text and the court's own expected
    values — never from thin air. `<slot>` and `*-command-here`
    markers are DATAFLOW, resolved at run time from instruments
    and neighbor fences (operational access)."""
    var = suspect["var"]
    roads = []
    fences = _fences(readme)
    bash = _bash_fences(readme)
    if var["kind"] in ("file", "file-content"):
        name = var["name"]
        base = name.split("/")[-1]
        # (a) TOLD-FILE: the readme names the file; the next
        # fence is its contents (the git course's own shape)
        pos = readme.find(base)
        if pos >= 0:
            fence = re.search(r"```[a-z]*\n(.*?)```",
                              readme[pos:], re.S)
            if fence and not _HERE.search(fence.group(1).strip()):
                roads.append(dict(
                    kind="TOLD-FILE",
                    write=(name, fence.group(1).strip() + "\n"),
                    lines=[], slots=[], fences=bash,
                    why=f"readme names {base}; next fence = "
                        f"contents"))
        # (b) CAPTURE: a told fence redirects into the path —
        # its placeholders resolve from neighbors + instruments
        # (redirection judged on a slot-stripped copy: `<hash>`
        # carries a `>` of its own — the one-character ghost)
        for b in bash:
            if ">" in _SLOT.sub("", b) and name in b:
                lines = [ln.strip() for ln in b.split("\n")
                         if ln.strip()
                         and not ln.startswith("#")
                         and not ln.startswith(">")]
                roads.append(dict(
                    kind="CAPTURE", lines=lines, fences=bash,
                    slots=sorted({s for ln in lines
                                  for s in _SLOT.findall(ln)}),
                    why=f"told fence captures into {name}"))
    elif var["kind"] == "commit-log":
        frag = (var.get("wants") or [""])[0]
        # fence road first (the lesson's own commands)
        for b in bash:
            if "git commit" in b:
                lines = [ln.strip() for ln in b.split("\n")
                         if ln.strip()
                         and not ln.startswith("#")]
                roads.append(dict(
                    kind="TOLD-CMDS", lines=lines, fences=bash,
                    slots=sorted({s for ln in lines
                                  for s in _SLOT.findall(ln)}),
                    why="told block commits (grows the log)"))
        # the transfer itself: commit = candidate -> past (his
        # tense tracker's own operation), the message dimensioned
        # by the court's OWN expected fragment
        if frag:
            slug = re.sub(r"[^\w ]", "",
                          lesson_title or "diagnosis")[:32]
            roads.append(dict(
                kind="COMPOSE-COMMIT", fences=bash,
                lines=["git add -A",
                       f'git commit -m "{frag} {slug}"'],
                slots=[],
                why=f"commit is the transfer that grows the log; "
                    f"the message carries the court's own "
                    f"'{frag}'"))
    elif var["kind"] == "config-key":
        key = var.get("cfgkey")
        vals = []
        for w in (var.get("wants") or []):
            if "=" in w:
                k, v = w.split("=", 1)
                fk = re.search(r"([\w]+\.[\w]*" + re.escape(k)
                               + r")", readme)
                vals.append((fk.group(1) if fk else k, v))
        if key and not vals:
            # value told in prose near the key ("set K to V")
            m = re.search(re.escape(key)
                          + r"[^\n]*?(?:to|=)\s+[\"'`]?"
                          + r"([\w .$-]+?)[\"'`.]?(?:\n|$)",
                          readme)
            if m:
                vals.append((key, m.group(1).strip()))
        scope = var.get("scope", "merged")
        flag = "" if scope in ("merged", "--local") else \
            f" {scope}"
        # old-style set (portable to every git): plain = local,
        # which is the court's own scope for --local and merged
        lines = [f'git config{flag} {k} "{v}"'
                 for k, v in vals]
        if lines:
            roads.append(dict(
                kind="CONFIG-SET", lines=lines, slots=[],
                fences=bash,
                why=f"set writes the key in the court's own "
                    f"scope ({scope})"))
    elif var["kind"] == "tense":
        for b in bash:
            if "git add" in b or "git status" in b:
                lines = [ln.strip() for ln in b.split("\n")
                         if ln.strip()
                         and not ln.startswith("#")]
                roads.append(dict(
                    kind="TOLD-CMDS", lines=lines, slots=[],
                    fences=bash,
                    why="told block moves the tenses"))
    return roads


def run_road(run, road, write_file=None, cwd_prefix="",
             admit=None):
    """Run one road. TOLD-FILE roads write their file (write_file
    (name, text) -> bool, supplied by the flight). Command lines
    run one by one: a bare `cd` HOLDS for the block; a `<slot>`
    fills from the previous line's single-token output, else from
    its instrument RESOLVER (operational access, receipted); a
    `*-command-here` placeholder takes the nearest OTHER told
    fence's command, its own slots resolved first. `admit` vets
    each line AFTER resolution, at the moment of truth (a
    placeholder is only judgeable once it is a command); an
    unadmitted line is skipped WITH its receipt. Returns the
    transcript [(line-as-run, out, code)...]."""
    transcript = []
    if road.get("write") and write_file:
        name, text = road["write"]
        ok = write_file(name, text)
        transcript.append((f"write {name}",
                           "written" if ok else "WRITE FAILED",
                           0 if ok else 1))
    prev, cd = "", cwd_prefix

    def _resolve_slots(ln):
        nonlocal prev
        for slot in _SLOT.findall(ln):
            tok = prev.strip()
            if tok and len(tok.split()) == 1 \
                    and "\n" not in tok:
                ln = ln.replace(f"<{slot}>", tok)
            elif slot in RESOLVERS:
                out, code = run(RESOLVERS[slot])
                tok = out.strip()
                if code == 0 and tok \
                        and len(tok.split()) == 1:
                    transcript.append(
                        (f"[resolve <{slot}>] "
                         f"{RESOLVERS[slot]}", tok[:40], 0))
                    ln = ln.replace(f"<{slot}>", tok)
        return ln

    for ln in road.get("lines", []):
        m = _HERE.search(ln)
        if m:
            donor = None
            for b in road.get("fences", []):
                cand = [x.strip() for x in b.split("\n")
                        if x.strip()
                        and not x.startswith((">", "#"))]
                if cand and not _HERE.search(cand[0]) \
                        and ">" not in _SLOT.sub("", cand[0]):
                    donor = cand[0]
            if donor:
                donor = _resolve_slots(donor)
                ln = ln.replace(m.group(0), donor)
                transcript.append(
                    (f"[fill {m.group(0)}]", donor[:60], 0))
        ln = _resolve_slots(ln)
        if ln.startswith("cd ") and "&&" not in ln:
            cd = (f"{cd} && {ln}" if cd else ln)
            transcript.append((ln, "(held for the block)", 0))
            continue
        if admit and not admit(ln):
            transcript.append((ln, "(not admitted — "
                                   "allowlist refusal)", 126))
            continue
        out, code = run(f"{cd} && {ln}" if cd else ln)
        transcript.append((ln, out.strip()[:120], code))
        prev = out
    return transcript


# ---------------------------------------------------------------
# the ask road — the fire-triangle residue made speakable
# ---------------------------------------------------------------

def featurize_darks(mind):
    """His own study ledger, said as flat records the miner can
    eat — features parsed from each record's OWN text (the bug
    string, the road string), never a hand-kept category list.
    Returns (records, failed, titles)."""
    records, failed, titles = [], [], []
    for n in sorted(list(mind.net.meta)):
        if not str(n).startswith("lesson:"):
            continue
        st = mind.net.get_meta(n, "status")
        if st not in ("PASSED", "DARK"):
            continue
        bug = mind.net.get_meta(n, "bug") or ""
        road = mind.net.get_meta(n, "road") or ""
        r = dict(road_family=(road.split(":")[0].split(" ")[0]
                              or "NONE") if road else "NONE")
        m = re.match(r"(stdout missing|exit|stdout has forbidden|"
                     r"too few|no CLI)", bug)
        r["check_kind"] = m.group(1) if m else (
            "none" if not bug else "other")
        mc = re.search(r"`(\S+)", bug)
        r["cmd_head"] = mc.group(1).split("/")[-1] if mc else "-"
        r["path_zone"] = ("/tmp" if "/tmp/" in bug else
                          ("repo" if bug else "-"))
        records.append(r)
        failed.append(st == "DARK")
        titles.append(mind.net.get_meta(n, "title"))
    return records, failed, titles


def ask_report(mind, name, hole, evidence,
               kind="missing-variable"):
    """THE ASK. A future-tense candidate node — kin to the goal
    tree's dark leaves ("a dark leaf is an answer: this branch
    needs a law nobody holds"). It wears its not-yet honestly:
    status OPEN, zero belief, evidence receipts attached. The
    answer, when it comes, is DATA through the telling/vet doors
    (who-stamped, told-unverified, validate later) — never a
    repair by this organ. Re-filing supersedes, never erases."""
    node = f"ask:{name}"
    old = mind.net.get_meta(node, "active")
    if old is not None:
        chain = mind.net.get_meta(node, "superseded") or []
        chain.append(dict(record=old,
                          why="re-diagnosed; newer ask supersedes"
                              " (kept, never erased)"))
        mind.net.set_meta(node, "superseded", chain)
    ask = dict(status="OPEN", tense="future", kind=kind,
               hole=hole, evidence=evidence,
               stamp=time.strftime("%Y-%m-%d %H:%M:%S"))
    mind.net.set_meta(node, "active", ask)
    mind.net.add_door("world:asks", node, tag="in:asks")
    mind.record_finding("ask", name, ask_kind=kind, hole=hole,
                        evidence=evidence)
    return ask


def ask_from_darks(mind, name):
    """The null-gated ask: mine the study ledger's darks against
    its passes (mine_commonality — the label-shuffle null rules).
    NO SCREAM = NO ASK: if nothing is named past the null, the
    refusal is the receipt and no ask fires. A named signature =
    the hole's shape WITH evidence = a self-generated curriculum
    request."""
    records, failed, titles = featurize_darks(mind)
    sig = mind.mine_commonality(records, failed,
                                name=f"ask-mine:{name}")
    if not sig.get("named"):
        return dict(asked=False, why=sig.get("why", "no scream"),
                    mined=sig)
    k, v, ex = sig["named"][0]
    hole = (f"the failures share {k}={v} (excess {ex:.2f} past "
            f"the shuffled-label null {sig['threshold']:.2f}) — "
            f"the successes lack it")
    dark_titles = [t for t, f in zip(titles, failed) if f]
    ask = ask_report(mind, name, hole,
                     evidence=dict(named=sig["named"][:5],
                                   n_fail=sig["n_fail"],
                                   n_succ=sig["n_succ"],
                                   darks=dark_titles[:10]),
                     kind="missing-skill")
    return dict(asked=True, ask=ask, mined=sig)


def say_diagnosis(d):
    """The diagnosis said plainly (a raw report, not generated
    speech — the corpus does not yet hold these words, and an
    unsayable hole ships its raw report honestly)."""
    if d.get("green"):
        return "green — nothing to diagnose"
    L = [f"failing check: {d['failing']}"]
    for c in d.get("variables", []):
        v = c["var"]
        mark = "agrees" if c["agree"] else "DIFFERS"
        L.append(f"  [{mark:7}] {v['kind']}:{v['name'][:36]} — "
                 f"expected {v['expected'][:48]}; current "
                 f"{c['current'][:72]}")
    for c in d.get("suspects", []):
        if c["var"]["kind"] == "file-content":
            L.append(f"  [DERIVED] file-content:"
                     f"{c['var']['name'][:36]} — "
                     f"{c['current'][:60]}")
    if d.get("named_unknown"):
        L.append("  ALL KNOWN VARIABLES AGREE AND IT STILL FAILS"
                 " — the model is missing a variable (the fire"
                 " triangle meets the engine). This is an ask.")
    else:
        L.append(f"  suspects: {len(d['suspects'])} — adjust one,"
                 f" re-court (the injection diagnostic)")
    return "\n".join(L)
