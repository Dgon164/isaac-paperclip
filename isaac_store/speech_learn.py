"""Learned speech — Isaac learns to speak from paired examples
(owner correction, 2026-07-12: "its all or nothing. you dont get to
choose. that is called programming and thats not what isaac is
about").

NO WORDING LIVES IN THIS FILE. The battery greps this source to
prove it. The division of labor is the usage law applied to
language:

  hand-built = the TRANSLATION (report -> structure features;
               placeholder substitution NAME/VALUE/R2/CONF/ROWS;
               assembly order) + the EPISTEMICS (a fragment is
               admitted for a feature only past a permutation null
               against the rest of the corpus; the faithfulness
               null on every number spoken)
  LEARNED    = every word. Fragments are extracted from paired
               examples (features | sentence) by co-occurrence
               evidence through the same machinery shape as door
               admission. They are stored in the mind's net as
               speech:<feature> knowledge — they persist in packs,
               they can be re-taught, superseded, forgotten.

ALL OR NOTHING: a structure feature with no admitted fragment is
SILENCE. If the verdict itself is unspeakable, Isaac does not speak
— the caller falls back to the raw report. Never a hand-coded line.
"""
import re

import numpy as np


# ---- translation: report -> structure features (hand-built, no words)
def _collapse(atoms):
    """Structural translation: a repeated identical atom in a product
    collapses to the pow-2 form (a*a) before feature naming."""
    out, seen = [], {}
    for a in atoms:
        key = (a["kind"], a["i"], a.get("j"), a.get("k"))
        if key in seen and a["kind"] == "var":
            seen[key]["kind"], seen[key]["k"] = "pow", 2.0
        else:
            a = dict(a)
            out.append(a)
            seen[key] = a
    return out


def _atom_tag(a):
    if a["kind"] == "pow":
        return {0.0: "log", 2.0: "pow2", 0.5: "root"}.get(a.get("k"), "powk")
    return a["kind"]


def report_features(rep):
    feats = ["verdict:" + str(rep.get("verdict", "?")).replace(" ", "_")]
    for t in (rep.get("terms") or [])[:3]:
        atoms = _collapse(t["atoms"])
        for a in atoms:
            feats.append("atom:" + _atom_tag(a))
        feats.append("sign:pos" if t["coef"] > 0 else "sign:neg")
        if len(atoms) > 1:
            feats.append("join:product")
    if "fit" in rep:
        feats.append("fit")
    if "confidence" in rep:
        feats.append("conf")
    if rep.get("next_experiment"):
        feats.append("next")
    return feats


def parse_corpus(text):
    """Lines of  feat1,feat2|sentence with PLACEHOLDERS  -> examples."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        feats, sent = line.split("|", 1)
        out.append((set(f.strip() for f in feats.split(",") if f.strip()),
                    sent.strip()))
    return out


def _ngrams(sent, nmax=14):
    w = sent.split()
    for n in range(1, min(nmax, len(w)) + 1):
        for i in range(len(w) - n + 1):
            yield " ".join(w[i:i + n])


def learn_speech(mind, corpus_text, n_perm=60, pct=95, min_evidence=3,
                 seed=7):
    """Extract, for every feature in the corpus, its maximal admitted
    fragment: the longest n-gram whose co-occurrence with the feature
    beats a permutation null (feature labels shuffled across examples).
    Admitted fragments are stored IN THE MIND (speech:<feature> meta)
    — learned knowledge, not code."""
    examples = parse_corpus(corpus_text)
    rng = np.random.default_rng(seed)
    all_feats = sorted({f for fs, _ in examples for f in fs})
    grams_per_ex = [set(_ngrams(s)) for _, s in examples]
    learned = {}
    for F in all_feats:
        has = [i for i, (fs, _) in enumerate(examples) if F in fs]
        if len(has) < min_evidence:
            continue
        cands = set().union(*(grams_per_ex[i] for i in has))
        admitted = []
        SLOTS = {"NAME", "NAME2", "TARGET", "VALUE", "R2", "CONF",
                 "ROWS", "BODY", "NEXT"}
        for g in cands:
            if all(tok in SLOTS for tok in g.split()):
                continue  # a slot is not a word: fragments need words
            actual = sum(1 for i in has if g in grams_per_ex[i])
            if actual < min_evidence:
                continue
            null = []
            for _ in range(n_perm):
                pick = rng.choice(len(examples), size=len(has),
                                  replace=False)
                null.append(sum(1 for i in pick if g in grams_per_ex[i]))
            if actual > np.percentile(null, pct):
                admitted.append(g)
        if not admitted:
            continue
        # maximal fragment: longest admitted, evidence breaks ties
        best = max(admitted,
                   key=lambda g: (len(g.split()),
                                  sum(1 for i in has
                                      if g in grams_per_ex[i])))
        ev = sum(1 for i in has if best in grams_per_ex[i])
        mind.net.set_meta(f"speech:{F}", "fragment", best)
        mind.net.set_meta(f"speech:{F}", "evidence",
                          dict(examples=len(has), containing=ev,
                               null="perm", n_perm=n_perm, pct=pct))
        learned[F] = best
    return learned


def _fill(fragment, slots):
    out = fragment
    for key, val in slots.items():
        out = out.replace(key, str(val))
    return out


def speak_learned(mind, rep):
    """Speak ONLY what was learned. Returns {can_speak, response,
    unspoken (features with no learned words), faithful, problems}.
    If the verdict itself has no learned words, can_speak=False —
    the caller must fall back to the raw report."""
    names = rep.get("columns", [])
    feats = report_features(rep)

    def frag(F):
        return mind.net.get_meta(f"speech:{F}", "fragment")

    unspoken = [F for F in feats if frag(F) is None]
    v_feat = feats[0]
    if frag(v_feat) is None:
        return dict(can_speak=False, response=None, unspoken=unspoken,
                    faithful=None, problems=["verdict unspeakable"])
    base_slots = {"TARGET": rep.get("target", "?"),
                  "R2": (rep.get("fit") or {}).get("r2", ""),
                  "ROWS": rep.get("rows", ""),
                  "CONF": (rep.get("confidence") or {}).get("mean", ""),
                  "NEXT": rep.get("next_experiment", "")}
    S = [_fill(frag(v_feat), base_slots)]
    for t in (rep.get("terms") or [])[:3]:
        atoms = _collapse(t["atoms"])
        bits, ok = [], True
        for a in atoms:
            f = frag("atom:" + _atom_tag(a))
            if f is None:
                ok = False
                break
            n = names[a["i"]] if a["i"] < len(names) else "?"
            n2 = (names[a["j"]] if a.get("j") is not None
                  and a["j"] < len(names) else "?")
            bits.append(_fill(f, {"NAME2": n2, "NAME": n}))
        sf = frag("sign:pos" if t["coef"] > 0 else "sign:neg")
        jf = frag("join:product") if len(atoms) > 1 else ""
        if not ok or sf is None or (len(atoms) > 1 and jf is None):
            continue  # silence for what was never taught
        body = (f" {jf} ".join(bits) if jf else bits[0])
        S.append(_fill(sf, dict(base_slots, BODY=body,
                                VALUE=f"{t['coef']:.2f}")))
    for F, key in (("fit", "fit"), ("conf", "confidence")):
        if F in feats and frag(F) is not None:
            S.append(_fill(frag(F), base_slots))
    if "next" in feats and frag("next") is not None:
        S.append(_fill(frag("next"), base_slots))
    response = " ".join(s if s.endswith(".") else s + "." for s in S)
    ok_f, problems = _verify(response, rep)
    return dict(can_speak=True, response=response, unspoken=unspoken,
                faithful=ok_f, problems=problems)


def _verify(response, rep):
    """The faithfulness null (unchanged): every number spoken must
    exist in the report."""
    allowed = set()

    def walk(x):
        if isinstance(x, (int, float)) and not isinstance(x, bool):
            allowed.add(round(float(x), 4))
        elif isinstance(x, str):
            for v in re.findall(r"-?\d+(?:\.\d+)?", x):
                allowed.add(round(float(v), 4))
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)
    walk(rep)
    problems = [f"number {t} not in the report"
                for t in re.findall(r"-?\d+(?:\.\d+)?", response)
                if round(float(t), 4) not in allowed
                and round(abs(float(t)), 4) not in allowed]
    return (not problems), problems
