"""practice_run.py — Isaac's practice block (owner, 2026-07-12:
"this is not a user account. or rather, perhaps we should have an
isaac user account"). Not the promote cycle: HIS life. The account
home (default Documents/isaac_home) persists — mind, corpus,
transcripts, progress journal — and every run continues where the
last one stopped.

usage: python practice_run.py [sessions] [scenario] [home]
"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402
from isaac_store.sparring import (IsaacAccount, OllamaPartner,  # noqa: E402
                                  SCENARIOS, _grams)

MODEL = "qwen2.5:1.5b-instruct"


def seed_corpus(acct):
    """One-time education: his DailyDialog corpus becomes the base of
    HIS OWN speech corpus, so every future relearn sees all evidence
    together (public-tier provenance)."""
    if os.path.exists(acct.corpus_path):
        return 0
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
    lines = []
    for p, r in pairs:
        fs = [f"heard:{g}" for g in set(_grams(p)) & feats]
        if fs:
            lines.append(",".join(sorted(fs)) + "|"
                         + " ".join(r.split()[:12]))
    with open(acct.corpus_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return len(lines)


def main():
    sessions = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    scen = SCENARIOS[sys.argv[2] if len(sys.argv) > 2 else "drill"]
    home = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.expanduser("~"), "Documents", "isaac_home")

    acct = IsaacAccount(home, mod)
    seeded = seed_corpus(acct)
    partner = OllamaPartner(MODEL, max_calls=40 * sessions)
    if not partner.reachable():
        print("REFUSED: no local partner reachable")
        sys.exit(1)

    print(f"isaac's account: {home}")
    print(f"  sessions so far: {acct.sessions_so_far()}, "
          f"fragments: {acct.fragments()}"
          + (f", corpus seeded: {seeded} lines" if seeded else ""))
    prog = acct.practice(partner, scen, sessions=sessions, turns=12,
                         relearn_every=5)
    print()
    print("session | pairs | fragments | spoke | silence")
    for p in prog:
        print(f"  {p['session']:5d} | {p['pairs']:5d} | "
              f"{p['fragments_after']:9d} | {p['spoke']:5d} | "
              f"{p['silence']:7d}")
    print()
    print(f"account now: {acct.sessions_so_far()} sessions lived, "
          f"{acct.fragments()} fragments held, corpus "
          f"{sum(1 for _ in open(acct.corpus_path, encoding='utf-8'))} "
          f"lines")


if __name__ == "__main__":
    main()
