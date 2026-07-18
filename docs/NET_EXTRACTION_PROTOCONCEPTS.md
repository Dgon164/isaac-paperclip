# NET EXTRACTION — THE PROTOCONCEPT DECODE (owner design, 2026-07-17)

**Owner, verbatim:** "ive been thinking about net extraction, and i
think i have been looking at it the wrong way. i think we should
consider protoconcepts and neurons. take each neuron, decode what
its major componants are like its activators and inhibitors, find
the atomic structures in the superposition sets, and then calculate
what the interactions are actually doing with information."

Status: DESIGN NOTE + attack list. A research segment, queued behind
the alpha push (session 2: vet wiring, kernel first light). Nothing
built; the planted-world probe is specified below and small.

## The correction this makes (why the old way was wrong)

The earlier framing read the net neuron-by-neuron, layer-by-layer.
The owner's correction: A NEURON IS NOT THE ATOM. Networks pack more
features than they have neurons, so each neuron carries a MIXTURE of
several underlying "protoconcepts" in superposition. Read a neuron
raw and you read a chord and call it a note — polysemantic mush,
which is the box-geometry ceiling the transplant experiments hit
from another angle. The right order is: UNMIX FIRST (find the atomic
structures inside the superposition sets), THEN read interactions
among the unmixed atoms. (The field that studies this professionally
reached the same correction — features-not-neurons, superposition,
sparse decompositions. The owner derived it independently. Isaac's
angle differs in the deliverable: readable equations under nulls
with receipts, never a dashboard of unnamed features.)

## The four steps, in Isaac's machinery

1. **Per-neuron decode (activators/inhibitors):** a neuron's input
   weights say what excites it (+) and what suppresses it (−). But
   the meaningful decomposition is not the raw weight list — it is
   the sparse combination of ATOMS the weight vector is built from.
   Deliverable per neuron: a readable card, e.g.
   "neuron 7 ≈ 0.8·(atom A) − 0.6·(atom B)", with receipts.
2. **Atoms from superposition sets:** the atom dictionary is minted
   the way Isaac mints everything — expand freely, compress by
   null. Candidate directions must EARN atom status past a
   scrambled-weights control, and ubiquitous directions that every
   neuron carries get the stopword treatment (the excess/base-rate
   law: a door every word has carries no identity — third
   appearance of that law, now in weight space).
3. **The interaction calculus:** with atoms in hand, ask what the
   layer DOES to information: which atoms reinforce into the same
   downstream atom, which inhibit, which merely interfere (the
   cross-talk superposition tolerates by design). The instruments
   already exist: the drop algebra with ORDER-3 EXCESS
   (excess-over-best-pair) is precisely an interaction meter;
   ablation predictions are the receipts.
4. **The rhyme that makes it SAYABLE:** ReLU is Isaac's own switch
   atom — relu(w·x) = (w·x)·[w·x > 0], a var×step product IN HIS
   EXISTING GRAMMAR (promotion #12). A small net is therefore not
   metaphorically but LITERALLY expressible as one of his
   equations. The decode target is the mission sentence itself: a
   trained net in, readable equations out.

## The two diseases, named with cures

- **Rotational non-identifiability:** without a sparsity demand the
  atom basis is not unique — any rotation explains the weights
  equally. Cures: sparsity as the minting prior; PLANTED ground
  truth first (below); on real nets, every claimed atom must carry
  a falsifiable ablation receipt ("remove this atom → this specific
  behavioral deficit"), judged against a scrambled control. An atom
  with no receipt is not an atom.
- **Inhibition vs interference:** superposition means some negative
  interaction is deliberate noise the net tolerates, not meaningful
  inhibition. The differential is an excess-over-null question —
  meaningful inhibition RECURS across contexts past what random
  packing predicts; interference does not. (The news-vs-error law,
  in weight space.)

## The probe (battery-first, planted truth first)

- **P-0 planted superposition world:** train tiny nets on k sparse
  planted features packed into d < k neurons (the canonical forcing
  of superposition). The true atoms are KNOWN by construction:
  recovery is checkable exactly (alignment to planted directions);
  the scrambled-weights control must recover nothing; the
  ubiquitous-direction stopword case planted deliberately.
- **P-1 planted circuit:** plant a known interaction (A AND B → C;
  A inhibits B's pathway). The interaction calculus must read the
  circuit; drop algebra's order-3 excess is the meter.
- **P-2 his own pools:** the _PoolMeter's weights are seeded and
  known — a specimen we own to the byte.
- **P-3 the prize:** the HIGGS deep net (0.885, unmatched by
  anything readable). If the protoconcept decode pulls honest
  structure out of THAT, it is the whole mission in one exhibit.

## Standing-law checks

No-nets-as-deliverable: intact (net = specimen; equations = the
deliverable). Veto-nets verdict: untouched (this extracts FROM nets;
it does not deploy one). Weights propose, behavior confirms: the
told-vs-earned split applied to decompositions — a weight-only read
is a CANDIDATE until planted/ablation behavior earns it.

## FIRST LIGHT — probe run 2026-07-17, same sitting as the design
(`experiments/protoconcept_probe.py`, PYTHONHASHSEED=0, **7/7**)

- **A1 the instrument:** 6 planted atoms in 20 dims, 96 neurons each
  a signed 2-sparse mixture — atoms recovered at **min |cos| 1.000**;
  neuron cards (support + signs) **95/96 exact**, the one miss
  counted; SCRAMBLED control: sparse structure GONE (residual 0.066
  → 0.766) — atomic structure is not free, it must be in the rows.
  Operating floor MEASURED: ~8 users per atom starved the decoder
  (24-neuron first try), ~32 works — said, not hidden.
- **A2 the stopword law, third domain:** the ubiquitous direction is
  the COMMON MODE — subtract what everyone shares before asking what
  distinguishes. Sign-flip permutation null: QUIET on the control
  (0.147 <= thr 0.258), FLAGGED where planted (0.706 > 0.279),
  direction named at |cos| 0.978; atoms recover at 0.999 after
  base-rate removal. (First try hunted it as a dictionary atom — the
  alternation smeared it; wrong-kept.)
- **A3 a trained net, decoded from weights:** 6 sparse features
  forced into 3 neurons (tied-weight ReLU autoencoder, SGD from
  scratch, reconstruction rel-err 0.02). Superposition REAL: 3/3
  neurons carry >=2 features; readable activator/inhibitor card per
  neuron. **THE SIGNED INTERFERENCE LAW, behaviorally confirmed:**
  +cos feature pairs co-activate (predicted pairs = measured pairs
  2/2 exact), −cos pairs mutually SUPPRESS (3/4 overall). The
  first-light lesson, wrong-kept: |cos| predicted nothing — the
  ReLU reads antipodal packing as zero, because MUTUAL INHIBITION
  is the net's packing trick for features that rarely co-occur. The
  sign is the information story: what the interactions are actually
  doing with information is (a) confusable-pair cross-talk where
  embeddings agree and (b) deliberate mutual inhibition where they
  oppose.

Next rungs unchanged: P1 planted circuit (drop algebra / order-3
excess as the interaction meter), P2 his own pools, P3 the HIGGS
deep net.

## OWNER RULINGS ON FIRST LIGHT (2026-07-17, same sitting)

**1. Inhibition = CHECKLISTS WITH REQUIREMENTS, not full veto.**
"thats the veto, but it doesnt have full veto powers, what im
thinking is it is basically checklists. it has requirements. what
information is present in the initial." The algebra agrees exactly:
a ReLU neuron IS a soft checklist — required evidence (positive
weights) minus disqualifiers (negative weights) must clear the pass
mark (the bias). A disqualifier can be OVERRULED by enough
requirements — partial veto, graded, conditional — which is
precisely what A3 measured (suppression bites only when features
co-occur). A FULL veto would be a multiplicative gate — a product
with the switch atom — a DIFFERENT form, distinguishable in Isaac's
own grammar: soft checklist = linear+threshold; hard veto =
x·[disqualifier absent]. The decode can now ask, per neuron, WHICH
kind it is — a checkable claim, not a metaphor. (Distinct from the
shelved veto-nets deliverable — this READS requirement structure as
information; it deploys nothing.)

**2. ENGINEERED SUPERPOSITION: overlapping refined pools.**
"overalapping several refined pools to create harmonic structures
and... interference patterns of information essentially, but we can
point at the direct sources and not need the full informational
interactions if we are clever about it." The inversion of the decode
problem: emergent superposition must be UNMIXED (P0 proved we can);
CONSTRUCTED superposition comes pre-receipted — every component
points at its direct source because we built it. And A3's sign
lesson becomes a design rule instead of a discovery: overlap pools
so that concepts which rarely co-occur get OPPOSING directions
(the packing trick, engineered on purpose), confusable concepts get
separated ones. This lands on the already-queued ENSEMBLE PROBE (N
frozen pools, agreement past scrambled nulls) — the harmonic/
interference framing is its design upgrade.

**3. THE HALLUCINATION LAW (incomplete ideas).**
"we take the most complete idea, and if there is no good match, its
unlearned. its just not present, and best fit would be a
hallucination." Recognition takes the MOST COMPLETE checklist
match; below the match floor the honest answer is UNLEARNED — not
present — because a forced best fit IS a hallucination. This is the
rank-plus-abstention pattern (which_law's NONE, honest silence, NO
RULE) promoted to a standing law of recognition, and "unlearned" is
not a dead end: it is the frontier signal that feeds the
curriculum loop (weakness named -> drilled -> re-elected).

## CLARIFICATION (owner, same sitting): THE FOREIGN NET IS THE POINT
"we need to know the trained information from scratch. if we have an
unbuilt net, one that someone has provided only the weights for, we
need to decode it." The engineered-pools road is for OUR OWN
representations; it does not replace the requirement. The
requirement is the blind decode: weights in, trained information
out, no training data, no provenance, no cooperation.

What weights-only honestly yields, and where meaning grounds:
- STRUCTURE always: atoms per layer, per-neuron checklist cards
  (requirements/disqualifiers/pass mark), signed interference,
  soft-vs-hard veto per neuron — the ALGEBRA of what it computes,
  composed layer by layer into readable form (ReLU = the switch
  atom keeps every step in Isaac's grammar).
- MEANING grounds at the boundary: first-layer atoms are
  combinations of the INPUT dimensions — if the provider names the
  inputs (HIGGS columns are named physics), meaning propagates
  upward through the composition. Unnamed inputs = an honest
  anonymous circuit diagram, said as such, never guessed at.
- THE SPECIMEN IS RUNNABLE: provided weights mean we can EXECUTE
  the net on inputs WE construct — interrogation, not training
  data. So the fresh-row court exists for foreign nets too:
  decode from weights, PREDICT behavior, confirm on synthesized
  probes; ablation receipts likewise. A claim with no surviving
  prediction is not a decode, it is a story.
- WITHOUT planted truth, the null discipline carries everything:
  scrambled-weights controls (structure exists at all), restart
  stability (the basis is pinned vs non-identifiable — SAID),
  cross-layer consistency (atoms leaving layer k must reappear in
  layer k+1's checklists — the composition receipt).

LADDER REVISED — the blind protocol added:
  P0  planted superposition (DONE 7/7).
  P1  planted circuit — interactions read by drop algebra /
      order-3 excess.
  P1.5 THE BLIND DRILL: we train a net, the decoder receives ONLY
      the weight matrices — no data, no truth, no hints. It files
      its claims FIRST (atoms, cards, interference, predicted
      behaviors on synthesized probes); THEN the unblinding scores
      them. The predictions-filed discipline, applied to nets.
      This is the honest rehearsal for "someone provided only the
      weights."
  P2  his own pools (constructed specimen).
  P3  the HIGGS deep net — named inputs, real physics, the prize.
  Landing spot for a successful decode: the foreign net's laws
  enter Isaac's net as TOLD knowledge (tell_law / flows) with
  provenance "decoded from provided weights" — told-unverified,
  belief earned by data, like any other teacher.

## RUNGS P1 / P1.5 / P2 / P3-FIRST-BITE — all run 2026-07-17, the
## same day as the design ("lets find out how much we can find out")

**netdecode_probe.py 8/8:**
- P1 planted circuit: AND(0,1) read from weights at coefficient
  2.00 (true 2.0) — carried by an ASSEMBLY [neurons 6,7], per-
  neuron contributions 0.80+1.19 summing to the coefficient (the
  receipt). First-pass lesson, wrong-kept: NO single neuron
  implements the gate — trained nets distribute; the truthful unit
  is the assembly. THE COUNTERFACTUAL RECEIPT: the cards predicted
  the ablation outcome (excess 0.00, linear path 1.00) BEFORE the
  intervention; the run confirmed (0.01, 1.00).
- P1.5 THE BLIND DRILL 5/5: five foreign nets, decoder saw ONLY
  weight matrices — every hidden pair named, every coefficient
  within 0.03, every readable summary carried the behavior (table
  max-err <= 0.021). "Someone provided only the weights" is now a
  practiced motion.
- P2 inverted — THE HALLUCINATION LAW ON THE DECODER: planted
  weights -> structure DECLARED (12.5x sparse gain, restart
  stability 1.00); random pool weights -> NO STRUCTURE declared
  (1.0x, 0.54) — unlearned, not present, no invented atoms.

**netdecode_higgs.py — REAL PHYSICS (machinery 2/2, predictions
filed first, both CONFIRMED):**
- Specimen: 28->32->1 ReLU net trained here on 800k HIGGS rows,
  test AUC 0.7959 on 200k fresh (the 0.885 deep monster remains
  the prize).
- FROM THE WEIGHTS ALONE, with names: the net's top-5 carriers are
  m_bb, m_wbb, m_jjj, m_wwbb, m_jlv — ALL seven engineered mass
  invariants outrank the low-level detector features (HP1 CONFIRMED
  at 4.3x mean share) — the physics story read straight off W.
- HP2 CONFIRMED: 6/7 phi angles land in ranks 23-28 — the net
  LEARNED rotational symmetry and the decode sees it in the
  weights.
- THE RECEIPT AT RATIO 1605x: ablating the decode's top-3 named
  features costs 0.1605 AUC; its bottom-3 cost -0.0001. The
  reading is the computation.
- HONEST FINDING, filed: the REAL first layer shows NO sparse
  atomic structure (gain 0.99x vs scrambled) — dense mixing, not
  dictionary packing, at this width/inputs. The carried-weight +
  card reads work anyway; the sparse-atom tool applies where
  packing exists (P0's regime), and the toolkit needs both reads.
  Named open door: activation-space atoms (the superposition may
  live in activations, not first-layer weights).

## THE FRAME (owner, 2026-07-17, closing the sitting): IDEOLOGICAL
## CHEMISTRY, AND WHERE THE SEGMENT LANDS
"the final output layer is where the 'ideas' become concrete and
tabulated, but the building blocks for those is constructed along
the way. its ideological chemistry. add this group, subtract this
group, carry this group, combine these groups, etc. they are group
superposition concepts and algebra, and then they reinforce
different elements and groups and interact to create a final
pattern match that says this is most like this structured equation,
use that output. we are just creating a concept net replacement and
correlating them into isaac speech."

The chemistry named, mapped to what is already measured:
- GROUPS = the assemblies (P1: no single neuron implements a gate;
  the functional unit is the group, and its contribution receipt is
  the sum).
- ADD / SUBTRACT = the signed interference (P0-A3: +cos reinforce,
  −cos suppress — measured, behaviorally confirmed).
- COMBINE = the interaction terms (the AND assemblies; order-3
  excess for triples when the circuits deepen).
- CARRY = a group passing through a layer intact — the decode
  primitive DEEP nets need next: detect near-identity propagation
  of a group across a layer (the composition receipt made
  mechanical). Named build target for the deep-net rung.
- THE OUTPUT LAYER = the TABULATOR: group votes summed against
  templates, "most like this structured equation, use that output"
  — recognition as most-complete-match with the hallucination law
  at the last layer (below the floor: unlearned, refuse).

THE LANDING, made explicit: the decode's product is not a report —
it is a CONCEPT NET REPLACEMENT. Groups become nodes; add/subtract/
carry/combine become doors and flows; the readable equations enter
as told laws (tell_law, provenance "decoded from weights",
told-unverified, belief earned); and the whole thing CORRELATES
INTO ISAAC SPEECH — the report/learned-speech road says what the
foreign net knows ("the b-quark pair mass matters most; the
azimuthal angles carry nothing") in earned words. A foreign net in,
a citizen of his net out — the same door his predecessor's telling
used at the launch.

## CORRECTION (owner, same sitting): NO CARRY — DEPTH IS THE NET'S
## PROBLEM, NOT OURS
"the carry is a direct shortcut. we dont need the carry. see in
these systems it works as a step through the thing. with us, it is
specifically not. we are assembling from componants. we collect and
immidiately use the parts. we are just able to see from the parts
that are here, we run the quick simplified interactions, and we can
say this will be the activation signal, find the checkboxes that
most match."

The ruling: depth is an artifact of the NEURAL substrate — it can
only compute by stepping a signal through layers, so "carry" exists
there as a mechanism. The concept-net replacement does NOT inherit
that constraint and needs no carry detector. Extraction reads
bottom-up (layer k's groups are the vocabulary for layer k+1's
checklists), but then SUBSTITUTION COLLAPSES THE DEPTH: layer-(k+1)
cards are rewritten over layer-k group expressions and simplified;
a "carried" group falls out as an identity term for free — the
algebra handles carry, no primitive required. The extracted form is
FLAT: components + quick simplified interactions + the tabulation.
Use is direct: collect the parts present, run the closed-form
interactions, predict the activation signal, find the checkboxes
that most match (the hallucination law below the floor).

The evidence already on the table: blind_decode NEVER steps —
neuron_resp is closed-form per card, the B2 truth tables were
predicted from the summary (not by simulating the weights) at
max-err 0.02, and the counterfactual receipts were computed the
same way. The method IS collect-and-immediately-use; the deep-net
rung extends the substitution upward, not a carry tracer.
Replaces the earlier "carry-detection" build target.

## THE THEORIES VALIDATED (netdecode_deep_probe.py, 7/7, 2026-07-17
## — "these are theories. so lets validate and assemble.")

Specimen: a TWO-hidden-layer net (5->8->6->1) trained to 0.007 on
y = 2*AND(XOR(x0,x1), x2) + x4 — XOR forms in layer 1, the AND
composes it in layer 2, x4 must cross both layers.

- SUBSTITUTION COLLAPSES DEPTH — CONFIRMED. The decode reads cards
  bottom-up once, then the flat interaction expansion holds
  everything: pairs (0,2)=+1.99, (1,2)=+1.99, TRIPLE (0,1,2)=-3.99
  (the order-3 excess, measured in a deep net), x4=+1.0, nothing
  else. The flat form ALONE — no stepping at use time — predicts
  all 32 input patterns at max err 0.037, including the 4- and
  5-feature patterns it never probed (any order-4 junk the net had
  learned would have shown there).
- CARRY FOR FREE — CONFIRMED. x4 crossed two layers and landed as
  a pure linear term, every interaction <= 0.017. No carry
  detector exists anywhere in the code. Depth was the neural
  substrate's problem; the algebra never had it.
- INTERVENTION-GRADE PREDICTION — CONFIRMED, with a gem: silencing
  the full (0,1) machinery, the cards predicted the outcome
  EXACTLY before the run — every composed term to 0.00, and x4 to
  0.97, NOT 1.00, because the assembly shares neurons with x4's
  path and the cards knew the collateral damage in advance.
  Wrong-kept en route: selecting the assembly by pair-excess alone
  missed its LINEAR members (the x0+x1 riders) — an assembly
  includes its linear parts; the cards correctly predicted the
  partial collapse that mistake produced.
- THE CITIZEN ASSEMBLED — CONFIRMED. The decoded flat form
  generated examples; Isaac DISCOVERED the law in his own grammar
  (creases and products — an EQUIVALENT form, exact on the domain);
  his law vs the original foreign net across all 32 patterns:
  max err 0.011. A stranger's weights, through the decode, through
  his own court, now a law node in his net. Named niceness door:
  his equation is an equivalent form, not the canonical minimal
  one — canonical simplification is a future door, not a defect
  (the verdict was honestly PARTIAL). Named debt: the crease is
  DISCOVERABLE but not TELLABLE (_parse_equation lacks the absd
  pattern) — extend the telling vocabulary through gates.

## CLARIFICATION (owner): THE TARGET IS FACTOR ENUMERATION, NOT
## EQUATION FORMS
"we are not looking for the crease. we are looking to enumerate the
input contribution signals. so out of the complex inputs, what are
the actual things. example, you have gpt2. it could be 64x12 i
think. and those 12 things are the primary factors. we only care
about how those 12 things contribute to the output activation. the
way it works is it amplifies certain carriers and inhibits others.
so of those 12 atoms or whatever, what are the combinations that
each output is looking for."

The deliverable, restated: complex inputs decompose into a small
set of PRIMARY FACTORS (in transformers the architecture hands them
to us — 12 heads x 64 dims; elsewhere the unmixer finds them). Per
OUTPUT, the decode enumerates:
  (1) WHICH factors it reads (amplified carriers vs inhibited),
  (2) the CONTRIBUTION SIGNAL inside each factor's block (the
      direction it actually reads, not the whole block),
  (3) the COMBINATIONS it is looking for (which factors must
      co-occur — the checklist at factor level).
Isaac's equation grammar remains the internal landing (the citizen
road), but the reported product is the factor-contribution table.
Named rung: GPT-2 small itself (12 heads/layer), when the weights
road is set up.

## FACTOR ENUMERATION VALIDATED — INCLUDING ON REAL GPT-2
## (factor_enumeration_probe.py 4/4; gpt2_head_enumeration.py 3/3;
## 2026-07-17, the same sitting as the clarification)

PLANTED (12 factor-blocks x 8 dims, 6 outputs, trained net, decode
gets weights + block boundaries only): recipes enumerated 6/6 EXACT
— every amplified pair named with gain (1.99-2.07 vs true 2.0),
every inhibitor named at -1, nothing extra; contribution SIGNALS
inside the blocks read at min |cos| 0.975 / mean 0.991 (the
single-operating-point Jacobian was fragile at thresholds — 0.42 on
one slot — cured by averaging over an amplitude grid, wrong-kept);
scrambled control 0/6.

REAL GPT-2 (small, 12 heads x 64 — the owner's example verbatim;
final attention layer; per-head contribution to the correct
next-token logit; PREDICTED = remove the head's direct term and
recompute only final-LN+unembed; MEASURED = zero the head's W_O
rows and run the whole model):
- Specimen sane 5/5 prompts. The enumeration is READABLE: head 0
  is the dominant amplifier for factual completions (+10 to +19
  logits: 'Paris is the capital of'->France, 'Two plus two
  equals'->four); head 11 amplifies the dialogue completion
  ('How are'->you at +28.7); and HEAD 8 IS A STANDING INHIBITOR
  on four of five prompts (-9.8 to -21.9) — a suppressor head the
  enumeration surfaced on its own.
- Rank agreement predicted~measured across heads: mean 0.77
  (0.40-0.95 per prompt); MEDIATION SHARE 0.44 reported — a real
  finding: roughly half of head influence flows through the final
  MLP, not the direct path. Named next door: extend the quick
  simplified interactions one block deeper.
- SIGN RECEIPTS PERFECT: ablating the predicted top amplifier
  LOWERED the correct-token logit 5/5; ablating the predicted top
  inhibitor RAISED it 5/5 — amplify/inhibit, exactly as the owner
  framed it, confirmed by weight-level intervention on the real
  model.
