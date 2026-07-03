# RESULTS LEDGER — every claim, its script, its last verification

**Rule:** a number may be quoted in this repo only if it has a row here.
Re-running is optional — this ledger + `runs/<date>/` are the stored evidence;
re-run any row's script to check it yourself. All randomness is seeded; the
battery CSVs come out **byte-identical** across re-runs.

**Statuses:**
- **VERIFIED** — re-run from this repo on the date shown; observed = claimed.
- **VERIFIED\*** — re-run, with a stated deviation or caveat.
- **RECORDED** — the number is from a documented past run, but the exact
  script/variant is NOT in this repo — quote only with the caveat.
- **NEEDS-DATA/TIME** — script is in this repo and believed good, but needs
  large datasets in `data/` (gitignored) or a long run; not re-verified today.

`data/` note: gitignored. On the home machine it is a junction to the parent
project's data directory (HIGGS.npy 1.2 GB, clocks, NORB, FSDD, Omniglot,
CIFAR, sunspots.csv, fraud_*.npy). A fresh clone populates it per the
per-row notes below.

## Engine

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| Self-test 10/10 capability areas | `python isaac.py` (repo root) | **VERIFIED** | 2026-07-03 | 10/10, 9.2 s (`runs/2026-07-03/selftest.txt`); discovery area 8/8 after the accounting was added |
| **THE ACCOUNTING (audit 2.8): articulated% + captured% + noise% = 100 per discover(), residual dossier attached** | in-engine, self-test (g) | **VERIFIED** | 2026-07-03 | planted law + known 26.5% noise share → measured articulated 72.7% (true 73.5%), sums to 100; pure noise → 0/0/100; red team + E9 0/20 unchanged after the capture-null fix |
| Kepler `T = a^1.5` UNDERSTOOD, R² 1.0000 | inside `cross_domain.py` retest | **VERIFIED** | 2026-07-03 | UNDERSTOOD, families found: 3 |
| Pluto 248.0 yr predicted via inherited ledger law / web UI | ledger+UI demo flow (`ui/isaac_ui.py`) | RECORDED | 2026-07-02 | 247.96 via web form (UI now in repo; demo flow not scripted) |

## Rebuilds A–F (planted ground truth)

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| A: proximity doors 4/4 — diagonal 99.0% vs box 88.0%; re-encoding invariance 100% vs 82.2% | `doors_proximity.py` | **VERIFIED** | 2026-07-03 | exact match, 0.2 s |
| B: uptake-edge composition 7/7 (dismantled-engine control; old membership = same identity) | `composition_uptake.py` | **VERIFIED** | 2026-07-03 | WORKS, 0.1 s |
| C: staged enumerator 4/4 — planted forms exact R² 1.000; noise → NO RULE 0 terms; old poly-L1 keeps 26 junk terms | `enumerator_staged.py` | **VERIFIED** | 2026-07-03 | exact match, 0.4 s |
| D: wave crystallizer 5/5 — planted groups/handoffs/circles exact; shuffled-time control kills movement; level-2 circle-of-circles | `wave_crystallizer.py` | **VERIFIED** | 2026-07-03 | WORKS, 0.5 s |
| E: interference 5/5 — masking discovered; 3-state readout 97.1%/tick | `wave_interference.py` | **VERIFIED** | 2026-07-03 | WORKS, 0.5 s |
| F: entity statuses 5/5 — clock 99.3% phase (99.2% during occlusion); statuses-are-doors explanation emerges | `entity_status.py` | **VERIFIED** | 2026-07-03 | WORKS, 0.4 s |

## Discovery stack (batteries + red team)

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| 0 false discoveries on pure noise | `discovery_battery.py` (E9) | **VERIFIED** | 2026-07-03 | **0/20** — the "0/40 across two batteries" phrasing in older docs was drift; 0/20 is the number this repo demonstrates |
| Battery failure-map (noise floor, sample onset, off-grid reach ≲2× grid, honest PARTIAL on nested sin) | `discovery_battery.py` | **VERIFIED** | 2026-07-03 | 11 s; CSV byte-identical to committed `discovery_battery_results.csv` |
| Wave battery scaling (groups/edges/circles vs length, flicker, dwell; zero noise-door admissions) | `wave_battery.py` | **VERIFIED** | 2026-07-03 | 18 s; noise column 0.0 in every row; CSV byte-identical |
| Red team: 0 kills, 0 crashes (8 adversarial attacks) | `redteam_discovery.py` | **VERIFIED** | 2026-07-03 | 6 SURVIVED + 2 FLESH WOUND, 1.1 s |
| Cross-domain: gravity ≡ coulomb exact; magnetism cold 0.821 → analogy-primed 0.995 (constant 3.26 vs true 3.2) | `cross_domain.py` | **VERIFIED** | 2026-07-03 | exact match, 4.2 s |

## Perception / classification

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| Toy collider: invariant recovered exactly; hidden resonance 96% purity / 100% recall | `demos/unsup_discover.py` | **VERIFIED** | 2026-07-03 | `+1.00·E² −1.01·px² −1.00·py²`; 96/100; 0.2 s |
| Perception lens on digits (boxes as concept-nodes in Isaac) | `demos/crystal_in_isaac.py` | **VERIFIED** | 2026-07-03 | 92.4% held-out, 1.5 s |
| Digits structural doors ~91% clean | `digits_structural.py` | **VERIFIED\*** | 2026-07-03 | observed 90.7% (docs recorded 91.5% — treat 90.7 as the repo's number) |
| Ideals + differentia 99.7% on six-way look-alike world; unreliable taught feature demoted | `ideals_differentia.py` | **VERIFIED** | 2026-07-03 | 99.7%, 1.6 s |
| Condensation scaling: per-item cost flat while naive grows; purity rises | `condensation_scaling.py` | **VERIFIED** | 2026-07-03 | 1.5 s |
| **Registration 84% under random position+size (16×16 canvas)** | `registration_perception_16.py` (rebuilt 2026-07-03) | **VERIFIED** | 2026-07-03 | raw canvas 23.7% → registered **84.4%** (recorded 84.4 — vindicated); novel bigger sizes 13–15 never trained: **85.4%** (recorded 86.5); tiny 6–7: 58.3% = information floor; clean control 89.1% exact; pose readout exact. VERDICT WORKS |
| Registration mechanism at 8×8 (edge-clipping caveat) | `registration_perception.py` | **VERIFIED\*** | 2026-07-03 | 8×8 canvas clips shifted pixels (information destruction): ~5–15% → 21–53%; kept as the caveat case |

## Real data (full datasets)

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| Covtype flat doors 56.2% (vs box 49.3%); class-conditional variant BROKEN ~20% (kept as marked failure) | `covtype_real_test.py` | **VERIFIED** | 2026-07-03 | 56.15% / 20.45%, 14 s (sklearn covtype cache) |
| Covtype compounds: 25 null-gated compound doors, 56.2 → 59.0%; captured road 90.0% (5-NN, 200k exemplars) | `covtype_compounds.py` | **VERIFIED** | 2026-07-03 | 25 admitted / 58.97% / 89.98%, 34 s |
| Covtype door-weighted exemplars ~94–95% (differentia weights, all 406k, k=1) | `covtype_door_weighted.py` (rebuilt 2026-07-03) | **VERIFIED\*** | 2026-07-03 | **95.3%** (recorded 94.4 — vindicated); learned weights readable: elevation 0.78 (recorded 0.76), then wilderness/roads/fire. **BUT read the next row before quoting this one.** |
| Covtype row-index-alone control (spatial leakage) | `covtype_door_weighted.py` | **VERIFIED — SUPERSEDES the recorded 79.1%** | 2026-07-03 | k=1 nearest ORIGINAL ROW INDEX, zero terrain features: **94.8%**. The recorded 79.1% was a weaker control protocol. The sharp control shows the covtype captured tier (90–95%) barely beats pure map-reading — **the honest covtype achievement is the articulated tier (56.2 → 59.0%)**; the exemplar numbers measure the dataset's spatial ordering as much as the terrain. This is the null-discipline law operating: the leakage null attacks exactly what the exemplar claim uses. |
| HIGGS doors 64.6% / AUC 0.700 on 11M rows | `higgs_real_test.py` (needs `data/HIGGS.npy`) | **VERIFIED** | 2026-07-03 | 64.64% / AUC 0.700, 70 s total |
| HIGGS m_jj wall: poly-L1 ~0.05, staged ~0.03, true-form cap R² 0.065 → proven DATA wall | `higgs_real_test.py` | **VERIFIED\*** | 2026-07-03 | old 0.050 / staged 0.033 observed (the 0.065 true-form scan is in the recorded diagnostic, not this script's output) |
| HIGGS physics naming + invariant-mass reconstruction R² ≈ 0.865 | `demos/interaction_extract.py`, `demos/higgs_residual.py` | NEEDS-DATA | — | needs `fetch_openml(23512)` download; not re-run today |

## Gauntlet (10 datasets, one frozen pipeline)

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| Scoreboard: mnist 95.2 / fashion 76.5 / cifar 32.6 (designed face-plant) / omniglot 1-shot 51.6 / fsdd 92→54 / smallnorb 87.7 / fraud recall 79 / kepler+noise honest refusals / sunspots NO RULE post-cap | `gauntlet.py` | NEEDS-DATA/TIME | (2026-07-02 recorded) | script now in repo with repo-local paths; needs `data/` populated (mnist/fashion via openml, cifar/fsdd/omniglot/norb archives, `fraud_*.npy`, `clocks_48.npz` from `clock_world.py`, `sunspots.csv`); multi-hour run |
| Clocks 22.9% | `gauntlet.py` | RECORDED (known harness bug) | (2026-07-02) | the readout peak-picking is the bug, engine unimplicated — repair before re-quoting |

## Known-stale numbers — do NOT quote

- "0/40 false discoveries across two batteries" → the verifiable number is 0/20 (discovery battery E9) plus a clean red team and zero wave noise admissions.
- Covtype "79.1% row-index control" → superseded by the sharp control: **94.8%** (see row above). Quoting 94–95% covtype exemplar accuracy without the leakage row next to it is dishonest — the articulated tier (56–59%) is the achievement.
- Registration "86.5%" novel-bigger → the rebuilt harness observes 85.4%; quote the observed number.
- "Self-test 5/5, 6/6, 7/7, 9/9" in older docs → the suite is 10/10 (grew over 07-01/02).
- Engine "~2,900 lines" → ~3,500 (accounting added 07-03).
