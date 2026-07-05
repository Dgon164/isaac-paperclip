# ISAAC — Current Build State

**The dated build ledger — history of what was built, when.**
Last savepoint: **2026-07-02** (path/count corrections 2026-07-03)

> **NOTE (2026-07-03):** this is a HISTORICAL ledger; dated entries keep the
> paths and expectations as they were at the time. In THIS repo the engine is
> `isaac.py` at the repo root, the harness is `experiments/`, and the self-test
> expects **11/11** (spatial joined 2026-07-03). For current verified state, read
> `experiments/RESULTS_LEDGER.md` and `docs/VERDICT_SHEET.md`; for the
> capability reference, `docs/ISAAC_MANUAL.md`.

> **Authoritative engine (2026-07-01, historical):** `isaac_project\code\isaac.py`
> (project root `code\`, NOT `2_the_machine\code\` — that copy is older). In this
> repo: `isaac.py` at root, byte-identical.

---

## 2026-07-05 — A RECORDED CLAIM OVERTURNED: the "detector equation" was a net

Audit triggered by the owner's dissatisfaction ("match extraction on
current record neural nets?"). The record carried "detector eqn: AUC
0.848 (2M) / ~0.88 full" from the 2026-06-28 era. Verified against the
surviving scripts (`equation_discovery/code/build_detector.py`,
`full_detector.py`): **both are trained torch MLPs** (256/512-wide, Adam,
dropout) whose output banners call the network "THE DETECTOR EQUATION —
~100k pinned constants." That is the 06-28 drift the no-nets law was
written against, preserved in the record wearing an equation costume.
The claim is OVERTURNED and kept here with its why (supersession law
applies to the RECORD too). Honest standing on HIGGS classification
within the laws: **doors AUC 0.729** (re-verified 2026-07-05, 500k
sample; compounds honestly refused — 0 conjunctions survived their
null). The deep-net benchmark ~0.885 is unmatched by ~0.156 AUC, and no
lawful road currently closes it. The lawful route to the number exists
but is different in kind: CAPTURE a record-grade net as a quarantined
stopgap, then interrogate/graduate — the accounting then names exactly
how much of the record is articulable. That is omega milestone 5, not a
benchmark chase.

## 2026-07-05 — HIGGS: THE CONTRAST AND THE BLIND SENSOR MAP

Owner: "it's got the answer sheet... find out what is different between
them? maybe... create a physical map of the sensors." Run:
`experiments/higgs_map.py` (log in runs/, 400k events sampled of 11M).
- **The contrast (labels used), physics-correct end to end**: top
  discriminators m_bb > m_wbb > m_wwbb (the Higgs decays to b-quark
  pairs — its mass peak IS the signal); **every phi channel
  indistinguishable** (the physics is rotation-symmetric — Isaac
  found azimuthal invariance from the answer sheet); **m_lv
  indistinguishable** (both signal and background contain a real
  W→lν — textbook). 17 of 28 channels differ past the
  selection-corrected null; signed directions reported.
- **The blind kinds map (labels never used): 28/28 correct.** All five
  phi channels → "angle (bounded, flat)"; all four b-tags → "counter
  (3 levels)"; etas → signed; pT/MET/masses → one-sided magnitudes.
- **The blind wiring**: derived-mass cluster correctly interlinked
  (m_wbb–m_wwbb MI 0.81), jets to composites, phi–phi coupling (angles
  relate only through differences), and j4_eta–j4_btag — a real
  detector-acceptance correlation.
- **The formula road (blind discover per derived channel)**: m_lv →
  **`+0.29*x0*x3 − 0.29*x0*x3*cos(1.7*(x2−x4))` = pT·MET·(1 −
  cos Δφ(lep,MET)) — THE TRANSVERSE-MASS FORMULA, said** (R² 0.856,
  correct wiring lepton+MET; short of UNDERSTOOD only because the
  stored channel is m not m²). m_bb/m_wbb/m_wwbb PARTIAL with the
  right channel families (jets+btags; lepton+MET+jets); m_jj/m_jjj
  failed (heavy-tailed squared targets; jet-pairing assumption) —
  recorded, not hidden.
- **New methods finding (filed as checklist A8)**: hill-climb
  refinement pushed a sine to k=1929 on a DISCRETE channel (btag) —
  a lookup-table surrogate wearing a trig costume. Refinement must be
  bounded by the grid's frequency reach / refuse scale-refinement on
  counter-kind channels.

## 2026-07-04 — LINES, RECTANGLES, RELATIONAL ROTATION (owner, same day)

"A slanted 8 is just two circles at 15 degrees, a 7 is a 25 degree 1 with
a second line on top." Battery `rotation_battery.py` **11/11**; shapes
11/11; wireframe 8/8; pattern3d 9/9; suite 11/11 after.
- **Identity vs pose, made operational**: every part carries rel_angle
  (identity, survives rotation); the glyph frame carries TILT (pose).
  Verified: the slanted 8 has the SAME relational description as the
  upright 8 plus "tilted -18°"; the rotated 7 keeps its joint angle
  (60°→61°) while its tilt moves (-18°→+8°).
- **Lines with corners**: skeleton strokes decompose by PEELING DIAMETER
  PATHS (BFS twice → longest path → Douglas–Peucker corner split →
  remove → repeat); joined lines relate by JOINT ANGLE. The 7: "two
  lines, joined at 60°". The 1: "one line".
- **Rectangles and squares**: round-vs-square is FILL in the region's own
  frame (ellipse π/4 vs rectangle ~1; discrete cut at 0.92); hollow rect
  = FRAME, filled = RECT, square flagged. Full-vs-hollow stays topology.
- **THREE root-cause bugs found by the battery, in order**: (1) raw
  neighbour-count junctions shatter 8-connected diagonals (→ crossing
  number); (2) even crossing-number junctions chop strokes where
  thinning leaves 2px bits — junction detection ABANDONED for path
  peeling; (3) the deepest: `_ink_components` was 4-connected — a
  skeleton is an 8-connected path, so every diagonal step split it and
  the 7's top bar fell under the size floor (→ conn=8 for skeletons,
  conn=4 kept for holes, which NEED it).
- The connectivity fix cascaded: the MNIST signature road jumped
  **36.7% → 52–58% at 299/300 coverage** with no new learning — the
  perception was lying and stopped.

## 2026-07-04 — FULL AND HOLLOW: the shape vocabulary (owner, same day)

"What if it had full and hollow bones? circle vs disc vs sphere vs
ball... teach it the basic shapes and it could see the 8 is two circles
maybe one a bit squished." Battery `shapes_battery.py` **11/11**.
- `describe_shape`: holes→rings (squish+angle), blobs→discs, strokes→
  bars; arrangement = ink connectivity (a fact of the ink — the first
  cut thresholded center distances and missed the 8's own join, battery
  H2); decomposition ASSEMBLES into the net via C1 (whole + shape parts
  + touching/above/below edges) with gated English on the whole node.
  **The 8: "two rings, stacked, one squished (0.66)" — the owner's
  sentence, said by the engine.** The 0: one ring. Ring vs disc exact.
- `classify_solid`: sphere shell (radius cv→0) vs solid ball (cv≈0.26,
  the exact uniform-density value) with an honest middle-band refusal.
- Real handwriting (MNIST): hole counting agrees with canonical digit
  topology 86%; signature-only road 38.5% at 299/300 coverage. NAMED
  NEXT: the two-tier road — topology filters candidates (near-total
  coverage), bone patterns decide within the class (74.2% precision) —
  composition should beat both parents.

## 2026-07-04 — THE WIREFRAME (owner's 2D-transformer design, same day)

Owner's spec, verbatim commitments: "create a wireframe concept of the
thing that isaac can then run numbers over... tracks all objects...
basically a lidar 3d scan of the image faces... stitch them together into
an idea... assumed reflection axis of symmetry to fill out unknowns...
bones and structures... and for 2d the same thing across a single plane."
Battery `wireframe_battery.py` **8/8**; suite 11/11; spatial 13/13;
pattern3d 9/9 after.
- **Bones (2D)**: `keypoints_structural` — Zhang–Suen skeleton, spur
  pruning + junction merging (raw skeletons of thick strokes sprout
  spurious branches — battery W1: 20.7%→74.2% once pruned). MNIST
  patterns on bones: 74.2% where answered vs 33.3% ink sampling; more
  total correct; coverage 31/200 = the open dial.
- **Symmetry completion**: `complete_symmetry` — candidate planes FROM
  MIRROR PAIRS (normal = difference direction, offset = midpoint
  projection); v1 forced the plane through the observed centroid, which
  a partial scan's lopsidedness pulls off the true plane (W2 caught it);
  null-gated (10/10 refusals on asymmetric clouds); inferred points are
  provenance-marked hypotheses. Design honesty recorded: symmetry is
  UNFALSIFIABLE from one side alone — the first W2 draft demanded it and
  the organ correctly refused; the test was wrong.
- **Stitching**: `stitch_views` — partial scans merge via >=3 shared
  points, both factorization depth-signs tried; machine-exact (1.3e-15);
  refuses thin overlap.
- Named next steps: bone GRAPH into the net (ratios on bones →
  discover()), coverage dial on bone patterns, tracker (pixels→tracks),
  texture/color percepts.

## 2026-07-04 — THE LIFT AND THE PATTERN NET (owner: 2D→3D "but it needs
## to work on 2d to 2d abstraction too... it can learn the spatial pattern net")

One mechanism, two regimes (`pattern3d_battery.py` **9/9**; suite 11/11;
spatial 13/13; all six other batteries green):
- **2D→3D lift** in observe_spatial: Tomasi–Kanade + metric upgrade,
  TRIGGER-gated (attempted only when 2D perception finds NOTHING locked —
  an unconditional lift broke the four-bar, suite caught it) and
  TRIPLE-null-gated (planar refuses; non-rigid refuses; the RANK-CLIFF
  null — rank-3 reconstruction is rigid by construction, so random walks
  were being fabricated into rigid bodies until s3 >= 5*s4 was required;
  battery L3 caught it). Rotating rigid body: recovered 3D distances
  constant (cv 0.0000 vs 26% variation in 2D); same body across motions
  SAME, different body DIFFERENT — viewpoint-invariant recognition from
  2D tracks.
- **The SPATIAL PATTERN NET (2D→2D)**: learn_pattern/recognize_pattern —
  instances are views of a canonical form; ICP-lite registration factors
  the transform out; parts admitted past a scrambled-view null; pattern =
  net structure; recognition abstains at the measured chance-registration
  bar. Rotation freedom is class-dependent (n_rot=1 for digits — a 6 IS
  an upside-down 9). Glyphs 90%; junk 19/20 shrugged; MNIST keypoints
  under transform: 56.2% where answered (48/200 — trustworthy floor) vs
  38.5% unregistered baseline.
- Three battery-caught corrections, recorded: unconditional lift broke
  planar mechanisms (→ the nothing-locked trigger); low residual alone
  fabricated rigidity from noise (→ rank-cliff null); free ICP scale
  collapsed matches to fake low residuals, 25%→56% on digits when
  clamped to [0.8, 1.25].
- Honest remaining gaps (D8's open half): the TRACKER (pixels →
  identified tracks; farthest-point ink keypoints are unstable —
  structural keypoints next), multi-body SfM, texture/color percepts
  (CIFAR needs more than shape), clock readout.

## 2026-07-04 — C1 + C2 IN ENGINE: arrangement and binding (the two the audits kept converging on)

- **C1 — uptake composition** (`uptake_battery.py` **10/10** = rebuild B's
  (a)–(g) engine-native): wholes are parts + uptake edges as NET STRUCTURE
  (offer:/uptake:/whole: nodes; register_part / assemble / operable
  (fixed-point over doors) / emergent / dismantle / whole_as_part).
  Engine affords torque only when wired right; rewired = different whole,
  no torque; pile = nothing; engine+wheels+frame compose upward to a car
  that affords locomotion. THE LEARNED SIDE: wave_consolidate handoffs now
  mint the same uptake:<g>.activation-><h> structure and circles ARRANGE
  their edges — temporal wholes carry arrangement without being taught.
  Membership-only crystals (audit 2.3's designed-in flaw) are done.
- **C2 — compound doors + the ceiling trigger** (`compound_battery.py`
  **6/6**; audit 2.11's missing wiring): crystallize_features(
  compounds="auto") — when flat doors leave held-out confusions the
  trigger fires; conjunction doors mined per confused pair; admission =
  selection-corrected label-permutation null; KEPT only if held-out
  accuracy improves; the whole decision recorded (compound_report);
  classify_features augments identically. **XOR: flat 0.46 → 0.89.**
  Refusals: 0/3 random-label runs kept compounds; separable data leaves
  the trigger silent. Battery-caught migration bug, recorded: the covtype
  harness's marginal-separation work-filter (skip bins with marg < 0.02)
  HARD-BLOCKED pure XOR, where marginals are exactly zero and the signal
  lives only in the conjunction — pruning is not statistics; the null is
  the gate. Second battery-caught tune: 8-bin compound grid + keep-15 was
  too sparse to cover XOR's informative cells (0.59); 6-bin + keep-30 →
  0.89. Covtype re-run on the engine path rides with the gauntlet (F1).
- Regression: suite 11/11; sense 14/14; blockperm 10/10; periodfold 6/6;
  admission 10/10; crystallizer C1–C6 WORKS.

## 2026-07-04 — A2 + A4: tests replace thresholds in the crystallizer

The organ everything stands on gets its statistics. Admission battery
(`experiments/admission_battery.py`) **10/10**; crystallizer battery C1–C6
re-verified WORKS to owner spec; suite 11/11; sense/blockperm/periodfold
batteries green after.
- **The wrong/sound verdict is now a degrees-aware hypergeometric TEST**
  (numpy-only, `_hyper_tail`): p(type) = pairs-scanned selection charge ×
  P(two chanciest members share the k-door intent | degrees, universe) ×
  ∏ remaining members' coverage chance; sound iff p < 0.01; p stored on
  meta. SUPERSEDES the 07-03 global re-clustering shuffle — same battery
  verdicts (C1 sound, C3 chance-wrong) at O(types) instead of
  O(shuffles×n²); knee now ~26 s @ 800 (from 32 post-E3, ~420 pre-E3).
- **min_shared=2 KEPT as the candidate floor** — expansion by design
  (propose freely); admission is the test. **0.8 merge KEPT** — the
  owner-settled DEFINITION of near-identical (C2a law).
- **Wrong types demoted from ORGANIZING** — hierarchy requires both types
  sound (law-4 demotion, the senses precedent). Two battery-caught design
  corrections along the way: (1) chance-gating the hierarchy between
  SOUND types broke the abc/abd law (C2a FAIL — double-gating; reverted
  to definitional-between-sound); (2) a hypergeometric OR-branch for
  wrong types let 7 chance links through (A2b FAIL — chance types share
  members by construction; independent-draws significance is the wrong
  null for "should these organize"). Both wrong designs recorded here,
  wearing their defeats.
- **Rules face a chance gate** (overlap must beat independence at 1%;
  ratio stays as strength). Noise context: 0 rules.
- **A4 — lockouts evidence-weighted and revisable**: recomputed each
  sleep; 1 negative → ACTIVE provisional, ≥2 → confirmed
  (`lockout_status`); contradicted → RETRACTED to `wrong_lockouts` with
  the why (the old behavior — one glance locks forever, even against
  later positive evidence — is gone); the net keeps the door.

## 2026-07-04 — E7 CURED: the phase-fold period proposal (owner's design)

Hours after the block null unmasked E7 (off-grid frequencies unreachable
over long windows), the owner supplied the cure: "if you suspect a period
do the projection thing. you don't need the whole thing, you just need a
few samples and to map it." Built as `_Enumerator._propose_periods`:
before atoms are built, y is FOLDED onto candidate periods of each input
(t mod P → phase bins; coherence = variance explained; coarse geomspace
scan then fine scan around the winner); a period is proposed only past a
selection-corrected block-perm null that replays the identical two-stage
scan (99th pct, 100 draws). Proposed frequencies join the sin/cos grid
for that discover() and STILL face the admission null — expansion
widened, compression untouched (the Intellon pattern, stated by the
owner the same hour). Battery `periodfold_battery.py` **6/6**:
- the E7 case (sin(1.5t) + AR(0.9) over 40u, NO RULE pre-fold) →
  **`+3.10*sin(1.5061*x0)` PARTIAL** — truth through valid gates;
- **150 scattered timestamps → UNDERSTOOD** (`sin+cos` pair at 1.4805) —
  folding needs coverage of the CYCLE, not of time (the owner's "few
  samples" claim, verified);
- AR noise alone 0/5 false laws; white noise proposes ~nothing at the 1%
  gate; planted iid law untouched.
Two battery-caught corrections during the build: the coarse-only scan
proposed k 2% off and small-n refits couldn't walk it home (fine scan
added, null replays it); the 95% proposal gate tripped 2/10 on white
noise (raised to 99%, 100 draws). blockperm B5 updated: the case it
recorded as an honest refusal is now articulated legitimately.
Suite 11/11; discovery battery + red team green; calibration re-measured
(third time today — the standing rule).

## 2026-07-04 — DOWN THE CHECKLIST: E3 + A1 (the core before the additions)

Owner: "fix the core before adding on" — the debt checklist's attack order,
executed in order. Suite 11/11 throughout; discovery battery, red team,
sense battery all green after.
- **E3 CLOSED — the reverse index.** `Net.preds` maintained in add_door
  (lazy rebuild for pre-index snapshots); get_predecessors and
  get_full_profile read the index. Equivalence PROVEN exact (0 mismatches,
  10 random nets × all tags vs the old scan). The crystallizer knee, the
  measured limit E1, collapsed WITHOUT touching the crystallizer:
  50/200/800 nodes = 0.03/0.77/32.6 s (was 0.04/2.9/~420 — **13× at 800**),
  confirming E3 was the structural root.
- **A1 CLOSED — the block-permutation null** (the oldest methods debt; the
  sunspot 20-CPU-hour runaway's proper cure). Every admission round the
  residual's decorrelation length L is MEASURED (lag-1 significance at 1%,
  then the ACF's first in-band lag, capped so ≥20 blocks remain — the cap
  itself was measured in: uncapped, a slow signal's own period inflates L
  until the null protects the structure under test). L=1 → the old iid
  path bit-for-bit; L>1 → circular moving-block permutation. Battery
  `blockperm_battery.py` **10/10**: detector right on white/AR(0.6)/AR(0.95);
  planted iid law still exact; the runaway condition now stops at 0 terms
  NO RULE (0/5 false laws across seeds); power retained on-grid under
  AR(0.9). `max_terms=16` demoted to backstop.
- **Enumerator changed → calibration RE-MEASURED per the standing rule:**
  decay curve unchanged within noise (far point 0.373→0.353), ECE 0.079,
  Brier 0.255 vs flat 0.284 — DECAY_MEASURED updated with provenance.
- **NEW measured limit (E7), unmasked by the honest null:** grid frequency
  resolution over long windows — off-grid 1.5 between grid points 1 and 2
  is near-orthogonal to every proposal atom over ~10 cycles (r 0.12 vs
  gate 0.37) → honest NO RULE. The OLD null "found" such cases by letting
  near-miss atoms in for hill-climbing — power by accident through an
  invalid gate. Filed as E7 with the principled fix (adaptive spectral
  proposal — widen expansion, keep compression).

## 2026-07-04 — SENSES ARE THINGS (polysemy rebuilt on doors; suite 11/11)

The polysemy mechanism (crystallize_senses/route, 2026-06-23) audited on the
owner's question — "it should not be flat as such, but directed; that was the
point of the doors" — and found half-right: direction WAS preserved per sense,
but senses lived as set-blobs on node meta that only route() could read; every
other net-walker saw a flat door pile. Rebuilt to the standing laws:
- **Senses are first-class nodes** `sense:<node>#<gen>.<k>` with real doors:
  node→sense (`sense`), pred→sense / sense→succ (`sense_seq` — direction is
  net structure now), sense→context (`sense_ctx`). compare_nodes sees them.
- **Null-gated admission** (the old fixed-count limit was flagged in the
  manual since day one): a sense's coherence — (occurrences−1) × shared
  context core — must beat the best sense from context tokens reshuffled
  across occurrences (sizes + frequencies preserved; selection-corrected).
  0/20 false senses on random contexts. Found + fixed a hash-randomization
  nondeterminism in the null's shuffle pool (sets → sorted).
- **Wrong is kept and classified** — failed senses filed in
  `isaac.wrong_senses` with the why on the node meta; **supersession** on
  re-crystallize (old generation demoted `superseded`, never erased);
  **route() demotes** wrong/superseded from the comparison set (law 4) and
  reads winners from the doors, falling back to flat when nothing sound.
Battery: `experiments/sense_battery.py` **14/14** (planted polysemy, noise
refusal, doors-visible, supersession, mixed real+noise); polysemy check now
inside the language self-test area; save/load round-trip verified.
Remaining honest limits: candidate LINKING still fixed-count (admission is
the test); batch re-run, not incremental; membership door one-way.

## 2026-07-04 — THE CORRECTION-AND-REUSE ARC (suite 11/11 throughout)

One day, eight capabilities, every one owner-specified and battery-proven:
- **refine()** — the correction loop: law_confidence picks the weakest
  region, budgeted experiments go exactly there, re-derivation passes the
  Occam gate. Measured: beyond-range hold **50% → 75%** (+25 pts), terms
  flat. **Occam is a PREFERENCE, not a gate** ("its not only. its just
  preferred") — non-preferred candidates RETAINED as alternatives.
- **capture_net / graduate** — audit 2.8 CLOSED (flat level): the
  null-gated stopgap net + the distillation attack; planted x0·x1−x2
  captured then said EXACTLY (prune runs against REALITY, so net-warp
  terms die). Noise nets fail their null; nothing stored.
- **adequacy** — data too weak to interpret is a DIAGNOSIS with a cause
  (below-onset/provisional, missing-variable shadow, class limit,
  nothing-beats-chance, range-too-narrow).
- **interrogate / graduate_composite** — the captured made explicit in
  gated English (drivers, joint action, composite dependence vs matched
  level-set nulls, shape+frequency); the stuck sin(3·x0·x1) delivered
  "flows through the product ONLY" then graduated EXACT via the
  composite coordinate.
- **register_composite** — combinations are THINGS: comb:(x0*x1) nodes,
  ledger-persisted, offered to every future discover(). The canonical
  unsayable became UNDERSTOOD-exact after learning the combination on a
  DIFFERENT problem, including across a session boundary.
- **collectives** — the common mode enumerated SIGNED both directions
  ("darkening vs brightening"), gated vs sign-scrambled shifts, minted
  as mean(...) coordinates; mixed-sign groups refused.
- **ops open + ONE DIAL** — ratio and log composites (domain-guarded);
  then log folded INTO the power family at λ=0 (Box-Cox limit); rivals
  gain log+sqrt; `+2.00*log(x0) +1.00` sayable natively cold.
- **the audits** — calibration (100 worlds): form-true trust number
  **68%**, UNDERSTOOD-inside 100%, noise refusals 15/15, accounting
  median error 0.2 pts; extrapolated-confidence curve measured and
  validated out-of-sample (ECE 0.070); re-measured after the enumerator
  change: profile unchanged.
NEXT (queued): **effect entities** (the shadow pipeline: expect →
subtract → perceive-the-delta, signed); block-permutation null; pixel
clock; MVP track (CSV ingestion → Report → UI plots → packaging).

## 2026-07-03 (last) — EXTRAPOLATED CONFIDENCE: the stamp becomes a curve

- Owner: "maybe just a boundary confidence? what about extrapolated
  confidence?" → `law_confidence(name, X)` NEW: per-point graded belief —
  boundary confidence (edge R²) inside the hull, × the MEASURED survival
  curve beyond it (`DECAY_MEASURED`: 76/59/45/43/37% at δ = 0/.1/.3/.6/1.0
  spans; from 51 externally-graded laws; validated on 52 fresh: ECE 0.070,
  Brier beats the flat 68% baseline). Law nodes store observed `ranges` +
  `r2_edge`. Self-test (h): inside 0.88 > near 0.57 > far 0.38; discovery
  9/9; suite 11/11.
- Calibration audit (priority 4) DONE same session: form-true trust number
  68%; UNDERSTOOD-inside 100%; noise refusals 15/15; accounting median
  error 0.2 pts. `experiments/calibration_audit.py` +
  `confidence_curve.py`.

## 2026-07-03 (late night) — WRONG IS KEPT; SUPERSESSION, NOT OVERWRITE

- Owner's laws: "junk types would just be a different classification of
  wrong... it can learn not only what was wrong, but why. knowing what is
  right is intelligence. knowing what is wrong is wisdom." + "deprecation
  = supersession: if there is a and b, and b works better, use b." + "no
  optimizing before limits; telling it what was important broke
  everything before."
- **_crystallize Phase 3.5 NEW**: every type tested vs its chance-null
  (degree-preserving shuffle, best-of-chance selection-corrected); failures
  FILED in `wrong_types` with why on node meta — never prevented, never
  deleted, downstream untouched. C3: 249/249 chance types filed wrong;
  C1 categories all sound.
- **confirm() OVERTURN now supersedes**: the losing law appended to
  `superseded` with the why (equation, model, SSE margin). C6 NEW: the
  defeated parabola stays on the record wearing its defeat.
- Dropped from the plan per owner: forgetting/disuse-decay and salience
  weighting (human constraints Isaac doesn't have; importance-telling =
  the old trap). Suite 11/11.

## 2026-07-03 (night) — THE FOUNDATION FIX: DIVERGENT DOORS SELF-ASSEMBLE

- Owner: "the less you do, the more you let Isaac do... let the natural
  structures fall where they may" + "i didn't realize not/'divergent'
  doors weren't being created." Both fixed at the substrate:
- **`Net.door_counts` NEW** — per-door observation counts. Seen-once vs
  seen-a-hundred-times are different facts; no statistical divergence
  test was possible without this.
- **`_crystallize` Phase 1.5 NEW** — the atom's three verdicts all write:
  SAME → membership; **DIVERGENT → not_<door> minted from experience**
  (rest-of-intent carrier, ≥3 sightings, absence beats the
  like-your-siblings null at 1%, Laplace-smoothed); ABSENT → silence.
  Runs before the merge so fresh negatives veto collapses same-sleep.
  Minted negatives carry tag `neg` (never enter sequence generation);
  teach_not moved to tag `neg` too.
- Battery C2c NEW: **penguin earns not_fly by being WATCHED, never
  taught**; chick at 2 sightings earns nothing. C1/C2a/C2b/C2c all PASS;
  suite 11/11 unchanged.

## 2026-07-03 (evening) — CRYSTALLIZER AMENDED TO THE OWNER'S TWO LAWS

- Owner's spec, verbatim intent: negatives are POSITIVE facts (penguin
  not_fly vetoes collapse — "not just unknown, a positively negative
  result"); partial overlap FACTORS, never merges ("abc and abd are not
  the same thing, but they can both belong to the ab group").
- `_crystallize` Phase 2: merge now requires near-identical member sets
  (overlap vs the LARGER set ≥ 0.8) AND no positive-negative conflict.
  `teach_not()` NEW: cannot-fact + first-class not_<prop> door.
- `experiments/crystallizer_battery.py` NEW (before/after outputs in
  runs/): C1 clean categories PASS (unchanged — the regime it always
  handled); C2a abc/abd FAIL→**PASS**; C2b penguin FAIL→**PASS**; C3
  measured: 249 junk types from pure chance (admission null still OPEN —
  now MORE visible since stricter merging no longer hides it); C5 knee
  measured: 0.04/2.9/~420 s at 50/200/800 nodes (OPEN).
- Suite 11/11 unchanged.

## 2026-07-03 (later) — SPATIAL PERCEPTION IN THE ENGINE (suite 11/11)

- **observe_spatial(frames, label=)** + **compare_scenes(a, b)** migrated
  into `isaac.py` after harness validation (`spatial/test_isaac_bridge.py`
  4/4 + `spatial/test_null_battery.py` clean). Relations cross, coordinates
  never do: locked/bounded edges (null-gated — variance-ratio vs own noise
  floor; increment-shuffle surrogate for bounded), parts (pairwise-locked
  cliques), hinges, anchors, scale-free ratio signature. Facts enter via
  teach(); nothing survives the nulls → NOTHING taught.
- **New self-test area `spatial` (suite 10 → 11):** four-bar perceived (4
  bars incl. undeclared ground, 4 hinges, anchors, queryable facts);
  recognition across 2.4× scale + rotation + translation (signature gap
  0.0); rigid plate discriminated; random walkers teach 0 facts.
- Spatial GM worlds (`experiments/world_gm_spatial.py`): generator =
  sandbox forward solver, player = perceiver, GM grades; 3/3 incl. occluded
  crank 1.316 vs true 1.312 via 36 BOUGHT fold/extend probe angles.
- Registration 16×16 caveat RESOLVED (see §5 of the manual): 84.4%
  vindicated by the rebuilt committed harness.

## 2026-07-03 — the accounting + audit fixes (suite 10/10, discovery 8/8)

- **THE ACCOUNTING (audit 2.8) BUILT — flat level.** Every `discover()` now
  returns `articulated% + captured% + noise% = 100` (captured measured on the
  RESIDUAL of the kept equation, past a permuted null; noise = proven at this
  expressive class). Self-test (g): planted 73.5% law share → measured 72.7%.
  **Residual dossier**: >5% unexplained becomes a first-class `x:<name>` with
  share, responsive channels, RMS/edge-RMS — on the law node + ledger.
  Level-indexed accounting still OPEN.
- **CAPTURED-erases-law bug FIXED**: a real partial equation is stored even
  when capture wins the headline verdict.
- **Capture null re-targeted**: the null now replays the same
  max-over-candidate-neighbor-sets contest the real score won (was permuting
  only under the winner — anti-conservative). Red team + batteries unchanged
  (0 kills; E9 0/20).
- **confirm() absolute-fit guard**: fit collapse (R² < 0.2) on new data →
  REFUTED, never CONFIRMED-by-default with no rivals.
- **validate_law(name, X, y) NEW**: HOLDS/DEGRADED/FAILS on new evidence,
  ledger-recorded — the check that keeps ledger-inherited laws honest.
- **Harness variants rebuilt & committed** (were RECORDED-only):
  `experiments/registration_perception_16.py` — 84.4% random pos+size
  (recorded 84.4), novel-bigger 85.4%, raw canvas 23.7%, VERDICT WORKS;
  `experiments/covtype_door_weighted.py` — 95.3% door-weighted k=1 (recorded
  94.4; elevation weight 0.78 vs recorded 0.76) — **and the sharpened
  row-index control scores 94.8%**, so the covtype captured tier is almost
  entirely spatial leakage; the honest covtype number is the articulated
  tier (56–59%).
- Still OPEN (unchanged): block-permutation null; level-indexed accounting;
  CAPTURED→law graduation (distillation); shrug→discover reflex; compound
  doors in-engine; uptake edges in-engine.

> **Maintenance rule:** when you add, change, or break a capability, update THIS
> file in the same step. The Manual explains the theory; this doc tracks the
> live state. If a capability isn't listed here with a status, assume it doesn't
> exist. Status tags: **SOLID** (re-run, stands) · **RAN** (executed this
> session) · **PARTIAL** (works with a stated limit) · **OPEN** (not built).

---

## How to run

- Python 3.8+ and NumPy.
- **Canonical home:** `C:\Users\jtwee\Documents\isaac_project\` (the live working
  copy; the `Downloads\New folder (3)` copy + zip history remain there as backup).
  Reorganized 2026-06-24 into four parts — **the code now lives in
  `2_the_machine\code\`** (this doc is in `2_the_machine\docs\`).
- **Windows:** prefix scripts with `PYTHONUTF8=1` (the box-drawing output errors
  on cp1252 otherwise). Not a bug in Isaac.
- Engine self-test (in this repo): from the repo root, `PYTHONUTF8=1 python isaac.py` →
  expect **11/11** (the "6/6" of this entry's date grew to 10 areas by 07-02,
  11 with spatial on 07-03).

---

## The his / wired ledger (read this first)

The whole project hinges on the decision/difference running **in him**, not in
the harness around him (Rule 1). The honest split as it stands:

- **His (cognition):** typing, counting, `transduce` state-walk, working memory,
  recognition via `check`, negatives, logic combine (AND/NOT), inventory,
  honest-unknown.
- **Wired retina (allowed — cheap "looking"):** salience (GlobalBaseline),
  connected-components segmentation, bounding-box crop, locating part positions,
  computing displacement signs / neighbor contents.
- **Still harness (the unbuilt frontier):** control flow — loops over cells /
  directions, the survival-fallback structure, cross-frame data association.
  This is the genuine `if`/`while`-over-his-own-state gap.

**Representation direction (2026-06-22):** the world is a fixed alphabet of
meaning-bearing **glyphs** (parts), not pixels — e.g. snake `~~~~~<`. This plays
to his language muscle and around the pixel wall. The pixel→glyph retina is the
one piece deliberately bracketed for later.

---

## Capabilities

### Core engine (pre-session, verified this session)
| capability | status | where |
|---|---|---|
| Language: observe, crystallize, generate, type inference | SOLID | `isaac.py` |
| Math: tables + decompose-when-shrug | SOLID | `isaac.py` |
| Logic: truth tables, compound expr (`logic_eval`) | SOLID | `isaac.py` |
| Reasoning: is_a, capability inheritance w/ negative override, syllogism | SOLID | `isaac.py` |
| Problem solving: forward/backward/gap-fill/multi-step | SOLID | `isaac.py` |
| Persistence: consequence assessment, plan/think/execute | SOLID | `isaac.py` |
| `check` vs `lookup` (validate a claim vs retrieve best) | SOLID | `isaac.py` |
| Self-test | **6/6 RAN** (at this entry's date; **11/11** as of 07-03) | `python isaac.py` |

### Built / extended this session
| capability | status | where | result |
|---|---|---|---|
| **`transduce`** — universal state-walk; next state = his matmul | SOLID | `isaac.py`, `fst_transduce.py` | COUNT/PARITY/RUN 100% on novel grids |
| **`Scratch`** — working memory (registers/RAM): write/read/incr/append/latch/history | RAN | `isaac.py`, `working_memory.py` | counting in RAM: 2 doors, any N, 100% |
| episode boundaries (per-run trace reset) | RAN | `isaac.py` | trace is per-run, not lifetime |
| **Attention levels** — invisible / background / foreground, tunable floor | RAN | `attention_levels.py` | thorough scan surfaces background |
| Salience retina (per-cell EMA + field-relative) | SOLID | `global_baseline.py` | tracks normal, fades furniture |
| **Attention→Tracker** — salience opens a track, follows w/ identity+motion | PARTIAL | `attention_tracker.py` | works; **merges on contact** (occlusion) |
| **Auto-inventory + honest-unknown** (turtle loop) | RAN | `turtle_inventory.py` | dual unknown (word vs thing); mint → generalize |
| **Parts-alphabet creatures** — roles discovered from position | RAN | `ascii_creatures.py` | body/head/tongue by position; length via RAM |
| **Kindergarten curriculum** — length/facing/direction/in-line | RAN | `curriculum.py` | 100% novel (relative); absolute only 53% |
| **Multi-answer moves** via `check` (cardinal only, no diagonal) | RAN | `snake_moves.py` | check 100% exact-set; lookup 15% |
| **Negatives** — body/wall block a move, checked first | RAN | `snake_policy.py` | 100% never-suicidal, 100% optimal-when-possible |
| **Combine made his** — `(not blocked) and toward` via his gates | RAN | `snake_policy_his.py` | 100%/100%, decision end-to-end his |

### Known limits / open
| item | status | note |
|---|---|---|
| Scale / rotation invariance | OPEN | recognition is exact-bitmap; the recurring wall. Fix = relational/vector identity |
| Data association / occlusion | OPEN | two salient things touching merge into one blob |
| Control flow (`if`/`while` over his state) | OPEN | the loop/fallback structure is still harness |
| Self-directed working memory | OPEN | he's taught what to track/write, doesn't choose yet |
| Predict → surprise (change loop) | OPEN | RAM now holds "before"; loop not built |
| pixel → glyph retina | OPEN (bracketed) | deliberately deferred under the parts-alphabet choice |
| Live glyph-board Snake | OPEN | next buildable: stack runs in motion |

---

## File index (working bundle)
- `isaac.py` — the engine (Net, Isaac, Scratch, World) + self-test
- `fst_transduce.py` — transduce: 3 machines (count/parity/run)
- `working_memory.py` — registers demo (increment/track/associate/replay)
- `global_baseline.py` — salience retina
- `attention_levels.py` — invisible/background/foreground, tunable attention
- `attention_tracker.py` — salience → persistent tracker net
- `turtle_inventory.py` — auto-inventory + honest-unknown
- `ascii_creatures.py` — parts-alphabet, roles from position
- `curriculum.py` — kindergarten spatial questions
- `snake_moves.py` — multi-answer cardinal moves (check vs lookup)
- `snake_policy.py` — negatives + rule-out-then-keep policy
- `snake_policy_his.py` — the combine via his own logic gates
- `ISAAC_Manual.md` — full theory/reference · `ISAAC_BUILD_STATE.md` — this doc

---

## Changelog (savepoints)

### 2026-07-02 — the science-engine day: analogy, memory, persistence, a face

- **Power atoms** (x^k, grid ±{0.5,1,2} + {1.5,-0.5} with refine) →
  **Kepler exact: T = a^1.5, R² 1.0000** from 8 rows. **max_terms=16**
  runaway brake after the sunspot lesson: iid permutation nulls are
  INVALID on autocorrelated targets (20 CPU-hours of proof); block
  permutation = open item #1.
- **Cross-domain** (`rebuild/cross_domain.py`): laws matched by structure
  (log-track exponents = roles) — gravity ≡ coulomb; cooling ≡ capacitor;
  inverse-square role family; family abstraction nodes; **analogy-primed
  transfer**: magnetism n=24, cold 0.82 → primed 0.995 (constant 3.26/3.2).
- **Findings ledger**: record/recall/load (JSONL); negative knowledge kept;
  laws inherited across sessions — dead Isaac's Kepler predicted
  **Pluto 248.0 yr (true 247.9)**, outside training range.
- **Whole-mind save/load/fork** (9KB snapshots; forks diverge safely).
- **UI** (`ui/isaac_ui.py`, stdlib, :8674): converse / discover with
  verdict cards (equation, scope, rivals+probes) / apply laws / findings
  search / mind management. Verified end-to-end incl. Pluto via web form.
- **The Gauntlet** (10 datasets, one pipeline, `rebuild/gauntlet.py`):
  mnist 95.2, smallnorb 87.7, fsdd-audio 92 mixed, covtype arc → 94.4%
  door-weighted exemplars (row-index leakage control: 79%); honest
  refusals on kepler-without-power-atoms and noise; sunspots →
  multi-cycle solar structure (Schwabe/Gleissberg bands + modulation),
  periodogram-corroborated, honestly scoped range-valid.
- Status: **suite 10/10**; both repos pushed; handoff =
  `SESSION_HANDOFF_2026-07-02.md` (owner's four named priorities:
  scale testing, human interaction, information validation, accuracy
  validation/calibration audit).

### 2026-07-01c — DISCOVERY: the challenge loop (the thing that learns things)

- **`discover(X, y, name)`** — given examples of something he cannot do, find
  the rule: staged null-gated term enumeration (candidates grow only around
  admitted terms; admission must beat the max-over-candidates correlation on
  permuted residuals; survivors ARE the equation), validated on a held-out
  half. Four honest verdicts: **UNDERSTOOD** (equation, held-out R² ≥ 0.9) /
  **PARTIAL** (real equation, part explained, stated) / **CAPTURED**
  (nearest-exemplar prediction beats the permuted null — caught, tracked,
  not yet said; no nets) / **NO RULE** (proven nothing at this class).
- **`apply_law(name, X)`** — an UNDERSTOOD law becomes a `law:<name>` node
  (equation in meta, fact indexed); the challenge is computable from then on.
  (Named apply_law — `solve()` was already taken by the token-problem solver;
  collision found the hard way.)
- **Status: RAN — self-test `test_discovery` 5/5, suite 9/9.** Recovered
  `+1.00*x2*x2 -1.00*x3 +1.00*x0*x1` and `+1.00*x0*x1*cos(x2-x3)` EXACTLY
  (held-out R² 1.000, reusable R² 1.000); said NO RULE on noise; CAPTURED
  sin(3·x0·x1) (0.547 vs equation's 0.152) — the four epistemic verdicts,
  live in one method.
- This is the in-engine port of the equation-discovery program (rebuild C /
  equation_discovery scripts). Waves = a sensor; discover() = the learner.
- **2026-07-01d addendum — "only linear / no complex numbers" rumor killed:**
  the solver is linear in COEFFICIENTS over a nonlinear library, and the
  library was enriched with unary transcendentals (sin/cos/exp at a scale
  grid) + a REFINE pass that hill-climbs parameters INSIDE nonlinearities
  (frequency/decay/scale — where regression cannot reach). Complex-number
  structure = damped-oscillation pairs: recovered exp((-a+bi)t)'s real face
  `+1.00*cos(3*t)*exp(-0.4025*t)` with the 0.4 decay OFF-GRID. Single-input
  `0.5x² + 1.5·sin(2x)` recovered exactly (the case that used to degenerate
  to polynomials). Legibility hardening en route: trial-refit lookahead with
  reuse-aware parsimony (a scale-atom must BUY its flexibility; already-paid
  flexibility is free), structurally diverse shortlist (heavy-tailed raw
  variables lose correlation contests to bounded atoms — guarantee simple
  candidates a trial), completion bonus (a trial that finishes the equation
  outranks Taylor-expanding a surrogate term by term). test_discovery 7/7,
  every recovered equation exact and legible.
- **Open:** auto-trigger from shrug (compute/lookup failure → discover);
  symbolic/token challenges (currently numeric); law graduation for CAPTURED
  (function recovery attacking the exemplar memory — audit 2.6/2.8 loop);
  nested compositions f(g(x)) beyond degree-3 products (the deep/dense
  regime) still land in CAPTURED, by design.

### 2026-07-01b — THE GREAT REWIRING: five dormant organs connected

Audit found the engine full of built-but-never-called organs (0 call sites:
recognize_doors, transduce-pattern, predict_next, fit_lens, react...). Five
wiring jobs, zero new mechanisms, self-test now **8/8** (test_tracking added):

1. **The clock is his.** `follow(circle)` + tracked `tick()`: phase register
   and dwell counter live in Scratch; transitions are the circle's own
   `wave_next` doors; evidence comes through `recognize_doors` (partial
   recognition = permanence, the dormant organ, now load-bearing); learned
   dwell (net meta, measured at consolidation) dead-reckons when evidence is
   hidden. Phase 100% correct through occlusion in the self-test.
2. **Statuses are world state.** Registration (expected-vs-observed, each
   tick) opens `world.set_state(entity, "missing X")` after 2-tick persistence
   and clears on sight or when the entity leaves the stage (phase advance —
   absence-by-night opens no status). Isaac now owns a World instance.
   Status doors (miss:X) join the same tick — statuses are doors.
3. **Discovery reaches reasoning.** `_teach_fact` (fact_index + tagged door;
   not teach() — the tokenizer would shred structured names) records part_of,
   phase_of, and blocks facts. The status-explanation pass (ordinary
   co-activation scoped to the entity's phase rows) and the conditional
   rescue both teach `blocks` facts. Self-test: blocks(disk) <- cloud doors
   AND the cloud group node, queryable in fact_index.
4. **Conditional rescue in consolidation** (ported from rebuild E): a door
   exiled by heavy interference re-joins its group when membership is
   re-tested where a candidate blocker is absent — blocker taught as a fact
   in the same move. Needed immediately: the new 1.4x edge margin (which
   stops single-false-edge component bridging) exiles occluded members.
5. **Boxes are gone from the live path.** `fit_lens` default = null-gated
   correlation eigenbasis (the basis must beat chance); `crystallize_features`
   stores observed per-dim log-densities ("doors" meta), `classify_features`
   scores by summed log-likelihood. Legacy box meta still written for
   recognize_matrix/old scripts. Smoke test on diagonal (box-killer) data:
   **99.2% vs old boxes ~88%.**

Backup: `code\backups\isaac_pre-wiring_2026-07-01.py`. Caveat: clock ticks
are sensory ticks — mixing unrelated observe() streams into a followed
episode dead-reckons the clock; keep one stream per episode.

### 2026-07-01 — WAVES: temporal crystallization wired into the engine

- **What:** the static crystallizer is order-blind (compares door profiles).
  New idle-mode pass `wave_consolidate()` watches the whole matrix MOVE:
  co-activation **groups** (simultaneous activation as a first-class thing),
  **handoff edges** (one group dims as another lights — prior-frame vs
  later-frame registration), **circles** (waves that return to their start),
  and one level of recursion (circle activity becomes a door; same machinery
  → patterns of patterns, circles of circles).
- **Sensing:** `tick(active)` records one instant of simultaneous activation.
  `observe()` ticks each token with its type doors; the think loop ticks each
  context; `transduce`/`react` inherit via lookup. Any retina/game loop can
  call `tick()` directly. Log lives in `activation_log`.
- **Discoveries enter the net** as nodes (`wave:sun_light[2]`,
  `circle:dark>light>tools`) with tags `wave` / `wave_next` — composable
  upward like anything else.
- **Null discipline (the key method):** every admission beats a **jitter
  null** (±2–5-step shifts: keeps each door's own rhythm, breaks precise
  co-timing; jitter ONE side per pair). A full circular shift is the WRONG
  null for periodic waves — it relands in phase, making real simultaneity
  unbeatable. Handoffs must beat 1.5× the null's max.
- **Status: RAN** — self-test `test_waves` 4/4 (groups exact incl. zero noise
  doors; both planted circles; circles present as net nodes; shuffled-time
  control: groups survive, ALL movement dies). Full suite **7/7**.
- **Reference implementation + planted-truth harness:**
  `isaac_project\rebuild\wave_crystallizer.py` (5/5) and
  `rebuild\RESULTS.md` (Rebuild D) — includes the two generator lessons
  (fixed-length eras clock-lock to waves; global-clock processes are
  genuinely phase-locked — independent waves need independent phases).
- **Backup:** `code\backups\isaac_pre-wave_2026-07-01.py`.
- **Open:** feed a REAL stream (his own activation log during long tasks;
  a glyph-retina game session); wave concepts as parts for uptake-edge
  composition (rebuild B) — circles that consume each other's affordances.

### 2026-06-22 — perception/decision stack, his way
Added `transduce` (state-walk) and `Scratch` (working memory) to the engine.
Built the glyph-world line: salience attention with invisible/background/
foreground levels, salience→tracker, auto-inventory with honest-unknown, the
parts-alphabet representation (direction decision), a kindergarten spatial
curriculum that generalizes (relative » absolute), multi-answer moves via
`check`, taught **negatives** (body/wall block), and moved the final boolean
**combine into his own AND/NOT gates** — making the Snake move decision
end-to-end his. Engine still 6/6.

### 2026-06-22 — neural transplant: boxes as concepts in the net
Added `fit_lens`/`apply_lens` (the aligner = a swappable `lens:<name>` net node:
wired lift + strip-DC + Fisher dim-select now, replaceable by a learned aligner
later, same interface) and `crystallize_features`/`classify_features` (a trained
net's activations → per-class box concepts as `concept:<label>` net nodes with
`[lo,hi,med]` meta, scored by his membership+centroid). Boxes ARE Isaac's
per-container dims — they coexist with his language/math in one net. Verified
on digits (0.90, boxes + language together). Subproject lives in
`neural_transplant/` (range classifier, GPU sweep harness, decode demos).

### 2026-06-24 — contrast crystallizer (two interpretations + his comparator) — REVERTED
**ROLLED BACK 2026-06-24 (session 2, user request): `crystallize_contrast`/
`classify_contrast` were REMOVED from `isaac.py`; the engine is back to its
pre-session state (self-test 6/6). The entry below is kept as a record of what
was tried; the methods no longer exist in the code.**
~~Added `crystallize_contrast`/`classify_contrast` (RAN): user's design — keep TWO
interpretations per quantized cell, reinforced by the two label-streams; run HIS
`compare()` to null the shared and crystallize the RESIDUAL (the difference/bump),
not a per-class box. Decide by the residual. order=2 = compound cells (binding).
On HIGGS (the box-killer, hard tabular): box 0.525 (chance) → contrast 0.620
(≈ logistic), his way. FINDING: literal set-`compare()` = 0.465 (below chance);
the MAGNITUDE of the difference is the signal, so the soft log-contrast is needed
(his comparator needs "how different", not just same/different on continuous data).
Ceiling = logistic (first-order); order-2 barely moved (high-order still out of
reach via fixed pairwise). Engine 6/6 intact; contrast is a node beside language.~~

KEY FINDING: crystal quality is governed by box-geometry (axis-aligned blobs =
"box-friendly", e.g. digits ~99% retention; diagonally-interleaved =
"box-hostile", e.g. covtype caps ~0.62). The valuable lever is the ALIGNMENT
(un-superposition) front-end, now a swappable net node. Engine still 6/6.

### 2026-06-23 — binding / conditional computation (the "critical missing piece")
Diagnosed the recurring gap (polysemy muddle + box-hostility + old fraud Naive-
Bayes limit) as ONE missing primitive: condition the answer on a COMBINATION, not
independent parts. Fixed on both faces. NODE face: `crystallize_senses(node)` +
`route(node, incoming)` added to engine — clusters a node's doors into explicit
sense-sections by within-node context co-occurrence (the crystallizer turned
inward), stored on the node, and routes output by which sense the input matches.
Polysemy ("bank") now disambiguates node-locally + legibly. BOX face: compound/
interaction doors (centered pairwise products) — XOR goes 0.48 (chance, flat
boxes can't bind) → 0.89. Confirms the manual's compound-doors prediction. Both
are mechanism-proofs on toy/clean data; engine 6/6. NEXT real retest: fold
compound doors into the crystal pipeline on covtype (measured 0.62 box ceiling)
to see if binding breaks box-hostility at scale. Demos: `neural_transplant/
interaction_retest.py`; node router in `isaac.py`.

### 2026-06-23 — covtype binding retest: NULL (important finding)
Ran pairwise interaction/compound doors into the box pipeline on covtype
(`neural_transplant/binding_covtype.py`). Result: did NOT break the ceiling —
flat 0.48, +variants 0.54, +all-interactions 0.53, Fisher-selected-interactions
0.47 (WORSE), interactions+variants 0.55. RF 0.83. So pairwise binding does
nothing for covtype. WHY: XOR is a clean low-order interaction (binding nails it,
0.48→0.89); covtype is HIGH-ORDER/distributed/adaptive (RF wins via deep
recursive conditional splits, which fixed pairwise products can't reach). Sub-
finding: Fisher-selecting interactions HURT — you can't pick good interaction-
features with an independence criterion, because which interactions matter is
itself an interaction problem. CONCLUSION (corrects earlier overclaim): compound
doors fix clean, low-order, identifiable interactions (polysemy, XOR); they do
NOT substitute for representation-learning on deeply box-hostile data. Covtype's
ceiling is a REPRESENTATION problem (the registration/lens lever), not a missing-
interaction problem. Reinforces the session thesis: representation is the deep
lever; binding is a local patch.

### 2026-06-23 — covtype is SPATIAL-LEAKAGE-dominated (recontextualizes everything)
Researcher's theory, confirmed empirically: covtype's high accuracy is largely
spatial autocorrelation / lookup, not learned ecology. The 54 features act as a
location fingerprint; cover type is spatially autocorrelated; a RANDOM split
leaks (test cells' neighbors are in train). Tests: (1) kNN(k=1) random split =
0.855 ≈ RF 0.881 — a pure nearest-neighbor LOOKUP nearly matches RF, so the task
is proximity-dominated; (2) hold out a whole wilderness AREA (no neighbors to
look up) → RF collapses 0.88→~0.5-0.6 (area3 0.23, partly distribution shift).
IMPLICATION: the box→RF "gap" (0.69→0.95) is LEAKAGE RF exploits and boxes don't,
NOT deep ecology boxes can't learn — which is why the binding fix did nothing
(no real interaction to capture; just a map to memorize). The box family's ~0.69
was REFUSING to memorize the map = closer to the honest transferable signal
(~0.5-0.7) = aligned with "learn the truth not the consensus." Confirms the
researcher's own boundary-vs-occupancy finding (terrain=feasible set/transferable;
species=contingent/spatial=the leaked part). DO NOT use covtype to evaluate
honest learning — it rewards leakage; use leakage-free data or spatial CV.

### 2026-06-23 — VISION CRYSTAL + ROTATION LENS: registration thesis CONFIRMED on real data
Crystallized a frozen ResNet18's 512-d final embedding on CIFAR-10
(`neural_transplant/vision_crystal.py`, `vision_lens.py`). Encoder makes the rep
FAR more box-friendly than pixels: crystal on raw pixels 0.23 → crystal on
embedding 0.71 (linear probe 0.84, kNN 0.81). The 0.71-vs-0.84 gap = axis-aligned
boxes vs oblique linear boundaries. THEN the key result: a ROTATION LENS (LDA =
learned aligner) closes the ENTIRE gap — crystal after LDA rotation = 0.834 ≈
linear 0.839. So the cheap legible box reader MATCHES the linear head once you
ALIGN first. Registration is the lever, proven on real images. Corollary: variants
HURT after alignment (0.75 < 0.834) — good alignment makes the simplest box win
(max legibility). Validates the swappable-lens design (wired Fisher weak; learned
rotation strong → replace lens contents with a learned rotation). Honest product:
frozen encoder + cheap closed-form rotation + box crystal = legible + abstaining +
accuracy-matching head, no gradient training; but rides on the encoder (no encoder
compression) and LDA is LINEAR (deep nonlinear hostility needs nonlinear registration).
