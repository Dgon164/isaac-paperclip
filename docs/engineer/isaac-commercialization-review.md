# Isaac Commercialization — Consolidated Review & Research Agenda
*Compiled 2026-07-17. Filed to the repo 2026-07-18 from the owner's dev-handoff bundle.*

---

## Part 1 — What's been decided (the settled architecture)

### 1. Money handling
- **Payments are fully outsourced.** Stripe Checkout + Billing (Link/Apple Pay/Google Pay ride along automatically) or a merchant-of-record (Paddle, Lemon Squeezy) that also absorbs global sales tax/VAT. Card data never touches WTT servers.
- **Patreon is an acceptable v0 bootstrap:** OAuth login + membership API + webhooks drive the same license table. Merchant-of-record tax handling included. Known limits: ~8–12% fees, no metering/trials/coupons, platform risk. Migration later = swap the webhook source, not rebuild.
- **WTT's entire billing footprint** is one entitlements table (user id → tier, status, period end), a webhook handler, and API middleware with a grace period. ~150 lines of code.

### 2. Accounts & data custody
- **Auth outsourced** to a hosted provider (Clerk / Supabase / Firebase; Cognito only if AWS-native is worth the pain). Social login; no passwords stored, ever.
- **Processor, not warehouse.** User content is session-scoped: uploaded, processed, flushed — same principle as Isaac's existing scrub pipeline. Persistent storage, if offered, is client-side-encrypted or bring-your-own. Total standing data liability ≈ a mailing list plus license rows.

### 3. Pricing — bootstrap model
- **Byte-quota tiers metered on monthly ingest, not per-file size** (kills file-splitting gaming and the frequency problem). Free tier for small monthly volume; low/mid paid tiers; a self-serve professional tier between the $20 range and enterprise (don't leave the canyon); enterprise in the hundreds+ per month.
- **Value anchor:** the deliverable (model + groupings + outliers + causal decomposition + replication) is the contents of a months-long analytics engagement, not a $20 SaaS. Price tiers can start modest, but the ceiling should reflect the comparable.
- **Charge more than feels comfortable;** grandfather early supporters rather than launching cheap and raising later. Twenty people at $50 is better information than five hundred free users.

### 4. Pricing — mature model (architecturally native)
- **Cost tracks novelty, not volume.** Known structure = fast revalidation, no net change, near-zero cost. Novel lawful structure = one-time compute, condensed root. Incompressible residue = maximum compute AND maximum nodes. Cost and node count correlate by construction.
- **Endgame:** processing priced by surprisal (10ms fast pass = free instant quote), retention priced by *private* node count, the shared commons free. Condense-when-you-can means **bills decline as Isaac understands the data better** — a marketable, one-of-a-kind property.
- **Economies of understanding:** marginal cost falls as Prime grows; a mature Isaac processes common data cheaper than any fresh competitor could. The moat widens with every customer.
- **At maturity, matching is the product** and genuinely novel data is a *supply* — worth discounting or crediting ("known patterns are the service; new patterns earn credit"), aimed exactly at value creators.
- **Subnet split = billing boundary:** commons free, customer pays for nodes that are theirs alone.

### 5. Confidentiality & provenance (the one-way valve)
- **Output = f(client's data), always.** Prime is an accelerator, never a source, in client work. Every claim in a report is evidenced by the client's own upload.
- **Promotion rule (clean-room provenance):** customer data may *point* Isaac at things, but nothing enters Prime without re-derivation from an open, citable, non-customer source. Self-sorting: truly general patterns always find open corroboration; single-customer secrets never can, so they structurally cannot promote.
- **k-plurality:** corroboration must be genuinely independent and plural (two-players-in-a-niche is not "independent"). Applies one level up as well: don't let publishable research directions trace to a single customer trigger (the "direction of search" leak).
- **Bare outputs:** no provenance shipped to clients — they can't distinguish Prime-accelerated recognition from cold derivation. Receipts are kept internally: provenance on-demand (audit, legal, enterprise due diligence), never by default. Not shipped ≠ not kept.
- **Scrubber verification:** turn Isaac's own fingerprinting capability against Prime — adversarial re-identification attempts as a standing test. "Scrubbed" is a tested claim with receipts, not a hope.
- **Two regimes, both covered:** PII/privacy law (persons: GDPR/CCPA) and trade secret/contract law (businesses). "It's just math" is not a defense to either; the duty of confidence is what matters. ToS must speak to both.
- **Enterprise option:** flat no-promotion guarantee (private net only), priced accordingly — with an audit trail no neural-net vendor can offer.

### 6. Positioning & product doctrine
- **"Data processing system, not an AI."** Isaac works the client's datasets, period. Clients don't know what's in Prime; a reconfirmed pattern was already in their data. Sidesteps AI-hype baggage and serves the show-what-not-how disclosure stance.
- **Learn-but-not-use is a product gate, not a limitation.** The day Isaac uses Prime outward is a different product, a different consent story, a different price — sold deliberately, later.
- **Verification by replication, not explanation.** The deliverable is a function; the client can run it. Ritualize **held-out prediction**: withhold a slice, report performance on the unseen slice. "It predicted data Isaac never saw" ends the argument.
- **Correlation, not causation — enforced by report vocabulary.** "Losses concentrate around condition C" / "this reduces the candidate space." Investigation leads, never verdicts; humans corroborate with video, testimony, evidence. Bake into output templates and ToS.

### 7. Named product lanes (from this thread)
- Function/model extraction from datasets (core).
- Forensic anomaly classification: deliberate sabotage vs inept randomness vs noise/external factors — loss prevention, forensic accounting, audit. Whitedoc-ready with synthetic demo data.
- Independent-validation upsell: recurring pattern that fails open-world replication — "would you like independent validation?" Bias warning as a service; revalidation tier-2 surfacing inside the product.
- Bias/collection-fingerprint detection: "your dataset shows signs of selective recording under condition Q" — a deliverable, not a disclaimer.

---

## Part 2 — Open decisions (pending, not blocked)

1. Stripe vs merchant-of-record for the post-Patreon phase (tax burden vs fees).
2. Final tier boundaries and price points; where the professional tier sits between the $20 range and enterprise.
3. Unit of measure: raw bytes vs rows; how to handle format variance (Parquet vs CSV ~10x).
4. Free tier scope vs time-boxed trial (currently leaning free tier, no trial).
5. When/whether to shift from byte quotas to surprisal/node-retention pricing — gated on pool-two telemetry.
6. Enterprise pricing floor and the no-promotion guarantee's premium.

---

## Part 3 — Research agenda

### A. Market data ("pool one" — collectible now, weak signal)
- Scrape competitor pricing pages: Wolfram, Alteryx/Trifacta-class tools, data-cleaning SaaS, LLM tiers, forensic-accounting rates.
- Public dataset statistics (e.g., Kaggle size/type distributions) — what practitioners actually carry.
- Feed the corpus to Isaac; map the market's anchoring structure. Expect vendor guesses, not demand curves.

### B. Launch telemetry ("pool two" — the real signal, exists only after launch)
- Instrumentation schema, per event: dataset size, type, density (nodes/MB), node yield, processing time, tier, conversion, upgrade/churn, quota hits.
- After a few months: hand Isaac his own market dataset; find what actually predicts willingness to pay. Launch prices are the probe, not the answer.

### C. Legal (before first paying customer with data that matters)
- Attorney-drafted ToS covering: confidentiality duty and its exact scope; the open-corroboration promotion policy in plain terms; PII regime AND trade-secret regime; "findings are statistical patterns requiring independent investigation, not determinations of conduct" (forensics lane); enterprise no-promotion clause.
- Review data-processor obligations (GDPR/CCPA processor role fits the processor-not-warehouse posture).
- Sanity-check the "data processing system" framing against current AI-regulation definitions (marketing frame ≠ regulatory exemption).

### D. Technical research (with Isaac)
- **Spurious-correlation methodology:** holdout persistence as the primary test; carrier requirement (no plausible carrier → suspect coincidence; only-plausible-carrier-is-a-third-thing → confounder flag); multiple-comparisons handling; Simpson's-paradox / sampling-structure cases.
- **Collection fingerprints:** detect the sampling process as a generator — rounding signatures, truncation walls, day-of-week holes, shift-change clustering, suspicious smoothness.
- **Adversarial scrubber test:** standing job where Isaac attempts source re-identification against Prime; failures fixed at cause, passes archived as receipts.
- **Fast-pass node estimator:** turn the 10ms pass into the pre-purchase quote ("estimated complexity/nodes before you commit").
- **Holdout ritual:** automatic slice-withholding + unseen-slice performance section in every report.

### E. Validation experiments (cheap, high-information)
- **Concierge phase:** 5–10 paid manual engagements (flat fee, even $50) with real datasets from forums/researchers/small manufacturers. Record: what lanes people bring, what they gasp at, what they ask next, what price they didn't blink at.
- **Synthetic forensics demo:** till/transaction logs with planted theft, planted incompetence, planted sensor drift; publishable, nobody real in it; whitedoc and sales-demo double duty.
- **Pricing math check:** actual compute cost per job at target hosting, margin per proposed tier, and the $1,000/mo paths (100×$10 / 40×$25 / 20×$50).

### F. Sequencing (suggested order)
1. Legal ToS draft + Patreon-based license check (unblocks taking money at all).
2. Concierge engagements in parallel (unblocks value discovery).
3. Instrumentation + holdout ritual + report vocabulary (unblocks trustworthy launch).
4. Pool-one scrape → Isaac's market map (informs launch tier guesses).
5. Launch on byte quotas → collect pool two → let Isaac reprice.
6. Adversarial scrubber testing as a standing background job throughout.

---

## Part 4 — The one-paragraph version

WTT sells auditable data processing: upload a dataset, receive the generating function plus groupings, outliers, and causal decomposition — replicable by the client against data Isaac never saw, delivered in seconds instead of months. Payments, tax, and passwords belong to Stripe/Patreon and an auth provider; WTT holds a license table and nothing else. Client outputs are derivable solely from the client's own data; Prime grows only through openly corroborated, multiply-sourced knowledge, provably, with receipts. Pricing starts as simple monthly-ingest tiers and matures into the architecture's own physics: pay for novelty and private residue, the commons is free, and the bill goes down as Isaac understands you better.
