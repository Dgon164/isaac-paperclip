"""sparring.py — the local conversation partner (owner design,
2026-07-12: local AI conversations are FOR LEARNING AND TRAINING —
"a sparring partner, not a product mouth"; and the session order:
"lets try getting a small llm with a series of prompts that it can
use to talk to isaac and isaac can talk back to. we need to make
sure to monitor and adjust.")

This is World GM for language: a budgeted, local, monitored
environment Isaac practices in. THE MODEL'S OUTPUT IS DATA — an
untrusted stream to be null-gated by Isaac's own machinery, never
truth, never verdict. Local = nothing leaves the machine.

Isaac's side is HONEST speech only: the scenario opener (a task
seed), fragments his learned-speech organ has ADMITTED (past its
excess null), or SILENCE. He never fakes fluency. Every session
returns the full transcript with per-turn source tags — monitoring
is a first-class output, not a log file.

stdlib + numpy only (urllib against the local ollama door).
"""
import json
import os
import time
import urllib.request

from .speech_learn import _ngrams, learn_speech


# ── the partner: any local chat door with this contract ──────────
class OllamaPartner:
    """A local model behind ollama's /api/chat. Budgets are physical:
    max_calls per session, max_reply_chars per turn, per-call
    timeout. Exhaustion = clean stop, never a hang."""

    def __init__(self, model, url="http://127.0.0.1:11434",
                 max_calls=40, max_reply_chars=400, timeout_s=120,
                 temperature=0.7):
        self.model, self.url = model, url.rstrip("/")
        self.max_calls, self.max_reply_chars = max_calls, max_reply_chars
        self.timeout_s = timeout_s
        self.temperature = temperature
        self.calls = 0

    def reachable(self):
        try:
            with urllib.request.urlopen(self.url + "/api/tags",
                                        timeout=5) as r:
                names = [m.get("name", "") for m in
                         json.loads(r.read()).get("models", [])]
            return any(n.startswith(self.model.split(":")[0])
                       for n in names)
        except Exception:
            return False

    def say(self, messages):
        if self.calls >= self.max_calls:
            return None                       # budget spent: clean stop
        self.calls += 1
        body = json.dumps(dict(model=self.model, messages=messages,
                               stream=False,
                               options=dict(temperature=self.temperature,
                                            num_predict=120))).encode()
        req = urllib.request.Request(
            self.url + "/api/chat", data=body,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
            out = json.loads(r.read())
        text = (out.get("message") or {}).get("content", "").strip()
        return text[:self.max_reply_chars]


# ── Isaac's honest utterances ─────────────────────────────────────
def _grams(sent, nmax=3):
    return [g for g in _ngrams(sent.lower(), nmax=nmax)
            if "|" not in g and "," not in g]


def isaac_says(mind, heard):
    """Speak what he has been CORRECTED to say for this context first
    (a correction is told knowledge — the owner's loop), then what
    the learned-speech organ admitted, else silence. Returns
    (utterance|None, source_tag)."""
    # corrections first: the most specific (longest) corrected context
    best_c, best_len = None, 0
    for g in set(_grams(heard, nmax=4)):
        say = mind.net.get_meta(f"speech:corrected:{g}", "say")
        if say is not None and len(g.split()) > best_len:
            best_c, best_len = say, len(g.split())
    if best_c is not None:
        return best_c, "corrected"
    best, best_ev = None, -1
    for g in set(_grams(heard)):
        node = f"speech:heard:{g}"
        frag = mind.net.get_meta(node, "fragment")
        if frag is None:
            continue
        ev = (mind.net.get_meta(node, "evidence") or {}).get(
            "containing", 0)
        if ev > best_ev:
            best, best_ev = frag, ev
    if best is None:
        return None, "silence"
    return best, "learned-fragment"


# ── the session ───────────────────────────────────────────────────
def run_session(mind, partner, scenario, turns=10):
    """One budgeted conversation. Returns the transcript (list of
    dicts: who/text/source) — the monitoring artifact."""
    transcript = []
    messages = [dict(role="system", content=scenario["system"])]
    say = scenario["opener"]
    src = "opener"
    for _ in range(turns):
        transcript.append(dict(who="isaac", text=say, source=src))
        messages.append(dict(role="user", content=say))
        reply = partner.say(messages)
        if reply is None:
            transcript.append(dict(who="budget", text="(spent)",
                                   source="budget"))
            break
        transcript.append(dict(who="partner", text=reply,
                               source="model"))
        messages.append(dict(role="assistant", content=reply))
        utter, src = isaac_says(mind, reply)
        say = utter if utter is not None else "..."
    return transcript


# ── the harvest: the model's words become null-gated lessons ─────
def harvest(mind, transcripts, feats, corpus_path=None, n_perm=40,
            min_evidence=4):
    """Adjacent (heard -> next-said) pairs from sessions join the
    accumulated corpus; learn_speech re-admits fragments through its
    excess null. Returns (n_pairs_added, admitted_before, admitted
    _after). The corpus file is the raw record — kept, re-learnable,
    auditable."""
    lines = []
    for tr in transcripts:
        texts = [t["text"].lower() for t in tr
                 if t["who"] == "partner"]
        for a, b in zip(texts, texts[1:]):
            fs = [f"heard:{g}" for g in set(_grams(a)) & feats]
            if fs:
                b_short = " ".join(b.split()[:12])
                lines.append(",".join(sorted(fs)) + "|" + b_short)
    old = ""
    if corpus_path and os.path.exists(corpus_path):
        old = open(corpus_path, encoding="utf-8").read()
    corpus = (old + "\n" + "\n".join(lines)).strip()
    if corpus_path:
        with open(corpus_path, "w", encoding="utf-8") as f:
            f.write(corpus + "\n")
    before = sum(1 for n in list(mind.net.meta)
                 if str(n).startswith("speech:heard:"))
    learned = learn_speech(mind, corpus, n_perm=n_perm,
                           min_evidence=min_evidence)
    after = sum(1 for n in list(mind.net.meta)
                if str(n).startswith("speech:heard:"))
    return len(lines), before, after, learned


SCENARIOS = dict(
    learn_english=dict(
        opener="i am trying to learn english .",
        system=("You are a kind, patient conversation partner helping "
                "a beginner learn English. Use very short, simple "
                "sentences (at most two). Ask simple questions. If "
                "the learner replies with '...' they did not "
                "understand: say something simpler, or teach one "
                "common word with an example. Never use lists or "
                "markdown — just plain spoken lines.")),
    # measured adjustment #1 (first live probe): one free-form session
    # banks too few pairs for any admission — a LESSON drills the same
    # patterns over and over, so repetition crosses the null
    drill=dict(
        opener="i am trying to learn english .",
        system=("You are teaching a total beginner English by "
                "REPETITION. Pick very common exchanges (hello -> hi; "
                "how are you -> i am fine; what is this -> this is a "
                "book; thank you -> you are welcome; goodbye -> see "
                "you) and REPEAT them constantly, in slightly varied "
                "words, again and again, one short line per turn. If "
                "the learner replies with '...', repeat the last "
                "pattern in simpler words. If they say a word back, "
                "praise briefly and repeat the pattern once more. "
                "Never use lists or markdown — plain spoken lines "
                "only.")),
)


# ── THE CORRECTION LOOP (owner, 2026-07-12): "you cannot
# mathematically review [language], and you cannot get proper
# testing feedback... talk or say something, check for a response,
# and correct him on what he should have said if he failed, or
# correct him on what he should have said better if he passed."
# The correction IS language's residual. A correction is TOLD
# knowledge (usable at once); the wrong utterance is KEPT with its
# correction (wisdom applied to speech); a corrected context that
# fails again is SUPERSEDED with the new correction.

TUTOR = dict(
    opener="i am trying to learn english .",
    system=("You are an English tutor for a total beginner named "
            "Isaac. Speak ONE short simple line to Isaac (under 10 "
            "words), then wait. Every time Isaac replies, you MUST "
            "answer in EXACTLY this three-line format:\n"
            "VERDICT: pass or fail\n"
            "SAY: <the exact short line Isaac should have said>\n"
            "NEXT: <your next short line to Isaac>\n"
            "fail means his reply did not fit; pass means it fit and "
            "SAY is a better version of it. '...' always means fail. "
            "Keep SAY under 10 simple words. No lists, no markdown."))


def parse_tutor(reply):
    """The tutor's judgment, or None if the format broke (a broken
    judgment teaches nothing — skipped honestly, never guessed)."""
    out = {}
    for ln in (reply or "").splitlines():
        low = ln.strip()
        for key in ("verdict", "say", "next"):
            if low.lower().startswith(key + ":"):
                out[key] = low[len(key) + 1:].strip()
    if out.get("verdict", "").lower() not in ("pass", "fail"):
        return None
    if not out.get("say") or not out.get("next"):
        return None
    out["verdict"] = out["verdict"].lower()
    return out


def apply_correction(mind, context, said, verdict, say):
    """Store the correction as told speech on every context gram
    (most-specific wins at recall); keep the wrong utterance WITH its
    correction. Supersession: a re-corrected context replaces its
    old correction and the loser is filed."""
    for g in set(_grams(context, nmax=4)):
        node = f"speech:corrected:{g}"
        old = mind.net.get_meta(node, "say")
        if old is not None and old != say:
            hist = mind.net.get_meta(node, "superseded") or []
            hist.append(old)
            mind.net.set_meta(node, "superseded", hist)
        mind.net.set_meta(node, "say", say)
    wrongs = mind.net.get_meta("speech:wrong", "record") or []
    wrongs.append(dict(context=context, said=said, verdict=verdict,
                       correction=say))
    mind.net.set_meta("speech:wrong", "record", wrongs)


def run_tutored_session(mind, partner, turns=10, scenario=None):
    """The owner's loop, live: tutor line -> Isaac speaks -> verdict
    + correction -> stored -> next line. Returns the transcript;
    every Isaac turn carries its verdict and correction."""
    scen = scenario or TUTOR
    transcript = []
    messages = [dict(role="system", content=scen["system"]),
                dict(role="user", content=scen["opener"])]
    line = partner.say(messages)
    if line is None:
        return transcript
    line = line.splitlines()[0].strip()
    messages.append(dict(role="assistant", content=line))
    for _ in range(turns):
        transcript.append(dict(who="tutor", text=line, source="model"))
        utter, src = isaac_says(mind, line.lower())
        said = utter if utter is not None else "..."
        transcript.append(dict(who="isaac", text=said, source=src))
        messages.append(dict(role="user", content=said))
        reply = partner.say(messages)
        if reply is None:
            transcript.append(dict(who="budget", text="(spent)",
                                   source="budget"))
            break
        messages.append(dict(role="assistant", content=reply))
        j = parse_tutor(reply)
        if j is None:
            transcript.append(dict(who="tutor", text=reply[:60],
                                   source="unparseable-skipped"))
            line = reply.splitlines()[-1].strip()[:80]
            continue
        apply_correction(mind, line.lower(), said, j["verdict"],
                         j["say"].lower())
        transcript.append(dict(
            who="verdict", text=f"{j['verdict']} -> {j['say']}",
            source="correction"))
        line = j["next"]
    return transcript


# ── the Isaac account (owner, 2026-07-12: "this is not a user
# account. or rather, perhaps we should have an isaac user account")
# — his practice is HIS LIFE, not the promote cycle. The account is
# a persistent home: his mind state, his accumulating corpus, his
# transcripts, an append-only progress journal. He is the same Isaac
# tomorrow that he was today.
class IsaacAccount:
    def __init__(self, home, isaac_module):
        self.home = home
        self.mod = isaac_module
        os.makedirs(home, exist_ok=True)
        os.makedirs(os.path.join(home, "transcripts"), exist_ok=True)
        self.mind_path = os.path.join(home, "mind.isaac")
        self.corpus_path = os.path.join(home, "sparring_corpus.txt")
        self.journal_path = os.path.join(home, "practice_journal.jsonl")
        if os.path.exists(self.mind_path):
            self.mind = self.mod.Isaac.load(self.mind_path)
        else:
            self.mind = self.mod.Isaac()

    def _journal(self, entry):
        with open(self.journal_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def sessions_so_far(self):
        if not os.path.exists(self.journal_path):
            return 0
        return sum(1 for _ in open(self.journal_path,
                                   encoding="utf-8"))

    def fragments(self):
        return sum(1 for n in list(self.mind.net.meta)
                   if str(n).startswith("speech:heard:"))

    def practice(self, partner, scenario, sessions=10, turns=10,
                 feats=None, relearn_every=1):
        """The ongoing loop: converse -> bank -> relearn -> journal ->
        save. Returns the per-session progress list (the monitor)."""
        progress = []
        for s in range(sessions):
            tr = run_session(self.mind, partner, scenario, turns=turns)
            n0 = self.sessions_so_far()
            with open(os.path.join(
                    self.home, "transcripts",
                    f"session_{n0:05d}.json"), "w",
                    encoding="utf-8") as f:
                json.dump(tr, f, indent=1)
            texts = [t["text"].lower() for t in tr
                     if t["who"] == "partner"]
            fs = feats or set()
            from collections import Counter
            cnt = Counter()
            for x in texts:
                cnt.update(set(_grams(x)))
            fs = fs | {g for g, c in cnt.items() if c >= 3}
            before = self.fragments()
            if (s + 1) % relearn_every == 0:
                n_pairs, _, after, _ = harvest(
                    self.mind, [tr], fs, corpus_path=self.corpus_path)
            else:
                n_pairs, after = 0, before
            silence = sum(1 for t in tr if t["who"] == "isaac"
                          and t["source"] == "silence")
            spoke = sum(1 for t in tr if t["who"] == "isaac"
                        and t["source"] == "learned-fragment")
            entry = dict(session=n0, pairs=n_pairs,
                         fragments_before=before,
                         fragments_after=after,
                         silence=silence, spoke=spoke,
                         partner_calls=partner.calls, ts=time.time())
            self._journal(entry)
            progress.append(entry)
            self.mind.save(self.mind_path)
            if partner.calls >= partner.max_calls:
                break
        return progress
