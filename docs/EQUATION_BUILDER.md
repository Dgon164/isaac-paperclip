# THE ENUMERATION ALGEBRA — Isaac's equation builder
**The write-up.** Code: `isaac.py` lines ~375–861 (`_atom_specs`,
`_atom_col`, `_atom_label`, `_disc_col`, `class _Enumerator`), extracted
verbatim and runnable alone at `standalone/equation_builder.py`
(numpy only — `python standalone/equation_builder.py` self-demonstrates).

## What it is
Given examples `(X, y)` of something Isaac cannot do, it BUILDS THE
EQUATION — an explicit, human-readable algebraic law — or refuses.
Linear regression can only weigh columns it is given; the builder's job
is to PROPOSE the right columns (nonlinear forms with parameters INSIDE
them), admit only the ones that beat a null designed to kill them, and
then sharpen what regression cannot reach. The output is never a model
object; it is a sentence of algebra: `+2.00*log(x0) +0.50*x1*x2`.

## The pipeline, stage by stage

### 1. The vocabulary of forms (`_atom_specs`)
Linear-in-COEFFICIENTS over a NONLINEAR library. Per feature:
- the raw variable;
- `sin/cos(k·x)` at a scale grid k ∈ {0.5, 1, 2, 3, 4.5, 6, 8};
- `exp(±k·x)` (decay AND growth), k ∈ {0.25, 0.5, 1.0};
- **the one power dial**: `x^k`, k ∈ {−2, −1, −0.5, **0**, 0.5, 1.5},
  where λ=0 IS log (the Box–Cox limit — "isn't a log just a power?").
Per feature pair: `cos/sin/cosh(k·(xi−xj))` — differences are how
invariant masses, phase couplings, and registration live.
Scales k sit INSIDE the nonlinearity where regression cannot reach:
**the grid proposes, refinement sharpens** (stage 6).
Plus the OPEN OP FAMILY: composites learned on past problems
(`comb:(x0*x1)`, ratios, means) are offered as columns to every future
discovery — the vocabulary grows with experience.

### 2. Phase-fold period proposal (`_propose_periods`)
Before atoms are built, y is FOLDED onto candidate periods of each input
(`t mod P` → phase bins; coherence = variance the phase map explains;
coarse geomspace scan + fine scan around the winner). A period is
proposed only past a selection-corrected null that replays the identical
two-stage scan on block-permuted y (99th pct, 100 draws). Proposed
frequencies join the sin/cos grid for that run and STILL face admission.
This is how off-grid frequencies are reachable from scattered samples —
folding needs coverage of the CYCLE, not of time.

### 3. Staged, null-gated admission (the heart, in `fit`)
Terms are products of up to 3 atoms. Each round:
- every candidate's correlation with the CURRENT RESIDUAL is computed;
- the null: the residual is permuted and the MAX correlation over ALL
  candidates recorded (selection-corrected — decoys that win by being
  many die here); gate = 95th percentile over 40 draws;
- **the block-permutation null (A1)**: each round the residual's
  decorrelation length L is MEASURED (lag-1 test at 1%, then the ACF's
  first in-band lag, capped so ≥20 blocks remain). White residual → iid
  shuffle; autocorrelated → circular moving-block permutation, which
  preserves the data's texture and destroys only candidate↔residual
  alignment. This killed the sunspot runaway (20 CPU-hours of junk
  admission under the old iid null; now: 0 terms, honest NO RULE).
- nothing beats the gate → admission STOPS. `max_terms=16` remains as a
  backstop only.

### 4. The trial shortlist (structural diversity + parsimony)
Raw residual correlation is myopic (a wide cosine out-correlates the
true parabola on a bounded range), so the top candidates are
TRIAL-ADMITTED, refit, refined, and judged by train R²:
- the shortlist guarantees structural diversity: top-8 by correlation +
  best-4 simple raw-variable candidates + best-3 scale-free candidates;
- parsimony is a PREFERENCE, not a gate (owner's law): newly introduced
  scale-atoms are charged a small complexity price; flexibility already
  paid for is free;
- completers (train R² ≥ 0.995) are judged by F-TEST: significance
  decides; genuine ties go to the simpler form.
The winner's term seeds the beam: the frontier grows around admitted
terms only.

### 5. Held-out honesty (in the `discover()` wrapper)
The rule must WORK, not merely fit: half the data is held out; verdicts
come from the held half. `UNDERSTOOD` (R² ≥ 0.9 held-out) / `PARTIAL` /
`CAPTURED` (exemplars catch what algebra cannot yet say) / `NO RULE`
(0/20 false discoveries on pure noise, re-verified). Every discover()
also returns THE ACCOUNTING — articulated% + captured% + noise% = 100 —
and a residual dossier when >5% is unexplained.

### 6. Refinement (`_refine`, `_refine_term`)
Regression finds coefficients; it cannot reach parameters inside a
nonlinearity. Each admitted term's k is hill-climbed by trial-refit
(×0.7, 0.85, 1.15, 1.4 steps): the grid's proposal sharpens to the
data's true frequency/decay/scale. (Known debt A8: refined k is not yet
bounded by grid reach — on a discrete channel it once climbed to
k=1929, a lookup table in trig costume. Filed.)

### 7. Rivals with probes (`rival_check`)
Identifiability made explicit: classic look-alikes (parabola vs wide
cosine, exponential vs cubic...) are swapped in per single-feature term,
refit, F-tested. Rivals the data cannot reject stay ALIVE on the law's
record, each with a PROBE — where to sample to split them. `confirm()`
on new evidence retires rivals, OVERTURNS the law (the loser is kept,
wearing its defeat), or REFUTES on fit collapse.

## What wraps it in the engine
`discover()` adds verdicts/accounting/dossiers/adequacy; `refine()`
steers budgeted experiments to the weakest region (confidence as a
steering signal, +25pts beyond-range); `apply_law`/`validate_law` make
laws reusable computation; capture→interrogate→graduate attacks what
the algebra cannot yet say; `law_confidence` grades every claim by the
MEASURED decay curve (ECE ~0.08); everything lands in the findings
ledger and survives sessions.

## The record (verified, complete numbers)
- Planted laws: exact (incl. `+2.00*log(x0) +0.50*x1*x2` cold — the
  standalone's own demo; off-grid damped oscillation; sin(3·x0·x1) via
  graduation; cos(3·mean(x0..x7)) via a learned collective).
- Kepler from 8 planets: `+1.00*x0^1.5` exact; Pluto predicted 248.0 vs
  247.9 across a session boundary.
- Real collider data: the transverse-mass formula
  `pT·MET·(1−cos Δφ(lep,MET))` found blind among 21 channels (R² 0.856).
- Refusals: 0/20 false discoveries on noise; the sunspot condition dies
  at 0 terms in 2 seconds.

## Known limits (all documented in the manual)
Wrong-form risk at n < ~400 (provisional label); frequency reach ≈ 2×
grid max for non-periodic scales (periodic scales reachable via the
fold); nested nonlinearities land in CAPTURED by design; rational
functions admit usable trig surrogates (range-valid); refinement scale
unbounded on discrete channels (A8, filed).
