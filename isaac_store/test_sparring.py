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
                                  isaac_says, run_session)

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
    n_pairs, before, after, learned = harvest(
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

    print()
    print(f"SPARRING BATTERY: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
