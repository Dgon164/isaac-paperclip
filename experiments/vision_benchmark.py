# -*- coding: utf-8 -*-
"""VISION BENCHMARK (2026-07-10) — how the vision side works, measured.
All numbers COMPLETE numbers (accuracy against the whole task).

V1  MNIST recognition, per channel + fused + trained readout
    (the standing road; train 200/class, test 1000 unseen)
V2  THE SYMBOL TEST (owner, 2026-07-10: "7 should be '7'"):
    concepts trained ONLY on handwriting are shown PRINTED digits in
    10 fonts they have never seen. A channel that carries the CONCEPT
    (topology, bones, shape) should survive the substrate change; a
    channel that memorized handwriting statistics (density, exemplars)
    should collapse. This measures concept-vs-memorization directly.
V3  Shape language on real glyphs: "the 8 is two circles" — % of test
    8s described with 2 holes; 0s with 1 hole; 1s with 0 holes.
V4  Shape vocabulary on clean synthetic shapes (ring/disc/frame/rect/
    line), % of kinds named correctly.
Also recorded: the string tie as it stands — outbound label only; NO
inbound string channel (nothing doors from "7" onto concept:7).
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

t0 = time.time()
i = Isaac()
i.learn_glyphs(X[tr_idx], y[tr_idx])
i.train_readout(X[tr_idx], y[tr_idx])
classes = i.net.get_meta("crystal", "glyph_classes")
print(f"trained: all channels onto one set of concept nodes + readout "
      f"({len(tr_idx)} glyphs)  [{time.time()-t0:.0f}s]\n")

CHANNELS = ("topology", "bones", "dynamics", "density", "exemplar")

def bench(images, labels, title):
    hits = {k: 0 for k in CHANNELS}
    hits["FUSED+readout"] = 0
    n = len(images)
    for im, truth in zip(images, labels):
        got, posts = i.recognize_glyph(im)
        if got == truth:
            hits["FUSED+readout"] += 1
        for k in CHANNELS:
            p = posts.get(k)
            if p is not None and classes[int(np.argmax(p))] == truth:
                hits[k] += 1
    print(f"{title} (n={n}, complete numbers):")
    for k in CHANNELS + ("FUSED+readout",):
        print(f"  {k:14s}: {hits[k]/n*100:5.1f}%")
    return hits, n

# ── V1: the standing road ───────────────────────────────────────────
t0 = time.time()
h1, n1 = bench(X[te_idx], y[te_idx], "V1 MNIST handwritten test")
print(f"  [{time.time()-t0:.0f}s]\n")

# ── V2: the symbol test — printed digits, never seen ────────────────
from PIL import Image, ImageDraw, ImageFont
FONTS = ["arial.ttf", "times.ttf", "cour.ttf", "calibri.ttf", "georgia.ttf",
         "verdana.ttf", "tahoma.ttf", "consola.ttf", "comic.ttf",
         "segoeui.ttf"]

def render_digit(ch, fontfile, size=48):
    font = ImageFont.truetype(os.path.join("C:/Windows/Fonts", fontfile), size)
    img = Image.new("L", (96, 96), 0)
    dr = ImageDraw.Draw(img)
    x0, y0, x1, y1 = dr.textbbox((0, 0), ch, font=font)
    dr.text((48 - (x0 + x1) / 2, 48 - (y0 + y1) / 2), ch, fill=255, font=font)
    a = np.asarray(img, float)
    ys, xs = np.where(a > 20)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # MNIST style: longest side -> 20 px, centered by mass in 28x28
    hgt, wid = a.shape
    s = 20.0 / max(hgt, wid)
    im2 = Image.fromarray(a.astype(np.uint8)).resize(
        (max(1, int(round(wid * s))), max(1, int(round(hgt * s)))),
        Image.BILINEAR)
    a = np.asarray(im2, float)
    out = np.zeros((28, 28))
    ys, xs = np.mgrid[:a.shape[0], :a.shape[1]]
    m = a.sum()
    cy, cx = (ys * a).sum() / m, (xs * a).sum() / m
    ty, tx = int(round(14 - cy)), int(round(14 - cx))
    for yy in range(a.shape[0]):
        for xx in range(a.shape[1]):
            py, px = yy + ty, xx + tx
            if 0 <= py < 28 and 0 <= px < 28:
                out[py, px] = a[yy, xx]
    return out

font_imgs, font_labels = [], []
for f in FONTS:
    for c in range(10):
        font_imgs.append(render_digit(str(c), f))
        font_labels.append(c)
t0 = time.time()
h2, n2 = bench(np.array(font_imgs), np.array(font_labels),
               "V2 SYMBOL TEST — printed fonts, never seen")
print(f"  [{time.time()-t0:.0f}s]")
print("  (concept channels should survive the substrate change;")
print("   memorized-statistics channels should collapse)\n")

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

# ── the string tie, as it stands ────────────────────────────────────
got, _ = i.recognize_glyph(X[te_idx[0]])
print("string tie audit:")
print(f"  outbound: recognize_glyph returns the label object "
      f"{got!r} (type {type(got).__name__}) — the symbol exists at the "
      f"output, as an opaque training label")
print("  inbound:  NO channel doors from the string \"7\" onto concept:7 "
      "— named gap (polysemy is one-directional today)")
