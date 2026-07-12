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
    p.add_argument("source",
                   help="a csv/tsv/json/jsonl/npy/npz/xlsx file, a "
                        "folder, a zip, or raw/rich text "
                        "(txt/md/html/rtf/docx)")
    p.add_argument("--target", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--speak", action="store_true",
                   help="LEARNED speech (trained from the corpus, all "
                        "or nothing) with the full report beneath")
    a = p.parse_args()
    mod = bridge.load_isaac_module()

    if not (os.path.isfile(a.source) and a.source.lower().endswith(".csv")):
        # everything that is not a plain CSV goes through the one door
        from isaac_store.intake import ingest, table_csv
        got = ingest(a.source)
        tables = [i for i in got["items"] if i["kind"] == "table"]
        texts = [i for i in got["items"] if i["kind"] == "text"]
        for s in got["skipped"]:
            print(f"[skipped] {s['source']} — {s['why']}")
        for tx in texts:
            print(f"[text] {tx['name']} ({tx['provenance']['bytes']} "
                  f"bytes) — the text road is not wired to reports yet")
        if not tables:
            print("no numeric tables found to challenge.")
            return
        for i, t in enumerate(tables):
            if len(tables) > 1:
                print(f"\n===== {t['name']} =====")
            if t["dropped_columns"]:
                print(f"[dropped non-numeric columns: "
                      f"{', '.join(t['dropped_columns'])}]")
            rep = challenge(table_csv(t), target=a.target, mod=mod)
            print(render_text(rep))
        return

    rep = challenge(a.source, target=a.target, mod=mod)
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
