# STRUCTURAL DEBT CHECKLIST — every known limitation, stopgap, and gap
**Compiled 2026-07-04** from: `VERDICT_SHEET.md` (audit numbers), `ISAAC_MANUAL.md`
(per-section limits), `SESSION_HANDOFF_2026-07-04.md` (standing TODO), the
07-03 line-by-line code audit, and the code's own markers. One list, checkable,
with evidence. Settle order-of-attack disputes by battery, not argument.

**The governing law (owner's):** *no optimizing before measured limits.* Section E
is the only list that licenses optimization; everything else is correctness,
honesty, or capability debt.

---

## A. Null discipline debt — the epistemics' own gaps (fix FIRST; doors-first order)

- [ ] **A1. Block-permutation null** — iid permutation is INVALID on
      autocorrelated targets; only the `max_terms=16` emergency brake stands
      between discover() and the sunspot runaway (still reproducible up to the
      brake). The OLDEST methods debt. (2.10; handoff #2; also the MVP's
      autocorr guard.)
- [ ] **A2. Crystallizer admission null** — NEVER BUILT at type *formation*:
      `min_shared=2`, three 0.8 fixed overlaps, zero statistical tests in the
      organ everything stands on. The 07-03 wrong-section files chance types
      AFTER formation (C3: 249/249 classified with whys), but formation itself
      is ungated. (2.10b; battery C3.)
- [ ] **A3. Bare constants riding good nulls** — 1.4× anti-bridge margin,
      1.5×+2.0 in waves, F<10 with no dof accounting. Tests-over-thresholds
      (law 2) not yet applied to the nulls' own post-processing. (2.10.)
- [ ] **A4. Single negative observation = permanent lockout** (`:935` region) —
      one bad frame vetoes forever; no evidence-weighing. (2.10b.)
- [ ] **A5. `infer()` first-supporting-sibling wins** — adds a door as a side
      effect with no vote and no null. (Manual §4.)
- [ ] **A6. Sense candidate LINKING is fixed-count** — admission is null-gated
      (2026-07-04) but the `min_shared=2` linking rule that FORMS candidates is
      still a threshold. (Manual §3.)
- [ ] **A7. `crystallize_senses` is batch, not incremental** — must re-run (and
      supersede) after new observations; no dirty-scoped sense update.

## B. Stopgaps by design — exist to be destroyed (each has a named successor)

- [ ] **B1. `capture_net` tiny tanh net** — quarantined, null-gated, never the
      deliverable; graduation/interrogation built 07-04 and works, but the
      stopgap remains the only holder of out-of-class structure. Successor:
      richer expressive class + level-indexed accounting (D1). (2.8.)
- [ ] **B2. `max_terms=16` brake** — dies the day A1 lands.
- [ ] **B3. Fisher ratio still live** in `fit_lens(select=...)` — the audit's
      FORBIDDEN statistic for causal ranking; deprecated but present.
      Successor: drop-one keypoint relevance (D6 / audit 2.7). (2.7.)
- [ ] **B4. Legacy box meta** written by `crystallize_features` for
      `recognize_matrix`/old scripts — proximity doors are authoritative.
- [ ] **B5. Legacy `meta["senses"]` mirror** (pre-07-04 readers) — the sense
      doors are authoritative; mirror removable once nothing reads it.

## C. Harness-proven, NOT in engine (migration debt — the capability exists, the mind can't use it)

- [ ] **C1. Uptake / holarchy composition** (rebuild B, 7/7) — engine crystals
      are still membership-only; wave handoff edges are the sole arrangement
      info. THE structural gap the 07-03 crystallizer work re-confirmed
      (static crystallizer shallow, 2.3/2.4 want the same fix). (2.3.)
- [ ] **C2. Compound doors + ceiling→trigger** — covtype 56.2→59.0 null-gated
      in harness, one round; not wired into the crystal pipeline; the trigger
      (additive ceiling → try compounds) not built. Flagged highest-leverage
      toward the articulated tier. (2.11.)
- [ ] **C3. Registration front-end** (pose/identity factoring; 23.7%→84.4%
      digits under position+scale, novel-bigger 85.4%) — harness only.
      Wire-in target named at curriculum post-mortem. (Manual §5.)
- [ ] **C4. Ideals + differentia** (genus/species, minimal-overlap key
      identifiers, honest genus-level ties) — harness only. (Manual §5.)
- [ ] **C5. Cross-domain log-track + analogy priming** (cold 0.82 → primed
      0.995) — harness only; log-track inside discover() queued. (Manual §7.)
- [ ] **C6. Sprung classification** — in `spatial/engine.py`, not in-engine.
      (Manual §5b.)
- [ ] **C7. Shadow census as a general capability** — demonstrated once (HIGGS
      m_jj data-wall verdict), not an engine organ. (2.9.)

## D. Never built (so nobody assumes it)

- [ ] **D1. Level-indexed accounting** — residual at level N handed to level
      N+1 ("null at surface, lawful at whole level"); flat level closed 07-04,
      the level rule itself never built. (2.5, 2.8.)
- [ ] **D2. Depth-aware atom** — principled ABSENT-vs-decompose comparability
      test (the 3-verdict atom as specified in the audit). (2.1.)
- [ ] **D3. Abstention in `classify_features`** — it always answers; shrug +
      genus-level fallback queued. (Manual §5.)
- [ ] **D4. FCA lattice / overlap merging** in the crystallizer. (Manual §12.)
- [ ] **D5. Shrug→discover reflex + curiosity** — challenges arrive from
      outside; the probe queue is proposals only. (Manual §12.)
- [ ] **D6. Keypoints / drop-one causal relevance** (retires B3). (2.7.)
- [ ] **D7. Symbolic/token challenges in discover()** — the discovery stack is
      numeric-only. (Manual §12.)
- [ ] **D8. Learned-invariant perception (phase 4)** + **the pixel bridge**
      (render → tracker → observe_spatial) — the perception keystone; the
      22.9% clock readout is a known harness bug awaiting this. (Manual §12;
      handoff #4.)
- [ ] **D9. Effect entities (the shadow pipeline)** — expect → subtract →
      perceive-the-delta; signed; owner's design, NEXT #1 in the handoff.
- [ ] **D10. Scaling curves for every capability** — measured for waves/doors/
      condensation only. (2.13.)
- [ ] **D11. Interior-preservation gate in refine()** — known trade: inside-
      range hold eased 99%→94% when the refit weighs the new frontier.
- [ ] **D12. λ-continuous refine across 0** (power-dial polish).

## E. MEASURED limits — the only licensed optimization targets (owner's law)

- [ ] **E1. Crystallizer knee** — 0.04 s @ 50 nodes, 2.9 s @ 200, ~420 s @ 800;
      audit says O(n³–n⁴) in practice because of E3. Licensed to fix ONLY when
      a real workload bites (owner's explicit gate). (C5; 2.4.)
- [ ] **E2. `_capture` O(n²·d) broadcast** — unconditional, now up to TWICE per
      discover() (accounting adds a residual capture). Audit-flagged 07-03;
      optimization queued. (Carried suspects.)
- [ ] **E3. `Net.get_predecessors` is a full scan** — no reverse index; the
      structural root under E1 and several walkers. The single highest-value
      *structural* optimization in the file — and it's a data-structure fix,
      not a speed hack.
- [ ] **E4. `observe_spatial` all-pairs O(n²) per frame set.** (Manual §5b.)
- [ ] **E5. Wave envelope** (measured, not bugs): period ≥ 9 ticks,
      instantaneous handoffs, ≲4 concurrent aperiodic waves, fire rate ≥ 0.7,
      T ≥ ~1000. (Manual §3.)
- [ ] **E6. Discovery reach** (measured): wrong-form risk n<~400 (provisional
      rule exists); frequency reach ≈ 2× grid max; nested nonlinearities →
      CAPTURED by design; rational functions admit trig surrogates
      (range-valid). (Manual §7.)

## F. Protocol / hygiene debt

- [ ] **F1. Gauntlet re-run with the current stack** (standing since 07-03).
- [ ] **F2. Scoreboard numbers are RECORDED-not-reverified** (need datasets +
      long runs; manual §11 tags them honestly).
- [ ] **F3. `isaac_project/TODO.md` is stale** (says 10/10, engine at `code/`).
- [ ] **F4. Sense/wave/crystallizer batteries not in the 11-area self-test**
      (by design — suite = smoke; batteries = proof; keep the distinction
      but document it wherever a number is quoted).
- [ ] **F5. Covtype honest number discipline** — quote articulated 56–59%;
      the captured tier barely beats its own 94.8% row-index leakage null.

---

# THE FRESH SINGLE-FILE REBUILD — evaluation (asked 2026-07-04)

**Framing correction:** the engine already IS one file — `isaac.py`, 4,856
lines, 175 defs, one class + Net + module atoms, numpy only. So "full fresh
optimized build" = **rewrite from spec instead of accretion**, same form factor.

## What makes it FEASIBLE today (this didn't exist a month ago)
1. **The spec exists**: `ISAAC_MANUAL.md` (every capability, honestly scoped) +
   `ISAAC_THEORY_OF_OPERATION.md` + `AUDIT_STANDARD_v1.md`.
2. **The acceptance suite exists**: 11-area self-test + the batteries
   (crystallizer, wave, discovery, red-team, sense, capture/graduation,
   composite-reuse, collective, refinement, spatial 13/13, calibration
   100-world) + `RESULTS_LEDGER.md` (claim → script → observed). **The
   batteries ARE the rebuild contract** — a rebuild is DONE when every battery
   is green against the new file and A/B matches the frozen baseline.
3. **Measured curves are data, not code**: DECAY_MEASURED, the wave envelope,
   trust numbers — they transfer as constants but MUST be re-measured on the
   new enumerator (the 07-04 rule: recalibrate after any enumerator change).

## What it would cost (realistic, in focused sessions)
| Phase | Content | Sessions |
|---|---|---|
| 0 | Freeze the contract: baseline oracle pinned (current engine), every battery + ledger row enumerated as gates | 1 |
| 1 | Substrate: Net **with reverse index** (kills E3 by design), door counts, meta, persistence, atoms | 1–2 |
| 2 | Consolidation organs: crystallizer with **admission null native** (A2), senses, waves, statuses | 2–3 |
| 3 | Discovery stack: enumerator with **block-perm null native** (A1, retires B2), accounting, confidence, refine, capture/interrogate/graduate, composites | 2–3 |
| 4 | Perception: lens (no Fisher — D6 native, retires B3), proximity doors **with abstention** (D3), spatial; fold in harness-only C1–C4 | 2–3 |
| 5 | Re-measure everything: calibration audit, decay curve, gauntlet, envelope | 1–2 |
| | **Total** | **~9–14** |

## The honest risk register
- **The file encodes hard-won corrections** that look like noise to a fresh
  writer: the capture-null retarget, the CAPTURED-erases-law fix, signed
  deltas, the confirm() REFUTED guard, hash-determinism fixes, the
  selection-corrected nulls. Every one was a bug that BIT. Battery coverage
  protects exactly the ones that have batteries — and 2.13 says coverage is
  partial. A rewrite re-exposes the uncovered ones.
- **The owner's law cuts against it**: *no optimizing before measured limits.*
  The measured limits are E1–E3 — and E1 is explicitly gated on "when a real
  workload bites." Nothing else in the file has a measured limit that a
  rewrite would fix. A fresh build motivated by "optimized" is the old trap
  wearing new clothes; a fresh build motivated by **A-section nulls designed
  in rather than patched in** is defensible.
- **Accretion is partly a feature**: wrong-kept, supersession, the dated
  build ledger — the history IS the wisdom record. Git preserves it either
  way, but the working file stops being the archaeology.

## Recommendation (settle by battery if disputed)
**Not a big-bang rewrite. A ship-of-Theseus rebuild inside the same file**,
organ by organ, in dependency order (doors first — the audit's own order),
each swap gated by its battery plus A/B against the frozen baseline:
1. **E3 reverse-index Net** (structural, measured, enables everything below);
2. **A1 block-perm null** (retires B2; unblocks the MVP autocorr guard);
3. **A2 crystallizer admission null** (the organ everything stands on);
4. **C1 uptake + C2 compound doors into the engine** (the two the audits
   keep converging on);
then re-measure (phase 5) and REASSESS whether anything still wants a fresh
file. Prediction recorded here so it can be graded: after those four, the
fresh-build motivation largely evaporates — what remains is capability debt
(D-section), which a rewrite doesn't buy.

*Maintenance: check items off with the battery/evidence that closed them;
this file joins the manual's same-step update rule for anything it lists.*
