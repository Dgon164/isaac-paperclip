"""Native gated English battery — road 2 of the translation layer.

E1 UNDERSTOOD -> plain English in the user's column names, zero
   x0-jargon, verdict framing first
E2 noise -> the refusal SPOKEN with the same directness
E3 faithfulness holds by construction on real reports
E4 THE NULL CATCHES INVENTION: a tampered number fails verification
E5 every atom kind realizes to honest words (wave/log/square/root/
   decay/alignment/gap)
E6 gated omission: a missing field is never spoken (no confidence
   field -> no confidence claim; no terms -> no what-moves sentence)
E7 PARTIAL/CAPTURED framings say exactly what they are
Run: python test_speech.py   (from isaac_store/)
"""
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.report import challenge
from isaac_store.speech import speak, verify_faithful

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def make_csv(rng, law=True, n=400):
    a = rng.uniform(-2, 2, n)
    b = rng.uniform(-2, 2, n)
    y = 3.0 * a * b + a ** 2 if law else rng.normal(0, 1, n)
    return "\n".join(["alpha,beta,energy"] +
                     [f"{a[i]:.6f},{b[i]:.6f},{y[i]:.6f}" for i in range(n)])


def main():
    print("  loading engine...")
    mod = bridge.load_isaac_module()
    rng = np.random.default_rng(43)

    print("E1. plain English, the user's words")
    rep = challenge(make_csv(rng, True), mod=mod)
    out = speak(rep)
    r = out["response"]
    check("verdict framing leads", r.startswith("I understand"))
    check("speaks in column names, zero jargon",
          "alpha times beta" in r and "the square of alpha" in r
          and not re.search(r"\bx\d+\b", r), r[:120])
    check("complete numbers spoken (r2 + rows + weights)",
          "r2 1.0" in r and "400 rows" in r and "3.00" in r)

    print("E2. the refusal, spoken")
    rep_n = challenge(make_csv(rng, False), mod=mod)
    out_n = speak(rep_n)
    check("refusal is direct, first person, no pretending",
          out_n["response"].startswith("I could not find")
          and "will not pretend" in out_n["response"])
    check("refusal still offers the next step",
          "next" in out_n["response"].lower())

    print("E3. faithfulness by construction")
    check("real UNDERSTOOD response verifies clean",
          out["faithful"] and out["problems"] == [])
    check("real refusal response verifies clean", out_n["faithful"])

    print("E4. the null catches invention")
    tampered = r.replace("400 rows", "5000 rows")
    ok_t, problems = verify_faithful(tampered, rep)
    check("a number the report never said FAILS verification",
          not ok_t and "5000" in problems[0])

    print("E5. every atom kind speaks honestly (unit-level)")
    from isaac_store.speech import _atom_phrase
    CASES = [
        (dict(kind="sin", i=0, j=None, k=2.0), "a repeating wave in a"),
        (dict(kind="pow", i=0, j=None, k=0.0), "the logarithm of a"),
        (dict(kind="pow", i=1, j=None, k=0.5), "the square root of b"),
        (dict(kind="pow", i=0, j=None, k=2.0), "the square of a"),
        (dict(kind="exp", i=0, j=None, k=1.0), "exponential decay in a"),
        (dict(kind="cosd", i=0, j=1, k=1.0), "the alignment between a and b"),
        (dict(kind="coshd", i=0, j=1, k=1.0),
         "steep growth with the gap between a and b"),
    ]
    for atom, want in CASES:
        check(f'says "{want}"', _atom_phrase(atom, ["a", "b"]) == want)
    fake = dict(verdict="UNDERSTOOD", target="output", rows=10,
                columns=["a", "b"], fit=dict(r2=0.95), terms=[
                    dict(coef=1.0, atoms=[dict(kind="sin", i=0, j=None, k=2.0)]),
                    dict(coef=-2.0, atoms=[dict(kind="pow", i=0, j=None, k=0.0)]),
                ])
    rf = speak(fake)["response"]
    check("raises/lowers track the sign",
          "lowers" in rf and "raises" in rf)

    print("E6. gated omission")
    no_conf = {k: v for k, v in rep.items() if k != "confidence"}
    r6 = speak(no_conf)["response"]
    check("no confidence field -> no confidence claim",
          "confident" not in r6)
    bare = dict(verdict="NO RULE", target="y", rows=5, columns=["a"])
    r7 = speak(bare)["response"]
    check("nothing but a verdict -> one honest sentence, verified",
          r7.startswith("I could not find")
          and verify_faithful(r7, bare)[0])

    print("E7. PARTIAL/CAPTURED framings")
    p = speak(dict(fake, verdict="PARTIAL"))["response"]
    c = speak(dict(fake, verdict="CAPTURED", terms=None))["response"]
    check("PARTIAL says part-of-the-pattern", "part of the pattern" in p)
    check("CAPTURED says predict-but-not-say",
          "cannot yet say" in c and "formula" in c)
    print()
    print("  SAMPLE (UNDERSTOOD):")
    print("  " + r)
    print()
    print("  SAMPLE (refusal):")
    print("  " + out_n["response"])
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
