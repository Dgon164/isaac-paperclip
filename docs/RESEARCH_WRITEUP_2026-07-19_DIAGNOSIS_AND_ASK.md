# The Diagnosis Court and the Ask Road — 2026-07-19 (afternoon)

## What the owner asked for

The observation that started the session: every campaign keeps
reaching the same kind of ending. Isaac works until he hits a
wall, the wall turns out to be ONE missing critical skill, and a
human diagnoses it and explains it to him. The last one was the
desync law (his model of the git repo drifting out of sync with
the repo itself). The owner's ask: he needs the ability to
identify these holes and ask for help — or think them through
himself.

Two design statements were dictated and filed verbatim in
DESIGN_INTENT.md:

1. **INTERNAL MODELLING** (the umbrella name): "internal
   modelling is what ive been trying to say with shapes and
   theory of mind and stuff. being able to model current and
   potential states of something."

2. **DIAGNOSIS — EVALUATING BACKWARD** (the correction that
   became the build): "really its being able to model the cause
   and effect of failure modes. there is an expected state, what
   is different between the expected state and the current state
   that is preventing this from working. its evaluating backward
   ... there are only so many variables to adjust ... if you are
   diagnosing an engine, you are under the understanding of the
   fire triangle, but with an engine you need air, spark, fuel,
   and compression. and you can check each state directly."

## The evidence that this is THE pattern

Before building, a sweep of both repos' docs enumerated every
historical wall of this kind — seventeen of them, from the
binding wall of June ("three unrelated-looking plateaus, one
missing primitive") through the vocabulary wall, the judge's
additive hole, the Kung Pow correction bug, the Bookbot
authoring wall, the dict-accumulation textbook hole, and the
desync law. Five properties recur:

1. The failure is FLAT in effort — more data, more retries, more
   time change nothing (a data wall improves with volume; a
   skill wall does not).
2. Failures cluster in one nameable class while neighbors stay
   green.
3. The hole lives at the generative layer (a proposer, a
   vocabulary, a state model) — the courts stay honest inside
   the vocabulary they were handed.
4. The decisive diagnostic is INJECTION: hand-feed the suspected
   missing piece and the whole cluster goes green at once.
5. The cure grows vocabulary THROUGH the unchanged court, and
   the old failure is kept as a permanent gate.

Historically the diagnosis came three ways: owner insight in
plain English, deliberate measurement/ablation, and — twice, on
speech — Isaac's own miners. The mission of this build: make the
third mode general.

## What was built (isaac_store/diagnosis.py, battery 10/10)

**The requirements model.** Derived from the grader's own
published checks — never hand-coded per lesson. Each check names
an expected state; the command that courts it names the variable
kind it reads (a log, a file, a config key, the status report).
The menu of variables is finite and each one is directly
checkable — the owner's engine metaphor, literally.

**The backward walk.** Court the structure. If red: court every
variable at its own instrument, compare expected against
current. The differing ones are the suspects, each with a
receipt.

**The cause-and-effect menu.** Each variable kind carries its
transfer — the act that moves it:
- a told fence that names the file, followed by its contents
  (TOLD-FILE);
- a told fence that captures output into the wanted path
  (CAPTURE), with two dataflow moves: a `*-command-here`
  placeholder takes the neighboring fence's command, and a
  `<hash>` slot is resolved by ASKING THE REPO
  (`git rev-parse HEAD`) — operational access, never a guess;
- a commit as the transfer that grows the log (his tense
  tracker's own candidate→past move), its message dimensioned by
  the court's OWN expected fragment (COMPOSE-COMMIT);
- a config write in the COURT'S OWN SCOPE (CONFIG-SET).

Suspects adjust in causal order — files before the commits that
store them. Adjust one variable, re-court: the injection
diagnostic. Every line is vetted against the allowlist AFTER its
placeholders resolve (a placeholder is only judgeable once it is
a command).

**The fire-triangle clause.** When every known variable checks
green and the structure still fails, the requirements model
itself is missing a variable. That residue is a NAMED UNKNOWN —
never a repair (a verifier never repairs what it checks). It
opens the ask road.

**The ask road.** Two sources, both null-gated:
- the ledger mine: darks featurized from their own bug text and
  mined against the passes (mine_commonality's shuffled-label
  null) — no scream, no ask;
- the residue ask: a dark whose told road references an
  artifact from outside the lesson, or a suspect no told road
  moves, files `ask:<name>` — future tense, status OPEN, zero
  belief, evidence attached, superseded never erased. Kin to the
  goal tree's dark leaves: "a dark leaf is an answer."

## What happened live (the receipts)

The seven standing Learn Git darks were flown twice.

**First flight (before the cause-and-effect menu): 0 cured — but
every backward walk was correct.** Second Commit's suspect was
exactly "log contains 'B:' — current log holds only A:". And the
Git Config walk exposed a contradiction: my merged-scope probe
saw `ceo=ThePrimeagen` while the court's instrument did not. The
court reads `git config list --local`; the readme's own fence
teaches `git config set --global`. The key sat in the wrong
scope. **The scope is a variable his model did not hold — a
real fourth variable found by the organ's own tension report,**
exactly the fire-triangle story. It became battery check DX8.

**Second flight (menu in place): 5 of 7 cured, server-graded.**
- Cat File — CAPTURE: `catfile-command-here` filled with the
  neighbor fence's `git cat-file -p <hash>`, hash asked of his
  own repo. PASSED.
- Second Commit — COMPOSE-COMMIT carrying the court's own `B:`.
  PASSED.
- Storing Data — two TOLD-FILEs written (quotes/), then the
  `C:` commit; causal order held. PASSED.
- Git Config — CONFIG-SET in the court's own local scope.
  PASSED.
- Get — no adjustment at all: **cured transitively** by Git
  Config's fix. The backward walk found the bench already green
  and submitted. PASSED.

Learn Git: **10/44 → 15/44 CLI lessons passed.**

**The two survivors name ONE hole, and he filed it himself.**
Both darks (The Object File, Trees and Blobs) need an artifact
discovered in a PREVIOUS lesson (`path/to/file/from-before`;
the blob's own hash). His first two self-generated asks are now
in his account:

- `ask:lesson:The Object File` — "the told road references
  ['path/to/file/from-before'] — artifact(s) from a previous
  lesson I do not hold (cross-lesson memory)"
- `ask:lesson:Trees and Blobs` — "no told road moves
  file:/tmp/blobfile.txt — the transfer is not in the lesson's
  text or not in my menu"

The ledger miner, correctly, went quiet after the cures (the
remaining two darks share their features with now-cured passes,
so nothing clears the null) — the residue asks carried the
signal instead. Honest silence plus a named hole beats a forced
signature.

## The build's own bugs, kept with their diagnoses

- The battery first ran its commands on the wrong interpreter
  (cmd.exe vs bash) — cascade of five false reds; cured by
  running bash explicitly with MSYS_NO_PATHCONV=1.
- The one-character ghost: the donor filter rejected commands
  containing `>` — but the slot syntax `<hash>` carries a `>` of
  its own. Redirection is now judged on a slot-stripped copy.
- The battery's first ask-mine plant (3 darks of 8 records)
  could not beat the selection-corrected null — the 119/120
  lesson applying to the battery itself; re-planted at 6 of 18.
- A kwarg collision in ask_report (record_finding owns `kind`).

## What this means

The walls history shows the project's arc: diagnosis by owner
insight → diagnosis by measurement → diagnosis by his own
machinery. Speech crossed that line twice (length=short,
question-shaped prompts). Today CODE AND STATE crossed it: the
same evening the owner said "evaluating backward" in English,
the organ walked seven real failures backward, cured five with
the lessons' own told materials, and converted the residue into
named, evidenced, future-tense asks — one of which is the next
missing skill (cross-lesson artifact memory), identified by him
rather than by us.

The wall grew 60 → 62 (composer, tense) → 63 (diagnosis) the
same day.

## Open doors, in order

1. **Answer his asks** (the telling road is the sanctioned
   intake): design cross-lesson artifact memory — what a lesson
   DISCOVERS (paths, hashes) landing as study-ledger artifacts
   the next lesson's roads can resolve against. This also cures
   `path/to/file/from-before`.
2. README-order tense-tracked full flight for the remaining CLI
   lessons (29 of 44 outstanding: 15 passed).
3. The ask-answering loop end-to-end: owner answers an ask in
   English → telling road lands it told-unverified → the road
   re-flies → the ask closes by supersession with the answer
   cited.
4. The one-ontology migration (queued from the morning).
5. Engine-side who-stamps at intake; speech-corpus audit;
   pickle hardening (standing from the audit).
