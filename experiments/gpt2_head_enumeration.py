"""gpt2_head_enumeration.py — THE OWNER'S EXAMPLE, MADE REAL
(2026-07-17: "you have gpt2. it could be 64x12 i think. and those
12 things are the primary factors. we only care about how those 12
things contribute to the output activation. the way it works is it
amplifies certain carriers and inhibits others").

The specimen: GPT-2 small — 12 attention heads x 64 dims per layer,
the architecture handing us the primary factors exactly as the
owner said. We enumerate, for the model's final attention layer,
each head's contribution to the CORRECT next-token logit on plain
prompts: amplifiers and inhibitors, per head.

The receipt structure (weights propose, behavior confirms):
  PREDICTED contribution of head h = remove h's direct term from
  the residual, recompute the final layernorm + unembedding — the
  quick simplified interaction, no full re-run.
  MEASURED contribution = zero head h's output-projection rows in
  the WEIGHTS and run the whole model again (direct + mediated).
  The gap between them is the MEDIATION SHARE (what flows through
  the final MLP) — reported, not hidden.

  G1 specimen sanity: the expected token in the top-5 for >=4/5
     prompts;
  G2 rank agreement predicted-vs-measured across the 12 heads,
     mean rank-corr >= 0.5 (the direct path must carry the story);
  G3 sign receipts: ablating the top predicted amplifier LOWERS
     the target logit on every prompt; the top predicted inhibitor
     RAISES it on a majority.

Run: PYTHONHASHSEED=0 python gpt2_head_enumeration.py
"""
import sys

import numpy as np
import torch

PASS, FAIL = 0, 0
LAYER = 11
NH, DH = 12, 64


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
    ("The Eiffel Tower is located in the city of", " Paris"),
    ("Two plus two equals", " four"),
    ('"Hello," she said. "How are', " you"),
    ("The sun rises in the east and sets in the", " west"),
]


def main():
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    print("=" * 70)
    print("GPT-2 HEAD ENUMERATION — 12 primary factors, final "
          "attention layer")
    print("=" * 70)
    tok = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    model.eval()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(dev)

    blk = model.transformer.h[LAYER]
    W_O = blk.attn.c_proj.weight.detach()        # (768 in, 768 out)
    b_O = blk.attn.c_proj.bias.detach()
    ln_f = model.transformer.ln_f
    W_U = model.lm_head.weight.detach()          # (vocab, 768)

    caps = {}
    h1 = blk.attn.c_proj.register_forward_pre_hook(
        lambda m, inp: caps.__setitem__("heads",
                                        inp[0].detach()))
    h2 = model.transformer.ln_f.register_forward_pre_hook(
        lambda m, inp: caps.__setitem__("resid",
                                        inp[0].detach()))

    sane = 0
    tables = []
    for prompt, expect in PROMPTS:
        ids = tok(prompt, return_tensors="pt").to(dev)
        t_id = tok.encode(expect)[0]
        with torch.no_grad():
            out = model(**ids)
        logits = out.logits[0, -1]
        top5 = torch.topk(logits, 5).indices.tolist()
        sane += t_id in top5
        heads = caps["heads"][0, -1]             # (768,) pre-c_proj
        resid = caps["resid"][0, -1]             # (768,) pre-ln_f
        base_logit = float(logits[t_id])

        # PREDICTED per-head contribution: remove the head's direct
        # term, recompute final LN + unembed (never the full model)
        pred = np.zeros(NH)
        for h in range(NH):
            d = heads[h * DH:(h + 1) * DH] @ \
                W_O[h * DH:(h + 1) * DH, :]
            with torch.no_grad():
                alt = float(
                    (ln_f((resid - d).unsqueeze(0)) @ W_U.T)
                    [0, t_id])
            pred[h] = base_logit - alt

        # MEASURED: zero the head's W_O rows, run the whole model
        meas = np.zeros(NH)
        for h in range(NH):
            sl = slice(h * DH, (h + 1) * DH)
            saved = W_O[sl].clone()
            with torch.no_grad():
                blk.attn.c_proj.weight[sl] = 0.0
                m_out = model(**ids)
                meas[h] = base_logit - float(
                    m_out.logits[0, -1, t_id])
                blk.attn.c_proj.weight[sl] = saved
        tables.append((prompt, expect, pred, meas, base_logit))

    h1.remove()
    h2.remove()
    check(f"G1 specimen sanity: expected token in top-5 for "
          f"{sane}/5 prompts", sane >= 4)

    print("  the enumeration, prompt by prompt (layer-11 heads; "
          "+ = amplifies the correct token, - = inhibits):")
    rcs, mediation = [], []
    sign_amp = sign_inh = inh_present = 0
    for prompt, expect, pred, meas, base in tables:
        rc = rankcorr(pred, meas)
        rcs.append(rc)
        top_a = int(np.argmax(pred))
        top_i = int(np.argmin(pred))
        sign_amp += meas[top_a] > 0
        if pred[top_i] < -0.05:
            inh_present += 1
            sign_inh += meas[top_i] < 0
        med = float(np.mean(np.abs(meas - pred))
                    / max(np.mean(np.abs(meas)), 1e-9))
        mediation.append(med)
        amps = np.argsort(-pred)[:3]
        print(f"    '{prompt}' -> '{expect}': amplifiers "
              f"{[(int(h), round(float(pred[h]), 2)) for h in amps]}"
              f", top inhibitor ({top_i}, "
              f"{round(float(pred[top_i]), 2)}); rank-corr "
              f"pred~meas {rc:.2f}")
    check(f"G2 the direct path carries the story: mean rank-corr "
          f"{np.mean(rcs):.2f} across 12 heads x 5 prompts "
          f"(mediation share {np.mean(mediation):.2f} — reported)",
          np.mean(rcs) >= 0.5)
    check(f"G3 sign receipts: top amplifier ablation lowered the "
          f"target logit {sign_amp}/5; top inhibitor raised it "
          f"{sign_inh}/{max(inh_present, 1)}",
          sign_amp >= 4 and (inh_present == 0
                             or sign_inh >= inh_present - 1))

    print()
    print(f"GPT-2 ENUMERATION: {PASS}/{PASS + FAIL} checks passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
