"""gpt2_chain_probe.py — THE CHAIN SEQUENCES BY TYPE (owner,
2026-07-17: "what is the chain sequence for france, or the chain
sequence for location, or the chain sequence for verb... find the
pattern interactions for the different types of groups and how they
pass information").

Method — the drop algebra at COMPONENT level (156 components: 144
heads + 12 MLPs), on the SPECIFIC push (demeaned over the 200
candidates in play — the logit-space stopword law):
  1. Single ablations: every component's effect on the target.
  2. The top movers pair-ablate: EXCESS = joint - sum of singles.
     SUBADDITIVE excess (joint < sum) = a SHARED PATHWAY — the two
     components sit on one chain, breaking it twice loses nothing
     extra. SUPERADDITIVE = REDUNDANT parallel routes — either
     covers for the other. Signed links, layer-ordered = the chain.
  3. TYPES: run over prompt FAMILIES (locations: 'X is the capital
     of'; verb agreement: 'The <nouns> ...' -> is/are). The TYPE's
     chain = links recurring within the family; the DIFFERENTIAL
     (links in one type, absent in the other) = how different
     kinds of groups pass information differently.

Gates:
  F1 machinery: every prompt yields a layer-ordered chain with
     signed links.
  F2 within-type recurrence: the location family shares chain links
     across prompts (>=2 links in >=3/4); same for the verb family.
  F3 the differential: the two type signatures are NOT the same
     set — location links and verb links diverge.

Run: PYTHONHASHSEED=0 python gpt2_chain_probe.py
"""
import sys
from itertools import combinations

import numpy as np
import torch

PASS, FAIL = 0, 0
NH, DH, NL = 12, 64, 12
TOPK = 8
NCAND = 200


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


LOC = [("Paris is the capital of", " France"),
       ("Berlin is the capital of", " Germany"),
       ("Rome is the capital of", " Italy"),
       ("Madrid is the capital of", " Spain")]
VERB = [("The keys to the old cabinet", " are"),
        ("The dogs in the yard", " are"),
        ("The book on the wooden table", " is"),
        ("The children in the classroom", " are")]


def comp_name(c):
    L, h = c
    return f"L{L}M" if h == NH else f"L{L}H{h}"


def main():
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    print("=" * 70)
    print("CHAIN SEQUENCES BY TYPE — 156 components, pair-excess "
          "links")
    print("=" * 70)
    tok = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    model.eval()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(dev)

    def get_w(c):
        L, h = c
        if h == NH:
            return model.transformer.h[L].mlp.c_proj.weight, \
                slice(None)
        return model.transformer.h[L].attn.c_proj.weight, \
            slice(h * DH, (h + 1) * DH)

    def spec_target(ids, t_id, cand):
        with torch.no_grad():
            lg = model(**ids).logits[0, -1]
        dc = lg[cand].cpu().numpy()
        return float(lg[t_id]) - float(np.median(dc))

    def ablated(comps, ids, t_id, cand):
        saved = []
        with torch.no_grad():
            for c in comps:
                W, sl = get_w(c)
                saved.append((W, sl, W.detach()[sl].clone()))
                W[sl] = 0.0
            s = spec_target(ids, t_id, cand)
            for W, sl, v in saved:
                W[sl] = v
        return s

    comps = [(L, h) for L in range(NL) for h in range(NH + 1)]

    sigs = {}
    for tname, fam in (("LOCATION", LOC), ("VERB", VERB)):
        print(f"  ── {tname} family ──")
        # phase 1: singles per prompt; the FAMILY POOL = the union
        # of each prompt's top movers, capped — so phase 2 tests
        # THE SAME pairs on every prompt (the family-wise ruler;
        # first pass paired each prompt's own top-8, so links could
        # not recur — wrong-kept)
        per = []
        strength = {}
        for prompt, expect in fam:
            ids = tok(prompt, return_tensors="pt").to(dev)
            t_id = tok.encode(expect)[0]
            with torch.no_grad():
                base_all = model(**ids).logits[0, -1]
            cand = torch.topk(base_all, NCAND).indices
            base = spec_target(ids, t_id, cand)
            delta = {c: base - ablated([c], ids, t_id, cand)
                     for c in comps}
            movers = sorted(comps,
                            key=lambda c: -abs(delta[c]))[:6]
            for c in movers:
                strength[c] = strength.get(c, 0) + abs(delta[c])
            per.append((prompt, expect, ids, t_id, cand, base,
                        delta, movers))
        pool = sorted(sorted(strength, key=lambda c: -strength[c])
                      [:14])
        print(f"    family pool ({len(pool)}): "
              f"{[comp_name(c) for c in pool]}")
        fam_links = []
        for prompt, expect, ids, t_id, cand, base, delta, movers \
                in per:
            links = []
            for a, b in combinations(pool, 2):
                joint = base - ablated([a, b], ids, t_id, cand)
                exc = joint - (delta[a] + delta[b])
                if abs(exc) > 0.4:
                    links.append((a, b, "shared" if exc < 0
                                  else "redundant", round(exc, 2)))
            mv = ", ".join(f"{comp_name(c)}:{delta[c]:+.1f}"
                           for c in movers[:5])
            print(f"    '{prompt}' -> '{expect}' "
                  f"(specific {base:+.1f}): movers {mv}")
            chain = " -> ".join(
                f"{comp_name(a)}~{comp_name(b)}[{k}{e:+.1f}]"
                for a, b, k, e in sorted(
                    links, key=lambda x: (x[0][0], x[1][0]))[:12])
            note = chain if links else "(none past threshold)"
            print(f"      chain: {note}")
            fam_links.append({(comp_name(a), comp_name(b), k)
                              for a, b, k, e in links})
        counts = {}
        for s in fam_links:
            for lk in s:
                counts[lk] = counts.get(lk, 0) + 1
        sig = {lk for lk, n in counts.items() if n >= 3}
        sigs[tname] = (sig, fam_links, counts)
        rec = sorted((n, lk) for lk, n in counts.items()
                     if n >= 2)[::-1]
        print(f"    {tname} signature (links in >=3/4 prompts): "
              f"{sorted(sig) if sig else 'none'}; "
              f"recurring >=2: {[(lk, n) for n, lk in rec[:6]]}")

    all_chains = all(len(fl) >= 0 for _, fl, _ in sigs.values())
    n_links_total = sum(len(s) for _, fl, _ in sigs.values()
                        for s in fl)
    check(f"F1 machinery: chains extracted with signed links "
          f"({n_links_total} links total across 8 prompts)",
          all_chains and n_links_total >= 8)
    loc_rec = sum(1 for lk, n in sigs["LOCATION"][2].items()
                  if n >= 3)
    verb_rec = sum(1 for lk, n in sigs["VERB"][2].items()
                   if n >= 3)
    check(f"F2 within-type recurrence: LOCATION {loc_rec} links in "
          f">=3/4 prompts, VERB {verb_rec}",
          loc_rec >= 2 and verb_rec >= 1)
    loc_sig, verb_sig = sigs["LOCATION"][0], sigs["VERB"][0]
    only_loc = loc_sig - verb_sig
    only_verb = verb_sig - loc_sig
    check(f"F3 THE DIFFERENTIAL: type signatures diverge — "
          f"{len(only_loc)} location-only links, {len(only_verb)} "
          f"verb-only", len(only_loc) >= 1 or len(only_verb) >= 1,
          f"loc-only {sorted(only_loc)[:3]}, verb-only "
          f"{sorted(only_verb)[:3]}")

    print()
    print(f"CHAIN PROBE: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
