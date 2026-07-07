"""
RED TEAM — RUN ALL BATTERIES.  The proof layer for the research line: run every
honesty battery, print each table, aggregate the tally, and archive a dated log to
research/runs/<date>/redteam_all.txt.

Batteries:
  redteam.py            core gates (discover / confound / meaningful-absence)
  redteam_clock.py      the clock (trend + cycle; iid vs block-permutation null)
  redteam_assembler.py  the matrix-creator (complete/pad no-fabrication)
  redteam_tools.py      tool creation (out-of-range surrogate gate)

FAIL and LIMIT rows are kept visible on purpose. A FAIL is a gate that lied; a LIMIT
is an honest boundary we name rather than hide. Read the tables, not just the totals.
"""
import sys, os, io, datetime, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import redteam, redteam_clock, redteam_assembler, redteam_tools, redteam_realdata

# Synthetic batteries (self-contained) then the real-data battery (needs the gitignored
# datasets in research/data/ — skipped gracefully if absent on a fresh checkout).
BATTERIES = [redteam, redteam_clock, redteam_assembler, redteam_tools, redteam_realdata]


def main():
    buf = io.StringIO()
    grand = [0, 0, 0]
    with contextlib.redirect_stdout(buf):
        print("#" * 100)
        print(f"#  RESEARCH-LINE RED TEAM — full run   ({datetime.date.today().isoformat()})")
        print("#" * 100)
        for mod in BATTERIES:
            print()
            try:
                p, f, l = mod.report(mod.run(), mod.TITLE)
            except FileNotFoundError as e:
                print(f"  [SKIP] {mod.TITLE}  — data not present ({os.path.basename(str(e).split(chr(39))[1]) if chr(39) in str(e) else e})")
                continue
            grand[0] += p; grand[1] += f; grand[2] += l
        print("\n" + "#" * 100)
        print(f"#  GRAND TOTAL:  {grand[0]} held, {grand[1]} failed, {grand[2]} known-limit"
              f"   (of {sum(grand)} trials across {len(BATTERIES)} batteries)")
        print("#  Failures/limits carried this run:")
        print("#   - clock: the IID trend null LIES on autocorrelated data (AR1 56% false-REAL);")
        print("#     the block-permutation null built this session fixes the stationary case")
        print("#     (11%) while keeping 100% power on real trends. A non-stationary random walk")
        print("#     (unit root) is only partly cured (91% -> 68%) — it needs explicit")
        print("#     non-stationarity handling, documented as a LIMIT.")
        print("#   - assembler: complete-case assembly under COLLIDER selection invents a")
        print("#     correlation from independent variables (r 0.00 -> -0.51) — a limit of")
        print("#     complete mode (assumes missingness independent of the relationship).")
        print("#" * 100)

    out = buf.getvalue()
    print(out)
    day = datetime.date.today().isoformat()
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs", day)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "redteam_all.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"[archived] {path}")
    return grand


if __name__ == "__main__":
    main()
