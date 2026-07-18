"""sparring_probe.py â€” the first live conversations (owner,
2026-07-12: "lets try getting a small llm with a series of prompts
that it can use to talk to isaac and isaac can talk back to. we need
to make sure to monitor and adjust. for the first thing maybe about
a prompt like im trying to learn english.")

Partner: qwen2.5:1.5b-instruct through local ollama (RTX 3090,
nothing leaves the machine). Isaac is SEEDED with what he learned
from DailyDialog earlier today (his admitted heard->reply fragments)
and speaks ONLY those or silence. Two sessions run back to back;
between them the harvest turns the partner's words into null-gated
lessons â€” the monitoring question is whether session two knows
things session one did not.

Full transcripts printed and saved: monitor and adjust.
"""
import os
import sys
from collections import Counter

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402
from isaac_store.sparring import (OllamaPartner, SCENARIOS,   # noqa: E402
                                  _grams, harvest, run_session)
from isaac_store.speech_learn import learn_speech      # noqa: E402

MODEL = "qwen2.5:1.5b-instruct"


def seed_from_dailydialog(mind, lines_out):
    import pandas as pd
    df = pd.read_parquet(os.path.join(ROOT, "data", "dialogue",
                                      "dd_train.parquet"))
    pairs = []
    for _, row in df.iterrows():
        t = [str(x).strip().lower() for x in row["dialog"]
             if str(x).strip()]
        pairs += list(zip(t, t[1:]))
        if len(pairs) >= 4000:
            break
    freq = Counter()
    for p, _ in pairs:
        freq.update(set(_grams(p)))
    feats = {g for g, c in freq.items() if 15 <= c <= 150}
    feats = set(sorted(feats, key=lambda g: -freq[g])[:120])
    corpus = []
    for p, r in pairs:
        fs = [f"heard:{g}" for g in set(_grams(p)) & feats]
        if fs:
            corpus.append(",".join(sorted(fs)) + "|"
                          + " ".join(r.split()[:12]))
    learned = learn_speech(mind, "\n".join(corpus), n_perm=40,
                           min_evidence=5)
    lines_out.append(f"seeded from DailyDialog: {len(learned)} "
                     f"admitted heard->reply fragments")
    return feats


def show(lines, tr, title):
    lines.append("")
    lines.append(f"â”€â”€ {title} â”€â”€")
    for t in tr:
        tag = f" [{t['source']}]" if t["who"] == "isaac" else ""
        lines.append(f"  {t['who']:7s}: {t['text'][:76]}{tag}")


def main():
    lines = ["SPARRING PROBE â€” first live conversations (2026-07-12)",
             f"partner: {MODEL} via local ollama", ""]
    partner = OllamaPartner(MODEL, max_calls=40)
    if not partner.reachable():
        print("REFUSED: no local partner reachable â€” start ollama and "
              "pull the model")
        sys.exit(1)

    mind = mod.Isaac()
    feats = seed_from_dailydialog(mind, lines)

    scen = SCENARIOS["learn_english"]
    tr1 = run_session(mind, partner, scen, turns=12)
    show(lines, tr1, "session 1: i am trying to learn english")

    # the harvest between sessions: his words become lessons
    session_texts = [t["text"].lower() for t in tr1
                     if t["who"] == "partner"]
    sfreq = Counter()
    for s in session_texts:
        sfreq.update(set(_grams(s)))
    feats2 = feats | {g for g, c in sfreq.items() if c >= 3}
    cpath = os.path.join(ROOT, "data", "dialogue",
                         "sparring_corpus.txt")
    n_pairs, before, after, _, _ = harvest(mind, [tr1], feats2,
                                        corpus_path=cpath)
    lines.append("")
    lines.append(f"harvest: {n_pairs} heard->reply pairs banked; "
                 f"admitted fragments {before} -> {after}")

    tr2 = run_session(mind, partner, scen, turns=12)
    show(lines, tr2, "session 2 (after the harvest)")

    src_counts = Counter(t["source"] for t in tr1 + tr2
                         if t["who"] == "isaac")
    lines.append("")
    lines.append(f"isaac's utterance sources across both sessions: "
                 f"{dict(src_counts)}")
    lines.append(f"partner calls spent: {partner.calls}/"
                 f"{partner.max_calls}")

    report = "\n".join(lines)
    print(report)
    out = os.path.join(ROOT, "experiments", "runs", "2026-07-12")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "sparring_probe.txt"), "w",
              encoding="utf-8") as f:
        f.write(report + "\n")


if __name__ == "__main__":
    main()
