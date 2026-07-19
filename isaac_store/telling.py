"""telling.py — THE TELLING ROAD (owner, 2026-07-18 evening: "if he
could just interpret 'ohm's law is v=ir' and he would create a node
for ohms law containing v=ir and will use it but validate with more
information later").

Plain-English law-telling, landed ENTIRELY on promoted roads — this
organ is translation + vet only, it owns no knowledge and no new
node kinds:

  "ohm's law is v=ir"
     -> parse (the v1 telling grammar, refusals loud)
     -> vet (a held law with the same NAME but a DIFFERENT form
        refuses — supersession is the duel's job, not the teller's;
        a self-referencing equation refuses)
     -> tell_law (the promoted door: MATCHES becomes a witness on
        the shared form, a new form enters TOLD-UNVERIFIED — usable
        at once, belief measured never told)
     -> the application fact-bundle (the curriculum's own ontology:
        uses-form / output / slots taught as facts, so the NAME
        stays recallable even when the form is shared — ohm and
        rect-area are one shape wearing two labels)

THE V1 TELLING GRAMMAR, SAID PLAINLY (ceilings declared, never
silent): sentence = "<name> is <out>=<expr>" (or "<name>: ...").
Quantities are SINGLE LETTERS (physics style — "ir" reads i*r);
"pi" is the one word the grammar knows. Factors: letters, numbers,
'*', '/', '^' with numeric powers (halves and negatives fine),
'+'/'-' terms, a bare number as intercept. NO parentheses, NO
functions in v1 — refused by name, never guessed at.

READ PROPOSES, THE ECHO CONFIRMS: every accepted telling is echoed
back rendered from what was actually stored ("v = +1*i*r"), so a
mis-parse is visible at the door, not discovered downstream.
"""
import math
import re

_SENT = re.compile(r"^\s*(?P<name>.+?)\s*(?:\bis\b|:)\s*"
                   r"(?P<eq>[^=]+=.+?)\s*$", re.IGNORECASE)
_TOK = re.compile(r"\s*(?:(?P<num>\d+\.?\d*|\.\d+)"
                  r"|(?P<let>[a-zA-Z]+)"
                  r"|(?P<pow>\^-?\d+\.?\d*)"
                  r"|(?P<op>[*/+\-]))")


def norm_name(raw):
    s = raw.strip().lower()
    s = re.sub(r"'s\b", "s", s)          # ohm's -> ohms
    s = re.sub(r"^the\s+", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def _refuse(why):
    return dict(refused=why)


def parse_told_law(text):
    """Sentence -> dict(name, output, slots, positional, said) or
    dict(refused=why). The grammar's ceilings refuse BY NAME."""
    m = _SENT.match(text)
    if not m:
        return _refuse("not a telling — the v1 shape is "
                       "\"<name> is <out>=<expression>\"")
    name = norm_name(m.group("name"))
    if not name:
        return _refuse("the law needs a name before 'is'")
    eq = m.group("eq").replace(" ", "")
    lhs, rhs = eq.split("=", 1)
    if not re.fullmatch(r"[a-zA-Z]", lhs):
        return _refuse(f"output '{lhs}' — v1 outputs are a single "
                       f"quantity letter (like v=ir)")
    out = lhs.lower()

    # tokenize the right side
    toks, i = [], 0
    while i < len(rhs):
        t = _TOK.match(rhs, i)
        if not t or t.end() == i:
            return _refuse(f"unreadable at '{rhs[i:i + 8]}' — the "
                           f"v1 vocabulary is letters, numbers, "
                           f"* / ^ + - (no parentheses, no "
                           f"functions)")
        toks.append(t)
        i = t.end()

    order = []                       # slots in first-appearance order

    def slot(ch):
        if ch not in order:
            order.append(ch)
        return order.index(ch)

    terms = []                       # (coef, {letter: exponent})
    coef, powers, sign, div = 1.0, {}, 1.0, False
    started = False

    def close_term():
        nonlocal coef, powers, sign, div, started
        if started:
            terms.append((sign * coef, dict(powers)))
        coef, powers, sign, div, started = 1.0, {}, 1.0, False, False

    def add_factor(base_letters=None, number=None):
        nonlocal coef, div, started
        started = True
        exp = -1.0 if div else 1.0
        div = False
        if number is not None:
            coef *= number ** (1.0 if exp > 0 else -1.0)
            return None
        return exp

    k = 0
    while k < len(toks):
        t = toks[k]
        if t.group("op") in ("+", "-"):
            if started and not div:
                close_term()
                sign = -1.0 if t.group("op") == "-" else 1.0
            elif not started:
                sign *= -1.0 if t.group("op") == "-" else 1.0
            else:
                return _refuse("a '/' with nothing after it")
        elif t.group("op") == "*":
            pass
        elif t.group("op") == "/":
            div = True
        elif t.group("num"):
            add_factor(number=float(t.group("num")))
        elif t.group("pow"):
            return _refuse(f"'^' needs a quantity before it "
                           f"(at '{t.group(0).strip()}')")
        elif t.group("let"):
            run = t.group("let")
            if run.lower() == "pi":
                add_factor(number=math.pi)
                k += 1
                continue
            if div and len(run) > 1:
                return _refuse(f"ambiguous '/{run}' — division "
                               f"applies to ONE quantity; write "
                               f"/{run[0]}/{run[1]} or use ^-1")
            letters = list(run.lower())  # physics style: ir = i*r
            for j, ch in enumerate(letters):
                exp = add_factor()
                p = 1.0
                if j == len(letters) - 1 and k + 1 < len(toks) \
                        and toks[k + 1].group("pow"):
                    p = float(toks[k + 1].group("pow")[1:])
                    k += 1
                powers[ch] = powers.get(ch, 0.0) + exp * p
        k += 1
    if div:
        return _refuse("a '/' with nothing after it")
    close_term()
    if not terms:
        return _refuse("no right-hand side to tell")

    # vet inside the parse: self-reference
    for _c, pw in terms:
        if out in pw:
            return _refuse(f"'{out}' appears on both sides — a law "
                           f"may not define a quantity by itself")
    # register slots in first-appearance order across terms
    for _c, pw in terms:
        for ch in pw:
            slot(ch)
    if not order:
        return _refuse("no quantities on the right side — that is "
                       "a constant, not a law")

    # render the canonical positional grammar tell_law speaks
    parts = []
    for c, pw in terms:
        if not pw:
            parts.append(f"{c:+.10g}")
            continue
        fs = []
        for ch in order:
            if ch not in pw:
                continue
            p = pw[ch]
            if p == 0:
                continue
            if p == 1.0:
                fs.append(f"x{slot(ch)}")
            elif p in (2.0, 3.0):
                # the house canonical for small integer powers is
                # repeated var factors (galileo is +33.08*x0*x0) —
                # a told square must wear the same form or kinship
                # goes blind to it
                fs.extend([f"x{slot(ch)}"] * int(p))
            else:
                fs.append(f"x{slot(ch)}^{p:g}")
        if not fs:
            parts.append(f"{c:+.10g}")
        else:
            parts.append(f"{c:+.10g}*" + "*".join(fs))
    positional = " ".join(parts)

    def said_from(eq_str):
        s = eq_str
        for ix in range(len(order) - 1, -1, -1):
            s = s.replace(f"x{ix}", order[ix])
        return f"{out} = {s}"

    return dict(name=name, output=out, slots=list(order),
                positional=positional, said=said_from(positional),
                grammar="v1: single-letter quantities; pi known; "
                        "no parentheses/functions")


def tell_english(mind, text, who="owner", container=None):
    """The front door for a told law: parse -> vet -> the promoted
    roads (tell_law + the application fact-bundle) -> the echo.
    Nothing lands unless the whole telling is admissible."""
    got = parse_told_law(text)
    if got.get("refused"):
        return got
    name = got["name"]
    try:
        new_model = mind._parse_equation(got["positional"])
    except ValueError as e:
        return _refuse(f"parsed but outside the told grammar: {e}")

    # THE NAME VET (container-blind on purpose — a name is a name
    # in every world; the dry road caught the blind version calling
    # the curriculum's own circle-area a stranger): a held name
    # with a DIFFERENT form refuses — supersession is the duel's
    # job, not the teller's.
    held_forms = list(mind.fact_index.get((name, "uses-form"), []))
    held_node = (f"law:{name}"
                 if mind.net.get_meta(f"law:{name}", "model")
                 else (f"law:{held_forms[0]}" if held_forms
                       else None))
    if held_node:
        held = mind.net.get_meta(held_node, "model")
        eq_held = ((mind.net.get_meta(held_node, "status") or {})
                   .get("equation")
                   or mind.net.get_meta(held_node, "equation")
                   or "?")
        if held and (mind._form_signature(held)
                     != mind._form_signature(new_model)):
            return _refuse(f"he already holds '{name}' as "
                           f"{eq_held} — a different form must win "
                           f"a duel, not a retelling")
        if held and mind._coefs_match(new_model, held):
            # a RETELLING of what he holds: a confirming witness on
            # HIS OWN node, never a scan that might land elsewhere
            st = mind.net.meta[held_node].setdefault("status", {})
            st.setdefault("witnesses", []).append(
                dict(who=who, equation=got["positional"]))
            mind.record_finding("told_match", name,
                                matches=str(held_node)[4:],
                                provenance=who)
            got.update(form=str(held_node)[4:],
                       tell=dict(status="MATCHES",
                                 law=str(held_node)[4:],
                                 retold=True),
                       who=who,
                       container=container or getattr(
                           mind, "active_container", "base"))
            return got

    if container:
        mind.open_world(container)
    r = mind.tell_law(name, got["positional"],
                      d=len(got["slots"]), who=who)
    form = r["law"] if r.get("status") == "MATCHES" else name
    mind.teach(name, "uses-form", form, container=container)
    mind.teach(name, "output", got["output"], container=container)
    mind.teach(name, "slots", ",".join(got["slots"]),
               container=container)
    got.update(form=form, tell=r,
               who=who, container=container or getattr(
                   mind, "active_container", "base"))
    return got


def recall_law(mind, name):
    """Name -> what he holds: the form, the equation rendered in
    the teller's own letters, the state, the witnesses. Reads the
    fact index directly (container-blind — recall is a READ face;
    the fact still wears its world on the law node itself), and
    falls back across told/discovered meta shapes (a discovered
    law keeps its equation outside status)."""
    name = norm_name(name)
    form = list(mind.fact_index.get((name, "uses-form"), []))
    node = (f"law:{form[0]}" if form else
            (f"law:{name}"
             if mind.net.get_meta(f"law:{name}", "model")
             else None))
    if node is None:
        return None
    formname = str(node)[4:]
    status = mind.net.get_meta(node, "status") or {}
    eq = (status.get("equation")
          or mind.net.get_meta(node, "equation") or "")
    out = (list(mind.fact_index.get((name, "output"), []))
           or ["y"])[0]
    slots = (list(mind.fact_index.get((name, "slots"), []))
             or [""])[0].split(",")
    said = eq
    for ix in range(len(slots) - 1, -1, -1):
        if slots[ix]:
            said = said.replace(f"x{ix}", slots[ix])
    return dict(name=name, form=formname, node=node,
                equation=eq, said=f"{out} = {said}",
                state=(status.get("state")
                       or status.get("verdict")
                       or mind.net.get_meta(node, "verdict")),
                who=(status.get("provenance")
                     or mind.net.get_meta(node, "provenance")),
                witnesses=len((status.get("witnesses") or [])),
                container=mind.net.get_meta(node, "container"),
                slots=slots, output=out)


# ── the goal grammar (the scaling campaign's rung 2 front door:
# "<want> from <name>=<value> <name> ..." — names without values
# ask for structure only) ─────────────────────────────────────────
_GOAL = re.compile(r"^\s*([a-zA-Z][\w-]*)\s+from\s+(.+)$",
                   re.IGNORECASE)


def parse_goal(text):
    m = _GOAL.match(text)
    if not m:
        return _refuse("not a goal — the shape is \"<want> from "
                       "<name>=<value> <name> ...\"")
    known = {}
    for tok in re.split(r"[,\s]+", m.group(2).strip()):
        if not tok:
            continue
        if "=" in tok:
            k, _, v = tok.partition("=")
            try:
                known[k.lower()] = float(v)
            except ValueError:
                return _refuse(f"'{tok}' — the value after = must "
                               f"be a number")
        else:
            known[tok.lower()] = None
    if not known:
        return _refuse("a goal needs at least one known quantity "
                       "after 'from'")
    return dict(want=m.group(1).lower(), known=known)


def render_goal_tree(out):
    """The decomposition, said plainly with its receipts."""
    L = [f"GOAL: {out['goal']}"
         + (f" = {out['value']:.6g}" if out.get("value") is not None
            else " (structure only — no full values given)"
            if not out["dark"] else "")]

    def walk(node, depth):
        pad = "  " * (depth + 1)
        q = node["quantity"]
        if node["status"] == "known":
            L.append(f"{pad}{q}: known")
        elif node["status"] == "via":
            v = (f" = {node['value']:.6g}"
                 if node.get("value") is not None else "")
            alt = (f"  [+{node['alternatives']} other road(s)]"
                   if node.get("alternatives") else "")
            L.append(f"{pad}{q}{v} via {node['app']}{alt}")
            for n in node["needs"]:
                walk(n, depth + 1)
        else:
            L.append(f"{pad}{q}: {node['status'].upper()} — "
                     f"{node.get('why', '')}")
    walk(out["tree"], 0)
    if out["dark"]:
        L.append(f"  DARK (teach or discover these): "
                 f"{', '.join(out['dark'])}")
    for r in out["receipts"]:
        L.append(f"  receipt: {r}")
    return "\n".join(L)
