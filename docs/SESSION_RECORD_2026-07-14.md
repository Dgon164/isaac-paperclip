# SESSION RECORD — 2026-07-14
**The verdict rewrite arc: r² dethroned, exactness-first, taught
reduction, should-vs-can, failure commonality, and the data-ops plan.
Everything discussed this session, with complete numbers. All code
produced here is REFERENCE-TOY grade (probes, not engine); nothing
integrates without its own battery + the promote cycle. Companion
artifacts (5): `surprise_verdict_probe.py`, `taught_reduction_probe.py`,
`should_vs_can_probe.py`, `failure_commonality_probe.py`,
`DATA_OPS_SEGMENT_PLAN.md`.**

*(Transcribed to disk 2026-07-14 from the authoring session's paste;
em-dashes/arrows re-encoded, content verbatim. UPDATE 2026-07-15: all
four probe scripts landed in dc/experiments/ and re-ran GREEN under
PYTHONHASHSEED=0, reproducing the numbers below — incl. W8's floor
0.1243 to the digit and the commonality excesses to three decimals.
The reduction corpus on disk includes the two 0+a cure lessons, so it
mints 7 rules / 5-of-5 unseen, matching §6's post-cure state.)*

---

## §1 The review pass (where the session started)

Full read of ISAAC_ANATOMY / ISAAC_MANUAL / THEORY_OF_OPERATION as of
the 07-13 snapshot. Assessment: epistemics and knowledge organs are
ENGINE-real; the language ladder works but is SCRIPT-held; the reach
audit's one-sentence finding ("he owns everything he has learned and
owns none of the ways he learned it") is the correct diagnosis and the
interpreter segment is aimed at the right layer. Pushes registered:
- **The case-class question (G in the repair order):** wrapping organs
  as nodes is cheap; defining what an ORGAN'S failure receipt scopes to
  (the case class piecewise supersession keys on) was undesigned.
  [RESOLVED THIS SESSION — §6: the failure-commonality miner IS the
  case-class minter.]
- Ladder constants (ADOPT_MIN=3, WINDOW=8, DECO_MIN=3) violate
  tests-over-thresholds and sit inside the poisoning cures — measure
  them before promotion.
- Category C fragility: the cures live in one experiment file; the
  account still saves via pickle though the pack road is proven.
  Recommendation: move the account onto packs BEFORE the segment.
- Gate 6 preconditions: "always co-present" is not "excess past a
  null" — a constant distractor enters requirements; will bite outside
  the toy world.
- The 31/31 vs 48/49 hash-seed discrepancy must reconcile before any
  duel verdicts mean anything.
- Defended §5F's line: judging may stay outside; deciding-how-to-learn
  moves inside. Hold it during the segment.

## §2 r² dethroned (owner decision)

Owner: r² "fails more times than is acceptable" — useless on non-math,
troublesome on math. Confirmed by the record: the additive hole is
r²'s crime scene (wrong form stamped UNDERSTOOD at ~0.96 on exact
additive data), and R²>=0.9 was the last big unconverted threshold in a
system whose law 2 is tests-over-thresholds.
**Decision: exactness-first ("make it perfect").** Search the structure
until the right result; constants land on ruler marks (3x, never
3.000154x when the data can't tell them apart); r² demoted to a
reported descriptive number, wrong-kept as a verdict with the additive
hole as exhibit. Known cost: DECAY_MEASURED / confidence-curve
calibration is defined against r²-graded outcomes — the curve
re-measures when the verdict changes (bigger change than any enumerator
tweak that triggered re-measurement before).

## §3 Precision is instrument-relative (owner refinement)

"You don't measure a mile with a micrometer; you measure a house in
16ths" — exact means exact WITHIN THE INSTRUMENT. (Owner pre-empted the
LIGO objection correctly: LIGO measures relatives, not distances — and
that is §13 of the theory doc: comparison is registration; differences
beat absolutes; a law about a difference/ratio can be certified finer
than either input's absolute floor because common-mode error lands in
the shared bucket.)
Consequences: two regimes (exact-checkable worlds = machine-zero
residual, checked outright, no statistics; noisy continuous worlds =
residual indistinguishable from the evidenced floor). Constants stated
to floor-supported digits — significant figures as a law of the report.
3 vs 3.000154 becomes arithmetic: difference x range leverage vs floor.

## §4 The surprise element (owner: "it had a surprise element before —
why aren't we using that?")

Honest answer: Isaac uses surprise everywhere ON THE WAY IN (every
admission null = "more surprising than the best coincidence") and
nowhere ON THE WAY OUT — the verdict tier asked r² instead of asking
whether the RESIDUAL still carries surprise.
**The verdict, restated in the native currency: a law is UNDERSTOOD
when the law is surprising and the residual is not.** Surprise in
(existing nulls) + no surprise out (residual replayed through the full
proposal machinery admits nothing) + constants on the coarsest marks
surviving the refit within the floor. Catches the additive hole
(the wrong form's residual is the missing structure, screaming) and
unifies with the clock's statuses and the coming organ failure receipts
(a receipt IS a surprise landing on a method — the snake lesson: no
prediction → no surprise → no learning signal).
Carried distinction (owner's own earlier correction): surprise vs
change-relative-to-baseline matters at the MOTIVATION layer (reward),
not the verdict — different organ, same instrument, different
calibration.

## §5 The surprise-verdict probe (built and run this session, 3 versions)

`surprise_verdict_probe.py` — old verdict (greedy halt + r²>=0.9) vs new
verdict, side by side, planted worlds. FINAL NUMBERS (v3):
- W1 additive hole: OLD blessed 0.32*x0*x1 at r² 0.9747; NEW found
  **x0 + x1** (product pruned at held-out tie, both coefs snapped).
- W2 3x @ 1/16 grain: NEW says **3*x**, UNDERSTOOD.
- W3a 3.000154 fine ruler: digits STAND. W3b coarse ruler: says 3 —
  correctly (the ruler cannot say otherwise).
- W4 lagged sleeper (y=2*x0+0.6*x1[t-4]): OLD blessed the flat model at
  r² 0.9367; replay screamed (obs 0.99 vs null 0.23); NEW landed
  **2*x0 + 0.6*x1[t-4]**.
- W5 interpolation trap: refused (surprise left).
- W6 pure noise x20: 0/20 false UNDERSTOOD both verdicts (no
  regression on the oldest number).
- W7 FALSE-ALARM CONTROL x20 (true model, replay must stay quiet):
  1/20 fires — nominal. The control that must be green before anything
  else counts.
- W1t/W4t resolution TOLD — UNDERSTOOD unlocked; W8 repeats road:
  floor MEASURED 0.1243 vs true 0.12, law 1.5*x^2.

WRONG-KEPT (probe lessons, hard requirements for the engine port):
1. **Marginal-correlation replay MISSED the additive hole** (0.211 vs
   thr 0.259) — an admitted collinear term hides leftover structure.
   Cure: PARTIAL correlation (residualize candidates against admitted
   terms) / joint refit — the duel, done cheap.
2. Mark ladder must be GRIDS of {1,1/2,1/4}x10^k coarsest-first (3 was
   not a "mark" as points; it is on the integer grid).
3. The snap referee must HOLD earned marks fixed during subsequent
   refits (a later term's refit was re-freeing an earlier snapped 1
   into 1.00124).
4. Grain-only floors UNDER-EVIDENCE when process noise exceeds
   quantization — honest PARTIAL results; the cure is the told/repeats
   roads, never a looser gate. NN noise estimators rejected for v1
   (gradient contamination inflates them — r²'s ghost via the side
   door).
5. Selection correction on the replay is mandatory (the 119/120
   dialogue lesson replays here — the replay tries everything).
KEY BEHAVIOR: continuous data with no repeats, nothing told, no grain —
exactness UNCLAIMABLE; verdict = BEST-RESIDUAL in units and the report
ASKS for the instrument's resolution (logical_gaps posture). No ruler,
no perfect.

## §6 Display — taught reduction (owner correction chain)

Owner: unit coefficients render bare ("1x becomes x"; single input =
plain x, indices only when >1 variable). Implemented in the probe as
`fmt_eq` — then the owner superseded the approach itself: **reduction/
simplification should be TAUGHT, not programmed** (the learned-speech
law applied to math rendering). `fmt_eq` wrong-kept as scaffold: right
output, wrong road.
`taught_reduction_probe.py` — reduction learned from example pairs:
templates by anti-unification across lessons; three gates before
minting: RECURRENCE >=2 independent pairs, VALUE GATE (exact agreement
on random assignments — polynomial identity testing; the null in
mathematics' own currency), STRICT DESCENT (RHS smaller — termination
by construction). RESULTS: 6 rules minted from 12 lessons (1*a→a,
a*1→a, a+0→a, a^1→a, a-a→0, 0*a→0); 8 candidates wrong-kept (4 invent
a slot, 4 value-gate incl. the template "?0 → a"); scrambled pairings
minted 0; poisoned lesson (x+1→x) REFUSED at the value gate — reduction
cannot be poisoned; unseen expressions 4/5 with the MISS being the
philosophy in one line: (0*q + 1*w) → (0 + w) and STOPPED because 0+a
was never taught (only a+0) — cured by TWO MORE LESSONS, not code —
5/5. Named next rungs: commutativity is CANONICALIZATION not reduction
(no descent; needs a learned ordering; the descent gate correctly
refuses it — protecting termination); constant folding routes through
the compute road; **taught rounding is this same organ aimed at
constants** (value gate = "within the ruler"); reduction = Occam turned
from a judge's preference into an operator he wields.

## §7 Should vs can vs cannot (owner question → probe)

Three tiers in existing vocabulary: **CANNOT** = gates (lockouts,
certified nevers, value gate) — never violable. **CAN** = passes the
gates — technically allowed, keeps its discovered guards. **SHOULD** =
learned preference AMONG the cans — rate-measured (decoration-by-rate
is the precedent), context/want-indexed, supersedable, NEVER promoted
to a gate; deviation carries a receipt (he knew the convention and
chose otherwise). Engine precedent: Occam already "a preference, not a
gate," alternatives retained.
**THE ROUTER (the session's cleanest find): the value gate classifies
corrections automatically.** Values equal → the tutor taught CONVENTION
(norm lane). Values differ → TRUTH CLAIM (faces the gates; a lying
tutor is refused). One instrument, two lanes, no human labeling.
`should_vs_can_probe.py` RESULTS: 1*a→a adopted (3 sightings), a+0→a
(2), a/a→1 adopted **WITH ITS GUARD DISCOVERED BY PROBING: a != 0**
("technically allowed" has edges, found not programmed); lying tutor
(a+1→a) routed to truth lane and refused; one-off style quirk held
below the adoption floor; and the context test: the SAME identity
carries OPPOSITE shoulds in different wants — expand (a+b)^2 for
integrate, factor it for root-find — no conflict, because a should is
indexed by the goal it serves. CAN is context-free; SHOULD never is.
WRONG-KEPT (probe bug, instructive): an eagerly-evaluated dict computed
the '/' branch on every call, so a+0 threw division-by-zero and the
exception was READ AS "values differ" — an implementation artifact
masquerading as an epistemic verdict. Engine-port requirement: value-
gate refusals must record WHY (which assignment, which side threw) so
harness bugs cannot impersonate truth judgments.

## §8 Language application + failure commonality (owner questions)

Language: the ladder's correction factoring already IS the router —
"did the correction change content or form?" The language value gate is
HIS OWN READING (same idea-whole/roles = style lesson; different
reading = content lesson). Decoration-by-rate = norm strength; the flip
test = norm supersession; register = context-indexing. NEW third tier:
**unacceptable language = lockout territory** (told nevers, usable at
once, never learned away by frequency, owner-retractable) — style
guides become teachable content: preferred style / acceptable
alternatives / denied constructions.
Failure commonality (owner: "assess failures and find commonalities...
specifically denied"): partial precedent exists (negatives crystallize
— penguin/ostrich share not_fly; confusion-pair compound mining), but
the general organ is new, and its definition matters: **commonality of
the denied is a DIFFERENTIAL against the allowed** — compare()'s
only-in-failures, gated by a selection-corrected label-shuffle null.
Never a frequency.
`failure_commonality_probe.py` RESULTS: planted frontier named exactly
(tense=perfect excess 0.496, voice=passive 0.431 vs null 0.159; junk
never named) — the frontier pile SELF-ASSEMBLING from receipts; owner
lockout world named word=slang alone (0.897 vs 0.140); random failures
— honest nothing (0.078 vs 0.176); CONTROL B: a feature on 100% of
failures (lang=english, also on 100% of successes) correctly NOT named.
TWO UNLOCKS: (1) this organ IS the case-class minter Trace C's
piecewise supersession needs — organ failure receipts → named failure
class → duel scope; §1's open question, closed. (2) a named failure
signature is a GAP WITH EVIDENCE — self-generated curriculum request
(serve passive-voice corrections next) — the residual arrow feeding the
DIRECTION of learning, not just its content. Requirement: fat failure
receipts (context recorded at failure time — can't mine what wasn't
kept).

## §9 Benchmarks — the data-ops lane (owner repositioning)

Owner asked for market/data analytics benchmarks; blocker stated
honestly: the engine is not in this chat session (uploads don't
persist across conversations) — hence everything above is reference-toy
grade. Proposed 3-tier suite (symbolic recovery / time series with
returns-as-noise-battery / tabular vs GBM baselines with the artifact
difference reported), with predictions filed before running.
Then the owner's sharper positioning: **"data refinement and updating,
data entry, organization, trend graphing and system modelling — Isaac
would be really good at that."** Assessment: correct — every one is a
TRUST problem before an accuracy problem, and the lane mostly ASSEMBLES
from existing organs (intake, triangulate, crystallizer, validate_law,
which_law, period/lag roads, confidence curve, report/speech,
provenance). Honest weak spot: data ENTRY itself is I/O; Isaac is the
validation gate behind the clerk, not the clerk. Product shape:
`askisaac --audit` (flags with receipts: ERROR-CANDIDATE vs
NEWS-CANDIDATE decided by recurrence via the §8 miner, DUPLICATE,
OUT-OF-DOMAIN, UNVALIDATABLE; trend cards with refusals; the remainder
dossier). Full spec delivered as **DATA_OPS_SEGMENT_PLAN.md** (audit
face + battery A1-A8, the instrument-floor organ §2 with three roads,
the verdict-rewrite dependency §2b with the five hard requirements from
§5's wrong-kepts, benchmark harness B1-B4 with INTEGRITY law restated,
work order, named risks incl. the lane's r²-ghost: never "just
estimate" an unevidenced floor — the ASK is the answer).

## §10 Standing owner decisions recorded this session
1. r² is dethroned as verdict; exactness-first, instrument-relative.
2. Verdict currency = surprise: law surprising in, residual
   unsurprising out.
3. Rendering conventions (1x→x etc.) are to be TAUGHT as reduction,
   not programmed — the fmt_eq scaffold is deprecated-by-design.
4. Should/can/cannot as three learnable tiers, for math AND language;
   unacceptable language = owner-specified lockouts.
5. Failure self-assessment = the differential commonality miner.
6. Product lane = data ops; plan doc is the handoff.

## §11 Open items / owner calls
- Upload isaac.py to a session (or point the harness at the repo) for
  any real benchmark run — nothing in this session touched the engine.
- Reconcile 31/31 vs 48/49 (PYTHONHASHSEED) before duel verdicts.
- Account → packs migration (owed; before the audit writes into a
  living mind). [DONE 2026-07-15 — account_pack_migration.py, 346
  records 0-diff, runner switched, pickle frozen+kept.]
- Ladder constants: measure, don't inherit, at promotion.
- Commutativity/canonicalization ordering: named, not solved.
- Confidence-curve re-measurement is gated to the verdict rewrite.
- Work order in the plan doc §5 is proposed, not decided.
