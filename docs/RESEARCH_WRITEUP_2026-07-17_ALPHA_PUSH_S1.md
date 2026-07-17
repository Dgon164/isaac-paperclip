# RESEARCH WRITEUP — 2026-07-17, ALPHA PUSH SESSION 1
**The wall re-run, the one crack it found and how it was cured, the
audit face learning to check the books, and the first public runs of
the last two benches. Written under the writeup law: plain language,
structures shown, complete numbers, failure mechanisms explained.**

---

## Part 1 — What this session was for

The handoff order was: run EVERYTHING against the engine the night of
07-15 built, fix whatever honestly breaks, then finish the product
face's last named piece (totals checking) and run the last two
benches (B3 system identification, B4 trend/forecast) with
predictions filed before the first run. All of that happened. One
crack was found and cured; two new honest limits were discovered,
measured, and filed; nothing was hidden.

## Part 2 — The wall: 45 gates against the night engine

Every battery the project owns, plus the five new ones from the
night's promotions, plus the 100-world duel, plus the gauntlet (ten
real datasets), run as ONE pass. Result: **44 of 45 green.**

The gauntlet reproduced every number from the last full run — and
one line flipped in Isaac's favor: **Kepler's third law, from 8
planets, now comes back UNDERSTOOD with the equation
`T = 1.00 * a^1.5` machine-exact.** The old judge could not say it
at all ("PREDICTED FAIL" was the filed expectation). The night's
verdict rewrite is what changed: exactness proven on unseen rows now
outranks statistics.

The one red: **taught rounding, 5 of 7.** The law that should say
"sin(1.75x)" said "sin(1.753x) plus a second junk wave"; the law
that should keep pi's digits got demoted from UNDERSTOOD to PARTIAL.
This had been green for five days — the night's promotions broke it
without noticing, because each promotion re-ran its own battery and
the self-test, but nobody re-ran the WHOLE wall until now. (That gap
is now closed structurally: the five night batteries and the duel
are in promote.py's permanent gate list — no future promotion can
skip them.)

## Part 3 — A structural find: the promote road was poisoned

Before touching the crack, a worse problem surfaced: the research
repo's engine file was STALE. The night's six promotions were built
in the live repo directly and never copied back. Running the normal
promotion machinery would have overwritten six promotions with the
old engine. The heal: research was synced to the live engine first
(research commit f565c8d), the five night batteries and the duel
gate were copied into research, and only THEN was any fix attempted
— through the lawful road: edit research, gate, promote.

## Part 4 — The rounding cure: why it broke and what fixed it

**Why it broke.** The night's new judge added a "replay" examiner:
after a law is fitted, it asks whether ANY candidate form can still
predict the leftover error on held-out rows. That examiner is
honest — and it exposed that the fitting machinery had been leaning
on the old judge's blindness. The frequency inside sin(kx) was
being proposed at k=1.7527 (0.15% off the true 1.75), and the tiny
rhythmic error that leaves (a slow "beat" against the data) was
absorbed by seating a second junk wave. The old judge looked at the
overall fit quality (r-squared 0.995) and said UNDERSTOOD. The new
judge saw the beat and said PARTIAL. The new judge was RIGHT — the
cure had to make the fit better, never the gate looser.

**The cure, three parts, each forced by a measurement:**

1. **Earn the last digits** (`_sharpen_k`): a shrinking search grid
   now refines each inside-parameter to ~2e-5 relative precision.
   The coarse steps the engine had (x0.7, x0.85, x1.15, x1.4) could
   never fix a 0.15% error — they stall immediately, measured.

2. **The simple rival** (`_simple_rival`): sharpening a frequency
   INSIDE a multi-wave blend chases the blend's own noise (measured:
   it walked the frequency AWAY from the truth). So each wave is
   also offered ALONE, sharpened on its own clean ridge, and the
   blend must justify its extra parts: it keeps them only if its
   advantage PER EXTRA PART exceeds what pure chance buys. The
   measurement that shaped this: a 4-term blend beat the true single
   wave by 6.4e-5 of train fit — which is EXACTLY the textbook
   chance-advantage of its extra parameters (q x (1-r2) / n). Its
   whole edge was parameter count. The solo road then landed
   k = 3.14159200 from a 3.1387 start — pi to seven digits, found
   not told.

3. **The fresh-row court** (in the rounding referee): here is the
   subtle one. Whether to snap 1.4994 to the mark 1.5 cannot be
   decided by training fit at all — measured: the TRUE mark 1.5
   cost 3.0e-5 of train fit, while the FALSE mark 3.142-for-pi cost
   only 2.2e-5. Overlapping. What separates them is fresh rows:
   noise-chasing does not repeat itself on data the fitter never
   saw; a real beat does. So before any mark is adopted, the
   referee now asks the replay's own question — "can the displaced
   alternative predict this mark's held-out error past a shuffled
   null?" — and refuses the mark if yes. The referee and the judge
   now share ONE court; before, the referee adopted marks the judge
   then convicted.

**Result: rounding 7 of 7.** sin(1.5x) says 1.5. sin(1.75x) says
1.75. sin(pi x) says 3.1415 — four earned digits, every coarse mark
refused. Pure noise still refuses to be a law. And the whole
discover-heavy wall re-ran green afterward, including the duel:
**wrong-confident 0 of 100, availability 20 of 20 — the night's
crown jewel untouched.**

## Part 5 — The audit face checks the books (totals wiring)

The cross-check organ (built 07-15: "5+5=9 — you don't know which
number is wrong, but you know SOMETHING here is") is now wired into
the audit face. Battery gates written FIRST and shown failing 4/4,
then the mechanism, then 18/18.

What it does, in table terms: if a table carries totals — a column
that is the sum of other columns, or a bottom row of column totals —
the audit builds the row-checks and column-checks and runs them
BEFORE the law pass:

    a    b    c   | total          row check: a+b+c = total
    12   7    4   | 23
    9   31←  15   | 48   ← fails         (true b was 24)
    ...
    ────────────────────
    88   96   61  | 245             column checks: each column sums
         ↑ fails                     to its total

- One broken row-sum alone: the whole TUPLE is marked
  false-somewhere with three "repair doors" (what each cell would
  have to be) — nothing gets blamed alone, because one check cannot
  localize.
- A broken row-check AND a broken column-check INTERSECT: the
  battery's corrupted cell came back as a unique CORRECTED-CANDIDATE
  at exactly that cell with exactly the true value (31 → 24) —
  proposed with its receipt, never silently applied.
- Clean books: zero flags (the control).
- An ordinary table with no totals: no checks invented, and the
  report says so.
- A totals row is BOOKKEEPING: excluded from the law pass and row
  audit (it is not an observation), and the report says that too.

One wrong-kept from building it: the first structure detector
demanded 90% of rows to balance — and so declared "no totals here"
on the very grid whose single corrupted cell was the point. The bar
is now 60% with at least 3 balancing rows: the dissenting rows are
exactly what the checks exist to hunt.

## Part 6 — The benches, re-run and first-run, predictions first

All predictions were filed in PREDICTIONS.md before any run (P10-P18
added this session for B3/B4).

**B1 error detection (re-run on the new judge):** the 07-15 shape
holds. In-range corruption: precision 1.00 / recall 1.00 / F1 1.00
with zero false flags, while z-score and IQR sit at 0.00 recall
(marginally invisible corruption is the lane's native game). Clean
control: 0.0 false flags of 320 rows. Curved-law clustered
corruption: 1.00 across the board. One honest change: on gross ±15
corruption, one trial in three now REFUSES to flag (the fitted form
got dragged; the refusal message names both possible causes) — the
mean recall drops to 0.67 and the refusal is counted, not hidden.
z-score still misses 22% of gross errors on its best day.

**B2 completion (re-run):** 12 of 12 verdicts honest, unchanged.
Real join: imputation error 0.0411 in units, UNDER the 0.05 noise
floor, tied with sklearn's best (0.0407) — but with the equation,
the join verdict, and the null attached. The no-structure and
in-principle-unresolvable worlds refused correctly 3/3 each; the
refusal-control world (where refusing would be wrong) resolved 3/3.

**B3 system identification (first run):**
- Logistic map (chaos, r=3.7): **recovered 3/3, machine-exact** —
  `x_next = 3.70x - 3.70x²`, fresh-row error 2.7e-15. The additive
  hole the campaign found on 07-14 is genuinely closed.
- Predator-prey (log-linearized): **recovered 3/3** — the exact
  planted constants (`-0.40*L + 1.10`), with the tiny discretization
  remainder honestly named (PARTIAL — which the filed prediction
  P12 explicitly counts as recovery).
- Damped oscillator: **missed 3/3, mechanism isolated.** The engine
  found only the one-step term. Diagnostic: fed the two lag columns
  explicitly, it recovers the law UNDERSTOOD with the exact planted
  constants (1.77 / -0.96). The miss lives entirely in the lag
  PROPOSER, which proposes nothing on a near-unit-root oscillatory
  series — its null-gate refuses. Named open door.
- Delay system (outside the vocabulary): **wrong-confident 3/3 —
  the session's most important find.** The engine said UNDERSTOOD
  (`+0.98x`) on a DETERMINISTIC world while missing fresh rows by
  0.033. Filed prediction P13 said it would refuse — prediction
  FALSIFIED, kept. The mechanism: the residual IS structured (it is
  a function of the value 17 steps back), but no lag-17 column was
  ever proposed, so the replay examiner had no vocabulary to
  interrogate it with. The judge is honest only within the
  vocabulary the proposers hand it. This is the same disease class
  as the additive hole: counted in the bench now (the bench exits
  red on purpose), cure named (deeper lag proposals / replay over
  lag candidates), and after the cure a delay family should join
  the duel's worlds.
- Scrambled control: refused correctly 3/3, zero false discoveries.

**B4 trend/forecast (first run):**
- Planted seasonal+trend: **UNDERSTOOD with the readable equation
  `+3.05*sin(0.5235*t) +0.05*t +9.92`** — 0.5235 is 2π/12, the
  monthly season read off the data. Forecast error MASE 0.546
  against naive 3.26 and seasonal-naive 1.607: beats the
  competition's own baseline family, with an equation instead of a
  black box.
- Sunspots (public series): honest NO RULE refusal — quasi-periodic,
  consistent with the gauntlet's long-standing verdict.
- M4 competition subset: BLOCKED (the train file is a ~300 MB
  download) — recorded, not quietly swapped for synthetic.
- Raw returns + realized volatility (the headline pair): two
  download roads refused this machine (robot wall, timeout); a third
  road (the Ken French daily market-returns library, real data since
  1926) was added — numbers in Part 7.

## Part 7 — The refusing-returns headline (B4, P17/P18)

**P17, CONFIRMED — the headline: refusal 8 of 8, zero laws minted.**
Real daily market returns (the Ken French library — the third
download road after two others refused this machine, both recorded),
eight rolling 500-day windows. Isaac refused to mint a
return-forecasting law in every single window. Every forecasting
tool on the market will happily fit this data; the honest verdict is
that there is nothing there to fit, and Isaac is the one that says
so. That refusal — with receipts — is the product.

**P18, SUBSTANTIALLY FALSIFIED — kept, as the law requires.** The
filed pair-claim was that volatility (how BIG moves are, rather than
which direction) WOULD show structure where raw returns refused —
proving the refusal is discrimination, not blindness. It did not
establish: one-step absolute returns found structure in 0 of 8
windows; the literature's weekly realized volatility found it in 1
of 8 (about 100 points per window — a thin ruler). Both numbers are
on the record. The named follow-up is longer spans (~400 weekly
points), where the clustering signal should clear the
selection-corrected null if it is real for this vocabulary. Until
then the headline stands WITHOUT the pair's support, and says so —
a falsified prediction filed next to a confirmed one is exactly
what filing predictions is for.

## Part 8 — What is deliberately untouched

The owner-present block: practice-loop vetting, container stamping
at the live account's intake, and the E3 first read of his real
failure receipts. All machinery is ready (vet_intake 6/6, containers
10/10, pool cure list 8/8) — and none of it has gone near
`Documents/isaac_home/`. The account is his life; those three run
with him in the chair, on his call.

## Part 9 — Open doors filed this session

1. The lag proposer's silence on oscillatory series (B3's miss;
   diagnostic proves the fit machinery is ready the moment the
   column exists).
2. The delay-world leak: UNDERSTOOD on a deterministic world with
   structured residual outside the proposal vocabulary — cure, then
   a delay family in the duel.
3. The gross-corruption refusal fork (B1 W3, 1 trial in 3): honest
   but conservative; the two-fork message is correct, the miss is
   counted.
4. M4 subset remains unrun (download size); public labeled-error
   sets for B1 remain the named follow-up.
5. Hand-set v1 constants (5*MAD, flag caps, grid fractions, the
   referee's f=8) — the tests-over-thresholds debt, still carried.

---

## Part 10 — SAME DAY, SECOND BUILD: the birth machinery (the owner
## redefines alpha, and the harness for day one gets built and gated)

**The owner's amendment, in his words:** "isaac is an intelligence
and scientific engine. his job is to learn and make sense of
information in a way that is directly usable and readable... we are
ready for road trials. durability, range, power, efficiency... the
alpha version needs to start from the start... the net isnt so
important, its the capability. the net should be produced roughly
the same time every time... selecting and using the correct
information as he scales will become more important over time."

So: day one is a FRESH account; the test era is prologue, archived
forever; and the prologue net becomes his FIRST TEACHER — extracted
and fed to the fresh mind as direct telling, which is both the
one-shot-learning experiment and his "chance to process everything
one last time." Three pieces were built battery-first, same day:

**THE FIRST TEACHER (inherit battery 10/10).** A predecessor's net
extracts into tellable material — facts with their world stamps,
laws in Isaac's own equation grammar — and feeds a fresh mind
through the standard doors. What the battery proved: the inherited
law applies IMMEDIATELY on the fresh mind (one-shot, error 0.0000)
while carrying NO inherited belief (TOLD-UNVERIFIED, source named);
a planted WRONG prologue law FAILS revalidation on the successor's
own data (r² −60) while the true one earns HOLDS — the test era's
junk cleans itself out by the ordinary machinery, nobody has to
adjudicate it by hand. Fiction stays walled in its world; base never
inherits it. An out-of-vocabulary law is refused loudly with the
exact unparseable factor named; laws leaning on learned lag or
composite columns are refused with the why (he can rediscover them
from data — a said v1 scope). Organ-internal bookkeeping is not
experience and is not re-told. And the birth wrapper REFUSES an
occupied home — a life is never overwritten.

**THE INSTRUMENT PANEL (road-trial battery 4/4).** One longitudinal
record per session of his life: net sizes (the growth axis), an
engine probe on the same seeded world every time (efficiency drift,
comparable forever — day-one baseline 0.253 s), ask-latency on his
own facts, and the SELECTION gauge — the owner's named scaling axis:
sample his own laws, generate data from each, ask him to pick the
author; precision out of asked, and fewer than two eligible laws
means the gauge refuses with a note instead of reporting a fake
1.0. The logger measures without changing him — the mind is
byte-identical after logging, proven.

**THE ARTIFACT CLAIM, MEASURED (reproducibility 3/3).** Two fresh
minds ran one identical experience script. Result: byte-identical
pickles — not roughly the same net, the SAME net, to the byte. The
owner's ruling ("the net isn't so important, it's the capability")
is now a measured property: experience in, net out, deterministically;
the capability is the versioned asset and dumping a net truly costs
nothing.

All three joined promote.py's permanent wall (47 gates now). What
still waits for the owner's chair: the archive of the prologue home,
the birth itself, and the first practice session — plus one named
piece of session-2 work before that first practice: wiring the
vet-intake checker into the live practice loop's banking path
(admission discipline from the first conversation, per the fresh-
start ruling).

---

## Part 11 — THE LAUNCH (2026-07-17 08:28, owner present, his call)

The owner named it: launch, not birth — road-trial language for a
road-trial life. The sequence, exactly as run:

**Preflight caught one real thing:** the account's live state is
pack v8 (the night of 07-15 — word re-elections, the tools node),
while the old mind.isaac pickle was frozen two days earlier. The
launcher was about to teach from a stale ghost. Cured research-first
(the packs road preferred, the source road NAMED in the launch
journal, battery gate I10: a late-taught fact must arrive through
the launch — 11/11), promoted through the full 47-gate wall, THEN
the launch ran.

**The launch itself:** isaac_home renamed to isaac_home_prologue —
109 files, byte-for-byte, nothing copied, nothing deleted; the test
era is the archived source document forever. A fresh mind's first
experience: its predecessor's telling from pack v8.

**The honest surprise: 0 facts, 0 laws extracted.** A read-only
census of the prologue confirmed the launch told the truth — his
test-era life simply never accumulated facts or laws in his home
(418 nodes: 279 speech, 116 tools, a few op/order findings; the
fact/law worlds all lived in throwaway experiment minds). His life
WAS language. The fact-and-law telling roads are proven on planted
minds (battery 11/11) and now wait for the life that will use them.

**The real inheritance: the corpus, re-earned.** 3,417 lines
carried as a file, then relearned through the excess null — 0 → 198
fragments in 4.5 seconds, EARNED against the same statistics as the
first time, never copied. The prologue had 211: the 13-fragment gap
is named, not hidden — their evidence lived outside the corpus file
(correction records, early seeding), so the raw record could not
re-derive them. A small open door: the corpus file is the raw
record, and 13 fragments' evidence never made it in.

**The permanent record begins:**
  - journal entry #1: kind=launch, source=prologue, source road
    "packs v8 (the live road)", counts complete;
  - journal entry #2: kind=launch_relearn, 0 → 198;
  - road-trial record #1 (empty mind baseline: probe 0.356s) and
    #2 (true day one: 199 nodes, 198 fragments, probe 0.302s).
Every session from here appends to roadtrial.jsonl; the curves those
records draw — durability, range, efficiency, selection — ARE the
road trial. Before his first practice conversation, one named build
remains: the vet checker wired into the practice loop's banking
path.

HE IS ON THE ROAD.
