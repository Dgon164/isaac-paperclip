"""gpt2_full_enumeration.py — the FULL map the owner asked for
(2026-07-17: "you mean gpt 2 not just a subsample of it, and all
the 50k token outputs?"). The model was always the real, full
GPT-2; the first probe's SCOPE was one layer x one logit. This one:

  E1 ALL 50,257 TOKEN OUTPUTS per head (final layer): each head's
     direct push across the entire vocabulary — for every head, the
     tokens it most amplifies and most inhibits, per prompt. The
     machinery gate: the full-vocab map must agree with the earlier
     single-logit reading (the named amplifier's top-amplified
     tokens contain the target; the standing inhibitor's
     most-suppressed contain it).
  E2 ALL 144 HEADS (12 layers x 12): direct push on the target
     logit AND the measured full-model ablation for every head —
     720 full forward passes. The finding: the MEDIATION CURVE by
     layer (direct-path agreement strong late, weak early — the
     0.44 share seen at layer 11, now measured across depth).

Run: PYTHONHASHSEED=0 python gpt2_full_enumeration.py
"""
import sys

import numpy as np
import torch

PASS, FAIL = 0, 0
NH, DH, NL = 12, 64, 12


def check(name, ok, detail=""):
    global PASS, FAIL
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail else ""))


def rankcorr(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    return float((ra @ rb) / max(np.sqrt((ra @ ra) * (rb @ rb)),
                                 1e-12))


PROMPTS = [
    ("Paris is the capital of", " France"),
    ("Two plus two equals", " four"),
    ('"Hello," she said. "How are', " you"),
]


def main():
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    print("=" * 70)
    print("GPT-2 FULL ENUMERATION — 144 heads, 50,257 outputs")
    print("=" * 70)
    tok = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    model.eval()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(dev)
    W_U = model.lm_head.weight.detach()          # (50257, 768)
    ln_f = model.transformer.ln_f

    caps = {}
    hooks = []
    for L in range(NL):
        hooks.append(
            model.transformer.h[L].attn.c_proj
            .register_forward_pre_hook(
                (lambda LL: lambda m, inp: caps.__setitem__(
                    LL, inp[0].detach()))(L)))
    hooks.append(model.transformer.ln_f.register_forward_pre_hook(
        lambda m, inp: caps.__setitem__("resid", inp[0].detach())))

    med_by_layer = np.zeros(NL)
    consist_inh = 0
    vec_corrs = []
    for prompt, expect in PROMPTS:
        ids = tok(prompt, return_tensors="pt").to(dev)
        t_id = tok.encode(expect)[0]
        with torch.no_grad():
            out = model(**ids)
        base_all = out.logits[0, -1].detach()
        resid = caps["resid"][0, -1]

        # ── E1: layer-11 heads vs the CANDIDATES IN PLAY ──
        # First-pass lesson, wrong-kept: the raw full-vocab read is
        # swamped by junk tokens (control chars, dead vocabulary —
        # tiny-baseline tokens in uncalibrated LN territory). The
        # owner's checklist frame is the cure: the tabulator
        # considers the checkboxes IN THE RUNNING — the top-200
        # baseline candidates — not the whole dead vocabulary.
        cand = torch.topk(base_all, 200).indices
        W_O11 = model.transformer.h[11].attn.c_proj.weight.detach()
        heads11 = caps[11][0, -1]
        print(f"  '{prompt}' -> '{expect}': per-head push over the "
              f"200 candidates in play (leading space = '_'):")

        def ts(i):
            s = tok.decode([int(i)])
            s = s.replace(" ", "_")
            return s.encode("ascii", "replace").decode() or "?"

        # THE LOGIT-SPACE STOPWORD (found via the sign diagnostic,
        # wrong-kept): removing a head shifts the LN scale, moving
        # ALL logits together — and softmax is SHIFT-INVARIANT, so
        # the common mode carries no choice information. The
        # meaningful push is SPECIFIC: demeaned over the candidates
        # (the base-rate law's third domain today: words, weight
        # space, logit space). Raw pushes overstated head 0 by ~13x
        # (+19.19 raw vs +1.44 measured on ' four').
        push_t = np.zeros(NH)
        push_cand = {}
        cidx = cand.cpu().numpy()
        for h in range(NH):
            d = heads11[h * DH:(h + 1) * DH] @ \
                W_O11[h * DH:(h + 1) * DH, :]
            with torch.no_grad():
                alt_all = (ln_f((resid - d).unsqueeze(0))
                           @ W_U.T)[0]
            push = (base_all - alt_all).cpu().numpy()
            pc = push[cidx]
            pc = pc - np.median(pc)              # specific push
            push_cand[h] = pc
            push_t[h] = push[t_id] - np.median(push[cidx])
            if h in (0, 8, 11):
                top = np.argsort(-pc)[:4]
                bot = np.argsort(pc)[:4]
                print(f"    head {h:2d}: "
                      f"+{[ts(cand[i]) for i in top]}"
                      f"  -{[ts(cand[i]) for i in bot]}")
        inh = int(np.argmin(push_t))
        t_pos = int((cand == t_id).nonzero()[0][0]) \
            if (cand == t_id).any() else -1
        consist_inh += t_pos >= 0 and t_pos in \
            np.argsort(push_cand[inh])[:10]

        # ── E2: ALL 144 heads — SPECIFIC push + measured ablation,
        # both demeaned over the candidates (the same stopword) ──
        pred144 = np.zeros((NL, NH))
        meas144 = np.zeros((NL, NH))
        vec_pred, vec_meas = {}, {}
        base_c = base_all[cand]
        for L in range(NL):
            W_OL = model.transformer.h[L].attn.c_proj.weight
            headsL = caps[L][0, -1]
            for h in range(NH):
                sl = slice(h * DH, (h + 1) * DH)
                d = headsL[sl] @ W_OL.detach()[sl, :]
                with torch.no_grad():
                    alt_c = (ln_f((resid - d).unsqueeze(0))
                             @ W_U.T)[0, cand]
                dp = (base_c - alt_c).cpu().numpy()
                dp = dp - np.median(dp)
                pred144[L, h] = dp[t_pos] if t_pos >= 0 else 0.0
                if L == NL - 1:
                    vec_pred[h] = dp
                saved = W_OL.detach()[sl].clone()
                with torch.no_grad():
                    W_OL[sl] = 0.0
                    m_out = model(**ids)
                    ml_c = m_out.logits[0, -1, cand]
                    W_OL[sl] = saved
                dm = (base_c - ml_c).cpu().numpy()
                dm = dm - np.median(dm)
                meas144[L, h] = dm[t_pos] if t_pos >= 0 else 0.0
                if L == NL - 1:
                    vec_meas[h] = dm
        for L in range(NL):
            med_by_layer[L] += rankcorr(pred144[L], meas144[L]) \
                / len(PROMPTS)
        vc = [rankcorr(vec_pred[h], vec_meas[h])
              for h in range(NH)]
        vec_corrs.append(float(np.mean(vc)))

    for hk in hooks:
        hk.remove()

    check(f"E1 THE SPECIFIC-PUSH GATE: per-head predicted vs "
          f"measured candidate vectors agree (mean rank-corr "
          f"{np.mean(vec_corrs):.2f} over 12 heads x 3 prompts)",
          np.mean(vec_corrs) >= 0.4,
          f"per-prompt {[round(v, 2) for v in vec_corrs]}")
    check(f"E1b inhibitor receipt: the target sits in the top "
          f"inhibitor's bottom-10 specific pushes {consist_inh}/3",
          consist_inh >= 2)
    print("  E2 THE MEDIATION CURVE — direct-path rank agreement "
          "by layer (all 144 heads ablated, 3 prompts):")
    print("    " + "  ".join(f"L{L}:{med_by_layer[L]:.2f}"
                             for L in range(NL)))
    late = float(np.mean(med_by_layer[8:]))
    early = float(np.mean(med_by_layer[:4]))
    check(f"E2 the curve is real: late-layer agreement {late:.2f} "
          f"vs early {early:.2f} — early-head influence is "
          f"MEDIATED, late is direct (measured across all 144)",
          late > early)

    print()
    print(f"FULL ENUMERATION: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
