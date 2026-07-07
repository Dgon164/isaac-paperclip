# Research Line — Handoff (early July 2026)

The `research/` line: the step from "an engine that runs methods" to **an autonomous,
honest researcher** that assembles its own data from real-world mess, discovers,
**judges honestly** (a full epistemic vocabulary), forges its own tools, and
**accumulates across time**. Every piece is an external harness on the existing
`../isaac.py` — the capability is in the *composition*, not new engine primitives.
Holonic by design: each script is a whole and a part.

---

## How to continue (environment)

- **Laptop setup:** Python 3.12.7 (per-user from python.org — the Store `python.exe`
  is a dead stub; use the venv or the `py` launcher). PortableGit at
  `%LOCALAPPDATA%\PortableGit\cmd\git.exe` (no admin). Repos at
  `C:\Users\Turtle\Desktop\Isaac\{isaac-paperclip, isaac-project}`.
- **venv:** `isaac-paperclip\.venv` — has numpy 2.5, scipy, scikit-learn, pandas.
  Run any research script: `.venv\Scripts\python.exe research\<x>.py` with
  `$env:PYTHONUTF8=1`. Scripts import `../isaac.py` via a relative `sys.path` insert.
- **Data (gitignored):** `research/data/wx.csv.gz` — fetch with
  `Invoke-WebRequest https://bulk.meteostat.net/v2/hourly/10637.csv.gz -OutFile research/data/wx.csv.gz`
  (Frankfurt hourly, 1926–present; meteostat schema, no header — see any script's NAMES).
- **Sync:** `git push` from the workstation, `git pull` here. The numpy-2 compat fix
  (removed 2-D `np.cross`) is committed (`6872e57`) so the perception path runs on modern numpy.
- **`divergence_probe`** lives in `git stash@{0}` AND `research/divergence_probe.patch`
  (per-law extrapolation-confidence; the scorer that stops surrogates being crowned).

---

## What was built (each a working demo on `../isaac.py`)

| file | what it does | status |
|---|---|---|
| `method_discovery.py` | raw data + a toolkit → find the KEY that derives the answer (unprompted) | found `identity`/`log`/`diff` correctly |
| `self_verify.py` | confirm/deny own findings via **held-out + permutation null** | 3 honest states: CONFIRM / DENY-empty / DENY-partial |
| `researcher_loop.py` | closed loop: decompose → verify → find the **constant core** → retain as a **holon** → reuse | velocity/acceleration tower; transfer worked |
| `orchestrator.py` | **persistent lifetime**: boot from prior self, work a bounded burst, commit, save | proven across 3 reboots; `isaac_state.pkl` is its saved mind (gitignored) |
| `orchestrator_parallel.py` | concurrent fork-workers, **composition search** | ~2.9× concurrency; cracked `combo_lock` via `diff→log` |
| `tool_creation.py` | the **toolkit grows itself** — mint successful compositions as new keys | works; out-of-range gate is load-bearing (w/o it, fooled by surrogates); primitive-forge scoped |
| `real_data_discovery.py` | **unsupervised** on raw weather: which column is lawful vs independent | uncovered dew-point↔temp↔humidity trio (R²=1.0); refused wind/pressure |
| `matrix_assembler.py` | **the matrix-creator**: build discover-ready matrices from messy/ragged/missing data | missing = absent dim (`complete`/`pad`); no global drop |
| `best_guess.py` | **usable-pattern vs resolved-cause** verdict; confound detection by conditioning | flags confound (`B←A` via `C`), keeps genuine direct |
| `meaningful_absence.py` | detect **what should be there but isn't** (Mendeleev) | flags interior gaps, not edges; MISSING vs FORBIDDEN |
| `temporal_detector.py` | **the clock**: detect time columns, tick+span, cycles + trends + anchor events | recovered seasons, a real warming trend (+3.3 °C/century, null-gated), record days |
| `redteam.py` | adversarial **honesty battery** — try to make the gates lie | **6 held, 0 failed, 1 documented limit** |
| `divergence_probe.patch` | per-law extrapolation confidence (the surrogate killer) | stashed; reconcile into `rivals` |

---

## The epistemic vocabulary developed (each with a gate + a resolution-path)

```
UNDERSTOOD          the form, and direct-consistent
BEST-GUESS          usable pattern, cause UNRESOLVED   → investigate / intervene
CAPTURED            real but weak; only a rough shape
MEANINGFUL ABSENCE  should be there and isn't          → MISSING (predict it) / FORBIDDEN (find suppressor)
idk (shrug)         no handle — but the shape of what would help  (a −0, a shaped hole)
NOISE / absent      nothing there (a true 0)
```

Two orthogonal axes: **predictive power** (idk→captured→pattern→law) × **causal
resolution** (unresolved→resolved). Quaternary logic: yes / no / **idk** (undetermined,
a shaped hole = the agenda for autonomy) / **irrelevant** (absent, no expectation).

---

## Design principles / laws established this session

- **Relative-native default** — committed to `docs/DESIGN_INTENT.md` (`177240b`).
  Compute in relative space; absolute = ONE correction factor, applied last,
  cross-checked, never baked in. Measured 0.15% (relative) vs 18% (absolute).
- **The out-of-range gate is load-bearing.** In-range R² *lies* (surrogates). A claim
  must hold on data it never saw. This underpins self-verify, tool-creation, best-guess.
- **Missing = an absent dimension, not a row to drop.** Assume data is flawed, a
  subsample, always missing something. `discover` needing a clean matrix is fine;
  the **matrix-CREATOR** is the critical capability.
- **Holonic chain-of-functions.** The assembler (data-functions) and the toolkit
  (transform-keys) are the *same* composition mechanism; go as granular as needed.
- **Bounded autonomy is the goal** (close your own `idk`s, driven by the residual /
  prediction-error / negentropy). **Unbounded** (choose what *matters*) stays seeded —
  and that's honest, not a shortfall.

---

## Honest assessment (read this before trusting anything here)

- Everything in `research/` is a **working demo, not a proven capability.** Each shows
  its mechanism **once, on a case chosen to make it work.**
- The real-data result (weather) is genuine and verifiable — but it's **one dataset**
  and **known physics** (verification, not new discovery — the correct *first* result).
- The proof layer is **started (red-team spine) but thin**, and capabilities are being
  added faster than they're proven. Nothing is graduated into the engine's self-test.

---

## TODO (priority order)

1. **Proof layer catch-up (HIGHEST).** Extend `redteam.py` to the *new* gates: the clock
   (plant a spurious cycle + a sparse-data fake trend — must refuse), the assembler
   (`pad` must never fabricate), tool-creation (a surrogate must NOT be minted). Add
   per-capability batteries with dated runs in `research/runs/` (mirror `experiments/`).
2. **Real-data breadth.** 2–3 more real datasets beyond weather, verified where possible.
3. **Graduate survivors** into `isaac.py` + the 11/11 self-test — stop being a parallel folder.
4. **Integration.** Compose the chain end-to-end in the orchestrator:
   `assemble → detect time/place → discover → judge (verdict) → persist`, accumulating
   across sessions. The holonic whole from the holonic parts.
5. **Reconcile `divergence_probe`** (stash/patch) into `rivals`/the method-scorer, per
   DESIGN_INTENT (door onto existing organs, don't bolt on a parallel system).
6. **CAPTURED-smooth tier + deflate-recurse.** A *simple smooth* statistical model of the
   residual (null-gated, labeled CAPTURED), used to describe latent-but-unresolvable
   signal AND to deflate → re-discover a deeper layer.
7. **Wire the clock into the assembler** as a column-type detector; add the spatial
   ("where") analogue.
8. **Frontier (later).** Cross-net / D5 meta-structure — compare whole nets for shared
   *relational-signature* motifs (needs a planted-motif gauntlet + a brutal null; runs
   into the unsupervised-aligner problem, so approach via relational signatures). Also:
   tool-creation for genuinely-new discontinuous primitives (`sign`/`floor`/threshold).

---

## Goals / directions / objectives

- **Ultimate objective:** point the whole autonomous, honest, self-growing researcher at
  **real data the owner cares about** — unknown-answer domains (fire/tree ecology was
  raised) — and uncover genuine structure a black box couldn't give: a legible law +
  an honest *"here's what I can't explain and what to check next"* + cross-domain reuse.
- **The differentiated lane** (from the honest review at the start): NOT prediction
  accuracy (deep nets win that, and chasing it wastes the project). Isaac's real edge =
  **legible discovery + honest uncertainty/refusal + cross-domain**, on real data. The
  bar to aim at: *do something a black box structurally cannot, on real data, undeniably.*
  Concrete neutral first target: **SRBench / the Feynman symbolic-regression benchmark**
  (real competitors, leakage-free) — this is where a clean win is both achievable and
  worth something.
- **The autonomy objective:** bounded, self-fueled inquiry — an **`idk`-ledger** (shaped
  holes) + a **drive** to close them (prediction-error / negentropy) + method-discovery
  to attack them + self-verification + retention. The persistent orchestrator is the
  seed; parallel workers and tool-creation extend it. *Learning harder things needs
  persistence* — structure must accumulate across sessions to cross the crystallization
  phase-transition threshold; a fresh-boot mind stays "seconds old."

---

## Project context (the map under all of this)

Isaac is a **differentiation-based** engine (compare two things, keep what recurs;
knowledge is legible **doors** that compile to a matrix; every claim beats a **null**).
The owner's theory names what this line implements: the **Intellon method**
(compression / expansion / emergence / breakdown), **Understanding-as-Closure** (the
four verdicts UNDERSTOOD/PARTIAL/CAPTURED/NO-RULE *are* the four states of a closure;
"every closure must beat its null"), the **Puzzle-Piece theory** (superlinear
accumulation → holographic recursion → downward inference *is* understanding), and
**DIM** (shared/divergent/absent from comparison alone). This session largely
**re-derived and extended Understanding-as-Closure and Puzzle-Piece from the
implementation side** — and added the pieces the theory named but hadn't wired: the
matrix-creator, the BEST-GUESS (usable-vs-causal) verdict, meaningful-absence, the clock,
and the honesty red-team. Standing law the whole thing obeys: **confident-wrong is the
only true failure.**
