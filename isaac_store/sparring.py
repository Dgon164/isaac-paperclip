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
                 max_calls=40, max_reply_chars=400, timeout_s=120):
        self.model, self.url = model, url.rstrip("/")
        self.max_calls, self.max_reply_chars = max_calls, max_reply_chars
        self.timeout_s = timeout_s
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
                               options=dict(temperature=0.7,
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
    """Speak ONLY what the learned-speech organ has admitted for what
    was just heard; otherwise silence. Returns (utterance|None,
    source_tag)."""
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
)
