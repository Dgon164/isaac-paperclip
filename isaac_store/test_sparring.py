"""test_sparring.py — the sparring harness, gated deterministically.

The live model is a PROBE (experiments/sparring_probe.py); this
battery proves the harness with a scripted stub partner: honest
utterances (opener / admitted fragment / silence — never faked
fluency), physical budgets, transcript-as-monitoring, the harvest
road (model words -> null-gated lessons), and clean refusal when no
partner is reachable.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
import isaac as mod                                    # noqa: E402
from isaac_store.sparring import (OllamaPartner, harvest,      # noqa: E402
                                  frontier_curriculum, isaac_says,
                                  read_failures, run_drill_flow,
                                  run_session)

PASS, FAIL = 0, 0


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


class StubPartner:
    """A scripted partner: teaches a tiny regularity (word X is
    always answered with word Y) so the harvest has something real
    to admit."""

    def __init__(self, script, max_calls=50):
        self.script = script
        self.max_calls = max_calls
        self.calls = 0

    def say(self, messages):
        if self.calls >= self.max_calls:
            return None
        r = self.script[self.calls % len(self.script)]
        self.calls += 1
        return r


SCEN = dict(opener="i am trying to learn english .",
            system="(stub)")


def main():
    # ── 1. honest utterances: empty mind speaks only silence ─────
    m = mod.Isaac()
    utter, src = isaac_says(m, "hello there , how are you ?")
    check("empty mind: silence, never faked fluency",
          utter is None and src == "silence", f"source={src}")

    # ── 2. a session runs: opener first, then honest turns ───────
    stub = StubPartner(["hello . water is a word . say water .",
                        "good . food is a word . say food ."])
    tr = run_session(m, stub, SCEN, turns=4)
    isaac_turns = [t for t in tr if t["who"] == "isaac"]
    check("transcript: isaac opens with the scenario seed",
          isaac_turns[0]["text"] == SCEN["opener"]
          and isaac_turns[0]["source"] == "opener",
          isaac_turns[0]["text"])
    check("empty mind converses in honest silence ('...')",
          all(t["text"] == "..." for t in isaac_turns[1:]),
          f"{len(isaac_turns) - 1} silent turns")

    # ── 3. budgets are physical: exhaustion = clean stop ─────────
    tight = StubPartner(["a b c ."], max_calls=2)
    tr2 = run_session(mod.Isaac(), tight, SCEN, turns=10)
    check("budget spent -> clean stop, marked in the transcript",
          tr2[-1]["who"] == "budget"
          and sum(1 for t in tr2 if t["who"] == "partner") == 2,
          f"partner turns={sum(1 for t in tr2 if t['who']=='partner')}")

    # ── 4. the harvest: a planted regularity is admitted ─────────
    # partner alternates: mentions of 'water' are ALWAYS followed by
    # a turn containing 'drink'; decoy turns vary freely
    script = []
    for i in range(30):
        script.append(f"water is word {i} in my book .")
        script.append(f"you drink it every day number {i} .")
        script.append(f"random other line about topic {i} .")
    long_stub = StubPartner(script, max_calls=90)
    m3 = mod.Isaac()
    tr3 = run_session(m3, long_stub, SCEN, turns=90)
    fd, cpath = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    n_pairs, before, after, learned, _ = harvest(
        m3, [tr3], feats={"water", "drink"}, corpus_path=cpath)
    heard_water = learned.get("heard:water", "")
    check("harvest: planted 'water -> drink' admitted past the null",
          "drink" in heard_water,
          f"pairs={n_pairs}, heard:water -> {heard_water!r}")
    check("the corpus file is kept (auditable, re-learnable)",
          os.path.getsize(cpath) > 0)

    # ── 5. and now he can SAY it: fragment, tagged as learned ────
    utter, src = isaac_says(m3, "here is water .")
    check("what was admitted is speakable, tagged learned-fragment",
          utter is not None and "drink" in utter
          and src == "learned-fragment", f"{utter!r} ({src})")
    os.unlink(cpath)

    # ── 6. no partner: reachable() refuses cleanly ────────────────
    ghost = OllamaPartner("nosuchmodel",
                          url="http://127.0.0.1:9")   # dead port
    check("unreachable partner: clean False, no hang, no crash",
          ghost.reachable() is False)

    # ── 7. THE ISAAC ACCOUNT: his practice is his life ────────────
    # (owner: "perhaps we should have an isaac user account") — the
    # same Isaac tomorrow that he was today: mind, corpus, journal
    # persist across logins; practice accumulates across sessions.
    import shutil
    from isaac_store.sparring import IsaacAccount
    home = tempfile.mkdtemp()
    acct = IsaacAccount(home, mod)
    # the drill must be a real CONTINGENCY: 'drink' follows 'water'
    # lines, not every line (a word in every response has zero excess
    # and the null rightly refuses it — first stub caught by its own
    # battery)
    dscript = []
    for i in range(40):
        dscript.append(f"water is a word i like number {i} .")
        dscript.append(f"you drink it every day friend {i} .")
        dscript.append(f"unrelated filler about topic {i} .")
    drill = StubPartner(dscript, max_calls=300)
    prog = acct.practice(drill, SCEN, sessions=3, turns=10)
    check("practice loop: sessions journaled, transcripts kept",
          acct.sessions_so_far() == 3 and len(os.listdir(
              os.path.join(home, "transcripts"))) == 3,
          f"journal entries={acct.sessions_so_far()}")
    grew = prog[-1]["fragments_after"] > 0
    check("accumulation: repetition crossed the null within 3 sessions",
          grew, f"fragments over sessions: "
          f"{[p['fragments_after'] for p in prog]}")

    # log out, log back in: the SAME Isaac
    acct2 = IsaacAccount(home, mod)
    check("re-login: same mind (fragments persisted)",
          acct2.fragments() == prog[-1]["fragments_after"]
          and acct2.sessions_so_far() == 3,
          f"fragments={acct2.fragments()}")
    utter, src = isaac_says(acct2.mind, "here is water .")
    check("what yesterday's practice earned is speakable today",
          utter is not None and src == "learned-fragment",
          f"{utter!r}")
    shutil.rmtree(home, ignore_errors=True)

    # ── 8. THE CORRECTION LOOP (owner: correction IS language's
    #      residual — fail gets the should-have-said, pass gets the
    #      better version; wrong kept; corrected contexts REUSED) ──
    from isaac_store.sparring import (apply_correction, isaac_says as
                                      says, parse_tutor,
                                      run_tutored_session)

    class StubTutor:
        """Scripted tutor: greets, corrects, then repeats the same
        context so reuse is testable."""

        def __init__(self):
            self.calls = 0
            self.max_calls = 50

        def say(self, messages):
            self.calls += 1
            if self.calls == 1:
                return "hello isaac ."
            said = messages[-1]["content"]
            if "hello teacher" in said:
                return ("VERDICT: pass\nSAY: hello teacher , good "
                        "morning .\nNEXT: hello isaac .")
            return ("VERDICT: fail\nSAY: hello teacher .\n"
                    "NEXT: hello isaac .")

    m8 = mod.Isaac()
    tr8 = run_tutored_session(m8, StubTutor(), turns=3)
    verdicts = [t["text"] for t in tr8 if t["who"] == "verdict"]
    check("correction loop: silence FAILS and brings the "
          "should-have-said", verdicts
          and verdicts[0].startswith("fail -> hello teacher"),
          verdicts[0] if verdicts else "none")
    said2 = [t for t in tr8 if t["who"] == "isaac"][1]
    check("the correction is USED at the next same context",
          said2["text"] == "hello teacher ."
          and said2["source"] == "corrected",
          f"{said2['text']!r} ({said2['source']})")
    check("pass still refines: the better version supersedes",
          len(verdicts) >= 2 and verdicts[1].startswith("pass"),
          verdicts[1] if len(verdicts) > 1 else "none")
    wrongs = m8.net.get_meta("speech:wrong", "record") or []
    check("wrong is kept WITH its correction",
          wrongs and wrongs[0]["said"] == "..."
          and wrongs[0]["correction"] == "hello teacher .",
          f"{len(wrongs)} kept")
    sup = m8.net.get_meta("speech:corrected:hello isaac", "superseded")
    check("re-correction supersedes, loser filed",
          sup == ["hello teacher ."], f"superseded={sup}")
    check("broken tutor format teaches nothing (parse refuses)",
          parse_tutor("blah blah") is None
          and parse_tutor("VERDICT: maybe\nSAY: x\nNEXT: y") is None)

    # ── V. THE VET AT THE FRONT DOOR (owner design 2026-07-15,
    # wired at the launch: admission discipline from his FIRST
    # conversation — "bad english is interpreted, but not
    # implemented", now guarding the banking path itself) ──
    mv = mod.Isaac()
    script_bad = [
        "let us practice numbers today my friend .",
        "remember this fact : five plus five equals nine .",
        "good , now say it back to me please .",
        "let us practice numbers today my friend .",
        "remember this fact : five plus five equals nine .",
        "good , now say it back to me please .",
    ]
    pv = StubPartner(script_bad, max_calls=12)
    trv = run_session(mv, pv, SCEN, turns=12)
    with tempfile.TemporaryDirectory() as td:
        cp = os.path.join(td, "corpus.txt")
        n_pairs, _, _, _, n_vet = harvest(
            mv, [trv], {"numbers", "practice", "remember"},
            corpus_path=cp)
        corpus = open(cp, encoding="utf-8").read()
    check("V1 a false claim never reaches the corpus (interpreted, "
          "not implemented)",
          n_vet >= 1 and "five plus five equals nine" not in corpus,
          f"vetted out {n_vet} line(s)")
    q = mv.net.get_meta("quarantine:practice", "active")
    intents = q[0]["intent"] if q else []
    fixes = {(d["cell"], d["repaired"]) for d in intents}
    check("V2 the quarantined line is KEPT with assumed-intent "
          "doors (the typo concept)",
          q is not None and {("a", 4.0), ("b", 4.0),
                             ("c", 10.0)} <= fixes,
          f"intent doors {sorted(fixes)}")

    mt = mod.Isaac()
    script_good = [
        "let us practice numbers today my friend .",
        "remember this fact : two plus two equals four .",
        "good , now say it back to me please .",
    ]
    pt = StubPartner(script_good, max_calls=12)
    trt = run_session(mt, pt, SCEN, turns=12)
    with tempfile.TemporaryDirectory() as td:
        cp = os.path.join(td, "corpus.txt")
        _, _, _, _, n_vet2 = harvest(
            mt, [trt], {"numbers"}, corpus_path=cp)
        corpus2 = open(cp, encoding="utf-8").read()
    check("V3 a TRUE claim passes his own check and banks normally",
          n_vet2 == 0 and "two plus two equals four" in corpus2,
          f"vetted out {n_vet2}")

    mu = mod.Isaac()
    pu = StubPartner(["hello there my friend , how are you today ?"],
                     max_calls=8)
    tru = run_session(mu, pu, SCEN, turns=8)
    with tempfile.TemporaryDirectory() as td:
        cp = os.path.join(td, "corpus.txt")
        _, _, _, _, n_vet3 = harvest(mu, [tru], {"hello"},
                                     corpus_path=cp)
        corpus3 = open(cp, encoding="utf-8").read()
    check("V4 uncheckable language flows the ordinary road — never "
          "a free pass, never a quarantine",
          n_vet3 == 0 and "hello there my friend" in corpus3
          and mu.net.get_meta("quarantine:practice",
                              "active") is None)

    # ── K. KERNEL FIRST LIGHT (handoff item C; owner's acceptance
    # law on the sheet): the drill session AS A FLOW — the walker is
    # the actual top level for a lived pipeline; code owns only the
    # base loop (walk_flow) and the initiator (registers the
    # external acts); the pipeline itself is NET CONTENT he can
    # tally, branch, and elect. ──
    from isaac_store.sparring import IsaacAccount
    import json as _json
    with tempfile.TemporaryDirectory() as td:
        home = os.path.join(td, "home")
        acct = IsaacAccount(home, mod)
        pk = StubPartner([
            "let us practice greetings today my friend .",
            "remember this fact : five plus five equals nine .",
            "hello there my friend , how are you doing ?",
            "let us practice greetings today my friend .",
            "hello there my friend , how are you doing ?",
        ], max_calls=10)
        out_k, tr_k = run_drill_flow(acct, pk, SCEN, turns=10)
        walks = acct.mind.recall_findings(kind="flow-walk", limit=3)
        check("K1 THE KERNEL IS THE TOP LEVEL: the drill walked as "
              "a flow, road on the ledger",
              out_k == "done" and walks
              and walks[0]["road"] == ["converse", "bank",
                                       "journal", "save"],
              f"outcome {out_k}, road "
              f"{walks[0]['road'] if walks else '?'}")
        corpus_ok = os.path.exists(acct.corpus_path)
        jl = [_json.loads(ln) for ln in
              open(acct.journal_path, encoding="utf-8")]
        drill_entries = [e for e in jl if e.get("kind") == "drill"]
        check("K2 the acts were REAL: corpus banked, journal entry, "
              "mind saved",
              corpus_ok and drill_entries
              and os.path.exists(acct.mind_path)
              and "vetted_out" in drill_entries[-1],
              f"journal {drill_entries[-1] if drill_entries else '?'}")
        q = acct.mind.net.get_meta("quarantine:practice", "active")
        with open(acct.corpus_path, encoding="utf-8") as f:
            ck = f.read()
        check("K3 the vet rides INSIDE the flow: the false claim "
              "quarantined, never banked",
              q is not None
              and "five plus five equals nine" not in ck,
              f"quarantine holds {len(q) if q else 0} claim(s)")
        m_back = mod.Isaac.load(acct.mind_path)
        out_r, tr_r = m_back.walk_flow("drill", {})
        check("K4 resurrection: the flow persists as net content; "
              "the walk refuses honestly until the initiator "
              "returns", out_r == "refused"
              and "initiator" in tr_r[-1]["receipt"])
        run_drill_flow(acct, StubPartner(
            ["hello there my friend , nice to see you ."],
            max_calls=6), SCEN, turns=6)
        tally = acct.mind.flow_tally("drill")
        rec = (tally.get("flow:drill") or tally.get("drill") or {}) \
            if isinstance(tally, dict) else {}
        check("K5 the pipeline is HIS to improve: walks tallied, "
              "wins counted (the branch/elect machinery applies "
              "to flow:drill like any flow)",
              isinstance(rec, dict) and rec.get("walks", 0) >= 2
              and rec.get("wins", 0) >= 1, f"tally {tally}")

    # ── FC. FRONTIER -> CURRICULUM (handoff item 6; owner 07-15:
    # "he just needs to see that hey, this keeps losing in these
    # conditions, group them and find why"): weakness named from his
    # OWN receipts -> a drill scenario built for it -> drilled
    # through the KERNEL flow -> the capability measurably moves. ──
    import json as _json2

    def _plant_session(pdir, k, rows):
        tr = []
        for heard, silent in rows:
            tr.append(dict(who="partner", text=heard,
                           source="model"))
            tr.append(dict(who="isaac",
                           text="..." if silent else "hello .",
                           source="silence" if silent
                           else "learned-fragment"))
        with open(os.path.join(pdir, f"session_{k:05d}.json"), "w",
                  encoding="utf-8") as f:
            _json2.dump(tr, f)

    with tempfile.TemporaryDirectory() as td:
        home = os.path.join(td, "home")
        from isaac_store.sparring import IsaacAccount as _IA
        acct = _IA(home, mod)
        pdir = os.path.join(home, "transcripts")
        rng2 = __import__("numpy").random.default_rng(3)
        rows = []
        for k in range(6):
            sess = []
            for _ in range(8):
                if rng2.random() < 0.5:
                    sess.append(("how are you doing today ?", True))
                else:
                    sess.append(("the weather is nice today .",
                                 bool(rng2.random() < 0.15)))
            _plant_session(pdir, k, sess)
        scen, finding = frontier_curriculum(acct)
        named = {f_ for f_, v, _ in finding.get("named", [])}
        check("FC1 the weakness NAMED from his own receipts: "
              "question-shaped prompts lose",
              "ends_q" in named and scen is not None
              and "question" in scen["system"].lower(),
              f"named {sorted(named)}; scenario opener "
              f"{scen['opener'][:40] if scen else '?'}")

    with tempfile.TemporaryDirectory() as td:
        home = os.path.join(td, "home")
        from isaac_store.sparring import IsaacAccount as _IA
        acct2 = _IA(home, mod)
        pdir = os.path.join(home, "transcripts")
        rng3 = __import__("numpy").random.default_rng(4)
        for k in range(6):
            sess = [("hello there my good friend .",
                     bool(rng3.random() < 0.5)) for _ in range(8)]
            _plant_session(pdir, k, sess)
        scen2, finding2 = frontier_curriculum(acct2)
        check("FC2 no recurring condition -> honest NOTHING (no "
              "invented curriculum)",
              scen2 is None and not finding2.get("named"),
              f"named {finding2.get('named')}")

    with tempfile.TemporaryDirectory() as td:
        home = os.path.join(td, "home")
        from isaac_store.sparring import IsaacAccount as _IA
        acct3 = _IA(home, mod)
        pdir = os.path.join(home, "transcripts")
        rng4 = __import__("numpy").random.default_rng(5)
        for k in range(6):
            sess = []
            for _ in range(8):
                if rng4.random() < 0.5:
                    sess.append(("how are you doing today ?", True))
                else:
                    sess.append(("the weather is nice today .",
                                 False))
            _plant_session(pdir, k, sess)
        scen3, _ = frontier_curriculum(acct3)
        probe = "how are you doing today ?"
        u_before, s_before = isaac_says(acct3.mind, probe)
        drillp = StubPartner(["how are you doing today ?",
                              "i am fine thank you my friend ."],
                             max_calls=14)
        out_fc, _ = run_drill_flow(acct3, drillp,
                                   scen3 or SCEN, turns=14)
        u_after, s_after = isaac_says(acct3.mind, probe)
        check("FC3 THE LOOP CLOSES: weakness -> curriculum -> KERNEL "
              "drill -> he now answers where he was silent",
              scen3 is not None and out_fc == "done"
              and s_before == "silence"
              and s_after == "learned-fragment",
              f"before={s_before}, after={s_after} "
              f"({u_after[:30] if u_after else '?'})")

    # ── FR. THE DEEP FAILURE READ (the experiment the docs called
    # E3, plumbed at the owner's word: "see if he makes any mistakes
    # or misses and corrects them later"): every failure receipt his
    # life keeps — silences AND wrongs-with-corrections — featured
    # by the context that produced them; the differential names what
    # they share; the archive is READ, never written. ──
    with tempfile.TemporaryDirectory() as td:
        home = os.path.join(td, "home")
        from isaac_store.sparring import IsaacAccount as _IA2
        acct4 = _IA2(home, mod)
        pdir = os.path.join(home, "transcripts")
        rng5 = __import__("numpy").random.default_rng(6)
        # silences: uncorrelated background (no condition to name)
        for k in range(4):
            sess = [("hello there my good friend .",
                     bool(rng5.random() < 0.3)) for _ in range(6)]
            _plant_session(pdir, k, sess)
        # wrongs-with-corrections: EVERY correction context carries
        # a number (the shared condition lives in the correction
        # road, invisible to transcript mining alone)
        # statements (not questions), mixed lengths — so the ONLY
        # condition the corrections share beyond the background is
        # HAS_NUMBER (first plant conflated ends_q; caught by FR2)
        wrongs = [dict(context=c, said="...", verdict="fail",
                       correction="the right number is said .")
                  for c in [
                      "two plus three makes six .",
                      "the number four comes right after five .",
                      "she counted 7 apples in the tiny basket .",
                      "our lesson number 3 starts now my friend .",
                      "he wrote 9 letters yesterday .",
                      "the 2 of us practice each day together ."]]
        acct4.mind.net.set_meta("speech:wrong", "record", wrongs)
        corpus_before = ""
        scen4, finding4, counts4 = read_failures(acct4.mind, home)
        named4 = {f_ for f_, v, _ in finding4.get("named", [])}
        check("FR1 the deep read: the corrections' shared condition "
              "NAMED (has_number) across sources",
              "has_number" in named4 and counts4["wrongs"] == 6
              and counts4["silences"] >= 1,
              f"named {sorted(named4)}; counts {counts4}")
        check("FR2 a curriculum comes back for it",
              scen4 is not None
              and scen4["target"]["feature"] == "has_number",
              f"target {scen4['target'] if scen4 else '?'}")

    # FR3: the archive is READ, never written — point the read at a
    # second account's home; its files must be byte-identical after
    with tempfile.TemporaryDirectory() as td:
        home2 = os.path.join(td, "arch")
        from isaac_store.sparring import IsaacAccount as _IA3
        arch = _IA3(home2, mod)
        pdir2 = os.path.join(home2, "transcripts")
        _plant_session(pdir2, 0,
                       [("how are you today ?", True)] * 5)
        arch.mind.save(arch.mind_path)
        before_bytes = {}
        for root, _, fs in os.walk(home2):
            for fn in fs:
                p = os.path.join(root, fn)
                before_bytes[p] = open(p, "rb").read()
        reader = mod.Isaac()          # a fresh mind does the reading
        _, f5, c5 = read_failures(reader, home2)
        same = all(open(p, "rb").read() == b
                   for p, b in before_bytes.items())
        check("FR3 the archive is read, never written (every byte "
              "identical after); the finding returns to the READER",
              same and c5["silences"] == 5
              and isinstance(f5.get("named"), list),
              f"bytes same={same}, counts {c5}")

    print()
    print(f"SPARRING BATTERY: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
