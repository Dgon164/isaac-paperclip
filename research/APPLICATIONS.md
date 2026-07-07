# Applications & Capability Ideas (future)

Companion to `HANDOFF.md`. **Grounding rule:** Isaac's real edge is *legible discovery
+ honest verdicts (incl. refusal) + relational/cross-domain structure + messy-data
ingestion + cheap/CPU + cumulative-over-time.* Applications that lean on **those** are
strong fits; ones that need raw predictive accuracy or heavy pixel perception are
stretches. Marked **[strong] / [medium] / [stretch]**, honestly.

---

## A. Capability building blocks to add (feed the TODO)

- **Regime / subtype discovery** *(your "specialization within datasets")* **[strong]** —
  a dataset is rarely one law; it has *strata* where different laws hold. Discover
  "this data has 3 regimes, each with its own relationship," and the *scope* of each law
  (which rows it governs). The crystallizer (circles / subtypes / hierarchy) is built for
  exactly this; wire it to the discovery side.
- **Automated experimental design / "what to measure next"** **[strong — a real
  differentiator]** — turn the resolution-paths that BEST-GUESS and MEANINGFUL-ABSENCE
  already emit into a *ranked* list of the single measurement/intervention that would
  resolve the most (upgrade a pattern to a cause, fill a hole, split confound-vs-mediation).
  Most systems predict; Isaac can say *what to do next*.
- **Inverse / outcome-derived solving** *(your "outcome-derived processing")* **[medium]** —
  given a desired *outcome*, find the process/inputs that produce it. `method_discovery`
  (find the chain that derives an answer) and `discover`'s solve/gap-fill are the seed;
  add search over the discovered laws toward a target.
- **Anomaly detection + diagnosis** **[strong]** — learn the normal lawful structure,
  flag deviations (a value off the manifold, or a MEANINGFUL-ABSENCE: an expected
  relationship that broke), *and* diagnose (which relationship failed; cause vs symptom).
  Legible + on-device + honest → predictive maintenance, sensor/industrial/medical monitoring.
- **Sensor fusion / multi-source integration** **[strong]** — the "no separation" law +
  the matrix-assembler: fuse ragged, differently-sampled, partly-missing streams into one
  substrate and find the *cross-source* relationships. (The fire-ecology multi-source idea.)
- **Spatial: relational 3D/2D recognition + articulated tracking + the rangefinder**
  **[medium]** — recognize structures by pose/scale-free *relational signature* (no metric
  reconstruction); articulated SfM (segment by the locked-null → lift each rigid part →
  join at hinges); the monocular relative-range chain we designed. Robotics / AR on-device.
- **CAPTURED-smooth + deflate-recurse** **[medium]** — already in the TODO; the honest
  handler for latent-but-unresolvable signal, and a way to peel layers.
- **Cross-net / D5 meta-structure** **[stretch, highest ceiling]** — already in the TODO;
  compare whole nets for shared *relational* motifs (a cross-domain principle).

---

## B. Application domains

- **General scientific research** **[strong — the core objective]** — any tabular /
  time-series dataset → the lawful relationships, the independent drivers, the meaningful
  absences, correlation-vs-cause, and *what to measure next*. Benchmark: SRBench/Feynman.
- **Chemical analysis** **[strong–medium]** — spectroscopy (a missing expected peak is a
  MEANINGFUL-ABSENCE = a forbidden transition or absent compound); reaction kinetics (rate
  laws via the derivative tower + the clock); legible structure–property relationships;
  compound ID by relational signature.
- **Medical / diagnostic reasoning** **[strong on honesty]** — which measures are lawfully
  linked (the lipid-panel demo), which are independent, is a marker *causal* or a proxy
  (BEST-GUESS + resolution-path), an expected-but-absent symptom as information. In
  high-stakes / regulated settings, *honest refusal* beats black-box confidence — that's
  the selling point.
- **Anomaly / fault detection & predictive maintenance** **[strong]** — industrial, IoT,
  aerospace, energy grids. Learns normal structure, flags + diagnoses, runs cheap on-device.
- **Time-series forecasting with honesty** **[medium]** — the clock (trend + cycle/circle)
  + "usable pattern, cause unresolved." Forecasts that say how far to trust them and where
  they break. Demand, climate, ops — with the refusal intact.
- **Game development** **[medium / stretch]** — legible, *learnable, debuggable* NPC AI
  (differentiation, inspectable — not a black-box net); balance analysis from playtest data
  (what drives win-rate; unused mechanics = meaningful absences; correlation-vs-cause in
  tuning); emergent-mechanic discovery via the interaction map; procedural generation from
  *learned* structural grammars. Big plus: CPU-cheap, ships on-device, no GPU.
- **Modelling & 3D/2D tracking** **[medium]** — see the spatial block above: mechanism
  perception, relational recognition, monocular rangefinding; robotics/AR.
- **Outcome-derived processing & solutions** **[medium]** — inverse problems, root-cause
  analysis (an outcome → its drivers + the resolution-path), design-to-target.
- **Cross-domain transfer / analogy** **[stretch, highest ceiling]** — the same motif in
  two unrelated domains = a general principle. This is the one that could be genuinely
  *novel*; it runs into the unsupervised-aligner problem, so approach via relational
  signatures + a planted-motif gauntlet + a brutal null.
- **Education / explanation** **[strong]** — because the net *is* the equation and doors
  are readable, Isaac can *explain what it found and why*. A discovery engine that teaches —
  the opposite of an oracle you can't question.
- **Knowledge / ontology extraction** **[medium]** — the FCA/crystallizer side: concepts,
  hierarchies, and relationships out of structured/semi-structured data.

---

## C. The honest north star for choosing among these

Pick the ones where **"a legible law + an honest 'here's what I can't explain and what to
measure next'"** is worth more than a raw prediction. That's scientific discovery, high-
stakes/regulated domains, anomaly diagnosis, experimental design, and cross-domain transfer —
*not* leaderboard accuracy, which deep nets own. The differentiator is always the same:
**do something a black box structurally cannot — be legible, be honest, and say what it
doesn't know.** Everything above is a way to point that one edge at a real problem.
