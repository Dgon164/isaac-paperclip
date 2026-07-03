# Verdict Sheet — filled 2026-07-01, refreshed 2026-07-03

Against `AUDIT_STANDARD_v1.md`. Strict: WORKS / BROKEN / NEVER BUILT, with the
evidence number. "In engine" = wired into `isaac.py` (repo root) and covered by
its self-test (10/10); "harness" = validated in `experiments/` scripts only.
The 07-03 refresh adds a line-by-line code audit of the engine (line numbers
below refer to `isaac.py` as of this date) and a full re-run of the in-repo
harness (`experiments/RESULTS_LEDGER.md` has every observed number).

| # | Capability | Code path | Test | Verdict | Evidence |
|---|------------|-----------|------|---------|----------|
| 2.2 | Doors / dims / ranges | `isaac.py` fit_lens + crystallize_features (proximity doors); `experiments/doors_proximity.py` | rebuild A 4/4 + engine smoke | **WORKS** (in engine) | re-verified 07-03: diagonal 99.0% vs box 88.0%; re-encoding invariance 100% vs 82.2% |
| 2.1 | Atom (3-verdict SAME/DIVERGENT/ABSENT) | `compare()` gives shared/only-a/only-b; no principled ABSENT-vs-decompose | none | **NEVER BUILT** (as specified) | depth-aware comparability test does not exist |
| 2.10 | Permuted-null infra | enumerator admission (:429–439, selection-corrected — the best null in the file); wave jitter nulls (:244–303) | batteries, re-run 07-03 | **WORKS at the core gates; BROKEN at three edges** | (1) capture null MIS-TARGETED: score is max over d+1 neighbor sets (:1388) but null permutes only the winner (:1390) — anti-conservative; (2) NO block permutation — iid null invalid on autocorrelated targets, only the max_terms=16 brake (:408–416); (3) good nulls post-processed by bare constants (1.4× :265, 1.5×+2.0 :303, F<10 no dof :494/:1343) |
| 2.10b | Null discipline in the static crystallizer | `_crystallize` | none | **NEVER BUILT** | min_shared=2 (:832), 0.8 overlaps (:863,:890,:909), single negative observation = permanent lockout (:935) — zero statistical tests in the organ everything stands on |
| 2.4 | Crystallizer / FCA lattice | `_crystallize` (types, FCA-ish closure); wave groups = connected components, NOT a lattice | test_language etc. | **BROKEN** (partial) | overlap cannot be represented (shared doors merge groups); no concept lattice; scaling confirmed O(n³–n⁴): pair loop (:819) × closure scan (:835) × get_predecessors full-dict scan (:58) |
| 2.5 | Null detection (level-indexed) | discover() NO RULE verdict; wave nulls | E9, re-run 07-03 | **WORKS** (flat), level-indexing NEVER BUILT | 0/20 false discoveries on pure noise (E9, re-verified); no "null at surface, lawful at whole level" machinery |
| 2.3 | Holarchy / composition (uptake) | `experiments/composition_uptake.py` ONLY | rebuild B 7/7, re-run 07-03 | **WORKS (harness)** — NOT in engine | dismantled-engine control passes; engine crystals still membership-only (:843–846, :873–877); wave_next handoff edges (:1498) are the sole arrangement info, group-level temporal only |
| 2.11 | Classification flat+compound | flat: proximity doors (in engine); compound: `experiments/covtype_compounds.py` (harness) | covtype/HIGGS, re-run 07-03 | flat **WORKS**; compound **WORKS (harness, one round)** — NOT in engine; ceiling→trigger NOT wired | covtype flat 56.15% re-verified to the decimal; compounds 56.2→59.0 null-gated (pair 3-6 admitted zero — the gate declining junk); HIGGS 64.6%/AUC 0.700; captured road 90.0% re-runnable; the 94.4% door-weighted variant was never committed (RECORDED only) |
| 2.7 | Keypoints (drop-one causal) | `_fisher` (:206–214) still live in `fit_lens(select=...)` (:2066) — the FORBIDDEN statistic | none | **NEVER BUILT** (and Fisher still present in a selection path) | audit says Fisher MUST NOT rank; it remains the supervised dim-select path |
| 2.8 | Completeness (3-valued % accounting) | discover() verdicts only | test_discovery 7/7 | **NEVER BUILT** (as specified) — the #1 priority gap | verdicts are a mutually exclusive elif chain (:1261–1268), not additive fractions; law%+captured%+noise%=100 never computed; residual dropped, no dossier, no level rule, no mini-net to distill; BUG: strong-partial-law + strong-capture → CAPTURED and the real equation is DISCARDED (:1272). All ingredients (held-out R², edge R², cap R²+null) already computed — the accounting is a synthesis step away |
| 2.6 | Function recovery | `discover()`/`_Enumerator` in engine | batteries + red team, re-run 07-03 | **WORKS** (see battery limits) | exact forms incl. off-grid damped oscillation re-verified; red team 0 kills 0 crashes; identifiability clause WORKS for declaration (rival_check inside discover :1270, probes incl. beyond-range :611–633, test_rivalry in the 10/10) — single-feature terms only (:588), resolution manual via confirm() |
| 2.6b | apply_law / ledger re-validation | `apply_law` (:1300), `load_ledger` (:1194), `confirm` (:1314) | none | **BROKEN** (applied blind) | apply_law checks shape only; load_ledger rehydrates laws with no confirm step; confirm() with an empty rivals list returns CONFIRMED without any absolute-fit check (:1360) |
| 2.9 | Shadow census | equation_discovery scripts only | HIGGS m_jj diagnostic | **PARTIAL (harness)** | m_jj wall proven a data wall (true form R² 0.065 across all pairings) — verdict #4 demonstrated once, not a general engine capability |
| 2.13 | Scaling curves | batteries log CSV per run | wave + discovery batteries, re-run 07-03 | **PARTIAL** | onset/saturation measured for waves + doors bins (CSVs byte-identical across re-runs — deterministic); condensation scaling measured; not yet for every capability |

## Carried suspects — status (07-03)

- Membership-only composition: CONFIRMED as designed-in flaw; fixed in harness (B), **engine migration still pending**.
- Representation-variance of doors: CONFIRMED and measured (box 17.8% verdict flips); fixed by proximity doors; re-verified 07-03.
- Fisher-ratio in ranking paths: **still present** as `fit_lens(select=...)` (:2066) — replace with drop-one relevance (2.7).
- Compound doors: built in harness (one round, covtype); **not in engine; ceiling→trigger not wired** — still the highest-leverage missing piece toward the articulated tier.
- O(n²) crystallizer: **confirmed worse** (O(n³–n⁴) with the get_predecessors full scan); unaddressed.
- NEW (07-03): capture null mis-target (:1388 vs :1390); CAPTURED-discards-law bug (:1272); `_capture` O(n²·d) broadcast unconditional in every discover() (:1373); apply_law/load_ledger blind application; no block-permutation null (the sunspot runaway condition still reproducible up to the brake).
- NEW (07-03): two headline numbers trace to harness variants that were never committed — registration 84–87% (16×16 canvas; committed 8×8 script shows 21–53% from edge clipping) and covtype 94.4% (door-weighted k=1 over 406k exemplars). Both are RECORDED, not re-runnable, until the variants are rebuilt and committed. The re-runnable neighbors: registration mechanism demonstrated at 8×8; covtype captured road 90.0%.
