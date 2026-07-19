"""tense_battery.py — PROMOTION GATE for THE TENSE TRACKER
(owner, 2026-07-19: "he doesnt have dual state tracking yet?
thing exists, but he thinks it exists for all... an update on one
thing does not update the others").

Pins:
  TT1 CREATE — present only: predicts 'Untracked files'.
  TT2 ADD — present copied to candidate: predicts 'Changes to be
      committed:' (and untracked gone).
  TT3 COMMIT — candidate snapshotted to past: predicts clean.
  TT4 THE DESYNC LAW — update AFTER commit changes present only:
      predicts 'Changes not staged for commit:'; candidate and
      past hold the OLD content simultaneously (one name, three
      values).
  TT5 THE INSTRUMENT CONFIRMS — the same sequence run in a REAL
      git repo; at every moment his predicted phrases must appear
      in real `git status` output. READ PROPOSES, THE INSTRUMENT
      CONFIRMS, at the state level.

Run: cd experiments && PYTHONHASHSEED=0 python tense_battery.py
"""
import os
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")))
from isaac_store.composer import TenseTracker    # noqa: E402


def real_git_status(repo):
    out = subprocess.run(["git", "-C", repo, "status"],
                         capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    return out.stdout


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(bool(ok))
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    tt = TenseTracker()
    tt.create("contents.md", "# contents")
    check("TT1 create — present only, predicts untracked",
          tt.predict_phrases() == ["Untracked files"]
          and tt.status()["untracked"] == ["contents.md"],
          f"{tt.predict_phrases()}")

    tt.add("contents.md")
    check("TT2 add — candidate holds it, predicts to-be-committed",
          tt.predict_phrases() == ["Changes to be committed:"]
          and not tt.status()["untracked"],
          f"{tt.predict_phrases()}")

    tt.commit()
    check("TT3 commit — all tenses agree, predicts clean",
          tt.predict_phrases() == ["working tree clean"],
          f"{tt.predict_phrases()}")

    tt.update("contents.md", "# contents\n# titles")
    st = tt.status()
    check("TT4 THE DESYNC LAW — present moved alone; candidate "
          "and past still hold the old; one name, three tenses",
          tt.predict_phrases() == ["Changes not staged for "
                                   "commit:"]
          and tt.present["contents.md"] != tt.candidate[
              "contents.md"]
          and tt.candidate["contents.md"] == tt.past[
              "contents.md"],
          f"present!={'candidate'}; {tt.predict_phrases()}")

    # TT5 — the instrument confirms, moment by moment
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["git", "-C", td, "init", "-q"],
                       capture_output=True)
        subprocess.run(["git", "-C", td, "config", "user.name",
                        "isaac"], capture_output=True)
        subprocess.run(["git", "-C", td, "config", "user.email",
                        "isaac@example.com"], capture_output=True)
        tt2 = TenseTracker()
        moments, all_ok = [], True
        # moment 1: create
        open(os.path.join(td, "contents.md"), "w").write(
            "# contents")
        tt2.create("contents.md", "# contents")
        for ph in tt2.predict_phrases():
            ok = ph in real_git_status(td)
            all_ok &= ok
            moments.append((1, ph, ok))
        # moment 2: add
        subprocess.run(["git", "-C", td, "add", "."],
                       capture_output=True)
        tt2.add()
        for ph in tt2.predict_phrases():
            ok = ph in real_git_status(td)
            all_ok &= ok
            moments.append((2, ph, ok))
        # moment 3: commit
        subprocess.run(["git", "-C", td, "commit", "-q", "-m",
                        "A: add contents.md"], capture_output=True)
        tt2.commit()
        for ph in tt2.predict_phrases():
            ok = ph in real_git_status(td)
            all_ok &= ok
            moments.append((3, ph, ok))
        # moment 4: update after commit (the desync law, real)
        open(os.path.join(td, "contents.md"), "w").write(
            "# contents\nchanged")
        tt2.update("contents.md", "# contents\nchanged")
        for ph in tt2.predict_phrases():
            ok = ph in real_git_status(td)
            all_ok &= ok
            moments.append((4, ph, ok))
        check("TT5 the instrument confirms — every predicted "
              "phrase found in REAL git status at its moment",
              all_ok and len(moments) >= 4,
              "; ".join(f"m{m}:{'Y' if ok else 'N'}"
                        for m, _p, ok in moments))

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  BATTERY: {npass} passed, {len(checks) - npass} "
          f"failed of {len(checks)}  ({dt:.1f}s)")
    sys.exit(0 if npass == len(checks) else 1)


if __name__ == "__main__":
    main()
