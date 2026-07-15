# DATA OPS SEGMENT — the plan
**Positioning, deliverables, batteries, and promotion gates for the data
lane: refinement & updating, entry validation, organization, trend
graphing, system modelling. Drafted 2026-07-14 from the owner's product
assessment. Status: PLAN, nothing built, nothing promoted. Companion
reference probes (run green 2026-07-14, reference toys, NOT engine code):
`surprise_verdict_probe.py`, `taught_reduction_probe.py`,
`should_vs_can_probe.py`, `failure_commonality_probe.py`.**

*(Transcribed to disk 2026-07-14 from the authoring session's paste;
em-dashes/arrows re-encoded, content verbatim. UPDATE 2026-07-15: all
four probe scripts landed in dc/experiments/ and re-ran GREEN under
PYTHONHASHSEED=0, reproducing the recorded numbers — see the anatomy's
07-14 addendum for the reconciliation.)*

> Owner positioning (2026-07-14): "data refinement and updating, data
> entry, organization, trend graphing and system modelling — i feel like
> isaac would be really good at that." This segment aims the existing
> honesty machinery at that market. The product is TRUST: verdicts,
> receipts, refusals, provenance, supersession — the things no competing
> tool ships. Accuracy leaderboards where GBMs win are explicitly NOT
> the lane; benchmarks below are chosen so the native currency
> (precision, refusal, recovered structure, auditability) is what gets
> scored.

---

## §0 WHAT ALREADY EXISTS (no new build; the lane mostly assembles)

| lane need | existing organ | where |
|---|---|---|
| ingest anything, account for skips | intake (csv/tsv/json/xlsx/docx/zip/folders, skipped-with-why) | isaac_store.intake |
| update without destroying | supersession, confirm/OVERTURN, validate_law HOLDS/DEGRADED/FAILS, restore points | engine + store |
| organization | crystallizer (types, hierarchy, null-gated), senses, structural.analyze (text templates) | engine + store |
| join discovery across tables | triangulate (COMPLETION road: shared key + scrambled-pairing null) | isaac_store.triangulate |
| trend + scope + honest refusal | discover() period roads, lag atoms, law_confidence decay curve, NO RULE | engine |
| system modelling | composition (uptake edges, operable/emergent), wave circles, law families + which_law, residual dossiers | engine |
| entry validation | which_law rank+veto+abstain, lockouts, compare (duplicates), check | engine |
| speak it honestly | report.render_text + learned speech, faithfulness null | isaac_store |
| provenance end to end | findings ledger, packs, Provenance Gate, scrubber | isaac_store |

The genuinely NEW engine work in this segment is ONE organ (§2, the
instrument floor) plus ONE scripted face (§1) plus the benchmark
harness (§3). Everything else is assembly.

---

## §1 DELIVERABLE 1 — `askisaac --audit` (the audit face)

`python askisaac.py <source> --audit [--target col] [--resolution col=sigma ...]`
Same door laws as the existing faces: refusals are answers, no silent
skips, caps checked before reading, access/report content rules per the
Identity Law. Scripted control flow is ACCEPTED for this face (the
askisaac precedent) — the loop is a fixed workflow, not learning; it
migrates to the interpreter when the kernel exists. Judging stays
outside; deciding-how-to-learn is not in this face at all.

### Pipeline stages (each stage's output is a report section)
1. **INGEST & ACCOUNT** — intake walks the source; every table and text
   item listed; every skip with its why; provenance (path, sha, bytes)
   on every item.
2. **FLOOR READING, per numeric column** (needs §2) — instrument
   resolution from three roads: repeats (measured, strongest) > told
   (`--resolution`, usable at once, believed when spread agrees) >
   grain (quantization, LOWER BOUND only). Columns with no evidenced
   floor are marked FLOOR UNEVIDENCED and exactness claims about them
   are refused downstream. The report ASKS for unevidenced resolutions
   (the logical_gaps posture: name the gap, ask).
3. **ORGANIZATION MAP** — crystallizer over rows/columns; types and
   hierarchy with p_chance; structural.analyze on text items; proposed
   grouping of files/tables. Wrong types filed, shown as wrong.
4. **JOIN DISCOVERY** — triangulate alignment scan across all table
   pairs; joins reported with coverage + the scrambled-pairing null
   result; NO ALIGNMENT is reported, not hidden.
5. **LAW PASS, per table** — discover() on declared/inferred targets;
   which_law against the ledger (inherited laws re-validated, never
   trusted on shape alone); trend cards for time-like columns: period
   roads + lag scan + graded confidence + scope + rivals with probes.
   A refusal (NO RULE, quasi-periodic, adequacy diagnosis) is a card
   with the same prominence as a law.
6. **ROW AUDIT** — every row against every applicable law + lockouts +
   duplicate check (compare on row identity). Flags are CLASSIFIED,
   each with its receipt:
   - `ERROR-CANDIDATE` — violates an applicable law beyond the column
     floor; deviation does NOT recur in any structured way.
   - `NEWS-CANDIDATE` — deviation RECURS (the failure-commonality miner,
     §4, names the shared factor): propose law update / new variant via
     the ordinary supersession-duel road. Errors are noise; news is
     structure. The differential decides, never a threshold.
   - `DUPLICATE` — identity by compare, both rows cited.
   - `OUT-OF-DOMAIN` — outside every law's validity (range/guard),
     honestly unvalidatable by laws, so said.
   - `UNVALIDATABLE` — no applicable law exists; counted, never
     silently passed.
7. **THE REMAINDER** — dossier per table: unexplained share, captured
   share, top responsive channels. The audit never claims completeness
   it doesn't have.

### Output contract
Text report rendered ONLY from report fields (faithfulness law; learned
speech where taught, raw report beneath always) + `audit.jsonl` findings
(one line per flag/law/join, ledger-compatible) + exit summary with
complete numbers (rows audited / flagged by class / laws found /
refusals). Every flag traceable to law + binding + floor + row.

### Battery: `isaac_store/test_audit.py` (write FIRST, per discipline)
- A1 planted-error table: known law + N corrupted cells — all flagged
  ERROR-CANDIDATE with correct receipts; complete precision/recall.
- A2 CLEAN table control: false-flag rate reported; must be ~0 at the
  floor's stated rate. THE control — without it A1 means nothing.
- A3 news-vs-error: a recurring deviation (planted regime shift) lands
  NEWS-CANDIDATE with the shared factor named; the one-off lands ERROR.
- A4 duplicates: exact + near (within floor) both caught, receipts cite
  both rows.
- A5 floor behavior: repeats-column floor measured; told floor adopted;
  grain-only column with process noise above grain — flags REFUSED as
  under-evidenced (the honest miss, by design); unevidenced column —
  the ASK appears in the report.
- A6 join discovery: two tables sharing a key — join found past null;
  scrambled — NO ALIGNMENT.
- A7 refusal rendering: a noise table produces a NO RULE audit that
  still accounts for every row.
- A8 door laws: oversized input, garbage file, zip bomb — clean whys.

---

## §2 THE INSTRUMENT FLOOR ORGAN (engine work, small, load-bearing)

New engine methods (names indicative): `read_floor(col)` /
`tell_resolution(col, sigma)`; floor stored on column/law meta with
PROVENANCE (which road, what evidence).
- Road 1 REPEATS: duplicate-X rows; pooled within-group spread; needs
  >=5 groups / >=10 dof (probe numbers; battery to pin).
- Road 2 TOLD: usable immediately; belief measured — flagged when the
  observed spread contradicts it (told-unverified pattern, same as
  tell_law).
- Road 3 GRAIN: quantization step read off values; consistency-checked;
  a LOWER BOUND, never sufficient alone for an exactness stamp when
  residual exceeds it.
- Floor = max of evidenced roads. NO road evidenced — exactness verdicts
  refuse; reports say BEST-RESIDUAL in units.
Wrong-kept to carry in comments (from the 07-14 probes): grain-only
floors under-evidence real process noise — the honest PARTIAL that
results is correct behavior, and the cure is a told/repeats road, not a
looser gate. Nearest-neighbor noise estimators were CONSIDERED AND
REJECTED for v1: gradient contamination inflates them (a floor
estimated too high launders wrong forms back in — r²'s ghost).

### Battery: `experiments/floor_battery.py`
grain read exact on planted quantizations (0.001, 1/16); truncated-CSV
grain honestly coarser; float64 — unevidenced; repeats floor vs planted
sigma; told-vs-spread contradiction flagged; provenance round-trips
through packs.

## §2b THE VERDICT REWRITE (dependency, separately gated)
The surprise verdict (law surprising IN, residual unsurprising OUT,
constants on the coarsest surviving marks, exactness relative to the
floor) is specified by the 07-14 probe with these HARD requirements
proven there: (1) the residual replay must be PARTIAL-CORRELATION /
joint-refit — marginal correlation MISSED the additive hole (wrong-kept,
2026-07-14); (2) the replay is selection-corrected max-over-everything
(the 119/120 dialogue lesson applies); (3) mark snap uses GRIDS of
{1,1/2,1/4}x10^k coarsest-first, and HOLDS earned marks fixed during
subsequent refits (both were probe bugs, wrong-kept); (4) exact-checkable
data (integers/symbols) stamps on machine-zero residual WITHOUT a floor
(Kepler n=8 must survive); (5) full false-alarm control before anything
else counts. r²-as-verdict is then demoted to a reported number and
wrong-kept with the additive hole as exhibit. Gauntlet re-run + the
100-world verdict duel (wrong-form UNDERSTOOD rate, old vs new) +
confidence-curve re-measurement are the promotion gates.
The audit face v1 may ship on current verdicts + floors; B3 below and
the audit's exactness claims get materially stronger after this lands.

---

## §3 DELIVERABLE 2 — the benchmark harness `experiments/dataops_bench/`

INTEGRITY law restated: sklearn/statsmodels run BASELINES ONLY, labeled
BASELINE, never the cognition. All finding/deciding is engine. Planted
worlds run before public data (own truth first, then the world's).
PYTHONHASHSEED=0 everywhere. Every benchmark reports Isaac's number,
the baseline's number, AND the artifact difference (equations, receipts,
refusals vs a bare score).

- **B1 ERROR DETECTION** (the audit's public scoreboard): planted-
  corruption battery first; then public labeled-error sets
  (hospital/flights-style). Metric: cell-level precision/recall/F1 +
  false-flag rate on clean tables. Baselines: z-score/IQR flaggers,
  IsolationForest (BASELINE).
- **B2 IMPUTATION / COMPLETION**: triangulation completion road on
  held-out masked values; metric: error in UNITS vs floor + refusal
  honesty (NO CLOSURE counted as correct where identifiability fails —
  the ICA-limit refusal is a feature, score it as one). Baselines:
  mean/kNN/iterative imputer (BASELINE).
- **B3 SYSTEM IDENTIFICATION** (SINDy-lane): planted difference/ODE
  systems within the atom library (logistic map, damped oscillator via
  lag atoms, predator-prey linearizable forms). Metric: SYMBOLIC
  SOLUTION RATE — recovered the governing form or refused; fit numbers
  secondary. Expect the additive hole to show until §2b lands; COUNT
  it, don't hide it — it is the fix's price tag made visible.
- **B4 TREND / FORECAST**: M4 subset (monthly/quarterly), MASE/sMAPE vs
  naive2 (the competition's own baseline); electricity/demand series;
  then the adversarial pair — RAW RETURNS (expected verdict: NO RULE;
  report the refusal rate as the headline — the world's most expensive
  pure-noise battery) and REALIZED VOLATILITY (clustering structure,
  the lag atoms' home game).
- Predictions filed BEFORE running (so results can surprise honestly):
  B1 competitive (the lane's native game); B2 strong where joins exist,
  honest refusals elsewhere; B3 mid until the additive fix, strong
  after; B4 respectable on seasonal series, behind big statistical
  ensembles on aggregate, alone on refusing returns.

---

## §4 SHARED ORGAN — the failure-commonality miner (small, feeds A3/A6 and Trace C)

From kept receipts (flags, denials, wrongs), name the DIFFERENTIAL
signature: feature=value excess in failures over successes, gated by a
selection-corrected label-shuffle null. Probe-proven 2026-07-14:
planted frontier named exactly (excess .50/.43 vs null .16), lockout
signature named alone (.90 vs .14), random failures — honest nothing,
and the 100%-of-failures background feature correctly NOT named —
commonality is a differential (compare()'s only-in-failures), never a
frequency. Engine home: run over receipt records like any observation
set; conjunctions via the existing confusion-pair/compound move.
NOTE: this same organ is the CASE-CLASS MINTER the interpreter
segment's piecewise supersession needs (organ failure receipts →
named failure class → duel scope). Build once, serves both segments.

---

## §5 ORDER OF WORK (proposed; owner's call)
1. Floor organ + battery (§2) — everything downstream leans on it.
2. Audit face + battery (§1) — ships on current verdicts; first product
   artifact for the lane; also the first real consumer of intake +
   triangulate + report together.
3. Bench harness B1/B2 (§3) — scores the audit publicly.
4. Failure-commonality miner (§4) — upgrades A3, then hands the
   interpreter segment its case-class organ.
5. Verdict rewrite (§2b) + gauntlet/duel/curve gates — then B3/B4.
Standing rules: batteries written before mechanisms; manual + anatomy
updated in the same step as every promotion; account/pack adoption
(already owed) SHOULD land before the audit writes anything into a
living mind.

## §6 HONEST RISKS, NAMED
- Control flow remains caller-side; the audit is a scripted face by
  design. Do not let it quietly become a second interpreter.
- Categorical columns bin badly under the quantile model (covtype
  lesson) — audit v1 restricts law-pass claims to numeric columns and
  SAYS so.
- Public error-detection sets have label quirks; planted worlds are the
  truth anchor, public sets the reality check.
- Floor abuse is the lane's r²-ghost: any pressure to "just estimate a
  floor" when unevidenced must be refused — the ASK is the answer.
- Scale: all-pairs join scans are O(tables^2); cap and account.
