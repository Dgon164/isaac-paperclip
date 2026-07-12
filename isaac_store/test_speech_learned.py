"""Learned-speech battery — the proof standard the owner set:
"that is called programming and thats not what isaac is about."

W1 EMERGENCE: trained on the corpus, Isaac speaks a real report —
   and the wording came from the corpus, not from us
W2 THE GREP PROOF: the spoken words exist NOWHERE in speech_learn.py
   source — no phrase table, no template, no hidden wording
W3 ALL OR NOTHING: an untaught verdict -> he cannot speak at all
   (fall back to report); an untaught atom -> that term is SILENCE,
   listed as unspoken, never a hand-coded line
W4 CORPUS SWAP: retrain on different wording -> the SAME report is
   spoken in the new words (speech follows data, not code)
W5 THE NULL: ubiquitous words are not admitted as feature fragments
W6 RETENTION: learned speech is knowledge — it survives
   save_pack/load_pack and speaks identically
W7 faithfulness: every number spoken exists in the report
Run: python test_speech_learned.py   (from isaac_store/)
"""
import os
import re
import shutil
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.report import challenge
from isaac_store.speech_learn import learn_speech, speak_learned

PASS = FAIL = 0
HERE = os.path.dirname(os.path.abspath(__file__))


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def make_csv(rng, law=True, n=400):
    a = rng.uniform(-2, 2, n)
    b = rng.uniform(-2, 2, n)
    y = 3.0 * a * b + a ** 2 if law else rng.normal(0, 1, n)
    return "\n".join(["alpha,beta,energy"] +
                     [f"{a[i]:.6f},{b[i]:.6f},{y[i]:.6f}" for i in range(n)])


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_speechlearn_")
    try:
        print("  loading engine...")
        mod = bridge.load_isaac_module()
        rng = np.random.default_rng(47)
        corpus = open(os.path.join(HERE, "speech_corpus.txt"),
                      encoding="utf-8").read()
        rep = challenge(make_csv(rng, True), mod=mod)
        rep_n = challenge(make_csv(rng, False), mod=mod)

        print("W1. emergence: he speaks, and the words are the corpus's")
        mind = mod.Isaac()
        learned = learn_speech(mind, corpus)
        out = speak_learned(mind, rep)
        r = out["response"]
        check("speaks the verdict he was taught",
              out["can_speak"] and
              "I understand this data about energy" in r)
        check("terms spoken in learned words with real names",
              "alpha on its own times beta on its own" in r
              and "raises energy" in r
              and "the square of alpha" in r, r[:140])
        check("fit and confidence in learned words",
              "r squared" in r and "my confidence is" in r)

        print("W2. the grep proof: no wording in the code")
        src = open(os.path.join(HERE, "speech_learn.py"),
                   encoding="utf-8").read()
        for word in ("wave", "square", "raises", "lowers", "understand",
                     "alignment", "logarithm", "pretend", "confidence is"):
            check(f'"{word}" absent from speech_learn.py', word not in src)

        print("W3. all or nothing")
        # a corpus with NO refusal lessons: he cannot speak a refusal
        corpus_no_refusal = "\n".join(
            ln for ln in corpus.splitlines() if "NO_RULE" not in ln)
        m2 = mod.Isaac()
        learn_speech(m2, corpus_no_refusal)
        out_n = speak_learned(m2, rep_n)
        check("untaught verdict -> cannot speak (fall back to report)",
              not out_n["can_speak"]
              and "verdict unspeakable" in out_n["problems"])
        # a corpus with no square lessons: that term is silence
        corpus_no_sq = "\n".join(
            ln for ln in corpus.splitlines() if "atom:pow2" not in ln)
        m3 = mod.Isaac()
        learn_speech(m3, corpus_no_sq)
        out3 = speak_learned(m3, rep)
        check("untaught atom -> that term is SILENCE, and it is listed",
              out3["can_speak"]
              and "the square of" not in out3["response"]
              and "atom:pow2" in out3["unspoken"])

        print("W4. corpus swap: the words follow the data")
        corpus_b = (corpus
                    .replace("I understand this data about",
                             "I grasp what is happening with")
                    .replace("raises", "boosts")
                    .replace("the square of", "the self-product of"))
        m4 = mod.Isaac()
        learn_speech(m4, corpus_b)
        r4 = speak_learned(m4, rep)["response"]
        check("same report, new teacher, new words",
              "I grasp what is happening with energy" in r4
              and "boosts energy" in r4
              and "the self-product of alpha" in r4)
        check("the old words are gone",
              "I understand" not in r4 and "raises" not in r4)

        print("W5. the null rejects ubiquitous words")
        frags = list(learned.values())
        check("no fragment is a bare stopword",
              all(f not in ("the", "of", "in", "and", "a", "NAME")
                  for f in frags))
        check("fit's fragment is fit's own words, not the verdict's",
              "understand" not in learned.get("fit", ""))

        print("W6. retention: speech is knowledge in the net")
        d = os.path.join(tmp, "packs")
        mind.save_pack(d)
        resumed = mod.Isaac.load_pack(d)
        check("resumed mind speaks identically",
              speak_learned(resumed, rep)["response"] == r)

        print("W7. faithfulness on learned speech")
        check("every number spoken exists in the report",
              out["faithful"] and out["problems"] == [])
        print()
        print("  ISAAC SPEAKS (learned, corpus A):")
        print("  " + r)
        print()
        print("  ISAAC SPEAKS (learned, corpus B — same report):")
        print("  " + r4)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
