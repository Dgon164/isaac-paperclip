"""dialogue_probe.py — "lets just see what he learns" (owner,
2026-07-12): real back-and-forth conversation data (DailyDialog,
11,118 human dialogues) fed through Isaac's EXISTING organs. Nothing
is taught, nothing is hand-wired to conversation; every claim below
passes the organs' own nulls or is reported as silence.

P1  the shape of conversation (structural patterner): dialogue-act
    streams and raw punctuation streams — which turn-taking
    constraints does analyze() certify?
P2  the reply reflex (learned-speech organ REUSED, zero engine
    changes): features = what was HEARD (prompt n-grams), sentence =
    the response; learn_speech's permutation null admits
    heard->reply fragment correspondences. CONTROL: the same run on
    scrambled pairings must admit ~nothing.
P3  speaking with strangers: on held-out prompts, reply with learned
    fragments or SILENCE — complete numbers, abstentions counted,
    samples verbatim (good and bad).

Corpus: data/dialogue/dd_train.parquet (public, research corpus —
public-tier provenance). pandas is used ONLY here to read parquet;
the engine stays stdlib+numpy.
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402
from isaac_store.structural import analyze             # noqa: E402
from isaac_store.speech_learn import learn_speech, _ngrams  # noqa: E402

ACT = {1: "inform", 2: "question", 3: "directive", 4: "commissive"}


def load_dialogs(path, limit=None):
    import pandas as pd
    df = pd.read_parquet(path)
    out = []
    for _, row in df.iterrows():
        turns = [str(t).strip() for t in row["dialog"] if str(t).strip()]
        acts = [ACT.get(int(a), "?") for a in row["act"]][:len(turns)]
        if len(turns) >= 2:
            out.append((turns, acts))
        if limit and len(out) >= limit:
            break
    return out


def grams_upto(sent, nmax=3):
    return [g for g in _ngrams(sent.lower(), nmax=nmax)
            if "|" not in g and "," not in g]


def main():
    lines = ["DIALOGUE PROBE — what he learns from real conversation "
             "(2026-07-12)", ""]
    dlgs = load_dialogs(os.path.join(ROOT, "data", "dialogue",
                                     "dd_train.parquet"))
    n_turns = sum(len(t) for t, _ in dlgs)
    lines.append(f"corpus: {len(dlgs)} dialogues, {n_turns} turns "
                 f"(DailyDialog train)")

    # ── P1: the shape of conversation ────────────────────────────
    sep = "<end>"
    act_stream, punct_stream = [], []
    for turns, acts in dlgs[:3000]:
        for t, a in zip(turns, acts):
            act_stream.append(a)
            last = t.rstrip()[-1] if t.rstrip() else "."
            punct_stream.append(last if last in "?!." else ".")
        act_stream.append(sep)
        punct_stream.append(sep)
    st = analyze(act_stream)
    lines.append("")
    lines.append(f"P1  dialogue-act stream (3000 dialogues): "
                 f"pattern={st['pattern']}")
    cons = (st.get("levels") or [{}])[0].get("constraints", {})
    for key in ("forks", "never_follows", "det_links"):
        if cons.get(key):
            items = cons[key]
            lines.append(f"      {key}: "
                         f"{str(items)[:100]}")
    stp = analyze(punct_stream)
    lines.append(f"    punctuation stream: pattern={stp['pattern']}")
    consp = (stp.get("levels") or [{}])[0].get("constraints", {})
    if consp.get("never_follows"):
        lines.append(f"      never_follows: "
                     f"{str(consp['never_follows'])[:100]}")

    # ── P2: the reply reflex, through the learned-speech organ ───
    pairs = []
    for turns, _ in dlgs:
        for i in range(len(turns) - 1):
            pairs.append((turns[i].lower(), turns[i + 1].lower()))
    rng = np.random.default_rng(11)
    idx = rng.permutation(len(pairs))
    train_ix, test_ix = idx[:4000], idx[4000:4400]
    train = [pairs[i] for i in train_ix]
    test = [pairs[i] for i in test_ix]

    # features = what was heard: prompt n-grams frequent enough to
    # carry evidence (15..150 prompts), capped by frequency
    from collections import Counter
    freq = Counter()
    for p, _ in train:
        freq.update(set(grams_upto(p)))
    feats = {g for g, c in freq.items() if 15 <= c <= 150}
    feats = set(sorted(feats, key=lambda g: -freq[g])[:120])
    lines.append("")
    lines.append(f"P2  heard->reply correspondences: {len(train)} "
                 f"adjacent pairs, {len(feats)} heard-features offered")

    def corpus_text(pair_list):
        out = []
        for p, r in pair_list:
            fs = [f"heard:{g}" for g in set(grams_upto(p)) & feats]
            if not fs:
                continue
            r_short = " ".join(r.split()[:12])
            out.append(",".join(sorted(fs)) + "|" + r_short)
        return "\n".join(out)

    mind = mod.Isaac()
    learned = learn_speech(mind, corpus_text(train), n_perm=40,
                           min_evidence=5)
    lines.append(f"    ADMITTED: {len(learned)} heard->reply fragments "
                 f"past the permutation null")
    top = sorted(
        learned.items(),
        key=lambda kv: -mind.net.get_meta(f"speech:{kv[0]}",
                                          "evidence")["containing"])
    for F, frag in top[:12]:
        ev = mind.net.get_meta(f"speech:{F}", "evidence")
        lines.append(f"      {F[6:]!r} -> {frag!r}  "
                     f"({ev['containing']}/{ev['examples']})")

    # CONTROL: scrambled pairings — the correspondences must die
    sh = rng.permutation(len(train))
    scrambled = [(train[i][0], train[int(j)][1])
                 for i, j in enumerate(sh)]
    mind2 = mod.Isaac()
    learned_scr = learn_speech(mind2, corpus_text(scrambled),
                               n_perm=40, min_evidence=5)
    lines.append(f"    CONTROL (scrambled pairings): "
                 f"{len(learned_scr)} admitted (want ~0)")

    # ── P3: speaking with strangers ───────────────────────────────
    answered, abstained, samples = 0, 0, []
    for p, r_true in test:
        fs = [f"heard:{g}" for g in set(grams_upto(p)) & feats]
        known = [(F, learned[F]) for F in fs if F in learned]
        if not known:
            abstained += 1
            reply = None
        else:
            F, reply = max(
                known,
                key=lambda kv: mind.net.get_meta(f"speech:{kv[0]}",
                                                 "evidence")["containing"])
            answered += 1
        if len(samples) < 8:
            samples.append((p, reply, r_true))
    lines.append("")
    lines.append(f"P3  held-out prompts: {answered}/{len(test)} answered "
                 f"with a learned fragment, {abstained}/{len(test)} "
                 f"SILENCE (nothing admitted applies — honest)")
    for p, reply, r_true in samples:
        lines.append(f"      heard : {p[:64]}")
        lines.append(f"      isaac : {reply if reply else '(silence)'}")
        lines.append(f"      human : {r_true[:64]}")
        lines.append("")

    report = "\n".join(lines)
    print(report)
    out_dir = os.path.join(ROOT, "experiments", "runs", "2026-07-12")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "dialogue_probe.txt"), "w",
              encoding="utf-8") as f:
        f.write(report + "\n")


if __name__ == "__main__":
    main()
