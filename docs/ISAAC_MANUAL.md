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
   F-test at the noise ceiling; block-permutation needed for autocorrelated
   targets — the last is still an open item, guarded by a term cap.)
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
  fly-types but still in the shared birds group). **Still-open limits,
  measured in the battery:** no admission null (249 types form from pure
  chance co-occurrence — C3) and the scale knee (0.04 s @ 50 nodes,
  2.9 s @ 200, ~420 s @ 800 — C5).
- `teach_not(subject, prop)` — a positive negative: indexes a cannot-fact
  (the reasoning layer honors it) AND writes a first-class `not_<prop>`
  door (tag `neg`, so negatives never leak into sequence generation) —
  crystallization can share it (penguins and ostriches share `not_fly`)
  and be vetoed by it. Known-different never collapses; only unknown may.
- **WRONG IS KEPT AND CLASSIFIED (owner's law, 2026-07-03).** "Knowing
  what is right is intelligence. Knowing what is wrong is wisdom." Every
  crystallized type is tested against its chance-null (the same context
  with door targets shuffled, degrees preserved; scored by the BEST
  structure chance produces — selection-corrected). Types that fail are
  neither prevented nor deleted: they are filed in `isaac.wrong_types`
  with the WHY on the node meta (`verdict: wrong`, `why_wrong: ...`) —
  error itself is learnable material. Sound types carry `verdict: sound`.
  Downstream behavior is deliberately unchanged: no pruning, no
  importance-weighting (the old trap — "we fell into that by telling it
  what was important and it broke everything"). Battery C3: 249/249
  chance types filed wrong with reasons; C1 category types all sound.
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
- `crystallize_senses(node, min_shared=2)` — the crystallizer turned
  inward on ONE node: every occurrence of the node (from
  `observed_sequences`) carries the context it appeared in; occurrences
  sharing ≥ `min_shared` context tokens are linked into clusters; each
  cluster becomes a SENSE (its own in-doors, out-doors, context) stored
  on the node's meta. Returns the sense list. Gives a node internal
  structure instead of one flat door pile. **Limit:** the link rule is a
  fixed count, not a statistical test (pre-dates law 2).
- `route(node, incoming)` — read through a node BY SENSE: `incoming` (one
  token or a set of context tokens) is overlap-matched against each
  sense's in-doors + context; the best-matching sense's out-doors are
  returned. Falls back to the node's flat `seq` door-set when no sense
  matches.

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
- `crystallize_features(X, y, lens=)` — one concept-node per class whose
  doors are **observed quantile log-densities** (proximity doors). Legacy
  box meta still written for `recognize_matrix`/old scripts.
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
- Limits (honest): 2D/3D point trajectories with identities given (the
  pixel bridge — render → tracker → these methods — is the named next
  keystone); all-pairs cost O(n²) per frame set; bounded certification
  needs enough revisits (weak evidence is refused, by design — earn more
  frames or probe deliberately); sprung classification exists in the
  harness (`spatial/engine.py`) but not yet in-engine.
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
    grids; exp decay AND growth; **powers** (±0.5, ±1, −2, 1.5 grids);
    pairwise cos/sin/cosh of differences. Grids PROPOSE scale parameters
    (unreachable by regression); hill-climbing refits SHARPEN them.
  - **staged, null-gated admission**: candidates grow only around admitted
    terms; a term must beat the max-over-candidates correlation on
    permuted residuals; trial shortlist is structurally diverse (raw-var
    candidates guaranteed trials); completers judged by **F-test**
    (significance decides; genuine ties go to the simpler form);
    `max_terms=16` brake (autocorrelated targets — see law 1).
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
  `experiments/confidence_curve.py` whenever the enumerator changes.
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
  n < ~400 (provisional rule); frequency reach ≈ 2× grid max; nested
  nonlinearities land in CAPTURED by design; iid permutation invalid on
  autocorrelated targets (cap + pending block-perm); rational functions
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

- Engine self-test (10 areas): language, math, logic, reasoning, decompose,
  persistence, waves, tracking, discovery, rivalry.
- Harness (`experiments/`): six rebuild proofs (doors, composition,
  enumerator, waves, interference, entity-status); batteries with per-run
  CSVs (`wave_battery`, `discovery_battery`); adversarial
  `redteam_discovery`; real-data (`covtype_*`, `higgs_real_test`,
  `experiments/gauntlet.py` — 10 datasets, one pipeline);
  `experiments/cross_domain.py`; `condensation_scaling`;
  `experiments/clock_world.py`; `registration_perception`;
  `ideals_differentia`; `digits_structural`. Run logs from this repo:
  `experiments/runs/2026-07-03/`.
- Reports: `experiments/RESULTS.md`, `experiments/WAVE_TEST_REPORT.md`,
  `docs/WRITEUP_FOR_REVIEW.md` (§7 = verify-everything commands).

## 11. Current honest scoreboard (2026-07-02) — [RECORDED — script not in this repo or data required; not independently re-verified] (the gauntlet and cross-domain scripts ARE now in `experiments/`, but the scoreboard numbers need their datasets and long runs)

Competitive: covtype 94.4% (record ~97.5); exact law recovery incl.
off-grid damped oscillation; cross-domain transfer. Commodity-or-below:
MNIST 95.2 / Fashion 76.5 / CIFAR 32.6 / Omniglot 1-shot 51.6 / FSDD 92
mixed–54 transfer. Differentiated (the product): verdicts + scope +
rivals + probes + precedent-dossier explanations + cross-session
inheritance — honesty machinery wrapped around discovery, on a CPU,
readable end to end.

## 12. What does NOT exist yet (so nobody assumes it)

No abstention in classify_features; no compound doors in-engine; uptake
composition harness-only; no FCA lattice (overlap merging); no
shrug→discover reflex; no block-permutation null; no symbolic/token
challenges in discover(); no CAPTURED→law graduation loop; no
learned-invariant perception (phase 4); no curiosity — challenges arrive
from outside, and the probe queue is proposals only. The clock-reading
harness readout is broken (22.9% — harness bug, engine unimplicated).
