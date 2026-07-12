"""Native gated English — road 2 of the translation layer (owner,
2026-07-12: "train isaac on how to speak english" before falling
back to an LLM mouth).

Isaac does not generate language; he REALIZES structure as speech.
Every sentence is produced from a report field by a fixed
compositional realizer — so faithfulness holds BY CONSTRUCTION —
and then verify_faithful() runs anyway as the null: every number in
the response must exist in the report (a tampered response is
caught). What has no field is not said: gated omission, never
invention. The full report stays attached beneath the response as
ground truth.

This is interrogate()'s gated-English road grown toward the user:
plain words, complete numbers, refusals spoken with the same
directness as answers.
"""
import re


def _atom_phrase(a, names):
    kind, i, j, k = a["kind"], a["i"], a["j"], a["k"]
    n = names[i] if i < len(names) else f"x{i}"
    n2 = names[j] if j is not None and j < len(names) else f"x{j}"
    if kind == "var":
        return n
    if kind == "pow":
        if k == 0:
            return f"the logarithm of {n}"
        if k == 2:
            return f"the square of {n}"
        if k == 0.5:
            return f"the square root of {n}"
        if k == -1:
            return f"the inverse of {n}"
        return f"{n} to the power {k:g}"
    if kind in ("sin", "cos"):
        return f"a repeating wave in {n}"
    if kind == "exp":
        return (f"exponential decay in {n}" if k > 0
                else f"exponential growth in {n}")
    if kind in ("sind", "cosd"):
        return f"the alignment between {n} and {n2}"
    if kind == "coshd":
        return f"steep growth with the gap between {n} and {n2}"
    return f"{kind}({n})"


def _term_phrase(term, names):
    # collapse repeats: a*a is "the square of a", not "a times a"
    parts, counts = [], {}
    for a in term["atoms"]:
        p = _atom_phrase(a, names)
        counts[p] = counts.get(p, 0) + 1
    for p, c in counts.items():
        if c == 1:
            parts.append(p)
        elif c == 2:
            parts.append(f"the square of {p}" if " " not in p
                         else f"({p}) squared")
        else:
            parts.append(f"the cube of {p}" if " " not in p
                         else f"({p}) cubed")
    body = " times ".join(parts)
    verb = "raises" if term["coef"] > 0 else "lowers"
    return f"{body} {verb} it (weight {term['coef']:.2f})"


_BANDS = [(0.9, "very confident"), (0.7, "fairly confident"),
          (0.5, "tentative"), (0.0, "low-confidence")]


def speak(rep):
    """Report dict -> {response, faithful, problems}. Every sentence
    realized from a field; nothing without a field is uttered."""
    names = rep.get("columns", [])
    target = rep.get("target", "the target")
    v = rep.get("verdict", "?")
    S = []
    if v == "UNDERSTOOD":
        S.append(f"I understand this data.")
    elif v == "PARTIAL":
        S.append(f"I found part of the pattern in {target}, "
                 f"but not all of it.")
    elif v == "CAPTURED":
        S.append(f"I can predict {target}, but I cannot yet say the "
                 f"rule as a formula — prediction without articulation.")
    else:
        S.append(f"I could not find a reliable relationship for "
                 f"{target} in this data — and I will not pretend to.")
    terms = rep.get("terms")
    if terms and v in ("UNDERSTOOD", "PARTIAL"):
        ranked = sorted(terms, key=lambda t: -abs(t["coef"]))
        lead = [f"mainly, {_term_phrase(ranked[0], names)}"]
        lead += [f"also, {_term_phrase(t, names)}" for t in ranked[1:3]]
        if len(ranked) > 3:
            lead.append("plus smaller terms — see the exact "
                        "equation below")
        S.append(f"What moves {target}: " + "; ".join(lead) + ".")
    if "fit" in rep:
        S.append(f"The fit explains the data with r2 {rep['fit']['r2']}"
                 f" over {rep['rows']} rows.")
    if "confidence" in rep:
        c = rep["confidence"]["mean"]
        band = next(b for lo, b in _BANDS if c >= lo)
        S.append(f"On your own data I am {band} ({c}).")
    if "accounting" in rep:
        a = rep["accounting"]
        bits = ", ".join(f"{v}% {k}" for k, v in a.items())
        S.append(f"Where the signal went: {bits}.")
    if rep.get("rivals"):
        S.append("Honesty note: rival explanations survive that the "
                 "data cannot yet tell apart.")
    if rep.get("next_experiment"):
        S.append(f"What I would do next: {rep['next_experiment']}")
    response = " ".join(S)
    ok, problems = verify_faithful(response, rep)
    return dict(response=response, faithful=ok, problems=problems)


def _all_numbers(x, out):
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        out.add(round(float(x), 4))
    elif isinstance(x, str):
        for v in re.findall(r"-?\d+(?:\.\d+)?", x):
            out.add(round(float(v), 4))
    elif isinstance(x, dict):
        for v in x.values():
            _all_numbers(v, out)
    elif isinstance(x, (list, tuple)):
        for v in x:
            _all_numbers(v, out)


def verify_faithful(response, rep):
    """The faithfulness null: every number spoken must exist in the
    report (rounded). A response that says a number the report does
    not contain FAILS — no invention survives, even our own."""
    allowed = set()
    _all_numbers(rep, allowed)
    problems = []
    for tok in re.findall(r"-?\d+(?:\.\d+)?", response):
        v = round(float(tok), 4)
        if v not in allowed and round(abs(v), 4) not in allowed:
            problems.append(f"number {tok} not in the report")
    return (not problems), problems
