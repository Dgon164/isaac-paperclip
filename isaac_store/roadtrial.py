"""The road-trial instrument panel (owner, 2026-07-17: "we are ready
for road trials. durability, range, power, efficiency, etc. does
performance increase or decrease over time and if so how?"). One
longitudinal record per call, appended to the account's
roadtrial.jsonl — the curves those records draw over his life ARE
the road trial:

  - SIZES: nodes / doors / facts / laws / findings / fragments —
    the growth axis every other gauge is plotted against.
  - PROBE_SECS: a fresh throwaway mind runs discover() on the SAME
    seeded world every time — engine efficiency drift, comparable
    across his whole life (durability of the capability).
  - ASK_MS: mean latency reading his own facts — does his net slow
    him down as it grows?
  - SELECTION: the owner's named scaling axis ("selecting and using
    the correct information as he scales will become more important
    over time") — sample his own laws, generate rows from each law's
    stored ranges, ask which_law to pick the author; precision out
    of asked. Fewer than two eligible laws = the gauge REFUSES with
    a note, never a fake 1.0.

The logger MEASURES and never changes him: every operation that
could write (which_law records findings; apply_law is engine work)
runs on an in-memory COPY of the mind; the account's mind is
byte-identical after logging (battery R2 proves it).
"""
import json
import os
import pickle
import time

import numpy as np

from . import bridge

_PROBE_SEED = 777
_SELECT_SEED = 555
_MAX_SELECT = 5
_ASK_SAMPLE = 20


def _eligible_laws(mind):
    out = []
    for node in sorted(map(str, mind.net.meta)):
        if not node.startswith("law:"):
            continue
        m = mind.net.get_meta(node, "model")
        if not m or m.get("lags_used") or m.get("composites_used"):
            continue
        d = int(m.get("d_raw") or m.get("d") or 0)
        ranges = m.get("ranges")
        if 1 <= d <= 3 and ranges and len(ranges) >= d:
            out.append((node[4:], d, ranges[:d]))
    return out[:_MAX_SELECT]


def log_roadtrial(home, mind, mod=None):
    mod = mod or bridge.load_isaac_module()
    counts = dict(
        nodes=len(mind.net.meta),
        doors=sum(len(v) for v in mind.net.doors.values()),
        facts=sum(len(v) for v in mind.fact_index.values()),
        laws=sum(1 for n in mind.net.meta
                 if str(n).startswith("law:")
                 and mind.net.get_meta(str(n), "model")),
        findings=len(mind.findings),
        fragments=sum(1 for n in mind.net.meta
                      if str(n).startswith("speech:heard:")))

    # engine probe: the same world every time, a fresh mind every time
    prng = np.random.default_rng(_PROBE_SEED)
    xp = prng.uniform(0, 10, 200).reshape(-1, 1)
    yp = 2.0 * xp[:, 0] + 1.0 + prng.normal(0, 0.02, 200)
    t0 = time.perf_counter()
    mod.Isaac().discover(xp, yp, name="roadtrial_probe")
    probe_secs = round(time.perf_counter() - t0, 3)

    # everything below runs on a COPY — measurement never writes
    copy = pickle.loads(pickle.dumps(mind))
    keys = sorted(map(repr, mind.fact_index.keys()))[:_ASK_SAMPLE]
    kmap = {repr(k): k for k in mind.fact_index.keys()}
    ask_ms = 0.0
    if keys:
        t0 = time.perf_counter()
        for k in keys:
            s, r = kmap[k]
            copy.ask(s, r)
        ask_ms = round((time.perf_counter() - t0) * 1000 / len(keys),
                       4)

    laws = _eligible_laws(copy)
    if len(laws) < 2:
        selection = dict(asked=0, right=0, precision=None,
                         note=f"insufficient laws ({len(laws)} "
                              f"eligible, need >=2) — gauge skipped,"
                              f" said")
    else:
        srng = np.random.default_rng(_SELECT_SEED)
        asked = right = 0
        for name, d, ranges in laws:
            X = np.column_stack([srng.uniform(lo, hi, 60)
                                 for lo, hi in ranges])
            y = copy.apply_law(name, X)
            if y is None or not np.isfinite(y).all():
                continue
            got = copy.which_law(X, y)
            asked += 1
            right += int(got.get("law") == name)
        if asked < 2:
            selection = dict(asked=asked, right=right, precision=None,
                             note="insufficient answerable laws — "
                                  "gauge skipped, said")
        else:
            selection = dict(asked=asked, right=right,
                             precision=round(right / asked, 3),
                             note="")

    rec = dict(stamp=time.strftime("%Y-%m-%d %H:%M:%S"), **counts,
               probe_secs=probe_secs, ask_ms=ask_ms,
               selection=selection)
    os.makedirs(home, exist_ok=True)
    with open(os.path.join(home, "roadtrial.jsonl"), "a",
              encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec
