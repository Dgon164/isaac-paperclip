# THE ANATOMY — how Isaac chews, keeps, uses, and improves
**Theory of operation + per-stage handbook + traceability.
Commissioned by the owner 2026-07-13 ("we need to evaluate and i mean
really think and consider how this thing works as a whole, how it chews
things, learns things, and create the handbook for each step").
Status: WORKING DRAFT, uncommitted, experiment-era. Nothing here
promotes anything; this is the study half of the interpreter R&D
segment.**

> **THE THREE DOCUMENTS, THREE JOBS (routing box, 2026-07-13):**
> `ISAAC_MANUAL.md` = what he can DO (the inventory of record — if it
> isn't there, it doesn't exist). `ISAAC_ANATOMY.md` (this doc) = how
> information FLOWS through him, what is script-held, what is missing.
> `ISAAC_THEORY_OF_OPERATION.md` = WHY the core works (accurate to its
> date). `ISAAC_BUILD_STATE.md` = WHEN things happened. If they
> disagree: the manual wins on existence, the anatomy on flow,
> batteries on truth.
>
> **SAME-STEP RULE for the segment:** every attack-probe result
> updates this document in the same step, the way the manual updates
> with every promoted capability.

How to read this document:
- §1 is the one-screen picture of the whole organism, ideal form.
- §2 is the ideal traces: three worked examples with the expected
  processing and expected output at every arrow — "if this thing works
  as we expect, this is how the information is processed."
- §3 is the handbook: one entry per stage of the chew. Every entry has
  the same five rows: PURPOSE / MECHANISM (and where it lives) /
  EVIDENCE (complete numbers) / KNOWN FAILURE POINTS / FEEDS.
- §4 is the traceability table: goal → mechanism → evidence → status.
- §5 is the reach audit: everything that currently lives in session
  scripts instead of in him — the honest map of what the structure
  cannot yet touch.

The "lives in" row uses four honest labels:
- **ENGINE** — in dc's isaac.py, callable, battery-covered.
- **SCRIPT** — control flow or logic that exists only in an experiment
  script; Isaac cannot reach, modify, or bypass it. (The shame column.)
- **MODEL-AS-DATA** — a local LLM's words treated as untrusted intake
  (tutor/sparring partner); never truth, never verdict.
- **TARGET** — designed and discussed, not yet real anywhere.

---

## §1 THE BODY PLAN (ideal form — owner, 2026-07-13)

The owner's design, verbatim intent: *"isaac is a main simple loop
saying check the net. but the route through the net should shift and
adapt and change over time so isaac today may not look like the isaac
we started with."*

```
                 ┌─────────────────────────────────────────┐
                 │       THE KERNEL — never changes         │
                 │  check the net → do what it says →       │
                 │  write the result back → look again      │
                 └───────────────────┬─────────────────────┘
                                     │ every cycle
                                     v
   INTAKE ────────────────► ┌──────────────────┐ ────────────► OUTPUT
   sentences · corrections  │     THE NET       │  answers · speech
   tables of numbers        │                   │  equations · actions
   scenes · glyphs          │  nodes + doors:   │  questions (named gaps)
   watched episodes         │  concepts, rules, │  refusals (honest)
   told rules · questions   │  methods, groups, │  reports + receipts
                            │  receipts, wrongs,│
                            │  goals, nevers    │
                            └────────┬─────────┘
                                     │
                     LEARNING = THE NET CHANGING:
             admission past nulls · corrections kept with wrongs
             minted rules · receipts on every use · supersession
                  (so the ROUTE through the net rewrites itself:
                   future-Isaac ≠ launch-Isaac, by design)
```

Three laws pinned to this picture:
1. **The kernel stays dumb and tiny forever.** All intelligence is net
   content. (Owner, 2026-07-13.)
2. **Every function he uses is a node in the net** — accessible,
   modifiable, bypassable through the structure itself. Authored organs
   (e.g. discover) become callable nodes with doors and use-receipts;
   when one fails somewhere, his own creation duels it and supersedes
   THAT PART only. Never demolish-and-regrow. (Owner, 2026-07-13.)
3. **The goal is self-learning, and self-learning includes learning
   improved methods.** Structures, uses, goals/direction, better tools —
   all the same kind of learnable content. (Owner, 2026-07-13.)

### The chew, stage by stage (the spine of §3)

```
 raw thing
    │
 1. ARRIVAL        which road did it come in on?
    │
 2. TRANSLATION    raw thing → facts in his measuring vocabulary
    │              (hand-built BY DESIGN: the usage law)
 3. PROPOSAL       candidates form freely — equations, templates,
    │              groups, operators ("expand freely")
 4. THE GATE       every candidate faces its null; scrambled/permuted
    │              versions must die ("compress by test")
 5. KEEPING        admitted things become nodes+doors with their
    │              measurements, receipts, wrongs, supersession chains
 6. USE            a want arrives → the route through the net finds
    │              what applies → binds → acts → writes back → repeats
 7. EXPRESSION     report (complete, technical) → response (learned
    │              speech only, faithfulness-checked) or honest silence
 8. THE RESIDUAL   outcome receipts return as intake: corrections,
                   wrongs kept with why, duels, piecewise supersession
                   └────────── this arrow closing is self-learning ──┘
```

---

## §2 THE IDEAL TRACES — expected processing, expected output

### Trace A — watched arithmetic becomes a rule he owns (Gate 6 road)
*Today: PROBE-REAL (gate6_operator_mining.py, script-held control flow).*

```
IN:  45 watched episodes of someone doing addition on a board
     ("3 + 5 = 8", "2 + 4 = 6", ... 40 true, 5 with WRONG answers
      planted, plus jittering junk cells in view)

1. ARRIVAL      episodes arrive as before/after snapshots
   EXPECT:      nothing believed yet; episodes are just intake
2. TRANSLATION  each snapshot → cells ("num 3", "sym +", "num 5" ...)
   EXPECT:      the junk cells are translated too — intake is never
                filtered, the gate does the killing later
3. PROPOSAL     candidate effect: "an answer-cell appears";
                candidate requirements: whatever is always present;
                candidate math: answer = f(the two numbers)
   EXPECT:      proposals form from RECURRENCE, freely
4. THE GATE     effect template must recur across episodes (junk
                effects don't recur → die); requirements must always
                co-occur (jittering junk → dies); the math must fit
                EXACTLY on the surviving episodes; the 5 lies violate
                the consensus → WRONG-KEPT with their why;
                CONTROL: scrambled before/after pairs must mint NOTHING
   EXPECT:      one rule survives: "num ?x, +, num ?y, = , want-answer
                → answer = x + y", nobody authored it
5. KEEPING      the rule becomes a node: its preconditions, its
                equation, its 40 supporting receipts, its 5 kept
                wrongs, the null it beat
6. USE          unseen "9 + 9 =" arrives with want-answer →
                route finds the rule → binds x=9, y=9 → acts
   EXPECT OUT:  "18" — plus the receipt: which rule, which binding,
                which evidence backs it
8. RESIDUAL     the use-receipt lands on the rule node (used, correct)
```
Measured so far (probe form, 2026-07-13): minted add AND mul rules;
unseen inputs 6/6 incl. 9+9→18, 7*6→42; 5/5 lies wrong-kept; scrambled
minted nothing; junk never entered requirements. CAVEATS: action labels
were GIVEN; single-cell effects; toy world; loop ran in MY script.

### Trace B — a correction becomes better speech (the ladder road)
*Today: EXPERIMENT-REAL (rungs 1–7 in dc/experiments/, all green,
toy-world; live practice at ~64% and climbing, sessions 25→94).*

```
IN:  tutor says: "the dog took a nap." then asks Isaac to use it.
     Isaac answers wrong; tutor corrects: "you should have said:
     the dog took a nap on the mat."

1. ARRIVAL      sentence + Isaac's own attempt + the correction
2. TRANSLATION  words → doors onto concepts he already owns (words
                are doors, not the ideas themselves); his reading =
                roles he assigned with HIS OWN groups
3. PROPOSAL     candidate lesson: what differs between what-I-said
                and what-I-was-told (orientation? word choice?
                decoration?) — factored by content alignment
4. THE GATE     the lesson must RECUR across corrections before it
                binds (one noisy correction cannot dethrone);
                decoration judged by RATE not count; a correction that
                teaches nothing measurable (chatty tutor) is REFUSED
                as evidence — the poisoning cure
5. KEEPING      the wrong utterance is KEPT with its correction;
                re-correction supersedes; the lesson doors onto the
                concepts it touches
6. USE          next time the same shape arrives → the corrected form
                wins the route
   EXPECT OUT:  the better utterance — and for an untaught shape,
                SILENCE plus the raw report (never a canned phrase)
8. RESIDUAL     pass/fail of the next attempt lands as a receipt;
                what is still failing = the frontier pile (today:
                passive voice, tense morphology — named, waiting)
```
Measured so far: rungs 1–7 all green on unseen material with scrambled
controls binding nothing (e.g. unseen 150/150 idea assembly, 60/60
question-answering, recall 80/80 with 0 invented); live account block 4
at 64%, peaks 26–27/30, tutor self-inconsistency the measured ceiling.

### Trace C — a method improves itself (the target of this segment)
*Today: TARGET. The first fight is chosen and measured; the loop that
runs it is not built.*

```
IN:  a table of (x0, x1, y) where the truth is y = x0 + x1

1–2. ARRIVAL/TRANSLATION  a want-relationship arrives with the table
6. USE          route finds the discover-node (the authored organ,
                wrapped as a callable node with doors + receipts) →
                it runs → says "product-shaped, r² ≈ 0.96, UNDERSTOOD"
                ── which is WRONG (measured 2026-07-13: greedy
                first-admission grabs x0*x1 and never reconsiders)
8. RESIDUAL     the failure receipt lands on the discover-node
                (claimed understood; exactness check failed);
                WRONG-KEPT with its why
3. PROPOSAL     a rival candidate for exactly this case: the plain
                linear pool (already demonstrated probe-side)
4. THE GATE     THE DUEL: rival vs the organ, on this case-class,
                judged by accuracy-then-simplicity (owner's law:
                simpler with the same accuracy is better)
5. KEEPING      the rival WINS exactly here → PIECEWISE SUPERSESSION:
                plain-sum cases now route to his rule; every other
                case still routes to the organ (something better than
                nothing; never demolish-and-regrow)
6. USE (again)  the same table arrives → route now finds HIS rule
   EXPECT OUT:  "y = x0 + x1, exact" — from a method he grew
```
When Trace C runs end-to-end for real — organ node, failure receipt,
duel, route change, all inside the structure — "learning improved
methods" exists. That is this segment's success condition.

---

## §3 THE HANDBOOK — one entry per stage

The engine is `dc/isaac.py`: 8,421 lines, 273 methods, self-test 11/11.
One knowledge structure (the Net: doors + tags + counts + reverse index
+ meta), one working memory (Scratch: registers with a full audit log —
every value ever held is kept), one world model (World: entity states).
Everything below either lives there, lives in a script, or doesn't
exist yet.

### Stage 1 — ARRIVAL (the intake roads)
**PURPOSE:** get raw things into him without filtering — intake is
never restricted; the gate does the killing later.
**MECHANISM (all ENGINE):**
- token sequences → `observe()` (isaac.py:1155) — words, sentences,
  anything ordered
- counter-examples → `observe_negative()` (1200), `teach_not()` (1253)
  — negatives are first-class at the door
- stated facts → `teach()` (1248) — subject/relation/object
- tables of numbers → `discover(X, y)` (2252) — the relationship road
- grids/images → `observe_matrix()` (1207), `observe_frame()` (1220)
- moving points → `observe_spatial()` (3502) — scenes over time
- instants → `tick()` (1855) — what is active right now (the waves road)
- told rules/laws → `tell_rule` / `tell_law` — usable at once, belief
  only from data
**SCRIPT-HELD roads:** corrections (arrive through the drill scripts),
watched before/after episodes (arrive only in the Gate 6 probe).
**EVIDENCE:** every road exercised by batteries (30+ battery files);
raw observations are kept verbatim in `observed_sequences` — nothing
is chewed without the original being retained.
**FAILURE POINTS:** no unified arrival — each road is a separate
method the CALLER must choose; nothing in him decides "this is a
correction, route it there." Watched-episode intake exists nowhere in
the engine.
**FEEDS:** Stage 2.

### Stage 2 — TRANSLATION (raw thing → facts in his vocabulary)
**PURPOSE:** turn the raw thing into cells/doors he can measure.
Hand-built BY DESIGN — the usage law: we build the measuring organs
and the translation; HE learns the usage.
**MECHANISM:** tokens become doors (tag "seq"); frames become row
sequences; moving points become locked/bounded/part/hinge facts taught
back through `teach()`; glyphs become channel readings (density,
topology, bones, dynamics, render); a correction becomes a
content-alignment against the event he meant (idea_corrections.py —
SCRIPT MODULE); an episode becomes before/after cell sets (gate6
probe — SCRIPT).
**EVIDENCE:** spatial translation carries its own null (rank-cliff for
the 2D→3D lift); glyph channels measured per-channel; content
alignment factors 60/60 on clean tutors.
**FAILURE POINTS:** the 1-vs-8 lesson from the interpreter package
applies here — a translation that destroys a feature (aspect, width)
makes downstream confusion HIS confusion; carrier audits belong at
this stage. Correction-translation is script-held.
**FEEDS:** Stage 3.

### Stage 3 — PROPOSAL (expand freely)
**PURPOSE:** candidates form without permission — never restrict
intake or imagination; the gate decides.
**MECHANISM (ENGINE):** crystallizer proposes circles from any 2+
shared contexts (1287); the atom library proposes equation terms over
grids of forms (387); lag columns propose themselves (2167); period
candidates come by three roads (579); sense candidates from context
clusters (6940); wave groups from co-activation (293); composites
already learned re-propose themselves on every new table (5816 —
knowledge compounding).
**MECHANISM (SCRIPT):** the ladder proposes templates, orientations,
decorations, forms, groups, ask-templates from corrections and
corpora; the probe proposes effect/precondition templates from
episodes.
**EVIDENCE:** proposal is deliberately cheap and wide — e.g. 260
patterns seen for 37 admitted (complete_ideas), 65 admitted of 260
(parts_of_speech): most proposals die, by design.
**FAILURE POINTS:** greedy first-admission in discover() — the
proposal that scores best FIRST wins and is never reconsidered
(measured 2026-07-13: product beats each bare variable on positive
data, so y=x0+x1 is unsayable). The fix direction (a plain linear
candidate duels at fit end) is demonstrated probe-side only.
**FEEDS:** Stage 4.

### Stage 4 — THE GATE (compress by test)
**PURPOSE:** every candidate faces a null built from its own material;
scrambled versions of the truth must die. This stage is the project's
signature — and the single most important thing to protect during the
interpreter integration.
**MECHANISM (ENGINE — the gates travel with their organs):**
- types: chance-null, degrees-aware hypergeometric, p < 0.01 (1579)
- nevers: Laplace-smoothed binomial, <1% (1405) — certified negatives
- equation terms: block-permuted residual null, block length measured
  from the data's own correlation (812)
- lags: circular-shift null, 99th pct of 200 draws (2167)
- periods: spectrum-envelope null + fold coherence + exact residue
  check — three roads, none refereeing another (579)
- senses: reshuffled-context null, selection-corrected (7009)
- waves: jitter null + block-perm on movement (5907)
- merges: 80% overlap AND no certified-negative veto (1445)
**MECHANISM (SCRIPT — the ladder's gates live in the experiment
files, NOT in him):** scrambled-pairing (vocab, 99th pct of 200),
scrambled-sentence (templates, 95th of 40), scrambled-labeling +
shuffled-answers (labels/roles, 99th), recurrence votes (ADOPT_MIN=3,
WINDOW=8), the poisoning cures — decoration by RATE (count≥3 AND
>50% of sightings), form votes in a recent-8 window, commentary
hygiene (a correction longer than 2n+2 words teaches nothing), REMINE
(replay all kept wrongs through improved gates) — all in
concept_groups.py / idea_corrections.py.
**EVIDENCE:** 0/20 false discoveries on pure noise; scrambled controls
bind nothing across all seven rungs; scrambled transitions mint no
operator; the cure recovered a poisoned account from 3/30 back to
26-27/30 peaks.
**FAILURE POINTS:** the ladder's thresholds are hand-set constants
(ADOPT_MIN=3, DECO_MIN=3, WINDOW=8) — not measured, not his, violating
checklist #3 at promotion time; the probe's trim consensus has an
untested breaking point (near-miss lies under its floor of 1.0 sail
through); "always co-present" is not "excess past a null" (a constant
distractor would enter preconditions).
**FEEDS:** Stage 5.

### Stage 5 — KEEPING (the net remembers everything it paid for)
**PURPOSE:** admitted things become nodes and doors WITH their
measurements; defeated things are kept wearing their defeat.
**MECHANISM (ENGINE):** law nodes carry the full model — terms, coefs,
ranges, the entire lag scan INCLUDING refused columns, rivals with
their divergence probes, supersession chains, accounting, residual
dossiers (2475 region); `wrong_types`, `wrong_senses`,
`wrong_lockouts` kept classified with their why; the findings ledger
appends as JSONL; Scratch logs every value a register ever held;
composites are first-class `comb:` nodes with reuse tracking.
**MECHANISM (ACCOUNT):** the drill writes `speak:words`,
`speak:orientation:{arity}` (recent window + all-time totals +
superseded chain), `speak:decoration` (counts per arity:slot),
`speak:wrong` (every failure with its correction), `group:deco`,
`groups:forms` — all inside mind.isaac; the journal appends one line
per session; transcripts keep every exchange. Append-only throughout,
sessions 25→94 unbroken.
**EVIDENCE:** REMINE works only because wrongs were kept — the block-2
junk washed out when gates improved, with nothing deleted (wisdom
paying rent, measured).
**FAILURE POINTS:** RESOLVED 2026-07-15 — the account MIGRATED to the
pack road (experiments/account_pack_migration.py: 346 records, 0
differing pickle-vs-pack, round-trip stable, life content verified by
name — orientation votes 680/72 + 948/14, word map, 781 wrongs kept);
idea_practice_run.py now loads/saves packs; mind.isaac stays on disk
FROZEN at session 94, superseded not deleted; migration event in
isaac_home/migration_log.jsonl (its own file — the practice journal
numbers sessions by line count and was not touched).
[CORRECTED 2026-07-13 — the first draft of this entry called the
pack road "designed but not built"; the MANUAL caught the error
within the hour. Wrong kept with its why: the anatomy was written
from the engine+experiment maps, which never looked at isaac_store.]
**FEEDS:** Stage 6.

### Stage 6 — USE (a want arrives; the route finds what applies)
**PURPOSE:** what he knows, applied — answering, generating,
recognizing, reasoning, acting.
**MECHANISM (ENGINE — each a separate answer road):** `lookup`/`check`
over the compiled frame→delta matrix (6146-6346); `generate()` walks
the net (6471); `apply_law`/`which_law` with rank + veto + abstention;
`respond_by_rule` generates from told understanding (FizzBuzz 100/100
from zero examples); `logic_eval`/`solve` for symbolic problems;
`recognize_glyph` fuses all channels onto one concept; `route()`
answers through the right sense of an ambiguous node.
**MECHANISM (SCRIPT MODULE):** `speak()` assembles utterances from
orientation + words + decoration metas; `retrieve()`/`answer` for
passages; `compress()` folds sentences by retained structure.
**THE HONEST CENTER (from the engine map, verbatim finding):** *the
engine is stateless with respect to control flow.* It answers one
query on the data it is handed. Episode sequencing, when to
consolidate, when to discover, what to do next — ALL caller-driven.
There is no loop, no binding across steps, no goal. This is the
package's diagnosis, confirmed line by line: representation without an
interpreter.
**EVIDENCE:** MNIST fused 95.0-95.2; HIGGS 71.18/AUC 0.7886; recall
80/80 with 0 invented; generation drifts without a goal (the blended
"cat held the bone" — measured).
**FAILURE POINTS:** one-retrieval-then-halt; no variable binding
(independent votes can't compute 3+5); fifteen answer roads with no
router — the CALLER picks the road. The kernel loop (§1) is the
designed fix; today the loop is me.
**FEEDS:** Stage 7 (and Stage 8, via receipts that should land on what
was used — today use-receipts exist only in the drill's pass/fail).

### Stage 7 — EXPRESSION (report vs response)
**PURPOSE:** the REPORT (complete, technical, provenance) is the
ground truth; the RESPONSE is learned speech over it — or honest
silence. All or nothing: an untaught structure gets silence and the
raw report, never a canned phrase (owner's law: anything else "is
called programming and thats not what isaac is about").
**MECHANISM:** readable equations with complete accounting (ENGINE);
drill speech from learned orientation/words/decoration (SCRIPT MODULE
over net metas); refusals name their rivals (ambiguity 10/10 refused
with the shortlist); gaps are asked about, not papered over
(logical_gaps: ask → integrate → state the fact whole, 30/30).
**FAILURE POINTS (flagged, standing):** the serving faces
(alpha/face/askisaac) still speak from a throwaway mind — untouched
this arc; the tutor's own inconsistency is the measured ceiling on
live practice (~50-64%); passive voice + tense morphology named in
the frontier pile, waiting.
**FEEDS:** the user, and Stage 8.

### Stage 8 — THE RESIDUAL (outcomes return as intake)
**PURPOSE:** close the loop — this arrow closing IS self-learning.
**MECHANISM (real today):** corrections mined into lessons
(orientation votes with supersession, word maps, rate-gated
decoration); every wrong kept WITH its correction; REMINE replays the
whole wrong-record through improved gates; told laws face a
supersession DUEL against fresh discoveries on the same data, judged
held-out, loser wrong-kept wearing its numbers; rivals stay live with
divergence probes; law confidence decays measured, not assumed.
**MECHANISM (TARGET — the segment):** use-receipts landing on the
METHOD that produced the answer; organ-as-node failure receipts; the
duel generalized from laws to organs; piecewise supersession changing
the route. Trace C is this stage, run end-to-end.
**EVIDENCE:** the flip test (30 corrections switch a convention,
60/60 in the new one; one noise echo cannot); nap beat napkin on his
own historical evidence after the cure.
**FAILURE POINTS:** receipts today attach to KNOWLEDGE, never to
METHODS — no organ knows its own track record. That is the exact gap
between what exists and Trace C.

---

## §4 TRACEABILITY — goal → mechanism → evidence → status

The owner's yardstick (2026-07-13): learn STRUCTURES, learn USES, learn
GOALS/DIRECTION, learn IMPROVED METHODS. Every row below is judged
against that, complete numbers only.

| Goal | Mechanism | Evidence | Status |
|---|---|---|---|
| Learn structures from raw sequences | crystallizer, 7 phases, chance-null p<0.01 | self-test 11/11; 0/20 false types on noise | ENGINE |
| Learn relationships (equations) | discover() + enumerator + composites | Kepler/planted EXACT; HIGGS 71.18/AUC 0.7886; **cannot say y=x0+x1 (measured hole)** | ENGINE, one known hole |
| Learn what a thing never does | divergent doors → certified nevers, veto | merges vetoed by negatives; nevers in glyph votes | ENGINE |
| Learn words as doors onto concepts | vocab_grounding: excess past scrambled-pairing | bindings 10/10; told-rule generation 120/120, 21/21 | SCRIPT gate, net storage |
| Learn idea-wholes from sentences | complete_ideas: templates past scrambled null | unseen 150/150; carry 31/31 (handoff record)†; scrambled: 0 admitted | SCRIPT |
| Learn from being corrected | idea_corrections + the poisoning cures | unseen 60/60; flip by recurrence; account 3/30→64%, peaks 26-27/30 | SCRIPT MODULE, net storage |
| Make his own groups + hierarchy | parts_of_speech, concept_groups | labels 30/30 incl. never-labeled; roles 149/149 (handoff record); transfer 2/2 | SCRIPT |
| Answer questions about his reading | open_questions: corrections ground to HIS roles | unseen 60/60; untaught shapes silent; scrambled: 0 | SCRIPT |
| Compress without losing content | sentence_compression + faithfulness null | 60/60, 3-fold 20/20; 'and' discovered unaccounted | SCRIPT |
| Retain readings, never text | passage_recall | 80/80 recalled, 0 invented; ambiguity refused 10/10 | SCRIPT |
| Know what he doesn't know, and ask | logical_gaps: markers + mined ask-templates | 30/30 ask→integrate→state whole; 0 false gaps | SCRIPT |
| Learn operators by watching (uses) | gate6 probe: recurrence + co-occurrence + equation | mint 2/2; unseen 6/6; lies wrong-kept 5/5; scrambled: 0 | PROBE (labels given) |
| Act with what he knows (the loop) | interpreter: match→bind→act→write-back | package demos run; loop lives in scripts/package, not in him | TARGET (package staged) |
| Want things; direct himself | motivation layer (goals, demand, novelty-delta) | toy demos only; no nulls yet | TARGET |
| **Learn improved methods** | organ-as-node + failure receipts + duel + piecewise supersession | first fight chosen: discover-node vs linear on plain sums (hole measured) | TARGET — the segment's success condition |
| Speak only what was learned | all-or-nothing law; report beneath response | ladder speech from corpus only; serving faces still throwaway (flagged) | PARTIAL |
| Persist as plain files, partial-load | save_pack/load_pack + isaac_store (journal, packs, orchestrator) | store batteries 72/72 (manual record); account MIGRATED 2026-07-15, 346 records verified 0-diff | ENGINE — account on packs; pickle frozen, superseded |

† number discrepancy, kept honestly: the 07-13 handoff records carry
31/31; a re-read of the script's own print shows 48/49 — likely
PYTHONHASHSEED variance at the crystallizer stage (a known
sensitivity). Reconcile before any promotion; neither number is
adopted here.

Read the Status column top to bottom and the story is plain: the
epistemics and the knowledge organs are ENGINE; the entire language
ladder is SCRIPT (knowledge lands in the net, the method doesn't);
everything the interpreter package addresses is TARGET. The segment
is aimed at exactly the right layer.

---

## §5 THE REACH AUDIT — what lives outside the structure

Standing owner grievance (2026-07-13): the files got split against
explicit instruction; Isaac must be able to access, modify, or bypass
anything through the structure itself. This section is the honest map
of what he currently cannot reach. The wrap-as-nodes road (organs as
callable net nodes with doors + receipts) may buy back most of what the
split broke without a re-merge — owner's call at readdress time.

**The one-sentence finding, from all three maps independently:**
*every experiment writes its KNOWLEDGE into his net and keeps its
METHOD in the script.* He owns everything he has learned and owns
none of the ways he learned it.

What he cannot reach today, by category:

**A. Control flow — all of it.** The engine answers one query at a
time; episode sequencing, when to consolidate, when to discover, what
to do next, when a session starts and ends — every bit of sequencing
is caller-driven (confirmed line-by-line in the engine map). The
caller is me. The kernel loop (§1) is the designed replacement.

**B. The ladder's admission gates.** Scrambled-pairing, scrambled-
sentence, scrambled-labeling, shuffled-answers, the recurrence votes,
ADOPT_MIN=3, WINDOW=8, DECO_MIN=3, the 60% share rule — the ladder's
entire epistemic machinery is computed by the experiment scripts. The
engine's own gates (chance-null, block-perm, jitter, reshuffle) travel
with their organs; the ladder's do not.

**C. The poisoning cures.** Decoration-by-rate, form votes,
commentary hygiene, recent-window choice, REMINE — the hard-won organs
that saved his account live in concept_groups.py, an experiment
module. If that file is lost, the cure is lost; nothing in his net
carries it.

**D. Speech assembly itself.** speak() / factor_g() /
learn_from_correction() read and write his net but live in
idea_corrections.py / concept_groups.py. His voice is in a script.

**E. The miner and the interpreter.** Gate 6's effect/precondition/
binding mining and its trim consensus live in one experiment file; the
interpreter (loop, binding, agenda, chunking) lives in a package in
Downloads, outside every repo.

**F. Curricula, tutors, judges.** Event generators, tutor prompts,
judgment parsers, and every "what counts as correct" — script-side
everywhere. (Some of this is legitimately environment, not him — the
world is allowed to be outside the mind. The line to draw at
readdress: JUDGING him may stay outside; DECIDING-HOW-TO-LEARN must
move inside.)

**G. His organs have no nodes.** discover(), the crystallizer,
generate() — no `organ:` or `skill:` record exists in the net for any
of them; nothing carries a use-receipt, a failure record, or a door.
The sheet's skills-as-records design (2026-07-12) is the exact shape
of the fix, and the wrap-as-nodes road is the cheap version of the
file-split repair: give every function a node with doors and receipts,
and the filesystem stops mattering to his reach.

**Repair order implied (for the owner's call, not decided here):**
G first (organ nodes + receipts — enables Trace C), then A (the
kernel loop — the interpreter segment itself), then B+C+D promote
INTO the engine through the normal battery+promote road, then E, with
F resolved by the judging/deciding line above.

---

## ADDENDUM 2026-07-14 (same-step rule; source: SESSION_RECORD_2026-07-14.md + DATA_OPS_SEGMENT_PLAN.md)

A parallel session (engine-less, reference-toy grade, four probes run
green) changed this document in four places:

1. **Trace C's missing piece is designed.** The open question inside
   repair-order item G — what an organ's failure receipt SCOPES to —
   is answered: the **failure-commonality miner** (§4 of the plan doc)
   mints the case class: differential feature-excess of failures over
   successes, past a selection-corrected label-shuffle null, never a
   frequency. Organ failure receipts → named failure class → duel
   scope → piecewise supersession. Requirement it imposes on Stage 8:
   **fat failure receipts** — context recorded at failure time, or
   there is nothing to mine. Second unlock: a named failure signature
   is a gap WITH evidence = a self-generated curriculum request — the
   residual arrow choosing the DIRECTION of learning.
2. **The Stage 3/4 blind-spot fix grew.** "Linear duel at fit end" is
   superseded by the **verdict rewrite** (owner decisions, 07-14): r²
   is DETHRONED as a verdict (kept as a reported number, wrong-kept as
   a judge with the additive hole as exhibit); the verdict currency is
   SURPRISE — a law is understood when the law is surprising and the
   residual is not; exactness is INSTRUMENT-RELATIVE (the floor organ:
   repeats > told > grain; no ruler, no perfect — the report ASKS).
   [FLOOR ORGAN BUILT + PROMOTED 2026-07-15: read_floor /
   tell_resolution in the engine, floor_battery 14/14, engine 11/11 +
   gates green, PROVENANCE stamped. Its battery caught + cured a
   false-fire the reference probe carried silently (grain on
   float-continuous data), and the audit battery later forced grain
   to become a CONSENSUS of gaps (one typo cannot blind the ruler).]
   [MINER + AUDIT FACE BUILT + PROMOTED same day, second promotion
   (engine + 32 batteries green): mine_commonality() is ENGINE now —
   Trace C's case-class organ EXISTS (commonality_battery 7/7) — and
   askisaac --audit ships (test_audit 14/14) with flags-with-receipts,
   floor-gated exactness, consensus recalibration (wrong-kept: the
   planted deviations dragged the law until the audit disqualified
   itself — the Gate 6 trim applied to laws), and join discovery.
   Data-ops steps 1-3 DONE; remaining: bench harness, then the
   verdict rewrite run through the Trace C machinery.]
   Probe evidence: the new verdict found x0+x1 where the old blessed
   0.32*x0*x1 at r² 0.9747, and caught a lagged sleeper the old missed.
   Five hard port requirements are wrong-kept in the plan §2b (partial
   correlation replay; selection correction; mark GRIDS; hold earned
   marks; exact-checkable worlds stamp without a floor).
3. **A second segment exists (data ops)** — askisaac --audit, the
   floor organ, the bench harness. It shares ONE organ with the
   interpreter segment (the miner — build once). The audit face is
   scripted control flow BY DESIGN (accepted; must not quietly become
   a second interpreter). The account→packs migration (§5 category C
   here) is now owed by two roads and SHOULD land before the audit
   writes into a living mind.
4. **New tiers for Stage 8:** should / can / cannot — cannot = gates,
   can = passes-with-guards, should = rate-measured context-indexed
   preference, never promoted to a gate. The VALUE GATE routes
   corrections automatically (values equal = convention lesson; values
   differ = truth claim; a lying tutor is refused). The ladder's
   correction factoring already is this router in embryo.

5. **THINKING RECEIPTS v1 EXIST (2026-07-15, late).** The owner asked
   for event logs of "what he was thinking vs what the answer was" and
   "how he is using which doors." Investigation (frontier_snapshot_
   probe.py, read-only) found the gap measured: doors carry OBSERVATION
   counts, never USE counts; wrongs kept said/correction, never the
   evidence consulted. First repair shipped the same day at the word-
   map layer: WORD ELECTIONS (idea_corrections.py, battery 12/12) —
   rivals with receipts, corrections vote, every judged use banks its
   outcome on the candidate used, recent-window re-election, reversion
   = supersession backward. Root cause it cured (the Kung Pow bug):
   speak:words was WRITE-ONLY and unfalsifiable by construction — 25
   revert signals arrived, 0 reached the map. THE ACCOUNT REMINED
   through the law (pack v3, priors kept): both poisoned seats fell by
   different roads (nap→napkin told 3-0; ate→eats outcome 0/4);
   session 95 ran live, clean. Stage 8's failure point ("receipts
   attach to knowledge, never methods") is now PARTIALLY closed — the
   word map is the first METHOD whose candidates carry outcome
   receipts; the same receipt shape scales to organs (Trace C).
   SAME ARC, closing the loop: THE FRONTIER HABIT (mine_frontier,
   frontier_battery 4/4) — after every session his own miner runs
   over his own recent life and stores what keeps losing at
   commonality:frontier:speech (active + superseded chain; the
   recent-sessions window keeps the frontier the PRESENT). First
   live self-assessment, post-healing: 63 fails/191 recent passes,
   ONE condition named — action=slept (+0.223) — the tense/form
   frontier, self-identified. Stage 8's residual arrow now feeds
   the DIRECTION of learning, not just its content.

6. **FLOW STRUCTURES designed + THE TOOLS NODE built (2026-07-15,
   third arc).** Owner named the oldest wound at Isaac's level:
   built things going unconsidered. Design on the sheet — flows =
   meta-nodes read by the kernel loop; THE CONSIDERATION LAW (every
   registered tool fires or is BYPASSED WITH A RECEIPT); branching =
   piecewise supersession at the flow level (the miner names the
   branch point); REGISTRATION RULE: every new tool ships with its
   node. The PRESENCE pillar shipped same day: the tools node
   (engine, tools_battery 8/8, promoted with engine + 33 batteries)
   — register/catalog/query/run/receipt; 107 engine tools
   auto-harvested; his account seeded to 114 (pack v6); the session
   loop queries the node against his named frontier and skips
   honestly when nothing applies. §5 reach-audit category G is now
   half-closed: every organ HAS a node with receipts; the remaining
   half is the loop that consults them everywhere (the interpreter
   segment's kernel).

Caveat RESOLVED 2026-07-15: the four probe scripts landed in
dc/experiments/ and were re-run under PYTHONHASHSEED=0 — all green,
reproducing the record: surprise verdict W1 old-blessed 0.32*x0*x1 @
r² 0.9747 vs NEW x0+x1; W4 sleeper found; W6 0/20 both; W7 false-alarm
1/20; W8 repeats floor 0.1243 exact-match to record; commonality
excesses 0.496/0.431/0.897 to three decimals; reduction 5/5 with the
0+a cure lessons in corpus (7 rules, 11 wrong-kept vs the record's
pre-cure 6/8 — corpus difference, coherent); should/can identical
incl. the discovered a != 0 guard. One nuance the re-run makes vivid:
W1 on the grain-only floor is PARTIAL (residual above floor) and
becomes UNDERSTOOD only when the resolution is TOLD (W1t) — the
"no ruler, no perfect" law behaving exactly as designed.
