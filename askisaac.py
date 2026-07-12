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


def main():
    p = argparse.ArgumentParser(description="Ask Isaac about your data")
    p.add_argument("csv")
    p.add_argument("--target", default=None)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    rep = challenge(a.csv, target=a.target)
    if a.json:
        print(json.dumps(rep, default=str, indent=2))
    else:
        print(render_text(rep))


if __name__ == "__main__":
    main()
