"""Scrubber — the strip-identity worker (owner role, 2026-07-11).

Enforces the Identity Law on every intake path to Prime: "we want
isaac to understand the world, but we dont want him to identify
people, businesses or anything like that." Finds identifiable
information, strips it to category placeholders, keeps only the
general abstraction, and reports WHAT KINDS were stripped (counts
only — the report itself must never leak content).

Honest scope (owner: "to the best of our abilities"): pattern classes
below + an optional customer-supplied deny_list of known identities.
Free-text person/business names beyond those are the known limit —
which is exactly why the scrubber is one LAYER: the structural
quarantine underneath it does not depend on it being perfect, and
identity_gate() sits at Prime's admission as the final backstop
(anything identity-shaped that reaches the gate is REFUSED, not
cleaned).

Refusal rule: when identity is LOAD-BEARING — it appears in a dict
key or node name, so the structure itself depends on who — the scrub
is refused back to the sender. Refusals are answers.
"""
import json
import re

PATTERNS = [
    ("email", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("ssn", re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")),
    ("phone", re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)")),
    ("card", re.compile(r"(?<!\d)\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{4}(?!\d)")),
    ("ip", re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")),
    ("address", re.compile(r"\b\d+\s+\w+(?:\s\w+)?\s(?:St|Street|Ave|Avenue|Rd|Road|"
                           r"Blvd|Boulevard|Ln|Lane|Dr|Drive|Ct|Court|Way)\b", re.I)),
    ("honorific_name", re.compile(r"\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+"
                                  r"(?:\s+[A-Z][a-z]+)?")),
]


def _scrub_text(text, deny_list, report):
    for name in deny_list:
        if name and name in text:
            report["deny_list"] = report.get("deny_list", 0) + len(
                re.findall(re.escape(name), text))
            text = text.replace(name, "[deny_list]")
    for cat, rx in PATTERNS:
        text, n = rx.subn(f"[{cat}]", text)
        if n:
            report[cat] = report.get(cat, 0) + n
    return text


def _walk(x, deny_list, report, refusals, in_key=False):
    if isinstance(x, str):
        out = _scrub_text(x, deny_list, report)
        if in_key and out != x:
            refusals.append("identity in a key/name — the structure depends on WHO")
        return out
    if isinstance(x, dict):
        return {_walk(k, deny_list, report, refusals, in_key=True):
                _walk(v, deny_list, report, refusals) for k, v in x.items()}
    if isinstance(x, list):
        return [_walk(v, deny_list, report, refusals) for v in x]
    if isinstance(x, tuple):
        return tuple(_walk(v, deny_list, report, refusals) for v in x)
    if isinstance(x, (set, frozenset)):
        out = {_walk(v, deny_list, report, refusals) for v in x}
        return frozenset(out) if isinstance(x, frozenset) else out
    return x  # numbers/bools/None: measurements pass untouched


def scrub(payload, deny_list=()):
    """Scrub a share/intake payload. Returns a dict:
      ok True  -> {"ok": True, "clean": <scrubbed>, "report": {cat: n}}
      ok False -> {"ok": False, "why": ..., "report": {cat: n}}
    The report carries CATEGORIES AND COUNTS only, never content."""
    report, refusals = {}, []
    clean = _walk(payload, list(deny_list), report, refusals)
    if refusals:
        return {"ok": False, "report": report,
                "why": "cannot cleanly separate abstraction from identity: "
                       + refusals[0]}
    return {"ok": True, "clean": clean, "report": report}


def identity_gate(inner=None, deny_list=()):
    """Prime's admission backstop: anything identity-shaped that
    reaches the gate is REFUSED outright (scrubbing happens in the
    Scrubber worker — the gate never cleans, it only judges).
    Wraps an inner admission gate if given."""
    def gate(edit, state):
        report, refusals = {}, []
        _walk(edit, list(deny_list), report, refusals)
        if report or refusals:
            cats = ", ".join(f"{k}x{v}" for k, v in sorted(report.items()))
            return False, (f"Identity Law: identity-shaped content refused "
                           f"at the gate ({cats or 'structural'})")
        if inner is not None:
            return inner(edit, state)
        return True, "identity gate: clean"
    return gate
