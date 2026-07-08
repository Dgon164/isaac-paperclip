# The Crystallizer, as envisioned — active, incremental, holonic, amortizing
*Design intent, captured 2026-07-07 from the owner. This is the target the loop-to-stability
work (see ANALYSIS.md §6b, experiment E-LOOP) should build toward. Not yet implemented.*

The crystallizer was never a batch, single-use pass. It is **active pattern retrieval**: a
living process that refines concepts a little on every sense, bounded to only what it touched,
and amortizes — frequently-used concepts resolve and become cheap to pull up.

## 0. The guiding principle — it must eat its own dog food
Every mechanism below is one principle: **run the same operation on your own output, and
swallow what you cook.** Three consequences:
1. **Re-admission (output → input).** Concepts re-enter as tokens — the recursion ("same
   function, called twice"). The current code refuses this (the `type:` exclusion + no `seq`
   doors on types = the crystallizer declining to eat its own meal).
2. **Uniform representation (output format = input format).** A concept must be
   indistinguishable from an atom-token to the machinery, so the same operation applies with
   zero per-floor special-casing. `token = group` is what makes this free.
3. **Self-correcting quality pressure (the payoff).** A crystallizer that eats its output
   immediately *tastes its own impurity* — a bad concept becomes a bad token next pass and the
   compression invariant catches it. A single-pass crystallizer never tastes its output, so it
   never feels the rot: **this is why the tower collapses silently above L1.** Dog-fooding is
   what makes the compression invariant load-bearing instead of decorative.

## 1. Primitives (the owner's vocabulary)
- **Sense** — one input/observation (the "sentence"). An experience, not a string.
- **Token = a group.** Holonic all the way down; there are no bare atoms, only groups of
  groups. A token carries internal structure.
- **Concept = its applications across tokens.** Meaning is use. A concept is not a definition;
  it is the accumulated set of how it applies (its door/application profile).
- **Application-breakdown** — a resolved concept's generalized profile of how it applies; what
  gets "pulled up" instead of re-derived.

## 2. The loop (per sense — active, not batch)
1. **Active retrieval.** A sense arrives; pull up what is already held; create/update a
   structure for it.
2. **Mini direct passes.** Do small, focused passes on *each thing touched* — NOT a global
   re-crystallization.
3. **Build on the last refinement.** Each pass accumulates onto the prior state; never restart.
4. **Crystallize → refine → collect → compare → extract meaning.** The differentiation engine,
   run incrementally on the touched set.
5. **Runaway governor: only touched things get the extra reprocessing.** Bounded work per
   sense. There is no global fixpoint to spin out — the net is always in a good-enough
   quasi-stable state that each sense nudges forward.

## 3. Resolution & amortization
- Repeated touches accumulate. After enough use (the owner's "~50th time"), a concept
  **resolves**: stop re-deriving it and just **pull up its generalized application-breakdown.**
- Frequent concepts become cheap lookups; rare ones stay under active refinement. **Expertise
  = amortization.** ("Consultation pays rent"; a resolved concept is cheap to consult.)
- **"Resolved" is an epistemic status, not a freeze (owner, 2026-07-07): "currently settled —
  refined to the best of our ability, based on my experience, this is what this is."** Held
  with epistemic humility. **Cost and epistemics are ORTHOGONAL axes:** resolution makes
  retrieval *cheap*; it does NOT make the account *certain*. A concept can be maximally cheap
  to pull up AND still fully provisional.

## 4. Why this answers the open loop questions (from ANALYSIS.md §6b)
- **Convergence without runaway.** Convergence is **per-concept and incremental**, not a global
  fixpoint. Always good-enough, always improving on the touched set. This supersedes the
  "iterate the whole net to a fixpoint" framing and its non-convergence risk.
- **How deep concepts (L3/L4) accumulate — touch propagates UP the holarchy.** A sense touches
  a token → its group → its group's group … each getting a *little* bounded refinement. Over
  many senses the high concepts quietly accumulate enough touches to resolve. **This is the
  "potential" accumulation (H-B) given a concrete, bounded delivery mechanism** — spreading
  activation with rent, not a batch climb.

## 5. What Isaac already has vs. what's missing
**Has (partial):** `consolidate()` is already dirty-scoped ("only touched" — O(d×n)); a senses
substrate (`crystallize_senses`, `route`); an activation log + `tick`; the "consultation pays
rent" / route-demotion law.
**Missing (the build):**
- **Holonic re-admission** — drop the `type:` exclusion ([isaac.py:1014]) and give types
  co-occurrence (`seq`) doors, so a discovered group is a token at the next level.
- **Touch-propagation upward** — a touch on a token ripples up the holarchy with bounded,
  decaying strength, so higher concepts accumulate.
- **Per-concept resolution / amortization state** — a use-count / confidence that flips a
  concept from "under active refinement" to "resolved, pull up the cached breakdown."

## 6. Design tensions to honor (honest)
- **"Resolved" = currently settled, NOT frozen — and it needs no special machinery.**
  Resolution is *"refined to the best of our ability, based on my experience — this is what
  this is,"* held with epistemic humility (owner, 2026-07-07). It inherits the engine's NATIVE
  honesty: a *possible* account, not THE account (the proposal principle), **scoped to the
  experience that formed it**, and revised like any claim when experience arrives outside that
  scope. No bolt-on "invalidate-on-contradiction" is required — that was a wrong framing that
  conflated the two axes. Keep cost and epistemics separate and amortization cannot ossify a
  concept: the cached account is always labelled "current best," never "true."
- **Touch-propagation strength/decay is THE knob.** Too weak → deep concepts never get touched
  (the current collapse). Too strong → runaway. The decay of touch-strength up the holarchy is
  probably where the tower's recovery curve is actually set. It should be *learned/adaptive*,
  not a constant, wherever possible.

## 7. Relation to the experiment plan
This is the concrete specification for **E-LOOP**: the loop is *active, dirty-scoped,
touch-propagating, and amortizing* — not a global batch fixpoint. The benchmark (Foundry →
Python + scorer) measures whether this flattens the ~10×/floor recovery curve on dirty data.
