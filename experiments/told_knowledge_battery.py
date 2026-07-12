"""Told-knowledge battery — direct equations as supersession test
candidates (owner design, 2026-07-12).

TK0 Isaac parses HIS OWN printed equation back into a working law
TK1 a told law is usable IMMEDIATELY (apply_law exact on truth)
TK2 but carries NO belief until data: law_confidence is None
TK3 RETENTION: save_pack -> load_pack -> the told law still works,
    status intact (memory across sessions is the ordinary pack road)
TK4 duel, told law TRUE: challenger cannot beat it -> TOLD-CONFIRMED,
    belief EARNED from the data (ranges + edge-r2 now present)
TK5 duel, told law WRONG: fresh discovery wins -> the told law is
    SUPERSEDED, kept wearing its defeat (why + numbers), and the
    active law now predicts correctly
TK6 match check: a same-form submission becomes a confirming WITNESS
    on the existing law, never a duplicate node
Run: python told_knowledge_battery.py   (from experiments/)
"""
import os
import shutil
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from isaac_store import bridge  # noqa: E402

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    PASS += ok
    FAIL += (not ok)


def main():
    tmp = tempfile.mkdtemp(prefix="isaac_told_")
    try:
        print("  loading engine...")
        mod = bridge.load_isaac_module()
        rng = np.random.default_rng(11)

        print("TK0. Isaac parses his own printed equation")
        i0 = mod.Isaac()
        X0 = rng.uniform(-2, 2, (400, 2))
        y0 = 3.0 * X0[:, 0] * X0[:, 1] + X0[:, 0] ** 2
        i0.discover(X0, y0, name="own")
        printed = i0.findings[-1]["equation"]
        i1 = mod.Isaac()
        r = i1.tell_law("reparsed", printed, d=2)
        p_own = i0.apply_law("own", X0)
        p_re = i1.apply_law("reparsed", X0)
        check("printed equation round-trips into a working law",
              r["status"] == "TOLD-UNVERIFIED" and p_re is not None
              and float(np.corrcoef(p_own, p_re)[0, 1]) > 0.9999,
              printed[:60])

        print("TK1. told law usable immediately")
        kepler = mod.Isaac()
        kepler.tell_law("kepler", "+1.00*x0^1.5", d=1)
        a = rng.uniform(0.3, 30, (300, 1))          # semi-major axis
        T = a[:, 0] ** 1.5                           # orbital period
        pred = kepler.apply_law("kepler", a)
        ss = float(np.sum((T - pred) ** 2)) / float(np.sum((T - T.mean()) ** 2))
        check("told Kepler applies exactly", pred is not None and ss < 1e-12,
              f"r2={1 - ss:.6f}")

        print("TK2. no belief without data")
        conf = kepler.law_confidence("kepler", a)
        check("law_confidence None until validated (belief is measured)",
              conf is None)
        st = kepler.net.get_meta("law:kepler", "status")
        check("status carries provenance", st["state"] == "TOLD-UNVERIFIED"
              and st["provenance"] == "told")

        print("TK3. retention across sessions (the pack road)")
        d = os.path.join(tmp, "mind_packs")
        kepler.save_pack(d)
        resumed = mod.Isaac.load_pack(d)
        p2 = resumed.apply_law("kepler", a)
        st2 = resumed.net.get_meta("law:kepler", "status")
        check("told law survives save/load and still applies",
              p2 is not None and np.allclose(p2, pred)
              and st2["state"] == "TOLD-UNVERIFIED")

        print("TK4. the duel when the told law is TRUE")
        noisy_T = T + rng.normal(0, 0.02 * T.std(), len(T))
        duel = resumed.supersession_duel("kepler", a, noisy_T)
        st3 = resumed.net.get_meta("law:kepler", "status")
        m3 = resumed.net.get_meta("law:kepler", "model")
        check("true told law CONFIRMED", duel["verdict"] == "CONFIRMED",
              f"incumbent r2={duel['r2_incumbent']:.4f} vs "
              f"challenger {duel['r2_challenger']:.4f}")
        check("belief earned: ranges + edge-r2 now on the law",
              st3["state"] == "TOLD-CONFIRMED" and "ranges" in m3
              and m3["r2_edge"] > 0.99)
        conf2 = resumed.law_confidence("kepler", a)
        check("law_confidence now answers", conf2 is not None
              and float(np.mean(conf2)) > 0.9)

        print("TK5. the duel when the told law is WRONG")
        w = mod.Isaac()
        w.tell_law("wrong", "+1.00*x0^2", d=1)      # told: T = a^2 (false)
        duel2 = w.supersession_duel("wrong", a, noisy_T)
        stw = w.net.get_meta("law:wrong", "status")
        check("wrong told law SUPERSEDED by discovery",
              duel2["verdict"] == "SUPERSEDED",
              f"told r2={duel2['r2_incumbent']:.3f} vs "
              f"discovered {duel2['r2_challenger']:.4f}")
        check("the defeat is KEPT with why + numbers",
              stw["state"] == "DISCOVERED-SUPERSEDED-TOLD"
              and len(stw["superseded"]) == 1
              and "lost the supersession duel" in stw["superseded"][0]["why"])
        p3 = w.apply_law("wrong", a)
        ss3 = float(np.sum((T - p3) ** 2)) / float(np.sum((T - T.mean()) ** 2))
        check("active law now predicts correctly", 1 - ss3 > 0.99,
              f"r2={1 - ss3:.4f}")

        print("TK6. match check: same form -> witness, not duplicate")
        r2_ = resumed.tell_law("kepler_again", "+0.99*x0^1.5", d=1)
        st4 = resumed.net.get_meta("law:kepler", "status")
        check("same-form submission MATCHES the existing law",
              r2_["status"] == "MATCHES" and r2_["law"] == "kepler")
        check("filed as a confirming witness on that law",
              len(st4.get("witnesses", [])) == 1
              and "law:kepler_again" not in resumed.net.meta)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  BATTERY: {PASS} passed, {FAIL} failed of {PASS + FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
