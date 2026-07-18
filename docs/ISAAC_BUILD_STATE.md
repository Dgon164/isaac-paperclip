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

## 2026-07-15 — THE INSTRUMENT FLOOR (data-ops segment §2; owner's law
## 2026-07-14: "no ruler, no perfect" — exactness is instrument-relative)

Battery written FIRST (`experiments/floor_battery.py`, 13/13), then the
organ: `read_floor(y, X=None, name=None)` + `tell_resolution(name,
sigma)` in the engine. Three roads, every measurement kept, floor = the
LARGEST evidenced noise scale: REPEATS (duplicate-input rows' answer
spread; >=5 groups, >=10 dof), TOLD (usable at once, belief measured —
FLAGGED kept-not-erased when a measured road contradicts it, the larger
wins), GRAIN (quantization step; a LOWER BOUND only). No road evidenced
→ the floor is REFUSED: exactness unclaimable, BEST-RESIDUAL posture,
the report ASKS for the resolution (logical_gaps posture). Named
readings live at `floor:<name>` (active + superseded chain, findings
ledger, pack-proven) — a supersedable tool in the chain (owner law
2026-07-15). WRONG-KEPT the same hour, caught by battery F4: the
reference probe's grain tolerance scaled with the multiple (0.02×mult),
so float-continuous data false-fired a microscopic grain (visible in
the probe's own W8 output, masked there by max-of-roads); cure = the
tolerance is a fraction of ONE STEP. Promotion run 2026-07-15: engine
11/11 + 30 batteries all green, PROVENANCE stamped (research @ aeb3d7d).
Also this date: the ACCOUNT migrated to the pack road
(dc/experiments/account_pack_migration.py — 346 records 0-diff vs the
pickle, round-trip stable, life content verified by name; runner on
packs; mind.isaac frozen at session 94, kept superseded). Discipline
correction, kept: the organ was first built in dc directly — promote.py
says edit in RESEARCH and promote; fixed (research holds the organ, the
promotion above is the honest road in).

SAME DAY, second promotion — THE COMMONALITY MINER + THE AUDIT FACE
(data-ops §4 + §1, batteries first): `mine_commonality()` in the
engine (differential-vs-allowed past a label-shuffle null, never a
frequency; commonality_battery 7/7; the CASE-CLASS MINTER Trace C
needs — organ failure receipts → named class → duel scope) and
`askisaac --audit` + isaac_store/audit.py (flags with receipts:
error/news/duplicate; floors gate exactness, unevidenced → ASK; joins
via triangulate; audit.jsonl; test_audit 14/14). WRONG-KEPT ×3 caught
by batteries within hours: triangulate zero-feature crash (one-column
join tables) → honest mean-model; planted deviations DRAGGING the law
(slope 2.0→1.89, the audit disqualified itself) → CONSENSUS
RECALIBRATION (the Gate 6 trim applied to laws; affine v1, verdict
rewrite is the deeper cure); one off-grid typo blinding the grain
reader → grain by CONSENSUS of gaps (floor battery F14). Promotion
2026-07-15 07:43: engine 11/11 + 32 batteries green, PROVENANCE
stamped. Data-ops steps 1-3 done; remaining: bench harness (B1/B2),
verdict rewrite (§2b, to run through the Trace C machinery).

SAME DAY, sixth arc — THE BENCH RAN + THE FLOOR-CONTAMINATION CURE
(data-ops step 4; promotions #6-7). `dc/experiments/dataops_bench/`
(dc-only harness; PREDICTIONS.md filed BEFORE the first run; sklearn
= labeled BASELINE only): B1 error detection — in-range corruption
ISAAC 24/24 P/R/F1 1.00 with 0 false flags vs z-score/IQR recall
0.00; gross corruption 18/18 while baselines missed 22-33%; clean
control 0 false flags; fresh-eyes #4 measured (heavy-tail t(3) false
flags 0.84-2.5%/table vs 0 Gaussian). B2 completion — 12/12 verdicts
honest incl. the refusal-control world; real-join masked values MAE
0.041 UNDER the 0.05 floor. THE FIND (unpredicted, then filed as
algebra, then confirmed): FLOOR CONTAMINATION — corruption ≥ ~6% of
rows inflated the pooled repeats floor until the 4×floor line
outgrew the corruption at ANY magnitude; recall 1.00→0.00 between 5%
and 7.5% with the audit still saying `flags: active`. THE CURE
(owner call "add outlier ejection"; floor_battery F15-F18 written
first and shown failing — old engine read 0.977 at 10% corruption,
confident 1.91 at 40%): consensus ejection in `_floor_repeats` —
deviations around group MEDIANS, >5×-consensus values ejected FROM
THE MEASUREMENT and FILED in provenance (never from the record),
majority dissent (>20%) REFUSES the road. floor_battery **18/18**;
post-cure sweep recall 1.00 through 15% corruption, floor 0.050
throughout. The cure EXPOSED a second wrong (bench W3 2/3): gross
outliers can drag the discovered FORM, which affine recalibration
cannot unbend — the audit now honestly refuses there and (promotion
#7) its refusal names the fork (under-evidenced floor OR law not
holding at that precision) instead of blaming the user's ruler;
robust law refit = §2b's lane. Full write-up
dataops_bench/RESULTS.md; ledger has the rows.

SAME EVENING, seventh arc — THE CLOUD RECONCILIATION + THE TYPO
CONCEPT (promotion #8). The abandoned claude.ai session's branch
(claude/isaac-dc-local-setup-2e51bt) was found holding ~6.9k lines:
12 attack probes + TESTING_SEGMENT record + LOCAL_PROCESSING.md (the
efficiency ledger: 5 owner designs incl. pregrouping and group-level
outlier ejection with the mine_commonality nursery) + the reservoir
instrument probe 13/13 (proposed §2b second leg); all 17 files
brought into dc's working tree. Its repeats-floor BROKEN rows all
flipped against the cured engine. Its two GRAIN breaks were then
cured by OWNER DESIGN ("word and wrod ... a door between them
connected through the typo concept"): _floor_grain picks the
COARSEST consistent grain (>=0.95 band, else >0.80 typo-story band),
files dissenting gaps as mis-entry candidates, refuses beyond 20%
dissent. floor_battery F19-F22 written first, F19/F20 failing on the
old engine (4 slips of 150 blinded the road; one half-step slip
rescaled the ruler 2x down); now 22/22, engine + 36 batteries green.
Cloud probe re-run: W2b holds through k=8, W2c step held, floor
1.00x true. SECOND OWNER DESIGN captured on the sheet, not built:
MEANINGFUL DOORS — a,b:relationship where the relationship is a
third pointer with executable meaning (3,8:add5); doors today carry
tag strings; the design makes the label a NODE that can be verified,
applied, composed, and mined.

SAME EVENING, eighth arc — THE BOOKS MUST BALANCE (owner design:
"5+5=9 ... you know something here is incorrect ... mark it as
false and return to it ... 40,000 inputs and they dont add up ...
someone somewhere did something wrong"; promotion #9, battery
FIRST). `cross_check(values, checks, floor, name)` in ENGINE
(crosscheck_battery **9/9**; engine + 37 batteries green;
promote.py gained the gate): a failing sum-check marks the TUPLE
false, never the output alone; candidate repairs = mis-entry doors
(the typo concept), proposed never applied; row totals × column
totals localize one bad cell at their intersection (the Hamming/ECC
move; two errors detected and REFUSED, capacity said); a failing
grand total over 40,000 values certifies an error EXISTS with
candidates counted not enumerated; floors gate tolerance; passing
checks veto repairs; FALSE-SOMEWHERE marks persist at
inconsistency:<name> and are RETURNABLE — a later witness check
resolves by supersession (E7: 5+5=9 + a+2=6 → a=4 unique). Next
rung: audit-face totals wiring; relation-shaped checks ride the
MEANINGFUL DOORS design.

SAME DAY, fifth arc — WHEN ORDER MATTERS (owner theory: "additive
does not matter, but subtractive methods are... restricting the
space counts as subtractive"): `order_matters(op)` in engine —
MEASURED never told: swap operands, compare; sensitive verdicts
carry a verified WITNESS pair, free verdicts say "no counterexample
in N probes". Measured: + * max min free; - / ^ matter (witnessed).
Theory + sharpening on the sheet (order matters where slots carry
DIFFERENT ROLES; a-b != b-a for the reason "dog bites man" != "man
bites dog"). order_matters_battery 7/7; promotion 11:13 engine +
35 batteries; account measured all 7 ops itself (pack v8, tools 116).

SAME DAY, fourth arc — STRUCTURE AND ORDER (owner: "ab vs ba. if the
difference is just position he should be able to identify that"):
`compare_order(a, b)` in engine — registration applied to sequences
(parts = identity, arrangement = pose, reported separately); content
multiset-honest; transforms NAMED (swap/reversed/rotated/reordered);
every positional claim carries a mapping VERIFIED to turn a into b;
content-and-order cases factored apart. order_battery **10/10**
(incl. 50 random shuffles all verified). Promotion 11:03: engine
11/11 + 34 batteries. Known v1 scope: flat sequences; trees
(commutativity/canonicalization) = named next rung. Account
re-cataloged (tools node picks up the new organ).

SAME DAY, third arc — WORD ELECTIONS, THE FRONTIER HABIT, THE TOOLS
NODE (owner directives, all battery-first): (1) word_reelection
12/12 — speak:words was write-only/unfalsifiable (25 revert signals,
0 reached the map — the Kung Pow bug); now rivals-with-receipts +
recent-window re-election; ACCOUNT REMINED (pack v3): both poisoned
seats fell by different roads (nap→napkin told 3-0; ate→eats outcome
0/4); session 95 live clean. (2) frontier habit 4/4 — mine_frontier
after every session; first live self-assessment named ONE condition:
action=slept (+0.223). (3) FLOW STRUCTURES design on the sheet
(consideration law: fires or BYPASSED WITH A RECEIPT; branching =
piecewise supersession at flow level; registration rule) + THE TOOLS
NODE built + promoted (tools_battery 8/8; engine + 33 batteries,
PROVENANCE 09:05): register/catalog/query/run/receipt — 107 engine
tools auto-harvested from docstrings; account seeded to 114 incl.
drill tools (pack v6); the session loop queries the node against his
named frontier and skips honestly when nothing applies.

## 2026-07-05 — ALL METHODS, ONE CONCEPT (owner's architecture correction)

Owner: "is it not using all methods? it should be using all methods...
the doors are just pointer connections... they all point to the same
nodes. we don't care what or where or how the information is sorted, we
only care that the information is represented." The separate "roads"
(density/topology/bones/exemplar reported as rival classifiers) were the
HARNESS'S framing, not the design — recognize_doors always said a
concept fires from whatever doors are present. Built:
`learn_glyphs` (every channel attaches evidence to the SAME concept:<c>
nodes) + `recognize_glyph` (each channel's standardized scores → a
posterior; summed log-posteriors decide; the vote returned readable).
Battery `fusion_battery.py` 2/2 — COMPLETE numbers (whole 500-digit test
set, 200 train/class, the owner's same-day reporting rule):
  topology 55.8% | bones 10.0% | density 79.4% | exemplar 85.4%
  **FUSED 88.6%** — the sum beats every specialist channel.
Also this session, the owner's reporting rule adopted permanently:
complete numbers only (coverage multiplied through, per-class wins as
their share of the whole task), no padding, no consolation comparisons.

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

## 2026-07-15 (night): THE VERDICT REWRITE PORTED (S2b, promotion #11 [EXPERIMENTAL])
UNDERSTOOD is now EARNED before examiners and a ruler; r2 demoted to a
reported number. discover() gains: the EXACT ROAD (machine precision
on unseen rows, may override the admitted form; Kepler n=8 stamps
where the old judge said NO RULE), the REPLAY (partial-corr of every
unadmitted candidate + replay-only crease columns vs the held-out
residual, selection-corrected max-null), the POOL meter (frozen
random net, gates-and-names only, scope n>=48 with bypass receipts),
and a CERTIFICATE (machine-exact / within floor / above floor [caps
verdict at PARTIAL] / uncertified) read by the CURED read_floor organ
(told via told_sigma= kwarg or floor:<name> meta). GATES: 100-world
duel wrong-confident 74/100 -> 9/100 with true-law availability 20/20
and 0 false examiner fires; Kepler machine-exact; engine self-test
11/11. The 9 residual leaks = two NAMED classes: F3 poison absorbed
into constants, all examiners honestly quiet (cure = rival-form duel,
queued port requirement) and F5 crease worlds, unsayable until the
mechanisms atoms promote (next promotion: |a-b| makes max a word; the
exact road then stamps it exactly). Surgery notes kept: two port
bugs found by the gate itself and cured by REUSE — a naive private
grain road hallucinated floors on continuous data at n=400 (vacuous
large-multiple tolerance; the engine's cured _floor_grain refuses
correctly) and a naive repeats road was poison-inflatable (the cured
consensus-ejection _floor_repeats already existed) — never ship a
rival reader for an organ that exists. Gate harness:
experiments/verdict_port_gate.py (runs/verdict_gate_*.json).

## 2026-07-15 (night): THE COMPARISON WORDS PROMOTED (promotion #12 [EXPERIMENTAL])
The mechanisms enter the engine both ways. VOCABULARY: the CREASE atom
|xi-xj| (max/min become sayable: max = (a+b+|a-b|)/2) and the SWITCH
atom [xi>t] with thresholds proposed FROM THE DATA (deciles + the
0.5-mark ladder per var, capped 16/var by stride, every proposal
facing the admission null; thresholds are MARKS — excluded from the
multiplicative refine glide after it slid one out of range into a
constant column, wrong-kept). The exact road gains DEEP ESCALATION
(k<=5 when n_train<=100 — exact conditional rules live in small data)
and CREASE SEATS in its shortlist (the diversity rule's fourth
sighting: the step flood crowds |xi-xj| out of a correlation top-N).
TOOLS: compare/larger/smaller/switch are engine organs with receipt
chains — larger routes THROUGH compare (the owner's a-b<0 wiring; the
execution cycle's smallest trace). BATTERY 8/8
(mechanisms_promotion_battery.py): max mints the textbook identity
(+0.50*x0 +0.50*x1 +0.50*|x0-x1|, machine-exact, 3/3); the step world
mints thresholds AT 1 and 2; the blended conditional mints its exact
5-term form at n=48 AND n=96; noise 0/10 false; availability 5/5.
DUEL RE-RUN: wrong-confident 74 -> 2/100 (F5 max ZEROED by vocabulary,
not guards; F3 4->2), availability 20/20, Kepler intact. COST, said
plainly: discover at n=400 d=5 now averages 8.8s/call (max 24s) — the
step atoms make admission scans heavier; the efficiency ledger's
measure-first pass is the named home for reclaiming it. Remaining 2
leaks = poison-into-constants; cures queued: rival-form duel + THE
OUTLIER'S OWN LAW (owner design, same night).

## 2026-07-15 (night): THE OUTLIER'S OWN LAW (promotion #13 [EXPERIMENTAL]) — the duel gate closes at 0/100
Owner design, same night: "if the outlier is a plus something else,
can it quantify that something else to create a correlation pattern
and identify the model of the source?" discover() gains the outlier
pass: rows the law cannot carry are ISOLATED and their deviations
QUANTIFIED in units, then asked what they ARE. Three roads: (A') THE
CLEAN-MAJORITY SEARCH — the rival-form duel fused in: a simple
pure-variable form machine-exact on >=85% of rows, with the remainder
sitting exact grain multiples off it, SUPERSEDES the flexible fit
that had ABSORBED the poison; cells quarantined with receipts (row,
value, predicted, deviation), never banked. (A) grain-multiple
deviations of the admitted fit -> mis-entry quarantine + clean
refit. (B) SECOND SOURCE: >=24 flagged rows and a throwaway
discover() on (X_flagged, deviations) that mints past a
SCRAMBLED-deviation control -> the source model recorded on the law
node (news, not error). One round only; 0.35 flag cap ("a law that
calls a third of the data outlier is the wrong law"). BATTERY 5/5
(outlier_source_battery.py): poisoned sums cured 5/5 to the TRUE
constants (err 7e-15) with 6/6 cells quarantined; source world mints
+0.41*x1 from deviations; scrambled control quiet; clean worlds
untouched 5/5. THE DUEL GATE CLOSES: wrong-confident 74/100 (old
judge) -> 0/100, availability 20/20, Kepler machine-exact, 0 false
examiner fires — 4/4 gate checks. Three wrong-kept bugs cured en
route, each a lesson: the k<3 early-return killed the pass exactly
when the absorber hid its poison (guards moved below the clean-
majority road); rival_check's state restore REFIT on the
contaminated train and re-poisoned the cure (skipped on mis-entry —
clean exactness IS the contest); the flexible fit with step atoms
absorbs point poison entirely (isolation must run against SIMPLE
RIVAL FORMS — the duel and the outlier road are one mechanism).
v1 constants (5*MAD, 0.35 cap, 0.8 grid fraction, 0.15 trim) are
hand-set — tests-over-thresholds debt, filed.
OPEN ANOMALY, filed: one self-test invocation during the #13 gates
crashed with TypeError (unhashable set) in Net.get_doors; the
identical deterministic rerun (PYTHONHASHSEED=0, same code, full
capture) passed 11/11 with zero tracebacks and the crash has not
reproduced. Unexplained = unfinished: watch for recurrence; if seen
again, capture the full traceback and the findings ledger state.

## 2026-07-15 (night): EFFICIENCY PASS #1 (measure-first, ledger discipline)
Profiled: _exact_road = 17.7s of a 19.0s discover (621,021 lstsq —
the seat guarantees fed combinations() directly at d=5). Fix: bounded
diverse combo pools (k=1 sweeps everything; k>=2 over ~<=40 seats;
deep k>=4 pure-var-first, capped 26) with SINGLES GUARANTEED BY
CONSTRUCTION after the first re-gate caught the cap cutting x0/x1
from the blended sentence (the crowding disease's FIFTH sighting,
inside the efficiency fix itself — wrong-kept in the ledger). AFTER,
all gates re-run green: mechanisms 8/8 (discover 8.8 -> 1.23s/call,
7.2x), outlier road 5/5, 100-world duel 0/100 wrong-confident with
availability 20/20 (gate wall-clock 174 -> 40s), self-test 11/11.
Full ledger entry: LOCAL_PROCESSING.md, Efficiency pass #1.

## 2026-07-15 (night): CONTAINERS PROMOTED (promotion #14 [EXPERIMENTAL])
World-scoped truth is engine-native: open_world(container) sets
routing state with a receipt; teach(subject, relation, obj,
container=None) stamps every fact with the world it is true IN (a
door tag, in:<world> — zero new primitives, the probe's finding);
ask(subject, relation, container=None) routes by world — facts in
force answer, fiction INHERITS base one-way with an
inherited-from-base receipt, base NEVER inherits fiction, and
container-less facts (organ-internal fact_index writes) land in base
with a receipt. In-world contradictions flag into
container_tensions (both readings kept); cross-world difference
never flags. BATTERY 10/10 (containers_promotion_battery.py): the
probe's 8 checks through the engine organs + pickle round-trip
(worlds and the active container survive save/load) + catalog
registration (open_world/ask harvested). Self-test 11/11 with zero
tracebacks — the new tagged subject->object doors disturbed no
capability area. Duel not re-run (containers do not touch
discover()); noted, not skipped silently. THE WALL THIS BUYS: the
practice corpus contains fiction — E3 and practice-loop reading can
now stamp provenance before anything reaches base. Deferred to the
owner's call, as standing: wiring vet_intake/practice-loop to stamp
containers on the LIVE account.

## 2026-07-15 (night): THE WALKER PROMOTED (promotion #15 [EXPERIMENTAL]) — the kernel loop's first permanent slice
The execution cycle is engine-native: define_flow(name, steps)
authors process as NET CONTENT (flow:/step: nodes, readable specs —
equations of process); walk_flow(name, state) is the walker — do op
(a registered organ) -> take result door (declarative predicates
routed THROUGH the compare organ) -> return to main (hop cap
guaranteed; missing organs refused honestly); mint_chunk reifies a
winning chain as ONE node walkable by name (the function generator
v1). Every juncture receipts the door taken AND the doors bypassed
(the consideration law at the routing layer), and EVERY WALK lands
in the findings ledger (kind=flow-walk: outcome, hops, road) —
process leaves the same paper trail as knowledge. BATTERY 12/12
(flow_promotion_battery.py: the probe's 10 through engine organs +
catalog registration + the walk ledger); self-test 11/11, zero
tracebacks. SEGMENT REMAINDER, named: flow steps facing word-style
elections; piecewise flow supersession (clone the failing step for
the miner-named case, duel decides); the 07-13 interpreter attack
list (refraction/loops, rule interference, chunk correctness) now
has its execution substrate.

## 2026-07-15 (night): FLOW ELECTIONS + SUPERSESSION PROMOTED (promotion #16 [EXPERIMENTAL]) — the flow-structures design is COMPLETE
The sheet's three missing things are all engine organs now: PRESENCE
(#15 flows as net content), CONSIDERATION (bypass receipts at every
door), and ADAPTATION — flow_tally (wins by DECLARED success steps
over the walk ledger, recent-window like word elections), elect_flow
(champion by measured win rate; losers kept with tallies; the task
node carries an active/superseded chain — the read_floor pattern;
elections land in the ledger), branch_flow (piecewise supersession's
mechanical half: clone + graft one door before the default + the
steps it leads to; the miner names the condition, the election
decides, the loser is kept). BATTERY 6/6 (flow_election_battery.py):
one-call branch reproduced the adaptation duel (3/5 -> 5/5);
windowed re-election FLIPPED the champion on reversed fortunes with
the prior champion kept in the chain; window-vs-full-history
measurably disagree (recency is a choice, recorded per election).
Self-test 11/11, zero tracebacks. Carried caveat, not hidden:
step-level credit assignment is CRUDE (whole-walk outcome banks on
the flow, not per step — the word-elections fresh-eyes #1 caveat,
now at the flow level; per-step attribution is named segment work).

## 2026-07-17 — SESSION 1 OF THE ALPHA PUSH: the wall re-run, the one red CURED (the fresh-row court), and the totals wiring
THE WALL (handoff step 1): full 45-gate re-run against the night
engine as ONE pass — engine suite, the 37 promote batteries, the five
night promotion batteries, the verdict duel (4/4, wrong-confident
0/100 held), THE GAUNTLET (all datasets reproduce the 07-04 numbers;
KEPLER FLIPPED: "PREDICTED FAIL" → UNDERSTOOD +1.00*x0^1.5
machine-exact — the new judge's win on the gauntlet's own stage).
ONE RED: rounding battery 5/7 — sin(1.75x) lost its mark (two junk
waves seated at 1.753/1.7), sin(pi*x) demoted to PARTIAL. Honest
breakage the night's per-promotion gates never saw (they ran
self-test + own batteries, not the full wall).

THE PROMOTE ROAD HEALED FIRST: research's isaac.py was STALE
(pre-#11) — the night's engine work landed in dc directly; running
promote.py would have overwritten six promotions. research synced to
the dc engine (commit f565c8d) before any fix; the five night
batteries + verdict_port_gate + flow probes copied into research so
the road is self-contained.

THE CURE, three organs, each measured into place (research-first):
(1) _sharpen_k — a shrinking multiplicative grid on inside-parameters
(6 rounds, ~2e-5 relative resolution; the coarse 0.7/0.85/1.15/1.4
climb could not correct a 0.15% frequency error, and the beat such an
error leaves is EXACTLY what the replay leg fires on). Single-term
fits only: inside a blend, coordinate sharpening chased the co-fit's
noise (measured: walked 1.7527 AWAY from 1.75 — wrong-kept).
(2) _simple_rival — the clean-majority law one level up: a flexible
blend absorbs its own error (a pair of close waves imitates one wave
of slightly-wrong k by seating junk on its own beat). Each admitted
k-term is offered ALONE, sharpened on its clean ridge; the F-test
shape decides — the blend keeps its extra parts only if its edge PER
EXTRA PARAMETER beats what noise buys (measured: a 4-term blend's
train edge over the true single wave was 6.4e-5 = exactly
q*(1-r2)/n — pure parameter count, no signal). The solo road landed
k = 3.14159200 from a 3.1387 start.
(3) THE FRESH-ROW COURT for the rounding referee — train r2 CANNOT
arbitrate marks (measured: the TRUE mark 1.5 cost 3.0e-5 while the
FALSE mark 3.142-for-pi cost 2.2e-5 — they overlap); fresh rows can:
noise-chasing does not replicate on the held-out half, a real beat
does. A mark is adopted only if the displaced-alternative column
cannot predict the mark's held-out residual past a permuted null —
the replay's own question asked BEFORE adoption, so the referee and
the judge share ONE court instead of convicting each other's
verdicts. Referee tie widened to f=8 (chi2(1) 99.5th pct; f=4 refused
true marks on ~1-in-20 draws) — safe ONLY because the fresh-row court
now catches what the wider tie lets through.
ROUNDING 7/7 (1.5 and 1.75 said exactly; pi says 3.1415, coarse marks
refused; noise NO RULE). Re-gate green across the discover-heavy set:
mechanisms 8/8, outlier 5/5, containers 10/10, flow 12/12, elections
6/6, duel gate 4/4, lag 14/14, gravity 13/13, floor, told, engine
suite 11/11.

THE TOTALS WIRING (cross_check's named rung, audit battery FIRST —
A9a-d written and shown failing 4/4 before the mechanism): the audit
face detects exact-books totals structure (sum column over >=2 parts;
last-row totals row) and hands cross_check the row x column sum
checks. A broken sum marks the TUPLE false with repair doors (A9a:
3 doors, nothing blamed alone); clean books = zero flags (A9b); row x
column checks INTERSECT to a unique CORRECTED-CANDIDATE at the exact
cell with the exact value (A9c: r2:b, 31 → 24); ordinary tables get
no checks invented (A9d). A totals row is BOOKKEEPING — excluded from
the law pass and row audit, said in the report. Wrong-kept in the
detector: the first 90%-balanced bar declared NO STRUCTURE on the
very grid whose one corrupted cell was the point (8/9 rows); the bar
is now >=60% + >=3 balancing — the dissenting rows are exactly what
the cross-checks hunt. Audit battery 18/18; counts/summary/records/
render all carry the inconsistency numbers.

B3/B4 PREDICTIONS FILED (P10-P18 in dataops_bench/PREDICTIONS.md)
BEFORE any run, per the plan; bench_b3_sysid.py written. B1/B2 re-run
and B3/B4 first runs follow the promotion.

## 2026-07-17 (launch day, cont.) — THE VET AT THE FRONT DOOR: wired
## into the practice loop's banking path (battery-first, 22/22)
The named rung from promotion #10 ("wire into the live sparring/
practice loop") landed before his first practice conversation, per
the fresh-start ruling: admission discipline from the permanent
record's first entry. sparring.py gains extract_claims (v1 scope,
said: plus/minus arithmetic, digits + number words to twenty) and
vet_texts — every partner line carrying a checkable claim is vetted
through vet_intake BEFORE the banking road; a failing line is
INTERPRETED (kept verbatim at quarantine:practice with assumed-
intent doors — the typo concept) but never IMPLEMENTED (never
enters the corpus, never relearned as speech evidence); uncheckable
language flows the ordinary excess-null road — never a free pass,
never a quarantine. harvest() returns the vetted-out count; the
practice journal carries vetted_out per session. Battery V1-V4 in
test_sparring.py (written first, shown failing): false claim
"five plus five equals nine" quarantined with doors a->4/b->4/c->10
and ABSENT from the corpus; true claim "two plus two equals four"
banks; plain language identical to before. 22/22.

## 2026-07-17 (launch day, cont.) — KERNEL FIRST LIGHT: the drill
## session IS a flow (battery-first, sparring 27/27, flow 14/14)
The handoff's item C and the owner's base-loop/initiator law, made
real. ENGINE (gated): register_ext_op — THE INITIATOR'S DOOR: an
external act (conversation partner, file I/O) registers as a
runtime op the walker can run; the registry NEVER pickles
(__getstate__ drops it) — a resurrected mind honestly REFUSES
ext-op walks until its initiator re-registers (flow battery W13/
W14). STORE: run_drill_flow = the initiator + one walk — registers
drill_converse/drill_bank/drill_journal/drill_save as ext ops,
authors flow:drill ONCE as net content, then hands control to
walk_flow: THE BASE LOOP IS THE TOP LEVEL; the Python function
never sequences the pipeline. The drill's banking act carries the
vet inside (K3: a false claim arriving mid-conversation is
quarantined by the flow's own road). Battery K1-K5: the walk's road
[converse, bank, journal, save] on the ledger; real artifacts
(corpus, transcript, journal entry with vetted_out, mind saved);
resurrection honest; flow_tally counts the drill's walks and wins —
flow:drill is HIS to tally, branch, and elect. THE ACCEPTANCE TEST
(the sheet): from here, improving the drill = Isaac changing
flow:drill in his net (branch_flow/elect_flow) — never editing
Python. Code that accumulates domain decisions is the old trap
wearing the kernel's clothes.

## 2026-07-17 (launch day, cont.) — FRONTIER→CURRICULUM: the
## self-learning loop CLOSES (battery-first, sparring 30/30)
Handoff item 6, the owner's 07-15 design ("he just needs to see
that hey, this keeps losing in these conditions, group them and
find why") wired end to end: frontier_curriculum(account) features
every reply in his recent transcripts by the line he HEARD
(question-shaped / first word / length) with SILENCE as the failure
signal, and mine_commonality's null-gated differential names the
losing condition — a gap WITH evidence. The named condition builds
the next drill's scenario (repetition-teaching, targeted); nothing
named past the null = honest nothing, no invented curriculum (FC2).
FC3 = THE WHOLE LOOP IN ONE CHECK: planted life where questions
always met silence → 'ends_q=yes' NAMED → scenario built → drilled
through run_drill_flow (THE KERNEL — the walker as top level) →
re-probed: before=silence, after=learned-fragment ("i am fine thank
you my friend"). Weakness named → drilled → capability measurably
moved, every stage receipted in his own net.

## 2026-07-17 — the get_doors flake, SECOND SIGHTING (filed)
The frontier-curriculum promote wall went 31 gates green and the
engine suite struck the 07-15 open anomaly: TypeError unhashable
set, tail-line only (the wall then rightly REFUSED promotion). Hunt:
25 back-to-back engine-suite runs, identical cwd/env/seed — 0/25
reproduced. Bounds: 2 sightings, both inside promote walls, never
in direct runs. HARNESS CURE (dc promote.py): every failing gate's
FULL output now saves to experiments/runs/gate_failures/ — the
traceback can never be lost a third time. Filed in
KNOWN_LIMITS_ALPHA #13; the watch stands; promotion re-run on the
unchanged commit.

## 2026-07-17 (launch day, cont.) — THE DEEP FAILURE READ plumbed
## (the docs' "E3"; battery-first, sparring 33/33)
Owner: "lets get that plumbed and see if he makes any mistakes or
misses and corrects them later." read_failures(mind, home): every
failure receipt a life keeps — SILENCES from transcripts + WRONGS-
WITH-CORRECTIONS from the tutored road — featured by the context
that produced them (_line_features: ends_q/first/length/has_number);
the differential miner names what failures share past the null; the
top condition returns as a drill scenario (_scenario_for, shared
with frontier_curriculum). FR1: a condition living ONLY in the
correction road (has_number) named alone across sources (first
plant conflated ends_q — caught, fixed: plants must separate
conditions). FR2 curriculum returned. FR3 THE ARCHIVE IS READ,
NEVER WRITTEN — every byte identical after; the finding lands in
the reading mind. v1 sources said: transcripts + speech:wrong (vet
quarantines keep claims, not lines — named future source).

## 2026-07-17 (evening) — PER-DATASET CONTAINERS + CROSS-DOMAIN
## CRYSTALLIZATION (the feeding design, promotion #17)
Owner, settling the feeding direction and the standing stamping item
in one design: "each dataset is defaulted to its own container, and
it can crystalize the container structures into cross domain
structures." Probe-first (container_crystal_probe.py, 8/8 after two
kept wrong-predictions), then the engine: discover() gained
container= with the per-dataset default (bare feed -> data-<name>;
open world captures; explicit wins) + the earned verdict stored on
the law node; _teach_fact made container-aware (run 1 MEASURED the
old road leaking every discovered explains-fact into base's answers
— the wound, closed); _install_law stamps the world a law is told
in; crystallize_forms() mints lawform: parents across containers
with THE TOOTH (only UNDERSTOOD-in-own-container laws crystallize —
kinship between confusions is not knowledge; scrambled-assignment
null dies by exactly this) and tell_law's own crc32 naming (told +
crystallized families UNIFY — proven: lawform:6b98f4af from both
roads). Selection composes: which_law right per world, NONE on the
interleaved mix — the >=2-laws precondition of the selection gauge,
first demonstrated. Battery container_crystal_battery.py 8/8 joins
the permanent wall. Curriculum ruling same message: staging =
convenience, never a gate.

## 2026-07-18 — THE FIRST MEAL STAGED + MEASURED-JITTER KINSHIP
## (promotion #18)
Meal 1 built (meal1_first_laws.py, dry/--live): REAL sky + Boyle's
actual 1662 table. Two findings from the first real food, both
cured through the full road: (1) 6-7 row dishes REFUSED (3 training
rows after holdout) — cured by more real moons (more knowledge, not
looser gates; both moon tables now 11-12 real bodies); (2)
MEASURED-JITTER KINSHIP — real data earned exponents 1.5/1.49938/
1.5007 and machine-identical form grouping called kin strangers (0
families, wrong-kept in the battery's B9): crystallize_forms now
groups by atom structure with inner constants at the family
machinery's own 5% tolerance, family id snapped to quarter-step
ruler marks — Kepler's form is ONE node (lawform:6b98f4af) told,
discovered, synthetic or real. Dry receipts: 4/4 UNDERSTOOD
(+1.00*a^1.5; +1413.86*V^-1 from Boyle's own rows, r2 0.99995), ONE
family across three sky containers, Pluto 247.90 yr (true 248.09,
0.07%), Adrastea 0.2979 d (true 0.2983), Pan 0.5761 d (true 0.575),
selection 4/4 named + refusal on the interleave. Battery grown to
9/9 (B9 = the real-sky case, permanent). His account untouched —
the --live road awaits the owner's go.

## 2026-07-18 — ALPHA RUNS FULL: MEALS 1+2 LIVE, THE DIVERSITY RULING
Owner: "run full in the alpha v.1... its mainly diversity that im
interested in" (captured on the sheet: FORM DIVERSITY OVER VOLUME —
size revalidates, new forms teach). MEAL 1 LIVE (his first real
food): real sky + Boyle 1662 — 4/4 UNDERSTOOD, Kepler ONE family
across three sky containers, Pluto 0.07% never-fed, THE SELECTION
GAUGE FIRED FOR THE FIRST TIME (laws 0->4, precision 4/4 = 1.0).
MEAL 2 LIVE (the diversity plate): galileo-1604 UNDERSTOOD
(+33.08*t^2 from the folio 107v punti; tick-9 receipt 2678 vs 2673),
atmosphere-1976 UNDERSTOOD (107.24*exp(-0.125*alt), 8 km scale
height), co2-maunaloa PARTIAL (+0.20*t^1.5 +318.33, r2 0.9988,
residual honestly dark). TWO NAMED FRONTIERS from honest refusals:
(1) CROSS-VARIABLE POWER PRODUCTS — planet-gravity (g=66.74*M/R^2,
11 real bodies) NO RULE, and the diagnostic settles WHY: n=200
well-conditioned synthetic ALSO fails (PARTIAL 0.71 surrogate) —
the enumerator's vocabulary cannot say x0*x1^-2; the wall is the
vocabulary, not the evidence (basic-mechanisms-style campaign
queued); side wart filed: lag atoms joined that surrogate on a
NON-series table. (2) sunspots-1700 NO RULE — the pre-named
oscillatory-lag leak (2026-07-16 bench) confirmed on 326 years of
real SILSO data. Account after: 582 nodes, 7 laws, selection 5/5
precision 1.0, probe 0.277s. Road-trial records #7-#8.

## 2026-07-18 — THE GROWING GRAMMAR, rung 1 probed 7/7
Owner named the root wound ("the algebra enumeration stuff is hand
coded still... we need isaac to work harder and look for novel
solutions, not just the ones we programmed") — the genesis loop
pointed at algebra. harder_road_probe.py 7/7: scream (pool) -> aim
(ablation, decoy excluded) -> compose (powered products the menu
never nested, log-ruler informer) -> the ORDINARY court -> mint ->
GROW (earned word offered first; Coulomb world solved with no new
search; grown vocabulary crystallizes cross-domain). Three lessons
wrong-kept incl. the run-3 jewel: the real planets' PARTIAL is the
machine being RIGHT (rotation/oblateness IS the above-floor
leftover). Full capture + ladder on the design sheet. NEXT = the
promotion campaign (registry generalized to powered products;
harder road as engine organ; rank-ruler pool; effort dial under the
consideration law).
