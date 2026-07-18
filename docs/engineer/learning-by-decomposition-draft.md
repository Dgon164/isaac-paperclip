# Learning by Decomposition
### Shape, dimension, and construction as a complete account of understanding
*Draft v0.1 — for review. Written to the whitedoc standard: claims carry receipts, limits are stated, nothing about implementation is disclosed or required.*

---

## Abstract

We describe a method of machine understanding that proceeds by decomposition rather than by fit. Information is broken into overlapping parts; parts are reduced to root atoms; atoms are grouped into proto-concepts; the interactions among them are explicitly typed; and the result of full decomposition is a *shape* — an invariant form whose dimensions are free variables. Learning, under this account, is the recovery of shape; understanding is demonstrated by construction — the ability to build a *different* instance of the learned shape that works. We show the method operating on real data: planetary systems reduced to a single shared law-form with per-system constants preserved exactly; a 364-year-old pressure table yielding its law from the original rows; predictions of never-provided values to within a tenth of a percent. We state the method's limits as precisely as its claims, because a refusal, under this account, is an answer with the same standing as a law.

## 1. The cycle

The procedure is old enough to be unfashionable. A machinist handed an unfamiliar engine does not fit a curve to it; he takes it apart.

1. **Ingest.** Information arrives whole: a dataset, a system, a machine. No assumption is made about its quality. Bad data is usually better than no data, provided nothing unverified is ever treated as verified.
2. **Deconstruct.** The whole is broken into overlapping parts — a car into engine, suspension, brakes; a time series into trend, cycle, and remainder. Overlap is not a defect of the partition but a source of information: what two decompositions share is more trustworthy than what either claims alone.
3. **Reduce to atoms.** Parts are broken again, and again, until further division stops yielding new kinds: pistons, valves, rods; growth terms, periodic terms, thresholds. The atoms are the vocabulary the domain is written in.
4. **Group into proto-concepts.** Recurring clusters of atoms are gathered into candidate concepts — not yet trusted, merely named. A proto-concept earns concept status by surviving comparison across independent instances: what never varies across the instances is the concept; what varies is not part of it.
5. **Type the interactions.** Parts alone are inventory. What makes a system is how its parts couple: sealing, force transfer, mechanical linkage, electrical signal; in data, dependence, delay, gating, exclusion. Interaction types are learned content, not schema — defined once, reused everywhere they recur.
6. **Construct.** The decomposition is complete when it runs in reverse: when the recovered structure suffices to build an instance. Construction is not an application of the learning. It is the *test* of it.

## 2. Shape and dimension

Full decomposition terminates in a specific kind of object: a form with its numbers removed. Kepler's third law, recovered independently from two different star systems, is one shape wearing two constants:

    system A:  y = 1.00 · a^1.5
    system B:  y = 4.90 · a^1.5

The shape — period as the three-halves power of distance — is what was learned. The constants are what a particular world happens to be. Nothing is averaged; each system keeps its own numbers exactly, to machine precision, and the kinship between them is itself recorded as a first-class fact. When a third instance later arrives from an entirely different source, it files itself into the same family without being told the family exists.

This is the payoff of decomposition over fit, and it is the difference between memorization and understanding. A fit owns one dataset. A shape owns a *design space*: every instance the form permits, including ones never observed. Learn one engine by decomposition and you have not learned an engine — you have learned the engine family, parameterized by bore, stroke, and count. The dimensions are just the variables of the shape, and a different design is a different assignment of them.

The same holds for concepts that are not equations. A cylinder is a tube; or a circle extruded; or a set of faces; or edges joined by planes. These decompositions are all correct, and none is canonical. A concept is the invariant that survives across its representations — one identity, many consistent views, with the simplest view sufficient for most purposes and richer views available when the question demands them. Fire is hot; fire is also an exothermic reorganization of matter. Steel is a hard working metal; steel is also body-centered cubic. Consistency among views is required. Uniqueness of view is not.

## 3. Dependence is part of the shape

A shape carries more than its parts: it carries which dimensions constrain which. In an engine, the bore does not change alone — the piston, the ring grooves, the clearances move with it, some by fixed offsets, some by proportion. A decomposition that recovers the parts but not the dependencies has recovered inventory, not design. Under this method, dependencies are recovered as typed relations with the same standing as the parts themselves, so that a change to one dimension propagates, is re-verified everywhere, and any member of the model that has diverged from its expectation is flagged with the size and direction of the divergence. The learned object is not a snapshot of a thing. It is the thing's rules for remaining itself.

## 4. Construction as proof

Every account of machine understanding faces the same question: how do you know it understood, rather than matched? Our answer is deliberately old-fashioned. The deliverable of a decomposition is a generative form — an equation, a parameterized structure — and the reader is invited to run it. Replication of the observed instance is the entry-level test. The decisive test is *held-out construction*: predicting or building what was never provided.

Receipts, from real data:

- The orbital shape above, recovered from planets and moons, predicted the period of a body it was never fed to within 0.07% of the measured value, and the periods of two small moons to comparable precision.
- Robert Boyle's original 1662 pressure table — the actual rows — yielded its inverse law at r² 0.99995, from data older than the calculus.
- The annual carbon-dioxide record decomposed into trend, a twelve-month cycle, and a seasonal profile whose shape was learned rather than assumed; the decomposition, fit on all but the final two years, walked forward through those years and held.
- On real market returns, the same machinery returned refusals — eight of eight series declined a law — because no shape above the noise floor was present to recover. We count this among the successes. A method that can say "there is a law here" is only trustworthy if it can also say "there is not."

## 5. What this account rejects

It rejects the premise that understanding requires novelty of mechanism. Every element above — decomposition, invariance across instances, typed constraint, parameterized form, verification by construction — has existed for decades, some for centuries; they are the working epistemology of every machine shop and every physics course. What has been missing is not a part but an assembly: the elements operating as one continuous cycle, applied uniformly from raw data to buildable design, with every claim carrying its evidence and every limit stated with its measurement.

It also rejects the treatment of the unexplained as disposable. What decomposition cannot yet reduce is not discarded; it is kept, labeled, and revisited, because today's residue is tomorrow's atom — the difference between an outlier and a discovery is usually one more comparison. That, however, is a subject for its own paper.

## 6. Limits

The recovered shape is bounded by the vocabulary of atoms available at the time of decomposition; a form outside that vocabulary is refused rather than approximated, and the refusal is recorded. Structures whose influence arrives at long delay are a measured present weakness. Dimensional dependence recovered from a single instance is a hypothesis, not a law, until corroborated across independent instances. And a shape validated on the instances presented says nothing, yet, about instances of a kind not presented: completeness is always relative to what has come through the door. These limits are carried openly. A limit named with its evidence is a feature of the record, not a confession.

## 7. Closing

Learning, on this account, is what a good machinist has always done: take it apart until the parts stop dividing, learn what holds them together, and prove you understood by building one that runs. The contribution here is not the idea. It is the demonstration that the idea, executed completely and without exception, is sufficient — that decomposition and analysis, carried all the way down and then run in reverse, is a full account of what it means for a machine to learn a thing and use it.
