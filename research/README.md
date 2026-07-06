# Method Lab — toward autonomous discovery

The step past *finding information in data* to *discovering the methods that find
it*, and *confirming or denying its own findings with no answer key.* The
scientific method as a running loop: **test → predict → verify → reuse.**

Everything here uses only the existing engine (`../isaac.py`) — `discover`, its
held-out split, and its permutation nulls — plus a small toolkit of transforms.
No new primitives; the capability is in the *loop*, not new machinery.

## The scripts (run each with the repo venv)

- **`method_discovery.py`** — raw data + a toolkit of transforms; Isaac must find
  *which key* turns the data into a recoverable form, **without being told**.
  Result: found `identity` for a plain polynomial, `log` for a power law it
  couldn't express directly (degree-5 product), `diff` for a cumulative signal
  that raw discovery reads as noise. It prefers the *simplest* key that works.

- **`self_verify.py`** — Isaac gets the **answer** but not the method, and grades
  *itself*: held-out reproduction (does the derived process reproduce the answer
  on data it never fit?) + a permutation null (could the toolkit reproduce a
  *shuffled* answer just as well?). CONFIRM only if it reproduces past the null;
  otherwise DENY — including real-but-unreachable structure. Produced three honest
  states: **CONFIRM** / **DENY-empty** (no structure) / **DENY-partial** (structure
  present, current keys can't reach it — *this is the next question to itself*).

- **`researcher_loop.py`** — the closed loop. Decompose a signal into its
  derivative tower (position → velocity → acceleration …) until it bottoms at a
  **constant core**; self-verify each level; retain the tower as a reusable
  **holon**; then reuse it to recognize + solve a *new* problem without relearning.
  Notable: raw position *denied* itself (an extrapolation-fragile surrogate), but
  one derivative down the law became linear and **verifiable** — decomposition
  didn't just simplify, it made the law confirmable, and the core was the true
  constant acceleration.

## The principle (the "middle pass")

decompose → identify the core elements → find their values → **verify against
reality** (feed inputs, compare to the answer, past the null) → compose to the
result → **retain the whole (or parts) as a holon** for reuse. "You need velocity
to figure out acceleration": each level is a whole built of the one below,
reusable in whole or part. That reuse is what makes it cumulative.

## Open next rungs

- composition chains (depth-2+ tool pipelines) and a bigger toolkit (fold,
  residualize, stratify, project, the parallax lift);
- **retention**: winning chains become permanent named methods (the library
  *grows* — it gains keys it didn't have);
- a **metacognitive map**: problem-signature → the key that opens it, so it
  routes instead of brute-forcing;
- a **better scorer**: recovery + parsimony + extrapolation (see
  `divergence_probe.patch`) so it never crowns a surrogate;
- **cross-route agreement**: two independent chains reproducing the same answer =
  a stronger CONFIRM than one.

See also DESIGN_INTENT law: *everything relative; absolute is one correction
factor.* All measurement here is relative-native by default.
