"""tutor_probe.py — the correction loop, live (owner, 2026-07-12:
"talk or say something, check for a response, and correct him on
what he should have said if he failed, or correct him on what he
should have said better if he passed").

Runs tutored sessions in Isaac's own account: the local model plays
tutor (VERDICT/SAY/NEXT format; unparseable judgments teach nothing),
corrections stored as told speech, wrongs kept with their
corrections, corrected contexts reused on sight.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                    # noqa: E402
from isaac_store.sparring import (IsaacAccount, OllamaPartner,  # noqa: E402
                                  run_tutored_session)

MODEL = "mistral:latest"      # the 1.5B could not hold the format
                              # (0 corrections banked — parse refused
                              # every broken judgment, honestly)


def main():
    home = os.path.join(os.path.expanduser("~"), "Documents",
                        "isaac_home")
    acct = IsaacAccount(home, mod)
    partner = OllamaPartner(MODEL, max_calls=80, temperature=0.2)
    if not partner.reachable():
        print("REFUSED: no local partner reachable")
        sys.exit(1)
    before = len(acct.mind.net.get_meta("speech:wrong", "record") or [])
    lines = [f"TUTOR PROBE — corrections are language's residual",
             f"account: {home} ({acct.fragments()} fragments held)", ""]
    for s in range(2):
        tr = run_tutored_session(acct.mind, partner, turns=10)
        lines.append(f"── tutored session {s + 1} ──")
        for t in tr:
            tag = f" [{t['source']}]" if t["who"] in ("isaac",) else ""
            lines.append(f"  {t['who']:7s}: {t['text'][:70]}{tag}")
        lines.append("")
    acct.mind.save(acct.mind_path)
    wrongs = acct.mind.net.get_meta("speech:wrong", "record") or []
    corrected = sum(1 for n in acct.mind.net.meta
                    if str(n).startswith("speech:corrected:"))
    srcs = {}
    lines.append(f"corrections banked this probe: {len(wrongs) - before}"
                 f" (total wrongs kept: {len(wrongs)}); corrected "
                 f"contexts held: {corrected}")
    report = "\n".join(lines)
    print(report)
    out = os.path.join(ROOT, "experiments", "runs", "2026-07-12")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "tutor_probe.txt"), "w",
              encoding="utf-8") as f:
        f.write(report + "\n")


if __name__ == "__main__":
    main()
