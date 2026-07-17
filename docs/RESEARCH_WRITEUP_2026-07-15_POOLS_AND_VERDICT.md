# RESEARCH WRITEUP — 2026-07-15: THE NEW JUDGE AND THE POOLS' THREE CLIMBS
**Plain-language research record (the writeup law: what was built, what
the structures look like, how information is represented, what was
found, how it performs, where it breaks). Companion to
POOL_BRANCH_EVAL_2026-07-15.md (the verdict sheet) and
verdict_rewrite_probe.py / the three pool_*.py probes (the code).
dc-only, like the testing-segment records.**

---

## PART 1 — THE NEW JUDGE (the §2b verdict rewrite, reference build)

### What was built
Isaac's judge is the piece of code that looks at a candidate equation
and decides: do we UNDERSTAND this data, or not. The old judge was one
number: if the equation matched 90% of the held-out variance
(r² ≥ 0.9), stamp UNDERSTOOD. Four measured attack families showed
that number can be earned by WRONG equations.

The new judge (reference v3, `experiments/verdict_rewrite_probe.py`,
23/23) is a court with three independent examiners and a metrology
rule:

1. **The exact road.** Before any statistics, try tiny formulas
   (1–3 terms). A hit must reproduce EVERY row to machine precision —
   on the training half AND the held-out half. Noise cannot fake
   machine-perfection on rows the fit never saw (measured: 0/20 fake
   stamps on noise at n=8). This is how Kepler's law with only 8
   planets gets stamped — where the OLD judge found nothing at all
   (r² = −2.94).

2. **The replay (leg 1).** After fitting, take the leftover error on
   held-out rows and ask every known building block: "can YOU predict
   this leftover?" The bar is selection-corrected: because we ask many
   candidates, the threshold is the maximum score over all of them on
   shuffled leftovers (the 119/120 lesson). If anything clears it,
   something is missing — never stamp UNDERSTOOD.

3. **The pool (leg 2).** A frozen random net — the kiddie pool — asks
   the grammar-free version of the same question: can ANY cheap
   function of the inputs predict this leftover better than its own
   shuffled self? This catches structure that no known building block
   expresses (a conditional rule, a bent form).

4. **The floor rule (the 13-inch foot).** UNDERSTOOD also requires the
   leftover to sit within 3× an EVIDENCED measurement floor — a floor
   read from the data's grain, from repeated measurements, or told by
   the owner. No floor evidenced and not machine-exact? The verdict is
   BEST-RESIDUAL — "here is the best equation so far, and I cannot
   certify it," never a confident stamp. Constants also snap to the
   coarsest ruler marks that survive held-out refit: 3.000154 measured
   on a coarse ruler honestly says 3.

### How it represents things
The verdict is no longer a number — it is a RECORD: the equation, the
floor and its provenance, each examiner's state (fired / quiet /
bypassed-with-reason), and the residual in units. Every leg either
fires or leaves a receipt saying why not (the consideration law).

### What was found, and how it performs
- The additive hole is cured: given a correlated pair where the old
  judge shipped `0.32*x0*x1` as UNDERSTOOD, the new judge recovers
  exactly `x0 + x1` (4/5 seeds; never confidently wrong 0/5).
- Poisoned data (±1 errors in 10% / 5% of cells): confidently-wrong
  0/10 across both rates — and in the 10% case the POOL was the only
  examiner that fired (replay quiet at 0.465 vs bar 0.629; pool scream
  0.890 vs 0.062). The second leg earns its seat.
- The judge does not chase the ruler's own artifacts: a true law on a
  coarse grain leaves a sawtooth-shaped leftover that belongs to the
  instrument, not the world — pool quiet 4/4, law stamped clean.
- Availability cost, filed: under poison the true form is recovered
  0/10 (an impostor term gets admitted first and cannot be displaced).
  Safety is solved; recovery needs the RIVAL-FORM DUEL (already proven
  3/3 elsewhere) — a port requirement, not a mystery.
- Cost: 0.77 s per full three-examiner verdict at n=400.

### Where it breaks / boundaries
Grain-only floors under-evidence real process noise (known, kept): an
honest PARTIAL results until a repeats road or a told sigma arrives.
The pool leg's competence starts at n≈48 rows (measured); below that
it bypasses with a receipt.

---

## PART 2 — RECURSIVE POOLS: relations between structures themselves

### The idea (owner): "what if we recursively applied these pools to
### find relational information about the structures themselves"
A matrix can hold pairwise relations between raw things — that is all
it can hold. The climb: make each discovered STRUCTURE a thing with
descriptors, and point the same instruments at the descriptors.
Relations among structures become ordinary channels one level up.

### What the structure actually looks like
```
LEVEL 0 — raw data, 10 groups per episode, each its own clean law:
  group A: 40 rows of (x, y) with y = a_A · x
  group B: 40 rows of (x, y) with y = a_B · x
  ...      (nothing relational is visible inside any group's rows)

LEVEL 1 — the DESCRIPTOR TABLE (one row per episode, 240 episodes):
  episode |  a_A    a_B    a_D  ...  (9 columns)   | target: a_C
     1    | +1.31  −0.62  +0.94 ...                |  −0.81
     2    | −1.75  +0.94  −1.22 ...                |  −1.65
    ...
  planted truth: a_C = a_A · a_B every episode — a relation between
  LAWS, not between data points. Marginally invisible (product of
  signed constants: correlation with either factor ≈ 0).
```
The pool is level-agnostic by construction — a frozen random
projection does not know what its channels mean — so the SAME
instrument that reads raw channels reads descriptor channels.

### What was found, with numbers
- Level 0 is honestly blind: 20/20 quiet on any group's own residual
  (the relation does not live in raw data).
- Level 1 detection: pool screams on the descriptor table (+0.536 vs
  null99 −0.431). Attribution names EXACTLY {A, B} of 9 candidates
  (0.93 / 1.00 vs threshold 0.10); plain correlation sees NOTHING
  (0.110 vs 0.189) — two channels that look unrelated to the target,
  told apart through the frozen net.
- GENESIS, pools removed: the engine mints the readable equation
  `a_C = 1.00 · a_A · a_B`, exact to 3e-15, predicts 12 UNSEEN
  episodes' constants to 2e-15, and composes down through the level-0
  law to predict raw y on fresh x to 4e-15. A relation between laws,
  discovered, named, minted readable, proven without the scaffolding.
- Scrambled control: alignment permuted → pool quiet AND the engine
  refuses (NO RULE). Noise robustness: at σ = 0.05 / 0.2 detection and
  naming hold exactly, mint errors scale linearly (3.96× measured vs
  4× predicted), no false exactness. Level 2+ follows by induction: a
  minted relation node has descriptors too.

### Where it breaks
- **The judge is the weak floor, not the pools** (BROKEN, verifier
  upheld): plant a relation OUTSIDE the equation grammar —
  a_C = max(a_A, a_B) — and the pools still point perfectly (scream;
  name {A,B}), but the engine's OLD judge stamps a confident
  UNDERSTOOD (r² = 0.99945) on a 9-term sin/cos/exp impostor hugging
  the max-surface, with error 7e-2 on an EXACT world. The single-lens
  pool gate is quiet on that residual (−0.740 vs −0.547): after a
  9-term fit the leftover is a thin high-frequency crease along the
  fold line a_A ≈ a_B — too sharp for smooth frozen features to grab.
  THE CURE IS ALREADY BUILT: v3's floor rule refuses this exact shape
  (exact world, floor unevidenced, residual astronomically above
  machine-zero → BEST-RESIDUAL, never UNDERSTOOD). Port urgency:
  every mint the recursion produces INHERITS THE JUDGE.
- Multi-target scanning needs a family-wise bar: scan all 10 possible
  targets instead of the planted one and you buy one confident false
  scream (survives 5/5 fresh nulls, p ≈ 0.003) — N lenses = N chances
  to hallucinate, the selection lesson at level 1.

---

## PART 3 — THE DROP ALGEBRA: how two contributors combine

### The idea (owner): "compare how parts get transformed compared to
### base to see how they abate"
Ablation through the pool measures NECESSITY: d_i = how much
prediction quality dies when channel i is scrambled. The finding
settled by the probe: the DEVIATION FROM ADDITIVITY of these death
tolls is itself a diagnostic. For a pair (i, j):

    S = d_i + d_j − d_ij      (solo drops minus the both-at-once drop)

```
ADDITIVE   (y = 1.2·x0 + 0.8·x2):  two separate pipes.
           Kill each alone: lose its share. Kill both: lose the sum.
           S ≈ 0                    measured S = −0.073, band ±0.075
SYNERGY    (y = 0.9·x1·x3):        two keys to one lock.
           Kill EITHER alone: everything dies. Kill both: same death.
           S >> 0                   measured S = +1.452, band ±0.206
REDUNDANCY (x4 = x1 + tiny noise): two copies of the same key.
           Kill one: twin covers. Kill both: everything dies.
           S << 0                   measured S = −0.435, band ±0.081
```
The instrument carries a measured self-correction: tanh features mix
channels slightly, so even a true additive pair shows a small S bias.
A planted KNOWN-additive pair inside the probe measures that bias
(0.0052 of pair scale) and the classification margin includes it —
measured, never hand-set.

### How it performs under attack
- Twins tightened from noise 0.05 to 0.005 (correlation 0.99999):
  REDUNDANCY holds 3/3 at 3.5–4.2× margin — and the feared
  solo-naming blindness NEVER OPENED (the solos symmetrize toward
  0.49/0.49 because tanh mixing means scrambling one twin still
  corrupts every hidden unit). The probe's own filed worry, falsified
  in its favor.
- Wrong pair hints invent nothing: non-contributing pairs land at
  0.10–0.52× band; naming is hint-independent.
- Mixed world (synergy pair + additive bystander in one law): all
  three junction calls correct, naming exact, 0 false names.

### Where it breaks / the vocabulary's edge
A pure THREE-WAY product saturates pairwise ablation: killing any one
channel kills everything, so solo ≈ pair ≈ triple drop (1.65 ± 0.09)
and the pairwise output is indistinguishable from genuine 2-way
synergy. Correct-but-incomplete, not misleading — and the cure is one
line: the order-3 statistic S3 = d_i + d_j + d_k − d_ijk reads +3.364
(≈ 2× capture) for a true triple vs ≈ 1× for a real 2-way. The kinds
ladder, honestly stated: pairs proven, order-3 named and cheap, not
yet claimed.

---

## PART 4 — E1, THE BRIDGE TO LANGUAGE

### The idea (owner): "how do we test this on non mathematical
### structures? like english?"
Pools never worked on math — they worked on CHANNELS. A
sentence-event's reading becomes a channel vector the moment each
feature value becomes an indicator column:

```
event: {voice: passive, tense: past, deco: comma, subj: cat, ...}
   →   [0 1 | 1 0 | 0 1 0 | 1 0 0 0 | ...]   (16 indicator columns)
```

### The world and why it matters
Planted rule: FAIL iff voice and tense DISAGREE with the planted
agreement pattern — fail = XOR(voice=passive, tense=perfect), plus 5%
verdict noise. At 50/50 base rates XOR has PERFECTLY FLAT marginals:
P(fail | passive) = P(fail | active) = 0.5. Isaac's own frontier miner
(mine_commonality) is a per-feature-value statistic, so it is blind
BY THEOREM — measured blind 3/3 seeds and 20/20 in the sweep. This is
not a toy: conjunctive frontiers in his real practice history are
invisible to the current self-assessment organ.

### The funnel, step by step, with the numbers
1. POOL SCREAMS on the indicator table: capture +0.64..0.70 vs null
   ≈ −0.2 → "a rule exists," grammar-free.
2. GROUPED ABLATION (scramble a whole feature's indicator block with
   one shared permutation) names exactly {voice, tense}: drops
   1.1–1.3 vs decoy threshold 0.03–0.05; subj/verb/junk ≤ 0.02.
3. DROP ALGEBRA on the named pair: S ≈ +1.2 vs band ±0.08 → SYNERGY,
   the conjunction's fingerprint (jointly necessary).
4. ARTICULATION collapses to a 2×2 fail-rate table on training rows:
   ```
                tense=past   tense=perfect
   voice=active     0.05          0.95
   voice=passive    0.95          0.05
   ```
   Cells > 0.5 read off the XOR rule EXACTLY; held-out verdict
   accuracy 0.91–0.96 = the 5% noise ceiling. The search that was
   2^k subsets became one pair and one small table — readable,
   evidenced, pools removed.

### How it performs under attack
- 20-seed sweep: 7/8 checks perfect; the one failure isolated to seed
  1004 where an innocent squeaked over a thin threshold at 1.4× (the
  real cause sat at ~90× threshold every seed).
- Skewed base rates (tense 70/30): funnel unaffected (names exact,
  SYNERGY at 9–13× band, articulation 0.947–0.973); the miner starts
  seeing again because marginal signal returns — correct behavior on
  both sides.
- Autonomy: remove the oracle pair-hint and choose the pair from the
  named set — identical results end to end. The scaffold is
  convenience, not load-bearing (production still owes the ~15-line
  chooser).

### Where it breaks
- CORRELATED INNOCENTS (the important one for language): make subj
  travel with voice (ρ ≈ 0.55, causally innocent) and the funnel
  over-names it 3/3 seeds at 1.6–2.7× threshold. Mechanism, measured:
  the decoy null calibrates the zero for an UNCORRELATED channel, but
  the readout genuinely leans a little on a correlated proxy, so
  scrambling it genuinely hurts. The true pair still towers 15–36×
  above the proxy, and the branch's claims were scoped to independent
  features (in-scope control clean) — but correlated features are the
  NORM in real language, so the null must grow correlated decoys (or
  a conditional permutation) BEFORE E3 runs on his real receipts.
- THE BASE-RATE TRAP (gate design): on a rare three-way rule (~8%
  fail rate), the articulation gate "accuracy ≥ 0.90" is passed by an
  empty rule that predicts "always passes" (0.911) while recovering
  NOTHING. The gate must demand BEATING THE ALL-PASS PREDICTOR, not
  an absolute score. (The honest 2×2×2 table closes the same world at
  0.96 vs base 0.88.)

---

## PART 5 — WHAT TONIGHT MEANS AT THE THEORY LEVEL
- The keystone held up as machinery: a structure (a law) was reified
  into a thing with descriptors, and the SAME unchanged instrument
  read relations among structures — representation → processing →
  new representation, one full turn of the crank, level 0 → level 1,
  with the mint proven and composed back down to raw prediction.
- The instruments (pools) point reliably across every world family
  tried — numeric, categorical, relational, mixed — and every
  deliverable stayed readable (an equation, a named pair, a small
  table). The scaffolding came down every time.
- The single deepest liability is now precisely located: THE JUDGE.
  The old r²-stamp fails identically at level 0 (additive hole) and
  level 1 (max relation), and recursion multiplies exposure — every
  minted level feeds the next. The v3 rewrite refuses every measured
  failure shape so far; porting it into the engine, with the
  rival-form duel, is the gate everything else queues behind.
- One statistical discipline showed up in four costumes: thresholds
  estimated from few samples + many simultaneous questions = rare
  confident false names. Family-wise bars, studentized/correlated
  decoys — one cure family, filed with numbers.

## THE QUEUE THIS SETS (owner's call on order)
1. §2b ENGINE PORT + gates (gauntlet, 100-world duel, confidence
   curve) + rival-form duel — the judge everything inherits.
2. Naming-null hardening (correlated decoys, family-wise scan bar,
   studentization) — cheap, unblocks E3.
3. E3 ON THE REAL ACCOUNT: the pool funnel over his actual practice
   receipts — first look at what marginal mining never saw.
4. S3 (order-3) + all-pass-beating articulation gate + the pair
   chooser — small, closes the measured holes.

---

## PART 6 — THE COMPARISON WORDS (added same night, owner's design)

### The question that started it
The owner, reading Part 2's break: "does it have a way to show simple
logic structures? if a−b is <0 (negative), then b>a?" The answer was
no — the equation vocabulary had powers, products, waves, decay, and
lags, but not one comparison. Three of the night's exhibits (the max
relation, the blended conditional, the plant step) were the same
missing word in different costumes. His follow-up set the design:
route it through the tool structures, and add every basic computer
mechanism to the toolkit.

### What was built (probe-proven 12/12; engine promotion queued)
One mechanism family in two dialects:

DIALECT 1 — new WORDS for the equation grammar:
```
|a−b|      the CREASE — his a−b with direction dropped. One atom
           makes max plain algebra:  max(a,b) = (a + b + |a−b|) / 2
[x > t]    the SWITCH — thresholds proposed from the data on ruler
           marks and deciles, never hand-set (a threshold is a
           constant, so the ruler discipline applies to it too)
[f]·xi·xj  the GATED PRODUCT — a switch routed into a product
```
DIALECT 2 — TOOLS that route, with receipts: compare, larger,
smaller, switch. larger(a,b) literally calls compare(a,b) and carries
the receipt chain — the "if a−b is negative, then b>a" wiring made
visible and replayable.

THE BRIDGE between dialects: identity recognition. The minted
equation `0.5·x0 + 0.5·x1 + 0.5·|x0−x1|` was checked numerically and
IS larger(x0,x1) — so the mint doors onto the tool node. Two
representations of one law, joined: the keystone move again.

### What happened to the night's broken worlds, with numbers
- THE MAX WORLD (Part 2's one BROKEN): now mints machine-exact in one
  line — `0.5·x0 + 0.5·x1 + 0.5·|x0−x1|`, residual 4e-16, stamped by
  the exact road. The crease residual the pool couldn't grab is now a
  word the grammar can say.
- THE STEP WORLD (v3's V5 refusal): now UNDERSTOOD as
  `2·x0 − 1.5·[x1>2] + 1.5·[x1>1]` — the thresholds were FOUND at
  exactly 1 and 2 (proposed on the mark ladder, earned by admission),
  amplitudes ±1.5, residual at the told floor.
- THE BLENDED WORLD: the honest story of the night. The words now
  exist, but greedy one-at-a-time search could not assemble the
  five-word sentence at 48 training rows (prediction falsified, KEPT)
  — it fit a wrong-basin compromise and the new judge correctly
  refused it, while the OLD judge shipped `0.838·[f]·x0·x1` as
  UNDERSTOOD: new words hand the old judge new ways to be confidently
  wrong. The judge rewrite stays the gate. The cure, measured: the
  DEEP EXACT ROAD (search up to 5 terms, machine-exactness on unseen
  rows as the guard) recovered the exact form —
  `[f]·x0·x1 − f·x1 − f·x0 + x1 + x0`, held-out error 3e-15, zero
  false stamps in 30 noise controls. En route, a diagnosis worth
  keeping: the shortlist was clogged by CLONES (on integer data
  [x>6] and [x>6.5] are the same column; a binary flag's powers and
  lag-shifts are copies of itself) — duplicates vote as a bloc and
  starve real terms out of any correlation-ranked shortlist. Dedupe
  before the cut; filed as a port lesson for the whole pool.
- THE COST OF NEW WORDS, measured not assumed: with the enriched
  vocabulary, noise worlds 0/20 false UNDERSTOOD, true-law worlds
  20/20 stamped with 0 false surprise fires — no safety or
  availability toll at these scales (the selection-corrected bar
  rises automatically with pool size, as designed).

### What this opens
- The mechanisms register as TOOL NODES at promotion (consideration
  law: consulted or bypassed with receipts), joining the atoms so the
  same mechanism is sayable in equations AND routable in process.
- Named, deferred, honest: hinge, sign, remainder/parity — the next
  family members; remainder connects to the period machinery.
- TODO (owner's order, same message): MULTI-STEP PROCESSING /
  CHAINING — the interpreter segment's kernel-loop half. The routing
  receipts here (larger→compare) are its smallest seed: a two-step
  chain with a replayable trail.

---

## PART 7 — THE JUDGE MOVES IN (the S2b engine port, promotion #11)

### What was done
The reference judge from Part 1 left the lab and moved into the
engine itself: `discover()` now runs the exact road, the replay, the
pool meter, and the floor certificate on every discovery. The coarse
verdict names (UNDERSTOOD / PARTIAL / CAPTURED / NO RULE) are
unchanged for every consumer, but UNDERSTOOD is now EARNED: the
equation must explain held-out data AND leave a leftover that no
candidate form and no cheap function can predict AND not sit above an
evidenced noise floor. r-squared still rides along — as a reported
number, which is all it ever deserved to be.

### The duel, measured (the promotion gate the plan demanded)
100 worlds with known truths, old judge vs new, wrong-confident =
UNDERSTOOD while missing the known truth on fresh rows:
```
                    old judge     new judge
  true laws          0/20 wrong    0/20 wrong   (20/20 stamped — kept)
  additive hole     18/20 wrong    0/20
  near-miss poison  20/20 wrong    4/20
  blended rule      16/20 wrong    0/20
  max relation      20/20 wrong    5/20
  TOTAL             74/100         9/100
  Kepler n=8        NO RULE       UNDERSTOOD (machine-exact)
```
True-law availability stayed perfect with ZERO false examiner fires,
and the engine's own 11-area self-test suite passes untouched.

### What the port itself taught (the research part)
- **The first ported run collapsed availability to 2/20 — and the
  examiners were innocent.** The receipts showed both legs quiet;
  the killer was my own naively-ported grain-floor reader
  hallucinating a microscopic "grain" on continuous data (at n=400
  the tolerance window, which scales with the multiple, eventually
  covers the whole number line — the consistency test becomes
  vacuous), so every honest law sat "above floor." The engine
  ALREADY OWNED the cured organ (coarsest-consistent grain, promotion
  #8), and swapping the naive reader for the real `read_floor`
  restored 20/20 instantly. Same story on the repeats road: my naive
  port was poison-inflatable — the exact self-blinding disease the
  campaign documented — while the engine's consensus-ejection version
  (promotions #6-7) already refused it. LESSON, kept: never ship a
  rival reader for an organ that exists; the reuse checklist is not
  bureaucracy, it is where the cures live.
- **The exact road went blind on the easiest world** (y = x0+x1!)
  until the family-bloc disease was cured a second time: refine-
  spawned atom variants (pow 1.72, pow 1.98, exp -0.175...) of ONE
  variable flooded the correlation shortlist and crowded out the bare
  x0 and x1. The fix reuses the enumerator's own move: pure-variable
  polynomial terms are GUARANTEED a seat in the combo pool
  (structural diversity beats top-N correlation, third sighting
  tonight).

### The nine that remain, named exactly
- FOUR near-miss worlds where the poison is absorbed into the
  CONSTANTS: examiners honestly quiet (the 16-term fit soaks the bend
  into atoms; the leftover is genuinely structureless), the floor
  honestly covers the residual — the wrongness lives in coefficients
  no examiner reads. The cure is already a filed port requirement:
  the RIVAL-FORM DUEL (scream > margin > parsimony, proven 3/3),
  which contests the admitted form against simple rivals.
- FIVE max-relation worlds where the crease signal sat under the
  replay's selection-corrected bar (obs 0.17-0.36 vs thr 0.32-0.54).
  These become trivially exact the moment |a−b| is a WORD — the
  mechanisms atoms promotion, next in the queue, at which point the
  exact road stamps the true form at machine precision and this class
  goes to zero the honest way: not by a better guard, by a richer
  vocabulary.

### What rides on every discovery now
`certificate` (machine-exact / within floor / above floor /
uncertified — with the floor's provenance), `floor`, and `legs` (each
examiner's state with obs-vs-threshold receipts, or its bypass reason
— the consideration law) — in the result, the findings ledger, and
the law node's meta. Downstream exactness consumers (the audit,
cross_check) can now read certification instead of inferring it from
r-squared, which is the plan's §2b promise delivered.

---

## PART 8 — THE WORDS MOVE IN (mechanisms promotion #12)

### What was done
Part 6's comparison words left the lab too: the CREASE `|xi−xj|` and
the SWITCH `[xi>t]` are now atoms in the engine's own vocabulary, and
compare/larger/smaller/switch are organs with receipt chains (larger
literally calls compare — the execution cycle's first two-step trace,
inside the engine). Switch thresholds are proposed FROM the data
(deciles plus the half-unit mark ladder, every proposal facing the
same admission null as any atom), and the exact road learned to
search five-word sentences on small data, where exact conditional
rules live.

### What it bought, with numbers
- The max world now mints THE TEXTBOOK IDENTITY itself:
  `0.50*x0 + 0.50*x1 + 0.50*|x0−x1|`, machine-exact, 3/3 seeds — the
  pool-branch eval's one BROKEN world, closed by vocabulary rather
  than by a stricter guard, exactly as the honest cure demanded.
- The step world mints its thresholds AT the true marks:
  `2*x0 − 1.5*[x1>2] + 1.5*[x1>1]`, certified within the told floor.
- The blended conditional writes its exact five-term sentence at both
  tested sizes.
- The judge's duel, re-run: wrong-confident 74/100 (old) → 2/100.
  True-law availability 20/20 with zero false examiner fires, Kepler
  untouched, engine self-test 11/11, noise 0/10 false laws.
- The two survivors are the poison-into-constants class — the
  rival-form duel and THE OUTLIER'S OWN LAW (the owner's source-
  modeling design, same night) are their queued cures.

### What the promotion taught, kept
- REFINE MUST NOT GLIDE A MARK: the multiplicative refine pass slid a
  step threshold below the data range, turning it into a constant
  column wearing a switch's name (`0.25*x1*[x0>-2]`). A threshold is
  a location, not a scale — steps are now excluded from the glide and
  move only by re-proposal. The equation came back readable:
  the identity, three terms, nothing else.
- FOURTH SIGHTING of the shortlist-crowding disease: the new step
  atoms flooded the exact road's correlation top-N and cost the
  crease its seat (max unsayable on 2/3 seeds until creases got
  guaranteed seats). Same cure every time — structural diversity is
  a SEAT RULE, not a ranking suggestion. This is now a named design
  law for any future shortlist.
- COST, complete numbers: the bigger vocabulary prices discover at
  ~8.8s/call (max 24s) at n=400, d=5 — roughly 4x the wordless port.
  Not hidden: the efficiency ledger's measure-first pass is the
  named home for reclaiming it.

---

## PART 9 — THE OUTLIER'S OWN LAW (promotion #13): the duel closes at 0/100

### The owner's question, made machinery the same night
"If the outlier is a plus something else, can it quantify that
something else... and identify the model of the source?" Now yes.
When a law stands but is not machine-exact, discover() isolates the
rows the law cannot carry, quantifies their deviations IN UNITS, and
asks what the deviations ARE:

- **A simple form exact on the clean majority** (the rival-form duel
  fused into the road): a 2-term law machine-exact on 54/60 rows,
  with the 6 leftovers sitting EXACT grain multiples off it, beats
  the 16-term fit that had swallowed the poison. Verdict: MIS-ENTRY —
  the cells are quarantined with receipts (row, value, predicted,
  deviation), the law superseded by its clean refit. Measured: the
  poisoned worlds now return the TRUE constants at 7e-15.
- **A law of their own**: enough flagged rows get their own
  discover() — the deviations minted `+0.41*x1` in the planted
  second-source world, while the scrambled-deviation control minted
  nothing. Verdict: SECOND SOURCE — news, not error, recorded on the
  law's node. The anomaly had a model; something was discovered.
- **Neither**: deviations kept on the record, nothing invented.

### The final duel
```
                    old judge     after #11    #12      #13
  wrong-confident    74/100        9/100       2/100    0/100
  true-law found     20/20         20/20       20/20    20/20
  Kepler n=8         NO RULE       machine-exact ————————————
```
Availability never dipped, zero false examiner fires, engine
self-test 11/11. The complete arc: the JUDGE (who may stamp), the
WORDS (what can be said), the SOURCE ROAD (what the exceptions are)
— and the disease measured at 74% on the old engine is at zero on
worlds with known truths.

### Three bugs found by the battery, each a law now
1. The k<3 early-return killed the pass exactly when the flexible
   fit had ABSORBED its poison — the guard belonged below the
   clean-majority road, not above it. (A flexible fit hides its own
   contamination; only a simple rival exposes it.)
2. rival_check's state restore REFIT the constants on the
   contaminated train and silently re-poisoned the cure on its way
   out the door — on a mis-entry cure the rival contest is settled
   by clean-majority exactness, so it is skipped with a receipt.
3. Isolation must run against SIMPLE RIVAL FORMS, never against the
   admitted fit alone: with step atoms in the vocabulary, a 16-term
   fit can absorb point poison entirely (2/6 rows visible). The
   rival-form duel and the outlier road turned out to be ONE
   mechanism, not two — the cure list shrank by merging.
v1 thresholds (5*MAD, 0.35 cap, 0.8 grid fraction, 0.15 trim) are
hand-set — the standing tests-over-thresholds debt, filed. One
unreproduced self-test crash filed as an open anomaly (rerun clean).

---

## PART 10 — CONTAINERS: world-scoped truth (probe-proven, 8/8)

### The owner's requirement
"Certain details or facts change depending on the world you put it
in. Fiction world Harry Potter has different rules than fiction world
Hail Mary." The live account's practice corpus contains fiction, so
this is a wall, not a feature request.

### The finding: the mechanism was already in the house
A container is a DOOR TAG — `in:harry-potter` — saying which facts
are IN FORCE. Zero new primitives: the engine's door tags and tag-
filtered lookups, pointed at worlds for the first time. The design:
```
teach in base:          brooms —are-for→ sweeping   [in:base]
teach in harry-potter:  brooms —are-for→ flying     [in:harry-potter]
                        ONE 'brooms' node, both doors, tags decide
ask(brooms, are-for | base)         -> sweeping
ask(brooms, are-for | harry-potter) -> flying
ask(water, boils-at | harry-potter) -> 100C  "inherited from base"
ask(portraits, do    | base)        -> NOTHING (fiction never leaks)
```
Identity = relations, exactly as the keystone says: brooms in the
kitchen and brooms at Hogwarts are one concept wearing different
doors, and "which world is open" is routing state — the execution
cycle's address space.

### Measured, all 8/8
Per-world answers correct including a three-way conflicting fact
(stars shine/dim/sing under base/hail-mary/harry-potter);
cross-world difference raised ZERO contradiction flags while an
in-world contradiction still flagged (both readings kept); leakage
0/5 in both directions; inheritance one-way with receipts (fiction
inherits base; base NEVER inherits fiction); the poisoning guard
held byte-identical base answers after full fiction ingestion (0/7
drift); container-less facts landed in base with a receipt saying so.

### What promotion needs (queued, gated)
Active-container state on the mind, `container=` on teach, container
routing inside the reasoning layer (today's probe routes at the shim),
and provenance stamping at intake through vet_intake's existing door
— so the practice loop can read fiction safely before E3 ever runs.

### PART 10 ADDENDUM — promoted same night (#14, battery 10/10)
The shim moved inside: open_world / teach(container=) / ask are
engine organs, registered in the catalog, surviving the pickle
round-trip (a saved mind reopens with its worlds and its active
container intact). Self-test 11/11 — the tagged doors disturbed
nothing. The one deliberate deferral, standing: stamping containers
at the LIVE account's intake is the owner's call, since it touches
his practice loop.

---

## PART 11 — THE EXECUTION CYCLE RUNS (chaining segment, first build, 10/10)

### What was built
The owner's three sentences — "do op, take result door, or return to
main program; each node can act like a function generator" — as a
working walker over a REAL pipeline, flows stored as net content:

```
flow:triage
  step:floor     read_floor(y, X)          -> next
  step:discover  discover(X, y)            -> [verdict==UNDERSTOOD]? validate
                                              else refuse (default door)
  step:validate  apply_law on held-back rows
                 -> [rms SMALLER than 3*floor, via compare()]? report_pass
                    else report_flag
```
A flow is nodes and doors like everything else — same substrate as
content, different altitude — and its step specs are readable meta:
an equation of PROCESS, inspectable like any law.

### Measured, all 10/10
- A true-law world walks the green road end to end; a noise world
  takes the refusal road, and the not-taken door carries its
  receipt verbatim: "bypassed validate: verdict=='UNDERSTOOD'? got
  'NO RULE' -> False" — the consideration law at the routing layer.
- The branch predicate routes THROUGH the compare organ: the door
  receipt contains compare's own sign verdict
  ("smaller(4.7e-15, 1) via sign(...) -> -1 -> True") — the
  comparison words as routing predicates, exactly as captured.
- Return-to-main is guaranteed: a deliberately cyclic flow halts at
  the hop cap with a receipt; a step naming a missing organ refuses
  honestly, no crash, no silent skip.
- THE FUNCTION GENERATOR, v1: after three green runs the chain was
  minted as chunk:triage — one node whose op is the recorded chain;
  walking the chunk on a fresh world equals walking the chain, with
  a nested trace. The owner's "each node can act like a function
  generator", smallest true form.
- Replay reproduces the door sequence; flows and chunks survive the
  pickle round-trip; a full walk costs 0.04 s.

### What the segment still owes (named, not claimed)
Engine promotion of the walker AS the kernel loop; flow steps facing
word-style ELECTIONS; branching-by-evidence as piecewise flow
supersession (clone the step for the miner-named failing case, duel
decides); the interpreter attack list (refraction/loops, rule
interference, chunk correctness) — the blocked 07-13 items now have
their execution substrate to attack.

### PART 11 ADDENDUM — promoted same night (#15, battery 12/12)
The walker moved inside: define_flow / walk_flow / mint_chunk are
engine organs, catalog-registered, and every walk now lands in the
findings ledger (outcome, hops, road) — Isaac's processes leave the
same paper trail as his knowledge. Self-test 11/11. The segment's
remaining work (flow elections, piecewise flow supersession, the
interpreter attack list) attacks a substrate that now exists.

---

## PART 12 — FLOWS THAT ADAPT (elections + piecewise supersession, 11/11)

### The story, measured end to end
A flow that refuses PARTIAL verdicts loses on blended-conditional
worlds — lawful worlds refused. The adaptation loop the sheet
promised, now demonstrated with real organs at every step:
1. WALKS BANK: ten walks land in the findings ledger with roads and
   outcomes (wins 6/10 — five plain passes plus one blended world the
   engine legitimately solved; see the falsification note below).
2. THE MINER NAMES THE LOSING CLASS from the walk receipts
   themselves: mine_commonality over {verdict, pool-state, size}
   features named exactly {verdict=PARTIAL, pool=scream} — the
   commonality organ reading PROCESS receipts the same way it reads
   failure receipts anywhere else.
3. THE CLONE: one new door for the named case — PARTIAL routes to
   'deepen' (re-discover on a 96-row subsample, where the deep exact
   road lives) — everything else untouched.
4. PIECEWISE, verified: off the named class the branched flow's
   roads are IDENTICAL and the deepen door carries a bypass receipt
   on every plain walk. On the named class, all four failing walks
   took the deepen door and reached machine-exact passes.
5. THE DUEL: original 6/10 -> branched 10/10. LOSER KEPT: the
   original flow still walks, still loses the same way, its record
   intact — and the election (ledger tallies) picks the branched
   flow as champion with the loser's score on the books,
   re-electable.

### The attack-list items, unblocked and passed
Productive LOOPS halt by predicate (a retry loop reached UNDERSTOOD
and exited well under the hop cap); interleaved walks of different
flows stay separate; a minted CHUNK works as a STEP inside another
flow (composition: minted functions are callable words).

### The falsification worth savoring (kept, twice)
The probe's planted weakness — "blended worlds the big-n road cannot
say" — was OUTGROWN BY THE ENGINE TWICE while the probe was being
written: first the n=200 world split to a train half of exactly 100
rows, precisely the deep exact road's boundary, and stamped
machine-exact; then, moved to n=240, one seed in five STILL passed —
a genuinely-correct approximate law validating at rms<0.01 on fresh
truth. Tonight's earlier promotions made worlds designed as
too-hard... solvable, faster than the probe could exploit them. The
adaptation story stands on the four that really fail; the fifth is
the engine's, fairly won.

### What remains for the segment (named)
Engine promotion of the election/supersession mechanics as organs
(the probe runs them shim-side over the ledger); credit assignment
for step-level outcomes is CRUDE (whole-walk outcome banks on every
step — the same fresh-eyes caveat as word elections, carried
forward, not hidden).

### PART 12 ADDENDUM — promoted same night (#16, battery 6/6)
The adaptation mechanics moved inside: flow_tally / elect_flow /
branch_flow are organs. One call now clones a flow and grafts the
named-case door; elections run on measured win rates with losers
kept and supersession chains never erased; a windowed re-election
flipped a champion whose recent fortunes reversed while full history
still favored it — recency is a recorded choice, not an assumption.
With this, the FLOW STRUCTURES design (presence / consideration /
adaptation) is complete in the engine. Self-test 11/11.
