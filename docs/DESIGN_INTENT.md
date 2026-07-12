# DESIGN INTENT — the standing sheet
**Load this first. Every build is checked against this BEFORE it is written.**
(Created 2026-07-05 after the owner had to manually re-inject his own settled
designs — variants, normals, negative structure, all-methods-one-concept —
that the machinery had computed, discarded, or siloed.)

## THE LAW ABOVE THE CHECKLIST (owner, 2026-07-05)
**"There is no separation. Everything is all mixed together. There is no
different thing. Everything should always be universally applied if it
can."** No mechanism is domain-siloed: the readout is not a glyph tool
(it is for ANY channels — covtype jumped +11.4 the day it was applied
there); dynamics is not stroke-only (any path or series); variants are
not digit-only (any pattern class); nevers, normals, duels, ledgers —
if the inputs exist, the mechanism applies. When building or testing
ANYTHING, ask: where else does this apply RIGHT NOW? Then apply it.

## THE USAGE LAW (owner, 2026-07-10)
**"Giving it the language to understand is one thing — bones and
whatever — but telling it how to use them is not. It needs to learn how
to represent ideas using structures that we provide. We need to learn
how to translate something into these ideas, and if the ideas don't
work, we need to figure out what does."** The division of labor:
hand-built = the VOCABULARY (measuring organs: holes, bones, joints,
curves, deltas) + the TRANSLATION (raw thing → the vocabulary's facts)
+ the epistemics (nulls, doors, admission). LEARNED = the USAGE — which
facts and combinations carry identity is decided by Isaac's own
null-gated machinery, never by a hand-written signature or comparison
recipe. A hand-picked signature (e.g. "topology = holes+line-count") is
programming the lesson — the old trap. When the vocabulary cannot say a
difference, the measured residual/confusion IS the discovery signal:
grow the vocabulary, don't hand-wire the usage. (Found 2026-07-10
auditing the glyph stack: every channel's usage was hand-taught.)

## NOMENCLATURE + THE IDENTITY LAW (owner, 2026-07-11, eighth message)
**The roles, named:** **PRIME** = Isaac himself — the full net,
everything (what earlier sections call "core"). **ORCHESTRATOR** =
Prime's sole writer (queue → admission → journal → packs).
**WORKERS** = processing on snapshots; at the leaf, a worker is a
whole all-in-one Isaac with its security net. **SCRUBBERS** = the
strip-identity workers (a first-class role, not just the share path).
**CLIENT SIDE** = the customer/user side: overlays, security nets,
user-held data.

**THE IDENTITY LAW (owner's words):** "we want isaac to understand
the world, but we dont want him to identify people, businesses or
anything like that." Prime learns CONCEPTS AND LAWS, never identity
dossiers. Public-facing information: usable for PROCESSING. Anything
user-submitted: RESERVED client-side and scrubbed of identifiable
information to the best of our abilities before anything crosses.
**No datasets, no user info, no usage patterns ("usage ways") flow to
Prime — ALL personalization is localized on the user's end.** Note
what that last clause covers: even TELEMETRY/usage analytics stays
client-side; Prime's ops ledger describes Prime's own operation, never
user behavior. Enforcement is layered: structural quarantine (tiers) +
scrubbers on every intake path to Prime + an identity-shaped-content
refusal at Prime's admission gate.

## THE INFRASTRUCTURE ARC (owner, 2026-07-11)
Owner declared the next major shift: **persistence, structure
processing, batch processing, API calls, system/operational management,
and partial net loading for responses and processing.** Standing
constraints on all of it: the persistence schema is the Net made
durable — it keeps EVERY measurement, the wrong-section, and
supersession chains (checklist #4/#6 apply to the file format);
partial loading is the reverse index turned toward storage (recall
pages in only the doors a query touches; partial answers must equal
full answers or the delta is reported); ledgers are the ops organ too
(ops events append like findings); performance is graded against the
owner's ~3 s single-core trainer under a hard compute budget (owner,
2026-07-11), never internal before/after alone; no optimizing before a
measured profile. Full plan + phase batteries:
`isaac_project/INFRASTRUCTURE_ARC_2026-07-11.md`.

**The orchestrator (owner, 2026-07-11, second message):** ONE
orchestrator owns the mind and is the SOLE WRITER. Every other process
(discover jobs, perception/recognition batches, consolidation, API
front-ends) does its own processing on read snapshots ("live pulls as
needed") and routes every update or finished process through the
orchestrator as a QUEUED PROPOSED EDIT. The queue is not a lock
workaround — it is the admission gate made operational: every edit is
a proposal (expand freely), the orchestrator runs the epistemics
(compress by test: nulls, admission, supersession) before anything
touches the Net; rejected edits are wrong-kept with their why.
Conflicts between workers resolve by EXISTING organs: commutative
count increments merge; contradictory claims become RIVALS, never
overwrites. The orchestrator stays THIN — gatekeeper, not thinker;
hand-built stays only the epistemics.

**NO TRADITIONAL DATABASES (owner, 2026-07-11, third message):** owner
has had major scaling problems with SQLite and is averse to ANY
traditional database system. Storage is PLAIN FILES ONLY: append-only
JSONL journal (the findings-ledger organ) + IMMUTABLE indexed pack
snapshots (single file: header + node→offset index + records; loader
reads the tiny index, seeks/mmaps records on demand = partial loading;
published by write-new-then-atomic-rename; a new snapshot SUPERSEDES,
never overwrites — the wisdom laws as a file layout). Immutability is
what makes live pulls safe with zero locking. stdlib only, no
dependencies (the Raspberry-Pi line).

**CUSTOMER SUBNETS — the privacy quarantine (owner, 2026-07-11, fourth
message):** containerized deployments hold LOCAL SUBNETS that are
customer-specific and NEVER feed back to Isaac — not used for
education or any other purpose; identifiable information lives there
and ONLY there. The isolation is STRUCTURAL, not filtered: the core
net is a read-only layer in the customer container; all customer
writes go to the customer's own overlay (own journal + own packs, own
orchestrator); the core orchestrator's queue is simply not reachable
from customer containers. Sync is ONE-WAY, core → customer (the fork
organ made persistent: a private branch that tracks upstream core
snapshots and can never push).
**The share path (owner, 2026-07-11, fifth message):** whether an
overlay discovery ever reaches core is UP TO THE CUSTOMER — opt-in
share setting. If share is on: the discovery is sent to the core
orchestrator TO BE EVALUATED, which routes it to a dedicated SCRUBBER
WORKER that finds and strips ALL identifiable information and keeps
only the general abstraction details (the equation/relation/door
structure and measured stats — never rows, never names, never literal
customer values). Only the scrubbed abstraction enters the edit queue
for normal admission (nulls, rivals). Shares land in a QUARANTINE
INTAKE, never the Net; raw submissions are NOT retained core-side —
what is kept is the abstraction + a scrub report (categories/counts
stripped, not content; wrong-kept applies to the decision record,
never to PII). If the scrubber cannot cleanly separate abstraction
from identity, the share is REFUSED back to the customer — refusal is
an answer. Default with share off: no path at all.

**WORKER CACHING (owner, same message; interval SETTLED by owner
2026-07-11 sixth message):** workers live-load anything from the net,
keep it CACHED LOCALLY, and operate on the cache; **recheck FIXED at
30 minutes** — owner's reasoning: "really it would be the worker that
is doing the updating, not the net" — workers are the update
producers, so they are never surprised by their own edits, and the
net between contributions moves slowly. Owner's law: **"the longer
isaac runs the less anything should be updated."** Recheck = replay
the journal tail past the worker's watermark (cheap, shrinks as Isaac
matures). Standing companions (undisputed): a worker PINS one version
per job (rechecks between jobs, never mid-job — consistency beats
freshness) and staleness cannot corrupt because ADMISSION is the
arbiter (a stale proposal is rejected + wrong-kept at the gate).
Superseded rival, kept: assistant's three-layer design (fast
watermark heartbeat + delta refresh + 30-min backstop; per-node
churn-driven policy) — revisit only if a measured staleness cost ever
bites.

**SECURITY NETS (owner, 2026-07-11, seventh message — "custom
security nets"):** USER-side specific nets, one tier below customer
subnets: information stored and processed WITH Isaac but pullable
ONLY from the worker holding it — never from anywhere else; processed,
learned-from, and OUTPUT to the user, but never stored upstream or
shared. The worker acts as its own second orchestrator over its own
local net — equivalently, it IS "the older version of Isaac": a
classic all-in-one instance living at the leaf. THE RECURSION: core →
customer overlay → worker security net is ONE mechanism at three
scales (the sheet's no-separation law made literal). Spec points:
reads LAYER one-way (local ∪ customer ∪ core; local wins; shared
tiers can never read local); writes have NO upstream channel
structurally (the local mini-orchestrator's queue goes nowhere);
partial loading is what makes the leaf cheap (pull only the shared
nodes a question touches, door private evidence onto them locally);
two persistence modes — EPHEMERAL (RAM-only, evaporates at session
end) or USER-HELD (persisted only on the user's side, encrypted, key
user-side); **logging is a leak channel**: ops events from a
security-net worker carry counts/timing ONLY, never content.

**SKILLS — THE WORKER MODEL (owner, 2026-07-12, ninth message):**
"the scrubber is just a specialized skill, but it belongs to prime.
all information any worker will do is just prime, but its a specific
checkbox of things... its learned things and preloaded structures and
you just pull and access that directly for the net to be able to
process." ROLES ARE LOADOUTS, NOT SPECIES: every worker IS Prime with
a checkbox of skills loaded. A skill = a named record in Prime's net
(`skill:<name>`, learned things + preloaded structures) pulled
through the SAME partial-loading/caching path as any node — no
separate machinery. Educating Prime updates the skill record
(supersession); workers pick it up on their recheck; a pinned job
keeps its loadout until the job boundary. The scrubber's pattern
vocabulary is the first skill record; hand-coded module defaults are
only the SEED Prime is educated with.

**THE LEARNED SCRUBBER (owner, 2026-07-12 — TODO, its own research
thread soon, NOT now):** "we will have to train the scrubber... teach
it what counts as personal or not and generalize the information."
The regex scrubber (isaac_store/scrubber.py, 19/19) is the v1
VOCABULARY; the real scrubber LEARNS the personal/not-personal
boundary and GENERALIZES content (identity → the abstraction it
carries) with Isaac's own machinery — the usage law applied to
privacy: hand-built = pattern vocabulary + epistemics, LEARNED =
which content carries identity. Battery when built: measured strip
rate, refusal calibration, generalization utility. Until then the
three layers stand (structural quarantine + regex scrubber + gate).

**WORKING NETS (owner, 2026-07-11):** the full net will be BIG
(size unknown); working nets must be kept SMALL ENOUGH BUT CAPABLE
ENOUGH. Deployment is the compress stroke: working-set extraction =
task closure × measured usage/evidence, with the information_ledger
reporting what capability was kept vs left behind, in complete numbers
("this N-MB working net keeps X% of the full net on task Y").

## NO PRESET FREQUENCIES (owner, 2026-07-12, tenth message)
**"Preset cos and sin and stuff is just bad. its not that
complicated. you can look for periodicity and periodic periodicity.
if its a multiple that should be easy to tell by the pattern. if its
closer to something it will deviate slower than if it was farther.
it just needs to try and bracket and refine the answer."** A
frequency inside sin/cos/cosh is a MEASUREMENT, not a menu choice
(checklist #3 applied to atoms). The mechanism: BRACKET (coarse scan
proposes the neighborhood — the beat rate says how close: near-truth
mismatch deviates slowly, far mismatch thrashes) then REFINE (walk
the frequency until the fit stops improving). Found 2026-07-12 when
the frame duel suggested m_jj's blocker was the atom grid.
**VERIFIED SAME DAY (mjj_identity_probe): the mechanism ALREADY
EXISTS and works** — "the grid proposes, the refine pass sharpens"
(hill-climb on every admitted term's k): on planted truth the engine
said the invariant-mass law y²-frame UNDERSTOOD r²=0.9996, walking
1.5 → 1.026 ≈ 1. The real-HIGGS m_jj refusal was a MISSING-VARIABLE
SHADOW (textbook formula itself maxes corr 0.24 on the stored
columns — per-column standardization + mass computed from 4-vector
info absent from the features): the refusal was Isaac being RIGHT.
This law stands as the standing principle for any future atom
family; revisit the coarse refine ladder only if a case shows it
stalling (no optimizing before measured limits).

## The reuse checklist — ask these before writing ANY new mechanism
1. **Which existing organ already does this?** (Check §capabilities below.
   The answer is usually "one of them, turned toward a new input.")
2. **Does the new evidence DOOR ONTO EXISTING NODES?** New channels are new
   door tags on the same concepts — never a parallel system, never a rival
   classifier. All methods, one concept.
3. **Is every quantity MEASURED, not hand-told?** Thresholds → tests.
   Weights → calibration on held-out data. Tolerances → measured spreads.
4. **Does it KEEP its measurements?** If a number was computed for a gate
   (a spread, a residual, a null bar), it is KNOWLEDGE — store it on the
   node. Never compute-and-discard. (The bone-normals lesson.)
5. **Does it have a null?** Expansion proposes freely; compression is the
   null. Never restrict intake — improve the gate.
6. **Does it keep its wrong?** Failures filed with the why; supersession,
   never overwrite; losers wear their defeat. Applies to types, senses,
   lockouts, patterns, fixes, AND the project record itself.
7. **Does it honor hierarchy?** Subgroups are real things under parents
   (abc/abd): styles, senses, variants. NEVER smush by averaging across
   genuinely different sub-things.
8. **Are negatives first-class?** What a thing NEVER shows (past a binomial
   null) is a certified not_ door; candidates violating one are VETOED.
   "It is this or this, but never that."
9. **Identity = relations; pose = a report.** Scale structure over absolute
   scale; rel-angles, ratios, signatures. Tilt/scale/position are stated
   separately, never baked into identity.
10. **Output = rank + veto + abstention.** A shortlist with certified
    nevers beats a forced single answer; a shrug with a diagnosis beats a
    guess.

## The laws (owner's words, all in engine)
- "The less you do, the more you let Isaac do" — self-assembly over
  hand-taught structure; hand-built stays ONLY the epistemics.
- "Knowing what is right is intelligence. Knowing what is wrong is wisdom."
- "Simpler with the same accuracy is better" — a PREFERENCE, not a gate.
- Signed deltas always (darkening ≠ brightening).
- No optimizing before measured limits; no importance-telling.
- Expand, compress, expand, compress (the Intellon rhythm).
- Settle design disputes by BATTERY, not argument.
- **Everything relative; absolute is one correction factor** (owner,
  2026-07-05). Compute in relative space — ratios, signed deltas,
  fractional rates: robust, calibration-free. Any absolute value =
  relative value × ONE factor from a single known anchor (a size, a
  distance, a speed), applied LAST — never baked into the structure.
  Multiple anchors must resolve to the SAME factor (a null); a wrong
  factor scales all absolutes uniformly and leaves every relative
  relationship exact (the graceful failure). Generalizes #9 — the
  relation is the identity, scale is a separate report. (Measured:
  relative range 0.15% vs absolute 18% on the looming test — the error
  lived entirely in an early scale bake-in.)

## Reporting rules (hard)
- **COMPLETE numbers only**: accuracy against the WHOLE task; coverage
  multiplied through ("74% of the 31/200 answered" = 11.5%); perfect on one
  digit of ten = 10%.
- No padding, no "beats chance/baseline" dressing on a low number.
- Plain "% correct", never bare R²/ARI/jargon.

## Current capabilities (one line each; full detail in ISAAC_MANUAL.md)
- **Substrate**: Net (nodes/tagged doors/meta/counts, reverse-indexed);
  compare atom; Scratch; World; findings ledger; save/load/fork.
- **Discovery**: discover() (null-gated enumerator, block-perm valid on
  autocorrelated targets, phase-fold period proposal, one power dial,
  open op family, accounting=100%, residual dossiers, adequacy);
  rivals/confirm/refine/apply_law/validate_law; graded confidence
  (measured decay); capture→interrogate→graduate; composites minted+reused.
- **Consolidation**: crystallizer (admission TESTS, wrong-kept, hierarchy
  between sound types, divergent doors self-assemble); senses-as-nodes;
  waves (groups/handoffs→UPTAKE EDGES/circles/clock/statuses); lockouts
  evidence-weighted + revisable.
- **Composition**: parts/offers/assemble/operable/emergent — wholes with
  arrangement; whole_as_part composes upward.
- **Perception**: observe_spatial (locked/bounded/parts/hinges, 2D→3D lift
  behind trigger + rank-cliff null); stitch_views; complete_symmetry;
  describe_shape (rings/discs/frames/rects/lines, squish, joints, tilt vs
  rel-angle); skeleton bones (keypoints_structural); path_dynamics
  (curve/accel/jerk: line/arc/circle/spiral/s-curve); learn_pattern
  (+VARIANTS per style, per-bone NORMALS kept); compound doors behind
  ceiling trigger.
- **Recognition**: learn_glyphs/recognize_glyph — ALL channels door onto
  the same concept nodes (density, topology, bones, dynamics, exemplars,
  RENDER — owner 2026-07-10: "just print and overlay the nearest font
  number"; attach_symbol_forms puts rendered symbol templates on the
  concept, symbol:<c> -names-> concept:<c> closes polysemy inbound, and
  overlay_delta speaks the signed leftover = expect→subtract→delta,
  D9's vision face; render alone 100% on never-seen fonts, fused
  printed 86→92, handwritten 95.4→95.6);
  measured channel weights; pair judges; shortlist tournament; certified
  NEVERS veto; readable votes. information_ledger (said/caught/reachable/
  ceiling + where). train_readout/extract_readout: ONE softmax layer over
  node outputs as the comparator, extracted LOSSLESSLY into signed
  evidence equations (linear = the net IS the equation).
- **Interaction**: interaction_map (signed affects+/- graph, null-gated,
  noise refuses) + explain_link (translation factors: a link that DIES
  under stratum-matched conditioning is a CHAIN; near-threshold discrete
  terminal hops named PREEMPTIVE SIGNALS — the fireworks law). Identity
  includes the effect profile. STILL OPEN from the owner's same message:
  metastructure crystallization (components→humanity→civilization — the
  D1 tower), edges-of-things (boundary finding), interaction-as-identity
  recursed to every level.
- **Trust**: calibration audit; law_confidence (measured decay curve);
  0/20 false discoveries on noise; refusals are answers.

## Where things stand (complete numbers, 2026-07-09)
MNIST fused **95.0–95.2** (trained+extracted readout over node outputs;
hand-calibrated 92.2; pixel-softmax 86.0) | truth-in-shortlist ~97–98 |
covtype 59.1 | HIGGS classify **71.18 / AUC 0.7886** (higgs_pairs.py:
1D signals + 220 pair doors admitted by interaction excess, printable
softmax; 1D-only 68.07/0.7479; eqn road: transverse mass SAID; deep-net
0.885 NOT matched) | CIFAR 32.6 (needs texture percepts) | clocks 22.9
(pixel bridge open) | Kepler/planted laws EXACT.

## Standing next-lever list
Full training data (free) → self-assembled patch-percept retina (CIFAR's
door type) → per-variant duels → captures as ledger witnesses +
interrogation at scale → effect entities (D9, the engineer's core) →
SRBench (the differentiated lane).
