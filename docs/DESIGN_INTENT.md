# DESIGN INTENT — the standing sheet
**Load this first. Every build is checked against this BEFORE it is written.**
(Created 2026-07-05 after the owner had to manually re-inject his own settled
designs — variants, normals, negative structure, all-methods-one-concept —
that the machinery had computed, discarded, or siloed.)

## THE LAW ABOVE THE CHECKLIST (owner, 2026-07-05)
**"There is no separation. Everything is all mixed together. There is no
different thing. Everything should always be universally applied if it
can."** No mechanism is domain-siloed: the readout is not a glyph tool
(it is for ANY channels — covtype jumped +11.4 the day it was applied
there); dynamics is not stroke-only (any path or series); variants are
not digit-only (any pattern class); nevers, normals, duels, ledgers —
if the inputs exist, the mechanism applies. When building or testing
ANYTHING, ask: where else does this apply RIGHT NOW? Then apply it.

## THE USAGE LAW (owner, 2026-07-10)
**"Giving it the language to understand is one thing — bones and
whatever — but telling it how to use them is not. It needs to learn how
to represent ideas using structures that we provide. We need to learn
how to translate something into these ideas, and if the ideas don't
work, we need to figure out what does."** The division of labor:
hand-built = the VOCABULARY (measuring organs: holes, bones, joints,
curves, deltas) + the TRANSLATION (raw thing → the vocabulary's facts)
+ the epistemics (nulls, doors, admission). LEARNED = the USAGE — which
facts and combinations carry identity is decided by Isaac's own
null-gated machinery, never by a hand-written signature or comparison
recipe. A hand-picked signature (e.g. "topology = holes+line-count") is
programming the lesson — the old trap. When the vocabulary cannot say a
difference, the measured residual/confusion IS the discovery signal:
grow the vocabulary, don't hand-wire the usage. (Found 2026-07-10
auditing the glyph stack: every channel's usage was hand-taught.)

## NOMENCLATURE + THE IDENTITY LAW (owner, 2026-07-11, eighth message)
**The roles, named:** **PRIME** = Isaac himself — the full net,
everything (what earlier sections call "core"). **ORCHESTRATOR** =
Prime's sole writer (queue → admission → journal → packs).
**WORKERS** = processing on snapshots; at the leaf, a worker is a
whole all-in-one Isaac with its security net. **SCRUBBERS** = the
strip-identity workers (a first-class role, not just the share path).
**CLIENT SIDE** = the customer/user side: overlays, security nets,
user-held data.

**THE IDENTITY LAW (owner's words):** "we want isaac to understand
the world, but we dont want him to identify people, businesses or
anything like that." Prime learns CONCEPTS AND LAWS, never identity
dossiers. Public-facing information: usable for PROCESSING. Anything
user-submitted: RESERVED client-side and scrubbed of identifiable
information to the best of our abilities before anything crosses.
**No datasets, no user info, no usage patterns ("usage ways") flow to
Prime — ALL personalization is localized on the user's end.** Note
what that last clause covers: even TELEMETRY/usage analytics stays
client-side; Prime's ops ledger describes Prime's own operation, never
user behavior. Enforcement is layered: structural quarantine (tiers) +
scrubbers on every intake path to Prime + an identity-shaped-content
refusal at Prime's admission gate.

## THE INFRASTRUCTURE ARC (owner, 2026-07-11)
Owner declared the next major shift: **persistence, structure
processing, batch processing, API calls, system/operational management,
and partial net loading for responses and processing.** Standing
constraints on all of it: the persistence schema is the Net made
durable — it keeps EVERY measurement, the wrong-section, and
supersession chains (checklist #4/#6 apply to the file format);
partial loading is the reverse index turned toward storage (recall
pages in only the doors a query touches; partial answers must equal
full answers or the delta is reported); ledgers are the ops organ too
(ops events append like findings); performance is graded against the
owner's ~3 s single-core trainer under a hard compute budget (owner,
2026-07-11), never internal before/after alone; no optimizing before a
measured profile. Full plan + phase batteries:
`isaac_project/INFRASTRUCTURE_ARC_2026-07-11.md`.

**The orchestrator (owner, 2026-07-11, second message):** ONE
orchestrator owns the mind and is the SOLE WRITER. Every other process
(discover jobs, perception/recognition batches, consolidation, API
front-ends) does its own processing on read snapshots ("live pulls as
needed") and routes every update or finished process through the
orchestrator as a QUEUED PROPOSED EDIT. The queue is not a lock
workaround — it is the admission gate made operational: every edit is
a proposal (expand freely), the orchestrator runs the epistemics
(compress by test: nulls, admission, supersession) before anything
touches the Net; rejected edits are wrong-kept with their why.
Conflicts between workers resolve by EXISTING organs: commutative
count increments merge; contradictory claims become RIVALS, never
overwrites. The orchestrator stays THIN — gatekeeper, not thinker;
hand-built stays only the epistemics.

**NO TRADITIONAL DATABASES (owner, 2026-07-11, third message):** owner
has had major scaling problems with SQLite and is averse to ANY
traditional database system. Storage is PLAIN FILES ONLY: append-only
JSONL journal (the findings-ledger organ) + IMMUTABLE indexed pack
snapshots (single file: header + node→offset index + records; loader
reads the tiny index, seeks/mmaps records on demand = partial loading;
published by write-new-then-atomic-rename; a new snapshot SUPERSEDES,
never overwrites — the wisdom laws as a file layout). Immutability is
what makes live pulls safe with zero locking. stdlib only, no
dependencies (the Raspberry-Pi line).

**THE LEARNED SOCIETY (owner, 2026-07-12 — the organizing design):**
"basically this should be designed like a scholastic scientific...
society? like the royal institute of science or whatever." The
system IS a learned society (the Royal Society is the model), and
the existing organs already hold the offices: **CRAWLERS =
ARCHIVISTS** — settled by owner: "the crawler is just a router. it
crawls and builds and navigates the mind web. and it can spool up
and assign things. they are archivists. they manage the
information. they assign workers and scientists to do the work" —
v1 (router + division) ACCEPTED as-is; the assign/spool-up duty
(archivists dispatching workers/scientists to jobs) is their next
organ. **WORKERS** = the laboratory hands; **SCIENTISTS** = the
discover/seeker roles; **SCRUBBERS** = the ethics office; **the
admission gate = peer review**; **the journal = the society's
Proceedings** (append-only, refereed, corrections kept — never
retracted into nothing); **the findings ledger = the publication of
record**; **rivals = open disputes**; **batteries = replication
before acceptance**; **promotion = publication**. Design decisions
should keep consulting this map: when a new mechanism is needed,
ask what office a learned society would give it.

**MIND CRAWLERS (owner, 2026-07-12):** "maybe we need multiple
orchestrators... when one is unable to keep up they divide the
section and have specialized sections they manage and specialize
in, and they can make requests to other orchestrators... a page
file that has the data storage location for their section of the
web and do drive pulls." Prime federates: each crawler = a full
orchestrator (own journal + packs + ops = its PAGE FILE; the lazy
state = its drive pulls) owning a KEY RANGE. When a section
outgrows capacity it DIVIDES at its median key — splits are
journaled events (the lineage is wrong-kept); specialization
emerges from key locality (namespaced keys cluster: law:*, skill:*,
node:glyph:*). Requests between sections route through the range
table (the federation's own page file, an append-only split log).
Admission stays per-crawler — the gate travels with the section.

**CUSTOMER SUBNETS — the privacy quarantine (owner, 2026-07-11, fourth
message; ELEVATED 2026-07-12: "those containers are going to be what
is required for user application" — the tier architecture is THE
substrate for anything user-facing, not one option among many; every
user-application decision builds on Prime → client overlay → leaf
security net):** containerized deployments hold LOCAL SUBNETS that are
customer-specific and NEVER feed back to Isaac — not used for
education or any other purpose; identifiable information lives there
and ONLY there. The isolation is STRUCTURAL, not filtered: the core
net is a read-only layer in the customer container; all customer
writes go to the customer's own overlay (own journal + own packs, own
orchestrator); the core orchestrator's queue is simply not reachable
from customer containers. Sync is ONE-WAY, core → customer (the fork
organ made persistent: a private branch that tracks upstream core
snapshots and can never push).
**The share path (owner, 2026-07-11, fifth message):** whether an
overlay discovery ever reaches core is UP TO THE CUSTOMER — opt-in
share setting. If share is on: the discovery is sent to the core
orchestrator TO BE EVALUATED, which routes it to a dedicated SCRUBBER
WORKER that finds and strips ALL identifiable information and keeps
only the general abstraction details (the equation/relation/door
structure and measured stats — never rows, never names, never literal
customer values). Only the scrubbed abstraction enters the edit queue
for normal admission (nulls, rivals). Shares land in a QUARANTINE
INTAKE, never the Net; raw submissions are NOT retained core-side —
what is kept is the abstraction + a scrub report (categories/counts
stripped, not content; wrong-kept applies to the decision record,
never to PII). If the scrubber cannot cleanly separate abstraction
from identity, the share is REFUSED back to the customer — refusal is
an answer. Default with share off: no path at all.

**THE PROVENANCE GATE (owner, 2026-07-12): "if its something that can
be reconstructed exclusively from isaac source nodes, its game. if
it requires any user nodes it should be banned."** The shareability
criterion is ANCESTRY, not appearance: knowledge whose derivation
closure is Prime-only may leave the container; knowledge whose
closure touches ANY user node is banned from export (banned from
EXPORT, not from USE — it stays fully usable inside the leaf).
Fail-closed: unknown provenance counts as user. Every node carries
its source tiers (prime/client/user); derived things inherit the
UNION of their inputs' tiers (generalization through Isaac nodes
with learned forms from user data = user in the closure = banned).
Order of defenses: Provenance Gate FIRST (structural), scrubber
second (content), Prime's identity_gate last (backstop). The
criterion is LITERAL and testable: exportable things must actually
rebuild identically in a prime-only leaf.
**The recreation check (owner, same message): "specifically it
should see if it can recreate the information from public sources
too."** Recorded provenance is not the final word: a banned
(user-provenance) piece of knowledge gets an active RECREATION
ATTEMPT from prime/public-held sources alone — if the same knowledge
(form + constants) rebuilds without the user data, the user data was
NOT necessary, the provenance upgrades, and export unlocks. User
tier bans only what genuinely CANNOT exist without the user.

**WORKER CACHING (owner, same message; interval SETTLED by owner
2026-07-11 sixth message):** workers live-load anything from the net,
keep it CACHED LOCALLY, and operate on the cache; **recheck FIXED at
30 minutes** — owner's reasoning: "really it would be the worker that
is doing the updating, not the net" — workers are the update
producers, so they are never surprised by their own edits, and the
net between contributions moves slowly. Owner's law: **"the longer
isaac runs the less anything should be updated."** Recheck = replay
the journal tail past the worker's watermark (cheap, shrinks as Isaac
matures). Standing companions (undisputed): a worker PINS one version
per job (rechecks between jobs, never mid-job — consistency beats
freshness) and staleness cannot corrupt because ADMISSION is the
arbiter (a stale proposal is rejected + wrong-kept at the gate).
Superseded rival, kept: assistant's three-layer design (fast
watermark heartbeat + delta refresh + 30-min backstop; per-node
churn-driven policy) — revisit only if a measured staleness cost ever
bites.

**SECURITY NETS (owner, 2026-07-11, seventh message — "custom
security nets"):** USER-side specific nets, one tier below customer
subnets: information stored and processed WITH Isaac but pullable
ONLY from the worker holding it — never from anywhere else; processed,
learned-from, and OUTPUT to the user, but never stored upstream or
shared. The worker acts as its own second orchestrator over its own
local net — equivalently, it IS "the older version of Isaac": a
classic all-in-one instance living at the leaf. THE RECURSION: core →
customer overlay → worker security net is ONE mechanism at three
scales (the sheet's no-separation law made literal). Spec points:
reads LAYER one-way (local ∪ customer ∪ core; local wins; shared
tiers can never read local); writes have NO upstream channel
structurally (the local mini-orchestrator's queue goes nowhere);
partial loading is what makes the leaf cheap (pull only the shared
nodes a question touches, door private evidence onto them locally);
two persistence modes — EPHEMERAL (RAM-only, evaporates at session
end) or USER-HELD (persisted only on the user's side, encrypted, key
user-side); **logging is a leak channel**: ops events from a
security-net worker carry counts/timing ONLY, never content.

**SKILLS — THE WORKER MODEL (owner, 2026-07-12, ninth message):**
"the scrubber is just a specialized skill, but it belongs to prime.
all information any worker will do is just prime, but its a specific
checkbox of things... its learned things and preloaded structures and
you just pull and access that directly for the net to be able to
process." ROLES ARE LOADOUTS, NOT SPECIES: every worker IS Prime with
a checkbox of skills loaded. A skill = a named record in Prime's net
(`skill:<name>`, learned things + preloaded structures) pulled
through the SAME partial-loading/caching path as any node — no
separate machinery. Educating Prime updates the skill record
(supersession); workers pick it up on their recheck; a pinned job
keeps its loadout until the job boundary. The scrubber's pattern
vocabulary is the first skill record; hand-coded module defaults are
only the SEED Prime is educated with.

**THE ACCOUNT MODEL (owner, 2026-07-12):** API access = account id +
SESSION ACTIVATION KEY, auto-renewed hourly (rotating short-lived
keys); one auth path serves both the website GUI (the main door,
likely routed on/through AWS) and direct API users. Users get
CONCURRENT processing (their container's worker fleet) and LOCAL
processing (the leaf/user-held road). Account storage with upload
size limits. **PLAN TIERS ARE STORAGE-BASED, NOT COMPUTE-BASED**
(base 1 GB, next 5 GB, ...) **and each level up grants +1 worker.**
Rationale fit: Isaac's compute is cheap by design (the mission), so
storage is the honest marginal cost — sell what costs; metering
stays content-free (bytes and counts, the ops discipline). Security
backend owned by build: pbkdf2 password hashing (stdlib), rotating
session keys (grace-period on rotation), constant-time compares,
login rate-limits, upload caps enforced at the API door
(Content-Length before body read), TLS at the proxy layer, account
PII in ONE separate ops-side store no net can reach.

**THE RESTORE-POINT CACHE (owner, 2026-07-12):** per-customer
retention setting — DEFAULT = "latest version" keeping **3
supersession layers at any time** (the newest 3 pack snapshots +
the journal tail spanning them: 3 restore points, bounded storage);
OPTION = "full log" (nothing ever pruned). Restore is an APPEND, not
a rewrite: rewinding to a restore point is itself a journaled event
(history is never falsified; in full-log mode even the rewind's
before-state survives). Nuance vs wrong-kept: knowledge and its
defeats live IN the current pack (wisdom is cheap bytes); what the
default prunes is redundant SNAPSHOT COPIES — customer storage
economics, owner-settled.

**THE SEEKER (owner, 2026-07-12, public-intake design settled):**
"it acts like a search agent... does a quick web crawl for a few
sources, chews on the information, then gives its best answer." A
worker whose ENTIRE LIFETIME IS ONE QUESTION — no curiosity law
intact (the task arrives from outside; it never invents its own next
task). Per task: search (budgeted provider) → fetch K sources
DEPTH-ZERO (links are never followed — no recursion exists) → chew =
cross-source corroboration with nulls (a claim wants ≥2 independent
sources; agreement/disagreement measured) → best answer WITH
receipts (sources, hashes, support counts) or a REFUSAL with the
dossier (conflict/insufficiency stated). Budgets are physical: max
sources/bytes/time in the task record; exhaustion = clean stop.
Everything it learns is PUBLIC-tier provenance → exportable through
the Provenance Gate; scrubber still runs on intake (public ≠
identity-free). Real-web search backend = an owner dependency call
(API key vs none); the mechanism is provider-pluggable.

**SPEECH IS LEARNED OR IT IS NOT SPEECH (owner, 2026-07-12, the
correction):** "well then it doesnt speak now does it? its all or
nothing. you dont get to choose. that is called programming and
thats not what isaac is about." The template realizer (speech.py v1,
hand-written phrase table) is NOT Isaac speaking — it is my English,
programmed; DEMOTED to scaffold, wrong-kept with this why. The usage
law applied to language: hand-built = the word vocabulary's
DELIVERY (placeholder translation NAME/VALUE/R2, assembly order,
admission nulls, the faithfulness null); LEARNED = WHICH WORDS
EXPRESS WHICH STRUCTURES, from paired examples, through Isaac's own
evidence machinery (co-occurrence past a permutation null; fragments
stored as knowledge in the net; persists via packs). ALL OR NOTHING:
an untaught structure gets SILENCE and the raw report — never a
hand-coded phrase. The proof standard: the wording must exist in the
TRAINING CORPUS ONLY (grep the code for the words — absent); swap
the corpus and the speech changes; withhold training and he cannot
say it.

**THE TRANSLATION LAYER (owner, 2026-07-12 — road 2 v1 BUILT same day;
v1 DEMOTED same day, see the correction above):** "what is
reported vs what actually gets responded need to be different. we
need a translation layer. either an llm, or we need to train isaac
on how to speak english." The REPORT (internal: complete, technical,
verdict/accounting/provenance) and the RESPONSE (user-facing plain
language) are separate artifacts. Two roads, per the standing Omega
design: (a) an LLM as MOUTH ONLY — mouth-with-faithfulness-null:
it may rephrase, it may NEVER originate or alter a verdict, number,
or equation; a faithfulness check compares every claim in the
response against the report and refuses/falls back to the raw
report on any mismatch; (b) native gated English — grow Isaac's own
speech (the interrogate() road already produces gated-English
enumeration; this is its extension, pairs with the learned-scrubber
research thread). Either road, the report remains the ground truth
attached beneath every response.

**LOCAL AI CONVERSATIONS — FOR LEARNING AND TRAINING (owner,
2026-07-12, corrected same day: "not quite my tempo. i meant for
learning and training"):** a small LOCAL model (1.5B–7B,
llama.cpp/ollama class — dependency call open) as Isaac's SPARRING
PARTNER, not a product mouth. This is World GM for language: a
cheap, local, endless conversation environment Isaac practices in
and learns FROM. The model's output is DATA — untrusted intake to
be null-gated, never truth, never verdict (drink the firehose;
the nulls compress). Uses: (1) harvest paired examples so the
speech corpus GROWS from conversation instead of hand-written
lessons (fragments still face permutation-null admission); (2)
generate adversarial identity-laced text = training data for the
LEARNED SCRUBBER thread; (3) conversational practice — Isaac asks,
observes, extracts usage regularities with his own machinery.
Local = nothing leaves the machine. Budgeted like every
environment (the GM pattern: interaction costs budget; sessions
end).

**MULTICYCLE STRUCTURAL PATTERNING (owner, 2026-07-12):** "basically
a flowlogic chart... find the atoms of different things, then go
through the cycle to select the constraints that he can set and
output the pattern type that satisfies those constraints." The
general structural road (and the text road's engine): (1) ATOMS of
the thing (tokens/events/items — vocabulary per modality, as
always); (2) THE CYCLE measures constraint families, each behind its
own shuffle null — always-follows (determinism), forks (A then B or
C, never D), periodicity, balanced pairs (nesting), certified
never-follows (negatives first-class); constraints Isaac CAN SET =
the ones that pass; (3) the PATTERN TYPE is whatever satisfies the
admitted constraint set — chain / cycle / branch (the flow chart) /
hierarchy / repeat — or NO STRUCTURE as an honest refusal; the
output carries the chart itself (nodes + admitted links). (4)
MULTICYCLE: admitted patterns COLLAPSE into higher atoms and the
cycle runs again — patterns of patterns, the tower (this is the
metastructure/D1 thread given its mechanism). Reuse note: this is
discover()'s shape pointed at structure instead of quantity.

**INCOMPLETE INFORMATION ACROSS DATASETS (owner, 2026-07-12 — TODO,
a research thread):** "variable x that is explored in a different
dataset entirely, and it is only through comparing a and b datasets
together that you can resolve it. where they are both halves of the
same whole, but not contained in any single domain." Triangulation
as an engine capability. Canonical examples (assistant-supplied):
parallax (two viewpoints resolve the depth neither sees);
Eratosthenes (shadow angle in one city + distance between cities =
the Earth's circumference, in neither dataset alone); two laws with
a shared unknown (A: y=x·a up to scale, B: y=x+b up to offset —
identified only jointly). Mechanism sketch on existing organs: (1)
the MISSING-VARIABLE SHADOW in A is already detected (adequacy
diagnosis + residual dossier) — the new move is hypothesizing the
shadow LIVES in B; (2) the alignment problem (shared key / time /
entity — or distribution-level registration when no key; the
comparison-as-registration theory is the theory of exactly this);
(3) joint resolution: x = what is CONSISTENT WITH BOTH (constraint
intersection; laws-run-backward; Understanding-as-Closure says it
plainly — x is in the closure of A∪B but of neither alone); (4) THE
NULL: permute the pairing between A and B — a real resolution dies
under scrambled alignment, a fake one survives. Battery when built:
plant x across two synthetic datasets, neither sufficient, jointly
exact; scrambled-pairing kill; refusal when no alignment exists.

**THE LEARNED SCRUBBER (owner, 2026-07-12 — TODO, its own research
thread soon, NOT now):** "we will have to train the scrubber... teach
it what counts as personal or not and generalize the information."
The regex scrubber (isaac_store/scrubber.py, 19/19) is the v1
VOCABULARY; the real scrubber LEARNS the personal/not-personal
boundary and GENERALIZES content (identity → the abstraction it
carries) with Isaac's own machinery — the usage law applied to
privacy: hand-built = pattern vocabulary + epistemics, LEARNED =
which content carries identity. Battery when built: measured strip
rate, refusal calibration, generalization utility. Until then the
three layers stand (structural quarantine + regex scrubber + gate).

**WORKING NETS (owner, 2026-07-11):** the full net will be BIG
(size unknown); working nets must be kept SMALL ENOUGH BUT CAPABLE
ENOUGH. Deployment is the compress stroke: working-set extraction =
task closure × measured usage/evidence, with the information_ledger
reporting what capability was kept vs left behind, in complete numbers
("this N-MB working net keeps X% of the full net on task Y").

## NO PRESET FREQUENCIES (owner, 2026-07-12, tenth message)
**"Preset cos and sin and stuff is just bad. its not that
complicated. you can look for periodicity and periodic periodicity.
if its a multiple that should be easy to tell by the pattern. if its
closer to something it will deviate slower than if it was farther.
it just needs to try and bracket and refine the answer."** A
frequency inside sin/cos/cosh is a MEASUREMENT, not a menu choice
(checklist #3 applied to atoms). The mechanism: BRACKET (coarse scan
proposes the neighborhood — the beat rate says how close: near-truth
mismatch deviates slowly, far mismatch thrashes) then REFINE (walk
the frequency until the fit stops improving). Found 2026-07-12 when
the frame duel suggested m_jj's blocker was the atom grid.
**VERIFIED SAME DAY (mjj_identity_probe): the mechanism ALREADY
EXISTS and works** — "the grid proposes, the refine pass sharpens"
(hill-climb on every admitted term's k): on planted truth the engine
said the invariant-mass law y²-frame UNDERSTOOD r²=0.9996, walking
1.5 → 1.026 ≈ 1. The real-HIGGS m_jj refusal was a MISSING-VARIABLE
SHADOW (textbook formula itself maxes corr 0.24 on the stored
columns — per-column standardization + mass computed from 4-vector
info absent from the features): the refusal was Isaac being RIGHT.
This law stands as the standing principle for any future atom
family; revisit the coarse refine ladder only if a case shows it
stalling (no optimizing before measured limits).
**MEASURED QUALIFICATION (2026-07-12, lag battery):** bracket+refine
requires a GRADIENT — near-truth must deviate slower than far. Smooth
parameter families (frequencies, decays) have one. INTEGER ALIGNMENT
against an iid driver does NOT: an off-by-one lag carries zero signal
(k=40 planted between ladder anchors 29/41 → refusal, wrong-kept).
Where every candidate is cheap to measure exactly (FFT
cross-correlation scores ALL lags at once), exact full measurement
replaces bracketing — measuring everything is not a preset menu.

## GENERATION, NOT DUPLICATION (owner, 2026-07-12, the FizzBuzz
## correction): "he didnt learn it. you fed him a pattern and he had
## to mimic it. thats not generation, thats duplication."
**TOLD RULES:** "what i want is to say if its a 3 say fizz, if its a
5, say buzz, if its both say fizzbuzz, and if its neither increment
the number. i want him to be able to understand that kind of thing."
The capability is UNDERSTANDING AN INSTRUCTION: the rule is TOLD
(conditions -> utterances over the number line), Isaac builds the
executable understanding and GENERATES the behavior having seen ZERO
examples of the output. Precedence is his own general logic (the most
specific satisfied condition wins; unresolvable overlap = refusal),
never task-ordered by hand. Told rules follow the told-knowledge law:
usable at once, belief only from data (validate against an observed
stream), supersession duel against example-discovered laws. The
example-mimicry road (learn_responses) is DEMOTED to duel partner /
fallback-when-untold — wrong-kept with this why. Both roads must door
onto the SAME concept nodes (a discovered period-3 comb and a told
"multiple of 3" are one concept).

## NUMBER STRUCTURES — TAUGHT ROUNDING (owner, 2026-07-12, settled
## in three steps): first "if it looks or is close to a whole number,
## it should go to that whole number and check it just outright";
## then the general form: **"i think we just need to teach it
## rounding actually. if its 3.0018463 then its probably tested to
## 3. if its 1.764964 then it may be 1.75 etc."**
A measured constant's ROUNDINGS are hypotheses tested OUTRIGHT: from
its magnitude, candidates at the natural ruler marks ({1, 1/2, 1/4}
x powers of ten — note 1.75 is a mark), COARSEST FIRST; the simplest
that does not lose (>= the measured value's score) is adopted; if
every rounding loses, the measured digits stand — no invented
simplicity, no lost precision. The whole number is the coarsest mark.
STRICTLY POST-HOC, per the owner's phrasing ("its probably TESTED to
3"): measure precisely first, round after, with the sharpest referee
— the trial refit at fit end (_round_terms), on every admitted
term's inside-parameter. Wrong-kept x2 en route: (a) assistant's
digit-by-digit search-walk (rounding is not searching); (b) rounding
at PROPOSAL time — the fold referee cannot resolve 3.6 vs 3.5904
(inside its bin width), and a lucky adoption injected slightly-wrong
atoms that admission smeared into two-atom surrogates (measured:
planted 1.75 said [1.7525, 1.7]; post-hoc-only says [1.75]). On
integer-like axes, integer periods are still tested DIRECTLY by
residue classes (group by n mod P) — exact, cheap, no spectral
machinery. Divisibility ("every Pth") is a NAMED vocabulary concept,
and snapped discoveries become legible as it. Battery:
rounding_battery.py 7/7 (1.5 said, 1.75 said, exp(-0.4) said, pi
KEEPS its digits, noise still refuses).

## TOLD KNOWLEDGE = A SUPERSESSION TEST CANDIDATE (owner, 2026-07-12)
"If you just give it the equations directly, can it use them...
maybe it could go through and check if the submitted thing applies
or matches any and it can be listed as a supersession test candidate
or something." The design: direct knowledge is WELCOME but earns its
place. `tell_law(name, equation)` accepts an equation in Isaac's own
canonical vocabulary → (1) MATCH CHECK first: same-form as an
existing law → filed as a confirming witness on that law, never a
duplicate node (all methods, one concept); (2) else it enters as
TOLD-UNVERIFIED — usable immediately (apply works), but carrying NO
belief: law_confidence stays None until DATA arrives (belief is
measured, never told — a told law has no ranges/edge-r² until
validated); (3) when data arrives, the SUPERSESSION DUEL: the told
law vs a fresh discovery on the same data, judged held-out — winner
active, loser wrong-kept wearing its numbers (losing challenger
files into the rivals list; superseded told laws keep provenance +
defeat). Retention is the ordinary pack road: told laws persist and
resume like any knowledge.
**LAW FAMILIES (owner's overlap question, same day):** same form +
same constants = witness; same form + DIFFERENT constants = a
VARIANT — a sibling law doored under one `lawform:` parent (Earth /
Jupiter / Pluto gravity; hierarchy law applied to laws, never
smushed). `which_law(X, y)` resolves overlapping confusion by rank +
veto + abstention: clear winner names itself, near-ties are
AMBIGUOUS with the shortlist, nothing-fits is NONE = a new-variant
candidate (mixed-planet data REFUSES a single-planet answer;
battery: gravity_family_battery.py 13/13).

## The reuse checklist — ask these before writing ANY new mechanism
1. **Which existing organ already does this?** (Check §capabilities below.
   The answer is usually "one of them, turned toward a new input.")
2. **Does the new evidence DOOR ONTO EXISTING NODES?** New channels are new
   door tags on the same concepts — never a parallel system, never a rival
   classifier. All methods, one concept.
3. **Is every quantity MEASURED, not hand-told?** Thresholds → tests.
   Weights → calibration on held-out data. Tolerances → measured spreads.
4. **Does it KEEP its measurements?** If a number was computed for a gate
   (a spread, a residual, a null bar), it is KNOWLEDGE — store it on the
   node. Never compute-and-discard. (The bone-normals lesson.)
5. **Does it have a null?** Expansion proposes freely; compression is the
   null. Never restrict intake — improve the gate.
6. **Does it keep its wrong?** Failures filed with the why; supersession,
   never overwrite; losers wear their defeat. Applies to types, senses,
   lockouts, patterns, fixes, AND the project record itself.
7. **Does it honor hierarchy?** Subgroups are real things under parents
   (abc/abd): styles, senses, variants. NEVER smush by averaging across
   genuinely different sub-things.
8. **Are negatives first-class?** What a thing NEVER shows (past a binomial
   null) is a certified not_ door; candidates violating one are VETOED.
   "It is this or this, but never that."
9. **Identity = relations; pose = a report.** Scale structure over absolute
   scale; rel-angles, ratios, signatures. Tilt/scale/position are stated
   separately, never baked into identity.
10. **Output = rank + veto + abstention.** A shortlist with certified
    nevers beats a forced single answer; a shrug with a diagnosis beats a
    guess.

## The laws (owner's words, all in engine)
- "The less you do, the more you let Isaac do" — self-assembly over
  hand-taught structure; hand-built stays ONLY the epistemics.
- "Knowing what is right is intelligence. Knowing what is wrong is wisdom."
- "Simpler with the same accuracy is better" — a PREFERENCE, not a gate.
- Signed deltas always (darkening ≠ brightening).
- No optimizing before measured limits; no importance-telling.
- Expand, compress, expand, compress (the Intellon rhythm).
- Settle design disputes by BATTERY, not argument.
- **Everything relative; absolute is one correction factor** (owner,
  2026-07-05). Compute in relative space — ratios, signed deltas,
  fractional rates: robust, calibration-free. Any absolute value =
  relative value × ONE factor from a single known anchor (a size, a
  distance, a speed), applied LAST — never baked into the structure.
  Multiple anchors must resolve to the SAME factor (a null); a wrong
  factor scales all absolutes uniformly and leaves every relative
  relationship exact (the graceful failure). Generalizes #9 — the
  relation is the identity, scale is a separate report. (Measured:
  relative range 0.15% vs absolute 18% on the looming test — the error
  lived entirely in an early scale bake-in.)

## Reporting rules (hard)
- **COMPLETE numbers only**: accuracy against the WHOLE task; coverage
  multiplied through ("74% of the 31/200 answered" = 11.5%); perfect on one
  digit of ten = 10%.
- No padding, no "beats chance/baseline" dressing on a low number.
- Plain "% correct", never bare R²/ARI/jargon.

## Current capabilities (one line each; full detail in ISAAC_MANUAL.md)
- **Substrate**: Net (nodes/tagged doors/meta/counts, reverse-indexed);
  compare atom; Scratch; World; findings ledger; save/load/fork.
- **Discovery**: discover() (null-gated enumerator, block-perm null
  with per-block rolls — phase-blindness cured 2026-07-12; THREE
  period roads: integer-residue outright check / DFT comb / fold,
  whole-number snap, none refereeing another; LAG ATOMS —
  2026-07-12 causality cure: every integer lag FFT-measured, shift-null
  gated, x0[t-k] named, history-less rows refuse — one power dial,
  open op family, accounting=100%, residual dossiers, adequacy);
  TOLD RULES: tell_rule/generate_by_rule (generation from told
  understanding, zero examples; most-specific-wins precedence;
  validate_rule = belief from data); learn_responses/respond =
  the example road, demoted to duel partner (owner correction).
  rivals/confirm/refine/apply_law/validate_law; graded confidence
  (measured decay); capture→interrogate→graduate; composites minted+reused.
- **Consolidation**: crystallizer (admission TESTS, wrong-kept, hierarchy
  between sound types, divergent doors self-assemble); senses-as-nodes;
  waves (groups/handoffs→UPTAKE EDGES/circles/clock/statuses); lockouts
  evidence-weighted + revisable.
- **Composition**: parts/offers/assemble/operable/emergent — wholes with
  arrangement; whole_as_part composes upward.
- **Perception**: observe_spatial (locked/bounded/parts/hinges, 2D→3D lift
  behind trigger + rank-cliff null); stitch_views; complete_symmetry;
  describe_shape (rings/discs/frames/rects/lines, squish, joints, tilt vs
  rel-angle); skeleton bones (keypoints_structural); path_dynamics
  (curve/accel/jerk: line/arc/circle/spiral/s-curve); learn_pattern
  (+VARIANTS per style, per-bone NORMALS kept); compound doors behind
  ceiling trigger.
- **Recognition**: learn_glyphs/recognize_glyph — ALL channels door onto
  the same concept nodes (density, topology, bones, dynamics, exemplars,
  RENDER — owner 2026-07-10: "just print and overlay the nearest font
  number"; attach_symbol_forms puts rendered symbol templates on the
  concept, symbol:<c> -names-> concept:<c> closes polysemy inbound, and
  overlay_delta speaks the signed leftover = expect→subtract→delta,
  D9's vision face; render alone 100% on never-seen fonts, fused
  printed 86→92, handwritten 95.4→95.6);
  measured channel weights; pair judges; shortlist tournament; certified
  NEVERS veto; readable votes. information_ledger (said/caught/reachable/
  ceiling + where). train_readout/extract_readout: ONE softmax layer over
  node outputs as the comparator, extracted LOSSLESSLY into signed
  evidence equations (linear = the net IS the equation).
- **Interaction**: interaction_map (signed affects+/- graph, null-gated,
  noise refuses) + explain_link (translation factors: a link that DIES
  under stratum-matched conditioning is a CHAIN; near-threshold discrete
  terminal hops named PREEMPTIVE SIGNALS — the fireworks law). Identity
  includes the effect profile. STILL OPEN from the owner's same message:
  metastructure crystallization (components→humanity→civilization — the
  D1 tower), edges-of-things (boundary finding), interaction-as-identity
  recursed to every level.
- **Trust**: calibration audit; law_confidence (measured decay curve);
  0/20 false discoveries on noise; refusals are answers.

## Where things stand (complete numbers, 2026-07-09)
MNIST fused **95.0–95.2** (trained+extracted readout over node outputs;
hand-calibrated 92.2; pixel-softmax 86.0) | truth-in-shortlist ~97–98 |
covtype 59.1 | HIGGS classify **71.18 / AUC 0.7886** (higgs_pairs.py:
1D signals + 220 pair doors admitted by interaction excess, printable
softmax; 1D-only 68.07/0.7479; eqn road: transverse mass SAID; deep-net
0.885 NOT matched) | CIFAR 32.6 (needs texture percepts) | clocks 22.9
(pixel bridge open) | Kepler/planted laws EXACT.

## Standing next-lever list
Full training data (free) → self-assembled patch-percept retina (CIFAR's
door type) → per-variant duels → captures as ledger witnesses +
interrogation at scale → effect entities (D9, the engineer's core) →
SRBench (the differentiated lane).


