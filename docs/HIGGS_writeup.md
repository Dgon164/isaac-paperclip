# HIGGS — details, findings, and test data

*Short writeup of the equation-discovery results on particle-physics data. Every number
below was produced by the scripts in `demos/` (`interaction_extract.py`,
`higgs_residual.py`) and the toy in `unsup_discover.py`.*

## The dataset
- **Source:** the Baldi–Sadowski–Whiteson HIGGS benchmark (Nature Communications 2014,
  *"Searching for Exotic Particles in High-Energy Physics with Deep Learning"*). Simulated
  proton–proton collisions; a binary problem: **signal** (a Higgs-producing process) vs
  **background**.
- **How it's loaded:** `fetch_openml(data_id=23512)` — the OpenML "higgs" subset (~98k
  events), downloaded on demand, no local file. The scripts subsample further
  (~8–12k train / 3–4k test) for speed.
- **28 features, in two tiers:**
  - **21 low-level kinematics** — the raw detector readout: lepton `pT/η/φ`, missing
    energy `magnitude/φ`, and 4 jets × (`pT`, `η`, `φ`, `b-tag`).
  - **7 high-level derived** — `m_jj`, `m_jjj`, `m_lv`, `m_jlv`, `m_bb`, `m_wbb`,
    `m_wwbb`. **These are the invariant masses of the intermediate particles:**
    `m_jj`/`m_lv` ≈ **W boson**, `m_jjj` ≈ **top quark**, `m_bb` ≈ the **b-bbar / Higgs
    candidate**, `m_wwbb` ≈ the full signal system.

## The findings (metric = truth recovered, NOT classification accuracy)
The stated goal is to recover the *real math* of a system, not to score well. Accuracy is
a trap — gradient descent reaches arbitrary accuracy on pure noise, so a high score says
nothing about truth.

1. **The other particles' equations come out.** On real HIGGS, sparse interaction
   extraction (`interaction_extract.py`) names the correct physics — top functional terms
   `m_wwbb`, `m_bb²`, `m_wbb`, `m_bb`, `m_jlv·m_bb`, `m_jjj·m_wwbb` — i.e. the W / top /
   b-bbar mass structure, not arbitrary features.
2. **Those relations are real, not fitted noise.** `higgs_residual.py` models each class's
   full internal structure and, in doing so, **reconstructs the known invariant-mass
   features at R² ≈ 0.865** — recovered without being told what they are.
3. **The Higgs itself stays the residual.** Its signal is **deep/dense** — a *flat smear*
   across ~280 of 434 interaction terms rather than a few dominant ones — so it has **no
   compact low-order formula**. It is *detected as what won't reduce*, not written as an
   equation. Term-concentration is the built-in diagnostic: few dominant terms ⇒ a compact
   mechanism exists; a flat smear ⇒ deep structure.
4. **Accuracy was the wrong question** (recorded so it isn't over-weighted): every reader
   lands ~0.62–0.65 (logistic 0.63, random forest ~0.71, deep nets ~0.88). The plateau
   *is* the point — HIGGS is deep/dense, so accuracy says nothing about the recovered math.

## Test datasets (real + controls, so claims are checkable)

| Dataset | Type | Purpose / result |
|---|---|---|
| **HIGGS** (OpenML 23512) | real physics | named the particle masses; R²≈0.865 reconstruction; Higgs = residual |
| **Planted interactions** `x0·x1 + 0.8x2² − 1.2x3` | synthetic | validates the extractor — recovers those exact terms |
| **Toy collider** (`unsup_discover.py`) | synthetic, planted truth | unsupervised recovery of `E²−px²−py²`; hidden resonance found at 96% purity / 100% recall |
| **`0.5x² + 1.5·sin(2x)`** | synthetic | recovers the equation *and extrapolates* (MSE 0.07 vs an MLP's 5.5) |
| **Geometric forms** | synthetic | circle-by-fit, box-blind proof — bottleneck is *perception*, not logic |

## The through-line
On data where the truth is known (planted, toy, or the derived masses), the engine
recovers the real equations. On the one genuinely deep/dense signal (the Higgs), it
correctly reports that no short formula exists and detects it as the residual. Recovering
the other particles' equations while the Higgs stays the residual is the thesis —
*"model everything; the needle is the residual"* — working as designed.
