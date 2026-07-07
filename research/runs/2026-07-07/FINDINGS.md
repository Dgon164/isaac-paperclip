# Proof-layer catch-up — findings (2026-07-07)

TODO #1 from `HANDOFF.md`: extend the honesty red-team to the *new* gates (the clock,
the assembler, tool-creation), with dated runs. Done, and not made easy — several trials
were designed to **find** failures. Run log: `redteam_all.txt` (this folder).

**Grand total: 25 held, 1 failed, 3 known-limit (of 29 trials, 4 batteries).**
The one FAIL is a naive-baseline null kept visible *on purpose*, with its cure passing in
the adjacent row. Read the tables, not the totals.

To reproduce: `.venv\Scripts\python.exe research\redteam_all.py` (`$env:PYTHONUTF8=1`).

---

## What was built

- **Made the three demo scripts importable** — the batteries test the *real* gate code,
  not a drifting copy. `temporal_detector.py`, `matrix_assembler.py`, `tool_creation.py`
  now guard their demos under `if __name__ == "__main__":`; the clock additionally exposes
  `trend_gate()` and `cycle_gate()`.
- **`redteam_clock.py`, `redteam_assembler.py`, `redteam_tools.py`** — per-capability
  adversarial batteries. **`redteam.py`** refactored to the same `run()/report()` shape.
  **`redteam_all.py`** runs all four and archives a dated log to `research/runs/<date>/`.
- **Block-permutation null** added to `trend_gate(..., null="block")` — the autocorrelation-
  aware null the old handoff named ("block-permutation null") but never built.

---

## The gates that HELD (legitimately)

- **Tool-creation surrogate gate (6/6).** A Runge surrogate that discover crowns in-range
  (R²=1.00) is **rejected out-of-range** by the mint gate. Pure noise → nothing born. tanh
  (no exact key form) → honest idk, no false law. Positive controls hold: `combo_lock` mints
  `diff.log`; a genuine reciprocal law is solved. The gate isn't just refusing everything.
- **Assembler no-fabrication (5/6 + 1 limit).** `complete` returns exactly the present rows,
  no NaN. `pad`'s presence flag matches the mask exactly. On noise, pad invents no law. Under
  **MNAR where the signal IS the absence**, pad surfaces it as the flag (|c_flag|=0.98 vs
  |c_val|=0.01) — absence recorded, not fabricated away. Mean-imputation does **not** corrupt
  a recovered slope (2.00 vs true 2.00) — the flag absorbs the imputed cluster.
- **Clock cycle gate + calibrated trend.** Real seasonal cycle → UNDERSTOOD R²=1.0; random
  phase vs noise → NO RULE (no spurious cycle). Flat iid noise and a sparse 6-year series →
  ~4% false-REAL (calibrated, not inflated by small N).

---

## The FAILURE, and why (kept visible)

- **The iid trend null LIES on autocorrelated data.** On AR(1) noise (φ=0.8, no trend) the
  iid label-shuffle null calls a trend REAL **56.5%** of the time; on a random walk, **91%**.
  Shuffling destroys the autocorrelation, making the null far too narrow. This is the
  sunspot-runaway lesson, now demonstrated concretely on the clock's trend gate.
- **The cure works (for the stationary case).** The **block-permutation null** (preserves
  autocorrelation) drops the AR(1) false-REAL rate to **11.5%** while keeping **100%** power
  on real trends. This is a legitimate fix, not a threshold tweak.

## The LIMITs (honest boundaries, documented not hidden)

1. **Non-stationary random walk (unit root).** Block null helps (91% → 68%) but does not
   fully cure it — a unit-root series violates the exchangeability every permutation null
   assumes. Needs explicit non-stationarity/drift handling. **Open item.**
2. **`complete` under collider selection (Berkson).** Two **independent** variables (full
   r≈0.00), with `p` missing based on a collider of the two, produce a **fabricated −0.51
   correlation** in the complete subset. Complete-case assembly assumes missingness is
   independent of the relationship; when it isn't, the assembled matrix carries an invented
   association. A limit of `complete` mode, not a bug in `assemble`.
3. **Confound vs mediation** (carried from `redteam.py`) — both die under conditioning;
   observation alone can't separate them.

---

## Bonus: the real-data result re-validated under the honest null

The project's flagship real result — Frankfurt **+3.29 °C/century** warming — was originally
gated by the (now-known-invalid) iid null. Annual means have lag-1 autocorrelation **0.50**,
so this mattered. Re-tested under the block-permutation null: **still REAL, +3.29 °C/century**.
The trend is strong enough to survive the correct null. `temporal_detector.py`'s demo now uses
`null="block"` so the flagship demo is methodologically honest (same number).

---

## Next (proof layer)

- Non-stationarity detection for the trend gate (unit-root / drift-on-increments) — close
  LIMIT #1. Then re-test the sunspot multi-cycle claims under the honest null.
- Batteries for the remaining new gates: `best_guess` (confound resolution-path),
  `meaningful_absence` (MISSING vs FORBIDDEN), `self_verify` (permutation-null honesty).
- Then TODO #2 (2–3 more real datasets) and #3 (graduate survivors into `isaac.py`'s self-test).
