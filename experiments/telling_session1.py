"""telling_session1.py — THE FIRST TELLING SESSION (owner,
2026-07-18 evening: "lets see if we can start teaching him some
laws"). Plain-English laws through the telling road, into his LIVE
account — the first knowledge he is ever TOLD IN ENGLISH.

The menu (diversity ruling: new FORMS are the prize):
  recall  ohms-law            — the curriculum's knowledge read
                                back BY NAME through the new road
  tell    kepler t=a^1.5      — told-confirms-DISCOVERED (his own
                                sky law gains an owner witness)
  tell    circle a=pi*r^2     — told-confirms-TOLD (curriculum)
  tell    coulomb f=q*p/d^2   — a NEW 3-quantity form
  tell    pendulum t=2.007*l^0.5 — a NEW sqrt form
  then    coulomb VALIDATED on fresh rows (use now, believe when
                                measured — the owner's whole ask)

DRY (default): a scratch COPY of his home — full receipts, his
life untouched. LIVE (--live): his account, mind.isaac.bak first,
journal kind=telling, road-trial line.

usage: python telling_session1.py [--live] [home]
"""
import os
import shutil
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
import isaac as mod                                    # noqa: E402
from isaac_store.telling import (tell_english,         # noqa: E402
                                 recall_law)

TELLINGS = [
    "kepler's third law is t=a^1.5",
    "circle area is a=pi*r^2",
    "coulomb's form is f=q*p/d^2",
    "pendulum period is t=2.007*l^0.5",
]


def run(home, live):
    from isaac_store.sparring import IsaacAccount
    from isaac_store.roadtrial import log_roadtrial
    acct = IsaacAccount(home, mod)
    mind = acct.mind
    n_laws0 = sum(1 for n in mind.net.meta
                  if str(n).startswith("law:"))
    print(f"{'LIVE' if live else 'DRY (scratch copy)'} — account: "
          f"{home}\n  laws before: {n_laws0}")

    # 1) the recall road reads the CURRICULUM's knowledge by name
    back = recall_law(mind, "ohms-law")
    print(f"\n  recall ohms-law: "
          f"{back['said'] if back else 'NOT HELD'}"
          + (f"  [{back['state']}, who={back['who']}]"
             if back else ""))

    # 2) the tellings
    for txt in TELLINGS:
        r = tell_english(mind, txt, who="owner")
        if r.get("refused"):
            print(f"  TELL \"{txt}\" -> REFUSED: {r['refused']}")
            continue
        t = r["tell"]
        line = t.get("status")
        if line == "MATCHES":
            line += f" (form {r['form']})"
        elif line == "VARIANT":
            line += (f" (family {t.get('family', '?')[:22]}, "
                     f"sibling {t.get('sibling')})")
        print(f"  TELL \"{txt}\"\n        heard {r['said']}  ->  "
              f"{line}")

    # 3) use now, believe when measured: validate coulomb live
    rng = np.random.default_rng(11)
    q = rng.uniform(0.5, 4, 50)
    p = rng.uniform(0.5, 4, 50)
    dd = rng.uniform(1, 9, 50)
    got = mind.validate_law("coulombs-form",
                           np.column_stack([q, p, dd]),
                           q * p / dd ** 2)
    print(f"\n  coulombs-form validated on 50 fresh rows: "
          f"{got['status']} (r2 {got['r2']:.6f})")

    # 4) what he holds now, by name
    for nm in ("keplers-third-law", "coulombs-form",
               "pendulum-period"):
        b = recall_law(mind, nm)
        if b:
            print(f"  recall {nm}: {b['said']}  [{b['state']}, "
                  f"who={b['who']}, witnesses {b['witnesses']}]")

    n_laws1 = sum(1 for n in mind.net.meta
                  if str(n).startswith("law:"))
    print(f"\n  laws after: {n_laws1} (+{n_laws1 - n_laws0})")

    if live:
        acct._journal(dict(
            kind="telling",
            stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            told=TELLINGS,
            note="the first plain-english telling session; "
                 "who=owner; validated coulombs-form live"))
        mind.save(acct.mind_path)
        line = log_roadtrial(home, mind, mod)
        print(f"\n  TELLING JOURNALED + mind saved; road-trial "
              f"line:\n  {line}")
    else:
        print("\n  DRY — nothing saved; his life untouched.")


def main():
    args = [a for a in sys.argv[1:] if a != "--live"]
    live = "--live" in sys.argv[1:]
    home = args[0] if args else os.path.join(
        os.path.expanduser("~"), "Documents", "isaac_home")
    if live:
        shutil.copy2(os.path.join(home, "mind.isaac"),
                     os.path.join(home, "mind.isaac.bak"))
        print(f"[mind.isaac.bak written]")
        run(home, True)
    else:
        with tempfile.TemporaryDirectory() as td:
            scratch = os.path.join(td, "isaac_home_scratch")
            shutil.copytree(home, scratch)
            run(scratch, False)


if __name__ == "__main__":
    main()
