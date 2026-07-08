# The Tower — why Isaac's hierarchy recovery collapses above L1
*Analysis v1, 2026-07-07. Analyze → understand → document → (then) experiment → refine.
This document is the first three steps. No solution is prescribed yet; the experiment
plan below carries registered predictions, per the Comparison Tower's falsification discipline.*

Companion artifacts (currently loose, to be linked into this folder): the Foundry v2
world/observation generator (`foundry_v2.jsx`), the Crystallizer v1–v4 browser resolvers
(`crystallizer_v4.jsx`), the Comparison Tower v2 theory doc (`the_comparison_tower_v2.md`),
and Isaac's own `isaac.py::_crystallize`.

---

## 1. The measured failure signature

Isaac, run blind on a Foundry tower world, recovered:

| floor | recovered | rate | notes |
|---|---|---|---|
| L1 (base groups) | 60 / 60 | **100%** | perfect |
| L2 | 16 / 160 | **~10%** | |
| L3 | 4 / 420 | **~1%** | |
| L4+ | 0 / ~5000 | **0%** | dark |

Two readings, both informative:
- **Recovery RATE falls ~10× per floor** (100% → 10% → 1% → 0%). A clean geometric collapse.
- **Absolute recovered COUNT falls ~4× per floor** (60 → 16 → 4 → 0), close to the world's
  mean group span (~4). Suggestive, not yet load-bearing — see experiment E-COUNT.

The regularity matters: a smooth exponential decay is the fingerprint of a **single
compounding mechanism**, not a pile of unrelated bugs. It is NOT a cliff (which would
implicate one threshold) and NOT the "landfill" over-claiming disease (which would show
many low-precision claims, not near-zero recall). It is a **silent geometric fade**.

---

## 2. The central mechanism: observation and recovery run in OPPOSITE directions

The Foundry generates a view **top-down** (`viewDropout`): pick 1–2 **top-layer** groups,
expand downward, keep each child edge with probability `detect`. So:

- **Every observation is a top-group sample**, attenuated to ≈ `detect^depth` by the time it
  reaches atoms (0.55⁴ ≈ **9%** at the reference world). Intermediate wholes are never
  observed as wholes — only as partial atom-bags inside a top-group sample. This is the
  doc's law *"hierarchy is written in the dropout"* stated generatively.

Isaac (and the Crystallizer, and every resolver so far) recovers **bottom-up**: atoms → L1 →
L2 → …, mining floor L from the recovered tokens of floor L-1.

**These directions are opposed, and that is the paradox in the curve.** The top layer seeds
*every* view yet is recovered *worst* (0/5000). The information about top groups is present
in literally every observation — but it is only legible top-down, and a bottom-up climber
reaches it last, standing on the most-corrupted substrate. We are reading the book
back-to-front.

---

## 3. Why the decay is geometric: three losses multiply per floor

Each step up the tower multiplies recoverability by a roughly constant factor < 1. Three
independent losses stack:

1. **Evidence attenuation (channel).** A floor-L group's co-occurrence signal passes through
   one more dropout gate than floor L-1, so it is ~`detect`× weaker each floor. Deep groups
   are seen through more fog. (Foundry: the recursive `if (rand() < detect)` per edge.)
2. **Substrate impurity compounding (the load-bearing one).** Floor L is mined from floor
   L-1's *recovered* tokens — which are incomplete (only that floor's recall was found) and
   impure. You cannot compose a group from constituents you never cleanly recovered. The
   doc's *"bottom-floor precision is the entire game"*, quantified: L3 carried ~1,200
   activations/group and still went dark because the tokens beneath it were dirty.
3. **Combinatorial dilution (identifiability).** More groups per floor share a fixed
   observation/mining budget, and larger sets collide more (extent collisions are "one thing
   to any set observer, forever") and blur at the boundary ("closure is a negative fact
   positive co-occurrence cannot state").

Product of three per-floor factors ≈ the observed constant ~10× shrink. Attenuation and
impurity plausibly dominate; dilution sets the residual ceiling. The split is unmeasured —
that is the point of the experiments.

---

## 4. Which named laws/diseases this is (mapping to the Comparison Tower)

- **PRIMARY — the compounding-impurity law** (§4 "bottom-floor precision is the entire game")
  and **the dropout-attenuation law** (§4 "hierarchy is written in the dropout"). Together
  they produce the geometric fade.
- **CEILING — the boundary/closure disease** and **extent collisions** (§7, §8 standing
  walls). Because Isaac's `_crystallize` is **set-based**, it inherits both as a hard cap: it
  can find the right neighborhood (J≥0.5) but not the exact closed group, and can never split
  two groups with identical flattened atom-sets.
- **NOT primarily** the "landfill" over-generation disease (recall is near-zero, not
  precision) — though landfill may appear at the marginal floor (L2), where a few real groups
  and many fragments coexist. To be checked (E-DISEASE).

## 5. Why Isaac specifically has no defense

`isaac.py::_crystallize` (read 2026-07-07) is a **single-pass FCA closure over door
profiles**. Relative to what the Crystallizer v1→v4 program found to be *necessary* to climb,
it is missing:

| the climb needs | Isaac has it? |
|---|---|
| tier-climbing loop (re-tokenize, mine the next floor) | partial — `consolidate` is single-pass; no built-in dirty-regime climb |
| **top-down purification** (clean L-1 tokens before mining L) | **no** — bottom-up only |
| **compression invariant** (detect when a tier is junk) | **no** — cannot see the 24→302 inflation |
| **absorption** (truncation-shadow dedup; only maximal-closed survive) | no (has a within-tier merge, not cross-tier absorption) |
| **explanatory-cover parsing** (groups compete to consume items) | no (FCA annotates; it does not parse) |
| **count channel** (multiplicities; break collisions) | **no** — set-based |

Conclusion: **Isaac did not fail at hierarchy; it failed at the channel, with a layer-1
tool.** It climbs clean substrate fine (the good-science regime closes 60/60 and re-tokenizes
to 12/12) and cannot climb dirty substrate, because it has no machinery to purify the
substrate as it climbs.

---

## 5b. Competing hypotheses (owner's challenge, 2026-07-07 — record before deciding)

The analysis above (§2–§3) leans on **substrate-impurity from sequential bottom-up
composition**. The owner challenges the load-bearing beam: *"the order/layer you built from
doesn't matter — detection and potential matter."* This is a real, decidable fork. Both are
recorded; the experiment decides.

- **H-A (direction / substrate — the §2–§3 story).** Recovery is compositional; L2 fails
  because it is mined from dirty, incomplete L1 tokens; the fix is to purify the substrate
  (top-down) before climbing. *Presupposes* that recovery must proceed floor-by-floor.

- **H-B (detection + potential — the owner's, and better-grounded in the theory).** Layer
  index is **epiphenomenal** — a proxy for fragment size. A unit is recovered iff (i) its
  per-sighting fragment is big/frequent enough (**detection** ≈ `detect^depth`) and (ii) the
  system can hold it as an unconfirmed **potential** (`⁻⁰`, the x-ledger) and accumulate
  sparse fragments across a long span until it crystallizes. Deep units fail because each
  sighting is a tiny fragment AND Isaac's single-pass crystallizer has **no long-span
  potential accumulation**. Build-order is irrelevant; you detect potentials at any level
  directly from the stream.
  - Note: §2's "every view is a top-group sample" actually SUPPORTS H-B — top units are
    maximally present in the data, so they are detectable directly; they fail only because
    Isaac cannot bank their sparse fragments as a held-open potential. The observation being
    top-down is not a "wrong direction," it is evidence that direction is the wrong frame.

**Discriminator = E-ORACLE.** H-A predicts clean L1 tokens make L2 jump; H-B predicts clean
tokens barely help (the loss is detection+potential, not dirty substrate). **E-POTENTIAL**
tests H-B's positive claim: an x-ledger on a DIRTY substrate should crack the deep layers.

## 6. Experiment plan — registered predictions (the NEXT phase)

Each isolates one loss. Run blind on Foundry worlds; score extensionally (best-Jaccard per
layer vs unique extents). Predictions are registered here BEFORE running; a failed prediction
is reported with its diagnosis.

- **E-CLEAN — is it structure or channel?** Run Isaac in the whole-unit regime (complete
  groups, no dropout). *Prediction:* recovers all floors (≫ L2 10%), confirming the collapse
  is channel-induced, not a structural inability. *Falsifier:* still collapses clean → the
  problem is in the resolver's composition, not the channel.
- **E-ORACLE — isolate substrate impurity.** Feed Isaac the TRUE L1 tokens (oracle
  purification) and mine L2. *Prediction:* L2 jumps far above 10%. *Falsifier:* L2 stays ~10%
  → impurity is not the dominant loss; attenuation/dilution is.
- **E-SWEEP — the attenuation law.** Vary `detect` ∈ {0.35, 0.55, 0.65, 0.85, 1.0}. *Prediction
  (from the doc):* L2 recovery is non-monotone, peaking ~0.65; at `detect`→1.0 the hierarchy
  ERASES (even L1 dies). *Falsifier:* monotone in detect → the "occlusion is the ink" law is
  wrong in this world.
- **E-MIX — the untested prescription.** Observe at a MIXTURE of detection rates
  (e.g. 35/55/75%). *Prediction:* whole-tower recovery beats any single rate (each rate a
  focal depth). *Falsifier:* no better than the best single rate → mixed-rate prescription
  dead.
- **E-TOPDOWN — the direction hypothesis (H-A).** Add a top-down pass: use recovered higher
  units to purify/confirm lower tokens (bottom-up propose, top-down verify), then re-mine.
  *Prediction:* beats pure bottom-up on L2+. *Falsifier:* no gain → direction is not the lever.
- **E-POTENTIAL — the ledger hypothesis (H-B, the owner's positive claim).** Bolt an
  x-ledger / potential-accumulator onto the resolver: posit unconfirmed units at ANY level
  directly from the stream, hold them open, accumulate sparse fragments across the full span,
  crystallize when constraints suffice — leaving the substrate DIRTY (no oracle purification).
  *Prediction:* the deep layers crack anyway (recovery ≫ the 10×/floor curve). *Falsifier:*
  no gain without clean substrate → potential is not sufficient; H-A's impurity term is real.
- **E-DISEASE — landfill vs boundary at the margin.** At L2, measure precision and the
  J≥0.5-vs-exact gap. *Prediction:* high J≥0.5, low exact (boundary), with a fragment tail
  (mild landfill). Informs whether closure/counts or purification is the first fix.

**Decision rule.** (E-ORACLE, E-POTENTIAL) separate the two live hypotheses:
- E-ORACLE jumps L2 → **H-A** (substrate impurity): first fix = top-down purification.
- E-ORACLE barely helps but E-POTENTIAL cracks deep layers → **H-B** (detection + potential):
  first fix = an x-ledger / potential-accumulator, plus attending to detection (E-SWEEP/E-MIX);
  layer/order is a non-lever and substrate purity is a red herring.
- Both help → the losses coexist; sequence fixes by measured effect size.

Only after the machine decides do we refine a solution. Candidate levers, licensed in whatever
order the evidence supports: potential-ledger, the count channel, mixed-rate observation,
top-down purification, and the compression invariant + absorption + parsing from Crystallizer v4.

---

## 7. What this is NOT claiming (yet)

- The exact split among the three losses is **unmeasured**; §3 is a hypothesis with a shape,
  not a result.
- "Isaac is set-based → inherits the collision wall" is read from the code, but its *size* in
  this world is unmeasured (needs the Foundry collision count for these seeds).
- No solution is endorsed. §6 is how we earn one.
