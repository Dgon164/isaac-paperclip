# Isaac — Operation Paperclip

**One engine, two lenses, one operation.** A different kind of AI, built not on weights
and gradients but on a single primitive — *differentiation* (compare two things; record
*same / different / doesn't-matter*; keep what recurs). Everything it knows is stored as
readable **doors** in a graph that compiles to an inspectable matrix. Explainable by
construction, cheap enough to run on a Raspberry Pi.

This is a **curated, shareable snapshot** of a larger multi-year research line. For the
full picture, read the manual and the docs below.

---

## What's here

```
isaac.py                    the engine — one file, one class (self-test: python isaac.py → 10/10)
PAPERCLIP_MANUAL.md         the full manual (Starter / Operation / Reference / Theory)
docs/
  THE_COMPLETE_PICTURE.md      the whole research line, front to back
  ISAAC_THEORY_OF_OPERATION.md how the engine actually works
  EQUATION_DISCOVERY_ENGINE.md the equation-discovery engine, in depth
  HIGGS_writeup.md             the HIGGS results: details, findings, datasets
demos/
  crystal_in_isaac.py       perception lens → boxes as concept-nodes inside Isaac (digits)
  unsup_discover.py         law lens → recovers an invariant equation, unsupervised (toy)
  interaction_extract.py    law lens → names the particle physics in real HIGGS data
  higgs_residual.py         law lens → reconstructs invariant masses (R²≈0.865)
```

## The idea in one line

> The system differentiates. Everything else is *what field* you point it at, and *at
> what scale*. A **lens** is the thing that does the pointing.

- **The cortex (Isaac)** — the reasoning engine: nodes, doors, types; `lookup` (argmax)
  and `check` (validate a specific claim); active + idle ("sleep") modes.
- **The perception lens** — reads a trained net's representation into cheap, explicit
  answer-sheet nodes *inside Isaac's net*.
- **The law lens** — reads raw data's governing equations; the signal is the residual.

## Run it

```bash
python isaac.py                       # engine self-test → 6/6

python demos/crystal_in_isaac.py      # net-lens into Isaac (sklearn digits; instant, CPU)
python demos/unsup_discover.py        # equation discovery on a toy collider (no data needed)
python demos/interaction_extract.py   # real HIGGS via fetch_openml(23512); names the physics
python demos/higgs_residual.py        # reconstructs the intermediate-particle masses
```

Requirements: Python 3.10+, `numpy`, `scikit-learn` (the vision-lens work also uses
`torch`/`torchvision`). On Windows, `set PYTHONUTF8=1` first if box-drawing chars error.

## Honest status (what's proven, what's open)

**Verified / runs:**
- Cortex self-test 6/6 (language, math, logic, reasoning, computation, persistence), and
  it generalizes (computes `999×999` by decomposition; novel objects via verb-level).
- Perception lens: held-out digits ~90%; frozen ResNet18/CIFAR features read at 71%
  (numpy box) → **79%** (matrix-native log-likelihood reader).
- Law lens: recovered a planted invariant law exactly (96% purity / 100% recall on a
  hidden resonance); on **real HIGGS**, named the intermediate-particle masses (W boson,
  top quark, b-bbar) and reconstructed them at **R²≈0.865**. The Higgs itself is
  deep/dense — detected as the residual, not reducible to a short formula.

**Open (the honest frontier):**
- The **unsupervised aligner** — finding a lens's alignment *without* labels. The single
  most important open problem.
- **Perception from raw signal** — turning a raw field into typed parts.
- **The law lens's emission** — writing discovered equations back into Isaac as nodes so
  both lenses feed one substrate.
- **The persistence/"preserver" subsystem** is spoon-fed (per-verb outcomes given by the
  harness, not discovered) and is being reworked — see the manual's audit. It still
  passes its own self-test but does not *understand* the categories it classifies.

The rule the whole project runs on: **a trained neural net is never the deliverable** —
the deliverable is explicit, readable structure. Nulls are reported as nulls.

## More

The full corpus (history, theory sources, the personal story, all experiments) lives
outside this snapshot. Start with `PAPERCLIP_MANUAL.md`, then `docs/THE_COMPLETE_PICTURE.md`.

---

## Update — 2026-07-01/02: the discovery stack

The engine grew four capability areas in two days (self-test now **10/10**),
all numpy, all null-gated, no trained networks anywhere:

- **discover()** — the challenge loop: given examples of something it cannot
  do, it recovers the explicit equation (held-out validated, reusable via
  `apply_law()`) or says honestly what state its knowledge is in:
  UNDERSTOOD / PARTIAL / CAPTURED (caught by exemplars, not yet said) /
  NO RULE. 0/40 false discoveries on pure noise across two batteries.
  Rival look-alike forms (parabola vs wide cosine, exp vs cubic) are held
  open with a named discriminating probe until `confirm()` settles them.
- **Waves** — temporal crystallization: simultaneity groups, handoffs,
  circles, recursively (circles of circles); a tracked circle gives an
  internal clock (100% phase through occlusion), expectation, and
  temporary statuses whose explanations EMERGE from ordinary co-activation
  (`blocks(disk) <- cloud`), entering the fact index.
- **Registration perception** (experiments/) — pose/identity factoring:
  digits under random position+scale go from ~5-15% to 84-87%; ideals +
  learned key identifiers (differentia) hit 99.7% on a six-way look-alike
  world and correctly demote unreliable taught features.
- **Covtype accounting** (experiments/) — articulated doors 59%, captured
  exemplars **94.4%** with a learned readable metric (elevation 0.76) vs
  the old 82% net baseline; the row-index-alone control (79%) quantifies
  the dataset's spatial leakage.

Full methods, numbers, limits, and how to verify every claim:
`docs/WRITEUP_FOR_REVIEW.md`. Theory: `docs/Understanding_as_Closure.md`.
The audit discipline: `docs/AUDIT_STANDARD_v1.md` + `docs/VERDICT_SHEET.md`.
The `experiments/` folder is the full harness (planted ground truth,
batteries, red team) — every result re-runnable; nothing requires trust.
