"""task_battery.py — told the GOAL, he finds the method (owner,
2026-07-12: "you tell him the goals and he needs to figure out what
to do... all he needs to do is respond with fizz or buzz. next token
prediction style.")

The organ under test: learn_responses(prompts, responses) +
respond(prompt). Hand-built = translation + epistemics ONLY. The
proof standard mirrors learned speech:
  - the engine contains NO task words (grep proof);
  - the SAME organ, zero code changes, solves FOREIGN worlds;
  - a world whose exceptions are random is REFUSED, not invented;
  - accuracy is judged on prompts BEYOND every training example
    (a lookup cannot follow) and reported as complete numbers.

WRONG-KEPT: the assistant's first probe (fizzbuzz_probe.py) hand
built one-vs-rest targets and composed them with argmax — programming
the lesson (owner correction, same day). Here the decomposition is
Isaac's own: classes = the distinct tokens HE observes; echo = the
relation HIS compare primitive finds.
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import isaac as mod                                # noqa: E402

PASS, FAIL = 0, 0


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


def world_fizzbuzz(n):
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("fizzbuzz")
        elif i % 3 == 0:
            out.append("fizz")
        elif i % 5 == 0:
            out.append("buzz")
        else:
            out.append(str(i))
    return out


def world_woof(n):                      # foreign world 1
    return ["woof" if i % 7 == 0 else str(i) for i in range(1, n + 1)]


def world_pingpong(n):                  # foreign world 2, composed
    out = []
    for i in range(1, n + 1):
        if i % 36 == 0:
            out.append("pingpong")
        elif i % 4 == 0:
            out.append("ping")
        elif i % 9 == 0:
            out.append("pong")
        else:
            out.append(str(i))
    return out


def run_world(make, n_train, n_test, taskname):
    mind = mod.Isaac()
    truth = make(n_train + n_test)
    prompts = [str(i) for i in range(1, n_train + 1)]
    rec = mind.learn_responses(prompts, truth[:n_train], name=taskname)
    right, abstained = 0, 0
    for i in range(n_train + 1, n_train + n_test + 1):
        r = mind.respond(str(i), name=taskname)
        if r["token"] is None:
            abstained += 1
        elif r["token"] == truth[i - 1]:
            right += 1
    return mind, rec, right, abstained


def main():
    # ── 1. the grep proof: no task words in the engine ───────────
    import re
    src = open(os.path.join(ROOT, "isaac.py"), encoding="utf-8").read()
    words = [w for w in ("fizz", "buzz", "woof", "ping", "pong")
             if re.search(rf"\b{w}", src.lower())]
    check("engine contains no task words", words == [],
          f"found={words or 'none'}")

    # ── 2+3. FizzBuzz, his way: goal told, method his ────────────
    mind, rec, right, abst = run_world(world_fizzbuzz, 300, 100, "t1")
    lawful = sorted(rec["laws"].keys())
    check("he differentiates the classes himself (echo + 3 tokens)",
          len(rec["classes"]) == 4 and rec["echo_rate"] > 0.5,
          f"classes={[c['token'] for c in rec['classes']]} "
          f"echo_rate={rec['echo_rate']}")
    check("END-TO-END n=301..400 (beyond all training): >=95/100 exact",
          right >= 95,
          f"{right}/100 exact, {abst}/100 abstained; class laws: "
          f"{[(c['token'], c['verdict']) for c in rec['classes']]}")

    # ── 4. foreign world, SAME organ, zero changes ───────────────
    _, rec2, right2, abst2 = run_world(world_woof, 280, 70, "t2")
    check("foreign world (one exception token, period 7): >=67/70",
          right2 >= 67, f"{right2}/70 exact, {abst2} abstained")

    # ── 5. foreign composed world, SAME organ ────────────────────
    # (720 training rows: the 36-class needs enough positives in
    # discover's own half-split — at 360 it refused with the honest
    # small-sample diagnosis, which is correct but tests starvation,
    # not the organ)
    _, rec3, right3, abst3 = run_world(world_pingpong, 720, 90, "t3")
    check("foreign composed world (4/9/36): >=85/90",
          right3 >= 85,
          f"{right3}/90 exact, {abst3} abstained; "
          f"{[(c['token'], c['verdict']) for c in rec3['classes']]}")

    # ── 6. the refusal world: random exceptions are NOT invented ─
    rng = np.random.default_rng(7)
    n = 300
    resp = [str(i) for i in range(1, n + 1)]
    for i in rng.choice(n, size=60, replace=False):
        resp[i] = "blip"
    m4 = mod.Isaac()
    rec4 = m4.learn_responses([str(i) for i in range(1, n + 1)], resp,
                              name="t4")
    blip_law = "blip" in rec4.get("laws", {})
    check("random-exception world: no exception law invented",
          not blip_law,
          f"blip verdict: "
          f"{[c['verdict'] for c in rec4['classes'] if c['token'] == 'blip']}")

    # ── 7. and it answers honestly there: never says the token ───
    said_blip = 0
    for i in range(301, 361):
        r = m4.respond(str(i), name="t4")
        said_blip += (r["token"] == "blip")
    check("refusal world: 'blip' never emitted on fresh prompts",
          said_blip == 0, f"emitted {said_blip}/60 times")

    # ── 8. non-numeric prompts refuse loudly ─────────────────────
    m5 = mod.Isaac()
    rec5 = m5.learn_responses(["a", "b", "c"], ["x", "y", "z"],
                              name="t5")
    check("untranslatable prompts: loud refusal, no crash",
          "refused" in rec5, str(rec5.get("refused", ""))[:50])

    print()
    print(f"TASK BATTERY: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
