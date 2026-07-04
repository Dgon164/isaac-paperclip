# -*- coding: utf-8 -*-
"""SENSE BATTERY — senses as first-class nodes (2026-07-04).

The claim under test: crystallize_senses mints senses as NODES with
directed doors (not meta blobs), admission is null-gated (chance context
overlap is filed wrong, kept, classified), routing reads the doors and
demotes non-sound senses, re-crystallization supersedes (never erases).

S1  planted two senses        -> both sound, direction preserved, routing right
S2  chance contexts (20 trials) -> 0 sound senses minted from noise
S3  doors are real            -> compare_nodes sees sense structure; nodes in net
S4  supersession on re-run    -> old generation kept + demoted; routing uses new
S5  mixed real + noise        -> real sense sound, chance filed wrong with why
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

PASS, FAIL = "PASS", "FAIL"
results = []

def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{PASS if ok else FAIL}] {name}" + (f" — {detail}" if detail else ""))

# ── S1: planted two senses ──────────────────────────────────────────
print("\nS1 — planted polysemy ('bank'), enough evidence to beat chance")
i = Isaac()
river = [
    ["river", "water", "flows", "past", "the", "bank", "shore"],
    ["muddy", "river", "bank", "erodes", "water", "slowly"],
    ["the", "river", "bank", "flooded", "water", "rose"],
    ["fish", "swim", "near", "the", "river", "bank", "water"],
    ["boat", "moored", "river", "bank", "water", "calm"],
]
money = [
    ["money", "deposit", "at", "the", "bank", "teller"],
    ["bank", "loan", "money", "interest", "teller", "counter"],
    ["the", "bank", "vault", "holds", "money", "teller"],
    ["savings", "money", "bank", "account", "teller", "opened"],
    ["cash", "money", "withdrawn", "bank", "teller", "queue"],
]
for s in river + money:
    i.observe(s)
senses = i.crystallize_senses("bank")
sound = [s for s in senses if s["verdict"] == "sound"]
check("two sound senses crystallized", len(sound) == 2,
      f"{len(sound)} sound of {len(senses)} total")
r_out = i.route("bank", {"river", "water"})
m_out = i.route("bank", {"money", "teller"})
check("routing disambiguates river context",
      r_out and r_out <= {"shore", "erodes", "flooded", "water"}, str(sorted(r_out)))
check("routing disambiguates money context",
      m_out and m_out <= {"teller", "loan", "vault", "account"}, str(sorted(m_out)))
# direction preserved: in-doors and out-doors differ per sense
directed = all(
    i.net.get_predecessors(s["name"], tag="sense_seq")
    != i.net.get_doors(s["name"], tag="sense_seq")
    for s in sound)
check("direction is preserved (in-doors != out-doors per sense)", directed)

# ── S2: chance contexts must mint ZERO sound senses ────────────────
print("\nS2 — noise refusal: random contexts, 20 trials")
rng = np.random.default_rng(7)
vocab = [f"w{k}" for k in range(12)]
false_sound = 0
for trial in range(20):
    j = Isaac()
    for _ in range(8):
        ctx = list(rng.choice(vocab, size=5, replace=False))
        pos = rng.integers(0, 6)
        j.observe(ctx[:pos] + ["node"] + ctx[pos:])
    ss = j.crystallize_senses("node")
    false_sound += sum(1 for s in ss if s["verdict"] == "sound")
check("0 sound senses from pure chance co-occurrence", false_sound == 0,
      f"{false_sound} false senses across 20 trials")

# ── S3: senses are net structure, visible to every walker ──────────
print("\nS3 — the doors are real")
a, b = sound[0]["name"], sound[1]["name"]
cmp = i.compare_nodes(a, b, tag="sense_seq")
check("compare_nodes works on sense nodes (the atom sees them)",
      bool(cmp["outgoing"]["only_a"]) and bool(cmp["outgoing"]["only_b"]))
check("sense nodes live in the net", a in i.net.all_nodes() and b in i.net.all_nodes())
check("membership doors node->sense exist",
      set(i.net.get_doors("bank", tag="sense")) >= {a, b})

# ── S4: supersession, never overwrite ───────────────────────────────
print("\nS4 — re-crystallization supersedes the old generation")
i.observe(["steep", "river", "bank", "water", "collapsed"])
senses2 = i.crystallize_senses("bank")
old_alive = a in i.net.all_nodes() and b in i.net.all_nodes()
old_demoted = (i.net.get_meta(a, "verdict") == "superseded"
               and i.net.get_meta(b, "verdict") == "superseded")
check("old generation KEPT in the net", old_alive)
check("old generation demoted to 'superseded'", old_demoted)
r_out2 = i.route("bank", {"river", "water"})
check("routing works through the new generation",
      bool(r_out2) and r_out2 <= {"shore", "erodes", "flooded", "water", "collapsed"},
      str(sorted(r_out2)))

# ── S5: mixed — real sense sound, chance filed wrong with the why ──
print("\nS5 — wrong is kept and classified")
k = Isaac()
for s in river:
    k.observe(s)
rng5 = np.random.default_rng(11)
for _ in range(4):
    ctx = list(rng5.choice(vocab, size=5, replace=False))
    k.observe(ctx[:2] + ["bank"] + ctx[2:])
ss5 = k.crystallize_senses("bank")
sound5 = [s for s in ss5 if s["verdict"] == "sound"]
wrong5 = [s for s in ss5 if s["verdict"] == "wrong"]
check("the real sense survives among noise",
      any("river" in s["context"] for s in sound5), f"{len(sound5)} sound")
check("chance clusters filed wrong WITH the why",
      all("why_wrong" in s for s in wrong5) and len(k.wrong_senses) == len(wrong5),
      f"{len(wrong5)} filed")
check("routing demotes wrong senses (sound one wins on its context)",
      k.route("bank", {"river", "water"}) <= {"shore", "erodes", "flooded", "water"})

# ── verdict ─────────────────────────────────────────────────────────
n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*60}\nSENSE BATTERY: {n_pass}/{len(results)} passed")
sys.exit(0 if n_pass == len(results) else 1)
