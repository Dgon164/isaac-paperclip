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

from isaac_store.report import challenge, render_text  # noqa: E402
from isaac_store.speech import speak                   # noqa: E402


def main():
    p = argparse.ArgumentParser(description="Ask Isaac about your data")
    p.add_argument("csv")
    p.add_argument("--target", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--speak", action="store_true",
                   help="plain-English response (native gated English), "
                        "with the full report attached beneath")
    a = p.parse_args()
    rep = challenge(a.csv, target=a.target)
    if a.json:
        print(json.dumps(rep, default=str, indent=2))
    elif a.speak:
        out = speak(rep)
        print(out["response"])
        if not out["faithful"]:  # the null even distrusts ourselves
            print(f"\n[faithfulness check FAILED: {out['problems']} — "
                  f"trust the report below]")
        print("\n" + "-" * 60 + "\n" + render_text(rep))
    else:
        print(render_text(rep))


if __name__ == "__main__":
    main()
