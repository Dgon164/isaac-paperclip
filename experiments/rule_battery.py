"""rule_battery.py — GENERATION, NOT DUPLICATION (owner, 2026-07-12:
"he didnt learn it. you fed him a pattern and he had to mimic it...
what i want is to say if its a 3 say fizz, if its a 5, say buzz, if
its both say fizzbuzz, and if its neither increment the number. i
want him to be able to understand that kind of thing.")

The organ: tell_rule / respond_by_rule / generate_by_rule /
validate_rule. The rule is TOLD; the behavior is GENERATED having
seen ZERO examples of the output. Precedence is Isaac's own general
logic (most specific clause wins — clause ORDER must not matter);
ambiguity refuses; belief comes only from data; the example road
(learn_responses) is the duel partner, and both roads must land on
the same divisibility concept (reads_as bridge).

Task words live in THIS file only — the engine grep stays clean
(task_battery check 1).
"""
import json
import os
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                # noqa: E402

PASS, FAIL = 0, 0


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


def truth(i):
    if i % 15 == 0:
        return "fizzbuzz"
    if i % 3 == 0:
        return "fizz"
    if i % 5 == 0:
        return "buzz"
    return str(i)


# the rule, in canonical clauses — note the ORDER IS SCRAMBLED on
# purpose: base case first, the both-clause in the middle. Isaac's
# precedence must come from specificity, never from clause order.
RULE = [
    {"when": {}, "say": "__number__"},
    {"when": {"multiple_of": [3, 5]}, "say": "fizzbuzz"},
    {"when": {"multiple_of": [3]}, "say": "fizz"},
    {"when": {"multiple_of": [5]}, "say": "buzz"},
]


def main():
    m = mod.Isaac()
    m.tell_rule("fb", RULE)

    # ── 1. GENERATION from zero examples ─────────────────────────
    gen = m.generate_by_rule("fb", 100)
    want = [truth(i) for i in range(1, 101)]
    right = sum(g == w for g, w in zip(gen, want))
    check("told the rule, saw no examples: generates 1..100 exactly",
          right == 100, f"{right}/100; first 15: {gen[:15]}")

    # ── 2. spot semantics: both-case and the neither-case ────────
    check("n=30 -> the both-clause; n=7 -> the number itself",
          m.respond_by_rule("fb", 30)["token"] == "fizzbuzz"
          and m.respond_by_rule("fb", 7)["token"] == "7",
          f"30->{m.respond_by_rule('fb', 30)['token']}, "
          f"7->{m.respond_by_rule('fb', 7)['token']}")

    # ── 3. precedence is HIS, not clause order ───────────────────
    m2 = mod.Isaac()
    m2.tell_rule("fb_rev", list(reversed(RULE)))
    gen2 = m2.generate_by_rule("fb_rev", 100)
    check("clause order scrambled: same behavior (specificity wins)",
          gen2 == gen, "reversed-clause rule generates identically")

    # ── 4. ambiguity refuses, never guesses ──────────────────────
    m3 = mod.Isaac()
    m3.tell_rule("amb", [
        {"when": {"multiple_of": [3]}, "say": "A"},
        {"when": {"multiple_of": [5]}, "say": "B"},
        {"when": {}, "say": "__number__"},
    ])
    r15 = m3.respond_by_rule("amb", 15)
    check("n=15 under 3->A / 5->B with no both-clause: refusal + why",
          r15["token"] is None and "ambiguous" in r15["why"],
          r15["why"][:60])

    # ── 5. unknown condition words refuse loudly ─────────────────
    try:
        m3.tell_rule("bad", [{"when": {"bigger_than": [3]}, "say": "x"}])
        loud = False
    except ValueError as e:
        loud = "unknown condition" in str(e)
    check("unknown condition word: loud refusal at tell time", loud)

    # ── 6. non-whole prompts refuse ──────────────────────────────
    r = m.respond_by_rule("fb", 2.5)
    check("prompt 2.5: refusal (conditions live on whole numbers)",
          r["token"] is None, r["why"][:50])

    # ── 7. belief only from data: validation against a stream ────
    v = m.validate_rule("fb", [str(i) for i in range(1, 201)],
                        [truth(i) for i in range(1, 201)])
    check("true rule vs observed stream: validated, complete number",
          v["status"] == "validated" and v["match"] == 200
          and v["of"] == 200, f"{v['match']}/{v['of']} {v['status']}")

    # ── 8. a WRONG told rule is contradicted, disagreements kept ─
    m4 = mod.Isaac()
    m4.tell_rule("wrong", [
        {"when": {"multiple_of": [4]}, "say": "fizz"},
        {"when": {}, "say": "__number__"},
    ])
    v4 = m4.validate_rule("wrong", [str(i) for i in range(1, 101)],
                          [truth(i) for i in range(1, 101)])
    check("wrong rule vs the stream: contradicted + diffs kept",
          v4["status"] == "contradicted" and v4["match"] < 60
          and len(v4["disagreements"]) == 5,
          f"{v4['match']}/{v4['of']}, first diff: "
          f"{v4['disagreements'][0]}")

    # ── 9. THE DUEL: told rule vs the example road ────────────────
    m5 = mod.Isaac()
    stream = [truth(i) for i in range(1, 301)]
    rec = m5.learn_responses([str(i) for i in range(1, 301)], stream,
                             name="dup")
    ex_right = sum(
        m5.respond(str(i), name="dup")["token"] == truth(i)
        for i in range(301, 401))
    rule_right = sum(
        m.respond_by_rule("fb", i)["token"] == truth(i)
        for i in range(301, 401))
    check("duel on n=301..400: told rule >= example road",
          rule_right == 100 and rule_right >= ex_right,
          f"rule {rule_right}/100 vs example road {ex_right}/100")

    # ── 10. the bridge: the discovered 15s-class READS AS a
    #        divisibility concept (all methods, one concept) ───────
    fb_cls = [c for c in rec["classes"] if c["token"] == "fizzbuzz"]
    check("example road's 15s-class reads as 'every 15th'",
          bool(fb_cls) and fb_cls[0].get("reads_as") == "every 15th",
          f"reads_as={fb_cls[0].get('reads_as') if fb_cls else None}")

    # ── 11. rules persist: ledger round-trip ─────────────────────
    fd, ledger = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for e in m.findings:
            f.write(json.dumps(e, default=str) + "\n")
    fresh = mod.Isaac()
    fresh.load_ledger(ledger)
    os.unlink(ledger)
    gen3 = fresh.generate_by_rule("fb", 30)
    check("ledger round-trip: the told rule still generates",
          gen3 == gen[:30], f"first 5: {gen3[:5]}")

    print()
    print(f"RULE BATTERY: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
