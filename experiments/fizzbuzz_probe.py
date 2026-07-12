"""fizzbuzz_probe.py — logic actions measured (owner, 2026-07-12:
"can we test logic actions? say fizz buzz?").

WRONG-KEPT (owner correction, same day): this probe's framing —
one-vs-rest indicator targets composed by argmax — was the assistant
DECOMPOSING THE TASK FOR HIM ("you fed him a pattern and he had to
mimic it. thats not generation, thats duplication"). It stays as a
VOCABULARY measurement (can the atoms say divisibility at all?); the
capability the owner asked for is told-rule GENERATION — see
rule_battery.py — with the example road demoted to duel partner
(task_battery.py).

FizzBuzz is periodicity + composition: divisibility by 3/5/15 is
period structure (for integer n, 1[3|n] = (1+2cos(2pi n/3))/3 EXACTLY,
and the 15-class is a PRODUCT of the 3- and 5-forms), and the label
logic is one-vs-rest + argmax. Nothing here is taught: four binary
indicator discoveries from labeled examples, the engine's own
vocabulary, argmax as the comparator (rank, no hand thresholds).

Roads measured:
P1 structural: the label-class sequence -> analyze(); does Isaac SEE
   the period-15 repeat?
P2 discovery: one-vs-rest indicators (num/fizz/buzz/fizzbuzz) from
   n=1..300; every verdict + equation + adequacy reported.
P3 the complete number: % of n=301..400 (EXTRAPOLATION - beyond every
   training sample; a lookup cannot follow) labeled exactly right by
   argmax over the four discovered laws.

Refusals and PARTIALs are answers: if the vocabulary cannot propose
period 3 on an integer grid, the probe measures that blocker.
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from isaac_store import bridge                    # noqa: E402
from isaac_store.structural import analyze        # noqa: E402

LABELS = ["num", "fizz", "buzz", "fizzbuzz"]


def label_of(n):
    if n % 15 == 0:
        return "fizzbuzz"
    if n % 3 == 0:
        return "fizz"
    if n % 5 == 0:
        return "buzz"
    return "num"


def main():
    print("  loading engine...")
    mod = bridge.load_isaac_module()
    lines = ["FIZZBUZZ PROBE — logic actions, measured (2026-07-12)", ""]

    # ── P1: does Isaac SEE the structure of the label sequence? ──
    seq = [label_of(n) for n in range(1, 301)]
    st = analyze(seq)
    per = None
    if st.get("levels"):
        per = st["levels"][0]["constraints"].get("global_period")
    lines.append(f"P1  structural read of the label sequence: "
                 f"pattern={st['pattern']}"
                 f"{', period ' + str(per) if per else ''} "
                 f"(truth: repeat, period 15)")

    # ── P2: one-vs-rest indicator discovery, nothing taught ──────
    train = np.arange(1, 301, dtype=float)
    test = np.arange(301, 401, dtype=float)
    y_train = [label_of(int(n)) for n in train]
    y_test = [label_of(int(n)) for n in test]
    mind = mod.Isaac()
    lines.append("")
    lines.append("P2  one-vs-rest indicators from n=1..300 "
                 "(y in {0,1}; half held out inside discover):")
    preds = {}
    for lab in LABELS:
        y = np.array([1.0 if l == lab else 0.0 for l in y_train])
        res = mind.discover(train.reshape(-1, 1), y, name=f"is_{lab}")
        p = mind.apply_law(f"is_{lab}", test.reshape(-1, 1))
        preds[lab] = p
        ad = res["adequacy"]["verdict"]
        lines.append(f"    is_{lab:9s}: {res['verdict']:10s} "
                     f"r2={res['r2']:.3f}  [{ad}]")
        lines.append(f"      eq: {res['equation'][:66]}")
        if res["verdict"] not in ("UNDERSTOOD",) and res["adequacy"]["reasons"]:
            lines.append(f"      why: {res['adequacy']['reasons'][0][:66]}")

    # ── P3: the complete number — end-to-end, EXTRAPOLATED ───────
    lines.append("")
    ok_rows = [lab for lab in LABELS if preds[lab] is not None]
    if len(ok_rows) == len(LABELS):
        P = np.column_stack([np.asarray(preds[lab], float)
                             for lab in LABELS])
        fin = np.isfinite(P).all(1)
        guesses = [LABELS[j] for j in np.argmax(P, axis=1)]
        right = sum(1 for g, t, f in zip(guesses, y_test, fin)
                    if f and g == t)
        answered = int(fin.sum())
        lines.append(
            f"P3  END-TO-END FizzBuzz, n=301..400 (beyond all training): "
            f"{right}/100 exactly right "
            f"({answered}/100 answered; refusals count as wrong)")
        # where it fails, say so — the confusion is the discovery signal
        wrong = {}
        for g, t, f in zip(guesses, y_test, fin):
            if not f or g != t:
                wrong[f"{t}->{g if f else 'refused'}"] = \
                    wrong.get(f"{t}->{g if f else 'refused'}", 0) + 1
        if wrong:
            worst = sorted(wrong.items(), key=lambda kv: -kv[1])[:4]
            lines.append("    confusions: " + ", ".join(
                f"{k} x{v}" for k, v in worst))
    else:
        missing = [lab for lab in LABELS if preds[lab] is None]
        lines.append(f"P3  END-TO-END: not runnable — no law stored for "
                     f"{missing} (refusal is the answer at this "
                     f"vocabulary)")

    report = "\n".join(lines)
    print()
    print(report)
    out_dir = os.path.join(ROOT, "experiments", "runs", "2026-07-12")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "fizzbuzz_probe.txt"), "w",
              encoding="utf-8") as f:
        f.write(report + "\n")


if __name__ == "__main__":
    main()
