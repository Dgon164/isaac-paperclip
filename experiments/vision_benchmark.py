# -*- coding: utf-8 -*-
"""VISION BENCHMARK (2026-07-10) — how the vision side works, measured.
All numbers COMPLETE numbers (accuracy against the whole task).

V1  MNIST recognition, per channel + fused + trained readout
    (the standing road; train 200/class, test 1000 unseen)
V2  THE SYMBOL TEST (owner: "7 should be '7'"): concepts trained ONLY
    on handwriting shown PRINTED digits in 5 fonts nobody trained on.
V1r/V2r  THE PRINT-AND-OVERLAY CHANNEL (owner, 2026-07-10: "just print
    and overlay the nearest font number"): same model + symbol forms
    rendered from 5 DIFFERENT fonts (template fonts and test fonts are
    disjoint). Registered predictions: render tops V2; fused V2 rises;
    V1 fused does not fall.
V5  THE BADLY-DRAWN TEST (owner: "at worst... see this is a badly
    drawn 7 vs a bunch of other badly drawn numbers"): the 150 WORST
    drawn test glyphs (lowest overlay similarity — badness is now a
    measured number), fused accuracy without vs with render.
V3  Shape language on real glyphs (8=two holes, 0=one, 1=zero).
V4  Shape vocabulary on clean synthetic shapes.
Plus the string-tie audit: inbound polysemy now exists
(symbol:<c> -names-> concept:<c>) and overlay_delta speaks the delta.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from isaac import Isaac

rng = np.random.default_rng(8)
from sklearn.datasets import fetch_openml
d = fetch_openml("mnist_784", version=1, as_frame=False, parser="liac-arff")
X = d.data.reshape(-1, 28, 28)
y = d.target.astype(int)

tr_idx = np.concatenate([np.where(y[:40000] == c)[0][:200] for c in range(10)])
te_idx = rng.choice(np.where(np.arange(len(y)) > 40000)[0], 1000, replace=False)

from PIL import Image, ImageDraw, ImageFont
TEMPLATE_FONTS = ["arial.ttf", "times.ttf", "cour.ttf", "calibri.ttf",
                  "georgia.ttf"]
TEST_FONTS = ["verdana.ttf", "tahoma.ttf", "consola.ttf", "comic.ttf",
              "segoeui.ttf"]

def render_digit(ch, fontfile, size=48):
    """Raw render only — the ENGINE does the normalization now."""
    font = ImageFont.truetype(os.path.join("C:/Windows/Fonts", fontfile), size)
    img = Image.new("L", (96, 96), 0)
    dr = ImageDraw.Draw(img)
    x0, y0, x1, y1 = dr.textbbox((0, 0), ch, font=font)
    dr.text((48 - (x0 + x1) / 2, 48 - (y0 + y1) / 2), ch, fill=255, font=font)
    return np.asarray(img, float)

symbol_forms = {c: [render_digit(str(c), f) for f in TEMPLATE_FONTS]
                for c in range(10)}

CHANNELS = ("topology", "bones", "dynamics", "density", "exemplar",
            "render")

def bench(i, classes, images, labels, title):
    hits = {k: 0 for k in CHANNELS}
    hits["FUSED+readout"] = 0
    n = len(images)
    wrong = []
    for im, truth in zip(images, labels):
        got, posts = i.recognize_glyph(im)
        if got == truth:
            hits["FUSED+readout"] += 1
        else:
            wrong.append((truth, got))
        for k in CHANNELS:
            p = posts.get(k)
            if p is not None and classes[int(np.argmax(p))] == truth:
                hits[k] += 1
    print(f"{title} (n={n}, complete numbers):")
    for k in CHANNELS + ("FUSED+readout",):
        if hits[k] or k in ("FUSED+readout",):
            print(f"  {k:14s}: {hits[k]/n*100:5.1f}%")
    return hits, n, wrong

# ── model A: without symbol forms (the standing road) ───────────────
t0 = time.time()
iA = Isaac()
# font test set: the 5 fonts NO model trained on, passed through the
# engine's own glyph normalizer (recognition expects 28x28)
font_imgs = np.array([iA._norm_glyph(render_digit(str(c), f)) * 255
                      for f in TEST_FONTS for c in range(10)])
font_labels = np.array([c for f in TEST_FONTS for c in range(10)])
iA.learn_glyphs(X[tr_idx], y[tr_idx])
iA.train_readout(X[tr_idx], y[tr_idx])
clA = iA.net.get_meta("crystal", "glyph_classes")
print(f"model A trained (no symbol forms)  [{time.time()-t0:.0f}s]")
t0 = time.time()
h1, n1, _ = bench(iA, clA, X[te_idx], y[te_idx],
                  "V1  MNIST handwritten, WITHOUT render")
h2, n2, _ = bench(iA, clA, font_imgs, font_labels,
                  "V2  printed (5 held-out fonts), WITHOUT render")
print(f"  [{time.time()-t0:.0f}s]\n")

# ── model B: + print-and-overlay channel (5 template fonts) ─────────
t0 = time.time()
i = Isaac()
i.learn_glyphs(X[tr_idx], y[tr_idx], symbol_forms=symbol_forms)
i.train_readout(X[tr_idx], y[tr_idx])
classes = i.net.get_meta("crystal", "glyph_classes")
w = i.net.get_meta("crystal", "glyph_weights")
print(f"model B trained (+ symbol forms, template fonts disjoint from "
      f"test fonts)  [{time.time()-t0:.0f}s]")
print("  measured channel weights: " +
      ", ".join(f"{k} {v:.2f}" for k, v in sorted(w.items(),
                                                  key=lambda kv: -kv[1])))
t0 = time.time()
h1r, _, _ = bench(i, classes, X[te_idx], y[te_idx],
                  "V1r MNIST handwritten, WITH render")
h2r, _, _ = bench(i, classes, font_imgs, font_labels,
                  "V2r printed (5 held-out fonts), WITH render")
print(f"  [{time.time()-t0:.0f}s]\n")

# ── V5: the badly-drawn test ────────────────────────────────────────
t0 = time.time()
sims = []
for ix in te_idx:
    r = i.overlay_delta(X[ix], label=int(y[ix]))
    sims.append(r["similarity"] if r else 0.0)
worst = np.argsort(sims)[:150]          # measured badness, not opinion
okA = sum(1 for k in worst
          if iA.recognize_glyph(X[te_idx[k]])[0] == y[te_idx[k]])
okB = sum(1 for k in worst
          if i.recognize_glyph(X[te_idx[k]])[0] == y[te_idx[k]])
print(f"V5 the 150 WORST-drawn test glyphs (lowest overlay similarity, "
      f"median badness {np.median([sims[k] for k in worst]):.2f}):")
print(f"  fused WITHOUT render: {okA/150*100:.1f}%")
print(f"  fused WITH    render: {okB/150*100:.1f}%")
d0 = i.overlay_delta(X[te_idx[int(worst[0])]])
print(f"  worst glyph, spoken: truth {y[te_idx[int(worst[0])]]}, overlay "
      f"says {d0['label']} (sim {d0['similarity']}, extra ink "
      f"{d0['extra_ink']*100:.0f}%, missing ink "
      f"{d0['missing_ink']*100:.0f}%)  [{time.time()-t0:.0f}s]\n")

# ── V3: shape language on real glyphs ───────────────────────────────
t0 = time.time()
want_holes = {8: 2, 0: 1, 1: 0}
print("V3 shape language on handwritten glyphs (complete numbers):")
for digit, holes in want_holes.items():
    idx = np.where(y[te_idx] == digit)[0]
    imgs = X[te_idx][idx]
    ok = tot = 0
    for im in imgs:
        r = i.describe_shape(im)
        tot += 1
        if r is not None and r["n_holes"] == holes:
            ok += 1
    print(f"  '{digit}' described with {holes} hole(s): {ok}/{tot} "
          f"({ok/max(tot,1)*100:.1f}%)")
print(f"  [{time.time()-t0:.0f}s]\n")

# ── V4: shape vocabulary on clean synthetic shapes ──────────────────
def draw(kind, size=28):
    im = np.zeros((size, size))
    yy, xx = np.mgrid[:size, :size]
    cy = cx = size / 2 + rng.uniform(-2, 2)
    if kind == "disc":
        r = rng.uniform(6, 10)
        im[(yy - cy) ** 2 + (xx - cx) ** 2 <= r ** 2] = 1
    elif kind == "ring":
        r = rng.uniform(7, 10)
        d2 = (yy - cy) ** 2 + (xx - cx) ** 2
        im[(d2 <= r ** 2) & (d2 >= (r - 2.5) ** 2)] = 1
    elif kind == "rect":
        h, w = rng.uniform(6, 10), rng.uniform(9, 12)
        im[(np.abs(yy - cy) <= h) & (np.abs(xx - cx) <= w)] = 1
    elif kind == "frame":
        h, w = rng.uniform(7, 10), rng.uniform(9, 12)
        inside = (np.abs(yy - cy) <= h) & (np.abs(xx - cx) <= w)
        inner = (np.abs(yy - cy) <= h - 2.5) & (np.abs(xx - cx) <= w - 2.5)
        im[inside & ~inner] = 1
    elif kind == "line":
        ang = rng.uniform(0, np.pi)
        t = np.linspace(-10, 10, 200)
        py = (cy + t * np.sin(ang)).astype(int)
        px = (cx + t * np.cos(ang)).astype(int)
        m = (py >= 0) & (py < size) & (px >= 0) & (px < size)
        im[py[m], px[m]] = 1
    return im

t0 = time.time()
kinds = ["disc", "ring", "rect", "frame", "line"]
ok = tot = 0
per = {k: [0, 0] for k in kinds}
for k in kinds:
    for _ in range(30):
        r = i.describe_shape(draw(k))
        tot += 1; per[k][1] += 1
        got = None
        if r is not None and len(r["parts"]) >= 1:
            main = max(r["parts"], key=lambda p: p.get("area", p.get("n", 0)))
            got = main["kind"]
        if got == k:
            ok += 1; per[k][0] += 1
print("V4 shape vocabulary on clean synthetic shapes:")
for k in kinds:
    print(f"  {k:6s}: {per[k][0]}/{per[k][1]}")
print(f"  TOTAL : {ok}/{tot} ({ok/tot*100:.1f}%)  [{time.time()-t0:.0f}s]\n")

# ── the string tie, after the build ─────────────────────────────────
got, _ = i.recognize_glyph(X[te_idx[0]])
sym = i.net.get_meta("symbol:7", "string")
print("string tie audit:")
print(f"  outbound: recognize_glyph returns {got!r} — the label")
print(f"  inbound:  symbol:7 (string {sym!r}) -names-> concept:7 — the "
      f"name now reaches the concept; its rendered forms vote as the "
      f"render channel (polysemy closed in both directions)")
