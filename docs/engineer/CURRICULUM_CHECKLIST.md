# THE CHECKLIST CURRICULUM — the engineer lane's complete testable inventory
*Owner directive, 2026-07-18: "i want anything and everything you can do as a feature in cad, anything and everything as a list of python things like variables and common structures, anything and everything as a list of electrical design elements, tracing and blueprinting... a list of every testable thing in any of these fields so we can see a, if he can learn it, b if he understands it, and c if he can use it."*

*Conventions: items marked `[x]` carry a receipt (probe/battery reference). Items marked `[ ]` are untested. Results get appended inline as they land — this document is the lane's scoreboard. The ownership discipline applies to every item: LEARNED means IN THE NET (told/taught/discovered, container-stamped, supersedable), never in Python.*

---

## THE GRADING STANDARD (applies to every item below)

**A — LEARN.** The item enters his net through a legitimate door: told with provenance (`tell_law`/`tell_rule`/handbook ingestion), taught as facts (`teach`/`teach_not` in a container), or discovered from data/code (the discover/read roads). Receipt: the node exists, wears its container, and is supersedable. *An item that lives only in Python is NOT learned (the ownership audit's law).*

**B — UNDERSTAND.** He answers courts he was never directly told the answers to: derive the missing quantity (laws-run-backward), keep multiple views consistent (the view court), refuse a corrupted instance with the residual named, name the degrees of freedom, and explain via receipts (which of his laws/facts fired). Understanding = closure: the answer set exceeds the input set.

**C — USE.** Construction: apply the item in a build that an INSTRUMENT can check — generate the geometry, compute the stack-up, patch the code, size the resistor — and transfer: use it in a context it wasn't taught in. Instruments (mesh integration, execution, circuit evaluation) confirm and never mind.

Every item's full grade = A+B+C with receipts at each letter. A null must exist per test (a scrambled/corrupted instance must refuse).

---

## SECTION 1 — CAD / MECHANICAL DESIGN

### 1.1 Sketch entities & 2D geometry
- [ ] point, line, arc (3-pt, center), circle, ellipse
- [ ] rectangle (corner/center), polygon (n-gon), slot
- [ ] spline / interpolated curve
- [ ] construction geometry (reference-only entities)
- [ ] 2D fillet, 2D chamfer, trim, extend, offset curve
- [ ] mirror, linear pattern, circular pattern (2D)
- [ ] projection of edges into a sketch plane

### 1.2 Sketch constraints (the 2D constraint court)
- [ ] coincident, concentric, tangent
- [ ] parallel, perpendicular, horizontal, vertical
- [ ] equal, symmetric, midpoint, colinear, fixed
- [ ] driving vs driven dimensions
- [ ] fully-constrained detection (zero DOF, receipt)
- [ ] under-constrained → DOF NAMED (never a guess)
- [ ] over-constrained/inconsistent → REFUSED with residual
- [x] the constraint-arithmetic court itself — `engineer_transplant_probe` X2/X3 (derive/corroborate/refuse/DOF from a told constraint)

### 1.3 Part features (3D)
- [ ] extrude (boss), extrude (cut), extrude to-surface/through-all
- [x] the recipe→solid instantiation road — `engineer_m_probe` P2 (tube recipe → watertight mesh, volume exact at the mesh's own ruler)
- [ ] revolve (boss/cut), axis selection
- [ ] sweep (path + profile), loft (multi-profile)
- [ ] hole: simple, counterbore, countersink, tapped (callout-bearing)
- [ ] 3D fillet (const/variable radius), 3D chamfer
- [ ] shell (uniform wall from solid), rib, draft angle
- [ ] linear/circular/mirror pattern (3D), scale
- [ ] thread (as spec, not cosmetic), boss, groove, keyway
- [ ] feature ORDER matters (rollback semantics — order_matters applied to construction history)

### 1.4 Datums, parameters, configurations
- [ ] datum planes/axes/points; coordinate systems
- [ ] construction history as first-class structure (the recipe IS the model — D2)
- [x] parametric dimensions drive geometry — `engineer_m_probe` P3 (the family: one recipe, many instances)
- [ ] design tables / configurations (a table of instances = a family enumerated)
- [ ] equations between dimensions (his laws driving his geometry)

### 1.5 Tolerances & fits
- [ ] dimensional tolerance (bilateral, unilateral, limit)
- [ ] fit classes: clearance / transition / interference; hole-basis & shaft-basis
- [x] interference vs clearance decided + NAMED — `engineer_m_probe` P4, transplant X7
- [ ] IT grades / standard fit callouts (H7/g6 etc. — handbook ingestion, cited)
- [ ] GD&T: flatness, straightness, circularity, cylindricity
- [ ] GD&T: perpendicularity, parallelism, angularity
- [ ] GD&T: position, concentricity, symmetry, runout (circular/total), profile
- [ ] datum reference frames; material condition modifiers (MMC/LMC)
- [ ] surface finish (Ra) as a spec item
- [x] tolerance stack-up along a dependency chain — transplant X4 (bore→piston→groove propagation + stale flag); worst-case [ ] RSS [ ]

### 1.6 Mass properties & materials
- [x] volume / section area from the recipe — `engineer_m_probe` P1
- [x] mass at cited density — P1 (steel 7850 kg/m³, told w/ citation)
- [ ] center of gravity; moments of inertia
- [ ] material as told-knowledge with properties (density, E, yield — handbook, cited)
- [ ] thermal expansion (ΔL = αLΔT as a told law, courted)

### 1.7 Assemblies & mates
- [ ] mate: coincident, concentric, distance, angle, tangent
- [ ] mate: gear (ratio), rack-pinion, cam-follower, slot, limit, symmetric
- [ ] joints: revolute, prismatic, cylindrical, spherical, planar, fixed
- [ ] assembly DOF accounting (mates consume DOF; the leftover is motion)
- [ ] interference detection in an assembly (two solids, one space = WOUND)
- [x] contact taxonomy: connected / touching / not-touching w/ quantities named — `engineer_m_probe` P4-P5, transplant X5/X7 (HIS facts)
- [x] force/load path tracing over the contact graph — P6, transplant X6
- [ ] exploded views (assembly order as a sequence structure)
- [ ] subassemblies (hierarchy law applied to assemblies)

### 1.8 Machine elements (each: spec → court → sizing use)
- [ ] fasteners: bolt/nut/washer, thread standards (UNC/UNF/metric), grade → strength, torque spec
- [ ] bearings: ball/roller/thrust/journal; bore/OD/width; load rating basics
- [ ] gears: spur (module/DP, pressure angle, tooth count, ratio, center distance = m(z1+z2)/2 — a tellable law)
- [ ] gears: helical, bevel, worm (ratio + hand)
- [ ] belts & pulleys (ratio, wrap), chains & sprockets
- [ ] springs: compression/extension/torsion; rate k = Gd⁴/(8D³n) (tellable, courted)
- [ ] shafts, keys & keyways, splines, retaining rings
- [ ] seals & o-rings (groove sizing — a fit problem)
- [ ] couplings; cams & followers (profile → motion)
- [ ] linkages: four-bar (Grashof condition — a tellable inequality), slider-crank
- [x] slider-crank kinematics vs closed form — QUEUED as M5 (not yet green)
- [ ] lead screws (lead, pitch, mechanical advantage)

### 1.9 The construction gates
- [x] a real 3D model emitted from a recipe (.obj, watertight) — `engineer_m_probe` P2
- [ ] a bracket with holes from spec (multi-feature construction)
- [ ] a mating pair designed to a chosen fit (his fit tables, his court)
- [ ] the M6 single-cylinder engine gate (piston/pin/rod/bore: recipes + mates + dependencies + contact kinds; change the bore, the machine follows with receipts)
- [ ] the V8 (M6 with bigger counts, when M6 is boring)

---

## SECTION 2 — PYTHON / CODE

### 2.1 Values & types
- [ ] int, float, bool, str, None; complex; bytes
- [ ] literals (incl. underscores, bases: hex/oct/bin)
- [ ] float precision & equality (why 0.1+0.2 ≠ 0.3 — a floors lesson)
- [ ] truthiness (empty containers, 0, None)
- [ ] type() / isinstance; conversion between types

### 2.2 Variables & scope
- [x] assignment; names bind to values — `engineer_c12_probe` M1 (writes/reads as doors)
- [ ] multiple assignment & unpacking (a, b = b, a)
- [ ] augmented assignment (+=, the AugAssign the read road already reads)
- [ ] scope: local / enclosing / global / nonlocal; shadowing
- [ ] aliasing vs copying (two names, one object — identity vs equality)
- [ ] del; constants by convention

### 2.3 Operators
- [ ] arithmetic (+ - * / // % **), precedence
- [ ] comparison + chained comparison (0 <= x < 10 — the read road parses these in guards)
- [ ] logical and/or/not + short-circuit
- [ ] bitwise (& | ^ ~ << >>)
- [ ] is vs ==; in / not in
- [ ] ternary expression; walrus

### 2.4 Collections & their operations
- [ ] list: index, slice (negative/step), append/extend/insert/pop/remove/sort/reverse
- [ ] tuple (immutability; as record), namedtuple concept
- [ ] dict: get/setdefault/update/items/keys/values; insertion order
- [ ] set / frozenset: union/intersection/difference/symmetric difference
- [ ] comprehensions: list/set/dict/generator
- [ ] nesting; shallow vs deep copy
- [ ] stack (append/pop), queue/deque, heap (heapq)
- [ ] linked list, tree, graph as structures (nodes+doors — HIS substrate, literally)
- [ ] hash map mechanics (why dict lookup is O(1) — concept)

### 2.5 Control flow
- [x] if/elif/else as branch doors — `engineer_c12_probe` M1/M2 (control flow mapped as doors, map regenerates the program)
- [ ] while; for + range; iteration over collections
- [ ] break / continue / else-on-loop; pass
- [ ] match/case
- [x] guard conditions dominating outcomes — `engineer_gread_probe` R5 (fatal guards read + classified)
- [ ] exceptions: try/except/else/finally; raise; custom exceptions; hierarchy
- [ ] recursion (base case + progress = a loop invariant)

### 2.6 Functions
- [ ] def / return (incl. multiple returns, implicit None)
- [ ] parameters: positional, keyword, defaults (+ the mutable-default trap)
- [ ] *args / **kwargs; keyword-only; positional-only
- [x] slot signatures: inputs, outputs, RESIDUE mandatory — `engineer_e0_probe` S1, `test_engineer` N3 (division is two-in two-out)
- [ ] lambda; first-class functions; closures (+ late-binding trap)
- [ ] decorators; generators (yield); iterator protocol
- [ ] pure vs side-effecting (a function's slot signature tells)

### 2.7 OOP
- [ ] class / instance; __init__ / self
- [ ] instance vs class attributes; methods (instance/class/static)
- [x] attribute state machines read from a class — `engineer_gread_probe` (Snake's state read from step())
- [ ] inheritance; super(); MRO; polymorphism
- [ ] dunder protocol: __repr__ __eq__ __len__ __iter__ __enter__/__exit__
- [ ] properties; composition vs inheritance

### 2.8 Modules & environment
- [ ] import forms; __name__ == "__main__"; packages
- [ ] stdlib survey as vocabulary: math, os, sys, json, re, itertools, collections, functools
- [ ] file IO (read/write/append; context managers)
- [ ] string formatting (f-strings)

### 2.9 Program-level structures (the shapes — C4's quarry)
- [ ] validation shape (check-then-use)
- [ ] error-handling shape (try/log/reraise vs swallow)
- [ ] retry shape; timeout shape
- [ ] accumulator, counter, sentinel, flag patterns
- [ ] EAFP vs LBYL as rival shapes (duelable!)
- [ ] common bugs as NEGATIVE knowledge: off-by-one, mutation-during-iteration, float ==, mutable default, late-binding closure, integer division surprise

### 2.10 Program courts (the built capability, growing)
- [x] read → map as doors; exactly-once completeness; map-alone regeneration — `engineer_c12_probe` M1/M2, `test_engineer` N5
- [x] scramble null (a different program maps differently) — M3/N6
- [x] containment: CONTAINED/UNCONTAINED/REFUSED w/ escapes named — K1-K5, N7
- [x] goal recovery from mechanism (behavioral) — `engineer_grung_probe` 8/8 (mod null, superstition null, construction 15.3×)
- [x] goal recovery from TEXT (the read road) — `engineer_gread_probe` 8/8 (valence from code; FREE by dead data flow)
- [x] physics constants + force law read from sim source, instrument-confirmed — `engineer_m_probe` P7/P8
- [ ] intent triangulation (docs vs code-majority vs data) — C3, queued
- [ ] shape mining on code via the genesis loop — C4, queued
- [ ] construction closes the loop (synthesize patch → re-read with same court) — C5, queued
- [ ] the rebuild gauntlet (map → rebuild, divergence ledger, Chesterton's fence) — C6, queued

---

## SECTION 3 — ELECTRICAL DESIGN

### 3.1 Fundamentals (each a tellable law + its courts)
- [ ] charge, current, voltage, resistance, power, energy (the vocabulary)
- [ ] Ohm's law V = IR (told; derive any of three — laws-run-backward is BUILT for this; note: product form needs the nonlinear solve rung)
- [x] Kirchhoff current/voltage as slot-balance — transplant X4 (series voltage sum via the generic solver); full node/loop courts [ ]
- [ ] series/parallel resistance (1/R rules — the parallel form is the harder tell)
- [ ] voltage divider; current divider (sizing = the USE test)
- [ ] power: P = VI = I²R = V²/R (multi-view identity on one quantity!)
- [ ] ground/reference; open vs short as limit cases
- [ ] conductance; wire resistance/ampacity (tables, cited)

### 3.2 Passive components
- [ ] resistor: E-series values, color bands, tolerance, power rating (derating court)
- [ ] capacitor: C, series/parallel (the INVERSE of resistors — a beautiful duel-of-forms), charge/discharge, τ = RC
- [ ] inductor: L, τ = L/R, back-EMF (sign!)
- [ ] impedance/reactance: Xc = 1/(2πfC), Xl = 2πfL (frequency-dependent laws)
- [ ] RLC resonance f = 1/(2π√(LC))
- [ ] filters: low/high/band-pass; cutoff = 1/(2πRC) (design-to-spec = USE)

### 3.3 Semiconductors
- [ ] diode: forward drop, reverse blocking, the exponential reality vs the 0.7V view (multi-view!)
- [ ] zener regulation; LED + current-limit resistor sizing (the classic USE test)
- [ ] BJT: NPN/PNP, base current, β, cutoff/active/saturation; as switch; as amplifier
- [ ] MOSFET: gate threshold, as switch; gate charge concept
- [ ] op-amp ideal rules (no input current, virtual short); follower, inverting, non-inverting (gain = -Rf/Rin — tellable, courted); comparator
- [ ] rectification: half/full/bridge + smoothing cap ripple

### 3.4 Sources, protection, practice
- [ ] batteries: series/parallel, internal resistance (loaded vs open voltage — a shadow!)
- [ ] voltage regulators: linear (dropout, dissipation) vs switching (concept)
- [ ] fuses/breakers (sizing court), transformers (turns ratio law)
- [ ] datasheets as slot signatures (limits ingested with citations — EL2)
- [ ] decoupling; pull-up/pull-down sizing
- [ ] safety: isolation, fusing, creepage (told rules, cited)

### 3.5 Digital
- [ ] logic levels; gates AND/OR/NOT/NAND/NOR/XOR (truth tables = told rules — the XOR frontier already probe-proven in pools!)
- [ ] De Morgan (a rewrite law — dueling forms of one function)
- [ ] combinational: half/full adder, mux, decoder (construction tests)
- [ ] latches/flip-flops (state!), counters, shift registers
- [ ] timing: setup/hold concept; debouncing
- [ ] PWM; ADC/DAC concept; serial protocols concept (UART/SPI/I2C framing)

### 3.6 Analysis courts
- [ ] node analysis; mesh analysis (the systematic roads)
- [ ] Thevenin/Norton equivalents (multi-view identity of a network!)
- [ ] superposition (additive-order law applied to sources)
- [ ] transient vs steady state; AC: RMS/peak/phase
- [x] conservation as the court (unbalanced net refuses w/ residual) — the E0 slot court generalizes; EL1 full form [ ]
- [ ] planted-fault forensics (wrong resistor located by residual accounting — EL4, the shadow organ with a soldering iron)
- [ ] synthesis to spec + verification (EL5: divider under load, RC filter at f)

---

## SECTION 4 — TRACING & BLUEPRINTING

### 4.1 Mechanical drawings (a drawing is a VIEW — the view court applies)
- [ ] orthographic projection; first vs third angle
- [ ] view selection & alignment; iso/pictorial views
- [ ] section views: full, half, offset, revolved, broken-out; hatching conventions
- [ ] auxiliary views; detail views; broken views; scale
- [ ] line conventions: visible/hidden/center/phantom/section/dimension
- [ ] dimensioning rules (placement, chains vs baseline, reference dims)
- [ ] thread & hole callouts (⌀, CBORE, CSK, tap specs)
- [ ] GD&T frames + datums on drawings
- [ ] weld symbols; surface finish symbols
- [ ] title block, BOM, balloons, revision block
- [ ] DRAWING → MODEL (tracing: rebuild the solid from views; court: the rebuilt model re-projects to the same drawing)
- [ ] MODEL → DRAWING (blueprinting: emit views from the recipe; court: round-trip)
- [ ] drawing ↔ artifact consistency (a wrong dimension on one view = a WOUND between views)

### 4.2 Electrical schematics
- [ ] component symbols (the full vocabulary of 3.2-3.5)
- [ ] reference designators (R1, C3, U2 conventions)
- [ ] junction vs crossover; net labels; power/ground symbols
- [ ] pin numbers; connectors; buses; hierarchical sheets
- [ ] SCHEMATIC → NETLIST (extraction — the circuit's map-as-doors, C1's twin)
- [ ] NETLIST → SCHEMATIC (synthesis of a readable drawing)
- [ ] schematic ↔ netlist ↔ built-circuit consistency courts
- [ ] wiring diagrams vs schematics; ladder logic basics
- [ ] PCB reading: layers, traces, vias, silkscreen, ground plane

### 4.3 Diagrams general
- [x] code ↔ flowchart (both directions exist: code_map + map-regeneration) — `engineer_c12_probe` M1/M2
- [ ] block diagrams (system level; slots between blocks)
- [ ] state diagrams (the Snake state machine drawn — and read back)
- [ ] timing diagrams; P&ID basics
- [ ] signal tracing: follow one net source→load through a schematic
- [x] load-path tracing (mechanical) — `engineer_m_probe` P6
- [x] dependency tracing (TMS chains) — `engineer_e0_probe` P1, transplant X4

---

## THE SCOREBOARD (as of 2026-07-18)

**Items enumerated: ~330. Green with receipts: 24. Everything else: honestly untested.**

The already-green cluster proves the GRADING MACHINERY works end to end at least once per letter: A (constraint told, taxonomy taught, goal sheets read), B (derive/corroborate/refuse/DOF; multi-view; the intent court), C (the .obj construction; the sheet-policy playing Snake at 15.3×; k and e confirmed by instrument).

**The curriculum discipline:**
1. Items are fed in checklist order within a section; sections interleave freely (E0's law: park and switch).
2. Every item lands as NET CONTENT (the ownership law) — the checklist is a list of things to TELL, TEACH, or have him DISCOVER, never a list of functions to write.
3. Every A gets its B court and C construction before the box checks; a box may be PARTIALLY checked (A✓B✓C✗) and says so.
4. Wrong predictions stay in the record next to the item.
5. This file is the scoreboard: append `— [date, probe, result]` to items as they land.

---

## RESULTS — 2026-07-18, THE FULL FEED (curriculum_feed.py, fed LIVE)

**A-grade (learned, in his net):** 48 law applications over 28 form
nodes (20 applications landed on SHARED forms — see the shapes
discovery below), 148 facts, 10 certified negatives — containers:
cad-mechanical / python-code / electrical / drafting. His account
after the meal: 843 nodes, 1,524 doors, 37 laws, 311 facts
(road-trial #14).

**B-grade (courted):** 28/28 forms full-courted — corrupt instances
refused 28/28; unknowns derived round-trip 53/57 (the 4 misses are
the generic solver's honest scope limit: mixed-power forms like
gauss-sum — named, queued for solver v3).

**C-grade (constructed, sampled):** 5/5 — LED resistor sized from
his law + his E12 facts + his safety rule (350Ω → 390Ω); power
computed three ways from three of his laws, one answer (multi-view
on a quantity); a voltage divider solved by CHAINING his laws
(series → Ohm backward → Ohm forward = 6.0V exact); an H7/g6
mating pair classified through his fit facts + a sleeve OD from his
tube law; the mutable-default bug flagged from HIS negative
knowledge. C coverage is SAMPLED, not exhaustive — the checklist
boxes above check only where a receipt exists.

**THE SHAPES DISCOVERY (forced by the feed itself):** Ohm's law,
density, Hooke's law, spring force, torque, work, momentum, Q=CV,
τ=RC — ALL one form (y = x0·x1). tell_law correctly answered
MATCHES on every re-telling; the curriculum therefore lands as FEW
FORMS + MANY APPLICATIONS (fact-bundles binding quantities to
shared slots) — the shapes-and-labels ontology arriving by itself,
measured: 48 applications compress to 28 forms.

**SELECTION AT SCALE, first real load:** 37 laws held, precision
1.0, probe 0.264s, ask 0.0022ms — the gauge's curve begins.
