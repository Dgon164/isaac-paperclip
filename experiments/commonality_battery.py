"""commonality_battery.py — THE FAILURE-COMMONALITY MINER (data-ops
segment §4; owner ask 2026-07-14: "assess failures and find
commonalities... specifically denied"). Battery FIRST, per discipline.

The law under test: the commonality of the denied is a DIFFERENTIAL
against the allowed — compare()'s only-in-failures, gated by a
selection-corrected label-shuffle null. NEVER a frequency: a feature
on 100% of failures that is also on 100% of successes says nothing.

This organ is double-duty by design (build once, serves both
segments): it names the shared factor behind audit flags
(news-vs-error) AND it is the CASE-CLASS MINTER for piecewise
supersession (organ failure receipts -> named failure class -> duel
scope). Requirement it imposes upstream: FAT failure receipts —
context recorded at failure time, or there is nothing to mine.

Checks C1-C7. Run: PYTHONHASHSEED=0 python commonality_battery.py
"""
import json
import os
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

rng = np.random.default_rng(11)
CHECKS = []

FEATS = {
    "voice":   ["active", "passive"],
    "tense":   ["present", "past", "perfect"],
    "length":  ["short", "long"],
    "pronoun": ["none", "i", "you", "he"],
    "junk":    ["j1", "j2", "j3", "j4"],
    "lang":    ["english"],
}


def check(name, ok, detail=""):
    CHECKS.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" +
          (f"   {detail}" if detail else ""))


def sample(n, extra=None):
    feats = dict(FEATS)
    if extra:
        feats.update(extra)
    return [{k: str(rng.choice(v)) for k, v in feats.items()}
            for _ in range(n)]


def main():
    print("=" * 70)
    print("COMMONALITY BATTERY — the failure-commonality miner")
    print("=" * 70)
    m = mod.Isaac()

    # ── C1: planted frontier — passive+perfect named, junk/lang never ──
    recs = sample(600)
    failed = [bool(rng.random() < (0.90 if (r["voice"] == "passive"
              and r["tense"] == "perfect") else 0.08)) for r in recs]
    r = m.mine_commonality(recs, failed, name="frontier")
    got = {(f, v) for f, v, _ in r["named"]}
    ok = (("tense", "perfect") in got and ("voice", "passive") in got
          and not any(f in ("junk", "lang") for f, v in got))
    check("C1 planted frontier named (passive+perfect); junk/lang never",
          ok, f"named {sorted(got)} thr {r['threshold']:.3f}")

    # ── C2: owner lockout — the denied word named ALONE ──
    recs = sample(600, extra={"word": ["fine", "fine", "fine", "slang"]})
    failed = [bool(r["word"] == "slang" or rng.random() < 0.03)
              for r in recs]
    r = m.mine_commonality(recs, failed)
    ok = (len(r["named"]) == 1 and r["named"][0][0] == "word"
          and r["named"][0][1] == "slang")
    check("C2 lockout world: word=slang named alone", ok,
          f"named {[(f, v) for f, v, _ in r['named']]}")

    # ── C3: random failures — honest nothing ──
    recs = sample(600)
    failed = [bool(rng.random() < 0.15) for _ in recs]
    r = m.mine_commonality(recs, failed)
    check("C3 random failures name NOTHING", len(r["named"]) == 0,
          f"top {r['top']:.3f} vs thr {r['threshold']:.3f}")

    # ── C4: 100%-of-failures background feature NOT named ──
    recs = sample(600)
    failed = [bool(rng.random() < (0.90 if (r["voice"] == "passive"
              and r["tense"] == "perfect") else 0.08)) for r in recs]
    r = m.mine_commonality(recs, failed)
    bg = any(f == "lang" for f, v, _ in r["named"])
    check("C4 shared background (lang=english, 100% of failures AND "
          "successes) not named", not bg,
          "differential, never a frequency")

    # ── C5: degenerate worlds refuse with a why ──
    recs = sample(40)
    r_all = m.mine_commonality(recs, [True] * 40)
    r_none = m.mine_commonality(recs, [False] * 40)
    ok = (r_all["named"] == [] and "why" in r_all
          and r_none["named"] == [] and "why" in r_none)
    check("C5 all-fail / all-pass refuse honestly", ok,
          r_all.get("why", "")[:50])

    # ── C6: named reading recorded; re-mining supersedes, old kept ──
    hits = m.recall_findings(kind="commonality")
    recs = sample(600, extra={"word": ["fine", "slang"]})
    failed = [bool(r["word"] == "slang") for r in recs]
    m.mine_commonality(recs, failed, name="frontier")   # re-mine same name
    chain = m.net.get_meta("commonality:frontier", "superseded") or []
    ok = (len(hits) >= 1 and hits[0].get("name") == "frontier"
          and len(chain) == 1 and "why" in chain[0])
    check("C6 findings recorded; re-mine supersedes, old kept", ok,
          f"findings {len(hits)}, chain {len(chain)}")

    # ── C7: the reading survives the pack road ──
    a = json.dumps(m.net.get_meta("commonality:frontier", "active"),
                   sort_keys=True, default=str)
    with tempfile.TemporaryDirectory() as td:
        m.save_pack(td)
        m2 = mod.Isaac.load_pack(td)
    b = json.dumps(m2.net.get_meta("commonality:frontier", "active"),
                   sort_keys=True, default=str)
    check("C7 commonality reading survives packs", a == b and a != "null")

    n_ok = sum(CHECKS)
    print("=" * 70)
    print(f"COMMONALITY BATTERY: {n_ok}/{len(CHECKS)}")
    print("=" * 70)
    sys.exit(0 if n_ok == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
