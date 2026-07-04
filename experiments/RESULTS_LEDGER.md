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
| Self-test 11/11 capability areas | `python isaac.py` (repo root) | **VERIFIED** | 2026-07-03 | 11/11 (spatial area added same day: bridge 4/4 in-engine — perceive, recognize across pose+scale, discriminate, refuse); discovery 8/8 with the accounting |
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

## World GM (generative worlds, oracle-only teaching — NEW 2026-07-03)

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| World GM v1: primitives programmed, laws emergent (never written as laws), information EARNED (observe/run/submit on a budget), GM grades beyond the observed range | `world_gm.py` | **VERIFIED** (instrument works) | 2026-07-03 | 6 s, 4 world types. Composed tertiary law `c ∝ a^(α·β)` recovered exactly in one draw (form-true, never programmed); NULL world correctly refused (accounting 0/0/100 = GM truth); gated world solved by a smooth surrogate that held beyond range (0.91); scope self-check loop works (Isaac spends budget on beyond-hull experiments, validate_law, re-learns with earned points — UNDERSTOOD honestly downgraded once) |
| **NEW ENGINE FINDING 1 (via GM): the form-true scope label is over-generous** | `world_gm.py` | **VERIFIED** | 2026-07-03 | the engine's edge check tests only the outer quartile of the OBSERVED cloud; 2 of 3 form-true labels failed the GM's external beyond-range audit (exchange −0.44, chain 0.596). This is the calibration audit (owner priority 4) operating: the label should say what was tested ("edges-hold"), or earn "form-true" via beyond-hull validation. Engine item queued. |
| **NEW ENGINE FINDING 2 (via GM): sum-of-many-singles laws lose to product impostors** | `world_gm.py` (exchange world) | **VERIFIED** | 2026-07-03 | the exchange world's emergent law is plain linear mixing (exactly representable, R²=1 achievable); the enumerator instead admits x_i·x_j and cos terms (on positively-correlated support a product out-correlates the single terms) and cannot recover the linear form even with earned far points. The discovery battery never caught this — no plain-sum case exists in it. Battery case + fix queued. |

## Spatial sandbox (curated in 2026-07-03 from the parallel session; `spatial/`)

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| Mechanism solver + variance-ledger perceiver: structure/joints/DOF from trajectories alone (incl. undeclared ground link; invisible-crank lengths to 0.0000; slop measured; TDC asymmetry predicted; materials from invariance signatures; design-from-curve; hidden pressure by breach; 3D joint taxonomy from clique overlap; ego-motion "I"; logic circuit from waveforms) | `spatial/test_*.py` (11 files) | **VERIFIED** | 2026-07-03 | 11/11 pass, all <2 s, pure python, zero deps — re-verified after curation from `Downloads/spatial-sandbox` (the lost-harness lesson, applied same-day) |
| **Null-gated edge vocabulary** (locked/bounded/sprung/free with NO hand-tuned thresholds): locked = variance-ratio vs the pair's own noise floor (estimated from first differences); bounded = repeatable extremes beating an increment-shuffle surrogate null | `spatial/engine.py` `classify_edges` | **VERIFIED** | 2026-07-03 | four-bar + noise: 4/4 true links LOCKED (incl. ground), 2/2 constrained pairs BOUNDED, zero extras |
| **The spatial E9** (false-positive battery): random walkers → zero locked/bounded; random waveforms → zero gates; independent walkers → zero false lag; planted rigid pair under noise → found, where the old rel_tol threshold finds NOTHING | `spatial/test_null_battery.py` | **VERIFIED** | 2026-07-03 | N1 28/28 free; N2 exactly (6,7) locked (std .0283 vs noise floor .0284; old gate: nothing); N3 0 gates; N4 0/15 false lags. The battery caught two real classifier defects during its own construction (noise-flicker visits; lucky walk revisits) — both fixed with hysteresis + the increment-shuffle null |

## The bridge + spatial GM (steps 4–5, 2026-07-03)

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| **THE BRIDGE: perception → Isaac's net.** Relations cross (locked/bounded edges, parts as pairwise-locked cliques, hinges, anchors, scale-free ratio signature); coordinates never do. Isaac answers structural queries from his fact index; **recognizes the same mechanism across 2.7× scale + 40° rotation + translation** (identical signatures); discriminates door vs four-bar; and the null gate holds AT the bridge (random walkers teach zero facts) | `spatial/test_isaac_bridge.py` | **VERIFIED** | 2026-07-03 | B1 19 relations taught, 4 bars incl. undeclared ground, 4 hinges, 2 anchors, all queries answered; B2 signatures (0.25, 0.75, 0.875, 1.0) identical across pose+scale → SAME; B3 door ≠ four-bar; B4 0 facts from noise. Building it caught 2 more perceiver defects (greedy clique growth missing sibling bars; bare anchor threshold dying to noise) — both fixed with edge-seeded cliques + the calibrated variance-ratio gate |
| **Spatial worlds for the World GM**: the sandbox's forward solver generates hidden mechanisms; the perceiver plays; the GM grades. Player never sees the world type — decides from what it perceives; probes are CHOSEN configurations (fold/extend by request, not luck) | `experiments/world_gm_spatial.py` | **VERIFIED** | 2026-07-03 | 3/3 in 0.2 s: S1 visible four-bar — all 4 lengths to ≤0.01%; S2 occluded — hidden crank 1.316 vs true 1.312 and coupler 7.632 vs 7.631 via 36 bought probe angles after the bounded null rightly refused weak 2-cycle evidence; S3 null — honest refusal |

## What spatial unlocked — benchmark reruns + the matrix-as-geometry translation (2026-07-03)

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| Digits-as-point-sets: pose-free pairwise-distance spectrum, NO registration step | `digits_spectrum.py` | **VERIFIED** | 2026-07-03 | random pos+size **55.0%** (raw 23.7 / registered 84.4); novel-bigger 46.5%; tiny 35.2%. Honest verdict: pure relational representation more than DOUBLES the raw baseline with zero pose handling, but is lossy (spectrum also confers unwanted rotation invariance — 6≈9); **registration remains the better road for digits**, now with the gap measured (~29 pts) |
| **Matrix → spatial structure → abstraction** (the sandbox WRITEUP's original pitch, closed): Isaac's fact matrix → dissimilarities → sprung-constraint embedding (the same projection loop) → the perceiver reads the geometry | `spatial/explore_concept_geometry.py` | **VERIFIED** | 2026-07-03 | 12 things taught as plain property facts, category labels NEVER taught → 3 clusters precipitate, **100% pure** (animals/fruits/tools); **level-2 abstraction emerges**: animal-group ↔ fruit-group closest (0.789 vs 0.97), matching the alive+grows overlap; null: **0/20 shuffled-property worlds even form 3 substantial clusters** (real crystal score 3.71 vs 0.00). Two nulls were sharpened during construction (single-gap statistic under-powered; ungated separation rewarded chance pairs) — the discipline caught both |

## Crystallizer battery + the owner's-laws amendment (2026-07-03 evening)

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| **The crystallizer, tested against planted ground truth for the first time** — the owner's two laws as the spec: positive negatives veto merges; partial overlap factors under a shared parent instead of collapsing | `crystallizer_battery.py` (before/after outputs in `runs/2026-07-03/`) | **VERIFIED** | 2026-07-03 | PRE-FIX: C1 clean categories PASS (the regime it always handled — the owner's experience confirmed); C2a abc/abd **FAIL** (collapsed); C2b penguin **FAIL** (merge erased `fly` from the type to absorb the penguin). POST-FIX (merge = near-identical members only + positive-negative veto; `teach_not()` added): **C1/C2a/C2b all PASS**, suite 11/11 unchanged |
| **The foundation fix: DIVERGENT doors self-assemble** — Net.door_counts (observation evidence) + consolidation Phase 1.5 (rest-of-intent carrier, ≥3 sightings, absence beats the like-your-siblings null at 1%) | `crystallizer_battery.py` C2c | **VERIFIED** | 2026-07-03 | penguin earns `not_fly` from experience alone (never taught) and the fresh negative vetoes the collapse in the same sleep; chick at 2 sightings earns nothing (ABSENT stays silent); suite 11/11 unchanged |
| **Wrong is kept and classified, with why** (owner's law: junk = a classification of error, not something to prevent or delete) | `crystallizer_battery.py` C3 | **VERIFIED** | 2026-07-03 | **249/249 chance types filed in the wrong section** with readable reasons ("coherence 8 within chance — best shuffled structure scores 12 — co-occurrence alone explains it"); C1 category types all classified SOUND vs the same null; downstream behavior deliberately unchanged (no pruning/importance-weighting — the owner's old trap) |
| **Supersession, not overwrite** ("if there is a and b, and b works better, use b" — and A is kept, wearing its defeat) | `crystallizer_battery.py` C6 | **VERIFIED** | 2026-07-03 | pendulum overturn: cosine in use; the defeated parabola preserved on the law's `superseded` list with why ("overturned by rival 'cosine' on new evidence: SSE 3.198 vs 1253") |
| Crystallizer scale knee, measured (untouched — no optimizing before limits, per owner) | `crystallizer_battery.py` C5 | **VERIFIED** (as measurement) | 2026-07-03 | **0.04 s @ 50 nodes, 2.9 s @ 200, ~420 s @ 800** — the knee is known and deliberately left alone until a real limit bites |

## THE CALIBRATION AUDIT (owner's priority 4, tier 5.2 — 2026-07-03)

| Claim | Script | Status | Verified | Observed |
|---|---|---|---|---|
| **The ONE trust number: when Isaac claims form-true, it holds beyond his data 68% of the time** (36/53 over a 100-world externally-graded deck) | `calibration_audit.py` (10 s, seeds fixed) | **VERIFIED** | 2026-07-03 | Full instrument panel: **UNDERSTOOD-inside 54/54 = 100%** (within his data, a claimed law always held); **noise false discoveries 0/15** (refusal fully trustworthy); accounting calibration **median error 0.2 pts / mean 2.4** vs GM truth (1 outlier at 76); out-of-class overclaims 2/15; **linear-sum pathology 0/15 fooled on symmetric support** — refines the GM finding: the product-impostor trap is POSITIVE-support-specific (the exchange world's regime), not universal |
| The scope label is the miscalibrated part: "range-valid" was used 1/54 times; "form-true" is the default and is only 68% reliable | `calibration_audit.py` | **VERIFIED** | 2026-07-03 | the internal edge check (outer quartile of observed data) is too easy to pass — 1 in 3 form-true labels fails real extrapolation. Fix candidates (owner to choose): rename to "edges-hold"; earn "form-true" via beyond-hull probes (the GM-style scope self-check, now proven in world_gm.py); or attach the measured 68% reliability to the label itself |

| **Extrapolated confidence (owner's design): the binary scope stamp becomes graded, measured belief** — `law_confidence(name, X)` = boundary confidence inside the hull × the measured survival curve beyond it | `confidence_curve.py` (fit on 60 worlds, validated on 60 FRESH) | **VERIFIED** | 2026-07-03 | measured decay: 76% at boundary → 59% (+0.1 spans) → 45% (+0.3) → 43% (+0.6) → 37% (+1.0); out-of-sample reliability: predicted 0.22→actual 34%, 0.40→48%, 0.60→60%; **ECE 0.070; Brier 0.249 vs flat-68% baseline 0.288 (better)**; in-engine with provenance (`DECAY_MEASURED`), self-test (h): inside 0.88 > near 0.57 > far 0.38; suite 11/11, discovery 9/9 |

| **THE CORRECTION LOOP (owner's design): confidence as a steering signal — probe the weakest region, re-derive, accept only better-or-tied-and-simpler, supersede with why, Occam-prune** | `refinement_audit.py` + `isaac.refine()` | **VERIFIED** | 2026-07-03 | 100-world deck, 60 experiments/law: **beyond-range hold 50% → 75% (+25 pts)**; Occam held complexity flat (2.8 → 2.8 mean terms) while accuracy rose; 90 refinements accepted through the gate, **47 terms pruned at F-ties** (simpler won); known trade: inside-range 99% → 94%; instrument failures (non-finite probes) handled; 36 s total; suite 11/11 |

| **Audit 2.8 CLOSED (flat level): capture nets + the distillation attack + graduation** — the stopgap that exists to be destroyed | `capture_graduation.py` + `isaac.capture_net/graduate` | **VERIFIED** | 2026-07-04 | G1: planted x0·x1−x2 captured by the null-gated tiny net (0.984 vs null −0.13) → distilled → pruned against reality → **`+1.00*x0*x1 −1.00*x2` exact, R² 1.000 vs truth**; G2: out-of-class sin(3·x0·x1) captured, honestly STILL CAPTURED after distillation; G3: noise net FAILED its null, nothing stored (the lie-killer); the razor at graduation runs against the ORIGINAL data so net-warp terms die while truth terms survive |
| **Data-adequacy diagnosis** in every discover(): too-weak data gets a cause, not a shrug | `capture_graduation.py` G4 | **VERIFIED** | 2026-07-04 | hidden driver → "driver may not be among these columns (shadow)"; nested → "expressive-class limit, not weak data"; n=40 → "interpretable (provisional: small sample)"; suite 11/11 |

| **Interrogation: the captured made explicit** — drivers, joint action, composite dependence (level-set invariance vs matched random-direction null), shape+frequency, all in gated English; then `graduate_composite` re-discovers in the coordinate Isaac identified | `interrogation_battery.py` | **VERIFIED** | 2026-07-04 | I1 the stuck case UNSTUCK: sin(3·x0·x1) capture → "lives in x0,x1 (50/50), acts JOINTLY (97%), flows through the PRODUCT only (0.87 vs null 0.37), periodic ~2.5 rad/unit" → **graduated to `+1.00*sin(3*(x1*x0))` exact**; I2 additive control invented NO structure; I3 (x0+x1)² → sum found, graduated exact; 1.2 s; suite 11/11 |

| **Combinations are first-class, memorized, REUSED** — comb:<name> nodes minted by interrogation, ledger-inherited, auto-offered to every discover() | `composite_reuse_battery.py` | **VERIFIED** | 2026-07-04 | R0 control: sin(3·x0·x1)+0.5·x2 cold = PARTIAL 0.80 (unsayable); R1: after learning (x0*x1) on a DIFFERENT problem → **UNDERSTOOD `+1.00*sin(3*(x0*x1)) +0.50*x2` exact**, applies to fresh raw data at 0.999; R2: a fresh Isaac inherits the combination through the ledger and solves it cold; R3: (x0*x1), (x0+x1), (x1*x2) are three distinct nodes with provenance; full regression green (suite 11/11, all batteries, refinement +24) |

## Known-stale numbers — do NOT quote

- "0/40 false discoveries across two batteries" → the verifiable number is 0/20 (discovery battery E9) plus a clean red team and zero wave noise admissions.
- Covtype "79.1% row-index control" → superseded by the sharp control: **94.8%** (see row above). Quoting 94–95% covtype exemplar accuracy without the leakage row next to it is dishonest — the articulated tier (56–59%) is the achievement.
- Registration "86.5%" novel-bigger → the rebuilt harness observes 85.4%; quote the observed number.
- "Self-test 5/5, 6/6, 7/7, 9/9, 10/10" in older docs → the suite is 11/11 (spatial joined 2026-07-03).
- Engine "~2,900 lines" → ~3,500 (accounting added 07-03).
