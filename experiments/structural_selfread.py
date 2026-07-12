"""structural_selfread.py — Isaac reads his own operational record.

The multicycle structural patterner pointed at REAL sequences: the
event streams of this repo's own journals and ledgers from the
2026-07-12 runs. No planting — whatever the verdicts are, they are
the result.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from isaac_store.structural import analyze  # noqa: E402


def journal_kinds(path):
    """A journal/ledger -> its sequence of event kinds (no content).
    Orchestrator journals decode through the Journal organ itself."""
    if path.endswith("journal.jsonl"):
        from isaac_store.journal import Journal
        out = []
        for _seq, ev in Journal(path).read_since(0):
            edit = ev.get("edit", {})
            op = edit.get("op", "?") if isinstance(edit, dict) else "?"
            out.append(f"{ev.get('verdict', '?')}:{op}")
        return out
    out = []
    for line in open(path, encoding="utf-8"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "kind" in e:
            out.append(str(e["kind"]))
    return out


def main():
    run_dir = os.path.join(ROOT, "experiments", "runs", "2026-07-12")
    targets = []
    for sub in sorted(os.listdir(run_dir)):
        p = os.path.join(run_dir, sub, "journal.jsonl")
        if os.path.exists(p):
            targets.append((f"{sub}/journal", p))
    findings_path = os.path.join(ROOT, "data", "findings.jsonl")
    if os.path.exists(findings_path):
        targets.append(("data/findings.jsonl", findings_path))

    lines = ["ISAAC READS HIS OWN RECORD — structural pass, 2026-07-12", ""]
    for name, path in targets:
        seq = journal_kinds(path)
        r = analyze(seq)
        lines.append(f"  {name}: {len(seq)} events -> {r['pattern']}"
                     + (f" (tower: {' -> '.join(r['tower'])})"
                        if len(r.get('tower', [])) > 1 else ""))
        if r.get("levels"):
            for c in r["levels"][0]["chart"][:6]:
                lines.append(f"      {c}")
        lines.append("")
    report = "\n".join(lines)
    print(report)
    out = os.path.join(run_dir, "structural_selfread.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report + "\n")


if __name__ == "__main__":
    main()
