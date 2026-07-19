"""engineer_grung_probe.py — THE ENGINEER LANE, G-RUNG: implied-goal
recovery from mechanism (owner D6-D7; build queue item 3).

RESEARCH, NOT THE ENGINE. A game's dos, don'ts, and INDIFFERENTS
recovered from instrumented mechanism — never from cultural memory:

  REWARDS    monotone celebrated counters (variables that never step
             down and jump on events), valence MEASURED from the
             jumps; the reward's SOURCE recovered by association
             (at score jumps, head==food at 1.0).
  BUFFERS    bidirectional bounded resources whose exhaustion
             associates with the absorbing state (energy: -1/step,
             +40 on food, death at 0).
  FORBIDDEN  transitions that DO NOT EXIST (lockout): the reverse
             command never yields the reversed direction — distinct
             from PUNISHED (allowed, then fatal: wall, body).
  FATAL      death predicates mined from a candidate vocabulary,
             admitted only at P(death|pred)=1 vs P(death|~pred)~0;
             innocent decoys must not be implicated.
  FREE       the planted lucky variable files FREE — the interior
             you get to not compute.

THE TWO NULLS (D6's teeth):
  MOD THE GAME — invert the reward line (food pays -10): the
    recovered sheet must report the INVERTED valence from code, not
    the culturally-remembered one.
  SUPERSTITION — the constructed policy must be bit-identical under
    different lucky streams: no rituals on a FREE variable.

CONSTRUCTION PROOF: a policy built ONLY from the recovered sheet
beats blind random survival by a wide margin.

PREDICTIONS (filed before the first run; wrong ones kept)
  G1 score recovered as celebrated counter, valence +10 measured;
     length monotone too.
  G2 the do: at score jumps, head==food association 1.0.
  G3 energy recovered as buffer (-1/step, +40 refill on the same
     food event, exhaustion associates with death).
  G4 forbidden vs punished: reverse = lockout (commanded direction
     NEVER results); wall-ward moves ARE taken (exist) and kill.
  G5 fatal predicates mined at P=1 vs ~0; decoys (left-half,
     lucky>50) not implicated.
  G6 THE MOD NULL: inverted game -> sheet says food pays -10.
  G7 THE SUPERSTITION NULL: lucky files FREE; policy actions
     bit-identical across lucky streams.
  G8 CONSTRUCTION: sheet-policy survival >= 3x random, score >= 5x.

WRONG-KEPT (runs 1-3, four lessons):
  (1) a curled starting body TRAPPED the head — every driver died
      in ~3 steps and the corpus starved; nothing was recoverable
      because nothing was observable.
  (2) THE CORPUS DECIDES WHAT IS KNOWABLE: at a rich diet every
      refill hit the energy cap and the +40 was GENUINELY
      unobservable (median said +5; even max said +15) — the
      magnitude became knowable only when a STARVING driver joined
      the corpus. Instrumenting a mechanism means driving it into
      the regimes you want to know about.
  (3) an arbitrary sample-count threshold rejected a P=1.0 court
      with 29 one-sided observations — thresholds must serve the
      evidence, not round numbers.
  (4) 'lucky' wandered into the BUFFER class on bidirectionality
      alone — a resource EARNS the title by a LAWFUL drain
      (constant negative step); a wobbling variable falls through
      to the free court. Classification without a tooth is naming,
      not knowledge.

Run: cd experiments && PYTHONHASHSEED=0 python engineer_grung_probe.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

DIRS = dict(U=(0, -1), D=(0, 1), L=(-1, 0), R=(1, 0))


class Snake:
    """The mechanism under study. 12x12; length-8 start; reverse is
    a LOCKOUT (ignored); energy -1/step, +40 on food, death at 0;
    'lucky' is planted indifference on its own rng stream."""

    def __init__(self, seed=0, invert_reward=False, lucky_seed=None):
        self.rng = np.random.default_rng(seed)
        self.lrng = np.random.default_rng(
            seed + 7777 if lucky_seed is None else lucky_seed)
        self.W = self.H = 12
        # run-1 wrong-kept: a curled start TRAPPED the head (two
        # neighbors body, reverse locked into a third) — every
        # driver died in ~3 steps and the corpus starved. The tail
        # now trails away from the head's neighborhood.
        self.body = [(6, 6), (5, 6), (4, 6), (3, 6), (2, 6),
                     (2, 7), (3, 7), (4, 7)]
        self.dir = (1, 0)
        self.score, self.energy, self.alive = 0, 100, True
        self.invert = invert_reward
        self.lucky = int(self.lrng.integers(0, 100))
        self._place_food()

    def _place_food(self):
        while True:
            f = (int(self.rng.integers(0, self.W)),
                 int(self.rng.integers(0, self.H)))
            if f not in self.body:
                self.food = f
                return

    def state(self):
        return dict(score=self.score, energy=self.energy,
                    length=len(self.body), lucky=self.lucky,
                    head=self.body[0], food=self.food,
                    body=tuple(self.body), dir=self.dir,
                    alive=self.alive)

    def step(self, action):
        d = DIRS[action]
        if d == (-self.dir[0], -self.dir[1]):
            d = self.dir                    # the lockout
        else:
            self.dir = d
        self.lucky = int(self.lrng.integers(0, 100))
        nx = self.body[0][0] + d[0]
        ny = self.body[0][1] + d[1]
        if not (0 <= nx < self.W and 0 <= ny < self.H) \
                or (nx, ny) in self.body:
            self.alive = False
            return
        self.body.insert(0, (nx, ny))
        if (nx, ny) == self.food:
            self.score += (-10 if self.invert else 10)
            self.energy = min(100, self.energy + 40)
            self._place_food()
        else:
            self.body.pop()
        self.energy -= 1
        if self.energy <= 0:
            self.alive = False


def play(seed, policy, invert=False, max_steps=500, lucky_seed=None):
    g = Snake(seed, invert, lucky_seed)
    log = []
    while g.alive and len(log) < max_steps:
        s = g.state()
        a = policy(s)
        g.step(a)
        log.append((s, a, g.state()))
    return log


def random_policy(seed):
    r = np.random.default_rng(seed)
    return lambda s: "UDLR"[int(r.integers(0, 4))]


def scout_policy(seed):
    """A blind food-ward walker: prefers reducing distance to food,
    knows nothing about walls or bodies (it dies plenty — but it
    EATS, which fattens the reward-event corpus)."""
    r = np.random.default_rng(seed)

    def pol(s):
        ranked = sorted(
            DIRS.items(),
            key=lambda kv: (abs(s["head"][0] + kv[1][0] - s["food"][0])
                            + abs(s["head"][1] + kv[1][1]
                                  - s["food"][1])
                            + float(r.uniform(0, 0.5))))
        return ranked[0][0]
    return pol


def starver_policy(seed):
    """Patrol until hungry, then chase — the only diet that ever
    eats at LOW energy, making the uncapped refill observable (the
    corpus decides what is knowable)."""
    ringp = ring_policy()
    scoutp = scout_policy(seed)

    def pol(s):
        return ringp(s) if s["energy"] >= 45 else scoutp(s)
    return pol


def ring_policy():
    """A blind wall-patroller (drives the mechanism into exhaustion
    territory the random walker rarely reaches)."""
    def pol(s):
        x, y = s["head"]
        if x > 0 and y > 1:
            return "L" if s["dir"] != (1, 0) else "U"
        if x == 0 and y > 0:
            return "U"
        if y == 0 and x < 11:
            return "R"
        if x == 11 and y < 11:
            return "D"
        return "L"
    return pol


# ── THE RECOVERY (mechanical, from logs only) ─────────────────────
def recover(logs):
    steps = [t for ep in logs for t in ep]
    sheet = dict(rewards={}, buffers={}, free=[], forbidden=[],
                 fatal=[])
    NUM = ("score", "energy", "length", "lucky")
    deltas = {v: [t[2][v] - t[0][v] for t in steps] for v in NUM}
    deaths = [t for t in steps if not t[2]["alive"]]
    for v in NUM:
        d = np.asarray(deltas[v], float)
        jumps = d[d != 0]
        if len(jumps) and d.min() >= 0:
            sheet["rewards"][v] = dict(
                valence=round(float(np.mean(jumps)), 3),
                events=int(len(jumps)))
        elif (len(jumps) and d.min() < 0 < d.max()
              and d[d < 0].std() < 1e-9):
            # THE BUFFER TOOTH (run-3 lesson: 'lucky' wandered into
            # the buffer branch on bidirectionality alone): a
            # resource EARNS the title by a LAWFUL drain — constant
            # negative step. A wobbling variable falls through to
            # the free court.
            exhausted = [t for t in deaths if t[2][v] <= 0]
            refills = jumps[jumps > 0]
            # refill = the MAX positive jump: a ceiling cap makes
            # near-full refills read small (run-2 lesson: median said
            # +5 because most eats happened near the cap)
            sheet["buffers"][v] = dict(
                drain=round(float(np.median(d[d < 0])), 3),
                refill=(round(float(refills.max()), 3)
                        if len(refills) else None),
                capped_events=(int(np.sum(refills < refills.max()))
                               if len(refills) else 0),
                deaths_at_zero=len(exhausted))
        # FREE court: value carries no information about outcomes
        vals = np.asarray([t[0][v] for t in steps], float)
        died = np.asarray([not t[2]["alive"] for t in steps], float)
        got = np.asarray([t[2]["score"] != t[0]["score"]
                          for t in steps], float)
        rng = np.random.default_rng(11)

        def assoc(a, b):
            if a.std() < 1e-12 or b.std() < 1e-12:
                return 0.0
            return abs(float(np.corrcoef(a, b)[0, 1]))
        real = max(assoc(vals, died), assoc(vals, got))
        null = 0.0
        for _ in range(25):
            vs = vals.copy()
            rng.shuffle(vs)
            null = max(null, max(assoc(vs, died), assoc(vs, got)))
        if real <= null and vals.std() > 1e-12 \
                and v not in sheet["rewards"] \
                and v not in sheet["buffers"]:
            sheet["free"].append(v)
    # reward source: what coincides with the celebration, always
    hits = [t for t in steps if t[2]["score"] != t[0]["score"]]
    if hits:
        at_food = np.mean([t[2]["head"] == t[0]["food"]
                           for t in hits])
        sheet["reward_source"] = dict(predicate="head==food",
                                      association=round(float(at_food),
                                                        3))
    # forbidden vs existing transitions (the lockout court)
    rev_attempts = taken = 0
    for s, a, s2 in steps:
        want = DIRS[a]
        if want == (-s["dir"][0], -s["dir"][1]):
            rev_attempts += 1
            taken += (s2["dir"] == want)
    if rev_attempts and taken == 0:
        sheet["forbidden"].append(dict(
            action="reverse", attempts=rev_attempts,
            receipt="commanded direction never results — the "
                    "transition does not exist (lockout)"))
    # fatal predicates: candidate vocabulary, court P(death|pred)
    W = max(t[0]["head"][0] for t in steps) + 1
    H = max(t[0]["head"][1] for t in steps) + 1

    def eff(s, a):
        d = DIRS[a]
        return s["dir"] if d == (-s["dir"][0], -s["dir"][1]) else d

    def nxt(s, a):
        d = eff(s, a)
        return (s["head"][0] + d[0], s["head"][1] + d[1])

    CANDS = dict(
        next_cell_wall=lambda s, a: not (0 <= nxt(s, a)[0] < W
                                         and 0 <= nxt(s, a)[1] < H),
        next_cell_body=lambda s, a: nxt(s, a) in s["body"],
        energy_exhausted=lambda s, a: s["energy"] <= 1,
        left_half=lambda s, a: s["head"][0] < W // 2,
        lucky_high=lambda s, a: s["lucky"] > 50)
    courts = {}
    for name, fn in CANDS.items():
        pred = np.asarray([fn(s, a) for s, a, _ in steps], bool)
        died = np.asarray([not t[2]["alive"] for t in steps], bool)
        if pred.sum() == 0:
            courts[name] = dict(verdict="UNOBSERVED")
            continue
        p_hit = float(died[pred].mean())
        p_miss = float(died[~pred].mean()) if (~pred).sum() else 0.0
        courts[name] = dict(p_death=round(p_hit, 3),
                            p_base=round(p_miss, 3),
                            n=int(pred.sum()))
        if p_hit >= 0.999 and p_miss < 0.05:
            sheet["fatal"].append(dict(predicate=name,
                                       p_death=round(p_hit, 3),
                                       n=int(pred.sum())))
    sheet["courts"] = courts
    sheet["bounds"] = (W, H)
    return sheet


def build_policy(sheet):
    """Construction from the sheet ONLY: refuse fatal predicates,
    respect the lockout, chase the recovered reward source."""
    W, H = sheet["bounds"]
    fatal = {f["predicate"] for f in sheet["fatal"]}
    seek = sheet.get("reward_source", {}).get("association", 0) > 0.99
    good = sheet["rewards"].get("score", {}).get("valence", 0) > 0

    def pol(s):
        best, bestd = None, 1e9
        for a, d in DIRS.items():
            if d == (-s["dir"][0], -s["dir"][1]):
                continue                     # forbidden — recovered
            nx, ny = s["head"][0] + d[0], s["head"][1] + d[1]
            if "next_cell_wall" in fatal \
                    and not (0 <= nx < W and 0 <= ny < H):
                continue
            if "next_cell_body" in fatal and (nx, ny) in s["body"]:
                continue
            dist = abs(nx - s["food"][0]) + abs(ny - s["food"][1])
            rank = dist if (seek and good) else -dist
            if rank < bestd:
                bestd, best = rank, a
        return best or "U"
    return pol


def main():
    t0 = time.perf_counter()
    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"  [{'ok ' if ok else 'FAIL'}] {name} — {detail}")

    logs = [play(s, random_policy(1000 + s)) for s in range(50)]
    logs += [play(200 + s, ring_policy()) for s in range(8)]
    logs += [play(400 + s, scout_policy(500 + s)) for s in range(10)]
    logs += [play(600 + s, starver_policy(700 + s)) for s in range(8)]
    sheet = recover(logs)

    # G1 — the celebrated counters
    sc = sheet["rewards"].get("score", {})
    ok1 = (abs(sc.get("valence", 0) - 10.0) < 1e-9
           and "length" in sheet["rewards"])
    check("G1 rewards — score celebrated at +10 measured; length "
          "monotone", ok1, f"score {sc}; rewards "
          f"{sorted(sheet['rewards'])}")

    # G2 — the do: reward source association
    rs = sheet.get("reward_source", {})
    ok2 = rs.get("association", 0) == 1.0
    check("G2 the do — at every celebration, head==food", ok2,
          f"{rs}")

    # G3 — the buffer
    en = sheet["buffers"].get("energy", {})
    ok3 = (en.get("drain") == -1.0 and en.get("refill") == 39.0
           and en.get("deaths_at_zero", 0) > 0)
    check("G3 the buffer — energy -1/step, +39 net refill (cap "
          "observed), exhaustion kills", ok3, f"{en}")

    # G4 — forbidden vs punished
    fb = sheet["forbidden"]
    wall_court = sheet["courts"]["next_cell_wall"]
    ok4 = (len(fb) == 1 and fb[0]["action"] == "reverse"
           and fb[0]["attempts"] > 100
           and wall_court.get("n", 0) >= 20)
    check("G4 forbidden vs punished — reverse is a lockout (never "
          "results); wall moves exist and kill", ok4,
          f"reverse attempts {fb[0]['attempts'] if fb else 0}, taken 0; "
          f"wall court {wall_court}")

    # G5 — fatal predicates at P=1; decoys unimplicated
    fatal = {f["predicate"] for f in sheet["fatal"]}
    dec1 = sheet["courts"]["left_half"]
    dec2 = sheet["courts"]["lucky_high"]
    ok5 = ({"next_cell_wall", "next_cell_body"} <= fatal
           and "left_half" not in fatal and "lucky_high" not in fatal
           and dec1["p_death"] < 0.2 and dec2["p_death"] < 0.2)
    check("G5 fatal mined at P=1; decoys stay innocent", ok5,
          f"fatal {sorted(fatal)}; decoys p_death "
          f"{dec1['p_death']}/{dec2['p_death']}")

    # G6 — THE MOD NULL: the inverted game reports itself
    logs_inv = [play(s, random_policy(3000 + s), invert=True)
                for s in range(30)]
    sheet_inv = recover(logs_inv)
    # score now steps DOWN on food: no longer a monotone counter —
    # the court must reclassify and the measured valence go negative
    d_inv = [t[2]["score"] - t[0]["score"] for ep in logs_inv
             for t in ep if t[2]["score"] != t[0]["score"]]
    ok6 = ("score" not in sheet_inv["rewards"]
           and len(d_inv) > 0 and float(np.mean(d_inv)) == -10.0)
    check("G6 THE MOD NULL — inverted reward read from code, not "
          "culture", ok6,
          f"food pays {float(np.mean(d_inv)) if d_inv else '?'}; "
          f"score dethroned from rewards: "
          f"{'score' not in sheet_inv['rewards']}")

    # G7 — THE SUPERSTITION NULL
    ok_free = "lucky" in sheet["free"]
    pol = build_policy(sheet)
    acts_a = [a for _, a, _ in play(77, pol, lucky_seed=1)]
    acts_b = [a for _, a, _ in play(77, pol, lucky_seed=999)]
    ok7 = ok_free and acts_a == acts_b and len(acts_a) > 50
    check("G7 THE SUPERSTITION NULL — lucky filed FREE; policy "
          "bit-identical across lucky streams", ok7,
          f"free {sheet['free']}; {len(acts_a)} actions identical: "
          f"{acts_a == acts_b}")

    # G8 — construction beats blind random by a wide margin
    surv_r, score_r, surv_p, score_p = [], [], [], []
    for s in range(30):
        ep = play(5000 + s, random_policy(6000 + s))
        surv_r.append(len(ep))
        score_r.append(ep[-1][2]["score"])
        ep = play(5000 + s, pol)
        surv_p.append(len(ep))
        score_p.append(ep[-1][2]["score"])
    m_sr, m_ss = float(np.mean(surv_r)), float(np.mean(score_r))
    m_pr, m_ps = float(np.mean(surv_p)), float(np.mean(score_p))
    ok8 = m_pr >= 3 * m_sr and m_ps >= 5 * max(m_ss, 1.0)
    check("G8 construction — the recovered sheet plays the game", ok8,
          f"survival {m_pr:.0f} vs {m_sr:.0f} steps "
          f"({m_pr / max(m_sr, 1):.1f}x); score {m_ps:.0f} vs "
          f"{m_ss:.0f}")

    dt = time.perf_counter() - t0
    npass = sum(checks)
    print(f"\n  PROBE: {npass} passed, {len(checks) - npass} failed "
          f"of {len(checks)}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
