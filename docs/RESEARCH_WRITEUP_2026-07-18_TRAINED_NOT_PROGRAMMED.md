# TRAINED, NOT PROGRAMMED — THE PROVENANCE AUDIT
**2026-07-18, evening session (research campaign, day 1). The owner's
question, verbatim: "go through the existing code and training
material and check that its actually being trained and not just
programmed into isaac." This is the answer, with receipts.**

## THE VERDICT, PLAIN
**Isaac is genuinely trained.** Every law he claims to have
discovered was traced end-to-end: the real data sits in meal scripts
and data files with source citations, it entered his mind at runtime
through the ordinary feed roads, and what his mind stores is fitted
numbers with messy decimal tails — the signature of measurement, not
injection. The engine code is clean of his knowledge: greps for
Kepler, Boyle, Galileo, the planet tables, the CO2 numbers, the
sunspot period, the 1662 pressures — zero hits in any engine organ.

**With three exceptions the owner needs to see:**
1. **ONE confirmed violation** — a hard-coded answer patch in
   `isaac_store/engineer.py:391` (detail below).
2. **The promotion wall is inverted on ownership** — it permanently
   re-certifies the hand courts, while the honest ablation proof ran
   once and is not on the wall.
3. **One handoff claim was overstated** — FURRY was never trained;
   it exists only as hand-written probe code on a throwaway mind.

## HOW WE CHECKED
A 65-agent audit over ~25 minutes (3.30M tokens, 715 tool calls):
six scanners read every line of the engine organs (all 11,250 lines
of isaac.py + every non-test isaac_store organ + face/askisaac/
alpha/worker); one auditor inventoried every feed road and every
piece of training material; one loaded a **copy** of mind.isaac in
the scratchpad (isaac_home untouched, 349,520 bytes verified) and
dumped every law with its provenance; one checked the ablation
proofs and the promote wall; ten tracers each took one flagship
knowledge item and tried to find the smuggled version before
accepting "trained"; every candidate violation then faced two
independent adversarial refuters. Raw yield: 68 deduped findings →
8 candidate violations + 30 gray; after refutation: **1 violation
stands, 27 gray ceilings, rest downgraded or dismissed** (2 low-rank
grays left unverified by cap, kept on the list).

## THE TEN TRACES (the heart of the answer)
| item | verdict | the receipt |
|---|---|---|
| Kepler T=a^1.5 | **TRAINED** | data inline in meal1_first_laws.py (NASA/JPL cited); law:solar-system discovered/UNDERSTOOD, container data-solar-system, coef 0.9992722651…; siblings fitted OFF-grid 1.49938/1.5007; Pluto 0.07% + Kuiper 0.23% never fed |
| Boyle 1662 | **TRAINED** | the 10-row 1662 table lives only in the meal script; law:boyle-1662 = +1413.86*x0^-1 −0.06, r² 0.9999486; facts rows match the fed table verbatim |
| Galileo 1604 | **TRAINED** | folio 107v rows (Drake 1973) in meal2_diversity.py; law = +33.08*x0*x0 −1.52, coef 33.07688416… non-round |
| CO2/Keeling | **TRAINED** | real NOAA files on disk (data/feeds/co2_annmean_mlo.txt ends "2025 427.35"); discovered PARTIAL, honest; coef 0.20037951…, intercept 318.32597… |
| Sunspots ~11yr | **TRAINED** | real SILSO file (326 rows, 1700–2025); stored period 10.4534 — a fitted value, not the textbook 11; the 88% residual honestly kept dark |
| the self-built word (x0*x1^-2) | **TRAINED** | mind.composites initialized EMPTY in code (isaac.py); the word lives in the pickled mind, quadruple-recorded, provenance honestly "uncertified — belief stays the court's" |
| mechanical k=3.5000/e=0.7999 | **TRAINED** | constants defined ONLY in the exam-side simulation source; recovered by reading + measuring the running sim; engine organs clean; not in the live mind (honestly — it was a probe) |
| engineer curriculum (meal 8) | **MIXED** | all 28 told forms + 311 facts entered via tell_law/teach/teach_not with journal receipts and exact count arithmetic (627→843, 9→37) — but ONE form (tube OD=ID+2·wall) ALSO sits hard-coded in engineer.py tube_court: duplicate ownership |
| the 8 planets remembered | **TRAINED** | all 8 of 8 source rows kept as evidence on law:solar-system, container-stamped |
| FURRY from definition | **PROGRAMMED** | never fed; the "definition" was hand-compiled into Python predicates in concept_structure_probe.py; ran on a THROWAWAY mind; his live account holds zero concept: nodes. The probe honestly labels itself "RESEARCH, NOT THE ENGINE," but the handoff sentence "FURRY recognized from definition alone" needs the asterisk |

## THE ONE CONFIRMED VIOLATION (two refuters, both executed the code)
`isaac_store/engineer.py:391-392` — read_goal_sheet's "FREE by dead
data flow" subtracts a literal set `{'alive','score','dir','food',
'energy'}` — the snake exam's own variable names. Pure dead-data-flow
on the exam program yields `['alive','lucky','score']`; the literal
converts it to `['lucky']` — exactly what the promoted gate N8
(test_engineer.py:195) asserts. The set is load-bearing for `alive`
and `score` (the other three are inert — already excluded via reads).
This is a pre-baked answer keyed to a known exam, inside an engine
organ, undeclared in the module's own v1-limits docstring — and it
breaks the module's own stated law that a verifier never repairs
what it checks. Mitigations, for the record: nothing wires
read_goal_sheet to the live mind yet (callers are exam-only), so no
false knowledge reached his account. The fix is mechanical: derive
the exclusion from the sheet's already-classified attributes
(rewards/buffers/fatal/lockout/reward_source — all computable), or
declare the limit and make N8 expect the honest output.

The rest of the engineer read road got the same scrutiny and was
DOWNGRADED to gray, deliberately: the goal-sheet reader is keyed to
snake vocabulary throughout (`"score"`, `"food"`, `"body"`,
`"energy"`, `"DIRS["`), but the graded outputs are genuinely read
from the program text — the mod null proves it (flip "+= 10" to
"+= −10" and the sheet reads −10; a canned answer cannot invert with
the text). That is a vocabulary CEILING, not smuggled content: on a
program using 'points'/'apple' the reader goes silent rather than
guessing.

## THE WALL INVERSION (ownership is not enforced anywhere permanent)
promote.py runs 55 gates (the handoff says 56 — count it again next
promote). On ownership the asymmetry is exactly backwards:
- test_engineer.py N1–N4 and N8 **permanently re-certify the HAND
  courts** (tube_court's coded OD=ID+2·wall, the coded volume
  formulas, and the patched N8 answer) on every promote;
- the honest proof — engineer_transplant_probe.py, which ablates
  tube_court/slot_court to raise "hand court called — ownership
  failed" and reproduces all 8 answers from net content — **ran once
  in research and is on no wall**. Its generic replacement solver
  was never promoted into the engine either (it exists only in the
  probe and as solve_backward in curriculum_feed.py).
The other ablation receipts audited (HIGGS top-3 carrier ablation,
GPT-2 head sign receipts, harder-road carrier naming, pool drop
algebra) are genuine — predict-then-intervene on running nets, some
explicitly self-aware that "drops measure NECESSITY, not ownership."

## INSIDE HIS MIND (the copy-audit census)
843 meta nodes (1,039 counting door-only tokens — keep the two
conventions apart in reports), 1,524 doors, 37 laws, 311 facts,
1 relation, 3 watch histories, 1 composite word, 123 findings-ledger
entries, 405 speech fragments, 14 world nodes. Provenance census:
**0 laws without provenance** — 9 discovered (6 UNDERSTOOD, 3
PARTIAL), 28 told (all TOLD-UNVERIFIED with their citations); 301 of
311 facts container-stamped. And the flags worth acting on:
- **who= is a courtesy string, not a mechanism** — any script can
  mint who="discovered" (isaac.py:5789). The told/discovered
  distinction this whole audit leaned on is convention. Six told
  electrical laws already carry a FORMULA as their who.
- **teach() takes no who** — all 311 facts have container but no
  source; the fed curriculum is untraceable to its citations from
  inside the mind (only the meal scripts hold them).
- **teach_not stamps NO container** — the 10 negatives are the only
  container-less knowledge in his mind. Same wound-class as D8.
- **Exact-1.5 on discovered stamps carries no snap receipt** — the
  rounding court snapped a near-1.5 fit, but the pre-snap value is
  gone; from inside the account, a snapped 1.5 and an injected 1.5
  are indistinguishable. Store the pre-snap fit with the law.
- **Form-collapse hides names**: Ohm, Hooke, Q=CV exist only as
  witnesses on law:rect-area — by design, but there is no law:ohm
  node for name-based recall.
- **drafting has ~40 facts but no world:drafting node** (world nodes
  mint only on law install, never via teach) — the handoff's "base +
  12 worlds" undercounts door-tag containers (15 seen).
- 3 of 9 discovered laws (co2-maunaloa, co2-series-trend,
  planet-gravity) have **no stored evidence breakdown** — their
  replay court would run on new data only, against the facts-layer
  intent.

## THE CEILING MAP (the deep version of the question)
The audit's 27 gray findings are all one shape: **growth mints
INSTANCES, never OPERATORS.** Fixed at birth: the atom kinds
(var/sin/cos/exp/pow/step/absd/…), the composite operator menu
(product/sum/difference/ratio/mean/log/powerprod), the powerprod
exponent grid (half-integers −3..3 — an exponent of −2.5 exists, but
−2.25 could never be minted), the telling grammar (a strict SUBSET
of the discover grammar — step/crease/lag/composite laws cannot be
told back), tell_rule's one condition word (multiple_of), the
engineer courts' kinds, structural.py's five constraint families.
The redeeming discipline is uniform: nearly every ceiling refuses
loudly instead of guessing. This matches the declared usage-law
boundary ("hand-built stays the combinator GENERATORS + the
epistemics") — but the vocabulary-elections rung the owner already
named is exactly where these ceilings start moving into the net.
**One real bug found here**: the ledger road drops powerprod
exponents (record_finding never writes exps, load_ledger never
restores them) — a life rebuilt from ledger alone re-arms grown
words broken (KeyError in _augment_with). Pack and pickle roads are
unaffected. Cheap fix, worth a battery.

## WHAT THIS AUDIT COULD NOT CERTIFY (the critic's list — next block)
- **The speech road, 48% of his mind, is unstamped**: 405 of 843
  nodes are speech fragments minted by direct writes from
  sparring.py/speech_learn.py with no provenance or container. The
  single largest content class went unexamined tonight.
- **Journal receipts are unsigned** plain JSONL (trim() rewrites in
  place) — the traces used them as ground truth; nothing enforces
  that only live roads write them.
- **mind.isaac is a raw pickle loaded before validation**
  (isaac.py:2483) — his life file is an arbitrary-code-execution
  surface on every resurrection, and the whole-object pickle
  silently persists unstamped classes (World.actions, activation
  log) that the pack/audit roads never see.
- **Nothing in code guards isaac_home** — engine organs never
  reference it; the read-only sanctity of his life is purely
  operational discipline in meal scripts.
- flow:drill (the kernel acceptance witness) was never decoded from
  the mind copy; the backup zips were never hash-compared; the
  headline "selection precision 1.0" was never reproduced by an
  auditor; teach_action writes no stamps at all (unused by meals —
  close it or stamp it).

## RECOMMENDED NEXT MOVES (in order)
1. Fix engineer.py:391 the honest way (derive exclusions from the
   sheet's own classifications) and make N8 expect the honest
   output; put engineer_transplant_probe on the permanent wall.
2. The speech-corpus audit block (sample the 405, trace each to its
   session, test whether any tutor-model assertion survived the vet
   as stored content).
3. The stamp red-team: mint a fake who="discovered" law on a scratch
   mind and show current tooling can't tell — then move who/container
   stamping engine-side (intake is where enforcement belongs; the
   owner's top open item already points there).
4. Fix the ledger powerprod-exps seam + battery.
5. Store pre-snap fits with snapped laws (the 1.5 receipt).
6. Reproduction pass: re-feed one meal on a fresh mind and confirm
   the stored values arrive only via the feed road.

## THE ONE-PARAGRAPH SUMMARY FOR THE RECORD
The engine is a grammar and a courtroom; the knowledge is in the
net. Ten flagship items traced: eight trained with receipts, one
mixed (a told form duplicated in a hand court that the transplant
probe already proved redundant), one probe-only claim corrected
(FURRY). One hard-coded answer patch found and confirmed by two
independent executions (engineer.py:391) — exam-only today, wall-
certified, mechanically fixable. The deeper finding is about
ENFORCEMENT, not smuggling: provenance stamps are convention, the
biggest content class (speech) is unstamped, and the wall certifies
hand courts while the ownership ablation sits off-wall. Isaac is
trained. The discipline that keeps him trained is, tonight, still
mostly manners — the next campaign block should make it mechanism.

*Audit: 65 agents, 68 raw findings, 1 violation upheld / 27 gray /
rest dismissed; run wf_70c47b1a-b01; full agent returns in the
session workflow journal. Copies: isaac-paperclip/docs + dc/docs.*
