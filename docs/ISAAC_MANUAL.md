# THE ISAAC MANUAL
### The complete, current capability reference — every part, every method, honestly scoped
**Engine:** `isaac.py` (repo root) (one file, one class, numpy only, no neural nets in any decision path)
**Self-test:** `PYTHONIOENCODING=utf-8 python isaac.py` → expect **11/11**
**UI:** `python ui/isaac_ui.py` → http://127.0.0.1:8674

> **MAINTENANCE RULE (same as ISAAC_BUILD_STATE.md):** when a capability is
> added, changed, or broken, update THIS manual in the same step. If a
> capability isn't documented here, assume it doesn't exist. The narrative
> introduction lives in `PAPERCLIP_MANUAL.md`; the day-by-day state ledger in
> `docs/ISAAC_BUILD_STATE.md`; THIS doc is what he can DO.

**Verification status legend** (every capability section below is tagged):
- **[VERIFIED 2026-07-03 — re-run from this repo]** — re-executed from this
  repo on 2026-07-03; output logs in `experiments/runs/2026-07-03/`.
- **[VERIFIED IN ENGINE SELF-TEST 11/11]** — exercised by `python isaac.py`
  (re-run 2026-07-03 from this repo: "11/11 capability areas passed").
- **[HARNESS-ONLY — experiments/, not wired into engine]** — the capability
  lives in a harness script under `experiments/`, not in `isaac.py`.
- **[RECORDED — script not in this repo or data required; not independently
  re-verified]** — a number from the research record; reproducing it needs
  datasets, long runs, or a script variant not yet committed here.

---

## 0. The two primitives and the four laws

Everything below is two operations composing: **differentiation** (compare;
keep what recurs) and **memory recursion** (a discovery becomes a thing that
can enter further discoveries). Four laws govern every mechanism:

1. **The null law** — every admitted claim beats a null designed to destroy
   exactly the claimed structure, nothing else. (Five case studies: jitter
   null for co-timing; null-gated basis; conditional rate-gap for blockers;
   F-test at the noise ceiling; block-permutation for autocorrelated
   targets — the last CLOSED 2026-07-04: the admission null now permutes
   blocks at the residual's measured decorrelation length.)
2. **Tests over thresholds** — wherever a fixed threshold caused trouble, a
   statistical test replaced it.
3. **The proposal principle** — "we offer possible solutions, not THE
   solution." Teaching adds candidates; only evidence adds conclusions.
4. **Everything enters, nothing leaves** — forgetting is demotion from the
   comparison set, never deletion.

---

## 1. The mind's substrate — [VERIFIED IN ENGINE SELF-TEST 11/11]

| part | what it is | key methods |
|---|---|---|
| `Net` | the only data structure: nodes + directed tagged doors + metadata | `add_door(src,tgt,tag)`, `get_doors(node,tag)`, `get_predecessors`, `get_full_profile`, `set_meta/get_meta` |
| `Scratch` | working memory: named registers with history | `write/read/incr/append/latch/history/snapshot` |
| `compare(a,b)` | the differentiation atom (sets): shared / only-a / only-b | module function |
| `World` | mutable entity states + taught actions | `set_state/clear_state/has_state`, `teach_action`, `execute` |
| findings | the scientific memory (see §8) | `record_finding/recall_findings/load_ledger` |

## 2. Sensing (how experience enters) — [VERIFIED IN ENGINE SELF-TEST 11/11]

- `observe(tokens)` — sequence → sequential doors; dirty-marking; immediate
  type-slotting (`_sense`); auto-`tick`s each token with its type doors.
- `observe_negative / observe_tagged / observe_frame / observe_matrix` —
  negation, custom tags, frames, tabular ingestion.
- `teach(subject, relation, object)` — a fact: observed AND indexed in
  `fact_index[(s,r)] → [objects]`. (Internal discoveries use `_teach_fact`,
  which skips the tokenizer — structured names would be shredded.)
- `tick(active_set)` — one instant of simultaneous activation. Any retina,
  game loop, or sensor can call it; it feeds `activation_log` and, if a
  circle is being followed (§6), advances the clock and opens statuses.
  **Caveat:** clock ticks are sensory ticks — keep one stream per episode.

## 3. Consolidation (idle mode — "sleep") — [VERIFIED IN ENGINE SELF-TEST 11/11]

- `consolidate()` / `crystallize()` — FCA-style type discovery from door
  profiles (dirty-scoped or full). Types are nodes; membership doors both
  ways. **Merge amended 2026-07-03 to the owner's two laws** (battery:
  `experiments/crystallizer_battery.py`, before/after runs kept):
  (1) merge only near-identical member sets — a proper subgroup stays a
  distinct type and is linked by hierarchy instead ("abc and abd are not
  the same thing, but they can both belong to the ab group" — verified:
  abc + abd + shared ab parent all survive); (2) a **positive negative
  vetoes any merge** — penguin `not_fly` is evidence, not absence; a merge
  that would erase a positively-disclaimed distinction is forbidden
  (verified: fly-birds keep `fly` in their intent, penguin excluded from
  fly-types but still in the shared birds group). **A2 CLOSED
  2026-07-04** (admission battery 10/10 + C1–C6 re-verified): the
  wrong/sound verdict is a degrees-aware hypergeometric TEST (below);
  `min_shared=2` stays as the candidate floor (expansion — propose
  freely; admission is the test); wrong-verdict types are demoted from
  ORGANIZING (no hierarchy minting — law 4 demotion, same as senses);
  co-occurrence rules face a chance gate. Scale knee RE-MEASURED after
  the E3 reverse index + shuffle removal: 0.02 s @ 50, 0.65 @ 200,
  ~26 s @ 800 (was 0.04/2.9/~420).
- `teach_not(subject, prop)` — a positive negative: indexes a cannot-fact
  (the reasoning layer honors it) AND writes a first-class `not_<prop>`
  door (tag `neg`, so negatives never leak into sequence generation) —
  crystallization can share it (penguins and ostriches share `not_fly`)
  and be vetoed by it. Known-different never collapses; only unknown may.
- **WRONG IS KEPT AND CLASSIFIED (owner's law, 2026-07-03; test upgraded
  2026-07-04).** "Knowing what is right is intelligence. Knowing what is
  wrong is wisdom." Every crystallized type is tested against chance —
  since A2, a **degrees-aware hypergeometric test** (supersedes the 07-03
  global re-clustering shuffle, which gave the same battery verdicts at
  8× the cost): p(type) = pairs-scanned selection charge × P(the two
  chanciest members share the k-door intent | their degrees, the
  context's door universe) × each further member's chance of covering the
  whole intent; sound iff p < 0.01, p stored on the node meta
  (`p_chance`). Types that fail are neither prevented nor deleted: filed
  in `isaac.wrong_types` with the WHY (now naming the degrees and
  universe). Wrong types are demoted from ORGANIZING (hierarchy needs
  both types sound) but otherwise downstream behavior is unchanged: no
  pruning, no importance-weighting (the old trap). Battery C3 re-verified
  under the new test: chance types filed wrong with reasons; C1 category
  types sound with p < 0.01.
- **Lockouts are evidence-weighted and revisable (A4, 2026-07-04).** One
  negative observation → ACTIVE lockout labeled `provisional`
  (`isaac.lockout_status`); ≥2 → `confirmed`; a lockout later
  contradicted by positive observation is RETRACTED from the active set
  into `isaac.wrong_lockouts` with the why — the net keeps the door
  (nothing leaves the net; the active set is a comparison set, law 4).
  Admission battery A4a–c: provisional/confirmed/retraction all pinned.
- **SUPERSESSION, not overwrite (owner's law, 2026-07-03).** "If there is
  a and b, and b works better, use b" — and A is KEPT, wearing its
  defeat. `confirm()` OVERTURN now appends the losing form to the law's
  `superseded` list with the why (what was believed, what beat it, by how
  much). Battery C6: after the pendulum overturn, the parabola remains on
  the record with "overturned by rival 'cosine'... SSE 3.198 vs 1253".
- **DIVERGENT doors self-assemble (the foundation fix, 2026-07-03).** The
  atom's three verdicts all write now: SAME → membership (always did);
  **DIVERGENT → a `not_<door>` minted from experience**; ABSENT →
  nothing. During every consolidation, a node carrying the REST of a
  circle's intent, observed repeatedly (≥3 sightings) WITHOUT the one
  door its siblings show essentially always, has positively diverged —
  the gate is a Laplace-smoothed binomial against the "you are like your
  siblings" null at 1%, on the net's new per-door observation counts
  (`Net.door_counts` — "seen once" and "seen a hundred times" are
  different facts now). Runs BEFORE the merge phase, so a fresh negative
  can veto a collapse in the same sleep. Battery C2c: penguin earns
  `not_fly` by being watched, never taught; a chick seen twice earns
  nothing (ABSENT stays silent).
- `wave_consolidate()` — the temporal crystallizer, one mechanism recursed:
  - **groups** — doors that fire together (jitter-null + independence floor,
    1.4× anti-bridge margin);
  - **conditional rescue** — a door exiled by heavy interference re-joins
    when membership holds where a candidate blocker is absent; the blocker
    is taught as a `blocks` fact in the same move;
  - **handoffs** — group g off co-timed with h on (the wave moving);
  - **circles** — closed handoff paths; entered as nodes with `wave_next`
    order; dwell learned as meta (the clock's calibration);
  - **level 2** — circle activity becomes doors; same stages rerun
    (circles of circles, demonstrated);
  - **status explanations** — `miss:X` doors get explained by ordinary
    co-activation scoped to the entity's own timeframe → `blocks` facts.
  Operating envelope (battery-measured): period ≥ 9 ticks, instantaneous
  handoffs, non-overlapping groups, fire rate ≥ 0.7, ≲4 concurrent
  aperiodic waves, T ≥ ~1000. Movement claims: 0/20 false on noise.
- **Composition: wholes with ARRANGEMENT (C1, 2026-07-04; battery
  `experiments/uptake_battery.py` 10/10 — rebuild B's (a)–(g) now
  engine-native).** A whole = parts + uptake edges
  (provider —affordance→ consumer); configuration IS the edge set;
  everything is net structure (`offer:`, `uptake:`, `whole:` nodes).
  Methods: `register_part(name, offers)` (teach affordances +
  requirements), `assemble(name, parts, edges)` (identity =
  order-independent (parts, edges); a rewired whole is a DIFFERENT
  whole), `operable(whole)` (fixed-point propagation: an affordance
  lives when its requirements arrive via edges from live providers),
  `emergent(whole)` (operable at the whole, in no part alone),
  `dismantle(whole)`, `whole_as_part(whole)` (upward composition —
  engine+wheels+frame → car affords locomotion). LEARNED arrangement:
  `wave_consolidate` handoffs mint the same `uptake:` structure and
  circles ARRANGE their edges — temporal wholes carry arrangement
  without being taught. (Membership-only crystals were the audit's
  designed-in flaw 2.3 — engine migration done.)
- `crystallize_senses(node, min_shared=2)` — **SENSES ARE THINGS
  (rebuilt 2026-07-04; battery `experiments/sense_battery.py` 14/14).**
  The crystallizer turned inward on ONE node: occurrences (from
  `observed_sequences`) sharing ≥ `min_shared` context tokens link into
  candidate senses — and each candidate is minted as a **first-class
  node** `sense:<node>#<gen>.<k>` with real directed doors, not a meta
  blob: node→sense (tag `sense`), pred→sense and sense→succ (tag
  `sense_seq` — direction is net structure), sense→context (tag
  `sense_ctx`). Every net-walker (`compare_nodes`, the crystallizer,
  inference) can see sense structure now. **Admission is null-gated**:
  each sense's coherence score ((occurrences−1) × shared context core)
  must beat the BEST sense produced by reshuffling context tokens across
  occurrences (sizes and token frequencies preserved — the null destroys
  exactly the claimed assignment; selection-corrected max over shuffles;
  0/20 false senses on random contexts). Failures are **kept and
  classified wrong** with the why (`isaac.wrong_senses` + node meta).
  Re-crystallizing **supersedes** the old generation (verdict
  `superseded`, kept in the net), never overwrites. Verified in the
  engine self-test (language area) incl. save/load round-trip.
  **Remaining limits:** candidate *linking* is still the fixed
  `min_shared` count (only *admission* is a test); re-run is batch, not
  incremental; membership door is node→sense only.
- `route(node, incoming)` — read through a node BY SENSE, **from the
  doors**: `incoming` (one token or a set of context tokens) is
  overlap-matched against each sense node's in-doors + context doors;
  only SOUND senses compete (wrong and superseded are demoted from the
  comparison set — law 4 — never deleted); the winning sense's
  `sense_seq` out-doors are returned. Falls back to the node's flat
  `seq` door-set when no sound sense matches.

## 4. Thinking (query paths) — [VERIFIED IN ENGINE SELF-TEST 11/11]

- `lookup(context)` / `check(context, target)` — argmax / specific-cell read
  through the think loop (recall → process → evaluate) over the compiled
  frame→delta matrix. Auto-compiles when dirty.
- `predict_next`, `walk_chain`, `generate` — door-walking alternatives.
- `transduce(start, stream)` — the universal state walk: next state =
  `lookup([state, symbol])`; state lives in Scratch. Counting, parity,
  motion all reuse this loop; only the taught doors differ.
- `compute(a, op, b)` — arithmetic with decompose-when-shrug + memoization.
- `solve(problem)` — token problems with `?` unknowns (forward / backward /
  gap-fill). *(Distinct from `apply_law` — see §7.)*
- `solve_steps(steps, verbose=True)` — multi-step solving: a list of
  problem strings in which `$0`, `$1`, … reference earlier steps'
  answers; each resolved step runs through `solve`. Returns the list of
  results (the working shown step by step when verbose).
- `logic_eval`, `reason_chain`, `is_a_check`, `can_check`,
  `containment_check`, `property_check`, `syllogism` — the symbolic layer;
  reads facts and type doors.
- `assess / plan_think_execute` + `World` actions — consequence layer.
- Introspection / net-walking:
  - `check_connection(src, tgt)` — is src→tgt a valid connection? Walks
    the net and returns `(valid, manifest)`; the manifest records direct
    `seq`/`neg` doors, lockout, and per-type support vs contradiction.
    Valid = a direct seq door OR ≥1 type whose other members have the
    door; a lockout vetoes everything.
  - `compare_nodes(a, b, tag=None)` — the differentiation atom applied to
    two nodes: shared / only-a / only-b, computed over both outgoing and
    incoming doors (optionally one tag).
  - `infer(src, tgt, tag="seq")` — can src connect to tgt? Walks src's
    types looking for a sibling member that already has the door; if one
    is found the door is ADDED (a side effect, not just a query) and
    `{"inferred": True, "via": member, "type": t}` returned, else
    `{"inferred": False}`. **Limit:** the first supporting sibling wins —
    no vote, no null.
  - `status()` — the mind's vitals as one dict: node/door counts, tags in
    use, types/rules/lockouts/starts, observations, indexed facts,
    compiled flag + matrix shape, dirty counters. (Printed at the end of
    the self-test.)

## 5. Perception (doors, not boxes) — [VERIFIED 2026-07-03 — re-run from this repo] (in-engine methods, via `experiments/doors_proximity.py` + `experiments/digits_structural.py`; harness-side items tagged inline)

- `fit_lens(name, X, ...)` — registers an aligner. **Default = the
  null-gated basis**: standardize, then rotate only along correlations
  beating ~3/√n (the basis itself must beat chance). Optional random lift,
  discriminative select (Fisher option survives but is deprecated by
  audit 2.7 — do not use it for causal ranking).
- `crystallize_features(X, y, lens=, compounds="auto")` — one
  concept-node per class whose doors are **observed quantile
  log-densities** (proximity doors). Legacy box meta still written for
  `recognize_matrix`/old scripts. **Compound doors + the ceiling trigger
  (C2, 2026-07-04; audit 2.11 wired; battery
  `experiments/compound_battery.py` 6/6):** when flat doors leave
  held-out confusions, conjunction doors ("feature i in bin a AND
  feature j in bin b") are mined per confused class pair — admitted only
  past a selection-corrected label-permutation null, KEPT only if
  held-out accuracy improves; the decision is recorded
  (`compound_report` in the crystal calib) and `classify_features`
  augments identically. XOR: flat 0.46 → compounds 0.89. Migration note:
  the harness's marginal-separation work-filter hard-blocked pure-XOR
  structure (marginals exactly zero) — removed; the null is the gate.
- `classify_features(X)` — summed log-likelihood, one matmul-shaped
  decision. **Known gap: no abstention** — it always answers (fix queued:
  shrug + genus-level answers).
- `recognize_doors(active, tag)` — partial, recursive recognition: a
  concept fires from the fraction of its `part` doors present (permanence;
  load-bearing in the clock).
- `apply_lens(name, X)` — run data through a registered lens: optional
  random lift + ReLU, then the null-gated rotation (standardize, rotate)
  or DC-strip, then dim selection — whatever the transform stored on
  `lens:<name>` specifies. `name=None` is the identity. Returns the
  aligned array. Used internally by crystallize/classify; public so you
  can inspect what a lens does to data.
- Harness-side **[HARNESS-ONLY — experiments/, not wired into engine]**:
  **registration front-end** (`experiments/registration_perception.py` —
  pose/identity factoring; pose returned as data) and **ideals +
  differentia** (`experiments/ideals_differentia.py` — genus/species
  recognition, key identifiers discovered by minimal inter-sibling door
  overlap, honest genus-level ties, truncation cue).
  **Registration number caveat [RECORDED — script not in this repo]:**
  the headline 84–87% (digits under position+scale, up from ~5–15% raw)
  came from a 16×16-canvas variant of the harness that was never
  committed. **RESOLVED same day:** the 16×16 harness was rebuilt as
  `experiments/registration_perception_16.py` and the numbers vindicated —
  raw canvas 23.7% → registered **84.4%** (recorded 84.4 exact), novel
  bigger sizes 85.4%, tiny sizes 58.3% (information floor). The 8×8 script
  remains as the edge-clipping caveat case (~5–15% → 21–53%: information
  destruction, not registration failure).

## 5b. Spatial perception — the bridge (relations from motion) — [VERIFIED IN ENGINE SELF-TEST 11/11]

The perception wall, crossed (2026-07-03; validated in harness first —
`spatial/test_isaac_bridge.py` — then migrated into the engine). The rule:
**coordinates are scratch, relations are storage.** The engine watches point
trajectories and stores only what refuses to vary.

- `observe_spatial(frames, label=)` — frames = (T × n_points × dims) array
  of positions over time (any dimensionality; assumes temporally
  continuous observation — adjacent frames close in time). Classifies
  every point pair, **null-gated, no hand-tuned thresholds**:
  - **locked** — total variation explained by measurement noise alone
    (variance-ratio test against the pair's own noise floor, estimated
    from its first differences);
  - **bounded** — repeatable extremes (hysteresis-counted) that beat an
    increment-shuffle surrogate null (a random walk CAN revisit extremes
    by luck; the surrogate is the test);
  - **free** — the rest.
  Then: parts = maximal pairwise-locked cliques (grown from edges);
  hinges = single-point clique overlaps; anchors = points whose
  coordinate variation is noise-sized (same calibrated gate). Teaches
  facts via `teach()` (indexed AND observed, so doors form):
  `locked_to / bounded_with / contains / hinge_at / anchored_at`, plus a
  **scale-free signature** (sorted locked-length ratios) on a
  `scene:<label>` node. **If nothing survives the nulls, NOTHING is
  taught** — perception that can refuse (random walkers teach 0 facts).
- `compare_scenes(a, b)` — SAME/DIFFERENT from stored relations only:
  signature + part-size multiset + hinge count. Pose, scale and position
  cannot matter because they were never stored. Self-test: the same
  four-bar at 2.4× scale, rotated and translated → SAME (signature gap
  0.0); a rigid plate on a pin → DIFFERENT.
- **The 2D→3D lift (owner's build, 2026-07-04; battery
  `experiments/pattern3d_battery.py` 9/9).** `observe_spatial` on 2D
  tracks now attempts depth recovery behind a TRIGGER (same discipline
  as compound doors): only when flat perception hits its ceiling —
  nothing locked in 2D (a planar mechanism has locked bars and never
  triggers; the four-bar broke under an unconditional lift — suite
  caught it). `_lift_depth` = Tomasi–Kanade factorization + metric
  upgrade, TRIPLE-null-gated: planar scenes refuse (2 components
  suffice), non-rigid scenes refuse (rank-3 leaves structure), and
  smooth noise refuses via the **rank-cliff null** (rank-3
  reconstruction is rigid BY CONSTRUCTION, so small residual alone
  proves nothing — random walks were being FABRICATED into rigid
  bodies until s3≫s4 was required; battery L3). Verified: a rotating
  rigid body's recovered 3D distances are constant (cv 0.0000 where 2D
  distances varied 26%); same body across different motions → SAME;
  different body → DIFFERENT.
- **The SPATIAL PATTERN NET — 2D→2D abstraction (owner: "it needs to
  work on 2d to 2d abstraction too... it can learn the spatial pattern
  net").** `learn_pattern(views, label, n_rot=)`: instances of a class
  are VIEWS of a canonical form; ICP-lite similarity registration
  factors the view-transform out; a canonical part is admitted only if
  its cross-view spread beats scrambled-view registration (the null);
  the pattern is NET STRUCTURE (pattern:/part: nodes + doors).
  `recognize_pattern(points)` — best registration residual wins, WITH
  ABSTENTION at the pattern's measured chance-registration bar (junk
  19/20 shrugged). Rotation freedom is part of the CLASS (n_rot=1 for
  digits — a 6 is an upside-down 9). Glyphs: 90% on fresh transformed
  instances. MNIST keypoints under shift+scale+tilt: **56.2% where he
  answers (48/200 answered — a trustworthy floor)** vs 38.5%
  unregistered; the honest gap is keypoint quality (farthest-point ink
  sampling is unstable — structural keypoints are the named next
  step). ICP note: free scale invites collapse (shrink to fake a low
  residual) — clamped to [0.8, 1.25]; battery caught it at 25%→56%.
- **The WIREFRAME organs (owner's 2D-transformer design, 2026-07-04;
  battery `experiments/wireframe_battery.py` 8/8).** "A wireframe
  concept of the thing that Isaac can then run numbers over":
  - `keypoints_structural(img)` — **bones**: Zhang–Suen skeleton →
    spur-pruned, junction-merged endpoints/junctions (the bone ends).
    On MNIST patterns: **74.2% where answered vs 33.3%** for raw ink
    sampling, and more total correct (23 vs 19 per 200); coverage
    (31/200 answered) is the open dial — precision-first, honestly.
  - `complete_symmetry(points)` — **the assumed reflection axis fills
    unknowns**: candidate planes come from mirror PAIRS (normal = pair
    difference, offset = midpoint projection — a plane through the
    lopsided centroid of a partial scan was v1's bug); earned only past
    a scrambled-cloud null (asymmetric refuses 10/10; symmetry is
    honestly UNFALSIFIABLE from one side alone — some sliver of the
    other side must be seen); unmatched mirrors return as INFERRED
    geometry, provenance-marked, never mixed with observations. Sliver
    test: 3 hidden points inferred at 0.0000 error.
  - `stitch_views(views)` — **faces stitched into an idea**: partial
    rigid scans (ids, local coords) merge through ≥3 shared points
    (Procrustes, both depth signs tried — the factorization sign
    ambiguity); machine-exact on ground truth (1.3e-15); refuses when
    overlap is too thin.
- **FULL AND HOLLOW — the shape vocabulary (owner, 2026-07-04: "circle
  vs disc vs sphere vs ball... it could see the 8 is two circles maybe
  one a bit squished"; battery `experiments/shapes_battery.py` 11/11).**
  Topology is identity, geometry is framing — a HOLE is what makes a
  ring a ring. `describe_shape(img)`: holes → rings (with squish =
  axis ratio and angle), hole-less compact blobs → discs, thin strokes
  → bars; arrangement = INK CONNECTIVITY (parts of one component touch
  — a fact, not a radius estimate; the first cut thresholded center
  distances and missed the 8's own join); output is parts +
  arrangement + gated English, and with teach_label the decomposition
  ASSEMBLES into the net (a whole whose parts are shapes — the C1
  machinery). The 8 answers: **"two rings, stacked, one squished
  (0.66)"**. `classify_solid(points)`: 3D shell (sphere, radius cv→0)
  vs solid (ball, cv≈0.26 exact for uniform), middle band refuses.
  **Lines, rectangles, and RELATIONAL ROTATION (owner, same day;
  battery `experiments/rotation_battery.py` 11/11):** skeleton strokes
  decompose by peeling diameter paths + Douglas–Peucker corner splits
  into LINES; joined lines carry their JOINT ANGLE; round-vs-square is
  FILL in the region's own frame (frame/rect kinds, square flagged);
  every part carries rel_angle (identity) and the whole carries tilt
  (pose) — a slanted 8 is the upright 8 plus "tilted -18°"; the 7 is
  "two lines, joined at 60°" and keeps that joint when rotated while
  its tilt moves. Three root-cause perception bugs battery-caught
  (see BUILD_STATE; deepest: components were 4-connected, skeletons
  are 8-connected paths). Real handwriting: hole-count agrees with
  canonical digit topology **86%**; the (holes, lines) signature road
  now scores **52–58% at 299/300 coverage** (was 38.5 pre-fix) — the
  two-tier road (topology filters, bone patterns decide) is the named
  next step.
- **ALL METHODS, ONE CONCEPT (owner, 2026-07-05; battery
  `experiments/fusion_battery.py` 2/2).** "The doors are just pointer
  connections... they all point to the same nodes." `learn_glyphs` puts
  EVERY channel's evidence on the same concept nodes — pixel-density
  doors, topology/line signatures, bones pattern nets, exemplars — and
  `recognize_glyph` sums every channel's posterior into one vote (the
  vote is returned readable, channel by channel). COMPLETE numbers
  (whole test set, 200 training glyphs/class, 500 test): topology
  55.8%, bones 10.0%, density 79.4%, exemplar 85.4%, **FUSED 88.6%**
  — the sum beats every specialist. Channels are not rival classifiers;
  they are doors on one node.
- **THE TRAINED READOUT + THE EXTRACTOR (owner, 2026-07-05; study
  `experiments/single_layer_study.py`).** "How information from multiple
  sources is compared to total activation": `train_readout` fits ONE
  softmax layer over the node structure outputs (5 channels × classes,
  named inputs; trained only on glyphs outside the exemplar store).
  Because it is linear, `extract_readout` is LOSSLESS — the layer IS an
  equation set: per class, signed weighted evidence terms (signed-deltas
  law: inhibition is a fact), written as readout doors and said in
  English ("decide 8: +6.5·density[8] +4.7·topology[8]... inhibited by
  bones[5]"). Learned inhibitions mirror the measured confusion pairs.
  COMPLETE numbers (200/class train, 500 test): softmax on raw pixels
  86.0; one-hidden-layer on pixels 89.4; **softmax on node outputs
  95.0–95.2 — the percepts beat raw data by +9 under the identical
  linear model**, and the trained comparator beats hand calibration by
  ~3. When a readout exists, recognize_glyph uses it as the comparator
  (vetoes and shortlist semantics kept on top).
- **PRINT-AND-OVERLAY: THE SYMBOL CHANNEL (owner, 2026-07-10; benchmark
  `experiments/vision_benchmark.py`).** "Just print and overlay the
  nearest font number... trivial for a computer." `attach_symbol_forms`
  (or `learn_glyphs(symbol_forms=...)`) puts RENDERED forms of each
  class's symbol on the same concept node as templates (engine
  normalizes via `_norm_glyph`: crop→20px→center-of-mass in 28×28, soft
  ink) and mints `symbol:<c> -names-> concept:<c>` — the string is a net
  object; polysemy runs BOTH directions. `recognize_glyph` gains the
  `render` channel: cosine overlay vs every form at ±2px shifts, nearest
  print votes; the weight is measured like every channel's; pair judges
  hire it per duel automatically. `overlay_delta` is the effect-entity
  face (D9, vision): expectation rendered → subtracted → SIGNED delta
  (extra ink vs missing ink are different facts) + similarity as a
  MEASURED badness-of-drawing score. COMPLETE numbers (templates from 5
  fonts, tested on 5 DISJOINT fonts): render alone **100%** on printed
  digits never seen, 58.0% on handwritten; fused printed 86.0→**92.0**;
  fused handwritten 95.4→95.6 (no regression). Honest miss: on the 150
  worst-drawn glyphs (lowest overlay similarity, median 0.60) render
  added +0.0 — the print is least informative exactly where the glyph
  least resembles it; the badness NUMBER itself is the win there.
  Rendering (fonts, PIL) stays outside the engine — it is observation
  I/O; the engine takes images.
- Limits (honest): trajectories need identities given (the tracker half
  of the pixel bridge is still open); the lift is single-rigid-body
  (multi-body SfM not built — stitch_views covers the multi-VIEW case,
  not multi-BODY); all-pairs cost O(n²) per frame set; bounded
  certification needs enough revisits; sprung classification exists in
  the harness (`spatial/engine.py`) but not yet in-engine; pattern-net
  keypoints are geometry-only (no texture/color — CIFAR needs more than
  shape); bone-pattern coverage low (abstains 84% on transformed MNIST
  — the recognition bar and per-class bone variation are the next
  dials); wireframe BONE GRAPH (bones as net edges with length-ratio
  meta, "run numbers over it") is minted only as keypoints so far —
  ratios-on-bones discovery is the named next step.
- The full spatial suite (solver, occlusion inference, materials, maps,
  circuits, the null battery) lives in `spatial/` — 13 standalone tests.
  The GM plays mechanism worlds against this capability:
  `experiments/world_gm_spatial.py` (3/3 incl. hidden-link recovery via
  bought probe angles).

## 6. The clock, statuses, expectation — [VERIFIED IN ENGINE SELF-TEST 11/11]

- `follow(circle)` — attend to a discovered circle: phases ordered by
  `wave_next`, members and learned dwell loaded; registers live in Scratch.
- every `tick` then: evidence advances the phase (via `recognize_doors` —
  occlusion-tolerant); learned dwell dead-reckons when evidence is hidden;
  expected-but-dark doors persist 2 ticks → **status**: `world.set_state
  (phase, "missing X")` + a `miss:X` door fed back into the same tick
  (statuses are doors — explanations emerge in §3). Statuses clear on
  sight or when the entity leaves the stage (absence-by-night ≠ occlusion).
- Self-test: phase 100% through occlusion; statuses 94.1%/tick;
  `blocks(disk) ← cloud` queryable in `fact_index`.

## 7. Discovery — the challenge loop (the thing that learns things) — [VERIFIED IN ENGINE SELF-TEST 11/11]

- `discover(X, y, name=)` — given examples of something he cannot do:
  - **atom library**: variables; products to degree 3; sin/cos at scale
    grids; exp decay AND growth; **the power DIAL** (−2, −1, −0.5, **0**,
    0.5, 1.5 — where **λ=0 IS log**, the Box-Cox limit: "isn't a log just
    a power? it's not special" — correct; log and sqrt also joined the
    rival look-alikes); pairwise cos/sin/cosh of differences. Grids
    PROPOSE scale parameters (unreachable by regression); hill-climbing
    refits SHARPEN them. `y = a·ln(x)+b` is sayable natively:
    cold discovery writes `+2.00*log(x0) +1.00` exact.
    **Phase-fold period proposal (E7 cure, owner's design 2026-07-04:
    "do the projection thing... a few samples and to map it")**: before
    atoms are built, y is FOLDED onto candidate periods of each input
    (coarse geomspace scan + fine scan around the winner); coherence =
    variance explained by phase bins; a period is proposed only past a
    selection-corrected block-perm null replaying the same two-stage
    scan (99th pct, 100 draws — white noise proposes ~nothing). Proposed
    frequencies join the sin/cos grid for that discover() and still face
    the admission null. Battery `experiments/periodfold_battery.py` 6/6:
    off-grid sin(1.5t) over 40u + AR noise — NO RULE pre-fold —
    articulated at k=1.506; **150 scattered timestamps suffice**
    (UNDERSTOOD; folding needs coverage of the cycle, not of time);
    0/5 false laws on AR noise; iid path untouched.
    **Period proposal is now THREE ROADS, none refereeing another
    (2026-07-12, the divisibility arc):** road 0 — integer axes get
    integer periods 2..min(n/4,128) CHECKED OUTRIGHT by residue
    classes (owner: "if it looks or is close to a whole number, it
    should go to that whole number and check it just outright") —
    exact, no spectral machinery; fundamental = smallest P of its
    family (multiples are shadows). Road 1 — regular axes: the DFT
    comb (enrichment of power at j + harmonics vs bins occupied;
    null = median-smoothed spectrum-envelope surrogates × Exp(1) —
    block-perm was wrong-kept here: blocks preserve short periods
    internally and the gate inflates exactly when a true comb is
    present; fundamental = LARGEST j with its family's full share —
    flat combs TIE plain enrichment across divisors, wrong-kept).
    Road 2 — any axis: the fold (Nyquist floor 2.05×median-spacing —
    the old 8-samples/cycle floor blocked periods 3/5 on integer
    grids, wrong-kept; two fine stages ±7% then ±0.7%). Roads 1+2
    picks get the WHOLE-NUMBER SNAP (near-whole → test the whole
    outright, adopt on ≥; cures the measured refine walk 3.0→3.0105).
    Each road dedups only within itself (cross-road dedup and
    cross-road refinement both wrong-kept: comb quantization shadowed
    the fold's precise 4.189; fold-refining comb picks walked exact
    truths off) — expansion is free, admission compresses. THE
    ADMISSION NULL ITSELF gained a per-block circular roll (block
    order + one global roll is PHASE-BLIND to sub-block periodicity:
    ~1/P of null draws replicate a period-P alignment — measured:
    period-2 residual unfindable at L=18; per-block rolls scramble
    periodic phase while keeping within-block texture; sunspot
    protection intact, blockperm battery 10/10). Vocabulary result:
    divisibility indicators are exactly sayable — all four
    stream-class laws UNDERSTOOD r²=1.000 (fizzbuzz_probe re-run;
    calibration re-measured same day: form-true 31/52=60% beyond
    range vs standing 68%, within binomial noise — DECAY_MEASURED
    stands).
    **Lag-atom proposal (2026-07-12 — the causality cure)**: the
    causality probe measured temporal blindness exactly (on
    y(t)=f(x(t−k)) raw discover r²=0.000 at EVERY k≥1). Now, before
    atoms are built, EVERY integer lag 1..n/4 of each input is
    measured at once: FFT cross-correlation of y against three
    vocabulary transforms of the column (x, x², |x| — the linear
    projections of any dependence shape), max per lag. A lag is
    proposed only past a selection-corrected **circular-shift null**
    (max over all lags AND transforms, replayed on shifted y — the
    shift preserves autocorrelation texture exactly, destroys only
    alignment; shift range keeps a true peak outside the window; the
    gate is the observed MAX of 200 draws, never an interpolated
    percentile — measured: a 100-draw p99 estimate sat at 0.26 when
    the truth was 0.37, a false fire). Proposed lag columns join X
    as first-class variables (`[raw | composites | lags]`; equations
    print `x0[t-3]`), are recorded in law meta `lags_used` plus the
    full scan — refused columns wearing their numbers — in
    `lag_scan`, and still face the admission null term by term. Rows
    are read as consecutive samples; on exchangeable rows nothing
    survives (iid path untouched). **History-less rows refuse
    per-row**: NaN from `apply_law`/`law_confidence` (which also
    ignores proposed-but-unused lag columns), masked and counted by
    `validate_law` (`refused_rows`); `refine()` refuses lag laws
    whole (a point-probe cannot set a lagged value — extend the
    series and re-discover). WRONG-KEPT ×2: (a) v1 bracketed a
    coarse lag ladder + refine ±1 — on an iid driver an off-by-one
    lag carries ZERO signal, no gradient between anchors (k=40
    planted, anchors 29/41, refusal); exact full-lag FFT measurement
    is cheaper AND complete; bracket-and-refine stands for smooth
    parameter families only. (b) block-perm null for cross-alignment
    — seams break the very autocorrelation that generates spurious
    alignment (3/10 false proposals on unrelated AR(1) pairs; shift
    null + max gate: 0/10 false LAWS end-to-end). Battery
    `experiments/lag_battery.py` **14/14**: k=3 exact
    (`+2.00*x0[t-3]*x0[t-3]`, r²=0.9995); mixed same-row+lagged both
    named; two delays of one channel (x0[t-2], x0[t-6]) both said;
    k=40 iid driver found exactly; unrelated AR(1) pairs 0/10 false
    laws (2/10 gate-passing proposals — expansion free, admission
    compresses); ledger round-trip identical; probe re-run: raw road
    r²=1.000 at k=1,2,4,8, lag named every time (was 0.000).
  - **the open op family (learned combinations)**: product, sum,
    difference, **ratio** (guarded at b≈0), **log** (arity-1, guarded at
    x≤0), **mean** (arity-N collectives). Out-of-domain rows drop
    honestly at discover-time. Minted composites are columns for every
    future discover(); calibration was re-measured after the enumerator
    change (trust profile unchanged — `DECAY_MEASURED` stands).
  - **staged, null-gated admission**: candidates grow only around admitted
    terms; a term must beat the max-over-candidates correlation on
    permuted residuals; trial shortlist is structurally diverse (raw-var
    candidates guaranteed trials); completers judged by **F-test**
    (significance decides; genuine ties go to the simpler form). **The
    admission null is autocorrelation-valid (A1, 2026-07-04)**: each round
    the residual's decorrelation length L is measured (lag-1 test at 1%,
    then the ACF's first in-band lag, capped so ≥20 blocks remain); L=1 →
    the iid shuffle exactly as before; L>1 → circular moving-block
    permutation, preserving the data's texture and destroying only
    candidate↔residual alignment. The sunspot-runaway condition now stops
    at 0 terms with NO RULE (0/5 false laws across seeds; battery
    `experiments/blockperm_battery.py` 10/10). `max_terms=16` stays as a
    backstop only.
  - **half held out**: the rule must WORK, not merely fit.
  - **verdicts**: `UNDERSTOOD` (R² ≥ .9 held-out) / `PARTIAL` / `CAPTURED`
    (nearest-exemplar beats permuted null — incl. per-feature 1-D
    fallback; caught, not said; no nets) / `NO RULE` (0/20 false
    discoveries on the battery's pure-noise trials, re-verified
    2026-07-03). Since 2026-07-03 a real partial equation is stored even
    when the headline verdict is CAPTURED (previously it was discarded —
    the CAPTURED-erases-law bug), and the capture null replays the same
    max-over-candidate-neighbor-sets contest the real score won (it
    previously permuted only under the winner — anti-conservative).
  - **THE ACCOUNTING (audit 2.8, added 2026-07-03)** — every discover()
    returns `accounting`: **articulated% + captured% + noise% = 100**.
    Articulated = held-out R² of the kept equation; captured = what
    exemplars additionally predict ON THE RESIDUAL past a permuted null;
    noise = the remainder that beat nothing — proven noise **at this
    expressive class**, never absolutely. Self-test (g): planted law with
    a known 26.5% noise share → measured articulated 72.7% vs true 73.5%.
  - **residual dossier** — when >5% is unexplained, the unknown becomes a
    first-class object: `dossier` = name (`x:<challenge>`), share %,
    how much of it is captured, top responsive channels (|corr| ranked),
    RMS and edge-RMS. Stored on the law node meta and in the ledger —
    can't say what it is; can characterize how it behaves; track it.
    (Level-indexed accounting — residual at level N handed to level N+1 —
    is still open; this is the flat level.)
  - **scope**: `form-true` (edges of observed range hold) vs `range-valid`
    (usable inside; never silently swapped). Both are knowledge.
    **Calibration, measured (2026-07-03, 100-world external audit):** the
    label is right 68% of the time when it says form-true — the edge
    check can only test edges that were observed. Superseded in practice
    by graded belief (below); the label remains as the coarse summary.
- `law_confidence(name, X)` — **graded belief instead of a binary stamp**
  (owner's design: "maybe just a boundary confidence? what about
  extrapolated confidence?"). Per query point: inside the observed hull →
  the law's boundary confidence (held-out edge R²); beyond it → boundary
  confidence × the **measured survival curve** of extrapolating claims
  (76% at the boundary → 59% at +0.1 spans → 45% at +0.3 → 37% at +1.0;
  measured on 51 externally-graded laws, validated on 52 FRESH ones:
  ECE 0.070, Brier 0.249 vs flat-baseline 0.288 — the curve is what
  actually happened, not an opinion). Curve provenance lives on
  `Isaac.DECAY_MEASURED`; re-measure via
  `experiments/confidence_curve.py` whenever the enumerator changes
  (done 2026-07-04 after the block null joined: unchanged within noise,
  far point 0.373→0.353; ECE 0.079, Brier 0.255 vs flat 0.284).
  Law nodes now also store per-feature observed `ranges` + `r2_edge`.
  - **rivals**: classic look-alikes (linear/quadratic/cubic/sin/cos/
    exp±) swapped in per single-feature term, F-tested; survivors stay
    LIVE on the law with a **probe** — the input where the tied forms
    diverge (usually outside the observed range).
- `confirm(name, X, y)` — new evidence retires rivals (CONFIRMED) or
  **OVERTURNS** and rewrites the law. (Pendulum demo: parabola chosen on
  ±1.2, cosine tie declared, probe "x≈3", overturned on the wide view.)
  Since 2026-07-03: an **absolute-fit guard** — a law whose fit collapses
  on the new data (R² < 0.2) is **REFUTED**, not CONFIRMED-by-default,
  even with no live rivals.
- `apply_law(name, X)` — a law is reusable computation. (Kepler, learned
  from 8 planets, predicted Pluto: 248.0 vs 247.9 — beyond training range,
  across a session boundary.)
- `validate_law(name, X, y)` — added 2026-07-03: re-validate a (possibly
  ledger-inherited) law on new evidence → HOLDS / DEGRADED / FAILS,
  recorded in the ledger. apply_law itself checks only shape; call this
  before trusting an inherited law.
- **`capture_net(name, X, y)` / `graduate(name, X=, y=)` — the stopgap
  that exists to be destroyed** (audit 2.8's closing loop, 2026-07-04).
  THE NO-NETS LAW HOLDS: the tiny numpy net (1 tanh layer) is never the
  deliverable — it is quarantined on the unknown's node `x:<name>`, it
  counts ONLY past a permuted-output null that replays the whole training
  contest (a noise-net stores NOTHING — verified), and its purpose is the
  distillation attack: `graduate()` queries the net as a free oracle
  (answers carry the net's own held-out residual as noise — its honest
  uncertainty), runs discover() on the answers, and prunes the result
  **against the original data** so terms serving the net's private warp
  die at F-ties while terms serving the truth survive. Battery
  (`experiments/capture_graduation.py`): planted x0·x1−x2 captured at
  0.984 → graduated to `+1.00*x0*x1 −1.00*x2` exactly (R² 1.000 vs
  truth); out-of-class sin(3·x0·x1) captured and HONESTLY not graduated;
  noise net failed its null, nothing stored.
- **`interrogate(name)` / `graduate_composite(name, X, y)` — enumerate
  what a capture is detecting** (owner, 2026-07-04: "define the heuristic
  connections... they can at least point in the direction — 'this is a
  pattern' as a deliverable"). The captured net is queried as an object
  of study; every claim is gated: **drivers** (permutation importance),
  **joint action** (2-D ANOVA interaction share), **composite
  dependence** (level-set invariance through xi*xj / xi+xj / xi−xj,
  judged against random-direction level sets — the matched null), and
  **shape along the composite** (monotone / peaked / periodic + a
  frequency estimate). Output is English sentences stored on x:<name>
  and in the ledger — a deliverable even when the law is out of reach.
  THE CLOSING MOVE: `graduate_composite` re-discovers in the composite
  coordinate Isaac himself identified — battery: the stuck
  sin(3·x0·x1) capture delivered "flows through the product ONLY,
  periodic ~2.5 rad/unit" and then graduated to
  **`+1.00*sin(3*(x1*x0))` exactly**; additive control invented nothing;
  (x0+x1)² found the sum and graduated exactly.
- **Combinations are THINGS** (owner, 2026-07-04: "it's combinatorial...
  memorize and reuse those combinations — a topological venn diagram, a
  dimensionless structure"). `register_composite(op, features)` mints a
  first-class node `comb:(x0*x1)` — distinct from its parts and from
  every other combination — auto-minted by interrogation when a composite
  beats its null, persisted through the ledger, and **offered to every
  future discover() as a column**, so all atoms (sin/cos/exp/pow) act on
  learned combinations. apply_law / confirm / law_confidence / refine all
  speak raw coordinates outside and augmented inside. Battery
  (`experiments/composite_reuse_battery.py` 4/4): the canonical unsayable
  sin(3·x0·x1)+0.5·x2 is PARTIAL (0.80) cold — after learning (x0*x1)
  from a DIFFERENT easy problem it is UNDERSTOOD **`+1.00*sin(3*(x0*x1))
  +0.50*x2` exact**, including in a fresh Isaac that inherited the
  combination through the ledger. The vocabulary grows with experience.
- **COLLECTIVE signals — signed, gated, minted** (owner, 2026-07-04:
  "a strong significant collective signal, but a weak individual signal";
  "darkening vs brightening" — deltas are SIGNED, both directions,
  always). interrogate() shifts all drivers TOGETHER vs one at a time vs
  the matched null (same-size shifts with scrambled signs — coherence
  broken, perturbation kept). A certified common mode is reported with
  both signed responses and minted as a collective coordinate
  `mean(x0,...)` — an arity-N composite the registry reuses. Battery
  (`experiments/collective_battery.py` 4/4): 8 faint columns → "move
  TOGETHER, +3.82 up / −3.34 down, 6.1× any single, beats scrambled";
  −2·mean reported as DARKENING; mixed-sign group correctly refused;
  and the minted collective made cos(3·mean(x0..x7)) — CAPTURED 0.38
  cold — **UNDERSTOOD `+1.00*cos(3*mean(x0..x7))` exact**.
- **`adequacy` (in every discover() result)** — data too weak to
  interpret is a DIAGNOSIS, not a shrug: names the cause with evidence —
  sample below onset (attaches as "provisional" even to successes),
  no responsive channel (missing-variable shadow), expressive-class
  limit ("structure IS present but no equation in the library says it"),
  nothing-beats-chance, or range-too-narrow (live rivals + probes).
- `refine(name, X, y, ask=, budget=, rounds=)` — **THE CORRECTION LOOP**
  (owner's design, 2026-07-03: the confidence indicator becomes a
  steering signal). Each round: (1) fan candidate probes past the hull
  and let `law_confidence` pick the WEAKEST region; (2) spend budget
  asking the instrument (`ask(X)->y`; non-finite answers discarded);
  (3) re-derive on everything known; (4) **Occam as a preference, not a
  gate** ("its not only. its just preferred"): accuracy decides by
  F-test; at ties the simpler form is preferred for use; a candidate
  that is not preferred is RETAINED on the law's `alternatives` list
  with the why — nothing is rejected into nothing; (5) the displaced law
  is SUPERSEDED with the why, never erased. Ends with an Occam prune
  (`_prune_terms`: greedily drop terms that survive an F-tie on held-out
  data). **Measured** (`experiments/refinement_audit.py`, 100-world
  deck): beyond-range hold 50% → **75%** with mean terms flat (2.8) and
  47 terms pruned; known trade: inside-range hold eased 99% → 94% (the
  refit weighs the new frontier; a strict interior-preservation gate is
  a queued option).
- **Cross-domain** (harness `experiments/cross_domain.py` — [HARNESS-ONLY
  — experiments/, not wired into engine]; re-run 2026-07-03 from this
  repo: cold 0.82 → primed 0.995 reproduced): laws
  matched by structure via log-track exponents (power laws are linear in
  log-log); families become abstraction nodes (`instance_of` facts);
  **analogy-primed transfer** solves data-starved domains (magnetism n=24:
  cold 0.82 → primed 0.995). Log-track inside `discover()` is a queued
  engine item.
- Known limits (battery + red team, all documented): wrong-form risk at
  n < ~400 (provisional rule); frequency reach ≈ 2× grid max for
  non-periodic scales (periodic scales now reachable by the phase-fold
  proposal — grid RESOLUTION over long windows was measured 2026-07-04,
  unmasked by the block null, and CURED the same day by folding);
  nested nonlinearities land in CAPTURED by design; rational functions
  admit usable trig surrogates (range-valid).

## 8. Memory that outlives the process — [VERIFIED IN ENGINE SELF-TEST 11/11]

- **Findings ledger** — `record_finding` fires automatically on every
  discover (laws AND verdicts — negative knowledge included), confirm
  (confirmations/overturns), and wave consolidation. One JSON line each:
  verdict, equation, scope, rivals+probes, provenance, full model for laws.
  `recall_findings(kind=, contains=)` searches; `load_ledger(path)`
  rehydrates a previous session's laws as APPLICABLE. Set `ledger_path`
  to persist (UI uses `data/findings.jsonl`).
- **Whole-mind persistence** — `save(path)` / `Isaac.load(path)`: the
  entire mind, one small file. `fork()`: deep-copy branch for
  counterfactual experiments (teach the fork; the original is untouched).
- The distinction is deliberate: **the snapshot preserves a mind; the
  ledger preserves knowledge.** Minds are cheap to fork and discard;
  knowledge accumulates across all of them.

## 9. The UI (`ui/isaac_ui.py`) — [VERIFIED 2026-07-03 — re-run from this repo] (server starts and serves on 127.0.0.1:8674)

One stdlib file. Panels: **Mind** (save/load/new/fork; laws held),
**Converse** (teach s-r-o; observe; ask — `cat is_a ?` or next-token),
**Discover** (paste CSV → verdict card: equation, R², edge, scope, rivals
with probes; apply any law to new rows), **Remember** (ledger search).
Server binds 127.0.0.1:8674; minds stored in `data/minds/`; the findings
ledger at `data/findings.jsonl`.

## 10. Test map (what proves what)

- Engine self-test (11 areas): language, math, logic, reasoning, decompose,
  persistence, waves, tracking, discovery, rivalry, spatial.
- Harness (`experiments/`): six rebuild proofs (doors, composition,
  enumerator, waves, interference, entity-status); batteries with per-run
  CSVs (`wave_battery`, `discovery_battery`); adversarial
  `redteam_discovery`; `sense_battery` (senses-as-nodes, 14 checks);
  real-data (`covtype_*`, `higgs_real_test`,
  `experiments/gauntlet.py` — 10 datasets, one pipeline);
  `experiments/cross_domain.py`; `condensation_scaling`;
  `experiments/clock_world.py`; `registration_perception`;
  `ideals_differentia`; `digits_structural`. Run logs from this repo:
  `experiments/runs/2026-07-03/`.
- Reports: `experiments/RESULTS.md`, `experiments/WAVE_TEST_REPORT.md`,
  `docs/WRITEUP_FOR_REVIEW.md` (§7 = verify-everything commands).

## 11. Current honest scoreboard — [VERIFIED 2026-07-04 — full gauntlet re-run from this repo with the upgraded stack] (log: `experiments/runs/2026-07-04/gauntlet_rerun.txt`)

Every recorded number REPRODUCED, two improved:
- **Kepler: UNDERSTOOD `+1.00*x0^1.5` EXACT from n=8** — the gauntlet's
  own note still says "PREDICTED FAIL (a^1.5 inexpressible)"; the one
  dial (λ=1.5 in the power family, 2026-07-04) made it expressible.
- **Sunspots: honest NO RULE in 2 seconds** — the dataset that caused
  the 20-CPU-hour runaway now terminates instantly under the block-perm
  null with no false law (quasi-periodic: folding correctly refuses a
  fixed period).
- Covtype articulated: flat engine doors 57.0% (bins=12) / **59.1%
  (bins=32)** — reaches the harness's augmented number flat; compound
  keep-guard correctly REFUSES compounds here (held-out drops: binary
  indicator columns bin badly under the quantile log-density model — a
  known-why on the checklist, not a silent regression). Captured
  door-weighted 95.3% remains RECORDED-only; honest number stays the
  articulated tier (row-index leakage 94.8%).
- Commodity-or-below, unchanged (the D8/phase-4 perception wall, as
  predicted): MNIST 95.2 exemplar / 86.5 doors; Fashion 76.5/69.3;
  CIFAR 32.6/26.9 (designed face-plant); Omniglot 1-shot 51.6;
  smallNORB 87.7/40.1 (viewpoint unhandled); FSDD 92 mixed → 54
  speaker-transfer; fraud minority recall 79% (accuracy is majority
  theater there); clocks 22.9% (known harness readout bug, D8).

Differentiated (the product, unchanged): verdicts + scope + rivals +
probes + accounting + graded confidence + cross-session inheritance —
honesty machinery wrapped around discovery, on a CPU, readable end to
end. The strengths are the discovery stack; the wall is pixel-level
perception — exactly where the checklist points next (D8, D9).

## 12. What does NOT exist yet (so nobody assumes it)

> The complete audited inventory — every limitation, stopgap, and gap with
> evidence and attack order — lives in `docs/STRUCTURAL_DEBT_CHECKLIST.md`
> (2026-07-04). This section stays as the quick list.

No abstention in classify_features; no FCA lattice (overlap merging); no
shrug→discover reflex; no symbolic/token
challenges in discover(); no
learned-invariant perception (phase 4); no curiosity — challenges arrive
from outside, and the probe queue is proposals only. The clock-reading
harness readout is broken (22.9% — harness bug, engine unimplicated).
(Closed 2026-07-04 and no longer on this list: block-permutation null,
compound doors + trigger, uptake composition — see the checklist.)


## Persistence v2 — packs, journal, orchestrator (2026-07-11)
The infrastructure arc's storage layer, at `isaac_store/` next to the
engine (plain files + stdlib only; NO pickle for new saves, NO database
— owner constraint).
- `mind.save_pack(directory)` / `Isaac.load_pack(directory, version=None)`
  — the whole mind as an immutable, versioned, indexed pack file.
  A new save SUPERSEDES (v2 beside v1), never overwrites. Old pickle
  `save()/load()` still work; migration proven.
- Partial loading is a property of the format: `PackReader` opens
  header+index only, then fetches single node records by seek —
  measured 100k-node mind: index open 28 ms, one node 0.04 ms vs
  5.3 s full load (133,000x).
- `isaac_store.Orchestrator` — sole-writer edit queue behind an
  admission gate; rejections wrong-kept with why; RECOVERY INVARIANT
  battery-proven: latest pack + journal tail == live state.
- Battery: `isaac_store/test_store.py` = 29/29 (codec/journal/pack/
  orchestrator/real-mind round-trip/pickle migration/engine-native);
  engine suite 11/11 after wiring.
- Measured cost, stated plainly (`scale_test.py`, synthetic 100k
  nodes/500k doors): pack 141.5 MB vs pickle 27.1 MB (5.2x — the price
  of readable typed records), save 10.1 s vs 0.5 s, full load 5.3 s vs
  0.4 s. Compaction is background so the times are acceptable; the 5x
  size is the known next lever (per-record compression) — not
  optimized yet, per no-optimizing-before-measured-limits.

**LiveCache (Worker read side, 2026-07-11):** `isaac_store.LiveCache`
— workers live-load node records from Prime's packs, serve from local
cache, recheck FIXED at 30 min (owner-settled; recheck = journal-tail
delta, only touched keys invalidated; adopts newer packs). `with
cache.job():` pins one consistent view per job — an overdue recheck
waits for the job boundary. Staleness cannot corrupt: proposals are
judged at the admission gate (battery H6: stale proposal rejected +
wrong-kept). Battery `isaac_store/test_cache.py` = 13/13.

**LeafIsaac (the security-net worker, 2026-07-11):**
`isaac_store.LeafIsaac` — the all-in-one Isaac at the leaf tier
(Prime -> client overlay -> leaf). pull(node) = layered read, local
wins; shared nodes GRAFT into the local net with origin tags; private
evidence doors onto them locally. NO upstream channel by construction
(no orchestrator reference exists in a leaf). Modes: "ephemeral"
(RAM-only, save() refuses) / "user-held" (packs only under the user's
directory; resumes across sessions; encryption-at-rest = open item,
needs a vetted crypto library — owner's call on the dependency).
Battery `isaac_store/test_leaf.py` = 13/13, headline = the QUARANTINE
PROOF: full private teach/observe/answer cycle with a planted secret,
then a byte-scan of every file outside the user's directory — zero
hits (ephemeral mode: zero hits on ANY disk).

**PrimeServer (the between-programs doorway, 2026-07-12):**
`isaac_store.PrimeServer` — Prime's orchestrator served over HTTP
(stdlib only) so Workers/Scrubbers/front-ends run as separate
programs. Endpoints: GET /api/watermark (cheap recheck), /api/journal
?since=N (delta), /api/record?key= (single-record live pull); POST
/api/submit (queued edit -> admission -> verdict returned),
/api/compact. Contract: REFUSALS ARE ANSWERS — rejections and misses
are HTTP 200 with ok:false + why (wrong-kept in the journal); 400/401
only for malformed/unauthed; no stack traces leave the process.
Security defaults: binds 127.0.0.1 only; optional bearer token
(mandatory before any non-localhost bind); access log = method+path
only, never query strings or content (the Identity Law applied to
logging). Wire format = the codec's JSON (tuples/sets/arrays survive).
Battery `isaac_store/test_server.py` = 17/17. All four store
batteries: 29+13+13+17 = 72/72.

**Scrubber (the Identity Law, enforced, 2026-07-12):**
`isaac_store.scrubber` — `scrub(payload, deny_list)` strips
identifiable info (email/ssn/phone/card/ip/address/honorific-names +
customer deny_list) to category placeholders, keeps the abstraction
byte-identical, reports categories+counts only (the report cannot
leak); REFUSES when identity is load-bearing (in keys/node names).
`identity_gate(inner)` = Prime's admission backstop: identity-shaped
edits refused outright (the gate judges, never cleans), wrong-kept
with categories not content; wraps any inner gate. Honest scope:
best-effort pattern classes — the structural quarantine underneath
does not depend on scrubber perfection. Battery
`isaac_store/test_scrubber.py` = 19/19; promotion gates now include
it (engine + 5 batteries = 91 checks + 11/11).

**Skills — roles are loadouts (owner, 2026-07-12):** every worker IS
Prime with a checkbox of skills loaded. A skill = a plain record in
Prime's net (`skill:<name>`: learned things + preloaded structures),
published through the normal queue (`isaac_store.publish_skill`) and
pulled by workers like any node (`pull_skill(cache, name)` — same
LiveCache, same 30-min recheck, same job pinning, same HTTP doorway).
The scrubber is the first skill: its module patterns are only the
SEED (`seed_skill()`); `scrub(payload, vocabulary=<pulled record>)`
runs on Prime's living vocabulary, so educating Prime re-equips every
worker at its next recheck. Battery `isaac_store/test_skills.py` =
7/7. Promotion gates: engine + 7 batteries = 107/107.

**Ops + the alpha launcher (2026-07-12):** `isaac_store.OpsLedger` —
the ledger organ applied to operations: process/compact/http events
with counts, sizes, timings appended to ops.jsonl. CONTENT-FREE BY
CONSTRUCTION (Identity Law): the ledger refuses long strings and
structured values at write time; http events carry method+path (no
query)+status+ms. `alpha.py` (repo root) = the alpha live launcher:
`python alpha.py` boots Prime as a service (orchestrator + identity
gate + doorway + ops) from a persistent data dir; first boot educates
Prime with the seed scrubber skill; restart resumes via the recovery
invariant; non-localhost bind REFUSED without a token; Ctrl+C
compacts a final pack. Battery `isaac_store/test_ops.py` = 13/13
(incl. leak-channel proof: PII driven through HTTP appears in zero
ops/journal bytes). Promotion gates: engine + 8 batteries = 120/120.

**Multicore (2026-07-12): the orchestrator/worker design at full
purpose.** `worker.py` (repo root) = a Worker as a separate OS
process: pulls jobs from Prime over the doorway, claims them
optimistically (`"expect": <the open record>` — queue order
arbitrates races, no locks anywhere; the orchestrator now enforces
expect natively), computes with the engine on its own core, submits
results back through the queue (numpy rides the `_encoded` codec
envelope — server-side decode-then-validate fixed). Measured
(test_multicore.py, 7/7): 8 discover-jobs, 1 worker 10.1 s vs 4
workers 3.5 s = **2.90x**, all 4 processes participated, 8/8 laws
exact, zero double-claims. Prime's write path stays single-writer by
design — edits are milliseconds; COMPUTE is what fans out. Promotion
gates: engine + 9 batteries.

**Told knowledge = supersession test candidate (owner design,
2026-07-12):** `tell_law(name, equation, d=)` — direct equations in
Isaac's canonical vocabulary (x0, x0^k, log, sin/cos(k*x),
exp(k*x), sin/cos/cosh(k*(xi-xj)); unparseable factors refused
loudly). Match check FIRST: same-form submission = confirming
WITNESS on the existing law, never a duplicate node. New forms enter
TOLD-UNVERIFIED: apply_law works immediately, but law_confidence
stays None — belief is measured, never told. `supersession_duel(
name, X, y)`: told law vs fresh discovery, judged on a held-out
quarter; CONFIRMED = belief earned (ranges + edge-r2 from the data),
SUPERSEDED = told law kept wearing its defeat (why + numbers),
losing challengers file into rivals. Retention = the ordinary pack
road (proven: save_pack/load_pack preserves law + status). Battery
`experiments/told_knowledge_battery.py` = 13/13 (incl. round-trip:
Isaac parses his own printed equations). Suite 11/11. Promotion
gates: engine + 10 batteries.

**Told RULES — generation, not duplication (owner design + owner
correction, 2026-07-12):** "he didnt learn it. you fed him a pattern
and he had to mimic it. thats not generation, thats duplication...
what i want is to say if its a 3 say fizz... i want him to be able to
understand that kind of thing." `tell_rule(name, clauses)` — clauses
= `{'when': {'multiple_of': [ints]}, 'say': token}` with `'say':
'__number__'` speaking the prompt itself and a bare `when: {}` as the
base case; unknown condition words refused loudly at tell time.
`respond_by_rule(name, n)` / `generate_by_rule(name, upto)`:
GENERATION from the told understanding, zero examples seen —
precedence is Isaac's own general logic (the MOST SPECIFIC satisfied
clause wins; clause ORDER is proven irrelevant; an equal-specificity
disagreement REFUSES with the why). `validate_rule(name, prompts,
responses)`: belief only from data — told-unverified → validated
(complete match count) or CONTRADICTED with the first disagreements
kept. Rules persist through the ledger. The EXAMPLE road —
`learn_responses(prompts, responses)` + `respond(prompt)` — is
DEMOTED to duel partner / fallback-when-untold (wrong-kept): it
learns echo (his compare primitive), differentiates classes from
observed tokens, discovers when each fires (own nulls), abstains
when nothing is admitted, and REFUSES random-exception worlds; a
discovered class firing exactly on multiples of P READS AS "every
Pth" (the bridge: both roads, one divisibility concept). Proof
standard held: the engine contains no task words (grep-proven);
foreign worlds (period-7 echo world 70/70, a 4/9/36 composed world
85/90) solved by the same untouched organ. THE HEADLINE, complete
numbers: told rule generates the stream 100/100 on 1..100 and
100/100 on n=301..400; example road 100/100 on n=301..400 (all
learned laws UNDERSTOOD). Batteries: `rule_battery.py` 11/11 +
`task_battery.py` 8/8. Promotion gates: engine + 28 batteries.

**Taught rounding (owner design, 2026-07-12):** "i think we just
need to teach it rounding actually. if its 3.0018463 then its
probably tested to 3. if its 1.764964 then it may be 1.75 etc." A
measured constant's roundings are hypotheses tested OUTRIGHT:
`_round_candidates` builds the ladder of natural ruler marks ({1,
1/2, 1/4} × powers of ten, coarsest first — 1.75 IS a mark);
`_round_terms` runs at fit end on every admitted term's
inside-parameter with the TRIAL REFIT as referee — the simplest mark
that does not lose is what the law says; all marks losing = the
measured digits stand (no invented simplicity, no lost precision).
Strictly POST-HOC: rounding at proposal time was measured wrong ×2
(the fold referee cannot resolve marks inside its bin width; a lucky
adoption smeared planted 1.75 into [1.7525, 1.7]) — wrong-kept in
the engine comments. Battery `experiments/rounding_battery.py`
**7/7**: sin(1.5x) SAYS 1.5; sin(1.75x) SAYS 1.75; exp(-0.4x) SAYS
0.4; sin(πx) keeps its digits (3.14 — refuses the coarse marks);
pure noise still NO RULE. Promotion gates: engine + 29 batteries.

**Law families + which_law (2026-07-12):** overlapping-confusion
machinery. tell_law now compares CONSTANTS on a form match (5%
relative): same form + same constants = witness; different constants
= VARIANT doored under a `lawform:` family parent (Earth/Jupiter/
Pluto gravity stay distinct — hierarchy, never smushed).
`which_law(X, y)` scores every candidate law on the data and answers
rank + veto + abstention: MATCH (clear winner), AMBIGUOUS
(shortlist), NONE = new-variant candidate (mixed-planet data refuses
a single answer; unknown planet abstains until told/discovered).
Battery `experiments/gravity_family_battery.py` = 13/13. Promotion
gates: engine + 11 batteries.

**The Provenance Gate + recreation check (owner design, 2026-07-12):**
shareability is ANCESTRY, not appearance. Every leaf node carries
source tiers (prime/client/user/public; FAIL-CLOSED: unknown =
user). `leaf.exportable(node)`: closure within {prime, public} =
game; ANY user tier = banned FROM EXPORT (never from local use).
`share_candidate(law)` = first defense on the share path (before
the scrubber): record released only on GAME, verdict filed either
way. `recreation_check(law)` (owner: "see if it can recreate the
information from public sources too"): attempts the rebuild from
prime/client-held knowledge alone — a form+constants match means
the user data was NOT necessary, provenance upgrades, export
unlocks; no match, ban stands. Defense order: Provenance Gate ->
scrubber -> Prime identity_gate. Battery
`isaac_store/test_provenance.py` = 13/13 (incl. literal
reconstruction: a prime-only leaf rebuilds the identical law).
Promotion gates: engine + 12 batteries.

**Seeker — the one-question search worker (owner design, 2026-07-12):**
`isaac_store.seeker.Seeker(search_provider)` — "acts like a search
agent... quick web crawl for a few sources, chews, gives its best
answer." Lifetime = ONE task (no-curiosity law intact; it has no
task queue and no way to add to one). DEPTH ZERO: fetches exactly
the search results; links inside pages are never followed (battery
plants 20 bait links per page — zero requested). Budgets physical:
max sources/bytes/time in the task; exhaustion = clean stop. Chew
v1 = cross-source corroboration for numeric questions: values
clustered at 2%, an ANSWER needs >=2 sources AND a majority;
otherwise AMBIGUOUS/NONE refusals with the dossier (dissent is
reported, never hidden). Receipts on everything (url + content
hash); answers are PUBLIC-tier provenance, Provenance-Gate ready.
Search backend pluggable — real-web provider is an owner dependency
call; batteries run a local mock web. Battery
`isaac_store/test_seeker.py` = 11/11. Promotion gates: engine + 13
batteries.

**Restore-point cache (owner design, 2026-07-12):** per-customer
retention. DEFAULT: keep the newest **3 supersession layers** (pack
snapshots) + the journal tail spanning them — 3 restore points,
bounded storage; journal events older than the oldest kept snapshot
are trimmed (recovery invariant proven intact on the trimmed
journal). OPTION: full log (retention_keep=None) — nothing ever
pruned. `orchestrator.restore(v)` rewinds to a kept snapshot as an
APPENDED journal event (history is never rewritten; cold-start
replays THROUGH the restore correctly). Measured: keep-3 224 KB vs
full-log 378 KB on the same 6-generation run. Prunes are content-
free ops events. Battery `isaac_store/test_retention.py` = 10/10.
Promotion gates: engine + 14 batteries.

**The Honest Report — how people use Isaac (owner MVP, built
2026-07-12):** `python askisaac.py data.csv [--target col]` — drop a
CSV, get the report: VERDICT FIRST (refusals are real answers with a
diagnosis), the equation IN THE USER'S COLUMN NAMES ("energy =
+3.00*alpha*beta +1.00*alpha*alpha"), complete numbers (r2, held-out
edge, rows), calibrated confidence with its calibration note, the
accounting when present, live rivals with their settling probes, a
NEXT-EXPERIMENT suggestion, and a provenance appendix (rows, cols,
data hash, engine, date — every report traceable). Module:
`isaac_store.report` (load_csv/challenge/render_text). Battery
`isaac_store/test_report.py` = 11/11 (noise -> NO RULE refusal
report, never a fake equation). Promotion gates: engine + 15
batteries.

**Native gated English — road 2 v1 (2026-07-12):**
`isaac_store.speech.speak(report)` — Isaac REALIZES structure as
speech: every sentence produced from a report field by a fixed
compositional realizer (verdict framing first; terms spoken from
the MODEL dict in the user's column names — "mainly, alpha times
beta raises it (weight 3.00); also, the square of alpha..."; atom
vocabulary: wave/logarithm/square/root/decay/alignment-between/
gap-between; complete numbers; refusals spoken with the same
directness). Faithfulness BY CONSTRUCTION plus verify_faithful() as
the null: every number spoken must exist in the report — a tampered
response fails (proven). Gated omission: missing fields are never
spoken. `askisaac.py --speak` prints the response with the full
report attached beneath as ground truth. Battery
`isaac_store/test_speech.py` = 20/20. LLM-mouth (road 1) stays the
fallback design if native speech hits its ceiling. Promotion gates:
engine + 16 batteries.

**LEARNED SPEECH — the correction applied (owner, 2026-07-12: "its
all or nothing. you dont get to choose. that is called programming
and thats not what isaac is about"):** speech.py (template realizer)
DEMOTED to deprecated scaffold — it is programming, not speech.
`isaac_store.speech_learn` is the real road 2: Isaac LEARNS wording
from paired examples (`speech_corpus.txt` = the teacher's data;
format "features|sentence with PLACEHOLDERS"). learn_speech() admits
a fragment for a feature only past a permutation null vs the rest of
the corpus (placeholder-only fragments inadmissible — a slot is not
a word); fragments live IN THE NET (speech:<feature> meta — persist
via packs, supersedable). speak_learned() = ALL OR NOTHING: untaught
atom = silence + listed unspoken; untaught verdict = cannot speak,
fall back to the report. PROOF STANDARD (battery 20/20): the grep
proof (spoken words absent from code — even a code comment got
caught), corpus swap changes the words, withheld lessons produce
silence, retention across save/load, faithfulness null on numbers.
`askisaac --speak` uses learned speech only. Promotion gates: engine
+ 18 batteries.
**The admission null hardened at corpus scale (2026-07-12, dialogue
probe):** feeding 4,000 real conversation pairs (DailyDialog)
through learn_speech, the probe's scrambled-pairing CONTROL caught
the per-gram null false-admitting 119/120 features (selection
correction missing — hundreds of candidates each at a 5% pass rate;
tiny teaching corpora never tripped it). A raw-count max-null then
over-corrected (universal grams saturate the gate; the
fit/confidence lesson went silent). Settled: **EXCESS over base
rate, selection-corrected by the max-over-candidates null** —
battery 20/20 restored, dialogue control calibrated (8 admissions on
scrambled ≈ the nominal rate). First real-conversation learnings
(dialogue_probe.py, 45 admitted): pronoun MIRRORING (did/why/did
you → 'i'; am/i think/i have → 'you'), topic persistence
(he → he), questions/thanks draw statements back; held-out replies
198/400 answered, 202/400 honest silence. Corpora at data/dialogue/
(git-ignored, refetch README) — public-tier provenance.

**The Face (2026-07-12):** `python face.py` -> http://127.0.0.1:8676
— the alpha's web door: drop or paste a CSV in a browser, Isaac
answers with LEARNED SPEECH (when taught) and the honest report
always attached. Separate from PrimeServer by design (heavy
per-request discover work never blocks the orchestrator's doorway).
Door laws enforced: 20 MB upload cap checked BEFORE the body is
read (413), garbage gets a clean why (400, no stack traces),
refusals arrive as 200 answers with the refusal spoken, access log
is method+path only (no query strings, no content). Stdlib only,
localhost only. Battery `isaac_store/test_face.py` = 7/7. Promotion
gates: engine + 19 batteries.

**Intake — every format through one door (owner ask, 2026-07-12:
"file formats and data converters... direct files, folders, zips,
raw text and rich text"):** `isaac_store.intake.ingest(source)` —
csv/tsv/json/jsonl/npy/npz/xlsx -> numeric tables (headers detected,
non-numeric columns dropped AND ACCOUNTED); txt/md/log/html/rtf/docx
-> text (docx and xlsx parsed as what they are: zips of XML, stdlib
only); folders recursed; zips walked in memory with the zip-bomb
guard (per-entry byte cap, file-count and total-byte budgets); raw
text auto-dispatched (delimited numbers -> table, prose -> text).
Everything unsupported or over budget is SKIPPED WITH ITS WHY —
never silent. Every item carries provenance (source/sha/bytes).
`table_csv(item)` feeds report.challenge() directly; askisaac.py now
accepts any source (multi-table folders/zips report each table).
Battery `isaac_store/test_intake.py` = 19/19. Promotion gates:
engine + 20 batteries.

**Multicycle structural patterning (owner design, 2026-07-12):**
`isaac_store.structural.analyze(x)` — the flow-logic road: atoms ->
constraint families each behind its own admission rule
(always-follows links via shuffle null; forks via family gate +
per-fork null; EXACT periodicity, chance-proof by construction;
balanced pairs requiring >=3 DEEP nesting episodes — the ballot
problem cannot fake repeated depth; certified never-follows only
where chance says the pair should have touched) -> the pattern type
that satisfies the admitted set (CHAIN / CYCLE / BRANCH / HIERARCHY
/ REPEAT / NO STRUCTURE as an honest refusal) + the chart itself
("check -> {fail | pass}"). MULTICYCLE: admitted chains COLLAPSE
into higher atoms and the cycle reruns — the tower (level 1 finds
the motifs, level 2 finds their rhythm). Text mode: rare tokens
become the <slot> atom, so templates emerge without memorizing
names ("open -> the ; the -> file ; file -> <slot>"). Noise: 0/10
false structures. askisaac now reads text items' structure. Battery
`isaac_store/test_structural.py` = 12/12. Promotion gates: engine +
21 batteries.

**Remote workers (2026-07-12):** `isaac_store.RemoteCache(url,
token=)` — the Worker read side over the HTTP doorway: same contract
as LiveCache (get / 30-min recheck as a journal delta / job pinning
/ keys()), but Prime lives across the wire — workers and whole
LEAVES can run on a different machine (`LeafIsaac(prime_url=...,
token=...)`). PrimeServer gained /api/keys (prefix listing) so the
recreation check works remotely. Proven (test_remote.py 16/16):
codec-exact reads, delta rechecks dropping only touched keys,
pinning semantics identical, clean 401 refusals without a token, a
remote leaf grafting from Prime while Prime's journal shows ZERO
writes from it, skills equipping across the wire, and the
Provenance Gate recreation upgrade against a remote public record.
The client side is now location-independent. Promotion gates:
engine + 22 batteries.

**Triangulation — incomplete information across datasets (owner
design, built under carte blanche 2026-07-12):**
`isaac_store.triangulate(table_a, table_b)` — "both halves of the
same whole, not contained in any single domain," resolved. Two
roads: COMPLETION (A's missing variable is B's COLUMN: join on the
shared key, joint discovery; gain must beat the SCRAMBLED-PAIRING
null — battery: alone r2 0.000 -> joint 1.000, law said exactly);
HALVES (the latent lives in NEITHER: each side's articulated
residual is a different mixture of the same hidden pair; agreement
across the join, CONFIRMED independently in both halves of the data
each against its own null, unmixes them — battery: x recovered
r2 0.9915 and s r2 0.9866 from two datasets each holding only ~0.61
of x). Refusals: NO ALIGNMENT (no shared key / poor coverage), NO
CLOSURE (0 false closures; scrambled pairing recovers nothing).
KNOWN LIMIT, kept honestly (found by the battery itself):
equal-variance Gaussian latents in sum/difference mixtures are
unresolvable IN PRINCIPLE (the ICA identifiability limit) — the
refusal there is mathematically correct. Battery
`isaac_store/test_triangulate.py` = 11/11. Promotion gates: engine
+ 23 batteries.

**Scale + permanence hardening (owner audit question, 2026-07-12):**
three gaps closed before learning-at-scale. (1) LAZY PRIME: the
orchestrator no longer load_all()s — state = latest pack (seek on
demand) + journal overlay; compaction STREAMS record by record and
rebases; restore rebases. Prime bigger than RAM is now real: cold
start 9 ms at 20k records (vs 70 ms full read), one node 0.02 ms.
(2) PER-RECORD COMPRESSION (pack format v-z, default on, old packs
readable forever): each record zlib'd individually so the index
still seeks — real-mind pack 12 KB vs 147 KB (8%); at 100k
nodes/500k doors the pack fell 141.5 MB -> 30.3 MB (pickle parity,
partial fetch 0.054 ms retained; save 12 s = background compaction
cost, documented). (3) THE EDUCATION ROAD proven
(test_education.py 10/10): a WHOLE real mind through the queue into
Prime; cold-start lazy; single-node recall; the mind rebuilt FROM
PRIME answers identically (laws + facts); SESSION TWO grows the
same Prime and a third cold start holds old AND new — permanent
memory across sessions. Promotion gates: engine + 24 batteries.

**Mind crawlers — Prime federates (owner design, 2026-07-12):**
`isaac_store.MindCrawlers(dir, capacity)` — multiple orchestrators,
each owning a KEY RANGE. A section that outgrows capacity DIVIDES at
its median key into a new crawler; splits are journaled in
crawl.jsonl (the lineage wrong-kept: parent, boundary, records
moved) and a cold start rebuilds the exact federation from that log.
Each crawler is a full Orchestrator — its pack index is its PAGE
FILE, its lazy state does the DRIVE PULLS, its journal keeps its own
wrong; admission travels with the section (proven: a gated edit dies
in ITS OWN crawler's journal, even after splits). Specialization is
emergent from key locality (namespaced keys form CONTIGUOUS
territories — proven). Battery `isaac_store/test_crawlers.py` =
12/12 (1,400 records through repeated divisions, ZERO lost, every
value exact after cold start). Promotion gates: engine + 25
batteries.
