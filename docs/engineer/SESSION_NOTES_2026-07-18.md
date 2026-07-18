# SESSION NOTES — 2026-07-18 — ENGINEER LANE, GOAL RECOVERY, FIDELITY, LEDGER ETHICS
*Handoff for the dev. Design conversation, no code written. Four companion docs in this bundle; build items at the bottom. Conventions as usual: predictions filed before first run, every rung has a null that must refuse, receipts everywhere.*

---

## 1. Decisions made today (Turtle's, unless marked)

**D1 — Engineer lane committed.** Regardless of other outcomes, Isaac's next capability arc is engineering. Order: **software → mechanical → electrical**. Full rung checklist in `engineer-lane-checklist.md` (segments E0–E3). E0 (kinds, multi-view identity, slot signatures, dependency propagation) gates everything and is the first build.

**D2 — Structural kinds via CAD semantics.** Data structures as "3D CAD models of information": parts as parametric *recipes* (store the construction history, derive properties on demand). Tube = hollow cylinder = extrusion(ID) = extrusion(OD) = wall/schedule — multiple views, one identity. Consistency court = constraint arithmetic (OD = ID + 2·wall): two given → third derived; three consistent → corroboration receipt; three inconsistent → refusal with residual named; one given → named DOF, never a guess.

**D3 — Dependency propagation (the TMS rung).** Dependencies are typed **fixed** (.002") or **relative** (.5%). Change one value → propagate → re-verify all → divergence flagged with size/direction. Unlike CAD, anchoring comes from *vocabulary* (a piston's kind knows it depends on a bore), not per-model authorship. Tolerance stack-up = walking dependency chains with receipts.

**D4 — Multi-representation principle.** A concept's exact decomposition doesn't matter as long as all decompositions are consistent. Keep one or all; no canonical form; select the simplest view adequate to the need, escalate by viewpoint (LOD for meaning). Cross-view disagreement = wound → conflict machinery. Views are cheap: compositions over shared atoms, not copies.

**D5 — Slot signatures.** Every operation/part declares inputs, outputs, AND residue as official slots (division = two-in two-out: quotient + remainder). Court: presence, type, balance. Convergent ancestors: arity, valence, valency, interface contracts. Residue slot is mandatory — an operation without one is an accounting error.

**D6 — Implied-goal recovery rung (code lane).** Decompose simple games (Tetris, Snake, Mario, Duck Hunt) and recover the dos/don'ts/**indifferents** from mechanism: find monotone celebrated counters (reward), absorbing states (punishment), resources (buffers). Distinguish **forbidden** (transition doesn't exist — lockout) from **punished** (allowed, costed — valence). Key null: **mod the game** (invert one reward line) — the recovered goal sheet must report the inverted valence from code, not the culturally-remembered one. Second null (superstition): a planted indifferent variable must be filed FREE — the recovered policy must not develop rituals. Cheap construction proof: policy from recovered rules must beat random survival by a wide margin.

**D7 — Rule taxonomy.** Hard rules (walls, mechanically enforced) / soft rules (lives, time, coins — valenced) / free rules (location in play area — indifferent). The free channel is the *interior* — most of the space, and what you get to not compute. Then the 2×2: hard/soft × failure/success — **hard is binary (topology/reachability), soft is gradient (metric)**. Gradients and binaries interconvert at thresholds; **margin = distance-to-wall in the soft currency** is the central engineering quantity. Lives = hard fail with a recovery condition. Deepest cut: truly hard = **irreversible**.

**D8 — Redundancy layer.** Redundancy converts hard fails to soft by installing lives (NASA Crit 1 / 1R / 2). Two courts: (a) **R is state, not type** — a 1R item with a failed channel IS a 1 right now (track current lives, MEL-style); (b) **independence required** — lives count only after proving no common cause (two O-rings sharing one frozen joint = one O-ring). Same independence test as source corroboration.

**D9 — C-cost / court-depth rule.** Deliberation/verification is itself an action with soft cost. **Court depth is set by wall hardness, never by available time.** Schedule pressure on a Crit-1 court returns a named refusal ("insufficient consideration for the criticality class").

**D10 — Fix-menu structure.** A negative margin implies four repair families: move the operating point / move the wall / add lives / restrict the envelope. Menu sorts by **verification lead time**; envelope restriction deploys immediately (court already passed), engineering fixes carry their own rung ladder whose duration IS the pend (8D shape: interim containment now, verified permanent fix later). Fixes enter the same ledger they repair (a heater has its own criticality lines; sensor + commit rule convert it from hope to receipt).

**D11 — Net-extraction fidelity DEFINED.** Understanding = signal accounting: of the throughput entering, what fraction is accounted on the other side vs the unidentified remainder. Per-neuron procedure: identify atomic contributors + structures; success = accounting for the full input matrix, one neuron at a time (arithmetic identity — reconstruct W, residual = unaccounted). Distinctions: (a) only the *consumed* (output-channel) throughput counts, not waste; (b) residual court = the reservoir surprise probe (screams → structure remains; quiet past null → proven noise); (c) operational test = **progressive replacement** (splice extraction into the net layer-by-layer, measure damage); (d) behavioral coverage is open-world (the 2+2 rule — report by input-frequency band), structural accounting is closed-world (the artifact is finite). Meaningful % = **condensed-vs-parked**, since accounting hits 100% by construction under keep-everything.

**D12 — Big-model road (600GB-class).** Weight-reading streams per-layer (mmap sharded safetensors; peak RAM = largest tensor; single workstation viable). Activation capture streams too (layer-at-a-time offload over a probe batch; ~1 disk sweep per batch). Real blocker is internal: the crystallizer O(n²+) knee (~800 nodes) — the tiered working-set design must land first. Ladder before mountain: GPT-2 (with fidelity harness) → Pythia suite → 8B → 70B → 600GB. MoE models likely *friendlier* (experts = separable modules).

**D13 — Persistence-ethic heuristic (parked as research, explicitly NOT "alignment solved").** Value kernel: cost of letting exist << cost of destroying; idealized goal = persistence of complex things. Conflict court = **replacement cost**: walk the construction tree (steps, materials, precision, prerequisite tooling, knowledge), denominated in the situation's binding constraint ("effective firewood"); redundancy is LOCAL; design intent counts (consumables are pre-priced for destruction); downstream information effects on the ledger at stated resolution; no sacred categories — "last copy" is a large number, not a wall; irreplaceables (persons; culture as the culmination of persons) top the ledger by derivation, not assertion. Agent files its own complexity below its principals. Fast pass = cached categories; deep traversal on stakes/anomaly. Test bench = the game rung (planted vase battery; planted conflict battery; equal-simplicity null). Turtle's final calibration: "if it's not solving alignment, it's a pretty good heuristic."

**D14 — Challenger retrospective (queued, whitedoc-grade candidate).** All-public-data case study: seal-race lawform (t_recover(T) vs t_gap), full-flights correlation (the selection-bias refusal), envelope refusal (31°F vs 53°F floor), 1R→1 supersession propagation. Punchline: prevention required an epistemology, not a supercomputer. Turtle independently rederived NASA's actual fix (joint heaters + envelope criteria + capture feature) from the margin analysis.

---

## 2. Build queue for the dev (suggested order)

1. **E0.1–E0.4** — the four foundation courts (kinds/tube, multi-view, slots, TMS propagation). Tube battery T1–T4 as specced in the checklist. Mostly arithmetic; first green wall of the lane.
2. **C1–C2** — code read→map + the containment court with three verdicts. Toy corpus with planted uncontained edges.
3. **G-rung (D6)** — game goal recovery with the modded-game null and the superstition null. Open-source Snake/Tetris implementations as corpus.
4. **Fidelity harness (D11)** — frozen probe sets; behavior-agreement (per-band); reservoir residual court; progressive-replacement protocol. First target: GPT-2, so the 2,300-node claim gets a measured percentage.
5. **Tiered crystallizer** (pre-existing spec) — gates the big-model road (D12).
6. Parked: Challenger retrospective (D14), collider initial-state forensics, persistence-ethic batteries (D13), legacy-remediation lane (see commercialization review §product lanes).

## 3. Companion docs in this bundle

- `engineer-lane-checklist.md` — segments E0–E3, rung by rung, with nulls and gates.
- `isaac-information-structure-overview.md` — full-stack methodology overview (rev. 07-18: shapes-and-labels ontology, multi-representation, slot signatures added). Status labels: [validated]/[claimed]/[theoretical].
- `learning-by-decomposition-draft.md` — the cycle as a notes-draft paper (NOT committed to any publication structure).
- `isaac-commercialization-review.md` — billing/pricing/confidentiality architecture + research agenda (from the earlier session; included for completeness).

*— compiled by Claude from the 07-17/07-18 sessions, for Turtle's dev handoff.*
