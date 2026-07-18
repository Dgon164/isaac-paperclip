# ISAAC — alpha (2026-07-17)

**Isaac is an intelligence and scientific engine. His job is to
learn and make sense of information in a way that is directly
usable and readable.** Give him data, and what comes back is an
equation you can read, a verdict you can trust, a refusal that
tells you why — never a black box, never a confident guess.

Alpha means ROAD TRIALS: the engine left the test bench on
2026-07-17 with a fresh, permanent account, and every session of
his life from here appends a road-trial record — durability, range,
efficiency, and selection quality, measured over time.

## What he does today

- **Discovers laws** from raw numbers: `discover(X, y)` returns an
  equation in plain algebra with four honest verdicts — UNDERSTOOD
  (earned before examiners: an exact road proven on unseen rows, a
  residual replay, a pool meter, a floor certificate), PARTIAL,
  CAPTURED, or NO RULE. Kepler's third law from 8 planets comes
  back machine-exact. Pure noise comes back refused: on eight
  windows of real market returns he refused to mint a forecasting
  law eight times — the refusal IS the product.
- **Audits data** (`askisaac --audit`): flags with receipts (law +
  residual + floor + row), error-vs-news told apart by recurrence,
  duplicate detection, join discovery, totals checked like error-
  correcting codes (a broken sum marks the TUPLE, intersecting
  checks localize the exact cell), and questions where information
  is missing — never an estimated floor.
- **Learns from developed sources one-shot**: told knowledge lands
  usable immediately with NO inherited belief — belief is earned by
  his own data, and wrong tellings fail revalidation naturally.
  His own predecessor taught him this way at the launch; a decoded
  foreign net enters by the same door.
- **Practices language honestly**: speaks only fragments earned
  past a statistical null, or stays silent. His practice loop runs
  THROUGH his own net (the kernel flow), with a vetting gate at the
  front door — a false claim arriving mid-conversation is
  quarantined with its assumed intent, never learned.
- **Improves himself, measurably**: his own failures are mined for
  the losing condition; the named condition becomes the next
  drill's curriculum; the drill runs through his kernel; the
  re-measure shows whether the weakness closed. Weakness → drill →
  moved: proven end to end.

## The laws the whole build lives by

Everything is measured, nothing is hand-told. Every mechanism faces
a scrambled null before it counts. Wrongs are kept with their
classifications, superseded, never erased. Batteries are written
before mechanisms; promotion runs a 47-gate wall; nothing ships on
a red gauntlet. Belief is measured, never told. Refusals are
answers. The net is a reproducible artifact of experience (two
fresh minds fed one script come out byte-identical); the CAPABILITY
is the asset.

## Quickstart

    # the engine self-test (11 capability areas)
    PYTHONHASHSEED=0 python isaac.py

    # discover a law
    from isaac import Isaac
    m = Isaac()
    r = m.discover(X, y)         # -> verdict, equation, receipts

    # audit a data source
    python askisaac.py mydata.csv --audit

    # the practice loop (his live account)
    # runs as a flow through his own net — see isaac_store/sparring.py

## Read next

- `docs/KNOWN_LIMITS_ALPHA.md` — what alpha does NOT claim, with
  evidence. As load-bearing as this file.
- `docs/ISAAC_MANUAL.md` — the capability reference ("if it isn't
  in the manual, it doesn't exist").
- `docs/DESIGN_INTENT.md` — the standing laws every build is
  checked against.
- `experiments/RESULTS_LEDGER.md` — every quoted number's script
  and last verification.
