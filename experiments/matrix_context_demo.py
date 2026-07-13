"""matrix_context_demo.py — the box->matmul lesson, applied to words
(owner, 2026-07-12: "it can handle 11 million lines of higgs data in
less than a minute. so what is happening?")

WHAT WAS HAPPENING: HIGGS flows through numpy as matrices (C-speed,
no Python objects per row). The word-net ran as Python object-graph
surgery — every shared-context check a Python set op, and FCA
superlinear in candidate circles because ubiquitous contexts make
every pair look shared. 3,400 sentences is not big data; the
representation was wrong for the compute.

THE DEMO (measured): vocab x context sparse counts, columns weighted
by the EXCESS law (a context everything has carries nothing), ONE
matmul = all-pairs weighted shared context. 3,417 sentences,
vocab 1,029: **0.07 s** (the crystallizer road took 20+ minutes).
Groups read straight off the matrix:
  is  ~ was, wasn't, isn't, does     (copula/aux + tense + negation)
  she ~ he, it                        (pronouns; third person)
  you ~ we, they, i                   (personal pronouns)
  eat ~ quit, learn, fix, hear, work  (verbs)

THE DESIGN IT JUSTIFIES (next build): doors stay the KNOWLEDGE —
durable, readable, in the net; the shared-context COMPUTE moves to
matrix land. Propose groups from the top matrix entries past a null,
mint them as type nodes with doors — same laws, same record, engine
room swapped. "Stop fitting boxes: observe + matmul."
"""
