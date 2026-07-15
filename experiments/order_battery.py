"""order_battery.py — STRUCTURE AND ORDER (owner ask, 2026-07-15:
"he needs to be able to assess structure and order. ab vs ba. if the
difference is just position he should be able to identify that").
Battery FIRST, per discipline.

The gap: compare() is set-based — 'ab' vs 'ba' look IDENTICAL to it.
The organ under test: compare_order(a, b) — comparison-as-
registration applied to sequences (theory doc §13): align, then read
(a) the TRANSFORM (the permutation = the pose) and (b) the RESIDUAL
(content difference = the identity). Checklist #9 made literal for
order: the parts are the identity, the arrangement is the pose,
reported separately — and a positional claim is only made when the
returned mapping VERIFIABLY turns a into b (checked, never asserted).

Checks O1-O10. Run: PYTHONHASHSEED=0 python order_battery.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" +
          (f"   {detail}" if detail else ""))


def apply_mapping(a, mapping, n):
    out = [None] * n
    for i, j in enumerate(mapping):
        out[j] = a[i]
    return out


def main():
    print("=" * 70)
    print("ORDER BATTERY — structure and order, ab vs ba")
    print("=" * 70)
    m = mod.Isaac()

    # ── O1: identical -> same ──
    r = m.compare_order(["a", "b"], ["a", "b"])
    check("O1 identical sequences -> same", r["verdict"] == "same")

    # ── O2: THE OWNER'S EXAMPLE — ab vs ba: position only, a swap ──
    r = m.compare_order(["a", "b"], ["b", "a"])
    ok = (r["verdict"] == "reordered"
          and r["content"]["only_a"] == [] and r["content"]["only_b"] == []
          and r["arrangement"]["kind"] == "swap"
          and r["arrangement"]["moved_positions"] == [0, 1])
    check("O2 ab vs ba: parts identical, difference IS position (swap)",
          ok, f"{r['verdict']} / {r['arrangement']['kind']}")

    # ── O3: reversal named ──
    r = m.compare_order(list("abcd"), list("dcba"))
    check("O3 abcd vs dcba: reversed",
          r["verdict"] == "reordered"
          and r["arrangement"]["kind"] == "reversed")

    # ── O4: rotation named ──
    r = m.compare_order(list("abcd"), list("cdab"))
    check("O4 abcd vs cdab: rotated",
          r["verdict"] == "reordered"
          and r["arrangement"]["kind"] == "rotated by 2")

    # ── O5: duplicates — a valid verified mapping is still produced ──
    a, b = list("aab"), list("aba")
    r = m.compare_order(a, b)
    ok = (r["verdict"] == "reordered"
          and apply_mapping(a, r["arrangement"]["mapping"], len(b)) == b
          and r["arrangement"]["moved_positions"] == [1, 2])
    check("O5 aab vs aba: reordered, mapping verifies", ok,
          f"mapping {r['arrangement']['mapping']}")

    # ── O6: content differs, order of the shared part does NOT ──
    r = m.compare_order(list("abc"), list("abd"))
    ok = (r["verdict"] == "content differs"
          and r["content"]["only_a"] == ["c"]
          and r["content"]["only_b"] == ["d"]
          and r.get("shared_order") == "kept")
    check("O6 abc vs abd: content differs, shared part order kept", ok,
          f"{r['verdict']}, shared_order {r.get('shared_order')}")

    # ── O7: content AND order differ — both said, factored apart ──
    r = m.compare_order(list("abc"), list("bad"))
    ok = (r["verdict"] == "content and order differ"
          and r["content"]["only_a"] == ["c"]
          and r["content"]["only_b"] == ["d"]
          and r.get("shared_order") == "reordered")
    check("O7 abc vs bad: both differences said, factored apart", ok,
          f"{r['verdict']}")

    # ── O8: count differences are content (multiset honesty) ──
    r = m.compare_order(list("aab"), list("ab"))
    check("O8 aab vs ab: the extra 'a' is CONTENT, not order",
          r["verdict"] == "content differs"
          and r["content"]["only_a"] == ["a"])

    # ── O9: edges — empty vs empty, empty vs something ──
    r1 = m.compare_order([], [])
    r2 = m.compare_order([], ["a"])
    check("O9 empty edges honest", r1["verdict"] == "same"
          and r2["verdict"] == "content differs"
          and r2["content"]["only_b"] == ["a"])

    # ── O10: every positional claim carries a VERIFIED mapping ──
    import numpy as np
    rng = np.random.default_rng(2)
    ok = True
    for _ in range(50):
        n = int(rng.integers(2, 9))
        a = [str(rng.integers(0, 4)) for _ in range(n)]
        b = list(a)
        rng.shuffle(b)
        r = m.compare_order(a, b)
        if r["verdict"] == "same":
            ok = ok and a == b
        else:
            ok = (ok and r["verdict"] == "reordered"
                  and apply_mapping(a, r["arrangement"]["mapping"],
                                    n) == b)
    check("O10 50 random shuffles: mapping verifies every time", ok)

    n_ok = sum(CHECKS)
    print("=" * 70)
    print(f"ORDER BATTERY: {n_ok}/{len(CHECKS)}")
    print("=" * 70)
    sys.exit(0 if n_ok == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
