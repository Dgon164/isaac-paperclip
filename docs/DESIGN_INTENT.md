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

## THE LANGUAGE CORRECTION LOOP (owner, 2026-07-12): "the thing with
## language is you cannot mathematically review it, and you cannot
## get proper testing feedback. i think what we need to look for is
## content words and ideas. talk or say something, check for a
## response, and correct him on what he should have said if he
## failed, or correct him on what he should have said better if he
## passed."
Language has no held-out residual — CORRECTION is the error signal.
The loop: Isaac speaks in context → a tutor judges → FAIL brings the
should-have-said, PASS brings the better version. The correction is
TOLD KNOWLEDGE (usable at once; belief from recurrence); the wrong
utterance is KEPT WITH its correction (wisdom applied to speech;
re-failing a corrected context supersedes the correction). Focus on
CONTENT WORDS AND IDEAS, not surface: content-ness is MEASURED, not
listed — function words are precisely the words whose contexts carry
no identity (the excess/ubiquity law, fourth appearance). Standing
constraint from the owner: the destination is Isaac "working
entirely within structures and connections" — the correction loop
teaches USE of structures, not more strings; NLTK-style external
linguistics failed before and is not the road ("something about the
design itself that we need to resolve").

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

## FLOW STRUCTURES — metainformation about the information (owner,
## 2026-07-15): "we build something, and then it just doesnt get
## used. it should at least be present, and or checked if it is
## necessary or bypassed. but it just doesnt even consider it...
## how do we create flow processes, and how can isaac modify or
## branch them to be applicable? this is structural and will still
## be nodes and doors, but it will be different than the content."
The recurring wound, named at Isaac's level (this sheet itself exists
because settled designs kept getting silently dropped — same disease,
human scale). THE THREE MISSING THINGS behind every unused tool:
(1) PRESENCE — tools live as Python functions with no node in the
net, invisible to any scan; (2) CONSIDERATION — nothing enumerates
"which of my tools apply here?", and unuse leaves no trace; (3)
ADAPTATION — even a considered flow cannot branch on evidence.
THE DESIGN: flows are NET CONTENT in their own namespace (flow:/
step: nodes; doors carry next-step and branch conditions; steps
point at organ/tool nodes) — same substrate as content, different
altitude: these nodes are read by the KERNEL LOOP to decide what
happens next. THE CONSIDERATION LAW: at every juncture, every
registered step whose domain overlaps the situation is SCANNED and
either FIRES or is BYPASSED WITH A RECEIPT (why-class + count;
silent unconsideration is outlawed — bypass receipts are cheap,
absence of consideration is the expensive thing). ADAPTATION BY THE
EXISTING LAWS: steps carry use/outcome receipts and face the same
recent-window ELECTIONS as words (2026-07-15 precedent); a flow that
keeps losing gets mined (the commonality organ) and the named
condition IS the branch point — BRANCHING A FLOW = PIECEWISE
SUPERSESSION AT THE FLOW LEVEL (clone the step for the named case,
duel decides, loser kept). New tools door themselves in by declaring
when-tags (the affordance-index move: a thing entering the net
announces its operators) — an unregistered tool is a visible defect,
a registered one is either used or wearing bypass receipts.
REGISTRATION RULE, standing: every new tool ships WITH its flow node.
This is the interpreter segment's true shape: the kernel loop is the
flow executor; the package's affordance scan is the consideration
law's mechanism. First build: ONE real pipeline (the drill session or
the audit face) as flow nodes + a walker with bypass receipts + one
evidence-driven branch demonstrated end to end.
THE EXECUTION CYCLE (owner refinement, 2026-07-15 night, after the
basic-mechanisms probe): "essentially the flow structures would be
internal processing, code, as well as routing pointers. do op, take
result door, or return to main program. each node can act like a
function generator." Pinned as the interpreter's execution model:
each step = DO OP (the node fires its operation) -> TAKE RESULT DOOR
(the result's properties choose the outgoing door — the comparison
booleans ARE the routing predicates, so a conditional is just which
door the result takes; a door walked is an if executed) -> or RETURN
TO MAIN (the kernel loop regains control — one simple loop, check
the net). NODES AS FUNCTION GENERATORS: a node can emit new callable
behavior — smallest form: a node with bound context (partial
application); grown form: a repeatedly-winning CHAIN reified as one
new node (chunking = a minted function; flows become ordinary
vocabulary and face elections like everything else — the genesis
loop applied to PROCESS). The mechanism receipts already built
(larger routes through compare, replayable) are the seed of the
execution trace; the consideration law governs every hop.

## WHEN ORDER MATTERS — additive vs subtractive (owner theory,
## 2026-07-15): "with plus it doesnt matter, but with minus or divide
## it does. so what i think i just figured out is additive does not
## matter, but subtractive methods are. so with language and these
## other examples they are restricting the space and as such count as
## subtractive."
The owner's conjecture, kept with its sharpening: ADDITIVE
(accumulating) operations are order-free — plus, times, max, union:
the slots are INTERCHANGEABLE. SUBTRACTIVE operations are
order-sensitive — minus, divide, power: the slots carry DIFFERENT
ROLES (the taker vs the taken-from), and swapping roles changes the
outcome. Sharpening (assistant, kept honestly): pure restriction as
INTERSECTION actually commutes (filters land in the same place in any
order) — what breaks order in language/code/images is that each
element's restriction DEPENDS ON THE SLOT/STATE it lands in ("dog
bites man" ≠ "man bites dog" for exactly the reason a−b ≠ b−a: agent
and patient are roles; minuend and subtrahend are roles). So the
learnable law: **ORDER MATTERS EXACTLY WHERE THE SLOTS HAVE DIFFERENT
ROLES** — subtraction is the simplest role-asymmetric relation, and
the ABC=D four-slot frame is the general one. NOT told to Isaac:
MEASURED — order_matters(op) probes an operation by swapping operands
(the value-gate move); a violation keeps its WITNESS pair (5-3 vs
3-5) as the receipt; order-freeness is claimed only as "no
counterexample in N probes." Composes with compare_order: one organ
says WHEN two things differ only in position; the other says WHETHER
that difference changes the outcome under the operation at hand —
the same pair can be "same thing" under + and "different things"
under −, the should/can context-indexing applied to order.

## THE TYPO CONCEPT — same thing, different bit string (owner design,
## 2026-07-15): "if they are typos, they should be introduced under a
## different bit string. so word and wrod should generally be
## considered as a typo and just have a door between them connected
## through the typo concept"
A typo is the SAME THING arriving under a DIFFERENT bit string. The
law, at every level: the variant becomes its OWN node (different
bits = different node — never smushed, never overwritten), with a
DOOR to what it is a variant of, and the door goes THROUGH the typo
concept — the connection itself says "mis-entry", with the evidence
on it (closeness in the thing's own currency + the consensus that
makes one form canonical and the other the slip). Two teeth,
everywhere it applies: (1) the variant must NEVER be allowed to
rewrite the RULER — the consensus reads the measure, the dissenter
gets filed; (2) the filed dissenter is a FLAG CANDIDATE with its
correction attached (the door points at what it probably meant).
Instances: text — word↔wrod through typo (closeness = edit
distance + shared contexts, earned not told; language lane, not yet
built); numbers — an off-grid value ↔ its nearest grid value through
mis-entry (built into the grain road 2026-07-15: one half-step slip
used to RESCALE the ruler 2x down and four slips used to blind it;
now the consensus keeps the ruler and the slips are filed with their
nearest-grid door). Same family as group-level outlier ejection
(the nursery) — eject from the measurement, file in the record,
point the door at the likely intent.

## MEANINGFUL DOORS — the relationship as a third pointer (owner
## idea, 2026-07-15): "you have a pointer door. a to b. but what if
## you had something else. a,b:relationship where relationship is
## effectively a third pointer for the type of connection between
## them. give the connection actual meaning that can be interpreted
## and used as structure or math or something. 3,8:add5"
STATUS: DESIGN CAPTURED, not built — assess against existing organs
first (reuse checklist). What exists already: doors carry TAGS
(net.door_tags), some tags name relations (names→, typo would be
one); laws/rules are nodes. What the owner adds that is NEW: the
relationship label should itself be a NODE — a third pointer — whose
meaning is INTERPRETABLE AND EXECUTABLE: 3,8:add5 means the door
from 3 to 8 IS "+5", and +5 is a thing you can (a) verify (3+5=8 —
the door can be CHECKED, a door that fails its own meaning is a
flag), (b) apply elsewhere (10 →add5→ 15 — the door generalizes),
(c) compose (add5 then add3 = add8 — door algebra), (d) MINE (many
(a,b) pairs → discover() names the relation — relations are laws
living on edges, minted through the ordinary nulls). The typo door
is the first citizen of this family (a,b:typo); add5 is the numeric
one; the interaction_map's signed affects± edges and the uptake
edges are earlier instances that never got the general form. This
turns the net's wiring from "connected" into "connected HOW" — and
because the how is a node, it gets doors, receipts, supersession,
and duels like everything else. First probe shape when its turn
comes: mint add5 from pairs past a scrambled-pairing null, verify /
apply / compose, and let a wrong claimed relation be CAUGHT by its
own execution.

## THE BOOKS MUST BALANCE — ECC for data (owner design, 2026-07-15):
## "you have the inputs and the outputs. 5+5=9. you dont know if 9
## was wrong, or if one of the 5s was supposed to be a 4, but you
## know something here is incorrect. and even if he cant resolve it,
## he can mark it as false and return to it maybe. if you have a data
## table with 40,000 inputs and they dont add up at the end, then
## someone somewhere did something wrong."
BUILT same day (cross_check in engine, crosscheck_battery 9/9,
promotion #9). The laws: a failing check marks the TUPLE false —
never the output alone (the audit used to blame the answer cell;
this design corrected that); candidate repairs are the typo
concept's doors (cell → the value that balances the books), PROPOSED
with receipts, NEVER silently applied; overlapping checks localize
like parity bits — row totals × column totals intersect at the bad
cell (the Hamming/ECC move; correction capacity = one error per
tangle, more errors are DETECTED and refused); an unresolvable
violation is FALSE-SOMEWHERE, kept OPEN and RETURNABLE — a later
check can resolve it by supersession (5+5=9 alone has three suspects;
add a+2=6 and a=4 is the unique repair of both); a grand total that
fails certifies an error EXISTS even when nothing can say where —
batch parity catches what per-item checks cannot (the measured 2x
detectability wall has a hole punched in it at the batch level);
floors gate tolerance — noise-level imbalance is not a finding.
NEXT RUNG, named: wire into the audit face (askisaac --audit gains
totals checks); relation-shaped checks beyond sums ride the
MEANINGFUL DOORS design (a check IS a relation door executed).

## INTERPRETED, NOT IMPLEMENTED — the front door's immune system
## (owner design, 2026-07-15): "if its something where we have a
## known answer, vs the received answer, then he can check. so he can
## check incoming grammar and math and stuff based off of what he
## expects and assess whether its right or not. if he determines its
## wrong, he can still acknowledge the assumed intent and continue
## but doesnt learn the assumed flaw for integration. bad english is
## interpreted, but not implemented."
BUILT same day (vet_intake in engine, vet_intake_battery 6/6,
promotion #10). The law: UNDERSTANDING AND ADOPTION ARE SPLIT.
Incoming claims are checked against what he already expects (known
answers; sums via cross_check; his own learned rules when the wiring
lands). A claim that fails his check is INTERPRETED — assumed intent
recorded as typo-concept doors to the likely-meant value, so the
conversation continues — but integrate=False: the flawed form NEVER
reaches learning. Quarantine is wrong-kept, not deletion: original
verbatim + why + intent persist at quarantine:<name>, supersedable.
No expectation = UNCHECKABLE = the ordinary nulls road (never a free
pass, never a quarantine). WHY THIS MATTERS HERE: the account
poisoning entered exactly through this door (bad tutor output was
LEARNED); the word elections made bad adoptions reversible — this is
the PREVENTIVE twin. NEXT RUNG, named (owner's call — it touches the
live practice loop): wire the gate into sparring/practice so partner
and tutor lines are vetted against HIS OWN learned expectations
before banking — bad english interpreted for meaning, never banked
into the corpus; composes with the value gate (convention vs
truth-claim) and tutor-format refusals already standing.

## THE REPRESENTATION ENGINE — what Isaac IS (owner keystone,
## 2026-07-15): "isaac is a representation engine. i finally figured
## it out. the whole goal is information is represented, it is
## processed in some way in which it can represent something else,
## repeat adnauseum. we are just finding different ways to represent
## that info."
THE KEYSTONE — and it was latent in the owner's own 2026-07-05
correction ("we don't care what or where or how the information is
sorted, we only care that the information is represented"). It
unifies every organ on this sheet as ONE MOVE repeated: numbers →
equations; sentences → concepts-with-doors; a seen shape → identity
+ pose; a group → its crystal (compare crystals, not members); parts
→ wholes → parts of bigger wholes (repeat ad nauseam is already in
the engine); a typo → two representations of one intent, doored; a
relationship → itself a node (MEANINGFUL DOORS); a total → a
redundant representation of its parts (why cross_check catches
lies); intake → received-representation vs expected-representation.
And the deepest instance: HIS OWN METHODS are represented in the
same medium as his knowledge (every function a node) — a method that
is represented can be examined, duelled, and superseded like any
other information, which is what makes self-learning possible; a
method that lives only in code cannot (the anatomy's headline wound,
explained). Sharpening (assistant's, offered not settled): all
computing re-represents — what distinguishes Isaac is that his
representations are READABLE, EVIDENCED, and SUPERSEDABLE — every
one carries its receipts (evidence, nulls, floors, provenance,
supersession); a net's representations are mute, Isaac's can be
interrogated (the no-black-boxes law restated as the theory). What
the frame directs next: the verdict rewrite = choosing between rival
representations by surprise relocation (a good law-representation
soaks up the surprise and leaves the residual boring); MEANINGFUL
DOORS = representing the transformations BETWEEN representations;
the interpreter = representing PROCESS itself.

## THE REPRESENTATION DUEL — the keystone as a mechanism (owner,
## 2026-07-15, immediately after the keystone): "is this something we
## can design and integrate as a result? testing different methods
## for isaac to represent information and picking the best one for
## the format?"
STATUS: DESIGN CAPTURED, build on owner go. Isaac tests rival
representations of the same information and elects winners — BEST IS
PURPOSE-RELATIVE, never absolute: the same table's equation wins for
prediction, exemplars for exact recall, the matrix form for speed,
doors for explanation-with-receipts; so the organ keeps a PORTFOLIO
with measured badges per format (the should/can context-indexing +
order_matters badge shape), losers KEPT (variants-not-smushing),
champions re-electable out when they start losing (word-elections
machinery generalized). A candidate proves itself by: FIDELITY —
regenerate the represented thing within the floor (the
generation-not-duplication law IS the test); COST — size and time,
measured, complete numbers; REACH — what it newly represents
(unseen-row prediction, transfer); RECEIPTS — readable and
evidenced, or it fails the house law regardless of score. When a
task arrives, candidate representations are consulted or bypassed
WITH RECEIPTS (consideration law applied to representations; they
register like tools). PRECEDENTS, all hand-run — the design makes
Isaac run the contest himself (= the mission: self-learning includes
learning improved methods): box→matrix 17,000x (matrix_context_demo);
recognition channels with measured weights (five representations of
one digit); word elections (rival forms re-elected by outcomes).
First build slice when called: one dataset, 3-4 candidate
representations (raw exemplars / discovered equation / matrix form /
crystal summary), measured on regenerate-vs-floor, bytes, query
time, unseen-row transfer; badges minted per purpose with witnesses;
battery pins that no single "global best" is ever claimed.

## THE GENESIS LOOP — how he BUILDS representations that didn't
## exist (owner, 2026-07-15, third step of the keystone arc): "but
## how does he build and design a new kind of representation? build
## a new structure that didnt exist before? instead of us finding
## all the edge detection and patterns, he builds the systems to
## find each individual pattern and is able to represent it
## internally. he kind of did this with shapes and corners before,
## but we want it to work with any concepts."
STATUS: DESIGN CAPTURED, the segment beyond the interpreter; first
demonstration specced below. The recipe, extracted from every
minting he has ALREADY done (composites via capture→interrogate→
graduate; the collective common-mode axis; self-proposed lag
columns; crystallizer types; the outlier nursery minting C):
  1. A STRUCTURED LEFTOVER — current vocabulary fails and the
     failure rhymes (not noise). The RESERVOIR is the trigger organ:
     it detects that a residual HAS structure before any grammar for
     it exists ("the difference that makes a difference").
  2. INTERROGATE in his own currency — where it lives, which
     channels, joint or marginal, through what combination, what
     survives scrambling (nulls throughout).
  3. MINT the failure's invariant as a NEW NODE of one of his
     structural kinds (composite / axis / group / transform / lag /
     relation-door / percept).
  4. DUEL — the mint must explain what old vocabulary could not and
     lose nothing elsewhere (piecewise supersession, loser kept).
  5. REUSE — the minted node becomes ordinary vocabulary and the
     NEXT level's raw material (the keystone's "repeat ad nauseam":
     each level's leftover is the next level's alphabet).
The frontier habit chooses WHERE genesis aims (what keeps failing);
the consideration law guarantees minted representations get
consulted; every mint ships with its node (registration rule).
THE HONEST LADDER (say it, never overclaim): new instances (done) →
new combinations (done: graduate) → new axes/groups (done in spots)
→ NEW STRUCTURAL KINDS (open research — the signal for a needed new
kind is a miner-named failure class that no composition of existing
kinds clears; not a promised feature).
FIRST DEMONSTRATION, specced: raw pixel-style grids, ZERO pre-built
detectors — predict-each-cell-from-neighbors fails structurally at
contrast lines → miner names the contrast invariant → EDGE minted;
loop climbs: edge-prediction fails at bends → CORNER; corners fail
to close → SHAPE. Success = re-deriving the shapes-and-corners
result with none of our hands; controls: scrambled grids mint
NOTHING, and every mint beats its null. What he did before with our
help, done again with none — the mission sentence as machinery.

### THE POOLS (the reservoir ensemble) — where to dig (owner, same arc,
### 2026-07-15): "the reservoirs could tell him what to look for.
### each one finds different meaning and structure that is a good
### signal, and he can spool up a bunch of resnets [reservoirs] and
### compare what they are finding in the structures and say this
### angle here is important for telling a 7 from a 1, so i will
### integrate and look closer at that specifically"
The genesis loop's step-1 trigger, multiplied. Receipt: the
single-lens version is PROBE-PROVEN (reservoir_surprise_probe
13/13 — channel ablation named exactly {x2} / exactly {x1,x3} where
marginal correlation named NOTHING). The ensemble adds:
(a) AGREEMENT ACROSS INDEPENDENT FROZEN LENSES = a built-in null —
each lens frozen before data (uncapturable ruler), so independent
lenses agreeing on WHERE structure lives is chance-doesn't-repeat
discipline for free; guard kept: many lenses = many chances to
hallucinate, the scrambled control stays mandatory (the 119/120
selection lesson). (b) DISAGREEMENT IS SIGNAL — which lens family
sees it says what KIND of structure it is (scale/locality — a crude
spectroscope). (c) CONTRAST-AIMED ablation = THE DIFFERENTIA ROAD,
domain-general: aim the ensemble at the DIFFERENCE between two
concepts (7 vs 1) and the agreeing lenses name the differentia
candidates (the stroke angle) — feeding the differentia machinery
that until now had no general finder. THE HARD LAW, restated: the
reservoirs POINT, they never answer — what ships is the minted
READABLE node, and the mint must prove itself WITH THE RESERVOIRS
REMOVED (ordinary nulls, regeneration, discrimination on fresh
data); a reservoir that became the deliverable would be a small
mute net — the thing this project exists to not be. Lenses are
scaffolding: they say look here, the loop builds the readable
representation, the scaffolding comes down.
NAMING (owner, 2026-07-15, after the handoff): "i would like to call
them res or rez, but people would not know what that means, but we
just call them pools, or training pools, or kiddie pools for some
levity. a shallow fixed pool to help him learn to swim." POOLS
henceforth in everything new (docs, code, probe names: pool_*); the
already-committed reservoir_surprise_probe.py keeps its name
(promoted history is never hand-edited); "reservoir computing" kept
in parentheses for outside readers. Never "resnet" — that names a
trained deep residual network, the opposite thing. The name carries
the design: SHALLOW (not deep), FIXED (frozen before data — the
13-inch foot), and LEARN TO SWIM (scaffolding: he swims, the pool
never ships).

## THE 13-INCH FOOT — trust flows up from measurements, never down
## from the instrument (owner law, 2026-07-15, closing the keystone
## arc): "bottom line, dont trust the instrument, trust the
## measurements. if they are all wrong, you cant get a correct
## answer, but you can get a correct relationship. a foot that is 13
## inches is useless for building a house, but perfect for measuring
## things."
The epistemics of the whole machine, one sentence: RELATIONSHIPS
SURVIVE BAD RULERS; ABSOLUTES NEED ANCHORS. Instances already
obeying it: Kepler's T = a^1.5 found in arbitrary units (the FORM is
ruler-free, the constant is instrument-relative); cross_check needs
no calibration at all (a ledger measured with any foot must still
sum — balance is pure relationship); registration/comparison-as-
nulling (relations, not absolutes); the affine consensus
recalibration (fixing the foot by internal agreement while the
law's form stands); triangulate's halves road (two instruments'
leftovers agreeing across a join, no shared calibration needed).
AND THE THEORY OF THE RESERVOIR: a frozen random lens is the
ultimate 13-inch foot — uncalibrated, absolutely meaningless,
relationally perfect ("this residual has structure"; "these two
channels contribute differently") — the owner's law is WHY the
instrument is legitimate. The two boundaries the law draws, both
already machinery: (1) THE HOUSE — interfacing with the outside
world (real units, exactness stamps) requires an ANCHOR no internal
cleverness can conjure = the ASK posture ("no ruler, no perfect");
(2) THE FOOT MUST BE CONSISTENTLY 13 — an instrument wrong
DIFFERENTLY each time poisons even relationships, so consistency is
itself MEASURED never assumed (the repeats road + consensus
ejection: the instrument earns its consistency from its own
measurements' agreement, and is refused when it doesn't). Trust the
measurements; make even the instrument earn its keep from them —
the no-importance-telling law in metrology clothes.

COMPLETION (owner, same night): **"absolute is a myth. everything is
relative, including meaning."** This dissolves the boundary's
seeming exception: the HOUSE's anchor is not an absolute either —
a standard foot is a foot everyone AGREED on; building never needed
an absolute ruler, only rulers that agree with each other. So the
ASK asks for the CONVENTION, not for reality — and the value gate
already routes exactly this (convention lesson vs truth claim). And
meaning: the machine embodies it structurally — IDENTITY = RELATIONS
(already law on this sheet; a concept IS its doors); the typo door
works because meaning lives in relations, not letters; the 7 is
partly not-a-1 (contrast constitutive); and the null discipline is
the deepest instance — REAL is defined as beats-its-own-scrambled-
self, realness itself measured relatively. Sharpening (assistant's,
offered): relative ≠ arbitrary — what earns "true" in Isaac is WHAT
SURVIVES across re-representations, scramblings, and disagreeing
instruments; invariance under change of ruler is the only
absolute-like thing there is, and it is built of relations all the
way down.

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



### RECURSIVE POOLS — group and sibling nets (owner, 2026-07-15, the
### arc's next rung): "that's what the matrix was supposed to be but
### it can only represent 2d relations. what if we recursively
### applied these pools to find relational information about the
### structures themselves."
WHY THE MATRIX CAPPED: a matrix IS pairwise relation materialized —
higher-order structure (relations among relations, group-of-groups,
sibling patterns) needs reification + recursion, not bigger tables:
represent the structure as a thing with descriptors (its constants,
its crystal, its doors — the keystone move), and relations among
structures become ordinary channels one level up; pairwise at level
k+1 covers arbitrary order at level k. Pools are LEVEL-AGNOSTIC by
construction (a frozen projection does not know what its channels
mean), so the proven instrument climbs unchanged — only the
world-builder changes. Per-level laws: nulls must be LEVEL-MATCHED
(scramble the episode alignment of descriptors, not raw rows), and
the hard law holds per level (pools point; mints prove themselves
with pools removed).
RECEIPT — probe-proven same day (experiments/pool_relations_probe.py,
10/10, 6.2s): 10 groups x 240 episodes, each group a clean level-0
law y=a_g*x; planted relation a_C = a_A * a_B (product: marginally
invisible). Level 0: 20/20 quiet — the relation does not live in raw
data (exact road first; run-1 wrong-kept: pooling a machine-zero
residual is ill-posed). Level 1: pool screams (+0.536 vs null99
-0.431); ablation names EXACTLY {A,B} of 9 candidates (0.93/1.00 vs
<=0.015, thr 0.103); marginal correlation blind (0.110 vs 0.189);
scrambled alignment quiet AND discover refuses. GENESIS closes with
pools removed: discover() on descriptors mints '+1.00*x0*x1' at
2.2e-15; 12 held-out episodes predicted to 1.8e-15, COMPOSED through
the level-0 law down to raw values. What the matrix could not hold,
found by recursion, named by ablation, minted readable, proven
without the scaffolding. Level 2+ follows by induction: a minted
relation node has descriptors too.

### THE DROP ALGEBRA — junction types from ablation patterns (owner
### framing 2026-07-15: "from an algebra structure this makes
### sense... compare how parts get transformed compared to base to
### see how they abate"; assistant sharpening, now PROBE-SETTLED:
### ablation drops measure NECESSITY, not ownership — and the
### deviation from additivity is itself the diagnostic).
For a contributing pair (i,j): S = d_i + d_j - d_ij (solo drops vs
both-permuted pair drop), judged against decoy band + a CALIBRATED
instrument bias (a planted known-additive pair measures the tanh
channel-mixing bias — 0.0052 of pair scale, measured not hand-set).
S ~ 0 -> ADDITIVE; S >> 0 -> SYNERGY (jointly necessary: each solo
carries the whole signal's death warrant); S << 0 -> REDUNDANCY
(either suffices: solos subadditive, pair drop ~ capture). The
classifier runs BEFORE enumeration and may only inform search ORDER,
never admission (the Fisher law: informers do not judge).
RECEIPT (experiments/pool_drop_algebra_probe.py, 8/8, 9.2s):
additive world S=-0.073 in band ±0.075 -> ADDITIVE, parts named
exactly; synergy world S=+1.452 vs ±0.206 -> SYNERGY, solos 1.49/1.44
on capture 0.914; redundancy world S=-0.435 vs ±0.081 -> REDUNDANCY,
pair 1.566 ~ capture 0.997 over subadditive solos 1.13; 0 false
names; twin visibility measured (solo ablation SAW both twins at
0.05 twin-noise, asymmetrically 0.92/0.21 — the predicted blindness
did not occur at this correlation; tighter twins go on the attack
list). Wrong-kepts in the docstring: run 1's shared-twin world
contamination; the saturation/mixing bias invisible to no-signal
nulls, cured by in-probe calibration.

### E1 — THE BRIDGE TO LANGUAGE, probe-proven (owner question
### 2026-07-15: "how do we test this on non mathematical structures?
### like english?"): pools never worked on math — they worked on
### CHANNELS, and a sentence-event's reading (voice, tense,
### decoration, word seats) is a channel vector the moment features
### become INDICATORS (never ordinals — re-encoding-invariance law).
RECEIPT (experiments/pool_conjunctive_frontier_probe.py, 8/8 x 3
seeds, 11s; seed-sweep arg for big boxes): planted HIDDEN AGREEMENT
rule — fail iff XOR(voice=passive, tense=perfect), 5% verdict noise.
XOR at 50/50 has PERFECTLY FLAT marginals, so mine_commonality
(the frontier habit's own miner, a MARGINAL statistic) is blind BY
THEOREM — measured 3/3 seeds naming nothing. The pool funnel on the
same receipts: screams (+0.64..0.70 vs null ~-0.2), grouped ablation
names exactly {voice, tense} (decoy-feature null), drop algebra
stamps SYNERGY (S ~ +1.2 vs band ~0.08), and articulation collapses
to a 2x2 table read: XOR cells recovered exactly, held-out verdict
accuracy 0.91-0.96 = the noise ceiling — enumeration shrunk from 2^k
to one pair. Agreement control (marginal cause deco=exclaim): BOTH
instruments find it; scrambled verdicts: BOTH quiet; innocents named
0/3 worlds. CONSEQUENCE FOR THE LIVE MIND: conjunctive frontiers in
his practice history are invisible to the current frontier habit;
E3 (desktop, needs the account) = run the pool over his real fat
failure receipts and see what marginal mining never saw. E2 next:
hidden long-range grammar rule via role-indexed lag channels; mint
through the told-rule road; prove by generation, pools removed.

## THE WRITEUP LAW (owner, 2026-07-15: "we need to make sure that we
## are doing thorough writeups and post evals. i want to know what is
## happening in the code, what is being found, what the structures
## look like, this is where we get into the research. what is being
## built and structured that i missed, how is it being represented,
## and how well does it perform or break.")
Every build campaign and every evaluation ends with a RESEARCH
WRITEUP — plain language, internal labels translated, part of the
deliverable, never optional, never just a verdict count:
  1. WHAT WAS BUILT — the mechanism in plain words.
  2. WHAT THE STRUCTURES LOOK LIKE — show the shape itself (a
     sketched table, an example row, the actual equation), not only
     its name.
  3. HOW IT IS REPRESENTED — what form the information takes and
     what receipts it carries.
  4. WHAT WAS FOUND — the findings, complete numbers.
  5. HOW IT PERFORMS AND WHERE IT BREAKS — boundaries and failure
     MECHANISMS explained, not just counted.
Verdict sheets (the strict WORKS/PARTIAL/BROKEN tables) remain; the
writeup is the research narrative on top of them. First instance:
RESEARCH_WRITEUP_2026-07-15_POOLS_AND_VERDICT.md (dc docs).

### THE BASIC MECHANISMS — comparison words + routable tools (owner,
### 2026-07-15 night): "does it have a way to show simple logic
### structures? if a-b is <0 (negative), then b>a? ... im sure there
### is some computer something or other that is simpler than that
### too." And the build order: "hes got tool structures, and we have
### a way to route through other concept nodes and tools, so what if
### we did that? ... adding these basic tools and any other basic
### computer mechanism to his toolkit will be extremely helpful. ill
### leave the implementation and design to your discretion as long
### as it matches the rules."
STATUS: PROBE-PROVEN (basic_mechanisms_probe.py, 12/12, 29s, dc);
PROMOTED 2026-07-15 night (#12 [EXPERIMENTAL]: crease + switch atoms
in the enumerator, thresholds data-proposed on marks and never
refine-glided, deep exact road k<=5 on small data with crease seats,
compare/larger/smaller/switch as receipted organs; battery 8/8, duel
74->2/100 wrong-confident with F5 max ZEROED by vocabulary, self-test
11/11; cost 8.8s/call at n=400 d=5 — efficiency pass queued). One mechanism family,
TWO DIALECTS of the keystone: WORDS for the equation grammar (atoms:
the CREASE |a-b| — max/min become plain algebra, max=(a+b+|a-b|)/2,
the owner's a-b insight with direction dropped; the SWITCH [x>t],
thresholds PROPOSED on ruler marks + deciles, never hand-set — the
ruler discipline applies to thresholds because they are constants;
GATED PRODUCTS [f]*xi*xj for binary channels) and TOOLS that route
(compare/larger/smaller/switch with receipt chains — larger() calls
compare(): the a-b<0 wiring made visible). THE BRIDGE: identity
recognition doors a mint onto its tool node (the minted
0.5*x0+0.5*x1+0.5*|x0-x1| IS larger(x0,x1), verified to 0 on fresh
rows) — two representations of one law, joined. RECEIPTS: the max
world (the eval's one BROKEN) now mints machine-exact in one line;
the step world mints 2*x0 - 1.5*[x1>2] + 1.5*[x1>1] with thresholds
found AT the marks 1 and 2, UNDERSTOOD at the told floor; the
blended conditional's exact 5-term form recovered by the DEEP EXACT
ROAD (held-out rms 3e-15; 0/30 false stamps) after run-2 falsified
greedy assembly (KEPT: the wall is the search, not the vocabulary —
the old judge with the same new words still shipped a confident
impostor). Vocabulary cost MEASURED, not assumed: safety 0/20 false,
availability 20/20 — no toll at these scales. PORT LESSONS filed:
(a) dedupe affine-clone candidates globally (on integer data
[x>6]==[x>6.5]; a binary flag's powers/lags are copies — clones vote
as a bloc and starve real terms out of prefilters); (b) the deep
exact road (k<=5, clone-deduped top-20) joins the port; (c) the
rival-form duel remains the availability cure under noise/poison;
(d) mechanisms register as TOOL NODES under the consideration law at
promotion. HONEST LADDER: hinge, sign, remainder/parity NAMED but
deferred. TODO (owner, same message): MULTI-STEP PROCESSING /
CHAINING — the interpreter segment's kernel-loop half, now explicitly
ordered; routing receipts here are its seed.

### CONTAINERS — world-scoped truth (owner, 2026-07-15 night): "we
### still need to make sure the containers are working. worlds as you
### put it. that certain details or facts change depending on the
### world or situation you put it in. fiction world harry potter has
### different rules than fiction world hail mary."
STATUS: PROBE-PROVEN 8/8 (containers_probe.py, 2026-07-15 night,
<0.1s) — and the mechanism was ALREADY IN THE HOUSE: a container is
a DOOR TAG saying which facts are IN FORCE (add_door(tag='in:world'),
get_door_tags — zero new primitives). One concept node carries every
world's doors (identity=relations; brooms sweep in base and fly in
harry-potter on the SAME node); the active container is routing
state; inheritance is ONE-WAY (fiction overlays base — HP water
still boils at 100C, WITH an inherited-from-base receipt; base never
inherits from fiction = the anti-poisoning wall, measured: base
byte-identical after full fiction ingestion, 0/7 drift, 0/5 leaks
both directions); cross-world difference raises no contradiction
while in-world contradiction still flags (both kept); container-less
facts land in base with a receipt. ENGINE PROMOTION QUEUED: active-
container state on the mind, container= on teach, routing in the
reasoning layer, provenance stamping at intake (vet_intake's door). The ask: facts carry their CONTAINER; the same question
answers differently per ACTIVE world; cross-container disagreement is
NOT contradiction (different worlds legitimately differ) while
in-container contradiction still flags; and fiction NEVER leaks into
the base world (anti-poisoning — the practice corpus contains
fiction; container hygiene protects the live account). PIECES THAT
EXIST: word senses (one word, many senses, each with verdicts);
should/can context-indexed badges; the value gate's convention-vs-
truth routing; vet_intake's received-vs-expected. MISSING (verify,
then build): a first-class world/container node facts door onto;
retrieval routed by the active container (the execution cycle's
routing pointers — which world is OPEN is routing state); container
provenance stamped at intake. PROBE SHAPE: plant two fiction
containers with CONFLICTING rules + a base world; same questions
under each; leakage 0 both directions; in-container contradictions
still caught; container-less facts land in base WITH a receipt.
Keystone reading: a container is itself a representation — a node
whose doors scope which facts are IN FORCE; ABSOLUTE IS A MYTH made
structural (truth was already relative; containers give the
relativity a home address).

### THE OUTLIER'S OWN LAW — source modeling (owner, 2026-07-15
### night): "is it able to isolate and quantify the outlier
### componants? like if the outlier is a plus something else, can it
### quantify that something else to create a correlation pattern and
### identify the model of the source?"
STATUS: DESIGN CAPTURED; build queued (composes with the rival-form
duel as the F3 leak-class cure; the strongest form of the standing
EFFECT ENTITIES item, open since 07-04). THE ROAD, all existing
organs pointed one new way: (1) ISOLATE — audit flags past k*floor
under the admitted law, receipts kept; (2) QUANTIFY — deviation
d_i = y_i - law(x_i) in UNITS, first-class, kept; (3) INTERROGATE —
the funnel on the deviations: commonality miner (what outlier rows
share), pool (does d have structure vs X?), floors ON d (is the
deviation itself quantized?); (4) MODEL THE SOURCE — discover() on
the deviations. THE THREE-WAY VERDICT this buys: deviations WITH A
LAW = a SECOND SOURCE, minted as its own node (y = law1 +
law2*[condition]) — NEWS, not error (the audit's NEWS class earns a
mechanism); deviations with GRAIN but no law (exactly +-1, +-10 —
digit-shaped) = MIS-ENTRY (the typo concept generalized: interpreted,
quarantined, never banked); NEITHER = honest unknown, dossier kept,
frontier fed. Accounting extends: articulated + source-articulated +
captured + noise = 100. IMMEDIATE PAYOFF, measured need: the port
gate's F3 leak class (poison absorbed into constants, examiners
honestly quiet) falls to exactly this road — isolate the 6 poisoned
cells, deviations exactly +-1 on grain 1 -> mis-entry source ->
constants refit on clean rows -> exact law recovered. Attack list on
build: the source model must beat scrambled-deviation nulls (mint
nothing on shuffled outliers); selection over isolation thresholds
(k*floor sweep, family-wise); a source law must survive with the
flagging law REFIT (no circular flag->model->flag loops); NEWS vs
mis-entry boundary probed at mixed worlds (a lawful source ON a
grain).

### THE REAL WORLD (containers refinement, owner, 2026-07-15 night):
### "which means there should be a 'real' world? at least the
### currently understood presently occupied context or something?
### basically our reality as it is understood?"
Pinned: BASE IS THE REAL WORLD — named precisely as the owner named
it: REALITY AS CURRENTLY UNDERSTOOD, a living model, supersedable
like everything else (ABSOLUTE IS A MYTH applied to containers: base
is the agreed ruler, not cosmic truth; its facts get corrected, kept,
never overwritten). Two things the question separates, both now
explicit: (1) the REALITY CONTAINER (base — the inheritance root,
where container-less facts land, what measurements feed) vs (2) the
PRESENTLY-OCCUPIED CONTEXT (which world is OPEN — pure routing state;
he can stand inside harry-potter for a story while base stays the
anchor; being IN a world and BELIEVING a world are different).
Sharpening (assistant's, offered): what makes base special is not
metaphysics but ADMISSION DISCIPLINE — fiction containers admit by
authorial fiat; base is the one container whose facts must pass the
full court (evidence, verdicts, floors, receipts) and the only one
measurements feed. The real world is not the privileged container,
it is the EXPENSIVE one. FORWARD DOOR this opens (queued with the
interpreter segment): HYPOTHETICALS AS CHEAP CONTAINERS — open a
scratch world, overlay base, simulate, then either promote its facts
into base THROUGH THE GATES or discard the world whole; planning,
counterfactuals, and other-minds beliefs are all the same move.

## THE ROAD TRIALS + THE FRESH START (owner, 2026-07-17)
**"Isaac is an intelligence and scientific engine. his job is to
learn and make sense of information in a way that is directly usable
and readable... we are ready for road trials. durability, range,
power, efficiency... the alpha version needs to start from the
start... the net isnt so important, its the capability. the net
should be produced roughly the same time every time... selecting and
using the correct information as he scales will become more important
over time."**
The rulings, applied to every build from here:
- **Alpha = ROAD TRIALS**: the questions are LONGITUDINAL (does
  performance rise or fall with accumulated experience, and why);
  every session of his life leaves a road-trial record from day one.
- **Day one = a FRESH account** with admission discipline on from
  the first entry (vet + world stamps). The test era is PROLOGUE —
  archived forever as the source document, never reset-able into
  life and never his life.
- **The prologue net = the first developed source**: extraction →
  direct telling through the standard doors (teach with world
  stamps, tell_law told-unverified, refusals loud and counted).
  Told knowledge is usable at once and carries NO inherited belief —
  belief is earned by HIS data (the one-shot-learning experiment is
  measured, not assumed).
- **The net is a build artifact; the capability is the asset.**
  Same experience script → roughly the same net, and that claim is
  MEASURED (two fresh minds, one script, diff), never assumed.
- **SELECTION-AT-SCALE is the named growing axis**: instrument
  which-law precision, considered-vs-bypassed receipts, and
  retrieval quality against net size from the first session —
  reprocessing forgotten material is cheap; selection is the
  scaling problem.

## THE BASE LOOP + THE INITIATOR (owner, 2026-07-17, at the launch)
**"it does need a base loop and an initiator. thats fine. it needs
code to be able to access and build the initial net so thats fine.
as long as the base loop and information is self building and
modifying and structuring."**
The division, made law: HAND-WRITTEN CODE is allowed exactly two
standing jobs — (1) THE BASE LOOP: the fixed kernel iterator (check
the net -> pick the door -> do the op -> take the result door ->
return), which never grows domain logic; and (2) THE INITIATOR: the
bootstrap that builds/accesses the initial net (the launch road,
catalog_tools seeding controller nodes, the corpus relearn). ALL
CONTENT ABOVE THAT — flows, routes, structures, decisions, tools'
standing — must be NET CONTENT that Isaac himself builds, modifies,
and restructures through measured machinery: flows mined from walk
receipts, branched piecewise on miner-named failures, elected on
outcomes with losers kept, winning chains minted as chunks. The
acceptance test for kernel first light (session 2, drill-as-flow):
after it, improving the drill means ISAAC changing HIS net (branch,
elect, mint) — never us editing Python. Code that accumulates
domain decisions is the old trap wearing the kernel's clothes.

## PER-DATASET CONTAINERS + CROSS-DOMAIN CRYSTALLIZATION (owner,
## 2026-07-17, the feeding design): "what if we had it so that each
## dataset is defaulted to its own container, and it can crystalize
## the container structures into cross domain structures."
STATUS: DESIGN CAPTURED same-step; this RESOLVES the standing
"container stamping at intake" item (the top open owner item since
the launch). THE DEFAULT FLIPS: container-less intake no longer
lands in base — every intake door (discover on a table, sessions
with a partner, tell_law, a decoded foreign net) stamps its
SOURCE's own container (in:<source>) by default. Container = SOURCE
IDENTITY (the dataset, the partner model, the decoded net — never
per-session; provenance is measured, not designed). Base stays THE
EXPENSIVE CONTAINER (the real-world section's law): nothing enters
base except through the full court — a dataset container admits
cheaply by its source's fiat, exactly the hypotheticals-as-cheap-
containers move with datasets as the first citizens. WHY THIS IS
THE RIGHT STAMPING ANSWER: it kills the hand-taxonomy trap — nobody
designs an ontology of subjects ("the less you do, the more you let
Isaac do"); the taxonomy EMERGES — cross-domain structure is FOUND,
not filed. THE CRYSTALLIZATION ROAD, all existing organs pointed one
new way: same form across >=2 containers = the lawform-variant
machinery one level up (same form + different constants = siblings
under one lawform: parent — the PARENT is the cross-domain
structure, doored from every container that carries a variant);
relations among structures = the recursive-pools rung (probe-proven
10/10; level-matched nulls apply); the crystallizer's group→crystal
is the same move on a container's contents. THE DISCIPLINE: two
containers are two independently-earned instruments — agreement
across them is the 13-inch-foot discipline for free, and the null is
LEVEL-MATCHED: scramble the fact→container assignment and a real
cross-domain mint must die; the anti-poisoning walls stay measured
(base byte-identical under dataset ingestion; cross-container
difference is NOT contradiction; in-container contradiction still
flags). COMPOSES WITH: incomplete-information-across-datasets (the
triangulation thread — per-dataset containers give the halves of one
whole a home address each, and cross-container comparison is where
resolution lives); selection-at-scale (which-container is routing
state the selection instrument can watch). PROBE SHAPE: two
synthetic datasets sharing a hidden common FORM with different
constants + one unrelated stranger; containers auto-stamped at
intake; crystallization names the shared form across exactly the two
kindred containers (never the stranger) and mints the lawform parent
doored from both; scrambled assignment mints NOTHING; base
byte-identical throughout; promotion of the parent into base goes
THROUGH THE GATES or not at all.
ALSO CAPTURED (owner, same message — the feeding ruling): a staged
curriculum is a CONVENIENCE, never a requirement — order-of-
operations feeding hands him the low-dimensional structures cheaply
("it has the lower dimensional structures and doesnt need to work as
hard to find them"), "but he seems to be pretty efficient now."
Staging is adopted where it is cheap; it never gates intake.
RECEIPT — PROBE-PROVEN same day, then PROMOTED same day (#17:
discover container= + per-dataset default + verdict-on-node,
container-aware _teach_fact, _install_law stamping,
crystallize_forms with the tooth; battery
container_crystal_battery.py 8/8 joins the permanent wall; told and
crystallized families proven to UNIFY, lawform:6b98f4af both roads).
Probe (container_crystal_probe.py, 8/8, 4.0s): Kepler's third law fed as
two star systems (sol 1.0*a^1.5, trappist 4.9*a^1.5) + one stranger
(falling bodies 3.0*t^2), each auto-stamped into its own container;
crystallization minted exactly ONE lawform parent spanning exactly
the two orbit worlds (variant doors both ways, stranger excluded,
constants machine-exact per world at 3e-16/1e-15, parent holds form
never numbers); selection by container: which_law names the right
law per world and refuses the interleaved mix (NONE — and this is
the >=2-laws selection-gauge precondition demonstrated); base
byte-identical throughout (0 drift on 6 questions). TWO RUN-1
FAILURES, both kept as the probe's real findings: (a) THE TOOTH —
scrambled pseudo-worlds minted PARTIAL mixture-laws (linear
surrogates +7.84*x0 / +9.77*x0) and crystallized; cure: ONLY LAWS
THAT EARNED UNDERSTOOD IN THEIR OWN CONTAINER MAY CRYSTALLIZE
(kinship between confusions is not knowledge) — with the tooth the
null dies clean (families 0, excluded-by-verdict 2); (b) a
range-separable mix is honestly piecewise-answerable — the refusal
test needs SUPERPOSITION (interleaved worlds). THE WOUND, MEASURED
(the promotion case): discover()'s _teach_fact indexes 'law:<n>
explains <n>' with NO container tag and ask()'s base road answers
container-less facts — the raw road provably leaks every dataset
feeding into base (D8: raw mind answers under base; shim-stamped
mind does not). PROMOTION SHAPE: stamping inside discover/tell_law/
the session road (source identity -> container, _teach_fact made
container-aware), crystallize_across as an engine organ reading the
law's own certificate instead of a carried verdict, batteries +
walls per the healed promote road.
THE FIRST REAL MEAL (2026-07-18, meal1_first_laws.py — promotion
#18): real sky (8 planets, 11 Jupiter + 12 Saturn moons, NASA/JPL) +
Boyle's actual 1662 table. TWO REAL-FOOD FINDINGS, cured through the
road: (a) 6-7 row dishes REFUSE (3 training rows after holdout) —
cure was MORE REAL MOONS, never a loosened gate; (b) MEASURED-JITTER
KINSHIP — real data earned exponents 1.5/1.49938/1.5007 and
machine-identical form grouping called kin strangers: forms now
group by atom structure w/ inner constants at the family machinery's
own 5% tolerance, family id snapped to quarter-step marks — KEPLER'S
FORM IS ONE NODE (lawform:6b98f4af) told, discovered, synthetic, or
real; battery grown to 9/9 (B9 = the real-sky case, permanent).
Dry receipts: 4/4 UNDERSTOOD, ONE family across three sky
containers, Pluto 0.07% never-fed, selection 4/4 + refusal.
NAMED RUNG: one FORM COURT deciding same-form everywhere.
## THE GROWING GRAMMAR (owner, 2026-07-18, after the vocabulary
## wall was measured): "the algebra enumeration stuff we have going
## is hand coded still. ideally we have a system that can grow and
## expand and experiment. so we need isaac to be able to work harder
## on problems and look for novel solutions, not just the ones we
## programmed."
THE WOUND, NAMED AT ITS ROOT: the enumerator is the last big organ
living entirely in code — a hand menu wearing the discoverer's
clothes (the representation-engine keystone already said it: a
method that lives only in code cannot be examined, duelled, or
superseded). The diversity meals measured the ceiling: g=M/R^2
unsayable at ANY n (vocabulary, not evidence). THE DESIGN = the
genesis loop pointed at ALGEBRA, on existing organs: (1) SCREAM —
the pool says whether a dark residual HAS structure (no scream = no
dig, receipt); (2) AIM — ablation names WHERE it lives (informer,
never judge); (3) EXPERIMENT — novel coordinates COMPOSED from
combinators applied recursively over the named variables (nesting
the menu never did), ranked by log-ruler correlation (leverage dies
under the log); (4) THE COURT unchanged — every candidate faces
ordinary discover (nulls, holdout, examiners; the search widens,
the court never loosens); (5) MINT + GROW — winners join the
composite registry and are OFFERED FIRST on every future problem
(growth = reuse before search). THE USAGE-LAW BOUNDARY, explicit:
hand-built stays the combinator GENERATORS + the epistemics; what
Isaac owns is WHICH compositions exist, survive, and are offered —
the claim is never "no code", it is NO CEILING IN CODE.
RUNG 1 PROBE-PROVEN same day (harder_road_probe.py, 7/7, 24s):
plain road dark on clean g=66.74*M/R^2 (PARTIAL 0.711 surrogate);
scream real 0.311 vs null -0.245 (scrambled: quiet, REFUSES to
dig); aim names exactly {M,R}, decoy 0.007; FIRST candidate tried
courts UNDERSTOOD +66.74*c machine-exact — a coordinate nobody
programmed; the earned word then carries a fresh Coulomb-shaped
world with NO NEW SEARCH and the two laws CRYSTALLIZE cross-domain
(the grown vocabulary immediately participates in kinship). THREE
LESSONS WRONG-KEPT IN THE PROBE: (a) tiny tables skip the aim with
a receipt (the Sun drowned the pool; the court still judges); (b)
the informer ranks in LOG space (leverage made every M-loaded
candidate score ~1.0 linearly); (c) THE REAL PLANETS' PARTIAL IS
THE MACHINE BEING RIGHT — form said (+66.74*c, r2 0.9948), residual
above floor kept dark, and it IS dark: published g carries rotation
and oblateness the point-mass form does not explain; mint withheld
(the garden grows only on UNDERSTOOD).
THE HONEST LADDER: rung 1 done (composition search + effort
escalation, probe); rung 2 PROMOTED same day (#19: powerprod in
register_composite/_augment_with/_applicable_composites;
discover_harder as the escalation organ with receipts under
'harder'; qualifying PARTIAL registers the ENABLER while belief
stays the court's — a PARTIAL law never crystallizes; battery
harder_road_battery.py 7/7 permanent: the law wears the grown
word's name +66.74*(x0*x1^-2), Coulomb solves PLAIN through the
earned word + crystallizes kinship, the real planets' honest
PARTIAL predicts Eris 0.786 vs ~0.82, the null refuses to dig, the
word survives save/load); rung 3 = elections/supersession on the
vocabulary itself (methods duel, losers wear defeats); rung 4 =
new structural KINDS from structured leftovers (the genesis loop's
open-research rung — named, never promised; the sunspot cycle
wants a periodicity kind). Still queued: the rank-ruler pool for
extreme-leverage tables; the effort dial budgeted and receipted
under the consideration law.

THE DIVERSITY RULING (owner, 2026-07-18, the standing feeding
order): "from now on, lets run full in the alpha v.1... diverse
forms, large sets, i want to really push it. larger sets dont do
much theoretically because after he gets the structure down it is
just revalidating what he already knows so those arent high
priority. its mainly diversity that im interested in." The law:
FEEDING PRIORITY = FORM DIVERSITY OVER VOLUME — a bigger table of a
learned structure only revalidates; a NEW FORM is new knowledge.
The live account (isaac_home) is the standing feeding target from
here on (alpha v1 road trials, full on); every meal dry-proves
first, then feeds live, journals kind=meal, logs its road-trial
line.
