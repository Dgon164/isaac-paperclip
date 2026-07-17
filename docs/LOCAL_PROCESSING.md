# LOCAL PROCESSING — running dc long-term on your own machines
*(2026-07-15, testing-segment session. dc-only doc; survives
promotion — copy_tree never deletes dc-only files.)*

## Per-machine setup (PC and laptop, once each)
```
git clone <repo> && cd dc            # or git pull on an existing clone
pip install -r requirements.txt      # numpy, scikit-learn
```
- Python >= 3.12 required for `isaac_store/test_intake.py` (PEP 701
  f-string at :62 — the only 3.12-only file; everything else runs on
  3.11).
- Windows: `set PYTHONUTF8=1` (README law).
- Batteries/probes: always `PYTHONHASHSEED=0` (hash-seed sensitivity
  at the crystallizer stage, 07-13 hygiene note).
- On boxes with <= 8 cores, pin BLAS before multicore work:
  `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`
  — measured on a 4-core container: unpinned, 4 workers ran 3x
  SLOWER than 1 (0.31x); pinned, 3.39x speedup, and the 1-worker
  baseline is unchanged (Isaac's small-matrix numpy never used BLAS
  threads anyway). The web-session hook does this automatically;
  locally it's on you.

## Long-term processing, reachable from anywhere
- **Primary: the desktop runs the work; you steer from any browser.**
  In the repo folder on the desktop: `claude remote-control` — the
  session appears at claude.ai/code (and the mobile app) from any
  device. Requirements: machine on, network up (a drop >10 min ends
  the session); claude.ai subscription auth. Server mode exists for
  several concurrent sessions.
- **Fallback: web sandbox sessions** (repo-only work; 4-core
  container; no account, no ollama, no interpreter package).
- **Bridge: git is the only artery.** Code and docs travel by
  commit/push/pull. `claude --teleport <session-id>` pulls a cloud
  session (conversation + branch) into a local terminal.
- **The account never travels by git.** `isaac_home` (journal, packs,
  session history) stays on the desktop with ollama. If it must ever
  move: explicit copy of the latest pack + journal (packs are
  immutable snapshots — that is the supported shape), never a sync
  tool, never the repo.

## Processing time — what is already built, what is owed
The owner's question (2026-07-15): "if it only pulls from the net
what is used, and doesn't flush in between, that should help — is it
already doing that?" ANSWER: at the store layer, YES, built and
battery-proven:
- **Packs pull only what is used**: records are fetched by seek on
  demand (pack.py — the index seeks straight to any single record;
  measured 0.04 ms for one node vs 5.3 s full load at 100k nodes).
- **Nothing flushes in between**: LiveCache rechecks are DELTAS, not
  reloads (journal tail past the last cursor), invalidation touches
  ONLY the keys the delta named, and a pinned job never rechecks at
  all ("consistency beats freshness", cache.py).
- **The engine loads once per process**: a live mind is in-RAM;
  worker.py loads the engine once per worker and reuses it across
  jobs. Long-lived workers, not process-per-job, is the intended
  shape for batch work.

## EFFICIENCY TODO (the optimization pass, when its turn comes)
Named debts, all previously recorded, none new — collected here so
the pass has a work order:
1. **Crystallizer scaling** — O(n^2) by design, measured worse
   (O(n^3)-O(n^4) with the get_predecessors full scan; knee at ~800
   nodes). Carried suspect since 07-03; the reverse-index promotion
   (66x at language scale) cured the inner scan for language — the
   general organ still owes it. The single biggest engine hot spot.
   **OWNER DESIGN (2026-07-15, on the sheet): tiered working sets —
   "keep different sets of cache... quick access nodes, chunked
   recall nodes, and swapping between them; do 100 ops, then the
   next 100, and you don't do an 800x800x800 check."** Sharpened to
   the dirty-set rule: a pair needs re-checking ONLY if a member
   changed since the last pass (LiveCache's delta discipline moved
   inside the engine) — cold x cold unchanged pairs are skipped,
   not deferred; recency (L1 ~100 hot nodes) is the index of where
   new work can exist; L2 warm chunks run as batched consolidation
   (idle-time work); L3 = the pack's seek-on-demand (built). Two
   battery obligations before any port: EQUIVALENCE (tiered vs full
   crystallizer -> byte-identical nets; scheduling must never change
   epistemics) and COMPLETENESS (a hot change that makes a cold x
   cold merge newly true must still be found — dirtying propagates
   through the reverse index; planted world required).
   **OWNER REFINEMENT (same day): hierarchical block pruning —
   "you do 100x100, then you do 8x8; you do the 100x100 chunks as a
   single."** Within-chunk exact work + chunk-vs-chunk as single
   units, descending into a cross-block only when the chunk-level
   check cannot rule it out. 800^2=640k checks -> 8*100^2 + 8^2
   ~ 80k (~8x); recursed, ~n log n (the Barnes-Hut shape). SOUNDNESS
   CONDITION (what makes pruning provable, not heuristic): the chunk
   signature must be a conservative OVER-approximation of its
   members (e.g. union of member doors) — empty signature overlap
   then PROVES no member pair can pass min_shared, so the skipped
   block is proof-backed; the coarse pass only rules out, never
   decides. Isaac-native framing: a chunk-as-single is a COMPOSITE —
   the crystallizer indexing with its own hierarchy, groups before
   members. Composed with the dirty-set rule: dirty nodes -> dirty
   chunks -> incremental signature update -> 8x8 only on dirty
   rows/cols -> descend survivors; clean x clean blocks untouched.
   **OWNER REFINEMENT 2 (same day): significance-weighted sampled
   descent — "if you really really need, do say 20 from each group
   identified as significant; maybe 30 from the first, 5 from the
   second, 25 from the third."** LAW BOUNDARY, said out loud: tiers
   0-1 are PROOFS (lossless), sampling is EVIDENCE (lossy) — two
   sanctioned uses only: (a) TRIAGE, lossless — sampled merge-density
   estimates ORDER the full descents, never replace them; (b)
   BUDGETED ANSWER — the sampled pass carries the order_matters
   badge shape ("no counterexample in N sampled pairs — absence,
   not proof"), stamps its coverage (never a silent pass; unexplored
   remainder counted, audit charter), and queues the remainder for
   idle consolidation which finishes it EXACTLY — sampling moves
   WHEN full truth arrives, never WHETHER. Weights are measured,
   not hand-set (tests-over-thresholds): signature-overlap mass,
   dirty fraction, recent merge YIELD per chunk (use-counter shape).
   The stack, top to bottom: 0 dirty-set (proof) / 1 block
   signatures (proof) / 2 full descent, hot+small blocks (exact) /
   3 weighted samples, cold+big blocks (evidence, badged,
   remainder -> consolidation). Foveated attention for the
   crystallizer: periphery samples, fovea resolves, and the
   periphery never pretends to be the fovea.
   **OWNER REFINEMENT 3 (same day): the PREGROUPING layer at
   ingestion — "an initial scan, just stick like with like; pregroup
   the groups of 100 as needed... you don't need to always compare a
   with b: figure out what a is, what b is, then compare the final
   interpretation of a vs b with a few specific examples for
   refinement."** This answers where the chunks COME FROM: not
   arbitrary blocks but likeness buckets from a cheap single-pass
   coarse-signature scan at intake (O(n log n), no pairwise work) —
   manufacturing the locality every tier below exploits (dense merge
   yield within, provably-empty blocks across). LAW: pregrouping is
   a SCHEDULING HYPOTHESIS, never a verdict — sloppy grouping costs
   time, not truth, because the proof tiers still check everything
   signatures cannot rule out; the equivalence battery stays
   passable by construction. The two-level comparison in native
   vocabulary: within-group crystallize (the group's interpretation
   IS its crystal, earned through the ordinary nulls at n~100);
   across groups compare CRYSTALS not members; refinement = tier-3
   samples aimed by the crystal comparison; a group merge is an
   ordinary supersession with receipts. DRIFT GUARD (build in from
   day one): membership is provisional — an item that fits its own
   group's crystal poorly is re-bucketed and re-judged (the owner's
   "swapping"); membership is a supersedable claim with evidence.
   Precedents, named: record-linkage BLOCKING; pre-attentive
   perceptual grouping (like-with-like before recognition).
   **OWNER REFINEMENT 4 (same day, in processing with another
   session): OUTLIER EJECTION — "rather than trying to force
   something in, if it doesn't fit, it doesn't fit. mark it as
   outlier. if it's kind of like a but doesn't fit a, and it
   definitely is not b, it could be c. maybe c is a superset of a
   and something else."** Absorption-of-misfits is the same failure
   shape the campaign measured at the verdict tier (plant-absorbed
   laws, additive impostors); ejection is the cure at group level.
   Three obligations: (1) outlier is a VERDICT WITH A RECEIPT (what
   it failed in A, what ruled out B, distances in the group's own
   currency) — the receipt is the evidence C will be minted from;
   (2) the pile is a NURSERY, MINED not stored: mine_commonality
   over outlier receipts periodically — a shared differential
   signature past the null MINTS C (frontier-miner self-assembly,
   aimed at ingestion); audit charter applies — outliers counted,
   never silently passed, and a pile that only grows is itself a
   finding; (3) C-as-superset is the proven C2b lattice move
   (penguin: excluded from the subgroup, retained by the parent) —
   exclusion without destruction, parent minted from what the
   receipts say the ejected DO share, through the ordinary p_chance
   gates. Payoff: ejection keeps crystals SHARP, which makes the
   crystal-vs-crystal tier more decisive — honesty and speed are
   the same policy here.
2. **_capture broadcast** — O(n^2 * d), unconditional, runs up to
   TWICE per discover() since accounting added a residual capture.
   Optimization queued 07-03.
3. **Engine module exec** — importing isaac.py execs a 426KB module
   (~seconds). Fine per worker, wasteful per job. Batch runners
   should hold minds, not respawn them.
4. **BLAS pinning locally** — see setup above; already automatic on
   the web.
5. (New, cheap, from the reservoir probe) the CaptureMeter
   factorizations cache per fold — the same pattern would serve any
   repeated-null organ.
Discipline note: this is a MEASURE-FIRST pass — profile the gauntlet,
fix the top item, re-run the gauntlet, keep the numbers. No
speculative rewrites; the promotion law applies (research-first).

## Long-run hygiene (learned 2026-07-15, first overnight on the 14900K)
The wall you hit on a long run may be COMMIT, not RAM: Windows fails
allocations when total committed (RAM + pagefile) hits its limit even
with physical memory free (observed: 38.7 GB in use, commit 138/144,
python innocent at ~350 MB). Checklist before/during overnight runs:
- Task Manager -> Details -> add the "Commit size" column (default
  view hides commit gluttons with small working sets).
- Known bystander leakers OFF the compute box: Logitech G HUB
  (observed 12 GB committed; CEF app, chronic leak — kill
  lghub*.exe or replace with Onboard Memory Manager).
- Commit unattributed to any process -> RAMMap Use Counts: Shareable
  (leaked pagefile-backed sections), Driver Locked (VM balloon),
  Nonpaged Pool (driver leak; poolmon names the tag).
- If WSL is in the stack: Vmmem hoards the Linux page cache —
  cap it in .wslconfig ([wsl2] memory=16GB, [experimental]
  autoMemoryReclaim=gradual); `wsl --shutdown` reclaims now.
- ollama parks models resident: `ollama ps` / `ollama stop <model>`.
- A ballooned pagefile stays ballooned until reboot; reboot once
  after clearing the leaker, then watch Committed hourly during the
  next run to catch any grower in the act.
- Isaac-side law stands: long-lived workers, never process-per-job
  (a spawn-per-item loop shows up as a swarm of small-commit
  pythons — that one IS ours to fix if ever observed).
- MEASURED CLEAN BASELINE (14900k box, 2026-07-15, post-purge
  reboot): 16 GB in use / 20 GB committed. That is the ruler: check
  Committed before and during overnight runs — sustained growth
  without a matching process commit means the leaker (or a new one)
  is back. The 07-15 incident peaked at 138 GB committed with the
  compute stack measured innocent (~1-2 GB total); the cure was
  removal, not RAM.

## Efficiency pass #1 (2026-07-15 night, measure-first as specced)
TRIGGER: the mechanisms promotion priced discover() at ~8.8s/call
(max 24s) at n=400 d=5 — ~4x the wordless port. PROFILE (cProfile,
one representative call): 19.0s total, of which _exact_road 17.7s =
621,021 lstsq calls — the exact road's k>=2 combinations exploded
when the shortlist seat guarantees (top-16 + ALL pure-var terms +
creases, ~85 seats at d=5) fed combinations() directly. FIX (top item
only): k=1 still sweeps every seated candidate; k>=2 combos run over
a bounded diverse subpool (top-16 deduped + best-12 pure-var +
creases, <=~38 -> ~9k fits); deep k>=4 pool is pure-var-first, capped
24. MEASURED AFTER: the same call 19.0s -> 1.41s (13.5x), same
verdict, same equation to the digit. WRONG-KEPT from the first
re-gate: the naive cap cut the pure-var SINGLES out of the deep pool
(high-corr products crowd them — the crowding disease's FIFTH
sighting, this time inside the efficiency fix itself; blended B3 fell
0/2). Cure: singles are guaranteed BY CONSTRUCTION (only d of them),
products compete for the remaining seats. GATES RE-RUN after both
fixes: mechanisms battery, outlier battery, 100-world duel, engine
self-test (results in the build-state entry). Next candidates if a
second pass is ever warranted (measured, not assumed): A_ho built
twice per discover (exact road + replay); the pool meter's 200
permutations at large n; step-atom count in the enumerator scans.
