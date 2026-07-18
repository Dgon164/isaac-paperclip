# RESEARCH WRITEUP — 2026-07-17 (evening): PER-DATASET CONTAINERS + CROSS-DOMAIN CRYSTALLIZATION

**The owner's design, verbatim: "what if we had it so that each
dataset is defaulted to its own container, and it can crystalize the
container structures into cross domain structures." Designed,
probed, cured twice, and promoted in one sitting — promotion #17.**

## 1. What was built

Two things, both of which existed as scattered pieces and needed
only to be pointed at each other:

**Stamped intake.** Every dataset Isaac eats now lands in its own
world, automatically, named after the source itself. Feed him a
table called `orbits-sol` and everything he learns from it — the law,
the law's bookkeeping facts — is stamped as true *in the world of
that dataset*, not in base (his model of reality). Nothing about the
container is designed by anyone: the source's identity IS the
container. Base — the expensive world, the only one measurements
feed — is never the default landing zone again. If a world is
already open (a practice session, a decoded foreign net), the law
lands there; an explicit container wins over everything.

**Cross-domain crystallization.** A new organ, `crystallize_forms`,
walks his laws and groups them by *shape with the numbers removed*.
When the same shape shows up in two different worlds with different
constants, that kinship becomes a real thing in the net: a parent
node (a `lawform:`) with a door to each world's variant. The parent
holds the shared form and nothing else — no averaged constants exist
anywhere, each world keeps its own numbers exactly.

## 2. What the structures look like

The probe world is Newton's actual situation. Kepler's third law
was fed as two separate star systems and one stranger:

    data-orbits-sol       law: y = 1.00 * a^1.5   (UNDERSTOOD, exact)
    data-orbits-trappist  law: y = 4.90 * a^1.5   (UNDERSTOOD, exact)
    data-falling-bodies   law: y = 3.00 * t^2     (UNDERSTOOD, exact)

Crystallization then produced exactly one new node:

    lawform:6b98f4af  --variant-->  law:orbits-sol
    lawform:6b98f4af  --variant-->  law:orbits-trappist

That parent IS "Kepler's third law" as a cross-domain object — the
recognition that two worlds obey one shape — while each world keeps
its own constant (its star's mass, in physical terms). The stranger
joined nothing.

## 3. How it is represented, and the receipts it carries

A container is still just a door tag (`in:<world>`), exactly as the
07-15 containers work built it — no new primitives. The law node now
carries three new pieces of meta: its `container`, its earned
`verdict`, and (via the family) its `status.family`. Every exclusion
from crystallization carries a receipt saying why (the consideration
law). The family naming reuses `tell_law`'s checksum exactly, which
bought the best receipt of the day for free: when a third same-form
law was TOLD afterward (`+2.50*x0^1.5`), tell_law's own variant road
filed it into `lawform:6b98f4af` — the *same node* the crystallizer
minted. Told knowledge and discovered knowledge converge on one
family without either road knowing the other ran.

## 4. What was found (complete numbers)

- Probe `container_crystal_probe.py`: **8/8** (4.1s). Battery
  `container_crystal_battery.py`: **8/8** (4.2s), joins the
  permanent promotion wall.
- Variants keep their constants to **3.3e-16 / 1.3e-15** relative —
  nothing is smushed.
- Selection by container: `which_law` names the right law per world
  (both MATCH), and on a 50/50 interleaved superposition of the two
  worlds it answers **NONE — new variant candidate**. This is the
  first demonstration of the selection gauge's ≥2-laws precondition
  — the road-trial instrument that has been skipping "insufficient
  laws" since launch now has its food defined.
- The wound, measured then closed: before this promotion, a bare
  `discover()` indexed its `explains` fact with no container tag,
  and base's container-less road answered it — **every dataset
  feeding leaked into base**. Measured on a fresh mind (run 1, D8),
  closed by making `_teach_fact` container-aware, re-proven closed
  (run 2, D8 flipped): base sees `[]`, the dataset's world sees the
  fact.

## 5. Where it broke, and what the breaks taught

Run 1 of the probe went 6/8, and both failures are the research:

**The crystallizer was gullible (D6).** Scrambling the row→container
assignment built two pseudo-worlds, each a 50/50 mixture of the two
star systems. Discover, honestly, could only mint mush from mixture
— linear surrogates (`+7.84*x0`, `+9.77*x0`), PARTIAL verdicts — but
the mush *shared a shape across the two pseudo-worlds*, so the
crystallizer minted a family from it. The cure is a principle, not a
patch: **only laws that earned UNDERSTOOD in their own container may
crystallize.** Kinship between two confusions is not knowledge. With
the tooth in, the scrambled null dies cleanly (0 families, 2
exclusions with receipts) — and note *why* it dies: not because the
shapes stop matching, but because mixtures never earn the verdict.
The admission discipline IS the null's teeth.

**The first refusal test was accidentally answerable (D5).** The
mixed set initially gave one world the small values and the other
the large — a range split, which the heavy end's law legitimately
fits. Kept as a lesson: a range-separated mix is honestly
piecewise-answerable; testing refusal requires true superposition
(interleaved worlds). The refusal then came correctly.

## Standing next doors (named, not promised)

- **The universality road**: same form + same constants across
  independent containers is currently a witness record. Promoting
  such a law INTO BASE through the full court is the natural next
  rung — that is how a dataset's truth becomes Isaac's truth.
- **Session intake stamping**: datasets now stamp; the sparring/
  practice road still lands speech in base's space — the same
  design wants the partner model to be a source container.
- **Crystallization at higher levels**: relations among lawforms
  (the recursive-pools rung, probe-proven 10/10) — families of
  families when the food creates them.
