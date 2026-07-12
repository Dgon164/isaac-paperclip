"""Provenance Gate battery (owner, 2026-07-12): "reconstructable
exclusively from isaac source nodes = game; requires any user nodes
= banned" + "see if it can recreate the information from public
sources too."

R1 FAIL-CLOSED: undeclared provenance counts as user -> banned
R2 banned from EXPORT, never from USE (the law still applies locally)
R3 prime-provenance knowledge is game, and the criterion is LITERAL:
   a second, prime-only leaf rebuilds the identical law
R4 mixed ancestry (user data doored onto prime knowledge) -> banned
   (any user in the closure bans)
R5 share_candidate: gate verdict filed either way; record released
   only on GAME
R6 THE RECREATION CHECK: user-told Kepler is banned — until the
   check rebuilds it from Prime's public record: provenance upgrades
   to public, export unlocks (the user data was not necessary)
R7 genuinely user-specific knowledge: recreation fails, ban stands
Run: python test_provenance.py   (from isaac_store/)
"""
import os
import shutil
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from isaac_store import bridge
from isaac_store.leaf import LeafIsaac
from isaac_store.orchestrator import Orchestrator

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_prov_")
    try:
        print("  loading engine...")
        mod = bridge.load_isaac_module()
        prime_dir = os.path.join(tmp, "prime")
        orch = Orchestrator(prime_dir)
        kepler_model = mod.Isaac._parse_equation("+1.00*x0^1.5", 1)
        orch.submit({"op": "put", "key": "node:law:kepler_public",
                     "value": {"meta": {"model": kepler_model},
                               "public": True},
                     "who": "education"})
        orch.process()
        orch.compact()

        rng = np.random.default_rng(31)
        X = rng.uniform(-2, 2, (300, 2))
        y = 2.0 * X[:, 0] * X[:, 1] + X[:, 0] ** 2

        print("R1. fail-closed: unknown provenance = user = banned")
        leaf = LeafIsaac(prime_dir, mode="ephemeral", isaac_module=mod)
        leaf.leaf_discover(X, y, "userlaw")
        ok, why, tiers = leaf.exportable("law:userlaw")
        check("user-data law banned from export",
              not ok and "user" in why and tiers == {"user"})
        ok2, _, _ = leaf.exportable("law:never_declared")
        check("even an unknown node is banned (fail-closed)", not ok2)

        print("R2. banned from export, never from use")
        p = leaf.mind.apply_law("userlaw", X)
        r2 = 1 - float(np.sum((y - p) ** 2)) / float(np.sum((y - y.mean()) ** 2))
        check("the banned law still works locally", p is not None and r2 > 0.99,
              f"local r2={r2:.4f}")

        print("R3. prime-only ancestry is game — and literally rebuilds")
        leaf.leaf_tell("kepler", "+1.00*x0^1.5", d=1, tiers=("prime",))
        ok3, why3, _ = leaf.exportable("law:kepler")
        check("prime-provenance law is exportable", ok3, why3)
        leaf2 = LeafIsaac(prime_dir, mode="ephemeral", isaac_module=mod)
        leaf2.leaf_tell("kepler", "+1.00*x0^1.5", d=1, tiers=("prime",))
        m1 = leaf.mind.net.get_meta("law:kepler", "model")
        m2 = leaf2.mind.net.get_meta("law:kepler", "model")
        check("a prime-only leaf rebuilds the identical law",
              mod.Isaac._form_signature(m1) == mod.Isaac._form_signature(m2)
              and mod.Isaac._coefs_match(m1, m2))

        print("R4. mixed ancestry bans")
        leaf.leaf_discover(X, y, "mixedlaw", data_tiers=("user", "prime"))
        ok4, why4, t4 = leaf.exportable("law:mixedlaw")
        check("any user tier in the closure bans",
              not ok4 and t4 == {"prime", "user"})

        print("R5. share_candidate: gate before scrubber")
        sc_bad = leaf.share_candidate("userlaw")
        sc_good = leaf.share_candidate("kepler")
        check("banned: no record released, why stated",
              not sc_bad["ok"] and "banned" in sc_bad["why"]
              and "record" not in sc_bad)
        check("game: record + provenance released",
              sc_good["ok"] and sc_good["record"]["provenance"] == ["prime"])
        verdicts = [f for f in leaf.mind.findings
                    if f["kind"] == "provenance_gate"]
        check("both verdicts filed locally", len(verdicts) == 2)

        print("R6. the recreation check upgrades what public sources rebuild")
        leaf3 = LeafIsaac(prime_dir, mode="ephemeral", isaac_module=mod)
        leaf3.leaf_tell("kepler_u", "+1.00*x0^1.5", d=1)  # default: user
        ok5, _, _ = leaf3.exportable("law:kepler_u")
        rc = leaf3.recreation_check("kepler_u")
        ok6, why6, t6 = leaf3.exportable("law:kepler_u")
        check("user-told Kepler starts banned", not ok5)
        check("recreated from Prime's PUBLIC record",
              rc["recreated"] and rc["source"] == "node:law:kepler_public"
              and rc["tiers"] == ["public"])
        check("export unlocked after recreation", ok6 and t6 == {"public"})

        print("R7. genuinely user-specific: ban stands")
        leaf3.leaf_tell("custom", "+0.31*x0^2", d=1)
        rc2 = leaf3.recreation_check("custom")
        ok7, _, _ = leaf3.exportable("law:custom")
        check("no public source rebuilds it -> still banned",
              not rc2["recreated"] and not ok7, rc2["why"])
        leaf.close(); leaf2.close(); leaf3.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
