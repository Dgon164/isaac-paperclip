"""order_matters_battery.py — WHEN ORDER MATTERS (owner theory,
2026-07-15: "additive does not matter, but subtractive methods are...
restricting the space counts as subtractive"). Battery FIRST.

The organ under test: order_matters(op) — MEASURED, never told
(checklist #3): probe the operation with random operand pairs, swap
them, compare. A violation keeps its WITNESS pair as the receipt
(5-3 vs 3-5); order-freeness is claimed only as "no counterexample
in N probes" — honest absence, not proof. The measured badge lands
on op:<symbol> nodes and in the findings ledger.

Checks M1-M7. Run: PYTHONHASHSEED=0 python order_matters_battery.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" +
          (f"   {detail}" if detail else ""))


def main():
    print("=" * 70)
    print("ORDER-MATTERS BATTERY — additive vs subtractive, measured")
    print("=" * 70)
    m = mod.Isaac()

    # ── M1: the additive family measures order-free ──
    free = {op: m.order_matters(op) for op in ("+", "*", "max", "min")}
    ok = all(not r["matters"] and r["probes"] >= 50
             and "no counterexample" in r["why"]
             for r in free.values())
    check("M1 additive family (+ * max min): order-free, said honestly",
          ok, free["+"]["why"][:52])

    # ── M2: the subtractive family measures order-SENSITIVE ──
    sens = {op: m.order_matters(op) for op in ("-", "/", "^")}
    ok = all(r["matters"] and r.get("witness") for r in sens.values())
    check("M2 subtractive family (- / ^): order matters, witnessed",
          ok)

    # ── M3: the witness is a real receipt — it actually disagrees ──
    w = sens["-"]["witness"]
    ok = (abs((w["a"] - w["b"]) - w["ab"]) < 1e-9
          and abs((w["b"] - w["a"]) - w["ba"]) < 1e-9
          and w["ab"] != w["ba"])
    check("M3 the '-' witness verifies (ab != ba, both recomputed)",
          ok, f"{w['a']:g}-{w['b']:g}={w['ab']:g} vs "
              f"{w['b']:g}-{w['a']:g}={w['ba']:g}")

    # ── M4: the badge lands on the op node ──
    badge = m.net.get_meta("op:-", "order")
    ok = badge is not None and badge["matters"] is True
    check("M4 measured badge stored at op:-", ok)

    # ── M5: findings recorded (negative knowledge included) ──
    hits = m.recall_findings(kind="order")
    check("M5 verdicts land in the ledger",
          len(hits) >= 7 and any(h["name"] == "+" for h in hits))

    # ── M6: an unknown operation refuses with a why ──
    r = m.order_matters("flurble")
    check("M6 unknown operation refused honestly",
          r.get("refused") is True and "why" in r, r.get("why", "")[:50])

    # ── M7: badges survive the pack road ──
    a = json.dumps(m.net.get_meta("op:-", "order"), sort_keys=True)
    with tempfile.TemporaryDirectory() as td:
        m.save_pack(td)
        m2 = mod.Isaac.load_pack(td)
    b = json.dumps(m2.net.get_meta("op:-", "order"), sort_keys=True)
    check("M7 badges survive packs", a == b and a != "null")

    n_ok = sum(CHECKS)
    print("=" * 70)
    print(f"ORDER-MATTERS BATTERY: {n_ok}/{len(CHECKS)}")
    print("=" * 70)
    sys.exit(0 if n_ok == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
