# Isaac alpha — demo MVP checklist & run-sheet

**Audience:** potential users (practical, hands-on).
**Hero:** tabular law-discovery first, with real time-series as the "and it works on real messy data too" moment.
**Pitch:** *Give it data → it finds a readable law, shows the fit, tells you how sure it is, and says what it can't explain.* The hook is what a black box **can't** do: legible + honest + it refuses when it should.

## How to run
```
$env:PYTHONUTF8=1
.venv\Scripts\python.exe ui\isaac_ui.py      # then open http://127.0.0.1:8674
```
Requires the real datasets in `research/data/` (`co2_mlo.csv`) — already present on the demo laptop.

## The demo flow (click order + what to say)
The four preset chips across the top run the whole story in four clicks. Each click loads real
data and finds the law automatically, with a plot.

1. **Kepler's law** — *"Paste any table. Here's real NASA orbital data."* → **✓ Understood**,
   `T = a^1.5`, R²≈1.0, data + fitted curve. *"It didn't look this up — it derived it, and it's
   a readable equation, not a black box."*
2. **CO₂ rising (real)** — *"Now real, messy climate data."* → **✓ Understood**, R²≈0.94, the rise
   as a legible law over a real scatter. *"Same engine, real-world noise, still a law you can read."*
3. **CO₂ seasons (real)** — *"The same data, the seasonal part — the planet's yearly breath."* →
   **✓ Understood**, R²≈0.96, a clean repeating wave. *"It found the cycle."*
4. **Pure noise → refusal** — *"And when there's nothing there…"* → **— No rule found**, no fake
   equation. *"This is the part a black box never does. It refuses to invent a law. Confident-wrong
   is the only real failure, and it won't do it."*

Close on: *"Legible, honest, and it knows what it doesn't know — on your data, on a laptop, no GPU."*

## Checklist
### P0 — must-have core (DONE 2026-07-07)
- [x] One-click preset datasets (Kepler, CO₂ rise, CO₂ seasons, noise→refusal)
- [x] Live plot in Discover (data scatter + fitted-law curve; predicted-vs-actual for multi-feature)
- [x] Consumer framing pass (title + pitch, lead with Discover, dev console collapsed at bottom)
- [x] Full-flow smoke test — all 4 presets verified through the live HTTP server (verdict + plot)

### P1 — the differentiator (if time before demo)
- [ ] Honesty made explicit: separate cards for *what I'm sure of* / *what I can't explain yet* /
      *what to measure next* (the probe). The rival→probe line already renders; promote it.
- [ ] A second refusal that's real data, not synthetic (e.g. a column pair with no relationship).
- [ ] Copy polish: plain-language verdict subtitles (mostly done in `VMAP`).

### P2 — post-demo
- [ ] Time-series mode proper: trend + cycle + "sticky leftover" cards (needs clock→UI wiring).
- [ ] File upload (drag-drop CSV); progress spinner for long discovers; mobile layout.
- [ ] Guard: presets that need `research/data/` should show a friendly message if a file is absent.

## Known rough edges (be ready for)
- The CO₂-rise equation has an `exp` term (honest fit of a slightly super-linear curve, R²=0.94) —
  it reads a little busy. Fine to say "the rise, captured as a law" and point at the plot.
- CO₂-seasons x-axis is "position within the year" (radians) — the *shape* (a wave) is the point.
- Only single-predictor datasets get the pretty x–y plot; multi-column data shows predicted-vs-actual.
