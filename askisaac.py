"""askisaac.py — drop a CSV, get the honest report (owner MVP).

  python askisaac.py data.csv                # target = last column
  python askisaac.py data.csv --target y     # target by column name
  python askisaac.py data.csv --json         # machine-readable

The report leads with the VERDICT — and a refusal is a real answer,
delivered with its diagnosis and what to try next.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from isaac_store import bridge                          # noqa: E402
from isaac_store.report import challenge, render_text   # noqa: E402
from isaac_store.speech_learn import (learn_speech,     # noqa: E402
                                      speak_learned)


def main():
    p = argparse.ArgumentParser(description="Ask Isaac about your data")
    p.add_argument("csv")
    p.add_argument("--target", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--speak", action="store_true",
                   help="LEARNED speech (trained from the corpus, all "
                        "or nothing) with the full report beneath")
    a = p.parse_args()
    mod = bridge.load_isaac_module()
    rep = challenge(a.csv, target=a.target, mod=mod)
    if a.json:
        print(json.dumps(rep, default=str, indent=2))
    elif a.speak:
        mind = mod.Isaac()
        corpus = open(os.path.join(HERE, "isaac_store",
                                   "speech_corpus.txt"),
                      encoding="utf-8").read()
        learn_speech(mind, corpus)
        out = speak_learned(mind, rep)
        if out["can_speak"]:
            print(out["response"])
            if out["unspoken"]:
                print(f"\n[not yet taught to speak: {out['unspoken']} — "
                      f"see the report below]")
            if not out["faithful"]:
                print(f"\n[faithfulness check FAILED: {out['problems']}"
                      f" — trust the report below]")
        else:
            print("[Isaac has not been taught to speak this verdict "
                  "— the report follows.]")
        print("\n" + "-" * 60 + "\n" + render_text(rep))
    else:
        print(render_text(rep))


if __name__ == "__main__":
    main()
