"""tools_battery.py — THE TOOLS NODE (owner design, 2026-07-15:
"a tools node that he can query. it has the preset files of every
thing he has designed or we have built as a function for him to
directly access. he can either test them, just go through trial and
error and run them all, or he can know what they do and choose the
one he is looking for... if nothing in tools is applicable, then he
just skips to next."). Battery FIRST, per discipline.

The presence pillar of the flow-structures design: every capability
gets a NODE in the net (tool:<name> doored under 'tools') carrying
what it does (his readable description), how to call it, tags, and
use/outcome receipts (the election shape, ready for the same
recent-window law as words). Three usage modes: QUERY (know what
they do, choose), RUN (trial and error — run them and see), RECEIPT
(every use keeps score). An empty query is an HONEST SKIP, never a
stall.

Checks T1-T8. Run: PYTHONHASHSEED=0 python tools_battery.py
"""
import json
import os
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402

rng = np.random.default_rng(3)
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" +
          (f"   {detail}" if detail else ""))


def main():
    print("=" * 70)
    print("TOOLS BATTERY — the tools node")
    print("=" * 70)
    m = mod.Isaac()

    # ── T1: register + query by need ──
    m.register_tool("sharpen", "make a dull pencil sharp again",
                    how="sharpen(pencil)", tags=("stationery",))
    r = m.query_tools("my pencil is dull")
    ok = r["matches"] and r["matches"][0]["name"] == "sharpen"
    check("T1 registered tool found by what it does", ok,
          r["matches"][0]["does"] if r["matches"] else r["why"])

    # ── T2: the catalog — everything we ever built, auto-harvested ──
    n = m.catalog_tools()
    names = {d.split("tool:", 1)[1]
             for d in m.net.get_doors("tools", tag="tool")}
    core = {"discover", "read_floor", "tell_resolution",
            "mine_commonality", "observe", "teach", "generate",
            "save_pack"}
    ok = n >= 40 and core <= names
    check(f"T2 catalog harvests the built world ({n} tools)", ok,
          f"missing: {sorted(core - names)}" if not core <= names
          else f"{len(names)} tool nodes")

    # ── T3: informed choice — query finds the right organ ──
    r = m.query_tools("how precise is the measuring instrument — "
                      "the resolution floor of these values")
    top3 = [x["name"] for x in r["matches"][:3]]
    check("T3 'instrument resolution' query surfaces the floor organ",
          "read_floor" in top3 or "tell_resolution" in top3,
          f"top: {top3}")

    # ── T4: nothing applicable -> honest skip, never a stall ──
    r = m.query_tools("zxqv flurble")
    check("T4 empty query = honest skip", r["matches"] == []
          and "skip" in r["why"], r["why"])

    # ── T5: trial and error — run a tool through the node ──
    y = np.round(rng.uniform(0, 10, 300) / 0.01) * 0.01
    out = m.run_tool("read_floor", y)
    rec = m.net.get_meta("tool:read_floor", "record")
    ok = (out is not None and out.get("floor") is not None
          and rec["used"] == 1)
    check("T5 run_tool executes through the node; use counted", ok,
          f"floor {out.get('floor'):.5g}, used {rec['used']}"
          if out else "no result")

    # ── T6: outcome receipts — the election shape, ready ──
    m.tool_receipt("read_floor", True)
    m.tool_receipt("read_floor", False)
    rec = m.net.get_meta("tool:read_floor", "record")
    ok = rec["passed"] == 1 and rec["recent"] == [1, 0]
    check("T6 outcome receipts bank on the tool", ok,
          f"passed {rec['passed']}, recent {rec['recent']}")

    # ── T7: re-cataloging does not duplicate; records survive packs ──
    doors_before = len(m.net.get_doors("tools", tag="tool"))
    m.catalog_tools()
    doors_after = len(m.net.get_doors("tools", tag="tool"))
    a = json.dumps(m.net.get_meta("tool:read_floor", "record"),
                   sort_keys=True, default=str)
    with tempfile.TemporaryDirectory() as td:
        m.save_pack(td)
        m2 = mod.Isaac.load_pack(td)
    b = json.dumps(m2.net.get_meta("tool:read_floor", "record"),
                   sort_keys=True, default=str)
    ok = doors_before == doors_after and a == b and a != "null"
    check("T7 idempotent catalog; receipts survive packs", ok,
          f"{doors_before} -> {doors_after} tools")

    # ── T8: run_tool on an unknown tool refuses with a why ──
    out = m.run_tool("flurble")
    check("T8 unknown tool refused honestly",
          isinstance(out, dict) and out.get("refused") is True
          and "why" in out, out.get("why", "")[:50])

    n_ok = sum(CHECKS)
    print("=" * 70)
    print(f"TOOLS BATTERY: {n_ok}/{len(CHECKS)}")
    print("=" * 70)
    sys.exit(0 if n_ok == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
