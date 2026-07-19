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
    p.add_argument("source", nargs="?", default=None,
                   help="a csv/tsv/json/jsonl/npy/npz/xlsx file, a "
                        "folder, a zip, or raw/rich text "
                        "(txt/md/html/rtf/docx)")
    p.add_argument("--tell", default=None, metavar="SENTENCE",
                   help="tell him a law in plain english, e.g. "
                        "\"ohm's law is v=ir\" — parsed, vetted, "
                        "echoed back; DRY unless --account names "
                        "his home")
    p.add_argument("--recall", default=None, metavar="NAME",
                   help="ask what he holds under a told name "
                        "(needs --account)")
    p.add_argument("--goal", default=None, metavar="GOAL",
                   help="end-goal decomposition over HIS laws: "
                        "\"current from voltage=6 resistance=3\" "
                        "(needs --account; names without values "
                        "ask for structure only)")
    p.add_argument("--account", default=None, metavar="DIR",
                   help="his home directory (e.g. "
                        "Documents/isaac_home) — telling LANDS "
                        "there and is saved; a .bak of mind.isaac "
                        "is written first")
    p.add_argument("--container", default=None,
                   help="the world a told law lands in (with "
                        "--tell --account)")
    p.add_argument("--target", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--audit", action="store_true",
                   help="the audit face: flags WITH RECEIPTS "
                        "(error/news/duplicate), floors per column, "
                        "joins across tables, honest refusals, and "
                        "ASKs where the instrument's resolution is "
                        "unevidenced; writes audit.jsonl")
    p.add_argument("--resolution", action="append", default=[],
                   metavar="COL=SIGMA",
                   help="tell the instrument's resolution for a "
                        "column (repeatable), e.g. --resolution y=0.05")
    p.add_argument("--speak", action="store_true",
                   help="LEARNED speech (trained from the corpus, all "
                        "or nothing) with the full report beneath")
    p.add_argument("--analyst", action="store_true",
                   help="the ANALYST face: trend + cycle + anomalies "
                        "+ relations + forecast + the watch, per "
                        "column, plain language with receipts")
    p.add_argument("--time", default=None, metavar="COL",
                   help="the time column for --analyst (else "
                        "auto-detected: first strictly-increasing)")
    p.add_argument("--plot", nargs="?", const="plots", default=None,
                   metavar="DIR",
                   help="with --analyst: write an SVG per column "
                        "(points, error bars, trend, frame "
                        "averages) into DIR (default ./plots)")
    a = p.parse_args()
    mod = bridge.load_isaac_module()

    if a.goal:
        from isaac_store.telling import parse_goal, render_goal_tree
        g = parse_goal(a.goal)
        if g.get("refused"):
            print(f"[refused: {g['refused']}]")
            return
        if not a.account:
            print("[a goal decomposes over HIS laws — name his "
                  "home with --account]")
            return
        mind = mod.Isaac.load(os.path.join(a.account, "mind.isaac"))
        out = mind.decompose(g["want"], known=g["known"])
        print(render_goal_tree(out))
        return

    if a.tell or a.recall:
        from isaac_store.telling import (tell_english, recall_law,
                                         parse_told_law)
        if a.account:
            import shutil
            mp = os.path.join(a.account, "mind.isaac")
            if not os.path.isfile(mp):
                print(f"[no mind at {mp}]")
                return
            if a.tell:
                shutil.copy2(mp, mp + ".bak")
            mind = mod.Isaac.load(mp)
        else:
            mind = mod.Isaac()
        if a.recall:
            got = recall_law(mind, a.recall)
            if not got:
                print(f"[he holds nothing under "
                      f"'{a.recall}'{'' if a.account else ' — dry mind; name his home with --account'}]")
            else:
                print(f"{got['name']}: {got['said']}")
                print(f"  form {got['form']} [{got['state']}] "
                      f"who={got['who']}; witnesses "
                      f"{got['witnesses']}")
            return
        got = (tell_english(mind, a.tell, who="owner",
                            container=a.container)
               if a.account else parse_told_law(a.tell))
        if got.get("refused"):
            print(f"[refused: {got['refused']}]")
            return
        print(f"heard: {got['said']}")
        if a.account:
            r = got["tell"]
            print(f"  landed: {r.get('status')}"
                  + (f" (form {got['form']})"
                     if r.get("status") == "MATCHES" else "")
                  + f"; who=owner; container={got['container']}")
            mind.save(mp)
            print(f"  saved ({mp}; .bak kept)")
        else:
            print(f"  [dry — name {got['name']}, slots "
                  f"{got['slots']}, canonical "
                  f"{got['positional']}; add --account to teach "
                  f"him]")
        return

    if a.source is None:
        p.error("source is required unless --tell/--recall is used")

    if a.plot is not None and not a.analyst:
        print("[--plot refused: plots ride the analyst face — "
              "re-run with --analyst]")

    if a.analyst:
        from isaac_store.analyst import analyst_source, render_analyst
        rep = analyst_source(a.source, time_col=a.time, mod=mod,
                             plots=a.plot)
        if a.json:
            print(json.dumps(rep, default=str, indent=2))
        else:
            print(render_analyst(rep))
        return

    if a.audit:
        from isaac_store.audit import audit_source, render_audit
        res = {}
        for spec in a.resolution:
            col, _, sig = spec.partition("=")
            res[col.strip()] = float(sig)
        rep = audit_source(a.source, target=a.target,
                           resolutions=res or None, mod=mod)
        if a.json:
            print(json.dumps(rep, default=str, indent=2))
        else:
            print(render_audit(rep))
        with open("audit.jsonl", "w", encoding="utf-8") as f:
            for r in rep["records"]:
                f.write(json.dumps(r, default=str) + "\n")
        print(f"\n[{len(rep['records'])} records -> audit.jsonl]")
        return

    if not (os.path.isfile(a.source) and a.source.lower().endswith(".csv")):
        # everything that is not a plain CSV goes through the one door
        from isaac_store.intake import ingest, table_csv
        got = ingest(a.source)
        tables = [i for i in got["items"] if i["kind"] == "table"]
        texts = [i for i in got["items"] if i["kind"] == "text"]
        for s in got["skipped"]:
            print(f"[skipped] {s['source']} — {s['why']}")
        from isaac_store.structural import analyze
        for tx in texts:
            st = analyze(tx["text"])
            chart = " ; ".join(st["levels"][0]["chart"][:5]) \
                if st.get("levels") else ""
            print(f"[text] {tx['name']} ({tx['provenance']['bytes']} "
                  f"bytes) — structure: {st['pattern']}"
                  + (f" | {chart}" if chart else ""))
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
